"""Functions to load and parse PDFs"""

from ..core.cleaners import is_datetime, str_to_datetime

import re
import io
import copy
import requests
import numpy as np
import pandas as pd
from PyPDF2 import PdfFileReader, PdfReader, PdfWriter

def pdf_to_dict(file_path = None):
    
    """
    Reads PDF from file and outputs data as a dictionary.
    """
    
    # Requesting file address from user input if none provided
    if file_path == None:
        file_path = input('File path: ')
    
    # Reading PDF file
    pdf_file = PdfReader(file_path) 
    
    # Extracting metadata
    info = pdf_file.metadata
    
    # Iterating throigh pages and extracting text
    first_page_raw = pdf_file.pages[0]
    raw_text = []
    for i in pdf_file.pages:
        raw_text.append(i.extract_text())
    
    # Joining text list to make string
    full_text = ' \n '.join(raw_text)
    
    # Cleaning text
    full_text = re.sub(r"\s+[0-9]+\s", "", full_text).replace('\n ', ' <p> ').replace('\n', ' \n ').replace('  ', ' ')
    
    # Creating output dictionary 
    output_dict = {'metadata': info,
                  'raw': raw_text,
                  'first_page': first_page_raw,
                  'full_text': full_text}
    
    return output_dict


def pdf_url_to_dict(url = None):
    
    """
    Reads PDF from URL and outputs data as a dictionary.
    """
    
    # Requesting URL from user input if none provided
    if url == None:
        url = input('URL: ')
    
    # Setting browser headers for site request
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'}
    
    # Retrieving PDF data
    response = requests.get(url = url, headers=headers, timeout=120)
    on_fly_mem_obj = io.BytesIO(response.content)
    pdf_file = PdfReader(on_fly_mem_obj)
    
    # Extracting metadata
    info = pdf_file.metadata
    
    # Iterating throigh pages and extracting text
    first_page_raw = pdf_file.pages[0].extract_text()
    raw_text = []
    for i in pdf_file.pages:
        raw_text.append(i.extract_text())
    
    # Joining text list to make string
    full_text = ' \n '.join(raw_text)
    
    # Cleaning text
    full_text = re.sub(r"\s+[0-9]+\s", "", full_text).replace('\n ', ' <p> ').replace('\n', ' \n ').replace('  ', ' ')
    
    # Creating output dictionary
    output_dict = {'metadata': info,
                  'raw': raw_text,
                  'first_page': first_page_raw,
                  'full_text': full_text}
    
    return output_dict


def parse_pdf_text(input_data):
    
    """
    Parses text from PDF reader result.
    """
    
    # Checking type of input data and defining text variable for parsing
    if type(input_data) == str:
        text = input_data

    if (type(input_data) == dict) and ('full_text' in input_data.keys()):
        text = input_data['full_text']
    
    # Splitting text by line breaks
    lines = text.split('\n')
    
    # Calculating mean length of lines
    mean_length = pd.Series(lines).apply(len).describe()['mean']
    
    # Reformatting lines to reduce errors from PDF import
    new_lines = []
    
    # Iterating through each line
    for i in range(0, len(lines)):
        length = len(lines[i])
        
        # Checking if line is relatively short for document (under 20% of mean)
        if length <= (mean_length / 5):
            
            # If the length is 2 characters or more, adds line to previous line
            if (length >= 2) and (i != 0):
                new_line = (lines[i-1] + lines[i])
                
                # Removing previous line to prevent duplicates
                if lines[i-1] in new_lines:
                    new_lines.remove(lines[i-1])
                
                # Appending result to list
                new_lines.append(new_line)

        else:
            # If line is not shorter than minumum, appending line to lines
            if lines[i] not in new_lines:
                new_lines.append(lines[i])
    
    # Cleaning text
    new_lines = pd.Series(new_lines).str.replace(' \.', '.', regex = False).str.replace(' ;', ';', regex = False).str.replace(' :', ':', regex = False).str.replace(' ,', ',', regex = False).str.strip().to_list()
    
    # Rejoining text to form string
    text = ' '.join(new_lines[1:]).replace('<p>', '\n').replace('  ', '')
    
    # Removing paragraph tags
    new_lines = pd.Series(new_lines).str.replace('<p>', '\n', regex = False).to_list()
    
    # Creating output dictionary
    output = {'top': new_lines[0:5],
             'main_body': text[:refs_index]}
    
    return output


