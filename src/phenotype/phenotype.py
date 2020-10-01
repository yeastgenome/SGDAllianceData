""" Aggregate phenotype data for Alliance data submission

The script extracts data from 1 table into a dictionary that is written to a json file.
The json file is submitted to Alliance for futher processing

This file requires packages listed in requirements.txt file and env.sh file.
The env.sh file contains environment variables

This file can be imported as a modules and contains the following functions:
    get_phenotypephenotype_data
"""
import os
import sys
import json
import concurrent.futures
from datetime import datetime
from ..models.models import Phenotypeannotation, DBSession
from ..data_helpers.data_helpers import get_output, SUBMISSION_VERSION


def get_phenotypephenotype_data(root_path):
    """ Extract phenotype data and write to file.

    Parameters
    ----------
    root_path
        root directory name path
    Returns
    -------
    file
        write Phenotype Annotation objects to json file
    """

    phenotype_data = DBSession.query(Phenotypeannotation).all()
    result = []
    print(("computing " + str(len(phenotype_data)) + " phenotypes"))
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        for item in phenotype_data:
            obj = {
                "objectId": "",
                "phenotypeTermIdentifiers": [],
                "phenotypeStatement": "",
                "dateAssigned": ""
            }
            if item.phenotype.qualifier:
                pString = item.phenotype.qualifier.display_name
                obj["phenotypeTermIdentifiers"].append({
                    "termId":
                    str(item.phenotype.qualifier.apoid),
                    "termOrder":
                    1
                })
                if item.phenotype.observable:
                    pString = pString + " " + item.phenotype.observable.display_name
                    obj["phenotypeTermIdentifiers"].append({
                        "termId":
                        str(item.phenotype.observable.apoid),
                        "termOrder":
                        2
                    })

            else:
                if item.phenotype.observable:
                    pString = item.phenotype.observable.display_name
                    obj["phenotypeTermIdentifiers"].append({
                        "termId":
                        str(item.phenotype.observable.apoid),
                        "termOrder":
                        1
                    })
            obj["objectId"] = "SGD:" + str(item.dbentity.sgdid)
            obj["phenotypeStatement"] = pString

            if item.reference.pmid:
                pubId = "PMID:" + str(item.reference.pmid)
            else:
                pubId = "SGD:" + str(item.reference.sgdid)
            obj["evidence"] = {"publicationId": pubId}
            obj["dateAssigned"] = item.date_created.strftime(
                "%Y-%m-%dT%H:%m:%S-00:00")
            result.append(obj)

        if len(result) > 0:
            output_obj = get_output(result)
            file_name = 'src/data_dump/SGD' + SUBMISSION_VERSION + 'phenotype.json'
            json_file_str = os.path.join(root_path, file_name)
            with open(json_file_str, 'w+') as res_file:
                res_file.write(json.dumps(output_obj))
