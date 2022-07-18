"""
This module indexes the Pubmed dataset using Whoosh
"""
import os
import os.path
import argparse
import shutil
from whoosh import index
from whoosh.fields import Schema, TEXT, IDLIST, ID, NUMERIC
from whoosh.analysis import StemmingAnalyzer
from whoosh.qparser import QueryParser
from PubmedReader import PubmedReader
from PubmedArticle import PubmedArticle
from datetime import datetime
from typing import List

# Note: COMMIT_THRESHOLD is somewhat arbitrary - if too small, then we will
#       create too many segment files, slowing down searches and maybe
#       creating a too many files open error when searching.
#       If too large, then we will get an index overflow error when indexing
#  I know a threshold of 10000 will create a too many files open error
#  I know that no thrsehold will cause it to crash on file 277, and each file
#       contains 30000 files
#  Therefore, I am using a threshold of 276*30000 which should be a good balance
COMMIT_THRESHOLD = 8280000


class PubmedIndexer:
    """
    PubmedIndexer is the main class that clients are expected to to use.
    The primary functions it performs are:
    1. Indexing the pubmed articles into a Whoosh index
    2. Allowing the free text searching of the pubmed articles

    NOTES:
    1. The pubmed data is provided here:
      ftp://ftp.ncbi.nlm.nih.gov/pubmed/updatefiles/
    2. We do not index all the fields per article -- we index:
      a. The pubmed ID
      b. The Journal name
      c. The Year of publication
      d. The Article title
      e. The Article Abstract
    3. The complete pubmed dataset is just under 7 GB of compressed
      XML shards (as of this writing)
    4. This module allows all this data to be indexed
    5. The index takes about 5 hours to generate on a medium powered laptop
    6. The index directly is roughly 7 GB
    7. The index directory can be tarred(zipped) and shared between users
    8. We will probably rename this module pubmed_ir soon and relase it to PyPI

    MISSING & DESIRABLE FUNCTIONALITY
    1. It would be good to have utility function that is able to download
      the pub med data
    2. We should get __init__.py, etc. files done so we can publish to PyPi
    3. We should have a partial indexing feature that indexes only data needed
       for biosqr task b
    4. We might make the index generation system more customization interms
       of things such as Analyzers, stop-words, etc.
    5. We may need a customizable result scoring function -- beyond BM25
    6. We may want a more sophisticated querying interface, boolean queries, etc
    7. We need a lot of testing to certify the system
    8. It is not clear if we can add documents to an existing index
    9. It is not clear how we can re-index an existing index
    10. We should swap out prints with a formal logging framework
    11. We should have example modules which demonstrate the use of this system
    12. We really need to modify the directory structure of the project

    BUGS & KNOWN LIMITATIONS
    1. At the moment the free text query only searches the Abstract Text
      it does not search the title

    """

    def __init__(self):
        """
        default construstor it does nothing at the moment
        """
        pass

    def mk_index(self, indexpath: str = "indexdir",
                 overwrite: bool = False) -> None:
        """
        creates a Whoosh based index for subsequent IR operatons

        Prameters
        ---------
        indexpath: str
            The absolute or relative path where you want the index to be stored
               Note: the index path is a directory
               this directory will contain all the Whoosh files
        overwrite: boolean
            This will overwrite any existing index (directory) if set to True
            The default value is set to False (safe setting)

        Returns:
        None
            it is a void method and returns the None value
        """
        use_existing_index = True
        if os.path.exists(indexpath):
            if overwrite:
                shutil.rmtree(indexpath)
                use_existing_index = False
        if not os.path.exists(indexpath):
            os.mkdir(indexpath)
            use_existing_index = False
        self.pubmed_article_schema = Schema(
            pmid=ID(stored=True),
            title=TEXT(stored=True),
            journal=TEXT(stored=True),
            mesh_major=IDLIST(stored=True),
            year=NUMERIC(stored=True),
            abstract_text=TEXT(stored=True, analyzer=StemmingAnalyzer()))
        print(use_existing_index)
        if not use_existing_index:
            self.pubmed_article_ix = index.create_in(
                indexpath,
                self.pubmed_article_schema,
                indexname="pubmed_articles")
        else:
            self.pubmed_article_ix = index.open_dir(
                indexpath, indexname="pubmed_articles")
        print("index object created")

    def rm_index(self, indexpath: str = "indexdir") -> None:
        """
        This is a utility function to delete an existing index

        Parameters
        ----------
        indexpath: str
            The absolute or relative path of the index location

        Returns
        -------
        None
            This void medhod return nothing
        """
        if os.path.exists(indexpath):
            os.rmdir(indexpath)

