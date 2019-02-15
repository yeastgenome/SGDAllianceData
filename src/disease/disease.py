""" Aggregate disease data for Alliance data submission

The script extracts data from ajson file into a dictionary that is written to another json file.
The json file is submitted to Alliance for futher processing

This file requires packages listed in requirements.txt file and env.sh file.
The env.sh file contains environment variables

This file can be imported as a modules and contains the following functions:
    get_disease_association_data
"""
import os
import sys
import json
import concurrent.futures
from datetime import datetime
from ..models.models import Phenotypeannotation, DBSession
from ..data_helpers.data_helpers import get_output, SUBMISSION_VERSION

def get_disease_association_data(root_path):
    result = []
    file_name = 'src/data_assets/disease_association.json'
    json_file_str = os.path.join(root_path, file_name)
    with open(json_file_str) as data_file:
        content = json.load(data_file)
    if(content):
        for item in content:
            obj = {
                "DOid":
                    "",
                "taxonId":
                    "",
                "objectRelation": {
                    "associationType": "",
                    "objectType": ""
                },
                "objectId":
                    "",
                "dateAssigned":
                    "",
                "dataProvider":
                    "SGD",
                "with": [],
                "evidence": [{
                    "evidenceCode": "",
                    "publications": {
                        "pubMedId": ""
                    }
                }]
            }
            if(len(item) > 1):
                #import pdb ; pdb.set_trace()
                obj["DOid"] = item.get("DOID")
                obj["taxonId"] = item.get("Taxon")
                obj["objectRelation"]["associationType"] = item.get("Association type")
                obj["objectRelation"]["objectType"] = item.get("DB Object type")
                obj["objectId"] = item.get("DB Object ID")
                obj["dateAssigned"] = str(
                    datetime.strptime(str(item.get("Date")), "%Y%m%d").isoformat())
                obj["dataProvider"] = item.get("Assigned By")
                obj["with"].append(item.get("with - Ortholog"))
                obj["evidence"][0]["evidenceCode"] = item.get("Evidence Code")
                obj["evidence"][0]["publications"]["pubMedId"] = item.get("DB:Reference")
                result.append(obj)

    if len(result) > 0:
        output_obj = get_output(result)
        file_name = 'src/data_dump/SGD' + SUBMISSION_VERSION + 'disease_association.json'
        json_file_str = os.path.join(root_path, file_name)
        if(output_obj):
            with open(json_file_str, 'w+') as res_file:
                res_file.write(json.dumps(output_obj))

'''
DOid = 
obj["DOid"] = item[6]
obj["taxonId"] = item[0]
obj["objectRelation"]["associationType"] = item[5]
obj["objectRelation"]["objectType"] = item[1]
obj["objectId"] = item[2]
obj["dateAssigned"] = str(
    datetime.strptime(str(item[10]), "%Y%m%d").isoformat())
obj["dataProvider"] = item[11]
obj["with"].append(item[7])
pdb.set_trace()
obj["evidence"][0]["evidenceCode"] = item[8]
obj["evidence"][0]["publications"]["pubMedId"]["PMID"] = item[9]
'''
