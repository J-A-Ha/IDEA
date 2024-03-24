from .obj_properties import CaseObjectProperties
from .obj_superclasses import CaseObject, CaseObjectSet
from .relationships import CaseRelation, SourceFileOf, CaseRelationSet
from .files import stat_result, CaseFile, CaseFileSet
from .casespecial import CaseSpecial

from typing import List, Dict, Tuple
import copy

import numpy as np
import pandas as pd


class CaseEntity(CaseSpecial):
    
    """
    This is a CaseEntity object. It represents a person, organisation, object, or other known entity associated with a case.
    
    Parameters
    ----------
    entity_id : str
        ID used for retrieving entity. Defaults to requesting user input.
    parent_obj_path : str
        if CaseEntity is an attribute, object path of the parent object. Defaults to None.
    
    Attributes
    ----------
    entity_id : str
        ID for CaseEntity object.
    details : pandas.DataFrame
        a dataframe of details on the entity.
    connections : pandas.DataFrame
        a dataframe documenting the entity's connections.
    properties : CaseOjectProperties
        metadata associated with the CaseEntity object.
    
    Notes
    -----
        * Intended to be assigned as an attribute of a CaseEntitySet within a Case object.
        * Subclass of CaseSpecial class.
    """
    
    def __init__(self, entity_id = 'request_input', parent_obj_path = None):
        
        """
        Initialises CaseEntity instance.
        
        Parameters
        ----------
        entity_id : str
            ID used for retrieving entity. Defaults to requesting user input.
        parent_obj_path : str
            if CaseEntity is an attribute, object path of the parent object. Defaults to None.
        """
        
        
        super().__init__(obj_name = entity_id, obj_type = 'CaseEntity', parent_obj_path = parent_obj_path)
        
        if entity_id == 'request_input':
            entity_id = input('Entity ID: ')
            
        if entity_id == None:
            entity_id = self.get_name_str()
        
        self.entity_id = entity_id
        self.details = pd.DataFrame()
        self.connections = pd.DataFrame()
    
        self.properties = CaseObjectProperties(obj_name = entity_id, obj_type = 'CaseEntity', parent_obj_path = parent_obj_path, size = None)
        self.update_properties()
    
    # Methods for editing and retrieving entity properties
    
    
    def update_properties(self):
        
        """
        Updates CaseEntity's properties.
        
        Updates
        -------
            * obj_id
            * obj_size
            * last_changed
            * hash
        """
        
        self.properties.obj_id = id(self)
        self.properties.obj_size = str(self.__sizeof__()) + ' bytes'
        self.properties.update_last_changed()
        self.properties.hash = self.__hash__()
    
    def add_id(self):
        
        """
        Adds ID to entity if no valid ID set.
        """
        
        if (self.entity_id == None) or (type(self.entity_id) != str):
            self.entity_id = self.get_name_str()
    
    def get_id(self):
        
        """
        Returns entity's ID.
        """
        
        if (self.entity_id == None) or (type(self.entity_id) != str) or (self.entity_id == '_') or (self.entity_id == '__'):
            self.add_id()
        
        return self.entity_id
    

