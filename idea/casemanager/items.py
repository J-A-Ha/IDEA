from ..core.basics import dict_to_str, map_inf_to_1, map_inf_to_0
from ..core.cleaners import join_df_col_lists_by_semicolon, parse_data, html_words_cleaner, is_int, is_float, is_date, is_time, is_datetime, str_to_datetime
from ..visualisation.visualise import plot_timeline, plot_date_range_timeline
from ..text.textanalysis import cosine_sim
from ..text.information_extraction import extract_names, extract_countries, extract_cities, extract_cities, extract_languages
from ..location.geolocation import coordinates_distance, lookup_coordinates, lookup_location, get_location_coordinates, normalised_coordinates_distance, normalised_coordinates_distance_inverse, normalised_locations_distance, normalised_locations_distance_inverse
from ..location.chronolocation import time_difference, normalised_time_difference, normalised_time_difference_inverse
from ..internet.webanalysis import get_ip_geocode, get_ip_coordinates, get_ip_physical_location, lookup_ip_coordinates, lookup_whois, is_registered_domain, domain_whois, ip_whois, regex_check_then_open_url
from ..internet.scrapers import scrape_url, scrape_url_links
from ..internet.crawlers import crawl_web, fetch_sitemap, crawl_site, correct_link_errors
from ..socmed.sherlock_interpreter import search_username
from ..importers.pdf import read_pdf, read_pdf_url
from .defaults_manager import get_default_case
from .obj_properties import CaseObjectProperties
from .obj_superclasses import CaseObject, CaseObjectSet
from .relationships import CaseRelation, CaseRelationSet, SourceFileOf
from .files import stat_result, CaseFile, CaseFileSet
from .casespecial import CaseSpecial

from typing import List, Dict, Tuple
import os
import sys
import copy
import json
import pickle
from datetime import datetime, timedelta
import itertools

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from Levenshtein import distance as lev


class CaseItem(CaseSpecial):
    
    """
    This is a CaseItem object. It represents a piece of material or evidence associated with a case.
    
    Parameters
    ----------
    item_id : str
        ID used for retrieving item. Defaults to requesting user input.
    parent_obj_path : str
        if relationship is an attribute, object path of the parent object. Defaults to None.
    data : object
        data associated with item. Defaults to None.
    metadata : object
        item's metadata. Defaults to None.
    information : object
        information associated with item. Defaults to None.
    lookup_whois : bool
        whether to run WhoIs lookup on item metadata. Defaults to False.
    keywords : dict
        keywords associated with item. Defaults to an empty dictionary.
    links : list
        links associated with item. Defaults to an empty list.
    references : list
        references associated with item. Defaults to an empty list.
    contains : list
        objects contained by item. Defaults to an empty list.
    user_assessments : dict
        user notes and assessments. Defaults to an empty dictionary.
    
    Attributes
    ----------
    properties : CaseObjectProperties
        metadata for CaseItem object.
    metadata : pandas.DataFrame
        a dataframe of metadata associated with the item.
    data : pandas.DataFrame
        a dataframe of data associated with the item.
    information : pandas.DataFrame
        a dataframe of information associated with the item.
    whois : WhoisResult
        a WhoisResult object containing Whois data associated with the item.
    links : list
        a list of links associated with the item.
    references : list
        a list of references associated with the item.
    contains : list
        a list of content associated with the item.
    user_assessments : dict
        a dictionary of information assigned by the user.
    relations : CaseRelationSet
        a CaseRelationSet object of relations associated with the item in a case.
    
    Notes
    -----
        * Intended to be assigned as an attribute of a CaseItemSet within a Case object.
        * Subclass of CaseSpecial class.
    """
    
    def __init__(self, 
                 item_id: str = 'request_input', 
                 parent_obj_path: str = None, 
                 data: object = None, 
                 metadata: object = None, 
                 information: object = None, 
                 lookup_whois: bool = False, 
                 keywords: dict = {}, 
                 links: list = [], 
                 references: list = [], 
                 contains: list = [], 
                 user_assessments: dict = {}):
        
        """
        Initialises CaseItem instance.
        
        Parameters
        ----------
        item_id : str
            ID used for retrieving item. Defaults to requesting user input.
        parent_obj_path : str
            if relationship is an attribute, object path of the parent object. Defaults to None.
        data : object
            data associated with item. Defaults to None.
        metadata : object
            item's metadata. Defaults to None.
        information : object
            information associated with item. Defaults to None.
        lookup_whois : bool
            whether to run WhoIs lookup on item metadata. Defaults to False.
        keywords : dict
            keywords associated with item. Defaults to an empty dictionary.
        links : list
            links associated with item. Defaults to an empty list.
        references : list
            references associated with item. Defaults to an empty list.
        contains : list
            objects contained by item. Defaults to an empty list.
        user_assessments : dict
            user notes and assessments. Defaults to an empty dictionary.
        """
        
        # Requesting item ID from user input if none provided
        if item_id == 'request_input':
            item_id = input('Item ID: ')
        
        # Inheriting methods and attributes from CaseSpecial class
        super().__init__(obj_name = item_id, obj_type = 'CaseItem', parent_obj_path = parent_obj_path)
        
        # Setting item properties
        self.properties = CaseObjectProperties(obj_name = item_id, obj_type = 'CaseItem', parent_obj_path = parent_obj_path, size = None)
        
        # Setting item ID attribute. If current ID is None, retrieving item variable string name
        self.item_id = item_id
        
        if self.item_id == None:
            self.item_id = self.get_id()
        
        self.properties.obj_name = self.item_id
        
        # Initialising data dataframe
        if data == None:
            self.data = pd.DataFrame(columns = ['Datatype', 'Format', 'Stored as', 'Size (bytes)', 'Raw data', 'Parsed data'])
        elif type(data) == pd.DataFrame:
            self.data = data
        
        # Initialising metadata dataframe
        if metadata == None:
            self.metadata = pd.DataFrame(columns = ['Metadata', 'Category'])                  
        elif type(metadata) == pd.DataFrame:
            self.metadata = metadata
        
        # Initialising information dataframe
        if information == None:
            self.information = pd.DataFrame(columns = ['Label', 'Category'])
        elif type(information) == pd.DataFrame:
            self.information = information
        
        # Running WhoIs lookup if requested
        if lookup_whois == True:
            self.whois = self.lookup_whois()
        else:
            self.whois = None
        
        # Assigning links, references, contents, and user assessments
        self.links = links
        self.references = references 
        self.contains = contains
        self.user_assessments =  user_assessments
        
        # Updating properties
        self.update_properties()
        

    # Methods for editing and retrieving item properties
    
    def update_properties(self):
        
        """
        Updates CaseItem's properties.
        
        Updates
        -------
            * obj_id
            * obj_size
            * item_id
            * data_count
            * metadata_count
            * information_count
            * links_count
            * references_count
            * contents_count
            * last_changed
            * hash
        """
        
        # Retrieving object ID code
        self.properties.obj_id = id(self)
        
        # Retrieving item ID
        self.properties.item_id = self.get_id()
        
        # Updating data count
        if ('data' in self.__dict__.keys()) and (type(self.data) != None):
            self.properties.data_count = len(self.data.index)
        else:
            self.properties.data_count = 0
        
        # Updating metadata count
        if ('metadata' in self.__dict__.keys()) and (type(self.metadata) != None):
            self.properties.metadata_count = len(self.metadata.index)
        else:
            self.properties.metadata_count = 0
        
        # Updating information count
        if ('information' in self.__dict__.keys()) and (type(self.information) != None):
            self.properties.information_count = len(self.information.index)
        else:
            self.properties.information_count = 0
        
        # Updating links count
        if ('links' in self.__dict__.keys()) and (self.links != None):
            self.properties.links_count = len(self.links)
        else:
            self.properties.links_count = 0
        
        # Updating references count
        if ('references' in self.__dict__.keys()) and (self.references != None):
            self.properties.references_count = len(self.references)
        else:
            self.properties.references_count = 0
        
        # Updating contents count
        if ('contains' in self.__dict__.keys()) and (self.contains != None):
            self.properties.contents_count = len(self.contains)
        else:
            self.properties.contents_count = 0
        
        # Updating object size
        self.properties.obj_size = str(self.__sizeof__()) + ' bytes'
        
        # Updating last changed time
        self.properties.update_last_changed()
        
        # Updating hash code
        self.properties.hash = self.__hash__()
    
    def __repr__(self):
        
        """
        Defines how CaseItems are represented in string form.
        """
        
        output = '\n' + str(self.properties)
        return output
    


    # Methods for checking if data and objects are attributes of an item set or case object
    
    def in_itemset(self, itemset):
        
        """
        Checks if item is part of an inputted item set.
        """
        
        # Retrieving item ID
        item_id = self.get_id()
        
        # Checking if item ID is in item set
        return hasattr(itemset, item_id)
    
    
    def in_case(self, case = 'default_case'):
        
        """
        Checks if item is part of an inputted case.
        """
        
        # Returning default case if no case provided
        if case == 'default_case':
            case = get_default_case()
        
        # Retrieving item ID
        item_id = self.get_id()
        
        # Checking if item ID is in case
        return hasattr(case.items, item_id)

    # Methods for adding and editing an item's data
    
    def add_id(self):
        
        """
        Adds ID to item if no valid ID set.
        """
        
        # Adding ID if none present or current ID is not a string
        if (self.item_id == None) or (type(self.item_id) != str):
            self.item_id = self.get_name_str()
        
        self.update_properties()
        
    
    def add_data(self, data_type = 'request_input', data_format = 'request_input', raw_data = 'request_input'):
        
        """
        Adds single data entry to an item's data dataframe.
        """
        
        # Requesting data type from user if none provided
        if data_type == 'request_input':
            data_type = input('Data type: ')
        
        # Requesting data format from user if none provided
        if data_format == 'request_input':
            data_format = input('Data format: ')
        
        # Requesting raw data (if text) from user if none provided
        if raw_data == 'request_input':
            raw_data = input('Raw data: ')
        
        # Calculating index position to add data to
        index_pos = len(self.data.index)
        
        # Adding data
        self.data.loc[index_pos, 'Raw data'] = raw_data
        self.data.loc[index_pos, 'Parsed data'] = None
        self.data.loc[index_pos, 'Datatype'] = data_type
        self.data.loc[index_pos, 'Format'] = data_format
        self.data.loc[index_pos, 'Stored as'] = type(raw_data)
        size = sys.getsizeof(raw_data)
        self.data.loc[index_pos, 'Size (bytes)'] = size
        
        self.update_properties()
        
    def add_metadata(self, metadata_category = 'request_input', metadata_entry = 'request_input'):
        
        """
        Adds single metadata entry to an item's metadata dataframe; adds custom metadata category if one given doesn't exist.
        """
        
        # Requesting metadata category from user if none provided
        if metadata_category == 'request_input':
            metadata_category = input('Category: ')
        
        # Requesting metadata entry from user if none provided
        if metadata_entry == 'request_input':
            metadata_entry = input('Entry: ')
        
        # If the metadata category already exists, overwriting existing metadata
        if metadata_category in self.metadata['Category'].values:

            top_index = self.metadata[self.metadata['Category'] == metadata_category].index.values[0]

            if (
                (self.metadata.loc[top_index, 'Metadata'] == None)
                or (self.metadata.loc[top_index, 'Metadata'] == 'None')
                ):
                self.metadata.loc[top_index, 'Metadata'] = metadata_entry

            else:
                updated_entry = [self.metadata.loc[top_index, 'Metadata'], metadata_entry]
                self.metadata.loc[top_index, 'Metadata'] = updated_entry
        
         # If the metadata category doesn't exist, adding new category
        else: 

            index = len(self.metadata.index)
            self.metadata.loc[index, 'Category'] = metadata_category
            self.metadata.loc[index, 'Metadata'] = metadata_entry
        
        self.update_properties()
    
    def add_metadata_df(self, metadata_df):
        
        """
        Concatenates a new metadata dataframe to an item's existing metadata dataframe.
        """

        if type(metadata_df) != pd.DataFrame:
            raise TypeError('This method requires a DataFrame')

        self.metadata = pd.concat([self.metadata, metadata_df])

        self.update_properties()
        

    def replace_metadata(self, metadata_df):
        
        """Replaces an item's metadata with a dictionary."""

        if type(metadata_df) != pd.DataFrame:
            raise TypeError('Input must be dataframe')

        self.metadata = metadata_df

        self.update_properties()
    
    
    def add_address(self, address = 'request_input'):
        
        """
        Adds a metadata entry under the category 'address'; appends to any existing addresses.
        """
        
        if address == 'request_input':
            address = input('Address: ')

        if 'address' in self.metadata['Category'].values:

            top_index = self.metadata[self.metadata['Category'] == 'address'].index.values[0]

            if (
                (self.metadata.loc[top_index, 'Metadata'] == None)
                or (self.metadata.loc[top_index, 'Metadata'] == 'None')
                ):
                self.metadata.loc[top_index, 'Metadata'] = address

            else:
                if type(self.metadata.loc[top_index, 'Metadata']) != list:
                    updated_entry = [self.metadata.loc[top_index, 'Metadata'], address]
                    self.metadata.loc[top_index, 'Metadata'] = updated_entry
                    
                else:
                    self.metadata.loc[top_index, 'Metadata'].append(address)

        else: 

            index = len(self.metadata.index)
            self.metadata.loc[index, 'Category'] = 'address'
            self.metadata.loc[index, 'Metadata'] = address
                                                  
        self.update_properties()
        

    def add_info(self, info = 'request_input', info_category = 'request_input', suppress_warnings = False):
        
        """Adds a single information entry to object."""

        if info == 'request_input':
            info = input('Information entry: ')

        if info_category == 'request_input':
            info_category = input('Category: ')

        if (
            (info_category in self.information['Category'].values)
            and (info in self.information['Label'].values)
           ):
            if suppress_warnings == False:
                res = input('This entry is a duplicate of an information entry. Do you wish to proceed? (Yes / No): ')
                res = res.lower().strip()
            else:
                res = 'yes'

            if res == 'yes':
                pos = len(self.information.index)
                self.information.loc[pos, 'Category'] = info_category
                self.information.loc[pos, 'Label'] = info

            else:
                return

        else: 

            pos = len(self.information.index)
            self.information.loc[pos, 'Category'] = info_category
            self.information.loc[pos, 'Label'] = info
        
        self.update_properties()
        
    def add_info_df(self, new_info_df):
        
        """Adds a new information dataframe to an item's existing information dataframe."""
        
        if type(new_info_dict) != pd.DataFrame:
            raise TypeError('This method requires a DataFrame')

        self.information = pd.concat([self.information, new_info_df])
        
        self.update_properties()
        

    def add_link(self, link = 'request_input'):
        
        """Adds a link to an item's list of links."""
        
        if link == 'request_input':
            link = input('Link: ')

        self.links.append(link)

        self.update_properties()
        

    def add_links(self, links_list = 'request_input'):
        
        """Adds a list of links to an item."""
        
        if links_list == 'request_input':
            links_list = input('Links: ')

        if type(links_list) == str:
            links_list = [links_list]

        self.links = self.links + links_list

        self.update_properties()
        
        

    def add_reference(self, reference = 'request_input'):
        
        """Adds a reference to an item's list of references."""
        
        if reference == 'request_input':
            reference = input('Reference: ')

        self.references.append(reference)

        self.update_properties()
        

    def add_references(self, references_list = 'request_input'):
        
        """Adds list of references to an item."""

        if references_list == 'request_input':
            references_list = input('References: ')

        if type(references_list) == str:
            references_list = [references_list]

        self.references = self.references + references_list
    
        self.update_properties()
        
    
    def add_content(self, content = None):
        
        """Adds a content entry to an item's list of contents."""
        
        if content == None:
            content = input('Content: ')

        self.contains.append(content)

        self.update_properties()
        
    def add_contents(self, content_list = None):
        
        """Adds list of contents to an item."""
        
        if content_list == None:
            content_list = input('Contents: ')

        if type(content_list) == str:
            content_list = [content_list]

        self.contains = self.contains + content_list
        self.update_properties()
        
        
    def add_pdf_data(self, file_path = None):
        
        """
        Reads PDF file and adds to item data.
        """
        
        # Reading and parsing PDF file
        parsed_pdf = read_pdf(file_path = file_path)
        
        # Adding data
        self.data = self.data.astype(object)
        index_pos = len(self.data.index)
        self.data.at[index_pos, 'Datatype'] = 'text'
        self.data.at[index_pos, 'Format'] = 'PDF'
        self.data.at[index_pos, 'Stored as'] = type(parsed_pdf['full_text'])
        self.data.at[index_pos, 'Size (bytes)'] = sys.getsizeof(parsed_pdf['full_text'])
        self.data.at[index_pos, 'Raw data'] = parsed_pdf['full_text']
        self.data.at[index_pos, 'Parsed data'] = None
        
        self.links = parsed_pdf['links']
    

    # Methods for creating or updating an item from other variables
    
    def from_dict(self, item_dict):
        
        """
        Creates CaseItem from dictionary.
        """
        
        if (
            ('data' not in item_dict.keys())
            and ('information' not in item_dict.keys())
            and ('metadata' not in item_dict.keys())
            and ('other' not in item_dict.keys())
            and ('whois' not in item_dict.keys())
            and ('links' not in item_dict.keys())
            and ('references' not in item_dict.keys())
            and ('contains' not in item_dict.keys())
            and ('keywords' not in item_dict.keys())
            and ('user_assessments' not in item_dict.keys())
           ):
            raise ValueError('JSON does not contain any of the necessary fields: "data", "metadata", "information", "other", "whois", "links", "references", "contains", "keywords", or "user_assessments"')
        
        try:
            if type(item_dict['data']) == pd.DataFrame:
                self.data = item_dict['data']
        except:
            None
        
        try:
            if type(item_dict['metadata']) == pd.DataFrame:
                self.metadata = item_dict['metadata']
        except:
            None
        
        try:
            if type(item_dict['information']) == pd.DataFrame:
                self.information = item_dict['information']
        except:
            None
        
        try:
            if type(item_dict['other']) == pd.DataFrame:
                self.links = item_dict['other']['links'].to_list()
                self.references = item_dict['other']['references'].to_list()
                self.contains = item_dict['other']['contains'].to_list()
        except:
            None
        
        try:
            if type(item_dict['whois']) == pd.DataFrame:
                self.whois = item_dict['whois']
        except:
            None
        
        try:
            if type(item_dict['links']) == list:
                self.links = item_dict['links']
        except:
            None
        
        try:
            if type(item_dict['references']) == list:
                self.references = item_dict['references']
        except:
            None
        
        try:
            if type(item_dict['contains']) == list:
                self.contains = item_dict['contains']
        except:
            None  
        
        try:
            if type(item_dict['user_assessments']) == dict:
                self.user_assessments = item_dict['user_assessments']
        except:
            None
    
        self.update_properties()
        

    # Methods for importing files and adding to item
    
    def import_json(self, file_address = 'request_input'):
        
        """
        Creates CaseItem from JSON file.
        """
        
        if file_address == 'request_input':
            file_address = input('File address: ')
        
        with open(file_address) as json_file:
            item_dict = json.load(json_file)
        
        self.from_dict(item_dict)
        self.files.add_file(file_address)
        source_path = self.files[0].properties.obj_path
        target_path = self.properties.obj_path
        self.files[0].relations.item_source = SourceFileOf(name = 'item_source', 
                                                                    source_obj_path = source_path,
                                                                  target_obj_path = target_path,
                                                                parent_obj_path = self.files[0].relations.properties.obj_path)
        self.relations.item_source = SourceFileOf(name = 'item_source', 
                                                                    source_obj_path = source_path,
                                                                  target_obj_path = target_path,
                                                                parent_obj_path = self.relations.properties.obj_path)
    
        self.update_properties()
    
    def import_metadata_csv(self, file_address = 'request_input'):
        
        """
        Adds metadata from CSV file.
        """
        
        if file_address == 'request_input':
            file_address = input('File address: ')
        
        df = pd.read_csv(file_address, header = 0, index_col = 0, dtype = 'object').replace({np.nan: 'None', 'none': None})  
        
        if df.columns.to_list() != ['Metadata', 'Category']:
            raise KeyError('CSV columns are incorrect. The CSV should be formatted as: "Metadata", "Category"')
    
        self.metadata = pd.concat([self.metadata, df])
        self.files.add_file(file_address)
        path_obj = Path(file_address)
        source_path = path_obj.parent.name + '__' + path_obj.name
        target_path = self.metadata.properties.obj_path
        self.files[0].relations.metadata_source = SourceFileOf(name = 'metadata_source', 
                                                                    source_obj_path = source_path,
                                                                  target_obj_path = target_path,
                                                                parent_obj_path = self.files[0].relations.properties.obj_path)
        self.metadata.relations.metadata_source = SourceFileOf(name = 'metadata_source', 
                                                                    source_obj_path = source_path,
                                                                  target_obj_path = target_path,
                                                                parent_obj_path = self.metadata.relations.properties.obj_path)
    
        
        self.update_properties()
    
    
    def import_data_csv(self, file_address = 'request_input'):
        
        """
        Adds data from CSV file.
        """
        
        if file_address == 'request_input':
            file_address = input('File address: ')
        
        df = pd.read_csv(file_address, header = 0, index_col = 0, dtype = 'object').replace({np.nan: 'None', 'none': None})  
        
        if df.columns.to_list() != ["Datatype", "Format", "Stored as", "Size (bytes)", "Raw data", "Parsed data"]:
            raise KeyError('CSV columns are incorrect. The CSV should be formatted as: "Datatype", "Format", "Stored as", "Size (bytes)", "Raw data", "Parsed data"')
        
        self.data = pd.concat([self.data, df])
        self.files.add_file(file_address)
        path_obj = Path(file_address)
        source_path = path_obj.parent.name + '__' + path_obj.name
        target_path = self.data.properties.obj_path
        self.files[0].relations.data_source = SourceFileOf(name = 'data_source', 
                                                                    source_obj_path = source_path,
                                                                  target_obj_path = target_path,
                                                                parent_obj_path = self.files[0].relations.properties.obj_path)
        self.data.relations.data_source = SourceFileOf(name = 'data_source', 
                                                                    source_obj_path = source_path,
                                                                  target_obj_path = target_path,
                                                                parent_obj_path = self.data.relations.properties.obj_path)
        
        self.update_properties()
    
    def import_info_csv(self, file_address = 'request_input'):
        
        """
        Adds information from CSV file.
        """
        
        if file_address == 'request_input':
            file_address = input('File address: ')
        
        df = pd.read_csv(file_address, header = 0, index_col = 0, dtype = 'object').replace({np.nan: 'None', 'none': None})  
        
        if df.columns.to_list() != ['Label', 'Category']:
            raise KeyError('CSV columns are incorrect. The CSV should be formatted as: "Label", "Category"')
    
        self.metadata = pd.concat([self.information, df])
        self.files.add_file(file_address)
        path_obj = Path(file_address)
        source_path = path_obj.parent.name + '__' + path_obj.name
        target_path = self.information.properties.obj_path
        self.files[0].relations.info_source = SourceFileOf(name = 'info_source', 
                                                                    source_obj_path = source_path,
                                                                  target_obj_path = target_path,
                                                                parent_obj_path = self.files[0].relations.properties.obj_path)
        self.information.relations.info_source = SourceFileOf(name = 'info_source', 
                                                                    source_obj_path = source_path,
                                                                  target_obj_path = target_path,
                                                                parent_obj_path = self.information.relations.properties.obj_path)
        
        
        self.update_properties()
    
    
    def import_other_csv(self, file_address = 'request_input'):
        
        """
        Adds links, references, and contents from CSV file.
        """
        
        if file_address == 'request_input':
            file_address = input('File address: ')
        
        df = pd.read_csv(file_address, header = 0, index_col = 0, dtype = 'object').replace({np.nan: 'None', 'none': None})  
        
        if df.columns.to_list() != ['links', 'references', 'contents', 'other']:
            raise KeyError('CSV columns are incorrect. The CSV should be formatted as: "links", "references", "contents", "other"')
    
        try:
            self.links = self.links.append(df.loc[0, 'links'])
        except:
            None
        
        try:
            self.references = self.links.append(df.loc[0, 'references'])
        except:
            None
        
        try:
            self.contains = self.links.append(df.loc[0, 'contents'])
        except:
            None
        
        self.files.add_file(file_address)
        path_obj = Path(file_address)
        source_path = path_obj.parent.name + '__' + path_obj.name
        target_path = self.properties.obj_name + '.links'
        self.files[0].relations.other_source = SourceFileOf(name = 'other_source', 
                                                                    source_obj_path = source_path,
                                                                  target_obj_path = target_path,
                                                                parent_obj_path = self.files[0].relations.properties.obj_path)
        
        self.update_properties()
    
    def import_item_csvs(self, folder_address = 'request_input'):
        
        """
        Adds data, metadata, information, links, references, and contents from folder of CSV files.
        """
        
        if folder_address == 'request_input':
            folder_address = input('File address: ')
        
        metadata_address = folder_address + '/' + 'metadata.csv'
        info_address = folder_address + '/' + 'information.csv'
        data_address = folder_address + '/' + 'data.csv'
        other_address = folder_address + '/' + 'other.csv'
        
        self.import_metadata_csv(file_address = metadata_address)
        self.files.add_file(metadata_address)
        self.import_data_csv(file_address = data_address)
        self.files.add_file(data_address)
        self.import_info_csv(file_address = info_address)
        self.files.add_file(info_address)
        self.import_other_csv(file_address = other_address)
        self.files.add_file(other_address)
    
        self.update_properties()
        

    # Methods for exporting data from item
    
    def export_txt(self, new_file = True, file_name = 'request_input', file_address = 'request_input'):
        
        """
        Exports item as pickled .txt file.
        """
        
        if new_file == True:
            
            if file_name == 'request_input':
                file_name = input('File name: ')
            
            if file_address == 'request_input':
                file_address = input('File address: ')
                file_address = file_address + '/' + file_name
            
        if new_file == False:
            
            if file_address == 'request_input':
                file_address = input('File path: ')
        
        if '.case_item' != file_address[-9:]:
            file_address = file_address + '.case_item'

        with open(file_address, 'wb') as f:
            pickle.dump(self, f) 


    def export_excel(self, new_file = True, file_name = 'request_input', file_address = 'request_input'):
        
        """
        Exports item as Excel (.xlsx) file.
        """
        
        if new_file == True:
            
            if file_name == 'request_input':
                file_name = input('File name: ')
            
            if file_address == 'request_input':
                file_address = input('File address: ')
                file_address = file_address + '/' + file_name
            
        if new_file == False:
            
            if file_address == 'request_input':
                file_address = input('File path: ')
        
        if '.xlsx' != file_address[-5:]:
            file_address = file_address + '.xlsx'
        
        metadata_df = self.metadata.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(metadata_df)

        info_df = self.information.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(info_df)

        data_df = self.data.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(data_df)
        
        try:
            whois_df = self.whois.astype(str).replace('NaT', None).replace('None', None)
            join_df_col_lists_by_semicolon(whois_df)
        except:
            pass
        
#         links_df = self.links.astype(str).replace('NaT', None).replace('None', None)
#         join_df_col_lists_by_semicolon(links_df)
        
#         refs_df = self.references.astype(str).replace('NaT', None).replace('None', None)
#         join_df_col_lists_by_semicolon(refs_df)
        
#         contents_df = self.contains.astype(str).replace('NaT', None).replace('None', None)
#         join_df_col_lists_by_semicolon(contents_df)
        
#         assessments_df = self.user_assessments.astype(str).replace('NaT', None).replace('None', None)
#         join_df_col_lists_by_semicolon(assessments_df)

        
        with pd.ExcelWriter(file_address) as writer:  
            
            metadata_df.to_excel(writer, sheet_name='Metadata')
            data_df.to_excel(writer, sheet_name='Data')
            info_df.to_excel(writer, sheet_name='Information')
            
            try:
                whois_df.to_excel(writer, sheet_name='WhoIs')
            except:
                pass
            
#             links_df.to_excel(writer, sheet_name='Links')
#             refs_df.to_excel(writer, sheet_name='References')
#             contents_df.to_excel(writer, sheet_name='Contents')
#             assessments_df.to_excel(writer, sheet_name='User assessments')


    def export_csv_folder(self, folder_address = 'request_input', folder_name = 'request_input'):
        
        """
        Exports item as a folder of CSV files.
        """
        
        metadata_df = self.metadata.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(metadata_df)

        info_df = self.information.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(info_df)

        data_df = self.data.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(data_df)
        
        try:
            whois_df = self.whois.astype(str).replace('NaT', None).replace('None', None)
            join_df_col_lists_by_semicolon(whois_df)
        except:
            whois_df = None
        
#         links_df = self.links.astype(str).replace('NaT', None).replace('None', None)
#         join_df_col_lists_by_semicolon(links_df)
        
#         refs_df = self.references.astype(str).replace('NaT', None).replace('None', None)
#         join_df_col_lists_by_semicolon(refs_df)
        
#         contents_df = self.contains.astype(str).replace('NaT', None).replace('None', None)
#         join_df_col_lists_by_semicolon(contents_df)
        
