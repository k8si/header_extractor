import argparse
import glob




def process_dir(indir):
    filenames = glob.glob('%s/*.cermxml' % indir)
    print filenames


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert (Cerm)XML to paper metadata.')
    parser.add_argument('indir', type=str, help='directory where *.cermxml files are stored')
    args = parser.parse_args()
    print args
    process_dir(args.indir)