class CaseEntitySet(CaseObjectSet):
    
    """This is a collection of CaseEntity objects. 
    
    Parameters
    ----------
    obj_name : str
        ID used for entity set.
    parent_obj_path : str
        if CaseEntitySet is an attribute, object path of the parent object. Defaults to None.
    entities : list
        iterable of CaseEntities to assign to CaseEntitySet. Defaults to an empty list.
    
    Notes
    -----
        * Subclass of CaseObjectSet class.
        * Intended to assigned to all Case objects.
    """
    
    def __init__(self, obj_name = 'entities', parent_obj_path = None, entities = []):
        
        """
        Initialises CaseEntitySet instance.
        
        Parameters
        ----------
        obj_name : str
            ID used for entity set.
        parent_obj_path : str
            if item set is an attribute, object path of the parent object. Defaults to None.
        entities : list
            iterable of CaseEntities to assign to CaseEntitySet. Defaults to an empty list.
        """
        
         # Inheriting methods and attributes from CaseObjectSet class
        super().__init__(obj_name = obj_name, obj_type = 'CaseEntitySet', parent_obj_path = parent_obj_path)
        
        self.properties = CaseObjectProperties(obj_name = obj_name, obj_type = 'CaseEntitySet', parent_obj_path = parent_obj_path, size = None)
        
        # If only one entity is provided, wrapping as list
        if type(entities) == CaseEntity:
            entities = [entities]
        
        # Adding entities if provided
        for i in entities:
            self.add_entity(i)
        
        # Updating properties
        self.update_properties()
    
    
    # Methods for editing and retrieving entity set properties
    
    def update_properties(self):
        
        """
        Updates CaseEntitySet's properties.
        
        Updates
        -------
            * obj_id
            * obj_size
            * entity_count
            * last_changed
            * hash
        """
        
        self.properties.obj_id = id(self)
        self.properties.obj_size = str(self.__sizeof__()) + ' bytes'
        self.properties.update_last_changed()
        self.properties.hash = self.__hash__()
        self.properties.entity_count = len(self.contents())
    
    def __repr__(self):
        
        """
        Defines how CaseEntitySets are represented in string form.
        """
        
        contents = self.contents()
        output = f'\nEntity count: {self.properties.entity_count}\n\n'
        
        index = 0
        for entity in contents:
            output = output + f'[{str(index)}] {entity}\n'
            index += 1
        
        return output
            
    def __setitem__(self, key, entity):
        
        """
        Adds CaseEntity to collection using a key name.
        
        WARNING: will not allow user to set 'properties' attribute.
        """
        
        if type(entity) != CaseEntity:
            raise TypeError('Key value assignment requires a CaseEntity object')
            
        self.__dict__[key] = entity
    
    
    def __delitem__(self, key):
        
        """
        Deletes CaseEntity in collection using a key.
        
        WARNING: will not allow user to delete collection's 'properties' attribute.
        """
        
        if key != 'properties':
            delattr(self, key)
            self.update_properties()
    
    def count_entities(self):
        
        """
        Returns the number of CaseEntities in the collection.
        """
        
        return len(self.contents())
    
    def __add__(self, obj):
        
        """
        Defines the functionality of addition operations on CaseEntitySets.
        
        Notes
        -----
            * CaseEntitySets can only have CaseEntities or other CaseEntitySets added to them.
            * Adding a CaseEntity to a set will add that entity to the set's collection of entities.
            * Adding a CaseEntitySet to another CaseEntitySet will produce a new CaseEntitySet that includes both sets' entities. 
        """
        
        new_entity_set = self.copy()
        
        if (type(obj) == CaseEntity) or (CaseEntity in obj.__class__.__bases__):
        
            new_entity_set.add_entity(obj)
            new_entity_set.update_properties()
            return new_entity_set
        
        if (type(obj) == CaseEntitySet) or (CaseEntitySet in obj.__class__.__bases__):
            
            contents = new_entity_set.contents()
            
            for entity_id in obj.contents():
                entity = obj.__dict__[entity_id]
                if entity_id not in contents:
                    new_entity_set.__dict__[entity_id] = entity
                else:
                    entity_id = entity_id + '_copy'
                    new_entity_set.__dict__[entity_id] = entity
            new_entity_set.update_properties()
            return new_entity_set
        
        else:
            raise TypeError('CaseEntitySet objects can only be added to CaseEntity objects or CaseEntitySet objects')
    
    
    # Methods for retrieving entity set objects and attributes
    
    def get_entity(self, entity_id):
        
        """
        Returns an entity if given its ID.
        """
        
        return self.__dict__[entity_id]
    
    
    # Methods for adding objects and attributes to entity set
    
    def add_blank_entity(self, entity_id = 'request_input'):
        
        """
        Adds a blank entity to the collection. Returns the new entity in collection.
        
        Parameters
        ----------
        entity_id : str
            the entity's ID. This will become its attribute name. Defaults to requesting from user input.
        
        Returns
        -------
        entity : CaseEntity
            the new blank entity object.
        """
        
        if entity_id == 'request_input':
                entity_id = input('New entity ID: ')
    
        if entity_id == None:
                entity_code = self.count_entities() + 1
                entity_id = 'entity_' + str(entity_code)

        self.__dict__[entity_id] = CaseEntity(entity_id = entity_id, parent_obj_path = self.properties.obj_path)
        
        self.update_properties()
        
        return self.get_entity(entity_id)
    
    
    def add_entity(self, entity = 'request_input'):
        
        """
        Adds an entity to the collection. Returns the entity.
        
        Parameters
        ----------
        entity : CaseEntity
            the entity to be added. Defaults to None; this adds a blank entity.
        
        Returns
        -------
        entity : CaseEntity
            the added entity.
        """
        
        if entity == None:
            return self.add_blank_entity()
        
        if entity == 'request_input':
            entity_id = input('Entity name: ')
            
            if entity_id == '':
                return self.add_blank_entity(entity_id = None)
            
            if entity_id in globals():
                entity = globals()[entity_id]
            else:
                return self.add_blank_entity(entity_id = entity_id)
        
        if type(entity) != CaseEntity:
            raise TypeError('Entity must be of type "CaseEntity"')
        
        if entity in self.__dict__.values():
            raise ValueError("Entity is already in the case's entities collection")
        
        entity_id = entity.get_name_str()
        
        if entity_id in self.contents():
            entity_id = entity_id + ".copy"
        
        entity.properties.obj_path = self.properties.obj_path + '.' + entity_id
        
        self.__dict__[entity_id] = entity
        
        self.update_properties()
        
        return self.__dict__[entity_id]
    
    
    # Methods for deleting entity set objects and attributes
    
    def delete_entity(self, entity_id = 'request_input'):
        
        """
        Deletes an entity from the collection. Takes either a CaseEntity or an item ID string.
        """
        
        if entity_id == 'request_input':
            entity_id = input('Entity ID: ')
        
        delattr(self, entity_id)
        self.update_properties()
    
    def delete_all(self):
        
        """
        Deletes all entities from the collection.
        """
        
        ids = self.contents()
        for entity_id in ids:
            self.delete_entity(entity_id)
        
        self.update_properties()