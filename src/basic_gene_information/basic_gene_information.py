""" Aggregate basic gene information  for Alliance data submission

The script extracts data from ~8 tables into a dictionary that is written to a json file.
The json file is submitted to Alliance for futher processing

This file requires packages listed in requirements.txt file and env.sh file.
The env.sh file contains environment variables

This file can be imported as a modules and contains the following functions:
    get_expression_data
"""

import os
import json
import re
import time
from random import randint
from datetime import datetime
from sqlalchemy import create_engine, and_, inspect
import concurrent.futures
from ..models.models import LocusAlias, Dnasequenceannotation, DBSession, Eco, Locusdbentity, Goannotation, Go, Referencedbentity
from ..data_helpers.data_helpers import combine_panther_locus_data, pair_pantherid_to_sgdids, get_output, get_locus_alias_data


engine = create_engine(os.getenv('SQLALCHEMY_PROD_DB_URI'), pool_recycle=3600)
SUBMISSION_VERSION = os.getenv('SUBMISSION_VERSION', '_1.0.0.0_')
DBSession.configure(bind=engine)

"""
combine_panther_locus_list
get_panther_sgdids
Locusdbentity.get_s288c_genes
output_obj

"""


def get_basic_gene_information(root_path):
    """ Extract basic gene information.

    Parameters
    ----------
    root_path
        root directory name path    

    Returns
    --------
    file
        writes data to json file

    """

    combined_list = combine_panther_locus_data(
        pair_pantherid_to_sgdids(root_path), Locusdbentity.get_s288c_genes())
    print("computing " + str(len(combined_list)) + " genes")
    result = []
    if (len(combined_list) > 0):

        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
            for item_key in combined_list:
                obj = {
                    "crossReferences": [],
                    "primaryId":
                        "",
                    "symbol":
                        "",
                    "genomeLocations": [{
                        "startPosition": 0,
                        "chromosome": "",
                        "assembly": "R64-2-1",
                        "endPosition": 0,
                        "strand": ""
                    }],
                    "soTermId":
                        "",
                    "taxonId":
                        "NCBITaxon:559292",
                    "synonyms": [],
                    "geneSynopsis":
                        ""
                }
                item = combined_list[item_key]["locus_obj"]
                temp_itm = ["gene"]
                temp_itm.append("gene/references")
                temp_itm.append("homepage")
                if (item.has_expression):
                    temp_itm.append("gene/expression")
                    temp_itm.append("gene/spell")
                if (item.has_interaction):
                    temp_itm.append("gene/interactions")
                if (item.has_disease):
                    temp_itm.append("gene/disease")

                obj["crossReferences"].append({
                    "id": "SGD:" + item.sgdid,
                    "pages": temp_itm
                })
                item_panther = combined_list[item_key]["panther_id"]
                locus_alias_data = DBSession.query(LocusAlias).filter(
                    LocusAlias.locus_id == item.dbentity_id).all()

                if (len(locus_alias_data) > 0):
                    dna_seq_annotation_obj = DBSession.query(
                        Dnasequenceannotation).filter(
                            Dnasequenceannotation.dbentity_id == item
                            .dbentity_id,
                            Dnasequenceannotation.taxonomy_id == 274901,
                            Dnasequenceannotation.dna_type == "GENOMIC").all()

                    if (len(dna_seq_annotation_obj) > 0):
                        strnd = ""
                        if dna_seq_annotation_obj[0].strand == "0":
                            strnd = "."
                        else:
                            strnd = dna_seq_annotation_obj[0].strand
                        chromosome = dna_seq_annotation_obj[
                            0].contig.display_name.split(" ")
                        obj["genomeLocations"][0][
                            "startPosition"] = dna_seq_annotation_obj[
                                0].start_index
                        obj["genomeLocations"][0][
                            "endPosition"] = dna_seq_annotation_obj[0].end_index
                        obj["genomeLocations"][0]["strand"] = strnd
                        obj["genomeLocations"][0][
                            "startPosition"] = dna_seq_annotation_obj[
                                0].start_index
                        obj["genomeLocations"][0][
                            "chromosome"] = "chr" + chromosome[1]
                        if dna_seq_annotation_obj[0].so.so_id == 263757:
                            obj["soTermId"] = "SO:0001217"
                        else:
                            obj["soTermId"] = dna_seq_annotation_obj[0].so.soid
                    mod_locus_alias_data = get_locus_alias_data(
                        locus_alias_data, item.dbentity_id, item)

                    for mod_item in mod_locus_alias_data:
                        mod_value = mod_locus_alias_data.get(mod_item)
                        if (type(mod_value) is list):
                            if (mod_locus_alias_data.get("aliases") is
                                    not None):
                                obj["synonyms"] = mod_locus_alias_data.get(
                                    "aliases")

                        else:
                            if (mod_value.get("secondaryIds") is not None):
                                temp_sec_item = mod_value.get("secondaryIds")
                                if (len(temp_sec_item) > 0):
                                    if (item.name_description is not None):
                                        obj["name"] = item.name_description
                                    if (len(temp_sec_item) > 1):
                                        obj["secondaryIds"] = [
                                            str(x) for x in temp_sec_item
                                        ]
                                    else:
                                        if (len(temp_sec_item) == 1):
                                            obj["secondaryIds"] = [
                                                str(temp_sec_item[0])
                                            ]
                            if (mod_value.get("crossReferences") is not None):
                                temp_cross_item = mod_value.get(
                                    "crossReferences")
                                if (len(temp_cross_item) > 1):
                                    for x_ref in temp_cross_item:
                                        obj["crossReferences"].append({
                                            "id": str(x_ref)
                                        })
                                else:
                                    if (len(temp_cross_item) == 1):
                                        obj["crossReferences"].append({
                                            "id": str(temp_cross_item[0])
                                        })
                                        #obj["crossReferences"] = [str(temp_cross_item[0])]
                    if (item_panther is not None):
                        obj["crossReferences"].append({
                            "id": "PANTHER:" + item_panther
                        })
                        #obj["crossReferences"].append("PANTHER:" + item_panther)
                        obj["primaryId"] = "SGD:" + item.sgdid
                        item = combined_list[item_key]["locus_obj"]
                        obj["geneSynopsis"] = item.description
                        obj["symbol"] = item.gene_name if item.gene_name is not None else item.systematic_name
                        obj["synonyms"].append(item.systematic_name)
                        result.append(obj)

                    else:
                        obj["primaryId"] = "SGD:" + item.sgdid
                        item = combined_list[item_key]["locus_obj"]
                        obj["geneSynopsis"] = item.description
                        obj["symbol"] = item.gene_name if item.gene_name is not None else item.systematic_name
                        obj["synonyms"].append(item.systematic_name)
                        result.append(obj)
            if (len(result) > 0):
                output_obj = get_output(result)

                file_name = 'src/data_dump/SGD' + SUBMISSION_VERSION + 'basicGeneInformation.json'
                json_file_str = os.path.join(root_path, file_name)
                with open(json_file_str, 'w+') as res_file:
                    res_file.write(json.dumps(output_obj))
