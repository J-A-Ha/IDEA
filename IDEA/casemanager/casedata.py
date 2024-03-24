from ..core.cleaners import str_to_datetime, join_df_col_lists_by_semicolon
from ..location.geolocation import get_coordinates_location, get_location_coordinates, get_coordinates_geocode, get_location_geocode, coordinates_distance
from ..internet.webanalysis import get_ip_coordinates, get_ip_physical_location, domain_from_ip, ip_from_domain, domains_whois, ips_whois
from .obj_properties import CaseObjectProperties
from .obj_superclasses import CaseObjectSet
from .relationships import CaseRelation, SourceFileOf, CaseRelationSet
from .files import stat_result, CaseFile, CaseFileSet

from typing import List, Dict, Tuple
import os
import copy
import pickle
from datetime import timedelta

import numpy as np
import pandas as pd



class CaseKeywords(CaseObjectSet):
    
    """
    This is a collection of Case keyword dataframes. 
    
    Parameters
    ----------
    obj_name : str
        name for CaseKeywords object.
    parent_obj_path : str
        path for parent object of CaseKeywords object. This should be a CaseData object.
    
    Attributes
    ----------
    properties : CaseObjectProperties
        metadata associated with the CaseKeywords object.
    frequent_words : pandas.DataFrame
        a dataframe containing keywords ranked by frequency.
    central_words : pandas.DataFrame
        a dataframe containing keywords ranked by centrality in the case's words coincidence network.
        
    Notes
    -----
        * Subclass of CaseObjectSet class.
        * Intended to assigned to all CaseData objects.
    """
    
    def __init__(self, obj_name = None, parent_obj_path = None):
        
        """
        Initialises CaseKeywords instance.
        
        Parameters
        ----------
        obj_name : str
            name for CaseKeywords object.
        parent_obj_path : str
            path for parent object of CaseKeywords object. This should be a CaseData object.
        """
        
        # Inheriting methods and attributes from CaseObjectSet class
        super().__init__(obj_name = obj_name, obj_type = 'CaseKeywords', parent_obj_path = parent_obj_path)
        
        
        # Creating dataframes
        freq_cols = ['frequency', 'found_in', 'found_in_count', 'frequency_per_item', 'breakdown']
        self.frequent_words = pd.DataFrame(columns = freq_cols)
        
        central_cols = ['weighted_degree', 'degree', 'eigencentrality', 'betweenness']
        self.central_words = pd.DataFrame(columns = central_cols)
    
    
    # Methods for editing and retrieving keyword set properties
    
    def __repr__(self):
        
        """
        Defines how CaseKeywords objects are represented in string form.
        """
        
        return f'\nWord count: {self.__len__()}\n\nFrequent words (top 20):\n{self.frequent_words.head(20)}\n\nCentral words (top 20):\n{self.central_words.head(20)}\n'
    
    def __len__(self):
        
        """
        Returns the number of keywords in the collection.
        """
        
        return len(self.all_keywords())
    
    def all_keywords(self, head = 100):
        
        """
        Returns a list of all keywords in the collection.
        """
        
        return list(set(self.frequent_words.index).union(set(self.central_words.index)))
    
    
