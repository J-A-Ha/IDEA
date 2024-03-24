from ..core.basics import Iterator
from ..exporters.general_exporters import export_obj, obj_to_folder
from .obj_properties import CaseObjectProperties

import copy

class CaseAttr:
    
    """
    This is a general class of objects intended for use as a superclass for all case attributes.
    
    Parameters
    ----------
    obj_type : str
        type of object.
    obj_name : str
        name for object.
    parent_obj_path : str
        if object is an attribute of another object, object path for the parent object. 
    size : float
        size of object in memory.
        
    Attributes
    ----------
    properties : CaseObjectProperties
        metadata for CaseAttr object.
    """
    
    def __init__(self, obj_type = 'CaseAttr', obj_name = None, parent_obj_path = None, size = None):
        
        """
        Initialises CaseAttr instance.
        
        Parameters
        ----------
        obj_type : str
            type of object.
        obj_name : str
            name for object.
        parent_obj_path : str
            if object is an attribute of another object, object path for the parent object. 
        size : float
            size of object in memory.
        """
        
        self.properties = CaseObjectProperties(obj_name = obj_name, obj_type = obj_type, parent_obj_path = parent_obj_path, size = size)
    
    def get_obj_type(self):
        
        """
        Returns the object's type as stored in its properties attribute.
        """
        
        return self.properties.obj_type
    
    def get_obj_path(self):
        
        """
        Returns the object's path in the environment, as stored in its properties attribute.
        """
        
        return self.properties.obj_path
    
    def copy(self):
        
        """
        Returns a copy of object.
        """
        
        return copy.deepcopy(self)
    
    def attributes(self):
        
        """
        Returns a list of attributes assigned to object.
        """
        
        return list(self.__dict__.keys())
    
    def __iter__(self):
        
        """
        Makes CaseAttr objects iterable.
        """
        
        return Iterator(self)
    
    def get_name_str(self):
        
        """
        Returns the object's variable name as a string. 
        
        Notes
        -----
            * Searches global environment dictionary for objects sharing object's ID. Returns key if found.
            * If none found, searches local environment dictionary for objects sharing object's ID. Returns key if found.
        """
        
        for name in globals():
            if id(globals()[name]) == id(self):
                return name
        
        for name in locals():
            if id(locals()[name]) == id(self):
                return name
    
    def varstr(self) -> str:
        
        """
        Returns the object's name as a string. Defaults to using its variable name; falls back to using its name property.
        
        Notes
        -----
            * Searches global environment dictionary for objects sharing object's ID. Returns key if found.
            * If none found, searches local environment dictionary for objects sharing object's ID. Returns key if found.
            * If none found, returns object's name property.
            * If name property is None, 'none', or 'self', returns an empty string.
        """
        
        try:
            string = self.get_name_str()
        except:
            string = None
        
        if (string == None) or (string == 'self'):
            
            try:
                string = self.properties.obj_name
            except:
                string = ''
                
        if (string == None) or (string == 'self'):
            string = ''
            
        return string
    
    
    def __getitem__(self, index):
        
        """
        Retrieves object attribute using its key.
        """
        
        return self.__dict__[index]
    
    def __setitem__(self, key, item):
        
        """
        Sets object attribute using its key.
        
        WARNING: will not allow user to set object's 'properties' attribute.
        """
        
        if key != 'properties':
            self.__dict__[key] = item
        
        self.update_properties()
        
        
    def __delitem__(self, key):
        
        """
        Deletes object attribute using its key.
        
        WARNING: will not allow user to delete object's 'properties' attribute.
        """
        
        if key != 'properties':
            delattr(self, key)
        
        self.update_properties()
    

    def hashable_list(self):
        
        """
        Converts object into a list of strings for hashing. Does not include object properties attribute.
        """
        
        return [str(i) for i in self if (type(i) != CaseObjectProperties)]
    
    def __hash__(self):
        
        """
        Hashes object. Returns a unique integer.
        """
        
        self_tuple = tuple(self.hashable_list())
        return hash(self_tuple)

    # Methods to convert item to other object types
    
    def to_list(self):
        
        """
        Returns the object's attributes as a list. Excludes object properties attribute.
        """
        
        return [i for i in self if (type(i) != CaseObjectProperties)]
    
    def to_dict(self):
        
        """
        Returns the object's attributes as a dictionary. Excludes object properties attribute.
        """
        
        output_dict = {}
        keys = [i for i in self.__dict__.keys() if i != 'properties']
        for index in keys:
            output_dict[index] = self.__dict__[index]
        
        return output_dict
    
    def contents(self):
        
        """
        Returns the object's attributes as a list. Excludes object properties attribute.
        """
        
        contents = [i for i in self.__dict__.keys() if i != 'properties']
        return contents
    
    def export_folder(self, folder_name = 'obj_name', folder_address = 'request_input', export_str_as = 'txt', export_dict_as = 'json', export_pandas_as = 'csv', export_network_as = 'graphML'):
        
        """
        Exports object's contents to a folder.
        
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
    
    
    def update_properties(self):
        
        """
        Updates CaseAttr's properties.
        
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
    
    def get_parent_obj(self):
        
        """
        If the object is an attribute of another object, returns that parent object. 
        """
        
        path = self.properties.obj_path
        parent_path = path.split(f'.{self.properties.obj_name}')[0]
        return eval(parent_path)

