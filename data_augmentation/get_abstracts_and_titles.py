import argparse
import json
import os
from lxml import etree as ET

# function to get pmids from the dataset
def get_dataset_pmids(dataset_loc):
    dataset = None
    with open(dataset_loc) as d:
        dataset = json.loads(d.read())
    questions = dataset["questions"]
    pmids = set()
    for question in questions:
        documents = question.get("documents")
        if documents:
            ids = [url.rsplit('/', 1)[-1] for url in documents]
            if ids:
                pmids.update(ids)
    return pmids

# function to get abstracts for each pmid in the dataset
def map_abstracts_to_ids(pmids, database_dir):
    pmid_abstract_dict = dict()

    #iterate through each db file
    db_files= os.listdir(database_dir)
    for db_file in db_files:
        full_path = database_dir+ "/" + db_file

        #only process .xml.gz files
        if full_path[-7:] != '.xml.gz':
            continue

        # read the pubmed file
        print(f"opening db: {full_path}")
        pm_tree = ET.parse(full_path)
        if not pm_tree:
            print(f"ERROR: failed to open pubmed file {str(db_file)}")
            return
        root = pm_tree.getroot()
        pubmed_articles = root.findall("PubmedArticle")
        for article in pubmed_articles:
            try:
                id = article.find("MedlineCitation").find("PMID").text
                if id in pmids:
                    try:
                        art_ref = article.find('MedlineCitation').find('Article')
                        abstract = art_ref.find('Abstract').find('AbstractText').text
                        title = art_ref.find('ArticleTitle').text
                        pmid_abstract_dict[id] = (title,abstract)
                    except Exception as e:
                        # no abstract for this article
                        print(f"no abstract OR title for PMID {id}")
                        print(str(e))
            except Exception as e:
                print(str(e)) 

    return pmid_abstract_dict

# function to add the found abstracts to the dataset
def add_full_abstracts(old_dataset, pmid_abstract_dict, new_dataset):
    print(f"adding full_abstracts to {old_dataset}")
    
    dataset = None
    with open(old_dataset) as d:
        dataset = json.loads(d.read())
    questions = dataset["questions"]
    n = 1
    for question in questions:
        documents = question.get("documents")
        print(f"question ({n} / {len(questions)})")
        if documents:
            ids = [url.rsplit('/', 1)[-1] for url in documents]
            title_and_full_abs = [pmid_abstract_dict[id] for id in ids if id in pmid_abstract_dict.keys()]
            titles = [ta[0] for ta in title_and_full_abs]
            full_abs = [ta[1] for ta in title_and_full_abs]
            question["full_abstracts"] = full_abs
            question["titles"] = titles
            print(f"found ({len(full_abs)} / {len(ids)}) full_abstracts for question {n}")
        n=n+1
    with open(new_dataset,'w') as outfile:
        json.dump(dataset,outfile,indent=4)
    print("Done!")

if __name__ == "__main__":

    # get arguments from the user
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_data", help="The filepath to the qa data (e.g. data/training8b.json")
    parser.add_argument("path_to_pubmed_dir", help="The filepath to the directory containing PubMed (e.g. the .xml.gz files, not the pubmed index") 

    args = parser.parse_args()
    path_to_data = args.path_to_data
    path_to_pubmed_dir = args.path_to_pubmed_dir

    pmids = get_dataset_pmids(path_to_data)
    pmids_to_abstracts = map_abstracts_to_ids(pmids, path_to_pubmed_dir)
    add_full_abstracts(path_to_data, pmids_to_abstracts, path_to_data)

