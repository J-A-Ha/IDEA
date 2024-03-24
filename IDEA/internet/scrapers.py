"""Functions for scraping web data"""

from .webanalysis import correct_url, get_domain, is_domain, domain_splitter, is_registered_domain, url_to_valid_attr_name

from typing import List, Dict, Tuple
import json
import requests

import numpy as np
import pandas as pd

from requests_html import HTML
from requests_html import HTMLSession

import cloudscraper

from trafilatura import fetch_url, extract, feeds, sitemaps, extract_metadata

from urllib import robotparser
from urllib.parse import quote, quote_plus, urlparse

from bs4 import BeautifulSoup

from courlan import extract_domain, normalize_url, clean_url, validate_url, sample_urls, check_url, scrub_url, is_external

from selenium import webdriver
from selenium.webdriver.common.by import By


def get_url_source(url = 'request_input'):
    
    """Returns the HTTP response for the provided URL. 

    Parameters
    ---------- 
    url : str
        URL of the page to scrape.

    Returns
    -------
    response : object
        HTTP response object from cloudscraper.
    """
    
    # Requesting URL from user input if none given
    if url == 'request_input':
        url = input('URL: ')
    
    # Correcting errors in URL (e.g. missing HTTPS prefix)
    url = correct_url(url)
   
    # Trying to scrape site using CloudScraper to avoid Cloudflare protection
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        return response
    
    # Handling errors
    except:
        raise ValueError('Scraper failed')

        
def scrape_url_html(url = 'request_input') -> str:
    
    """Scrapes raw HTML code from the provided URL. 

    Parameters
    ---------- 
    url : str
        URL of the page to scrape.

    Returns
    -------
    HTML : str
        the returned HTML as a string."""
    
    # Requesting URL from user input if none given
    if url == 'request_input':
        url = input('URL: ')
    
    # Correcting errors in URL (e.g. missing HTTPS prefix)
    url = correct_url(url = url)
    
    # Retrieving HTTP response
    response = get_url_source(url = url)
    
    # Extracting HTML
    result = response.text
    
    return result


def scrape_url_metadata(url = 'request_input') -> dict:
    
    """Scrapes metadata from the provided URL. 

    Parameters
    ---------- 
    url : str 
        URL of the page to scrape.

    Returns
    -------
    metadata : dict
        the URL's metadata as a dictionary."""
    
    # Requesting URL from user input if none given
    if url == 'request_input':
        url = input('URL: ')
    
    # Correcting errors in URL (e.g. missing HTTPS prefix)
    url = correct_url(url = url)
    
    # Using trafilatura to fetch site data
    downloaded = fetch_url(url = url)
    
    # Creating empty result variable to avoid errors
    result = None
    
    # Extracting metadata and assigning to result variable
    if downloaded != None:
        result = extract_metadata(downloaded)
        
        if result != None:
            
            # Converting result to dictionary
            result = result.as_dict()
            
        else:
            result = None
        
    return result


def scrape_url_rawtext(url = 'request_input') -> str:
    
    """Scrapes raw text from the provided URL. 

    Parameters
    ---------- 
    url : str 
        URL of the page to scrape.

    Returns
    -------
    rawtext : str
        the URL's raw text as a string."""
    
    # Requesting URL from user input if none given
    if url == 'request_input':
        url = input('URL: ')
    
    # Correcting errors in URL (e.g. missing HTTPS prefix)
    url = correct_url(url = url)
    
    # Using trafilatura to fetch site data
    downloaded = fetch_url(url = url)
    
    if downloaded != None:
        
        # Extracting raw text and assigning to result variable
        result = extract(downloaded, include_tables=True, include_comments=True, include_images=True, include_links=True)
    
    return result

def scrape_url_xml(url = 'request_input') -> str:
    
    """Scrapes data from the provided URL and returns in XML format. 

    Parameters
    ---------- 
    url : str 
        URL of the page to scrape.

    Returns
    -------
    xml : str
        the URL's data as an XML-formatted string."""
    
    # Requesting URL from user input if none given
    if url == 'request_input':
        url = input('URL: ')
    
    # Correcting errors in URL (e.g. missing HTTPS prefix)
    url = correct_url(url = url)
    
    # Using trafilatura to fetch site data
    downloaded = fetch_url(url)
    if downloaded != None:
        
        # Extracting data and assigning to result variable
        result = extract(downloaded, output_format="xml", include_tables=True, include_comments=True, include_images=True, include_links=True)
    
    return result