class CaseObject(CaseAttr):
    
    """
    This is a general class of case objects. It is intended for use as a superclass for all case objects.
    
    Parameters
    ----------
    obj_name : str
        name for object.
    obj_type : str, default : 'CaseObject'
        type of object.
    parent_obj_path : str
        if object is an attribute of another object, object path for the parent object. 
    size : float
        size of object in memory.
    
    Attributes
    ----------
    properties : CaseObjectProperties
        metadata for CaseAttr object.
    """
    
    def __init__(self, obj_name = None, obj_type = 'CaseObject', parent_obj_path = None, size = None):
        
        """
        Initialises CaseObject instance.
        
        Parameters
        ----------
        obj_name : str
            name for object.
        obj_type : str, default : 'CaseObject'
            type of object.
        parent_obj_path : str
            if object is an attribute of another object, object path for the parent object. 
        size : float
            size of object in memory.
        """
        
        # Retrieving methods and attributes from CaseAttr superclass
        super().__init__(obj_name = obj_name, obj_type = obj_type, parent_obj_path = parent_obj_path, size = size)
    
    
    def is_in(self, object_set):
        
        """
        Checks if CaseObject is part of an inputted set of objects
        """
        
        # Retrieving item ID
        self_id = self.get_id()
        
        # Checking if item ID is in item set
        return hasattr(object_set, self_id)


