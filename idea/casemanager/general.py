from ..core.globaltools import get_var_name_str
from ..internet.crawlers import crawler
from .defaults_manager import DEFAULT_SET, DEFAULT_CASE_NAME, set_default_case, get_default_case_name, get_default_case, is_default_case, check_default_case, remove_default_case, update_default_case
from .backups_manager import Backups, get_backups, BACKUPS
from .case import Case
from .items import CaseItem, CaseItemSet, url_to_item_id
from .projects import Project

import sys
import os

import numpy as np 
import pandas as pd

def new_blank_case(name = 'request_input', project = None, make_default = True):
    
    """
    Creates a new, blank Case object.
        
    Parameters
    ----------
    name : str
        name for Case. This is intended to be the same string as the Case's variable name.
    project : str
        name of Project object Case will be an attribute of. Defaults to None.
    make_default : bool
        whether to set the Case as the default case in the environment. 
    """
    
    if name == 'request_input':
        name = input('Case name: ')
    
    globals()[name] = Case(case_name = name, project = project, make_default = make_default, parse = False, keywords = False, coincidences = False, indexes = False, networks = False, analytics = False)
    
    globals()[name].create_new_backup()
    
    globals()[name].backup()
    
    return globals()[name]


def crawl_res_to_case_obj(crawl_df, case_name):
    
    """
    Creates a Case object from the results of a web crawl.
        
    Parameters
    ----------
    crawl_df : pandas.DataFrame
        web crawl result.
    case_name : str
        name for Case. This is intended to be the same string as the Case's variable name.
    """
    
    case = Case(case_name = case_name)
    case.dataframes.metadata = case.dataframes.metadata.astype(object)
    case.dataframes.data = case.dataframes.data.astype(object)
    case.dataframes.other = case.dataframes.other.astype(object)
    
    
    df = crawl_df.copy(deep=True).astype(object)
    
    urls = list(df.index)
    for url in urls:
        
        item_id = url_to_item_id(url)
        
        items_set = set(
                            list(case.dataframes.metadata.index) 
                            + list(case.dataframes.data.index) 
                            + list(case.dataframes.other.index)
                            )
        if item_id in items_set:
            count = len([i for i in items_set if (i == item_id)])
            item_id = item_id + '_' + str(count+1)
        
        case.dataframes.metadata.loc[item_id] = pd.Series(dtype=object)
        case.dataframes.metadata.loc[item_id, 'name'] = df.loc[url, 'title']
        case.dataframes.metadata.loc[item_id, 'data_id'] = df.loc[url].name
        case.dataframes.metadata.loc[item_id, 'unique_id'] = df.loc[url, 'fingerprint']
        case.dataframes.metadata.loc[item_id, 'description'] = df.loc[url, 'description']
        case.dataframes.metadata.loc[item_id, 'type'] = df.loc[url, 'pagetype']
        case.dataframes.metadata.loc[item_id, 'format'] = 'html'
        case.dataframes.metadata.loc[item_id, 'source'] = df.loc[url, 'source']
        case.dataframes.metadata.loc[item_id, 'domain'] = df.loc[url, 'hostname']
        case.dataframes.metadata.loc[item_id, 'url'] = df.loc[url, 'url']
        case.dataframes.metadata.loc[item_id, 'created_by'] = df.loc[url, 'author']
        case.dataframes.metadata.loc[item_id, 'last_changed_at'] = df.loc[url, 'date']
        case.dataframes.metadata.loc[item_id, 'language'] = df.loc[url, 'language']
        case.dataframes.metadata = case.dataframes.metadata.replace(np.nan, None)
        
        case.dataframes.data.loc[item_id] = pd.Series(dtype=object)
        case.dataframes.data.loc[item_id, 'html'] = df.loc[url, 'html']
        case.dataframes.data.loc[item_id, 'text'] = df.loc[url, 'raw_text']
        case.dataframes.data.loc[item_id, 'image'] = df.loc[url, 'image']
        case.dataframes.data = case.dataframes.data.replace(np.nan, None)
        
        case.dataframes.other.loc[item_id] = pd.Series(dtype=object)
        case.dataframes.other.at[item_id, 'links'] = df.loc[url, 'links']
        case.dataframes.other = case.dataframes.other.replace(np.nan, None)
    
    case.update_items_from_dataframes()
    case.dataframes.update_properties()
    case.items.update_properties()
    case.update_properties()
    
    return case
    
    
