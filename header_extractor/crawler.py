import os
import time
import codecs
from bs4 import BeautifulSoup

WAIT = 30  # how long to sleep (ms) after requests


class Crawler(object):

    def __init__(self, outdir, index_url):
        self.outdir = outdir.rstrip('/')
        self.index_url = index_url
        self.index_file = self.download_index_page()
        self.links = self.extract_index_links()

    def download(self, target, outdoc, do_wait=True):
        outdir = self.outdir
        existing = set(['%s/%s' % (outdir, f) for f in os.listdir(outdir)])
        if outdoc in existing:
            print 'found ', outdoc, ', skipping.'
            return
        cmd = 'wget --output-document=%s %s' % (outdoc, target)
        print cmd
        os.system(cmd)
        if do_wait:
            print 'waiting', WAIT, '...'
            time.sleep(WAIT)

    def download_index_page(self):
        outfile = '%s/INDEX' % self.outdir
        self.download(self.index_url, outfile, do_wait=False)
        return outfile

    def extract_index_links(self):
        return []

    def download_paper(self, link):
        pass

    def download_papers(self, npapers=-1):
        if npapers < 0:
            for link in self.links:
                self.download_paper(link)
        else:
            for link in self.links[:npapers]:
                self.download_paper(link)


class NIPSCrawler(Crawler):

    def __init__(self, outdir, index_url):
        Crawler.__init__(self, outdir, index_url)

    def download_paper(self, link):
        outfile_base = link.split('/')[-1]
        # download the PDF
        outfile_pdf = '%s/%s.pdf' % (self.outdir, outfile_base)
        pdf_req = link + '.pdf'
        self.download(pdf_req, outfile_pdf, do_wait=False)
        # download the Bibtex file
        outfile_bib = '%s/%s.bib' % (self.outdir, outfile_base)
        bibtex_req = link + '/bibtex'
        self.download(bibtex_req, outfile_bib, do_wait=True)

    def extract_index_links(self):
        """
        Extract the links to download from an 'index page' like
        https://papers.nips.cc/book/advances-in-neural-information-processing-systems-28-2015
        :param index_page: html of INDEX_URL
        :return: list of links
        """
        links = []
        soup = BeautifulSoup(codecs.open(self.index_file, 'r', 'utf8').read())
        divs = soup.find_all('div')
        for div in divs:
            cls = div['class'][0]
            if cls == 'main-container':
                ul = div.find('ul')
                for li in ul.find_all('li'):
                    anchs = li.find_all('a')
                    for a in anchs:
                        href = a['href']
                        if href.startswith('/paper/'):
                            links.append(href)
        full_links = []
        prefix = 'https://papers.nips.cc'
        for link in links:
            fl = '%s%s' % (prefix, link)
            full_links.append(fl)
        return full_links


class ICMLCrawler(Crawler):

    def __init__(self, outdir, index_url):
        Crawler.__init__(self, outdir, index_url)

    def download_paper(self, link):
        outfile_base = link.split('/')[-1]
        outfile_base = outfile_base.split('.')[0]
        outfile_pdf = '%s/%s.pdf' % (self.outdir, outfile_base)
        self.download(link, outfile_pdf, do_wait=True)

    def extract_index_links(self):
        links = []
        soup = BeautifulSoup(codecs.open(self.index_file, 'r', 'utf8').read())
        divs = []
        for div in soup.find_all('div'):
            if 'class' in div.attrs:
                if div['class'][0] == 'paper':
                    divs.append(div)
        for div in divs:
            ps = div.find_all('p')
            for p in ps:
                if p['class'][0] == 'links':
                    anchs = p.find_all('a')
                    for anch in anchs:
                        if anch['href'].endswith('.pdf') and not anch['href'].endswith('-supp.pdf'):
                            link = anch['href']
                            if link.startswith('http'):
                                links.append(link)
                            else:
                                full_link = '%s/%s' % (self.index_url, link)
                                links.append(full_link)
        return links

