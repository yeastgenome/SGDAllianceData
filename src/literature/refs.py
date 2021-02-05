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

###### REFERENCES with PMIDS ###########

    print("getting References")
## change limit when ready ##
    referencesObjList = DBSession.query(Referencedbentity).filter(Referencedbentity.pmid != None).limit(10).all()

    print("computing " + str(len(referencesObjList)) + " references")
    print("start time:" + str(datetime.now()))
    
    #sys.exit()
    
    ref_result = []
    ref_exchange_result = []

### Process references with PMIDs ###
    if (len(referencesObjList) > 0):
        with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
      #  try:
            for refObj in referencesObjList:
                print(str(referencesObjList.index(refObj)) + ': reference:' + refObj.sgdid)

                newRefObj = refObj.to_dict()
 
            ## figure out if ref, resource or reference exchange
 
  #          if refObj.pmid:  ## make reference and referenceExchange files
                refExObj = {  # refexchange obj
                    "pubMedId": "PMID:" + str(newRefObj['pubmed_id']),
                    "modId": "SGD:" + refObj.sgdid
                }

                obj = { #reference obj
                    "primaryId": "SGD:" + refObj.sgdid,
                    "title": refObj.title,
                    "datePublished": str(refObj.year),
                    "citation": refObj.citation,
                    "volume": str(refObj.volume),
                    "pages": refObj.page,
                    "authors":[],
                    "crossReferences":[{'id':'SGD:'+refObj.sgdid,'pages':['reference']}]
                }
                if refObj.issue is not None:
                    obj["issueName"] = refObj.issue

                if newRefObj["abstract"] is not None:
                    obj['abstract'] = newRefObj['abstract']['text']
            

                if refObj.date_revised: # dateLastModified for refexchange & refs (opt)
                    obj['dateLastModified'] = refExObj["dateLastModified"] = refObj.date_revised.strftime("%Y-%m-%dT%H:%m:%S-00:00")
#ds.date_public.strftime("%Y-%m-%dT%H:%m:%S-00:00")

              ### alliance category for both objects (req'd) and make MODReferenceTypes (opt)               
                if 'reftypes' in newRefObj:
                    refTypesList = []
                    modRefTypeList = []

                    for eachType in newRefObj['reftypes']:
                        refTypesList.append(eachType['display_name'])
                        modRefTypeList.append({'referenceType':eachType['display_name'], 'source':'SGD'})
                    
                #print("|".join(refTypesList))
                    refExObj["MODReferenceTypes"] = modRefTypeList
                    obj["MODReferenceTypes"] = modRefTypeList

## default category - research article
                    refTypes = "|".join(refTypesList)

                    if re.search('Journal Article', refTypes):#'Journal Article' in refTypesList:
                        refExObj['allianceCategory'] = obj['allianceCategory'] = "Research Article"
                    #if len(refTypesList) == 1:
                      #  continue
                        if re.search('Review', refTypes): #'Review' in refTypesList:
                            refExObj['allianceCategory'] = obj['allianceCategory'] = "Review Article"
                       # continue
                        if re.search('Retracted Publication', refTypes): #Retracted Publication' in refTypesList:
                            refExObj['allianceCategory'] = obj['allianceCategory'] = "Retracted"
                       # continue
                        if re.search("Personal Communication in Publication", refTypes): # in refTypesList:
                            refExObj['allianceCategory'] = obj['allianceCategory'] = "Personal Communication"
                       # continue
                        if re.search("Erratum", refTypes) or re.search("Comment", refTypes): #in refTypesList or "Comment" in refTypesList:
                            refExObj['allianceCategory'] = obj['allianceCategory'] = "Other" 
                    else:
                        if 'Book' in refTypesList:
                            refExObj['allianceCategory'] = obj['allianceCategory'] = "Book"
                        if 'Thesis' in refTypesList:
                            refExObj['allianceCategory'] = obj['allianceCategory'] = "Thesis"
                        if 'Preprint' in refTypesList:
                            refExObj['allianceCategory'] = obj['allianceCategory'] = "Preprint"
                        if "Clinical Conference" in refTypesList:
                            refExObj['allianceCategory'] = obj['allianceCategory'] = "Conference Publication"
                        if "Personal Communication to SGD" in refTypesList:
                            refExObj['allianceCategory'] = obj['allianceCategory'] = "Personal Communication"
                        if "Direct Submission to SGD" in refTypesList:
                            refExObj['allianceCategory'] = obj['allianceCategory'] = "Direct Data Submission"
                        else:  # not any of the others
                            refExObj['allianceCategory'] = obj['allianceCategory'] = "Other" 
                else:
                    refExObj['allianceCategory'] = obj['allianceCategory'] = "Unknown"

#            print('category=' + refExObj['allianceCategory'])

## datePublished (req'd) - refObj.date_published || refObj.year if date_published isn't available
                if refObj.date_published:
                    obj['datePublished']= refObj.date_published #.strftime("%Y-%m-%dT%H:%m:%S-00:00")

## Authors for references##
                authorOrder = 1
                authorList = []
                for name in newRefObj['authors']:
               # nameList = name['display_name'].split(' ')
                    authObj = {
                        'name': name['display_name'],
                        'referenceId': 'SGD:' + refObj.sgdid,
                        'authorRank': newRefObj['authors'].index(name) + 1
                    }
 
                    obj['authors'].append(authObj)
## crossref for author? id: SGD:last_first, pages"["/author"] 
              #  authorOrder += 1

## journal or book publication ##
                if refObj.book:
                    obj['publisher'] = refObj.book.publisher
                    obj['resourceAbbreviation'] = refObj.book.title
                elif refObj.journal:
                    obj['publisher'] = refObj.journal.title
                    obj['resourceAbbreviation'] = refObj.journal.med_abbr    

## crossReferences for reference.json file #
              # refObj.pmid, refObj.pmcid refObj.doi
                if refObj.pmcid:
                    obj['crossReferences'].append({'id': 'PMCID:' + refObj.pmcid, 'pages': []})

                if refObj.doi:
                    obj['crossReferences'].append({'id': 'DOI:' + refObj.doi, 'pages': ['DOI']})
                if refObj.pmid:
                    obj['crossReferences'].append({'id': 'PMID:' + str(refObj.pmid), 'pages': ['PubMed']})
            
#            print("obj:" + "*".join(obj.keys()))
#            print('refex:' + "|".join(refExObj.keys()))
 
        ## ADD TO ref_result and ref_exchange_result
 #           print(obj)
 #           print(refExObj)

                ref_result.append(obj)
                ref_exchange_result.append(refExObj)
        
#        print(str(len(ref_result)))
#        print(str(len(ref_exchange_result)))
  
    if (len(ref_result) > 0):
        ref_output_obj = get_output(ref_result)
        file_name = 'src/data_dump/SGD' + SUBMISSION_VERSION + 'references.json'
        json_file_str = os.path.join(root_path, file_name)
        
        with open(json_file_str, 'w+') as res_file:
            res_file.write(json.dumps(ref_output_obj))
    
    if (len(ref_exchange_result) > 0):
        refExch_obj = get_output(ref_exchange_result)
        refExch_file = 'src/data_dump/SGD' + SUBMISSION_VERSION + 'referenceExchange.json'
        refEx_str = os.path.join(root_path, refExch_file)

        with open(refEx_str, 'w+') as res_file:
            res_file.write(json.dumps(refExch_obj))
    
 