def scrape_url_json(url = 'request_input') -> str:
    
    """Scrapes data from the provided URL and returns in JSON format. 

    Parameters
    ---------- 
    url : str 
        URL of the page to scrape.

    Returns
    -------
    json : str
        the URL's data as a JSON-formatted string."""
    
    # Requesting URL from user input if none given
    if url == 'request_input':
        url = input('URL: ')
    
    # Correcting errors in URL (e.g. missing HTTPS prefix)
    url = correct_url(url = url)
    
    # Using trafilatura to fetch site data
    downloaded = fetch_url(url)
    if downloaded != None:
        
        # Extracting data and assigning to result variable
        result = extract(downloaded, output_format="json", include_tables=True, include_comments=True, include_images=True, include_links=True)
    else:
        result = ''
        
    return result


def scrape_url_csv(url = 'request_input'):
    
    """Scrapes data from the provided URL and returns in CSV format. 

    Parameters
    ---------- 
    url : str 
        URL of the page to scrape.

    Returns
    -------
    csv : str
        the URL's data as a CSV-formatted string."""
    
    # Requesting URL from user input if none given
    if url == 'request_input':
        url = input('URL: ')
    
    # Correcting errors in URL (e.g. missing HTTPS prefix)
    url = correct_url(url = url)
    
    # Using trafilatura to fetch site data
    downloaded = fetch_url(url)
    if downloaded != None:
        
        # Extracting data and assigning to result variable
        result = extract(downloaded, output_format="csv", include_tables=True, include_comments=True, include_images=True, include_links=True)
    
    return result


def scrape_url_to_dict(url = 'request_input') -> str:
    
    """Scrapes data from provided URL and returns as a dictionary. 

    Parameters
    ---------- 
    url : str 
        URL of the page to scrape.

    Returns
    -------
    result : dict 
        the URL's data as a dictionary."""
    
    # Retrieving site data as a JSON-formatted string
    result_json = scrape_url_json(url = url)
    
    # Avoiding errors if no result retrieved
    if result_json == None:
        result = {}
    
    else:
        # Converting JSON to dictionary
        result = json.loads(result_json)
    
    return result
    

def scrape_url_links(url = 'request_input') -> List[str]:
    
    """Scrapes links from provided URL and returns as a list. 

    Parameters
    ---------- 
    url : str 
        URL of the page to scrape.

    Returns
    -------
    links : list 
        the URL's links as a list."""
    
    # Requesting URL from user input if none given
    if url == 'request_input':
        url = input('URL: ')
    
    # Scraping data
    scraped_data = scrape_url_html(url = url)
    
    # Making HTML soup
    soup = BeautifulSoup(scraped_data, "html.parser")
    
    # Selecting dividers
    href_select = soup.select("a")  
    
    # Extracting links as list and applying corrections 
    links = [correct_link_errors(source_domain = url, url = i['href']) for i in href_select if 'href' in i.attrs]
    
    return links

    
def scrape_url(url = 'request_input', parse_pdf = True, output: str = 'dict'):
    
    """Scrapes data from URL. Returns any HTML code, text, links, and metatdata found. 
    
    Defaults to returning a dictionary.
    
    Parameters
    ---------- 
    url : str 
        URL of the page to scrape.
    parse_pdf : bool
        whether to detect PDFs and parse them using PDF parser.

    Returns
    -------
    result : object
        the result in a user-selected format.
    """
    
    # Requesting URL from user input if none given
    if url == 'request_input':
        url = input('URL: ')
        
    # Cleaning URL
    url = url.strip("'").strip('"').strip()
    
    # Running scrapers depending on the format specified
    
    output = output.lower().strip()
    
    if output == 'html':
        result = scrape_url_html(url = url)
    
    if (output == 'raw') or (output == 'rawtext') or (output == 'raw text'):
        result = scrape_url_rawtext(url = url)
    
    if output == 'xml':
        result = scrape_url_xml(url = url)
    
    if output == 'json':
        result = scrape_url_json(url = url)
    
    if output == 'csv':
        result = scrape_url_csv(url = url)
    
    # If the output format selected is dictionary, scrapes all data available
    if output == 'dict':
        
        # Running main scraper
        result = scrape_url_to_dict(url = url)
        
        # Appending html to output dict
        result['html'] = scrape_url_html(url = url)
        
        # Extracting links
        current_url = url
        soup = BeautifulSoup(result['html'], "html.parser")
        href_select = soup.select("a")
        links = [correct_link_errors(source_domain = current_url, url = i['href']) for i in href_select if 'href' in i.attrs]
        result['links'] = links
        
        # If parse_pdf is selected, check if URL is PDF and parse
        
        if parse_pdf == True:
            
            if url.endswith('.pdf') == True:
                
                # Running PDF downloader and parser
                pdf_parsed = read_pdf_url(url = url)
                
                # Appending result
                result['title'] = pdf_parsed['title']
                result['author'] = pdf_parsed['authors']
                result['raw_text'] = pdf_parsed['raw']
                result['text'] = pdf_parsed['full_text']
                result['date'] = pdf_parsed['date']
                result['links'] = pdf_parsed['links']
                result['format'] = 'PDF'
                result['type'] = 'document'
        
        # Scraping URL metadata using trafilatura
        metadata = scrape_url_metadata(url = url)
        if metadata != None:
            for key in metadata.keys():
                if key not in result.keys():
                    result[key] = metadata[key]
        
        # Appending URL
        result['url'] = url
        
    return result