def case_from_web_crawl(case_name = 'request_input',
                        make_global_var = True,
                        seed_urls = 'request_input',
                        visit_limit = 5, 
                        excluded_url_terms = 'default',
                        required_keywords = None, 
                        excluded_keywords = None, 
                        case_sensitive = False,
                        ignore_urls = None, 
                        ignore_domains = 'default',
                        be_polite = True,
                        full = True
                        ):
    
    
    """
    Crawls internet from a single URL or list of URLs and returns a Case object.
    
    Parameters
    ---------- 
    case_name : str
        name for Case. This is intended to be the same string as the Case's variable name.
    seed_urls : str or list
        one or more URLs from which to crawl.
    visit_limit : int
        how many URLs the crawler should visit before it stops.
    excluded_url_terms : list
        list of strings; link will be ignored if it contains any string in list.
    required_keywords : list
        list of keywords which sites must contain to be crawled.
    excluded_keywords : list
        list of keywords which sites must *not* contain to be crawled.
    case_sensitive : bool
        whether or not to ignore string characters' case.
    ignore_urls : list
        list of URLs to ignore.
    ignore_domains : list
        list of domains to ignore.
    be_polite : bool
        whether respect websites' permissions for crawlers.
    full : bool
        whether to run a full scrape on each site. This takes longer.
    
    Returns
    -------
    result : object
        an object containing the results of a crawl.
    """
    
    if case_name == 'request_input':
        case_name = input('Case name: ')
    
    crawl_df = crawler(
                    seed_urls = seed_urls,
                    visit_limit = visit_limit, 
                    excluded_url_terms = excluded_url_terms,
                    required_keywords = required_keywords, 
                    excluded_keywords = excluded_keywords, 
                    case_sensitive = case_sensitive,
                    ignore_urls = ignore_urls, 
                    ignore_domains = ignore_domains,
                    be_polite = be_polite,
                    full = full,
                    output_as = 'dataframe'
                    )
    
    case = crawl_res_to_case_obj(crawl_df = crawl_df, case_name = case_name)
    
    if make_global_var == True:
        globals()[case_name] = case
    
    return case


    
def crawl_res_to_case_items(crawl_df, case):
    
    """
    Creates a CaseItemSet object from the results of a web crawl and adds to a Case.
        
    Parameters
    ----------
    crawl_df : pandas.DataFrame
        web crawl result.
    case  : Case
        Case to add results to.
    """
    
    case_obj = copy.deepcopy(case)
    df = crawl_df.copy(deep=True).astype(object)
    
    urls = list(df.index)
    for url in urls:
        
        item_id = url_to_item_id(url)
        
        items_set = set(
                            list(case_obj.dataframes.metadata.index) 
                            + list(case_obj.dataframes.data.index) 
                            + list(case_obj.dataframes.other.index)
                            )
        if item_id in items_set:
            count = len(
                [
                    i for i in items_set if (i == item_id)
                ]
                )
            item_id = item_id + '_' + str(count+1)
        
        print(item_id)
        
        case_obj.dataframes.metadata.loc[item_id] = pd.Series(dtype=object)
        case_obj.dataframes.metadata.loc[item_id, 'name'] = df.loc[url, 'title']
        case_obj.dataframes.metadata.loc[item_id, 'data_id'] = df.loc[url].name
        case_obj.dataframes.metadata.loc[item_id, 'unique_id'] = df.loc[url, 'fingerprint']
        case_obj.dataframes.metadata.loc[item_id, 'description'] = df.loc[url, 'description']
        case_obj.dataframes.metadata.loc[item_id, 'type'] = df.loc[url, 'pagetype']
        case_obj.dataframes.metadata.loc[item_id, 'format'] = 'html'
        case_obj.dataframes.metadata.loc[item_id, 'source'] = df.loc[url, 'source']
        case_obj.dataframes.metadata.loc[item_id, 'domain'] = df.loc[url, 'hostname']
        case_obj.dataframes.metadata.loc[item_id, 'url'] = df.loc[url, 'url']
        case_obj.dataframes.metadata.loc[item_id, 'created_by'] = df.loc[url, 'author']
        case_obj.dataframes.metadata.loc[item_id, 'last_changed_at'] = df.loc[url, 'date']
        case_obj.dataframes.metadata.loc[item_id, 'language'] = df.loc[url, 'language']
        case_obj.dataframes.metadata = case_obj.dataframes.metadata.replace(np.nan, None)
        
        case_obj.dataframes.data.loc[item_id] = pd.Series(dtype=object)
        case_obj.dataframes.data.loc[item_id, 'html'] = df.loc[url, 'html']
        case_obj.dataframes.data.loc[item_id, 'text'] = df.loc[url, 'raw_text']
        case_obj.dataframes.data.loc[item_id, 'image'] = df.loc[url, 'image']
        case_obj.dataframes.data = case_obj.dataframes.data.replace(np.nan, None)
        
        case_obj.dataframes.other.loc[item_id] = pd.Series(dtype=object)
        case_obj.dataframes.other.at[item_id, 'links'] = df.loc[url, 'links']
        case_obj.dataframes.other = case_obj.dataframes.other.replace(np.nan, None)
    
    case_obj.update_items_from_dataframes()
    case_obj.dataframes.update_properties()
    case_obj.items.update_properties()
    case_obj.update_properties()
    
    return case_obj


