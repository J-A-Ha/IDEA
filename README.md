---
title: 'Investigative Data Analyser'
---

<!-- Investigative Data and Evidence Analyser (IDEA)
=== -->
<!-- ![downloads](https://img.shields.io/github/downloads/atom/atom/total.svg) -->
<!-- ![build](https://img.shields.io/appveyor/ci/:user/:repo.svg)
![chat](https://img.shields.io/discord/:serverId.svg) -->

# Investigative Data and Evidence Analyser (IDEA)

IDEA is a toolkit for conducting investigations using data. It is written in Python and R.

## Table of Contents

[TOC]

## Description

### Features

Case management
* File management
* Object-oriented case management interface

Data cleaning
* Text cleaning
    * Reformatting
    * Stopword removal
* Text tokenizing
    * Word tokenization
    * Sentence tokenization
* HTML parsing

Metadata analysis
* Metadata similarity analysis

Text analysis
* Keyword analysis
* Extraction of key information (e.g. names, locations)
* Text similarity analysis

Image analysis
* Reverse image search

Location analysis
* Geolocation
* Chronolocation

Internet analysis
* Web scraping and crawling
* WhoIs lookups on domains and IP addresses
* Web search
* Website similarity analysis
* Web archiving
    * Internet Archive/Wayback Machine
    * Archive.is
    * Common Crawl

Social media analysis
* Platform-specific searches
* Username lookups
* Scraping

Network analysis
* Centrality analysis
* Co-link analysis
* Community detection
* and much more...

Data visualisation
* Network visualisation
* Timelines



## User Guide

### Installation



To download from GitHub, run the following code in your command interface:
```bash
cd downloads
git clone <repository address>
```

### Beginners Guide


<!-- > Read more about sequence-diagrams here: http://bramp.github.io/js-sequence-diagrams/
 -->

### Examples

#### Importing IDEA

```python!
import invdata as idea
```

#### Creating and saving a case from an Excel file

```python!
example = idea.open_case(case_name = 'example', file_address = 'example.xlsx')

example.save_as(file_name = 'example', file_type = 'case', file_address = '/')
```

#### Creating a case from a web crawl

```python!
example = idea.Case(case_name = 'example')
example.crawl_web()

# You will be asked to input a URL or list of URLs to crawl from.
```

#### Running all analysis functions on a case

This will:
* Parse all raw data
* Extract keywords
* Identify instances of coinciding data, metatada, links, etc.
* Index all items, data, metadata, etc.
* Generate similarity networks based on inputted data
* Generate link networks if links are provided
* Run all statistical analytics
* Save to the Case object

```python!
example = idea.open_case(case_name = 'example', file_address = 'example.case')
example.run_full_analysis()
print(example.analytics)
```

### Key Classes and Functions

#### Classes
##### Project

```python!
class Project(...)
```
A collection of Case objects.

Useful methods:
* 

##### Case

```python!
class Case(...)
```
An object to store raw data, metadata, and other information related to investigative cases.

Useful methods:
* 

##### CaseData
```python!
class CaseData(...)
```
A collection of Pandas dataframes containing the combined data for a Case.

Useful methods:
* 

##### CaseItem
```python!
class CaseItem(...)
```
An object representing a piece of material or evidence associated with a Case.

Useful methods:
* 

##### CaseNetwork

```python!
class CaseNetwork(igraph.Graph)
```
A modified igraph.Graph object. It provides additional analytics methods and functionality for Case management. CaseNetworks can convert both igraph and NetworkX graph objects.

Useful methods:
* 

##### CaseFile

```python!
class CaseFile(CaseObject)
```
An object which stores details about a digital file associated with a case or piece of evidence.

Useful methods:
* 

#### Functions
##### Case management

* [open_case()](../docs/_build/html/ida.casemanager.html?highlight=open_case#ida.casemanager.general.open_case)
* [save()](../docs/_build/html/ida.casemanager.html?highlight=save_as#ida.casemanager.general.save)
* [save_as()](../docs/_build/html/ida.casemanager.html?highlight=save_as#ida.casemanager.general.save_as)
* [get_backups()](../docs/_build/html/ida.casemanager.html?highlight=get_backups#ida.casemanager.backups_manager.get_backups)
* [set_default_case()](../docs/_build/html/ida.casemanager.html?highlight=set_default_case#ida.casemanager.defaults_manager.set_default_case)
* [get_default_case()](../docs/_build/html/ida.casemanager.html?highlight=get_default_case#ida.casemanager.defaults_manager.get_default_case)

##### Importing files
* [import_case_excel()](../docs/_build/html/ida.casemanager.html?highlight=import_case_excel#ida.casemanager.general.import_case_excel)
* [import_case_csv_folder()](../docs/_build/html/ida.casemanager.html?highlight=import_case_csv#ida.casemanager.general.import_case_csv_folder)
* [import_case_txt()](../docs/_build/html/ida.casemanager.html?highlight=import_case_txt#ida.casemanager.general.import_case_txt)
* [read_pdf()](../docs/_build/html/ida.importers.html?highlight=read_pdf#ida.importers.pdf.read_pdf)
* [read_pdf_url()](../docs/_build/html/ida.importers.html?highlight=read_pdf#ida.importers.pdf.read_pdf)

##### Location analysis
* get_coordinates_location()
* get_location_address()
* get_location_coordinates()

##### Internet analysis
* lookup_whois()

##### Web searching
* open_url()
* open_url_source()
* search_web()
* multi_search_web()
* search_images()
* search_social_media()

##### Web crawling
* crawl_site()
* crawl_web()

##### Social media analysis
* search_username()

### Documentation

For the full documentation, click [here](../docs/_build/html/index.html).

### Dependencies

Python packages and modules:
* NumPy
* SciPy
* Pandas
* NLTK
* numpy
* matplotlib
* geopy
* geocoder
* python-whois
* ipwhois
* igraph
* NetworkX
* mpl-tools
* PyPDF2
* requests
* beautifulsoup4
* requests-html
* scikit-learn
* Levenshtein
* wayback
* htmldate
* selectolax
* Pillow
* sewar
* trafilatura
* rpy2
* courlan
* comcrawl
* Sherlock
* Shodan
* Instaloader
* Cloudscraper

R libraries:
* ERGM


## Contributing

## Authors and acknowledgments

IDEA was created by Jamie Hancock.

It relies on packages and modules created by:
* Geocoder: 
* Geopy:
* Shodan: 
* Sherlock: 
* Instaloader:
* RPy2
* ERGM
* python-whois
* ipwhois
* trafilatura
* Cloudscraper
* Levenshtein
* python-whois
* ipwhois


## License


## Appendix and FAQ

### Project Timeline
---
```mermaid
gantt
    title Timeline
```

<!-- > Read more about mermaid here: http://mermaid-js.github.io/mermaid/ -->


###### tags: `Python`, `R`, `Investigations`, `OSI`, `OSINT`, `Documentation`
