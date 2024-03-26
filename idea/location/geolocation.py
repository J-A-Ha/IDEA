"""Functions for geolocation analysis"""

from ..core.basics import map_inf_to_1, map_inf_to_0

from typing import List, Dict, Tuple
import copy
import geopy
from geopy import distance
from geopy.geocoders import Nominatim
import geocoder
import webbrowser
from urllib.parse import quote, urlparse


# Instructions for creating satellite imagery-based maps: https://blog.goodaudience.com/geo-libraries-in-python-plotting-current-fires-bffef9fe3fb7

def get_coordinates_geocode(coordinates: list = None, latitude: str = 'request_input', longitude: str = 'request_input') -> geopy.location.Location:
    
    """
    Takes co-ordinate as a string and returns its associated geocode.
    
    Parameters
    ----------
    coordinates : list or str, default : None
        list or string of coordinates to use. Defaults to None.
    latitude : str
        if no list or string of coordinates given, requests for latitude.
    longitude : str
        if no list or string of coordinates given, requests for longitude.
    
    Returns
    -------
    result : geopy.location.Location
        a geopy geocode.
    """
    
    # Formatting coordinates if inputted
    if coordinates != None:
        
        if coordinates == str:
            coordinates = coordinates.replace('[').replace(']').replace('{').replace('}')
            coordinates = coordinates.split(',')
        
        if coordinates == list:
            
            latitude = coordinates[0]
            longitude = coordinates[1]
        
        
    # Requesting latitude from user input if no latitude given
    if latitude == 'request_input':
        latitude = input('latitude: ')
    
    # Requesting latitude from user input if no latitude given
    if longitude == 'request_input':
        longitude = input('longitude: ')
    
    # Formatting latitude and longitude as strings
    latitude = str(latitude)
    longitude = str(longitude)
        
    # Initialising Nominatim geolocator object
    geolocator = Nominatim(user_agent="location_app")
    
    # Retrieving geocode
    result = geolocator.reverse([latitude, longitude])
    
    return result


def get_location_geocode(location: str = 'request_input') -> geopy.location.Location:
    
    """
    Takes location as a string and returns its associated Geopy geocode.
    
    Parameters
    ----------
    location : str
        an address or location name. Defaults to requesting from user input.
    
    Returns
    -------
    result : geopy.location.Location
        a geopy geocode.
    """
    
    # Requesting location from user input if none given
    if location == 'request_input':
        location = input('Location details: ')
    
    # Initialising Nominatim geolocator object
    geolocator = Nominatim(user_agent="location_app")
    
    # Retrieving geocode and handling errors
    try:
        return geolocator.geocode(location)
    
    except:
        raise ValueError('Lookup failed. Please check the location details provided.')

        
def get_coordinates_location(coordinates = None, latitude: str = 'request_input', longitude: str = 'request_input') -> str:
    
    """
    Takes coordinates and returns the location associated by Geopy's geocoder.
    
    Parameters
    ----------
    coordinates : list or str, default : None
        list or string of coordinates to use. Defaults to None.
    latitude : str
        if no list or string of coordinates given, requests for latitude.
    longitude : str
        if no list or string of coordinates given, requests for longitude.
    
    Returns
    -------
    result : str
        an address or location name associated with the inputted coordinates.
    """
    
    # Formatting coordinates if inputted
    if coordinates != None:
        
        if coordinates == str:
            coordinates = coordinates.replace('[').replace(']').replace('{').replace('}')
            coordinates = coordinates.split(',')
        
        if coordinates == list:
            
            latitude = coordinates[0]
            longitude = coordinates[1]
    
    # Requesting latitude from user input if no latitude given
    if latitude == 'request_input':
        latitude = input('latitude: ')
    
    # Requesting latitude from user input if no latitude given
    if longitude == 'request_input':
        longitude = input('longitude: ')
    
    # Formatting latitude and longitude as strings
    latitude = str(latitude)
    longitude = str(longitude)
    
    # Joining coordinates into one string for geopy
    coordinates = latitude + ', ' + longitude
    
    # Initialising Nominatim geolocator object
    geolocator = Nominatim(user_agent="location_app")
    
    # Retrieving geocode and handling errors
    try:
        return geolocator.geocode(coordinates).address
    
    except:
        raise ValueError('Lookup failed. Please check the coordinates provided.')

        
def get_location_coordinates(location: str = 'request_input') -> list:
    
    """
    Takes location details and returns the coordinates associated by Geopy's geocoder.
    
    Parameters
    ----------
    location : str
        an address or location name. Defaults to requesting from user input.
    
    Returns
    -------
    result : list
        list of coordinates associated with the inputted coordinates.
    """
    
    # Requesting location from user input if none given
    if location == 'request_input':
        location = input('Location details: ')
    
    # Initialising Nominatim geolocator object
    geolocator = Nominatim(user_agent="location_app")
    
    # Retrieving geocode and handling errors
    try:
        output_location = geolocator.geocode(location)
    
    except Exception as e:
        raise Exception
    
    # Outputting latitude and longitude if lookup was successful
    try:
        return [output_location.latitude, output_location.longitude]
    except:
        raise ValueError('Lookup failed. Please check the location details provided.')
    