def items_from_web_crawl(case = 'default_case',
                        update_global_var = True,
                        seed_urls = 'request_input',
                        visit_limit = 2, 
                        excluded_url_terms = 'default',
                        required_keywords = None, 
                        excluded_keywords = None, 
                        case_sensitive = False,
                        ignore_urls = None, 
                        ignore_domains = 'default',
                        be_polite = True,
                        full = True,
                        output_as = 'dataframe'
                        ):
    
    """
    Crawls internet from a single URL or list of URLs and adds to an existing Case object.
    
    Parameters
    ---------- 
    case  : str 
        name of Case to add results to.
    seed_urls : str or list 
        one or more URLs from which to crawl.
    visit_limit : int 
        how many URLs the crawler should visit before it stops.
    excluded_url_terms : list 
        list of strings. The link will be ignored if it contains any string in list.
    required_keywords : list 
        list of keywords which sites must contain to be crawled.
    excluded_keywords : list 
        list of keywords which sites must *not* contain to be crawled.
    case_sensitive : bool 
        whether or not to ignore string characters' case.
    ignore_urls : list 
        list of URLs to ignore.
    ignore_domains : list 
        list of domains to ignore.
    be_polite : bool 
        whether respect websites' permissions for crawlers.
    full : bool 
        whether to run a full scrape on each site. This takes longer.
    
    Returns
    -------
    result : object 
        an object containing the results of a crawl.
    """
    
    if case == 'default_case':
        case = get_default_case()
    
    crawl_df = crawler(
                    seed_urls = seed_urls,
                    visit_limit = visit_limit, 
                    excluded_url_terms = excluded_url_terms,
                    required_keywords = required_keywords, 
                    excluded_keywords = excluded_keywords, 
                    case_sensitive = case_sensitive,
                    ignore_urls = ignore_urls, 
                    ignore_domains = ignore_domains,
                    be_polite = be_polite,
                    full = full,
                    output_as = output_as
                    )
    
    udpated_case = crawl_res_to_case_items(crawl_df = crawl_df, case = case)
    
    if update_global_var == True:
        case_name = get_var_name_str(case)
        globals()[case_name] = udpated_case
    
    return udpated_case

## Functions for importing data and files

def clean_metadata_import(metadata_import):
    
    """
    Cleans imported metadata dataframe.
    """
    
    if type(metadata_import) != pd.DataFrame:
        raise TypeError('Metadata import must be of type "DataFrame"')
    
    for column in metadata_import.columns:
        metadata_import[column] = metadata_import[column].apply(empty_to_none)
        metadata_import[column] = metadata_import[column].astype(str)
        metadata_import[column] = metadata_import[column].str.lower().str.strip()
        metadata_import[column] = metadata_import[column].replace('none', None).replace('None', None)
        metadata_import[column] = metadata_import[column].apply(series_none_list_to_empty_lists)
    
    metadata_import['created_at'] = metadata_import['created_at'].apply(series_to_datetimes).astype(object).where(metadata_import.created_at.notnull(), None)
    metadata_import['last_changed_at'] = metadata_import['last_changed_at'].apply(series_to_datetimes).astype(object).where(metadata_import.last_changed_at.notnull(), None)
    metadata_import['uploaded_at'] = metadata_import['uploaded_at'].apply(series_to_datetimes).astype(object).where(metadata_import.uploaded_at.notnull(), None)
    
    return metadata_import
    

