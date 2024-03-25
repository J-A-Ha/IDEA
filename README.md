---
title: 'Investigative Data and Evidence Analyser (IDEA)'
---

<!-- Investigative Data and Evidence Analyser (IDEA)
=== -->
<!-- ![downloads](https://img.shields.io/github/downloads/atom/atom/total.svg) -->
<!-- ![build](https://img.shields.io/appveyor/ci/:user/:repo.svg)
![chat](https://img.shields.io/discord/:serverId.svg) -->

# Investigative Data and Evidence Analyser (IDEA)

The Investigative Data and Evidence Analyser (IDEA) is a toolkit for conducting investigations using data. It is a Python package, written in Python and R.

## **Table of Contents**

[TOC]

## **Description**

IDEA is a toolkit for conducting investigations using data, written in Python and R. It provides a Python package which bundles functionality for case management, item/evidence comparisons, data cleaning, metadata analysis, internet analysis, network analysis, web crawling, and more. IDEA can read and write your results to a large variety of file types (e.g. .xlsx, .csv, .txt, .json, .graphML).

### **Features**

*Case management*
* File management
* Item/evidence analysis and comparisons
* Object-oriented case management interface

*Data cleaning*
* Text cleaning
    * Reformatting
    * Stopword removal
* Text tokenizing
    * Word tokenization
    * Sentence tokenization
* HTML parsing

*Metadata analysis*
* Metadata similarity analysis

*Text analysis*
* Keyword analysis
* Extraction of key information (e.g. names, locations)
* Text similarity analysis

*Image analysis*
* Reverse image search

*Location analysis*
* Geolocation
* Chronolocation

*Internet analysis*
* Web scraping and crawling
* WhoIs lookups on domains and IP addresses
* Web search
* Website similarity analysis
* Web archiving
    * Internet Archive/Wayback Machine
    * Archive.is
    * Common Crawl

*Social media analysis*
* Platform-specific searches
* Username lookups
* Scraping

*Network analysis*
* Centrality analysis
* Co-link analysis
* Community detection
* and much more...

*Data visualisation*
* Network visualisation
* Timelines



## **User Guide**

### **Installation**

To download from GitHub, run the following code in your console:
```bash
gh repo clone J-A-Ha/IDEA
cd IDEA
pip install -r requirements.txt
```

### **Examples**

#### Importing IDEA

```python!
import idea
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

#### Running all analysis functions on a case using run_full_analysis()

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

### **Beginners Guide**

##### 1. Install Python (version >=3.9) if it is not yet installed.

Download Python from [here](https://www.python.org/downloads/) or using a tool like [Anaconda](https://www.anaconda.com/).


##### 2. Install the repository and dependencies.
```bash

# In the command line, navigate to the folder you wish to install IDEA in.

gh repo clone J-A-Ha/IDEA
cd IDEA
pip install -r requirements.txt
```


##### 3. Run Python and import the package.
```bash
python
```

```python
import idea
```

##### 4. Creating a Project.
```python
project = idea.Project(project_name = 'project')
```

##### 5. Adding a Case.
```python

# Adding a blank case
project.add_case(case_name = 'example')

# Viewing the case's contents and properties
project.example
```

##### 6. Running a limited web crawl and adding results to the case.
```python
# visit_limit defines the number of websites to be crawled.
project.example.from_web_crawl(seed_urls='https://example.com/', visit_limit=5, be_polite=True)
```

##### 7. Running analyses
```python
project.example.parse_rawdata()
project.example.generate_keywords()
project.example.infer_all_info_categories()
project.example.generate_indexes()
project.example.generate_all_networks()
project.example.generate_analytics()

# Viewing analytics results
print(project.example.analytics)
```

##### 8. Saving the Case
```python
project.example.save_as()
```
The package will ask for you to input:
* File name.
* File type. ('.case' is the recommended format).
* File path to save to.


<!-- > Read more about sequence-diagrams here: http://bramp.github.io/js-sequence-diagrams/
 -->


### **Key Classes and Functions**

#### Classes
##### *Project*

```python!
class Project(...)
```
A collection of Case objects. See in [docs](./docs/html/ida.casemanager.html?highlight=project#ida.casemanager.projects.Project).

Key methods:
* [contents](./docs/html/ida.casemanager.html?highlight=project#ida.casemanager.projects.Project.contents): Returns the Project’s attributes as a list. Excludes object properties attribute.
* [add_case](./docs/html/ida.casemanager.html?highlight=project#ida.casemanager.projects.Project.add_case): Adds a Case object to the Project.
* [get_case](./docs/html/ida.casemanager.html?highlight=project#ida.casemanager.projects.Project.get_case): Returns a Case when given its attribute name.
* [export_folder](./docs/html/ida.casemanager.html?highlight=project#ida.casemanager.projects.Project.export_folder): Exports Project’s contents to a folder.

##### *Case*

```python!
class Case(...)
```
An object to store raw data, metadata, and other information related to investigative cases. See in [docs](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case).

Contents:
* properties
* dataframes
* items
* entities
* events
* indexes
* networks
* analytics
* description
* notes

Key methods:
* [backup](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.backup): Creates backup of the Case.
* [make_default](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.make_default): Sets the Case as the default case in the environment.
* [contents](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.contents): Returns the Case’s attributes as a list.
* [search](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.search): Searches Case for a query string. If found, returns a dataframe of all items containing the string.
* [advanced_search](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.advanced_search): An advanced search function. Searches items using a series of keyword commands. If found, returns a dataframe of all items containing the string.
* [add_item](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.add_item): Adds an item to the Case’s item set.
* [from_web_crawl](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.from_web_crawl): Creates a Case object from a web crawl.
* [get_item](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.get_item): Returns an item if given its ID.
* [get_info](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.get_info): Returns all information entries as a Pandas series.
* [get_metadata](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.get_metadata): Returns all metadata entries as a Pandas series.
* [get_keywords](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.get_keywords): Returns a keywords dataframe based on user’s choice of ranking metric.
* [get_project](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.get_project): If the Case is assigned to a Project, returns that Project.
* [parse_rawdata](./file:///Users/jhancock/Documents/Tool_dev/Investigative_data_analyser/Development/Current/docs/_build/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.parse_rawdata): Parses raw data entries for all items.
* [generate_indexes](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.generate_indexes): Generates all indexes and assigns them to the Case’s CaseIndexes attribute. Returns the updated CaseIndexes.
* [generate_all_networks](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.generate_all_networks): Generates all network types and assigns to the Case’s CaseNetworks collection.
* [generate_analytics](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.generate_analytics): Generates all analytics and appends the results to the Case’s CaseAnalytics collection.
* [identify_coincidences](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.identify_coincidences): Runs all coincidence identification methods.
* [infer_all_info_categories](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.infer_all_info_categories): Identifies potential information from items’ text data and appends to information sets. Parses data if not parsed.
* [run_full_analysis](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.run_full_analysis): Runs all analysis functions on the Case.
* [export_folder](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.export_folder): Exports the Case to a folder.
* [export_network](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.export_network): Exports a network to one of a variety of graph file types. Defaults to .graphML.
* [save](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.save): Saves the Case to its source file. If no source given, saves to a new file.
* [save_as](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.case.Case.save_as): Saves the Case to a file.


##### *CaseData*
```python!
class CaseData(...)
```
A collection of Pandas dataframes containing the combined data for a Case. See in [docs](./docs/html/ida.casemanager.html?highlight=casedata#ida.casemanager.casedata.CaseData).

Contents:
* data: item data
* metadata: item metadata
* information: items' labelled information
* other: items' links, references, contents, and other miscellaneous data.
* keywords: keywords associated with the case.
* coinciding_data: patterns of how data coincides.

##### *CaseItem*
```python!
class CaseItem(...)
```
An object representing a piece of material or evidence associated with a Case. See in [docs](./docs/html/ida.casemanager.html?highlight=caseitem#ida.casemanager.items.CaseItem).

Key methods:
* [add_metadata](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.items.CaseItem.add_metadata): Adds single metadata entry to an item’s metadata dataframe.
* [add_data](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.items.CaseItem.add_data): Adds single data entry to an item’s data dataframe.
* [add_info](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.items.CaseItem.add_info): Adds a single information entry to object.
* [add_link](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.items.CaseItem.add_link): Adds a link to an item’s list of links.
* [get_data](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.items.CaseItem.get_data): Returns item’s data.
* [get_metadata](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.items.CaseItem.get_metadata): Returns item’s metadata.
* [get_info](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.items.CaseItem.get_info): Returns item’s information.
* [get_url](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.items.CaseItem.get_url): Returns URL metadata.
* [scrape_url](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.items.CaseItem.scrape_url): Scrapes data from item URL’s site.
* [crawl_web_from_url](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.items.CaseItem.crawl_web_from_url): Runs web crawl from item’s URL metadata.
* [export_excel](./docs/html/ida.casemanager.html?highlight=case#ida.casemanager.items.CaseItem.export_excel): Exports item as Excel (.xlsx) file.

##### *CaseNetwork*

```python!
class CaseNetwork(igraph.Graph)
```
A modified igraph.Graph object. It provides additional analytics methods and functionality for Case management. CaseNetworks can convert both igraph and NetworkX graph objects. See in [docs](./docs/html/ida.casemanager.html?highlight=casenetwork#ida.casemanager.networks.CaseNetwork).

Key attributes:
* vs['name']: returns a list of vertex names.
* es['name']: returns a list of edge names.
* es['weight']: returns a list of edge weights.

Key methods:
* attributes: returns the network's global attributes.
* summary: Returns the summary of the network.
* vs.attributes: returns a list of the names of all vertex attributes.
* es.attributes: returns a list of the names of all edge attributes.
* get_adjacency: Returns the adjacency matrix of the network.
* degree: Returns some vertex degrees from the network.
* density: Calculates the density of the network.
* average_path_length: Calculates the average path length in the network.
* diameter: Calculates the diameter of the network.
* betweenness: Calculates or estimates the betweenness of vertices in the network.
* eigenvector_centrality: Calculates the eigenvector centralities of the vertices in the network.
* [all_centralities](./docs/html/ida.casemanager.html?highlight=casenetwork#ida.casemanager.networks.CaseNetwork.all_centralities): Calculates all centrality measures for network. Returns as a dataframe.
* [colinks](./docs/html/ida.casemanager.html?highlight=casenetwork#ida.casemanager.networks.CaseNetwork.colinks): Runs a colink analysis on the network. Returns a dataframe.
* [community_detection](./docs/html/ida.casemanager.html?highlight=casenetwork#ida.casemanager.networks.CaseNetwork.community_detection): Identifies communities in the network. Gives the option of using different algorithms.
* [degrees_dataframe](./docs/html/ida.casemanager.html?highlight=casenetwork#ida.casemanager.networks.CaseNetwork.degrees_dataframe): Returns the network's degree distribution as a dataframe.
* [export_network](./docs/html/ida.casemanager.html?highlight=casenetwork#ida.casemanager.networks.CaseNetwork.export_network): Exports network to one of a variety of graph file types. Defaults to .graphML.
* to_networkx: Converts the CaseNetwork to networkx format.

##### *CaseFile*

```python!
class CaseFile(CaseObject)
```
An object which stores details about a digital file associated with a case or piece of evidence. See in [docs](./).

#### Functions
##### *Case management*

* [open_case](./docs/html/ida.casemanager.html?highlight=open_case#ida.casemanager.general.open_case): Opens a Case from a file.
* [save](./docs/html/ida.casemanager.html?highlight=save_as#ida.casemanager.general.save): Saves a Case to its source file. If no file exists, requests file details from user input.
* [save_as](./docs/html/ida.casemanager.html?highlight=save_as#ida.casemanager.general.save_as): Saves a Case to a file. Requests file details from user input.
* [get_backups](./docs/html/ida.casemanager.html?highlight=get_backups#ida.casemanager.backups_manager.get_backups): Returns the Backups directory and registry.
* [set_default_case](./docs/html/ida.casemanager.html?highlight=set_default_case#ida.casemanager.defaults_manager.set_default_case): Sets a case as the default in the environment.
* [get_default_case](./docs/html/ida.casemanager.html?highlight=get_default_case#ida.casemanager.defaults_manager.get_default_case): Returns the default case.

##### *Importing files*
* [import_case_excel](./docs/html/ida.casemanager.html?highlight=import_case_excel#ida.casemanager.general.import_case_excel): Imports a Case from a formatted Excel (.xlsx) file.
* [import_case_csv_folder](./docs/html/ida.casemanager.html?highlight=import_case_csv#ida.casemanager.general.import_case_csv_folder): Imports a Case from a folder of formatted CSV (.csv) files.
* [import_case_txt](./docs/html/ida.casemanager.html?highlight=import_case_txt#ida.casemanager.general.import_case_txt): Imports a Case from a pickled text file (.txt or .case).
* [read_pdf](./docs/html/ida.importers.html?highlight=read_pdf#ida.importers.pdf.read_pdf): Loads and parses PDF file. Returns a dictionary of data.
* [read_pdf_url](./docs/html/ida.importers.html?highlight=read_pdf#ida.importers.pdf.read_pdf): Downloads and parses PDF file from a URL. Returns a dictionary of data.

##### *Location analysis*
* [get_coordinates_location](/docs/html/ida.location.html?highlight=get_coordinates_location#ida.location.geolocation.get_coordinates_location): Takes coordinates and returns the location associated by Geopy’s geocoder.
* [get_location_address](./docs/html/ida.location.html?highlight=get_location_address#ida.location.geolocation.get_location_address): Takes location details and returns the address associated by Geopy’s geocoder.
* [get_location_coordinates](./docs/html/ida.location.html?highlight=get_location_coordinates#ida.location.geolocation.get_location_coordinates): Takes location details and returns the coordinates associated by Geopy’s geocoder.

##### *Internet analysis*
* [lookup_whois](./docs/html/ida.internet.html?highlight=lookup_whois#ida.internet.webanalysis.lookup_whois): Performs a WhoIs lookup on an inputted domain or IP address.

##### *Web searching*
* [open_url](./docs/html/ida.internet.html?highlight=open_url_source#ida.internet.webanalysis.open_url): Opens URL in the default web browser.
* [open_url_source](./docs/html/ida.internet.html?highlight=open_url_source#ida.internet.webanalysis.open_url_source): Opens URL’s source code in the default web browser.
* [search_web](./docs/html/ida.internet.html?highlight=search_web#ida.internet.search.search_web): Launches a website-specific Google search for an inputted query and URL.
* [multi_search_web](./docs/html/ida.internet.html?highlight=multi_search_web#ida.internet.search.multi_search_web): Launches multiple web searches by iterating on a query through a list of terms.
* [search_images](./docs/html/ida.internet.html?highlight=search_images#ida.internet.search.search_images): Launches an image search using the default web browser.
* [search_social_media](./docs/html/ida.internet.html?highlight=search_social_media#ida.internet.search.search_social_media): Launches a Google search focused on specified social media platform for inputted query.

##### *Web crawling*
* [crawl_site](./docs/html/ida.internet.html?highlight=crawl_site#ida.internet.crawlers.crawl_site): Crawls website’s internal pages. Returns any links found as a list.
* [crawl_web](./docs/html/ida.internet.html?highlight=crawl_web#ida.internet.crawlers.crawl_web): Crawls internet from a single URL or list of URLs. Returns details like links found, HTML scraped, and site metadata.

##### *Social media analysis*
* [search_username](./docs/html/ida.socmed.html?highlight=search_username#ida.socmed.sherlock_interpreter.search_username): Runs a Sherlock search for a username.

### **Documentation**

For the full documentation, click [here](./docs/html/index.html).



## **Contributing**

## **Authors and acknowledgments**

IDEA was created by [Jamie Hancock](https://github.com/J-A-Ha).

It relies on packages and modules created by:
* Geocoder: [Denis Carriere](https://github.com/DenisCarriere)
* Geopy: [Adam Tygart et al.](https://github.com/geopy/geopy/blob/master/AUTHORS)
* Shodan: [John Matherly](https://github.com/achillean/shodan-python/blob/master/AUTHORS)
* Sherlock: [Siddharth Dushantha et al.](https://github.com/sherlock-project/sherlock/graphs/contributors)
* Instaloader: [Alexander Graf et al.](https://github.com/instaloader/instaloader/blob/master/AUTHORS.md)
* youtube-comment-downloader: [Egbert Bouman](https://github.com/egbertbouman)
*  youtube-dl: [Ricardo Garcia Gonzalez et al.](https://github.com/ytdl-org/youtube-dl/blob/master/AUTHORS)
* RPy2: [Laurent Gautier](https://github.com/lgautier)
* ERGM: [Mark S. Handcock et al.](https://cran.r-project.org/web/packages/ergm/index.html)
* python-whois: [Richard Penman](https://github.com/richardpenman/)
* ipwhois: [Phillip Hane](https://pypi.org/project/ipwhois/)
* Trafilatura: [Adrien Barbaresi](https://github.com/adbar)
* Cloudscraper: [VeNoMouS](https://github.com/VeNoMouS)
* Levenshtein: [Max Bachmann](https://github.com/maxbachmann)


## **License**

IDEA is licensed under GPL-3.0.

IDEA is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

IDEA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with IDEA. If not, see <https://www.gnu.org/licenses/>. 


## **Appendix and FAQ**

### **Project Timeline**
---
```mermaid
gantt
    title Timeline
```

<!-- > Read more about mermaid here: http://mermaid-js.github.io/mermaid/ -->


###### tags: `Python`, `R`, `Investigations`, `OSI`, `OSINT`, `Documentation`
