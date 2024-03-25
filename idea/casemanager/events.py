from .obj_properties import CaseObjectProperties
from .obj_superclasses import CaseObject, CaseObjectSet
from .relationships import CaseRelation, SourceFileOf, CaseRelationSet
from .files import stat_result, CaseFile, CaseFileSet
from .casespecial import CaseSpecial

from typing import List, Dict, Tuple
import copy

import numpy as np
import pandas as pd


class CaseEvent(CaseSpecial):
    
    """
    This is a CaseEvent object. It represents an event associated with a case.
    
    Parameters
    ----------
    event_id : str
        ID used for retrieving event. Defaults to requesting user input.
    parent_obj_path : str
        if CaseEvent object is an attribute, object path of the parent object. Defaults to None.
    
    Attributes
    ----------
    event_id : str
        ID for CaseEvent object.
    details : pandas.DataFrame
        a dataframe containing details on the event.
    connections : pandas.DataFrame
        a dataframe detailing connections to the event.
    properties : CaseObjectProperties
        metadata associated with the CaseEvent object.
    
    Notes
    -----
        * Intended to be assigned as an attribute of a CaseEventSet within a Case object.
        * Subclass of CaseSpecial class.
    """
    
    def __init__(self, event_id = 'request_input', parent_obj_path = None):
        
        """
        Initialises CaseEvent instance.
        
        Parameters
        ----------
        event_id : str
            ID used for retrieving event. Defaults to requesting user input.
        parent_obj_path : str
            if CaseEvent object is an attribute, object path of the parent object. Defaults to None.
        """
        
        super().__init__(obj_type = 'CaseEvent')
        
        if event_id == 'request_input':
            event_id = input('Event ID: ')
            
        if event_id == None:
            event_id = self.get_name_str()
        
        self.event_id = event_id
        self.details = pd.DataFrame()
        self.connections = pd.DataFrame()
    
        self.properties = CaseObjectProperties(obj_name = event_id, obj_type = 'CaseEvent', parent_obj_path = parent_obj_path, size = None)
        self.update_properties()
    
    # Methods for editing and retrieving event
    
    
    def update_properties(self):
        
        """
        Updates CaseEvent's properties.
        
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
        Adds ID to event if no valid ID set.
        """
        
        if (self.event_id == None) or (type(self.event_id) != str):
            self.event_id = self.get_name_str()
    
    def get_id(self):
        
        """
        Returns event's ID.
        """
        
        if (self.event_id == None) or (type(self.event_id) != str) or (self.event_id == '_') or (self.event_id == '__'):
            self.add_id()
        
        return self.event_id
    
    