#         assessments_df = self.user_assessments.astype(str).replace('NaT', None).replace('None', None)
#         join_df_col_lists_by_semicolon(assessments_df)
    
        dfs_dict = {
                    'item_metadata': metadata_df,
                    'item_data': data_df, 
                    'item_information': info_df,
                    'item_whois': whois_df
#                     'Links': links_df,
#                     'References': refs_df,
#                     'Contents': contents_df,
#                     'User assessments': assessments_df
                    }
        
        if folder_address == 'request_input':
            folder_address = input('Folder address: ')
        
        if folder_name == 'request_input':
            folder_name = input('Folder name: ')
        
        path = os.path.join(folder_address, folder_name) 
        
        os.mkdir(path) 

        for item in dfs_dict.keys():
            file_name = item
            file_path = path + '/' + file_name + '.csv'
            df = dfs_dict[item]
            
            try:
                df.to_csv(file_path)
            except:
                continue
          
    def save_as(self, file_name = 'request_input', file_address = 'request_input', file_type = 'request_input'):
        
        """
        Exports item as a file type selected by user.
        
        File type options:
            * case
            * txt
            * pickle
            * xlsx
            * csv
        """
        
        if file_type == 'request_input':
            file_type = input('File type: ')
        
        file_type = file_type.strip().strip('.').strip().lower()
        
        
        if (file_type.lower() == None) or (file_type.lower() == '') or (file_type.lower() == 'case') or (file_type.lower() == 'text') or (file_type.lower() == 'txt') or (file_type.lower() == 'pickle'):
            
            self.export_txt(new_file = True, file_name = file_name, file_address = file_address)
        
        
        if (file_type.lower() == 'excel') or (file_type.lower() == 'xlsx'):
            
            self.export_excel(new_file = True, file_name = file_name, file_address = file_address)
        
        
        if (file_type.lower() == 'csv') or (file_type.lower() == 'csvs'):
            
            self.export_csv_folder(folder_address = file_address, folder_name = file_name)

            

    # Methods for deleting data from item
    
    def delete_metadata(self):
        
        """
        Deletes all item metadata.
        """
        
        delattr(self, 'metadata')
        self.metadata = pd.DataFrame(columns = ['Metadata', 'Category'])
        self.update_properties()
    
    def delete_metadata_by_category(self, category = 'request_input'):
        
        """
        Deletes all item metadata in an inputted category.
        """
        
        if category == 'request_input':
            category = input('Category to delete: ')
        
        indexes = self.metadata[self.metadata['Category'] == category].index
        self.metadata = self.metadata.drop(indexes)
        self.update_properties()
        
    def delete_data(self):
        
        """
        Deletes all item data.
        """
        
        delattr(self, 'data')
        self.data = pd.DataFrame(columns = ['Datatype', 'Format', 'Stored as', 'Size (bytes)', 'Raw data', 'Parsed data'])
        self.update_properties()
    
    def delete_data_by_datatype(self, datatype = 'request_input'):
        
        """
        Deletes all item data of an inputted datatype.
        """
        
        if datatype == 'request_input':
            datatype = input('Datatype to delete: ')
        
        indexes = self.data[self.data['Datatype'] == datatype].index
        self.data = self.data.drop(indexes)
        self.update_properties()
        
    def delete_data_by_format(self, data_format = 'request_input'):
        
        """
        Deletes all item data of an inputted format.
        """
        
        if data_format == 'request_input':
            data_format = input('Format to delete: ')
        
        indexes = self.data[self.data['Format'] == data_format].index
        self.data = self.data.drop(indexes)
        self.update_properties()
        
    def delete_rawdata(self, rawdata = 'request_input'):
        
        """
        Deletes all item rawdata.
        """
        
        if rawdata == 'request_input':
            rawdata = input('Raw data to delete: ')
        
        indexes = self.data[self.data['Raw data'] == rawdata].index
        self.data = self.data.drop(indexes)
        self.update_properties()
        
    def delete_info(self):
        
        """
        Deletes all item information.
        """
        
        delattr(self, 'information')
        self.information = pd.DataFrame(columns = ['Label', 'Category'])
        self.update_properties()
        
    def delete_info_by_category(self, category = 'request_input'):
        
        """
        Deletes all item informatiion in an inputted category.
        """
        
        if category == 'request_input':
            category = input('Category to delete: ')
        
        indexes = self.information[self.information['Category'] == category].index
        self.information = self.information.drop(indexes)
        self.update_properties()
        
    def delete_info_by_label(self, label = 'request_input'):
        
        """
        Deletes all item information with a specific label.
        """
        
        if label == 'request_input':
            label = input('Labels to delete: ')
        
        indexes = self.information[self.information['Label'] == label].index
        self.information = self.information.drop(indexes)
        self.update_properties()
    

    def clear(self, itemset = None, case = 'default_case'):
        
        """
        Deletes all item attributes and returns a new item.
        """
        
        item_id = self.get_id()
        
        if item_id in globals():
            is_global = True
            del globals()[item_id]
        else:
            is_global = False
            
        new_item = CaseItem(item_id = item_id)
        
        if item_id in locals():
            is_local = True
            del locals()[item_id]
            locals()[item_id] = new_item
        
        if itemset == None:
            itemset == CaseItemSet()
        
        if self.in_itemset(itemset = itemset) == True:
            del itemset.__dict__[item_id]
            itemset.add_item(new_item)
        
        if self.in_case(case = case) == True:
            del case.items.__dict__[item_id]
            case.items.add_item(new_item)
        
        if is_global == False:
            del globals()[item_id]
            
        return new_item

    # Methods for retrieving data from item
    
    def get_id(self):
        
        """
        Returns item's ID.
        """
        
        if (self.item_id == None) or (type(self.item_id) != str) or (self.item_id == '_') or (self.item_id == '__'):
            self.add_id()
        
        return self.item_id

    def get_metadata(self, select_by_category = None, ignore_nones = True):
        
        """
        Returns item's metadata.
        """
        
        df = self.metadata

        if ignore_nones == True:
            df = df.dropna()

        if type(select_by_category) == str:
            select_by_category = [select_by_category]

        if type(select_by_category) == list:
            output = pd.DataFrame()
            for i in select_by_category:
                masked = df[df['Category'] == i]
                output = pd.concat([masked, output])
            
            df = output

        return df
    
    def get_geolocation_metadata(self, ignore_nones = True):
        
        """
        Returns item's geolocation metadata.
        """
        
        df = self.metadata

        if ignore_nones == True:
            df = df.dropna()
        
        df = df[(df['Category'] == 'coordinates') | (df['Category'] == 'location') | (df['Category'] == 'region')]
        
        return df[['Category', 'Metadata']]

    
    def get_metadata_dict(self, select_by_category = None, ignore_nones = True):
        
        """
        Returns item's metadata as a dictionary.
        """
        
        df = self.get_metadata(select_by_category = select_by_category, ignore_nones = ignore_nones)
        
        output_dict = {}
        for entry in df.index:
            output_dict[df.loc[entry, 'Category']] = df.loc[entry, 'Metadata']
            
        return output_dict
    
    
    def get_metadata_series(self, select_by_category = None, ignore_nones = True):
        
        """
        Returns item's metadata as a Pandas series.
        """
        
        df = self.get_metadata(select_by_category = select_by_category, ignore_nones = ignore_nones)

        if ignore_nones == True:
            df = df.dropna()

        metadata_series = df['Category'].astype(str) + ': ' + df['Metadata'].astype(str)

        return metadata_series
    
    
    def get_metadata_list(self, select_by_category = None, ignore_nones = True):
        
        """
        Returns item's metadata as a list.
        """
        
        return list(self.get_metadata_series(select_by_category = select_by_category, ignore_nones = ignore_nones))
    

    def get_metadata_set(self, select_by_category = None, ignore_nones = True):
        """
        Returns item's metadata as a set.
        """
        return set(self.get_metadata_series(select_by_category = select_by_category, ignore_nones = ignore_nones))
    
    def created_at(self):
        
        """
        Returns item's created at metadata.
        """
        
        return self.metadata[self.metadata['Category'] == 'created_at'].set_index('Category')
    
    def uploaded_at(self):
        
        """
        Returns item's uploaded at metadata.
        """
        
        return self.metadata[self.metadata['Category'] == 'uploaded_at'].set_index('Category')
        
    def last_changed_at(self):
        
        """
        Returns item's last changed at metadata.
        """
        
        return self.metadata[self.metadata['Category'] == 'last_changed_at'].set_index('Category')
    
    def get_time_metadata(self):
        
        """
        Returns all time metadata.
        """
        
        return pd.concat([self.created_at(), self.uploaded_at(), self.last_changed_at()])
    
    
    def get_info(self, select_by_category = None, ignore_nones = True):
        
        """
        Returns item's information.
        """
        
        df = self.information

        if ignore_nones == True:
            df = df.dropna()

        if type(select_by_category) == str:
            select_by_category = [select_by_category]

        if type(select_by_category) == list:
            output = pd.DataFrame()
            for i in select_by_category:
                masked = df[df['Category'] == i]
                output = pd.concat([masked, output])
            
            df = output

        return df
    
    def get_info_series(self, select_by_category = None, ignore_nones = True):
        
        """
        Returns item's information as a Pandas series.
        """
        
        df = self.get_info(select_by_category = select_by_category, ignore_nones = ignore_nones).copy(deep=True)
        df['combined'] = list(zip(df['Label'], df['Category']))
        return df['combined']
    
    def get_info_list(self, select_by_category = None, ignore_nones = True):
        
        """
        Returns item's information as a list of tuples.
        """
        
        df = self.get_info(select_by_category = select_by_category, ignore_nones = ignore_nones).copy(deep=True)
        df['combined'] = list(zip(df['Label'], df['Category']))
        return df['combined'].to_list()
    
    def get_info_set(self, select_by_category = None, ignore_nones = True):
        
        """
        Returns item's information as a set of tuples.
        """
        
        result = set(self.get_info_series(select_by_category = select_by_category, ignore_nones = ignore_nones))
        return result
    
    def get_info_categories(self):
        
        """
        Returns all information categories.
        """
        
        return self.information['Category']
    
    def get_info_categories_list(self):
        
        """
        Returns all information categories as a list.
        """
        
        return self.information['Category'].to_list()
    
    def get_info_categories_set(self):
        
        """
        Returns all information categories as a set.
        """
        
        return set(self.information['Category'])
    
    
    def get_data(self, select_by_type = None, select_by_format = None, ignore_nones = True):

        """
        Returns item's data.
        """
        
        df = item.data

        if ignore_nones == True:
            df = df.dropna()

        if type(select_by_type) == str:
            select_by_type = [select_by_type]
        
        if type(select_by_type) == list:
            output = pd.DataFrame()
            for i in select_by_type:
                masked = df[df['Datatype'] == i]
                output = pd.concat([masked, output])
            
            df = output
        
        if type(select_by_format) == str:
            select_by_format = [select_by_format]
        
        if type(select_by_format) == list:
            output = pd.DataFrame()
            for i in select_by_format:
                masked = df[df['Format'] == i]
                output = pd.concat([masked, output])
            
            df = output
        
        return df
    
    def get_rawdata(self):
        
        """
        Returns all raw data.
        """
        
        return self.data['Raw data']
    
    def get_rawdata_list(self):
        
        """
        Returns all raw data as a list.
        """
        
        return self.get_rawdata().to_list()
    
    def get_rawdata_set(self):
        
        """
        Returns all raw data as a set.
        """
        
        return set(self.get_rawdata())
    
    def get_links(self):
        
        """
        Returns item's links.
        """
        
        return self.links
    
    def get_links_set(self):
        
        """
        Returns item's links as a set.
        """
        
        if self.links == None:
            return set()
        else:
            return set(self.links)
    
    def get_refs(self):
        
        """
        Returns item's references.
        """
        
        return self.references
    
    def get_refs_set(self):
        
        """
        Returns item's references as a set.
        """
        
        if self.references == None:
            return set()
        else:
            return set(self.references)
    
    def get_contents(self):
        
        """
        Returns item's contents.
        """
        
        return self.contains
    
    def get_contents_set(self):
        
        """
        Returns item's contents as a set.
        """
        
        if self.contains == None:
            return set()
        else:
            return set(self.contains)
    
    def get_address(self):
        
        """
        Returns address metadata.
        """
        
        df = self.get_metadata(select_by_category = ['address', 'Address', 'ADDRESS'], ignore_nones = False)

        result = list(set(df['Metadata'].str.lower()))
        
        return result[0]
    
    
    def get_url(self):
        
        """
        Returns URL metadata.
        """
        
        df = self.get_metadata(select_by_category = ['url', 'URL'], ignore_nones = False)

        result_list = list(set(df['Metadata']))
        if len(result_list) > 0:
            result = result_list[0]
        else:
            result = None
        
        return result

    
    def get_coordinates_metadata(self):
        
        """
        Returns coordinates metadata.
        """
        
        df = self.metadata
        
        series = df[df['Category'] == 'coordinates']['Metadata']
        
        if len(series) == 1:
            return series.values[0]
        
        if len(series) > 1:
            return series.to_list()
        
        if len(series) == 0:
            return None
    
    def get_location_metadata(self):
        
        """
        Returns location metadata.
        """
        
        df = self.metadata
        
        series = df[df['Category'] == 'location']['Metadata']
        
        if len(series) == 1:
            return series.values[0]
        
        if len(series) > 1:
            return series.to_list()
        
        if len(series) == 0:
            return None
    
    def get_ip_address_metadata(self):
        
        """
        Returns IP address metadata.
        """
        
        df = self.metadata
        
        series = df[df['Category'] == 'ip_address']['Metadata']
        
        if len(series) == 1:
            return series.values[0]
        
        if len(series) > 1:
            return series.to_list()
        
        if len(series) == 0:
            return None
    
    # Methods for searching item data
    
    def search_metadata(self, search_query = 'request_input'):
        
        """
        Searches metadata for inputted string.
        """
        
        if search_query == 'request_input':
            search_query = input('Search query: ')
        
        if type(search_query) != str:
            raise TypeError('Search query must be a string')
        
        df = self.metadata.copy(deep=True).replace(np.nan, None).dropna().astype(str)
        metadata_result = df[df['Metadata'].str.contains(search_query)]
        category_result = df[df['Category'].str.contains(search_query)]
        
        result = pd.concat([metadata_result, category_result])
        result = result.drop_duplicates().reset_index().drop('index', axis=1)
        
        return result
    
    def search_info(self, search_query = 'request_input'):
        
        """
        Searches information for inputted string.
        """
        
        if search_query == 'request_input':
            search_query = input('Search query: ')
        
        if type(search_query) != str:
            raise TypeError('Search query must be a string')
        
        df = self.information.copy(deep=True).replace(np.nan, None).dropna().astype(str)
        labels_result = df[df['Label'].str.contains(search_query)]
        category_result = df[df['Category'].str.contains(search_query)]
        
        result = pd.concat([labels_result, category_result])
        result = result.drop_duplicates().reset_index().drop('index', axis=1)
        
        return result
    
    def search_data(self, search_query = 'request_input'):
        
        """
        Searches data for inputted string.
        """
        
        if search_query == 'request_input':
            search_query = input('Search query: ')
        
        if type(search_query) != str:
            raise TypeError('Search query must be a string')
            
        search_query = search_query.lower()
        
        df = self.data.copy(deep=True).replace(np.nan, None).dropna()
        
        def df_to_str(item):
            return str(list(item.values()))
        
        try:
            df['Parsed data'] = df['Parsed data'].apply(df_to_str)
        except:
            pass
        
        datatypes_result = df[df['Datatype'].str.lower().str.contains(search_query)]
        formats_result = df[df['Format'].str.lower().str.contains(search_query)]
        rawdata_result = df[df['Raw data'].str.lower().str.contains(search_query)]
        parsed_result = df[df['Parsed data'].str.lower().str.contains(search_query)]
        
        result = pd.concat([datatypes_result, formats_result, rawdata_result, parsed_result])
        result = result.drop_duplicates().reset_index().drop('index', axis=1)
        
        return result
    
    
    def search_links(self, search_query = 'request_input'):
        
        """
        Searches links for inputted string.
        """
        
        if search_query == 'request_input':
            search_query = input('Search query: ')
        
        if type(search_query) != str:
            raise TypeError('Search query must be a string')
            
        search_query = search_query.lower()
        
        all_links = self.links
        
        
        if all_links != None:
            return [i for i in all_links if search_query in i]
        
        else:
            return print('\nNo links found')
    
    def search_refs(self, search_query = 'request_input'):
        
        """
        Searches references for inputted string.
        """
        
        if search_query == 'request_input':
            search_query = input('Search query: ')
        
        if type(search_query) != str:
            raise TypeError('Search query must be a string')
            
        search_query = search_query.lower()
        
        all_refs = self.references
        
        
        if all_refs != None:
            return [i for i in all_refs if search_query in i]
        
        else:
            return print('\nNo references found')
        
        
    def search_contents(self, search_query = 'request_input'):
        
        """
        Searches contents for inputted string.
        """
        
        if search_query == 'request_input':
            search_query = input('Search query: ')
        
        if type(search_query) != str:
            raise TypeError('Search query must be a string')
            
        search_query = search_query.lower()
        
        all_contents = self.contains
        
        if all_contents != None:
            return [i for i in all_contents if search_query in i]
        
        else:
            return print('\nNo contents found')
    
    def search(self, search_query = 'request_input'):
        
        """
        Searches item for inputted string.
        """
        
        if search_query == 'request_input':
            search_query = input('Search query: ')
        
        if type(search_query) != str:
            raise TypeError('Search query must be a string')
            
        search_query = search_query.lower()
        
        metadata_res = self.search_metadata(search_query = search_query)
        metadata_res['Result'] = metadata_res['Metadata']
        metadata_res['Category']
        metadata_res = metadata_res.drop('Metadata', axis=1)
        metadata_res['Found in'] = 'metadata'
        
        info_res = self.search_info(search_query = search_query)
        info_res['Result'] = info_res['Label']
        info_res = info_res.drop('Label', axis=1)
        info_res['Found in'] = 'information'
        info_res = info_res[['Result', 'Category', 'Found in']]
        
        data_res = self.search_data(search_query = search_query)
        data_res['Result'] = 'Raw data: ' +  data_res['Raw data'] + ', Parsed data: ' + data_res['Parsed data']   
        data_res['Category'] = data_res['Datatype'] + ' (format: ' + data_res['Format'] + ')'
        data_res = data_res.drop(['Datatype', 'Format', 'Stored as', 'Size (bytes)', 'Raw data', 'Parsed data'], axis=1)
        data_res['Found in'] = 'data'
        
        links_list = self.search_links(search_query = search_query)
        links_res = pd.DataFrame(columns = ['Result', 'Category', 'Found in'])
        links_res['Result'] = links_list
        links_res['Category'] = 'link'
        links_res['Found in'] = 'links'
        
        refs_list = self.search_refs(search_query = search_query)
        refs_res = pd.DataFrame(columns = ['Result', 'Category', 'Found in'])
        refs_res['Result'] = refs_list
        refs_res['Category'] = 'reference'
        refs_res['Found in'] = 'references'
        
        contents_list = self.search_contents(search_query = search_query)
        contents_res = pd.DataFrame(columns = ['Result', 'Category', 'Found in'])
        contents_res['Result'] = contents_list
        contents_res['Category'] = 'content'
        contents_res['Found in'] = 'contents'
        
        result = pd.concat([metadata_res, data_res, info_res, links_res, refs_res, contents_res])
        result = result[['Result', 'Category', 'Found in']]
        
        return result.reset_index().drop('index', axis=1)
    
    
    # Methods for raw data and handling the results
    
    def parse_rawdata(self, append_to_item = True):
        
        """
        Parses item's rawdata. Adds to data set by default.
        
        Parameters
        ----------
        append_to_item : bool
            whether to add parsed data to item data set.
        
        Returns
        -------
        result : list or pandas.Series
            parsed data.
        """
        
        parsed_list = []

        for i in range(0, len(self.data.index)):
            datatype = self.data.loc[i, 'Datatype']
            raw = self.data.loc[i, 'Raw data']
            parsed = parse_data(raw, datatype, ignore_case = True)
            parsed_list.append(parsed)
        
        if append_to_item == True:
            
            self.data['Parsed data'] = parsed_list
            self.update_properties()
        
            return self.data['Parsed data']
        
        else:
            return parsed_list
    
    
    def extract_links_from_html(self, append_to_item = True):
        
        """
        Extracts links from HTML data. Adds to data set by default.
        
        Parameters
        ----------
        append_to_item : bool
            whether to add extracted links to item data set.
        
        Returns
        -------
        extracted_links : list
            extracted links.
        """
        
        if 'html' in self.data['Datatype'].to_list():

            data = self.data[self.data['Datatype'] == 'html'].copy(deep=True).reset_index()
            html = data.loc[0, 'Raw data']
            soup = BeautifulSoup(html, "html.parser")
            href_select = soup.select("a")
            metadata = self.metadata
            current_url = metadata[metadata['Category'] == 'url'].reset_index().loc[0, 'Metadata']
            extracted_links = [correct_link_errors(source_domain = current_url, url = i['href']) for i in href_select if 'href' in i.attrs]

            if append_to_item == True:

                if type(self.links) != List:
                    self.links = []
                
                self.links = self.links + extracted_links

            return extracted_links
            


    def data_entry_words(self, index_pos = 0, clean = True):
        
        """
        Retrieves words from parsed data entry. Parses data if not parsed.
        
        Parameters
        ----------
        index_pos : int
            dataframe index to retrieve text from.
        clean : bool
            whether to clean text.
        
        Returns
        -------
        words_list : list
            list of words.
        """
        
        df = self.data
        
        if (len(df.index) == 0) or (index_pos not in df.index):
            raise KeyError('Data entry does not exist')
        
        parsed_rows = [i for i in df['Parsed data'] if (i != None)]
        if len(parsed_rows) == 0:
            
            self.parse_rawdata()
        
        if 'words' in df.loc[index_pos, 'Parsed data'].keys():
            
            words_list = df.loc[index_pos, 'Parsed data']['words']

            if clean == True:
                words_list = html_words_cleaner(words_list)
        
        else:
            words_list = []
        
        
        return words_list
    
    
    def data_entry_word_frequencies(self, index_pos = 0, clean = True):
        
        """
        Returns word frequencies from parsed data entry. Parses data if not parsed.
        
        Parameters
        ----------
        index_pos : int
            dataframe index to retrieve text from.
        clean : bool
            whether to clean text.
        
        Returns
        -------
        result : pandas.Series
            words sorted by frequency.
        """
        
        words_list = self.data_entry_words(index_pos = index_pos, clean = clean)
        return pd.Series(words_list).value_counts()
    
    
    def data_entry_word_stats(self, index_pos = 0, clean = True):
        
        """
        Returns word frequency statistics from parsed data entry. Parses data if not parsed.
        
        Parameters
        ----------
        index_pos : int
            dataframe index to retrieve text from.
        clean : bool
            whether to clean text.
        
        Returns
        -------
        result : pandas.Series
            word frequency statistics.
        """
        
        return self.data_entry_word_frequencies(index_pos = index_pos, clean = clean).describe()
    
    def data_entry_most_frequent_words(self, index_pos = 0, clean = True, top = 15):
        
        """
        Returns most frequent words from parsed data entry. Parses data if not parsed.
        
        Parameters
        ----------
        index_pos : int
            dataframe index to retrieve text from.
        clean : bool
            whether to clean text.
        top : int
            how many results to return
        
        Returns
        -------
        result : pandas.Series
            words sorted by frequency.
        """
        
        return self.data_entry_word_frequencies(index_pos = index_pos, clean = clean).head(number)
    
    def get_all_text(self) -> dict:
        
        """
        Returns all parsed text from item. Parses data if not parsed.
        
        Returns
        -------
        result : dict
            dictionary containing full text, sentences, and words.
        """
        
        parsed_set = set(self.data['Parsed data'].astype(str).values)
        if (parsed_set== {'None'}) or (parsed_set== {None}):
            self.parse_rawdata()
        
        text_lol = [i['text'] for i in self.data['Parsed data'] if ((type(i) == dict) and ('text' in i.keys()))]
        text_list = []
        for i in text_lol:
            if type(i) == list:
                text_list = text_list + i
            if type(i) == str:
                text_list.append(i)
        
        text_list = [i for i in text_list if (
                                        (i != ')') 
                                        and (i != ')')
                                        and (i != '')
                                        and (len(i) > 0)
                                        )]
        
        sentences_lol = [i['sentences'] for i in self.data['Parsed data'] if ((type(i) == dict) and ('sentences' in i.keys()))]
        sentences_list = []
        for i in sentences_lol:
            if type(i) == list:
                sentences_list = sentences_list + i
            if type(i) == str:
                sentences_list.append(i)
        
        sentences_list = [i for i in sentences_list if (
                                        (i != ')') 
                                        and (i != ')')
                                        and (i != '')
                                        and (len(i) > 0)
                                        )]
        
        list_of_wordlists = [
                        i['words'] for i in self.data['Parsed data'] if (
                                                                        (i != None) 
                                                                        and (type(i) == dict) 
                                                                        and ('words' in i.keys())
                                                                        )
                        ]
    
        words_list = []
        for i in list_of_wordlists:
            words_list = words_list + i
        
        result = {'text': text_list, 'sentences': sentences_list, 'words': words_list}
        
        
        return result
    
    
    def get_all_words(self, clean = True):
        
        """
        Returns all parsed words from item. Parses data if not parsed.
        
        Returns
        -------
        words_list : list
            list of words.
        """
        
        parsed_set = set(self.data['Parsed data'].astype(str).values)
        if (parsed_set== {'None'}) or (parsed_set== {None}):
            self.parse_rawdata()
            
        list_of_lists = [
                        i['words'] for i in self.data['Parsed data'] if (
                                                                        (i != None) 
                                                                        and (type(i) == dict) 
                                                                        and ('words' in i.keys())
                                                                        )
                        ]
    
        words_list = []
        for i in list_of_lists:
            words_list = words_list + i
    
        return words_list
    
    

    # Methods for retrieving word stats
    
    def get_word_frequencies(self, clean = True):
        
        """
        Returns word frequencies from item's data. Parses data if not parsed.
        
        Parameters
        ----------
        clean : bool
            whether to clean text.
        
        Returns
        -------
        result : pandas.DataFrame
            dataframe of word frequencies.
        """
        
        series = pd.Series(self.get_all_words(clean = clean), dtype = 'object').value_counts()
        df = pd.DataFrame(series, columns=['frequency'])
        df.index.name = 'word'

        return df
    
    
    def get_word_stats(self, clean = True):
        
        """
        Returns word frequency statistics from item's data. Parses data if not parsed.
        
        Parameters
        ----------
        clean : bool
            whether to clean text.
        
        Returns
        -------
        result : pandas.DataFrame
            dataframe of word frequencies.
        """
        
        return self.get_word_frequencies(clean = clean).describe()
    
    def get_most_frequent_words(self, clean = True, top = 15):
        
        """
        Returns most frequent words from item's data. Parses data if not parsed.
        
        Parameters
        ----------
        clean : bool
            whether to clean text.
        top : int
            how many results to return.
        
        Returns
        -------
        result : pandas.DataFrame
            dataframe of word frequencies.
        """
        
        return self.get_word_frequencies(clean=clean).head(top)
    
    def get_words_set(self, clean = True):
        
        """
        Returns item's words with repeats removed. Parses data if not parsed.
        
        Parameters
        ----------
        clean : bool
            whether to clean text.
        
        Returns
        -------
        result : set
            set of words.
        """
        
        return set(self.get_all_words(clean = clean))
    
    # Methods for extracting information from raw text and adding it to info set
    
    def extract_names(self, names_source = 'all_personal_names'):
        
        """
        Extracts names from text data. Uses list of all personal names by default. Parses data if not parsed.
        
        Parameters
        ----------
        names_source : str or list
            key for names corpus to use; or names corpus as list. Defaults to 'all_personal names'.
        
        Returns
        -------
        names : list
            extracted names.
        """
        
        try:
            words = self.get_all_words()

        except:
            self.parse_rawdata()
            words = self.get_all_words()

        names = extract_names(words = words, source = names_source)

        return names
    

    def infer_names(self, names_source = 'all_personal_names'):
        
        """
        Identifies names from text data and adds to item information. Uses list of all personal names by default. Parses data if not parsed.
        
        Parameters
        ----------
        names_source : str or list
            key for names corpus to use; or names corpus as list. Defaults to 'all_personal names'.
        """
        
        names = self.extract_names(names_source = names_source)

        for n in names:
            self.add_info(info = n, info_category = 'names', suppress_warnings = True)
    

    def extract_countries(self, language = 'all'):
        
        """
        Extracts country names from text data. Uses list of all country names by default. Parses data if not parsed.
        
        Parameters
        ----------
        language : str or list
            language of country names corpus to use; or country names corpus as list. Defaults to 'all'.
        
        Returns
        -------
        countries : list
            extracted country names.
        """
        
        try:
            words = self.get_all_words()

        except:
            self.parse_rawdata()
            words = self.get_all_words()

        countries = extract_countries(words, language = language)

        return countries
    

    def infer_countries(self, language = 'all'):
        
        """
        Identifies country names from text data and adds to item information. Uses list of all country names by default. Parses data if not parsed.
        
        Parameters
        ----------
        language : str or list
            language of country names corpus to use; or country names corpus as list. Defaults to 'all'.
        """
        
        countries = self.extract_countries(language = language)

        for c in countries:
            self.add_info(info = c, info_category = 'countries', suppress_warnings = True)
    

    def extract_cities(self, language = 'all'):
        
        """
        Extracts city names from text data. Uses list of all city names by default. Parses data if not parsed.
        
        Parameters
        ----------
        language : str or list
            language of city names corpus to use; or city names corpus as list. Defaults to 'all'.
        
        Returns
        -------
        cities : list
            extracted city names.
        """
        
        try:
            words = self.get_all_words()

        except:
            self.parse_rawdata()
            words = self.get_all_words()

        cities = extract_cities(words, language = language)

        return cities
    

    def infer_cities(self, language = 'all'):
        
        """
        Identifies city names from text data and adds to item information. Uses list of all city names by default. Parses data if not parsed.
        
        Parameters
        ----------
        language : str or list
            language of city names corpus to use; or city names corpus as list. Defaults to 'all'.
        """
        
        cities = self.extract_cities(language = language)

        for c in cities:
            self.add_info(info = c, info_category= 'cities', suppress_warnings = True)
    

    def extract_languages(self, language = 'all'):
        
        """
        Extracts language names from text data. Uses list of all language names by default. Parses data if not parsed.
        
        Parameters
        ----------
        language : str or list
            language of language names corpus to use; or language names corpus as list. Defaults to 'all'.
        
        Returns
        -------
        languages : list
            extracted language names.
        """
        
        try:
            words = self.get_all_words()

        except:
            self.parse_rawdata()
            words = self.get_all_words()

        languages = extract_languages(words, language = language)

        return languages
    

    def infer_languages(self, language = 'all'):
        
        """
        Identifies language names from text data and adds to item information. Uses list of all language names by default. Parses data if not parsed.
        
        Parameters
        ----------
        language : str or list
            language of language names corpus to use; or language names corpus as list. Defaults to 'all'.
        """
        
        languages = self.extract_languages(language = language)

        for l in languages:
            self.add_info(info = l, info_category = 'languages', suppress_warnings = True)
    

    # Methods for analysing time differences between item and other items
    
    def created_changed_time_difference(self):
        
        """
        Returns the time difference between date-time created and last changed.
        
        Returns
        -------
        time_difference : datetime.timedelta
            time difference.
        """
        
        try:
            dt1 = self.get_metadata('created_at')['Metadata'].values[0]
        except:
            raise ValueError('Item has no created date-time')
        
        try:
            dt2 = self.get_metadata('last_changed_at')['Metadata'].values[0]
        except:
            dt2 = dt1
            
        return time_difference(dt1, dt2)
    
    
    def created_uploaded_time_difference(self):
        
        """
        Returns the time difference between date-time uploaded and last changed.
        
        Returns
        -------
        time_difference : datetime.timedelta
            time difference.
        """
        
        try:
            dt1 = self.get_metadata('created_at')['Metadata'].values[0]
        except:
            raise ValueError('Item has no created date-time')
        
        try:
            dt2 = self.get_metadata('uploaded_at')['Metadata'].values[0]
        except:
            dt2 = dt1
            
        return time_difference(dt1, dt2)
    
    

    def plot_metadata_timeline(self, units = 'months', intervals = 4, date_format = '%d.%m.%Y', colour = 'blue'):
        
        """
        Returns a plot of the item's date-time metadata.
        """
        
        plot = 'metadata'
        
        df = self.get_time_metadata().dropna()
        
        names = df.index.to_list()
        dates = df['Metadata'].to_list()
        
        plot_timeline(dates = dates, names = names, plot = plot, units = units, intervals = intervals, date_format = date_format, colour = colour)
        
    

    # Methods for analysing distance between item and other items
    
    def coordinates_distance(self, item, units = 'kilometers'):
        
        """
        Returns the geographic distance between item and another item using their coordinates.
        
        Parameters
        ----------
        item : CaseItem
            case item to compare with.
        units : str
            unit for measurement.
        
        Returns
        -------
        coordinates_distance : int
            distance in unit specified by user; defaults to 'kilometers'.
        """
        
        first_item_id = self.get_id()
        first_coordinates = self.get_coordinates_metadata()
        if first_coordinates == None:
            raise ValueError(f'{first_item_id} does not have coordinates metadata')
        
        second_item_id = item.get_id()
        second_coordinates = item.get_coordinates_metadata()
        if second_coordinates == None:
            raise ValueError(f'{second_item_id} does not have coordinates metadata')
        
        return coordinates_distance(first_coordinates, second_coordinates, units = units)
    
    
    def locations_distance(self, item, units = 'kilometers'):
        
        """
        Returns the geographic distance between item and another item using their locations.
        
        Parameters
        ----------
        item : CaseItem
            case item to compare with.
        units : str
            unit for measurement.
        
        Returns
        -------
        coordinates_distance : int
            distance in unit specified by user; defaults to 'kilometers'.
        """
        
        first_item_id = self.get_id()
        first_location = self.get_location_metadata()
        if first_location == None:
            raise ValueError(f'{first_item_id} does not have location metadata')
        
        second_item_id = item.get_id()
        second_location = item.get_location_metadata()
        if second_location == None:
            raise ValueError(f'{second_item_id} does not have location metadata')
        
        first_coordinates = get_location_coordinates(first_location)
        second_coordinates = get_location_coordinates(second_location)

        return coordinates_distance(first_coordinates = first_coordinates, second_coordinates = second_coordinates, units = units)

    

    # Methods for web crawling and website analysis
    
    def crawl_web_from_url(
                            self,
                            visit_limit = 5, 
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
        Runs web crawl from item's URL metadata.
        
        Parameters
        ---------- 
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
        output_as : str
            the format to output results in. Defaults to a pandas.DataFrame.
        
        Returns
        -------
        result : object
            an object containing the results of a crawl.
        """
        
        seed_url = self.get_url()
        
        output = crawl_web(
                            seed_urls = seed_url,
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
        
        return output
    
    def crawl_web(
                            self,
                            crawl_from = 'request_input',
                            visit_limit = 5, 
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
        Runs web crawl from URL or list of URLs.
        
        Parameters
        ---------- 
        crawl_from : str or list
            one or more URLs from which to crawl. Defaults to requesting user input.
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
        output_as : str
            the format to output results in. Defaults to a pandas.DataFrame.

        Returns
        -------
        result : object
            an object containing the results of a crawl.
        """
        
        if crawl_from == 'request_input':
            crawl_from = input('Metadata entry to crawl from: ')
        
        seed_urls = list(self.get_metadata(crawl_from)['Metadata'].values)
        
        output = crawl_web(
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
        
        return output
    
    
    def crawl_web_links(
                            self,
                            visit_limit = 5, 
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
        Runs web crawl from item's links.
        
        Parameters
        ---------- 
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
        output_as : str
            the format to output results in. Defaults to a pandas.DataFrame.

        Returns
        -------
        result : object
            an object containing the results of a crawl.
        """
        
        seed_urls = self.links
        
        output = crawl_web(
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
        
        return output
    
    
    def fetch_sitemap(self):
        
        """
        Fetches item URL's sitemap.

        Returns
        -------
        result : list
            list of fetched URLs.
        """
        
        url = self.get_url()
        return fetch_sitemap(url)
    
    def crawl_site_contents(self):
        
        """
        Runs internal site crawl on item's URL metadata.
        """
        
        url = self.get_url()
        return crawl_site(url)
    
    
    
    def fetch_site_contents(self, append_to_item = True):
        
        """
        Fetches list of item URL's website contents.

        Parameters
        ----------
        append_to_item : bool
            whether to append to item's contents set.
        
        Returns
        -------
        contents : list
            list of URLs contained by website.
        """
        
        source = self.get_url().replace('https://', '').replace('http://', '').replace('www.', '')
        
        site_map = self.fetch_sitemap()
        site_map_set = set(site_map)
        
        site_crawl = self.crawl_site_contents()
        site_crawl_set = set(site_crawl)
        
        result = list(
                        site_map_set.union(site_crawl_set)
                        )
        
        contents = [link for link in result if (source in link)]
        
        if append_to_item == True:
            self.contents = contents
        
        return contents
        
    def fix_links_str(self):
        
        """
        Checks if item links are stored as a string; if yes, converts to a list.
        """
        
        links = self.links
        
        if type(links) == str:
            links = links.replace('[', '').replace(']', '').replace('"', '').replace("'", "").replace(' ', '').strip().split(',')
            self.links = links
    
    
    def scrape_url(self):
        
        """
        Scrapes data from item URL's site.
        
        Returns
        -------
        result
            site data.
        """
        
        url = self.get_url()
        return scrape_url(url)
    
    
    def scrape_url_links(self):
        
        """
        Scrapes links from item URL's site.
        
        Returns
        -------
        links : list
            list of links.
        """
        
        url = self.get_url()
        links = scrape_url_links(url)

        return links
    
    
    def extract_links_from_source(self):
        
        """
        Extracts links from item data. 
        
        Parameters
        ----------
        language : str or list
            language of language names corpus to use; or language names corpus as list. Defaults to 'all'.
        
        Returns
        -------
        languages : list
            extracted language names.
        """
        
        current_url = self.metadata[self.metadata['Category'] == 'url'].copy(deep=True).reset_index().loc[0, 'Metadata']
        links = []
        
        if 'html' in self.data['Datatype']:
            
            data = self.data[self.data['Datatype'] == 'html'].copy(deep=True).reset_index().loc[0, 'Raw data']
            current_url = self.metadata[self.metadata['Category'] == 'url'].copy(deep=True).reset_index().loc[0, 'Metadata']
            
            
            soup = BeautifulSoup(scraped_data['html'], "html.parser")
            href_select = soup.select("a")  
            links = {correct_link_errors(source_domain = current_url, url = i['href']) for i in href_select if 'href' in i.attrs}
       
            
        else:
            
            if 'text' in self.data['Datatype']:
            
                text = self.data[self.data['Datatype'] == 'text'].copy(deep=True).reset_index().loc[0, 'Raw data']
                text = text.lower()
                if (
                    ('https://' in text)
                    or ('http://' in text)
                    or ('www.' in text)
                    or ('.co' in text)
                    or ('.gov' in text)
                    or ('.gov' in text)
                    ):
            
                    # Cleaning text
                    text = text.replace(' /', '/').replace(': ', ':').replace(' :', ':').replace('\n', ' ').replace('’', ' ').replace(';', ' ').replace(',', ' ').replace('|', ' ').replace('[', ' ').replace(']', ' ').replace('}', ' ').replace('{', ' ').replace('"', ' ').replace("'", ' ').replace('□', ' ').replace('“', ' ').replace('”', ' ').replace('^', ' ').replace('©', ' ').replace('   ', '').replace('  ', ' ')

                    # Splitting text into strings
                    text_split = text.split(' ')

                    # Extracting potential links
                    links_res = [
                            i for i in text_split if (
                                                    ('https:' in i.lower()) 
                                                    or ('http:' in i.lower()) 
                                                    or ('www.' in i.lower())
                                                    or ('.com' in i.lower())
                                                    or ('.org' in i.lower())
                                                    or ('.net' in i.lower())
                                                    or ('.io' in i.lower())
                                                    or ('.co.uk' in i.lower())
                                                    or ('.co' in i.lower())
                                                    or ('.gov' in i.lower())
                                                    )
                                    ]
            
                    # Cleaning links
                    links = {i.strip(')').strip('(').strip('source:').strip('See:').strip('vSee:').strip('Abstract').strip('Guard.iii').strip(':') for i in links_res}
                    links = {correct_link_errors(source_domain = current_url, url = i) for i in links}
       
            else:
                raise ValueError('No text or html data found')
            
        links = list(links)
        
        return links
                
        
    # Methods for analysing and looking up IP address data, coordinates metadata, and location metadata
    
    def get_ip_metadata_geocode(self):
        
        """
        Returns geocode associated with IP address metadata.
        """
        
        item_id = self.get_id()
        
        ip = self.get_ip_address_metadata()
        if ip == None:
            raise ValueError(f'{item_id} does not have IP address metadata')
            
        return get_ip_geocode(ip_address = ip)

    
    def get_ip_metadata_coordinates(self):
        
        """
        Returns coordinates associated with IP address metadata.
        """
        
        item_id = self.get_id()
        
        ip = self.get_ip_address_metadata()
        if ip == None:
            raise ValueError(f'{item_id} does not have IP address metadata')
        
        return get_ip_coordinates(ip_address = ip)
    
    def get_ip_metadata_physical_location(self):
        
        """
        Returns location associated with IP address metadata.
        """
        
        item_id = self.get_id()
        
        ip = self.get_ip_address_metadata()
        if ip == None:
            raise ValueError(f'{item_id} does not have IP address metadata')
            
        return get_ip_physical_location(ip_address = ip)

    def lookup_coordinates_metadata(self, site = 'Google Maps'):
        
        """
        Launches search for coordinates associated with IP address metadata in default browser.
        """
        
        item_id = self.get_id()
        coordinates = self.get_coordinates_metadata()
        if coordinates == None:
            raise ValueError(f'{item_id} does not have coordinates metadata')

        if type(coordinates) == str:
            coordinates = coordinates.split(',')

        if type(coordinates) != list:
            raise TypeError('Coordinates must be strings or lists')

        latitude = str(coordinates[0]).strip()
        longitude = str(coordinates[1]).strip()

        try:
            return lookup_coordinates(latitude = latitude, longitude = longitude, site = site)
        except:
            raise ValueError(f"Lookup failed. Please check {item_id}'s coordinates metadata")
            
    def lookup_ip_metadata_location(self, site = 'Google Maps'):
        
        """
        Launches search for location associated with IP address metadata in default browser.
        """
        
        item_id = self.get_id()
        ip_address = self.get_ip_address_metadata()
        if ip_address == None:
            raise ValueError(f'{item_id} does not have IP address metadata')

        try:
            return lookup_ip_coordinates(ip_address = ip_address, site = site)
        except:
            raise ValueError(f"Lookup failed. Please check {item_id}'s IP address metadata")

            
    def lookup_location_metadata(self, site = 'Google Maps'):
        
        """
        Launches search for location associated with item's location metadata in default browser.
        """
        
        item_id = self.get_id()
        location = self.get_location_metadata()
        if location == None:
            raise ValueError(f'{item_id} does not have location metadata')

        try:
            return lookup_location(location = location, site = site)
        except:
            raise ValueError(f"Lookup failed. Please check {item_id}'s location metadata")
            
    
    def lookup_domain(self):
        
        """
        Runs WhoIs lookup on item's domain metadata.
        """
        
        domain = self.get_metadata('domain')
        ip_address = self.metadata[self.metadata['Category'] == 'ip_address'].copy(deep=True).reset_index().loc[0, 'Metadata']
        
        if len(domain.index) > 0:
            domain = domain.reset_index().loc[0, 'Metadata']
        
        if domain == None:
            domain = domain_splitter(self.get_url())
        
        if (domain == None) and (ip_address != None):
            domain = domain_from_ip(ip_address)[1]
            dom_loc = self.metadata[self.metadata['Category'] == 'domain'].index
            self.metadata.loc[dom_loc, 'Metadata'] = domain
        
        if (ip_address == None) and (domain != None):
            ip_address = ip_from_domain(domain)
            ip_loc = self.metadata[self.metadata['Category'] == 'ip_address'].index
            self.metadata.loc[ip_loc, 'Metadata'] = ip_address
            
        return lookup_whois(domain)
    
    
    def domain_metadata_is_registered(self):
        
        """
        Checks whether the item's `domain_name` metadata is registered.
        """
        
        domain = self.get_metadata('domain')
        if len(domain.index) > 0:
            domain = domain.reset_index().loc[0, 'Metadata']
        
        if domain == None:
            return None
        
        return is_registered_domain(domain)
    
    
    def lookup_ip(self):
        
        """
        Runs WhoIs lookup on item's IP address metadata.
        """
        
        metadata = self.metadata
        ip_address = metadata[metadata['Category'] == 'ip_address'].reset_index().loc[0, 'Metadata']
        
        if ip_address == None:
            
            try:
                domain = self.get_metadata('domain').reset_index().loc[0, 'Metadata']
            except:
                domain = None
            
            if domain != None:
                ip_address = ip_from_domain(domain)
            
                cat_loc = self.metadata[self.metadata['Category'] == 'ip_address'].index
                self.metadata.loc[cat_loc, 'Metadata'] = ip_address
        
        return lookup_whois(ip_address)
    
    
    def lookup_whois(self, append_to_item = False):
        
        """
        Runs WhoIs lookup on item's internet metadata.
        """
        
        metadata = self.metadata
        address = metadata[metadata['Category'] == 'url'].reset_index().loc[0, 'Metadata']
        domain = metadata[metadata['Category'] == 'domain'].reset_index().loc[0, 'Metadata']
        ip_address = metadata[metadata['Category'] == 'ip_address'].reset_index().loc[0, 'Metadata']
        
        if (address != None) and (type(address) == str):
            
            address = address.strip('/').strip('.').strip()
            
            try:
                result = lookup_domain(address)
            except:
                
                    try:
                        domain = domain.replace('https://', '').replace('http://', '').strip('/').strip('.').strip()
                        result = lookup_domain(domain)
                    except:
                        
                        try:
                            result = lookup_ip(ip_address)
                        except:
                            pass
        
        else:
            if (domain != None) and (type(domain) == str):
                
                domain = domain.replace('https://', '').replace('http://', '').strip('/').strip('.').strip()
            
                try:
                    result = lookup_domain(domain)
                except:
                    try:
                        result = lookup_ip(ip_address)
                    except:
                        pass
            
            elif (ip_address != None) and (type(ip_address) == str):
                
                try:
                    result = lookup_ip(ip_address)
                except:
                    pass
        
            
        if append_to_item == True:
            self.whois = result
        
        return result

    # Methods for looking up item links and addresses
    
    def lookup_url(self):
        
        """
        Opens item's URL in default browser.
        """
        
        address = self.get_url()
        return regex_check_then_open_url(url = address)


    def lookup_link(self, link_index):
        
        """
        Opens item link in default browser. Takes an index.
        """
        
        self.fix_links_str()
        link = self.links[link_index]
        
        if link == None:
            return (print('This function requires one or more valid links'))
        
        link = link.strip().strip('/').strip('#').strip('.').strip()
        return regex_check_then_open_url(url = link)

            
    def open_all_links(self):
        
        """
        Opens all item links in default browser.
        """
        
        self.fix_links_str()
        links = self.links
        links_len = len(links)
        
        for i in range(0, links_len):
            self.lookup_link(link_index = i)
    
    
    def filter_links(self, 
                    contains_any_kwds = None, 
                    contains_all_kwds = None,
                    not_containing_any_kwds = None,
                    not_containing_all_kwds = None
                    ):
        
        """
        Selects item links based on provided criteria.
        
        Parameters
        ----------
        contains_any_kwds : list
            links must contain any of these strings.
        contains_all_kwds : list
            links must contain all of these strings.
        not_containing_any_kwds : list
            links must not contain any of these strings.
        not_containing_all_kwds : list
            links must not contain all of these strings.
        
        Returns
        -------
        selected_links : list
            selected links.
        """
        
        self.fix_links_str()
        
        links = self.links
        
        selected_links = []
        
        for link in links:
            
            any_kwds = True
            all_kwds = True
            not_any_kwds = True
            not_all_kwds = True
            
            if contains_any_kwds != None:
                any_kwds = False
                for i in contains_any_kwds:
                    if i in link:
                        any_kwds = True
            
            if contains_all_kwds != None:
                all_kwds = True
                for i in contains_all_kwds:
                    if i not in link:
                        all_kwds = False
            
            if not_containing_any_kwds != None:
                not_any_kwds = True
                for i in not_containing_any_kwds:
                    if i in link:
                        not_any_kwds = False
            
            if not_containing_all_kwds != None:
                not_all_kwds = False
                for i in not_containing_all_kwds:
                    if i not in link:
                        not_any_kwds = True
            
            if (
                (any_kwds == True)
                and (all_kwds == True)
                and (not_any_kwds == True)
                and (not_all_kwds == True)
                ):
            
                selected_links.append(link)
        
        return selected_links
    
    
    
    def open_filtered_links(
                            self, 
                            contains_any_kwds = None,
                            contains_all_kwds = None,
                            not_containing_any_kwds = None,
                            not_containing_all_kwds = None
                             ):
        
        """
        Selects and opens item links based on provided criteria in default browser.
        
        Parameters
        ----------
        contains_any_kwds : list
            links must contain any of these strings.
        contains_all_kwds : list
            links must contain all of these strings.
        not_containing_any_kwds : list
            links must not contain any of these strings.
        not_containing_all_kwds : list
            links must not contain all of these strings.
        """
        
        filtered_links = self.filter_links(
                              contains_any_kwds = contains_any_kwds, 
                              contains_all_kwds = contains_all_kwds,
                              not_containing_any_kwds = not_containing_any_kwds,
                             not_containing_all_kwds = not_containing_all_kwds
                             )
        
        for link in filtered_links:
            link = link.strip().strip('/').strip('#').strip('.').strip()
            regex_check_then_open_url(url = link)

# Functions for assigning the results of PDF parsing to item

def parsed_pdf_to_item(parsed_pdf):
    
    """
    Creates CaseItem from parsed PDF reader result. 
    """
    
    item_id = parsed_pdf['title']
    item = CaseItem(item_id)
    
    item.metadata = item.metadata.astype(object)
    item.metadata.loc[0] = [parsed_pdf['title'], 'name']
    item.metadata.loc[1] = ['document', 'type']
    item.metadata.loc[2] = ['PDF', 'format']
    try:
        item.metadata.loc[3] = [parsed_pdf['attached_metadata']['/CreationDate'], 'created_at']
    except:
        item.metadata.loc[3] = [parsed_pdf['date'], 'created_at']
    
    try:
        item.metadata.loc[3] = [parsed_pdf['attached_metadata']['/ModDate'], 'last_changed_at']
    except:
        item.metadata.loc[3] = [None, 'last_changed_at']
    
    item.data = item.data.astype(object)
    item.data.at[0, 'Datatype'] = 'text'
    item.data.at[0, 'Format'] = 'PDF'
    item.data.at[0, 'Stored as'] = type(parsed_pdf['full_text'])
    item.data.at[0, 'Size (bytes)'] = sys.getsizeof(parsed_pdf['full_text'])
    item.data.at[0, 'Raw data'] = parsed_pdf['full_text']
    item.data.at[0, 'Parsed data'] = None
    
    item.links = parsed_pdf['links']
    
    return item

def pdf_to_item(file_path = None):
    
    """
    Creates CaseItem from PDF file.
    """
    
    parsed_pdf = read_pdf(file_path = file_path)
    item = parsed_pdf_to_item(parsed_pdf = parsed_pdf)
    
    return item

def pdf_url_to_item(url = None):
    
    """
    Creates CaseItem from PDF URL.
    """
    
    parsed_pdf = read_pdf_url(url = url)
    item = parsed_pdf_to_item(parsed_pdf = parsed_pdf)
    
    return item

class CaseItemSet(CaseObjectSet):
    
    """This is a collection of CaseItems. 
    
    Parameters
    ----------
    obj_name : str
        ID used for item set.
    parent_obj_path : str
        if item set is an attribute, object path of the parent object. Defaults to None.
    items : list
        iterable of CaseItems to assign to CaseItemSet.
    
    Notes
    -----
        * Subclass of CaseObjectSet class.
        * Intended to assigned to all Case objects.
    """
    
    def __init__(self, obj_name = None, parent_obj_path = None, items: list = []):
        
        """
        Initialises CaseItemSet instance.
        
        Parameters
        ----------
        obj_name : str
            ID used for item set.
        parent_obj_path : str
            if item set is an attribute, object path of the parent object. Defaults to None.
        items : list
            iterable of CaseItems to assign to CaseItemSet.
        """
        
        # Inheriting methods and attributes from CaseObjectSet class
        super().__init__(obj_name = obj_name, obj_type = 'CaseItemSet', parent_obj_path = parent_obj_path)
        
        # Setting item properties
        self.properties = CaseObjectProperties(obj_name = obj_name, obj_type = 'CaseItemSet', parent_obj_path = parent_obj_path, size = None)
        
        # If only one item is provided, wrapping as list
        if type(items) == CaseItem:
            items = [items]
        
        # Adding items if provided
        for i in items:
            self.add_item(i)
        
        # Updating properties
        self.update_properties()
    
    
    # Methods for editing and retrieving item set properties
    
    def update_properties(self):
        
        """
        Updates CaseItemSet's properties.
        
        Updates
        -------
            * obj_id
            * obj_size
            * items
            * item_count
            * last_changed
            * hash
        """
        
        self.properties.obj_id = id(self)
        self.properties.item_count = len(self.contents())
        self.properties.items = self.ids()
        self.properties.obj_size = str(self.__sizeof__()) + ' bytes'
        self.properties.update_last_changed()
        self.properties.hash = self.__hash__()
        
    def __repr__(self):
        
        """
        Defines how CaseItemSets are represented in string form.
        """
        
        contents = self.contents()
        output = f'\nItem count: {self.properties.item_count}\n\n'
        
        index = 0
        for item_id in contents:
            output = output + f'[{str(index)}] {item_id}\n'
            index += 1
            
        return output
    
            
    def __setitem__(self, key, item):
        
        """
        Adding CaseItem to collection using a key name.
        
        WARNING: will not allow user to set 'properties' attribute.
        """
        
        if type(item) != CaseItem:
            raise TypeError('Key value assignment requires a CaseItem object')
            
        self.__dict__[key] = item
        self.update_properties()
        
    def __delitem__(self, key):
        
        """
        Deletes CaseItem in collection using its key.
        
        WARNING: will not allow user to delete collection's 'properties' attribute.
        """
        
        if key != 'properties':
            
            delattr(self, key)
            self.update_properties()
        

    def count_items(self):
        
        """
        Returns the number of CaseItems in the collection.
        """
        
        return len(self.contents())
    
    def __add__(self, obj):
        
        """
        Function for controlling addition operations on CaseItemSets.
        
        Notes
        -----
            * CaseItemSets can only have CaseItems or other CaseItemSets added to them.
            * Adding a CaseItem to a set will add that item to the set's collection of items.
            * Adding a CaseItemSet to another CaseItemSet will produce a new CaseItemSet that includes both sets' items. 
        """
        
        new_item_set = self.copy()
        
        if (type(obj) == CaseItem) or (CaseItem in obj.__class__.__bases__):
        
            new_item_set.add_item(obj)
            new_item_set.update_properties()
            return new_item_set
        
        if (type(obj) == CaseItemSet) or (CaseItemSet in obj.__class__.__bases__):
            
            contents = new_item_set.contents()
            
            for item_id in obj.contents():
                item = obj.__dict__[item_id]
                if item_id not in contents:
                    new_item_set.__dict__[item_id] = item
                else:
                    item_id = item_id + '_copy'
                    new_item_set.__dict__[item_id] = item
                    
            new_item_set.update_properties()
            return new_item_set
        
        else:
            raise TypeError(f'{str(type(obj))} objects cannot be added to CaseItemSets.')


    # Methods for adding items to item set
    
    def add_blank_item(self, item_id = None):
        
        """
        Adds a blank item to the item set. Returns the item.
        
        Parameters
        ----------
        item_id : str
            the item's ID. This will become its attribute name.
        
        Returns
        -------
        item : CaseItem
            the new blank item.
        """
        
        if item_id == None:
                item_code = self.count_items() + 1
                item_id = 'item_' + str(item_code)

        if item_id == 'request_input':
                item_id = input('New item ID: ')

        self.__dict__[item_id] = CaseItem(item_id = item_id, parent_obj_path = self.properties.obj_path)
        self.update_properties()
        
        return self.get_item(item_id)
    
    
    
    def add_item(self, item = None, item_id = None):
        
        """
        Adds an item to the item set. Returns the item.
        
        Parameters
        ----------
        item : CaseItem
            the item to be added. Defaults to None; this adds a blank item.
        item_id : str
            the item's ID. This will become its attribute name. Defaults to None.
            If none set, tries to retrieve details from item's properties.
        
        Returns
        -------
        item : CaseItem
            the added item.
        """
        
        if item == None:
            return self.add_blank_item(item_id = item_id)
            
        if type(item) != CaseItem:
            raise TypeError('Item must be of type "CaseItem"')
        
        if item in self.__dict__.values():
            raise ValueError('Item is already in items')
        
        if item_id == None:
            item_id = item.get_id()
        
        if item_id in self.contents():
            item_id = item_id + ".copy"
        
        item.properties.obj_path = self.properties.obj_path + '.' + item.properties.obj_name
        
        self.__dict__[item_id] = item
        self.update_properties()
        
        return self.get_item(item_id)
    
    
    # Methods for deleting items from item set
    
    def delete_item(self, item: CaseItem = None, item_id: str = None):
        
        """
        Deletes an item from the item set. Takes either an item or an item ID.
        """
        
        if item_id == None:
            if item != None:
                item_id = item.get_id()
        
        delattr(self, item_id)
        self.update_properties()
        
    
    def delete_all(self):
        
        """
        Deletes all items from the item set.
        """
        
        ids = self.contents()
        for item_id in ids:
            self.delete_item(item_id)
            
        self.update_properties()
            
    
    def delete_all_metadata(self):
        
        """
        Deletes all metadata from items.
        """
        
        ids = self.contents()
        for item_id in ids:
            self.get_item(item_id).delete_metadata()
            self.get_item(item_id).update_properties()
        self.update_properties()
            
        
    def delete_metadata_category(self, category = 'request_input'):
        
        """
        Deletes all metadata from items if tagged with a specified category.
        """
        
        if category == 'request_input':
            category = input('Category to delete: ')
        
        ids = self.contents()
        for item_id in ids:
            self.get_item(item_id).delete_metadata_by_category(category = category)
            self.get_item(item_id).update_properties()
        
        self.update_properties()
            
        
    
    def delete_all_data(self):
        
        """
        Deletes all data from items.
        """
        
        ids = self.contents()
        for item_id in ids:
            self.get_item(item_id).delete_data()
            self.get_item(item_id).update_properties()
        
        self.update_properties()
        
    
    def delete_datatype(self, datatype = 'request_input'):
        
        """
        Deletes all instances of a specified data type from items.
        """
        
        if datatype == 'request_input':
            datatype = input('Datatype to delete: ')
        
        ids = self.contents()
        for item_id in ids:
            self.get_item(item_id).delete_data_by_datatype(datatype = datatype)
            self.get_item(item_id).update_properties()
            
        self.update_properties()
    
    
    def delete_data_format(self, data_format = 'request_input'):
        
        """
        Deletes all instances of a specified data format from items.
        """
        
        if data_format == 'request_input':
            data_format = input('Data format to delete: ')
        
        ids = self.contents()
        for item_id in ids:
            self.get_item(item_id).delete_data_by_format(data_format = data_format)
            self.get_item(item_id).update_properties()
            
        self.update_properties()
    
    def delete_rawdata(self, rawdata = 'request_input'):
        
        """
        Deletes all raw data from items.
        """
        
        if rawdata == 'request_input':
            rawdata = input('Raw data to delete: ')
        
        ids = self.contents()
        for item_id in ids:
            self.get_item(item_id).delete_if_rawdata(data_format = rawdata)
            self.get_item(item_id).update_properties()
            
        self.update_properties()
        
    
    def delete_all_info(self):
        
        """
        Deletes all information from items.
        """
        
        ids = self.contents() 
        for item_id in ids:
            self.get_item(item_id).delete_info()
            self.get_item(item_id).update_properties()
            
        self.update_properties()
    
    def delete_info_category(self, category = 'request_input'):
        
        """
        Deletes all information from items if tagged with a specified category.
        """
        
        if category == 'request_input':
            category = input('Category to delete: ')
        
        ids = self.contents()
        for item_id in ids:
            self.get_item(item_id).delete_info_by_category(category = category)
            self.get_item(item_id).update_properties()
            
        self.update_properties()
    
    def delete_info_label(self, label = 'request_input'):
        
        """
        Deletes all information from items if it matches an inputted string.
        """
        
        if label == 'request_input':
            label = input('Labels to delete: ')
        
        ids = self.contents()
        for item_id in ids:
            self.get_item(item_id).delete_info_by_label(label = label)
            self.get_item(item_id).update_properties()
            
        self.update_properties()
    

    # Methods for retrieving items and data from item set
    
    def get_item(self, item_id = 'request_input'):
        
        """
        Returns an item if given its ID.
        """
        
        if item_id == 'request_input':
            item_id = input('Item ID: ')

        if item_id not in self.__dict__:
            raise KeyError(f'"{item_id}" not found in items')
        
        return self.__dict__[item_id]
    

    def get_all_data(self, select_by_type = None):
        
        """
        Returns all data from all items. Can choose to return only a specified data type.
        
        Parameters
        ----------
        select_by_type : str or None
            specifies a datatype to return. Defaults to None; all data types returned.
        """
        
        if (self.count_items() != 0) and (self.count_items() != None):
            concat_list = []
            items = self.contents()
            for item_id in items:
                df = self.get_item(item_id).data.copy(deep=True)
                df['Found in'] = item_id
                concat_list.append(df)

            concat_df  = pd.concat(concat_list).reset_index().drop('index', axis=1)

            if type(select_by_type) == str:
                select_by_type = [select_by_type]

            if type(select_by_type) == list:
                output_df = pd.DataFrame()
                for i in select_by_type:
                    masked = concat_df[concat_df['Datatype'] == i]
                    output_df = pd.concat([masked, output_df])
                concat_df = output_df
        
        else:
            concat_df = pd.DataFrame(columns = ['Datatype', 'Format', 'Stored as', 'Size (bytes)', 'Raw data', 'Parsed data'])
        
        return concat_df
    
    
    def get_all_datatypes(self):
        
        """
        Returns all data type names.
        """
        
        return self.get_all_data()['Datatype']
    
    def get_datatypes_set(self):
        
        """
        Returns all data type names as a set.
        """
        
        return set(self.get_all_datatypes())
    
    def get_datatypes_frequencies(self):
        
        """
        Returns the frequency counts of all data types.
        """
        
        return self.get_all_datatypes().value_counts()
    
    def get_datatypes_stats(self):
        
        """
        Returns frequency statistics for all data types.
        """
        
        return self.get_datatypes_frequencies().describe()
    
    def get_all_data_formats(self):
        
        """
        Returns all data format names.
        """
        
        return self.get_all_data()['Format']
    
    def get_data_formats_set(self):
        
        """
        Returns all data format names as a set.
        """
        
        return set(self.get_all_data_formats())
    
    def get_data_formats_frequencies(self):
        
        """
        Returns the frequency counts of all data types.
        """
        
        return self.get_all_data_formats().value_counts()
    
    def get_data_formats_stats(self):
        
        """
        Returns frequency statistics for all data types.
        """
        
        return self.get_data_formats_frequencies().describe()
    
    def get_all_data_sizes(self):
        
        """
        Returns all data entry sizes.
        """
        
        sizes = self.get_all_data()['Size (bytes)'].astype(float)
        return sizes
    
    def get_data_size_frequencies(self):
        
        """
        Returns frequencies for data sizes.
        """
        
        return self.get_all_data_sizes().value_counts()
    
    def get_data_size_stats(self):
        
        """
        Returns frequency statistics for data sizes.
        """
        
        return self.get_all_data_sizes().describe()
    
    def get_all_rawdata(self, select_by_type = None):
        
        """
        Returns all raw data entries.
        """
        
        return self.get_all_data(select_by_type = select_by_type)['Raw data']
    
    def get_rawdata_list(self, select_by_type = None):
        
        """
        Returns all raw data entries as a list.
        """
        
        return self.get_all_rawdata(select_by_type = select_by_type).to_list()
    
    def get_rawdata_list_size(self, select_by_type = None):
        
        """
        Returns the number of raw data entries.
        """
        
        return len(self.get_rawdata_list(select_by_type = select_by_type))
    
    def get_rawdata_dict(self):
        
        """
        Returns all raw data entries as a dictionary, where keys are items and values are entries.
        """
        
        all_data_dict = {}
        items = self.contents()
        for item_id in items:
            data_list = self.get_item(item_id).get_rawdata_list()
            all_data_dict[item_id] = data_list

        return all_data_dict
    
    def get_rawdata_set(self, select_by_type = None):
        
        """
        Returns the set of unique raw data entries.
        """
        
        return set(self.get_all_rawdata(select_by_type = select_by_type))
    
    def get_rawdata_set_dict(self):
        
        """
        Returns the set of unique raw data entries as a dictionary, where keys are items and values are entries.
        """
        
        data_set_dict = {}
        items = self.contents()
        for item_id in items:
            data_set = self.get_item(item_id).get_rawdata_set()
            data_set_dict[item_id] = data_set

        return data_set_dict
    
    def get_rawdata_set_size(self, select_by_type = None):
        
        """
        Returns the number of unique raw data entries.
        """
        
        return len(self.get_rawdata_set(select_by_type = select_by_type))
    
    def get_rawdata_frequencies(self, select_by_type = None):
        
        """
        Returns frequency counts for unique raw data entries.
        """
        
        return self.get_all_rawdata(select_by_type = select_by_type).value_counts()
    
    def get_rawdata_stats(self, select_by_type = None):
        
        """
        Returns frequency statistics for unique raw data entries.
        """
        
        return self.get_rawdata_frequencies(select_by_type = select_by_type).describe()
    
    def get_all_data_sets(self):
        
        """
        Returns unique raw data from all items as a list of sets.
        """
        
        set_list = []
        items = self.contents()
        for item_id in items:
            set_list.append(self.get_item(item_id).get_rawdata_set())
        
        return set_list
        
    def get_data_intersect(self):
        
        """
        Returns the intersect of raw data sets from all items.
        """
        
        set_list = self.get_all_data_sets()
        if len(set_list) != 0:
            set_intersection = set.intersection(*set_list)
        else:
            set_intersection = None

        return set()
    
    def get_data_symmetric_difference(self):
        
        """
        Returns the symmetric difference of raw data sets from all items.
        
        i.e., all raw data entries which are only in one set.
        """
        
        set_list = self.get_all_data_sets()
        
        if len(set_list) != 0:
            diff = set.symmetric_difference(*set_list)
            
        else:
            diff = set()
    
        return diff
    
    def data_sets_similarity(self):
        
        """
        Returns the Jaccard similarity between raw data sets from all items.
        
        i.e., how many entries are shared by all versus the total number.
        """
        
        set_list = self.get_all_data_sets()
        
        if len(set_list) != 0:
            set_union = set.union(*set_list)
            set_intersection = set.intersection(*set_list)
            
        else:
            set_union = set()
            set_intersection = set()
            
        ratio =  len(set_intersection) / len(set_union)
        return ratio
        
    

    def get_all_metadata(self, select_by_category: str = None, ignore_nones: bool = True):
        
        """
        Returns all metadata from all items.
        
        Parameters
        ----------
        select_by_category : str
            specifies a metadata category to return. Defaults to None: metadata from all categories are returned.
        ignore_nones : bool
            whether or not to return empty/None metadata entries. Defaults to True: empty/None entries are not returned.
        """
        
        all_metadata_dfs_list = []

        for item_id in self.contents():

            df = self.get_item(item_id).get_metadata(select_by_category = select_by_category, ignore_nones = ignore_nones).copy(deep=True)
            df['Found in'] = item_id
            all_metadata_dfs_list.append(df)

        all_metadata_df = pd.concat(all_metadata_dfs_list).reset_index().drop('index', axis=1)
        
        if ignore_nones == True:
            all_metadata_df = all_metadata_df.dropna()

        return all_metadata_df
    
    
    def get_metadata_dict(self, select_by_category: str = None, ignore_nones: str = True) -> dict:
        
        """
        Returns a dictionary of metadata from all items.
        
        Parameters
        ----------
        select_by_category : str
            specifies a metadata category to return. Defaults to None: metadata from all categories are returned.
        ignore_nones : bool
            whether or not to return empty/None metadata entries. Defaults to True: empty/None entries are not returned.
        """
        
        all_metadata_dict = {}
        
        if type(select_by_category) == str:
            select_by_category = [select_by_category]
        
        for item_id in self.contents():
            
            metadata_list = self.get_item(item_id).get_metadata_list(select_by_category = select_by_category, ignore_nones = ignore_nones)
            all_metadata_dict[item_id] = metadata_list
            
        return all_metadata_dict
    
    
    def get_metadata_nested_dict(self, select_by_category = None, ignore_nones = True) -> dict:
        
        """
        Returns metadata from all items as a dictionary of dictionaries.
        
        Parameters
        ----------
        select_by_category : str
            specifies a metadata category to return. Defaults to None: metadata from all categories are returned.
        ignore_nones : bool
            whether or not to return empty/None metadata entries. Defaults to True: empty/None entries are not returned.
        
        Returns
        -------
        result : dict
            a dictionary where each key is an item and each value is itself a dictionary containing metadata categories and values.
        """
        
        all_metadata_dict = {}
        
        for item_id in self.contents():
            all_metadata_dict[item_id] = self.get_item(item_id).get_metadata_dict(select_by_category = select_by_category, ignore_nones = ignore_nones)
            
        return all_metadata_dict
        
    
    def get_metadata_series(self, select_by_category = None, ignore_nones = True) -> pd.Series:
        
        """
        Returns all metadata from all items as a Pandas series.
        
        Parameters
        ----------
        select_by_category : str
            specifies a metadata category to return. Defaults to None: metadata from all categories are returned.
        ignore_nones : bool
            whether or not to return empty/None metadata entries. Defaults to True: empty/None entries are not returned.
        """
        
        df = self.get_all_metadata(select_by_category = select_by_category, ignore_nones = ignore_nones)
        df['combined'] = list(zip(df['Metadata'], df['Category']))

        return df['combined']
    
    
    def get_metadata_list(self, select_by_category = None, ignore_nones = True) -> set:
        
        """
        Returns a list of all metadata values from all items. Does not return metadata categories.
        
        Parameters
        ----------
        select_by_category : str
            specifies a metadata category to return. Defaults to None: metadata from all categories are returned.
        ignore_nones : bool
            whether or not to return empty/None metadata entries. Defaults to True: empty/None entries are not returned.
        """
        
        return self.get_metadata_series(select_by_category = select_by_category, ignore_nones = ignore_nones).to_list()
    
    
    def get_metadata_set(self, select_by_category = None, ignore_nones = True) -> set:
        
        """
        Returns a set of all unique metadata values from all items. Does not return metadata categories.
        
        Parameters
        ----------
        select_by_category : str
            specifies a metadata category to return. Defaults to None: metadata from all categories are returned.
        ignore_nones : bool
            whether or not to return empty/None metadata entries. Defaults to True: empty/None entries are not returned.
        """
        
        return set(self.get_metadata_series(select_by_category = select_by_category, ignore_nones = ignore_nones))
    
    def get_metadata_frequencies(self, select_by_category = None, ignore_nones = True):
        
        """
        Returns frequency counts for all combinations of metadata categories and values.
        
        Parameters
        ----------
        select_by_category : str
            specifies a metadata category to return. Defaults to None: metadata from all categories are returned.
        ignore_nones : bool
            whether or not to return empty/None metadata entries. Defaults to True: empty/None entries are not returned.
        """
        
        return self.get_all_metadata(select_by_category = select_by_category, ignore_nones = ignore_nones)[['Metadata', 'Category']].value_counts()
    
    def get_metadata_stats(self, select_by_category = None, ignore_nones = True):
        
        """
        Returns frequency statistics for all combinations of metadata categories and values.
        
        Parameters
        ----------
        select_by_category : str
            specifies a metadata category to return. Defaults to None: metadata from all categories are returned.
        ignore_nones : bool
            whether or not to return empty/None metadata entries. Defaults to True: empty/None entries are not returned.
        """
        
        return self.get_metadata_frequencies(select_by_category = select_by_category, ignore_nones = ignore_nones).describe()
    
    def get_all_metadata_sets(self):
        
        """
        Returns unique metadata values from all items as a list of sets.
        """
        
        return [self.get_item(item_id).get_metadata_set() for item_id in self.contents()]
        
    def get_metadata_intersect(self):
        
        """
        Returns the intersect of metadata sets from all items.
        """
        
        set_list = self.get_all_metadata_sets()
        return set.intersection(*set_list)
    
    def get_metadata_symmetric_difference(self):
        
        """
        Returns the symmetric difference of metadata sets from all items.
        
        i.e., all metadata entries which are only in one set.
        """
        
        set_list = self.get_all_metadata_sets()
        diff = set.symmetric_difference(*set_list)
        
        return diff
    
    def get_metadata_sets_similarity(self):
        
        """
        Returns the Jaccard similarity between metadata sets from all items.
        
        i.e., how many metadata entries are shared by all versus the total number.
        """
        
        set_list = self.get_all_metadata_sets()
        set_union = set.union(*set_list)
        set_intersect = set.intersection(*set_list)
        return len(set_intersect)/len(set_union)

    def get_metadata_categories(self, select_by_category = None, ignore_nones = True):
        
        """
        Returns all metadata categories from all items.
        
        Parameters
        ----------
        select_by_category : str
            specifies a metadata category to return. Defaults to None: metadata from all categories are returned.
        ignore_nones : bool
            whether or not to return empty metadata categories. Defaults to True: empty/None entries are not returned.
        """
        
        return self.get_all_metadata(select_by_category = select_by_category, ignore_nones = ignore_nones)['Category']

    def get_metadata_category_frequencies(self, select_by_category = None, ignore_nones = True):
        
        """
        Returns frequency counts for all metadata categories.
        
        Parameters
        ----------
        select_by_category : str
            specifies a metadata category to return. Defaults to None: metadata from all categories are returned.
        ignore_nones : bool
            whether or not to return empty metadata categories. Defaults to True: empty/None entries are not returned.
        """
        
        return self.get_metadata_categories(select_by_category = select_by_category, ignore_nones = ignore_nones).value_counts()

    def get_metadata_category_stats(self, select_by_category = None, ignore_nones = True):
        
        """
        Returns frequency statistics for all metadata categories.
        
        Parameters
        ----------
        select_by_category : str
            specifies a metadata category to return. Defaults to None: metadata from all categories are returned.
        ignore_nones : bool
            whether or not to return empty metadata categories. Defaults to True: empty/None entries are not returned.
        """
        
        return self.get_metadata_category_frequencies(select_by_category = select_by_category, ignore_nones = ignore_nones).describe()
    
    def get_all_addresses(self, ignore_nones = True):
        
        """
        Returns all address metadata entries.
        
        Parameters
        ----------
        ignore_nones : bool
            whether or not to return empty/None results. Defaults to True: empty/None entries are not returned.
        """
        
        return self.get_all_metadata(select_by_category = 'address', ignore_nones = True)
    
    def get_address_list(self, ignore_nones = True):
        
        """
        Returns all address metadata entries as a list.
        
        Parameters
        ----------
        ignore_nones : bool
            whether or not to return empty/None results. Defaults to True: empty/None entries are not returned.
        """
        
        return self.get_all_addresses(ignore_nones = True)['Metadata'].to_list()

    def get_address_set(self, ignore_nones = True) -> set:
        
        """
        Returns the set of unique address metadata entries.
        
        Parameters
        ----------
        ignore_nones : bool
            whether or not to return empty/None results. Defaults to True: empty/None entries are not returned.
        """
        
        return set(self.get_all_addresses(ignore_nones = True)['Metadata'])
    
    
    def get_address_dict(self, ignore_nones = True):
        
        """
        Returns a dictionary address metadata entries.
        
        Parameters
        ----------
        ignore_nones : bool
            whether or not to return empty/None results. Defaults to True: empty/None entries are not returned.
        """
        
        addresses = {}
        for item_id in self.contents():
            addresses[item_id] = self.get_item(item_id).get_address()
        
        return addresses
    
    def get_all_urls_metadata(self):
    
        """
        Returns all URL metadata entries.
        """
        
        all_urls = []

        ids = self.ids()

        for i in ids:
            url = self.get_item(i).get_url()
            all_urls.append(url)

        return all_urls

    def get_urls_metadata_set(self):
        
        """
        Returns the set of unique URL metadata entries.
        """
        
        all_urls = self.get_all_urls_metadata()
        return set(all_urls)

    def get_urls_metadata_dict(self):
        
        """
        Returns a dictionary containing all URL metadata entries.
        """
        
        urls_dict = {}

        ids = self.ids()

        for i in ids:
            url = self.get_item(i).get_url()
            urls_dict[i] = url

        return urls_dict

    def get_item_domain_metadata(self, item_id = 'request_input'):
        
        """
        Returns an item's domain metadata.
        """
        
        try:
            df = self.get_item(item_id).get_metadata('domain').reset_index().loc[0, 'Metadata']
            
        except:
            return None
    
    def get_all_domain_metadata(self):
        
        """
        Returns all domain metadata entries.
        """
        
        domains = pd.DataFrame(columns = ['item', 'domain'], dtype=object)
        index = 0
        for item_id in self.contents():
            domain = self.get_item_domain_metadata(item_id)
            row = [item_id, domain]
            domains.loc[index] = row
            index += 1
        
        return domains
    
    

    def get_all_info(self, select_by_category = None) -> pd.DataFrame:
        
        """
        Returns all information from all items.
        
        Parameters
        ----------
        select_by_category : str
            specifies an information category to return. Defaults to None: returns information from all categories.
        """
        
        concat_list = []

        for item_id in self.contents():
            df = self.get_item(item_id).information.copy(deep=True)
            df['Found in'] = item_id
            concat_list.append(df)

        concat_df  = pd.concat(concat_list).reset_index().drop('index', axis=1)
        
        if type(select_by_category) == str:
                select_by_category = [select_by_category]

        if type(select_by_category) == list:
                output_df = pd.DataFrame()
                for i in select_by_category:
                    masked = concat_df[concat_df['Category'] == i]
                    output_df = pd.concat([masked, output_df])
                concat_df = output_df
            
        return concat_df
    
    def get_info_series(self, select_by_category = None):
        
        """
        Returns all information entries as a Pandas series.
        
        Parameters
        ----------
        select_by_category : str
            specifies an information category to return. Defaults to None: returns information from all categories.
        """
        
        df = self.get_all_info(select_by_category = select_by_category)
        df['combined'] = list(zip(df['Label'], df['Category']))
        return df['combined']
    
    def get_info_list(self, select_by_category = None):
        
        """
        Returns all information entries as a list of tuples.
        
        Parameters
        ----------
        select_by_category : str
            specifies an information category to return. Defaults to None: returns information from all categories.
        """
        
        return self.get_info_series(select_by_category = select_by_category).to_list()
    
    def get_info_dict(self, select_by_category = None):
        
        """
        Returns all information entries as dictionary.
        
        Parameters
        ----------
        select_by_category : str
            specifies an information category to return. Defaults to None: returns information from all categories.
        """
        
        all_info_dict = {}
        
        if type(select_by_category) == str:
            select_by_category = [select_by_category]
        
        for item_id in self.contents():
            
            all_info_dict[item_id] = self.get_info_list(select_by_category = select_by_category)
            
        return all_info_dict
    
    
    def get_info_count(self, select_by_category = None):
        
        """
        Returns number of information entries.
        
        Parameters
        ----------
        select_by_category : str
            specifies a information category to return. Defaults to None: returns information from all categories.
        """
        
        return len(self.get_info_series(select_by_category = select_by_category))
    
    def get_info_set(self, select_by_category = None):
        
        """
        Returns set of unique information entries.
        
        Parameters
        ----------
        select_by_category : str
            specifies a information category to return. Defaults to None: returns information from all categories.
        """
        
        return set(self.get_info_series(select_by_category = select_by_category))
    
    def get_info_set_size(self, select_by_category = None):
        
        """
        Returns the number of unique information entries.
        
        Parameters
        ----------
        select_by_category : str
            specifies a information category to return. Defaults to None: returns information from all categories.
        """
        
        return len(self.get_info_set(select_by_category = select_by_category))
    
    def get_repeated_info_count(self, select_by_category = None):
        
        """
        Returns the number of repeated information entries.
        
        Parameters
        ----------
        select_by_category : str
            specifies a information category to return. Defaults to None: returns information from all categories.
        """
        
        unique_count = self.get_info_set_size(select_by_category = select_by_category)
        all_count = self.get_info_count(select_by_category = select_by_category)
        
        return all_count - unique_count

    
    def get_info_frequencies(self, select_by_category = None):
        
        """
        Returns the frequency counts for information entries.
        
        Parameters
        ----------
        select_by_category : str
            specifies a information category to return. Defaults to None: returns information from all categories.
        """
        
        series = self.get_info_series(select_by_category = select_by_category)
        frequencies = series.value_counts()
        return frequencies
    
    
    def get_info_stats(self, select_by_category = None):
        
        """
        Returns frequency statistics for information entries.
        
        Parameters
        ----------
        select_by_category : str
            specifies a information category to return. Defaults to None: returns information from all categories.
        """
        
        return self.get_info_frequencies(select_by_category = select_by_category).describe()
    
    def get_info_categories(self, select_by_category = None):
        
        """
        Returns all information categories from all items.
        
        Parameters
        ----------
        select_by_category : str
            specifies a category to return. Defaults to None: information from all categories are returned.
        ignore_nones : bool
            whether or not to return empty information entries. Defaults to True: empty/None entries are not returned.
        """
        
        return self.get_all_info(select_by_category = select_by_category)['Category']
    
    def get_info_frequencies_by_category(self, select_by_category = None):
        
        """
        Returns the frequency counts for information categories and labels.
        
        Parameters
        ----------
        select_by_category : str
            specifies a information category to return. Defaults to None: returns information from all categories.
        """
        
        df = self.get_all_info(select_by_category = select_by_category)[['Label', 'Category']]
        frequencies = df.value_counts()
        return frequencies
    
    def get_info_stats_by_category(self, select_by_category = None):
        
        """
        Returns frequency statistics for information categories and labels.
        
        Parameters
        ----------
        select_by_category : str
            specifies a information category to return. Defaults to None: returns information from all categories.
        """
        
        return self.get_info_frequencies_by_category(select_by_category = select_by_category).describe()
    
    
    def get_info_category_frequencies(self, select_by_category = None):
        
        """
        Returns frequency counts for all information categories.
        
        Parameters
        ----------
        select_by_category : str
            specifies a category to return. Defaults to None: all categories are returned.
        """
        
        df = self.get_info_categories(select_by_category = select_by_category)
        frequencies = df.value_counts()
        return frequencies
    
    def get_info_category_stats(self, select_by_category = None):
        
        """
        Returns frequency statistics for all information categories.
        
        Parameters
        ----------
        select_by_category : str
            specifies a category to return. Defaults to None: all categories are returned.
        """
        
        return self.get_info_category_frequencies(select_by_category = select_by_category).describe()
    
    def get_info_intersect(self):
        
        """
        Returns the intersect of information sets from all items.
        
        i.e., any information entries which are found in all items.
        """
        
        set_list = [self.get_item(item_id).get_info_set() for item_id in self.contents()]
        return set.intersection(*set_list)
    
    def get_info_symmetric_difference(self):
        
        """
        Returns the symmetric difference of information sets from all items.
        
        i.e., any information entries which are *not* found in all items.
        """
        
        set_list = [self.get_item(item_id).get_info_set() for item_id in self.contents()]
        set_union = set.union(*set_list)
        set_intersect = set.intersection(*set_list)
        
        return set_union - set_intersect
    
    def get_info_sets_similarity(self):
        
        """
        Returns the Jaccard similarity between information sets from all items.
        
        i.e., how many information entries are found in all versus the total number.
        """
        
        set_list = [self.get_item(item_id).get_info_set() for item_id in self.contents()]
        set_union = set.union(*set_list)
        set_intersect = set.intersection(*set_list)
        return len(set_intersect)/len(set_union)
    

    def get_all_words(self, clean = True):
        
        """
        Returns all words parsed from all items.
        
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        """
        
        out_df = pd.DataFrame(columns = ['word', 'found_in'])

        for item_id in self.contents():
            words_df = pd.DataFrame(columns = ['word', 'found_in'])
            words_df['word'] = self.get_item(item_id = item_id).get_all_words(clean=clean)
            words_df['found_in'] = item_id
            out_df = pd.concat([out_df, words_df])

        return out_df
    

    def get_words_set(self, clean = True):
        
        """
        Returns the set of unique words parsed from all items.
        
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        """
        
        return set(self.get_all_words(clean = clean)['word'])
    
    def get_words_set_size(self, clean = True):
        
        """
        Returns the number of unique words parsed from all items.
        
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        """
        
        return len(self.get_words_set(clean = clean))
    

    def get_all_links(self):
        
        """
        Returns all links found in items.
        """
        
        df = pd.DataFrame(columns = ['Link', 'Found in'])
        
        item_ids = self.ids()
        for item_id in item_ids:
            
            self.get_item(item_id).fix_links_str()
            links = self.get_item(item_id).links
            
            if links != None:
                for l in links:
                    index = len(df.index)
                    df.loc[index, 'Link'] = l
                    df.loc[index, 'Found in'] = item_id
            
        return df
    
    def get_links_list(self):
        
        """
        Returns all links as a list.
        """
        
        links_df = self.get_all_links()
        links = links_df['Link'].to_list()
        
        return links
    
    
    def get_links_set(self):
        
        """
        Returns the set of unique links found in items.
        """
        
        return set(self.get_all_links()['Link'])
    
    def get_all_link_sets(self):
        
        """
        Returns the unique links found in each item as a list of sets.
        """
        
        return [self.get_item(item_id).get_links_set() for item_id in self.contents()]
        
    def get_links_intersect(self):
        
        """
        Returns the intersection of all items' link sets.
        
        i.e., any links shared by all items.
        """
        
        set_list = self.get_all_link_sets()
        return set.intersection(*set_list)
    
    def get_links_symmetric_difference(self):
        
        """
        Returns the symmetric difference of all items' link sets.
        
        i.e., any links *not* shared by all items.
        """
        
        set_list = self.get_all_link_sets()
        diff = set.symmetric_difference(*set_list)
        
        return diff
    
    def get_link_sets_similarity(self):
        
        """
        Returns the Jaccard similarity between all items' link sets.
        
        i.e., how many links are found in all versus the total number.
        """
        
        set_list = self.get_all_link_sets()
        set_union = set.union(*set_list)
        set_intersect = set.intersection(*set_list)
        try:
            return len(set_intersect)/len(set_union)
        except:
            return np.nan
    
    
    def get_links_dict(self):
        
        """
        Returns links as a dictionary.
        
        Notes
        -----
        Dictiionary structure:
            * keys: item IDs
            * values: link lists
        """
        
        all_links_dict = {}
        for item_id in self.contents():
            links = self.get_item(item_id).links
            all_links_dict[item_id] = links

        return all_links_dict
    
    
    def get_links_frequencies(self):
        
        """
        Returns frequency counts for links.
        """
        
        return self.get_all_links()['Link'].value_counts()
    
    def get_links_frequencies_detailed(self):
        
        """
        Returns frequency counts for links with detail on where each link was found.
        """
        
        all_links = self.get_all_links()

        freqs = self.get_all_links()['Link'].value_counts()
        links_set = set(freqs.index)
        
        df = pd.DataFrame(columns = ['Link', 'Found in', 'Frequency'], dtype=object)

        for link in links_set:
            index = len(df.index)
            df.loc[index, 'Link'] = link
            df.loc[index, 'Frequency'] = freqs.loc[link]
            found_in = all_links[all_links['Link'] == link]['Found in'].to_list()
            df.at[index, 'Found in'] = found_in

        df = df.sort_values('Frequency', ascending=False).reset_index().drop('index', axis=1)

        return df
    
    def get_links_stats(self):
        
        """
        Returns frequency statistics for links.
        """
        
        return self.get_links_frequencies().describe()

    
    def get_all_refs(self):
        
        """
        Returns all references found in items.
        """
        
        df = pd.DataFrame(columns = ['Reference', 'Found in'])
        
        for item_id in self.contents():
            
            
            refs = self.get_item(item_id).references
            
            if refs != None:
                for ref in refs:
                    index = len(df.index)
                    df.at[index, 'Reference'] = ref
                    df.at[index, 'Found in'] = item_id
            
        return df
    
    
    def get_refs_set(self):
        
        """
        Returns the set of unique references found in items.
        """
        
        return set(self.get_all_refs()['Reference'])
    
    def get_all_refs_sets(self):
        
        """
        Returns the unique references found in each item as a list of sets.
        """
        
        return [self.get_item(item_id).get_refs_set() for item_id in self.contents()]
        
    def get_refs_intersect(self):
        
        """
        Returns the intersection of all items' references sets.
        
        i.e., any references shared by all items.
        """
        
        set_list = self.get_all_refs_sets()
        return set.intersection(*set_list)
    
    def get_refs_symmetric_difference(self):
        
        """
        Returns the symmetric difference of all items' references sets.
        
        i.e., any references *not* shared by all items.
        """
        
        set_list = self.get_all_refs_sets()
        diff = set.symmetric_difference(*set_list)
        
        return diff
    
    def get_refs_sets_similarity(self):
        
        """
        Returns the Jaccard similarity between all items' references sets.
        
        i.e., how many references are found in all versus the total number of unique references.
        """
        
        set_list = self.get_all_refs_sets()
        set_union = set.union(*set_list)
        set_intersect = set.intersection(*set_list)
        try:
            return len(set_intersect)/len(set_union)
        except:
            return np.nan
    
    
    def get_refs_dict(self):
        
        """
        Returns references as a dictionary.
        
        Notes
        -----
        Dictionary structure:
            * keys: item IDs
            * values: references lists
        """
        
        all_refs_dict = {}
        for item_id in self.contents():
            refs = self.get_item(item_id).references
            all_refs_dict[item_id] = refs

        return all_refs_dict
    
    
    def get_refs_frequencies(self):
        
        """
        Returns frequency counts for references.
        """
        
        return self.get_all_refs()['Reference'].value_counts()
    
    def get_refs_stats(self):
        
        """
        Returns frequency statistics for references.
        """
        
        return self.get_refs_frequencies().describe()
    

    def get_all_contents(self):
        
        """
        Returns all contents entries found in items.
        """
        
        df = pd.DataFrame(columns = ['Content', 'Found in'])
        
        for item_id in self.contents():
            
            
            contents = self.get_item(item_id).contains
            if contents != None:
                for c in contents:
                    index = len(df.index)
                    df.at[index, 'Content'] = c
                    df.at[index, 'Found in'] = item_id
            
        return df
    
    
    def get_contents_set(self):
        
        """
        Returns the set of unique contents entries found in items.
        """
        
        return set(self.get_all_contents()['Content'])
    
    def get_all_contents_sets(self):
        
        """
        Returns the unique contents entries found in each item as a list of sets.
        """
        
        return [self.get_item(item_id).get_contents_set() for item_id in self.contents()]
        
    def get_contents_intersect(self):
        
        """
        Returns the intersection of all items' contents sets.
        
        i.e., any contents entries shared by all items.
        """
        
        set_list = self.get_all_contents_sets()
        return set.intersection(*set_list)
    
    def get_contents_symmetric_difference(self):
        
        """
        Returns the symmetric difference of all items' contents sets.
        
        i.e., any contents entries *not* shared by all items.
        """
        
        set_list = self.get_all_contents_sets()
        diff = set.symmetric_difference(*set_list)
        
        return diff
    
    def get_contents_sets_similarity(self):
        
        """
        Returns the Jaccard similarity between all items' contents sets.
        
        i.e., how many contents entries are found in all versus the total number of unique references.
        """
        
        set_list = self.get_all_contents_sets()
        set_union = set.union(*set_list)
        set_intersect = set.intersection(*set_list)
        try:
            return len(set_intersect)/len(set_union)
        except:
            return np.nan
    
    
    def get_contents_dict(self):
    
        """
        Returns item contents as a dictionary.
        
        Notes
        -----
        Dictionary structure:
            * keys: item IDs
            * values: references lists
        """
        
        all_contents_dict = {}
        for item_id in self.contents():
            contents = self.get_item(item_id).contains
            all_contents_dict[item_id] = contents

        return all_contents_dict
    
    
    def get_contents_frequencies(self):
        
        """
        Returns frequency counts for contents entries.
        """
        
        return self.get_all_contents()['Content'].value_counts()
    
    def get_contents_stats(self):
        
        """
        Returns frequency statistics for contents entries.
        """
        
        return self.get_contents_frequencies().describe()
    

    def get_word_count(self, clean = True):
        
        """
        Returns the number of words found in parsed data across all items.
        
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        """
        
        return len(self.get_all_words().index)
    
    def get_word_frequencies(self, clean = True):
        
        """
        Returns frequency counts for all words found in parsed data across all items.
        
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        """
        
        freqs = self.get_all_words(clean = clean)['word'].value_counts()
        df = pd.DataFrame(freqs)
        df['frequency'] = df['word']
        df = df.drop('word',axis=1)
        df.index.name = 'word'

        return df
    
    
    def get_word_frequencies_detailed(self, clean = True):
        
        """
        Returns detailed breakdown of frequency counts for all words found in parsed data across all items.
        
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        
        Returns
        -------
        result : pandas.DataFrame
            a dataframe featuring:
                * word (index)
                * found_in: a list of item IDs where the word was found
                * found_in_count: how many items in which the word was found
                * frequency_per_item: the mean number of times each item contained the word
                * breakdown: a dictionary recording the number of times each item contained the word
         """
        
        all_words_df = self.get_all_words(clean = clean)
        freqs_df = self.get_word_frequencies(clean = clean)
        freqs_df['found_in'] = None
        freqs_df['found_in_count'] = None
        freqs_df['frequency_per_item'] = None
        freqs_df['breakdown'] = None

        for word in freqs_df.index:
            item_ids_masked = all_words_df[all_words_df['word'] == word]['found_in']
            item_ids_set = set(item_ids_masked)
            item_ids_dict = item_ids_masked.value_counts().to_dict()
            freqs_df.at[word, 'found_in'] = item_ids_set
            freqs_df.loc[word, 'found_in_count'] = len(item_ids_set)
            freqs_df.at[word, 'breakdown'] = item_ids_dict

        freqs_df['frequency_per_item'] = freqs_df['frequency'] / freqs_df['found_in_count']

        return freqs_df
    
    
    def word_mean_frequencies(self, clean = True):
        
        """
        Returns the mean number of times each word in items' parsed data occurred per item.
        
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        """
        
        return self.get_word_frequencies_detailed(clean = clean)['frequency_per_item'].sort_values(ascending=False)
    
    def get_most_frequent_words(self, clean = True, top = 15):
        
        """
        Returns the most frequently occurring words.
        
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        top : int
            how many words to return.
        """
        
        return self.get_word_frequencies(clean = clean).head(15)
    
    def highest_frequency_per_item_words(self, clean = True, top = 15):
        
        """
        Returns the most frequently occurring words per item.
        
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        top : int
            how many words to return.
        """
        
        return self.word_mean_frequencies(clean = clean).head(15)
    
    def get_word_stats(self, clean = True):
        
        """
        Returns frequency statistics for all words found in items' parsed data.
        """
        
        return self.get_word_frequencies(clean = clean).describe()
    
    
    def get_word_stats_detailed(self, clean = True):
        
        """
        Returns detailed frequency statistics for all words found in items' parsed data.
        
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        
        Returns
        -------
        result : pandas.DataFrame
            a dataframe featuring descriptive statistics for:
                * frequency: the number of times a word appeared across the item set.
                * found_in_count: how many items in which a word was found.
                * frequency_per_item: the mean number of times each item contained a word.
        """
        
        df = pd.DataFrame()
        frequencies_df = self.get_word_frequencies_detailed(clean = clean)
        cols = ['frequency', 'found_in_count', 'frequency_per_item']
        for col in cols:
            df[col] = frequencies_df[col].astype(float).describe()

        return df
    
    
    def rawdata_with_words(self) -> pd.DataFrame:
        
        """
        Returns a dataframe displaying items' raw data entries and the words extracted from them.
        """
        
        df = self.get_all_data()
        masked_df = df[(df['Format'] == 'txt') | (df['Format'] == 'html') | (df['Datatype'] == 'html') | (df['Datatype'] == 'text')]

        words_list = [
                        i['words'] for i in masked_df['Parsed data'].to_list() if (
                                                                                (type(i) == dict) 
                                                                                and ('words' in i.keys()))
                        ]
        
        word_counts = [len(i) for i in words_list]
        
        masked_df['Words'] = words_list
        masked_df['Word count'] = word_counts

        masked_df = masked_df[['Datatype', 'Raw data', 'Words', 'Word count', 'Found in']]

        return masked_df.sort_values('Word count', ascending=False).reset_index().drop('index', axis=1)
    

    def get_repeated_words_count(self):
        
        """
        Returns the number of times words were repeated.
        """
        
        return self.get_word_count() - self.get_words_set_size()
    
    def get_words_intersect(self, clean = True):
        
        """
        Returns the intersection of all items' word sets.
        
        i.e., any words shared by all items.
            
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        """
        
        ids = self.contents()
        set_list = [self.get_item(i).get_words_set(clean = clean) for i in ids]
        set_intersection = set.intersection(*set_list)

        return set_intersection
    
    def get_words_symmetric_difference(self, clean = True):
        
        """
        Returns the symmetric difference of all items' word sets.
        
        i.e., any words *not* shared by all items.
            
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        """
        
        ids = self.contents()
        set_list = [self.get_item(i).get_words_set(clean = clean) for i in ids]
        diff = set.symmetric_difference(*set_list)

        return diff
    
    def get_word_sets_similarity(self, clean = True):
        
        """
        Returns the Jaccard similarity between all items' word sets.
        
        i.e., how many words are found in all versus the total number of unique words.
            
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        """
        
        ids = self.contents()
        set_list = [self.get_item(i).get_words_set(clean = clean) for i in ids]
        set_intersection = set.intersection(*set_list)
        set_union = set.union(*set_list)

        return len(set_intersection) / len(set_union)
    
    
    def add_instagram_user_posts(self, username = 'request_input'):
        
        """
        Retrieves an Instagram user's posts from a username and adds to the Case.
        
        Parameters
        ----------
        username : str
            username to retrieve from.
        """
        
        posts = fetch_user_posts(username = username)

        for p in posts:
        
            shortcode = p.shortcode
            caption = p.caption
            hashtags = p.caption_hashtags
            comment_count = p.comments
            date = p.date
            date_local = p.date_local
            date_utc = p.date_utc
            is_video = p.is_video
            likes_count = p.likes
            location = p.location
            url = p.url
            title = p.title
            mediacount = p.mediacount
            user_id = p.owner_id
            username = p.owner_username
            item_id = shortcode.replace('-', '__')
        
            self.add_item(item_id = item_id)

            self.get_item(item_id).add_metadata(metadata_entry = shortcode, metadata_category = 'shortcode')
            self.get_item(item_id).add_metadata(metadata_entry = date, metadata_category = 'date')
            self.get_item(item_id).add_metadata(metadata_entry = date_local, metadata_category = 'date_local')
            self.get_item(item_id).add_metadata(metadata_entry = date_utc, metadata_category = 'date_utc')
            self.get_item(item_id).add_metadata(metadata_entry = likes_count, metadata_category = 'likes_count')
            self.get_item(item_id).add_metadata(metadata_entry = url, metadata_category = 'url')
            self.get_item(item_id).add_metadata(metadata_entry = location, metadata_category = 'location')
            self.get_item(item_id).add_metadata(metadata_entry = title, metadata_category = 'title')
            self.get_item(item_id).add_metadata(metadata_entry = mediacount, metadata_category = 'mediacount')
            self.get_item(item_id).add_metadata(metadata_entry = user_id, metadata_category = 'user_id')
            self.get_item(item_id).add_metadata(metadata_entry = username, metadata_category = 'username')
            self.get_item(item_id).add_metadata(metadata_entry = title, metadata_category = 'name')
            self.get_item(item_id).add_metadata(metadata_entry = username, metadata_category = 'author')

            self.get_item(item_id).add_data(data_type = 'text', data_format = 'str', raw_data = caption)
            self.get_item(item_id).add_data(data_type = 'text', data_format = 'str', raw_data = hashtags)
            self.get_item(item_id).add_data(data_type = 'text', data_format = 'str', raw_data = f'comment count: {comment_count}')
            self.get_item(item_id).add_data(data_type = 'text', data_format = 'str', raw_data = f'likes count: {likes_count}')
        
            self.update_properties()
        
    def items_from_username_search(self, username = 'request_input'):
        
        """
        Runs an Sherlock search on username and adds the results as CaseItems to the Case.
        
        Parameters
        ----------
        username : str
            username to retrieve from.
        """
        
        df = search_username(username = username)
        df = df.reset_index()

        for i in df.index:

            site = i
            data = df.loc[i, 'response_text']
            url = df.loc[i, 'url_user']
            domain = domain_splitter(url)
            item_id = url_to_valid_attr_name(df.loc[i, 'url_user'])

            self.add_item(item_id = item_id)

            self.get_item(item_id).add_metadata(metadata_entry = url, metadata_category = 'URL')
            self.get_item(item_id).add_metadata(metadata_entry = domain, metadata_category = 'domain')
            self.get_item(item_id).add_metadata(metadata_entry = site, metadata_category = 'site')

            self.get_item(item_id).add_data(data_type = 'html', data_format = 'html', raw_data = data)
        
    
    # Methods for comparing items
    
    def rawdata_cosine(self, item_1: CaseItem = 'request_input', item_2: CaseItem = 'request_input'):
        
        """
        Returns the cosine similarity of two items' sets of raw data based on word frequencies.
        
        Parameters
        ----------
        item_1 : str
            first item to compare.
        item_2 : str
            second item to compare.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')

        data_source1 = self.get_item(item_1).data['Raw data'].to_list()
        data_source2 = self.get_item(item_2).data['Raw data'].to_list()

        data_source1 = pd.Series(data_source1).str.replace('\n', ' ', regex=False).str.replace('<', '', regex=False).str.replace('>', '', regex=False).str.replace('\\', '', regex=False).str.replace('/', '', regex=False).str.replace('    ', '', regex=False).str.replace('   ', ' ', regex=False).str.replace('  ', ' ', regex=False).str.strip().str.lower().to_list()
        data_source2 = pd.Series(data_source2).str.replace('\n', ' ', regex=False).str.replace('<', '', regex=False).str.replace('>', '', regex=False).str.replace('\\', '', regex=False).str.replace('/', '', regex=False).str.replace('    ', '', regex=False).str.replace('   ', ' ', regex=False).str.replace('  ', ' ', regex=False).str.strip().str.lower().to_list()

        joined1 = ', '.join(data_source1)
        joined2 = ', '.join(data_source2)

        return cosine_sim([joined1, joined2])

    
    def rawdata_set_pair(self, item_1, item_2) -> tuple:
        
        """
        Returns two items' raw data sets as a tuple.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve from.
        item_2 : str
            second item to retrieve from.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        
        data_source1 = self.get_item(item_1).data['Raw data'].to_list()
        
        if len(data_source1) > 0:
            data_source1 = pd.Series(data_source1).str.replace('\n', ' ', regex=False).str.replace('\\', '', regex=False).str.replace('/', '', regex=False).str.replace('    ', '', regex=False).str.replace('   ', ' ', regex=False).str.replace('  ', ' ', regex=False).str.replace('  ', ' ', regex=False).str.strip().str.lower().str.split(' ')
            
            ds1_split = []
            for i in data_source1:
                ds1_split = ds1_split + i
            data_source1 = set(ds1_split)
            
        else:
            data_source1  = set()
        
        data_source2 = self.get_item(item_2).data['Raw data'].to_list()
        
        if len(data_source2) > 0:
            
            data_source2 = pd.Series(data_source2).str.replace('\n', ' ', regex=False).str.replace('\\', '', regex=False).str.replace('/', '', regex=False).str.replace('    ', '', regex=False).str.replace('   ', ' ', regex=False).str.replace('  ', ' ', regex=False).str.replace('  ', ' ', regex=False).str.strip().str.lower().str.split(' ')
            
            ds2_split = []
            for i in data_source2:
                ds2_split = ds2_split + i
            data_source2 = set(ds2_split)
        
        else:
            data_source2  = set()

        return (data_source1, data_source2)
        
    
    
    def rawdata_intersect(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the intersect of two items' raw data sets.
        
        i.e., any raw data sets shared by both items.
    
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        sets = self.rawdata_set_pair(item_1 = item_1, item_2 = item_2)
        data_source1 = sets[0]
        data_source2 = sets[1]
        
        return data_source1.intersection(data_source2)
    
    
    def rawdata_intersect_size(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the size of the intersect of two items' raw data sets.
        
        i.e., the number of raw data sets shared by both items.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        return len(self.rawdata_intersect(item_1 = item_1, item_2 = item_2))
    
    
    def rawdata_symmetric_difference(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the symmetric difference of two items' raw data sets.
        
        i.e., any raw data sets *not* shared by both items.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        sets = self.rawdata_set_pair(item_1 = item_1, item_2 = item_2)
        data_source1 = sets[0]
        data_source2 = sets[1]
        
        return data_source1.symmetric_difference(data_source2)
    
    
    def rawdata_symmetric_difference_size(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the size of the symmetric difference of two items' raw data sets.
        
        i.e., the number of raw data sets *not* shared by both items.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        return len(self.rawdata_symmetric_difference(item_1 = item_1, item_2 = item_2))

    
    def rawdata_jaccard_sim(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the Jaccard similarity between two items'raw data sets.
        
        i.e., how many raw data entries are found in both versus the total number of entries.
          
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')

        sets = self.rawdata_set_pair(item_1 = item_1, item_2 = item_2)
        data_source1 = sets[0]
        data_source2 = sets[1]

        intersect_size = len(data_source1.intersection(data_source2))
        union_size = len(data_source1.union(data_source2))

        try: 
            return intersect_size / union_size

        except:
            return 0

        
    def rawdata_comparison_series(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns all comparisons between two items' sets of raw data as a Pandas series.
          
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')

        series = pd.Series(index = ['Cosine similarity', 'Set similarity', 'Intersect', 'Intersect size', 'Disjunctive', 'Disjunctive size'], dtype = 'object')

        try:
            series['Cosine similarity'] = self.rawdata_cosine(item_1, item_2)
        except:
            series['Cosine similarity'] = 'N/A'

        series['Set similarity'] = self.rawdata_jaccard_sim(item_1, item_2)
        series['Intersect'] = self.rawdata_intersect(item_1, item_2)
        series['Intersect size'] = self.rawdata_intersect_size(item_1, item_2)
        series['Disjunctive'] = self.rawdata_symmetric_difference(item_1, item_2)
        series['Disjunctive size'] = self.rawdata_symmetric_difference_size(item_1, item_2)

        return series
    
    def get_all_rawdata_comparisons(self):
        
        """
        Compares items' raw data for all combinations of two items. Returns a dataframe.
        """
        
        items = self.contents()
        df = pd.DataFrame(list(itertools.combinations(items, 2)), columns = ['First item', 'Second item'], dtype='object')
        df[['Cosine similarity', 'Set similarity', 'Intersect', 'Intersect size', 'Disjunctive', 'Disjunctive size']] = None

        for row in df.index:
            
            item_1 = df.loc[row, 'First item']
            item_2 = df.loc[row, 'Second item']
            df.loc[row, ['Cosine similarity', 'Set similarity', 'Intersect', 'Intersect size', 'Disjunctive', 'Disjunctive size']] = self.rawdata_comparison_series(item_1 = item_1, item_2 = item_2)

        df['Intersect'] = df['Intersect'].apply(lambda y: None if len(y) == 0 else y)
        df['Disjunctive'] = df['Disjunctive'].apply(lambda y: None if len(y) == 0 else y)
        
        df = df.sort_values(['Set similarity'], ascending=False).reset_index().drop('index', axis=1)

        return df
    
    
    def text_cosine(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the cosine similarity of two items' text based on word frequencies.
        
        Parameters
        ----------
        item_1 : str
            first item to compare. Defaults to requesting from user input.
        item_2 : str
            second item to compare. Defaults to requesting from user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')

        data_source1 = self.get_item(item_1).get_all_text()
        data_source2 = self.get_item(item_2).get_all_text()

        data_source1 = pd.Series(data_source1).str.replace('\n', ' ', regex=False).str.replace('<', '', regex=False).str.replace('>', '', regex=False).str.replace('\\', '', regex=False).str.replace('/', '', regex=False).str.replace('    ', '', regex=False).str.replace('   ', ' ', regex=False).str.replace('  ', ' ', regex=False).str.strip().str.lower().to_list()
        data_source2 = pd.Series(data_source2).str.replace('\n', ' ', regex=False).str.replace('<', '', regex=False).str.replace('>', '', regex=False).str.replace('\\', '', regex=False).str.replace('/', '', regex=False).str.replace('    ', '', regex=False).str.replace('   ', ' ', regex=False).str.replace('  ', ' ', regex=False).str.strip().str.lower().to_list()

        joined1 = '. '.join(data_source1)
        joined2 = '. '.join(data_source2)

        return cosine_sim([joined1, joined2])
    
    
    def text_levenshtein(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the levenshtein distance between two items' text.
        
        Parameters
        ----------
        item_1 : str
            first item to compare. Defaults to requesting from user input.
        item_2 : str
            second item to compare. Defaults to requesting from user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        data_source1 = self.get_item(item_1).get_all_text()
        data_source2 = self.get_item(item_2).get_all_text()

        data_source1 = pd.Series(data_source1).str.replace('\n', ' ', regex = False).str.replace('<', '', regex = False).str.replace('>', '', regex = False).str.replace('\\', '', regex = False).str.replace('/', '', regex = False).str.replace('    ', '', regex = False).str.replace('   ', ' ', regex = False).str.replace('  ', ' ', regex = False).str.strip().str.lower().to_list()
        data_source2 = pd.Series(data_source2).str.replace('\n', ' ', regex = False).str.replace('<', '', regex = False).str.replace('>', '', regex = False).str.replace('\\', '', regex = False).str.replace('/', '', regex = False).str.replace('    ', '', regex = False).str.replace('   ', ' ', regex = False).str.replace('  ', ' ', regex = False).str.strip().str.lower().to_list()

        joined1 = '. '.join(data_source1)
        joined2 = '. '.join(data_source2)
        
        return lev(joined1, joined2)
    
    
    def words_pair_list_to_str(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns two items'parsed words lists as a tuple containing two strings of words.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve from. Defaults to requesting from user input.
        item_2 : str
            second item to retrieve from. Defaults to requesting from user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')

        data_source1 = self.get_item(item_1).get_all_words()
        if len(data_source1) > 0:
            data_source1 = pd.Series(data_source1).str.replace('\n', ' ', regex = False).str.replace('<', '', regex = False).str.replace('>', '', regex = False).str.replace('\\', '', regex = False).str.replace('/', '', regex = False).str.replace('    ', '', regex = False).str.replace('   ', ' ', regex = False).str.replace('  ', ' ', regex = False).str.strip().str.lower().to_list()
            joined1 = ', '.join(data_source1)
        else:
            joined1 = ''
        
        
        data_source2 = self.get_item(item_2).get_all_words()
        if len(data_source2) > 0:
            data_source2 = pd.Series(data_source2).str.replace('\n', ' ', regex = False).str.replace('<', '', regex = False).str.replace('>', '', regex = False).str.replace('\\', '', regex = False).str.replace('/', '', regex = False).str.replace('    ', '', regex = False).str.replace('   ', ' ', regex = False).str.replace('  ', ' ', regex = False).str.strip().str.lower().to_list()
            joined2 = ', '.join(data_source2)
        else:
            joined2 = ''
        
        return (joined1, joined2)
    
    def words_cosine(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the cosine similarity of two items' parsed words based on word frequencies.
        
        Parameters
        ----------
        item_1 : str
            first item to compare. Defaults to requesting from user input.
        item_2 : str
            second item to compare. Defaults to requesting from user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        pair = self.words_pair_list_to_str(item_1 = item_1, item_2 = item_2)

        return cosine_sim([pair[0], pair[1]])
    
    
    def words_levenshtein(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the levenshtein distance between two items' parsed word sets.
        
        Parameters
        ----------
        item_1 : str
            first item to compare. Defaults to requesting from user input.
        item_2 : str
            second item to compare. Defaults to requesting from user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')

        pair = self.words_pair_list_to_str(item_1 = item_1, item_2 = item_2)

        return lev(pair[0], pair[1])
    
    
    def words_set_pair(self, item_1, item_2):
        
        """
        Returns two items' parsed word sets as a tuple.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve from.
        item_2 : str
            second item to retrieve from.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        
        data_source1 = self.get_item(item_1).get_words_set()
        data_source2 = self.get_item(item_2).get_words_set()

        return (data_source1, data_source2)
        
    
    
    def words_intersect(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the intersect of two items' parsed word sets.
        
        i.e., any words shared by both items.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        sets = self.words_set_pair(item_1 = item_1, item_2 = item_2)
        data_source1 = sets[0]
        data_source2 = sets[1]
        
        return data_source1.intersection(data_source2)
    
    
    def words_intersect_size(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the size of the intersect of two items' parsed word sets.
        
        i.e., the number of words shared by both items.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        return len(self.words_intersect(item_1 = item_1, item_2 = item_2))
    
    
    def words_symmetric_difference(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the symmetric difference of two items' parsed word sets.
        
        i.e., any words *not* shared by both items.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        sets = self.words_set_pair(item_1 = item_1, item_2 = item_2)
        data_source1 = sets[0]
        data_source2 = sets[1]
        
        return data_source1.symmetric_difference(data_source2)
    
    
    def words_symmetric_difference_size(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the size of the symmetric difference of two items' parsed word sets.
        
        i.e., the number of words *not* shared by both items.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        return len(self.words_symmetric_difference(item_1 = item_1, item_2 = item_2))

    
    def words_set_sim(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the Jaccard similarity between two items' parsed words sets.
        
        i.e., how many words are found in both versus the total number of words found.
          
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')

        sets = self.words_set_pair(item_1 = item_1, item_2 = item_2)
        data_source1 = sets[0]
        data_source2 = sets[1]

        intersect_size = len(data_source1.intersection(data_source2))
        union_size = len(data_source1.union(data_source2))

        try: 
            return intersect_size / union_size

        except:
            return 0
        

    def words_comparison_series(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns all comparisons between two items' parsed words as a Pandas series.
          
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')

        series = pd.Series(index = ['Cosine similarity', 'Levenshtein distance', 'Set similarity', 'Intersect', 'Intersect size', 'Difference', 'Difference size'], dtype = 'object')

        try:
            series['Cosine similarity'] = self.words_cosine(item_1, item_2)
        except:
            series['Cosine similarity'] = 'N/A'

            
        series['Levenshtein distance'] = self.words_levenshtein(item_1, item_2)
        series['Set similarity'] = self.words_set_sim(item_1, item_2)
        series['Intersect'] = self.words_intersect(item_1, item_2)
        series['Intersect size'] = self.words_intersect_size(item_1, item_2)
        series['Difference'] = self.words_symmetric_difference(item_1, item_2)
        series['Difference size'] = self.words_symmetric_difference_size(item_1, item_2)

        return series
    
    def get_all_words_comparisons(self, sort_by = 'Set similarity'):
        
        """
        Compares items' parsed words for all combinations of two items. Returns a dataframe.
        """
        
        items = self.contents()
        df = pd.DataFrame(list(itertools.combinations(items, 2)), columns = ['First item', 'Second item'], dtype='object')
        df[['Cosine similarity', 'Levenshtein distance', 'Set similarity', 'Intersect', 'Intersect size', 'Difference', 'Difference size']] = None

        for row in df.index:
            
            item_1 = df.loc[row, 'First item']
            item_2 = df.loc[row, 'Second item']
            df.loc[row, ['Cosine similarity', 'Levenshtein distance', 'Set similarity', 'Intersect', 'Intersect size', 'Difference', 'Difference size']] = self.words_comparison_series(item_1 = item_1, item_2 = item_2)

        df['Intersect'] = df['Intersect'].apply(lambda y: None if len(y) == 0 else y)
        df['Difference'] = df['Difference'].apply(lambda y: None if len(y) == 0 else y)
        
        df = df.sort_values([sort_by], ascending=False).reset_index().drop('index', axis=1)

        return df
    
    def infer_names(self, names_source = 'all_personal_names'):
        
        """
        Identifies personal names from items' text data and appends to information sets. Uses list of all personal names by default. Parses data if not parsed.
        
        Parameters
        ----------
        names_source : str or list
            corpus of names corpus to use; or names corpus as list. Defaults to 'all_personal_names'.
        """
        
        ids = self.ids()
        for item_id in ids:
            self.get_item(item_id).infer_names(names_source = names_source)
    

    def infer_countries(self, language = 'all'):
        
        """
        Identifies country names from items' text data and appends to information sets. Uses list of all language names by default. Parses data if not parsed.
        
        Parameters
        ----------
        language : str or list
            language of country names corpus to use; or country names corpus as list. Defaults to 'all'.
        """
        
        ids = self.ids()
        for item_id in ids:
            self.get_item(item_id).infer_countries(language = language)

    def infer_cities(self, language = 'all'):
        
        """
        Identifies city names from items' text data and appends to information sets. Uses list of all city names by default. Parses data if not parsed.
        
        Parameters
        ----------
        language : str or list
            language of city names corpus to use; or city names corpus as list. Defaults to 'all'.
        """
        
        ids = self.ids()
        for item_id in ids:
            self.get_item(item_id).infer_cities(language = language)
    

    def infer_languages(self, language = 'all'):
        
        """
        Identifies language names from items' text data and appends to information sets. Uses list of all language names by default. Parses data if not parsed.
        
        Parameters
        ----------
        language : str or list
            language of language names corpus to use; or language names corpus as list. Defaults to 'all'.
        """
        
        ids = self.ids()
        for item_id in ids:
            self.get_item(item_id).infer_languages(language = language)
    
    def infer_all_info_categories(self, names = 'all_personal_names', language = 'all'):
        
        """
        Identifies potential information from items' text data and appends to information sets. Parses data if not parsed.
        
        Looks for:
            * personal names
            * country names
            * city names
            * language names
        
        Parameters
        ----------
        names : str or list
            corpus of names corpus to use; or names corpus as list. Defaults to 'all_personal_names'.
        language : str or list
            language of city names corpus to use; or city names corpus as list. Defaults to 'all'.
        """
        
        self.infer_names(names_source = names)
        self.infer_countries(language = language)
        self.infer_cities(language = language)
        self.infer_languages(language = language)
    
    def metadata_pair_df(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns two items' metadata entries a pandas.DataFrame.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve from.
        item_2 : str
            second item to retrieve from.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')

        df1 = self.get_item(item_1).metadata.astype('object').set_index('Category')
        df1[item_1] = df1['Metadata']
        df1 = df1.drop('Metadata', axis=1)
        
        df2 = self.get_item(item_2).metadata.astype('object').set_index('Category')
        df2[item_2] = df2['Metadata']
        df2 = df2.drop('Metadata', axis=1)
        
        return df1.join(df2)

    def metadata_category_levenshteins(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the levenshtein distance between metadata data entries for each category in two items.
        
        Parameters
        ----------
        item_1 : str
            first item to compare.
        item_2 : str
            second item to compare.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        input_df = self.metadata_pair_df(item_1 = item_1, item_2 = item_2).dropna().astype(str)
        output_df = pd.DataFrame(columns = ['Category', 'Levenshtein distance'])
        
        for category in input_df.index:
            
            m1 = str(input_df.loc[category, item_1])
            m2 = str(input_df.loc[category, item_2])
            
            if (m1 != None) and (m2 != None):
                
                if m1 == None:
                    m1 = ''

                if m2 == None:
                    m2 = ''

                distance = lev(m1, m2)
                
                index = len(output_df)
                output_df.loc[index, 'Category'] = category
                output_df.loc[index, 'Levenshtein distance'] = distance
        
        return output_df.sort_values('Levenshtein distance', ascending=True)
    
    
    def metadata_mean_levenshteins(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the mean levenshtein distance between metadata data entries for each category in two items.
        
        Parameters
        ----------
        item_1 : str
            first item to compare.
        item_2 : str
            second item to compare.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        return self.metadata_category_levenshteins(item_1 = item_1, item_2 = item_2)['Levenshtein distance'].mean()
    
    def metadata_list_pair(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns two items' metadata lists as a tuple.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve from.
        item_2 : str
            second item to retrieve from.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')

        data_source1 = self.get_item(item_1).get_metadata_list()
        if len(data_source1) > 0:
            joined1 = ', '.join(data_source1)
        else:
            joined1 = ''
        
        
        data_source2 = self.get_item(item_2).get_metadata_list()
        if len(data_source2) > 0:
            joined2 = ', '.join(data_source2)
        else:
            joined2 = ''
        
        return (joined1, joined2)
    
    
    def metadata_cosine(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the cosine similarity of two items' metadata lists based on word frequencies.
        
        Parameters
        ----------
        item_1 : str
            first item to compare.
        item_2 : str
            second item to compare.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        pair = self.metadata_list_pair(item_1 = item_1, item_2 = item_2)

        return cosine_sim([pair[0], pair[1]])
    
    
    def metadata_set_pair(self, item_1, item_2):
    
        """
        Returns two items' metadata sets as a tuple.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve from.
        item_2 : str
            second item to retrieve from.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        
        data_source1 = self.get_item(item_1).get_metadata_set()
        data_source2 = self.get_item(item_2).get_metadata_set()

        return (data_source1, data_source2)
    
    def metadata_union(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the union of two items' metadata sets.
        
        i.e., all metadata entries in either item.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        sets = self.metadata_set_pair(item_1 = item_1, item_2 = item_2)
        data_source1 = sets[0]
        data_source2 = sets[1]
        
        return data_source1.union(data_source2)
    
    def metadata_intersect(self, item_1 = 'request_input', item_2 = 'request_input'):

        """
        Returns the intersect of two items' metadata sets.
        
        i.e., any metadata shared by both items.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        sets = self.metadata_set_pair(item_1 = item_1, item_2 = item_2)
        data_source1 = sets[0]
        data_source2 = sets[1]
        
        return data_source1.intersection(data_source2)
    
    
    def metadata_intersect_size(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the size of the intersect of two items' metadata sets.
        
        i.e., the number of metadata entries shared by both items.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        return len(self.metadata_intersect(item_1 = item_1, item_2 = item_2))
    
    
    def metadata_symmetric_difference(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the symmetric difference of two items' metadata sets.
        
        i.e., any metadata *not* shared by both items.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        sets = self.metadata_set_pair(item_1 = item_1, item_2 = item_2)
        data_source1 = sets[0]
        data_source2 = sets[1]
        
        return data_source1.symmetric_difference(data_source2)
    
    
    def metadata_symmetric_difference_size(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the size of the symmetric difference of two items' metadata sets.
        
        i.e., the number of metadata entries *not* shared by both items.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        return len(self.metadata_symmetric_difference(item_1 = item_1, item_2 = item_2))

    
    def metadata_set_sim(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the Jaccard similarity between two items' metadata sets.
        
        i.e., how many metadata entries are found in both versus the total number of metadata entries found.
          
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')

        sets = self.metadata_set_pair(item_1 = item_1, item_2 = item_2)
        data_source1 = sets[0]
        data_source2 = sets[1]

        intersect_size = len(data_source1.intersection(data_source2))
        union_size = len(data_source1.union(data_source2))

        try: 
            return intersect_size / union_size

        except:
            return 0
        

    def metadata_comparison_series(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns all comparisons between two items' metadata entries as a Pandas series.
          
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')

        series = pd.Series(index = ['Cosine similarity', 'Mean levenshtein distance', 'Set similarity', 'Intersect', 'Intersect size', 'Difference', 'Difference size'], dtype = 'object')

        try:
            series['Cosine similarity'] = self.metadata_cosine(item_1, item_2)
        except:
            series['Cosine similarity'] = 'N/A'
            
        series['Mean levenshtein distance'] = self.metadata_mean_levenshteins(item_1, item_2)
        series['Set similarity'] = self.metadata_set_sim(item_1, item_2)
        series['Intersect'] = self.metadata_intersect(item_1, item_2)
        series['Intersect size'] = self.metadata_intersect_size(item_1, item_2)
        series['Difference'] = self.metadata_symmetric_difference(item_1, item_2)
        series['Difference size'] = self.metadata_symmetric_difference_size(item_1, item_2)

        return series
    
    def all_metadata_unions(self):
        
        """
        Returns the unions of all metadata sets from all cominations of two items as a pandas.DataFrame.
        """
        
        items = self.contents()
        df = pd.DataFrame(list(itertools.combinations(items, 2)), columns = ['First item', 'Second item'], dtype='object')
        df['Union'] = None
        df['Size'] = None

        for row in df.index:
            
            item_1 = df.loc[row, 'First item']
            item_2 = df.loc[row, 'Second item']
            union = self.metadata_union(item_1 = item_1, item_2 = item_2)
            df.at[row, 'Union'] = union
            df.loc[row, 'Size'] = len(union)
            
        df = df.sort_values('Size', ascending=False).reset_index().drop('index', axis=1)

        return df
    
    def get_all_metadata_comparisons(self, sort_by = 'Cosine similarity'):
        
        """
        Compares items' metadata for all combinations of two items. Returns a dataframe.
        """
        
        items = self.contents()
        df = pd.DataFrame(list(itertools.combinations(items, 2)), columns = ['First item', 'Second item'], dtype='object')
        df[['Cosine similarity', 'Set similarity', 'Intersect', 'Intersect size', 'Difference', 'Difference size', 'Mean levenshtein distance']] = None

        for row in df.index:
            
            item_1 = df.loc[row, 'First item']
            item_2 = df.loc[row, 'Second item']
            df.loc[row, ['Cosine similarity', 'Set similarity', 'Intersect', 'Intersect size', 'Difference', 'Difference size', 'Mean levenshtein distance']] = self.metadata_comparison_series(item_1 = item_1, item_2 = item_2)

        df['Intersect'] = df['Intersect'].apply(lambda y: None if len(y) == 0 else y)
        df['Difference'] = df['Difference'].apply(lambda y: None if len(y) == 0 else y)
        
        df = df.sort_values([sort_by], ascending=False).reset_index().drop('index', axis=1)

        return df
    
    def info_list_pair(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns two items' information lists as a tuple.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve from.
        item_2 : str
            second item to retrieve from.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')

        data_source1 = self.get_item(item_1).get_info_list()
        if len(data_source1) > 0:
            joined1 = ', '.join(data_source1)
        else:
            joined1 = ''
        
        
        data_source2 = self.get_item(item_2).get_info_list()
        if len(data_source2) > 0:
            joined2 = ', '.join(data_source2)
        else:
            joined2 = ''
        
        return (joined1, joined2)
    
    
    def info_cosine(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the cosine similarity of two items' information entries based on word frequencies.
        
        Parameters
        ----------
        item_1 : str
            first item to compare.
        item_2 : str
            second item to compare.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        pair = self.info_list_pair(item_1 = item_1, item_2 = item_2)

        return cosine_sim([pair[0], pair[1]])
    
    
    def info_set_pair(self, item_1, item_2):
        
        """
        Returns two items' information sets as a tuple.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve from.
        item_2 : str
            second item to retrieve from.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        
        data_source1 = self.get_item(item_1).get_info_set()
        data_source2 = self.get_item(item_2).get_info_set()

        return (data_source1, data_source2)
        
    def info_union(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the union of two items' information sets.
        
        i.e., all information entries in either item.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        sets = self.info_set_pair(item_1 = item_1, item_2 = item_2)
        data_source1 = sets[0]
        data_source2 = sets[1]
        
        return data_source1.union(data_source2)
    
    def info_intersect(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the intersect of two items' information sets.
        
        i.e., any information shared by both items.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        sets = self.info_set_pair(item_1 = item_1, item_2 = item_2)
        data_source1 = sets[0]
        data_source2 = sets[1]
        
        return data_source1.intersection(data_source2)
    
    
    def info_intersect_size(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the size of the intersect of two items' information sets.
        
        i.e., the number of information entries shared by both items.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        return len(self.info_intersect(item_1 = item_1, item_2 = item_2))
    
    
    def info_symmetric_difference(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the symmetric difference of two items' information sets.
        
        i.e., any information *not* shared by both items.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        sets = self.info_set_pair(item_1 = item_1, item_2 = item_2)
        data_source1 = sets[0]
        data_source2 = sets[1]
        
        return data_source1.symmetric_difference(data_source2)
    
    
    def info_symmetric_difference_size(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the size of the symmetric difference of two items' information sets.
        
        i.e., the number of information entries *not* shared by both items.
        
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')
        
        return len(self.info_symmetric_difference(item_1 = item_1, item_2 = item_2))

    
    def info_set_sim(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the Jaccard similarity between two items' information sets.
        
        i.e., how many information entries are found in both versus the total number of information entries found.
          
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')

        sets = self.info_set_pair(item_1 = item_1, item_2 = item_2)
        data_source1 = sets[0]
        data_source2 = sets[1]

        intersect_size = len(data_source1.intersection(data_source2))
        union_size = len(data_source1.union(data_source2))

        try: 
            return intersect_size / union_size

        except:
            return 0
        

    def info_comparison_series(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns all comparisons between two items' information entries as a Pandas series.
          
        Parameters
        ----------
        item_1 : str
            first item to retrieve data from. Defaults to requesting user input.
        item_2 : str
            second item to retrieve data from. Defaults to requesting user input.
        """
        
        if item_1 == 'request_input':
            item_1 = input('First item: ')

        if item_1 not in self.contents():
            raise KeyError(f'{item_1} not found in items')

        if item_2 == 'request_input':
            item_2 = input('Second item: ')

        if item_2 not in self.contents():
            raise KeyError(f'{item_2} not found in items')

        series = pd.Series(index = ['Cosine similarity', 'Mean levenshtein distance', 'Set similarity', 'Intersect', 'Intersect size', 'Difference', 'Difference size'], dtype = 'object')

        try:
            series['Cosine similarity'] = self.info_cosine(item_1, item_2)
        except:
            series['Cosine similarity'] = 'N/A'
        
        series['Set similarity'] = self.info_set_sim(item_1, item_2)
        series['Intersect'] = self.info_intersect(item_1, item_2)
        series['Intersect size'] = self.info_intersect_size(item_1, item_2)
        series['Difference'] = self.info_symmetric_difference(item_1, item_2)
        series['Difference size'] = self.info_symmetric_difference_size(item_1, item_2)

        return series
    
    def get_all_info_comparisons(self, sort_by = None):
        
        """
        Compares items' information entries for all combinations of two items. Returns a dataframe.
        """
        
        items = self.contents()
        df = pd.DataFrame(list(itertools.combinations(items, 2)), columns = ['First item', 'Second item'], dtype='object')
        df[['Cosine similarity', 'Set similarity', 'Intersect', 'Intersect size', 'Difference', 'Difference size', 'Mean levenshtein distance']] = None

        for row in df.index:
            
            item_1 = df.loc[row, 'First item']
            item_2 = df.loc[row, 'Second item']
            df.loc[row, ['Cosine similarity', 'Set similarity', 'Intersect', 'Intersect size', 'Difference', 'Difference size', 'Mean levenshtein distance']] = self.info_comparison_series(item_1 = item_1, item_2 = item_2)

        df['Intersect'] = df['Intersect'].apply(lambda y: None if len(y) == 0 else y)
        df['Difference'] = df['Difference'].apply(lambda y: None if len(y) == 0 else y)
        
        df = df.astype(object).replace(np.nan, None)
        
        
        if sort_by != None:
            df = df.sort_values(sort_by, ascending = False).reset_index().drop('index', axis=1)

        return df
    
    def all_info_unions(self):
        
        """
        Returns the unions of all metadata sets from all cominations of two items as a pandas.DataFrame.
        """
        
        items = self.contents()
        df = pd.DataFrame(list(itertools.combinations(items, 2)), columns = ['First item', 'Second item'], dtype='object')
        df['Union'] = None
        df['Size'] = None

        for row in df.index:
            
            item_1 = df.loc[row, 'First item']
            item_2 = df.loc[row, 'Second item']
            union = self.info_union(item_1 = item_1, item_2 = item_2)
            df.at[row, 'Union'] = union
            df.loc[row, 'Size'] = len(union)
            
        df = df.sort_values('Size', ascending=False).reset_index().drop('index', axis=1)

        return df


    def info_levenshteins(self, select_by_category = None, ignore_nones = True):
        
        """
        Calculates the levenshtein distance between all combinations of information labels, organised by category. Returns a pandas.DataFrame.
        """

        categories = set(self.get_info_categories())

        if type(select_by_category) == str:
            select_by_category = [select_by_category]

        if select_by_category == None:
            select_by_category = list(categories)

        if type(select_by_category) != list:
            raise TypeError('Select_by_category must be a list or sting')


        categories = [i for i in categories if i in select_by_category]

        output_df = pd.DataFrame(columns = ['Category', 'First label', 'First frequency', 'Second label', 'Second frequency', 'Levenshtein distance', 'Most frequent'])
        
        all_info_df = self.get_all_info()
        
        for category in categories:

            info_df = all_info_df[all_info_df['Category'] == category]
            info_set = set(info_df['Label'])

            category_df = pd.DataFrame(list(itertools.combinations(info_set, 2)), columns = ['First label', 'Second label'])
            category_df['Levenshtein distance'] = None

            np = category_df.to_numpy()
            index = 0

            for row in np:

                series = self.get_info_frequencies(select_by_category = category)

                first = category_df.loc[index, 'First label']
                first_freq = int(series[series.index == first].values)
                category_df.loc[index, 'First frequency'] = first_freq

                second = category_df.loc[index, 'Second label']
                second_freq = int(series[series.index == second].values)
                category_df.loc[index, 'Second frequency'] = second_freq

                category_df.loc[index, 'Levenshtein distance'] = lev(first, second)
                category_df.loc[index, 'Category'] = category

                if first_freq >= second_freq:
                    category_df.loc[index, 'Most frequent'] = first
                else:
                    category_df.loc[index, 'Most frequent'] = second

                category_df = category_df[['Category', 'First label', 'First frequency', 'Second label', 'Second frequency', 'Levenshtein distance', 'Most frequent']]
                index += 1

            output_df = pd.concat([output_df, category_df])

        output_df = output_df.sort_values('Levenshtein distance', ascending=True).reset_index().drop('index', axis=1)

        return output_df
    
    def find_info_close_matches(self, cutoff = 2, select_by_category = None, ignore_nones = True):
        
        """
        Finds similar information entries based on text similarity. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        cutoff : float
            the maximum levenshtein distance to be included in the result.
        select_by_category : str 
            specifies an information category to return. Defaults to None: metadata from all categories are returned.
        ignore_nones : bool 
            whether or not to return empty/None metadata entries. Defaults to True: empty/None entries are not returned.
        
        Notes
        -----
            * iterates through every combination of two information label/category tuples.
            * ranks based on levenshtein distance.
        """
        
        df = self.info_levenshteins(select_by_category = select_by_category, ignore_nones = ignore_nones)
        df = df[df['Levenshtein distance'] <= cutoff]
        
        return df


    def metadata_levenshteins(self, select_by_category = None, ignore_nones = True):

        """
        Calculates the levenshtein distance between two metadata entries, organised by category. Returns a dataframe.
        """
        
        categories = set(self.get_metadata_categories())

        if type(select_by_category) == str:
            select_by_category = [select_by_category]

        if select_by_category == None:
            select_by_category = list(categories)

        if type(select_by_category) != list:
            raise TypeError('Select_by_category must be a list or sting')


        categories = [i for i in categories if i in select_by_category]

        output_df = pd.DataFrame(columns = ['Category', 'First metadata', 'First frequency', 'Second metadata', 'Second frequency', 'Levenshtein distance', 'Most frequent'])
        
        all_metadata_df = self.get_all_metadata()
        
        for category in categories:

            metadata_df = all_metadata_df[all_metadata_df['Category'] == category]
            metadata_set = set(metadata_df['Metadata'])

            category_df = pd.DataFrame(list(itertools.combinations(metadata_set, 2)), columns = ['First metadata', 'Second metadata'])
            category_df['Levenshtein distance'] = None

            np = category_df.to_numpy()
            index = 0

            for row in np:

                series = self.get_metadata_frequencies(select_by_category = category).reset_index()
                first = category_df.loc[index, 'First metadata']
                first_freq = int(series[series['Metadata'] == first][0])
                
                category_df.loc[index, 'First frequency'] = first_freq

                second = category_df.loc[index, 'Second metadata']
                second_freq = int(series[series['Metadata'] == second][0])
                category_df.loc[index, 'Second frequency'] = second_freq

                category_df.loc[index, 'Levenshtein distance'] = lev(str(first), str(second))
                category_df.loc[index, 'Category'] = category

                if first_freq > second_freq:
                    category_df.loc[index, 'Most frequent'] = first
                if  second_freq > first_freq:
                    category_df.loc[index, 'Most frequent'] = second
                else:
                    category_df.loc[index, 'Most frequent'] = 'Equally frequent'

                category_df = category_df[['Category', 'First metadata', 'First frequency', 'Second metadata', 'Second frequency', 'Levenshtein distance', 'Most frequent']]
                index += 1

            output_df = pd.concat([output_df, category_df])

        output_df = output_df.sort_values('Levenshtein distance', ascending=True).reset_index().drop('index', axis=1)

        return output_df
    
    def find_metadata_close_matches(self, cutoff = 2, select_by_category = None, ignore_nones = True):
        
        """
        Finds similar metadata entries based on text similarity. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        cutoff : float
            the maximum levenshtein distance to be included in the result.
        select_by_category : str
            specifies a metadata category to return. Defaults to None: metadata from all categories are returned.
        ignore_nones : bool
            whether or not to return empty/None metadata entries. Defaults to True: empty/None entries are not returned.
        
        Notes
        -----
            * iterates through every combination of two metadata value/category tuples.
            * ranks based on levenshtein distance.
        """
        
        df = self.metadata_levenshteins(select_by_category = select_by_category, ignore_nones = ignore_nones)
        df = df[df['Levenshtein distance'] <= cutoff]
        
        return df

    def keyword_levenshteins(self, exclude_numbers = True, exclude_dates = True, limit = 600):
        
        """
        Calculates the levenshtein distance between all combinations of two keywords. Returns a pandas.DataFrame.
        """

        word_freqs_df = self.get_word_frequencies()
        
        if (limit != None) and (type(limit) == int):
            word_freqs_df = word_freqs_df[:limit]
            
        word_set = word_freqs_df.index.to_list()

        output_df = pd.DataFrame(list(itertools.combinations(word_set, 2)), columns = ['First word', 'Second word'])
        output_df['Levenshtein distance'] = None
        output_df['First frequency'] = None
        output_df['Second frequency'] = None
        output_df['Most frequent'] = None

        np = output_df.to_numpy()
        index = 0

        to_drop = []
        for row in np:

                    first = output_df.loc[index, 'First word']
                    first_freq = word_freqs_df.loc[first, 'frequency']
                    output_df.loc[index, 'First frequency'] = first_freq

                    second = output_df.loc[index, 'Second word']
                    second_freq = word_freqs_df.loc[second, 'frequency']
                    output_df.loc[index, 'Second frequency'] = second_freq

                    if exclude_numbers == True:
                        if (is_int(first) == True) and (is_int(second) == True):
                            to_drop.append(index)
                            index += 1
                            continue
                    
                    if exclude_dates == True:
                        if (
                            ((is_date(first)[0] == True)
                            or (is_time(first)[0] == True)
                            or (is_datetime(first)[0] == True))
                            and ((is_date(second)[0] == True)
                            or (is_time(second)[0] == True)
                            or (is_datetime(second)[0] == True))
                        ):
                            
                            to_drop.append(index)
                            index += 1
                            continue

                    output_df.loc[index, 'Levenshtein distance'] = lev(first, second)

                    if first_freq > second_freq:
                        output_df.loc[index, 'Most frequent'] = first
                    else:
                        if  second_freq > first_freq:
                            output_df.loc[index, 'Most frequent'] = second
                        else:
                            output_df.loc[index, 'Most frequent'] = 'Equally frequent'

                    index += 1

        output_df = output_df.drop(to_drop, axis = 0)
        output_df = output_df[['First word', 'First frequency', 'Second word', 'Second frequency', 'Levenshtein distance', 'Most frequent']]
        output_df = output_df.sort_values('Levenshtein distance', ascending=True).reset_index().drop('index', axis=1)

        return output_df

    def find_keywords_close_matches(self, cutoff = 2, exclude_numbers = True, limit = 600):
        
        """
        Finds similar keywords entries based on text similarity. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        cutoff : float
            the maximum levenshtein distance to be included in the result.
        exclude_numbers : bool
            whether to ignore strings which may be integers or floats.
        limit : int
            the maximum number of comparisons to calculate. Used to prevent excessive runtime. Defaults to 600.
        
        Notes
        -----
            * iterates through every combination of two keywords.
            * ranks based on levenshtein distance.
        """
        
        df = self.keyword_levenshteins(exclude_numbers = exclude_numbers, limit = limit)
        df = df[df['Levenshtein distance'] <= cutoff]

        return df
    
    

    # Methods for comparing multiple items
    
    def multi_items_metadata_union(self, item_list = 'request_input'):
        
        """
        Returns the union of multiple items' metadata sets.
        
        i.e., all metadata entries in all items given.
        
        Parameters
        ----------
        item_list : list
            list of item ID's to retrieve data from. Defaults to requesting user input.
        """
        
        if item_list == 'request_input':
            item_list = input('Item IDs (separate by ","): ')
            item_list = item_list.split(',')

        if type(item_list) == str:
            item_list = item_list.split(',')

        set_list = []
        for item in item_list:
            item = item.strip()
            set_list.append(self.get_item(item).get_metadata_set())
        union = set.union(*set_list)

        return union
    
    
    def multi_items_metadata_union_size(self, item_list = 'request_input'):
        
        """
        Returns the size of the union of multiple items' metadata sets.
        
        i.e., the number of unique metadata entries in all items given.
        
        Parameters
        ----------
        item_list : list
            list of item ID's to retrieve data from. Defaults to requesting user input.
        """
        
        return len(self.multi_items_metadata_union(item_list = item_list))
    
    
    def multi_items_metadata_intersect(self, item_list = 'request_input'):
        
        """
        Returns the intersect of multiple items' metadata sets.
        
        i.e., the metadata entries shared by all items given.
        
        Parameters
        ----------
        item_list : list
            list of item ID's to retrieve data from. Defaults to requesting user input.
        """
        
        if item_list == 'request_input':
            item_list = input('Item IDs (separate by ","): ')
            item_list = item_list.split(',')

        if type(item_list) == str:
            item_list = item_list.split(',')

        set_list = []
        for item in item_list:
            item = item.strip()
            set_list.append(self.get_item(item).get_metadata_set())
        intersect = set.intersection(*set_list)

        return intersect
    
    
    def multi_items_metadata_intersect_size(self, item_list = 'request_input'):
        
        """
        Returns the size of the intersect of multiple items' metadata sets.
        
        i.e., the number of metadata entries shared by all items given.
        
        Parameters
        ----------
        item_list : list
            list of item ID's to retrieve data from. Defaults to requesting user input.
        """
        
        return len(self.multi_items_metadata_intersect(item_list = item_list))
    
    
    def multi_items_metadata_symmetric_differences(self, item_list = 'request_input'):
        
        """
        Returns the symmetric difference of multiple items' metadata sets.
        
        i.e., the metadata entries *not* shared by all items given.
        
        Parameters
        ----------
        item_list : list
            list of item ID's to retrieve data from. Defaults to requesting user input.
        """
        
        if item_list == 'request_input':
            item_list = input('Item IDs (separate by ","): ')
            item_list = item_list.split(',')

        if type(item_list) == str:
            item_list = item_list.split(',')

        diff_set = set()
        for item in item_list:
            item = item.strip()
            item_set = self.get_item(item).get_metadata_set()
            diff_set = set.symmetric_difference(diff_set, item_set)
        
        return diff_set


    def multi_items_metadata_symmetric_differences_size(self, item_list = 'request_input'):
        
        """
        Returns the size of the symmetric difference of multiple items' metadata sets.
        
        i.e., the number of metadata entries *not* shared by all items given.
        
        Parameters
        ----------
        item_list : list
            list of item ID's to retrieve data from. Defaults to requesting user input.
        """
        
        return len(self.multi_items_metadata_symmetric_differences(item_list = item_list))
    
    
    def multi_items_metadata_set_similarity(self, item_list = 'request_input'):
        
        """
        Returns the Jaccard similarity between multiple items' metadata sets.
        
        i.e., how many metadata entries are found in all items versus the total number of metadata entries found.
          
        Parameters
        ----------
        item_list : list
            list of item ID's to retrieve data from. Defaults to requesting user input.
        """
        
        if item_list == 'request_input':
            item_list = input('Item IDs (separate by ","): ')
            item_list = item_list.split(',')
        
        metadata_union_size = self.multi_items_metadata_union_size(item_list = item_list)
        metadata_intersect_size = self.multi_items_metadata_intersect_size(item_list = item_list)
        metadata_similarity = metadata_intersect_size / metadata_union_size

        return metadata_similarity


    def multi_items_info_union(self, item_list = 'request_input'):
        
        """
        Returns the union of multiple items' information sets.
        
        i.e., all information entries in all items given.
        
        Parameters
        ----------
        item_list : list
            list of item ID's to retrieve data from. Defaults to requesting user input.
        """
        
        if item_list == 'request_input':
            item_list = input('Item IDs (separate by ","): ')
            item_list = item_list.split(',')

        if type(item_list) == str:
            item_list = item_list.split(',')

        set_list = []
        for item in item_list:
            item = item.strip()
            set_list.append(self.get_item(item).get_info_set())
        union = set.union(*set_list)

        return union
    
    
    def multi_items_info_union_size(self, item_list = 'request_input'):
        
        """
        Returns the size of the union of multiple items' information sets.
        
        i.e., the number of unique information entries in all items given.
        
        Parameters
        ----------
        item_list : list
            list of item ID's to retrieve data from. Defaults to requesting user input.
        """
        
        return len(self.multi_items_info_union(item_list = item_list))
    
    
    def multi_items_info_intersect(self, item_list = 'request_input'):
        
        """
        Returns the intersect of multiple items' information sets.
        
        i.e., the information entries shared by all items given.
        
        Parameters
        ----------
        item_list : list
            list of item ID's to retrieve data from. Defaults to requesting user input.
        """
        
        if item_list == 'request_input':
            item_list = input('Item IDs (separate by ","): ')
            item_list = item_list.split(',')

        if type(item_list) == str:
            item_list = item_list.split(',')

        set_list = []
        for item in item_list:
            item = item.strip()
            set_list.append(self.get_item(item).get_info_set())
        intersect = set.intersection(*set_list)

        return intersect
    
    
    def multi_items_info_intersect_size(self, item_list = 'request_input'):
        
        """
        Returns the size of the intersect of multiple items' information sets.
        
        i.e., the number of information entries shared by all items given.
        
        Parameters
        ----------
        item_list : list
            list of item ID's to retrieve data from. Defaults to requesting user input.
        """
        
        return len(self.multi_items_info_intersect(item_list = item_list))
    
    
    def multi_items_info_symmetric_differences(self, item_list = 'request_input'):
        
        """
        Returns the symmetric difference of multiple items' information sets.
        
        i.e., the information entries *not* shared by all items given.
        
        Parameters
        ----------
        item_list : list
            list of item ID's to retrieve data from. Defaults to requesting user input.
        """
        
        if item_list == 'request_input':
            item_list = input('Item IDs (separate by ","): ')
            item_list = item_list.split(',')

        if type(item_list) == str:
            item_list = item_list.split(',')

        diff_set = set()
        for item in item_list:
            item = item.strip()
            item_set = self.get_item(item).get_info_set()
            diff_set = set.symmetric_difference(diff_set, item_set)
        
        return diff_set


    def multi_items_info_symmetric_differences_size(self, item_list = 'request_input'):
        
        """
        Returns the size of the symmetric difference of multiple items' information sets.
        
        i.e., the number of information entries *not* shared by all items given.
        
        Parameters
        ----------
        item_list : list
            list of item ID's to retrieve data from. Defaults to requesting user input.
        """
        
        return len(self.multi_items_info_symmetric_differences(item_list = item_list))
    
    
    def multi_items_info_set_similarity(self, item_list = 'request_input'):
        
        """
        Returns the Jaccard similarity between multiple items' information sets.
        
        i.e., how many information entries are found in all items versus the total number of information entries found.
          
        Parameters
        ----------
        item_list : list
            list of item ID's to retrieve data from. Defaults to requesting user input.
        """
        
        if item_list == 'request_input':
            item_list = input('Item IDs (separate by ","): ')
            item_list = item_list.split(',')
        
        info_union_size = self.multi_items_info_union_size(item_list = item_list)
        info_intersect_size = self.multi_items_info_intersect_size(item_list = item_list)
        info_similarity = info_intersect_size / info_union_size

        return info_similarity

    # Methods for parsing and cleaning data
    
    def parse_rawdata(self, item_id = 'all'):
        
        """
        Parses raw data entries for all inputted items. Defaults to all. 
        
        Parameters
        ----------
        item_id : str
            one or more item ID's to parse.
        
        Returns
        -------
        result : pandas.Series
            a Pandas series of parsed data dictionaries.
        """
        
        if type(item_id) != str:
            raise TypeError('Item ID must be a string')
        
        if item_id == 'all':
            ids = self.ids()
        
        else:
            ids = [item_id]
        
        for item in ids:
            if item != 'all':
                self.get_item(item).parse_rawdata()
                self.get_item(item).extract_links_from_html(append_to_item = True)
        
        self.update_properties()
        
        return self.get_all_data()['Parsed data']
    
    
    def extract_links(self, item_id = 'all'):
        
        """
        Extracts links from all inputted items' raw data. Defaults to 'all'. 
        
        Parameters
        ----------
        item_id : str
            one or more item ID's to parse.
        """
        
        if type(item_id) != str:
            raise TypeError('Item ID must be a string')
        
        if item_id == 'all':
            ids = self.ids()
        
        else:
            ids = [item_id]
        
        for item in ids:
            if item != 'all':
                self.get_item(item).extract_links_from_html(append_to_item = True)

        self.update_properties()

        
    # Methods for comparing items' time metadata
    
    def created_time_difference(self, first_item = 'request_input', second_item = 'request_input'):
        
        """
        Returns the time difference between items' created time metadata entries.
        
        Returns
        -------
        time_difference : datetime.timedelta
            the time difference between items' created time metadata entries.
        """
        
        if first_item == 'request_input':
            first_item = input('First item ID: ')
        
        if second_item == 'request_input':
            second_item = input('Second item ID: ')
            
        try:
            dt1 = self.get_item(first_item).get_metadata('created_at')['Metadata'].values[0]
        except:
            raise ValueError(f'{first_item} does not have a created date-time')
        
        try:
            dt2 = self.get_item(second_item).get_metadata('created_at')['Metadata'].values[0]
        except:
            raise ValueError(f'{second_item} does not have a created date-time entry')
            
        return time_difference(str(dt1), str(dt2))
    
    
    def last_changed_time_difference(self, first_item = 'request_input', second_item = 'request_input'):
        
        """
        Returns the time difference between items' last changed time metadata entries.
        
        Returns
        -------
        time_difference : datetime.timedelta
            the time difference between items' last changed time metadata entries.
        """
        
        if first_item == 'request_input':
            first_item = input('First item ID: ')
        
        if second_item == 'request_input':
            second_item = input('Second item ID: ')
        
        try:
            dt1 = self.get_item(first_item).get_metadata('last_changed_at')['Metadata'].values[0]
        except:
            raise ValueError(f'{first_item} does not have a last edited date-time entry')
        
        try:
            dt2 = self.get_item(second_item).get_metadata('last_changed_at')['Metadata'].values[0]
        except:
            raise ValueError(f'{second_item} does not have a last edited date-time entry')

        return time_difference(str(dt1), str(dt2))
    
    
    def upload_time_difference(self, first_item = 'request_input', second_item = 'request_input'):
        
        """
        Returns the time difference between items' uploaded time metadata entries.
        
        Returns
        -------
        time_difference : datetime.timedelta
            the time difference between items' uploaded time metadata entries.
        """
        
        if first_item == 'request_input':
            first_item = input('First item ID: ')
        
        if second_item == 'request_input':
            second_item = input('Second item ID: ')
        
        try:
            dt1 = self.get_item(first_item).get_metadata('uploaded_at')['Metadata'].values[0]
        except:
            raise ValueError(f'{first_item} does not have an uploaded date-time entry')
        
        try:
            dt2 = self.get_item(second_item).get_metadata('uploaded_at')['Metadata'].values[0]
        except:
            raise ValueError(f'{second_item} does not have an uploaded date-time entry')

        return time_difference(str(dt1), str(dt2))

    def get_created_times(self) -> pd.DataFrame:

        """
        Returns created time metadata for all items as a pandas.DataFrame.
        """
        
        df = pd.DataFrame(columns = ['Item', 'Created at'])

        index = 0
        for item_id in self.contents():

            series = self.get_item(item_id).get_metadata('created_at')
            if len(series.index) > 0:
                dt = series.reset_index().loc[0, 'Metadata']
            else:
                dt = None
            df.loc[index] = [item_id, dt]
            index += 1

        return df.astype(object).sort_values('Created at', ascending=False).reset_index().drop('index',axis=1).replace(pd.NaT, None)
    
    

    def get_uploaded_times(self):
        
        """
        Returns uploaded time metadata for all items as a pandas.DataFrame.
        """
        
        df = pd.DataFrame(columns = ['Item', 'Uploaded at'])

        index = 0
        for item_id in self.contents():

                series = self.get_item(item_id).get_metadata('uploaded_at')
                if len(series.index) > 0:
                    dt = series.reset_index().loc[0, 'Metadata']
                else:
                    dt = None
                df.loc[index] = [item_id, dt]
                index += 1

        return df.astype(object).sort_values('Uploaded at', ascending=False).reset_index().drop('index',axis=1).replace(pd.NaT, None)

    def get_last_changed_times(self):
        
        """
        Returns last changed time metadata for all items as a pandas.DataFrame.
        """
        
        df = pd.DataFrame(columns = ['Item', 'Last changed at'])

        index = 0
        for item_id in self.contents():

            series = self.get_item(item_id).get_metadata('last_changed_at')
            if len(series.index) > 0:
                dt = series.reset_index().loc[0, 'Metadata']
            else:
                dt = None
            df.loc[index] = [item_id, dt]
            index += 1

        return df.astype(object).sort_values('Last changed at', ascending=False).reset_index().drop('index',axis=1).replace(pd.NaT, None)

    
    def get_all_time_metadata(self):
        
        """
        Returns all time metadata as a pandas.DataFrame.
        """
        
        created_df = self.get_created_times().set_index('Item')
        uploaded_df = self.get_uploaded_times().set_index('Item')
        changed_df = self.get_last_changed_times().set_index('Item')
        output_df = pd.concat([created_df, uploaded_df, changed_df], axis=1).sort_values('Created at')

        return output_df
    
    
    def created_time_range(self):
        
        """
        Returns the difference between the first and last created time metadata entries.
        """
        
        df = self.get_created_times()
        df = df.dropna()

        if len(df.index) > 2:
            return df.iloc[0][1] - df.iloc[-1][1]
        else:
            raise ValueError('No created times found')

    
    def uploaded_time_range(self):
        
        """
        Returns the difference between the first and last uploaded time metadata entries.
        """
        
        df = self.get_uploaded_times()
        df = df.dropna()
        
        if len(df.index) > 2:
            return df.iloc[0][1] - df.iloc[-1][1]
        else:
            raise ValueError('No uploaded times found')

            
    def last_changed_time_range(self):
        
        """
        Returns the difference between the oldest and most recent last changed time metadata entries.
        """
        
        df = self.get_last_changed_times()
        df = df.dropna()
        
        if len(df.index) > 2:
            return df.iloc[0][1] - df.iloc[-1][1]
        else:
            raise ValueError('No last changed times found')
    
    
    def timeline(self, plot = 'created_at', units = 'months', intervals = 4, date_format = '%d.%m.%Y', colour = 'blue'):
        
        """
        Plots a timeline of items' time metadata. User can select which metadata to plot and the units to use. Defaults to 'created_at'.
        
        Parameters
        ----------
        plot : str
            which time metadata variable to plot. Defaults to 'created_at'.
        units : str
            time units to use for plot. Defaults to 'months'.
        intervals : int
            time intervals to use for plot. Defaults to 4.
        date_format : str
            date format to use for plot. Defaults to '%d.%m.%Y'.
        colour : str
            colour to use for plot. Defaults to 'blue'.
        """
        
        if plot == 'created_at':
            dates_res = self.get_created_times().dropna()
            dates = dates_res['Created at'].to_list()

        if plot == 'uploaded_at':
            dates_res = self.get_uploaded_times().dropna()
            dates = dates_res['Uploaded at'].to_list()

        if plot == 'last_changed':
            dates_res = self.get_last_changed_times().dropna()
            dates = dates_res['Last changed at'].to_list()

        names = dates_res['Item'].to_list()
        
        plot_timeline(dates = dates, names = names, plot = plot, units = units, intervals = intervals, date_format = date_format, colour = colour)
        
        
    def metadata_time_ranges(self) -> pd.DataFrame:
        
        """
        Returns the time difference between created and last changed metadata for all items.
        """
        
        df = self.get_all_time_metadata()

        df['start'] = df['Created at']
        df['end'] = df['Last changed at']
        df = df[['start', 'end']].dropna(subset = 'start').reset_index()

        for i in df.index:
            try:
                df.loc[i, 'diff'] = df.loc[i,'end'] - df.loc[i,'start']
            except:
                try:
                    df['diff'] = df.loc[i,'start'] - df.loc[i,'start']
                except:
                    try:
                        df['diff'] = df.loc[i,'end'] - df.loc[i,'end']
                    except:
                        df['diff'] = timedelta(days=0)
        
        return df
    
    
    def plot_metadata_time_ranges(self):
        
        """
        Plots a timeline of items' edit histories.
        """
        
        df = self.metadata_time_ranges()
        labels = df['Item'].to_list()

        plot_date_range_timeline(source = df, labels = labels)
    
    

    def normalised_time_metadata_difference(self, first_item = 'request_input', second_item = 'request_input', time_metadata = 'created_at', units = 'years'):
        
        """
        Calculates the normalised time difference for two items' time metadata.
        
        Parameters
        ----------
        first_item : str
            item ID of first item for comparison. Defaults to requesting user input.
        second_item : str
            item ID of first item for comparison. Defaults to requesting user input.
        time_metadata : str
            name of time metadata category to use. Defaults to 'created_at'.
        units : str
            unit of time for results. Defaults to 'years'.
        
        Returns
        -------
        result : float
            a value between 0 and 1, where 0 is 0 distance and 1 is infinity.
        
        Notes
        -----
            * Normalisation function: map_inf_to_1()
        """
        
        if first_item == 'request_input':
            first_item = input('First item ID: ')
        
        if second_item == 'request_input':
            second_item = input('Second item ID: ')
    
        df1 = self.get_item(first_item).get_time_metadata()
        df2 = self.get_item(second_item).get_time_metadata()
        
        first_datetime = str(df1[df1.index == time_metadata]['Metadata'][time_metadata])
        second_datetime = str(df2[df2.index == time_metadata]['Metadata'][time_metadata])
    
        return normalised_time_difference(first_datetime = first_datetime, second_datetime = first_datetime, units = units)
    
    
    def normalised_time_metadata_similarity(self, first_item = 'request_input', second_item = 'request_input', time_metadata = 'created_at', units = 'years'):
        
        """
        Calculates the normalised time similarity for two items' time metadata.
        
        Parameters
        ----------
        first_item : str
            item ID of first item for comparison. Defaults to requesting user input.
        second_item : str
            item ID of first item for comparison. Defaults to requesting user input.
        time_metadata : str
            name of time metadata category to use. Defaults to 'created_at'.
        units : str
            unit of time for results. Defaults to 'years'.
        
        Returns
        -------
        result : float
            a value between 0 and 1, where 0 is 0 distance and 1 is infinity.
        
        Notes
        -----
            * Normalisation function: map_inf_to_0()
        """
        
        if first_item == 'request_input':
            first_item = input('First item ID: ')
        
        if second_item == 'request_input':
            second_item = input('Second item ID: ')
    
        df1 = self.get_item(first_item).get_time_metadata()
        df2 = self.get_item(second_item).get_time_metadata()
        
        first_datetime = str(df1[df1.index == time_metadata]['Metadata'][time_metadata])
        second_datetime = str(df2[df2.index == time_metadata]['Metadata'][time_metadata])

        return normalised_time_difference_inverse(first_datetime = first_datetime, second_datetime = second_datetime, units = units)

    

    def time_diff_from_date(self, select_by = 'created_at', date = 'request_input', within = 100, units = 'days', ignore_nones = True):
        
        """
        Returns all items which have time metadata within a specified range from a given date. 
        
        Parameters
        ----------
        select_by : str
            name of time metadata category to use. Defaults to 'created_at'.
        date : str
            date or datetime to compare items with. Defaults to requesting user input.
        within : int
            maximum time range.
        units : str
            unit of time for results. Defaults to 'years'.
        ignore_nones : bool
            whether or not to ignore time metadata values which equal None or ''. Defaults to True.
        
        
        Returns
        -------
        result : pandas.DataFrame
            a pandas.DataFrame containing details for items which lie in the time range.
        """
        
        if date == 'request_input':
            date = input('Find dates close to: ')

        ref_dt = str_to_datetime(date)

        output_df = pd.DataFrame(columns = ['Item', 'Time difference'], dtype = object)

        index = 0
        for item in self.contents():

            dt = self.get_item(item).created_at().loc[select_by, 'Metadata']

            if dt != None:
                time_delta = abs(ref_dt - dt)
            else:
                time_delta = None

            output_df.loc[index] = [item, time_delta]
            index += 1

        if ignore_nones == True:
            output_df = output_df.dropna()

        if units == 'days':
            limit = timedelta(within)

        output_df = output_df[output_df['Time difference'] <= limit]

        return output_df.sort_values('Time difference').reset_index().drop('index', axis=1)

    

    # Methods for comparing items' geolocation metadata
    
    def coordinates_distance(self, first_item = 'request_input', second_item = 'request_input', units = 'kilometers'):
        
        """
        Returns the geographic distance between two items using their coordinates metadata.
        
        Parameters
        ----------
        first_item : str
            item ID of first item for comparison. Defaults to requesting user input.
        second_item : str
            item ID of first item for comparison. Defaults to requesting user input.
        units : str
            unit for measurement.
        
        Returns
        -------
        coordinates_distance : int
            distance in unit specified by user; defaults to 'kilometers'.
        """
        
        if first_item == 'request_input':
            first_item = input('First item ID: ')
        
        if second_item == 'request_input':
            second_item = input('Second item ID: ')
            
        first_coordinates = self.get_item(first_item).coordinates_metadata()
        if first_coordinates == None:
            raise ValueError(f'{first_item} does not have coordinates metadata')
        
        second_coordinates = self.get_item(second_item).coordinates_metadata()
        if second_coordinates == None:
            raise ValueError(f'{second_item} does not have coordinates metadata')

        return coordinates_distance(first_coordinates, second_coordinates, units = units)
    
    
    def locations_distance(self, first_item = 'request_input', second_item = 'request_input', units = 'kilometers'):
        
        """
        Returns the geographic distance between two items using their locations metadata.
        
        Parameters
        ----------
        first_item : str
            item ID of first item for comparison. Defaults to requesting user input.
        second_item : str
            item ID of first item for comparison. Defaults to requesting user input.
        units : str
            unit for measurement.
        
        Returns
        -------
        locations_distance : int
            distance in unit specified by user; defaults to 'kilometers'.
        """
        
        if first_item == 'request_input':
            first_item = input('First item ID: ')
        
        if second_item == 'request_input':
            second_item = input('Second item ID: ')
        
        first_location = self.get_item(first_item).location_metadata()
        if first_location == None:
            raise ValueError(f'{first_item} does not have location metadata')
        
        second_location = self.get_item(second_item).location_metadata()
        if second_location == None:
            raise ValueError(f'{second_item} does not have location metadata')

        first_coordinates = get_location_coordinates(first_location)
        second_coordinates = get_location_coordinates(second_location)

        return coordinates_distance(first_coordinates = first_coordinates, second_coordinates = second_coordinates, units = units)

    def normalised_coordinates_metadata_diffference(self, first_item = 'request_input', second_item = 'request_input', units = 'kilometers'):
        
        """
        Calculates the normalised distance between two items' coordinates, using units provided by user.
        
        Parameters
        ----------
        first_item : str
            item ID of first item for comparison. Defaults to requesting user input.
        second_item : str
            item ID of first item for comparison. Defaults to requesting user input.
        units : str
            unit for measurement.
        
        Returns
        -------
        result : float
            a value between 0 and 1, where 0 is 0 distance and 1 is infinite distance.
        
        
        Notes
        -----
            * Normalisation function: map_inf_to_1()
        """
        
        if first_item == 'request_input':
            first_item = input('First item ID: ')
        
        if second_item == 'request_input':
            second_item = input('Second item ID: ')
            
        first_coordinates = self.get_item(first_item).coordinates_metadata()
        if first_coordinates == None:
            raise ValueError(f'{first_item} does not have coordinates metadata')
        
        second_coordinates = self.get_item(second_item).coordinates_metadata()
        if second_coordinates == None:
            raise ValueError(f'{second_item} does not have coordinates metadata')
        
        return normalised_coordinates_distance(first_coordinates = first_coordinates, second_coordinates = second_coordinates, units = units)
    
    
    def normalised_coordinates_metadata_similarity(self, first_item = 'request_input', second_item = 'request_input', units = 'kilometers'):
        
        """
        Calculates the inverse of the normalised distance between two items' coordinates, using units provided by user.
        
        Parameters
        ----------
        first_item : str
            item ID of first item for comparison. Defaults to requesting user input.
        second_item : str
            item ID of first item for comparison. Defaults to requesting user input.
        units : str
            unit for measurement.
        
        Returns
        -------
        result : float
            a value between 0 and 1, where 0 is infinite distance and 0 is infinite distance.
        
        Notes
        -----
            * Normalisation function: map_inf_to_0()
        """
        
        if first_item == 'request_input':
            first_item = input('First item ID: ')
        
        if second_item == 'request_input':
            second_item = input('Second item ID: ')
            
        first_coordinates = self.get_item(first_item).coordinates_metadata()
        if first_coordinates == None:
            raise ValueError(f'{first_item} does not have coordinates metadata')
        
        second_coordinates = self.get_item(second_item).coordinates_metadata()
        if second_coordinates == None:
            raise ValueError(f'{second_item} does not have coordinates metadata')
        
        return normalised_coordinates_distance_inverse(first_coordinates = first_coordinates, second_coordinates = second_coordinates, units = units)
    
    
    def normalised_location_metadata_difference(self, first_item = 'request_input', second_item = 'request_input', units = 'kilometers'):
        
        """
        Calculates the normalised distance between two items' location metadata entries, using units provided by user.
        
        Parameters
        ----------
        first_item : str
            item ID of first item for comparison. Defaults to requesting user input.
        second_item : str
            item ID of first item for comparison. Defaults to requesting user input.
        units : str
            unit for measurement.
        
        Returns
        -------
        result : float
            a value between 0 and 1, where 0 is 0 distance and 1 is infinite distance.
        
        
        Notes
        -----
            * Normalisation function: map_inf_to_1()
        """
        
        if first_item == 'request_input':
            first_item = input('First item ID: ')
        
        if second_item == 'request_input':
            second_item = input('Second item ID: ')
        
        first_location = self.get_item(first_item).location_metadata()
        if first_location == None:
            raise ValueError(f'{first_item} does not have location metadata')
        
        second_location = self.get_item(second_item).location_metadata()
        if second_location == None:
            raise ValueError(f'{second_item} does not have location metadata')

        return normalised_locations_distance(first_location = first_location, second_location = second_location, units = units)
    
    
    def normalised_location_metadata_similarity(self, first_item = 'request_input', second_item = 'request_input', units = 'kilometers'):
        
        """
        Calculates the inverse of the normalised distance between two items' location metadata entries, using units provided by user.
        
        Parameters
        ----------
        first_item : str
            item ID of first item for comparison. Defaults to requesting user input.
        second_item : str
            item ID of first item for comparison. Defaults to requesting user input.
        units : str
            unit for measurement.
        
        Returns
        -------
        result : float
            a value between 0 and 1, where 0 is infinite distance and 0 is infinite distance.
        
        Notes
        -----
            * Normalisation function: map_inf_to_0()
        """
        
        if first_item == 'request_input':
            first_item = input('First item ID: ')
        
        if second_item == 'request_input':
            second_item = input('Second item ID: ')
        
        first_location = self.get_item(first_item).location_metadata()
        if first_location == None:
            raise ValueError(f'{first_item} does not have location metadata')
        
        second_location = self.get_item(second_item).location_metadata()
        if second_location == None:
            raise ValueError(f'{second_item} does not have location metadata')

        return normalised_locations_distance_inverse(first_location = first_location, second_location = second_location, units = units)

    

    # Methods for checking if items and data are included in the item set
    
    def check_for_item_id(self, item_id = 'request_input') -> bool:
        
        """
        Checks if an item ID is in the item set.
        """
        
        if item_id == 'request_input':
            item_id = input('Item ID: ')
    
        if item_id in self.contents():
            return True

        else: 
            return False
    
    
    def check_for_info(self, label = 'request_input', category = 'all'):
        
        """
        Checks if a string matches any of the item set's information entries.
        """
        
        if label == 'request_input':
            label = input('Information label: ')
        
        if category == 'all':
            category = None
        
        df = self.get_all_info(select_by_category = category).copy(deep=True).astype(str)
        
        if label in df['Label'].str.lower().to_list():
            return True

        else: 
            return False
    
    
    def check_for_metadata(self, metadata = 'request_input', category = 'all'):
        
        """
        Checks if a string matches any of the item set's metadata entries.
        """
        
        if metadata == 'request_input':
            metadata = input('Metadata label: ')
        
        if category == 'all':
            category = None
        
        df = self.get_all_metadata(select_by_category = category).copy(deep=True).astype(str)
        
        if metadata in df['Metadata'].str.lower().to_list():
            return True

        else: 
            return False
    
    
    def check_for_link(self, link = 'request_input'):
        
        """
        Checks if a string matches any of the item set's link entries.
        """
        
        if link == 'request_input':
            link = input('Link: ')
        
        links_set = self.get_links_set()
        
        if link in links_set:
            return True
        
        else: 
            return False
    
    
    def check_for_address(self, address = 'request_input'):
        
        """
        Checks if a string matches any of the item set's address metadata entries.
        """
        
        if address == 'request_input':
            address = input('Address: ')
        
        addresses = self.get_all_addresses()
        
        if address in addresses['Metadata'].to_list():
            return True
        
        else: 
            return False
    
    

    def check_link_between(self, item_id1 = 'request_input', item_id2 = 'request_input'):
        
        """
        Checks if an item contains a link to another item.
        """
        
        if item_id1 == 'request_input':
            item_id1 = input('First item ID: ')

        if item_id2 == 'request_input':
            item_id2 = input('Second item ID: ')

        item_2_address = self.get_item(item_id2).get_url()
        if item_2_address == None:
            return False

        item_1_links = self.get_item(item_id1).links
        if item_1_links == None:
            return False

        if item_2_address in item_1_links:
            return True
        else: 
            return False

    def check_ref_between(self, item_id1 = 'request_input', item_id2 = 'request_input'):
        
        """
        Checks if an item contains a reference to another item.
        """
        
        if item_id1 == 'request_input':
            item_id1 = input('First item ID: ')

        if item_id2 == 'request_input':
            item_id2 = input('Second item ID: ')

        item_1_refs = self.get_item(item_id1).references
        if item_1_refs == None:
            return False

        item_2_refs = self.get_item(item_id2).references
        if item_2_refs == None:
            return False

        if item_2_refs in item_1_refs:
            return True
        else: 
            return False
        

    # Methods for indexing items by their data
    
    def index_by_info(self, by_labels = True, by_categories = True):
        
        """
        Indexes items by information each item contains. Returns a dataframe.
        """

        all_info = self.get_all_info()
        df = all_info[['Label', 'Category']].drop_duplicates()
        
        if (by_labels == True) and (by_categories == True):
            
            info = df.copy(deep=True)
            
            info['Items'] = None
            info['Item count'] = None
            info['Total frequency'] = None
            info['Mean frequency'] = None
            info['Breakdown'] = None

            for i in range(0, len(info.index)):
                index = info.index[i]
                label = info.iloc[i, 0]
                category = info.iloc[i, 1]
                found_series = all_info[
                                    (all_info['Label'] == label) 
                                    & (all_info['Category'] == category)
                                    ]['Found in']
                
                found_in = set(found_series)
                found_in_count = len(found_series)
                found_in_freqs = found_series.value_counts().to_dict()
                info.at[index, 'Items'] = found_in
                info.at[index, 'Item count'] = len(found_in)
                info.at[index, 'Total frequency'] = found_in_count
                info.at[index, 'Mean frequency'] = found_in_count / self.count_items()
                info.at[index, 'Breakdown'] = found_in_freqs
            
            info = info.drop_duplicates(['Label', 'Category', 'Item count', 'Total frequency', 'Mean frequency'])
        
        else:
            
            if by_labels == True:
                info = df['Label'].drop_duplicates().reset_index().drop('index',axis=1)
                mask = 'Label'

            
            if by_categories == True:
                info = df['Category'].drop_duplicates().reset_index().drop('index',axis=1)
                mask = 'Category'
        
            info['Items'] = None
            info['Item count'] = None
            info['Total frequency'] = None
            info['Mean frequency'] = None
            info['Breakdown'] = None
            
            for i in range(0, len(info.index)):
                index = info.index[i]
                mask_term = info.iloc[i, 0]
                found_series = all_info[all_info[mask] == mask_term]['Found in']
                found_in = set(found_series)
                found_in_count = len(found_series)
                found_in_freqs = found_series.value_counts().to_dict()
                info.at[index, 'Items'] = found_in
                info.at[index, 'Item count'] = len(found_in)
                info.at[index, 'Total frequency'] = found_in_count
                info.at[index, 'Mean frequency'] = found_in_count / self.count_items()
                info.at[index, 'Breakdown'] = found_in_freqs
            
            if 'Label' in info.columns:
                info = info.drop_duplicates(['Label', 'Item count', 'Total frequency', 'Mean frequency'])
            
            if 'Category' in info.columns:
                info = info.drop_duplicates(['Category', 'Item count', 'Total frequency', 'Mean frequency'])
            
        return info.sort_values('Item count', ascending=False).reset_index().drop('index',axis=1)
    
    def index_by_info_label(self):
        
        """
        Indexes items by information labels they contain. Returns a dataframe.
        """
        
        return self.index_by_info(by_categories = False)
    
    def index_by_info_category(self):
        
        """
        Indexes items by information categories they contain. Returns a dataframe.
        """
        
        return self.index_by_info(by_labels = False)
    
    def index_by_metadata(self, by_entries = True, by_categories = True):
        
        """
        Indexes items by each item's metadata. Returns a dataframe.
        """
        
        all_metadata = self.get_all_metadata()
        df = all_metadata[['Metadata', 'Category']].drop_duplicates()
        
        if (by_entries == True) and (by_categories == True):
            
            metadata = df.copy(deep=True)
            
            metadata['Items'] = None
            metadata['Item count'] = None
            metadata['Total frequency'] = None
            metadata['Mean frequency'] = None
            metadata['Breakdown'] = None

            for i in range(0, len(metadata.index)):
                index = metadata.index[i]
                entry = metadata.iloc[i, 0]
                category = metadata.iloc[i, 1]
                found_series = all_metadata[
                                    (all_metadata['Metadata'] == entry) 
                                    & (all_metadata['Category'] == category)
                                    ]['Found in']
                
                found_in = set(found_series)
                found_in_count = len(found_series)
                found_in_freqs = found_series.value_counts().to_dict()
                metadata.at[index, 'Items'] = found_in
                metadata.at[index, 'Item count'] = len(found_in)
                metadata.at[index, 'Total frequency'] = found_in_count
                metadata.at[index, 'Mean frequency'] = found_in_count / self.count_items()
                metadata.at[index, 'Breakdown'] = found_in_freqs
            
            metadata = metadata.drop_duplicates(['Metadata', 'Category', 'Item count', 'Total frequency', 'Mean frequency'])
        
        else:
            
            if by_entries == True:
                metadata = df['Metadata'].drop_duplicates().reset_index().drop('index',axis=1)
                mask = 'Metadata'

            
            if by_categories == True:
                metadata = df['Category'].drop_duplicates().reset_index().drop('index',axis=1)
                mask = 'Category'

            metadata['Items'] = None
            metadata['Item count'] = None
            metadata['Total frequency'] = None
            metadata['Mean frequency'] = None
            metadata['Breakdown'] = None
            
            for i in range(0, len(metadata.index)):
                index = metadata.index[i]
                mask_term = metadata.iloc[i, 0]
                found_series = all_metadata[all_metadata[mask] == mask_term]['Found in']
                found_in = set(found_series)
                found_in_count = len(found_series)
                found_in_freqs = found_series.value_counts().to_dict()
                metadata.at[index, 'Items'] = found_in
                metadata.at[index, 'Item count'] = len(found_in)
                metadata.at[index, 'Total frequency'] = found_in_count
                metadata.at[index, 'Mean frequency'] = found_in_count / self.count_items()
                metadata.at[index, 'Breakdown'] = found_in_freqs
            
            if 'Metadata' in metadata.columns:
                metadata = metadata.astype(str).drop_duplicates(['Metadata', 'Item count', 'Total frequency', 'Mean frequency'])
            
            if 'Category' in metadata.columns:
                metadata = metadata.astype(str).drop_duplicates(['Category', 'Items', 'Total frequency', 'Mean frequency'])
        
        metadata = metadata.sort_values('Item count', ascending=False).reset_index().drop('index',axis=1)
        return metadata
    
    def index_by_metadata_entry(self):
        
        """
        Indexes items by each item's metadata entries. Returns a dataframe.
        """
        
        return self.index_by_metadata(by_categories = False)
    
    def index_by_metadata_category(self):
        
        """
        Indexes items by each item's categories. Returns a dataframe.
        """
        
        return self.index_by_metadata(by_entries = False).sort_values('Item count', ascending=False).reset_index().drop('index',axis=1)


    def index_by_words(self, word_limit = None):
        
        """
        Indexes items by the words they contain. Returns a dataframe.
        """
        
        all_words = self.get_all_words()
        words = all_words.drop_duplicates().reset_index().drop('index', axis = 1)
        
        
        words['Items'] = None
        words['Item count'] = None
        words['Total frequency'] = None
        words['Mean frequency'] = None
        words['Breakdown'] = None
        
        if word_limit != None:
            words = words.loc[:word_limit]
        
        for i in words.index:
                entry = words.iloc[i, 0]
                found_series = all_words[all_words['word'] == entry]['found_in']
                found_in = set(found_series)
                found_in_count = len(found_series)
                found_in_freqs = found_series.value_counts().to_dict()
                words.at[i, 'Items'] = found_in
                words.at[i, 'Item count'] = len(found_in)
                words.at[i, 'Total frequency'] = found_in_count
                words.at[i, 'Mean frequency'] = found_in_count / self.count_items()
                words.at[i, 'Breakdown'] = found_in_freqs
        
        words['Word'] = words['word']
        words = words.drop('word', axis=1).reset_index().drop('index', axis=1)
        words = words[['Word', 'Items', 'Item count', 'Total frequency', 'Mean frequency', 'Breakdown']]
        
        return words.sort_values('Item count', ascending=False).drop_duplicates(['Word', 'Item count']).reset_index().drop('index',axis=1)
        
    
    
    def index_by_links(self):
        
        """
        Indexes items by their links. Returns a dataframe.
        """

        all_links = self.get_all_links()
        links = all_links.drop_duplicates().reset_index().drop(['index', 'Found in'], axis = 1)
        
        links['Items'] = None
        links['Item count'] = None
        links['Total frequency'] = None
        links['Mean frequency'] = None
        links['Breakdown'] = None

        for i in links.index:
                entry = links.iloc[i, 0]
                found_series = all_links[all_links['Link'] == entry]['Found in']
                found_in = set(found_series)
                found_in_count = len(found_series)
                found_in_freqs = found_series.value_counts().to_dict()
                links.at[i, 'Items'] = found_in
                links.at[i, 'Item count'] = len(found_in)
                links.at[i, 'Total frequency'] = found_in_count
                links.at[i, 'Mean frequency'] = found_in_count / self.count_items()
                links.at[i, 'Breakdown'] = found_in_freqs
        
        return links.sort_values('Item count', ascending=False).drop_duplicates(['Link', 'Item count', 'Total frequency']).reset_index().drop('index',axis=1)

    
    def index_by_refs(self):
        
        """
        Indexes items by their references. Returns a dataframe.
        """
        
        all_refs = self.get_all_refs()
        refs = all_refs.drop_duplicates().reset_index().drop(['index', 'Found in'], axis = 1)
        
        refs['Items'] = None
        refs['Item count'] = None
        refs['Total frequency'] = None
        refs['Mean frequency'] = None
        refs['Breakdown'] = None
    
        for i in refs.index:
                entry = refs.iloc[i, 0]
                found_series = all_refs[all_refs['Reference'] == entry]['Found in']
                found_in = set(found_series)
                found_in_count = len(found_series)
                found_in_freqs = found_series.value_counts().to_dict()
                refs.at[i, 'Items'] = found_in
                refs.at[i, 'Item count'] = len(found_in)
                refs.at[i, 'Total frequency'] = found_in_count
                refs.at[i, 'Mean frequency'] = found_in_count / self.count_items()
                refs.at[i, 'Breakdown'] = found_in_freqs
        
        return refs.sort_values('Item count', ascending=False).drop_duplicates(['Reference', 'Item count']).reset_index().drop('index',axis=1)

    def index_by_contents(self):
        
        """
        Indexes items by their contents. Returns a dataframe.
        """
        
        all_contents = self.get_all_contents()
        contents = all_contents.drop_duplicates().reset_index().drop(['index', 'Found in'], axis = 1)
        
        contents['Items'] = None
        contents['Item count'] = None
        contents['Total frequency'] = None
        contents['Mean frequency'] = None
        contents['Breakdown'] = None

        for i in contents.index:
                entry = contents.iloc[i, 0]
                found_series = all_contents[all_contents['Content'] == entry]['Found in']
                found_in = set(found_series)
                found_in_count = len(found_series)
                found_in_freqs = found_series.value_counts().to_dict()
                contents.at[i, 'Items'] = found_in
                contents.at[i, 'Item count'] = len(found_in)
                contents.at[i, 'Total frequency'] = found_in_count
                contents.at[i, 'Mean frequency'] = found_in_count / self.count_items()
                contents.at[i, 'Breakdown'] = found_in_freqs
        
        return contents.sort_values('Item count', ascending=False).drop_duplicates(['Content', 'Item count', 'Total frequency']).reset_index().drop('index',axis=1)
    
    

    # Methods for searching indexed items

    def search_items(self, query = 'request_input'):
        
        """
        Searches for an item ID. If found, returns that item's contents.
        """
        
        if query == 'request_input':
            query = input('Search query: ')
        
        if (type(query) == float) or (type(query) == int):
            query = str(query)
        
        if type(query) != str:
            raise TypeError('Search query must be a string')
        
        query = query.lower()
        
        items = pd.Series(self.contents(), dtype='str')
        search_result = items[items.str.lower().str.contains(query)]
        amount_found = len(search_result)
        
        if amount_found == 0:
            print('Item not found')
            return False 
        
        if amount_found == 1:
            
            try:
                item_id = search_result.values[0]
                print('\n' + 'Result: ' + item_id)
                return self.get_item(item_id)

            except: 
                print('Item not found')
                return False 
        
        else:
            print('\n' + 'Results: ')
            return search_result
    
    
    def search_info(self, query = 'request_input', search_in = 'all'):
        
        """
        Searches item set's information for a query string. If found, returns a dataframe of all items containing the string.
        """

        if query == 'request_input':
            query = input('Search query: ')
        
        if type(query) != str:
            raise TypeError('Search query must be a string')
        
        if type(search_in) != str:
            raise TypeError('Search term must be a string')

        if search_in.lower() == 'labels':
            labels = True
        else:
            labels = False
        
        if search_in.lower() == 'categories':
            categories = True
        else:
            categories = False
        
        if search_in.lower() == 'all':
            labels = True
            categories = True
        
        info_df = self.get_all_info().astype(str)
        
        if labels == True:
            label_res = info_df[info_df['Label'].str.contains(query)]
        else:
            label_res = pd.DataFrame(columns = info_df.columns)
        
        if categories == True:
            category_res = info_df[info_df['Category'].str.contains(query)]
        else:
            category_res = pd.DataFrame(columns = info_df.columns)
        
        return pd.concat([label_res, category_res])
    
     
    def search_metadata(self, query = 'request_input', search_in = 'all'):
        
        """
        Searches items' metadata for a query string. If found, returns a dataframe of all items containing the string.
        """

        if query == 'request_input':
            query = input('Search query: ')
        
        if type(query) != str:
            raise TypeError('Search query must be a string')
        
        if type(search_in) != str:
            raise TypeError('Search term must be a string')
        
        if search_in.lower() == 'entries':
            entries = True
        else:
            entries = False
        
        if search_in.lower() == 'categories':
            categories = True
        else:
            categories = False
        
        if search_in.lower() == 'all':
            entries = True
            categories = True
        
        metadata_df = self.get_all_metadata().astype(str)
        
        if entries == True:
            metadata_res = metadata_df[metadata_df['Metadata'].str.contains(query)]
        else:
            metadata_res = pd.DataFrame(columns = metadata_df.columns)
        
        if categories == True:
            category_res = metadata_df[metadata_df['Category'].str.contains(query)]
        else:
            category_res = pd.DataFrame(columns = metadata_df.columns)
        
        return pd.concat([metadata_res, category_res])

    
    def search_links(self, query = 'request_input'):
        
        """
        Searches items' links for a query string. If found, returns a dataframe of all items containing the string.
        """
        
        if query == 'request_input':
            query = input('Search query: ')
        
        if type(query) != str:
            raise TypeError('Search query must be a string')
        
        links_df = self.get_all_links()
        
        return links_df[links_df['Link'].str.contains(query)]
    
    def search_refs(self, query = 'request_input'):
        
        """
        Searches items' references for a query string. If found, returns a dataframe of all items containing the string.
        """
        
        if query == 'request_input':
            query = input('Search query: ')
        
        if type(query) != str:
            raise TypeError('Search query must be a string')
        
        refs_df = self.get_all_refs()
        
        return refs_df[refs_df['Reference'].str.contains(query)]
    
    def search_contents(self, query = 'request_input'):
        
        """
        Searches items' contents for a query string. If found, returns a dataframe of all items containing the string.
        """
        
        if query == 'request_input':
            query = input('Search query: ')
        
        if type(query) != str:
            raise TypeError('Search query must be a string')
        
        contents_df = self.get_all_contents()
        
        return contents_df[contents_df['Content'].str.contains(query)]
    
    def search_addresses(self, query = 'request_input'):
        
        """
        Searches items' address metadata for a query string. If found, returns a dataframe of all items containing the string.
        """
        
        if query == 'request_input':
            query = input('Search query: ')
        
        if type(query) != str:
            raise TypeError('Search query must be a string')
        
        addresses_df = self.get_all_addresses()
        result_df = addresses_df[addresses_df['Metadata'].str.contains(query)][['Metadata', 'Found in']]
        result_df['Address'] = result_df['Metadata']
        result_df = result_df.drop('Metadata', axis=1)[['Address', 'Found in']].reset_index().drop('index', axis=1)
        
        return result_df
    
    
    def search_data(self, search_query = 'request_input'):
        
        """
        Searches items' data entries for a query string. If found, returns a dataframe of all items containing the string.
        """
        
        if search_query == 'request_input':
            search_query = input('Search query: ')
        
        if type(search_query) != str:
            raise TypeError('Search query must be a string')
            
        search_query = search_query.lower()
        
        df = self.get_all_data().copy(deep=True)
        
        try:
            df['Parsed data'] = df['Parsed data'].apply(dict_to_str)
        except:
            pass
        
        datatypes_result = df[df['Datatype'].str.lower().str.contains(search_query)]
        formats_result = df[df['Format'].str.lower().str.contains(search_query)]
        rawdata_result = df[df['Raw data'].str.lower().str.contains(search_query)]
        parsed_result = df[df['Parsed data'].str.lower().str.contains(search_query)]
        
        result = pd.concat([datatypes_result, formats_result, rawdata_result, parsed_result])
        result = result.drop_duplicates().reset_index().drop('index', axis=1)
        
        return result
    
    def search_words(self, search_query = 'request_input'):
        
        """
        Searches items' words for a query string. If found, returns a dataframe of all items containing the string.
        """
        
        if search_query == 'request_input':
            search_query = input('Search query: ')
        
        if type(search_query) != str:
            raise TypeError('Search query must be a string')
            
        search_query = search_query.lower()
        
        df = self.get_all_words()
        df = df[df['word'].str.contains(search_query)]
        
        return df.drop_duplicates().reset_index().drop('index', axis=1).sort_values('word')
    
    

    def search(self, search_query = 'request_input'):
        
        """
        Searches items for a query string. If found, returns a dataframe of all items containing the string.
        """
        
        if search_query == 'request_input':
            search_query = input('Search query: ')
        
        if type(search_query) != str:
            raise TypeError('Search query must be a string')
            
        search_query = search_query.lower()
        
        metadata_res = self.search_metadata(query = search_query)
        metadata_res['Result'] = metadata_res['Metadata']
        metadata_res['Category']
        metadata_res = metadata_res.drop('Metadata', axis=1)
        metadata_res['Attribute'] = 'metadata'
        metadata_res['Found in'] = metadata_res['Found in'].astype(str)
        
        info_res = self.search_info(query = search_query)
        info_res['Result'] = info_res['Label']
        info_res = info_res.drop('Label', axis=1)
        info_res['Attribute'] = 'information'
        info_res['Found in'] = info_res['Found in'].astype(str)
        
        data_res = self.search_data(search_query = search_query)
        data_res['Result'] = 'Raw data: ' +   data_res['Raw data'] + ', Parsed data: ' + data_res['Parsed data']   
        data_res['Category'] = data_res['Datatype'] + ' (format: ' + data_res['Format'] + ')'
        data_res = data_res.drop(['Datatype', 'Format', 'Stored as', 'Size (bytes)', 'Raw data', 'Parsed data'], axis=1)
        data_res['Attribute'] = 'data'
        data_res['Found in'] = data_res['Found in'].astype(str)
        
        words_res = self.search_words(search_query = search_query)
        words_res['Result'] = words_res['word']
        words_res['Category'] = None
        words_res = words_res.drop('word', axis=1)
        words_res['Attribute'] = 'word'
        words_res['Found in'] = words_res['found_in'].astype(str)
        words_res = words_res.drop('found_in', axis=1)
        
        links_res = self.search_links(query = search_query)
        links_res['Result'] = links_res['Link']
        links_res['Category'] = None
        links_res = links_res.drop('Link', axis=1)
        links_res['Attribute'] = 'link'
        links_res['Found in'] = links_res['Found in'].astype(str)
        
        refs_res = self.search_refs(query = search_query)
        refs_res['Result'] = refs_res['Reference']
        refs_res['Category'] = None
        refs_res = refs_res.drop('Reference', axis=1)
        refs_res['Attribute'] = 'reference'
        refs_res['Found in'] = refs_res['Found in'].astype(str)
        
        contents_res = self.search_contents(query = search_query)
        contents_res['Result'] = contents_res['Content']
        contents_res['Category'] = None
        contents_res = contents_res.drop('Content', axis=1)
        contents_res['Attribute'] = 'content'
        contents_res['Found in'] = contents_res['Found in'].astype(str)
        
        result = pd.concat([metadata_res, data_res, words_res, info_res, links_res, refs_res, contents_res])
        result['Found in'] = result['Found in'].astype(str)
        result = result[['Result', 'Category', 'Attribute', 'Found in']]
        
        return result.reset_index().drop('index', axis=1)

    
    def return_all(self):
        
        """
        Returns a pandas.DataFrame containing all item contents from all items.
        """
        
        metadata_res = self.get_all_metadata()
        metadata_res['Result'] = metadata_res['Metadata']
        metadata_res = metadata_res.drop('Metadata', axis=1)
        metadata_res['Attribute'] = 'metadata'
        metadata_res['Found in'] = metadata_res['Found in'].astype(str)
        
        info_res = self.get_all_info()
        info_res['Result'] = info_res['Label']
        info_res = info_res.drop('Label', axis=1)
        info_res['Attribute'] = 'information'
        info_res['Found in'] = info_res['Found in'].astype(str)
        
        data_res = self.get_all_data()
        try:
            data_res['Parsed data'] = data_res['Parsed data'].apply(dict_to_str)
        except:
            pass
        data_res['Result'] = 'Raw data: ' +   data_res['Raw data'] + ', Parsed data: ' + data_res['Parsed data']   
        data_res['Category'] = data_res['Datatype'] + ' (format: ' + data_res['Format'] + ')'
        data_res = data_res.drop(['Datatype', 'Format', 'Stored as', 'Size (bytes)', 'Raw data', 'Parsed data'], axis=1)
        data_res['Attribute'] = 'data'
        data_res['Found in'] = data_res['Found in'].astype(str)
        
        words_res = self.get_all_words()
        words_res['Result'] = words_res['word']
        words_res['Category'] = None
        words_res = words_res.drop('word', axis=1)
        words_res['Attribute'] = 'word'
        words_res['Found in'] = words_res['found_in'].astype(str)
        words_res = words_res.drop('found_in', axis=1)
        
        links_res = self.get_all_links()
        links_res['Result'] = links_res['Link']
        links_res['Category'] = None
        links_res = links_res.drop('Link', axis=1)
        links_res['Attribute'] = 'link'
        links_res['Found in'] = links_res['Found in'].astype(str)
        
        refs_res = self.get_all_refs()
        refs_res['Result'] = refs_res['Reference']
        refs_res['Category'] = None
        refs_res = refs_res.drop('Reference', axis=1)
        refs_res['Attribute'] = 'reference'
        refs_res['Found in'] = refs_res['Found in'].astype(str)
        
        contents_res = self.get_all_contents()
        contents_res['Result'] = contents_res['Content']
        contents_res['Category'] = None
        contents_res = contents_res.drop('Content', axis=1)
        contents_res['Attribute'] = 'content'
        contents_res['Found in'] = contents_res['Found in'].astype(str)
        
        result = pd.concat([metadata_res, data_res, words_res, info_res, links_res, refs_res, contents_res])
        result['Found in'] = result['Found in'].astype(str)
        result = result[['Result', 'Category', 'Attribute', 'Found in']]
        
        return result
        
    
    def advanced_search(self, any_kwds = 'request_input', all_kwds = 'request_input', no_kwds = 'request_input', search_in = 'all'):
        
        """
        An advanced search function. Searches items using a series of keyword commands. If found, returns a dataframe of all items containing the string.
        
        Parameters
        ----------
        any_kwds : list
            results must contain any of these strings. Defaults to requesting user input.
        all_kwds : list
            results must contain all of these strings. Defaults to requesting user input.
        no_kwds : list
            results not must contain any of these strings. Defaults to requesting user input.
        search_in : list
            list of item attributes to search. 
        """
        
        if any_kwds == 'request_input':
            any_kwds = input('Containing any of the following (press RETURN to ignore): ')
            
        if any_kwds == '':
            any_kwds = None
        
        if type(any_kwds) == str:
            any_kwds = any_kwds.split(', ')
        
        
        if all_kwds == 'request_input':
            all_kwds = input('Containing all of the following (press RETURN to ignore): ')
            all_kwds = all_kwds.split(', ')
            
        if all_kwds == '':
            all_kwds = None
        
        if type(all_kwds) == str:
            all_kwds = all_kwds.split(', ')
        
        if (all_kwds != None) and (type(all_kwds) != list):
            return TypeError('"all_kwds" must be a list or string')

        
        if no_kwds == 'request_input':
            no_kwds = input('Containing none of the following (press RETURN to ignore): ')
            
        if no_kwds == '':
            no_kwds = None
        
        if type(no_kwds) == str:
            no_kwds = no_kwds.split(', ')

        if (no_kwds != None) and (type(no_kwds) != list):
            return TypeError('"no_kwds" must be a list or string')

        if type(any_kwds) == list:
            
            result_df = pd.DataFrame()

            for i in any_kwds:
                result_df = pd.concat([self.search(search_query = i), result_df])
        
        else:
            result_df = self.return_all()
            
        if all_kwds != None:
            for i in all_kwds:
                result_df = result_df[(result_df['Result'].str.contains(i) == True)]

        if no_kwds != None:
            for i in no_kwds:
                result_df = result_df[(result_df['Result'].str.contains(i) == False)]

        if search_in != 'all':

            if type(search_in) == str:
                search_in = [search_in]

            if type(search_in) != list:
                raise TypeError('"search_in" must be a list or string')

            out_df = pd.DataFrame
            for i in search_in:
                masked_df = result_df[(result_df['Attribute'] == i)]
                out_df = pd.concat([masked_df, out_df])

            result_df = out_df

        result_df = result_df.dropna().drop_duplicates().reset_index().drop('index', axis=1)

        if (all_kwds == None) or (all_kwds == ['']):
            all_kwds = []

        if (no_kwds == None) or (no_kwds == ['']):
            no_kwds = []

        search_term = 'Items including ANY OF ' + str(any_kwds) + ' AND ALL OF ' + str(all_kwds) + ' AND NONE OF' + str(no_kwds)

        print('\nSearch: ' + search_term )

        return result_df
    
    

    # Methods for filtering items in the item set based on their data
    
    def filter_by_distance(self, select_by = 'coordinates', close_to = 'request_input', within = 100, units = 'kilometers', ignore_nones = True) -> pd.DataFrame:
        
        """
        Selects items whose geolocation metadata falls within a distance of a given location. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        select_by : str
            category of geolocation metadata to use.
        close_to : str
            location or coordinates to measure from.
        within : int
            maximum distance from given location. 
        units : str
            units for distance.
        ignore_nones : bool
            whether to ignore items without geolocation metadata entries.
        """
        
        if close_to == 'request_input':
            close_to = input('Find items close to: ')

        output_df = pd.DataFrame(columns = ['Item ID', 'Item location', 'Item coordinates', f'Distance from {close_to}', 'Units'], dtype = object)

        if close_to in self.contents():
            select_by = 'items'
            ref_coordinates = self.get_item(close_to).coordinates_metadata()

            if ref_coordinates == None:
                return output_df

            if type(ref_coordinates) == str:
                ref_coordinates = ref_coordinates.split(',')

        if select_by == 'coordinates':
            if type(close_to) == str:
                ref_coordinates = close_to.split(',')

            if type(close_to) == list:
                ref_coordinates = close_to

            if (type(close_to) != str) and (type(close_to) != list):
                raise TypeError('Coordinates must be either a string or list')

        if select_by == 'location':

            if type(select_by) != str:
                raise TypeError('Location must be a string')

            ref_coordinates = get_location_coordinates(close_to)

        if (select_by != 'location') and (select_by != 'coordinates') and (select_by != 'items'):
            raise ValueError('"select_by" only accepts "coordinates" or "location"')

        if len(ref_coordinates) < 2:
            return output_df

        ref_latitude = str(ref_coordinates[0]).strip()
        ref_longitude = str(ref_coordinates[1]).strip()



        index = 0
        for item in self.contents():

            if item == close_to:
                continue

            item_coordinates = self.get_item(item).coordinates_metadata()
            item_location = self.get_item(item).location_metadata()

            if item_coordinates == None:
                distance = None
                continue


            if type(item_coordinates) == str:
                item_coordinates = item_coordinates.split(',')
                item_latitude = item_coordinates[0]
                item_longitude = item_coordinates[1]

            item_latitude = str(item_latitude).strip()
            item_longitude = str(item_longitude).strip()

            distance = coordinates_distance(first_coordinates = ref_coordinates, second_coordinates = item_coordinates, units = units)
            units = distance[1]
            distance = distance[0]


            output_df.loc[index, 'Item ID'] = item
            output_df.loc[index, 'Item location'] = item_location
            output_df.at[index, 'Item coordinates'] = item_coordinates
            output_df.loc[index, f'Distance from {close_to}'] = distance
            output_df.loc[index, 'Units'] = units
            index += 1


        if ignore_nones == True:
            output_df = output_df.dropna(subset = f'Distance from {close_to}')

        output_df = output_df[output_df[f'Distance from {close_to}'] <= within]

        return output_df.sort_values(f'Distance from {close_to}').reset_index().drop('index', axis=1)

    
    def triangulate_by_distance(self, locations, select_by = 'coordinates', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Selects items whose geolocation metadata falls within a distance of multiple given locations. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        locations : list
            a list of locations or coordinates to triangulate from.
        select_by : str
            category of geolocation metadata to use.
        within : int
            maximum distance from given location. 
        units : str
            units for distance.
        ignore_nones : bool
            whether to ignore items without geolocation metadata entries.
        """
        
        if type(locations) != list:
            raise TypeError('Locations must be inputted at a list')

        output_df = pd.DataFrame(columns = ['Item location', 'Item coordinates'])

        location_dfs = []
        index_sets = []
        for i in locations:
            output_df[f'Distance from {i}'] = None
            i = self.filter_by_distance(select_by = select_by, close_to = i, within = within, units = units, ignore_nones = ignore_nones)
            i = i.set_index('Item ID')
            index = set(i.index)
            index_sets.append(index)

            location_dfs.append(i)

        ids = list(index_sets[0].intersection(*index_sets[1:]))

        if len(ids) == 0:
            return None

        for item in ids:
            output_df.loc[item, 'Item location'] = self.get_item(item).location_metadata()
            output_df.loc[item, 'Item coordinates'] = self.get_item(item).coordinates_metadata()

            distances = []
            for i in location_dfs:
                col = i.columns[2]
                output_df.loc[item, col] = i.loc[item, col]
                distances.append(i.loc[item, col])

            if len(distances) > 0:
                    output_df.loc[item, 'Mean distance'] = sum(distances) / len(distances)
            else:
                    output_df.loc[item, 'Mean distance'] = None

        output_df['Units'] = units

        return output_df.sort_values('Mean distance')

    
    def filter_by_dates(self, select_by = 'Created at', from_date = 'request_input', to_date = 'request_input', ignore_nones = True):
        
        """
        Selects items whose time metadata falls within two datetimes. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        select_by : str
            category of time metadata to use. Defaults to 'Created at'
        from_date : str
            date or time to measure from. Defaults to requesting from user input.
        to_date : str
            date or time to measure to. Defaults to requesting from user input.
        ignore_nones : bool
            whether to ignore items without geolocation metadata entries. Defaults to True.
        """
        
        if from_date == 'request_input':
            from_date = input('From: ')

        if to_date == 'request_input':
            to_date = input('To: ')

        from_date = str_to_datetime(from_date)
        to_date = str_to_datetime(to_date)

        output_df = pd.DataFrame(self.get_all_time_metadata()[select_by])

        if ignore_nones == True:
            output_df = output_df.dropna()

        output_df = output_df[(output_df[select_by] >= from_date) & (output_df[select_by] <= to_date)]

        return output_df.sort_values(select_by).reset_index()
    
    

    # Methods for looking up items' internet metadata
    
    def lookup_item_domain(self, item_id = 'request_input'):
        
        """
        Runs a WhoIs lookup on an item's domain metadata.
        """
        
        try:
            return self.get_item(item_id).lookup_domain()
        except:
            return None
    
    
    def lookup_all_item_domains(self):
        
        """
        Runs WhoIs lookups on all items' domain metadata.
        """
        
        output_df = pd.DataFrame(dtype = object)
        for item_id in self.contents():
            try:
                try:
                    whois_res = self.lookup_item_domain(item_id)
                    whois = whois_res.all_results.T.reset_index().drop('index', axis=1)
                    try:
                        whois = whois.set_index('domain')
                    except:
                        try:
                            whois = whois.set_index('domain_name')
                        except:
                            pass
                            
                    whois.columns.name = None
                    whois['item_id'] = item_id
                    
                except:
                    whois = pd.DataFrame(columns = ['item_id', 'domain'], dtype = object)
                    whois.loc[0] = [item_id, None]
                    whois['item_id'] = item_id
                    whois = whois.set_index('domain')
                
                whois = whois.reset_index()
                whois = whois.set_index('item_id')
                output_df = pd.concat([output_df, whois])
        
            except:
                continue
        
        output_df = output_df.replace(np.nan, None)
        
        return output_df
    
    
    def lookup_item_ip_metadata(self, item_id = 'request_input'):
        
        """
        Runs a WhoIs lookup on an item's IP address metadata.
        """
        
        try:
            return self.get_item(item_id).lookup_ip()
        except:
            return None

    def lookup_all_item_ip_metadata(self):
        
        """
        Runs WhoIs lookups on all items' IP address metadata.
        """
        
        output_df = pd.DataFrame(dtype = object)
        for item_id in self.contents():
            try:
                try:
                    whois_res = self.lookup_item_ip_metadata(item_id)
                    whois = whois_res.all_results.T.reset_index().drop('index', axis=1).set_index('ip_address')
                    whois.columns.name = None
                    whois['item_id'] = item_id
                    
                except:
                    whois = pd.DataFrame(columns = ['item_id', 'ip_address'], dtype = object)
                    whois.loc[0] = [item_id, None]
                    whois['item_id'] = item_id
                    whois = whois.set_index('ip_address')
                
                whois = whois.reset_index()
                whois = whois.set_index('item_id')
                output_df = pd.concat([output_df, whois])
        
            except:
                continue
        
        output_df = output_df.replace(np.nan, None)
        
        return output_df
    
    def lookup_all_items_whois(self, append_to_items = False):
        
        """
        Runs WhoIs lookups on all items' internet metadata.
        """
        
        items = self.contents()
        
        for item_id in items:
            self.get_item(item_id).lookup_whois(append_to_item = append_to_items)
        
        

    def open_all_links(self):
        
        """
        Opens all items' links in the default web browser.
        """
        
        links = self.get_links_set()
        
        for link in links:
            regex_check_then_open_url(link)
            
    
    def filter_all_links(self, 
                        contains_any_kwds = None,
                        contains_all_kwds = None,
                        not_containing_any_kwds = None,
                        not_containing_all_kwds = None):
        
        """
        Filters items' links based on given criteria. Returns a list.
        
        Parameters
        ----------
        contains_any_kwds : list
            results must contain any of these strings. Defaults to None.
        contains_all_kwds : list
            results must contain all of these strings. Defaults to None.
        not_containing_any_kwds : list
            results not must contain any of these strings. Defaults to None.
        not_containing_all_kwds : list
            results not must contain all of these strings. Defaults to None.
        """
        
        selected_links = []
        
        item_ids = self.ids()
        for item_id in item_ids:
            links = self.get_item(item_id).filter_links(contains_any_kwds = contains_any_kwds, 
                                        contains_all_kwds = contains_all_kwds,
                                        not_containing_any_kwds = not_containing_any_kwds,
                                        not_containing_all_kwds = not_containing_all_kwds)
            
            selected_links = selected_links + links
        
        selected_links = list(set(selected_links))
        
        return selected_links
    
    
    def lookup_filtered_links(self, contains_any_kwds = None, contains_all_kwds = None, not_containing_any_kwds = None, not_containing_all_kwds = None):
        
        """
        Selects and opens items' links in the default web browser based on given criteria.

        Parameters
        ----------
        contains_any_kwds : list
            results must contain any of these strings. Defaults to None.
        contains_all_kwds : list
            results must contain all of these strings. Defaults to None.
        not_containing_any_kwds : list
            results not must contain any of these strings. Defaults to None.
        not_containing_all_kwds : list
            results not must contain all of these strings. Defaults to None.
        """
        
        filtered_links = self.filter_all_links(contains_any_kwds = contains_any_kwds, 
                                                contains_all_kwds = contains_all_kwds,
                                                not_containing_any_kwds = not_containing_any_kwds,
                                                not_containing_all_kwds = not_containing_all_kwds)
        
        for link in filtered_links:
            regex_check_then_open_url(link)
        
        
    # Methods for creating item from PDF imports
    
    def item_from_pdf(self, item_id = 'request_input', file_path = None):
        
        """
        Creates a CaseItem object from a PDF file.
        
        Parameters
        ----------
        item_id : str
            item ID for new item. Defaults to requesting from user input.
        file_path : str
            directory path for PDF file.
        """
        
        if item_id == 'request_input':
            item_id = input('New item ID: ')
        
        parsed_pdf = read_pdf(file_path = file_path)
        item = parsed_pdf_to_item(parsed_pdf = parsed_pdf)
        
        self.add_blank_item(item_id)
        self.get_item(item_id).properties = item.properties
        self.get_item(item_id).data = item.data
        self.get_item(item_id).metadata = item.metadata
        self.get_item(item_id).links = item.links
        
        return self.get_item(item_id)
    
    def item_from_pdf_url(self, item_id = 'request_input', url = None):
        
        """
        Creates a CaseItem object from a PDF hosted at a URL.
        
        Parameters
        ----------
        item_id : str
            item ID for new item. Defaults to requesting from user input.
        url : str
            URL for PDF file.
        """
        
        if item_id == 'request_input':
            item_id = input('New item ID: ')
        
        parsed_pdf = read_pdf_url(url = url)
        item = parsed_pdf_to_item(parsed_pdf = parsed_pdf)
        
        self.add_blank_item(item_id)
        self.get_item(item_id).properties = item.properties
        self.get_item(item_id).data = item.data
        self.get_item(item_id).metadata = item.metadata
        self.get_item(item_id).links = item.links
        
        return self.get_item(item_id)
    

    # Methods for scraping and crawling from item data
    
    def scrape_item_urls(self, append_to_items = True):
        
        """
        Scrapes data from all items' URLs if available. Appends to items if selected.
        
        WARNING: this function is very slow due to the speed of the packages it relies on.

        Parameters
        ----------
        append_to_items : bool
            whether to append scraper results to items
        """
        
        item_ids = self.ids()
        for item_id in item_ids:
            self.get_item(item_id).fetch_site_contents(append_to_item = append_to_items)
        
        self.update_properties()
    

    def crawl_web_from_items(self,
                        crawl_from = 'URL',
                        visit_limit = 5, 
                        excluded_url_terms = 'default',
                        required_keywords = None, 
                        excluded_keywords = None, 
                        case_sensitive = False,
                        ignore_urls = None, 
                        ignore_domains = 'default',
                        be_polite = True,                            
                        full = True,
                        output_as = 'dataframe'):
        
        """
        Runs web crawl from items' URL metadata.
        
        Parameters
        ---------- 
        crawl_from : str
            metadata category to retrieve URL data from. Defaults to 'URL'.
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
        output_as : str
            the format to output results in. Defaults to a pandas.DataFrame.

        Returns
        -------
        result : object
            an object containing the results of a crawl.
        """
        
        if crawl_from == 'request_input':
            crawl_from = input('Metadata entry to crawl from: ')
        
        seed_urls = []
        ids = self.ids()
        for item_id in ids:
            urls = list(self.get_item(item_id).get_metadata(crawl_from)['Metadata'].values)
            seed_urls = seed_urls + urls
        seed_urls = list(set(seed_urls))
        
        output = crawl_web(
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
                            output_as = output_as)
        
        return output
    
    
    def crawl_all_web_links(self,
                        visit_limit = 5, 
                        excluded_url_terms = 'default',
                        required_keywords = None, 
                        excluded_keywords = None, 
                        case_sensitive = False,
                        ignore_urls = None, 
                        ignore_domains = 'default',
                        be_polite = True,
                        full = True,
                        output_as = 'dataframe'):
        
        """
        Runs web crawl from items' links.
        
        Parameters
        ---------- 
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
        output_as : str
            the format to output results in. Defaults to a pandas.DataFrame.

        Returns
        -------
        result : object
            an object containing the results of a crawl.
        """
        
        seed_urls = []
        ids = self.ids()
        for item_id in ids:
            urls = self.get_item(item_id).links
            
            if type(urls) == str:
                urls = urls.strip().replace('[', '').replace(']', '').replace('"', '').replace("'", "")
                urls = urls.split(',')
            
            seed_urls = seed_urls + urls
            
        seed_urls = list(set(seed_urls))
        
        output = crawl_web(
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
                            output_as = output_as)
        
        return output
    
    

    # Methods for exporting items to external files
    
    
    
    def export_txt(self, new_file = True, file_name = 'request_input', file_address = 'request_input'):
        
        """
        Exports item set to a .txt file.
        
        Parameters
        ----------
        new_file : bool
            whether to create a new file. Defaults to True.
        file_name : str
            name for file. Defaults to requesting from user input.
        file_address : str
            directory address to save to. Defaults to requesting from user input.
        """
        
        if new_file == True:
            
            if file_name == 'request_input':
                file_name = input('File name: ')
            
            if file_address == 'request_input':
                file_address = input('File address: ')
                file_address = file_address + '/' + file_name
            
        if new_file == False:
            
            if file_address == 'request_input':
                file_address = input('File path: ')
        
        if '.caseitems' != file_address[-11:]:
            file_address = file_address + '.case_items'

        with open(file_address, 'wb') as f:
            pickle.dump(self, f) 
    
    
    def export_excel_folder(self, folder_address = 'request_input', folder_name = 'request_input'):
            
            """
            Exports item set to a folder of Excel (.xlsx) files.

            Parameters
            ----------
            folder_address : str
                directory address to save to. Defaults to requesting from user input.
            folder_name : str
                name for new folder.
            """
            
            if folder_address == 'request_input':
                folder_address = input('Folder address: ')

            if folder_name == 'request_input':
                folder_name = input('Folder name: ')

            path = os.path.join(folder_address, folder_name) 

            os.mkdir(path) 
            
            for item_id in self.contents():
                file_name = item_id
                file_path = path + '/' + file_name
                
                try:
                    self.get_item(item_id).export_excel(new_file = True, file_name = file_name, file_address = file_path)
                except:
                    continue
        
    def export_csv_folders(self, folder_address = 'request_input', folder_name = 'request_input'):
            
            """
            Exports item set's dataframes to a folder of CSVs.

            Parameters
            ----------
            folder_address : str
                directory address to save to. Defaults to requesting from user input.
            folder_name : str
                name for new folder.
            """
            
            if folder_address == 'request_input':
                folder_address = input('Folder address: ')

            if folder_name == 'request_input':
                folder_name = input('Folder name: ')

            path = os.path.join(folder_address, folder_name) 

            os.mkdir(path) 
            
            for item_id in self.contents():
                
                try:
                    self.get_item(item_id).export_csv_folder(folder_address = path, folder_name = item_id)
                except:
                    continue
        
        
    def save_as(self, file_name = 'request_input', file_address = 'request_input', file_type = 'request_input'):
        
        """
        Exports item set as a type selected by user.
        
        Parameters
        ----------
        file_name : str
            name for file. Defaults to requesting from user input.
        file_address : str
            directory address to save to. Defaults to requesting from user input.
        file_type : str
            type of files to save to. Defaults to requesting from user input.
        """
        
        if file_type == 'request_input':
            file_type = input('File type: ')
        
        file_type = file_type.strip().strip('.').strip().lower()
        
        
        if (file_type.lower() == None) or (file_type.lower() == '') or (file_type.lower() == 'case') or (file_type.lower() == 'text') or (file_type.lower() == 'txt') or (file_type.lower() == 'pickle'):
            
            self.export_txt(new_file = True, file_name = file_name, file_address = file_address)
        
        
        if (file_type.lower() == 'excel') or (file_type.lower() == 'xlsx'):
            
            self.export_excel(new_file = True, file_name = file_name, file_address = file_address)
        
        
        if (file_type.lower() == 'csv') or (file_type.lower() == 'csvs'):

            self.export_csv_folder(folder_address = file_address, folder_name = file_name)
            

## Functions to create/edit caseitem objects and their attributes

def url_to_item_id(url):
    
    """
    Converts a URL a format whic is valid to use as an item ID. Returns a string.
    """
    
    item_id = url_to_valid_attr_name(url)
        
    if len(item_id) > 30:
        item_id = item_id[:30] + '___'
    
    return item_id


def new_blank_item(name = 'request_input') -> CaseItem:
    
    """
    Creates a new, blank CaseItem. 
    
    Parameters
    ----------
    name : str
        item ID for new CaseItem. Defaults to requesting from user input.
    """
    
    if name == 'request_input':
        name = input('Item name: ')
    
    globals()[name] = CaseItem(item_id = name)
    return globals()[name]            