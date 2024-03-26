from ..core.globaltools import get_var_name_str
from ..core.basics import Iterator
from ..core.cleaners import join_df_col_lists_by_semicolon, empty_to_none, list_to_datetimes, nat_list_to_nones_list, series_to_datetimes, series_none_list_to_empty_lists, text_splitter, correct_series_of_lists
from ..visualisation.visualise import plot_timeline, plot_date_range_timeline
from ..internet.crawlers import crawl_web, crawler
from ..socmed.sherlock_interpreter import search_username
from ..networks.network_functions import generate_urls_network
from ..exporters.general_exporters import obj_to_folder

from .defaults_manager import DEFAULT_SET, DEFAULT_CASE_NAME, set_default_case, get_default_case_name, get_default_case, is_default_case, check_default_case, remove_default_case, update_default_case
from .backups_manager import Backups, get_backups, BACKUPS
from .obj_properties import Properties, CaseObjectProperties
from .obj_superclasses import CaseObject, CaseObjectSet
from .relationships import CaseRelation, CaseRelationSet, SourceFileOf
from .files import CaseFile, CaseFileSet, stat_result
from .casespecial import CaseSpecial
from .items import CaseItem, CaseItemSet, pdf_to_item, parsed_pdf_to_item, pdf_url_to_item, url_to_item_id, new_blank_item
from .entities import CaseEntity, CaseEntitySet
from .events import CaseEvent, CaseEventSet
from .casedata import CaseKeywords, CaseData
from .networks import CaseNetwork, CaseNetworkSet
from .indexes import CaseIndexes
from .analytics import CaseAnalytics

import numpy as np 
import pandas as pd

from typing import List, Dict, Tuple
import os
import sys
import copy
import json
import pickle
from datetime import datetime, timedelta
import itertools
import math
from pathlib import Path

import numpy as np
import pandas as pd
import igraph as ig
from igraph import Graph
from Levenshtein import distance as lev

class CaseProperties(Properties):
    
    """
    This is a set of values representing global properties of a Case object.
    
    Parameters
    ----------
    case_name : str
        name for Case. This is intended to be the same string as the Case's variable name.
    case_path : str
        object path for Case.
    project : str
        name of parent project (if Case is part of one; None if not).
    file_location : str
        location where Case files are saved.
    file_type : str
        file type for Case files.
    size : int
        size of object in memory.
    parsed : bool
        whether raw data has been parsed.
    keywords_generated : bool
        whether keywords have been generated from parsed data.
    indexed : bool
        whether Case items, entities, and events have been indexed by their contents.
    coincidences_identified : bool
        whether patterns fo coinciding data have been analysed.
    networks_generated : bool
        whether core networks have been generated from Case items.
    analytics_generated : bool
        whether Case analytics have been generated.
    
    Attributes
    ----------
    case_name : str
        name for Case. This is intended to be the same string as the Case's variable name.
    obj_path : str
        object path for Case.
    project : str
        name of parent project (if Case is part of one; None if not).
    file_location : str
        location where Case files are saved.
    file_type : str
        file type for Case files.
    size : int
        size of object in memory.
    parsed : bool
        whether raw data has been parsed.
    keywords_generated : bool
        whether keywords have been generated from parsed data.
    indexed : bool
        whether Case items, entities, and events have been indexed by their contents.
    coincidences_identified : bool
        whether patterns fo coinciding data have been analysed.
    networks_generated : bool
        whether core networks have been generated from Case items.
    analytics_generated : bool
        whether Case analytics have been generated.
    """
        
    def __init__(self, 
                    case_name = None, 
                    case_path = None,
                    project = None,
                    file_location = None, 
                    file_type = None, 
                    size = None,
                    parsed = False,
                    keywords_generated = False,
                    indexed = False,
                    coincidences_identified = False,
                    networks_generated = False,
                    analytics_generated = False):
        
        """
        Initialises a CaseProperties instance.
        
        Parameters
        ----------
        case_name : str
            name for Case. This is intended to be the same string as the Case's variable name.
        case_path : str
            object path for Case.
        project : str
            name of parent project (if Case is part of one; None if not).
        file_location : str
            location where Case files are saved.
        file_type : str
            file type for Case files.
        size : int
            size of object in memory.
        parsed : bool
            whether raw data has been parsed.
        keywords_generated : bool
            whether keywords have been generated from parsed data.
        indexed : bool
            whether Case items, entities, and events have been indexed by their contents.
        coincidences_identified : bool
            whether patterns fo coinciding data have been analysed.
        networks_generated : bool
            whether core networks have been generated from Case items.
        analytics_generated : bool
            whether Case analytics have been generated.
        """
        
        super().__init__(obj_name = case_name, parent_obj_path = case_path)
        
        if case_path == None:
            if project == None:
                case_path = case_name
            else:
                case_path = project + '.' + case_name
        
        self.case_name = case_name
        self.obj_path = case_path
        self.project = project
        self.last_backup = None
        self.size = size
        self.file_location = file_location
        self.file_type = file_type
        self.parsed = parsed
        self.keywords_generated = keywords_generated
        self.indexed = indexed
        self.coincidences_identified = coincidences_identified
        self.networks_generated = networks_generated
        self.analytics_generated = analytics_generated
        
        del self.obj_size
        del self.obj_name
        
           
    
    
    def __repr__(self):
        
        """
        Defines how CaseProperties objects are represented in string form.
        """
        
        self_dict = self.to_dict()
        output = '\n'
        for key in self_dict.keys():
            prop = self_dict[key]
            output = output + key + ': ' + str(prop) + '\n'
        
        return output
    