def parse_pdf_links(input_data):
    
    """
    Parses links from PDF reader result.
    """
    
    # Checking type of input data and defining variables for parsing
    if type(input_data) == str:
        text = input_data
        metadata = {}

    if (type(input_data) == dict) and ('first_page' in input_data.keys()):
        text = ' ~~~~~ '.join(input_data['raw'])
        metadata = input_data['metadata']
    
    # Checking if text contains web links
    if (
        ('https://' in text)
        or ('http://' in text)
        or ('www.' in text)
        or ('.co' in text)
        or ('.gov' in text)
        ):
            
            # Cleaning text
            text = text.replace(' /', '/').replace(': ', ':').replace(' :', ':').replace('\n', ' ').replace('’', ' ').replace(';', ' ').replace(',', ' ').replace('|', ' ').replace('[', ' ').replace(']', ' ').replace('}', ' ').replace('{', ' ').replace('"', ' ').replace("'", ' ').replace('□', ' ').replace('“', ' ').replace('”', ' ').replace('^', ' ').replace('©', ' ').replace('   ', '').replace('  ', ' ')
            
            # Splitting text into strings
            text_split = text.split(' ')
            
            # Extracting potential links
            links_res = [
                            i for i in text_split if (
                                                    ('https:' in i.lower()) 
                                                    or ('http:' in i.lower()) 
                                                    or ('www.' in i.lower())
                                                    or ('.com' in i.lower())
                                                    or ('.org' in i.lower())
                                                    or ('.net' in i.lower())
                                                    or ('.io' in i.lower())
                                                    or ('.co.uk' in i.lower())
                                                    or ('.co' in i.lower())
                                                    or ('.gov' in i.lower())
                                                    )
                        ]
            
            # Cleaning links
            links = [i.strip(')').strip('(').strip('source:').strip('See:').strip('vSee:').strip('Abstract').strip('Guard.iii').strip(':') for i in links_res]
            
            # Removing very string strings that are unlikely to be valid links
            links = [i for i in links if len(i) > 3]
            
            # Removing repeats
            result = list(set(links))
            
            return result
    

