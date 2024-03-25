"""A Python package for conducting investigations using data."""

from .core.globaltools import get_var_name_str

from .exporters.general_exporters import export_obj, obj_to_folder
from .exporters.network_exporters import export_network

from .visualisation.visualise import histogram, plot_date_range_timeline, plot_network, plot_timeline

from .location.geolocation import coordinates_distance, get_coordinates_location, get_coordinates_geocode, get_location_address, get_location_coordinates, get_location_geocode, locations_distance, lookup_coordinates, lookup_location

from .internet.webanalysis import domain_from_ip, get_ip_coordinates, get_ip_physical_location, get_domain, get_ip_geocode, get_my_ip, get_my_ip_coordinates, get_my_ip_geocode, get_my_ip_physical_location, ip_from_domain, is_domain, is_ip_address, is_registered_domain, WhoisResult, domains_whois, ips_whois, lookup_ip_coordinates, lookup_whois, open_url, open_url_source, regex_check_then_open_url

from .internet.search import search_web, search_images, search_social_media, search_twitter, search_website, reverse_image_search, multi_search_web

from .internet.archives import search_archiveis, search_internet_archive, open_internet_archive, search_common_crawl, search_cc_index, fetch_page_from_cc, fetch_common_crawl_record

from .internet.scrapers import get_url_source, scrape_dynamic_page, scrape_google_search, scrape_url

from .internet.crawlers import crawl_from_search, crawl_site, crawl_web, fetch_sitemap, fetch_feed_urls, fetch_url_rules, is_external_link, similarity_network_from_crawl, similarity_network_from_crawl_result, similarity_network_from_search_crawl, site_similarities_from_crawl, site_similarity_network

from .internet.shodan import search_ip as shodan_search_ip

from .socmed.sherlock_interpreter import search_username
from .socmed.instagram import download_user_posts as fetch_instagram_user_posts

from .importers.pdf import read_pdf, read_pdf_url

from .casemanager.defaults_manager import DEFAULT_SET, DEFAULT_CASE_NAME, set_default_case, get_default_case_name, get_default_case, is_default_case, check_default_case, remove_default_case, update_default_case
from .casemanager.backups_manager import Backups, get_backups, BACKUPS
from .casemanager.items import CaseItem
from .casemanager.entities import CaseEntity
from .casemanager.events import CaseEvent
from .casemanager.networks import CaseNetwork
from .casemanager.case import Case
from .casemanager.projects import Project
from .casemanager.general import new_blank_case, case_from_web_crawl, items_from_web_crawl, import_case_excel, import_case_csv_folder, import_case_pickle, import_case_txt, open_case, save_as, save, sync_items, update_case