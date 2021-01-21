""" Aggregate phenotype data for Alliance data submission

The script extracts data from 1 table into a dictionary that is written to a json file.
The json file is 
submitted to Alliance for futher processing

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
from ..models.models import Phenotypeannotation, PhenotypeannotationCond, Chebi, DBSession
from ..data_helpers.data_helpers import get_output, SUBMISSION_VERSION

COND_TO_ZECO = {"treatment": "ZECO:0000105", #biological treatment
"radiation":"ZECO:0000208", #radiation
"chemical":"ZECO:0000111", #chemical treatment
"assay":"ZECO:0000104", #experimental conditions
"media": "ZECO:0000238",  #chemical treatment by environment
"temperature":"ZECO:0000160", #temperature exposure
"phase": "ZECO:0000104"}  #experimental conditions

#ECO_ID_TO_TERM = {
#    "ZECO:0000105":"biological treatment",
#"ZECO:0000208":"radiation",
#"ZECO:0000111", #chemical treatment
#"ZECO:0000104", #experimental conditions
##"ZECO:0000238",  #chemical treatment by environment
#"ZECO:0000160", #temperature exposure
#}""" 

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
            if item.allele:  #make allele object if there is an allele associated with a phenotype #
                alleleObj = {
                "objectId": "",
                "phenotypeTermIdentifiers": [],
                "phenotypeStatement": "",
                "dateAssigned": ""
                }
            ## Check for conditions ##
            conditionObjs = DBSession.query(PhenotypeannotationCond).filter(PhenotypeannotationCond.annotation_id==item.annotation_id).all()
            
            if conditionObjs:
                conditionList = []
                for cond in conditionObjs:
                    cObj = {"conditionClassId": COND_TO_ZECO[cond.condition_class]}
                    
                    cObj["conditionStatement"] = cond.condition_class + ":" + cond.condition_name
                   # print(cond.condition_class + ":" + cond.condition_name)

                    if cond.condition_value and cond.condition_unit:
                        cObj["conditionQuantity"] = cond.condition_value + " " + cond.condition_unit

                    if cond.condition_class == 'chemical':  # get ChEBI ID
                       # print(cond.condition_name)
                        chebiObj = DBSession.query(Chebi).filter_by(display_name = cond.condition_name, is_obsolete='false').one_or_none()
                        #print(chebiObj)
                        cObj["ChemicalOntologyId"] = chebiObj.format_name

                    conditionList.append(cObj)   
                #print('has ' + "*".join(conditions.keys()) + " " + "|".join(conditions.values()))
                obj["conditionRelations"] = conditionList 
                
            if item.phenotype.qualifier:
                pString = item.phenotype.qualifier.display_name
                obj["phenotypeTermIdentifiers"].append({
                    "termId":
                    str(item.phenotype.qualifier.apoid),
                    "termOrder":
                    1
                })
                if item.allele: #add phenotype to allele obj
                    alleleObj["phenotypeTermIdentifiers"].append({
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
                    if item.allele: # adding observable to allele pheno obj
                        alleleObj["phenotypeTermIdentifiers"].append({
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
                    if item.allele: # adding only observable to allele pheno obj
                        alleleObj["phenotypeTermIdentifiers"].append({
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
            
            if item.allele:
               # add allele SGDID to gene-level phenotype; ADD STRAIN_BACKGROUND-- NCBI TaxonID? if NOT 'OTHER' 
                obj["primaryGeneticEntityIDs"] = ["SGD:" + item.allele.sgdid]

                # adding basic info to allele obj #
                alleleObj["objectId"] = "SGD:" + item.allele.sgdid
                alleleObj["phenotypeStatement"] = pString
                alleleObj["evidence"] = {"publicationId": pubId}
                alleleObj["dateAssigned"] = item.date_created.strftime(
                "%Y-%m-%dT%H:%m:%S-00:00") 

            result.append(obj)

            if item.allele: # adding allele level phenotype if it exists
                result.append(alleleObj)
          #  else:
          #      print("no allele for " + item.dbentity.display_name + " pheno:" + pString)
        if len(result) > 0:
            output_obj = get_output(result)
            file_name = 'src/data_dump/SGD' + SUBMISSION_VERSION + 'phenotype.json'
            json_file_str = os.path.join(root_path, file_name)
            with open(json_file_str, 'w+') as res_file:
                res_file.write(json.dumps(output_obj))
