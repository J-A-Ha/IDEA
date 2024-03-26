"""Functions for analysing dates and times"""

from ..core.basics import map_inf_to_1, map_inf_to_0
from ..core.cleaners import str_to_datetime

from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple
import copy


def time_difference(first_date: str = 'request_input', second_date: str = 'request_input') -> timedelta:
    
    """
    Returns the time difference between two datetimes.
    
    Parameters
    ----------
    first_date : str or datetime.datetime
        first date for comparison as a string or datetime object. Defaults to requesting from user input.
    second_date : str or datetime.datetime
        second date for comparison as a string or datetime object. Defaults to requesting from user input.
    
    Returns
    -------
    time_difference : datetime.timedelta
        the time difference between the inputted dates.
    """
    
    # Requesting first date from user input if none given
    if first_date == 'request_input':
        first_date = input('First date or time: ')
    
    # Requesting second date from user input if none given
    if second_date == 'request_input':
        second_date = input('Second date or time: ')
    
    # Converting first date to datetime object
    try:
        dt1 = str_to_datetime(first_date, False)
    except:
        return print('d1_error')
    
    # Converting second date to datetime object
    try:
        dt2 = str_to_datetime(second_date, False)
    except:
        return print('d2_error')
    
    # Calculating time difference
    result = abs(dt1 - dt2)
    
    return result

def years_difference(first_date: str = 'request_input', second_date: str = 'request_input'):
    
    """
    Returns the number of years separating two datetimes.
    
    Parameters
    ----------
    first_date : str or datetime.datetime
        first date for comparison as a string or datetime object. Defaults to requesting from user input.
    second_date : str or datetime.datetime
        second date for comparison as a string or datetime object. Defaults to requesting from user input.
    
    Returns
    -------
    time_difference : datetime.timedelta
        the time difference in years between the inputted dates.
    """
    
    # Requesting first date from user input if none given
    if first_date == 'request_input':
        first_date = input('First date or time: ')
    
    # Requesting second date from user input if none given
    if second_date == 'request_input':
        second_date = input('Second date or time: ')
    
    # Converting dates to datetime objects
    first_dt = str_to_datetime(first_date)
    second_dt = str_to_datetime(second_date)
    
    # Formatting datetime objects as years
    first_year = int(first_dt.strftime("%Y"))
    second_year = int(second_dt.strftime("%Y"))
    
    # Calculating time difference
    result = abs(second_year - first_year)
    
    return result
    

def datetime_to_years_decimal(date) -> float:
    
    """
    Converts datetime to a year with a decimal representing the number of additional days.
    
    Parameters
    ----------
    date : str or datetime.datetime
        date as a string or datetime object.
    
    Returns
    -------
    result : float
        the datetime as a year with a decimal representing the number of additional days.
    """
    
    # Checking types to ensure object is datetime
    if type(date) == datetime:
        dt = date
    
    elif type(date) == str:
        dt = str_to_datetime(date)
    
    # Converting datetime object to string in year format
    year = int(dt.strftime('%Y'))
    
    # Calculating the value of the next year
    next_year = year + 1
    
    # Converting inputted year and next year to datetime objects 
    year_dt = datetime.strptime(str(year), '%Y')
    next_year_dt = datetime.strptime(str(next_year), '%Y')
    
    # Calculating length of the remaining days in the year 
    year_len = next_year_dt - year_dt
    remainder = next_year_dt - dt
    remainder_decimal = remainder / year_len
    
    # Calculating final result
    result = year + remainder_decimal
    
    return result
        

def years_decimal_timedelta(first_date: str = 'request_input', second_date: str = 'request_input'):
    
    """
    Returns the number of years separating two datetimes as a float.
    
    Parameters
    ----------
    first_date : str or datetime.datetime
        first date for comparison as a string or datetime object. Defaults to requesting from user input.
    second_date : str or datetime.datetime
        second date for comparison as a string or datetime object. Defaults to requesting from user input.
    
    Returns
    -------
    result : float
        the time difference in years with a decimal representing the number of additional days.
    """
    
    # Requesting first date from user input if none given
    if first_date == 'request_input':
        first_date = input('First date or time: ')
    
    # Requesting second date from user input if none given
    if second_date == 'request_input':
        second_date = input('Second date or time: ')
    
    # Converting dates to datetime objects 
    first_dt = datetime_to_years_decimal(first_date)
    second_dt = datetime_to_years_decimal(second_date)
    
    # Calculating final result
    result =  abs(second_dt - first_dt)
    
    return result
    
    
