from .obj_superclasses import CaseObject, CaseObjectSet
from .obj_properties import CaseObjectProperties

from ..internet.webanalysis import open_url, open_url_source, domain_splitter, correct_url, domain_from_ip, domain_whois, get_ip_coordinates, get_ip_physical_location, get_domain, get_ip_geocode, get_my_ip, get_my_ip_coordinates, get_my_ip_geocode, get_my_ip_physical_location, ip_from_domain, is_domain, is_ip_address, is_registered_domain, WhoisResult, domain_whois, domains_whois, ip_whois, ips_whois, lookup_ip_coordinates, lookup_whois

from pathlib import Path
from igraph import Graph, Edge

class CaseRelation(CaseObject):
    
    """
    This is an object representing a relationship between two CaseObjects (e.g. CaseItem, CaseEntity, CaseEvent).
    
    Parameters
    ----------
    name : str
        relationship name. Defaults to requesting user input.
    source_id : str
        ID of start-point object. Defaults to requesting user input.
    source_obj : object
        copy of start-point object. Defaults to None.
    source_addr : str
        location of start-point object. Defaults to None.
    target_id : str
        ID of end-point object. Defaults to requesting user input.
    target_obj : object
        copy of end-point object. Defaults to None.
    target_addr : str
        location of end-point object. Defaults to None.
    category : str
        type of relationship. Defaults to requesting user input.
    directed : bool
        whether the releationship has a direction. Defaults to False.
    attributes : list
        a list of attributes. Defaults to None.
    parent_obj_path : str
        if relationship is an attribute, object path of parent object. Defaults to None.
    
    Attributes
    ----------
    name : str
        name for relationship.
    source : dict
        dictionary of data on source object. Contains source_id, source_obj, and source_addr.
    target : dict
        dictionary of data on target object. Contains target_id, target_obj, and target_addr.
    category : str
        category of relationship
    directed : bool
        whether the releationship has a direction.
    attributes : list
        a list of attributes.
    """
    
    def __init__(self, 
                 name = 'request_input', 
                 source_id = 'request_input',
                 source_obj = None,
                 source_addr = None, 
                 target_id = 'request_input', 
                 target_obj = None,
                 target_addr = None, 
                 category = 'request_input', 
                 directed = False, 
                 attributes = None, 
                 parent_obj_path = None):
        
        """
        Initialises CaseRelation instance.
        
        Parameters
        ----------
        name : str
            relationship name. Defaults to requesting user input.
        source_id : str
            ID of start-point object. Defaults to requesting user input.
        source_obj : object
            copy of start-point object. Defaults to None.
        source_addr : str
            location of start-point object. Defaults to None.
        target_id : str
            ID of end-point object. Defaults to requesting user input.
        target_obj : object
            copy of end-point object. Defaults to None.
        target_addr : str
            location of end-point object. Defaults to None.
        category : str
            type of relationship. Defaults to requesting user input.
        directed : bool
            whether the releationship has a direction. Defaults to False.
        attributes : list
            a list of attributes. Defaults to None.
        parent_obj_path : str
            if relationship is an attribute, object path of parent object. Defaults to None.
        """
        
        # Retrieving methods and attributes from CaseObject class
        super().__init__(obj_name = name, obj_type = 'CaseRelation', parent_obj_path = parent_obj_path, size = None)
        
        # Requesting name from user input if none provided
        if name == 'request_input':
            name = input('Relation name: ')
        
        # Retrieving object variable string name if name is none
        if name == None:
            name = self.get_name_str()
        
        # Requesting source ID from user input if none provided
        if source_id == 'request_input':
            source_id = input('Source object ID: ')
        
        # If source_id is tuple, set, or list, retrieving first item as source_id
        if (type(source_id) == tuple) or (type(source_id) == list) or (type(source_id) == set):
            source_id = source_id[0]
        
        # If source_id is dictionary, tries to find source_id in dict
        if type(source_id) == dict:
            source_id = source_id['source_id']
        
        # Cleaning source_id string
        if type(source_id) == str:
            source_id = source_id.lower().strip().replace(' ', '_').replace('.', '_').strip()
        
        # Requesting target ID from user input if none provided
        if target_id == 'request_input':
            target_id = input('Target object ID: ')
        
        # If target_id is tuple, set, or list, retrieving first item as target_id
        if (type(target_id) == tuple) or (type(target_id) == list) or (type(target_id) == set):
            target_id = target_id[0]
        
        # If target_id is dictionary, tries to find target_id in dict
        if type(target_id) == dict:
            target_id = target_id['target_id']
        
        # Cleaning target_id string
        if type(target_id) == str:
            target_id = target_id.lower().strip().replace(' ', '_').replace('.', '_').strip()
        
        # Requesting category from user input if none provided
        if category == 'request_input':
            category = input('Relationship category: ')
        
        # If category given is None, replacing with empty string to avoid errors
        if category == None:
            category = ''
        
        # If attributes given is None, replacing with empty dictionary to avoid errors
        if attributes == None:
            attributes = {}
        
        # Assigning data to instance as attributes
        self.name = name
        self.source = {'source_id': source_id, 'source_obj': source_obj, 'source_addr': source_addr}
        self.target = {'target_id': target_id, 'target_obj': target_obj, 'target_addr': target_addr}
        self.category = category
        self.directed = directed
        self.attributes = attributes
        
        self.update_properties()
    
    # Methods for editing and retrieving relation data
    
    
    def keys(self):
        
        """
        Returns the relation's attribute names as a list. Excludes relation properties attribute.
        """
        
        return self.contents()
    
    
    def add_name(self, name = None):
        
        """
        Adds name to relationship.
        """
        
        self.name = name
        
        # If no name provided or name is not a string, retrieving variable name string
        if (self.name == None) or (type(self.name) != str):
            self.name = self.get_name_str()
    
    def get_name(self):
        
        """
        Returns relationship name.
        """
        
        # Retrieving name if current name is not valid
        if (self.name == None) or (type(self.name) != str) or (self.name == '_') or (self.name == '__') or (self.name == '___') or (self.name == 'self'):
            self.add_name()
        
        return self.name
    
    def hashable_list(self):
        
        """
        Converts CaseRelation into a list of strings for hashing. Excludes relation's 'properties' attribute.
        """
        
        keys = self.__dict__.keys()
        hashable_list = [tuple([str(key), str(self.__dict__[key])]) for key in keys if key != 'properties']
        return hashable_list
    
    def __hash__(self):
        
        """
        Hashes CaseRelation. Returns a unique integer.
        """
        
        self_tuple = tuple(self.hashable_list())
        return hash(self_tuple)
    
    def __repr__(self):
        
        """
        Defines how CaseRelation objects are represented in string form.
        """
        
        keys = self.__dict__.keys()
        output = ''
        for key in keys:
            if key != 'properties':
                output = output + '\n' + str(key) + ': ' + str(self.__dict__[key])
        
        return output
        
    def __getitem__(self, index):
        
        """
        Retrieves an attribute using its key.
        """
        
        if index in self.source.keys():
            return self.source[index]
        
        if index in self.target.keys():
            return self.target[index]
        
        return self.__dict__[index]
    
        
    # Methods for exporting items to external files
    
    
    def to_edge(self, network = None):
        
        """
        Returns relationship as an igraph Edge object.
        """
        
        if network == None:
            network = Graph(n=2)
            network.vs['name'] = [self['source']['source_id'], self['target']['target_id']]
        
        edge = network.add_edge(self['source']['source_id'], self['target']['target_id'], name = self.name, category = self.category, attributes = self.attributes)
            
        return edge
        
        
