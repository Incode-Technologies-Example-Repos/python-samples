<img src="https://incode.com/wp-content/uploads/2022/12/cropped-favicon.jpg?w=96" alt="Incode Logo" title="Incode Developer Sample | Python" align="right" height="96" width="96"/>

# Batch process two sided ID documents within a folder

This python script performs ID validation in a batch process using Incode's API.  This script iterates a single directory of ID images to find front and back sides of a document and then submits them to Incode Omni for ID validation + Goverment validation.  

Batch processing score results will be written to an excel file when processing is done.

## Prerequisites

You will need a directory of ID documents.  The IDs must follow a strict naming convention.  Documents must include a root file name and include a suffex of either 'F' or 'B'.  Each root file name must coorispond to the same document.

```florida001F.png```

Font side documents should be suffexed with 'F' and the back side documents should be suffexed with a 'B'.

__Example:__

/IDS/florida001F.png

/IDS/florida001B.png

/IDS/alabama001F.png

/IDS/alabama001B.png

/IDS/maine002F.png

/IDS/maine002B.png

## Usage

Modify these variables to point to your Incode environment 

```
BASE_URL = 'https://demo-api.incodesmile.com/omni/'
API_KEY = '<your-api-key>'
FLOW_ID = '<your-flow-id>'
DIRECTORY = '<your-folder-name>'
OUTFILE_NAME = '<your-output-filename>'
```

## Features

* Batch processing using python
* Setting API Key and Flow ID
* ID validation
* Government Validation
* Fetching Scores
* Writing Scores, Images and Interview ID to Excel

