from .obj_properties import CaseObjectProperties
from .obj_superclasses import CaseObjectSet
from .relationships import CaseRelation, CaseRelationSet

import copy
import pandas as pd


class CaseIndexes(CaseObjectSet):
    
    """This is a collection of indexed Case items and data. 
    
    Parameters
    ----------
    obj_name : str
        ID used for item set.
    parent_obj_path : str
        if CaseIndexes object is an attribute, object path of the parent object. Defaults to None.
    
    Notes
    -----
        * Subclass of CaseObjectSet class.
        * Intended to assigned to all Case objects.
    """
    
    def __init__(self, obj_name = None, parent_obj_path = None):
        
        """
        Initialises CaseIndexes instance.
        
        Parameters
        ----------
        obj_name : str
            ID used for item set.
        parent_obj_path : str
            if CaseIndexes object is an attribute, object path of the parent object. Defaults to None.
        """
        
        # Inheriting methods and attributes from CaseObjectSet class
        super().__init__(obj_name = obj_name, obj_type = 'CaseIndexes', parent_obj_path = parent_obj_path)
        
        self.properties = CaseObjectProperties(obj_name = obj_name, obj_type = 'CaseIndexes', parent_obj_path = parent_obj_path, size = None)
        self.update_properties()
    
    
    # Methods for editing and retrieving index set properties
    
    
    def update_properties(self):
        
        """
        Updates CaseIndexes object's properties.
        
        Updates
        -------
            * obj_id
            * obj_size
            * indexes_count
            * last_changed
            * hash
        """
        
        self.properties.obj_id = id(self)
        self.properties.indexes_count = len(self.contents())
        self.properties.obj_size = str(self.__sizeof__()) + ' bytes'
        self.properties.update_last_changed()
        self.properties.hash = self.__hash__()
    
    
    def index_list(self):
        
        """
        Returns the names of all indexes as a list.
        """
        
        return list(self.contents())
    
    
    def __repr__(self):
        
        """
        Defines how CaseIndexes objects are represented in string form.
        """
        
        string_repr = f'\nIndexes: {self.contents()}\n'
        return string_repr
    