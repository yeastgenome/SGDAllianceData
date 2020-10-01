""" Aggregate expression data for Alliance data submission
The script extracts data from 5 tables into a dictionary that is written to a json file.
The json file is submitted to Alliance for futher processing
This file rewuires packages listed in requirements.txt file and env.sh file.
The env.sh file contains environment variables
This file can be imported as a modules and contains the following functions:
    get_htp_metadata

1. Get all HTP samples
2. skip ones that are not RNA-seq or transcription profiling by microarray
3. make sample objects, combine all datasets they are in
3b. keep track of datasets so objects aren't repeated
4. make dataset objects, include superseries
"""
import os
import sys
import json
import re
import concurrent.futures
from datetime import datetime
"""from ..models.models import DBSession, Diseaseannotation, Diseasesupportingevidence, Dbentity
from ..data_helpers.data_helpers import get_eco_ids, get_output, SUBMISSION_VERSION """

from sqlalchemy import create_engine, and_
from ..models.models import DBSession, Dataset, DatasetKeyword, DatasetReference, Referencedbentity, Datasetsample
from ..data_helpers.data_helpers import get_eco_ids, get_output, SUBMISSION_VERSION

engine = create_engine(os.getenv('SQLALCHEMY_PROD_DB_URI'), pool_recycle=3600)
DBSession.configure(bind=engine)

##SUBMISSION_VERSION = os.getenv('SUBMISSION_VERSION', '_1.0.0.0_')
DEFAULT_MMO = 'MMO:0000642'
CC = 'cellular component'
DEFAULT_TAXID = '559292'
DEFAULT_TAG = 'unclassified'

BIOSAMPLE_OBI_MAPPINGS = {
    'total RNA extract': 'OBI:0000895',
    'polyA RNA extract': 'OBI:0000869',
    'RNA extract': 'OBI:0000880',
    'nuclear RNA extract': 'OBI:0000862',
    'extract': 'OBI:0000423',
    'cytoplasmic RNA extract': 'OBI:0000876',
    'polyA depleted RNA extract': 'OBI:0002573',
    'ribosomal RNA-depleted RNA extract': 'OBI:0002627'
}
MICROARRAY_OBI = ['OBI:0001463', 'OBI:0001235', 'OBI:0001985']

OBI_MMO_MAPPING = {
    'OBI:0001271': 'MMO:0000659',
    'OBI:0001463': 'MMO:0000648',
    'OBI:0001235': 'MMO:0000650',
    'OBI:0001985': 'MMO:0000649',
    'OBI:0001318': 'MMO:0000666'
}
CATEGORY_TAG_MAPPING = {
    "cell cycle": "cell cycle regulation",
    "response to chemical stimulus": "chemical stimulus",
    "lipid metabolism": "lipid metabolic process",
    "organelles, biogenesis, structure, and function": "subcellular component",
    "response to hypoxia": "oxygen level alteration",
    "osmotic stress": "response to osmotic stress",
    "radiation": "response to radiation",
    "starvation": "response to starvation",
    "heat shock": "response to temperature stimulus"
}
"""
CATEGORY_TAG_MAPPING = {
cell aging
amino acid metabolism
amino acid utilization
bioinformatics and computational biology
carbon utilization
cell morphogenesis
cell wall organization
cellular ion homeostasis
chromatin organization
chromosome segregation
cofactor metabolism
colony morphology
cytoskeleton and molecular motors
diauxic shift
DNA damage stimulus
environmental-sensing
evolution
fermentation
filamentous growth
flocculation
genetic interaction
genome variation
histone modification
mating
metabolism
metabolism and metabolic regulation
metal or metalloid ion stress
metal or metalloid ion utilization
mitotic cell cycle
mRNA processing
nitrogen utilization
nuclear structure and function
nucleotide metabolism
nutrient utilization
oxidative stress
phosphorus utilization
physical interaction
ploidy
prions
protein dephosphorylation
protein glycosylation
protein modification
protein phosphorylation
protein structure and folding
protein trafficking, localization and degradation
proteolysis
QTL
respiration
RNA catabolism
RNA processing and metabolism
RNA structure
signaling
sporulation
stationary phase
stationary phase entry
stationary phase maintenance
stress
sulfur utilization
synthetic biology
transcription
transcriptional regulation
transcriptome
translational regulation
transposons
ubiquitin or ULP modification
chemical stimulus
DNA replication, recombination and repair
oxygen level alteration
disease
lipid metabolic process
response to osmotic stress
response to radiation
response to starvation
response to temperature stimulus
response to unfolded protein 
}
"""

