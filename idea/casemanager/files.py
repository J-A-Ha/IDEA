from .obj_properties import CaseObjectProperties
from .obj_superclasses import CaseObject, CaseObjectSet
from .relationships import CaseRelation, CaseRelationSet, SourceFileOf

import os
from os import stat_result
from pathlib import Path
from typing import List, Dict, Tuple
import copy

import numpy as np
import pandas as pd

def stat_file_to_dict(self):
    
    """
    Converts a stat_result object to a dictionary.
    """
    
    keys = ['mode', 'ino', 'dev', 'nlink', 'uid', 'gid', 'size', 'atime', 'mtime', 'ctime']
    
    dictionary = {}
    count = len(self)
    for i in range(0, count):
        dictionary[keys[i]] = self[i]
    
    return dictionary

stat_result.to_dict = stat_file_to_dict

def get_file_ext(filepath):
    
    """
    Takes a filepath and returns the file's extension.
    """
    
    filepath_str = str(filepath)
    path_obj = Path(filepath_str)
    
    is_dir = path_obj.is_dir()
    if is_dir == True:
        ext = None
    
    else:
        split_res = filepath_str.split('.')
        ext = split_res[-1]
    
    return ext
    
    

def get_filename(filepath):
    
    """
    Takes a filepath and returns the file's name.
    """
    
    filepath_str = str(filepath)
    filepath = filepath.strip().strip('/')
    split_res = filepath_str.split('/')
    end = split_res[-1]
    name = end.split('.')[0]
    
    return name

def check_filepath_type(path_obj):
    
    """
    Takes a Path object and checks the kind of directory object it leads to.
    """
    
    result = ''
    
    if path_obj.is_block_device() == True:
        result = 'block_device'
        
    if path_obj.is_char_device() == True:
        result = 'char_device'
    
    if path_obj.is_dir() == True:
        result = 'directory'
    
    if path_obj.is_fifo() == True:
        result = 'FIFO'
    
    if path_obj.is_file() == True:
        result = 'file'
    
    if path_obj.is_socket() == True:
        result = 'socket'
    
    if path_obj.is_symlink() == True:
        result = 'symlink'
    
    return result
    

class CaseFile(CaseObject):
    
    """
    This is a CaseFile object. It stores details about a digital file associated with a case.
    
    Parameters
    ----------
    obj_name : str or None
        name used for CaseFile object.
    filepath : str
        path used for retrieving file. Defaults to requesting user input.
    children : list
        list of filepaths for file's children in the directory.
    parent_obj_path = str or None
        path for parent object of CaseFile if CaseFile is an object attribute.
        
    Attributes
    ----------
    properties : CaseObjectProperties
        metadata for CaseFile object.
    relations : CaseRelationSet
        collection of CaseRelations associated with the CaseFile object.
    path : str
        directory path for directory object.
    name : str
        name for directory object.
    suffix : str
        extension for directory object (e.g. file type).
    type : str
        directory object type (e.g., 'file', 'folder').
    absolute : str
        the absolute filepath for the directory object.
    parent : str
        name of the directory object's parent object.
    root : str
        the root of the directory path.
    drive : str
        drive of the directory path.
    parts : list
        list of parts of the directory path.
    owner : str
        name of the directory object's owner.
    group : str
        name of the owner's group.
    children : list
        list of directory object's children.
    ...
    
    Notes
    -----
        * Intended to be assigned as an attribute of a CaseFileSet within a Case object.
        * Subclass of CaseObject class.
    """
    
    def __init__(self, obj_name = None, filepath: str = 'request_input', children: list = [], parent_obj_path = None):
        
        """
        Initialises CaseFile instance.
        
        Parameters
        ----------
        obj_name : str or None
            name used for CaseFile object.
        filepath : str
            path used for retrieving file. Defaults to requesting user input.
        children : list
            list of filepaths for file's children in the directory.
        parent_obj_path = str or None
            path for parent object of CaseFile if CaseFile is an object attribute.
        """
        
        super().__init__(obj_name = obj_name, obj_type = 'CaseFile', parent_obj_path = parent_obj_path)
        
        if filepath == 'request_input':
            filepath = input('File path: ')
        
        self.path = str(filepath)
        
        path_obj = Path(self.path)
        self.name = str(path_obj.name)
        self.suffix = str(path_obj.suffix)
        self.type = check_filepath_type(path_obj)
        self.absolute = str(path_obj.absolute())
        self.parent = str(path_obj.parent)
        self.root = str(path_obj.root)
        self.drive = str(path_obj.drive)
        self.parts = path_obj.parts
        self.owner = path_obj.owner()
        self.group = path_obj.group()
        
        metadata = path_obj.stat().to_dict()
        for key in metadata.keys():
            self.__dict__[key] = metadata[key]
        
        try:
            self.children = self.get_children()
        except:
            self.children = None
        
        self.properties = CaseObjectProperties(obj_name = obj_name, obj_type = 'CaseFile', parent_obj_path = parent_obj_path, size = None)
        
        self.relations = CaseRelationSet(obj_name = 'relations', parent_obj_path = self.properties.obj_path)
        
        self.properties.path = self.path
        self.update_properties()
    
    # Methods for editing and retrieving file
    
    def get_children(self):
        
        """
        Returns all child files of a CaseFile.
        """
        
        if self.type == 'directory':
            children = self.listdir()
            result = []
            path_obj = Path(self.path)
            for i in children:
                child = str(path_obj.joinpath(i))
                result.append(child)
        
        else:
            result = None
        
        return result
        
    def update_properties(self):
        
        """
        Updates CaseFile's properties.
        
        Updates
        -------
            * path
            * obj_id
            * obj_size
            * last_changed
            * hash
        """
        
        self.properties.path = self.path
        self.properties.obj_id = id(self)
        self.properties.obj_size = str(self.__sizeof__()) + ' bytes'
        self.properties.update_last_changed()
        self.properties.hash = self.__hash__()
    
    def __repr__(self):
        
        """
        Defines how CaseFiles are represented in string form.
        """
        
        return f'File name: {self.name}\nFile path: {self.path}\nFile extension: {self.suffix}\nType: {self.type}'

    
    def listdir(self):
        return os.listdir(self.path)
    
    def walk(self):
        return os.walk(self.path)
    
    def scandir(self):
        return os.scandir(self.path)
    