def clean_info_import(info_import):
    
    """
    Cleans imported information dataframe.
    """
    
    if type(info_import) != pd.DataFrame:
        raise TypeError('Information import must be of type "pd.DataFrame"')
    
    for column in info_import.columns:
        
        info_import[column] = info_import[column].apply(empty_to_none)
        
        if info_import[column].dtype == '<M8[ns]':
            info_import[column] = info_import[column].astype(str).str.replace('timestamp', '', regex = False)
            if ';' in str(info_import[column]):
                info_import[column] = info_import[column].apply(text_splitter, args = (';'))
            else:
                info_import[column] = info_import[column].apply(text_splitter, args = (','))
            
            info_import[column] = info_import[column].apply(list_to_datetimes)
#             info_import[column] = info_import[column].where(info_import.date_times.notnull(), None)
            info_import[column] = info_import[column].apply(nat_list_to_nones_list)
            
        else:
            info_import[column] = info_import[column].astype(str)
            info_import[column] = info_import[column].str.lower().str.strip()
            info_import[column] = info_import[column].str.replace('?', '', regex = False).str.replace("'", "", regex = False).str.replace('[', '', regex = False).str.replace(']', '', regex = False).str.replace('(', '', regex = False).str.replace(')', '', regex = False).str.replace('timestamp', '', regex = False)

            if "'," in str(info_import[column]):
                info_import[column] = info_import[column].str.replace("'", '', regex = False)
            elif '",' in str(info_import[column]):
                info_import[column] = info_import[column].str.replace('"', '', regex = False)

            if ';' in str(info_import[column]):
                info_import[column] = info_import[column].apply(text_splitter, args = (';'))
            else:
                info_import[column] = info_import[column].apply(text_splitter, args = (','))
                                                            
        info_import[column] = info_import[column].replace('[None]', None).replace('[none]', None).replace('None', None).replace('none', None).replace('NaT', None)
        info_import[column] = info_import[column].apply(series_none_list_to_empty_lists)
    
    info_import['date_times'] = info_import['date_times'].apply(series_to_datetimes).astype(object).where(info_import.date_times.notnull(), None)
    
    return info_import

def clean_other_import(other_import):
    
    """
    Cleans imported 'other' dataframe (links, references, and contents).
    """
    
    if type(other_import) != pd.DataFrame:
        raise TypeError('Other import must be of type "pd.DataFrame"')
    
    other_import = other_import.astype(object)
    
    list_cols = ['links', 'references', 'contents']
    
    for col in other_import.columns:
        
        other_import[col] = other_import[col].str.lower()
        
        if col in list_cols:
            other_import[col] = other_import[col].astype(object)
            other_import[col] = correct_series_of_lists(other_import[col])
    
    other_import = other_import.astype(object)
    
    return other_import
    
    
def item_from_data_import(data_import, item_id):
    
    """
    Takes imported data dataframe and returns an item.
    """
    
    if type(data_import) != pd.DataFrame:
        raise TypeError('Data import must be of type "pd.DataFrame"')
    
    if item_id in data_import.index:
            
            input_data = data_import.loc[item_id]
            data_df = pd.DataFrame(columns = ['Datatype', 'Format', 'Stored as', 'Size (bytes)', 'Raw data', 'Parsed data'])
            
            index = 0
            for col in input_data.index:
                if input_data[index] != None:
                    
                    data_df.loc[index, 'Raw data'] = input_data[index]
                    data_df.loc[index, 'Datatype'] = col
                    data_df.loc[index, 'Stored as'] = type(input_data[index])
                    size = sys.getsizeof(input_data[index])
                    data_df.loc[index, 'Size (bytes)'] = size
                    
                    if (data_df.loc[index, 'Datatype'] == 'text') or ('word' in data_df.loc[index, 'Datatype']):
                        data_df.loc[index, 'Format'] = 'txt'
                    
                    if ('html' in data_df.loc[index, 'Datatype']) or (data_df.loc[index, 'Datatype'] == 'web code'):
                        data_df.loc[index, 'Format'] = 'html'
                    
                index += 1  
            
            data_df = data_df.replace(np.nan, None)
            
            return data_df

