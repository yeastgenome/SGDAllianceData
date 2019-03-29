""" Aggregate expression data for Alliance data submission

The script extracts data from 5 tables into a dictionary that is written to a json file.
The json file is submitted to Alliance for futher processing

This file requires packages listed in requirements.txt file and env.sh file.
The env.sh file contains environment variables

This file can be imported as a modules and contains the following functions:
    get_expression_data
"""

import os
import json
from sqlalchemy import create_engine, and_

from ..models.models import DBSession, Eco, Locusdbentity, Goannotation, GoRelation, Go, Referencedbentity
from ..data_helpers.data_helpers import get_eco_ids, get_output

from datetime import datetime
engine = create_engine(os.getenv('SQLALCHEMY_PROD_DB_URI'), pool_recycle=3600)
DBSession.configure(bind=engine)

SUBMISSION_VERSION = os.getenv('SUBMISSION_VERSION', '_1.0.0.0_')
DEFAULT_MMO = 'MMO:0000642'
CC = 'cellular component'
ECO_FORMAT_NAME_LIST = ['ECO:0000314', 'ECO:0007005',
                        'ECO:0000353']  #IDA, HDA, IPI
ANNOT_EXT_EXCLUDE_LIST = []
PARENT_GOID_TO_EXCLUDE = 'GO:0032991'

PMID_TO_MMO = {
    14562095: 'MMO:0000662',
    26928762: 'MMO:0000662',
    16823961: 'MMO:0000534',
    24769239: 'MMO:0000534',
    22842922: 'MMO:0000662',
    14576278: 'MMO:0000534',
    11914276: 'MMO:0000662',
    22932476: 'MMO:0000662',
    24390141: 'MMO:0000662',
    16622836: 'MMO:0000664',
    26777405: 'MMO:0000662',
    12150911: 'MMO:0000662',
    14690591: 'MMO:0000662',
    10684247: 'MMO:0000534',
    16702403: 'MMO:0000662',
    16407407: 'MMO:0000534',
    19053807: 'MMO:0000662',
    23212245: 'MMO:0000534',
    12068309: 'MMO:0000662',
    9448009: 'MMO:0000662',
    11983894: 'MMO:0000534',
    19040720: 'MMO:0000534',
    15282802: 'MMO:0000662',
    24868093: 'MMO:0000662',
    10449419: 'MMO:0000534',
    12392552: 'MMO:0000534',
    8915539: 'MMO:0000647',
    10377396: 'MMO:0000534'
}

go_id_to_goid = {}
goid_list = list()


# make dict from Gorelation table -- all parents to children and also all go_ids to goid
def map_parent_to_children():
    allowed_ro = ['169782', '169299']
    pterm_to_cterm = {}
    #   all_gorel = DBSession.query(GoRelation).with_entityiesfilter(
    #      GoRelation.ro_id.in_(list(allowed_ro))).distinct()

    #    print "# of gorel: " + str(len(all_gorel))
    count = 0
    gorelations = DBSession.query(GoRelation).all()

    for row in gorelations:
        #DBSession.query(Goannotation).filter_by(go_id=self.go_id).all()
        #  import pdb
        # pdb.set_trace()
        # c_goObj = DBSession.query(Go).filter(Go.go_id == row[1]).one()
        # p_goObj = DBSession.query(Go).filter(Go.go_id == row[0]).one()

        if str(row.parent.go_id) in pterm_to_cterm.keys():
            pterm_to_cterm[str(row.parent.go_id)].append(str(row.child.go_id))
            go_id_to_goid[str(row.child.go_id)] = str(row.child.goid)

            print str(count) + ":" + row.parent.goid + "-" + row.child.goid

            count = count + 1

        else:
            pterm_to_cterm[str(row.parent.go_id)] = [str(row.child.go_id)]
            go_id_to_goid[str(row.parent.go_id)] = str(row.parent.goid)
            print str(count) + ":" + row.parent.goid + "-" + row.child.goid
            count = count + 1

    print 'done mapping ' + str(count) + ' rows. Parent go ids to children'

    return (pterm_to_cterm, go_id_to_goid)


# get all children GO IDs


def all_children_ids(go_id, parent_to_children, go_id_to_go, goid_list):

    if go_id not in parent_to_children:
        print 'returning: ' + "|".join(goid_list)
        return goid_list

    for this_go_id in parent_to_children[go_id]:
        goid_list.append(go_id_to_go[this_go_id])
        print 'parent: ' + go_id_to_go[go_id] + '-> child id:' + str(
            go_id_to_go[this_go_id])
        goid_list.extend(
            all_children_ids(this_go_id, parent_to_children, go_id_to_go,
                             goid_list))


