from bs4 import BeautifulSoup
import codecs
import os
import time


def extract_index_links(index_page):
    """
    Extract the links to download from an 'index page' like
    https://papers.nips.cc/book/advances-in-neural-information-processing-systems-28-2015
    :param index_page:
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


def download_paper(link):
    outdir = '/Users/kate/research/header_extractor/pages'
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
    links = extract_index_links(codecs.open('advances-in-neural-information-processing-systems-28-2015', 'r', 'utf8').read())
    for link in links[:1]:
        download_paper(link)
        time.sleep(30)
