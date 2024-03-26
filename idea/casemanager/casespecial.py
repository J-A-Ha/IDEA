from .obj_properties import CaseObjectProperties
from .obj_superclasses import CaseAttr, CaseObject
from .relationships import CaseRelation, SourceFileOf, CaseRelationSet
from .files import stat_result, CaseFile, CaseFileSet

class CaseSpecial(CaseObject):
    
    """
    This is a superclass for CaseItem, CaseEntity, and CaseEvent classes.
    
    Parameters
    ----------
    obj_name : str
        name for CaseSpecial object.
    obj_type : str
        type name for object. Defaults to 'CaseSpecial'.
    parent_obj_path : str
        path for parent object of CaseSpecial if CaseSpecial is an object's attribute.
    
    Attributes
    ----------
    properties : CaseObjectProperties
        metadata for CaseSpecial object.
    files : CaseFileSet
        CaseFiles associated with CaseSpecial object.
    relations : CaseRelationSet
        CaseRelations associated with CaseSpecial object.
    
    Notes
    -----
        * Subclass of CaseObject class.
    """
    
    def __init__(self, obj_name = None, obj_type = 'CaseSpecial', parent_obj_path = None):
        
        """
        Initialises CaseSpecial instance.
        
        Parameters
        ----------
        obj_name : str
            name for CaseSpecial object.
        obj_type : str
            type name for object. Defaults to 'CaseSpecial'.
        parent_obj_path : str
            path for parent object of CaseSpecial if CaseSpecial is an object's attribute.
        """
        
        super().__init__(obj_name = obj_name, obj_type = obj_type, parent_obj_path = parent_obj_path)
        self.properties = CaseObjectProperties(obj_name = obj_name, obj_type = 'CaseSpecial', parent_obj_path = parent_obj_path, size = None)
        self.files = CaseFileSet(obj_name = 'files', parent_obj_path = self.properties.obj_path, files = [])
        self.relations = CaseRelationSet(obj_name = 'relationships', parent_obj_path = self.properties.obj_path)
        
    
    def __repr__(self):
        
        """
        Defines how CaseSpecial subclasses are represented in string form.
        """
        
        output = '\n' + str(self.properties)
        return output