"""
Useful datasets for reference and analysis

Notes
-----
Corpus extracted from names_dataset module + NLTK module. Stored locally for efficiency. See https://pypi.org/project/names-dataset/ for source of first and last names; nltk.corpus.names for source of nltk names
"""

from .names import all_personal_names, first_names, last_names, nltk_names

# Corpus extracted from country_list module. Stored locally for efficiency.
from .countries import countries_all, country_names

# Corpus extracted from geonamescache module. Stored locally for efficiency.
from .cities import cities_all, cities_en

# Corpus extracted from language_data and langcodes modules. Stored locally for efficiency.
from .languages import language_names, languages_en, language_codes

from .stopwords import stopwords

# Corpus extracted from language_data and langcodes modules. Stored locally for efficiency.

from nltk import download


# Importing NLTK's Word Lists corpus as an NLTK text

try:
    from nltk.corpus import words as nltk_wordlists
    nltk_wordlists.words()
except:
    download('words')
    from nltk.corpus import words as nltk_wordlists


# Importing Swadesh corpus as an NLTK text

try:
    from nltk.corpus import swadesh as nltk_swadesh
    nltk_swadesh.words()
except:
    download('swadesh')
    from nltk.corpus import swadesh as nltk_swadesh

    
# Importing NLTK's Web Text corpus
try:
    from nltk.corpus import webtext as nltk_webtext
    nltk_webtext.words()
except:
    download('webtext')
    from nltk.corpus import webtext as nltk_webtext
      
    
# Importing WordNet 3.0 corpus

try:
    from nltk.corpus import wordnet as nltk_wordnet
    nltk_wordnet.words()
except:
    download('wordnet')
    from nltk.corpus import wordnet as nltk_wordnet

# Creating useful dictionaries of countries in major languages

countries_zh = country_names['zh']
countries_ar = country_names['ar']
countries_es = country_names['es']
countries_hi = country_names['hi']
countries_pt = country_names['pt']
countries_ru = country_names['ru']
countries_fr = country_names['fr']

languages_all = []
for l in language_names.values():
    languages_all = languages_all + list(l.values())

languages_all = list(set(languages_all))


# Extracting NLTK Words Lists as a list of words
nltk_words_list = nltk_wordlists.words()

# Extracting NLTK Web Text  as a list of words
nltk_webtext_words = nltk_webtext.words()