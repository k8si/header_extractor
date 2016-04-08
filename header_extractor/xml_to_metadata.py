import argparse
import glob
from bs4 import BeautifulSoup
import codecs
import bibtexparser as btp


class Author(object):
    def __init__(self, docid, name=None, affiliation=None, email=None):
        self.docid = docid
        self.name = name
        self.affiliation = affiliation
        self.email = email

    def __repr__(self):
        xml = ['<author>',
               '<name>%s</name>' % self.name,
               '%s' % (repr(self.affiliation)),
               '<email>%s</email>' % self.email,
               '</author>']
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
               '<name>%s</name>' % self.name,
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
        xml = ['<document>',
               '<title>%s</title>' % self.title,
               '<authors>%s</authors>' % (''.join([repr(a) for a in self.authors])),
               '<year>%s</year>' % self.year,
               '</document>']
        return ''.join(xml)

    def __str__(self):
        return repr(self)


class Doc(object):
    def __init__(self, id, dir):
        self.id = id
        self.dir = dir
        self.xml_file = '%s/%s.cermxml' % (dir, id)
        self.bib_file = '%s/%s.bib' % (dir, id)
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
                affid = aff.find('label').string
                aff = Affiliation(self.id,
                                  affid,
                                  aff,
                                  name=aff.find('institution').string)
                affmap[affid] = aff

            for contrib in cg.find_all('contrib'):
                if contrib['contrib-type'] == 'author':
                    affid = contrib.find('xref').string
                    assert affid in affmap, '%s %s' % (affid, ','.join(affmap.keys()))
                    aff = affmap[affid]
                    emailtag = contrib.find('email')
                    if emailtag:
                        email = emailtag.string
                    else:
                        email = None
                    author = Author(self.id,
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

        xml = codecs.open(self.xml_file, 'r', 'utf8').read()
        soup = BeautifulSoup(xml)
        header = soup.find('front')
        title = extract_title(header)
        authors = extract_authors(header)
        year = extract_year(header)
        mdata = Metadata(self.id,
                         title=title,
                         authors=authors,
                         year=year)
        return mdata

    def _process_bib(self):

        def extract_authors(bibmap):
            all = bibmap[u'author']
            names = all.split('and')
            authors = []
            for name in names:
                authors.append(Author(self.id, name=name))
            return authors

        with open(self.bib_file) as bibfile:
            s = bibfile.read()
        bib_db = btp.loads(s)
        bmap = bib_db.entries[0]
        authors = extract_authors(bmap)
        title = bmap[u'title']
        year = bmap[u'year']
        mdata = Metadata(self.id,
                         title=title,
                         authors=authors,
                         year=year)
        return mdata

    def __repr__(self):
        return repr(self.xml_metadata)


def process_dir(indir):
    xml_files = glob.glob('%s/*.cermxml' % indir)
    docs = {}
    for fname in xml_files:
        base = fname.split('/')[-1].split('.')[0]
        doc = Doc(base, indir)
        docs[base] = doc
    return docs


def write_docs(docs, outdir):
    for docid, doc in docs.items():
        outfname = '%s/%s.metadata' % (outdir, docid)
        with codecs.open(outfname, 'w', 'utf8') as writer:
            soup = BeautifulSoup(repr(doc), 'xml')
            writer.write(soup.prettify())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert (Cerm)XML to paper metadata.')
    parser.add_argument('indir', type=str, help='directory where *.cermxml files are stored')
    args = parser.parse_args()
    print args
    docs = process_dir(args.indir)
    write_docs(docs, args.indir)

