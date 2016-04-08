import os
import argparse
from pkg_resources import resource_filename


def process_dir(indir):
    # TODO change version to 1.8 release
    cermine_jar = resource_filename('header_extractor.resources',
                                  'cermine-impl-1.9-SNAPSHOT-jar-with-dependencies.jar')
    cmd = 'java -cp %s pl.edu.icm.cermine.PdfNLMContentExtractor -path %s' % (cermine_jar, indir)
    print cmd
    os.system(cmd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert PDFs to XML using CERMINE')
    parser.add_argument('indir', type=str, help='directory where pdfs/bibtex files are stored')
    args = parser.parse_args()
    print args
    process_dir(args.indir)