def item_from_metadata_import(metadata_import, item_id):
    
    """
    Takes imported metadata dataframe and returns an item.
    """
    
    if type(metadata_import) != pd.DataFrame:
        raise TypeError('Metadata import must be of type "pd.DataFrame"')
    
    metadata_df = pd.DataFrame(columns = ['Metadata', 'Category'])
    if item_id in metadata_import.index:
        
            input_metadata = metadata_import.loc[item_id]

            for index in input_metadata.index:
                item = input_metadata[index]
                new_row = {'Metadata': item, 'Category': index}
                metadata_df.at[len(metadata_df)] = new_row


            metadata_df['Metadata'] = metadata_df['Metadata'].replace('None', None).replace('none', None)
            metadata_df['Category'] = metadata_df['Category'].replace('None', None).replace('none', None)

    else:
            
            metadata_import.append(pd.DataFrame(index=[item_id],columns=metadata_import.columns))
        
    return metadata_df

def item_from_info_import(info_import, item_id):
    
    """
    Takes imported information dataframe and returns an item.
    """
    
    if type(info_import) != pd.DataFrame:
        raise TypeError('Information import must be of type "pd.DataFrame"')
    
    info_df = pd.DataFrame(columns = ['Label', 'Category'])
    if item_id in info_import.index:
        
            input_info = info_import.loc[item_id]

            for index in input_info.index:
                if input_info[index] != None:
                    for item in input_info[index]:
                        if (item != 'none') and (item != None):
                            new_row = {'Label': item, 'Category': index}
                            info_df.loc[len(info_df)] = new_row


            info_df['Label'] = info_df['Label'].replace('None', None).replace('none', None)
            info_df['Category'] = info_df['Category'].replace('None', None).replace('none', None)

    else:
            
            info_import.append(pd.DataFrame(index=[item_id],columns=info_import.columns))
        
    return info_df

def item_from_other_import(other_import, case_name, item_id):
    
    """
    Takes imported 'other' dataframe (links, references, and contents) and returns an item.
    """
    
    if type(other_import) != pd.DataFrame:
        raise TypeError('"Other" import must be of type "pd.DataFrame"')
    
    if item_id in other_import.index:
            
            globals()[case_name].items.get_item(item_id).links = other_import.loc[item_id, 'links']
            globals()[case_name].items.get_item(item_id).references = other_import.loc[item_id, 'references']
            globals()[case_name].items.get_item(item_id).contains = other_import.loc[item_id, 'contents']

            
def parse_data_import(case):
    
    """
    Parses raw data from imported data.
    """
    
    case.parse_rawdata()

    case.dataframes.keywords = {'frequent_words': all_evidence_entries_words_frequencies_with_evlists(case = case)}                                                    
    
    for item_id in case.items.keys():

        case.items.get_item(item_id).keywords = {
                                                'frequent_words': evidence_entry_most_freq_words(
                                                                                                item_id = item_id, 
                                                                                                case = case,
                                                                                                dataframe = None
                                                                                                )
                                                  }
        
        case.items.get_item(item_id).update_properties()
    
    case.update_properties()

    
def caseobj_from_df_imports(case_name, project, metadata_import, info_import, data_import, other_import, make_default, infer_internet_metadata, infer_geolocation_metadata, lookup_whois):
    
    """
    Creates a Case from imported dataframes.
    """
    
    new_blank_case(name = case_name, project = project, make_default = make_default)
    
    item_set = set(metadata_import.index).union(set(info_import.index)).union(set(data_import.index)).union(set(other_import.index))

    try:
        item_set.remove(np.nan)

    except:
        None
    
    for item_id in item_set:
        
        globals()[case_name].items.add_blank_item(item_id = item_id)
        globals()[case_name].items.get_item(item_id).metadata = item_from_metadata_import(metadata_import, item_id)
        globals()[case_name].items.get_item(item_id).data = item_from_data_import(data_import, item_id)
        globals()[case_name].items.get_item(item_id).information = item_from_info_import(info_import, item_id)
        item_from_other_import(other_import, case_name, item_id)
        
        if lookup_whois == True:
            globals()[case_name].items.get_item(item_id).lookup_whois(append_to_item = True)
    
        globals()[case_name].items.get_item(item_id).update_properties()
    
    for column in info_import.columns:
        info_import[column] = info_import[column].apply(empty_to_none)
        info_import[column] = info_import[column].replace('[', '').replace(']', '')
    
    globals()[case_name].dataframes.metadata = metadata_import
    globals()[case_name].dataframes.information = info_import
    globals()[case_name].dataframes.data = data_import
    globals()[case_name].dataframes.other = other_import
    
    
    if infer_internet_metadata == True:
        globals()[case_name].infer_internet_metadata()
    
        metadata_import = globals()[case_name].dataframes.metadata
    
    if infer_geolocation_metadata == True:
        globals()[case_name].infer_geolocation_metadata()
    
        metadata_import = globals()[case_name].dataframes.metadata
    
