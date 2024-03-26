"""
Functions for interacting with the Sherlock module using the Python interpreter. 

Developed by making edits to the sherlock.main() function.
"""

from .sherlock.result import QueryStatus
from .sherlock.result import QueryResult
from .sherlock.notify import QueryNotifyPrint
from .sherlock.sites import SitesInformation
from .sherlock.sherlock import module_name, __version__, SherlockFuturesSession, get_response, check_for_parameter, multiple_usernames, sherlock, timeout_check, handler, main

import pandas as pd
import os
import platform
import re
from time import monotonic
import requests
from requests_futures.sessions import FuturesSession
from torrequest import TorRequest

def search_username(username: str = 'request_input', site_list = None, sites_json = None, nsfw = True, tor = None, unique_tor = False, proxy = None, timeout = 60, browse = False, verbose = False, print_all = False, output = 'dataframe'):
    
    """
    Runs a Sherlock search for a username.
    
    
    Parameters
    ---------- 
    username: str 
        username to search for.
    site_list : list
        list of sites to search.
    sites_json : str
        JSON of site data.
    nsfw : bool
        whether to include NSFW websites in result.
    tor : str
        Tor node to route search through.
    unique_tor : bool
        whether to use a unique Tor instance.
    proxy : str
        proxy to route search through.
    timeout : int
        length of time to wait before timeout.
    browse : bool
        whether to open results in browser.
    verbose : bool
        whether to return verbose output.
    print_all : bool
        whether to print all results, including failed results.
    output : str
        type of data format to output. Defaults to dataframe.
    
    Returns
    -------
    result
        a set of usernames found by Sherlock.
    """
    try:
        # Setting version
        version_string = (
            f"%(prog)s {__version__}\n"
            + f"{requests.__description__}:  {requests.__version__}\n"
            + f"Python:  {platform.python_version()}"
                        )
    
        # Check for newer version of Sherlock. If it exists, let the user know about it
        try:
            r = requests.get(
                "https://raw.githubusercontent.com/sherlock-project/sherlock/master/sherlock/sherlock.py"
            )

            remote_version = str(re.findall('__version__ = "(.*)"', r.text)[0])
            local_version = __version__

            if remote_version != local_version:
                print(
                    "Update Available!\n"
                    + f"You are running version {local_version}. Version {remote_version} is available at https://github.com/sherlock-project/sherlock"
                )

        except Exception as error:
            print(f"A problem occurred while checking for an update: {error}")
    
    except:
        pass
    
    # Requesting username from user input if none provided
    if username == 'request_input':
        username = input('Username: ')
    
    # Argument check
    # TODO regex check on proxy
    if (tor != None) and (proxy != None):
        raise Exception("Tor and Proxy cannot be set at the same time.")

    # Make prompts
    if proxy is not None:
        print("Using the proxy: " + proxy)

    # Outputting warnings regarding Tor use
    if tor != None:
        print("Using Tor to make requests")

        print(
            "Warning: some websites might refuse connecting over Tor, so note that using this option might increase connection errors."
        )


    # Create object with all information about sites we are aware of.
    if sites_json != None:
        local = False
    else:
        local = True
        
    try:
        if local == True:
            sites = SitesInformation(
                os.path.join(os.path.dirname(__file__), "sherlock/resources/data.json")
            )
        else:
            sites = SitesInformation(sites_json)
    
    # Raising exception
    except Exception as error:
        print(f"ERROR:  {error}")
        sites = SitesInformation()
    
    # Removing NSFW sites if not wanted
    if not nsfw == False:
        sites.remove_nsfw_sites()

    # Create original dictionary from SitesInformation() object.
    # Eventually, the rest of the code will be updated to use the new object
    # directly, but this will glue the two pieces together.
    site_data_all = {site.name: site.information for site in sites}
    if site_list is None:
        # Not desired to look at a sub-set of sites
        site_data = site_data_all
    else:
        # User desires to selectively run queries on a sub-set of the site list.
        # Make sure that the sites are supported & build up pruned site database.
        site_data = {}
        site_missing = []
        for site in site_list:
            counter = 0
            for existing_site in site_data_all:
                if site.lower() == existing_site.lower():
                    site_data[existing_site] = site_data_all[existing_site]
                    counter += 1
            if counter == 0:
                # Build up list of sites not supported for future error message.
                site_missing.append(f"'{site}'")

        if site_missing:
            print(f"Error: Desired sites not found: {', '.join(site_missing)}.")

#         if not site_data:
#             sys.exit(1)

    # Create notify object for query results.
    query_notify = QueryNotifyPrint(
        result=None, verbose=verbose, print_all=print_all, browse=browse
    )

    # Run report on all specified users.
    
    all_usernames = []
    
    if type(username) == str:
        all_usernames = [username]
    
    elif type(username) == list:
        
        for u in username:
            if check_for_parameter(u):
                for name in multiple_usernames(u):
                    all_usernames.append(name)
            else:
                all_usernames.append(u)
    
    results_dict = {}
    
    
    for u in all_usernames:
        results = sherlock(
            u,
            site_data,
            query_notify,
            tor=tor,
            unique_tor=unique_tor,
            proxy=proxy,
            timeout=timeout,
        )

        results_dict[u] = results
        
    query_notify.finish()
    
    if output == 'dataframe':
        
        if len(results_dict.keys()) <= 1:
            df = pd.DataFrame.from_dict(results_dict[username], dtype = object).T
            df['status'] = df['status'].astype(str)
            df = df[df['status'] == 'Claimed']
            df.index.name = 'site'
            
            res = df
            
        
        else:
            res = {}
            for u in results_dict.keys():
                df = pd.DataFrame.from_dict(results_dict[u], dtype = object).T
                df['status'] = df['status'].astype(str)
                df = df[df['status'] == 'Claimed']
                df.index.name = 'site'
                output[u] = df
        
        return res