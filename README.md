Some tools to extract headers from academic paper PDFs (based on [CERMINE](https://github.com/CeON/CERMINE)).

Install the project: From the project dir, run `python setup.py install --user`

Run the NIPS crawler, e.g.: `python header_extractor/nips_crawler.py --npapers 5 ~/data`
This will download 5 PDFs with corresponding BibTex to the folder ~/data

Run CERMINE to convert the PDFs to XML: `python header_extractor/pdf_to_xml.py ~/data`

Parse CERMINE XML and extract paper metadata: `python header_extractor/xml_to_metadata.py ~/data`
