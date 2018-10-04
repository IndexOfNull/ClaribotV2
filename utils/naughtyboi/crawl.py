import asyncio
import aiohttp
import async_timeout
import re
import time
from urllib.parse import urlparse


try:
	from bs4 import BeautifulSoup
except Exception as e:
	raise ImportError('BeautifulSoup did not import properly ({0})'.format(e))

class HTTP():

	async def post(self,url,**kwargs):
		retjson = kwargs.pop('json',False)
		params = kwargs.pop("params",{})
		try:
			with async_timeout.timeout(10):
				async with aiohttp.ClientSession() as session:
					async with session.post(url,data=params,**kwargs) as resp:
						data = (await resp.read()).decode("utf-8")
						if retjson:
							data = json.loads(data)
						return data
		except asyncio.TimeoutError:
			return False
		except Exception as e:
			return False

	async def get(self,url,**kwargs):
		retjson = kwargs.pop('json',False)
		try:
			with async_timeout.timeout(10):
				async with aiohttp.ClientSession() as session:
					async with session.get(url,**kwargs) as resp:
						if retjson:
							data = json.loads(await resp.text())
						else:
							data = await resp.read()
						return data
		except asyncio.TimeoutError:
			return False
		except Exception as e:
			print(e)
			return False

class Crawler():

    def __init__(self,db,**kwargs):
        self.http = HTTP()
        self.db = db
        self.visited = []

    async def get_page_data(self,url,**kwargs): #returns BS4 object.
        response = await self.http.get(url,**kwargs)
        self.visited.append(url)
        if response:
            return BeautifulSoup(response,"html.parser")


    def fetch(d):
        raise NotImplementedError

    def record_data(url,data):
        db.query("")


class TumblrCrawler(Crawler):

    def __init__(self,db,**kwargs):
        super().__init__(db,**kwargs)
        self.visited = []
        self.post_ids = []
        self.to_crawl = []

    def record_data(self,d,url):
        if d.find("div",style='background-image: url("/images/pages/safe-mode/bg2.gif");'):
            print("safe mode")
            return
        url = "/".join(url.split("/", 3)[:3])
        if url.startswith("http") and not url.startswith("https"):
            url = "https" + url[4:]
        data = []
        posts = d.find_all("article",{"class":["type-photo","type_photo"]})
        if not posts or len(posts) <= 0:
            return
        #username = d.find("meta",property="og:title").get("content")
        up = urlparse(url)
        username = up.hostname.split('.')[0]
        sqlCommand = "INSERT INTO `tumblr_crawl` (`url`, `username`, `post_id`, `img_url`, `reblog`, `timestamp`) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}');"
        finalSql = ""
        for post in posts:

            pid = post.get("id").split("-")
            if len(pid) >= 2:
                pid = pid[1]
            else:
                pid = pid[0]
            if id in self.post_ids:
                continue
            permalink = url + "/post/" + pid
            reblogged = post.find("li",class_="date-reblogged")
            if reblogged:
                rfrom = "/".join(reblogged.find("a",class_="reblogged-from").get("href").split("/", 3)[:3])
                reblogged = "1" #true
                if not rfrom in self.visited and not rfrom in self.to_crawl:
                    self.to_crawl.append(rfrom)
            else:
                reblogged = "0" #false
            ts = int(time.time())
            #photo = post.find("div",class_="photo-panel").find("img").get("src")
            photo = post.find("img").get("src")
            sql = sqlCommand.format(permalink,username,pid,photo,reblogged,ts)
            self.post_ids.append(pid)
            self.db.execute(sql)
        if d.find("a",class_="next"):
            print(url + "/" + d.find("a",class_="next").get("href")[1:])
            self.to_crawl.append(url + "/" + d.find("a",class_="next").get("href")[1:])
        else:
            if url.rsplit("/",2)[1] == "page":
                current = int(url.split("/")[-1]) + 1
                self.to_crawl.append(url + "/page/" + str(current))
        self.db.commit()

    async def crawl(self,entry,depth=10):
        data = await self.get_page_data(entry)
        self.record_data(data,entry)
        for i in range(depth):
            for url in self.to_crawl:
                self.to_crawl.remove(url)
                if url in self.visited:
                    continue
                try:
                    data = await self.get_page_data(url)
                    if data:
                        self.record_data(data,url)
                except Exception as e:
                    print(e)