class CaseObjectSet(CaseAttr):
    
    """
    This is a collection of CaseObjects.
    
    Parameters
    ----------
    obj_type : str 
        type of object. Defaults to 'CaseObjectSet'.
    obj_type : str, default : 'CaseObjectSet'
        type of object.
    parent_obj_path : str
        if object is an attribute of another object, object path for the parent object. 
    
    Notes
    -----
        * Subclass of CaseAttr class.
        * Intended to used as a superclass for all collections of CaseObjects.
    """
    
    def __init__(self, obj_name = None, obj_type = 'CaseObjectSet', parent_obj_path = None):
        
        """
        Initialises CaseObjectSet instance.
        
        Parameters
        ----------
        obj_type : str 
            type of object. Defaults to 'CaseObjectSet'.
        obj_type : str, default : 'CaseObjectSet'
            type of object.
        parent_obj_path : str
            if object is an attribute of another object, object path for the parent object. 
        """
        # Retrieving methods and attributes from CaseAttr superclass
        super().__init__(obj_name = obj_name, obj_type = obj_type, parent_obj_path = parent_obj_path)
    
    def __len__(self):
        
        """
        Returns the number of objects in the collection. Excludes collection's 'properties' attribute.
        """
        
        keys = [i for i in self.__dict__.keys() if i != 'properties']
        return len(keys)
    
    def contents(self):
        
        """
        Returns the collection's contents. Excludes collection's 'properties' attribute.
        """
        
        return [i for i in self.__dict__.keys() if i != 'properties']
    
    def ids(self):
        
        """
        Returns the names of all objects in the collection. Excludes collection's 'properties' attribute.
        """
        
        return self.contents()

    def hashable_list(self):
        
        """
        Converts collection into a list of strings for hashing. Excludes collection's 'properties' attribute.
        """
        
        return [str(i) for i in self if (type(i) != CaseObjectProperties)]
    
    def __hash__(self):
        
        """
        Hashes collection. Returns a unique integer.
        """
        
        self_tuple = tuple(self.hashable_list())
        return hash(self_tuple)


    # Methods to convert object set to other object types
    
    def to_list(self):
        
        """
        Returns the collection as a list.  Excludes collection's 'properties' attribute.
        """
        
        return [i for i in self if (type(i) != CaseObjectProperties)]
    
    def to_set(self):
        
        """
        Returns the collection as a set.  Excludes collection's 'properties' attribute.
        """
        
        return set(self.to_list())
    
    def to_dict(self):
        
        """
        Returns the collection as a dictionary.  Excludes collection's 'properties' attribute.
        """
        
        output_dict = {}
        contents = self.contents()
        for index in contents:
            output_dict[index] = self.__dict__[index].to_dict()
        
        return output_dict

    def delete_all(self):
        
        """
        Deletes all objects in collection.
        """
        
        # Retrieving attribute names
        objects = list(self.contents())
        
        # Deleting retrieved names
        for i in objects:
            delattr(self, i)
            
    def __getitem__(self, index):
        
        """
        Returns object in collection using an index or list of indexes.
        
        Allows for integer slicing, negative indexes, and passing lists as indexes.
        
        Parameters
        ----------
        index : slice, object, str or int
            an object slice, attribute (object), attribute name (str), or index position (int).
        
        Returns
        -------
        result : CaseObjectSet or CaseObject
            the result.
        """
        
        contents = self.contents()
        
        res = None
        
        # Logic for handling index slices
        if type(index) == slice:
            
            # Retrieving start index
            start = index.start
            
            # If none given, starts at first index (0)
            if start == None:
                start = 0
            
            # Raising error if start index isn't an integer
            if type(start) != int:
                raise TypeError(f'{str(type(self))} slices must be integers')
            
            # If start index is negative, creating start index 
            # by counting back from size of collection
            if start < 0:
                start = len(contents) + start
            
            # Retrieving stop index
            stop = index.stop
            
            # If none given, starts at stops at final item in collection
            if stop == None:
                stop = len(contents)
            
            # Raising error if stop index isn't an integer
            if type(stop) != int:
                raise TypeError(f'{str(type(self))} slices must be integers')
            
            # If stop index is negative, creating stop index 
            # by counting back from size of collection
            if stop < 0:
                stop = len(contents) + stop
            
            # Creating new empty collection
            sliced_set = copy.deepcopy(self)
            sliced_set.delete_all()
            
            # Iterating through indexes in range; using recursion to add item to sliced collection
            for i in range(start, stop):
                entity = self.__getitem__(i)
                entity_id = contents[i]
                sliced_set.__dict__[entity_id] = entity
            
            # Updating sliced collection properties
            sliced_set.properties.entity_count = len(sliced_set)
            
            # Returning sliced collection
            res = sliced_set
        
        # Logic for integer, string, CaseObject, list, set, and tuple indexes
        else:
            
            # Initialising variable for sub-indexing logic
            sub_index = None
            
            # Splitting into index and sub-index if iterable passed
            if (type(index) == list) or (type(index) == set) or (type(index) == tuple):
                sub_index = index[1]
                index = index[0]
            
            # Returning object if the index is a CaseObject or CaseObjectProperties
            if index in self.__dict__.values():
                res = index
            
            # For all other types of index
            else:
                # Returning object if the index is an object key
                if index in contents:
                    res = self.__dict__[index]
            
                # Otherwise checking if index is an integer and using to retrieve object key
                elif type(index) == int:
                    
                    # Raising error if index is out of range
                    if index not in range(0, len(contents)):
                        raise KeyError(f'{index} is out of range for {get_var_name_str(self)}')
                    
                    # Retrieving key using index; using key to return result
                    obj = contents[index]
                    res = self.__dict__[obj]
            
            # If sub-index provided, using indexing to return attribute of result
            if sub_index != None:
                res = res[sub_index]
            
        # Checking if no result found
        if res == None:
            raise KeyError(f'"{index}" not found in {get_var_name_str(self)}')
            
        return res
    
    
    def __setitem__(self, key, item):
        
        """
        Adding object to collection using a key name.
        
        WARNING: will not allow user to set collection's 'properties' attribute.
        """
        
        if key != 'properties':
            self.__dict__[key] = item
        
        self.update_properties()
        
    def __delitem__(self, key):
        
        """
        Deletes object in collection using its key.
        
        WARNING: will not allow user to delete collection's 'properties' attribute.
        """
        
        if key != 'properties':
            delattr(self, key)
        
        self.update_properties()