def timedelta_to_days(timedelta):
    
    """
    Converts datetime timedelta object to a number of days with a decimal remainder.
    """
    
    # Retrieving time data and converting to float objects 
    days = float(timedelta.days)
    seconds = float(timedelta.seconds)
    
    # Calculating remainder
    remainder = seconds / float((60**2)*24)
    
    # Calculating final result
    result = days + remainder
    
    return result
    
    
def timedelta_to_weeks(timedelta):
    
    """
    Converts datetime timedelta object to a number of weeks with a decimal remainder.
    """
    
    # Calculating result
    result = timedelta_to_days(timedelta) / 7
    
    return result
    
def timedelta_to_hours(timedelta):
    
    """
    Converts datetime timedelta object to a number of hours with a decimal remainder.
    """
    
    # Calculating result
    result = timedelta_to_days(timedelta)*24
    
    return result

def timedelta_to_mins(timedelta):
    
    """
    Converts datetime timedelta object to a number of minutes with a decimal remainder.
    """
    
    # Calculating result
    result = timedelta_to_days(timedelta)*24*60
    
    return result


def timedelta_to_secs(timedelta):
    
    """
    Converts datetime timedelta object to a number of seconds with a decimal remainder.
    """
    
    # Calculating result
    result = timedelta.total_seconds()
    
    return result


def normalised_time_difference(first_datetime, second_datetime, units: str = 'days') -> float:
    
    """
    Calculates the normalised time difference for two dates/times.
    
    Parameters
    ----------
    first_datetime : str or datetime.datetime
        first date for comparison as a string or datetime object.
    second_datetime : str or datetime.datetime
        second date for comparison as a string or datetime object.
    units : str
        units for time difference calculation. Defaults to 'days'.
    
    Returns
    -------
    result : float
        a value between 0 and 1, where 0 is 0 time difference and 1 is infinity.
    
    Notes
    -----
    Normalisation function: map_inf_to_1()
    """
    
    # Calculating time difference
    td = time_difference(first_datetime, second_datetime)
    
    # Converting time difference into selected units
    
    if units == 'years':
        td = years_decimal_timedelta(first_datetime, second_datetime)
    
    if units == 'weeks':
        td = timedelta_to_weeks(td)
    
    if units == 'days':
        td = timedelta_to_days(td)
    
    if units == 'hours':
        td = timedelta_to_hours(td)
    
    if units == 'minutes':
        td = timedelta_to_mins(td)
    
    if units == 'seconds':
        td = timedelta_to_secs(td)
    
    # Normalising result
    result = map_inf_to_1(td)
    
    return result
    

def normalised_time_difference_inverse(first_datetime, second_datetime, units: str = 'days') -> float:
    
    """
    Calculates the inverse of the normalised distance between two coordinates.
    
    Parameters
    ----------
    first_datetime : str or datetime.datetime
        first date for comparison as a string or datetime object.
    second_datetime : str or datetime.datetime
        second date for comparison as a string or datetime object.
    units : str
        units for time difference calculation. Defaults to 'days'.
    
    Returns
    -------
    result : float
        a value between 0 and 1, where 1 is 0 distance and 0 is infinity.
    
    Notes
    -----
    Normalisation function: map_inf_to_0()
    """
    
    # Calculating time difference
    td = time_difference(first_datetime, second_datetime)
    
    # Converting time difference into selected units
    
    if units == 'years':
        td = years_decimal_timedelta(first_datetime, second_datetime)
    
    if units == 'weeks':
        td = timedelta_to_weeks(td)
    
    if units == 'days':
        td = timedelta_to_days(td)
    
    if units == 'hours':
        td = timedelta_to_hours(td)
    
    if units == 'minutes':
        td = timedelta_to_mins(td)
    
    if units == 'seconds':
        td = timedelta_to_secs(td)
    
    # Normalising result
    result = map_inf_to_0(td)
    
    return result