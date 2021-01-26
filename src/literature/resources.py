""" Resource object information for Alliance data submission

The script extracts data into a dictionary that is written to a json file.
The json file is submitted to Alliance for futher processing

This file requires packages listed in requirements.txt file and env.sh file.
The env.sh file contains environment variables

01/05/2021 - initial References objects
splits into 3 files -- references.json, resources.json, resourceExchange.json
resources.json -- non-PMID articles/books/personal communications

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
DBSession.configure(bind=engine)

###########
# Reference file requirements -
# required: [
# primaryId - string,
# title - string,
# datePublished -string (date-time format),
# citation - string,
# allianceCategory - string (ENUM),
# resourceId - globalId.json
# ],
# optional --
# dateLastModified - string, date-time,
# authors - list,
# volume - string
# pages - string
# abstract - string
# keywords - array
# pubMedType - list of strings (should be directly from PubMed)
# publisher - string,
# MODReferenceTypes - list of MODReferenceType objs
# issueName - string
# tags - list of referenceTag objs
# meshTerms - list of meshDetail.json objs
# crossReferences - list of crossReference.json  
####################### 
# Resource file requirements -- 
# required:
# primaryId - string
# title: string
#
# optional:
# 
# titleSynonyms - list
# abbreviationSynonyms -- list
# isoAbbreviation - string
# medlineAbbreviation - string
# copyrightDate - string (date-time)
# publisher - string
# printISSN - string
# onlineISSN - string
# editorsOrAuthors - list of authorRefObjects
# volumes -- list
# pages - string
# abstractOrSummary -string
# crossReferences - list of crossReference objects
##############
# referenceExchange file requirements
# required: 
# PubMedId: string
# allianceCategory - "enum": ["Research Article","Review Article","Thesis","Book","Other","Preprint","Conference Publication","Personal Communication","Direct Data Submission","Internal Process Reference", "Unknown","Retraction"],
# 
# optional: 
# MODReferenceTypes
# modId
# dataLastModified - string (date-time)
# tags - list of referenceTag objects
# ################




DEFAULT_TAXID = '559292'
REFTYPE_TO_ALLIANCE_CATEGORIES ={
"Journal Article": "Research Article",#
"Review": "Review Article",#
"Thesis": "Thesis",#
"Book": "Book",#
"Other": "Other",#
"Preprint": "Preprint",#
"Clinical Conference": "Conference Publication",#
"Personal Communication in Publication": "Personal Communication",#
"Direct Submission to SGD": "Direct Data Submission",#
#"": "Internal Process Reference",
"Unknown": "Unknown",#
"Retracted Publication": "Retraction"}#

def get_resources_information(root_path):
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

##### Process references with no PMIDs ####
    resources_result = []

    print ('Processing Resources -- refs without PMIDS')
    resourceObjList = DBSession.query(Referencedbentity).filter(Referencedbentity.pmid == None).all()

    print ("computing " + str(len(resourceObjList)) + " resources (non-PMID)") 

    if (len(resourceObjList) > 0):
       # with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
      #  try:
        for resource in resourceObjList:
            print(str(resourceObjList.index(resource)) + ': reference:' + resource.sgdid)

            obj = {'primaryId': 'SGD:' + resource.sgdid,
            'title': resource.title,
            'authors': [],
            'crossReferences': [{'id': 'SGD:' + resource.sgdid, 'pages': 'reference'}]
            }

            moreResObj = resource.to_dict()
            authList = []
            
            for name in moreResObj['authors']:
               # print ('author:' + name['display_name'])
               # nameList = name['display_name'].split(' ')
                authObj = {
                    'name': name['display_name'],
                 #   'lastName': nameList[0],
                    'referenceId': 'SGD:' + resource.sgdid,
                    'authorRank': moreResObj['authors'].index(name) + 1
                }
            #    if len(nameList) > 2:
            #        authObj['middleName']: nameList[2]

                obj['authors'].append(authObj)

            if moreResObj['abstract'] is not None:
                obj['abstractOrSummary'] = moreResObj['abstract']['text']        

            resources_result.append(obj)
        

    if (len(resources_result) > 0):
        resource_output_obj = get_output(resources_result)
        resources_file = 'src/data_dump/SGD' + SUBMISSION_VERSION + 'resources.json'
        resource_file_str = os.path.join(root_path, resources_file)
        
        with open(resource_file_str, 'w+') as res_file:
            res_file.write(json.dumps(resource_output_obj))