class WebLink(CaseRelation):
    
    """
    This is a WebLink object: a rich format for representing URLs and adding functionality.
    
    Parameters
    ----------
    url : str
        weblink URL. Defaults to requesting user input.
    source_id : str
        ID of start-point object. Defaults to requesting user input.
    target_id : str
        ID of end-point object. Defaults to requesting user input.
    attributes : list
        a list of attributes. Defaults to None.
    parent_obj_path : str
        if relationship is an attribute, object path of parent object. Defaults to None.
    
    Attributes
    ----------
    name : str
        name for relationship.
    source : dict
        dictionary of data on source object. Contains source_id, source_obj, and source_addr.
    target : dict
        dictionary of data on target object. Contains target_id, target_obj, and target_addr.
    category : str
        category of relationship
    directed : bool
        whether the releationship has a direction.
    attributes : list
        a list of attributes.
    """
    
    def __init__(self, url = 'request_input', source_id = 'request_input', target_id = 'request_input', attributes = None, parent_obj_path = None):
        
        """
        Initialises WebLink instance.
        
        Parameters
        ----------
        url : str
            weblink URL. Defaults to requesting user input.
        source_id : str
            ID of start-point object. Defaults to requesting user input.
        target_id : str
            ID of end-point object. Defaults to requesting user input.
        attributes : list
            a list of attributes. Defaults to None.
        parent_obj_path : str
            if relationship is an attribute, object path of parent object. Defaults to None.
        """
        
        # Requesting URL from user input if none provided
        if url == 'request_input':
            url = input('URL: ')
        
        # Retrieving methods and attributes from CaseRelation class
        super().__init__(name = url, source = 'request_input', target = 'request_input', category = WebLink, directed = True, attributes = None, parent_obj_path = None)
        
        # Setting URL as name
        self.name = url
        
    def __repr__(self):
        
        """
        Defines how WebLinks are represented in string form.
        """
        
        output = self.name
        return str(output)
    
    def open_url(self):
        
        """Opens WebLink URL in default browser."""
        
        url = str(self.name)
        open_url(url)
    
    def domain(self):
        
        """Returns WebLink URL's domain."""
        
        return domain_splitter(self.name)
    
    def ip(self):
        
        """Fetches IP address associated with WebLink URL."""
        
        return ip_from_domain(self.name)
    
    def geocode(self):
        
        """Fetches geocode associated with WebLink URL's IP address."""
        
        ip = self.ip()
        return get_ip_geocode(ip)
    
    def coordinates(self):
        
        """Fetches coordinates associated with WebLink URL's IP address."""
        
        ip = self.ip()
        coords = get_ip_coordinates(ip).replace('[', '').replace(']', '').split(', ')
        return coords
    
    def whois(self):
        
        """Runs WhoIs lookup on WebLink URL."""
        
        return lookup_whois(self.name)

