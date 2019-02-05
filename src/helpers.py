from math import pi, sqrt, acos
import datetime
import hashlib
import werkzeug
import os
import shutil
import string
import tempfile
import transaction
from sqlalchemy.exc import IntegrityError, InternalError, StatementError
import traceback
import requests
import csv

from .models import DBSession, Dbuser, Go, Referencedbentity, Keyword, Locusdbentity, FilePath, Edam, Filedbentity, FileKeyword, ReferenceFile, Disease


def tsv_file_to_dict(tsv_file):
    ''' parse file to list of dictionaries

    Paramaters
    ----------
    file: tsv_file object

    Returns
    -------
    list
        dictionary: each file row becomes a dictionary with column header
                    as keys.

    '''
    list_dictionary = []
    if (tsv_file):
        csv_obj = csv.DictReader(tsv_file, dialect='excel-tab')
        for item in csv_obj:
            list_dictionary.append(
                {k: v for k, v in item.items() if k is not None})
        return list_dictionary
    else:
        return list_dictionary


def set_string_format(str_param, char_format='_'):
    ''' format given string to replace space with underscore character

    Parameters
    ----------
    string: str_param
    string: char_format
            needs to be single character

    Returns
    -------
    string
        returns formated string or empty string if parameter str_param is not provided/empty or if char_format length is greater than 1

    '''
    if str_param and len(char_format) == 1:
        str_arr = str_param.strip().split(' ')
        temp_str = ''
        for element in str_arr:
            temp_str += element + char_format
        if temp_str.endswith(char_format):
            temp_str = temp_str[:-1]
        return temp_str
    else:
        return None


def link_gene_names(raw, locus_names_ids):
    # first create an object with display_name as key and sgdid as value
    locus_names_object = {}
    for d in locus_names_ids:
        display_name = d[0]
        sgdid = d[1]
        locus_names_object[display_name] = sgdid
    processed = raw
    words = raw.split(' ')
    for p_original_word in words:
        original_word = p_original_word.translate(None, string.punctuation)
        wupper = original_word.upper()
        if wupper in locus_names_object.keys() and len(wupper) > 3:
            sgdid = locus_names_object[wupper]
            url = '/locus/' + sgdid
            new_str = '<a href="' + url + '">' + wupper + '</a>'
            processed = processed.replace(original_word, new_str)
    return processed



def binary_search(value, f, lower, upper, e, max_iter=None):
    midpoint = lower + 1.0 * (upper - lower) / 2
    value_at_midpoint = f(midpoint)

    if max_iter is not None:
        max_iter = max_iter - 1

    if abs(value_at_midpoint - value) < e or (max_iter is not None and
                                              max_iter == 0):
        return midpoint
    elif value > value_at_midpoint:
        return binary_search(value, f, lower, midpoint, e, max_iter)
    else:
        return binary_search(value, f, midpoint, upper, e, max_iter)


def extract_topic(request):
    topic = DBSession.query(Edam).filter(
        Edam.edam_id == request.POST.get("topic_id")).one_or_none()
    if topic is None:
        log.info('Upload error: Topic ID ' + request.POST.get("topic_id") +
                 ' is not registered or is invalid.')
        raise HTTPBadRequest('Invalid or nonexistent Topic ID: ' +
                             request.POST.get("topic_id"))
    return topic


def extract_keywords(request):
    keywords = []
    if request.POST.get("keyword_ids") != '':
        keyword_ids = str(request.POST.get("keyword_ids")).split(",")
        for keyword_id in keyword_ids:
            keyword_obj = DBSession.query(Keyword).filter(
                Keyword.keyword_id == keyword_id).one_or_none()
            if keyword_obj is None:
                log.info('Upload error: invalid or nonexistent Keyword ID: ' +
                         keyword_id)
                raise HTTPBadRequest('Invalid or nonexistent Keyword ID: ' +
                                     keyword_id)
            else:
                keywords.append(keyword_obj.keyword_id)
    return keywords


def dbentity_safe_query(id, entity_class):
    attempts = 0
    dbentity = None
    while attempts < MAX_QUERY_ATTEMPTS:
        try:
            if entity_class is Locusdbentity:
                dbentity = DBSession.query(Locusdbentity).filter_by(
                    dbentity_id=id).one_or_none()
            elif entity_class is Go:
                dbentity = DBSession.query(Go).filter_by(go_id=id).one_or_none()
            elif entity_class is Disease:
                dbentity = DBSession.query(Disease).filter_by(
                    disease_id=id).one_or_none()
            break
        # close connection that has idle-in-transaction
        except InternalError:
            traceback.print_exc()
            log.info(
                'DB error corrected. Closing idle-in-transaction DB connection.'
            )
            DBSession.close()
            attempts += 1
        # rollback a connection blocked by previous invalid transaction
        except (StatementError, IntegrityError):
            traceback.print_exc()
            log.info(
                'DB error corrected. Rollingback previous error in db connection'
            )
            DBSession.rollback()
            attempts += 1
    return dbentity


def md5(fname):
    hash = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), ""):
            hash.update(chunk)
    return hash.hexdigest()
