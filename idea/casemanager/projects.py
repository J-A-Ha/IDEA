from ..core.basics import Iterator
from ..exporters.general_exporters import export_obj, obj_to_folder

from .obj_properties import Properties
from .case import Case, CaseProperties

import os
import copy
from datetime import datetime
import pickle

class ProjectProperties(Properties):
    
    """This is a set of values representing global properties of a Project object
    
    Parameters
    ----------
    project_name : str 
        name of project
    file_location : str 
        directory address for source file.
    file_type : str 
        file type for source file.
    size : int 
        size of object in memory in bytes.
    
    Attributes
    ----------
    project_name : str 
        name of project
    file_location : str 
        directory address for source file.
    file_type : str 
        file type for source file.
    size : int 
        size of object in memory in bytes.
    created_at : str
        date and time Project was created.
    last_changed_at : str
        date and time Project was last edited.
    last_backup : str or datetime
        date and time Project was last edited.
    case_count : int
        the number of cases in the Project.
    """
        
    def __init__(
                    self, 
                    project_name = None, 
                    file_location = None, 
                    file_type = None, 
                    size = None
                ):
        
        """
        Initialises PropertiesProperties instance.
        
        Parameters
        ----------
        project_name : str 
            name of project
        file_location : str 
            directory address for source file.
        file_type : str 
            file type for source file.
        size : int 
            size of object in memory.
        """
        
        super().__init__()
        
        self.project_name = project_name
        self.created_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.last_changed_at = self.created_at
        self.last_backup = None
        self.size = size
        self.file_location = file_location
        self.file_type = file_type
        self.case_count = 0
        
        del self.obj_size
        del self.obj_path
        del self.obj_name
        
    
    def __repr__(self):
        
        """
        Defines how ProjectProperties objects are represented in string form.
        """
        
        self_dict = self.to_dict()
        output = '\n'
        for key in self_dict.keys():
            prop = self_dict[key]
            output = output + key + ': ' + str(prop) + '\n'
        
        return output
    
    
