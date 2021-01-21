""" Reference object information for Alliance data submission

The script extracts data into a dictionary that is written to a json file.
The json file is submitted to Alliance for futher processing

This file requires packages listed in requirements.txt file and env.sh file.
The env.sh file contains environment variables

01/05/2021 - initial References objects
splits into 3 files -- references.json, resources.json, resourceExchange.json
references.json -- PMID articles
resources.json -- non-PMID articles/books/personal communications
refExchange.json -- all PMIDs to update? future submissions?

"""

import os
import json
import re, sys
import time
from random import randint
from datetime import datetime
from sqlalchemy import create_engine, and_, inspect
import concurrent.futures
from ..models.models import LocusAlias, Dbentity, DBSession, Straindbentity, Referencedbentity
from ..data_helpers.data_helpers import get_output, get_locus_alias_data


engine = create_engine(os.getenv('SQLALCHEMY_PROD_DB_URI'), pool_recycle=3600)
SUBMISSION_VERSION = os.getenv('SUBMISSION_VERSION', '_1.0.0.0_')
DBSession.configure(bind=engine

"""
File requirements -

   "required": [
    "primaryID" - string,
    "title" - string,
    "authors" - list,
    "datePublished" -string (date-time format),
    "citation" - string,
    "allianceCategory" - string (ENUM),
	  "resourceId" - globalId.json
  ],
    optional --
    'dateLastModified' - string, date-time
    'volume' - string
    'pages' - string
    'abstract' - string
    'keywords' - array
    'pubMedType' - list of strings (should be directly from PubMed)
    'publisher' - string,
    'MODReferenceTypes' - list of MODReferenceType objs
    'issueName' - string
    'tags' - list of referenceTag objs
    'meshTerms' - list of meshDetail.json objs
    'crossReferences' - list of crossReference.json    
"""

DEFAULT_TAXID = '559292'


def get_refs_information(root_path):
    """ Extract Reference information.

    Parameters
    ----------
    root_path
        root directory name path    

    Returns
    --------
    file
        writes data to json file

    """
    print("getting Referemces")

    referencesObjList = DBSession.query(Referencedbentity).all()

    print(("computing " + str(len(referencesObjList)) + " references"))
    #   sys.exit()
    result = []

    if (len(referencesObjList) > 0):
        # with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        try:
            for refObj in referencesObjList:
              obj = {
                "primaryID": "", #string
                "title": "", #string
                "authors": [], # list of author reference
                "datePublished": "",  #date-time string
                "citation": "",  # string
                "allianceCategory": ""  #string (ENUM),
                "resourceId": "",  #- globalId.json (SGD:XXXX),
                "dateLastModified": "",  # - string, date-time
                "volume": "",  # - string
                "pages": "",  #string
                "abstract": "",  #string
                "keywords": [],  #array
                "pubMedType": [],  # list of strings (should be directly from PubMed)
                "publisher": "",  #string,
                "MODReferenceTypes": [],  #list of MODReferenceType objs {'referenceType':"string","source":"string"}
                "issueName": "",  #string
                "tags": [],  # list of referenceTag objs
                #"meshTerms": [],  #list of meshDetail.json objs
                "crossReferences":[] # list of crossReference.json"{"id":"SGD:XXXX","pages":[list of pages from resourcedescriptor.yaml]}
              }

                
    if (len(result) > 0):
        ref_output_obj = get_output(ref_result)
        resource_output_obj = get_output(resources_result)
        refExch_obj = get_output(ref_exchange_result)

        file_name = 'src/data_dump/SGD' + SUBMISSION_VERSION + 'references.json'
        resources_file = 'src/data_dump/SGD' + SUBMISSION_VERSION + 'resources.json'
        refExch_file = 'src/data_dump/SGD' + SUBMISSION_VERSION + 'resourceExchange.json'

        json_file_str = os.path.join(root_path, file_name)
        resource_file_str = os.path.join(root_path, resources_file)
        refEx_str = os.path.join(root_path, refExch_file)
        )

        with open(json_file_str, 'w+') as res_file:
            res_file.write(json.dumps(output_obj))

        with open(resource_file_str, 'w+') as res_file:
            res_file.write(json.dumps(resource_output_obj))

        with open(refEx_str, 'w+') as res_file:
            res_file.write(json.dumps(refExch_obj))
