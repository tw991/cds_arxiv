import urllib
import feedparser
import os
import shutil
import numpy as np
import pyprind
from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import copy


def convert(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = file(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    return text


def combine_subject(sub_list):
    out_set = []
    for lst in sub_list:
        out_set = list(set(out_set + lst))
    return out_set


class arxiv:

    def __init__(self, author_input):
        '''
        :param author: Author's name
        :return:
        '''
        if isinstance(author_input, str):
            self.author = author_input.strip()
            self.feed = None
            self.count = 0
            self.arxiv_id = []
            self.time = []
            self.title = []
            self.category = []
            self.pdf = []
            self.subject = []
            self.contributor = []

    def query(self):
        if self.author is not None:
            base_url = 'http://export.arxiv.org/api/query?'
            query = 'search_query=au:+%s&max_results=1000' % self.author
            response = urllib.urlopen(base_url+query).read()
            response = response.replace('author','contributor')
            feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
            feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'
            self.feed = feedparser.parse(response)

    def parse(self):
        if self.feed is None:
            self.query()

        self.count = int(self.feed.feed.opensearch_totalresults)
        for entry in self.feed.entries:
            self.arxiv_id.append(entry.id.split('/abs/')[-1])
            self.time.append(entry.published[:10])
            self.title.append(entry.title.replace('\n', '').replace('  ', ' '))
            category_pre = [t['term'] for t in entry.tags]
            for cat in category_pre:
                if len(cat.split(', '))>1:
                    category_pre.remove(cat)
            self.category.append(category_pre)
            self.contributor.append([author.name for author in entry.contributors])
            for link in entry.links:
                if 'title' in link.keys():
                    if link.title == 'pdf':
                        self.pdf.append(link.href)
        self.subject = combine_subject(self.category)

    def institution_verify(self, save=False, institution=['nyu', 'new york university']):
        if self.count != 0:
            remove_list = []
            if save == True and not os.path.exists('./paper/%s/' %self.author):
                os.makedirs('./paper/%s/' %self.author)
            for count in pyprind.prog_bar(range(len(self.pdf))):
                os.system('wget -q -U "Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.3) Gecko/20100401 '
                          'Firefox/3.6.3" -O ./check.pdf %s' %self.pdf[count])
                if save == True:
                    #os.system('cp ./check.pdf ./paper/%s/%s.pdf' %(self.author, self.arxiv_id[count]))
                    if len(self.arxiv_id[count].split('/')) >1 :
                        temp_dir = self.arxiv_id[count].split('/')[0]
                        if not os.path.exists('./paper/%s/%s/' % (self.author, temp_dir)):
                            os.makedirs('./paper/%s/%s/' % (self.author, temp_dir))
                    shutil.copy('./check.pdf', './paper/%s/%s.pdf' %(self.author, self.arxiv_id[count]))
                try:
                    text = convert('./check.pdf', pages=[0,1,2]).lower()
                    match_flag = False
                    for match_text in institution:
                        if text.find(match_text) != -1:
                            match_flag = True
                            break
                    if match_flag == True:
                        continue
                    else:
                        remove_list.append(count)
                except:
                    print("Can not read file %s" % self.arxiv_id[count])
                    remove_list.append(count)
                    continue
            os.system("rm ./check.pdf")
            self.arxiv_id = (np.delete(np.array(self.arxiv_id), remove_list, axis=0)).tolist()
            self.time = (np.delete(np.array(self.time), remove_list, axis=0)).tolist()
            self.title = (np.delete(np.array(self.title), remove_list, axis=0)).tolist()
            self.category = (np.delete(np.array(self.category), remove_list, axis=0)).tolist()
            self.pdf = (np.delete(np.array(self.pdf), remove_list, axis=0)).tolist()
            self.contributor = (np.delete(np.array(self.contributor), remove_list, axis=0)).tolist()
            self.count = len(self.title)
            self.subject = combine_subject(self.category)
            print('Remove %d articles' % len(remove_list))


def subject_verify(new_arxiv):
    if new_arxiv.count > 0:
        subject_list = copy.copy(new_arxiv.subject)
        remove_list = []
        new_ver = arxiv(new_arxiv.author)
        new_ver.parse()
        for count in pyprind.prog_bar(range(len(new_ver.title))):
            if len(set(subject_list) & set(new_ver.category[count])) == 0:
                remove_list.append(count)
        new_ver.arxiv_id = (np.delete(np.array(new_ver.arxiv_id), remove_list, axis=0)).tolist()
        new_ver.time = (np.delete(np.array(new_ver.time), remove_list, axis=0)).tolist()
        new_ver.title = (np.delete(np.array(new_ver.title), remove_list, axis=0)).tolist()
        new_ver.category = (np.delete(np.array(new_ver.category), remove_list, axis=0)).tolist()
        new_ver.pdf = (np.delete(np.array(new_ver.pdf), remove_list, axis=0)).tolist()
        new_ver.contributor = (np.delete(np.array(new_ver.contributor), remove_list, axis=0)).tolist()
        new_ver.count = len(new_ver.title)
        new_ver.subject = combine_subject(new_ver.category)
        print('Remove %d articles' % len(remove_list))
        return new_ver
    else:
        return new_arxiv







if __name__ == '__main__':
    test = arxiv('Sontag_David')
    test.parse()
    print test.count
    print len(test.title)
    test.institution_verify()
    print test.contributor
    test = subject_verify(test)
    print test.count