def parse_pdf_authors(input_data):
    
    """
    Identifies author details from PDF reader result.
    """
    
    # Checking type of input data and defining variables for parsing
    if type(input_data) == str:
        text = input_data
        metadata = {}

    if (type(input_data) == dict) and ('first_page' in input_data.keys()):
        text = input_data['first_page']
        metadata = input_data['metadata']
    
    # Creating output variable
    result = None
    
    # Checking for author metadata with key '/Author'
    if ('/Author' in metadata.keys()):
        
        # Retrieving metadata
        auth = metadata['/Author']
        
        # Cleaning metadata
        if (
            (auth != 'OscarWilde') 
            and (len(auth) > 2)
            ):
            result = auth.replace(" and ", ', ').replace('  ', '').replace('authors', '').replace('Authors', '').replace('author', '').replace('Author', '').strip()
        
        return result
    
    # Checking for author metadata with key 'Author'
    if ('Author' in metadata.keys()):
            
            # Retrieving metadata
            auth = str(metadata['Author'])
            
            # Cleaning metadata
            if (
                (auth != 'OscarWilde') 
                and (len(auth) > 2)
                ):
                result = auth.replace(" and ", ', ').replace('  ', '').replace('authors', '').replace('Authors', '').replace('author', '').replace('Author', '').strip()
            return result
        
    # Checking for author metadata with key '/author'
    if ('/author' in metadata.keys()):
        
                # Retrieving metadata
                auth = str(metadata['/author'])
                
                # Cleaning metadata
                if (
                    (auth != 'OscarWilde') 
                    and (len(auth) > 2)
                    ):
                    result = auth.replace(" and ", ', ').replace('  ', '').replace('authors', '').replace('Authors', '').replace('author', '').replace('Author', '').strip()
                return result
            
    # Checking for author metadata with key 'author'
    if ('author' in metadata.keys()):
        
                # Retrieving metadata
                auth = str(metadata['author'])
                
                # Cleaning metadata
                if (
                    (auth != 'OscarWilde') 
                    and (len(auth) > 2)
                    ):
                    result = auth.replace(" and ", ', ').replace('  ', '').replace('authors', '').replace('Authors', '').replace('author', '').replace('Author', '').strip()
                return result
    
    # If no author metadata found, tries to extract it from text
    else:
        
        # Checking if authors are named in text
        if ('author' in text.lower()) or ('by' in text.lower()):
            
                        # Splitting text into lines
                        fp_lines = text.split('\n')
                    
                        # Cleaning text to identify author name strings
                        cleaned_lines = []
                        for i in fp_lines:
                            i_lower = i.lower()
                            if (('author ' in i_lower) or ('author:' in i_lower) or ('authors' in i_lower) or ('by:' in i_lower) or ('et al.' in i_lower) or (': ' in i_lower)):
                                cleaned_lines.append(i.split(' .')[0])
                                
                        # Cleaning text to identify author name strings, round 2
                        split_lines = []
                        for line in cleaned_lines:
                            split_line = line.replace('&', ',').replace('|', '').replace('et al', 'et al.').replace(' ,', ',').split(': ')
                            try:
                                split_lines.append(split_line[1])

                            except:
                                split_lines.append(split_line[0])
                        
                        # Creating set of cleaned line segments
                        lines_set = set(split_lines)
                        
                        # First line in result is assumed to likely contain author names
                        try:
                            
                            # Cleaning text
                            result = list(lines_set)[0].replace(" and ", ', ').replace('  ', '').replace('authors', '').replace('Authors', '').replace('author', '').replace('Author', '').strip()

                        except:
                            None
        
            
        
        return result    

def parse_pdf_date(pdf_dict):
    
    """
    Parses date from PDF reader result.
    """
    
    # Checking type of input
    if (type(pdf_dict) != dict) or ('metadata' not in pdf_dict.keys()):
        return TypeError('Input must be a dictionary of data outputted by parsing PDF')
    
    # Retrieving metadata
    metadata = pdf_dict['metadata']
    
    # Checking for date metadata with key '/CreationDate'
    if ('/CreationDate' in metadata.keys()):
        date = metadata['/CreationDate']
    
    # Checking for date metadata with key '/Date'
    if ('/Date' in metadata.keys()):
            date = metadata['/Date']
            
    # Checking for date metadata with key 'CreationDate'
    if ('CreationDate' in metadata.keys()):
        date = metadata['CreationDate']
    
    # Checking for date metadata with key 'creationdate'
    if ('creationdate' in metadata.keys()):
        date = metadata['CreationDate']
    
    # Checking for date metadata with key 'Date'
    if ('Date' in metadata.keys()):
            date = metadata['Date']
            
    # Checking for date metadata with key 'date'
    if ('date' in metadata.keys()):
            date = metadata['Date']
    
    # Checking if the result is already a datetime object; if yes, returning it
    if is_datetime(date) != True:
        return date
    
    # Else, converting to datetime object
    else:
        
        # Cleaning string
        date = date.strip().replace('D:', '').replace('.', '').replace("'", '.').strip("'").strip('.').strip()

        try:
            date = str_to_datetime(date)
        except:
            pass

        return date

        