class CaseFileSet(CaseObjectSet):
    
    """
    This is a collection of CaseFile objects. 
    
    Parameters
    ----------
    obj_name : str
        name used for file set.
    parent_obj_path : str
        if item set is an attribute, object path of the parent object. Defaults to None.
    files : list
        iterable of CaseFiles to assign to collection. Defaults to an empty list.
    parent_obj_path = str or None
        path for parent object of CaseFileSet if CaseFileSet is an object attribute.
    
    Notes
    -----
        * Subclass of CaseObjectSet class.
        * Intended to assigned to all Case objects.
    """
    
    def __init__(self, obj_name = None, obj_path = None, files = [], parent_obj_path = None):
        
        """
        Initialises CaseFileSet instance.
        
        Parameters
        ----------
        obj_name : str
            name used for file set.
        parent_obj_path : str
            if item set is an attribute, object path of the parent object. Defaults to None.
        files : list
            iterable of CaseFiles to assign to collection. Defaults to an empty list.
        parent_obj_path = str or None
            path for parent object of CaseFileSet if CaseFileSet is an object attribute.
        """
        
        # Inheriting methods and attributes from CaseObjectSet class
        super().__init__(obj_name = obj_name, obj_type = 'CaseFileSet', parent_obj_path = parent_obj_path)
        
        self.properties = CaseObjectProperties(obj_name = obj_name, obj_type = 'CaseFileSet', parent_obj_path = parent_obj_path, size = None)
        
        # If only one file is provided, wrapping as list
        if type(files) == CaseFile:
            files = [files]
        
        # Adding files if provided
        for i in files:
            self.add_file(i)
        
        
        self.update_properties()
    
    
    # Methods for editing and retrieving file set properties
    
    def __repr__(self):
        
        """
        Defines how CaseFileSets are represented in string form.
        """
        
        contents = self.contents()
        output = f'\nFiles: {self.properties.file_count}\n\n'
        
        index = 0
        for file in contents:
            output = output + f'[{str(index)}] {file}\n'
            index += 1
        
        return output
    
    def update_properties(self):
        
        """
        Updates CaseFileSet's properties.
        
        Updates
        -------
            * obj_id
            * obj_size
            * file_count
            * last_changed
            * hash
        """
        
        self.properties.obj_id = id(self)
        self.properties.obj_size = str(self.__sizeof__()) + ' bytes'
        self.properties.update_last_changed()
        self.properties.hash = self.__hash__()
        self.properties.file_count = len(self.contents())
    
    
    
    def __setitem__(self, key, file):
        
        """
        Adds CaseFile to collection using a key name.
        
        WARNING: will not allow user to set 'properties' attribute.
        """
        
        if type(file) != CaseFile:
            raise TypeError('Key value assignment requires a CaseFile object')
            
        self.__dict__[key] = file
        self.update_properties()
    
    def __delitem__(self, key):
        
        """
        Deletes CaseFile in collection using a key.
        
        WARNING: will not allow user to delete collection's 'properties' attribute.
        """
        
        if key != 'properties':
            delattr(self, key)
            self.update_properties()
    
    def __add__(self, obj):
        
        """
        Defines the functionality of addition operations on CaseFileSets.
        
        Notes
        -----
            * CaseFileSets can only have CaseFiles or other CaseFileSets added to them.
            * Adding a CaseFile to a set will add that file to the collection of files.
            * Adding a CaseFileSet to another CaseFileSet will produce a new CaseFileSet that includes both sets' files. 
        """
        
        new_file_set = self.copy()
        
        if (type(obj) == CaseFile) or (CaseFile in obj.__class__.__bases__):
        
            new_file_set.add_file(obj)
            new_file_set.update_properties()
            return new_file_set
        
        if type(obj) == CaseFileSet:
            
            contents = new_file_set.contents()
            
            for filepath in obj.contents():
                file = obj.__dict__[filepath]
                if filepath not in contents:
                    new_file_set.__dict__[filepath] = file
                else:
                    filepath = filepath + '_copy'
                    new_file_set.__dict__[filepath] = file
                    
            new_file_set.update_properties()
            return new_file_set
        
        else:
            raise TypeError('CaseFileSet objects can only be added to CaseFile objects, subclasses of the CaseFile class, or CaseFileSet objects')
    
    
    def count_files(self):
        
        """
        Returns the number of CaseFiles in the collection.
        """
        
        return len(self.contents())
    
    def get_file(self, file_id):
        
        """
        Returns an file if given its name.
        """
        
        return self.__dict__[file_id]
    
    
    # Methods for adding files and data to file set
    
    
    def add_file(self, file = 'request_input'):
        
        """
        Adds a CaseFile to the collection. Returns the file.
        
        Parameters
        ----------
        file : CaseFile or str
            the file or file path to be added. Defaults to None; this adds a blank CaseFile.
        
        Returns
        -------
        file : CaseFile
            the added file.
        """
        
        if type(file) == CaseFile:
            file_obj = file
            obj_name = file.properties.obj_name
            
        else:
        
            obj_name = file
        
            if file == 'request_input':
                filepath = input('File path: ')
            else:

                if type(file) == str:
                    filepath = file
                else:
                    
                    if type(file) == Path:
                        filepath = file.path
                    else:
                        filepath = ''
                
            path_obj = Path(filepath)
            file_name = str(path_obj.name)
            file_name = file_name.replace('/', '_').replace('.', '_')
            parent = str(path_obj.parent.name)

            if (parent != None) and (parent != ''):
                parent = parent
                obj_name = parent + '__' + file_name
            else:
                obj_name = file_name
            obj_name = obj_name.replace('/', '_').replace('.', '_')
            if obj_name == '':
                obj_name = '_'
            file_obj = CaseFile(obj_name = obj_name, filepath = filepath, parent_obj_path = self.properties.obj_path)
        
        if file_obj not in self.__dict__.values():
            if obj_name in self.__dict__.keys():
                
                obj_name = obj_name + '_copy'
                
            self.__dict__[obj_name] = file_obj
        
        self.update_properties()
        
        return self.__dict__[obj_name]
    
    def add_files(self, files: list):
        
        """
        Adds multiple CaseFiles to the collection.
        
        Parameters
        ----------
        files : list
            list containing CaseFiles or file paths to be added.
        """
        
        for file in files:
            self.add_file(file)
    
    # Methods for deleting files and data from file set
    
    def delete_file(self, file_id = 'request_input'):
        
        """
        Deletes an file from the collection. Takes either a CaseFile or an file name string.
        """
        
        if file_id == 'request_input':
            file_id = input('File ID: ')
        
        delattr(self, file_id)
        self.update_properties()
    
    def delete_all(self):
        
        """
        Deletes all files from the collection.
        """
        
        files = self.contents()
        for file in files:
            self.delete_file(file)
        
        self.update_properties()
        
    def add_children(self):
        
        """
        Adds all files' immediate children to the CaseFile.
        """
        
        contents = self.contents()
        
        for i in contents:
            file = self.get_file(i)
            children = file.children
            if children != None:
                self.add_files(children)
    
    def add_all_children(self):
        
        """
        Scans the file directories of all CaseFiles and adds their children to the collection.
        """
        
        contents = self.contents()
        scanned = []
        current_file_names = set(contents)
        
        # Storing the file paths to scan in a specific order
        to_scan = queue.PriorityQueue()

        # Queing seeds with highest priority
        for file in contents:
            to_scan.put((0.0001, file))
        
        while not to_scan.empty():
        
            _, i = to_scan.get()
        
            file = self.get_file(i)
            scanned.append(file.path)
            children = file.children
            if children != None:
                self.add_files(children)
            
            new_file_names = set(self.contents()).difference(current_file_names)
            for file in new_file_names:
                to_scan.put((0.0001, file))
            
            current_file_names = self.contents()
        
        self.update_properties()
    
    def scan(self):
        
        """
        Scans the file directories of all CaseFiles and returns a list containing the file structure.
        """
        
        contents = self.contents()
        
        result = {}
        for i in contents:
            result[i] = list(self.get_file(i).walk())
        return result
        
    def dl_instagram_posts(username = 'request_input'):
        
        """
        Downloads all posts from an Instagram user profile and adds to file set.
        """
        
        download_user_posts(username = username)
        
        path = os.getcwd() + '/' + username
        
        self.add_file(path)
        self.add_all_children()