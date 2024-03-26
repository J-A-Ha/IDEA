"""Basic classes and functions."""

from typing import List, Dict, Tuple
import math
import copy

class Iterator:
    
    """
    Class to be invoked to enable objects to be iterated on.
    
    Parameters
    ----------
    obj : object
    """
    
    def __init__(self, obj):
        
        """
        Initialises iterator object.
        """
        
        self.obj = obj
        self.index_len = len(obj.__dict__.keys())
        self._current_index = 0    
    
    def __iter__(self):
        
        """
        Returns iterator object.
        """
        
        return self    
    
    def __next__(self):
        
        """
        Returns next item in iterator object.
        """
        
        attrs = list(self.obj.__dict__.keys())
        
        if self._current_index < self.index_len:
                attr_name = attrs[self._current_index]
                attr = self.obj.__dict__[attr_name]
                self._current_index += 1
                return attr
        
        raise StopIteration

        
def dict_to_str(item: dict) -> str:
    
    """
    Returns string representation of a dictionary's values.
    """
    
    return str(list(item.values()))

def inv_logit(value: float) -> float:
    
    """
    Returns the inverse logit of a numeric value.
    """
    
    output = math.exp(value) / (1 + math.exp(value))
    return output

def map_inf_to_1(number: float) -> float:
    
    """
    Maps a number to a range between 0 and 1, where 0 -> 0 and infinity -> 1.
    """

    return number / (1 + number)

def map_inf_to_0(number: float) -> float:
                     
    """
    Maps a number to a range between 0 and 1, where 0 -> 1 and infinity -> 0.
    """
    
    return 1 - map_inf_to_1(number)

def type_str(obj: object):
    
    """
    Returns the string representation of an object's type.
    """
                     
    type_str = str(type(obj)).replace('<', '').replace('>', '').replace('class ', '').replace("'", "").strip()
    
    return type_str