def get_location_address(location: str = 'request_input') -> str:
    
    """
    Takes location details and returns the address associated by Geopy's geocoder.
    
    Parameters
    ----------
    location : str
        a location name. Defaults to requesting from user input.
    
    Returns
    -------
    result : str
        an address associated with the inputted location name.
    """
    
    # Requesting location from user input if none given
    if location == 'request_input':
        location = input('Location details: ')
    
    # Initialising Nominatim geolocator object
    geolocator = Nominatim(user_agent="location_app")
    
    # Retrieving address and handling errors
    try:
        return geolocator.geocode(location).address
    
    except:
        raise ValueError('Lookup failed. Please check the location details provided.')

        
def lookup_coordinates(coordinates = None, latitude: str = 'request_input', longitude: str = 'request_input', site: str = 'Google Maps'):
    
    """
    Searches for coordinates on inputted mapping platform.
    
    Parameters
    ----------
    coordinates : list or str, default : None
        list or string of coordinates to use. Defaults to None.
    latitude : str
        if no list or string of coordinates given, requests for latitude.
    longitude : str
        if no list or string of coordinates given, requests for longitude.
    site : str
        name of mapping platform to use to lookup coordinates. Defaults to 'Google Maps'.
    """
    
    # Formatting coordinates if inputted
    if coordinates != None:
        
        if coordinates == str:
            coordinates = coordinates.replace('[').replace(']').replace('{').replace('}')
            coordinates = coordinates.split(',')
        
        if coordinates == list:
            latitude = coordinates[0]
            longitude = coordinates[1]
    
    
    # Requesting latitude from user input if no latitude given
    if latitude == 'request_input':
        latitude = input('latitude: ')
    
    # Requesting latitude from user input if no latitude given
    if longitude == 'request_input':
        longitude = input('longitude: ')
    
    # Formatting latitude and longitude as strings
    latitude = str(latitude)
    longitude = str(longitude)
    
    # Initialising sites list variable
    sites_list = ['google earth', 'google maps', 'wikimapia']
    
    # If site to search is Google Earth, searching Google Earth
    if site.lower() == 'google earth':
        url_base = 'https://earth.google.com/web/@'
        url = url_base + latitude + ',' + longitude
        return webbrowser.open(url)
    
    # If site to search is Google Maps, searching Google Maps
    if site.lower() == 'google maps':
        url_base = 'https://www.google.com/maps/search/?api=1&query='
        query = quote(latitude + ',' + longitude)
        url = url_base + query
        return webbrowser.open(url)
    
    # If site to search is Wikimapia, searching Wikimapia
    if site.lower() == 'wikimapia':
        url_base = 'http://wikimapia.org/#lang=en&'
        url = url_base + 'lat='+ latitude + '&lon=' + longitude
        return webbrowser.open(url)
    
    # If site to search is 'all', using recursion to search Google Earth, Google Maps, and Wikipedia
    elif site == 'all':
        for item in sites_list:
            lookup_coordinates(latitude = latitude, longitude = longitude, site = item)

def lookup_location(location: str = 'request_input', site: str = 'Google Maps'):
    
    """
    Searches for coordinates on inputted mapping platform.
    
    Parameters
    ----------
    location : str
        an address or location name. Defaults to requesting from user input.
    site : str
        name of mapping platform to use to lookup coordinates. Defaults to 'Google Maps'.
    """
    
    # Requesting location from user input if none given
    if location == 'request_input':
        location = input('Location details: ')
    
    # Retrieving coordinates for location using Geopy
    coordinates = get_location_coordinates(location = location)
    
    # Running lookop_coordinates() on coordinates
    return lookup_coordinates(latitude = coordinates[0], longitude = coordinates[1], site = site)


def coordinates_distance(first_coordinates: str = 'request_input', second_coordinates: str = 'request_input', units: str = 'kilometers') -> tuple:
    
    """
    Returns the distance between two coordinates in units provided by user.
    
    Parameters
    ----------
    first_coordinates : str or list
        the first set of coordinates for comparison.
    second_coordinates : str or list
        the second set of coordinates for comparison.
    units : str
        units to use for distance calculation. Defaults to 'kilometers'.
    
    Returns
    -------
    result : tuple
        a tuple containing the distance and its units.
    """
    if type(first_coordinates) == list:
        first_coordinates = ','.join(first_coordinates)
    
    if type(second_coordinates) == list:
        second_coordinates = ','.join(second_coordinates)
    
    # Requesting first set of coordinates from user input if none given
    if first_coordinates == 'request_input':
        first_coordinates = input('First coordinates: ')
    
    # Requesting second set of coordinates from user input if none given
    if second_coordinates == 'request_input':
        second_coordinates = input('Second coordinates: ')
    
    # Calculating distance in inputted units 
    if units == 'kilometers':
        res = distance.geodesic(first_coordinates, second_coordinates).kilometers
    
    if units == 'miles':
        res = distance.geodesic(first_coordinates, second_coordinates).miles
        
    return res, units

