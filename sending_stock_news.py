# Import package

from pyshorteners import Shortener
from dateutil.parser import parse
from bs4 import BeautifulSoup
import datetime as dt
import pandas as pd
import requests
import os

# Get news

# get single stock news
def get_keyword_news(keyword, period):
  global news_dataframe

  # initial dataframe
  news_dataframe = pd.DataFrame(columns=['keyword', 'time', 'title', 'link'])
  
  # fetch news data
  res = requests.get('https://news.google.com/search?q="'+ keyword +'"%20when%3A'+ period +'&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant')
  if res.status_code == 200:
    content = res.content
    soup = BeautifulSoup(content, "html.parser")
    items = soup.findAll("div", class_="xrnccd")
    

    # sort out data
    for item in items:
      # title
      title = item.find("h3", {"class": "ipQwMb ekueJc RD0gLb"}).find("a").text
      
      # url
      href = item.find("h3", {"class": "ipQwMb ekueJc RD0gLb"}).find("a").get("href")
      link = "https://news.google.com"+href.lstrip('.')
      try:
        link = Shortener().tinyurl.short(link)
      except:
        pass
      
      # time
      time_chars = item.find("time").get("datetime")
      time = parse(time_chars).replace(tzinfo=None)

      # news_source
#       try:
#         print(item.find("a", {"class": 'wEwyrc AVN2gc WfKKme '}))
#         source = item.find("a", {"class": 'wEwyrc AVN2gc WfKKme '}).contents[0]
#       except:
#         source = 'NA'
      
      # fill-in dataframe
      news_dataframe.loc[len(news_dataframe)] = [keyword, time, title, link]
      
  
  # transform dtype
  for col in ['keyword', 'title', 'link']: news_dataframe[col] = news_dataframe[col].astype('string')
  
  
  # leave only the title with the stock name
  news_dataframe = news_dataframe[news_dataframe.title.str.contains(keyword.split(' ')[0])]
  
  # drop useless news
  shit_news_keyword = ['對帳單', '加權指數', '盤中焦點股', '熱門']
  news_dataframe = news_dataframe[~news_dataframe.title.str.contains('|'.join(shit_news_keyword))].reset_index(drop=True)

  # clean up similar news
  news_dataframe = news_dataframe.drop_duplicates(subset=['title']).reset_index(drop=True)
  
  clean_title = news_dataframe.title.copy()
  trash_word = ['是', '的', '「', '」', ' ', '：', '、', '？', '.', '！', 'TechNews', '\d+', ' ', '|', '，', '／']
  for i in trash_word:
    clean_title = clean_title.str.replace(i, '', regex=True)

  unique_titles, unique_title = [], str()
  for i in range(len(news_dataframe)):
    unique_title = news_dataframe.title[i]
    for j in range(len(news_dataframe)-i-1):
      a = list(clean_title[i])
      b = list(clean_title[i+j+1])
      if len(set(set(a) & set(b))) >= 8:
        unique_title = min(news_dataframe.title[i], news_dataframe.title[i+j+1], key=len)  
    unique_titles.append(unique_title)
  news_dataframe = news_dataframe[news_dataframe['title'].isin(list(set(unique_titles)))]
  
  return news_dataframe

# Send LINE message

def generate_message(all_news_dataframe):
  # title: 個股新聞/ date/ time
  update_time = dt.datetime.now() + dt.timedelta(hours=8)
  date, time = update_time.strftime("%m") +'/'+update_time.strftime("%d"), update_time.strftime("%H:%M:%S")
  message = '*'+'個股新聞'+'*'+'\n'+'```'+date+' '+time+'```'
  
  # detail: ticker & name / news title & source / link  
  for i in all_news_dataframe.keyword.unique():
    keyword = i
    message += '\n' + '*' + keyword + '*\n'
    
    df_single_keyword = all_news_dataframe[all_news_dataframe.keyword == i].reset_index(drop=True)
    for j in range(len(df_single_keyword)):   

      title = df_single_keyword.title[j]
#       news_source = df_single_keyword.news_source[j][:2]
      link = df_single_keyword.link[j]
      message += title + '\n' + link + '\n'
      if len(df_single_keyword) > 1:
         message += '\n'
  return message

def lineNotifyMessage(token, msg):
  headers = {
      "Authorization": "Bearer " + token, 
      "Content-Type" : "application/x-www-form-urlencoded"
      }

  payload = {'message': msg }
  r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
  return r.status_code

# wrap up

# compose multiple stocks news df
token = os.environ['LINE_NOTIFY_TOKEN']

# keywords= ['健策 3653', '智伸科 4551', '南亞科 2408', '台翰 1336', '創意 3443', '晶心科 6533', '宜特 3289', '眾達-KY 4977', '資本支出', 'Trendforce 預估', 'IDC 預估', 'Gartner 預估']
keywords = open('keyword_watchlist.txt', 'r').read().strip('\n').strip().split(',')

all_news_dataframe = pd.DataFrame()

for i in keywords:
  news_dataframe = get_keyword_news(i, '1d')
  all_news_dataframe = all_news_dataframe.append(news_dataframe, ignore_index=True)

if all_news_dataframe.empty == False:
  message = generate_message(all_news_dataframe)
  lineNotifyMessage(token, message)