class CaseEventSet(CaseObjectSet):
    
    """
    This is a collection of CaseEvent objects. 
    
    Parameters
    ----------
    obj_name : str
        ID used for entity set.
    parent_obj_path : str
        if CaseEventSet is an attribute, object path of the parent object. Defaults to None.
    events : list
        iterable of CaseEvents to assign to collection. Defaults to an empty list.
    
    Notes
    -----
        * Subclass of CaseObjectSet class.
        * Intended to assigned to all Case objects.
    """
    
    def __init__(self, obj_name = 'entities', parent_obj_path = None, events = []):
        
        """
        Initialises CaseEventSet instance.
        
        Parameters
        ----------
        obj_name : str
            ID used for entity set.
        parent_obj_path : str
            if CaseEventSet is an attribute, object path of the parent object. Defaults to None.
        events : list
            iterable of CaseEvents to assign to collection. Defaults to an empty list.
        """
        
        # Inheriting methods and attributes from CaseObjectSet class
        super().__init__(obj_type = 'CaseEventSet')
        
        self.properties = CaseObjectProperties(obj_name = obj_name, obj_type = 'CaseEventSet', parent_obj_path = parent_obj_path, size = None)
        
        # If only one event is provided, wrapping as list
        if type(events) == CaseEvent:
            events = [events]
        
        # Adding events if provided
        for i in events:
            self.add_event(i)
        
        
        self.update_properties()
    
    
    # Methods for editing and retrieving event set properties
    
    def __repr__(self):
        
        """
        Defines how CaseEventSets are represented in string form.
        """
        
        contents = self.contents()
        output = f'\nEvents count: {self.properties.event_count}\n\n'
        
        index = 0
        for event in contents:
            output = output + f'[{str(index)}] {event}\n'
            index += 1
        
        return output
    
    def update_properties(self):
        
        """
        Updates CaseEventSet's properties.
        
        Updates
        -------
            * obj_id
            * obj_size
            * event_count
            * last_changed
            * hash
        """
        
        self.properties.obj_id = id(self)
        self.properties.obj_size = str(self.__sizeof__()) + ' bytes'
        self.properties.update_last_changed()
        self.properties.hash = self.__hash__()
        self.properties.event_count = len(self.contents())
    
    
    
    def __setitem__(self, key, event):
        
        """
        Adds CaseEvent to collection using a key name.
        
        WARNING: will not allow user to set 'properties' attribute.
        """
        
        if type(event) != CaseEvent:
            raise TypeError('Key value assignment requires a CaseEvent object')
            
        self.__dict__[key] = event
        self.update_properties()
    
    def __delitem__(self, key):
        
        """
        Deletes CaseEvent in collection using a key.
        
        WARNING: will not allow user to delete collection's 'properties' attribute.
        """
        
        if key != 'properties':
            delattr(self, key)
            self.update_properties()
    
    def __add__(self, obj):
        
        """
        Defines the functionality of addition operations on CaseEventSets.
        
        Notes
        -----
            * CaseEventSets can only have CaseEvent or other CaseEventSets added to them.
            * Adding a CaseEvent to a set will add that event to the collection of events.
            * Adding a CaseEventSet to another CaseEventSet will produce a new CaseEventSet that includes both sets' events. 
        """
        
        new_event_set = self.copy()
        
        if (type(obj) == CaseEvent) or (CaseEvent in obj.__class__.__bases__):
        
            new_event_set.add_event(obj)
            new_event_set.update_properties()
            return new_entity_set
        
        if (type(obj) == CaseEventSet) or (CaseEventSet in obj.__class__.__bases__):
            
            contents = new_event_set.contents()
            
            for event_id in obj.contents():
                event = obj.__dict__[event_id]
                if event_id not in contents:
                    new_event_set.__dict__[event_id] = event
                else:
                    event_id = event_id + '_copy'
                    new_entity_set.__dict__[event_id] = event
                    
            new_event_set.update_properties()
            return new_event_set
        
        else:
            raise TypeError('CaseEventSet objects can only be added to CaseEvent objects or CaseEventSet objects')
    
    
    def count_events(self):
        
        """
        Returns the number of CaseEvents in the collection.
        """
        
        return len(self.contents())
    
    def get_event(self, event_id):
        
        """
        Returns an event if given its ID.
        """
        
        return self.__dict__[event_id]
    
    
    # Methods for adding events and data to event set
    
    def add_blank_event(self, event_id = 'request_input'):
        
        """
        Adds a blank CaseEvent to the collection. Returns the new event in collection.
        
        Parameters
        ----------
        event_id : str
            the event's ID. This will become its attribute name. Defaults to requesting from user input.
        
        Returns
        -------
        event : CaseEvent
            the new blank event object.
        """
        
        if event_id == 'request_input':
                event_id = input('New event ID: ')
    
        if event_id == None:
                event_code = self.count_entities() + 1
                event_id = 'event_' + str(event_code)

        self.__dict__[event_id] = CaseEvent(event_id = event_id, parent_obj_path = self.properties.obj_path)
        
        self.update_properties()
        
        return self.get_event(event_id)
    
    
    def add_event(self, event = 'request_input'):
        
        """
        Adds a CaseEvent to the collection. Returns the event.
        
        Parameters
        ----------
        event : CaseEvent
            the event or event ID to be added. Defaults to None; this adds a blank CaseEvent.
        
        Returns
        -------
        event : CaseEvent
            the added event.
        """
        
        if event == None:
            return self.add_blank_event()
        
        if event == 'request_input':
            event_id = input('Event name: ')
            
            if event_id == '':
                return self.add_blank_event(event_id = None)
            
            if event_id in globals():
                event = globals()[event_id]
            else:
                return self.add_blank_event(event_id = event_id)
        
        if type(event) != CaseEvent:
            raise TypeError('Event must be of type "CaseEvent"')
        
        if event in self.__dict__.values():
            raise ValueError("Event is already in the case's entities collection")
        
        event_id = event.get_name_str()
        
        if event_id in self.contents():
            event_id = event_id + ".copy"
        
        event.properties.obj_path = self.properties.obj_path + '.' + event_id
        
        self.__dict__[event_id] = event
        
        self.update_properties()
        
        return self.__dict__[event_id]
    
    
    # Methods for deleting events and data from event set
    
    def delete_event(self, event_id = 'request_input'):
        
        """
        Deletes an event from the collection. Takes either a CaseEvent or an event ID string.
        """
        
        if event_id == 'request_input':
            event_id = input('Event ID: ')
        
        delattr(self, event_id)
        self.update_properties()
    
    def delete_all(self):
        
        """
        Deletes all events from the collection.
        """
        
        ids = self.contents()
        for event_id in ids:
            self.delete_event(event_id)
        
        self.update_properties()
    