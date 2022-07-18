"""
This modeule implements reading pubmed xml fragments
"""
import os
import gzip
import xml.etree.ElementTree as ET
from typing import List
# In Google colab, the entire repo is cloned
from PubmedArticle import PubmedArticle


class PubmedReader:
    """
    This class is responsible for reading the Pubmed dataset
    """

    def __init__(self):
        """
        default constructor doesn't do anything
        """
        pass

    def get_xml_frags(self, dir: str) -> List[str]:
        """
        given a directory where all the xml fragments reside
        will return the list of all the xml fragments
        """
        file_names = os.listdir(dir)
        file_indexes = [i for i, val in enumerate(
            map(lambda nm: nm.startswith("pubmed")
                and nm.endswith(".xml.gz"),
                file_names)) if val]
        return list(map(lambda i: file_names[i], file_indexes))

    def process_xml_frags(
            self, dir: str) -> List[PubmedArticle]:
        frags = self.get_xml_frags(dir)
        for frag in frags:
            articles = self.process_xml_frag(dir + "/"
                                                 + frag)
            if len(articles) == 0:
                break
            for article in articles:
                yield article

                
    def process_xml_frag(
            self, fname: str) -> List[PubmedArticle]:
        """
        This method reads to a complete gzipped xml file
        and extracts each PubmedArticle, and returns a list
        of PubmedArticle objects that contain all the relevant
        fields
        """
        articles = []
        with gzip.open(fname, 'rt', encoding="utf-8") as f:
            count = 0
            pubmed_article_txt = ""
            record = False
            while True:
                line = f.readline()
                if not line:
                    break
                if '<PubmedArticle>' in line:
                    record = True
                if record:
                    pubmed_article_txt += line
                if '</PubmedArticle>' in line:
                    count += 1
                    record = False
                    articles.append(
                        self.process_pubmed_article_xml(pubmed_article_txt))
                    pubmed_article_txt = ""
        print("fname", fname, "articles", count)
        return articles

    def process_pubmed_article_xml(self, txt: str) -> PubmedArticle:
        """
        this article takes an XML fragment of a single Pubmed article
        entry and parses it for data
        It returns a populated PubmedArticle object
        """
        root = ET.fromstring(txt)
        pmid = root.findtext('.//PMID')
        title = root.findtext('.//ArticleTitle')
        abstract_text = root.findtext('.//AbstractText')
        journal = root.findtext('.//Title')
        year = root.findtext('.//PubDate/Year')
        mesh_major = list(
            map(lambda x: x.text, root.findall(".//DescriptorName")))
        return PubmedArticle(
            pmid, title, journal, year, abstract_text, mesh_major)


# TODO add unit tests
# TODO add ability to index right off the pubmed site
# fname = "data/allMeSH_2020.zip"
# f2 = "data/allMeSH_2020.json"
# f3 = "allMeSH_2020.json"


# print("startstart")
# reader = PubmedReader()
# count = 0
# for article in reader.process_xml_frags('data2', max_article_count=3000):
#     count += 1
#     if count % 1000 == 0:
#         print('count', count)

# print('count', count)
# print(article.abstract_text)
# print("done done")
