import argparse
import glob
from bs4 import BeautifulSoup
import codecs
import bibtexparser as btp


def enc_utf8(s):
    if s is None or len(s) == 0:
        return 'None'.encode('utf8')
    else:
        return s.encode('utf8')


class Author(object):
    def __init__(self, docid, name=None, affiliation=None, email=None):
        self.docid = docid
        self.name = name
        self.affiliation = affiliation
        self.email = email

    def __repr__(self):
        xml = ['<author>']
        xml.append('<name>%s</name>' % enc_utf8(self.name))
        if self.affiliation:
            xml.append('%s' % repr(self.affiliation))
        else:
            xml.append('<affiliation>None</affiliation>')
        xml.append('<email>%s</email>' % enc_utf8(self.email))
        xml.append('</author>')
        return ''.join(xml)

    def __str__(self):
        return repr(self)


class Affiliation(object):
    def __init__(self, docid, affiliation_id, xml, name=None):
        self.docid = docid
        self.affiliation_id = affiliation_id
        self.xml = xml
        self.name = name

    def __repr__(self):
        xml = ['<affiliation>',
               '<name>%s</name>' % enc_utf8(self.name),
               '</affiliation>']
        return ''.join(xml)


class Metadata(object):
    def __init__(self, docid, title=None, authors=None, year=None, **kwargs):
        self.docid = docid
        self.title = title
        self.authors = authors
        self.year = year
        self.other = kwargs

    def __repr__(self):
        xml = ['<document>']
        xml.append('<title>%s</title>' % enc_utf8(self.title))
        if self.authors:
            xml.append('<authors>%s</authors>' % (''.join([repr(a) for a in self.authors])))
        else:
            xml.append('<authors>None</authors>')
        xml.append('<year>%s</year>' % enc_utf8(self.year))
        xml.append('</document>')
        return ''.join(xml)

    def __str__(self):
        return repr(self)


class Doc(object):
    def __init__(self, docid, indir, use_bibtex=False):
        self.docid = docid
        self.indir = indir.rstrip('/')
        self.use_bibtex = use_bibtex
        self.xml_file = '%s/%s.cermxml' % (self.indir, self.docid)
        self.bib_file = '%s/%s.bib' % (self.indir, self.docid)
        self.xml_metadata = self._process_xml()
        self.bib_metadata = self._process_bib()

    def _process_xml(self):

        def extract_title(header):
            tg = header.find('title-group')
            if tg is None:
                return None
            title = tg.find('article-title')
            if title is None:
                return None
            return title.string

        def extract_authors(header):
            authors = []
            affmap = {}
            cg = header.find('contrib-group')
            if cg is None: return None
            for aff in cg.find_all('aff'):
                if aff is None: continue
                affid = aff.find('label').string
                inst = aff.find('institution')
                if inst:
                    inst_string = inst.string
                else:
                    inst_string = None
                aff = Affiliation(self.docid,
                                  affid,
                                  aff,
                                  name=inst_string)
                affmap[affid] = aff

            for contrib in cg.find_all('contrib'):
                if contrib['contrib-type'] == 'author':
                    xref = contrib.find('xref')
                    if xref is not None:
                        affid = xref.string
                        assert affid in affmap, '%s %s' % (affid, ','.join(affmap.keys()))
                        aff = affmap[affid]
                    else:
                        aff = None
                    emailtag = contrib.find('email')
                    if emailtag:
                        email = emailtag.string
                    else:
                        email = None
                    author = Author(self.docid,
                                    name=contrib.find('string-name').string,
                                    affiliation=aff,
                                    email=email)
                    authors.append(author)
            return authors

        def extract_year(header):
            pd = header.find('pub-date')
            if pd is None: return None
            year = pd.find('year')
            if year:
                return year.string
            return None

        try:
            xml = codecs.open(self.xml_file, 'r', 'utf8').read()
        except UnicodeDecodeError:
            try:
                xml = open(self.xml_file, 'r').read()
            except Exception:
                raise
        soup = BeautifulSoup(xml)
        header = soup.find('front')
        title = extract_title(header)
        authors = extract_authors(header)
        year = extract_year(header)
        mdata = Metadata(self.docid,
                         title=title,
                         authors=authors,
                         year=year)
        return mdata

    def _process_bib(self):

        def extract_authors(bibmap):
            all = bibmap[u'author']
            names = filter(lambda n: len(n) > 0 and n != ' ', all.split('and'))
            return [Author(self.docid, name=name) for name in names]

        with open(self.bib_file) as bibfile:
            s = bibfile.read()
        bib_db = btp.loads(s)
        bmap = bib_db.entries[0]
        authors = extract_authors(bmap)
        title = bmap[u'title']
        year = bmap[u'year']
        mdata = Metadata(self.docid,
                         title=title,
                         authors=authors,
                         year=year)
        return mdata

    def __repr__(self):
        if self.use_bibtex:
            return repr(self.bib_metadata)
        else:
            return repr(self.xml_metadata)


def process_dir(indir, use_bibtex=False):
    xml_files = glob.glob('%s/*.cermxml' % indir)
    docs = {}
    for fname in xml_files:
        base = fname.split('/')[-1].split('.')[0]
        try:
            doc = Doc(base, indir, use_bibtex=use_bibtex)
            docs[base] = doc
        except Exception:
            raise
    return docs


def write_docs(docs, outdir):
    for docid, doc in docs.items():
        outfname = '%s/%s.metadata' % (outdir, docid)
        with codecs.open(outfname, 'w', 'utf8') as writer:
            soup = BeautifulSoup(repr(doc))
            writer.write(soup.prettify())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert (Cerm)XML to paper metadata.')
    parser.add_argument('indir', type=str, help='directory where *.cermxml files are stored')
    parser.add_argument('-b', '--use-bibtex', type=int, default=0,
                        help='use *.bib files instead of *.cermxml for metadata extraction')
    args = parser.parse_args()
    print args
    use_bibtex = bool(args.use_bibtex)
    docs = process_dir(args.indir, use_bibtex=use_bibtex)
    write_docs(docs, args.indir)

