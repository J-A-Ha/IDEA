"""
Functions for interacting with Instagram.

Notes
-----
See https://instaloader.github.io/as-module.html.
"""

import os

from instaloader import Instaloader, Profile, Post, Hashtag, Story, StoryItem, TopSearchResults, save_structure_to_file

def set_login(username = 'request_input', password = 'request_input'):
    
    """
    Initialises Instagram login as variable in the global environment.
    
    Parameters
    ----------
    username : str
        Instagram username for login. Defaults to requesting from user input.
    password : str
        Instagram password for login. Defaults to requesting from user input.
    """
    
    # Requesting username from user input if none provided
    if username == 'request_input':
        username = input('Instagram username: ')
    
    # Replacing empty string with None to avoid errors
    if username == '':
        username = None
    
    # Initialising global USER variable
    global USER
    USER = username
    
    # Requesting password from user input if none provided
    if password == 'request_input':
        password = input('Instagram password: ')
    
    # Replacing empty string with None to avoid errors
    if password == '':
        password = None
    
    # Initialising global PASSWORD variable
    global PASSWORD
    PASSWORD = password
    
    
def init_session(login = False, username = None, password = None):
    
    """
    Initialises Instagram session as variable in the global environment.
    
    Parameters
    ----------
    login : bool, default : False
        whether to login to Instagram. Defaults to False.
    username : str
        Instagram username for login. Defaults to requesting from user input.
    password : str
        Instagram password for login. Defaults to requesting from user input.
    """
    
    # Initialising global SESSION variable
    global SESSION
    SESSION = Instaloader()
    
    # If no login, username, and/or password given, asks user if they wish to login
    if (login == False) or (username != None) or (password != None):
        
        res = input('Optional: login to Instagram? (yes/no): ')
        res = res.lower().strip()
        
        if (res == 'yes') or (res == 'y'):
            login = True
        else:
            login = False
    
    # Logging in if user wishes to login
    if login == True:
        
        # If no username provided
        if username == None:
            # If no username set in environment
            if 'USER' not in globals().keys():
                # Requesting login details
                set_login()
            
            # Retrieving username from global environment
            global USER
            username = USER
        
        # If no username provided
        if password == None:
            
            # If no username set in environment
            if 'PASSWORD' not in globals().keys():
                # Requesting login details
                set_login(username = username)
            
            # Retrieving password from global environment
            global PASSWORD
            password = PASSWORD
        
        # Logging into session 
        SESSION.login(username, password)
        
        # Deleting username and password from global environment once used
        del globals()['USER']
        del globals()['PASSWORD']
    
    return SESSION

def fetch_profile(username = 'request_input'):
    
    """
    Retrieves Instagram profile for given username.
    
    Parameters
    ----------
    username : str
        Instagram username to fetch profile from. Defaults to requesting from user input.
        
    Returns
    -------
    profile : instaloader.Profile
        The Instaloader Profile object associated with the username.
    """
    
    # Requesting username from user input if none provided
    if username == 'request_input':
        username = input('Username: ')
    
    # Checking if session has been intiated. If not, initiating session
    if 'SESSION' not in globals().keys():
        loader = init_session()
    
    # Retrieving session variable from global environment
    global SESSION
    loader = SESSION
    
    # Retrieving user profile
    profile = Profile.from_username(loader.context, username)
    
    return profile

def fetch_user(username = 'request_input'):
    
    """
    Retrieves Instagram profile for given username.
    
    Parameters
    ----------
    username : str
        Instagram username to fetch profile from. Defaults to requesting from user input.
        
    Returns
    -------
    profile : instaloader.Profile
        The Instaloader Profile object associated with the username.
    """
    
    return fetch_profile(username = username)

def fetch_user_posts(username = 'request_input'):
    
    """
    Retrieves all Instagram posts for given username.
    
    Parameters
    ----------
    username : str
        Instagram username to fetch posts from. Defaults to requesting from user input.
        
    Returns
    -------
    posts : object
        The posts associated with the username.
    """
    
    # Retrieving profile
    profile = fetch_profile(username = username)
    
    # Retrieving posts
    posts = profile.get_posts()
    
    return posts

def download_user_posts(username = 'request_input'):
    
    """
    Downloads all Instagram posts for given username.
    
    Parameters
    ----------
    username : str
        Instagram username to fetch posts from. Defaults to requesting from user input.
    """
    
    # Requesting username from user input if none provided
    if username == 'request_input':
        username = input('Username: ')
    
    # Checking if session has been intiated. If not, initiating session
    if 'SESSION' not in globals().keys():
        loader = init_session()
    
    # Retrieving session variable from global environment
    global SESSION
    loader = SESSION
    
    # Retrieving profile and posts
    profile = fetch_profile(username = username)
    posts = profile.get_posts()
    
    # Downloading posts
    for post in posts:
        loader.download_post(post, target=profile.username)


def save_user_posts_json(username = 'request_input', folder_address = 'request_input'):
    
    """
    Saves all Instagram posts for given username as a JSON file.
    
    Parameters
    ----------
    username : str
        Instagram username to fetch posts from. Defaults to requesting from user input.
    folder_address : str
        Directory path of folder to save to. Defaults to requesting from user input.
    """
    
    # Requesting username from user input if none provided
    if username == 'request_input':
        username = input('Username: ')
    
    # Requesting folder address from user input if none provided
    if folder_address == 'request_input':
        folder_address = input('Folder address: ')
    
    # Requesting username from user input if none provided
    folder_address = folder_address + '/' + username
    
    # Retrieving profile and posts
    profile = fetch_profile(username = username)
    posts = profile.get_posts()
    
    # Making folder
    os.mkdir(folder_address)
    
    # Saving posts
    for post in posts:
        shortcode = post.shortcode
        file_address = folder_address + '/' + shortcode + '.json'
        save_structure_to_file(post, file_address)

        
def get_user_posts_dict(username = 'request_input'):
    
    """
    Retrieves all Instagram posts for given username and returns a dictionary.
    
    Parameters
    ----------
    username : str:
        The username to retrieve posts from. Defaults to requesting from user input.
    
    Returns
    -------
    result : dict
        Posts and their metadata.
    """
    
    posts = fetch_user_posts(username = username)
    
    result = {}
    
    for p in posts:
        shortcode = p.shortcode
        result[shortcode] = p.__dict__
    
    return result