class Project:
    
    """
    This is a Project object. It is a collection of Case objects.
    
    Parameters
    ----------
    cases : list 
        an iterable of Case objects.
    """
    
    
    def __init__(self, cases = [], project_name = 'project', file_location = None, file_type = None):
        
        """
        Initialises a Project instance.
        
        Parameters
        ----------
        cases : list 
            an iterable of Case objects.
        """
        
        self.properties = ProjectProperties(project_name = project_name, file_location = file_location, file_type = file_type)
        self.description = ''
        self.add_cases(cases = cases)
        self.update_properties()
    
    def update_properties(self):
        
        """
        Updates Project's properties.
        
        Updates
        -------
            * obj_id
            * case_count
            * size
            * last_changed
        """
        
        self.properties.obj_id = id(self)
        self.properties.case_count = self.case_count()
        self.properties.size = str(self.__sizeof__()) + ' bytes'
        self.properties.update_last_changed()
    
    def __repr__(self):
        
        """
        Defines how Projects are represented in string form.
        """
        
        output = f'\nProperties:\n{self.properties}\n\nDescription:\n{self.description}\n\nContents:\n{self.contents()}\n\n\n---------------------\nCases:\n---------------------\n\n'
        cases = self.cases()
        
        for case_name in cases:
            case_obj = self.get_case(case_name)
            output = output + f'{case_name}:\n{case_obj}\n---------------------\n'
        
        return output
            
        
        
    def __iter__(self):
        
        """
        Implements iteration functionality for Project objects.
        """
        
        return Iterator(self)
    
    def __getitem__(self, case_name):
        
        """
        Retrieves Case using its name.
        """
        
        if case_name != 'properties':
            return self.__dict__[case_name]
    
    def contents(self):
        
        """
        Returns the Project's attributes as a list. Excludes object properties attribute.
        """
        
        return [i for i in self.__dict__.keys() if (i != 'properties')]
    
    def case_count(self):
        
        """
        Returns the number of Case objects in the project.
        """
        
        attrs = [i for i in self.__dict__.keys() if ((i != 'properties') and (i != 'description'))]
        
        return len(attrs)
        
    def to_list(self):
        
        """
        Returns the Project as a list.  Excludes the Project's 'properties' attribute.
        """
        
        return [i for i in self]
    
    def to_dict(self):
        
        """
        Returns the Project as a dictionary.  Excludes the Project's 'properties' attribute.
        """
        
        output_dict = {}
        for index in self.__dict__.keys():
            output_dict[index] = self.__dict__[index]
        
        return output_dict
    
    def copy(self):
        
        """
        Returns the a copy of the Project.
        """
        
        return copy.deepcopy(self)
    
    def get_case(self, case_name):
        
        """
        Returns a Case when given its attribute name.
        """
        
        return self.__dict__[case_name]
    
    def get_name_str(self):
        
        """
        Returns the Project's variable name as a string. 
        
        Notes
        -----
            * Searches global environment dictionary for objects sharing Project's ID. Returns key if found.
            * If none found, searches local environment dictionary for objects sharing Project's ID. Returns key if found.
        """
        
        for name in globals():
            if id(globals()[name]) == id(self):
                return name
        
        for name in locals():
            if id(locals()[name]) == id(self):
                return name
    
    def varstr(self):
        
        """
        Returns the Project's name as a string. Defaults to using its variable name; falls back to using its name property.
        
        Notes
        -----
            * Searches global environment dictionary for objects sharing Project's ID. Returns key if found.
            * If none found, searches local environment dictionary for objects sharing Project's ID. Returns key if found.
            * If none found, returns Project's name property.
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
    
    def add_case(self, case = None, case_name = 'from_obj'):
        
        """
        Adds a Case object to the Project.
        
        Parameters
        ----------
        case  : Case 
            the Case object to be added. Defaults to None; this adds a blank Case.
        case_name : str 
            the Case's name. This will become its attribute name. Defaults to None.
            If none set, tries to retrieve details from Case's properties.
        """
        
        if case == None:
            if case_name == 'from_obj':
                case_name = ''
            return self.add_blank_case(case_name = case_name)
        
        else:
            if case_name == 'from_obj':
                case_name = case.properties.case_name


            case.properties.project = self.varstr()

            self.__dict__[case_name] = case
            self.get_case(case_name).properties.case_name = case_name
            self.get_case(case_name).properties.obj_path = self.properties.project_name + '.' + case_name
            self.get_case(case_name).update_properties()
            self.update_properties()
            
            return
    
    def add_blank_case(self, case_name = 'request_input'):
        
        """
        Adds a blank Case object to the Project.
        
        Parameters
        ----------
        case_name : str 
            the Case's name. This will become its attribute name. Defaults to None.
            If none set, tries to retrieve details from Case's properties.
        """
        
        if case_name == 'request_input':
            case_name = input('Case name: ')
        
        if case_name == '':
            case_name = f'case_{str(self.case_count()+1)}'
            
        case_obj = Case(case_name = case_name, project = self.properties.project_name)
        case_obj.properties.project = self.varstr()
        
        self.__dict__[case_name] = case_obj
        self.get_case(case_name).properties.case_name = case_name
        self.get_case(case_name).properties.obj_path = self.properties.project_name + '.' + case_name
        self.get_case(case_name).update_properties()
        self.update_properties()
        
        
    def add_cases(self, cases):
        
        """
        Adds multiple Case objects to the Project.
        
        Parameters
        ----------
        cases : list 
            an iterable of Case objects to add.
        """
        
        if type(cases) == Case:
            self.add_case(cases)
        
        elif type(cases) == list:
            for c in cases:
                self.add_case(c)
        
        self.update_properties()
    
    
    def cases(self):
        
        """
        Returns all Case objects in the project as a list.
        """
        
        return [i for i in self.__dict__.keys() if (
                                                    (i != 'properties')
                                                    and (i != 'description')
                                                    )
                                                       ]
    
    
    def export_txt(self, file_name = 'request_input', file_address = 'request_input'):
        
        """
        Exports the Project to a .txt file.
        
        Parameters
        ----------
        file_name : str
            name of file to create. Defaults to using the object's variable name.
        file_address : str
            directory address to create file in. defaults to requesting for user input.
        """
        
        if file_name == 'request_input':
            file_name = input('File name: ')
            
        if file_address == 'request_input':
            file_address = input('File address: ')
            
        file_address = file_address + '/' + file_name

        if file_address.endswith('.project') == False:
            file_address = file_address + '.project'

        with open(file_address, 'wb') as f:
            pickle.dump(self, f) 
    
    def export_folder(self, folder_name = 'request_input', folder_address = 'request_input', export_str_as = 'txt', export_dict_as = 'json', export_pandas_as = 'csv', export_network_as = 'graphML'):
        
        """
        Exports Project's contents to a folder.
        
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
        
        if folder_name == 'request_input':
            folder_name = input('Folder name: ')
        
        if folder_name.endswith('_project') == False:
            folder_name = folder_name + '_project'
        
        obj_to_folder(self, folder_name = folder_name, folder_address = folder_address, export_str_as = export_str_as, export_dict_as = export_dict_as, export_pandas_as = export_pandas_as, export_network_as = export_network_as)

    
    def save_as(self, file_name = 'request_input', file_address = 'request_input', file_type = 'request_input'):
        
        """
        Saves the Project to a file or folder.
        
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
            * 'project': saves to a .project file. This is a specially labelled pickled .txt file.
            * 'text' or 'txt': saves to a pickled .txt file.
            * 'pickle': saves to pickled .txt file.
            * 'Excel': saves to a folder of .xlsx files.
            * 'xlsx': saves to a folder of .xlsx files.
            * 'csv': saves to a folder of folders of .csv files.
            * 'folder': saves to a folder.
        """
        
        if file_name == 'request_input':
            file_name = input('File name: ')

        if file_type == 'request_input':
            file_type = input('File type: ')
        
        if file_address == 'request_input':
            file_address = input('File address: ')
        
        file_type = file_type.strip().strip('.').strip().lower()
        
        
        if (file_type == None) or (file_type.lower().strip('.').strip() == '') or (file_type.lower().strip('.').strip() == '.project') or (file_type.lower().strip('.').strip() == 'project') or (file_type.lower().strip('.').strip() == 'text') or (file_type.lower().strip('.').strip() == 'txt') or (file_type.lower().strip('.').strip() == 'pickle'):
            
            self.export_txt(file_name = file_name, file_address = file_address)
        
        
        if (file_type.lower().strip('.').strip() == 'excel') or (file_type.lower().strip('.').strip() == 'xlsx'):

            file_address = file_address + '/' + file_name
            os.mkdir(file_address)
            cases = self.cases()
            for i in cases:
                self.get_case(i).export_excel(new_file = True, file_name = i, file_address = file_address)
        
        
        if (file_type.lower().strip('.').strip() == 'csv') or (file_type.lower().strip('.').strip() == 'csvs'):
            
            file_address = file_address + '/' + file_name
            os.mkdir(file_address)
            cases = self.cases()
            for i in cases:
                self.get_case(i).export_csv_folder(folder_address = file_address, folder_name = file_name)
    
    
    def save(self, save_as = None, file_type = None, save_to = None):
        
        """
        Saves the Project to its source file. If no source given, saves to a new file.
        
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
            * 'project': saves to a .project file. This is a specially labelled pickled .txt file.
            * 'text' or 'txt': saves to a pickled .txt file.
            * 'pickle': saves to pickled .txt file.
            * 'Excel': saves to a folder of .xlsx files.
            * 'xlsx': saves to a folder of .xlsx files.
            * 'csv': saves to a folder of folders of .csv files.
            * 'folder': saves to a folder.
        """
        
        if save_as == None:
            
            try:
                save_as = self.properties.file_location.split('/')[-1].split('.')[0]
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