#ECO_FORMAT_NAME_LIST = ['ECO:0000314', 'ECO:0007005', 'ECO:0000353']
"""OBI TO MMO: OBI:0001271 RNA-seq assay	MMO:0000659
OBI:0001463 high throughput transcription profiling by array	MMO:0000648
OBI:0001235 high throughput transcription profiling by tiling array	MMO:0000650
OBI:0001985 high throughput transcription profiling by microarray	MMO:0000649
high throughput proteomic profiling	MMO:0000664
OBI:0001318 high throughput proteomic profiling by array	MMO:0000666
"""
"""two files need to be output. SGD_htp_datasets.json and SGD_htp_datasetSamples.json #
dataset.json object:
 { "data": [
 { "datasetId": {"primaryId":"GEO ID"}, dataset->dbxref_id
   "publication": [{"publicationId":"PMID"}], dataset->reference_dbentity_id -> pubmed
   "title": "string", dataset->display_name
   "summary":"text", dataset->description
   "numChannels": 1 or 2 (if microarray), dataset->channel_count
   "dateAssigned":"string-time", dataset->
   "datasetIds": [], (if a superset)
   "categoryTags": ["text", "text2","text3"]}], dataset_id -> dataset_keyword -> display_name
 "metaData":{}
 }    
 """

result = []


## get dataset objects and make dataset file
def get_htp_datasets(root_path):
    #    dsObjs = DBSession.query(Dataset).filter_by(
    #  assay.obiId._in(OBI_MMO_MAPPING.keys())).all()
    dsObjs = DBSession.query(Dataset).all()
    print("processing " + str(len(dsObjs)) + " datasets")
    for ds in dsObjs:
        if ds.assay.obiid not in list(OBI_MMO_MAPPING.keys()):
            continue
        if ds.dbxref_id:
            datasetObject = {
                "datasetId": {
                    "primaryId":
                    ds.dbxref_type + ":" + ds.dbxref_id,
                    "preferredCrossReference": {
                        "id": "SGD:" + ds.format_name,
                        "pages": ["htp/dataset"]
                    },
                    "crossReferences": [{
                        "id": ds.dbxref_type + ":" + ds.format_name,
                        "pages": ["htp/dataset"]
                    }]
                },
                "title": ds.display_name,
                "summary": ds.description,
                "dateAssigned":
                ds.date_public.strftime("%Y-%m-%dT%H:%m:%S-00:00")
            }
            ## publication, category Tags, add #channels if microarray expt
            # add datasetIds if it is a superset #
            if ds.assay.obiid in MICROARRAY_OBI and (ds.channel_count == 1
                                                     or ds.channel_count == 2):
                datasetObject["numChannels"] = ds.channel_count

            dsRefList = []
            #            if len(ds.references) > 1:
            #                print str(len(ds.references)) + " refs for " + ds.dbxref_id

            if ds.references:
                for ref in ds.references:
                    # print ref.reference.pmid
                    dsRefList.append(
                        {"publicationId": "PMID:" + str(ref.reference.pmid)})


#                    if len(ds.references) > 1:
#                       print "PMID: " + str(ref.reference.pmid)

                datasetObject["publications"] = dsRefList

            keywordList = []

            if ds.keywords:
                for kw in ds.keywords:
                    if kw.keyword.display_name in list(CATEGORY_TAG_MAPPING.keys(
                    )):  ##some tags need to be mapped
                        keywordList.append(
                            CATEGORY_TAG_MAPPING[kw.keyword.display_name])
                    else:
                        keywordList.append(kw.keyword.display_name)
                datasetObject["categoryTags"] = keywordList
            else:
                datasetObject["categoryTags"] = [DEFAULT_TAG]

            result.append(datasetObject)
        else:  ## skip if there is no dbxref_id ##
            continue

    if (len(result) > 0):
        output_obj = get_output(result)
        file_name = 'src/data_dump/SGD' + SUBMISSION_VERSION + 'htp_dataset.json'
        json_file_str = os.path.join(root_path, file_name)
        with open(json_file_str, 'w+') as res_file:
            res_file.write(json.dumps(output_obj))
