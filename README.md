# Hands-On project: Finding Zero-day vulnerabilities in Github
This repository contains all the code produced/used by our group for this assignment.
## Usage
### Setup
To use this repository make sure to first setup a virtual environment with all requirements.  
This is done with:
```
python3 -m venv .venv
```
to create the virtual environment, which you can then activate with:
```
source .venv/bin/activate
```
Once activated you can then install all requirements with:
```
pip install -r requirements.txt
```
That's the setup all done!
### Diff extraction from MoreFixes
In the `diff_extract` folder three scripts that were used to extract data from the the [MoreFixes database](https://github.com/JafarAkhondali/Morefixes) can be found. These can all be ran individually.  

The three scripts within this folder can be ran in the any order after extracting a CSV file from the MoreFixes database, which is ideally filtered based on the `score` column as indicated in the original repository. 

### Vulnerability-fix patterns
To run the scripts make sure to be in the `src` folder, do this with:
```
cd src
```
after cloning the repository. 

In this folder there are three files that are meant to be executed: `vulnerability_fix_patterns.py`, `clustering.py` and `scrapper.py`, `scrapper_init.py`.  
These scripts do the following:  

- `vulnerability_fix_patterns.py` executes our processing of the extracted jsnol file from the MoreFixes Dataset to identify some common patterns.  
- `clustering.py` computes the Kmeans of our data from `vulnerability_fix_patterns.py` and makes some plots and data files, which can all be found under the `clustering` folder  
- `scrapper.py` makes use of the method described in the paper [Eradicating the Unseen](https://dl.acm.org/doi/full/10.1145/3708821.3736220) and is a modified version of the [originial recursive scrapper](https://github.com/JafarAkhondali/DotDotDefender/blob/main/scrapper/recursive-scrapper.py) that doesn't use a database. Make sure to have files already in the `downloads` folder or this won't work. 
- `scrapper_init.py` can be used to initialize a database of files relating to a vulnerability fix that was picked. To do this make sure to set the correct path to the clustering file, `hac_clustering` is recommended as these produce better separation. This also requires a Github token to be set in the `.env` file.

To be of note is that to run the `scrapper.py` file the `.env` file needs to be setup properly as describe within the [original repository](https://github.com/JafarAkhondali/DotDotDefender), although this version only needs a github token to increase the rate limit of the API.
### Notes 
The umap package seems to not be compatible with some newer versions of python. If you encounter issues with installing umap you can either not run the clustering script or have to downgrade to python `3.13.2` or lower