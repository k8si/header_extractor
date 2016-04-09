import argparse
from crawler import ICMLCrawler


INDEX_URL = 'http://jmlr.org/proceedings/papers/v32'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='download PDFs and Bibtex from ICML conference website')
    parser.add_argument('outdir', type=str, help='directory where downloaded pdfs/bibtex files will be stored')
    parser.add_argument('-n', '--npapers', default=5, type=int, help='number of papers to download (-1 for all)')
    args = parser.parse_args()
    print args
    crawler = ICMLCrawler(args.outdir, INDEX_URL)
    crawler.download_papers(npapers=args.npapers)