def scrape_urls_list(urls: list, parse_pdf = True, output: str = 'dataframe'):
    
    """Scrapes list of URLs. Returns any HTML code, text, links, and metatdata found. 
    
    Defaults to returning a dataframe.
    
    Parameters
    ---------- 
    url : str 
        URL of the page to scrape.
    parse_pdf : bool
        whether to detect PDFs and parse them using PDF parser.

    Returns
    -------
    result : object 
        the result in a user-selected format."""
    
    # Initialising dictionary for results
    output_dict = {}
    
    # Iterating through links and scraping
    for link in urls:
        output_dict[link] = scrape_url(url = link, parse_pdf = parse_pdf, output = 'dict')
    
    # If selected output is dataframe, converting to dataframe
    if output == 'dataframe':
        output = pd.DataFrame.from_dict(output_dict).T
    
    else:
        output = output_dict
    
    return output


def scrape_dynamic_page(url = 'request_input') -> dict:
    
    """Scrapes dynamic webpages using provided URL. Returns a dictionary of data. Uses Selenium.
    
    Parameters
    ---------- 
    url : str 
        URL of the page to scrape.

    Returns
    -------
    result : dict 
        the result as a dictionary."""
    
    # Initialising dictionary for results
    if url == 'request_input':
        url = input('URL: ')
    
    # Correcting errors in URL (e.g. missing HTTPS prefix)
    url = correct_url(url)
    
    # Initialising Selenium webdriver
    driver = webdriver.Chrome()
    
    # Retrieving data
    driver.get(url)
    
    # Selecting CSS elements
    items = driver.find_elements(By.CSS_SELECTOR, ".grid a[data-testid='link']")
    
    # Iterating through results, retrieving attributes, and adding to output dictionary
    output_dict = {}
    index = 0
    
    for item in items:
        
        name = item.accessible_name
        if name == None:
            try:
                name = item.get_attribute('name')
            except:
                name = None
        
        if name == None:
            name = index
            index += 1
        
        # Retrieving text
        text = item.text
        output_dict[name] = text
    
    return output_dict


def scrape_google_search(query: str = 'request_input'):

    """Fetches and parses Google Search results. Offers an alternative to using Google's API. 
    
    Requires user to manually copy and paste Google search source code to avoid Google's CAPCHA system.
    
    Parameters
    ----------
    query : str
        query to search. Defaults to requesting from user input.
    """
    
    print('This function will open your web browser. When prompted, copy and paste the code that appears into the space provided\n')
    
    # Launching web search
    search_web(
                query = query,
                search_engine = 'Google',
                view_source = True
                )
    
    # Requesting search source code from user
    html = input('Search page code: ')
    
    # Parsing result
    output = parse_google_result(html)
    
    return output


def crawler_scraper(current_url: str, full: bool) -> tuple:
    
    """Scraper used by web crawler. Returns result as a tuple. 
    
    Parameters
    ---------- 
    current_url : str 
        URL of the page to scrape.
    full : bool 
        whether to run complete scrape.

    Returns
    -------
    result : tuple 
        the result as a tuple containing BeautifulSoup object, the scraped data, and links."""
    
    # If full is selected, runs a complete scrape using tools
    if full == True:
        
        # Tries to scrape URL using standard scraper function
        try:
            scraped_data = scrape_url(current_url)
        
        # If scraper fails, runs cleaners on URL and tries to run it again
        except:
            current_url = clean_url(current_url)
            current_url = scrub_url(current_url)
            current_url = normalize_url(current_url)
            current_url = correct_url(current_url)

            try:
                scraped_data = scrape_url(current_url)

            except:
                
                # If standard scraper fails twice, tries to use cloudscraper's basic scraper
                try:
                    scraper = cloudscraper.create_scraper()
                    res = scraper.get(current_url)
                    scraped_data['html'] = res.content
                    
                except:
                    scraped_data['html'] = ''
    
    # If full is not selected, runs cloudscraper's basic scraper
    else:
        
        try:
            
            scraper = cloudscraper.create_scraper()
            res = scraper.get(current_url)
            scraped_data['html'] = res.content
            
        except:
            scraped_data['html'] = ''
        
    # Making HTML soup
    soup = BeautifulSoup(scraped_data['html'], "html.parser")
    
    # Selecting dividers
    href_select = soup.select("a")  
    
    # Extracting links
    links = [correct_link_errors(source_domain = current_url, url = i['href']) for i in href_select if 'href' in i.attrs]          
    
    # Returning results as tuple
    return (soup, scraped_data, links)