#     gen_coincidence_dfs(case = globals()[case_name])
    globals()[case_name].dataframes.update_properties()
    
    if make_default == True:
        globals()[case_name].make_default()
    
    return globals()[case_name]

def import_case_excel(case_name = 'request_input', file_address = 'request_input', project = None, infer_internet_metadata = False, lookup_whois = False, infer_geolocation_metadata = False, parse = False, keywords = False, index = False, coincidences = False, networks = False, analytics = False, make_default = True):
    
    """
    Imports a Case from a formatted Excel (.xlsx) file.
    
    Parameters
    ----------
    case_name : str 
        name for Case. This is intended to be the same string as the Case's variable name.
    file_address : str 
        directory address of file to use. defaults to requesting for user input.
    project : str 
        name of Project object Case will be an attribute of. Defaults to None.
    infer_internet_metadata : bool 
        whether to infer additional internet metadata from internet metadata provided.
    lookup_whois : bool 
        whether to run WhoIs lookups on items.
    infer_geolocation_metadata : bool 
        whether to infer additional geolocation metadata from geolocation metadata provided.
    make_default : bool 
        whether to make the Case object the default csae in the environment.
    parse : bool 
        whether to parse the case's raw data.
    keywords : bool 
        whether to generate keywords from parsed data.
    indexes : bool 
        whether to index Case items, entities, and events by their contents.
    coincidences : bool 
        whether to analyse patterns of coinciding data.
    networks : bool 
        whether to generate core networks from Case items.
    analytics : bool 
        whether to generate Case analytics.
    make_default : bool 
        whether to make the Case object the default csae in the environment.
    
    Returns
    -------
    Case
    """
    
    if case_name == 'request_input':
        case_name = input('Case name: ')
    
    if file_address == 'request_input':
        file_address = input('Case file(s) address: ')
    
    metadata_import = pd.read_excel(file_address, sheet_name = 'Item metadata', header = 0, index_col = 0, dtype = object).replace({np.nan: 'None', 'none': None})
    info_import = pd.read_excel(file_address, sheet_name = 'Item information', header = 0, index_col = 0, dtype = object).replace({np.nan: 'None'})
    data_import = pd.read_excel(file_address, sheet_name = 'Item data', header = 0, index_col = 0, dtype = object).replace({np.nan: 'None'})
    other_import = pd.read_excel(file_address, sheet_name = 'Item other', header = 0, index_col = 0, dtype = object).replace({np.nan: 'None'})
    
    info_import = clean_info_import(info_import)
    metadata_import = clean_metadata_import(metadata_import)
    other_import = clean_other_import(other_import)
    
    caseobj_from_df_imports(
                    case_name = case_name, 
                    project = project,
                     metadata_import = metadata_import, 
                     info_import = info_import, 
                     data_import = data_import, 
                     other_import = other_import,
                     make_default = make_default,
                    infer_internet_metadata = infer_internet_metadata,
                    infer_geolocation_metadata = infer_geolocation_metadata,
                    lookup_whois = lookup_whois
                    )
    
    globals()[case_name].properties.file_location = file_address
    globals()[case_name].properties.file_type = '.xlsx'
    
    if parse == True:
        globals()[case_name].parse_rawdata()
    
    if keywords == True:
        globals()[case_name].generate_keywords()
    
    if index == True:
        globals()[case_name].generate_indexes()
    
    if coincidences == True:
        globals()[case_name].identify_coincidences()
    
    if networks == True:
        globals()[case_name].generate_all_networks()
        
    if analytics == True:
        globals()[case_name].generate_analytics(networks = networks)
    
    globals()[case_name].files.add_file(file_address)
    source_path = globals()[case_name].files[0].properties.obj_path
    target_path = globals()[case_name].properties.obj_path
    globals()[case_name].files[0].relations.case_file = SourceFileOf(name = 'case_source_file', 
                                                                    source_obj_path = source_path,
                                                                  target_obj_path = target_path,
                                                                parent_obj_path = globals()[case_name].files[0].relations.properties.obj_path)
    
    globals()[case_name].update_properties()
    globals()[case_name].backup()
    
    return globals()[case_name]