class Reference(CaseRelation):
    
    """
    This is a Reference object: a rich format for representing references between case objects and adding functionality.
    
    Parameters
    ----------
    name : str
        object name. Defaults to requesting user input.
    source_id : str
        ID of start-point object. Defaults to requesting user input.
    target_id : str
        ID of end-point object. Defaults to requesting user input.
    attributes : list
        a list of attributes. Defaults to None.
    parent_obj_path : str
        if relationship is an attribute, object path of parent object. Defaults to None.
    
    Attributes
    ----------
    name : str
        name for relationship.
    source : dict
        dictionary of data on source object. Contains source_id, source_obj, and source_addr.
    target : dict
        dictionary of data on target object. Contains target_id, target_obj, and target_addr.
    category : str
        category of relationship
    directed : bool
        whether the releationship has a direction.
    attributes : list
        a list of attributes.
    """
    
    def __init__(self, name = 'request_input', source_id = 'request_input', target_id = 'request_input', attributes = None, parent_obj_path = None):
        
        """
        Initialises Reference instance.
        
        Parameters
        ----------
        name : str
            object name. Defaults to requesting user input.
        source_id : str
            ID of start-point object. Defaults to requesting user input.
        target_id : str
            ID of end-point object. Defaults to requesting user input.
        attributes : list
            a list of attributes. Defaults to None.
        parent_obj_path : str
            if relationship is an attribute, object path of parent object. Defaults to None.
        """
        
        super().__init__(name = name, source = source, target = target, category = Reference, directed = True, attributes = None, parent_obj_path = None)

        
class Content(CaseRelation):
    
    """
    This is a Content object: a rich format for representing how case objects contain one another and adding functionality.
    
    Parameters
    ----------
    name : str
        object name. Defaults to requesting user input.
    source_id : str
        ID of start-point object. Defaults to requesting user input.
    target_id : str
        ID of end-point object. Defaults to requesting user input.
    attributes : list
        a list of attributes. Defaults to None.
    parent_obj_path : str
        if relationship is an attribute, object path of parent object. Defaults to None.
    parent_obj_path : str
        if relationship is an attribute of another object, object path for the parent object. 
    
    Attributes
    ----------
    name : str
        name for relationship.
    source : dict
        dictionary of data on source object. Contains source_id, source_obj, and source_addr.
    target : dict
        dictionary of data on target object. Contains target_id, target_obj, and target_addr.
    category : str
        category of relationship
    directed : bool
        whether the releationship has a direction.
    attributes : list
        a list of attributes.
    """
    
    def __init__(self, name = 'request_input', source = 'request_input', target = 'request_input', attributes = None, parent_obj_path = None):
        
        """
        Initialises Content instance.
        
        Parameters
        ----------
        name : str
            object name. Defaults to requesting user input.
        source_id : str
            ID of start-point object. Defaults to requesting user input.
        target_id : str
            ID of end-point object. Defaults to requesting user input.
        attributes : list
            a list of attributes. Defaults to None.
        parent_obj_path : str
            if relationship is an attribute, object path of parent object. Defaults to None.
        parent_obj_path : str
            if relationship is an attribute of another object, object path for the parent object. 
        """
        
        super().__init__(name = name, source = source, target = target, category = Content, directed = True, attributes = None, parent_obj_path = None)

        