def get_expression_data(root_path):

    (term_mapping, go_id_map_dict) = map_parent_to_children()

    exclude = DBSession.query(Go).filter_by(goid=PARENT_GOID_TO_EXCLUDE).one()

    print 'go_id of parent: ' + str(exclude.go_id) + " = goid: " + str(
        exclude.goid)

    all_kids = all_children_ids(exclude.go_id, term_mapping, go_id_map_dict,
                                goid_list)

    print "|".join(all_kids)

    import pdb
    pdb.set_trace()
    """ Get gene expression
     data

    Parameters
    ----------
    root_path
        root directory name path

    Returns
    ------
    file
        writes expression data to json file
    """
    desired_eco_ids = get_eco_ids(ECO_FORMAT_NAME_LIST)
    genes = Locusdbentity.get_s288c_genes()
    result = []
    print("computing " + str(len(genes)) + " expression data points")
    dbentity_id_to_mmo = {}

    # exclude_go_parent = DBSession.query(Go).filter(
    #     Go.goid == PARENT_GOID_TO_EXCLUDE).all()

    # for parent in exclude_go_parent:
    # #     child_rel = DBSession.query(GoRelation).filter_by(
    #         parent_id=parent.go_id).all()
    #     parent_to_children[parent.go_id] = []

    #     for child in child_rel:
    #         parent_to_children[parent.go_id].append(child.go_id)
    #         go_id_to_go[child.go_id] = [child.goid, child.display_name]

    # exclude_go_list = all_children_ids(PARENT_GOID_TO_EXCLUDE,
    #                                    parent_to_children, go_id_to_go)

    #   excluded_go_list = [PARENT_GOID_TO_EXCLUDE]

    #   """   children_graph = []
    #     print "|".join(exclude_go_list)

    #     for parent in exclude_go_part:
    #         graph = parent.ontology_graph()
    #         print "GRAPH:" + "|".join(graph.keys())
    #         children_graph.append(graph)
    #  """
    #   children_relation_objs = DBSession.query(GoRelation).filter(
    #      GoRelation.parent_id.in_(parent_list)).all()
    #ontology_graph
    #  print "# of graph objs: " + str(len(children_graph))

    # for one_obj in children_graph:
    #     for child_obj in one_obj["all_children"]:
    #         print "Child GO term: " + child_obj["display_name"]
    #         exclude_go_list.append(child_obj["display_name"])

    # print 'excluded names:' + ",".join(exclude_go_list)
    # print "number of exluded GO terms:" + str(len(exclude_go_list))

    import pdb
    pdb.set_trace()

    for gene in genes:
        go_annotations = DBSession.query(Goannotation, Go).outerjoin(Go).filter(and_(\
            Goannotation.dbentity_id==gene.dbentity_id,\
            Goannotation.annotation_type != 'computational',\
            Goannotation.eco_id.in_(desired_eco_ids),\
            Go.go_namespace == CC,\
            Go.display_name != CC,\
            Go.display_name.notin_(list(exclude_go_list))\
        )).all()
        for x in go_annotations:
            annotation = x[0]
            ref_id = annotation.reference_id
            go = x[1]
            ref = DBSession.query(
                Referencedbentity.pmid, Referencedbentity.sgdid).filter(
                    Referencedbentity.dbentity_id == ref_id).one_or_none()
            pmid = ref[0]
            sgdid = ref[1]
            mmo = None
            if ref_id in dbentity_id_to_mmo.keys():
                mmo = dbentity_id_to_mmo[ref_id]
            else:
                if pmid not in PMID_TO_MMO.keys():
                    mmo = DEFAULT_MMO
                else:
                    mmo = PMID_TO_MMO[pmid]
                dbentity_id_to_mmo[ref_id] = mmo
            if pmid:
                publicationId = "PMID:" + str(pmid)
                pubSgdId = "SGD:" + sgdid
            else:
                publicationId = "SGD:" + sgdid
            obj = {
                "geneId":
                "SGD:" + str(gene.sgdid),
                "evidence": {
                    "publicationId": publicationId
                },
                "whenExpressed": {
                    "stageName": "N/A"
                },
                "whereExpressed": {
                    "whereExpressedStatement": go.display_name,
                    "cellularComponentTermId": go.format_name
                },
                "assay":
                mmo,
                "dateAssigned":
                annotation.date_created.strftime("%Y-%m-%dT%H:%m:%S-00:00")
            }
            if pubSgdId:
                obj["evidence"]["crossReference"] = sgdid
            result.append(obj)
    if (len(result) > 0):
        output_obj = get_output(result)
        file_name = 'src/data_dump/SGD' + SUBMISSION_VERSION + 'expression.json'
        json_file_str = os.path.join(root_path, file_name)
        with open(json_file_str, 'w+') as res_file:
            res_file.write(json.dumps(output_obj))