def locations_distance(first_location: str = 'request_input', second_location: str = 'request_input', units: str = 'kilometers') -> tuple:
    
    """
    Returns the distance between two coordinates, using units provided by user.
    
    Parameters
    ----------
    first_location : str
        the first location name or address for comparison.
    second_location : str
        the second location name or address for comparison.
    units : str
        units to use for distance calculation. Defaults to 'kilometers'.
    
    Returns
    -------
    result : tuple
        a tuple containing the distance and its units.
    """
    
    # Requesting first location from user input if none given
    if first_location == 'request_input':
        first_location = input('First location: ')
    
    # Requesting second location from user input if none given
    if second_location == 'request_input':
        second_location = input('Second location: ')
    
    # Retrieving coordinates associated with location from Geopy
    first_coordinates = get_location_coordinates(first_location)
    second_coordinates = get_location_coordinates(second_location)
    
    # Calculating and outputting distance between coordinates
    return coordinates_distance(
                                first_coordinates = first_coordinates, 
                                second_coordinates = second_coordinates, 
                                units = units
                                )

def normalised_coordinates_distance(first_coordinates: str, second_coordinates: str, units: str = 'kilometers') -> float:
    
    """
    Calculates the normalised distance between two coordinates, using units provided by user.
    
    Parameters
    ----------
    first_coordinates : str or list
        the first set of coordinates for comparison.
    second_coordinates : str or list
        the second set of coordinates for comparison.
    units : str
        units to use for distance calculation. Defaults to 'kilometers'.
    
    Returns
    -------
    result : float
        a value between 0 and 1, where 0 is 0 distance and 1 is infinite distance.
    
    Notes
    -----
    Normalisation function: map_inf_to_1()
    """
    
    # Calculating distance
    distance = coordinates_distance(first_coordinates, second_coordinates, units)
    
    # Normalising distance
    result = map_inf_to_1(distance[0])
    
    return result

def normalised_coordinates_distance_inverse(first_coordinates: str, second_coordinates: str, units: str = 'kilometers') -> float:
    
    """
    Calculates the inverse of the normalised distance between two coordinates.
    
    Parameters
    ----------
    first_coordinates : str or list
        the first set of coordinates for comparison.
    second_coordinates : str or list
        the second set of coordinates for comparison.
    units : str
        units to use for distance calculation. Defaults to 'kilometers'.
    
    Returns
    -------
    result : float
        a value between 0 and 1, where 1 is 0 distance and 0 is infinite distance.
    
    Notes
    -----
    Normalisation function: map_inf_to_0()
    """
    
    # Calculating distance
    distance = coordinates_distance(first_coordinates, second_coordinates, units)
    
    # Normalising distance
    result = map_inf_to_0(distance[0])
    
    return result


def normalised_locations_distance(first_location: str, second_location: str, units: str = 'kilometers') -> float:
    
    """
    Calculates the normalised distance between two locations.
    
    Parameters
    ----------
    first_location : str
        the first location name or address for comparison.
    second_location : str
        the second location name or address for comparison.
    units : str
        units to use for distance calculation. Defaults to 'kilometers'.
    
    Returns
    -------
    result : float
        a value between 0 and 1, where 0 is 0 distance and 1 is infinity.
    
    Notes
    -----
    Normalisation function: map_inf_to_1()
    """
    
    # Calculating distance
    distance = locations_distance(first_location, second_location, units)
    
    # Normalising distance
    result = map_inf_to_1(distance[0])
    
    return result

def normalised_locations_distance_inverse(first_location: str, second_location: str, units: str = 'kilometers') -> float:
    
    """
    Calculates the inverse of the normalised distance between two coordinates.
    
    Parameters
    ----------
    first_location : str
        the first location name or address for comparison.
    second_location : str
        the second location name or address for comparison.
    units : str
        units to use for distance calculation. Defaults to 'kilometers'.
    
    Returns
    -------
    result : float
        a value between 0 and 1, where 1 is 0 distance and 0 is infinity.
    
    Notes
    -----
    Normalisation function: map_inf_to_0()
    """
    
    # Calculating distance
    distance = locations_distance(first_location, second_location, units)
    
    # Normalising distance
    result = map_inf_to_0(distance[0])
    
    return result