class Case:
    
    """
    This is a Case object. It stores data, metadata, and other information related to investigative cases.

    Parameters
    ----------
    case_name : str
        name for Case. This is intended to be the same string as the Case's variable name.
    case_path : str
        object path for Case.
    project : str
        name of parent project (if Case is part of one; None if not).
    file_location : str
        location where Case files are saved.
    file_type : str
        file type for Case file(s).
    size : int
        size of object in memory.
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
    
    Attributes
    ----------
    properties : CaseProperties
        metadata for Case object.
    items : CaseItemSet
        items of data and evidence associated with the case.
    entities : CaseEntitySet
        entities associated with the case.
    events : CaseEventSet
        events associated with the case.
    indexes : CaseIndexes
        indexes of items, entities, events, and other data.
    networks : CaseNetworkSet
        networks derived from items, entities, and events.
    analytics : CaseAnalytics
        analytics derived from items, entities, and events.
    dataframes : CaseData
        collated data for items associated with the case.
    description : str
        a user-generated description of the case.
    notes : list
        user-generated notes assigned to the case.
    """
    
    def __init__(self, 
                    case_name = None,
                    case_path = None,
                    project = None,
                    file_location = None, 
                    file_type = None, 
                    size = None, 
                    make_default = True, 
                    parse = False, 
                    keywords = False, 
                    coincidences = False, 
                    indexes = False, 
                    networks = False, 
                    analytics = False
                ):
        
        """
        Initialises a Case instance.
        
        Parameters
        ----------
        case_name : str
            name for Case. This is intended to be the same string as the Case's variable name.
        case_path : str
            object path for Case.
        project : str
            name of parent project (if Case is part of one; None if not).
        file_location : str
            location where Case files are saved.
        file_type : str
            file type for Case file(s).
        size : int
            size of object in memory.
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
        """
        
        self.properties = CaseProperties(case_name = case_name,
                                            case_path = case_path,
                                            project = project,
                                            file_location = file_location, 
                                            file_type = file_type, 
                                            size = size,
                                            parsed = parse,
                                            keywords_generated = keywords,
                                            coincidences_identified = coincidences,
                                            indexed = indexes,
                                            networks_generated = networks,
                                            analytics_generated = analytics)
        
        self.dataframes = CaseData(obj_name = 'dataframes', parent_obj_path = self.properties.obj_path)
        self.items = CaseItemSet(obj_name = 'items', parent_obj_path = self.properties.obj_path)
        self.entities = CaseEntitySet(obj_name = 'entities', parent_obj_path = self.properties.obj_path)
        self.events = CaseEventSet(obj_name = 'events', parent_obj_path = self.properties.obj_path)
        self.indexes = CaseIndexes(obj_name = 'indexes', parent_obj_path = self.properties.obj_path)
        self.networks = CaseNetworkSet(obj_name = 'networks', parent_obj_path = self.properties.obj_path)
        self.analytics = CaseAnalytics(obj_name = 'analytics', parent_obj_path = self.properties.obj_path)
        self.files = CaseFileSet(obj_name = 'files', parent_obj_path = self.properties.obj_path)
        self.description = str()
        self.notes = pd.DataFrame(columns = ['Note', 'Created at'])
        
        if (case_name == None) or (case_name == 'self'):
            var_str = self.varstr()
            self.properties.case_name = var_str
        
        if make_default == True:
            self.make_default()
        
        if parse == True:
            self.parse_rawdata()
        
        if keywords == True:
            self.generate_keywords()
        
        if coincidences == True:
            self.identify_coincidences()
        
        if indexes == True:
            self.generate_indexes()
        
        if networks == True:
            self.generate_all_networks(items = True, 
                        keywords = keywords,
                        info = True,
                        metadata = True,
                        items_networks = True,
                        directed_networks = True, 
                        coincidence_networks = coincidences,
                        partitioned_networks = True)
        
        self.update_dataframes_from_all_items()
        self.properties.obj_id = id(self)
        self.properties.size = str(self.__sizeof__()) + ' bytes'
        self.properties.update_last_changed()
         # self.backup()
        

    # Methods for editing and retrieving case properties
    
    def update_properties(self):
        
        """
        Updates Case properties.
        
        Updates
        -------
            * obj_id
            * size
            * contents
            * last_changed
        """
        
        self.properties.contents = self.contents()
        self.properties.obj_id = id(self)
        self.properties.size = str(self.__sizeof__()) + ' bytes'
        self.properties.update_last_changed()
    
    def __repr__(self):
        
        """
        Defines how Case objects are represented in string form.
        """
        return f'\nProperties:\n{self.properties}\n\nDescription:\n{self.description}\n\nContents:\n{self.contents()}\n'
    
    def __iter__(self):
        
        """
        Function to make Case objects iterable.
        """
        
        return Iterator(self)
    
    def contents(self):
        
        """
        Returns the Case's attributes as a list. Excludes Case properties attribute.
        """
        
        return [i for i in self.__dict__.keys() if (i != 'properties')]
    
    def to_list(self):
        
        """
        Returns the Case's contents as a list. Excludes object properties attribute.
        """
        
        return [i for i in self if type(i) != CaseProperties]
    
    def to_dict(self):
        
        """
        Returns the Case's contents as a dictionary. Excludes object properties attribute.
        """
        
        output_dict = {}
        for index in self.__dict__.keys():
            if index != 'properties':
                output_dict[index] = self.__dict__[index]
        
        return output_dict
    
    
    def __getitem__(self, index):
        
        """
        Returns an attribute in the Case using an index or list of indexes.
        
        Parameters
        ----------
        index : str
            an attribute name.
        
        Returns
        -------
        result : CaseAttr
            a Case attribute.
        """
        
        if index in self.contents():
            return self.__dict__[index]
        
        if index in self.items.contents():
            return self.items.__dict__[index]
        
        if index in self.entities.contents():
            return self.entities.__dict__[index]
        
        if index in self.events.contents():
            return self.events.__dict__[index]
        
        if index in self.networks.contents():
            return self.networks.__dict__[index]
        
        if index in self.dataframes.contents():
            return self.dataframes.__dict__[index]
        
        if index in self.dataframes.keywords.contents():
            return self.dataframes.keywords.__dict__[index]
        
        if index in self.indexes.contents():
            return self.indexes.__dict__[index]
        
        if index in self.analytics.contents():
            return self.analytics.__dict__[index]
        
        else:
            raise KeyError(f'"{index}" not found in case')
    
    
    def copy(self):
        
        """
        Returns a copy of the Case object.
        """
        
        return copy.deepcopy(self)
    
    def get_project(self):
        
        """
        If the Case is assigned to a Project, returns that Project.
        """
        
        project = self.properties.project
        
        if (project != None) and (project != '') and (type(project) == str):
            return eval(project)
        else:
            return None
    
    def get_name_str(self):
        
        """
        Returns the Case's variable name as a string. 
        
        Notes
        -----
        Implementation:
            * Searches global environment dictionary for objects sharing case's name. Returns key if found.
            * If none found, searches local environment dictionary for objects sharing case's name. Returns key if found.
        """
        
        for name in globals():
            if id(globals()[name]) == id(self):
                return name
        
        for name in locals():
            if id(locals()[name]) == id(self):
                return name
    
    def varstr(self):
        
        """
        Returns the Case's name as a string. Defaults to using its variable name; falls back to using its name property.
        
        Notes
        -----
        Implementation:
            * Searches global environment dictionary for objects matching Case. Returns key if found.
            * If none found, searches local environment dictionary for objects matching Case. Returns key if found.
            * If none found, returns Case's name property.
            * If name property is None, 'none', or 'self', returns an empty string.
        """
        
        try:
            string = self.get_name_str()
        except:
            string = None
        
        if (string == None) or (string == 'self'):
            
            try:
                string = self.properties.project_name
            except:
                string = ''
                
        if (string == None) or (string == 'self'):
            string = ''
            
        return string
    
    def make_default(self):
        
        """
        Sets the Case as the default case in the environment.

        Setting a default case means the selected case will be called whenever a function or method calls for 'default_case'. 
        This is the default behaviour for several functions if no case is inputted.
        """
        
        set_default_case(self)
    
    
    def is_default(self):
        
        """
        Checks if Case is set as the default case.
        """
        
        try:
            res = self == get_default_case()
            return res
        except:
            return False
    
    
    def remove_default(self):
        
        """
        Deselects Case from being the default case.
        """
        
        if self.is_default() == True:

            remove_default_case()
            
    
    

    # Methods for creating, updating, and restoring from case backups
    
    def backup(self):
        
        """
        Creates backup of the Case.
        
        Notes
        -----
        Works by checking if Case has been backed up previously.
            * If yes: overwrites latest case backup with new backup.
            * If no: creates new backup in new directory location.
        """
        
        if 'BACKUPS' not in globals().keys():
            globals()['BACKUPS'] = Backups()
        
        global BACKUPS
        BACKUPS.save_backup(case = self)
        
        self.properties.last_backup = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    
    def create_new_backup(self):
        
        """
        Creates a backup of the Case.
        """
        
        if 'BACKUPS' not in globals().keys():
            globals()['BACKUPS'] = Backups()
        
        global BACKUPS
        BACKUPS.new_backup(case = self)
        self.properties.last_backup = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    
    def is_backed_up(self):
        
        """
        Checks if the Case object has been backed up.
        """
        
        case_name = self.get_name_str()
        
        if 'BACKUPS' not in globals().keys():
            globals()['BACKUPS'] = Backups()
        
        global BACKUPS
        return case_name in backups.registry['case'].values

    
    def last_backup(self):
        
        """
        Returns the Case's most recent backup.
        """
        
        case_name = self.get_name_str()
        
        if 'BACKUPS' not in globals().keys():
            globals()['BACKUPS'] = Backups()
        
        global BACKUPS
        return BACKUPS.last(case = self)
    
    
    def all_backups(self):
        
        """
        Returns a dataframe of the Case's backups.
        """
        
        case_name = self.get_name_str()
        
        if 'BACKUPS' not in globals().keys():
            globals()['BACKUPS'] = Backups()
        
        global BACKUPS
        return BACKUPS.get(case = self)

    
    def restore_from_backup(self, backup = 'last'):
        
        """
        Overwrites Case from a backup. Defaults to using the most recent backup.
        """
        
        if 'BACKUPS' not in globals().keys():
            globals()['BACKUPS'] = Backups()
        
        if backup == 'last':
            self = self.last_backup()[1]
            self.update_properties()
        
        else:
            global BACKUPS
            self = BACKUPS.directory[backup]
            self.update_properties()


    def overwrite_backup(self, backup = 'last'):
        
        """
        Overwrites a selected case backup with new backup.
        
        Parameters
        ----------
        backup: str or int
            which backup or backups to overwrite. Defaults to the most recent backup.
        """
        
        if 'BACKUPS' not in globals().keys():
            globals()['BACKUPS'] = Backups()
        
        if self.is_backed_up() == False:
            self.update_properties()
             # self.backup()
            return

        else:

            if backup == 'last':
                backup = self.last_backup()[0]['location']
                
            global BACKUPS
            BACKUPS.overwrite_backup(case = self, backup = backup)
            self.last_backup = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
        self.update_properties()
        

    # Methods for adding objects and data to case
    
    def add_blank_item(self, item_id = 'input'):
        
        """
        Adds a blank item to the Case's item set.
        
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
            item_code = self.items.count_items() + 1
            item_id = 'item_' + str(item_code)
        
        if item_id == 'input':
            item_id = input('New item ID: ')
        
        self.items.add_blank_item(item_id = item_id)
        self.update_dataframes_from_item(item_id)
        self.update_properties()
         # self.backup()
    
    def add_item(self, item = None, item_id = None):
        
        """
        Adds an item to the Case's item set.
        
        Parameters
        ----------
        item : CaseItem
            The item to be added. Defaults to None; this adds a blank item.
        item_id : str
            The item's ID. This will become its attribute name. Defaults to None.
            If none set, tries to retrieve details from item's properties.
        
        Returns
        -------
        item : CaseItem
            the added item.
        """
        
        if (type(item) == str) and (type(item_id) != None):
            item = item_id
        
        if (item == None) or (type(item) == str):
            return self.add_blank_item(item_id = item_id)
        
        if type(item) != CaseItem:
            raise TypeError('Item must be of type "CaseItem"')
        
        self.items.add_item(item = item, item_id = item_id)
        
        item_id = item.properties.item_id
        self.update_dataframes_from_item(item_id)
        self.update_properties()
         # self.backup()
        
    
    def add_items(self, item_list):
        
        """
        Adds a list of items to the Case's item set.
        
        Parameters
        ----------
        item : CaseItem
            The item to be added. Defaults to None; this adds a blank item.
        item_id : str
            The item's ID. This will become its attribute name. Defaults to None.
            If none set, tries to retrieve details from item's properties.
        
        Returns
        -------
        item : CaseItem
            the added item.
        """
        
        if type(item_list) == CaseItem:
            item_list = [item_list]
        
        for item in item_list:
            
            if type(item) != CaseItem:
                raise TypeError('Item must be of type "CaseItem"')
            
            if item not in self.items.values():
                item.add_id()
                item_id = item.item_id
                self.items.add_item(item)
        
        self.update_dataframes_from_all_items()
        self.update_properties()
        
         # self.backup()
        
    

    # Methods for creating case and case objects from imported data sources
    
    def from_web_crawl(self,
                    seed_urls = 'request_input',
                    visit_limit = 5, 
                    excluded_url_terms = 'default',
                    required_keywords = None, 
                    excluded_keywords = None, 
                    case_sensitive = False,
                    ignore_urls = None, 
                    ignore_domains = 'default',
                    be_polite = True,
                    full = True):
        
        """
        Creates a Case from a web crawl.
        
        Parameters
        ---------- 
        seed_urls : str or list
            one or more URls to crawl from. Defaults to requesting from user input.
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
        """
        
        output = case_from_web_crawl(case_name = '',
                        make_global_var = False,
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
                        output_as = 'dataframe')
        
        self = output
        
        var_name = get_var_name_str(self)
        
        self.properties.case_name = var_name
        
        return self

    def item_from_pdf(self, item_id = 'request_input', file_path = None):
        
        """
        Creates CaseItem from PDF file and adds to Case item set.
        """
        
        return self.items.item_from_pdf(item_id = 'request_input', file_path = file_path)
    
    def item_from_pdf_url(self, item_id = 'request_input', url = None):
        
        """
        Creates CaseItem from PDF URL and adds to Case item set.
        """
        
        return self.items.item_from_pdf_url(item_id = 'request_input', url = url)
    

    def import_item_json(self, item_id = 'request_input', file_address = 'request_input'):
        
        """
        Adds CaseItem from JSON file.
        """
        
        if item_id == 'request_input':
            item_id = input('Item ID: ')
        
        if item_id == None:
            item_id = input('New item ID: ')
            self.add_blank_item(item_id = item_id)
            
        if file_address == 'request_input':
            file_address = input('File address: ')
        
        self.items.get_item(item_id).import_json(file_address = file_address)
        self.items.get_item(item_id).update_properties()
        self.update_dataframes_from_item(item_id)
        self.update_properties()
         # self.backup()
        
    
    def import_multiple_items_json(self, file_address = 'request_input'):
        
        """
        Adds multiple CaseItems from JSON file.
        """
        
        if file_address == 'request_input':
            file_address = input('File address: ')
        
        with open(file_address) as json_file:
            items_dict = json.load(json_file)
        
        for item_id in items_dict.keys():
            try:
                if item_id in self.items.contents():
                    item_dict = items_dict[item_id]
                    self.items.get_item(item_id).from_dict(item_dict)
                    self.items.get_item(item_id).update_properties()

                else:
                    if type(item_id) == str:
                        item_dict = items_dict[item_id]
                        self.add_blank_item(item_id = item_id)
                        self.items.get_item(item_id).from_dict(item_dict)
                        self.items.get_item(item_id).update_properties()
            except:
                raise KeyError('JSON importer ran into an error')
        
        self.update_dataframes_from_all_items()
        self.update_properties()
         # self.backup()
        
    
    def overwrite(self, from_file = True, import_type = 'request_input', import_address = 'request_input'):
        
        """
        Overwrites Case attributes from a file.
        """
        
        case_name = self.get_name_str()
        is_default = self.is_default()
        
        if from_file == True:
            
            if import_type == 'request_input':
                import_type = input('File type: ')
            
            if import_address == 'request_input':
                import_address = input('File address: ')
            
            if import_type.lower() == 'csv':
                self = import_case_csv_folder(case_name = case_name, folder_address = import_address, file_names = 'default_names', parse = False, make_default = is_default)
            
            if (import_type.lower() == 'excel') or ('xlsx' in import_type.lower()):
                self = import_case_excel(case_name = case_name, file_address = import_address, parse = False, make_default = is_default)
            
            if (import_type.lower() == 'text') or (import_type.lower() == 'txt') or ('pickle' in import_type.lower()):
                self = import_case_pickle(case_name = case_name, make_default = is_default)
        
        self.update_properties()
        
        return self 
        
    

    # Methods for cleaning and parsing case data
    
    def parse_rawdata(self):
        
        """
        Parses raw data entries for all inputted items.
        """
        
        self.update_dataframes_from_all_items()
        self.items.parse_rawdata()
        self.properties.parsed = True
        self.update_dataframes_from_all_items()
        self.update_properties()
    
    
    def extract_links(self, item_id = 'all'):
        
        """
        Extracts links from all inputted items' raw data.
        
        Parameters
        ----------
        item_id : str
            one or more item ID's to parse.
        """
        
        self.items.extract_links(item_id = item_id)
        self.update_dataframes_from_all_items()
        self.update_properties()


    # Methods for identifying and analysing case keywords
    
    def generate_keywords(self, frequent_words = True, central_words = False, detailed = True, clean = True):
        
        """
        Generates keywords from Case item data and appends to case dataframes.
        
        Parameters
        ----------
        frequent_words : bool
            whether to generate keywords based on word frequency. Defaults to True.
        central_words : bool
            whether to generate keywords based on word centrality. Defaults to False.
        detailed : bool
            whether to return detailed keywords results. Defaults to True.
        clean : bool
            whether to clean raw data before analysing. Defaults to True.
        """
        
        if self.properties.parsed == False:
            self.parse_rawdata()
        
        if frequent_words == True:
            if detailed == True:
                self.dataframes.keywords.frequent_words = self.get_word_frequencies_detailed(clean = clean)
            else:
                self.dataframes.keywords.frequent_words = self.get_word_frequencies(clean = clean)
        
        if central_words == True:
            try:
                self.dataframes.keywords.central_words = self.sort_keywords_by_centrality()
            except:
                pass
        
        self.properties.keywords_generated = True
        self.dataframes.update_properties()
        self.update_properties()
        
    
    def sort_keywords_by_centrality(self, limit = 600):
        
        """
        Sorts keywords by their centrality in the words coincidence network. Returns a dataframe.
        
        Parameters
        ----------
        limit : int
            a limit for how many words to analyse.
        """
        
        if 'coinciding_words' not in self.networks.contents():
            self.generate_keywords_coincidence_network(limit = limit, append_to_case = True)
        
        df = self.networks.all_centralities(network = 'coinciding_words')
        df.index.name = 'keyword'
        
        return df
    
          

    # Methods for synchronising case objects
    
    def select_update_source(self):
        
        """
        Assesses whehther to use Case items or Case dataframes as the data source for data synchronisation.
        
        Returns
        -------
        result : str
            the attribute name of the most recently edited data source (items or dataframes).
        """
        
        changelog = self.get_objs_changelog()
        earliest = changelog.iloc[0, 1]
        latest = changelog.iloc[-1][1]
        total_td = latest - earliest

        if total_td == timedelta(0):
            update_source = 'do not update'
            return update_source

        items_dfs_changelog = changelog[(changelog.index == 'dataframes') | (changelog.index == 'items')]
        td = items_dfs_changelog.iloc[0,1] - items_dfs_changelog.iloc[1,1]

        if td == timedelta(0):

            df_items_ids = self.dataframes.get_items_set()
            items_obj_ids = set(self.items.ids())

            if df_items_ids == items_obj_ids:
                update_source = 'no source'

            else:
                    if df_items_ids.issubset(items_obj_ids) == True:
                        update_source = 'items'

                    else:
                        if items_obj_ids.issubset(df_items_ids) == True:
                            update_source = 'dataframes'

                        else:
                            df_ids_len = len(df_items_ids)
                            items_ids_len = len(items_obj_ids)

                            if df_ids_len > items_ids_len:
                                update_source = 'dataframes'

                            else:
                                if df_ids_len < items_ids_len:
                                    update_source = 'items'

                                else:
                                    raise ValueError()

        else:
            update_source = items_dfs_changelog.iloc[0].name

        return update_source

    

    def update_dataframes_from_item(self, item_id):
        
        """
        Updates Case dataframes with data from a specific CaseItem. Adds item to dataframes if not present.
        """
        
        df_ids = self.dataframes.get_items_set()

        if item_id not in df_ids:
            self.dataframes.metadata.loc[item_id] = pd.Series(dtype = object)
            self.dataframes.data.loc[item_id] = pd.Series(dtype = object)
            self.dataframes.information.loc[item_id] = pd.Series(dtype = object)
            self.dataframes.other.loc[item_id] = pd.Series(dtype = object)

        item_obj = self.items.get_item(item_id)
        item_metadata = item_obj.metadata
        item_data = item_obj.data
        item_info = item_obj.information
        item_links = item_obj.links
        item_refs = item_obj.references
        item_contents = item_obj.contains

        for index in item_metadata.index:
            metadata = item_metadata.iloc[index, 0]
            category = item_metadata.iloc[index, 1]
            self.dataframes.metadata.loc[item_id, category] = metadata

        for index in item_data.index:
            datatype = item_data.iloc[index, 0]
            rawdata = item_data.iloc[index, 4]
            self.dataframes.data.at[item_id, datatype] = rawdata

        info_categories = set(item_info['Category'].to_list())
        for category in info_categories:
            
            if category not in self.dataframes.information.columns:
                self.dataframes.information[category] = None
                
            info_list = item_info[item_info['Category'] == category]['Label'].to_list()
            self.dataframes.information.at[item_id, category] = info_list

        self.dataframes.other.at[item_id, 'links'] = item_links
        self.dataframes.other.at[item_id, 'references'] = item_refs
        self.dataframes.other.at[item_id, 'contents'] = item_contents

        self.dataframes.metadata = self.dataframes.metadata.replace(np.nan, None)
        self.dataframes.data = self.dataframes.data.replace(np.nan, None)
        self.dataframes.information = self.dataframes.information.replace(np.nan, None)
        self.dataframes.other = self.dataframes.other.replace(np.nan, None)
        
        self.dataframes.update_properties()


    def update_dataframes_from_all_items(self):
        
        """
        Updates Case dataframes with data from all CaseItems. Adds items to dataframes if not present.
        """
        
        item_ids = self.items.ids()

        for item_id in item_ids:
            self.update_dataframes_from_item(item_id)
        
        self.items.update_properties()
        self.dataframes.update_properties()

            
    def df_row_to_data(self, item_id):
        
        """
        Updates CaseItem data with data from Case dataframes.
        """
        
        if item_id not in self.dataframes.data.index:
            self.dataframes.data.loc[item_id] = len(self.dataframes.data.columns)*[None]
        
        data = self.dataframes.data.loc[item_id].copy(deep = True)

        item_data = self.get_item(item_id).data
        for row in data.index:

            raw_data = data[row]
            if raw_data not in item_data['Raw data'].to_list():

                index = len(item_data.index)
                item_data.loc[index, 'Datatype'] = row
                item_data.loc[index, 'Raw data'] = raw_data
                item_data.loc[index, 'Stored as'] = type(raw_data)
                size = sys.getsizeof(raw_data)
                item_data.loc[index, 'Size (bytes)'] = size

                if (row == 'text') or ('word' in row):
                    item_data.loc[index, 'Format'] = 'txt'

                if ('html' in row) or (row == 'web code'):
                    item_data.loc[index, 'Format'] = 'html'

        return item_data
    
    
    def df_row_to_metadata(self, item_id):
        
        """
        Updates CaseItem metadata with metadata from Case dataframes.
        """
        
        if item_id not in self.dataframes.metadata.index:
            self.dataframes.metadata.loc[item_id] = len(self.dataframes.metadata.columns)*[None]
        
        metadata = pd.DataFrame(self.dataframes.metadata.loc[item_id].copy(deep = True))
        metadata.index.name = 'Category'
        metadata = metadata.reset_index()
        metadata['Metadata'] = metadata[item_id]
        metadata = metadata[['Metadata', 'Category']]
        
        item_metadata = self.get_item(item_id).metadata
        item_metadata = pd.concat([item_metadata, metadata])
        item_metadata = item_metadata.drop_duplicates(['Metadata', 'Category'])
        
        return item_metadata
    
    
    def df_row_to_info(self, item_id):
        
        """
        Updates CaseItem information with information from Case dataframes.
        """
        
        if item_id not in self.dataframes.information.index:
            self.dataframes.information.loc[item_id] = len(self.dataframes.information.columns)*[None]
        
        information = pd.DataFrame(self.dataframes.information.loc[item_id]).copy(deep = True)

        information.index.name = 'Category'
        information = information.reset_index()
        information['Label'] = information[item_id]
        information = information[['Label', 'Category']].dropna().reset_index().drop('index', axis=1)

        to_drop = []
        for row in information.index:
            label = information.iloc[row, 0]

            if type(label) == list:
                to_drop.append(row)
                index_len = len(information.index)

                for info in label:
                    information.at[index_len, 'Label'] = info
                    information.at[index_len, 'Category'] = information.iloc[row, 1]
                    index_len += 1

        information = information.drop(to_drop).reset_index().drop('index', axis = 1)
        
        info_obj = self.get_item(item_id).information
        info_obj = pd.concat([info_obj, information])
        info_obj = info_obj.drop_duplicates(subset = ['Label', 'Category'])
        
        return info_obj
    
    
    def df_row_to_other(self, item_id):
        
        """
        Updates CaseItem links, references, and contents from Case dataframes.
        """
        
        if item_id not in self.dataframes.other.index:
            self.dataframes.other.loc[item_id] = len(self.dataframes.other.columns)*[None]
        
        other = pd.DataFrame(self.dataframes.other.loc[item_id]).copy(deep = True)
        
        links = other.loc['links', item_id]
        if links == None:
            links = []
            
        refs = other.loc['references', item_id]
        if refs == None:
            refs = []
        
        contents = other.loc['contents', item_id]
        if contents == None:
            contents = []
        
        item_links = self.get_item(item_id).links
        if item_links == None:
            item_links = []
        links_set = list(set(item_links + links))
        
        item_refs = self.get_item(item_id).references
        if item_refs == None:
            item_refs = []
        refs_set = list(set(item_refs + refs))
        
        item_contents = self.get_item(item_id).contains
        if item_contents == None:
            item_contents = []
        contents_set = list(set(item_contents + contents))
        
        return [links_set, refs_set, contents_set]
        
        
    def update_item_from_dataframes(self, item_id):
        
        """
        Updates CaseItem from Case dataframes.
        """
        
        if item_id not in self.items.ids():
            self.items.add_blank_item(item_id)

        self.get_item(item_id).data = self.df_row_to_data(item_id)
        self.get_item(item_id).metadata = self.df_row_to_metadata(item_id)
        self.get_item(item_id).information = self.df_row_to_info(item_id)

        other_res = self.df_row_to_other(item_id)
        self.get_item(item_id).links = other_res[0]
        self.get_item(item_id).references = other_res[1]
        self.get_item(item_id).contains = other_res[2]

        
    def update_items_from_dataframes(self):
        
        """
        Updates all CaseItems from Case dataframes.
        """
        
        df_ids = self.dataframes.get_items_set()

        for item_id in df_ids:
            self.update_item_from_dataframes(item_id)
        
        self.items.update_properties()
        self.dataframes.update_properties()

            
    def sync_items(self):
        
        """
        Synchronises Case items and dataframes.
        
        Notes
        -----
        Implementation:
            #. Checks for the most recently updated data source (items or dataframes). If both updated at same time, returns.
            #. Updates data from the selected source.
        """
        
        update_source = self.select_update_source()

        if (update_source == 'do not update') or (update_source == 'no source'):
            return

        if update_source == 'items':
            self.update_dataframes_from_all_items()

        if update_source == 'dataframes':
            self.update_items_from_dataframes()
        
        self.update_properties()
    
    def get_all_files(self):
        
        """
        Returns all CaseFile objects from the Case and its attributes.
        """

        files = self.files.to_list()

        item_files = []
        for i in self.items.ids():
            fileset = self.items.get_item(i).files.to_list()
            item_files = item_files + fileset

        for file in item_files:
            if file not in files:
                files.append(file)
    
        entities_files = []
        for i in self.entities.ids():
            fileset = self.entities.get_entity(i).files.to_list()
            entities_files = entities_files + fileset

        for file in entities_files:
            if file not in files:
                files.append(file)

        events_files = []
        for i in self.events.ids():
            fileset = self.events.get_event(i).files.to_list()
            events_files = events_files + fileset

        for file in events_files:
            if file not in files:
                files.append(file)

        return files

    def sync_files(self):
        
        """
        Retrieves all CaseFiles from Case's attributes and adds to the Case's top-level collection of CaseFiles.
        """

        all_files = self.get_all_files()
        all_files_plus_paths = [[i.properties.obj_name, i.properties.obj_path, i, i.path] for i in all_files]
        df = pd.DataFrame(all_files_plus_paths)

        paths = []
        for i in all_files_plus_paths:
            path = i[3]
            if path not in paths:
                paths.append(path)
        paths = set(paths)

        output = CaseFileSet()
    
        for p in paths:

            df_masked = df[df[3] == p].reset_index().drop('index', axis=1)
            first_source = df_masked.loc[0, 2].copy()

            relations = CaseRelationSet()
            for i in df_masked.index:
                rels = df_masked.loc[i, 2].relations
                relations = relations + rels

            first_source.relations = relations

            output.add_file(first_source)

        self.files = output

        return self.files
    
    def update_case(self, sync_items = True, sync_files = True):
        
        """
        Synchronises Case items and dataframes; reruns analysis processes on the updated data.
        
        Parameters
        ----------
        sync_items : bool
            whether or not to synchronise items and dataframes.
        """
        
        keywords = self.properties.keywords_generated
        indexes = self.properties.indexed
        coinciding_data = self.properties.coincidences_identified
        networks = self.properties.networks_generated
        analytics = self.properties.analytics_generated

        if sync_items == True:
            self.sync_items()
        
        if sync_files == True:
            self.sync_files()

        if keywords == True:
            self.generate_keywords()

        if indexes == True:
            self.generate_keywords()

        if coinciding_data == True:
            self.identify_coincidences()

        if networks == True:
            self.generate_all_networks()

        if analytics == True:
            self.generate_analytics()
        
        self.update_properties()

    # Methods for deleting objects and data from case
    
    def delete_item(self, item_id):
        
        """
        Deletes an item from the Case. Takes either an item or an item ID.
        """
        
        self.items.delete_item(item_id)
        self.dataframes.metadata = self.dataframes.metadata.drop(item_id)
        self.dataframes.data = self.dataframes.data.drop(item_id)
        self.dataframes.information = self.dataframes.information.drop(item_id)
        self.dataframes.other = self.dataframes.other.drop(item_id)
        self.update_properties()
        
    def delete_all_items(self):
        
        """
        Deletes all items from the Case.
        """
        
        ids = self.items.ids()
        for item_id in ids:
            self.delete_item(item_id)
        
        self.update_properties()
    
    def delete_all_metadata(self):
        
        """
        Deletes all metadata from Case items.
        """
        
        self.items.delete_all_metadata()
        delattr(self.dataframes, 'metadata')
        self.dataframes.metadata = pd.DataFrame(columns = ['name',
                                                     'data_id',
                                                    'hash',
                                                     'description',
                                                     'type',
                                                     'format',
                                                     'size',
                                                     'source',
                                                     'domain',
                                                    'url',
                                                     'created_at',
                                                     'created_by',
                                                     'last_changed_at',
                                                     'last_changed_by',
                                                     'uploaded_at',
                                                     'uploaded_by',
                                                     'region',
                                                     'location',
                                                        'address',
                                                     'coordinates',
                                                   'language']
                                               )
        
        self.items.update_properties()
        self.dataframes.update_properties()
        self.update_properties()
        
    def delete_all_data(self):
        
        """
        Deletes all data from Case items.
        """
        
        self.items.delete_all_data()
        delattr(self.dataframes, 'data')
        self.dataframes.data = pd.DataFrame(columns = ['html', 'text', 'image', 'video', 'audio'])
        self.update_properties()
    
    def delete_all_info(self):
        
        """
        Deletes all information from Case items.
        """
        
        self.items.delete_all_info()
        delattr(self.dataframes, 'information')
        self.dataframes.information = pd.DataFrame(columns = ['names',
                                                        'people',
                                                        'organisations',
                                                        'regions',
                                                        'places',
                                                        'coordinates',
                                                        'time periods',
                                                        'date_times',
                                                        'events',
                                                        'activities',
                                                        'symbols',
                                                        'weather',
                                                        'objects',
                                                        'languages'])
        
        self.items.update_properties()
        self.dataframes.update_properties()
        self.update_properties()
    
    

    # Methods for retrieving objects and data from case
    
    def get_obj(self, obj_name = 'request_input'):
        
        """
        Returns a Case object if given its name.
        """
        
        if obj_name == 'request_input':
            obj_name = input('Object name: ')
        
        return self.__dict__[obj_name]

    def get_objs_last_changed_dict(self):
        
        """
        Returns last changed time properties for all objects as a dictionary.
        """
        
        out_dict = {}
        contents = self.contents()
        for obj in contents:
            try:
                out_dict[obj] = self.get_obj(obj).properties.last_changed_at
            except:
                pass

        return out_dict

    
    def get_objs_changelog(self):
            
            """
            Returns changelog for all objects as a pandas.DataFrame.
            """
            
            df = pd.DataFrame(columns = ['Created at', 'Last changed at'])
            contents = self.contents()

            for obj_name in contents:
                try:
                    obj = self.get_obj(obj_name)
                    df.loc[obj_name] = [
                                    obj.properties.created_at, 
                                    obj.properties.last_changed_at
                                    ]
                except:
                    pass

            df.index.name = 'Object'
            df['Created at'] = df['Created at'].astype('datetime64[ns]')
            df['Last changed at'] = df['Last changed at'].astype('datetime64[ns]')
            
            return df.sort_values('Last changed at', ascending=False)

        
    
    
    def get_item(self, item_id = 'request_input'):
        
        """
        Returns an item if given its ID.
        """
        
        if item_id == 'request_input':
            item_id = input('Item ID: ')
        
        return self.items.__dict__[item_id]
    
    def get_items_dict(self):
        
        """
        Returns all items as a dictionary.
        """
        
        return self.items.to_dict()
    
    def get_item_ids(self):
        
        """
        Returns all item IDs.
        """
        
        return self.items.ids()
    
    def get_item_count(self):
        
        """
        Returns the number of items in the Case.
        """
        
        return self.items.count_items()
    
    def get_items_dfs_change_timedelta(self):
        
        """
        Returns time difference between when items and dataframes were last changed.
        """
        
        df = self.get_objs_changelog()
        df = df[(df.index == 'dataframes') | (df.index == 'items')]

        td = df.iloc[0,1] - df.iloc[1,1]

        return td
    
    def get_info(self, select_by_category = None):
        
        """
        Returns all information entries as a Pandas series.
        
        Parameters
        ----------
        select_by_category : str
            specifies an information category to return. Defaults to None: returns information from all categories.
        """
        
        df = self.dataframes.information.copy(deep=True)

        if type(select_by_category) == str:
            select_by_category = [select_by_category]
        
        if type(select_by_category) == list:
             df = df[select_by_category]
        
        return df
    
    def get_metadata(self, select_by_category = None):
        
        """
        Returns all metadata from dataframes as a Pandas series.
        
        Parameters
        ----------
        select_by_category : str
            specifies a metadata category to return. Defaults to None: metadata from all categories are returned.
        """
        
        df = self.dataframes.metadata.copy(deep=True)

        if type(select_by_category) == str:
            select_by_category = [select_by_category]
        
        if type(select_by_category) == list:
             df = df[select_by_category]
        
        return df
    
    
    def get_all_addresses(self, ignore_nones = True):
        
        """
        Returns all address metadata entries.
        
        Parameters
        ----------
        ignore_nones : bool
            whether or not to return empty/None results. Defaults to True: empty/None entries are not returned.
        """
        
        return self.get_all_addresses(ignore_nones = ignore_nones)
    
    
    def get_all_urls_metadata(self):
        
        """
        Returns all URL metadata entries.
        """
        
        return self.items.get_all_urls_metadata()
    
    def get_urls_metadata_set(self):
        
        """
        Returns the set of unique URL metadata entries.
        """
        
        return self.items.get_urls_metadata_set()
    
    def get_urls_metadata_dict(self):
        
        """
        Returns a dictionary containing all URL metadata entries.
        """
        
        return self.items.get_urls_metadata_dict()
    
    def get_all_data(self, select_by_type = None):
        
        """
        Returns all data from all items. Can choose to return only a specified data type.
        
        Parameters
        ----------
        select_by_type : str
            specifies a datatype to return. Defaults to None; all data types returned.
        """
        
        return self.items.get_all_data(select_by_type = select_by_type)
    
    def get_all_rawdata(self, select_by_type = None):
        
        """
        Returns all raw data entries.
        """
        
        return self.items.get_all_rawdata(select_by_type = select_by_type)
    
    def get_rawdata_set(self, select_by_type = None):
        
        """
        Returns the set of unique raw data entries.
        """
        
        return self.items.get_rawdata_set(select_by_type = select_by_type)
    
    def get_rawdata_frequencies(self, select_by_type = None):
        
        """
        Returns frequency counts for unique raw data entries.
        """
        
        return self.items.get_rawdata_frequencies(select_by_type = select_by_type)
    
    def get_rawdata_stats(self, select_by_type = None):
        
        """
        Returns frequency statistics for unique raw data entries.
        """
        
        return self.items.get_rawdata_stats(select_by_type = select_by_type)
    
    def get_data_intersect(self):
        
        """
        Returns the intersect of raw data sets from all items.
        """
        
        return self.items.get_data_intersect()
    
    def get_data_symmetric_difference(self):
        
        """
        Returns the symmetric difference of raw data sets from all items.
        
        i.e., all raw data entries which are only in one set.
        """
        
        return self.items.get_data_symmetric_difference()
    

    def get_all_words(self, clean = True):
        
        """
        Returns all words parsed from all items.
        
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        """
        
        return self.items.get_all_words(clean = clean)
    
    
    def get_word_frequencies(self, clean = True):
        
        """
        Returns frequency counts for all words found in parsed data across all items.
        
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        """
        
        return self.items.get_word_frequencies(clean = clean)
    
    
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
        
        return self.items.get_word_frequencies_detailed(clean = clean)
    
    def word_mean_frequencies(self, clean = True):
        
        """
        Returns the mean number of times each word in items' parsed data occurred per item.
        
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        """
        
        return self.items.word_mean_frequencies(clean = clean)
    
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
        
        return self.items.get_most_frequent_words(clean = clean, top = top)
    
    def highest_frequency_per_items_words(self, clean = True, top = 15):
        
        """
        Returns the most frequently occurring words per item.
        
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        top : int
            how many words to return.
        """
        
        return self.items.highest_frequency_per_items_words(clean = clean, top = top)
    
    def get_word_stats(self, clean = True):
        
        """
        Returns frequency statistics for all words found in items' parsed data.
        """
        
        return self.items.get_word_stats(clean = clean)
    
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
        
        return self.items.get_word_stats_detailed(clean = clean)
    
    def rawdata_with_words(self):
        
        """
        Returns a dataframe displaying items' raw data entries and the words extracted from them.
        """
        
        return self.items.rawdata_with_words()
    
    def get_words_set(self):
        
        """
        Returns the set of unique words parsed from all items.
        
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        """
        
        return self.items.get_words_set()
    
    def get_words_set_size(self, clean = True):
        
        """
        Returns the number of unique words parsed from all items.
        
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        """
        return self.items.get_words_set_size(clean = clean)
    
    def get_words_intersect(self, clean = True):
        
        """
        Returns the intersection of all items' word sets.
        
        i.e., any words shared by all items.
            
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        """
        
        return self.items.get_words_intersect(clean = clean)
    
    def get_words_symmetric_difference(self, clean = True):
        
        """
        Returns the symmetric difference of all items' word sets.
        
        i.e., any words *not* shared by all items.
            
        Parameters
        ----------
        clean : bool
            whether to clean text when parsing. Defaults to True.
        """
        
        return self.items.get_words_symmetric_difference(clean = clean)
    
    
    def get_keywords(self, ranking = 'frequency'):
            
            """
            Returns a keywords dataframe based on user's choice of ranking metric.
            
            Parameters
            ----------
            ranking : str
                metric for ranking keywords. Either 'frequency' or 'centrality'.
            """
            
            if (('frequent_words' in self.dataframes.keywords.contents()) and (len(self.dataframes.keywords.frequent_words.index) > 0)):
                self.properties.keywords_generated = True
            
            if (('central_words' in self.dataframes.keywords.contents()) and (len(self.dataframes.keywords.central_words.index) > 0)):
                self.properties.keywords_generated = True
            
            if type(ranking) != str:
                raise TypeError('Ranking must be a string')
            
            if (ranking == 'frequency') or (ranking == 'frequent') or (ranking == 'frequent_words'):
                return self.dataframes.keywords.frequent_words
            
            if (ranking == 'centrality') or (ranking == 'central') or (ranking == 'central_words'):
                return self.dataframes.keywords.central_words
    

    def get_all_info(self, select_by_category = None):
        
        """
        Returns all information from all items.
        
        Parameters
        ----------
        select_by_category : str
            specifies an information category to return. Defaults to None: returns information from all categories.
        """
        
        return self.items.get_all_info(select_by_category = select_by_category)
    
    def get_info_series(self, select_by_category = None):
        
        """
        Returns all information entries as a Pandas series.
        
        Parameters
        ----------
        select_by_category : str
            specifies an information category to return. Defaults to None: returns information from all categories.
        """
        
        return self.items.get_info_series(select_by_category = select_by_category)['Label']
    
    def get_info_list(self, select_by_category = None):
        
        """
        Returns all information entries as a list of tuples.
        
        Parameters
        ----------
        select_by_category : str
            specifies an information category to return. Defaults to None: returns information from all categories.
        """
        
        return self.items.get_info_list(select_by_category = select_by_category)
    
    def get_info_count(self, select_by_category = None):
        
        """
        Returns number of information entries.
        
        Parameters
        ----------
        select_by_category : str
            specifies a information category to return. Defaults to None: returns information from all categories.
        """
        
        return self.items.get_info_count(select_by_category = select_by_category)
    
    def get_info_set(self, select_by_category = None):
        
        """
        Returns set of unique information entries.
        
        Parameters
        ----------
        select_by_category : str
            specifies a information category to return. Defaults to None: returns information from all categories.
        """
        
        return self.items.get_info_set(select_by_category = select_by_category)
    
    def get_info_set_size(self, select_by_category = None):
        
        """
        Returns the number of unique information entries.
        
        Parameters
        ----------
        select_by_category : str
            specifies a information category to return. Defaults to None: returns information from all categories.
        """
        
        return self.items.get_info_set_size(select_by_category = select_by_category)
    
    def get_repeated_info_count(self, select_by_category = None):
        
        """
        Returns the number of repeated information entries.
        
        Parameters
        ----------
        select_by_category : str
            specifies a information category to return. Defaults to None: returns information from all categories.
        """
        
        return self.items.get_repeated_info_count(select_by_category = select_by_category)
    
    def get_info_dict(self, select_by_category = None):
        
        """
        Returns all information entries as dictionary.
        
        Parameters
        ----------
        select_by_category : str
            specifies an information category to return. Defaults to None: returns information from all categories.
        """
        
        return self.items.get_info_dict(select_by_category = select_by_category)
    
    def get_info_frequencies(self, select_by_category = None):
        
        """
        Returns the frequency counts for information entries.
        
        Parameters
        ----------
        select_by_category : str
            specifies a information category to return. Defaults to None: returns information from all categories.
        """
        
        return self.items.get_info_frequencies(select_by_category = select_by_category)
    
    def get_info_stats(self, select_by_category = None):
        
        """
        Returns frequency statistics for information entries.
        
        Parameters
        ----------
        select_by_category : str
            specifies a information category to return. Defaults to None: returns information from all categories.
        """
        
        return self.items.get_info_stats(select_by_category = select_by_category)
    
    def get_info_frequencies_by_category(self, select_by_category = None):
        
        """
        Returns the frequency counts for information categories and labels.
        
        Parameters
        ----------
        select_by_category : str
            specifies a information category to return. Defaults to None: returns information from all categories.
        """
        
        return self.items.get_info_frequencies_by_category(select_by_category = select_by_category)
    
    def get_info_stats_by_category(self, select_by_category = None):
        
        """
        Returns frequency statistics for information categories and labels.
        
        Parameters
        ----------
        select_by_category : str
            specifies a information category to return. Defaults to None: returns information from all categories.
        """
        
        return self.items.get_info_stats_by_category(select_by_category = select_by_category)
    
    def get_info_category_frequencies(self, select_by_category = None):
        
        """
        Returns frequency counts for all information categories.
        
        Parameters
        ----------
        select_by_category : str
            specifies a category to return. Defaults to None: all categories are returned.
        """
        
        return self.items.get_info_category_frequencies(select_by_category = select_by_category)
    
    def get_info_category_stats(self, select_by_category = None):
        
        """
        Returns frequency statistics for all information categories.
        
        Parameters
        ----------
        select_by_category : str
            specifies a category to return. Defaults to None: all categories are returned.
        """
        
        return self.items.get_info_category_stats(select_by_category = select_by_category)
    
    def get_info_intersect(self):
        
        """
        Returns the intersect of information sets from all items.
        
        i.e., any information entries which are found in all items.
        """
        
        return self.items.get_info_intersect()
    
    def get_info_symmetric_difference(self):
        
        """
        Returns the symmetric difference of information sets from all items.
        
        i.e., any information entries which are *not* found in all items.
        """
        
        return self.items.get_info_symmetric_difference()
    
    def case_info_sets_similarity(self):
        
        """
        Returns the Jaccard similarity between information sets from all items.
        
        i.e., how many information entries are found in all versus the total number.
        """
        
        return self.items.get_info_sets_similarity()
    
    def get_all_metadata(self, select_by_category = None, ignore_nones = True):
        
        """
        Returns all metadata from all items.
        
        Parameters
        ----------
        select_by_category : str
            specifies a metadata category to return. Defaults to None: metadata from all categories are returned.
        ignore_nones : bool
            whether or not to return empty/None metadata entries. Defaults to True: empty/None entries are not returned.
        """
        
        return self.items.get_all_metadata(select_by_category = select_by_category, ignore_nones = ignore_nones)
    
    def get_metadata_dict(self, select_by_category = None, ignore_nones = True):
        
        """
        Returns a dictionary of metadata from all items.
        
        Parameters
        ----------
        select_by_category : str
            specifies a metadata category to return. Defaults to None: metadata from all categories are returned.
        ignore_nones : bool
            whether or not to return empty/None metadata entries. Defaults to True: empty/None entries are not returned.
        """
        
        return self.items.get_metadata_dict(select_by_category = select_by_category, ignore_nones = ignore_nones)
    
    def get_metadata_nested_dict(self, select_by_category = None, ignore_nones = True):
        
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
        
        return self.items.get_metadata_nested_dict(select_by_category = select_by_category, ignore_nones = ignore_nones)
    
    def get_metadata_series(self, select_by_category = None, ignore_nones = True):
        
        """
        Returns all metadata from all items as a Pandas series.
        
        Parameters
        ----------
        select_by_category : str
            specifies a metadata category to return. Defaults to None: metadata from all categories are returned.
        ignore_nones : bool
            whether or not to return empty/None metadata entries. Defaults to True: empty/None entries are not returned.
        """
        
        return self.items.get_metadata_series(select_by_category = select_by_category, ignore_nones = ignore_nones)
    
    def get_metadata_list(self, select_by_category = None, ignore_nones = True):
        
        """
        Returns a list of all metadata values from all items. Does not return metadata categories.
        
        Parameters
        ----------
        select_by_category : str
            specifies a metadata category to return. Defaults to None: metadata from all categories are returned.
        ignore_nones : bool
            whether or not to return empty/None metadata entries. Defaults to True: empty/None entries are not returned.
        """
        
        return self.items.get_metadata_list(select_by_category = select_by_category, ignore_nones = ignore_nones)
    
    def get_metadata_set(self, select_by_category = None, ignore_nones = True):
        
        """
        Returns a set of all unique metadata values from all items. Does not return metadata categories.
        
        Parameters
        ----------
        select_by_category : str
            specifies a metadata category to return. Defaults to None: metadata from all categories are returned.
        ignore_nones : bool
            whether or not to return empty/None metadata entries. Defaults to True: empty/None entries are not returned.
        """
        
        return self.items.get_metadata_set(select_by_category = select_by_category, ignore_nones = ignore_nones)
    
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
        
        return self.items.get_metadata_frequencies(select_by_category = select_by_category, ignore_nones = ignore_nones)
    
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
        
        return self.items.get_metadata_stats(select_by_category = select_by_category, ignore_nones = ignore_nones)
    
    def get_all_metadata_sets(self):
        
        """
        Returns unique metadata values from all items as a list of sets.
        """
        
        return self.items.get_all_metadata_sets()
        
    def get_metadata_intersect(self):
        
        """
        Returns the intersect of metadata sets from all items.
        """
        
        return self.items.get_metadata_intersect()
    
    def get_metadata_symmetric_difference(self):
        
        """
        Returns the symmetric difference of metadata sets from all items.
        
        i.e., all metadata entries which are only in one set.
        """
        
        return self.items.get_metadata_symmetric_difference()
    
    def get_metadata_sets_similarity(self):
        
        """
        Returns the Jaccard similarity between metadata sets from all items.
        
        i.e., how many metadata entries are shared by all versus the total number.
        """
        
        return self.items.get_metadata_sets_similarity()

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
        
        return self.items.get_metadata_categories(select_by_category = select_by_category, ignore_nones = ignore_nones)
    
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
        
        return self.items.get_metadata_category_frequencies(select_by_category = select_by_category, ignore_nones = ignore_nones)

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
        
        return self.items.get_metadata_category_stats(select_by_category = select_by_category, ignore_nones = ignore_nones)
    
    def get_all_addresses(self, ignore_nones = True):
        
        """
        Returns all address metadata entries.
        
        Parameters
        ----------
        ignore_nones : bool
            whether or not to return empty/None results. Defaults to True: empty/None entries are not returned.
        """
        
        return self.items.get_all_addresses(ignore_nones = ignore_nones)
    
    def get_address_list(self, ignore_nones = True):
        
        """
        Returns all address metadata entries as a list.
        
        Parameters
        ----------
        ignore_nones : bool
            whether or not to return empty/None results. Defaults to True: empty/None entries are not returned.
        """
        
        return self.items.get_address_list(ignore_nones = ignore_nones)
    
    # returns set of all addresses

    def get_address_set(self, ignore_nones = True):
        
        """
        Returns the set of unique address metadata entries.
        
        Parameters
        ----------
        ignore_nones : bool
            whether or not to return empty/None results. Defaults to True: empty/None entries are not returned.
        """
        
        return self.items.get_address_set(ignore_nones = ignore_nones)
    
    def get_address_dict(self, ignore_nones = True):
        
        """
        Returns a dictionary address metadata entries.
        
        Parameters
        ----------
        ignore_nones : bool
            whether or not to return empty/None results. Defaults to True: empty/None entries are not returned.
        """
        
        return self.items.get_address_dict(ignore_nones = ignore_nones)
    
    def get_all_urls_metadata(self):
    
        """
        Returns all URL metadata entries.
        """
        
        return self.items.get_all_urls_metadata()
    

    def get_urls_metadata_set(self):
        
        """
        Returns the set of unique URL metadata entries.
        """
        
        return self.items.get_urls_metadata_set()

    def get_urls_metadata_dict(self):
        
        """
        Returns a dictionary containing all URL metadata entries.
        """
        
        return self.items.get_urls_metadata_dict()
    
    def get_all_links(self):
        
        """
        Returns all links found in items.
        """
        
        return self.items.get_all_links()
    
    def get_links_set(self):
        
        """
        Returns the set of unique links found in items.
        """
        
        return self.items.get_links_set()
    
    def get_all_link_sets(self):
        
        """
        Returns the unique links found in each item as a list of sets.
        """
        
        return self.items.get_all_link_sets()
        
    def get_links_intersect(self):
        
        """
        Returns the intersection of all items' link sets.
        
        i.e., any links shared by all items.
        """
        
        return self.items.get_links_intersect()
    
    def get_links_symmetric_difference(self):
        
        """
        Returns the symmetric difference of all items' link sets.
        
        i.e., any links *not* shared by all items.
        """
        
        return self.items.get_links_symmetric_difference()
    
    def get_link_sets_similarity(self):
        
        """
        Returns the Jaccard similarity between all items' link sets.
        
        i.e., how many links are found in all versus the total number.
        """
        
        return self.items.get_link_sets_similarity()
    
    def get_links_dict(self):
        
        """
        Returns links as a dictionary.
        
        Notes
        -----
        Dictionary structure:
            * keys: item IDs
            * values: link lists
        """
        
        return self.items.get_links_dict()
    
    def get_links_frequencies(self):
        
        """
        Returns frequency counts for links.
        """
        
        return self.items.get_links_frequencies()
    
    def get_links_frequencies_detailed(self):
        
        """
        Returns frequency counts for links with detail on where each link was found.
        """
        
        return self.items.get_links_frequencies_detailed()
    
    def get_links_stats(self):
        
        """
        Returns frequency statistics for links.
        """
        
        return self.items.get_links_stats()
    
    def get_all_refs(self):
        
        """
        Returns all references found in items.
        """
        
        return self.items.get_all_refs()
    
    def get_refs_set(self):
        
        """
        Returns the set of unique references found in items.
        """
        
        return self.items.get_refs_set()
    
    def get_all_refs_sets(self):
        
        """
        Returns the unique references found in each item as a list of sets.
        """
        
        return self.items.get_all_refs_sets()
        
    def get_refs_intersect(self):
        
        """
        Returns the intersection of all items' references sets.
        
        i.e., any references shared by all items.
        """
        
        return self.items.get_refs_intersect()
    
    def get_refs_symmetric_difference(self):
        
        """
        Returns the symmetric difference of all items' references sets.
        
        i.e., any references *not* shared by all items.
        """
        
        return self.items.get_refs_symmetric_difference()
    
    def get_refs_sets_similarity(self):
        
        """
        Returns the Jaccard similarity between all items' references sets.
        
        i.e., how many references are found in all versus the total number of unique references.
        """
        
        return self.items.get_refs_sets_similarity()
    
    def get_refs_dict(self):
        
        """
        Returns references as a dictionary.
        
        Notes
        -----
        Dictionary structure:
            * keys: item IDs
            * values: references lists
        """
        
        return self.items.get_refs_dict()
    
    def get_refs_frequencies(self):
        
        """
        Returns frequency counts for references.
        """
        
        return self.items.get_refs_frequencies()
    
    def get_refs_stats(self):
        
        """
        Returns frequency statistics for references.
        """
        
        return self.items.get_refs_stats()
    
    def get_all_contents(self):
        
        """
        Returns all contents entries found in items.
        """
        
        return self.items.get_all_contents()
    
    def get_contents_set(self):
        
        """
        Returns the set of unique contents entries found in items.
        """
        
        return self.items.get_contents_set()
    
    def get_all_contents_sets(self):
        
        """
        Returns the unique contents entries found in each item as a list of sets.
        """
        
        return self.items.get_all_contents_sets()
        
    def get_contents_intersect(self):
        
        """
        Returns the intersection of all items' contents sets.
        
        i.e., any contents entries shared by all items.
        """
        
        return self.items.get_contents_intersect()
    
    def get_contents_symmetric_difference(self):
        
        """
        Returns the symmetric difference of all items' contents sets.
        
        i.e., any contents entries *not* shared by all items.
        """
        
        return self.items.get_contents_symmetric_difference()
    
    def get_contents_sets_similarity(self):
        
        """
        Returns the Jaccard similarity between all items' contents sets.
        
        i.e., how many contents entries are found in all versus the total number of unique references.
        """
        
        return self.items.get_contents_sets_similarity()
    
    def get_contents_dict(self):
        
        """
        Returns item contents as a dictionary.
        
        Notes
        -----
        Dictionary structure:
            * keys: item IDs
            * values: references lists
        """
        
        return self.items.get_contents_dict()
    
    def get_contents_frequencies(self):
        
        """
        Returns frequency counts for contents entries.
        """
        
        return self.items.get_contents_frequencies()
    
    def get_contents_stats(self):
        
        """
        Returns frequency statistics for contents entries.
        """
        
        return self.items.get_contents_stats()
    

    # Methods for checking if objects and data are in case
    
    def check_for_item_id(self, item_id = 'request_input'):
        
        """
        Checks if the Case contains an item ID.
        """
        
        return self.items.check_for_item_id(item_id = item_id)
    
    def check_for_info(self, label = 'request_input', category = 'all'):
        
        """
        Checks if a string matches any of the Case's item information entries.
        """
        
        return self.items.check_for_info(label = label, category = category)
    
    def check_for_metadata(self, metadata = 'request_input', category = 'all'):
        
        """
        Checks if a string matches any of the Case's item metadata entries.
        """
        
        return self.items.check_for_metadata(metadata = metadata, category = category)
    
    def check_for_link(self, link = 'request_input'):
        
        """
        Checks if a string matches any of the Case's item link entries.
        """
        
        return self.items.check_for_link(link = link)
    
    def check_for_address(self, address = 'request_input'):
        
        """
        Checks if a string matches any of the Case's item address metadata entries.
        """
        
        return self.items.check_for_address(address = address)
    

    # Methods for analysing data similarity
    
    def items_text_cosine(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the cosine similarity of two items' text based on word frequencies.
        
        Parameters
        ----------
        item_1 : str
            first item to compare. Defaults to requesting from user input.
        item_2 : str
            second item to compare. Defaults to requesting from user input.
        """
        
        return self.items.text_cosine(item_1 = item_1, item_2 = item_2)
        
    
    def items_text_levenshtein(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the levenshtein distance between two items' text.
        
        Parameters
        ----------
        item_1 : str
            first item to compare. Defaults to requesting from user input.
        item_2 : str
            second item to compare. Defaults to requesting from user input.
        """
        
        return self.items.text_levenshtein(item_1 = item_1, item_2 = item_2)
    
    
    def items_words_cosine(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the cosine similarity of two items' parsed words based on word frequencies.
        
        Parameters
        ----------
        item_1 : str
            first item to compare. Defaults to requesting from user input.
        item_2 : str
            second item to compare. Defaults to requesting from user input.
        """
        
        return self.items.words_cosine(item_1 = item_1, item_2 = item_2)
    
    
    def items_words_levenshtein(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the levenshtein distance between two items' parsed word sets.
        
        Parameters
        ----------
        item_1 : str
            first item to compare. Defaults to requesting from user input.
        item_2 : str
            second item to compare. Defaults to requesting from user input.
        """
        
        return self.items.words_levenshtein(item_1 = item_1, item_2 = item_2)
    
    
    def items_words_intersect(self, item_1 = 'request_input', item_2 = 'request_input'):
        
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
        
        return self.items.words_intersect(input_1 = input_1, input_2 = input_2)

    def items_words_set_sim(self, item_1 = 'request_input', item_2 = 'request_input'):
        
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
        
        return self.items.words_set_sim(item_1 = item_1, item_2 = item_2)
        
    def all_items_words_comparisons(self, sort_by = 'Set similarity'):
        
        """
        Compares items' parsed words for all combinations of two items. Returns a dataframe.
        """
        
        return self.items.get_all_words_comparisons(sort_by = sort_by)

    def items_metadata_levenshteins(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the levenshtein distance between metadata data entries for each category in two items.
        
        Parameters
        ----------
        item_1 : str
            first item to compare.
        item_2 : str
            second item to compare.
        """
        
        return self.items.metadata_category_levenshteins(item_1 = item_1, item_2 = item_2)
        
    def items_metadata_mean_levenshtein(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the mean levenshtein distance between metadata data entries for each category in two items.
        
        Parameters
        ----------
        item_1 : str
            first item to compare.
        item_2 : str
            second item to compare.
        """
        
        return self.items.metadata_mean_levenshteins(item_1 = item_1, item_2 = item_2)
        
    def items_metadata_cosine(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the cosine similarity of two items' metadata lists based on word frequencies.
        
        Parameters
        ----------
        item_1 : str
            first item to compare.
        item_2 : str
            second item to compare.
        """
        
        return self.items.metadata_cosine(item_1 = item_1, item_2 = item_2)
    
    def items_metadata_set_sim(self, item_1 = 'request_input', item_2 = 'request_input'):
        
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
        
        return self.items.metadata_set_sim(item_1 = item_1, item_2 = item_2)
    
    def all_items_metadata_comparisons(self, sort_by = 'Cosine similarity'):
        
        """
        Compares items' metadata for all combinations of two items. Returns a dataframe.
        """
        
        return self.items.get_all_metadata_comparisons(sort_by = sort_by)
        
    def items_info_cosine(self, item_1 = 'request_input', item_2 = 'request_input'):
        
        """
        Returns the cosine similarity of two items' information entries based on word frequencies.
        
        Parameters
        ----------
        item_1 : str
            first item to compare.
        item_2 : str
            second item to compare.
        """
        
        return self.items.info_cosine(item_1 = item_1, item_2 = item_2)
        
    def items_info_set_sim(self, item_1 = 'request_input', item_2 = 'request_input'):
        
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
        
        return self.items.info_set_sim(item_1 = item_1, item_2 = item_2)
        
    def all_items_info_comparisons(self, sort_by = 'Cosine similarity'):
        
        """
        Compares items' information entries for all combinations of two items. Returns a dataframe.
        """
        
        return self.items.get_all_info_comparisons(sort_by = sort_by)
    

    def info_levenshteins(self, select_by_category = None, ignore_nones = True):
        
        """
        Calculates the levenshtein distance between two information labels, organised by category. Returns a pandas.DataFrame.
        """
        
        return self.items.info_levenshteins(select_by_category = select_by_category, ignore_nones = ignore_nones)
        
    
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
        
        return self.items.find_info_close_matches(cutoff = cutoff, select_by_category = select_by_category, ignore_nones = ignore_nones)


    def metadata_levenshteins(self, select_by_category = None, ignore_nones = True):
        
        """
        Calculates the levenshtein distance between two metadata entries, organised by category. Returns a pandas.DataFrame.
        """
        
        return self.items.metadata_levenshteins(select_by_category = select_by_category, ignore_nones = ignore_nones)
        
        
    
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
        
        return self.items.find_metadata_close_matches(cutoff = cutoff, select_by_category = select_by_category, ignore_nones = ignore_nones)
    

    def keyword_levenshteins(self, exclude_numbers = True, limit = 600):
        
        """
        Calculates the levenshtein distance between two keyword entries. Returns a pandas.DataFrame.
        """
        
        return self.items.keyword_levenshteins(exclude_numbers = exclude_numbers, limit = limit)

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
        
        return self.items.find_keywords_close_matches(cutoff = cutoff, exclude_numbers = exclude_numbers, limit = limit)
    

    # Methods for analysing time metadata
    
    def created_time_difference(self, first_item = 'request_input', second_item = 'request_input'):
        
        """
        Returns the time difference between items' created time metadata entries.
        
        Returns
        -------
        time_difference : datetime.timedelta
            the time difference between items' created time metadata entries.
        """
        
        return self.items.created_time_difference(first_item = first_item, second_item = second_item)
    
    def get_all_created_times(self):
        
        """
        Returns created time metadata for all items as a pandas.DataFrame.
        """
        
        df = pd.DataFrame(self.dataframes.metadata['created_at'], dtype=object)
        return df.sort_values('created_at', ascending=False)
    

    def get_all_upload_times(self):
        
        """
        Returns uploaded time metadata for all items as a pandas.DataFrame.
        """
        
        df = pd.DataFrame(self.dataframes.metadata['uploaded_at'], dtype=object)
        return df.sort_values('uploaded_at', ascending=False)

    
    def get_all_last_changed_times(self):
        
        """
        Returns last changed time metadata for all items as a pandas.DataFrame.
        """
        
        df = pd.DataFrame(self.dataframes.metadata['last_changed_at'], dtype=object)
        return df.sort_values('last_changed_at', ascending=False)
    
    def get_all_time_metadata(self):
        
        """
        Returns all time metadata as a pandas.DataFrame.
        """
        
        df = self.dataframes.metadata[['created_at', 'uploaded_at', 'last_changed_at']]
        return df.sort_values('created_at', ascending=False)
        
    
    def item_created_time_range(self):
        
        """
        Returns the difference between the first and last created time metadata entries.
        """
        
        df = self.get_all_created_times().dropna()
        
        if len(df.index) > 2:
            return df.iloc[0][0] - df.iloc[-1][0]
        else:
            raise ValueError('No item created times found')

    
    def item_uploaded_time_range(self):
        
        """
        Returns the difference between the first and last uploaded time metadata entries.
        """
        
        df = self.get_all_upload_times().dropna()
        
        if len(df.index) > 2:
            return df.iloc[0][0] - df.iloc[-1][0]
        else:
            raise ValueError('No uploaded times found')

            
    def item_last_changed_time_range(self):
        
        """
        Returns the difference between the oldest and most recent last changed time metadata entries.
        """
        
        df = self.get_all_last_changed_times().dropna()
        
        if len(df.index) > 2:
            return df.iloc[0][0] - df.iloc[-1][0]
        else:
            raise ValueError('No last changed times found')
            
    
    def items_timeline(self, plot = 'created_at', units = 'months', intervals = 4, date_format = '%d.%m.%Y', colour = 'blue'):
        
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
            dates_res = self.get_all_created_times().dropna()
            dates = dates_res['created_at'].to_list()

        if plot == 'uploaded_at':
            dates_res = self.get_all_upload_times().dropna()
            dates = dates_res['uploaded_at'].to_list()

        if (plot == 'last_changed') or (plot == 'last_changed_at'):
            dates_res = self.get_all_last_changed_times().dropna()
            dates = dates_res['last_changed_at'].to_list()

        names = dates_res.index.to_list()
        
        plot_timeline(dates = dates, names = names, plot = plot, units = units, intervals = intervals, date_format = date_format, colour = colour)
    
    def item_metadata_time_ranges(self):
        
        """
        Returns the time difference between created and last changed metadata for all items.
        """
        
        df = self.get_all_time_metadata().reset_index()
        df['Item'] = df['Item key']

        df['start'] = df['created_at']
        df['end'] = df['last_changed_at']
        df = df[['Item', 'start', 'end']].dropna(subset = 'start')

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
        
        df = self.item_metadata_time_ranges().reset_index()
        labels = df['Item'].to_list()

        plot_date_range_timeline(source = df, labels = labels)
    
    
    # Methods for inferring information from data
    
    def infer_names(self, names_source = 'all_personal_names'):
        
        """
        Identifies personal names from items' text data and appends to information sets. Uses list of all personal names by default. Parses data if not parsed.
        
        Parameters
        ----------
        names_source : str or list
            corpus of names corpus to use; or names corpus as list. Defaults to 'all_personal_names'.
        """
        
        return self.items.infer_names(names_source = names_source)
    

    def infer_countries(self, language = 'all'):
        
        """
        Identifies country names from items' text data and appends to information sets. Uses list of all language names by default. Parses data if not parsed.
        
        Parameters
        ----------
        language : str or list
            language of country names corpus to use; or country names corpus as list. Defaults to 'all'.
        """
        
        self.items.infer_countries(language = language)

    def infer_cities(self, language = 'all'):
        
        """
        Identifies city names from items' text data and appends to information sets. Uses list of all city names by default. Parses data if not parsed.
        
        Parameters
        ----------
        language : str or list
            language of city names corpus to use; or city names corpus as list. Defaults to 'all'.
        """
        
        self.items.infer_cities(language = language)
    
    def infer_languages(self, language = 'all'):
        
        """
        Identifies language names from items' text data and appends to information sets. Uses list of all language names by default. Parses data if not parsed.
        
        Parameters
        ----------
        language : str or list
            language of language names corpus to use; or language names corpus as list. Defaults to 'all'.
        """
        
        self.items.infer_languages(language = language)
    
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
        
        self.items.infer_all_info_categories(names = names, language = language)
        
    # Methods for inferring additional metadata from existing metadata
    
    def infer_locations_from_coordinates(self):
        
        """
        Identifies locations associated with coordinates metadata using Geopy. Appends to 'location' metadata category.
        """
        
        self.dataframes.infer_locations_from_coordinates()
        self.dataframes.update_properties()
        self.update_properties()

    def infer_coordinates_from_locations(self):
        
        """
        Identifies coordinates associated with locations metadata using Geopy. Appends to 'coordinates' metadata category.
        """
        
        self.dataframes.infer_coordinates_from_locations()
        self.dataframes.update_properties()
        self.update_properties()

    def infer_coordinates_from_ip_addresses(self):
        
        """
        Identifies coordinates associated with IP address metadata using Geopy. Appends to 'coordinates' metadata category.
        """
        
        self.dataframes.infer_coordinates_from_ip_addresses()
        self.dataframes.update_properties()
        self.update_properties()
            
    def infer_locations_from_ip_addresses(self):
        
        """
        Identifies locations associated with IP address metadata using Geopy. Appends to 'location' metadata category.
        """
        
        self.dataframes.infer_locations_from_ip_addresses()
        self.dataframes.update_properties()
        self.update_properties()
    
    def infer_internet_metadata(self, domains = True, ip_addresses = True):
        
        """
        Identifies additional internet metadata from existing internet metadata using WhoIs results. Appends to metadata dataframe.
        """
        
        self.dataframes.infer_internet_metadata(domains = domains, ip_addresses = ip_addresses)
        self.dataframes.update_properties()
        self.update_properties()
    
    def infer_geolocation_metadata(self, coordinates = True, locations = True, regions = True):
        
        """
        Identifies additional geolocation metadata from existing geolocation metadata using Geopy. Appends to metadata dataframe.
        """
        
        return self.dataframes.infer_geolocation_metadata(coordinates = coordinates, locations = coordinates, regions = regions)
    

    # Methods for analysing geolocation metadata
    
    def coordinates_metadata_distance(self, first_item = 'request_input', second_item = 'request_input', units = 'kilometers'):
        
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
        
        return self.items.coordinates_distance(first_item, second_item, units = units)
    
    def locations_metadata_distance(self, first_item = 'request_input', second_item = 'request_input', units = 'kilometers'):
        
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
        
        return self.items.locations_distance(first_item = first_item, second_item = second_item, units = units)
    
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
        
        return self.items.normalised_time_metadata_difference(first_item = first_item, second_item = second_item, time_metadata = time_metadata, units = units)
    
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
        
        return self.items.normalised_time_metadata_similarity(first_item = first_item, second_item = second_item, time_metadata = time_metadata, units = units)
    
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
        
        return self.items.normalised_coordinates_metadata_diffference(first_item = first_item, second_item = second_item, units = units)
    
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
        
        return self.items.normalised_coordinates_metadata_similarity(first_item = first_item, second_item = second_item, units = units)
    
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
        
        return self.items.normalised_location_metadata_difference(first_item = first_item, second_item = second_item, units = units)
    
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
            * Normalisation function: map_inf_to_1()
        """
        
        return self.items.normalised_location_metadata_similarity(first_item = first_item, second_item = second_item, units = units)
    

    # Methods for comparing case items to other items and/or the entire case
    
    def item_vs_other_metadata_comparison(self, item_id = 'request_input'):
        
        """
        Compares an item's metadata against all other combinations of items. Returns a dataframe.
        """
        
        if item_id == 'request_input':
            item_id = input('Item ID: ')

        df = self.all_items_metadata_comparisons()
        df_a = df[df['First item'] == item_id]
        df_b = df[df['Second item'] == item_id]
        df = pd.concat([df_a, df_b])

        return df
    
    
    def item_case_metadata_intersect(self, item_id = 'request_input'):
        
        """
        Returns the intersect between an item's metadata and the set derived from the rest of the Case.
        """
        
        if item_id == 'request_input':
            item_id = input('Item ID: ')

        df = self.dataframes.metadata
        comparison_list = list(df[df.index != item_id].index)

        other_items_set = set()
        for item in comparison_list:
            item_set = self.items.get_item(item).get_metadata_set()
            other_items_set = other_items_set.union(item_set)

        return self.get_item(item_id).get_metadata_set().intersection(other_items_set)
    
    
    def item_case_metadata_intersect_size(self, item_id = 'request_input'):
        
        """
        Returns the size of the intersect between an item's metadata set and the set derived from the rest of the Case.
        """
        
        return len(self.item_case_metadata_intersect(item_id = item_id))
    
    
    def item_case_metadata_difference(self, item_id = 'request_input'):
        
        """
        Returns the difference between an item's metadata set and the set derived from the rest of the Case.
        """
        
        if item_id == 'request_input':
            item_id = input('Item ID: ')

        df = self.dataframes.metadata
        comparison_list = list(df[df.index != item_id].index)

        other_items_set = set()
        for item in comparison_list:
            item_set = self.items.get_item(item).get_metadata_set()
            other_items_set = other_items_set.union(item_set)

        return self.get_item(item_id).get_metadata_set().difference(other_items_set)
    
    
    def item_case_metadata_difference_size(self, item_id = 'request_input'):
        
        """
        Returns the size of the difference between an item's metadata set and the set derived from the rest of the Case.
        """
        
        return len(self.item_case_metadata_difference(item_id = item_id))
    
    
    def item_case_metadata_similarity(self, item_id = 'request_input'):
        
        """
        Returns the Jaccard similarity between an item's metadata set and the set derived from the rest of the Case.
        """
        
        if item_id == 'request_input':
            item_id = input('Item ID: ')
    
        intersect_size = self.item_case_metadata_intersect_size(item_id)
        union_size = len(self.get_metadata_set())
        metadata_similarity = intersect_size / union_size

        return metadata_similarity
    
    
    def items_vs_case_metadata_comparisons(self):
        
        """
        Returns a dataframe of statistics comparing an item's metadata and the rest of the Case.
        """
        
        output_df = pd.DataFrame(columns = ['Shared', 'Shared size', 'Not shared', 'Not shared size', 'Similarity'])
        
        items = self.items.ids()
        
        for item_id in items:
            shared = self.item_case_metadata_intersect(item_id = item_id)
            shared_size = len(shared)
            not_shared = self.item_case_metadata_difference(item_id = item_id)
            not_shared_size = len(not_shared)
            similarity = self.item_case_metadata_similarity(item_id = item_id)
            output_df.loc[item_id] = [shared, shared_size, not_shared, not_shared_size, similarity]
        
        return output_df.sort_values('Similarity', ascending=False)
    
        
    def item_vs_other_info_comparison(self, item_id = 'request_input'):
            
        """
        Compares an item's information against all other combinations of items. Returns a dataframe.
        """
        
        if item_id == 'request_input':
            item_id = input('Item ID: ')

        df = self.all_items_info_comparisons()
        df_a = df[df['First item'] == item_id]
        df_b = df[df['Second item'] == item_id]
        df = pd.concat([df_a, df_b])

        return df
    
    
    def item_case_info_intersect(self, item_id = 'request_input'):
        
        """
        Returns the intersect between an item's information and the set derived from the rest of the Case.
        """
        
        if item_id == 'request_input':
            item_id = input('Item ID: ')

        df = self.dataframes.information
        comparison_list = list(df[df.index != item_id].index)

        other_items_set = set()
        for item in comparison_list:
            item_set = self.items.get_item(item).get_info_set()
            other_items_set = other_items_set.union(item_set)

        return self.get_item(item_id).get_info_set().intersection(other_items_set)
    
    
    def item_case_info_intersect_size(self, item_id = 'request_input'):
        
        """
        Returns the size of the intersect between an item's information set and the set derived from the rest of the Case.
        """
        
        return len(self.item_case_info_intersect(item_id = item_id))
    
    
    def item_case_info_difference(self, item_id = 'request_input'):
        
        """
        Returns the difference between an item's information set and the set derived from the rest of the Case.
        """
        
        if item_id == 'request_input':
            item_id = input('Item ID: ')

        df = self.dataframes.information
        comparison_list = list(df[df.index != item_id].index)

        other_items_set = set()
        for item in comparison_list:
            item_set = self.items.get_item(item).get_info_set()
            other_items_set = other_items_set.union(item_set)

        return self.get_item(item_id).get_info_set().difference(other_items_set)
    
    
    def item_case_info_difference_size(self, item_id = 'request_input'):
        
        """
        Returns the size of the difference between an item's information set and the set derived from the rest of the Case.
        """
        
        return len(self.item_case_info_difference(item_id = item_id))
    
    
    def item_case_info_similarity(self, item_id = 'request_input'):
        
        """
        Returns the Jaccard similarity between an item's information set and the set derived from the rest of the Case.
        """
        
        if item_id == 'request_input':
            item_id = input('Item ID: ')
    
        intersect_size = self.item_case_info_intersect_size(item_id)
        union_size = len(self.get_info_set())
        info_similarity = intersect_size / union_size

        return info_similarity
    
    
    def items_vs_case_info_comparisons(self):
        
        """
        Returns a dataframe of statistics comparing an item's information and the rest of the Case.
        """
        
        output_df = pd.DataFrame(columns = ['Shared', 'Shared size', 'Not shared', 'Not shared size', 'Similarity'])
        
        items = self.items.ids()
        
        for item_id in items:
            shared = self.item_case_info_intersect(item_id = item_id)
            shared_size = len(shared)
            not_shared = self.item_case_info_difference(item_id = item_id)
            not_shared_size = len(not_shared)
            similarity = self.item_case_info_similarity(item_id = item_id)
            output_df.loc[item_id] = [shared, shared_size, not_shared, not_shared_size, similarity]
        
        return output_df.sort_values('Similarity', ascending=False)

    

    # Methods for filtering and triangulating items based on their data
    
    def items_time_diff_from_date(self, select_by = 'created_at', date = 'request_input', within = 100, units = 'days', ignore_nones = True):
        
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
        
        return self.items.time_diff_from_date(select_by = select_by, date = date, within = within, units = units, ignore_nones = ignore_nones)
    
    def filter_items_by_distance(self, select_by = 'coordinates', close_to = 'request_input', within = 100, units = 'kilometers', ignore_nones = True):
        
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
        
        return self.items.filter_by_distance(select_by = select_by, close_to = close_to, within = within, units = units, ignore_nones = ignore_nones)
    
    def triangulate_items_by_distance(self, locations, select_by = 'coordinates', within = 100, units = 'kilometers', ignore_nones = True):
        
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
        
        return self.items.triangulate_by_distance(locations, select_by = select_by, within = within, units = units, ignore_nones = ignore_nones)
    
    def filter_items_by_dates(self, select_by = 'Created at', from_date = 'request_input', to_date = 'request_input', ignore_nones = True):
        
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
        
        return self.items.filter_by_dates(select_by = select_by, from_date = from_date, to_date = to_date, ignore_nones = ignore_nones)

    def metadata_time_diffs_from_date(self, select_by = 'created_at', date = 'request_input', within = 100, units = 'days', ignore_nones = True):
        
        """
        Returns the time differences between items' time metadata from a given date or time.
        
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
        time_difference : datetime.timedelta
            the time difference between items' time metadata entries and datetime.
        """
        
        return self.dataframes.metadata_time_diffs_from_date(select_by = select_by, date = date, within = within, units = units, ignore_nones = ignore_nones)

    def filter_metadata_by_distances(self, select_by = 'coordinates', close_to = 'request_input', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters metadata dataframe by entries whose geolocation metadata falls within a distance of a given location. Returns a pandas.DataFrame.
        
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
        
        return self.dataframes.filter_metadata_by_distances(select_by = select_by, close_to = close_to, within = within, units = units, ignore_nones = ignore_nones)

    def filter_info_by_distance_metadata(self, select_by = 'coordinates', close_to = 'request_input', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters information dataframe by entries whose geolocation metadata falls within a distance of a given location. Returns a pandas.DataFrame.
        
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
        
        return self.dataframes.filter_info_by_distance_metadata(select_by = select_by, close_to = close_to, within = within, units = units, ignore_nones = ignore_nones)

    def filter_data_by_distance_metadata(self, select_by = 'coordinates', close_to = 'request_input', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters data dataframe by entries whose geolocation metadata falls within a distance of a given location. Returns a pandas.DataFrame.
        
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
        
        return self.dataframes.filter_data_by_distance_metadata(select_by = select_by, close_to = close_to, within = within, units = units, ignore_nones = ignore_nones)

    def filter_other_by_distance_metadata(self, select_by = 'coordinates', close_to = 'request_input', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters 'other' (links, references, and contents) dataframe by entries whose geolocation metadata falls within a distance of a given location. Returns a pandas.DataFrame.
        
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
        
        return self.dataframes.filter_other_by_distance_metadata(select_by = select_by, close_to = close_to, within = within, units = units, ignore_nones = ignore_nones)

    def filter_metadata_by_dates(self, select_by = 'created_at', from_date = 'request_input', to_date = 'request_input', ignore_nones = True):
        
        """
        Filters metadata dataframe for entries whose time metadata falls between two datetimes. Returns a pandas.DataFrame.
        
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
        
        return self.dataframes.filter_metadata_by_dates(select_by = select_by, from_date = from_date, to_date = to_date, ignore_nones = ignore_nones)
    
    def filter_data_by_metadata_dates(self, select_by = 'created_at', from_date = 'request_input', to_date = 'request_input', ignore_nones = True):
        
        """
        Filters data dataframe for entries whose time metadata falls between two datetimes. Returns a pandas.DataFrame.
        
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
        
        return self.dataframes.filter_data_by_metadata_dates(select_by = select_by, from_date = from_date, to_date = to_date, ignore_nones = ignore_nones)
    
    def filter_info_by_metadata_dates(self, select_by = 'created_at', from_date = 'request_input', to_date = 'request_input', ignore_nones = True):
        
        """
        Filters information dataframe for entries whose time metadata falls between two datetimes. Returns a pandas.DataFrame.
        
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
        
        return self.dataframes.filter_info_by_metadata_dates(select_by = select_by, from_date = from_date, to_date = to_date, ignore_nones = ignore_nones)
    
    def filter_other_by_metadata_dates(self, select_by = 'created_at', from_date = 'request_input', to_date = 'request_input', ignore_nones = True):
        
        """
        Filters 'other' (links, references, and contents) dataframe for entries whose time metadata falls between two datetimes. Returns a pandas.DataFrame.
        
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
        
        return self.dataframes.filter_other_by_metadata_dates(select_by = select_by, from_date = from_date, to_date = to_date, ignore_nones = ignore_nones)
    
    def triangulate_metadata_by_distances(self, locations, select_by = 'location', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters metadata dataframe by entries whose geolocation metadata falls within a distance of multiple given locations. Returns a pandas.DataFrame.
        
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
        
        return self.dataframes.triangulate_metadata_by_distances(locations, select_by = select_by, within = within, units = units, ignore_nones = ignore_nones)
    
    def triangulate_data_by_metadata_distances(self, locations, select_by = 'location', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters data dataframe by entries whose geolocation metadata falls within a distance of multiple given locations. Returns a pandas.DataFrame.
        
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
        
        return self.dataframes.triangulate_data_by_metadata_distances(locations, select_by = select_by, within = within, units = units, ignore_nones = ignore_nones)
    
    def triangulate_info_by_metadata_distances(self, locations, select_by = 'location', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters information dataframe by entries whose geolocation metadata falls within a distance of multiple given locations. Returns a pandas.DataFrame.
        
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
        
        return self.dataframes.triangulate_info_by_metadata_distances(locations, select_by = select_by, within = within, units = units, ignore_nones = ignore_nones)
    
    def triangulate_other_by_metadata_distances(self, locations, select_by = 'location', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters 'other' (links, references, and contents) dataframe by entries whose geolocation metadata falls within a distance of multiple given locations. Returns a pandas.DataFrame.
        
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
        
        return self.dataframes.triangulate_other_by_metadata_distances(locations, select_by = select_by, within = within, units = units, ignore_nones = ignore_nones)
    
    def filter_keywords_by_distance_metadata(self, measure = 'frequency', select_by = 'location', close_to = 'request_input', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters keywords dataframes by entries whose geolocation metadata falls within a distance of a given location. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        measure : str
            which keywords dataframe to use.
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
        
        return self.dataframes.filter_keywords_by_distance_metadata(measure = measure, select_by = select_by, close_to = close_to, within = within, units = units, ignore_nones = ignore_nones)
        
    def filter_keywords_by_metadata_dates(self, measure = 'frequency', select_by = 'created_at', from_date = 'request_input', to_date = 'request_input', ignore_nones = True):
        
        """
        Filters keywords dataframes for entries whose time metadata falls between two datetimes. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        measure : str
            which keywords dataframe to use.
        select_by : str
            category of time metadata to use. Defaults to 'Created at'
        from_date : str
            date or time to measure from. Defaults to requesting from user input.
        to_date : str
            date or time to measure to. Defaults to requesting from user input.
        ignore_nones : bool
            whether to ignore items without geolocation metadata entries. Defaults to True.
        """
        
        return self.dataframes.filter_keywords_by_metadata_dates(measure = measure, select_by = select_by, from_date = from_date, to_date = to_date, ignore_nones = ignore_nones)
        
    def triangulate_keywords_by_metadata_distances(self, locations, measure = 'frequency', select_by = 'location', close_to = 'request_input', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters keywords dataframes by entries whose geolocation metadata falls within a distance of multiple given locations. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        measure : str
            which keywords dataframe to use.
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
        
        return self.dataframes.triangulate_keywords_by_metadata_distances(locations = locations, measure = measure, select_by = select_by, close_to = close_to, within = within, units = units, ignore_nones = ignore_nones)
        

    # Methods for looking up item internet metadata
    
    def lookup_item_domain(self, item_id = 'request_input'):
        
        """
        Runs a WhoIs lookup on an item's domain metadata.
        """
        
        return self.items.lookup_item_domain(item_id)
    
    def lookup_all_item_domains(self):
        
        """
        Runs WhoIs lookups on all items' domain metadata.
        """
        
        return self.items.lookup_all_item_domains()
    
    def lookup_all_domain_metadata(self):
        
        """
        Runs WhoIs lookups on all domain metadata.
        """
        
        return self.dataframes.lookup_all_domain_metadata()
    
    def lookup_all_item_ip_metadata(self):
        
        """
        Runs WhoIs lookups on all items' IP address metadata.
        """
        
        return self.items.lookup_all_item_ip_metadata()
    
    def lookup_all_ip_metadata(self):
        
        """
        Runs WhoIs lookups on all IP address metadata.
        """
        
        return self.dataframes.lookup_all_ip_metadata()
    
    def lookup_all_items_whois(self, append_to_items = False):
        
        """
        Runs WhoIs lookups on all items' internet metadata.
        """
        
        return self.items.lookup_all_items_whois(append_to_items = append_to_items)
    
    def lookup_all_whois_metadata(self, append_to_dataset = False):
        
        """
        Runs WhoIs lookups on all internet metadata.
        
        Parameters
        ----------
        append_to_dataset : bool
            whether to add WhoIs results to the metadata dataframe.
        """
        
        return self.dataframes.lookup_all_whois_metadata(append_to_dataset = append_to_dataset)

    
    def scrape_item_urls(self, append_to_items = True):
        
        """
        Scrapes data from all items' URLs if available. Appends to items if selected.
        
        WARNING: this function is very slow due to the speed of the packages it relies on.
        
        Parameters
        ----------
        append_to_items : bool
            whether to append scraper results to items
        """
        
        return self.items.scrape_item_urls(append_to_items = append_to_items)
    
    
    def lookup_url(self, item_id = 'request_input'):
        
        """
        Opens an item's URL in the default web browser.
        """
        
        if item_id == 'request_input':
            item_id = input('Item ID: ')

        if item_id == 'all':
            for item in self.items.ids():
                self.items.get_item(item).lookup_url()
        
        elif item_id in self.items.ids():
            return self.items.get_item(item_id).lookup_url()
        

    # Methods for looking up and filtering items' links
    
    def lookup_item_links(self, item_id = 'request_input', link_index = 'all'):
        
        """
        Opens an item's links in the default web browser. Can specify a link index; defaults to opening all
        """
        
        if item_id == 'request_input':
            item_id = input('Item ID: ')
        
        if link_index == 'all':
            return self.items.get_item(item_id).open_all_links()
        
        else:
            return self.items.get_item(item_id).lookup_link(link_index = link_index)
        

    def open_all_links(self):
        
        """
        Opens all items' links in the default web browser.
        """
        
        return self.items.open_all_links()
            
    
    def filter_links(self, contains_any_kwds = None, contains_all_kwds = None, not_containing_any_kwds = None, not_containing_all_kwds = None):
        
        """
        Filters items' links based on given criteria. Returns a list.
        
        Parameters
        ----------
        contains_any_kwds : list
            results must contain any of these strings. Defaults to None.
        contains_all_kwds : list results
            must contain all of these strings. Defaults to None.
        not_containing_any_kwds : list
            results not must contain any of these strings. Defaults to None.
        not_containing_all_kwds : list
            results not must contain all of these strings. Defaults to None.
        """
        
        return self.items.filter_all_links(contains_any_kwds = contains_any_kwds, contains_all_kwds = contains_all_kwds, not_containing_any_kwds = not_containing_any_kwds, not_containing_all_kwds = not_containing_all_kwds)
      
        
    def lookup_all_filtered_links(self, contains_any_kwds = None, contains_all_kwds = None, not_containing_any_kwds = None, not_containing_all_kwds = None):
        
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
        
        return self.items.lookup_filtered_links(contains_any_kwds = contains_any_kwds, contains_all_kwds = contains_all_kwds, not_containing_any_kwds = not_containing_any_kwds, not_containing_all_kwds = not_containing_all_kwds)
        

    # Methods for running web crawls from case and items
    
    
    def crawl_web(self,
                    append_to_case = True,
                    seed_urls = 'request_input',
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
        Crawls internet from a single URL or list of URLs. Returns details like links found,  HTML scraped, and site metadata.

        Parameters
        ---------- 
        append_to_case : bool
            whether or not to append crawl results to the Case.
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
        output_as : str
            the format to output results in. Defaults to a pandas.DataFrame.


        Returns
        -------
        result : object
            an object containing the results of a crawl.
        """
        
        # Append_to_case not currently working.
        
        if append_to_case == True:
            
            items_from_web_crawl(case = self,
                        update_global_var = True,
                        seed_urls = seed_urls,
                        visit_limit = visit_limit, 
                        excluded_url_terms = excluded_url_terms,
                        required_keywords = required_keywords, 
                        excluded_keywords = excluded_keywords, 
                        case_sensitive = case_sensitive,
                        ignore_urls = ignore_urls, 
                        ignore_domains = ignore_domains,
                        be_polite = be_polite,
                        full = full)
            
            return
            
            
        
        if append_to_case == False:
            
            output = crawl_web(seed_urls = seed_urls,
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
        
    

    def crawl_web_from_items(self,
                            append_to_case = False,
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
                            output_as = 'dataframe'):
        
        """
        Runs web crawl from items' URL metadata.
        
        Parameters
        ---------- 
        append_to_case : bool
            whether or not to append crawl results to the Case.
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
        ids = self.items.ids()
        for item_id in ids:
            urls = list(self.items.get_item(item_id).get_metadata(crawl_from)['Metadata'].values)
            seed_urls = seed_urls + urls
        seed_urls = list(set(seed_urls))
        
        return self.crawl_web(append_to_case = append_to_case,
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
            
        
    def crawl_all_web_links(self,
                            append_to_case = False,
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
        append_to_case : bool
            whether or not to append crawl results to the Case.
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
        ids = self.items.ids()
        for item_id in ids:
            urls = self.items.get_item(item_id).links
            
            if type(urls) == str:
                urls = urls.strip().replace('[', '').replace(']', '').replace('"', '').replace("'", "")
                urls = urls.split(',')
            
            seed_urls = seed_urls + urls
            
        seed_urls = list(set(seed_urls))
        
        return self.crawl_web(
                    append_to_case = append_to_case,
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
    
    def add_instagram_user_posts(self, username = 'request_input'):
        
        """
        Retrieves an Instagram user's posts from a username and adds to the Case.
        
        Parameters
        ----------
        username : str
            username to retrieve from.
        """
        
        self.items.add_instagram_user_posts(username = username)
        self.sync_items()
    
    def items_from_username_search(self, username = 'request_input'):
        
        """
        Runs an Sherlock search on username and adds the results as CaseItems to the Case.
        
        Parameters
        ----------
        username : str
            username to retrieve from.
        """
        
        self.items.items_from_username_search(username = username)
        self.sync_items()
    
    # Methods for indexing case objects by the data they contain

    def index_by_info(self, by_labels = True, by_categories = True):
        
        """
        Indexes case dataset by information each piece of item contains. Returns a dataframe.
        """
        
        return self.items.index_by_info(by_labels = by_labels, by_categories = by_categories)
    
    def index_by_info_label(self):
        
        """
        Indexes items by information labels they contain. Returns a dataframe.
        """
        
        return self.items.index_by_info_label()
    
    def index_by_info_category(self):
        
        """
        Indexes items by information categories they contain. Returns a dataframe.
        """
        
        return self.items.index_by_info_category()
    
    def index_by_metadata(self, by_entries = True, by_categories = True):
        
        """
        Indexes items by each item's metadata. Returns a dataframe.
        """
        
        return self.items.index_by_metadata(by_entries = by_entries, by_categories = by_categories)
            
    def index_by_metadata_entry(self):
        
        """
        Indexes items by each item's metadata entries. Returns a dataframe.
        """
        
        return self.items.index_by_metadata_entry()
    
    def index_by_metadata_category(self):
        
        """
        Indexes items by each item's categories. Returns a dataframe.
        """
        
        return self.items.index_by_metadata_category()

    def index_by_words(self, word_limit = None):
        
        """
        Indexes case items by the words they contain. Returns a dataframe.
        """
        
        return self.items.index_by_words(word_limit = word_limit)
    
    def index_by_links(self):
        
        """
        Indexes items by their links. Returns a dataframe.
        """
        
        return self.items.index_by_links()
    
    def index_by_refs(self):
        
        """
        Indexes items by their references. Returns a dataframe.
        """
        
        return self.items.index_by_refs()
    
    def index_by_contents(self):
        
        """
        Indexes items by their contents. Returns a dataframe.
        """
        
        return self.items.index_by_contents()
    
    def index_metadata_by_info(self):
        
        """
        Indexes metadata entries by the information entries they co-occur with. Returns a dataframe.
        """
        
        if 'information and metadata' in self.dataframes.coinciding_data.keys():
            coincidence_df = self.dataframes.coinciding_data['information and metadata']

            info_set = set(coincidence_df['Information'])

            index_df = pd.DataFrame(columns = ['Information', 'Metadata', 'Metadata count'])
            for info in info_set:
                metadata_assoc = coincidence_df[coincidence_df['Information'] == info]['Metadata'].to_list()
                index = len(index_df.index)
                index_df.at[index, 'Information'] = info
                index_df.at[index, 'Metadata'] = metadata_assoc
                index_df.at[index, 'Metadata count'] = len(metadata_assoc)

            return index_df
    
    
    def index_info_by_metadata(self):
        
        """
        Indexes information entries by the metadata entries they co-occur with. Returns a dataframe.
        """
        
        if 'information and metadata' in self.dataframes.coinciding_data.keys():
            coincidence_df = self.dataframes.coinciding_data['information and metadata']

            metadata_set = set(coincidence_df['Metadata'])

            index_df = pd.DataFrame(columns = ['Metadata', 'Information', 'Information count'])
            for metadata in metadata_set:
                info_assoc = coincidence_df[coincidence_df['Metadata'] == metadata]['Metadata'].to_list()
                index = len(index_df.index)
                index_df.at[index, 'Metadata'] = metadata
                index_df.at[index, 'Information'] = info_assoc
                index_df.at[index, 'Information count'] = len(info_assoc)

            return index_df
    
    
    def generate_indexes(self):
        
        """
        Generates all indexes and assigns them to the Case's CaseIndexes attribute. Returns the updated CaseIndexes.
        
        Indexes generated:
            * items indexed by information entries
            * items indexed by metadata entries
            * items indexed by link entries
            * items indexed by references entries
            * items indexed by contents
            * items indexed by words
            * metadata indexed by co-occuring information entries
            * information indexed by co-occuring metadata entries
        """
        
        if len(self.dataframes.information.index) > 1:
            self.indexes.items_by_information = self.index_by_info()
        
        if len(self.dataframes.information.index) > 1:
            self.indexes.items_by_metadata = self.index_by_metadata()
        
        if len(self.dataframes.other.index) > 1:
            self.indexes.items_by_links = self.index_by_links()
            self.indexes.items_by_references = self.index_by_refs()
            self.indexes.items_by_contents = self.index_by_contents()
        
        if self.properties.parsed == True:
            self.indexes.items_by_words = self.index_by_words()
        
        if 'information and metadata' in self.dataframes.coinciding_data.keys():
            self.indexes.metadata_by_information = self.index_metadata_by_info()
            self.indexes.information_by_metadata = self.index_info_by_metadata()

        
        self.properties.indexed = True
        self.update_properties()
         # self.backup()
        
        return self.indexes
    
    

    # Methods for searching case objects and data
    
    def search_items(self, query = 'request_input'):
        
        """
        Searches for an item ID. If found, returns that item's contents.
        """
        
        return self.items.search_items(query = query)
    
    def search_keywords(self, query = 'request_input', keyword_type = 'most_frequent'):
        
        """
        Searches keywords for a string. If found, returns all matches.
        """
        
        return self.dataframes.search_keywords(query = query, keyword_type = keyword_type)
    
    def search(self, search_query = 'request_input'):
        
        """
        Searches items for a query string. If found, returns a dataframe of all items containing the string.
        """
        
        return self.items.search(search_query = search_query)
    
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
        
        return self.items.advanced_search(any_kwds = any_kwds, all_kwds = all_kwds, no_kwds = no_kwds, search_in = search_in)
        
    

    # Methods for generating networks from case data 
    
    def items_to_vertices(self, directed_yn='undirected', append_to_case = True):
        
        """
        Creates a disconnected network where each vertex represents an item with attributes containing the item's data.
        
        Parameters
        ----------
        directed_yn : str
            direction for network edges. Options: 'undirected' or 'directed'.
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        """
        
        # Initialising network
        direction = (directed_yn == 'directed')
        items = pd.Series(self.items.ids()).sort_values().to_list()
        item_count = len(items)
        network = CaseNetwork(n=item_count, directed=direction, vertex_attrs={'name':items})
        network['item_ids'] = items
        network.vs['type'] = 'item'

        # Retrieving vertex attributes
        for vertex in network.vs():
            
            item_id = vertex['name']
            
            metadata = self.items.get_item(item_id).metadata.copy(deep=True)
            data = self.items.get_item(item_id).data.copy(deep=True)
            info = self.items.get_item(item_id).information.copy(deep=True)
            
            whois = self.items.get_item(item_id).whois
            if type(whois) == pd.DataFrame:
                whois = whois.copy(deep=True)
                whois = whois.astype(str)
                
            user_assessments = self.items.get_item(item_id).user_assessments
            if type(user_assessments) == pd.DataFrame:
                user_assessments = user_assessments.copy(deep=True)
                user_assessments = user_assessments.astype(str)
            
            vertex['metadata'] = metadata.astype(str)
            vertex['data'] = data.astype(str)
            vertex['information'] = info.astype(str)
            vertex['whois'] = whois
            vertex['links'] = self.items.get_item(item_id).links
            vertex['references'] = self.items.get_item(item_id).references
            vertex['contains'] = self.items.get_item(item_id).contains
            vertex['user_assessments'] = user_assessments
            vertex['address'] = self.items.get_item(item_id).get_address()
            vertex['url'] = self.items.get_item(item_id).get_url()

        if append_to_case == True:
            self.networks.disconnected_items_network = network
            self.networks.update_properties()
            self.update_properties()
            return
        
        else:
            return network

        
    def items_to_full_network(self, directed_yn='undirected', append_to_case = True):
        
        """
        Creates a fully connected network where each vertex represents an item with attributes containing the item's data.
        
        Parameters
        ----------
        directed_yn : str
            direction for network edges. Options: 'undirected' or 'directed'.
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        """
        
        # Initialising network
        direction = (directed_yn == 'directed')
        items = pd.Series(self.items.ids()).sort_values().to_list()
        item_count = len(items)
        full_network = CaseNetwork.Full(n=item_count, directed=direction, loops=False)
        full_network['item_ids'] = items

        # Retrieving vertex attributes
        full_network.vs['name'] = items
        full_network.vs['type'] = 'item'

        for vertex in full_network.vs():
            
            item_id = vertex['name']
            
            metadata = self.items.get_item(item_id).metadata.copy(deep=True)
            data = self.items.get_item(item_id).data.copy(deep=True)
            info = self.items.get_item(item_id).information.copy(deep=True)
            
            whois = self.items.get_item(item_id).whois
            if type(whois) == pd.DataFrame:
                whois = whois.copy(deep=True)
                whois = whois.astype(str)
                
            user_assessments = self.items.get_item(item_id).user_assessments
            if type(user_assessments) == pd.DataFrame:
                user_assessments = user_assessments.copy(deep=True)
                user_assessments = user_assessments.astype(str)
            
            vertex['metadata'] = metadata.astype(str)
            vertex['data'] = data.astype(str)
            vertex['information'] = info.astype(str)
            vertex['whois'] = whois
            vertex['links'] = self.items.get_item(item_id).links
            vertex['references'] = self.items.get_item(item_id).references
            vertex['contains'] = self.items.get_item(item_id).contains
            vertex['user_assessments'] = user_assessments
            vertex['address'] = self.items.get_item(item_id).get_address()
            vertex['url'] = self.items.get_item(item_id).get_url()

        if append_to_case == True:
            self.networks.full_items_network = full_network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return full_network

    
    def keywords_to_vertices(self, directed_yn='undirected', append_to_case = True):
        
        """
        Creates a disconnected network where each vertex represents a word in the case's dataset.
        
        Vertices have a 'frequency' attribute representing the number of times that word appears in the case set and a 'frequency_per_item' attribute representing the number of times it appears in item entries, on average.
        
        Parameters
        ----------
        directed_yn : str
            direction for network edges. Options: 'undirected' or 'directed'.
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        """

        # Initialising network
        direction = (directed_yn == 'directed')

        if self.properties.keywords_generated == False:
            self.generate_keywords()

        if self.properties.keywords_generated == True:
            df = self.dataframes.keywords.frequent_words.sort_index()

            if len(df.index) == 0:
                df = self.get_word_frequencies(clean = True).sort_index()

        word_set = df.index.to_list()
        network = CaseNetwork(n = len(word_set), directed = direction)
        network['all_keywords'] = df

        # Retrieving vertex attributes
        network.vs['name'] = word_set
        network.vs['type'] = 'word'
        network.vs['frequency'] = df['frequency'].to_list()
        network.vs['found_in'] = df['found_in'].to_list()
        network.vs['found_in_count'] = df['found_in_count'].to_list()
        network.vs['frequency_per_item'] = df['frequency_per_item'].to_list()
        network.vs['breakdown'] = df['breakdown'].to_list()

        if append_to_case == True:
            self.networks.disconnected_words_network = network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return network
    
    
    def keywords_to_full_network(self, directed_yn='undirected', append_to_case = True):
        
        """
        Creates a fully connected network where each vertex represents a keyword in the case's dataset.
        
        Vertices have a 'frequency' attribute representing the number of times that word appears in the case set and a 'frequency_per_item' attribute representing the number of times it appears in item entries, on average.
        
        Parameters
        ----------
        directed_yn : str
            direction for network edges. Options: 'undirected' or 'directed'.
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        """
        
        # Initialising network
        direction = (directed_yn == 'directed')

        if self.properties.keywords_generated == False:
            self.generate_keywords()

        if self.properties.keywords_generated == True:
            df = self.dataframes.keywords.frequent_words.sort_index()

            if len(df.index) == 0:
                df = self.get_word_frequencies(clean = True).sort_index()

        word_set = df.index.to_list()
        network = CaseNetwork.Full(n=len(word_set), directed=direction, loops=False)
        network['all_keywords'] = df

        # Retrieving vertex attributes
        network.vs['name'] = word_set
        network.vs['type'] = 'word'
        network.vs['frequency'] = df['frequency'].to_list()
        network.vs['found_in'] = df['found_in'].to_list()
        network.vs['found_in_count'] = df['found_in_count'].to_list()
        network.vs['frequency_per_item'] = df['frequency_per_item'].to_list()
        network.vs['breakdown'] = df['breakdown'].to_list()

        if append_to_case == True:
            self.networks.full_words_network = network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return network
    
    
    def info_to_vertices(self, directed_yn='undirected', append_to_case = True):
        
        """
        Creates a disconnected network where each vertex represents a piece of information in the case's total information set. 
        
        Vertices have a 'count' attribute representing the number of times that information appears in the item set.
        
        Parameters
        ----------
        directed_yn : str
            direction for network edges. Options: 'undirected' or 'directed'.
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        """

        # Initialising network
        direction = (directed_yn == 'directed')
        df = self.get_all_info().copy(deep=True)
        df = df.astype(str)
        df['Information'] = 'Label: ' + df['Label'] + ', Category: ' + df['Category']
        df = df.drop(['Label', 'Category'], axis=1)
        freqs = df.value_counts('Information')
        info_set = set(df['Information'])

        network = CaseNetwork(n = len(info_set), directed = direction)
        network['all_information'] = df
        
        # Retrieving vertex attributes
        network.vs['name'] = list(info_set)
        network.vs['type'] = 'information'

        for vertex in network.vs():
            vertex['count'] = int(freqs[vertex['name']])

        if append_to_case == True:
            self.networks.disconnected_info_network = network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return network

    def info_to_full_network(self, directed_yn = 'undirected', append_to_case = True):
        
        """
        Creates a fully connected network where each vertex represents a piece of information in the case's total information set. 
        
        Vertices have a 'count' attribute representing the number of times that information appears in the item set.
        
        Parameters
        ----------
        directed_yn : str
            direction for network edges. Options: 'undirected' or 'directed'.
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        """
        
        # Initialising network
        direction = (directed_yn == 'directed')
        df = self.get_all_info().copy(deep=True)
        df = df.astype(str)
        df['Information'] = 'Label: ' + df['Label'] + ', Category: ' + df['Category']
        df = df.drop(['Label', 'Category'], axis=1)
        freqs = df.value_counts('Information')
        info_set = set(df['Information'])

        full_network = CaseNetwork.Full(n = len(info_set), directed = direction, loops = False)
        full_network['all_information'] = df
        
        # Retrieving vertex attributes
        full_network.vs['name'] = list(info_set)
        full_network.vs['type'] = 'information'

        for vertex in full_network.vs():
            vertex['count'] = int(freqs[vertex['name']])

        if append_to_case == True:
            self.networks.full_info_network = full_network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return full_network

    
    def metadata_to_vertices(self, directed_yn='undirected', append_to_case = True):
        
        """
        Creates a disconnected network where each vertex represents a piece of metadata in the case's total metadata set.
        
        Vertices have a 'count' attribute representing the number of times that metadata appears in the item set.
        
        Parameters
        ----------
        directed_yn : str
            direction for network edges. Options: 'undirected' or 'directed'.
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        """
        
        # Initialising network
        direction = (directed_yn == 'directed')

        df = self.get_all_metadata().copy(deep=True)
        df = df.astype(str)
        df['result'] = df['Category'] + ': ' + df['Metadata']
        df = df.drop(['Category', 'Metadata'], axis=1)
        freqs = df.value_counts('result')
        metadata_set = list(freqs.index)
        size = len(metadata_set)
        network = CaseNetwork(n=size, directed=direction)
        network['all_metadata'] = df

        # Retrieving vertex attributes
        network.vs['name'] = metadata_set
        network.vs['type'] = 'metadata'
        
        for vertex in network.vs():
            vertex['count'] = int(freqs[vertex['name']])

        if append_to_case == True:
            self.networks.disconnected_metadata_network = network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return network

    def metadata_to_full_network(self, directed_yn = 'undirected', append_to_case = True):
            
            """
            Creates a fully connected network where each vertex represents a piece of metadata in the case's total metadata set.

            Vertices have a 'count' attribute representing the number of times that metadata appears in the item set.
            
            Parameters
            ----------
            directed_yn : str
                direction for network edges. Options: 'undirected' or 'directed'.
            append_to_case : bool
                whether to add the network to the Case's CaseNetworks collection.
            """
            
            direction = (directed_yn == 'directed')

            # Initialising network
            df = self.get_all_metadata().copy(deep=True)
            df = df.astype(str)
            df['result'] = df['Category'] + ': ' + df['Metadata']
            df = df.drop(['Category', 'Metadata'], axis=1)
            freqs = df.value_counts('result')
            metadata_set = list(freqs.index)
            size = len(metadata_set)

            full_network = CaseNetwork.Full(n = size, directed = direction, loops = False)
            full_network['all_metadata'] = df

            # Retrieving vertex attributes
            full_network.vs['name'] = list(metadata_set)
            full_network.vs['type'] = 'metadata'

            for vertex in full_network.vs():
                vertex['count'] = int(freqs[vertex['name']])

            if append_to_case == True:
                self.networks.full_metadata_network = full_network
                self.networks.update_properties()
                self.update_properties()
                return

            else:
                return full_network
    
    
    
    
    def generate_links_network(self, append_to_case = True):
        
        """
        Returns a directed network representing if/how items embed hyperlinks to one another.
        
        Parameters
        ----------
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        """

            # Initialising network
        links_network = self.items_to_vertices(directed_yn='directed', append_to_case = False)

        # Retrieving data
        url_addrs_dict = self.get_urls_metadata_dict()
        urls_items_dict = dict([tuple((i[1], i[0])) for i in url_addrs_dict.items()])
        links_dict = self.get_links_dict()


        # Adding edges
        for vertex in links_network.vs:

            v_name = vertex['name']
            v_index = vertex.index
            v_url = url_addrs_dict[v_name]
            v_links = links_dict[v_name]

            if (v_links != None) and ((type(v_links) == list) or (type(v_links) == set)):
                for link in v_links:
                    if link in urls_items_dict.keys():
                        end_name = urls_items_dict[link]
                        end_index = links_network.vs.find(name = end_name).index
                        CaseNetwork.add_edges(links_network, 
                                        [(v_index, end_index)], 
                                        attributes={
                                           'link': f'{v_name} -> {end_name}'})
                    
        if append_to_case == True:
            self.networks.items_links = links_network
            return

        else:
            return links_network 
    

    def generate_refs_network(self, append_to_case = True):
        
        """
        Returns a directed network representing how item entries reference one another.
        
        Parameters
        ----------
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        """
        
        # Initialising network
        refs_network = self.items_to_vertices(directed_yn='directed', append_to_case = False)
        other_df = self.dataframes.other
        refs_network['all_references'] = other_df.astype(str)
        
        # Adding edges
        for vertex in refs_network.vs:
            if vertex['references'] != None:
                for ref in vertex['references']:
                    if ref in refs_network.vs['name']:
                        end_index = refs_network.vs.find(name = ref)
                        CaseNetwork.add_edges(refs_network, 
                                    [(vertex, end_index)], 
                                    attributes={
                                           'reference': 'to '+ref})
        if append_to_case == True:
            self.networks.items_references = refs_network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return refs_network


    def generate_contents_network(self, append_to_case = True):
        
        """
        Returns a directed network representing how item entries contain one another.
        
        Parameters
        ----------
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        """
        
        # Initialising network
        contains_network = self.items_to_vertices(directed_yn='directed', append_to_case = False)
        other_df = self.dataframes.other
        contains_network['all_references'] = other_df.astype(str)
        
        # Adding edges for each vertex's set of conents.
        for vertex in contains_network.vs:
            if vertex['contains'] != None:
                for item in vertex['contains']:
        #             item = [item]

                    # Checking if item matches an  item. If one is found, an edge is created between the two vertices.
                    if item in contains_network.vs['name']:
                        end_index = contains_network.vs.find(name = item)
                        CaseNetwork.add_edges(contains_network, 
                                    [(vertex, end_index)], 
                                    attributes={
                                           'structure': 'contains '+item})

        if append_to_case == True:
            self.networks.items_contents = contains_network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return contains_network
        
    
    def generate_urls_network(self, append_to_case = True):
        
        """
        Returns a directed network representing if/how items' URLs embed hyperlinks to other URLs.
        
        Parameters
        ----------
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        """
        
        urls_dict = {}

        for i in self.items.ids():
            item = self.items.get_item(i)
            url = item.get_url()
            urls_dict[url] = item.links
        
        urls_network = generate_urls_network(urls_dict)
        urls_network = CaseNetwork(urls_network)
        
        if append_to_case == True:
            self.networks.urls_network = urls_network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return urls_network
        
        
    def generate_items_words_shared_network(self, append_to_case = True):
        
        """
        Returns an undirected network representing whether items share words. Item pairs with no shared words do not share edges.
        
        Parameters
        ----------
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        
        Notes
        -----
        Network details:
            * vertices: items.
            * edges: instances where two items share 1 or more words. 
            * edge weghts: number of words shared.
        """
        
        # Initialising network
        if 'full_items_network' not in self.networks.contents():
            self.items_to_full_network(directed_yn='undirected', append_to_case = True)

#         words_shared_network = copy.deepcopy(self.networks.full_items_network)
        words_shared_network = self.networks.full_items_network

        df = self.all_items_words_comparisons().copy(deep=True)
        df = df.sort_values('First item')
        words_shared_network['all_keyword_comparisons'] = df
#         df = df[df['Intersect size'] > 0]

        # Adding attributes to edges
        for row in list(df.index):
            
            item_1 = df.iloc[row, 0]
            item_2 = df.iloc[row, 1]
            start_vertex = words_shared_network.vs.find(name = item_1).index
            end_vertex = words_shared_network.vs.find(name = item_2).index
            edge_id = words_shared_network.get_eid(start_vertex, end_vertex)

            words_shared_network.es[edge_id]['name'] = item_1 + ' ∩ ' + item_2
            words_shared_network.es[edge_id]['weight'] = df.loc[row, 'Intersect size']
            words_shared_network.es[edge_id]['shared_words'] = df.loc[row, 'Intersect']
            words_shared_network.es[edge_id]['set_similarity'] = df.loc[row, 'Set similarity']
            words_shared_network.es[edge_id]['cosine'] = df.loc[row, 'Cosine similarity']
            words_shared_network.es[edge_id]['levenshtein'] = df.loc[row, 'Levenshtein distance']


        # Deleting redundant edges
        to_del = words_shared_network.es.select(lambda x: (x["weight"]==0) or (math.isnan(x["weight"]) == True) or (x["weight"]=="N/A") or (x["name"]=="N/A"))
        CaseNetwork.delete_edges(words_shared_network, to_del)

        if append_to_case == True:
            self.networks.items_words_shared = words_shared_network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return words_shared_network


    def generate_keywords_coincidence_network(self, limit = 600, append_to_case = True):
        
        """
        Returns an undirected network representing whether keywords coincide in items.
        
        Parameters
        ----------
        limit : int
            the number of keywords used to check coincidences. Uses the top n most frequent keywords (where n=limit).
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        
        Notes
        -----
        Network details:
            * vertices: keywords.
            * edges: instances where two keywords appear together in 1 or more items.
            * edge weghts: number of co-occurences.
        """
        
        # Initialising network
        words_co_network = self.keywords_to_vertices(directed_yn='undirected', append_to_case = False)

        if self.properties.coincidences_identified == False:
            self.identify_coincidences()

        df = self.dataframes.coinciding_data['words'].copy(deep=True)
        words_co_network['keyword_coincidences'] = df
        
        if (type(df) == None) or (len(df.index) == 0):
            if self.properties.parsed == False:
                self.parse_rawdata()

            df = self.word_coincidence(ignore_nones = True, limit = limit)
        
        df = df[df['Frequency'] > 0]

        for row in list(df.index):
            item_1 = df.iloc[row, 0]
            item_2 = df.iloc[row, 1]

            name = item_1 + ' & ' + item_2
            freq = df.iloc[row, 3]
            coincide_in = df.iloc[row, 2]

            start_vertex = words_co_network.vs.find(name = item_1).index
            end_vertex = words_co_network.vs.find(name = item_2).index

            CaseNetwork.add_edges(words_co_network, [(start_vertex, end_vertex)], attributes = {'name': name, 'weight': freq, 'coincide_in': coincide_in})

       # Deleting redundant edges
#         to_del = words_co_network.es.select(lambda x: (x["weight"]==0) or (math.isnan(x["weight"]) == True) or (x["weight"]=="N/A") or (x["name"]=="N/A"))
#         CaseNetwork.delete_edges(words_co_network, to_del)

        if append_to_case == True:
            self.networks.coinciding_words = words_co_network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return words_co_network

        
    def generate_items_words_similarity_network(self, weight_by = 'Cosine similarity', append_to_case = True):
        
        """
        Returns an undirected network representing the similarity between items' keywords.
        
        Parameters
        ----------
        weight_by : str
            the text similarity measure to weight by.  Defaults to 'Cosine similarity'.
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        
        Notes
        -----
        Network details:
            * vertices: items.
            * edges: paired comparisons. 
            * edge weghts: a text similarity measure. Defaults to 'Cosine similarity'.
        """
        
        # Initialising network
        if 'full_items_network' not in self.networks.contents():
            self.items_to_full_network(directed_yn='undirected', append_to_case = True)

        words_sim_network = copy.deepcopy(self.networks.full_items_network)

        df = self.all_items_words_comparisons().copy(deep=True)
        df = df.sort_values('First item')
        df = df.replace('N/A', np.nan)
        words_sim_network['all_keywords_comparisons'] = df

        # Adding attributes to edges
        for row in list(df.index):
            
            try:
                item_1 = df.iloc[row, 0]
                item_2 = df.iloc[row, 1]
                start_vertex = words_sim_network.vs.find(name = item_1).index
                end_vertex = words_sim_network.vs.find(name = item_2).index
                edge_id = words_sim_network.get_eid(start_vertex, end_vertex)

                words_sim_network.es[edge_id]['name'] = item_1 + ' ~ ' + item_2
                words_sim_network.es[edge_id]['weight'] = df.loc[row, weight_by]
                words_sim_network.es[edge_id]['shared_words'] = df.loc[row, 'Intersect']
                words_sim_network.es[edge_id]['shared_words_size'] = df.loc[row, 'Intersect size']
                words_sim_network.es[edge_id]['set_similarity'] = df.loc[row, 'Set similarity']
                words_sim_network.es[edge_id]['cosine'] = df.loc[row, 'Cosine similarity']
                words_sim_network.es[edge_id]['levenshtein'] = df.loc[row, 'Levenshtein distance']
            
            except:
                pass

        # Deleting redundant edges
        to_del = words_sim_network.es.select(lambda x: (x["weight"]==0) or (math.isnan(x["weight"]) == True) or (x["weight"]=="N/A") or (x["name"]=="N/A"))
        CaseNetwork.delete_edges(words_sim_network, to_del)

        if append_to_case == True:
            self.networks.items_words_similarity = words_sim_network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return words_sim_network


    def generate_items_info_shared_network(self, append_to_case = True):
        
        """
        Returns an undirected network representing whether items share information entries. Item pairs with no shared entries do not share edges.
        
        Parameters
        ----------
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        
        Notes
        -----
        Network details:
            * vertices: items.
            * edges: instances where two items share 1 or more information entries. 
            * edge weghts: number of information entries shared.
        """

        # Initialising network
        if 'full_items_network' not in self.networks.contents():
            self.items_to_full_network(directed_yn='undirected', append_to_case = True)

        info_shared_network = copy.deepcopy(self.networks.full_items_network)

        df = self.all_items_info_comparisons().copy(deep=True)
        df = df.sort_values('First item').reset_index().drop('index', axis=1)
        info_shared_network['all_information_comparisons'] = df
#         df = df[df['Intersect size'] > 0]

        # Adding attributes to edges
        for row in list(df.index):
            
            try:
                item_1 = df.iloc[row, 0]
                item_2 = df.iloc[row, 1]
                start_vertex = info_shared_network.vs.find(name = item_1).index
                end_vertex = info_shared_network.vs.find(name = item_2).index
                edge_id = info_shared_network.get_eid(start_vertex, end_vertex)

                info_shared_network.es[edge_id]['name'] = item_1 + ' ∩ ' + item_2
                info_shared_network.es[edge_id]['weight'] = df.loc[row, 'Intersect size']
                info_shared_network.es[edge_id]['shared_information'] = df.loc[row, 'Intersect']
                info_shared_network.es[edge_id]['set_similarity'] = df.loc[row, 'Set similarity']
                info_shared_network.es[edge_id]['cosine'] = df.loc[row, 'Cosine similarity']
                info_shared_network.es[edge_id]['mean_levenshtein'] = df.loc[row, 'Mean levenshtein distance']
            except:
                pass

        # Deleting redundant edges
        to_del = info_shared_network.es.select(lambda x: (x["weight"]==0) or (math.isnan(x["weight"]) == True) or (x["weight"]=="N/A") or (x["name"]=="N/A"))
        CaseNetwork.delete_edges(info_shared_network, to_del)

        if append_to_case == True:
            self.networks.items_information_shared = info_shared_network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return info_shared_network


    def generate_items_info_similarity_network(self, weight_by = 'Set similarity', append_to_case = True):
        
        """
        Returns an undirected network representing the similarity between items' information sets.
        
        Parameters
        ----------
        weight_by : str
            the similarity measure to weight by.  Defaults to 'Set similarity'.
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        
        Notes
        -----
        Network details:
            * vertices: items.
            * edges: paired comparisons. 
            * edge weghts: a similarity measure. Defaults to 'Set similarity'.
        """
        
        # Initialising network
        if 'full_items_network' not in self.networks.contents():
            self.items_to_full_network(directed_yn='undirected', append_to_case = True)

        info_sim_network = copy.deepcopy(self.networks.full_items_network)

        df = self.all_items_info_comparisons().copy(deep=True)
        df = df.sort_values('First item').reset_index().drop('index', axis=1)
        df = df.replace('N/A', np.nan)
        info_sim_network['all_information_comparisons'] = df

        # Adding attributes to edges
        for row in list(df.index):
            
            try:
                item_1 = df.iloc[row, 0]
                item_2 = df.iloc[row, 1]
                start_vertex = info_sim_network.vs.find(name = item_1).index
                end_vertex = info_sim_network.vs.find(name = item_2).index
                edge_id = info_sim_network.get_eid(start_vertex, end_vertex)

                info_sim_network.es[edge_id]['name'] = item_1 + ' ~ ' + item_2
                info_sim_network.es[edge_id]['weight'] = df.loc[row, weight_by]
                info_sim_network.es[edge_id]['shared_info'] = df.loc[row, 'Intersect']
                info_sim_network.es[edge_id]['shared_info_size'] = df.loc[row, 'Intersect size']
                info_sim_network.es[edge_id]['set_similarity'] = df.loc[row, 'Set similarity']
                info_sim_network.es[edge_id]['cosine_similarity'] = df.loc[row, 'Cosine similarity']
                info_sim_network.es[edge_id]['mean_levenshtein'] = df.loc[row, 'Mean levenshtein distance']
            except:
                pass

        # Deleting redundant edges
        to_del = info_sim_network.es.select(lambda x: (x["weight"]==0) or (math.isnan(x["weight"]) == True) or (x["weight"]=="N/A") or (x["name"]=="N/A"))
        CaseNetwork.delete_edges(info_sim_network, to_del)

        if append_to_case == True:
            self.networks.items_information_similarity = info_sim_network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return info_sim_network


    def generate_info_coincidence_network(self, append_to_case = True):
        
        """
        Returns an undirected network representing whether information entries coincide in items.
        
        Parameters
        ----------
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        
        Notes
        -----
        Network details:
            * vertices: information entries.
            * edges: instances where two information entries appear together in 1 or more items.
            * edge weghts: number of co-occurences.
        """
        
        # Initialising network
        if 'disconnected_info_network' not in self.networks.contents():
            info_to_vertices(self, directed_yn='undirected', append_to_case = True)

        info_co_network = copy.deepcopy(self.networks.disconnected_info_network)

        if self.properties.coincidences_identified == False:
            self.identify_coincidences()

        df = self.dataframes.coinciding_data['information'].copy(deep=True)
#         df = df.astype(str)
        info_co_network['information_coincidences'] = df
        
        if (type(df) == None) or (len(df.index) == 0):
            if self.properties.parsed == False:
                self.parse_rawdata()

            df = self.info_coincidence(ignore_nones = True)
        
        df = df[df['Frequency'] > 0]

        for row in list(df.index):
            item_1 = df.iloc[row, 0]
            item_2 = df.iloc[row, 1]

            name = item_1 + ' & ' + item_2
            freq = df.iloc[row, 3]
            coincide_in = df.iloc[row, 2]

            start_vertex = info_co_network.vs.find(name = item_1).index
            end_vertex = info_co_network.vs.find(name = item_2).index

            CaseNetwork.add_edges(info_co_network, [(start_vertex, end_vertex)], attributes = {'name': name, 'weight': freq, 'coincide_in': coincide_in})

        if append_to_case == True:
            self.networks.coinciding_information = info_co_network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return info_co_network


    def generate_items_metadata_shared_network(self, append_to_case = True):
        
        """
        Returns an undirected network representing whether items share metadata entries. Item pairs with no shared entries do not share edges.
        
        Parameters
        ----------
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        
        Notes
        -----
        Network details:
            * vertices: items.
            * edges: instances where two items share 1 or more metadata entries. 
            * edge weghts: number of metadata entries shared.
        """

        # Initialising network
        if 'full_items_network' not in self.networks.contents():
            self.items_to_full_network(directed_yn = 'undirected', append_to_case = True)

        metadata_shared_network = copy.deepcopy(self.networks.full_items_network)

        df = self.all_items_metadata_comparisons().copy(deep=True)
        df = df.sort_values('First item').reset_index().drop('index', axis=1)
#         df = df[df['Intersect size'] > 0]
        metadata_shared_network['all_metadata_comparisons'] = df
    
    
        # Adding attributes to edges
        for row in list(df.index):
            
            try:
                item_1 = df.iloc[row, 0]
                item_2 = df.iloc[row, 1]
                start_vertex = metadata_shared_network.vs.find(name = item_1).index
                end_vertex = metadata_shared_network.vs.find(name = item_2).index
                edge_id = metadata_shared_network.get_eid(start_vertex, end_vertex)

                metadata_shared_network.es[edge_id]['name'] = item_1 + ' ∩ ' + item_2
                metadata_shared_network.es[edge_id]['weight'] = df.loc[row, 'Intersect size']
                metadata_shared_network.es[edge_id]['shared_metadata'] = df.loc[row, 'Intersect']
                metadata_shared_network.es[edge_id]['set_similarity'] = df.loc[row, 'Set similarity']
                metadata_shared_network.es[edge_id]['cosine_similarity'] = df.loc[row, 'Cosine similarity']
                metadata_shared_network.es[edge_id]['mean_levenshtein'] = df.loc[row, 'Mean levenshtein distance']
                
            except:
                pass

        # Deleting redundant edges
        to_del = metadata_shared_network.es.select(lambda x: (x["weight"]==0) or (math.isnan(x["weight"]) == True) or (x["weight"]=="N/A") or (x["name"]=="N/A"))
        CaseNetwork.delete_edges(metadata_shared_network, to_del)

        if append_to_case == True:
            self.networks.items_metadata_shared = metadata_shared_network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return metadata_shared_network

    def generate_items_metadata_similarity_network(self, weight_by = 'Set similarity', append_to_case = True):
        
        """
        Returns an undirected network representing the similarity between items' metadata sets.
        
        Parameters
        ----------
        weight_by : str
            the similarity measure to weight by.  Defaults to 'Set similarity'.
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        
        Notes
        -----
        Network details:
            * vertices: items.
            * edges: paired comparisons. 
            * edge weghts: a similarity measure. Defaults to 'Set similarity'.
        """
        
        # Initialising network
        if 'full_items_network' not in self.networks.contents():
            self.items_to_full_network(directed_yn = 'undirected', append_to_case = True)

        metadata_sim_network = copy.deepcopy(self.networks.full_items_network)

        df = self.all_items_metadata_comparisons().copy(deep=True)
        df = df.sort_values('First item').reset_index().drop('index', axis=1)
#         df = df[df['Intersect size'] > 0]
        metadata_sim_network['all_metadata_comparisons'] = df
        
        # Adding attributes to edges
        for row in list(df.index):
            try:
                item_1 = df.iloc[row, 0]
                item_2 = df.iloc[row, 1]
                start_vertex = metadata_sim_network.vs.find(name = item_1).index
                end_vertex = metadata_sim_network.vs.find(name = item_2).index
                edge_id = metadata_sim_network.get_eid(start_vertex, end_vertex)

                metadata_sim_network.es[edge_id]['name'] = item_1 + ' ~ ' + item_2
                metadata_sim_network.es[edge_id]['weight'] = df.loc[row, weight_by]
                metadata_sim_network.es[edge_id]['shared_metadata'] = df.loc[row, 'Intersect']
                metadata_sim_network.es[edge_id]['shared_metadata_size'] = df.loc[row, 'Intersect size']
                metadata_sim_network.es[edge_id]['set_similarity'] = df.loc[row, 'Set similarity']
                metadata_sim_network.es[edge_id]['cosine_similarity'] = df.loc[row, 'Cosine similarity']
                metadata_sim_network.es[edge_id]['mean_levenshtein'] = df.loc[row, 'Mean levenshtein distance']
            except:
                pass

        # Deleting redundant edges
        to_del = metadata_sim_network.es.select(lambda x: (x["weight"]==0) or (math.isnan(x["weight"]) == True) or (x["weight"]=="N/A") or (x["name"]=="N/A"))
        CaseNetwork.delete_edges(metadata_sim_network, to_del)

        if append_to_case == True:
            self.networks.items_metadata_similarity = metadata_sim_network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return metadata_sim_network

        
        
    def generate_metadata_coincidence_network(self, append_to_case = True):
        
        """
        Returns an undirected network representing whether metadata entries coincide in items.
        
        Parameters
        ----------
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        
        Notes
        -----
        Network details:
            * vertices: metadata entries.
            * edges: instances where two metadata entries appear together in 1 or more items.
            * edge weghts: number of co-occurences.
        """
        
        # Initialising network
        if 'disconnected_metadata_network' not in self.networks.contents():
            metadata_to_vertices(self, directed_yn='undirected', append_to_case = True)

        metadata_co_network = copy.deepcopy(self.networks.disconnected_metadata_network)

        if self.properties.coincidences_identified == False:
            self.identify_coincidences()

        df = self.dataframes.coinciding_data['metadata'].copy(deep=True)
#         df = df.astype(str)
        metadata_co_network['metadata_coincidences'] = df
        
        if (type(df) == None) or (len(df.index) == 0):
            if self.properties.parsed == False:
                self.parse_rawdata()

            df = self.metadata_coincidence(ignore_nones = True)
        
        df = df[df['Frequency'] > 0]

        for row in list(df.index):
            item_1 = df.iloc[row, 0]
            item_2 = df.iloc[row, 1]

            name = item_1 + ' & ' + item_2
            freq = df.iloc[row, 3]
            coincide_in = df.iloc[row, 2]

            start_vertex = metadata_co_network.vs.find(name = item_1).index
            end_vertex = metadata_co_network.vs.find(name = item_2).index

            CaseNetwork.add_edges(metadata_co_network, [(start_vertex, end_vertex)], attributes = {'name': name, 'weight': freq, 'coincide_in': coincide_in})

       # Deleting redundant edges
#         to_del = metadata_co_network.es.select(lambda x: (x["weight"]==0) or (math.isnan(x["weight"]) == True) or (x["weight"]=="N/A") or (x["name"]=="N/A"))
#         CaseNetwork.delete_edges(metadata_co_network, to_del)

        if append_to_case == True:
            self.networks.coinciding_metadata = metadata_co_network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return metadata_co_network


    def info_items_partitioned(self, append_to_case = True):
        
        """
        Returns an undirected bipartite network representing which items contain information entries.
        
        Parameters
        ----------
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        
        Notes
        -----
        Network details:
            * vertices: 
                * Information entries
                * Items
            * edges: whether an information entry appears in an item.
        """

        item_vs = pd.Series(self.items.ids()).sort_values().to_list()
        
        info_df = self.get_all_info().copy(deep=True).astype(str)
        info_vs = info_df['Category'] + ': ' + info_df['Label']
        info_vs = pd.Series(list(set(info_vs))).sort_values().to_list()

        types = ['item']*len(item_vs) + ['information']*len(info_vs)
        names = item_vs + info_vs

        edgelist = []
        for item_id in item_vs:
            item_info = self.items.get_item(item_id).information.copy(deep=True).astype(str)
            labels = item_info['Category'] + ': ' + item_info['Label']
            labels = set(labels)
            for info in labels:
                edge_id = (item_id, info)
                edgelist.append(edge_id)

        network = CaseNetwork.Full_Bipartite(len(item_vs),len(info_vs))

        network.vs['type'] = types
        network.vs['name'] = names

        for vertex in network.vs():
            name = vertex['name']
            vtype = vertex['type']
            if (name in item_vs) and (vtype == 'item'):
                item_data = self.items.get_item(name)
                vertex['information'] = item_data.information.astype(str)
                vertex['metadata'] = item_data.metadata.astype(str)
                vertex['data'] = item_data.data.astype(str)


        to_del = []
        for edge in network.es():
            source = network.vs[edge.source]
            target = network.vs[edge.target]
            edge_pair = (source['name'], target['name'])
            if edge_pair not in edgelist:
                to_del.append(edge_pair)

        CaseNetwork.delete_edges(network, to_del)

        network.simplify()

        if append_to_case == True:
            self.networks.items_information_partitioned = network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return network


    def metadata_items_partitioned(self, append_to_case = True):
        
        """
        Returns an undirected bipartite network representing which items contain metadata entries.
        
        Parameters
        ----------
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        
        Notes
        -----
        Network details:
            * vertices: 
                * Metadata entries
                * Items
            * edges: whether a metadata entry appears in an item.
        """

        item_vs = pd.Series(self.items.ids()).sort_values().to_list()
        metadata_vs = pd.Series(list(self.get_metadata_set())).astype(str).sort_values().to_list()

        for item in metadata_vs:
            if ((': None' in item) or (': none' in item) or ('None' in item.strip()) or ('none' in item.strip()) or (item == None)):
                metadata_vs.remove(item)

        types = ['item']*len(item_vs) + ['metadata']*len(metadata_vs)
        names = item_vs + metadata_vs

        network = CaseNetwork.Full_Bipartite(len(item_vs),len(metadata_vs))
        network.vs['type'] = types
        network.vs['name'] = names

        edgelist = []
        for item_id in item_vs:
            series = self.items.get_item(item_id).metadata['Category'].astype(str) + ': ' + self.items.get_item(item_id).metadata['Metadata'].astype(str) 
            for metadata in series:
                item = (item_id, metadata)
                edgelist.append(item)

        for vertex in network.vs():
            name = vertex['name']
            vtype = vertex['type']
            if (name in item_vs) and (vtype == 'item'):
                    item_data = self.items.get_item(name)
                    vertex['information'] = item_data.information.astype(str)
                    vertex['metadata'] = item_data.metadata.astype(str)
                    vertex['data'] = item_data.data.astype(str)

        to_del = []
        for edge in network.es():
            source = network.vs[edge.source]
            target = network.vs[edge.target]
            edge_pair = (source['name'], target['name'])
            if edge_pair not in edgelist:
                to_del.append(edge_pair)

        CaseNetwork.delete_edges(network, to_del)

        for v in network.vs():
            if ': None' in v['name']:
                CaseNetwork.delete_vertices(network, [v])

        if append_to_case == True:
            self.networks.items_metadata_partitioned = network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return network

        
    def info_metadata_items_partitioned(self, append_to_case = True):
        
        """
        Returns an undirected tripartite network representing how items, information entries, and metadata entries occur together.
        
        Parameters
        ----------
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        
        Notes
        -----
        Network details:
            * vertices: 
                * Information entries
                * Metadata entries
                * Items
            * edges: whether an information entry or metadata entry appears in an item.
        """
        
        if 'items_information_partitioned' not in self.networks.contents():
            self.info_items_partitioned()

        g1 = copy.deepcopy(self.networks.items_information_partitioned)

        if 'items_metadata_partitioned' not in self.networks.contents():
            self.metadata_items_partitioned()

        g2 = copy.deepcopy(self.networks.items_metadata_partitioned)

        del g1.vs['information']
        del g2.vs['information']

        del g1.vs['metadata']
        del g2.vs['metadata']

        del g1.vs['data']
        del g2.vs['data']

        network = ig.union([g1,g2])
        network.simplify()

        if append_to_case == True:
            self.networks.items_information_metadata_partitioned = network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return network

    def info_metadata_partitioned(self, append_to_case = True):
        
        """
        Returns an undirected bipartite network representing how information entries and metadata entries occur together.
        
        Parameters
        ----------
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        
        Notes
        -----
        Network details:
            * vertices: 
                * Information entries
                * Metadata entries
            * edges: whether an information entry and metadata entry appear together in an item.
        """
        
        if 'items_information_metadata_partitioned' not in self.networks.contents():
            self.info_metadata_items_partitioned()

        base_network = copy.deepcopy(self.networks.items_information_metadata_partitioned)

        item_seq = base_network.vs.select(type='item')
        info_seq = base_network.vs.select(type='information')
        metadata_seq = base_network.vs.select(type='metadata')

        types = info_seq['type'] + metadata_seq['type']
        names = info_seq['name'] + metadata_seq['name']

        network = CaseNetwork.Full_Bipartite(len(info_seq),len(metadata_seq))

        network.vs['type'] = types
        network.vs['name'] = names

        edgelist = []

        for vertex in item_seq:

            neighbors_list = vertex.neighbors()
            info_neighbors = []
            metadata_neighbors = []

            for item in neighbors_list:
                match_index = network.vs.select(name=item['name'])[0].index

                if item['type'] == 'information':
                    info_neighbors.append(match_index)

                if item['type'] == 'metadata':
                    metadata_neighbors.append(match_index)

            for info in info_neighbors:
                 for meta in metadata_neighbors:
                    edgelist.append((info, meta))

        to_del = []

        for edge in network.es():
            source = network.vs[edge.source]
            target = network.vs[edge.target]
            edge_pair = (source.index, target.index)
            if edge_pair not in edgelist:
                to_del.append(edge_pair)

        CaseNetwork.delete_edges(network, to_del)
        network.simplify()

        if append_to_case == True:
            self.networks.information_metadata_partitioned = network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return network

        
    def info_metadata_items_co(self, append_to_case = True):
        
        """
        Returns an undirected tripartite network which represents how items, information entries, and metadata entries co-occur, as well as how much information and metadata items share with one another.
        
        Parameters
        ----------
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        
        Notes
        -----
        Network details:
            * vertices: 
                * Information entries
                * Metadata entries
                * Items
            * edges: whether one of the three object types occur together.
        """
        
        if 'items_information_metadata_partitioned' not in self.networks.contents():
            self.info_metadata_items_partitioned()

        g1 = copy.deepcopy(self.networks.items_information_metadata_partitioned)
        for attr in g1.vs.attributes():
            del g1.vs[attr]
        

        
        if 'items_information_shared' not in self.networks.contents():
                self.generate_items_info_shared_network()

        g2 = copy.deepcopy(self.networks.items_information_shared)
        for attr in g2.vs.attributes():
            del g2.vs[attr]

        if 'items_metadata_shared' not in self.networks.contents():
                self.generate_items_metadata_shared_network()

        g3 = copy.deepcopy(self.networks.items_metadata_shared)
        for attr in g3.vs.attributes():
            del g3.vs[attr]

        network = ig.union([g1,g2, g3])

        if append_to_case == True:
            self.networks.coinciding_items_information_metadata = network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return network


    def combined_items_network(self, append_to_case = True):
        
        """
        Returns a directed network which represents all data shared between items (metadata, information, links, etc.)
            
        Parameters
        ----------
        append_to_case : bool
            whether to add the network to the Case's CaseNetworks collection.
        
        Notes
        -----
        Network details:
            * vertices: Items
            * edges: 
                * Information shared
                * Metadata shared
                * Words shared
                * Links
                * References
                * Contents
        """
        
        new_network = self.items_to_vertices(directed_yn='directed', append_to_case = False)

        all_networks = self.networks.contents()

        if 'items_links' not in all_networks:
            self.generate_links_network()

        glinks = copy.deepcopy(self.networks.items_links)
        if glinks != None:
            for vertex in glinks.vs():
                if vertex['name'] not in new_network.vs['name']:
                    new_network.add_vertex(name=vertex['name'])


        if 'items_references' not in all_networks:
            self.generate_refs_network(append_to_case = True)

        grefs = copy.deepcopy(self.networks.items_references)
        if grefs != None:
            for vertex in grefs.vs():
                if vertex['name'] not in new_network.vs['name']:
                    new_network.add_vertex(name=vertex['name'])


        if 'items_contents' not in all_networks:
            self.generate_contents_network(append_to_case = True)

        gcontents = copy.deepcopy(self.networks.items_contents)
        if gcontents != None:
            for vertex in gcontents.vs():
                if vertex['name'] not in new_network.vs['name']:
                    new_network.add_vertex(name=vertex['name'])


        if 'items_information_shared' not in all_networks:
            self.generate_items_info_shared_network(append_to_case = True)

        ginfo = copy.deepcopy(self.networks.items_information_shared)
        if ginfo != None:
            ginfo_dir = ginfo.as_directed()
            for vertex in ginfo_dir.vs():
                if vertex['name'] not in new_network.vs['name']:
                    new_network.add_vertex(name=vertex['name'])


        if 'items_metadata_shared' not in all_networks:
            self.generate_items_metadata_shared_network(append_to_case = True)

        gmeta = copy.deepcopy(self.networks.items_metadata_shared)
        if gmeta != None:
            gmeta_dir = gmeta.as_directed()
            for vertex in gmeta_dir.vs():
                if vertex['name'] not in new_network.vs['name']:
                    new_network.add_vertex(name=vertex['name'])
        
        # Need to add links network
        networks_list = [grefs, gcontents, ginfo_dir, gmeta_dir]

        labels_list = ['references', 'contents', 'information shared', 'metadata shared']
        weights_list = [1, 1, ginfo_dir.es['weight'], gmeta_dir.es['weight']]
        index = 0

        for network in networks_list:

            if network != None:

                edgelist = []

                for edge in network.es():
                    source_id = edge.source
                    target_id = edge.target
                    addr = (source_id, target_id)
                    edgelist.append(addr)

                new_network.add_edges(edgelist, attributes={'type':labels_list[index], 'weight': weights_list[index]})
                index += 1

        if append_to_case == True:
            self.networks.combined_items_network = new_network
            self.networks.update_properties()
            self.update_properties()
            return

        else:
            return new_network


    def generate_base_networks(self, items = True, keywords = True, info = True, metadata = True):
        
        """
        Generates all base network types and assigns to the Case's CaseNetworks collection.
        
        Parameters
        ----------
        items : bool
            whether to generate items networks.
        keywords : bool
            whether to generate keywords networks.
        info : bool
            whether to generate information networks.
        metadata : bool
            whether to generate metadata networks.
        """
        
        if items == True:
            self.items_to_vertices(directed_yn='undirected', append_to_case = True)
            self.items_to_full_network(directed_yn='undirected', append_to_case = True)
        
        if keywords == True:
            self.keywords_to_vertices(directed_yn='undirected', append_to_case = True)
            self.keywords_to_full_network(directed_yn='undirected', append_to_case = True)
        
        if info == True:
            self.info_to_vertices(directed_yn='undirected', append_to_case = True)
            self.info_to_full_network(directed_yn = 'undirected', append_to_case = True)
        
        if metadata == True:
            self.metadata_to_vertices(directed_yn='undirected', append_to_case = True)
            self.metadata_to_full_network(directed_yn = 'undirected', append_to_case = True)
        
        self.networks.update_properties()
        self.update_properties()
         # self.backup()


    def generate_items_networks(self, keywords = True, info = True, metadata = True):
        
        """
        Generates all item network types and assigns to the Case's CaseNetworks collection.
        
        Parameters
        ----------
        keywords : bool
            whether to generate keywords networks.
        info : bool
            whether to generate information networks.
        metadata : bool
            whether to generate metadata networks.
        """
        
        if keywords == True:
            self.generate_items_words_shared_network(append_to_case = True)
            self.generate_items_words_similarity_network(weight_by = 'Cosine similarity', append_to_case = True)
        
        if info == True:
            self.generate_items_info_shared_network(append_to_case = True)
            self.generate_items_info_similarity_network(weight_by = 'Set similarity', append_to_case = True)
        
        if metadata == True:
            self.generate_items_metadata_shared_network(append_to_case = True)
            self.generate_items_metadata_similarity_network(weight_by = 'Set similarity', append_to_case = True)
        
        try:
            self.combined_items_network(append_to_case = True)
        except:
            pass
        
        self.networks.update_properties()
        self.update_properties()
         # self.backup()


    def generate_directed_networks(self):
        
        """
        Generates all directed networks and assigns to the Case's CaseNetworks collection.
        """
        
        self.generate_links_network(append_to_case = True)
        self.generate_refs_network(append_to_case = True)
        self.generate_contents_network(append_to_case = True)
        self.generate_urls_network(append_to_case = True)
        
        self.networks.update_properties()
        self.update_properties()
         # self.backup()

        

    def generate_coincidence_networks(self, keywords = False, info = True, metadata = True):
        
        """
        Generates all coincidence networks for data types and assigns to the Case's CaseNetworks collection. 
        
        WARNING: These operations are computationally intensive.
        
        Parameters
        ----------
        keywords : bool
            whether to generate keywords networks.
        info : bool
            whether to generate information networks.
        metadata : bool
            whether to generate metadata networks.
        """
        
        if keywords == True:
            self.generate_keywords_coincidence_network(limit = 600, append_to_case = True)

        if info == True:
            self.generate_info_coincidence_network(append_to_case = True)

        if metadata == True:
            self.generate_metadata_coincidence_network(append_to_case = True)
        
        self.networks.update_properties()
        self.update_properties()
         # self.backup()
    


    def generate_partitioned_networks(self):
        
        """
        Generates all n-partite networks and assigns to the Case's CaseNetworks collection.
        """
        
         # Creates a bipartite network between item entries and information entries

        self.info_items_partitioned(append_to_case = True)

        self.metadata_items_partitioned(append_to_case = True)

        self.info_metadata_items_partitioned(append_to_case = True)

        self.info_metadata_partitioned(append_to_case = True)

#         self.info_metadata_items_co(append_to_case = True) # not working currently
        
        self.networks.update_properties()
        self.update_properties()
         # self.backup()

        

    def generate_all_networks(self, items = True, keywords = True, info = True, metadata = True, directed_networks = True,  coincidence_networks = True, partitioned_networks = True):
        
        """
        Generates all network types and assigns to the Case's CaseNetworks collection.
        
        Parameters
        ----------
        items : bool
            whether to generate items networks.
        keywords : bool
            whether to generate keywords networks.
        info : bool
            whether to generate information networks.
        metadata : bool
            whether to generate metadata networks.
        directed_networks : bool
            whether to generate links, references, and contents networks.
        coincidence_networks : bool
            whether to generate coincidence networks.
        partitioned_networks : bool
            whether to generate partitioned networks.
        """
        
        self.generate_base_networks(items = items, 
                                    keywords = keywords, 
                                    info = info, 
                                    metadata = metadata)

        if items == True:
            self.generate_items_networks(keywords = keywords, info = info, metadata = metadata)

        if directed_networks == True:
            self.generate_directed_networks()

        if coincidence_networks == True:
            self.generate_coincidence_networks(keywords = keywords, info = info, metadata = metadata)

        if partitioned_networks == True:
            self.generate_partitioned_networks()
        
        self.networks.update_properties()
        self.properties.networks_generated = True
        self.update_properties()
         # self.backup()
    
    

    # Methods for identifying if and how datapoints coincide across the case
    
    def rawdata_coincidence(self, select_by_type = None, ignore_nones = True):
        
        """
        Counts the number of times two different sets of raw data occur together in item entries across the dataset. Returns a pandas.DataFrame.
        """
        
        all_data = self.get_all_data(select_by_type = select_by_type)
        rawdata_set = set(all_data['Raw data'])
        
        output_df = pd.DataFrame(list(itertools.combinations(rawdata_set, 2)), columns = ['First dataset', 'Second dataset'])
        output_df['Coincide in'] = None
        output_df['Frequency'] = None

        np = output_df.to_numpy()
        ids = self.items.contents()
        
        index = 0
        
        for row in np:
            
            found_in_1 = set(all_data[all_data['Raw data'] == row[0]]['Found in'])
            found_in_2 = set(all_data[all_data['Raw data'] == row[1]]['Found in'])
            
            coincide_in = found_in_1.intersection(found_in_2)
            frequency = len(coincide_in)
            
            output_df.at[index, 'Coincide in'] = list(coincide_in)
            output_df.loc[index, 'Frequency'] = frequency

            index += 1

        if ignore_nones == True:

            output_df = output_df.dropna().drop(index = output_df[output_df['Frequency'] == 0].index)
        
        output_df = output_df.sort_values('Frequency', ascending=False).reset_index().drop('index', axis=1)
        
        for i in output_df.index:
            if len(output_df.loc[i, 'Coincide in']) == 0:
                output_df.loc[i, 'Coincide in'] = None
        
        self.dataframes.coinciding_data['rawdata'] = output_df
        self.dataframes.update_properties()
        self.update_properties()
         # self.backup()
        
        return self.dataframes.coinciding_data['rawdata']

    
    def word_coincidence(self, ignore_nones = True, limit = 600):
        
        """Counts the number of times two different words occur together in item entries across the dataset. Returns a pandas.DataFrame.
        
        Notes
        -----
        Bug/issue: for some reason, the number of rows (i.e. pairs of words) fluctuates 
        each time I reset the kernal and re-run the full program. It only occurs when I set 'ignore_nones' to True,
        which indicates that the issue arises when it removes 'none' words.
        Possibly because the there is variation in which words were selected for comparison, due to variation
        in the order of words in the 'frequent_words' list. I'm not sure how to get rid of this issue.
        The difference is significant (~ 2-3000) but still small compared to the total number of rows that usually occur.
        """
        
        if (limit != None) and (type(limit) == int):

            if len(self.dataframes.keywords.frequent_words.index) != 0:
                all_words = self.dataframes.keywords.frequent_words.reset_index()
                iter_set = set(all_words.loc[:limit]['word'])
                lookup_df = all_words.reset_index().set_index('word')

            else:
                all_words = self.get_word_frequencies_detailed().sort_values('found_in_frequency', ascending=False).reset_index()
                iter_set = set(all_words.loc[:limit]['word'])
                lookup_df = all_words.reset_index().set_index('word')

        else:
            all_words = self.get_all_words()
            iter_set = set(all_words['word'])
            lookup_df = all_words.reset_index().set_index('word')

        output_df = pd.DataFrame(list(itertools.combinations(iter_set, 2)), columns = ['First word', 'Second word'])
        output_df['Coincide in'] = None
        output_df['Frequency'] = None

        np = output_df.to_numpy()
        index = 0
        
        for row in np:

            found_in_1 = lookup_df.loc[row[0], 'found_in']
            found_in_2 = lookup_df.loc[row[1], 'found_in']
            
            coincide_in = found_in_1.intersection(found_in_2)
            frequency = len(coincide_in)
            
            output_df.loc[index, 'Frequency'] = frequency
            if frequency == 0:
                output_df.at[index, 'Coincide in'] = None
            else:
                output_df.at[index, 'Coincide in'] = list(coincide_in)
            
            index += 1

        if ignore_nones == True:
            to_drop = output_df[(output_df['Frequency'] == 0) | (output_df['Coincide in'] == None)].index
            output_df = output_df.drop(to_drop)
        
        output_df = output_df.sort_values('Frequency', ascending=False).reset_index().drop('index', axis=1)
        
        self.dataframes.coinciding_data['words'] = output_df
        self.dataframes.update_properties()
        self.update_properties()
         # self.backup()
        
        return self.dataframes.coinciding_data['words']


    def info_coincidence(self, select_by_category = None, ignore_nones = True):
        
        """
        Counts the number of times two different pieces of information occur together in items across the case. Returns a pandas.DataFrame.
        """
        
        info_df = self.get_all_info(select_by_category = select_by_category).astype(str)
        info_df['Info'] = 'Label: ' + info_df['Label'] + ', Category: ' + info_df['Category']
        info_df = info_df.drop(['Label', 'Category'], axis=1)[['Info', 'Found in']]
        info_set = set(info_df['Info'])
        
        output_df = pd.DataFrame(list(itertools.combinations(info_set, 2)), columns = ['First item', 'Second item'])
        output_df['Coincide in'] = None
        output_df['Frequency'] = None

        np = output_df.to_numpy()
        index = 0
        
        for row in np:

            found_in_1 = set(info_df[info_df['Info'] == row[0]]['Found in'])
            found_in_2 = set(info_df[info_df['Info'] == row[0]]['Found in'])
            
            coincide_in = found_in_1.intersection(found_in_2)
            frequency = len(coincide_in)
            
            output_df.loc[index, 'Frequency'] = frequency
            if frequency == 0:
                output_df.at[index, 'Coincide in'] = None
            else:
                output_df.at[index, 'Coincide in'] = list(coincide_in)
            
            index += 1

        if ignore_nones == True:
            to_drop = output_df[(output_df['Frequency'] == 0) | (output_df['Coincide in'] == None)].index
            output_df = output_df.drop(to_drop)
        
        output_df = output_df.sort_values('Frequency', ascending=False).reset_index().drop('index', axis=1)
        
        self.dataframes.coinciding_data['information'] = output_df
        self.dataframes.update_properties()
        self.update_properties()
         # self.backup()
        
        return self.dataframes.coinciding_data['information']


    def metadata_coincidence(self, select_by_category = None, ignore_nones = True):
        
        """
        Counts the number of times two different pieces of metadata occur together in items across the case. Returns a pandas.DataFrame.
        """
        
        metadata_df = self.get_all_metadata(select_by_category = select_by_category).astype(str)
        metadata_df['Entry'] = metadata_df['Category'] + ': ' + metadata_df['Metadata']
        metadata_df = metadata_df.drop(['Metadata', 'Category'], axis=1)[['Entry', 'Found in']]
        metadata_set = set(metadata_df['Entry'])
        
        output_df = pd.DataFrame(list(itertools.combinations(metadata_set, 2)), columns = ['First item', 'Second item'])
        output_df['Coincide in'] = None
        output_df['Frequency'] = None

        np = output_df.to_numpy()
        index = 0
        
        for row in np:

            found_in_1 = set(metadata_df[metadata_df['Entry'] == row[0]]['Found in'])
            found_in_2 = set(metadata_df[metadata_df['Entry'] == row[0]]['Found in'])
            
            coincide_in = found_in_1.intersection(found_in_2)
            frequency = len(coincide_in)
            
            output_df.loc[index, 'Frequency'] = frequency
            if frequency == 0:
                output_df.at[index, 'Coincide in'] = None
            else:
                output_df.at[index, 'Coincide in'] = list(coincide_in)
            
            index += 1

        if ignore_nones == True:
            to_drop = output_df[(output_df['Frequency'] == 0) | (output_df['Coincide in'] == None)].index
            output_df = output_df.drop(to_drop)
        
        output_df = output_df.sort_values('Frequency', ascending=False).reset_index().drop('index', axis=1)
        
        self.dataframes.coinciding_data['metadata'] = output_df
        self.dataframes.update_properties()
        self.update_properties()
#         self.backup()
        
        return self.dataframes.coinciding_data['metadata']


    
    def info_metadata_coincidence(self):
        
        """
        Identifies the number of times one information entry and one metadata entry appear together each item in the case. Returns a dataframe and saves it to the case object.
        """
        
        if 'items_by_information' in self.indexes.contents():
            info_df = self.indexes.items_by_information
        else:
            info_df = self.index_by_info()
        
        if 'items_by_metadata' in self.indexes.contents():
            metadata_df = self.indexes.items_by_metadata
        else:
            metadata_df = self.index_by_metadata()

        info_dict = {}
        for i in range(0, len(info_df.index)):
            info_dict[(info_df.loc[i, 'Label'], info_df.loc[i, 'Category'])] = info_df.loc[i, 'Items']

        metadata_dict = {}
        for i in range(0, len(metadata_df.index)):
            metadata_dict[(metadata_df.loc[i, 'Metadata'], metadata_df.loc[i, 'Category'])] = metadata_df.loc[i, 'Items']

        info_keys = info_dict.keys()
        metadata_keys = metadata_dict.keys()

        df = pd.DataFrame(columns = ['Information', 'Metadata', 'Coincide in', 'Frequency'])

        for info in info_keys:
            info_in = info_dict[info]

            for metadata in metadata_keys:
                metadata_in = metadata_dict[metadata]

                both_in = info_in.intersection(metadata_in)
                count = len(both_in)

                index = len(df.index)
                df.loc[index] = [info, metadata, both_in, count]
                
        df = df.sort_values('Frequency', ascending=False).reset_index().drop('index', axis=1)
        
        for i in df.index:
            if len(df.loc[i, 'Coincide in']) == 0:
                df.loc[i, 'Coincide in'] = None
        
        self.dataframes.coinciding_data['information and metadata'] = df
        self.dataframes.update_properties()
        self.update_properties()
         # self.backup()
        
        return self.dataframes.coinciding_data['information and metadata']
    
    
    def links_coincidence(self, ignore_nones = False):
        
        """
        Counts the number of times two different links occur together in items across the case. Returns a pandas.DataFrame.
        """
        
        links_df = self.get_links_frequencies_detailed().copy(deep=True)
        links_set = set(links_df['Link'])
        links_df = links_df.set_index('Link')
        
        output_df = pd.DataFrame(list(itertools.combinations(links_set, 2)), columns = ['First link', 'Second link'])
        output_df['Coincide in'] = None
        output_df['Frequency'] = None

        np = output_df.to_numpy()
        index = 0
        
        for row in np:

            found_in_1 = set(links_df.loc[row[0], 'Found in'])
            found_in_2 = set(links_df.loc[row[1], 'Found in'])
            
            coincide_in = found_in_1.intersection(found_in_2)
            frequency = len(coincide_in)
            
            output_df.loc[index, 'Frequency'] = frequency
            if frequency == 0:
                output_df.at[index, 'Coincide in'] = None
            else:
                output_df.at[index, 'Coincide in'] = list(coincide_in)
            
            index += 1

        if ignore_nones == True:
            to_drop = output_df[(output_df['Frequency'] == 0) | (output_df['Coincide in'] == None)].index
            output_df = output_df.drop(to_drop)
        
        output_df = output_df.sort_values('Frequency', ascending=False).reset_index().drop('index', axis=1)
        
        self.dataframes.coinciding_data['links'] = output_df
        self.dataframes.update_properties()
        self.update_properties()
         # self.backup()
        
        return self.dataframes.coinciding_data['links']
    

    def refs_coincidence(self, ignore_nones = False):
        
        """
        Counts the number of times two different references occur together in items across the case. Returns a pandas.DataFrame.
        """
        
        refs_df = self.get_all_refs()
        refs_set = set(refs_df['Reference'])
        
        output_df = pd.DataFrame(list(itertools.combinations(refs_set, 2)), columns = ['First reference', 'Second reference'])
        output_df['Coincide in'] = None
        output_df['Frequency'] = None

        np = output_df.to_numpy()
        index = 0
        
        for row in np:

            found_in_1 = set(refs_df[refs_df['Reference'] == row[0]]['Found in'])
            found_in_2 = set(refs_df[refs_df['Reference'] == row[0]]['Found in'])
            
            coincide_in = found_in_1.intersection(found_in_2)
            frequency = len(coincide_in)
            
            output_df.loc[index, 'Frequency'] = frequency
            if frequency == 0:
                output_df.at[index, 'Coincide in'] = None
            else:
                output_df.at[index, 'Coincide in'] = list(coincide_in)
            
            index += 1

        if ignore_nones == True:
            to_drop = output_df[(output_df['Frequency'] == 0) | (output_df['Coincide in'] == None)].index
            output_df = output_df.drop(to_drop)
        
        output_df = output_df.sort_values('Frequency', ascending=False).reset_index().drop('index', axis=1)
        
        self.dataframes.coinciding_data['references'] = output_df
        self.dataframes.update_properties()
        self.update_properties()
         # self.backup()
        
        return self.dataframes.coinciding_data['references']
    

    def contents_coincidence(self, ignore_nones = False):
        
        """
        Counts the number of times two different pieces of content within items occur together in items across the case. Returns a pandas.DataFrame.
        """
        
        contents_df = self.get_all_contents()
        contents_set = set(contents_df['Content'])
        
        output_df = pd.DataFrame(list(itertools.combinations(contents_set, 2)), columns = ['First item', 'Second item'])
        output_df['Coincide in'] = None
        output_df['Frequency'] = None

        np = output_df.to_numpy()
        index = 0
        
        for row in np:

            found_in_1 = set(contents_df[contents_df['Content'] == row[0]]['Found in'])
            found_in_2 = set(contents_df[contents_df['Content'] == row[0]]['Found in'])
            
            coincide_in = found_in_1.intersection(found_in_2)
            frequency = len(coincide_in)
            
            output_df.loc[index, 'Frequency'] = frequency
            if frequency == 0:
                output_df.at[index, 'Coincide in'] = None
            else:
                output_df.at[index, 'Coincide in'] = list(coincide_in)
            
            index += 1

        if ignore_nones == True:
            to_drop = output_df[(output_df['Frequency'] == 0) | (output_df['Coincide in'] == None)].index
            output_df = output_df.drop(to_drop)
        
        output_df = output_df.sort_values('Frequency', ascending=False).reset_index().drop('index', axis=1)
        
        self.dataframes.coinciding_data['contents'] = output_df
        self.dataframes.update_properties()
        self.update_properties()
         # self.backup()
        
        return self.dataframes.coinciding_data['contents']
    
    
    def identify_coincidences(self, metadata = True, rawdata = True, words = True, info = True, links = True, references = True, contents = True, generate_networks = False, ignore_nones = False, limit = 600):
        
        """
        Runs all coincidence identification methods. 
        
        Parameters
        ----------
        generate_networks : bool
            whether to generate networks based on coincidences identified.
        
        Notes
        -----
            * Behaviour depends on the options selected by the user and on whether the underlying data processing (e.g. raw data parsing) has been done.
        """
        
        if metadata == True:
            self.metadata_coincidence(ignore_nones = ignore_nones)

        if rawdata == True:
            self.rawdata_coincidence(ignore_nones = ignore_nones)

        if words == True:
            if self.properties.parsed == False:
                self.parse_rawdata()
            
            self.word_coincidence(ignore_nones = ignore_nones, limit = limit)
            
        if info == True:
            self.info_coincidence(ignore_nones = ignore_nones)
            
        if links == True:
            self.links_coincidence(ignore_nones = ignore_nones)
        
        if references == True:
            self.refs_coincidence(ignore_nones = ignore_nones)

        if contents == True:
            self.contents_coincidence(ignore_nones = ignore_nones)

        if (metadata == True) and (info == True):
            self.info_metadata_coincidence()
        
        if generate_networks == True:
            self.generate_coincidence_networks(keywords = words, info = info, metadata = metadata)
            self.networks.update_properties()
        
        self.properties.coincidences_identified = True
        self.dataframes.update_properties()
        self.update_properties()
         # self.backup()
    

    # Methods for generating analytics from case data and adding to case object

    def analyse_data_entry_frequencies(self, append_to_case = True):
        
        """
        Analyses case-level attributes and adds them to case.
        """

        if 'analytics' not in self.contents():
            self.analytics = CaseAnalytics()
            
        cols = ['total_entries', 'unique_entries', 'repeated_entries', 'intersect_size', 'mean_frequency', 'most_frequent', 'most_frequent_count', 'least_frequent', 'least_frequent_count', 'mean_coincidence']
        
        df = pd.DataFrame(columns = cols, dtype = object)

        df.loc['data'] = self.get_data_frequency_stats()
        df.loc['keywords'] = self.get_words_frequency_stats()
        df.loc['metadata'] = self.get_metadata_frequency_stats()
        df.loc['information'] = self.get_info_frequency_stats()
    #     df.loc['links'] = get_case_lvl_links_analytics(self)
    #     df.loc['references'] = get_case_lvl_refs_analytics(self)
    #     df.loc['contents'] = get_case_lvl_contents_analytics(self)
    #     df.loc['entities'] = get_case_lvl_contents_analytics(self)


        if append_to_case == True:
            self.analytics.case_analytics = df
            self.analytics.update_properties()
            self.update_properties()
    #          # self.backup()

        return df

    
    def analyse_item_comparisons(self, append_to_case = True):
        
        """
        Runs all item comparison analytics.
        
        Parameters
        ----------
        append_to_case : bool
            whether to append analysis results to Case's CaseAnalytics collection.
        """
        
        data_comparisons = self.items.get_all_rawdata_comparisons()
        keyword_comparisons = self.items.get_all_words_comparisons()
        metadata_comparisons = self.items.get_all_metadata_comparisons()
        info_comparisons = self.items.get_all_info_comparisons()

        item_combos = list(zip(metadata_comparisons['First item'], metadata_comparisons['Second item']))
        
        cols = ['Data cosine similarity',
                'Data set similarity',
                'Data mean levenshtein distance',
                'Keywords cosine similarity',
                'Keywords set similarity',
                'Keywords mean levenshtein distance',
                'Metadata cosine similarity',
                'Metadata set similarity',
                'Metadata mean levenshtein distance',
                'Info cosine similarity',
                'Info set similarity',
                'Info mean levenshtein distance']
        
        df = pd.DataFrame(index = item_combos, columns = cols, dtype = object)

        for pair in df.index:
            index_tuple = pair

            data_index = data_comparisons[((data_comparisons['First item'] == index_tuple[0]) & (data_comparisons['Second item'] == index_tuple[1]) | (data_comparisons['First item'] == index_tuple[1]) & (data_comparisons['Second item'] == index_tuple[0]))].index[0]
            data_cosine = data_comparisons.loc[data_index, 'Cosine similarity']
            data_set_sim = data_comparisons.loc[data_index, 'Set similarity']

            keywords_index = keyword_comparisons[((keyword_comparisons['First item'] == index_tuple[0]) & (keyword_comparisons['Second item'] == index_tuple[1]) | (keyword_comparisons['First item'] == index_tuple[1]) & (keyword_comparisons['Second item'] == index_tuple[0]))].index[0]
            keywords_cosine = keyword_comparisons.loc[keywords_index, 'Cosine similarity']
            keywords_set_sim = keyword_comparisons.loc[keywords_index, 'Set similarity']
            keywords_lev = keyword_comparisons.loc[keywords_index, 'Levenshtein distance']

            metadata_index = metadata_comparisons[((metadata_comparisons['First item'] == index_tuple[0]) & (metadata_comparisons['Second item'] == index_tuple[1]) | (metadata_comparisons['First item'] == index_tuple[1]) & (metadata_comparisons['Second item'] == index_tuple[0]))].index[0]
            metadata_cosine = metadata_comparisons.loc[metadata_index, 'Cosine similarity']
            metadata_set_sim = metadata_comparisons.loc[metadata_index, 'Set similarity']
            metadata_lev = metadata_comparisons.loc[metadata_index, 'Mean levenshtein distance']

            info_index = info_comparisons[((info_comparisons['First item'] == index_tuple[0]) & (info_comparisons['Second item'] == index_tuple[1]) | (info_comparisons['First item'] == index_tuple[1]) & (info_comparisons['Second item'] == index_tuple[0]))].index[0]
            info_cosine = info_comparisons.loc[info_index, 'Cosine similarity']
            info_set_sim_var = info_comparisons.loc[info_index, 'Set similarity']
            info_lev = info_comparisons.loc[info_index, 'Mean levenshtein distance']

            df.at[pair, 'Data cosine similarity'] = data_cosine
            df.at[pair, 'Data set similarity'] = data_set_sim
            df.at[pair, 'Data mean levenshtein distance'] = None
            df.at[pair, 'Keywords cosine similarity'] = keywords_cosine
            df.at[pair, 'Keywords set similarity'] = keywords_set_sim
            df.at[pair, 'Keywords mean levenshtein distance'] = keywords_lev
            df.at[pair, 'Metadata cosine similarity'] = metadata_cosine
            df.at[pair, 'Metadata set similarity'] = metadata_set_sim
            df.at[pair, 'Metadata mean levenshtein distance'] =metadata_lev
            df.at[pair, 'Info cosine similarity'] = info_cosine
            df.at[pair, 'Info set similarity'] = info_set_sim_var
            df.at[pair, 'Info mean levenshtein distance'] = info_lev


        if append_to_case == True:
            self.analytics.item_comparisons = df
            self.analytics.update_properties()
            self.update_properties()
    #          # self.backup()
            return df

        else:
            return df


    def get_data_frequency_stats(self):
        
        """
        Returns all data frequency statistics.
        """
        
        all_data_df = self.get_all_data().copy(deep=True).astype(str)
        data_len = len(all_data_df)
        data_freqs = all_data_df.value_counts(['Datatype', 
                                                'Format', 
                                                'Stored as', 
                                                'Size (bytes)',
                                                'Raw data',
                                                'Parsed data']).reset_index()
        data_set_len = len(data_freqs)
        data_repeats_len = data_len - data_set_len
        data_intersect_len = len(self.get_data_intersect())
        data_mean_freq = data_freqs[0].mean()
        data_most_freq_list = data_freqs.iloc[0].astype(str).to_list()
        data_most_freq = {'Datatype': data_most_freq_list[0], 'Format': data_most_freq_list[1], 'Raw data': data_most_freq_list[4]}
        data_most_freq_count = data_most_freq_list[-1]
        data_least_freq_list = data_freqs.iloc[-1].astype(str).to_list()
        data_least_freq = {'Datatype': data_least_freq_list[0], 'Format': data_least_freq_list[1], 'Raw data': data_least_freq_list[4]}
        data_least_freq_count = data_least_freq_list[-1]
        data_co_mean = self.dataframes.coinciding_data['rawdata']['Frequency'].mean()

        return [
                data_len, 
                data_set_len, 
                data_repeats_len, 
                data_intersect_len, 
                data_mean_freq, 
                data_most_freq, 
                data_most_freq_count, 
                data_least_freq, 
                data_least_freq_count, 
                data_co_mean
                ]

    def get_words_frequency_stats(self):
        
        """
        Returns all word frequency statistics.
        """
        
        all_words_df = self.get_all_words().copy(deep=True).astype(str)
        words_len = len(all_words_df)
        words_freqs = self.dataframes.keywords.frequent_words
        words_set_len = len(words_freqs)
        words_repeats_len = words_len - words_set_len
        words_intersect_len = len(self.get_words_intersect())
        words_mean_freq = words_freqs['frequency'].mean()

        if words_set_len > 0:
            words_most_freq = words_freqs.iloc[0].name
            words_most_freq_count = words_freqs.iloc[0]['frequency']
            words_least_freq = words_freqs.iloc[-1].name
            words_least_freq_count = words_freqs.iloc[-1]['frequency']

        else:
            words_most_freq = None
            words_most_freq_count = None
            words_least_freq = None
            words_least_freq_count = None

        words_co_mean = self.dataframes.coinciding_data['words']['Frequency'].mean()

        return [
                words_len, 
                words_set_len, 
                words_repeats_len, 
                words_intersect_len, 
                words_mean_freq, 
                words_most_freq, 
                words_most_freq_count, 
                words_least_freq, 
                words_least_freq_count, 
                words_co_mean
                ]

    def get_info_frequency_stats(self):
    
        """
        Returns all information entry frequency statistics.
        """
        
        all_info_df = self.get_all_info().copy(deep=True).astype(str)
        info_len = len(all_info_df)
        info_freqs = all_info_df.value_counts(['Label', 'Category']).reset_index()
        info_set_len = len(info_freqs)
        info_repeats_len = info_len - info_set_len
        info_intersect_len = len(self.get_info_intersect())
        info_mean_freq = info_freqs[0].mean()
        info_most_freq_series = info_freqs.iloc[0].astype(str)
        info_most_freq = 'Label: ' + info_most_freq_series['Label'] + ', Category: ' + info_most_freq_series['Category']
        info_most_freq_count = info_most_freq_series[0]
        info_least_freq_series = info_freqs.iloc[-1].astype(str)
        info_least_freq = 'Label: ' + info_least_freq_series['Label'] + ', Category: ' + info_least_freq_series['Category']
        info_least_freq_count = info_least_freq_series[0]
        info_co_mean = self.dataframes.coinciding_data['information']['Frequency'].mean()


        return [
                info_len, 
                info_set_len, 
                info_repeats_len, 
                info_intersect_len, 
                info_mean_freq, 
                info_most_freq, 
                info_most_freq_count, 
                info_least_freq, 
                info_least_freq_count, 
                info_co_mean
                ]

    def get_metadata_frequency_stats(self):
        
        """
        Returns all metadata entry frequency statistics.
        """
        
        all_metadata_df = self.get_all_metadata().copy(deep=True).dropna().astype(str)
        metadata_len = len(all_metadata_df)
        metadata_freqs = all_metadata_df.value_counts(['Metadata', 'Category']).reset_index()
        metadata_set_len = len(metadata_freqs)
        metadata_repeats_len = metadata_len - metadata_set_len
        metadata_intersect_len = len(self.get_metadata_intersect())
        metadata_mean_freq = metadata_freqs[0].mean()
        metadata_most_freq_series = metadata_freqs.iloc[0].astype(str)
        metadata_most_freq = 'Metadata: ' + metadata_most_freq_series['Metadata'] + ', Category: ' + metadata_most_freq_series['Category']
        metadata_most_freq_count = metadata_most_freq_series[0]
        metadata_least_freq_series = metadata_freqs.iloc[-1].astype(str)
        metadata_least_freq = 'Metadata: ' + metadata_least_freq_series['Metadata'] + ', Category: ' + metadata_least_freq_series['Category']
        metadata_least_freq_count = metadata_least_freq_series[0]
        metadata_co_mean = self.dataframes.coinciding_data['metadata']['Frequency'].mean()


        return [
                metadata_len, 
                metadata_set_len, 
                metadata_repeats_len, 
                metadata_intersect_len, 
                metadata_mean_freq, 
                metadata_most_freq,
                metadata_most_freq_count, 
                metadata_least_freq, 
                metadata_least_freq_count, 
                metadata_co_mean
                ]

    def global_network_analytics_blank_df(self):
        
        """
        Returns an empty dataframe formatted to take global network analytics results.
        """
        
        # Cross-network comparison stats

        networks_list = self.networks.contents()
        to_ignore = ['disconnected_items_network',
                        'full_items_network',
                        'disconnected_words_network',
                        'full_words_network',
                        'disconnected_info_network',
                        'full_info_network',
                        'disconnected_metadata_network',
                        'full_metadata_network',
                        'info_ev_partitioned',
                        'info_metadata_partitioned',
                        'metadata_ev_partitioned',
                        'info_metadata_ev_partitioned',
                        'info_metadata_ev_co',
                        'combined_items_network'
                        'items_information_partitioned',
                         'items_metadata_partitioned',
                         'items_information_metadata_partitioned',
                         'information_metadata_partitioned',
                         'items_information_partitioned',
                         'combined_items_network',
                         'coinciding_items_information_metadata']

        networks_list = [i for i in networks_list if i not in to_ignore]

        dataframe = pd.DataFrame(index = networks_list,
                                                                    columns=[
                                                                    'average_path_length',
                                                                    'diameter',
                                                                    'density',
                                                                    'weighted_density',
                                                                    'reciprocity',
                                                                    'mean_degree',
                                                                    'mean_weighted_degree',
                                                                    'mean_betweenness',
                                                                    'mean_eigencentrality',
                                                                    'mean_authority_score',
                                                                    'mean_hub_score',
                                                                    'mean_coreness'
                                                                    ],
                                                                    dtype = object)

        return dataframe

    def global_network_analytics(self, dataframe):
        
        """
        Runs all global network analytics and returns a dataframe.
        """
        
        for i in dataframe.index:
            
            dataframe.loc[i, 'average_path_length'] = self.networks.get_network(i).average_path_length()
            dataframe.loc[i, 'diameter'] = self.networks.get_network(i).diameter()
            dataframe.loc[i, 'density'] = self.networks.get_network(i).density()
            dataframe.loc[i, 'weighted_density'] = self.networks.weighted_density(i)
            dataframe.loc[i, 'reciprocity'] = self.networks.get_network(i).reciprocity()
            
            degrees_stats = self.networks.degrees_stats(i)
            if 'mean' in degrees_stats.index:
                dataframe.loc[i, 'mean_degree'] = degrees_stats['mean']
                
            weighted_degrees_stats = self.networks.weighted_degrees_stats(i)
            if 'mean' in weighted_degrees_stats.index:
                dataframe.loc[i, 'mean_weighted_degree'] = weighted_degrees_stats['mean']
            
            betweenness_stats = self.networks.betweenness_stats(i)
            if 'mean' in betweenness_stats.index:
                dataframe.loc[i, 'mean_betweenness'] = betweenness_stats['mean']

            try:
                eigen_stats = self.networks.eigencentralities_stats(i)
                if 'mean' in eigen_stats.index:
                    dataframe.loc[i, 'mean_eigencentrality'] = eigen_stats['mean']
            except:
                dataframe.loc[i, 'mean_eigencentrality'] = np.nan
            
            auth_stats = self.networks.authority_scores_stats(i)
            if 'mean' in auth_stats.index:
                dataframe.loc[i, 'mean_authority_score'] = auth_stats['mean']
            
            hub_stats = self.networks.hub_scores_stats(i)
            if 'mean' in hub_stats.index:
                dataframe.loc[i, 'mean_hub_score'] = hub_stats['mean']
            
            coreness_stats = self.networks.coreness_stats(i)
            if 'mean' in coreness_stats.index:
                dataframe.loc[i, 'mean_coreness'] = coreness_stats['mean']

        return dataframe

    def undirected_network_analysis_results(self, network_name):
        
        """
        Runs all network analytics for an undirected network and returns a dictionary.
        """
        
        if network_name not in self.networks.contents():
            return None

        output_dict = {}

        output_dict = {}
        dfs_list = [self.networks.degrees_df(network_name, direction='all').set_index('vertex'),
                    self.networks.weighted_degrees_df(network_name, direction='all').set_index('vertex'),
                    self.networks.eigencentralities_df(network_name).set_index('vertex'),
                    self.networks.betweenness_df(network_name).set_index('vertex'),
                    self.networks.authority_scores_df(network_name).set_index('vertex'),
                    self.networks.hub_scores_df(network_name).set_index('vertex'),
                    self.networks.coreness_df(network_name).set_index('vertex')]
        
        output_dict['vertex_comparisons'] = pd.concat(dfs_list, axis=1)

        output_dict['components'] = self.networks.components(network_name)
        output_dict['degree_distribution'] = self.networks.degree_distribution(network_name, weighted = False, direction = 'all')
        output_dict['weighted_degree_distribution'] = self.networks.degree_distribution(network_name, weighted = True, direction = 'all')

        return output_dict

    def directed_network_analysis_results(self, network_name):
        
        """
        Runs all network analytics for a directed network and returns a dictionary.
        """

        if network_name not in self.networks.contents():
            return None

        output_dict = {}

        output_dict = {}
        
        dfs_list = [self.networks.degrees_df(network_name, direction='in').set_index('vertex'),
                    self.networks.degrees_df(network_name, direction='out').set_index('vertex'),
                    self.networks.weighted_degrees_df(network_name, direction='in').set_index('vertex'),
                    self.networks.weighted_degrees_df(network_name, direction='out').set_index('vertex'),
                    self.networks.betweenness_df(network_name).set_index('vertex'),
                    self.networks.authority_scores_df(network_name).set_index('vertex'),
                    self.networks.hub_scores_df(network_name).set_index('vertex'),
                    self.networks.coreness_df(network_name).set_index('vertex')]
        
        output_dict['vertex_comparisons'] = pd.concat(dfs_list, axis=1)
        output_dict['components'] = self.networks.components(network_name)
        output_dict['in_degree_distribution'] = self.networks.degree_distribution(network_name, weighted = False, direction = 'in')
        output_dict['out_degree_distribution'] = self.networks.degree_distribution(network_name, weighted = False, direction = 'out')

        return output_dict
    

    def analyse_all_networks(self, append_to_case = True):
        
        """
        Runs all network analysis statistics.
        
        Parameters
        ----------
        append_to_case : bool
            whether to append analysis results to Case's CaseAnalytics collection.
        """
        
        if 'network_analytics' not in self.analytics.contents():
            self.analytics.network_analytics = {}

        output_dict = {}

        global_analytics = self.global_network_analytics_blank_df()
        global_analytics = self.global_network_analytics(global_analytics)
        output_dict['network_comparisons'] = global_analytics

        network_list = global_analytics.index.to_list()

        for network in network_list:
            network_obj = self.networks.get_network(network)
            if network_obj.is_directed() == True:
                output_dict[network] = self.directed_network_analysis_results(network_name = network)
            else:
                output_dict[network] = self.undirected_network_analysis_results(network_name = network)

        if append_to_case == True:
            if 'network_analytics' not in self.analytics.contents():
                self.analytics.network_analytics = {}
            self.analytics.network_analytics = output_dict
            self.analytics.update_properties()
            self.update_properties()
            return output_dict

        else:
            return output_dict

        
    def item_attr_counts(self, item_id):
        
        """
        Returns the number of entries for all item attributes in an item.
        """
        
        output_df = pd.DataFrame(columns=['Data', 'Metadata', 'Information', 'Links', 'References', 'Contents'], index=[item_id])
        output_df['Data'] = len(self.items.get_item(item_id = item_id).data)
        output_df['Information'] = len(self.items.get_item(item_id = item_id).information)
        output_df['Metadata'] = len(self.items.get_item(item_id = item_id).metadata)
        
        try:
            output_df['Links'] = len(self.items.get_item(item_id = item_id).links)
        except:
            output_df['Links'] = np.nan
        
        try:
            output_df['References'] = len(self.items.get_item(item_id = item_id).references)
        except:
            output_df['References'] = np.nan
        
        try:
            output_df['Contents'] = len(self.items.get_item(item_id = item_id).contents)
        except:
            output_df['Contents'] = np.nan
        
        return output_df

    
    def item_info_stats(self, item_id):
        
        """
        Returns all information analytics for an item.
        """
        
        output_df = {}
        
        info_comparisons = self.item_vs_other_info_comparison(item_id).copy(deep=True).replace('N/A', np.nan)
        
        amounts_shared = info_comparisons['Intersect size']
        cosines = info_comparisons['Cosine similarity']
        set_similarities = info_comparisons['Set similarity']
        levenshteins = info_comparisons['Mean levenshtein distance']
        
        amounts_shared_stats = amounts_shared.astype(float).describe()
        cosines_stats = cosines.astype(float).describe()
        set_similarities_stats = set_similarities.astype(float).describe()
        levenshteins_stats = levenshteins.astype(float).describe()
        
        output_df['item_comparisons'] = info_comparisons
        output_df['item_comparisons_stats'] = pd.DataFrame([amounts_shared_stats, cosines_stats, set_similarities_stats, levenshteins_stats]).T
        
        return output_df

    
    def item_metadata_stats(self, item_id):
        
        """
        Returns all metadata analytics for an item.
        """
        
        output_df = {}
        
        metadata_comparisons = self.item_vs_other_metadata_comparison(item_id).copy(deep=True).replace('N/A', np.nan)
        
        amounts_shared = metadata_comparisons['Intersect size']
        cosines = metadata_comparisons['Cosine similarity']
        set_similarities = metadata_comparisons['Set similarity']
        levenshteins = metadata_comparisons['Mean levenshtein distance']
        
        amounts_shared_stats = amounts_shared.astype(float).describe()
        cosines_stats = cosines.astype(float).describe()
        set_similarities_stats = set_similarities.astype(float).describe()
        levenshteins_stats = levenshteins.astype(float).describe()
        
        output_df['item_comparisons'] = metadata_comparisons
        output_df['item_comparisons_stats'] = pd.DataFrame([amounts_shared_stats, cosines_stats, set_similarities_stats, levenshteins_stats]).T
        
        return output_df

    
    def item_words_stats(self, item_id, comparison_df):
        
        """
        Returns all words analytics for an item.
        """
        
        output_df = {}
        
        words_comparisons = comparison_df[(comparison_df['First item'] == item_id) | (comparison_df['Second item'] == item_id)]
        words_comparisons = words_comparisons.replace('N/A', np.nan)
        
        amounts_shared = words_comparisons['Intersect size']
        cosines = words_comparisons['Cosine similarity']
        set_similarities = words_comparisons['Set similarity']
        levenshteins = words_comparisons['Levenshtein distance']
        
        amounts_shared_stats = amounts_shared.astype(float).describe()
        cosines_stats = cosines.astype(float).describe()
        set_similarities_stats = set_similarities.astype(float).describe()
        levenshteins_stats = levenshteins.astype(float).describe()
        
        output_df['item_comparisons'] = words_comparisons
        output_df['item_comparisons_stats'] = pd.DataFrame([amounts_shared_stats, cosines_stats, set_similarities_stats, levenshteins_stats]).T
        
        return output_df

    
    def item_links_stats(self, item_id):
        
        """
        Returns all link analytics for an item.
        """
        
        if 'items_links' not in self.networks.contents():
            return None
        
        ## Links
        output_dict = {}
        
        try:
            output_dict['linked_by'] = self.networks.is_linked_by(item_id)
        except:
            pass
        
        try:
            output_dict['network_stats'] = self.analytics.network_analytics['items_links']['vertex_comparisons'].loc[item_id]
        except:
            pass
        
        return output_dict

    
    def item_refs_stats(self, item_id):
        
        """
        Returns all references analytics for an item.
        """
        
        if 'items_references' not in self.networks.contents():
            return None
        
        ## reference
        output_dict = {}
        
        try:
            output_dict['referred_by'] = self.networks.is_referred_by(item_id)
        except:
            None
        
        try:
            output_dict['network_stats'] = self.analytics.network_analytics['items_references']['vertex_comparisons'].loc[item_id]
        except:
            None
        
        return output_dict

    
    def item_contents_stats(self, item_id):
        
        """
        Returns all contents analytics for an item.
        """
        
        if 'items_contents' not in self.networks.contents():
            return None
        
        ## content
        output_dict = {}
        
        try:
            output_dict['contained_by'] = self.networks.is_contained_by(item_id)
        except:
            None
        
        try:
            output_dict['network_stats'] = self.analytics.network_analytics['items_contents']['vertex_comparisons'].loc[item_id]
        except:
            None
        
        return output_dict

    
    def analyse_all_items(self, append_to_case = True):
        
        """
        Generates all item analytics.
        
        Parameters
        ----------
        append_to_case : bool
            whether to append analysis results to Case's CaseAnalytics collection.
        """
        
        if 'item_analytics' not in self.analytics:
            self.analytics.item_analytics = {}

        item_ids = self.items.ids()

        output_dict = {}

        words_comparisons = self.all_items_words_comparisons()

        for item_id in item_ids:
            output_dict[item_id] = {}
            output_dict[item_id]['summary'] = self.item_attr_counts(item_id)
            output_dict[item_id]['keywords'] = self.item_words_stats(item_id, words_comparisons)
            output_dict[item_id]['metadata'] = self.item_metadata_stats(item_id)
            output_dict[item_id]['information'] = self.item_info_stats(item_id)
            output_dict[item_id]['links'] = self.item_links_stats(item_id)
            output_dict[item_id]['references'] = self.item_refs_stats(item_id)
            output_dict[item_id]['contents'] = self.item_contents_stats(item_id)

        if append_to_case == True:
            self.analytics.item_analytics = output_dict
            self.update_properties()
        
        return output_dict

    
    def info_entries_stats(self):
        
        """
        Returns analytics for all information entries in the Case.
        """
        
        output_df = {}

        all_info = self.get_all_info().copy(deep=True).astype(str)
        info_list = list(zip(all_info['Label'], all_info['Category']))

        items_by_info_df = self.indexes.items_by_information.copy(deep=True).astype(str)
        items_by_info_df['Information'] = list(zip(items_by_info_df['Label'], items_by_info_df['Category']))
        items_by_info_df = items_by_info_df.drop(['Label', 'Category'], axis=1)
        items_by_info_df = items_by_info_df.set_index('Information')

        #     metadata_by_info_dict = self.indexes.metadata_by_information

        for pair in info_list:

            vertex_name = 'Label: ' + pair[0] + ', Category: ' + pair[1]
            key = pair[1] + ': ' + pair[0]
            output_df[key] = {}
            
            try:
                output_df[key]['items_associated'] = items_by_info_df[items_by_info_df.index == pair]
            except:
                output_df[key]['items_associated'] = None
            

            try:
                output_df[key]['coincides_with'] = self.networks.get_neighbours('coinciding_information', vertex_name = vertex_name)['vertex_name'].to_list()
            except:
                output_df[key]['coincides_with'] = None

            try:
                output_df[key]['centrality_stats'] = self.analytics.network_analytics['coinciding_information']['vertex_comparisons'].loc[vertex_name]  
            except:
                output_df[key]['centrality_stats'] = None

    #         output_df[information_id]['metadata_associated'] = metadata_by_info_dict[information_id]

        return output_df

    def analyse_all_info(self, append_to_case = True):
        
        """
        Generates all information analytics.
        
        Parameters
        ----------
        append_to_case : bool
            whether to append analysis results to Case's CaseAnalytics collection.
        """
        
        if 'information_analytics' not in self.analytics.contents():
            self.analytics.information_analytics = {}

        output_dict = self.info_entries_stats()

        if append_to_case == True:
            self.analytics.information_analytics = output_dict

        return output_dict

    def metadata_entries_stats(self):
        
        """
        Returns analytics for all metadata entries in the Case.
        """
        
        output_df = {}

        all_metadata = self.get_all_metadata().copy(deep=True).astype(str)
        metadata_list = list(zip(all_metadata['Metadata'], all_metadata['Category']))


        items_by_metadata_df = self.indexes.items_by_metadata.copy(deep=True).astype(str)
        items_by_metadata_df['metadata'] = list(zip(items_by_metadata_df['Metadata'], items_by_metadata_df['Category']))
        items_by_metadata_df = items_by_metadata_df.drop(['Metadata', 'Category'], axis=1)
        items_by_metadata_df = items_by_metadata_df.set_index('metadata')

        #     metadata_by_info_dict = self.indexes.metadata_by_information

        for pair in metadata_list:

            key = pair[1] + ': ' + pair[0]
            output_df[key] = {}
            
            try:
                output_df[key]['items_associated'] = items_by_metadata_df[items_by_metadata_df.index == pair]
            except:
                output_df[key]['items_associated'] = None
            

            try:
                output_df[key]['coincides_with'] = self.networks.get_neighbours('coinciding_metadata', vertex_name = key)['vertex_name'].to_list()
            except:
                output_df[key]['coincides_with'] = None

            try:
                output_df[key]['centrality_stats'] = self.analytics.network_analytics['coinciding_metadata']['vertex_comparisons'].loc[key]  
            except:
                output_df[key]['centrality_stats'] = None

    #         output_df[metadata_id]['information_associated'] = metadata_by_metadata_dict[metadata_id]

        return output_df

    
    def analyse_all_metadata(self, append_to_case = True):
        
        """
        Generates all metadata analytics.
        
        Parameters
        ----------
        append_to_case : bool
            whether to append analysis results to Case's CaseAnalytics collection.
        """
        
        if 'metadata_analytics' not in self.analytics.contents():
            self.analytics.metadata_analytics = {}

        output_dict = self.metadata_entries_stats()

        if append_to_case == True:
            self.analytics.metadata_analytics = output_dict

        return output_dict

    
    def append_network_analytics_attrs(self):
        
        """
        Appends the results of network analyses to networks' vertices and edges.
        """
        
        # Getting networks and analytics
        network_analytics = self.analytics.network_analytics['network_comparisons'].copy(deep=True)
        networks_list = network_analytics.index.to_list()

        # Adding network-level stats to networks as attributes

        for network in networks_list:
            for column in network_analytics.columns.to_list():
                self.networks.get_network(network)[column] = network_analytics.loc[network, column]
        
        self.networks.update_properties()
        self.update_properties()
        
    def append_item_vertex_analytics_attrs(self):
        
        """
        Appends item analysis results to networks' vertices
        """
        
        # Appending to vertices for networks where vertices represent items

        all_networks = self.networks.contents()
        items_networks_list = [n for n in all_networks if (('item' in n) and ('partition' not in n) and ('combined' not in n) and ('coincid' not in n))]

        # Adding general vertex stats

        amounts_frame = pd.DataFrame()

        items = self.items.ids()
        for item_id in items:

            df = self.analytics.item_analytics[item_id]['summary']
            df.columns = df.columns.str.lower()

            # Information stats
            df['information_intersect_size'] = self.analytics.item_analytics[item_id]['information']['item_comparisons_stats'].loc['mean', 'Intersect size']
            df['information_set_similarity'] = self.analytics.item_analytics[item_id]['information']['item_comparisons_stats'].loc['mean', 'Set similarity']
            df['information_cosine_similarity'] = self.analytics.item_analytics[item_id]['information']['item_comparisons_stats'].loc['mean', 'Cosine similarity']
            df['information_mean_levenshtein'] = self.analytics.item_analytics[item_id]['information']['item_comparisons_stats'].loc['mean', 'Mean levenshtein distance']

            cols = df.columns.sort_values()
            df = df[cols]

            amounts_frame = pd.concat([amounts_frame, df])

        amounts_frame.index.name = 'item_id'
        amounts_frame = amounts_frame

        for network in items_networks_list:
            vertices = self.networks.get_network(network).vs
            for vertex in vertices:
                for col in amounts_frame.columns:
                    self.networks.get_network(network).vs[vertex.index][col] = amounts_frame.loc[vertex['name'], col]
        
        self.networks.update_properties()
        self.update_properties()

    def append_analytics_to_networks(self):
        
        """
        Appends the results of all analyses to networks as vertex and edge attributes.
        """
        
        if (('network_analytics' not in self.analytics.contents())or ('network_comparisons' not in self.analytics.network_analytics.keys())):
            self.analyse_all_networks()

        self.append_network_analytics_attrs()
        self.append_item_vertex_analytics_attrs()
        self.networks.update_properties()
        self.update_properties()

    def generate_analytics(self, items = True, data = True, metadata = True, information = True, networks = True):
        
        """
        Generates all analytics and appends the results to the Case's CaseAnalytics collection.
        
        Parameters
        ----------
        items : bool
            whether to generate item analytics.
        data : bool
            whether to generate data entry analytics.
        metadata : bool
            whether to generate metadata entry analytics.
        information : bool
            whether to generate information entry analytics.
        networks : bool
            whether to generate network analytics.
        """
        
        if networks == True:
            self.analyse_all_networks()
        
        if items == True:
            self.analyse_all_items()
        
        if information == True:
            self.analyse_all_info()
    
        if metadata == True:
            self.analyse_all_metadata()
        
        if networks == True:
            self.append_analytics_to_networks()

        self.properties.analytics_generated = True
        self.analytics.update_properties()
        self.update_properties()
         # self.backup()
    
    

    def run_full_analysis(self):
        
        """
        Runs all analysis functions on the Case.
        
        Functions:
            #. Parses all raw data entries.
            #. Generates keywords.
            #. Indexes all items, metadata, keywords, information entries, etc.
            #. Identifies if and how objects co-incide across the Case.
            #. Generates all default networks from Case data.
            #. Generates all analytics.
        """
        
        self.parse_rawdata()
        self.generate_keywords()
        self.generate_indexes()
        self.identify_coincidences()
        self.generate_all_networks()
        self.generate_analytics()
        
        self.update_properties()
        self.backup()
        

        
    # Methods for exporting data to external files
    
    def export_folder(self, folder_name = 'obj_name', folder_address = 'request_input', export_str_as = 'txt', export_dict_as = 'json', export_pandas_as = 'csv', export_network_as = 'graphML'):
        
        """
        Exports the Case to a folder.
        
        Parameters
        ----------
        folder_name : str
            name of folder to create. Defaults to using the object's variable name.
        folder_address : str
            directory address to create folder in. defaults to requesting for user input.
        export_str_as : str
            file type for exporting string objects. Defaults to 'txt'.
        export_dict_as : str
            file type for exporting dictionary objects. Defaults to 'json'.
        export_pandas_as : str
            file type for exporting Pandas objects. Defaults to 'csv'.
        export_network_as : str
            file type for exporting network objects. Defaults to 'graphML'.
        """
        
        obj_to_folder(self, folder_name = folder_name, folder_address = folder_address, export_str_as = export_str_as, export_dict_as = export_dict_as, export_pandas_as = export_pandas_as, export_network_as = export_network_as)

    def export_network_to_kumu(self, network = 'request_input', folder_address = 'request_input'):
        
        """
        Exports a network to a Kumu blue-print formatted .JSON file.
        """
        
        return self.networks.export_network_to_kumu(network = network, folder_address = folder_address)
        
    def export_network(self, network = 'request_input', folder_address = 'request_input', file_type = 'request_input'):
        
        """
        Exports a network to one of a variety of graph file types. Defaults to .graphML.
        """
        
        return self.networks.export_network(network = network, folder_address = folder_address, file_type = file_type)

    def export_all_networks(self, folder_address = 'request_input', file_type = 'request_input'):
        
        """"
        Exports all networks in the Case to one of a variety of graph file types. Defaults to .graphML.
        """
        
        return self.networks.export_all_networks(folder_address = folder_address, file_type = file_type)

    def export_txt(self, new_file = True, file_name = 'request_input', file_address = 'request_input'):
        
        """
        Exports the Case to a .txt file.
        
        Parameters
        ----------
        file_name : str
            name of file to create. Defaults to using the object's variable name.
        file_address : str
            directory address to create file in. defaults to requesting for user input.
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
        
        if '.case' != file_address[-5:]:
            file_address = file_address + '.case'
        
         # self.backup()

        with open(file_address, 'wb') as f:
            pickle.dump(self, f) 

            
    def export_excel(self, new_file = True, file_name = 'request_input', file_address = 'request_input'):
        
        """
        Exports the Case to an Excel (.xlsx) file.
        
        Parameters
        ----------
        file_name : str
            name of file to create. Defaults to using the object's variable name.
        file_address : str
            directory address to create file in. defaults to requesting for user input.
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
        
        metadata_df = self.dataframes.metadata.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(metadata_df)

        info_df = self.dataframes.information.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(info_df)

        data_df = self.dataframes.data.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(data_df)

        other_df = self.dataframes.other.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(other_df)

        frequent_words_df = self.dataframes.keywords.frequent_words.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(frequent_words_df)

        central_words_df = self.dataframes.keywords.central_words.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(central_words_df)
        
         # self.backup()
        
        with pd.ExcelWriter(file_address) as writer:  

            data_df.to_excel(writer, sheet_name='Item data')
            metadata_df.to_excel(writer, sheet_name='Item metadata')
            info_df.to_excel(writer, sheet_name='Item information')
            other_df.to_excel(writer, sheet_name='Item other')
            frequent_words_df.to_excel(writer, sheet_name='Frequent keywords')
            central_words_df.to_excel(writer, sheet_name='Central keywords')


    def export_csv_folder(self, folder_address = 'request_input', folder_name = 'request_input'):
        
        """
        Exports the Case to a folder of .csv files.
        
        Parameters
        ----------
        file_name : str
            name of file to create. Defaults to using the object's variable name.
        file_address : str
            directory address to create file in. defaults to requesting for user input.
        """
        
        metadata_df = self.dataframes.metadata.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(metadata_df)

        info_df = self.dataframes.information.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(info_df)

        data_df = self.dataframes.data.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(data_df)

        other_df = self.dataframes.other.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(other_df)

        frequent_words_df = self.dataframes.keywords.frequent_words.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(frequent_words_df)

        central_words_df = self.dataframes.keywords.central_words.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(central_words_df)
    
        dfs_dict = {'item_data': data_df, 
                    'item_metadata': metadata_df, 
                    'item_information': info_df, 
                    'item_other': other_df, 
                    'frequent_keywords': frequent_words_df, 
                    'central_keywords': central_words_df}
        
        if folder_address == 'request_input':
            folder_address = input('Folder address: ')
        
        if folder_name == 'request_input':
            folder_name = input('Folder name: ')
        
         # self.backup()
    
        path = os.path.join(folder_address, folder_name) 
        
        os.mkdir(path) 

        for item in dfs_dict.keys():
            file_name = item
            file_path = path + '/' + file_name + '.csv'
            df = dfs_dict[item]

            df.to_csv(file_path)
    
    
    def save_as(self, file_name = 'request_input', file_address = 'request_input', file_type = 'request_input'):
        
        """
        Saves the Case to a file.
        
        Parameters
        ----------
        file_name : str
            name of file to create. Defaults to using the object's variable name.
        file_address : str
            directory address to create file in. defaults to requesting for user input.
        file_type : str
            type of file to save.
        
        Notes
        -----
        Options for file_type:
            * 'text': saves to .txt file.
            * 'txt': saves to .txt file.
            * 'pickle': saves to pickled .txt file.
            * 'Excel': saves to .xlsx file.
            * 'xlsx': saves to .xlsx file.
            * 'csv': saves to .csv file.
        """
        
        if file_type == 'request_input':
            file_type = input('File type: ')
        
        file_type = file_type.strip().strip('.').strip().lower()
        
        
        if (file_type.lower().strip('.').strip() == None) or (file_type.lower().strip('.').strip() == '') or (file_type.lower().strip('.').strip() == '.case') or (file_type.lower().strip('.').strip() == 'case') or (file_type.lower().strip('.').strip() == 'text') or (file_type.lower().strip('.').strip() == 'txt') or (file_type.lower().strip('.').strip() == 'pickle'):
            
            self.export_txt(new_file = True, file_name = file_name, file_address = file_address)
        
        
        if (file_type.lower().strip('.').strip() == 'excel') or (file_type.lower().strip('.').strip() == 'xlsx'):
            
            self.export_excel(new_file = True, file_name = file_name, file_address = file_address)
        
        
        if (file_type.lower().strip('.').strip() == 'csv') or (file_type.lower().strip('.').strip() == 'csvs'):
            
            self.export_csv_folder(folder_address = file_address, folder_name = file_name)
    
    
    def save(self, save_as = None, file_type = None, save_to = None):
        
        """
        Saves the Case to its source file. If no source given, saves to a new file.
        
        Parameters
        ----------
        save_as : str
            name of file to create. Defaults to using the object's variable name.
        save_to : str
            directory address to save file in. Defaults to requesting for user input.
        file_type : str
            type of file to save.
        
        Notes
        -----
        Options for file_type:
            * 'text': saves to .txt file.
            * 'txt': saves to .txt file.
            * 'pickle': saves to pickled .txt file.
            * 'Excel': saves to .xlsx file.
            * 'xlsx': saves to .xlsx file.
            * 'csv': saves to .csv file.
        """
        
        if save_as == None:
            
            try:
                save_as = self.file_location.split('/')[-1].split('.')[0]
            except:
                save_as = self.case_name
        
        if file_type == None:
            file_type = self.file_type
        
        if save_to == None:
            save_to = self.file_location
        
        save_as = save_as.lower().strip('.').strip() 
        
        try:
            self.save_as(file_name = save_as, file_address = save_to, file_type = file_type)
        except:
            print('Save failed') 

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
    # source_path = globals()[case_name].files[0].properties.obj_path
    # target_path = globals()[case_name].properties.obj_path
    # globals()[case_name].files[0].relations.case_file = SourceFileOf(name = 'case_source_file', 
    #                                                                 source_obj_path = source_path,
    #                                                               target_obj_path = target_path,
    #                                                             parent_obj_path = None)
    
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
    
            