# This indexes on my machine at a rate of about 750 articles/second , (45,000)/min, 270k/hr
    def index_docs(self, articles: List[PubmedArticle]) -> None:
        """"
        indexes documents into the Whoosh index

        Parameters
        ----------
        articles: List[PubmedArticle]
            The list of articles to be added to the index
        
        Returns
        -------
        None:
           this is a void method an returns nothing

        TODO: add handling LockError
        TODO: add handling test for LockError
        """
        print("adding documents")
        pubmed_article_writer = self.pubmed_article_ix.writer()
        count_from_commit = 0
        total_count = 0
        for article in articles:
            count_from_commit += 1
            total_count += 1
            pubmed_article_writer.add_document(
                pmid=article.pmid,
                title=article.title,
                journal=article.journal,
                mesh_major=article.mesh_major,
                year=article.year,
                abstract_text=article.abstract_text)

            #perform intermediate commits to avoid overflow errors
            if count_from_commit > COMMIT_THRESHOLD:
                # commit and reopen the writer
                pubmed_article_writer.commit(merge=False)
                pubmed_article_writer = self.pubmed_article_ix.writer()
                count_from_commit = 0
                print ("   committing, current total_count = ", total_count)
                
        # perform the final commit
        pubmed_article_writer.commit()
        #Note: I think .commit(optimize=True) is the correct way to do this final commit
        #      but it causes the program to crash
        #      (OverflowError: 4294967519 is too big to fit in an array)
        print("commiting index, added", total_count, "documents")

    def search(self, query,
               max_results: int = 10) -> List[PubmedArticle]:
        """
        This is our simple starter method to query the index

        Parameters
        ----------
        query: str
           This is a plain text query string that Whoosh searches
           the index for matches
        max_results: int
           This parameter sets the maximum number of results the
           method will return
        """
        res = []
        qp = QueryParser("abstract_text", schema=self.pubmed_article_schema)
        q = qp.parse(query)
        with self.pubmed_article_ix.searcher() as s:
            results = s.search(q, limit=max_results)
            #PubmedIndexer.write_results(results)
            for result in results:
                pa = PubmedArticle(result['pmid'],
                                   result['title'],
                                   result['journal'],
                                   result['year'],
                                   result['abstract_text'],
                                   result['mesh_major'])
                res.append(pa)
            return res

    def print_results(results):
        """
        simple utility method to print search results to the console
        also serves as sample code to use in other modules to
        access search results
        """
        for result in results:
            print(result)

    def write_results(results):
        """
        Utility method to write results to a text file
        """
        file = open("searchResults.txt", "a", encoding="utf-8")
        for result in results:
            file.write(str(result))
            file.write("\n")
        file.close


#generates new pubmed index
def generate_new_index(index_location,db_location):
    print("now", datetime.now())
    pubmed_indexer = PubmedIndexer()
    pubmed_indexer.mk_index(indexpath=index_location,overwrite=True)
    reader = PubmedReader()
    print("now", datetime.now())
    print("starting reader")
    articles = reader.process_xml_frags(db_location)
    print("starting indexer")
    pubmed_indexer.index_docs(articles)
    print("done indexing")
    #print("now", datetime.now())
    #pubmed_indexer.search("disease")
    #print("now", datetime.now())
    #print("ran Query")
    return pubmed_indexer


def test_with_existing_index():
    print("now", datetime.now())
    pubmed_indexer = PubmedIndexer()
    pubmed_indexer.mk_index()
    pubmed_indexer.search("disease")
    print("now", datetime.now())
    print("ran Query")
    return pubmed_indexer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pubmed", help="The path where Pubmed is stored.")
    parser.add_argument("index", help="The path where the index will be saved.")

    args = parser.parse_args()
    print (f"Index Location: {args.index},Pubmed DB Location: {args.pubmed}")
    generate_new_index(args.index,args.pubmed)
