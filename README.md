# ember_qa_system
I can just run qa_system.py and it will automatically create everything for me
python3 qa_system.py -i <path_to_qu input, which is a csv of questions> -E -g(or something) <path to gold>

How to recreate the QA system:

1.	Create a virtual environment and install all dependencies
a.	python3 -m venv <venv_dir>
b.	source <venv_dir>/bin/activate
c.	pip install -r requirements.txt

2.	Create an Index of PubMed. This is used for augmenting the dataset and within the document processing component.
a.	Download PubMed (https://pubmed.ncbi.nlm.nih.gov/download/)
i.	These files can be downloaded by:
•	Navigate to the directory where you want to save the pubmed files
•	wget ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/*
ii.	The files are .xml.gz files. You do not need to extract them

b.	Run the indexer – this takes a long time, so using nohup is recommended
i.	python3 PubMedIndexer.py <pubmed_directory> <index_dir>
The <pubmed_dir> is where you downloaded all of PubMed
•	The <index_dir> is where the index is saved. It will be created if it doesn’t already exist
ii.	The created index will consist of one or more .seg files and a .toc file

3.	 Augment the BioASQ Dataset:  
a.	Acquire the BioASQ task b dataset. 
i.	Create an account on http://bioasq.org/ and log in
ii.	Download data from http://participants-area.bioasq.org/datasets/ 
•	For example, “Training 9b” and “9b golden enriched”
iii.	Extract the downloaded .zip files. e.g.:
unzip BioASQ-training9b.zip
iv.	The test set is distributed as 5 separate files. Combine them all into a single test set by running:
python3 data_augmentation/combine_jsons.py <path to dir with multiple jsons> <output_file_name>

b.	Augment the dataset with “human_concepts”. This will map the “concepts” which are URLs to MeSH IDs, then extract an English term for that concept
i.	This requires the MRCONSO.RRF of the UMLS
•	Navigate to: https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html
•	Select the MRCONSO.RRF link (we used the 2022AA version)
•	Sign in or create an account – your download should automatically begin
•	Extract the downloaded .zip file. e.g.:
unzip umls-2022AA-mrconso.zip 

ii.	Run get_human_concepts.py
•	python3 get_human_concepts.py <path to bioasq .json> <path_to_MRCONSO.RRF >
•	This will take a long time to run, once complete, it will add a “human_concepts” field to the .json file containing the data
•	Note: Later versions of BioASQ do not provide gold standard human concepts. Questions without any “concepts” field will be skipped, and no human concepts will be added. Furthermore, whole files may not contain any “concepts”, as is the case with the BioASQ 9b test set, and presumably test sets in the future.

c.	Augment the dataset with “titles” and “abstracts”
i.	This requires a PubMed Index (step 1)
ii.	Run get_titles_and_abstracts.py
•	python3 get_abstracts_and_titles.py <path to bioasq .json> <path to PubMed Dir>
•	The path to PubMed is the directory where you downloaded pubmed to
•	This will take a long time to run, once complete, it will add a “titles” and “full_abstracts” to the .json file containing the data

4.	Run the QA system

Note: There is currently a problem loading the QU model. I think this is a dependency issue. We need to rewrite that module.

