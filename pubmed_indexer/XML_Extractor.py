from PubmedReader import PubmedReader
from PubmedIndexer import PubmedIndexer
import lxml.etree as ET

def formatTree(filename):
    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(filename, parser)
    tree.write(filename, pretty_print=True)

def extract_and_write(filename):
    """
    Extract information from IR system and write to XML file. Format is:
    <Result PMID=1>
       <Journal>Title of journal</Journal>
       <Year>Year published</Year>
       <Title>Title of article</Title>
       <Abstract>Abstract (~couple of sentences/a paragraph)</Abstract>
       <MERS>tag1</MERS>
       <MERS>tag2</MERS>
    </Result>
    :param filename: Name of the XML file used in the QA system
    """
    origTree = ET.parse(filename)
    root = origTree.getroot()
    # parser = ET.XMLParser(remove_blank_text=True)
    # root = ET.parse(filename, parser).getroot()

    # Find the QP element and grab each query
    QP = root.find("QP")
    question = root.text
    query = QP.find("Query").text

    # Use the query as the search term in the IR system (assumed indexed)
    # pubmed_indexer = PubmedIndexer()
    # pubmed_indexer.mk_index()
    # results = pubmed_indexer.search(query)

    pubmed_indexer = PubmedIndexer()
    pubmed_indexer.mk_index(overwrite=True)
    reader = PubmedReader()
    articles = reader.process_xml_frags('data2', max_article_count=1000)
    pubmed_indexer.index_docs(articles, limit=1000)
    results = pubmed_indexer.search("flu")

    print("Results length", len(results))

    # Create IR subelement
    IR = ET.SubElement(root, "IR")

    # Create a subelement for each part of the result (there can be many)
    for pa in results:
        result = ET.SubElement(IR, "Result")
        result.set("PMID", pa.pmid)
        journal = ET.SubElement(result, "Journal")
        journal.text = pa.journal
        year = ET.SubElement(result, "Year")
        year.text = pa.year
        title = ET.SubElement(result, "Title")
        title.text = pa.title
        abstract = ET.SubElement(result, "Abstract")
        abstract.text = pa.abstract_text
        for mesh in pa.mesh_major:
            mesh_major = ET.SubElement(result, "MeSH")
            mesh_major.text = mesh

    tree = ET.ElementTree(root)
    tree.write(filename, pretty_print=True)

def main():
    extract_and_write("test.XML")

if __name__ == "__main__":
    main()