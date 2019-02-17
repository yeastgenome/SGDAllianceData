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
    if (content):
        for item in content:
            obj = {
                "DOid":
                    "",
                # "taxonId":
                #     "",
                "objectRelation": {
                    "associationType": "",
                    "objectType": ""
                },
                "objectId":
                    "",
                "dateAssigned":
                    "",
                "dataProvider": [{
                    "crossReference": {
                        "id": "SGD",
                        "pages": ["homepage"]
                    },
                    "type": "curated"
                }],
                "with": [],
                "evidence": {
                    "evidenceCodes": [],
                    "publication": {
                        "pubMedId": {}
                    }
                }
            }
            if (len(item) > 1):
                #import pdb ; pdb.set_trace()
                obj["DOid"] = item.get("DOID")
                obj["objectRelation"]["associationType"] = item.get(
                    "Association type")
                obj["objectRelation"]["objectType"] = item.get("DB Object type")
                obj["objectId"] = item.get("DB Object ID")
                obj["dateAssigned"] = str(
                    datetime.strptime(str(item.get("Date")), "%Y%m%d").strftime("%Y-%m-%dT%H:%m:%S-00:00"))
                obj["with"].append(item.get("with - Ortholog"))
                obj["evidence"]["evidenceCodes"] = item.get(
                    "Evidence Code").split(',')
                obj["evidence"]["publication"]["pubMedId"] = item.get(
                    "DB:Reference")
                result.append(obj)

    if len(result) > 0:
        output_obj = get_output(result)
        file_name = 'src/data_dump/SGD' + SUBMISSION_VERSION + 'disease_association.json'
        json_file_str = os.path.join(root_path, file_name)
        if (output_obj):
            with open(json_file_str, 'w+') as res_file:
                res_file.write(json.dumps(output_obj))