class CaseData(CaseObjectSet):
    
    """This is a collection containing the combined data for a Case. 
    
    Parameters
    ----------
    obj_name : str
        ID used for item set.
    parent_obj_path : str
        if CaseData object is an attribute, object path of object is attribute of. Defaults to None.
    data : pandas.DataFrame
        dataframe of item data to assign.
    metadata : pandas.DataFrame
        dataframe of item metadata to assign.
    information : pandas.DataFrame
        dataframe of item information to assign.
    other : pandas.DataFrame
        dataframe of item links, references, and contents to assign.
    coinciding_data : dict
        a dictionary of dataframes indexing coinciding data.
    keywords : CaseKeywords
        a CaseKeywords object containing keywords associated with items. 
    
    Attributes
    ----------
    properties : CaseObjectProperties
        metadata for the CaseData object.
    data : pandas.DataFrame
        a dataframe of data entries associated with items.
    metadata : pandas.DataFrame
        a dataframe of metadata entries associated with items.
    information : pandas.DataFrame
        a dataframe of information entries associated with items.
    other : pandas.DataFrame
        a dataframe of links, references, and contents entries associated with items.
    coinciding_data : dict
        a dictionary of dataframes indexing coinciding data.
    keywords : CaseKeywords
        a CaseKeywords object containing keywords associated with items. 
    
    Notes
    -----
        * Subclass of CaseObjectSet class.
        * Intended to assigned to all Case objects.
    """
    
    def __init__(self,
                 obj_name = None,
                 parent_obj_path = None,
                 data = None, 
                 metadata = None, 
                 information = None, 
                 other = None, 
                 coinciding_data = {}, 
                 keywords = None
                ):
        
        """
        Initialises CaseData instance.
        
        Parameters
        ----------
        obj_name : str
            ID used for item set.
        parent_obj_path : str
            if item set is an attribute, object path of object is attribute of. Defaults to None.
        data : pandas.DataFrame
            dataframe of item data to assign.
        metadata : pandas.DataFrame
            dataframe of item metadata to assign.
        information : pandas.DataFrame
            dataframe of item information to assign.
        other : pandas.DataFrame
            dataframe of item links, references, and contents to assign.
        coinciding_data : dict
            a dictionary of dataframes indexing coinciding data.
        keywords : CaseKeywords
            a CaseKeywords object containing keywords associated with items. 
        """
        
        # Inheriting methods and attributes from CaseObjectSet class
        super().__init__(obj_name = obj_name, obj_type = 'CaseData', parent_obj_path = parent_obj_path)
        
        self.properties = CaseObjectProperties(obj_name = obj_name, obj_type = 'CaseData', parent_obj_path = parent_obj_path, size = None)
        
        if data == None:
            self.data = pd.DataFrame(columns = ['html', 'text', 'image', 'video', 'audio'])
        elif type(data) == pd.DataFrame:
            self.data = data
        
        if metadata == None:
            self.metadata = pd.DataFrame(columns = ['name',
                                                     'data_id',
                                                    'hash',
                                                     'description',
                                                     'type',
                                                     'format',
                                                     'size',
                                                     'source',
                                                     'domain',
                                                    'url',
                                                     'created_at',
                                                     'created_by',
                                                     'last_changed_at',
                                                     'last_changed_by',
                                                     'uploaded_at',
                                                     'uploaded_by',
                                                     'region',
                                                     'location',
                                                        'address',
                                                     'coordinates',
                                                   'language']
                                        )
        elif type(metadata) == pd.DataFrame:
            self.metadata = metadata
        
        if information == None:
            self.information = pd.DataFrame(columns = ['names',
                                                        'people',
                                                        'organisations',
                                                        'regions',
                                                        'places',
                                                        'coordinates',
                                                        'time periods',
                                                        'date_times',
                                                        'events',
                                                        'activities',
                                                        'symbols',
                                                        'weather',
                                                        'objects',
                                                        'languages'])
        elif type(information) == pd.DataFrame:
            self.information = information
        
        if other == None:
            self.other = pd.DataFrame(columns = ['links', 'references', 'contents', 'other'])
        elif type(other) == pd.DataFrame:
            self.other = other
        
        if coinciding_data == None:
            self.coinciding_data = {}
        elif type(coinciding_data) == dict:
            self.coinciding_data = coinciding_data
        
        if keywords == None:
            self.keywords = CaseKeywords(obj_name = 'keywords', parent_obj_path = self.properties.obj_path)
        elif type(keywords) == CaseKeywords:
            keywords.properties.obj_type = self.properties.obj_path + '.' + 'keywords'
            self.keywords = keywords
        
        self.update_properties()
    
    # Methods for editing and retrieving data set properties
    
    def get_dataframe(self, frame_name = 'request_input'):
        
        """
        Returns a dataframe if given its attribute name.
        """
        
        if frame_name == 'request_input':
            frame_name = input('Dataset name: ')
        
        return self.__dict__[frame_name]
    
    def update_properties(self):
        
        """
        Updates CaseData object's properties.
        
        Updates
        -------
            * obj_id
            * obj_size
            * data_entries_count
            * metadata_entries_count
            * information_entries_count
            * other_entries_count
            * last_changed
            * hash
        """
        
        self.properties.obj_id = id(self)
        self.properties.data_entries_count = len(self.data.index)
        self.properties.metadata_entries_count = len(self.metadata.index)
        self.properties.information_entries_count = len(self.information.index)
        self.properties.other_entries_count = len(self.other.index)
        self.properties.obj_size = str(self.__sizeof__()) + ' bytes'
        self.properties.update_last_changed()
        self.properties.hash = self.__hash__()
        
    def __repr__(self):
        return f'\nData:\n{self.data}\n\nMetadata:\n{self.metadata}\n\nInformation:\n{self.information}\n\nOther:\n{self.other}\n\nCoinciding data:\n{self.coinciding_data}\n\nKeywords:\n{self.keywords}\n'
    
    def __len__(self):
        return len(self.__dict__.keys())
    
    
    # Methods for retrieving data
    
    def get_items_set(self):
        
        """
        Returns all item IDs found in dataframes as a set.
        """
        
        df_names = ['metadata', 'data', 'information', 'other']
        index_sets = []

        for df_name in df_names:
            
            df = self.get_dataframe(df_name)
            if type(df) == pd.DataFrame:
                index_set = set(df.index)
                index_sets.append(index_set)

        indexes = set.union(*index_sets)

        return indexes
    
    
    # Methods for searching data sets
    
    def search_keywords(self, query = 'request_input', keyword_type = 'most_frequent'):
        
        """
        Searches keywords for a string. If found, returns all matches.
        """
        
        if query == 'request_input':
            query = input('Search query: ')
            
        if type(query) != str:
            raise TypeError('Search query must be a string')
        
        if keyword_type == 'most_frequent':
            df = self.keywords.frequent_words
        
        df = self.keywords.frequent_words.copy(deep=True).reset_index()
        
        return df[df['word'].str.contains(query)]
        

    # Methods for analysing data    
        
    def infer_locations_from_coordinates(self):
        
        """
        Identifies locations associated with coordinates metadata using Geopy. Appends to 'location' metadata category.
        """
        
        metadata_df = self.metadata.copy(deep=True)

        for i in metadata_df.index:
            coordinates = metadata_df.loc[i, 'coordinates']
            location = metadata_df.loc[i, 'location']

            if (coordinates != None) and (location == None):

                if (type(coordinates) == str):
                    if ',' in coordinates:
                        coordinates = coordinates.split(',')
                    elif ' ' in coordinates:
                        coordinates = coordinates.split(' ')
                
                coordinates[0] = coordinates[0].strip()
                coordinates[1] = coordinates[1].strip()

                try:
                    new_location = get_coordinates_location(coordinates[0], coordinates[1])

                except:
                    new_location = location

                metadata_df.loc[i, 'location'] = new_location
            
        self.metadata = metadata_df
        self.update_properties()

        
    def infer_coordinates_from_locations(self):
        
        """
        Identifies coordinates associated with locations metadata using Geopy. Appends to 'coordinates' metadata category.
        """
        
        metadata_df = self.metadata

        for i in metadata_df.index:
            coordinates = metadata_df.loc[i, 'coordinates']
            location = metadata_df.loc[i, 'location']

            if (coordinates == None) and (location != None):

                try:
                    new_coordinates = get_location_coordinates(location)

                except:
                    new_coordinates = coordinates

                metadata_df.loc[i, 'coordinates'] = new_coordinates
        
        self.metadata = metadata_df
        self.update_properties()

    def infer_coordinates_from_ip_addresses(self):
        
        """
        Identifies coordinates associated with IP address metadata using Geopy. Appends to 'coordinates' metadata category.
        """
        
        metadata_df = self.metadata

        for i in metadata_df.index:
            coordinates = metadata_df.loc[i, 'coordinates']
            ip_address = metadata_df.loc[i, 'ip_address']

            if (coordinates == None) and (ip_address != None):

                try:
                    new_coordinates = get_ip_coordinates(ip_address)

                except:
                    new_coordinates = coordinates

                metadata_df.loc[i, 'coordinates'] = new_coordinates
        
        self.metadata = metadata_df
        self.update_properties()
            

    def infer_locations_from_ip_addresses(self):
        
        """
        Identifies locations associated with IP address metadata using Geopy. Appends to 'location' metadata category.
        """
        
        metadata_df = self.metadata

        for i in metadata_df.index:
            location = metadata_df.loc[i, 'location']
            ip_address = metadata_df.loc[i, 'ip_address']

            if (location == None) and (ip_address != None):

                try:
                    new_location = get_ip_physical_location(ip_address)

                except:
                    new_location = location

                metadata_df.loc[i, 'location'] = new_location
        
        self.metadata = metadata_df
        self.update_properties()
            
    def infer_regions_from_coordinates(self):
        
        """
        Identifies regions associated with coordinates metadata using Geopy. Appends to 'region' metadata category.
        """
        
        metadata_df = self.metadata

        for i in metadata_df.index:
            region = metadata_df.loc[i, 'region']
            coordinates = metadata_df.loc[i, 'coordinates']
            
            if (type(coordinates) == str):
                    if ',' in coordinates:
                        coordinates = coordinates.split(',')
                    elif ' ' in coordinates:
                        coordinates = coordinates.split(' ')
            
            if (region == None) and (coordinates != None):

                try:
                    new_region = get_coordinates_geocode(coordinates).address.split(', ')[-1]

                except:
                    new_region = region

                metadata_df.loc[i, 'region'] = new_region
        
        self.metadata = metadata_df
        self.update_properties()
        
                
    def infer_regions_from_locations(self):
        
        """
        Identifies regions associated with locations metadata using Geopy. Appends to 'region' metadata category.
        """
        
        metadata_df = self.metadata

        for i in metadata_df.index:
            region = metadata_df.loc[i, 'region']
            location = metadata_df.loc[i, 'location']

            if (region == None) and (location != None):

                try:
                    new_region = get_location_geocode(location).address.split(', ')[-1]

                except:
                    new_region = region

                metadata_df.loc[i, 'region'] = new_region
        
        self.metadata = metadata_df
        self.update_properties()
        
        
    def infer_regions_from_ip_addresses(self):
        
        """
        Identifies regions associated with IP address metadata using Geopy. Appends to 'region' metadata category.
        """
        
        metadata_df = self.metadata

        for i in metadata_df.index:
            region = metadata_df.loc[i, 'region']
            ip_address = metadata_df.loc[i, 'ip_address']

            if (region == None) and (ip_address != None):

                try:
                    new_region = get_ip_geocode(coordinates).address.split(', ')[-1]

                except:
                    new_region = region

                metadata_df.loc[i, 'region'] = new_region
        
        self.metadata = metadata_df
        self.update_properties()
        
    def infer_internet_metadata(self, domains = True, ip_addresses = True):
        
        """
        Identifies additional internet metadata from existing internet metadata using WhoIs results. Appends to metadata dataframe.
        """
        
        metadata_df = self.metadata.copy(deep=True)
        
        for i in metadata_df.index:
            
            address = metadata_df.loc[i, 'url']
            domain = metadata_df.loc[i, 'domain']
            ip_address = metadata_df.loc[i, 'ip_address']
            
            if (domains == True) and ((domain == '') or (domain == None)):
                try:
                    if (address != None) and (' ' not in address.strip()) and (('/' in address) or ('.' in address)):
                        address = address.replace('https://', '').replace('http://', '')
                        address_split = address.split('/')
                        domain = address_split[0].strip('/').strip()
                        metadata_df.loc[i, 'domain'] = domain
                        
                    else:
                        if ip_address != None:
                            domain = domain_from_ip(ip_address)['domain_name']
                            metadata_df.loc[i, 'domain'] = domain
                        else:
                            pass
                except:
                    pass
            
            if (ip_addresses == True) and ((ip_address == '') or (ip_address == None)):
                try:
                    if domain != None:
                        domain = domain.replace('https://', '').replace('http://', '').strip('/').strip()
                        ip_address = ip_from_domain(domain)
                        metadata_df.loc[i, 'ip_address'] = ip_address
         
                    else:
                        if (address != None) and (' ' not in address.strip()) and (('/' in address) or ('.' in address)):
                            address = address.replace('https://', '').replace('http://', '')
                            address_split = address.split('/')
                            domain = address_split[0].strip('/').strip()
                            metadata_df.loc[i, 'domain'] = domain
                            ip_address = ip_from_domain(domain)
                            metadata_df.loc[i, 'ip_address'] = ip_address
                    
                except:
                    pass
        
        self.metadata = metadata_df
        self.update_properties()
        
        
    def infer_geolocation_metadata(self, coordinates = True, locations = True, regions = True):
        
        """
        Identifies additional geolocation metadata from existing geolocation metadata using Geopy. Appends to metadata dataframe.
        """
        
        metadata_df = self.metadata.copy(deep=True)
        
        for i in metadata_df.index:
            region = metadata_df.loc[i, 'region']
            ip_address = metadata_df.loc[i, 'ip_address']
            domain = metadata_df.loc[i, 'domain']
            location = metadata_df.loc[i, 'location']
            item_coordinates = metadata_df.loc[i, 'coordinates']
            
            if (type(item_coordinates) == str):
                if ',' in item_coordinates:
                    item_coordinates = item_coordinates.strip().split(',')
                elif ' ' in item_coordinates:
                    item_coordinates = item_coordinates.strip().split(' ')
            
            if type(item_coordinates) == list:
                item_coordinates[0] = str(item_coordinates[0]).strip()
                item_coordinates[1] = str(item_coordinates[1]).strip()
            
            if (locations == True) and (location != None) and (item_coordinates != None):
                try:
                    coordinate_address = get_coordinates_location(item_coordinates[0], item_coordinates[1])
                    
                    if len(coordinate_address) > len(location):
                        metadata_df.loc[i, 'location'] = coordinate_address
                        location = coordinate_address
                except:
                    pass
                
            
            if (locations == True) and (location == None):
                
                try:
                    if item_coordinates != None:
                        
                        if type(item_coordinates) == str:
                            item_coordinates = item_coordinates.split(',')
                        
                        if type(item_coordinates) == list:
                            latitude = str(item_coordinates[0]).strip()
                            longitude = str(item_coordinates[1]).strip()
                        
                        location = get_coordinates_location(latitude, longitude)
                        metadata_df.loc[i, 'location'] = location

                    else:
                        if ip_address != None:
                            location = get_ip_physical_location(ip_address)
                            metadata_df.loc[i, 'location'] = location
                        else:
                            if domain != None:
                                ip_address = ip_from_domain(domain)
                                location = get_ip_physical_location(ip_address)
                                metadata_df.loc[i, 'location'] = location
                                
                    
                except:
                    pass
            
            if (coordinates == True) and (item_coordinates == None):
                
                try:
                    if (location != None):
                            item_coordinates = get_location_coordinates(location)
                            item_coordinates = str(item_coordinates[0]) + ', ' + str(item_coordinates[1])
                            metadata_df.loc[i, 'coordinates'] = item_coordinates
                    else:
                        if (ip_address != None):
                            item_coordinates = get_ip_coordinates(ip_address)
                            item_coordinates = str(item_coordinates[0]) + ', ' + str(item_coordinates[1])
                            metadata_df.loc[i, 'coordinates'] = item_coordinates

                        else:
                            if domain != None:
                                ip_address = ip_from_domain(domain)
                                item_coordinates = get_ip_coordinates(ip_address)
                                item_coordinates = str(item_coordinates[0]) + ', ' + str(item_coordinates[1])
                                metadata_df.loc[i, 'coordinates'] = item_coordinates
                            
                             
                except:
                    pass
            
            
            if (regions == True) and (region != None) and (item_coordinates != None):
                try:
                    
                    if type(item_coordinates) == str:
                            item_coordinates = item_coordinates.split(',')
                        
                    if type(item_coordinates) == list:
                            latitude = str(item_coordinates[0]).strip()
                            longitude = str(item_coordinates[1]).strip()
                    
                    coordinate_region = get_coordinates_location(latitude, longitude).split(', ')[-1]
                    
                    if coordinate_region.lower() != metadata_df.loc[i, 'region'].lower():
                        metadata_df.loc[i, 'region'] = coordinate_region
                        
                except:
                    pass
            
            if (regions == True) and (region == None):
                
                try:
                    if item_coordinates != None:
                        
                        if type(item_coordinates) == str:
                            item_coordinates = item_coordinates.split(',')
                        
                        if type(item_coordinates) == list:
                            latitude = str(item_coordinates[0]).strip()
                            longitude = str(item_coordinates[1]).strip()
                        
                        metadata_df.loc[i, 'region'] = get_coordinates_location(latitude, longitude).split(', ')[-1]

                    else:
                        if location != None:
                                metadata_df.loc[i, 'region'] = get_location_geocode(location).address.split(', ')[-1]
                        
                        else:
                            if ip_address != None:
                                metadata_df.loc[i, 'region'] = get_ip_physical_location(ip_address).address.split(', ')[-1]

                            else:
                                if domain != None:
                                    ip_address = ip_from_domain(domain)
                                    metadata_df.loc[i, 'region'] = get_ip_physical_location(ip_address).address.split(', ')[-1]
                       
                except:
                    pass
            
        self.metadata = metadata_df
        self.update_properties()
    
    
    def metadata_time_diffs_from_date(self, select_by = 'created_at', date = 'request_input', within = 100, units = 'days', ignore_nones = True):
        
        """
        Returns the time differences between items' time metadata from a given date or time.
        
        Parameters
        ----------
        select_by : str
            name of time metadata category to use. Defaults to 'created_at'.
        date : str or datetime
            date or time to compare items with. Defaults to requesting user input.
        within : int
            maximum time range.
        units : str
            unit of time for results. Defaults to 'years'.
        ignore_nones : bool
            whether or not to ignore time metadata values which equal None or ''. Defaults to True.
        
        Returns
        -------
        time_difference : datetime.timedelta
            the time difference between items' time metadata entries and datetime.
        """
        
        if date == 'request_input':
            date = input('Find dates close to: ')

        ref_dt = str_to_datetime(date)

        metadata_df = self.metadata.copy(deep=True)
        output_df = pd.DataFrame(metadata_df[select_by])
        
        if ignore_nones == True:
            output_df = output_df.dropna()
        
        output_df['time_difference'] = abs(ref_dt - output_df[select_by])

        if units == 'days':
            limit = timedelta(within)

        output_df = output_df[output_df['time_difference'] <= limit]
        
        return output_df.sort_values('time_difference')

    
    # Methods for filtering data sets
    
    def filter_metadata_by_distances(self, select_by = 'location', close_to = 'request_input', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters metadata dataframe by entries whose geolocation metadata falls within a distance of a given location. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        select_by : str
            category of geolocation metadata to use.
        close_to : str
            location or coordinates to measure from.
        within : int
            maximum distance from given location. 
        units : str
            units for distance.
        ignore_nones : bool
            whether to ignore items without geolocation metadata entries.
        """
        
        if close_to == 'request_input':
            close_to = input('Find items close to: ')
        
        metadata_df = self.metadata.copy(deep=True)
        metadata_df[f'Distance from {close_to}'] = None
        metadata_df['Units'] = None
        
        if close_to in metadata_df.index:
            select_by = 'items'
            ref_coordinates = metadata_df.loc[close_to, 'coordinates']

            if ref_coordinates == None:
                return metadata_df

            if type(ref_coordinates) == str:
                split_res = close_to.split(',')
                ref_coordinates = [i.strip() for i in split_res]

        if select_by == 'coordinates':
            if type(close_to) == str:
                split_res = close_to.split(',')
                ref_coordinates = [i.strip() for i in split_res]

            if type(close_to) == list:
                ref_coordinates = [i.strip() for i in close_to]

            if (type(close_to) != str) and (type(close_to) != list):
                raise TypeError('Coordinates must be either a string or list')

        if select_by == 'location':

            if type(select_by) != str:
                raise TypeError('Location must be a string')

            ref_coordinates = get_location_coordinates(close_to)

        if (select_by != 'location') and (select_by != 'coordinates') and (select_by != 'items'):
            raise ValueError('"select_by" only accepts "coordinates" or "location"')

        if len(ref_coordinates) < 2:
            return metadata_df

        ref_latitude = str(ref_coordinates[0]).strip()
        ref_longitude = str(ref_coordinates[1]).strip()

        for item in metadata_df.index:

            if item == close_to:
                continue

            item_coordinates = metadata_df.loc[item, 'coordinates']
            item_location = metadata_df.loc[item, 'location']

            if item_coordinates == None:
                distance = None
                continue

            if type(item_coordinates) == str:
                item_coordinates = item_coordinates.split(',')
                item_latitude = item_coordinates[0]
                item_longitude = item_coordinates[1]

            item_latitude = str(item_latitude).strip()
            item_longitude = str(item_longitude).strip()

            distance = coordinates_distance(first_coordinates = ref_coordinates, second_coordinates = item_coordinates, units = units)
            units = distance[1]
            distance = distance[0]

            metadata_df.loc[item, f'Distance from {close_to}'] = distance
            metadata_df.loc[item, 'Units'] = units

        if ignore_nones == True:
            metadata_df = metadata_df.dropna(subset = f'Distance from {close_to}')

        metadata_df = metadata_df[metadata_df[f'Distance from {close_to}'] <= within]

        return metadata_df.sort_values(f'Distance from {close_to}')

    
    
    def filter_info_by_distance_metadata(self, select_by = 'location', close_to = 'request_input', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters informatin dataframe by entries whose geolocation metadata falls within a distance of a given location. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        select_by : str
            category of geolocation metadata to use.
        close_to : str
            location or coordinates to measure from.
        within : int
            maximum distance from given location. 
        units : str
            units for distance.
        ignore_nones : bool
            whether to ignore items without geolocation metadata entries.
        """
        
        filtered_metadata = self.filter_metadata_by_distances(select_by = select_by, close_to = close_to, within = within, units = units, ignore_nones = ignore_nones)
        items = filtered_metadata.index.to_list()
        
        info_df = self.information.copy(deep=True)
        masked_df = info_df[info_df.index.isin(items)]
        
        return masked_df
    
    
    def filter_data_by_distance_metadata(self, select_by = 'location', close_to = 'request_input', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters data dataframe by entries whose geolocation metadata falls within a distance of a given location. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        select_by : str
            category of geolocation metadata to use.
        close_to : str
            location or coordinates to measure from.
        within : int
            maximum distance from given location. 
        units : str
            units for distance.
        ignore_nones : bool
            whether to ignore items without geolocation metadata entries.
        """
        
        filtered_metadata = self.filter_metadata_by_distances(select_by = select_by, close_to = close_to, within = within, units = units, ignore_nones = ignore_nones)
        items = filtered_metadata.index.to_list()
        
        data_df = self.data.copy(deep=True)
        masked_df = data_df[data_df.index.isin(items)]
        
        return masked_df
    
    
    def filter_other_by_distance_metadata(self, select_by = 'location', close_to = 'request_input', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters 'other' (links, references, and contents) dataframe by entries whose geolocation metadata falls within a distance of a given location. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        select_by : str
            category of geolocation metadata to use.
        close_to : str
            location or coordinates to measure from.
        within : int
            maximum distance from given location. 
        units : str
            units for distance.
        ignore_nones : bool
            whether to ignore items without geolocation metadata entries.
        """
        
        filtered_metadata = self.filter_metadata_by_distances(select_by = select_by, close_to = close_to, within = within, units = units, ignore_nones = ignore_nones)
        items = filtered_metadata.index.to_list()
        
        other_df = self.other.copy(deep=True)
        masked_df = other_df[other_df.index.isin(items)]
        
        return masked_df
    
    
    def filter_keywords_by_distance_metadata(self, measure = 'frequency', select_by = 'location', close_to = 'request_input', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters keywords dataframes by entries whose geolocation metadata falls within a distance of a given location. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        measure : str
            which keywords dataframe to use.
        select_by : str
            category of geolocation metadata to use.
        close_to : str
            location or coordinates to measure from.
        within : int
            maximum distance from given location. 
        units : str
            units for distance.
        ignore_nones : bool
            whether to ignore items without geolocation metadata entries.
        """
        
        filtered_metadata = self.filter_metadata_by_distances(select_by = select_by, close_to = close_to, within = within, units = units, ignore_nones = ignore_nones)
        items = filtered_metadata.index.to_list()
        
        if measure == 'frequency':
            words_df = self.keywords.frequent_words.copy(deep=True)
        
        if measure == 'centrality':
            words_df = self.keywords.central_words.copy(deep=True)
            
        output_df = pd.DataFrame(dtype = object)
        
        for i in items:

            masked_words = words[words['found_in'].str.contains(i)]
            output_df = pd.concat([output_df, masked_words])

        output_df = output_df.drop('breakdown', axis=1)
        output_df.drop_duplicates()
        
        return output_df

    
    def filter_metadata_by_dates(self, select_by = 'created_at', from_date = 'request_input', to_date = 'request_input', ignore_nones = True):
        
        """
        Filters metadata dataframe for entries whose time metadata falls between two datetimes. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        select_by : str
            category of time metadata to use. Defaults to 'Created at'
        from_date : str
            date or time to measure from. Defaults to requesting from user input.
        to_date : str
            date or time to measure to. Defaults to requesting from user input.
        ignore_nones : bool
            whether to ignore items without geolocation metadata entries. Defaults to True.
        """
        
        if from_date == 'request_input':
            from_date = input('From: ')

        if to_date == 'request_input':
            to_date = input('To: ')

        from_date = str_to_datetime(from_date)
        to_date = str_to_datetime(to_date)
        
        metadata_df = self.metadata.copy(deep=True)
        
        if ignore_nones == True:
            metadata_df = metadata_df.dropna(subset = select_by)

        metadata_df = metadata_df[(metadata_df[select_by] >= from_date) & (metadata_df[select_by] <= to_date)]

        return metadata_df.sort_values(select_by)
    
    
    def filter_data_by_metadata_dates(self, select_by = 'created_at', from_date = 'request_input', to_date = 'request_input', ignore_nones = True):
        
        """
        Filters data dataframe for entries whose time metadata falls between two datetimes. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        select_by : str
            category of time metadata to use. Defaults to 'Created at'
        from_date : str
            date or time to measure from. Defaults to requesting from user input.
        to_date : str
            date or time to measure to. Defaults to requesting from user input.
        ignore_nones : bool
            whether to ignore items without geolocation metadata entries. Defaults to True.
        """
        
        filtered_metadata = self.filter_metadata_by_dates(select_by = select_by, from_date = from_date, to_date = to_date, ignore_nones = ignore_nones)
        items = filtered_metadata.index.to_list()
        
        data_df = self.data.copy(deep=True)
        masked_df = data_df[data_df.index.isin(items)]
        
        return masked_df
    
    
    def filter_info_by_metadata_dates(self, select_by = 'created_at', from_date = 'request_input', to_date = 'request_input', ignore_nones = True):
        
        """
        Filters information dataframe for entries whose time metadata falls between two datetimes. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        select_by : str
            category of time metadata to use. Defaults to 'Created at'
        from_date : str
            date or time to measure from. Defaults to requesting from user input.
        to_date : str
            date or time to measure to. Defaults to requesting from user input.
        ignore_nones : bool
            whether to ignore items without geolocation metadata entries. Defaults to True.
        """
        
        filtered_metadata = self.filter_metadata_by_dates(select_by = select_by, from_date = from_date, to_date = to_date, ignore_nones = ignore_nones)
        items = filtered_metadata.index.to_list()
        
        info_df = self.information.copy(deep=True)
        masked_df = info_df[info_df.index.isin(items)]
        
        return masked_df
    
    
    def filter_other_by_metadata_dates(self, select_by = 'created_at', from_date = 'request_input', to_date = 'request_input', ignore_nones = True):
        
        """
        Filters 'other' (links, references, and contents) dataframe for entries whose time metadata falls between two datetimes. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        select_by : str
            category of time metadata to use. Defaults to 'Created at'
        from_date : str
            date or time to measure from. Defaults to requesting from user input.
        to_date : str
            date or time to measure to. Defaults to requesting from user input.
        ignore_nones : bool
            whether to ignore items without geolocation metadata entries. Defaults to True.
        """
        
        filtered_metadata = self.filter_metadata_by_dates(select_by = select_by, from_date = from_date, to_date = to_date, ignore_nones = ignore_nones)
        items = filtered_metadata.index.to_list()
        
        other_df = self.other.copy(deep=True)
        masked_df = other_df[other_df.index.isin(items)]
        
        return masked_df

    
    def filter_keywords_by_metadata_dates(self, measure = 'frequency', select_by = 'created_at', from_date = 'request_input', to_date = 'request_input', ignore_nones = True):
        
        """
        Filters keywords dataframes for entries whose time metadata falls between two datetimes. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        measure : str
            which keywords dataframe to use.
        select_by : str
            category of time metadata to use. Defaults to 'Created at'
        from_date : str
            date or time to measure from. Defaults to requesting from user input.
        to_date : str
            date or time to measure to. Defaults to requesting from user input.
        ignore_nones : bool
            whether to ignore items without geolocation metadata entries. Defaults to True.
        """
        
        filtered_metadata = self.filter_metadata_by_dates(select_by = select_by, from_date = from_date, to_date = to_date, ignore_nones = ignore_nones)
        items = filtered_metadata.index.to_list()
        
        if measure == 'frequency':
            words_df = self.keywords.frequent_words.copy(deep=True)
        
        if measure == 'centrality':
            words_df = self.keywords.central_words.copy(deep=True)
            
        output_df = pd.DataFrame(dtype = object)
        for i in items:

            masked_words = words[words['found_in'].str.contains(i)]

            output_df = pd.concat([output_df, masked_words])

        output_df = output_df.drop('breakdown', axis=1)
        output_df.drop_duplicates()
        
        return output_df
    
    
    # Methods for running data triangulation
    
    def triangulate_metadata_by_distances(self, locations, select_by = 'location', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters metadata dataframe by entries whose geolocation metadata falls within a distance of multiple given locations. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        locations : list
            a list of locations or coordinates to triangulate from.
        select_by : str
            category of geolocation metadata to use.
        within : int
            maximum distance from given location. 
        units : str
            units for distance.
        ignore_nones : bool
            whether to ignore items without geolocation metadata entries.
        """
        
        if type(locations) != list:
            raise TypeError('Locations must be inputted at a list')
        
        output_df = self.metadata.copy(deep=True)
        
        for i in locations:
            
            i_df = self.filter_metadata_by_distances(select_by = select_by, close_to = i, within = within, units = units, ignore_nones = ignore_nones)
            index_list = i_df.index.to_list()
            output_df = output_df[output_df.index.isin(index_list)]
            
            for index in index_list:
                
                if index not in output_df.index:
                    output_df.loc[index] = i_df.loc[index]
                
                output_df.loc[index, f'Distance from {i}'] = i_df.loc[index, f'Distance from {i}']
        
            
            
        output_df['Units'] = units
        
        if ignore_nones == True:
            col_count = (len(locations) + 1)*(-1)
            subset = output_df.columns[col_count:]
            output_df = output_df.dropna(subset = subset)
        
        return output_df
    
    
    def triangulate_data_by_metadata_distances(self, locations, select_by = 'location', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters data dataframe by entries whose geolocation metadata falls within a distance of multiple given locations. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        locations : list
            a list of locations or coordinates to triangulate from.
        select_by : str
            category of geolocation metadata to use.
        within : int
            maximum distance from given location. 
        units : str
            units for distance.
        ignore_nones : bool
            whether to ignore items without geolocation metadata entries.
        """
        
        filtered_metadata = self.triangulate_metadata_by_distances(locations, select_by = select_by, within = within, units = units, ignore_nones = ignore_nones)
        items = filtered_metadata.index.to_list()
        
        data_df = self.data.copy(deep=True)
        masked_df = data_df[data_df.index.isin(items)]
        
        return masked_df
    
    
    def triangulate_info_by_metadata_distances(self, locations, select_by = 'location', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters information dataframe by entries whose geolocation metadata falls within a distance of multiple given locations. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        locations : list
            a list of locations or coordinates to triangulate from.
        select_by : str
            category of geolocation metadata to use.
        within : int
            maximum distance from given location. 
        units : str
            units for distance.
        ignore_nones : bool
            whether to ignore items without geolocation metadata entries.
        """
        
        filtered_metadata = self.triangulate_metadata_by_distances(locations, select_by = select_by, within = within, units = units, ignore_nones = ignore_nones)
        items = filtered_metadata.index.to_list()
        
        info_df = self.information.copy(deep=True)
        masked_df = info_df[info_df.index.isin(items)]
        
        return masked_df
    
    
    def triangulate_other_by_metadata_distances(self, locations, select_by = 'location', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters 'other' (links, references, and contents) dataframe by entries whose geolocation metadata falls within a distance of multiple given locations. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        locations : list
            a list of locations or coordinates to triangulate from.
        select_by : str
            category of geolocation metadata to use.
        within : int
            maximum distance from given location. 
        units : str
            units for distance.
        ignore_nones : bool
            whether to ignore items without geolocation metadata entries.
        """
        
        filtered_metadata = self.triangulate_metadata_by_distances(locations, select_by = select_by, within = within, units = units, ignore_nones = ignore_nones)
        items = filtered_metadata.index.to_list()
        
        other_df = self.other.copy(deep=True)
        masked_df = other_df[other_df.index.isin(items)]
        
        return masked_df
    
    
    def triangulate_keywords_by_metadata_distances(self, locations, measure = 'frequency', select_by = 'location', close_to = 'request_input', within = 100, units = 'kilometers', ignore_nones = True):
        
        """
        Filters keywords dataframes by entries whose geolocation metadata falls within a distance of multiple given locations. Returns a pandas.DataFrame.
        
        Parameters
        ----------
        measure : str
            which keywords dataframe to use.
        locations : list
            a list of locations or coordinates to triangulate from.
        select_by : str
            category of geolocation metadata to use.
        within : int
            maximum distance from given location. 
        units : str
            units for distance.
        ignore_nones : bool
            whether to ignore items without geolocation metadata entries.
        """
        
        filtered_metadata = self.triangulate_metadata_by_distances(locations, select_by = select_by, within = within, units = units, ignore_nones = ignore_nones)
        items = filtered_metadata.index.to_list()
        
        if measure == 'frequency':
            words_df = self.keywords.frequent_words.copy(deep=True).drop('breakdown', axis=1)
        
        if measure == 'centrality':
            words_df = self.keywords.central_words.copy(deep=True).drop('breakdown', axis=1)
            
        output_df = pd.DataFrame(dtype = object)
        
        for i in items:

            masked_words = words[words['found_in'].str.contains(i)]
            output_df = pd.concat([output_df, masked_words])
        
        
        output_df = output_df.drop('breakdown', axis=1)
        output_df.drop_duplicates()
        
        
        return output_df
    
    
    # Methods for looking up data online
    
    def lookup_all_domain_metadata(self):
        
        """
        Runs WhoIs lookups on all domain metadata.
        """
        
        domains = self.metadata['domain'].to_list()
        
        return domains_whois(domains)
    
    
    def lookup_all_ip_metadata(self):
        
        """
        Runs WhoIs lookups on all IP address metadata.
        """
        
        ips = self.metadata['ip_address'].to_list()
        
        return ips_whois(ips)

    
    def lookup_all_whois_metadata(self, append_to_dataset = False):
        
        """
        Runs WhoIs lookups on all internet metadata.
        
        Parameters
        ----------
        append_to_dataset : bool
            whether to add WhoIs results to the metadata dataframe.
        """
        
        metadata = self.metadata
        addresses = metadata['url'].to_list()
        domains = metadata['domain'].to_list()
        ip_addresses = metadata['ip_address'].to_list()
                                
        if (
            (addresses != None)
            and (type(addresses) == list)
            and (len(addresses) > 0)
        ):
                                try:             
                                    result = domains_whois(addresses)
                                    if len(result.index) < len(addresses):
                                        if (domains != None) and (type(domains) == list) and (len(domains) > 0):
                                            try:
                                                result = self.lookup_all_domain_metadata()
                                            except:
                                                if (ip_addresses != None) and (type(ip_addresses) == list) and (len(ip_addresses) > 0):
                                                    try:
                                                        result = self.lookup_all_ip_metadata()
                                                    except:
                                                        pass

                                except:
                                        if (domains != None) and (type(domains) == list) and (len(domains) > 0):
                                            try:
                                                result = self.lookup_all_domain_metadata()
                                            except:
                                                    if (ip_addresses != None) and (type(ip_addresses) == list) and (len(ip_addresses) > 0):
                                                        try:
                                                            result = self.lookup_all_ip_metadata()
                                                        except:
                                                            pass
        
        else:
            if (domains != None) and (type(domains) == list) and (len(domains) > 0):
                try:
                    result = self.lookup_all_domain_metadata()
                except:
                        if (ip_addresses != None) and (type(ip_addresses) == list) and (len(ip_addresses) > 0):
                            try:
                                result = self.lookup_all_ip_metadata()
                            except:
                                pass
            
            elif (ip_addresses != None) and (type(ip_addresses) == list) and (len(ip_addresses) > 0):
                try:
                    result = self.lookup_all_ip_metadata()
                except:
                    pass
        
            
        if append_to_dataset == True:
            self.whois = result
        
        return result
    
    
    # Methods for exporting data to external files
    
    def export_txt(self, new_file = True, file_name = 'request_input', file_address = 'request_input'):
        
        """
        Exports CaseData object to a .txt file.
        
        Parameters
        ----------
        new_file : bool
            whether to create a new file. Defaults to True.
        file_name : str
            name for file. Defaults to requesting from user input.
        file_address : str
            directory address to save to. Defaults to requesting from user input.
        """
        
        if new_file == True:
            
            if file_name == 'request_input':
                file_name = input('File name: ')
            
            if file_address == 'request_input':
                file_address = input('File address: ')
                file_address = file_address + '/' + file_name
            
        if new_file == False:
            
            if file_address == 'request_input':
                file_address = input('File path: ')
        
        if '.case' != file_address[-5:]:
            file_address = file_address + '.casedata'

        with open(file_address, 'wb') as f:
            pickle.dump(self, f) 

            
    def export_excel(self, new_file = True, file_name = 'request_input', file_address = 'request_input'):
        
        """
        Exports dataframes to an Excel file.
        
        Parameters
        ----------
        new_file : bool
            whether to create a new file. Defaults to True.
        file_name : str
            name for file. Defaults to requesting from user input.
        file_address : str
            directory address to save to. Defaults to requesting from user input.
        """
        
        if new_file == True:
            
            if file_name == 'request_input':
                file_name = input('File name: ')
            
            if file_address == 'request_input':
                file_address = input('File address: ')
                file_address = file_address + '/' + file_name
            
        if new_file == False:
            
            if file_address == 'request_input':
                file_address = input('File path: ')
        
        if '.xlsx' != file_address[-5:]:
            file_address = file_address + '.xlsx'
        
        metadata_df = self.metadata.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(metadata_df)

        info_df = self.information.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(info_df)

        data_df = self.data.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(data_df)

        other_df = self.other.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(other_df)

        frequent_words_df = self.keywords.frequent_words.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(frequent_words_df)

        central_words_df = self.keywords.central_words.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(central_words_df)
        
        with pd.ExcelWriter(file_address) as writer:  

            data_df.to_excel(writer, sheet_name='Item data')
            metadata_df.to_excel(writer, sheet_name='Item metadata')
            info_df.to_excel(writer, sheet_name='Item information')
            other_df.to_excel(writer, sheet_name='Item other')
            frequent_words_df.to_excel(writer, sheet_name='Frequent keywords')
            central_words_df.to_excel(writer, sheet_name='Central keywords')


    def export_csv_folder(self, folder_address = 'request_input', folder_name = 'request_input'):
        
        """
        Exports dataframes to a folder of CSV files.
        
        Parameters
        ----------
        folder_name : str
            name for folder. Defaults to requesting from user input.
        folder_address : str
            directory address to save to. Defaults to requesting from user input.
        """
        
        metadata_df = self.metadata.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(metadata_df)

        info_df = self.information.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(info_df)

        data_df = self.data.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(data_df)

        other_df = self.other.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(other_df)

        frequent_words_df = self.keywords.frequent_words.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(frequent_words_df)

        central_words_df = self.keywords.central_words.astype(str).replace('NaT', None).replace('None', None)
        join_df_col_lists_by_semicolon(central_words_df)
    
        dfs_dict = {'item_data': data_df, 
                    'item_metadata': metadata_df, 
                    'item_information': info_df,
                    'item_other': other_df,
                    'frequent_keywords': frequent_words_df,
                    'central_keywords': central_words_df}
        
        if folder_address == 'request_input':
            folder_address = input('Folder address: ')
        
        if folder_name == 'request_input':
            folder_name = input('Folder name: ')
        
        path = os.path.join(folder_address, folder_name) 
        
        os.mkdir(path) 

        for item in dfs_dict.keys():
            file_name = item
            file_path = path + '/' + file_name + '.csv'
            df = dfs_dict[item]

            df.to_csv(file_path)

    
    def save_as(self, file_name = 'request_input', file_address = 'request_input', file_type = 'request_input'):
        
        """
        Exports CaseData object to a file or folder of a type selected by user.
        
        Parameters
        ----------
        file_name : str
            name for file. Defaults to requesting from user input.
        file_address : str
            directory address to save to. Defaults to requesting from user input.
        file_type : str
            type of files to save to. Defaults to requesting from user input.
        """
        
        if file_type == 'request_input':
            file_type = input('File type: ')
        
        file_type = file_type.strip().strip('.').strip().lower()
        
        
        if (file_type.lower() == None) or (file_type.lower() == '') or (file_type.lower() == 'case') or (file_type.lower() == 'text') or (file_type.lower() == 'txt') or (file_type.lower() == 'pickle'):
            
            self.export_txt(new_file = True, file_name = file_name, file_address = file_address)
        
        
        if (file_type.lower() == 'excel') or (file_type.lower() == 'xlsx'):
            
            self.export_excel(new_file = True, file_name = file_name, file_address = file_address)
        
        
        if (file_type.lower() == 'csv') or (file_type.lower() == 'csvs'):
            
            self.export_csv_folder(folder_address = file_address, folder_name = file_name)
    
    
    