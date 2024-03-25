from ..core.basics import Iterator
from .defaults_manager import DEFAULT_SET, DEFAULT_CASE_NAME, set_default_case, get_default_case_name, get_default_case, is_default_case, check_default_case, update_default_case

from datetime import datetime

class Properties:
    
    """
    This is a general class for properties to be assigned to Cases, CaseObjects, and Projects.
    
    Parameters
    ----------
    parent_obj_path : str 
        name of parent object if object is an attribute of another object.
    size : int 
        size of object in memory in bytes.
        
    Attributes
    ----------
    obj_name : str
        name of object in the environment.
    obj_path : str
        path to object in the environment.
    created_at : str
        date and time created.
    last_changed_at : str
        date and time the object was last edited.
    obj_size : float
        size of the object in memory in bytes.
    """
    
    def __init__(self, obj_name = None, parent_obj_path = None, size = None):
        
        """
        Initialises Properties instance.
        
        Parameters
        ----------
        parent_obj_path : str 
            name of parent object if object is an attribute of another object.
        size : int 
            size of object in memory.
        """
        if obj_name == None:
            obj_name = ''
        self.obj_name = obj_name
        
        if parent_obj_path == None:
            parent_obj_path = ''
        self.obj_path = parent_obj_path + '.' + obj_name
        
        self.created_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.last_changed_at = self.created_at
        self.obj_size = size
    
    def __iter__(self):
        
        """
        Function to make Properties objects iterable.
        """
        
        return Iterator(self)
    
    def to_list(self):
        
        """
        Returns Properties object as a list.
        """
        
        return [i for i in self]

    def to_dict(self):
        
        """
        Returns Properties object as a dictionary.
        """
        
        output_dict = {}
        for index in self.__dict__.keys():
            output_dict[index] = self.__dict__[index]

        return output_dict
    
    
    def update_last_changed(self):
        
        """
        Updates the last_changed attribute to the current date and time.
        """
        
        self.last_changed_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")


class CaseObjectProperties(Properties):
    
    """
    This is a collection of properties for a CaseObject. 
    
    Parameters
    ----------
    obj_name : str
        name of CaseObject.
    obj_type : str
        type of CaseObject.
    parent_obj_path : str
        name of parent object if CaseObject is an attribute of another object.
    size : int
        size of CaseObject in memory.
    
    Attributes
    ----------
    obj_name : str
        name of CaseObject.
    obj_type : str
        type of CaseObject.
    obj_path : str
        path to CaseObject in the environment.
    size : float
        size of CaseObject in memory in bytes.
    
    Notes
    -----
        * Subclass of Properties class.
        * Intended to be assigned as an attribute to all CaseObject classes.
    """
    
    def __init__(self, obj_name = None, obj_type = None, parent_obj_path = None, size = None):
        
        """
        Initialises CaseObjectProperties instance.
        
        Parameters
        ----------
        obj_name : str
            name of CaseObject.
        obj_type : str
            type of CaseObject.
        parent_obj_path : str
            name of parent object if CaseObject is an attribute of another object.
        size : int
            size of CaseObject in memory.
        """
        
        super().__init__(obj_name = obj_name, parent_obj_path = parent_obj_path, size = size)
        
        if obj_name == None:
            obj_name = ''
        self.obj_name = obj_name
        
        if obj_type == None:
            obj_type = ''
        self.obj_type = obj_type
        
        if (parent_obj_path == None) or (parent_obj_path == ''):
            self.obj_path = obj_name
        else:
            self.obj_path = parent_obj_path + '.' + obj_name
           
    
    def __repr__(self):
        
        """
        Defines how CaseObjectProperties objects are represented in string form.
        """
        
        self_dict = self.to_dict()
        output = '\n'
        for key in self_dict.keys():
            prop = self_dict[key]
            output = output + key + ': ' + str(prop) + '\n'
        
        return output