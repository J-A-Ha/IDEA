from __future__ import unicode_literals
import youtube_dl
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
import pandas as pd


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

ydl_opts = {
    'verbose': True,
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}        

def get_info(urls):
    
    ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})
        
    if type(urls) == str:
        urls = [urls]
    
    
    output = {}
    
    with ydl:
        for i in urls:
            result = ydl.extract_info(
                                    i,
                                    download=False # We just want to extract the info
                                    )
            output[i] = result
    
    return output


def download_video(urls, options = 'default'):
    
    if options == 'default':
        
        global ydl_opts
        options = ydl_opts
        
    if type(urls) == str:
        urls = [urls]
    
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download(urls)

        
def download_comments(urls = 'request_input', sort_by = 'most_popular', output = 'dataframe'):
    
    if urls == 'request_input':
        urls = input('URL(s): ')
    
    downloader = YoutubeCommentDownloader()
    
    if sort_by == 'most_popular':
        sort_by = SORT_BY_POPULAR
    
    if type(urls) == str:
        urls = urls.split(',')
    
    res_dict = {}
    
    for url in urls:
        result = downloader.get_comments_from_url(url, sort_by=sort_by)
        res_dict[url] = result
    
    if output == 'dict':
        return_obj = res_dict
    
    if output == 'dataframe':
        
        return_obj = {}
        
        for key in res_dict.keys():
            result = res_dict[key]
            df = pd.DataFrame.from_dict(result, dtype=object)
            return_obj[key] = df
        
        if len(return_obj.keys()) <= 1:
            key = list(return_obj.keys())[0]
            return_obj = return_obj[key]
        
    return return_obj