Install the project: From the project dir, run `python setup.py install`

Run the NIPS crawler, e.g.: `python header_extractor/nips_crawler.py --npapers 5 ~/data`
This will download 5 PDFs with corresponding BibTex to the folder ~/data

Run CERMINE to convert the PDFs to XML: `python header_extractor/pdf_to_xml.py ~/data`





