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


class arxiv:

    def __init__(self, author_input):
        '''
        :param author: Author's name
        :return:
        '''
        if isinstance(author_input, str):
            self.author = author_input
            self.feed = None
            self.count = 0
            self.arxiv_id = []
            self.time = []
            self.title = []
            self.category = []
            self.pdf = []

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
            for link in entry.links:
                if 'title' in link.keys():
                    if link.title == 'pdf':
                        self.pdf.append(link.href)

    def verify(self):
        remove_list = []
        for count in pyprind.prog_bar(range(len(self.pdf))):
            os.system('wget -q -U "Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3" -O ./check.pdf %s' %self.pdf[count])
            text = convert('./check.pdf',pages=[0,1,2]).lower()
            if text.find('nyu') or text.find('new york university'):
                continue
            else:
                remove_list.append(count)
        os.system("rm ./check.pdf")
        self.arxiv_id = list(np.delete(np.array(self.arxiv_id), remove_list))
        self.time = list(np.delete(np.array(self.arxiv_id), remove_list))
        self.title = list(np.delete(np.array(self.title), remove_list))
        self.category = list(np.delete(np.array(self.category), remove_list))
        self.pdf = list(np.delete(np.array(self.pdf), remove_list))
        self.count = len(self.title)
        print('Remove %d articles' %len(remove_list))





if __name__ == '__main__':
    test = arxiv('Hogg_David')
    test.parse()
    print test.count
    print len(test.title)