class OwnerOf(CaseRelation):
    
    """
    This is an OwnerOf object. It represents an ownership relation where the source owns the target.
    
    Attributes
    ----------
    name : str
        name for relationship.
    source : dict
        dictionary of data on source object. Contains source_id, source_obj, and source_addr.
    target : dict
        dictionary of data on target object. Contains target_id, target_obj, and target_addr.
    category : str
        category of relationship
    directed : bool
        whether the releationship has a direction.
    attributes : list
        a list of attributes.
    """
    
    def __init__(self, name = 'request_input', source = 'request_input', target = 'request_input', attributes = None, parent_obj_path = None):
        
        super().__init__(name = name, source = source, target = target, category = OwnerOf, directed = True, attributes = None, parent_obj_path = None)

        
class OwnedBy(CaseRelation):
    
    """
    This is an OwnedBy object. It represents an ownership relation where the source is owned by the target.
    
    Attributes
    ----------
    name : str
        name for relationship.
    source : dict
        dictionary of data on source object. Contains source_id, source_obj, and source_addr.
    target : dict
        dictionary of data on target object. Contains target_id, target_obj, and target_addr.
    category : str
        category of relationship
    directed : bool
        whether the releationship has a direction.
    attributes : list
        a list of attributes.
    """
    
    def __init__(self, name = 'request_input', source = 'request_input', target = 'request_input', attributes = None, parent_obj_path = None):
        
        super().__init__(name = name, source = source, target = target, category = OwnedBy, directed = True, attributes = None, parent_obj_path = None)

        
class CitizenOf(CaseRelation):
    
    """
    This is an CitizenOf object. It represents an relation where the source is a citizen of the target.
    
    Attributes
    ----------
    name : str
        name for relationship.
    source : dict
        dictionary of data on source object. Contains source_id, source_obj, and source_addr.
    target : dict
        dictionary of data on target object. Contains target_id, target_obj, and target_addr.
    category : str
        category of relationship
    directed : bool
        whether the releationship has a direction.
    attributes : list
        a list of attributes.
    """
    
    def __init__(self, name = 'request_input', source = 'request_input', target = 'request_input', attributes = None, parent_obj_path = None):
        
        super().__init__(name = name, source = source, target = target, category = CitizenOf, directed = True, attributes = None, parent_obj_path = None)

class AuthorOf(CaseRelation):
    
    """
    This is an AuthorOf object. It represents an authorship relation where the source is the author of the target.
    
    Attributes
    ----------
    name : str
        name for relationship.
    source : dict
        dictionary of data on source object. Contains source_id, source_obj, and source_addr.
    target : dict
        dictionary of data on target object. Contains target_id, target_obj, and target_addr.
    category : str
        category of relationship
    directed : bool
        whether the releationship has a direction.
    attributes : list
        a list of attributes.
    """
    
    def __init__(self, name = 'request_input', source = 'request_input', target = 'request_input', attributes = None, parent_obj_path = None):
        
        super().__init__(name = name, source = source, target = target, category = AuthorOf, directed = True, attributes = None, parent_obj_path = None)

class AuthoredBy(CaseRelation):
    
    """
    This is an AuthoredBy object. It represents an authorship relation where the source has been authored by the target.
    
    Attributes
    ----------
    name : str
        name for relationship.
    source : dict
        dictionary of data on source object. Contains source_id, source_obj, and source_addr.
    target : dict
        dictionary of data on target object. Contains target_id, target_obj, and target_addr.
    category : str
        category of relationship
    directed : bool
        whether the releationship has a direction.
    attributes : list
        a list of attributes.
    """
    
    def __init__(self, name = 'request_input', source = 'request_input', target = 'request_input', attributes = None, parent_obj_path = None):
        
        super().__init__(name = name, source = source, target = target, category = AuthoredBy, directed = True, attributes = None, parent_obj_path = parent_obj_path)

