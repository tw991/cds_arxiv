import urllib
import feedparser
import os
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
            self.time.append(entry.published)
            self.title.append(entry.title.replace('\n', '').replace('  ', ' '))
            self.category.append([t['term'] for t in entry.tags])
            self.contributor.append(entry.contributors)
            for link in entry.links:
                if 'title' in link.keys():
                    if link.title == 'pdf':
                        self.pdf.append(link.href)
        self.subject = combine_subject(self.category)

    def institution_verify(self, save=False, institution=['nyu', 'new york university']):
        remove_list = []
        if save == True:
            os.system('mkdir ./paper/%s/' %self.author)
        for count in pyprind.prog_bar(range(len(self.pdf))):
            if save == False:
                os.system('wget -q -U "Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.3) Gecko/20100401 '
                          'Firefox/3.6.3" -O ./check.pdf %s' %self.pdf[count])
            else:
                os.system('cp ./check.pdf ./paper/%s/%s.pdf' %(self.author, self.arxiv_id[count]))
            text = convert('./check.pdf', pages=[0,1,2]).lower()
            match_flag = False
            for match_text in institution:
                if match_text in text:
                    match_flag = True
                    break
            if match_flag == True:
                continue
            else:
                remove_list.append(count)
                print self.title[count]
        os.system("rm ./check.pdf")
        self.arxiv_id = list(np.delete(np.array(self.arxiv_id), remove_list))
        self.time = list(np.delete(np.array(self.arxiv_id), remove_list))
        self.title = list(np.delete(np.array(self.title), remove_list))
        self.category = list(np.delete(np.array(self.category), remove_list))
        self.pdf = list(np.delete(np.array(self.pdf), remove_list))
        self.contributor = list(np.delete(np.array(self.contributor), remove_list))
        self.count = len(self.title)
        self.subject = combine_subject(self.category)
        print('Remove %d articles' %len(remove_list))

    def subject_verify(self):
        subject_list = copy.copy(self.subject)
        remove_list = []
        self.parse()
        for count in pyprind.prog_bar(range(len(self.title))):
            if len(set(subject_list) & set(self.category[count])) == 0:
                remove_list.append(count)
        self.arxiv_id = list(np.delete(np.array(self.arxiv_id), remove_list))
        self.time = list(np.delete(np.array(self.arxiv_id), remove_list))
        self.title = list(np.delete(np.array(self.title), remove_list))
        self.category = list(np.delete(np.array(self.category), remove_list))
        self.pdf = list(np.delete(np.array(self.pdf), remove_list))
        self.contributor = list(np.delete(np.array(self.contributor), remove_list))
        self.count = len(self.title)
        self.subject = combine_subject(self.category)
        print('Remove %d articles' %len(remove_list))







if __name__ == '__main__':
    test = arxiv('Hogg_David')
    test.parse()
    print test.count
    print len(test.title)
    test.verify()