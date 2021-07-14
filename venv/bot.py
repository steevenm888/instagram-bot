from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
import re
from urllib.request import urlopen
import json
from pandas.io.json import json_normalize
import pandas as pd, numpy as np

username='andreiiflu'
browser = webdriver.Chrome('./chromedriver')
browser.get('https://www.instagram.com/'+username+'/?hl=en')
Pagelength = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

#Extract links from user profile page
links=[]
source = browser.page_source
data=bs(source, 'html.parser')
body = data.find('body')
script = body.find('script', text=lambda t: t.startswith('window._sharedData'))
page_json = script.string.split(' = ', 1)[1].rstrip(';')
data = json.loads(page_json)
#try 'script.string' instead of script.text if you get error on index out of range
for link in data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']:
    url = 'https://www.instagram.com'+'/p/'+link['node']['shortcode']+'/'
    links.append(url)
print(links)
for url in links:
    browser.get(url)
    source = browser.page_source
    data = bs(source, 'html.parser')
    comment = browser.find_element_by_class_name('C4VMK')
    print(comment.text)
#try with ['display_url'] instead of ['shortcode'] if you don't get links 
# #Extract links from hashtag page
# links=[]
# source = browser.page_source
# data=bs(source, 'html.parser')
# body = data.find('body')
# script = body.find('script', text=lambda t: t.startswith('window._sharedData'))
# page_json = script.text.split(' = ', 1)[1].rstrip(';')
# data = json.loads(page_json)
# for link in data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']:
#     links.append('https://www.instagram.com'+'/p/'+link['node']['shortcode']+'/')

# result=pd.DataFrame()
# for i in range(len(links)):
#     try:
#         page = urlopen(links[i]).read()
#         data=bs(page, 'html.parser')
#         body = data.find('body')
#         script = body.find('script')
#         raw = script.text.strip().replace('window._sharedData =', '').replace(';', '')
#         json_data=json.loads(raw)
#         posts =json_data['entry_data']['PostPage'][0]['graphql']
#         posts= json.dumps(posts)
#         posts = json.loads(posts)
#         x = pd.DataFrame.from_dict(json_normalize(posts), orient='columns')
#         x.columns = x.columns.str.replace('shortcode_media.', '')
#         result=result.append(x)
#     except:
#         np.nan
# result = result.drop_duplicates(subset = 'shortcode')
# result.index = range(len(result.index))

# import time
# from selenium import webdriver

# driver = webdriver.Chrome('./chromedriver')  # Optional argument, if not specified will search path.
# driver.get('http://www.google.com/')
# time.sleep(5) # Let the user actually see something!
# search_box = driver.find_element_by_name('q')
# search_box.send_keys('ChromeDriver')
# search_box.submit()
# time.sleep(5) # Let the user actually see something!
# driver.quit()