""" Alleles object information for Alliance data submission

The script extracts data into a dictionary that is written to a json file.
The json file is submitted to Alliance for futher processing

This file requires packages listed in requirements.txt file and env.sh file.
The env.sh file contains environment variables

09/29/20 - initial alleles objects

"""

import os
import json
import re, sys
import time
from random import randint
from datetime import datetime
from sqlalchemy import create_engine, and_, inspect
import concurrent.futures
from ..models.models import Alleledbentity, LocusAlias, Dbentity, DBSession, Straindbentity, Referencedbentity
from ..data_helpers.data_helpers import get_output, get_locus_alias_data

engine = create_engine(os.getenv('SQLALCHEMY_PROD_DB_URI'), pool_recycle=3600)
SUBMISSION_VERSION = os.getenv('SUBMISSION_VERSION', '_1.0.0.0_')
DBSession.configure(bind=engine)
"""
Allele object:
# requirements -- symbol, symbolText, taxonId, primaryId

properties": {
    "primaryId": {
      "$ref": "../globalId.json#/properties/globalId",
      "description": "The prefixed primary (MOD) ID for an entity. For internal AGR use, e.g. FB:FBgn0003301, MGI:87917."
    },
    "symbol": {
      "type": "string",
      "description": "The symbol of the entity."
    },
    "symbolText": {
      "type": "string",
      "description": "the symbol in text format, replacing all html tags with <>.  There may be more than one set of <> in the symbol."
    },
    "taxonId": {
      "$ref": "../globalId.json#/properties/globalId",
      "description": "The taxonId for the species of the genotype entity."
    },
    "synonyms": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "uniqueItems": true
    },
    "description": {
      "type": "string",
      "description":"optional free text annotation area provided for the allele by the MOD curators."
    },
    "secondaryIds": {
      "type": "array",
      "items": {
        "$ref": "../globalId.json#/properties/globalId"
      },
      "uniqueItems": true
    },
    "alleleObjectRelations": {
	  "type": "array",
	  "items": {
          {
          "title": "alleleOf",
          "type": "object",
          "description": "allele_of can only be applied when objectType is gene",
          "required": [
            "gene"
          ],
          "properties": {
            "associationType": {
              "enum": [
                "allele_of"
              ]
            },
	     "gene" : {
      "$ref": "../globalId.json#/properties/globalId",
      "description": "The single affected gene of the allele."
	     }
	  }
	}
	      "description": "An object that describes how this allele object is related to either a gene or a construct or both."
	  }
    },
    "crossReferences": {
      "type": "array",
      "items": {
        "$ref": "../crossReference.json#"
      },
      "uniqueItems": true
    }
}
  }

"""

DEFAULT_TAXID = '559292'


def get_allele_information(root_path):
    """ Extract Allele information.

    Parameters
    ----------
    root_path
        root directory name path    

    Returns
    --------
    file
        writes data to json file

     datasetSamples = DBSession.query(Datasetsample).filter(
        Datasetsample.biosample.in_(BIOSAMPLE_OBI_MAPPINGS.keys()),
        Datasetsample.dbxref_id != None).all()
    """
    print "getting Alleles"

    alleleObjList = DBSession.query(Alleledbentity).all()

    print("computing " + str(len(alleleObjList)) + " alleles")
    #   sys.exit()
    result = []

    if (len(alleleObjList) > 0):
        #with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        for alleleObj in alleleObjList:
            print "|".join(dir(alleleObj))
            obj = {}
            #"primaryID": "SGD:XXXXX",
            #    "symbol": "STRING"; symbol of the entity
            #    "symbolText": "STRING", the symbol in text format, replacing all html tags with <>.  There may be more than one set of <> in the symbol."
            #    "taxonId" ,"The taxonId for the species of the genotype entity."
            # "synonyms": LIST, strings
            # "description": free text
            # "secondaryIds": list of Ids (SGD:, etc)
            # "alleleObjectRelations": LIST of obj {
            #   "objectRelation": {"associationType":"allele_of", "gene":"SGD:XXXXX"}
            # }
            # "crossReferences": ["id":"Allele SGDID", "pages":["allele"]]
            obj["primaryID"] = "SGD:" + alleleObj.sgdid
            obj["symbolText"] = alleleObj.format_name
            obj["symbol"] = alleleObj.display_name
            obj["description"] = alleleObj.description
            obj["taxonId"] = "NCBITaxon:" + DEFAULT_TAXID
            if alleleObj.aliases:
                obj["synonyms"] = ",".join(alleleObj.aliases)

            obj["alleleObjectRelations"] = [{
                "associationType":
                "allele_of",
                "gene":
                "SGD:" + alleleObj.affected_gene.sgdid
            }]
            obj["crossReference"] = {
                "id": "SGD:" + alleleObj.sgdid,
                "pages": ["allele"]
            }

            result.append(obj)

    if (len(result) > 0):
        output_obj = get_output(result)

        file_name = 'src/data_dump/SGD' + SUBMISSION_VERSION + 'alleles.json'
        json_file_str = os.path.join(root_path, file_name)

        with open(json_file_str, 'w+') as res_file:
            res_file.write(json.dumps(output_obj))
