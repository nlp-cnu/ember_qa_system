"""
This module implements the class DataSetReader which contains
 the implementation of code to read the BioAsq dataset
"""
from typing import List


class PubmedArticle:
    # seem to be 14,913,938 articles

    def fromDict(data: dict):
        pmid = data["pmid"]
        title = data["title"]
        journal = data["journal"]
        mesh_major = data["meshMajor"]
        year = data["year"]
        abstract_text = data["abstractText"]
        return PubmedArticle(pmid, title, journal,
                             year, abstract_text, mesh_major)

    def __init__(self, pmid: str, title: str, journal: str,
                 year: str, abstract_text: str, mesh_major: List[str]):
        self.journal = journal
        self.mesh_major = mesh_major
        self.year = year
        self.abstract_text = abstract_text
        self.pmid = pmid
        self.title = title