class SourceFileOf(CaseRelation):
        
    """
    This is an SourceFileOf object. It represents a relation between a file and a Python object, where the file is the object's original source.
    
    Parameters
    ----------
    name : str
        name to assign SourceFileOf.
    source_obj_path : str
        object path for source CaseFile.
    target_obj_path : str
        object path for object derived from CaseFile.
    attributes : list
        list of attributes to assign to SourceFileOf.
    parent_obj_path : str
        if SourceFileOf is an attribute of another object, object path for the parent object.
    
    Attributes
    ----------
    name : str
        name for relationship.
    source : dict
        dictionary of data on source object. Contains source_id, source_obj, and source_addr.
    target : dict
        dictionary of data on target object. Contains target_id, target_obj, and target_addr.
    category : str
        category of relationship
    directed : bool
        whether the releationship has a direction.
    attributes : dict
        a dictionary of attributes containing data on the source file.
    """
    
    def __init__(self, name = 'request_input',
                 source_obj_path = 'request_input',
                 target_obj_path = 'request_input',
                 attributes = None, 
                 parent_obj_path = None):
        
        """
        Initialises a SourceFileOf instance.
        
        Parameters
        ----------
        name : str
            name to assign SourceFileOf.
        source_obj_path : str
            object path for source CaseFile.
        target_obj_path : str
            object path for object derived from CaseFile.
        attributes : list
            list of attributes to assign to SourceFileOf.
        parent_obj_path : str
            if SourceFileOf is an attribute of another object, object path for the parent object. 
        """
        
        if name == 'request_input':
            name = input('Object name: ')
        
        if source_obj_path == 'request_input':
            source_obj_path = input('Source object path: ')
        
        source_id = source_obj_path.split('.')[-1]
        
        if target_obj_path == 'request_input':
            target_obj_path = input('Target file path: ')
        
        target_id = target_obj_path.split('.')[-1]
        
        super().__init__(name = name, 
                 source_id = source_id,
                 source_addr = source_obj_path, 
                 target_id = target_id,
                 target_addr = target_obj_path, 
                 category = 'source file', 
                 directed = True, 
                 attributes = attributes, 
                 parent_obj_path = parent_obj_path)
        
        source_obj = eval(source_obj_path)
        
        self.attributes = {'source_filename': source_obj.name,
                           'source_filetype': source_obj.suffix,
                          'source_filepath': source_obj.path}
    
class CaseRelationSet(CaseObjectSet):
    
    """
    This is a collection of CaseRelations. 
    
    Parameters
    ----------
    obj_type : str
        type name for CaseRelationSet object.
    obj_name : str:
        name for CaseRelationSet object.
    parent_obj_path : str
        path for parent object if CaseRelationSet is an attribute.
    
    Attributes
    ----------
    properties : CaseObjectProperties
        metadata for CaseRelationSet object.
    
    Notes
    -----
        * Subclass of CaseObjectSet class.
    """
    
    def __init__(self, obj_type = 'CaseRelationSet', obj_name = None, parent_obj_path = None):
        
        """
        Initialises CaseRelationSet instance.
        
        Parameters
        ----------
        obj_type : str
            type name for CaseRelationSet object.
        obj_name : str:
            name for CaseRelationSet object.
        parent_obj_path : str
            path for parent object if CaseRelationSet is an attribute.
        """
        
        super().__init__(obj_name = obj_name, obj_type = obj_type, parent_obj_path = parent_obj_path)
        self.properties = CaseObjectProperties(obj_name = obj_name, obj_type = obj_type, parent_obj_path = parent_obj_path, size = None)
    
    def __repr__(self):
        
        """
        Defines how CaseObjectSets are represented in string forms.
        """
        
        contents = self.contents()
        
        output = '\n'
        for i in contents:
            rel = str(self.__dict__[i])
            output = output + rel + '\n'
    
        return output
    
    def __add__(self, obj):
        
        """
        Defines the functionality of addition operations on CaseRelationSets.
        
        Notes
        -----
            * CaseRelationSets can only have CaseRelations or other CaseRelationSets added to them.
            * Adding a CaseRelation to a set will add that relation to the collection of relations.
            * Adding a CaseRelationSet to another CaseRelationSet will produce a new CaseRelationSet that includes both sets' relations. 
        """
        
        new_rel_set = self.copy()
        
        if (type(obj) == CaseRelation) or (CaseRelation in obj.__class__.__bases__):
            
            obj_id = obj.properties.obj_id
            new_rel_set.__dict__[obj_id] = obj
            new_rel_set.update_properties()
            return new_rel_set
        
        if type(obj) == CaseRelationSet:
            
            contents = new_rel_set.contents()
            
            for rel_id in obj.contents():
                rel = obj.__dict__[rel_id]
                if rel_id not in contents:
                    new_rel_set.__dict__[rel_id] = rel
                else:
                    rel_id = rel_id + '_copy'
                    new_rel_set.__dict__[rel_id] = rel
                    
            new_rel_set.update_properties()
            return new_rel_set
        
        else:
            raise TypeError('CaseRelationSet objects can only be added to CaseRelation objects or CaseRelationSet objects')
    
    
    def to_network():
        ...