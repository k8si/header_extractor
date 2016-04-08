from bs4 import BeautifulSoup
import codecs
import os
import time
import argparse


INDEX_URL = 'https://papers.nips.cc/book/advances-in-neural-information-processing-systems-28-2015'
WAIT = 20  # how long to sleep (ms) after requests


def download_index_page(outdir):
    outfile = '%s/INDEX' % outdir
    cmd = 'wget --output-document=%s %s' % (outfile, INDEX_URL)
    print cmd
    os.system(cmd)
    print 'sleep ', WAIT, '...'
    time.sleep(WAIT)
    return outfile


def extract_index_links(index_page):
    """
    Extract the links to download from an 'index page' like
    https://papers.nips.cc/book/advances-in-neural-information-processing-systems-28-2015
    :param index_page: html of INDEX_URL
    :return: list of links
    """
    links = []
    soup = BeautifulSoup(index_page)
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


def download_paper(link, outdir):
    outfile_base = link.split('/')[-1]

    # download the PDF
    outfile_pdf = '%s/%s.pdf' % (outdir, outfile_base)
    pdf_req = link + '.pdf'
    cmd = 'wget --output-document=%s %s' % (outfile_pdf, pdf_req)
    print cmd
    os.system(cmd)

    # download the Bibtex file
    outfile_bib = '%s/%s.bib' % (outdir, outfile_base)
    bibtex_req = link + '/bibtex'
    cmd = 'wget --output-document=%s %s' % (outfile_bib, bibtex_req)
    print cmd
    os.system(cmd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='download PDFs and Bibtex from NIPS conference website')
    parser.add_argument('outdir', type=str, help='directory where downloaded pdfs/bibtex files will be stored')
    parser.add_argument('-n', '--npapers', default=5, type=int, help='number of papers to download (-1 for all)')
    args = parser.parse_args()
    print args
    indexfile = download_index_page(args.outdir)
    links = extract_index_links(codecs.open(indexfile, 'r', 'utf8').read())
    n = args.npapers
    for link in links[:n]:
        download_paper(link, args.outdir)
        print 'sleep ', WAIT, '...'
        time.sleep(WAIT)

