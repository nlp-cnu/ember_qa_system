Creates a Whoosh Index of PubMed to allow for quick access to PubMed information

1) Install Dependencies. Virtual environments are recommended:
   python3 -m venv <virtual_env_name>
   source <virtual_env_name>/bin/activate
   pip install -r requirements.txt
   
2) Download PubMed (https://pubmed.ncbi.nlm.nih.gov/download/)

   navigate to the directory where you want to save the pubmed files
   wget ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/*

   The files are .xml.gz files - you do not need to extract them

3) Run the indexer – this takes a long time, so using nohup is recommended
       python3 PubMedIndexer.py <pubmed_directory> <index_dir>
       The <pubmed_dir> is where you downloaded all of Pubmed
       The <index_dir> is where the index is saved. It will be created if it doesn’t already exist
