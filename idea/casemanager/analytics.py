from ..exporters.general_exporters import export_obj, obj_to_folder
from .obj_properties import CaseObjectProperties
from .obj_superclasses import CaseObjectSet
from .relationships import CaseRelation, CaseRelationSet, SourceFileOf
from .files import stat_result, CaseFile, CaseFileSet

from typing import List, Dict, Tuple
import os
import copy

import pandas as pd


class CaseAnalytics(CaseObjectSet):
    
    """This is a collection of Case analytics. 
    
    Parameters
    ----------
    obj_name : str
        ID used for item set.
    parent_obj_path : str
        if CaseAnalytics object is an attribute, object path of the parent object. Defaults to None.
    
    Attributes
    ----------
    case_analytics : dict
        a dictionary containing case-level analytics results.
    item_analytics : dict
        a dictionary containing analytics results for individual items.
    data_analytics : dict
        a dictionary containing analytics results for data entries.
    metadata_analytics : dict
        a dictionary containing analytics results for metadata entries.
    information_analytics : dict
        a dictionary containing analytics results for information entries.
    entity_analytics : dict
        a dictionary containing analytics results for individual entities.
    network_analytics : dict
        a dictionary containing analytics results for networks.
    properties : CaseObjectProperties
        metadata associated with CaseAnalytics object.
    
    Notes
    -----
        * Subclass of CaseObjectSet class.
        * Intended to assigned to all Case objects.
    """
    
    def __init__(self, obj_name = None, parent_obj_path = None):
        
        """
        Initialises CaseItemSet instance.
        
        Parameters
        ----------
        obj_name : str
            ID used for item set.
        parent_obj_path : str
            if CaseAnalytics object is an attribute, object path of the parent object. Defaults to None.
        """
        
        # Inheriting methods and attributes from CaseObjectSet class
        super().__init__(obj_name = obj_name, obj_type = 'CaseAnalytics', parent_obj_path = parent_obj_path)
        
        self.case_analytics = {}
        self.item_analytics = {}
        self.data_analytics = {}
        self.metadata_analytics = {}
        self.information_analytics = {}
        self.entity_analytics = {}
        self.network_analytics = {}
        
        self.properties = CaseObjectProperties(obj_name = obj_name, obj_type = 'CaseAnalytics', parent_obj_path = parent_obj_path, size = None)
        self.update_properties()
    
    
    # Methods for editing and retrieving analytics set properties
    
    
    def update_properties(self):
        
        """
        Updates CaseAnalytics object's properties.
        
        Updates
        -------
            * obj_id
            * obj_size
            * case_analytics_generated
            * item_analytics_generated
            * data_analytics_generated
            * metadata_analytics_generated
            * information_analytics_generated
            * entity_analytics_generated
            * network_analytics_generated
            * contents
            * last_changed
            * hash
        """
        
        if 'case_analytics' not in self.__dict__.keys():
            self.case_analytics = {}
        
        if len(self.case_analytics) == 0:
            self.properties.case_analytics_generated = False
        else:
            self.properties.case_analytics_generated = True
            
        if len(self.item_analytics) == 0:
            self.properties.item_analytics_generated = False
        else:
            self.properties.item_analytics_generated = True
            
        if len(self.data_analytics) == 0:
            self.properties.data_analytics_generated = False
        else:
            self.properties.data_analytics_generated = True
        
        if len(self.metadata_analytics) == 0:
            self.properties.metadata_analytics_generated = False
        else:
            self.properties.metadata_analytics_generated = True
            
        if len(self.information_analytics) == 0:
            self.properties.information_analytics_generated = False
        else:
            self.properties.information_analytics_generated = True
            
        if len(self.entity_analytics) == 0:
            self.properties.entity_analytics_generated = False
        else:
            self.properties.entity_analytics_generated = True
        
        if len(self.network_analytics) == 0:
            self.properties.network_analytics_generated = False
        else:
            self.properties.network_analytics_generated = True
        
        
        self.properties.obj_id = id(self)
        self.properties.obj_size = str(self.__sizeof__()) + ' bytes'
        self.properties.contents = self.contents()
        self.properties.update_last_changed()
        self.properties.hash = self.__hash__()
    
    
    def __repr__(self):
        
        """
        Defines how CaseAnalytics objects are represented in string form.
        """
        
        self.update_properties()
        
        string_repr = f'\nLast updated: {self.properties.last_changed_at}\n\n'
        string_repr = string_repr + f'Frequency analytics generated: {self.properties.case_analytics_generated}\n'
        string_repr = string_repr + f'Item analytics generated: {self.properties.item_analytics_generated}\n'
        string_repr = string_repr + f'Data analytics generated: {self.properties.data_analytics_generated}\n'
        string_repr = string_repr + f'Metadata analytics generated: {self.properties.metadata_analytics_generated}\n'
        string_repr = string_repr + f'Information analytics generated: {self.properties.information_analytics_generated}\n'
        string_repr = string_repr + f'Entity analytics generated: {self.properties.entity_analytics_generated}\n'
        string_repr = string_repr + f'Network analytics generated: {self.properties.network_analytics_generated}\n\n'
        string_repr = string_repr + f'Contents: {self.contents()}\n'
        
        return string_repr
    
    # Methods for exporting data to external files
    
    def export_folder(self, folder_name = 'obj_name', folder_address = 'request_input', export_str_as = 'txt', export_dict_as = 'json', export_pandas_as = 'csv', export_network_as = 'graphML'):
        
        """
        Exports analytics collection to a folder.

        Parameters
        ----------
        folder_address : str
            directory address to save to. Defaults to requesting from user input.
        folder_name : str
            name for new folder.            
        export_str_as : str
            file type to export strings to.
        export_dict_as : str
            file type to export dictionaries to.
        export_pandas_as : str
            file type to export dataframes to.
        export_network_as : str
            file type to export networks to.
        """
        
        if folder_name == 'obj_name':
            folder_name = get_var_name_str(self)
    
        if folder_name == None:
            folder_name = input('Folder name: ')

        if folder_name == 'request_input':
            folder_name = input('Folder name: ')

        if folder_address == 'request_input':
            folder_address = input('Folder address: ')

        folder_address = folder_address + '/' + folder_name

        os.mkdir(folder_address)
        
        for obj_key in self.__dict__.keys():
            
            obj = self.__dict__[obj_key]
            
            if type(obj) == CaseObjectProperties:
                export_obj(obj, file_name = obj_key, folder_address = folder_address, export_str_as = export_str_as, export_dict_as = export_dict_as, export_pandas_as = export_pandas_as, export_network_as = export_network_as)
            
            if type(obj) == dict:
                obj_to_folder(obj, folder_name = obj_key, folder_address = folder_address, export_str_as = export_str_as, export_dict_as = export_dict_as, export_pandas_as = export_pandas_as, export_network_as = export_network_as)
            
            else:
                export_obj(obj, file_name = obj_key, folder_address = folder_address, export_str_as = export_str_as, export_dict_as = export_dict_as, export_pandas_as = export_pandas_as, export_network_as = export_network_as)