def import_case_csv_folder(case_name = 'request_input', folder_address = 'request_input', file_names = 'default_names', project = None, infer_internet_metadata = False, lookup_whois = False, infer_geolocation_metadata = False, parse = False, keywords = False, index = False, coincidences = False, networks = False, analytics = False, make_default = True):
    
    """
    Imports a Case from a folder of formatted CSV  (.csv) files.
    
    Parameters
    ----------
    case_name : str 
        name for Case. This is intended to be the same string as the Case's variable name.
    folder_address : str 
        directory address of folder to use. defaults to requesting for user input.
    file_names : list 
        iterable of names of files. Defaults to using a pre-defined 'default' list.
    project : str 
        name of Project object Case will be an attribute of. Defaults to None.
    infer_internet_metadata : bool 
        whether to infer additional internet metadata from internet metadata provided.
    lookup_whois : bool 
        whether to run WhoIs lookups on items.
    infer_geolocation_metadata : bool 
        whether to infer additional geolocation metadata from geolocation metadata provided.
    make_default : bool 
        whether to make the Case object the default csae in the environment.
    parse : bool 
        whether to parse the case's raw data.
    keywords : bool 
        whether to generate keywords from parsed data.
    indexes : bool 
        whether to index Case items, entities, and events by their contents.
    coincidences : bool 
        whether to analyse patterns of coinciding data.
    networks : bool 
        whether to generate core networks from Case items.
    analytics : bool 
        whether to generate Case analytics.
    make_default : bool 
        whether to make the Case object the default case in the environment.
    
    Returns
    -------
    Case
    """
    
    if case_name == 'request_input':
        case_name = input('Case name: ')
    
    if folder_address == 'request_input':
        folder_address = input('Case folder address: ')
    
    if file_names == 'default_names':
        
        metadata_address = folder_address + '/' + 'item_metadata.csv'
        info_address = folder_address + '/' + 'item_information.csv'
        data_address = folder_address + '/' + 'item_data.csv'
        other_address = folder_address + '/' + 'item_other.csv'
        
    else:
        
        metadata_filename = input('Metadata file name: ')
        metadata_address = folder_address + '/' + metadata_filename + '.csv'
        
        info_filename = input('Information file name: ')
        info_address = folder_address + '/' + info_filename + '.csv'
        
        data_filename = input('Raw data file name: ')
        data_address = folder_address + '/' + data_filename + '.csv'
        
        other_filename = input('Other data file name: ')
        other_address = folder_address + '/' + other_filename + '.csv'
    
    metadata_import = pd.read_csv(metadata_address, header = 0, index_col = 0, dtype = object).replace({np.nan: 'None', 'none': None})
    info_import = pd.read_csv(info_address, header = 0, index_col = 0, dtype = object).replace({np.nan: None})
    data_import = pd.read_csv(data_address, header = 0, index_col = 0, dtype = object).replace({np.nan: None})
    other_import = pd.read_csv(other_address, header = 0, index_col = 0, dtype = object).replace({np.nan: None})
    
    caseobj_from_df_imports(
                    case_name = case_name, 
                    project = project,
                     metadata_import = metadata_import, 
                     info_import = info_import, 
                     data_import = data_import, 
                     other_import = other_import,
                     make_default = make_default,
                        infer_internet_metadata = infer_internet_metadata,
                        infer_geolocation_metadata = infer_geolocation_metadata,
                        lookup_whois = lookup_whois
                    )
    
    globals()[case_name].properties.file_location = folder_address
    globals()[case_name].properties.file_type = '.CSV folder'
    
    if parse == True:
        globals()[case_name].parse_rawdata()
    
    if keywords == True:
        globals()[case_name].generate_keywords()
    
    if index == True:
        globals()[case_name].generate_indexes()
    
    if networks == True:
        globals()[case_name].generate_all_networks()
        
    if analytics == True:
        globals()[case_name].generate_analytics(networks = networks)
    
    globals()[case_name].files.add_file(folder_address)
    source_path = globals()[case_name].files[0].properties.obj_path
    target_path = globals()[case_name].properties.obj_path
    globals()[case_name].files[0].relations.case_file = SourceFileOf(name = 'case_source_file', 
                                                                    source_obj_path = source_path,
                                                                  target_obj_path = target_path,
                                                                parent_obj_path = globals()[case_name].files[0].relations.properties.obj_path)
    
    globals()[case_name].files.add_all_children()
    globals()[case_name].update_properties()
    globals()[case_name].backup()
    
    return globals()[case_name]

