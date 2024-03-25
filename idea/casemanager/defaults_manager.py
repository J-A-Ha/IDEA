"""Functions for setting and interacting with global default case variables"""

from typing import List, Dict, Tuple

# Initialising global variables for handling defaults
DEFAULT_SET = False
DEFAULT_CASE_NAME = None

def set_default_case(case):
    
    """
    Sets a case as the default.
    
    Setting a default case means the selected case will be called whenever a function or method calls for 'default_case'. 
    This is the default behaviour for several functions if no case is inputted.
    """
    
    # Setting default case name to the string name of the variable given
    global DEFAULT_CASE_NAME 
    DEFAULT_CASE_NAME = case.varstr()
    
    # Updating environment to recognise that default has been set
    global DEFAULT_SET
    DEFAULT_SET = True
    
    # Updating environment to recognise that default has been set
    case.is_default = True
    
    # Backing up case
    case.backup()

def get_default_case_name():
    
    """
    Returns the default case's variable name.
    """
    
    global DEFAULT_CASE_NAME
    
    # Searching for default case name in globals. If found, returning name
    try:
        for entry in globals().keys():
            if entry == DEFAULT_CASE_NAME:
                return entry
    except:
        return None

        
def get_default_case():
    
    """
    Returns the default case.
    """
    
    global DEFAULT_CASE_NAME
    
    # Retrieving default case variable from globals
    try:
        return globals()[DEFAULT_CASE_NAME]
    
    except:
        return None



def is_default_case(case) -> bool:
    
    """
    Checks if case is set as the default case.
    """
    
    try:
        return case == get_default_case()
    
    except:
        return False
    

def check_default_case() -> str:

    """
    Checks if default case is set; if yes, returns its name.
    """
    
    if DEFAULT_CASE_NAME != None:
    
        global DEFAULT_SET
        DEFAULT_SET = True
        
        return print(f'The default case is: {DEFAULT_CASE_NAME}')
    
    else:
        
        DEFAULT_SET = False
        return (print('No default case set'))
    

def update_default_case():
    
    """
    Updates the default case.
    """
    
    case = globals()[DEFAULT_CASE_NAME]
    
    set_default_case(case)
    
    case.backup()
    
    return

def remove_default_case():
    
    """
    Resets the environment so there is no default case set.
    """
    
    global DEFAULT_CASE_NAME
    DEFAULT_CASE_NAME = None
    
    global DEFAULT_SET
    DEFAULT_SET = False