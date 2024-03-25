"""Classes and functions for storing backups of cases"""

from ..core.basics import type_str
from .defaults_manager import DEFAULT_SET, DEFAULT_CASE_NAME, set_default_case, get_default_case_name, get_default_case, is_default_case, check_default_case, update_default_case

from typing import List, Dict, Tuple
import copy
from datetime import datetime
import pandas as pd


class Backups:

    """This is a backups object. It stores backup copies of case objects and their attributes for easy data recovery."""
    
    def __init__(self):
        
        """
        Initialises Backups instance.
        """
        
        self.directory = {}
        self.registry = pd.DataFrame(columns = ['location', 'case', 'created_at'])
        self.most_recent = None
    
    def __repr__(self):
        
        """
        Defines how Backups objects are represented in string form.
        """
        
        reg = self.registry.copy(deep=True)
        reg = reg.set_index('location')
        output = str(reg)
        
        return output
    
    def copy(self):
        
        """
        Returns a copy of Backups object.
        """
        
        return copy.deepcopy(self)
    
    ## Creating and accessing backup case files

    def new_backup(self, case = 'default_case'):
        
        """
        Creates a new case backup.
        """
        
        # If no case provided, retrieving default case
        global DEFAULT_CASE_NAME
        if case == 'default_case':
            case_name = DEFAULT_CASE_NAME
            
            # Retrieving case name
            case = get_default_case()
        
        # Checking type; raising error if not case
        else:
            type_string = type_str(case)
            
            if type_string.endswith('.Case'):
                
                # Retrieving case name
                case_name = case.get_name_str()
                
            else:
                raise TypeError('Inputted item must be of type "Case"')
        
        # Assigning save location in directory
        location = len(self.directory.keys()) + 1
        
        # Adding save to directory
        self.directory[location] = case.copy()
        
        # Recording when last case backup was made
        global LAST_BACKUP_DT
        LAST_BACKUP_DT = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Assigning position in backups registry
        index = len(self.registry.index)
        self.registry.loc[index] = [location, case_name, LAST_BACKUP_DT]
        
    
    def __getitem__(self, index):
        
        """
        Retrieves case backup.
        
        Parameters
        ----------
        index : Case, str or int
            a Case, case name (str), or directory location (int).
        
        Returns
        -------
        result : Case
            a case backup.
        """
        
        # Checking type of index
        index_type = type(index)
        type_string = type_str(index)
        if (type_string.endswith('Case') == False) and (index_type != str) and (index_type != int):
            raise TypeError('Index must be a Case, string, or integer')
        
        # Ensuring list-like integer indexing behaviour works with directory structure
        if (index_type == int) and (index < 0):
            index = len(self.directory.keys()) + index
        
        # If index is a known directory location, returning backup
        if index in self.directory.keys():
            return self.directory[index]
        
        # Re-checking type of index
        index_type = type(index)
        type_string = type_str(index)
        
        # If index is a Case object or case name, retrieving most recent case backup
        if (type_string.endswith('Case')) or (index_type == str):
            return self.get_most_recent(index)
        
        # Raising an error for all other scenarios
        raise KeyError(f'"{index}" not found in backups')
    
    def update_backup(self, case = 'default_case'):
    
        """
        Overwrites latest case backup with new backup.
        """
    
        # Retrieving default case if no case given
        if case == 'default_case':
            global DEFAULT_CASE_NAME
            case_name = DEFAULT_CASE_NAME
            case = get_default_case()
        
        # Checking if object passed is a Case object
        else:
            type_string = type_str(case)
            if type_string.endswith('.Case'):
                case_name = case.get_name_str()
            else:
                raise TypeError('Inputted item must be of type "Case"')
        
        # Checking if case is in registry; raising error if not
        if case_name not in self.registry['case'].values:
            return KeyError(f'No backups found for "{case_name}"')
        
        # Retrieving most recent backup for case
        case_backups = self.registry[self.registry['case'] == case_name].sort_values('created_at', ascending=False).reset_index().drop('index', axis=1)
        last_backup = case_backups.iloc[0]
        backup_loc = last_backup['location']
        
        # Overwriting most recent backup
        self.directory[backup_loc] = case.copy()
        
        # Retrieving index for new backup
        try:
            index = self.registry[self.registry['location'] == backup_loc].index[0]
        except:
            return ValueError(f'No backups found for "{case_name}"')
        
        # Resetting datetime for most recent backup
        global LAST_BACKUP_DT
        LAST_BACKUP_DT = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.registry.loc[index, 'created_at'] = LAST_BACKUP_DT
        
    
    def save_backup(self, case = 'default_case'):
        
        """
        Creates backup of case.
        
        Notes
        -----
        Functions by checking if case has been backed up previously.
            * If yes: overwrites latest case backup with new backup.
            * If no: creates new backup in new directory location
        """
        
        # Retrieving default case if no case given
        if case == 'default_case':
            global DEFAULT_CASE_NAME
            case_name = DEFAULT_CASE_NAME
            case = get_default_case()
        
        
        else:
            # Checking if object passed is a Case object
            type_string = type_str(case)
            if type_string.endswith('Case'):
                case_name = case.get_name_str()
            else:
                raise TypeError('Inputted item must be of type "Case"')
        
        # Checking if case has been backed up
        if case_name in self.registry['case'].values:
            
            # If true, overwriting last backup
            self.update_backup(case = case)
        
        else:
            # If false, creating new backup in new directory location
            self.new_backup(case = case)
        
        
    def last(self, case = 'all'):
        
        """
        Returns the most recent backup.
        
        Parameters
        ----------
        case : str or Case
            which case or set of cases to search for backups. Defaults to all backed up cases.
        
        Returns
        -------
        result : Case
            the most recent case backup.
        """
        
        # If case set to all, returning most recent backup as recorded by the registry
        if case == 'all':
            series = self.registry.sort_values(by = 'created_at', ascending=False).iloc[0]
            location = series['location']
            case_item = self.directory[location]
            
            return (series, case_item)
        
        # Otherwise, returning most recent backup from subset of backups
        else:
            
            # Retrieving default case if no case given
            if case == 'default_case':
                global DEFAULT_CASE_NAME
                case_name = DEFAULT_CASE_NAME
                case = get_default_case()
            
            else:
                # Checking if object passed is a Case object
                type_string = type_str(case)
                if type_string.endswith('Case'):
                    case_name = case.get_name_str()
                else:
                    raise TypeError('Inputted item must be of type "Case"')
        
            
            # Retrieving most recent backup for case
            df = self.registry[self.registry['case'] == case_name]
            series = df.sort_values(by = 'created_at', ascending=False).iloc[0]
            location = series['location']
            case_item = self.directory[location]
            
            return (series, case_item)
        
    def overwrite_backup(self, case = 'default_case', backup = 'all_last'):
        
        """
        Overwrites a selected case backup with new backup.
        
        Parameters
        ----------
        case : str or Case
            the case to backup. Defaults to the default case if set.
        backup: str or int 
            which backup or backups to overwrite.
        """
        
        # Retrieving default case if no case given
        if case == 'default_case':
            global DEFAULT_CASE_NAME
            case_name = DEFAULT_CASE_NAME
            case = get_default_case()
            
        else:
            # Checking if object passed is a Case object
            type_string = type_str(case)
            if type_string.endswith('Case'):
                
                # If so, retrieving variable's name
                case_name = case.get_name_str()
            
            # If object passed is a string, assuming this is a case name 
            if type(case) == str:
                case_name = case
            
            else:
                raise TypeError('Inputted item must be of type "Case" or string')
        
        # If all_last backups selected, retrieving most recent backup location.
        if backup == 'all_last':
            location = self.last(case = 'all')[0]['location']
        
        else:
            # Otherwise, selecting specific backup
            location = backup
        
        # Ovewriting backup
        self.directory[location] = case.copy()
        index = self.registry[self.registry['location'] == location].index[0]
        self.registry.loc[index, 'case'] = case_name
        
        # Resetting datetime for most recent backup
        global LAST_BACKUP_DT
        LAST_BACKUP_DT = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.registry.loc[index, 'created_at'] = LAST_BACKUP_DT
        
        
    def all_most_recent(self) -> pd.DataFrame:
        
        """
        Returns the most recent backups for all cases in a dataframe.
        """
        
        # Creating output dataframe
        result = pd.DataFrame(columns = ['location', 'case', 'created_at'])
        
        # Identifying case names
        unique_cases = set(self.registry['case'].values)
        
        # Iterating through case names and retrieving most recent backup details
        for i in unique_cases:
            row = self.registry[self.registry['case'] == i].sort_values(by = 'created_at', ascending=False).iloc[0]
            index = len(result.index)
            
            # Appending to output dataframe
            result.loc[index] = row
        
        return result
        
    
    def list_all(self):
        
        """
        Returns a dataframe of all backups.
        """
        
        return self.registry
    
    
    def get_backups(self, case = 'default_case'):
        
        """
        Returns a dataframe of a case's backups.
        """
        
        # Retrieving default case name if no name case given
        if case == 'default_case':
            global DEFAULT_CASE_NAME
            case_name = DEFAULT_CASE_NAME
            case = get_default_case()
            
        else:
            # Checking if object passed is a Case object
            type_string = type_str(case)
            if type_string.endswith('Case'):
                # If so, retrieving variable's name
                case_name = case.get_name_str()
            
            else:
                # If object passed is a string, assuming this is a case name 
                if type(case) == str:
                    case_name = case
            
                else:
                    raise TypeError('Inputted item must be of type "Case" or string')
        
        
        # Retrieving backups details by masking and sorting registry dataframe
        result = self.registry[self.registry['case'] == case_name].sort_values('created_at', ascending=False)
        
        return result
    
    
    def get_most_recent(self, case = 'default_case'):
        
        """
        Returns a case's most recent backup.
        """
        
        # Retrieving case's backups sorted by most recent
        registry_df = self.get_backups(case = case).reset_index().drop('index', axis=1)
        
        # Identifying most recent
        key = registry_df.iloc[0,0]
        
        # Retrieving backup
        backup = self.directory[key]
        
        return backup
        

        
# Functions for retrieving and accessing backups


def get_backups(index = None):
    
    """
    Returns the Backups directory and registry.
    """
    
    global BACKUPS
    
    if index == None:
        return BACKUPS
    
    else:
        return BACKUPS[index]

BACKUPS = Backups()