def parse_pdf_title(input_data):
    
    """
    Parses title from PDF reader result.
    """
    
    # Checking type of input data and defining variables for parsing
    if type(input_data) == str:
        text = input_data
        metadata = {}

    if (type(input_data) == dict) and ('first_page' in input_data.keys()):
        text = input_data['first_page']
        metadata = input_data['metadata']
    
    # Checking for title metadata with key '/Title'
    if ('/Title' in metadata.keys()):
        
        # Retrieving metadata
        title = metadata['/Title']
        
        # Cleaning metadata
        if (
            (title != '') 
            and (len(title) > 2)
            ):
            return title.replace('  ', ' ').replace('titles', '').replace('Titles', '').replace('title', '').replace('Title', '').strip()
    
    # Checking for title metadata with key 'Title'
    if ('Title' in metadata.keys()):
        
            # Retrieving metadata
            title =str(metadata['Title'])
            
            # Cleaning metadata
            if (
                (title != '') 
                and (len(title) > 2)
                ):
                return title.replace('  ', ' ').replace('titles', '').replace('Titles', '').replace('title', '').replace('Title', '').strip()
    
    # Checking for title metadata with key 'title'
    if ('title' in metadata.keys()):
        
            # Retrieving metadata
            title = str(metadata['title'])
            
            # Cleaning metadata
            if (
                (title != '') 
                and (len(title) > 2)
                ):
                return title.replace('  ', ' ').replace('titles', '').replace('Titles', '').replace('title', '').replace('Title', '').strip()
    
    # If no title metadata found, looking for title string in text
    else:
                
        output = None
        
        # Checking if 'title' is in text
        if ('title' in text.lower()) or ('name' in text.lower()):
                        
                        # Splitting text into lines
                        fp_lines = text.split('\n')
                        
                        # Removing lines which don't include 'name' or 'title'
                        cleaned_lines = []
                        for i in fp_lines:
                            if ('Title' in i) or ('title ' in i) or ('title:' in i) or ('titles' in i) or ('Titles' in i) or ('name' in i) or ('Name' in i):
                                cleaned_lines.append(i.split(' .')[0])
                        
                        # Splitting lines into phrases
                        split_lines = []
                        for line in cleaned_lines:
            
                            split_line = line.replace('|', '').replace('et al', 'et al.').split('.')
                            try:
                                split_lines.append(split_line[1])

                            except:
                                split_lines.append(split_line[0])
                        
                        # Removing duplicates
                        lines_set = set(split_lines)
                        
                        # Returning first line found, assuming this is more likely to be the title
                        try:
                            
                            # Cleaning string
                            output = list(lines_set)[0].replace('  ', ' ').replace('titles', '').replace('Titles', '').replace('title', '').replace('Title', '').strip()
                            
                        except:
                            output = None
        
        # If the result so far is None or very short, tries to join result with second and third lines
        if (output == None) or (len(output) <5):
            output = ' - '.join(parse_pdf_text(input_data)['top'][0:2])
            if 'authors' in output.lower():
                output = None
            
        return output
                

def parse_pdf_reader_dict(pdf_dict):
    
    """
    Parses PDF reader result.
    """
    
    # Making copy of source data
    to_parse = copy.deepcopy(pdf_dict)
    
    # Initialising output variable
    output_dict = {}
    
    # Adding text and metadata to variable
    output_dict['raw'] = pdf_dict['raw']
    output_dict['full_text'] = pdf_dict['full_text']
    output_dict['attached_metadata'] = pdf_dict['metadata']
    
    # Trying to extract title
    try:
        output_dict['title'] = parse_pdf_title(to_parse)
    except:
        output_dict['title'] = None
    
    # Trying to extract authors
    try:
        output_dict['authors'] = parse_pdf_authors(to_parse)
    except:
        output_dict['authors'] = None
    
    # Trying to extract date
    try:
        output_dict['date'] = parse_pdf_date(to_parse)
    except:
        output_dict['date'] = None
    
    # Trying to extract links
    try:
        output_dict['links'] = parse_pdf_links(to_parse)
    except:
        output_dict['links'] = None
    
    # Trying to extract text
    try:
        output_dict['text'] = parse_pdf_text(to_parse)
    except:
        output_dict['text'] = None
    
    return output_dict

def read_pdf(file_path: str = None) -> dict:
    
    """
    Loads and parses PDF file. Returns a dictionary of data.
    """
    
    # Retrieving PDF data
    pdf_dict = pdf_to_dict(file_path = file_path)
    
    # Parsing PDF data
    output = parse_pdf_reader_dict(pdf_dict)
    
    return output
    

def read_pdf_url(url = None):
    
    """
    Downloads and parses PDF file from a URL. Returns a dictionary of data.
    """
    
    # Retrieving PDF data
    pdf_dict = pdf_url_to_dict(url = url)
    
    # Parsing PDF data
    output = parse_pdf_reader_dict(pdf_dict)
    
    return output