## Something related to the WhoIs lookups and Geocoder package cause the import/export pickle functions to fail.
## It happens when the exported case object included items that have WhoIs results.

def import_case_pickle(case_name = 'request_input', file_address = 'request_input', make_default = True):
    
    """
    Imports a Case from a pickled text file (.txt or .case).
    
    Parameters
    ----------
    case_name : str 
        name for Case. This is intended to be the same string as the Case's variable name.
    file_address : str 
        directory address to create file in. defaults to requesting for user input.
    make_default : bool 
        whether to make the Case object the default csae in the environment.
    
    Returns
    -------
    Case
    """
    
    if case_name == 'request_input':
        case_name = input('Case name: ')
    
    if file_address == 'request_input':
        file_address = input('File address: ')
    
    with open(file_address, 'rb') as f:
        
        globals()[case_name] = pickle.load(f)
    
    globals()[case_name].properties.file_location = file_address
    globals()[case_name].properties.file_type = '.case'
    
    if make_default == True:
        globals()[case_name].make_default()
    
    globals()[case_name].files.add_file(file_address)
    source_path = globals()[case_name].files[0].properties.obj_path
    target_path = globals()[case_name].properties.case_path
    globals()[case_name].files[0].relations.case_file = SourceFileOf(name = 'case_source_file', 
                                                                    source_obj_path = source_path,
                                                                  target_obj_path = target_path,
                                                                parent_obj_path = globals()[case_name].files[0].relations.properties.obj_path)
    
    globals()[case_name].backup()
    
    return globals()[case_name]

def import_case_txt(case_name = 'request_input', file_address = 'request_input', make_default = True):
    
    """
    Imports a Case from a pickled text file (.txt or .case).
    
    Parameters
    ----------
    case_name : str 
        name for Case. This is intended to be the same string as the Case's variable name.
    file_address : str 
        directory address to create file in. defaults to requesting for user input.
    make_default : bool 
        whether to make the Case object the default csae in the environment.
    
    Returns
    -------
    Case
    """
    
    return import_case_pickle(case_name = case_name, file_address = file_address, make_default = make_default)            

## Global functions for interacting with case objects

def open_case(case_name = 'request_input', file_address = 'request_input', make_default = True):
    
    """
    Opens a Case from a file.
    
    File types:
        * .case (a custom .txt file)
        * .txt (if pickled)
        * .xlsx
        * .csv
        * folder of .csv files.
    
    Parameters
    ----------
    case_name : str 
        name for Case. This is intended to be the same string as the Case's variable name.
    file_address : str 
        directory address to create file in. defaults to requesting for user input.
    make_default : bool 
        whether to make the Case object the default csae in the environment.

    Returns
    -------
    Case
    """
    
    if case_name == 'request_input':
        case_name = input('Case name: ')
    
    if file_address == 'request_input':
        file_address = input('address: ')
    
    path = Path(file_address)
    is_dir = path.is_dir()
    
    if is_dir == True:
        return import_case_csv_folder(case_name = case_name, folder_address = file_address, file_names = 'default_names', project = None, infer_internet_metadata = False, lookup_whois = False, infer_geolocation_metadata = False, parse = False, keywords = False, index = False, coincidences = False, networks = False, analytics = False, make_default = True)
    
    else:
    
        file_end = path.suffix
    
    if file_end == '.xlsx':
        return import_case_excel(case_name = case_name, file_address = file_address, make_default = make_default)
    
    if (file_end == '.case') or (file_end == '.txt'):
        return import_case_pickle(case_name = case_name, file_address = file_address, make_default = make_default)

def save_as(case = 'default_case'):
    
    """
    Saves a Case to a file. Requests file details from user input.
    
    Parameters
    ----------
    case : str 
        name of Case object to save.
    """
    
    if case == 'default_case':
        case = get_default_case()
    
    case.save_as()

def save(case = 'default_case'):
    
    """
    Saves a Case to its source file. If no file exists, requests file details from user input.
    
    Parameters
    ----------
    case : str 
        name of Case object to save.
    """
    
    if case == 'default_case':
        case = get_default_case()
    
    case.save()

def sync_items(case = 'default_case'):
    
    """
    Synchronises a Case's items and dataframes.
    """
    
    if case == 'default_case':
        case = get_default_case()
    
    case.sync_items()

def update_case(case = 'default_case'):
    
    """
    Updates a Case's contents and analytics.
    """
    
    if case == 'default_case':
        case = get_default_case()
    
    case.update_case()
    