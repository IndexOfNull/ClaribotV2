import asyncio
import aiohttp
import async_timeout
import re


try:
	from bs4 import BeautifulSoup
except Exception as e:
	raise ImportError('BeautifulSoup did not import properly ({0})'.format(e))

#Low-Level FurAffinity Scraper. Supports Searching, Getting post by id, and getting front page
#Please excuse the bad code, i really dont care about furry pictures all too much...


class Object(object):
	pass

class HTTP():

	async def post(self,url,**kwargs):
		retjson = kwargs.pop('json',False)
		params = kwargs.pop("params",{})
		cookies = kwargs.pop("cookies",None)
		try:
			with async_timeout.timeout(10):
				async with aiohttp.ClientSession(cookies=cookies) as session:
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
		cookies = kwargs.pop("cookies",None)
		try:
			with async_timeout.timeout(10):
				async with aiohttp.ClientSession(cookies=cookies) as session:
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

class FABaseObject():

	def __init__(self,**kwargs):
		self.base_url = kwargs.pop('base_url','http://www.furaffinity.net/')
		self.RATINGS = Object()
		self.RATINGS.GENERAL = 'general'
		self.RATINGS.MATURE = 'mature'
		self.RATINGS.ADULT = 'adult'
		self.VIEWS = Object()
		self.VIEWS.DEFAULT = 'view'
		self.VIEWS.FULL = 'full'
		self.TYPES = Object()
		self.TYPES.ART = 'art'
		self.TYPES.FLASH = 'flash'
		self.TYPES.PHOTOGRAPHY = 'photography'
		self.TYPES.MUSIC = 'music'
		self.TYPES.POETRY = 'poetry'
		self.TYPES.STORY = 'story'

class FurAffinity(FABaseObject):

	def __init__(self,**kwargs):
		super().__init__()
		self.http = HTTP()
		self.a_cookie = kwargs.pop("a",None)
		self.b_cookie = kwargs.pop("b",None)
		if self.a_cookie and self.b_cookie:
			self.cookies = {"a":self.a_cookie,"b":self.b_cookie}
		else:
			self.cookies = {}

	def get_preview_template(self,url):
		return re.sub(r"[@]\d\d\d","@{0}",url)

	async def get_front_page(self,**kwargs):
		try:
			type_in = kwargs.pop("type",["art"])
			response = await self.http.get('http://www.furaffinity.net',cookies=self.cookies)
			data = BeautifulSoup(response,"html.parser")
			posts_art = data.find("section",attrs={"id":"gallery-frontpage-submissions"})
			posts_writing = data.find("section",attrs={"id":"gallery-frontpage-writing"})
			posts_music = data.find("section",attrs={"id":"gallery-frontpage-music"})
			posts_crafts = data.find("section",attrs={"id":"gallery-frontpage-crafts"})
			types = {"art":posts_art,"writing":posts_writing,"music":posts_music,"crafts":posts_crafts}
			do = []
			for t in type_in:
				do.append(types[t])
			results = []
			for cat in do:
				posts = cat.find_all('figure')
				if not posts:
					break
				for post in posts:
					try:
						text = post.find("figcaption").find_all("a")
						name = text[0]
						by = text[1]
						rating = post["class"][0].replace("r-","")
						type = post["class"][1].replace("t-","")
						source = self.base_url + text[0].get("href")
						p_base = self.get_preview_template("http:"+post.find("img").get("src"))
						id = (post.get("id")).replace("sid-","")
						results.append(SearchResult(id=id,by=by,title=name,type=type,source=source,preview_base=p_base,rating=rating))
					except Exception as e:
						pass
			return results
		except Exception as e:
			return

	async def search(self,query,**kwargs):
		try:
			results = kwargs.pop("results",48)
			range = kwargs.pop("range","all")
			page = kwargs.pop("page",1)
			order = kwargs.pop("order","relevancy")
			direction = kwargs.pop("direction","desc")
			rating = kwargs.pop("rating",["general"])
			type = kwargs.pop("type",["art"])
			headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"}
			data = {
				"q": query,
				"page": page,
				"perpage": results,
				"order-by": order,
				"order-direction": direction,
				"range": range,
				"mode": "extended"
			}
			if page is 1:
				del data["page"]
			types = ["art","music","flash","photo","story","poetry"]
			for i in rating:
				data["rating-"+i] = "on"
			for i in types:
				if i in type:
					data["type-"+i] = "on"
			response = await self.http.post(self.base_url+'search',params=data,headers=headers,cookies=self.cookies)
			if response:
				data = BeautifulSoup(response,"html.parser")
				posts = data.findAll("figure")
				results = []
				if posts:
					for post in posts:
						fig = post.find("figcaption")
						text = fig.find_all("a")
						title = text[0].text
						by = text[1].text
						rating = post["class"][0].replace("r-","")
						type = post["class"][1].replace("t-","")
						source = "http://www.furaffinity.net" + text[0].get("href")
						preview_base = self.get_preview_template("http:"+post.find("img").get("src"))
						pid = (post.get("id")).replace("sid-","")
						res = SearchResult(title=title,id=pid,by=by,rating=rating,source=source,preview_base=preview_base)
						results.append(res)
					return results
				else:
					return []
			else:
				return
		except Exception as e:
			print(e)
			return

	async def parse_post_page(self,**kwargs): #Returns Post() object.
		r = None
		try:
			url = kwargs.pop('url',None)
			id = kwargs.pop('id',None)
			type = kwargs.pop('type',self.VIEWS.DEFAULT)
			if not url and not id:
				return
			if id and not url:
				url = self.base_url+'{0}/{1}/'.format(type,id)
			print(url)
			response = await self.http.get(url,cookies=self.cookies)
			if response:
				data = BeautifulSoup(response,'html.parser')
				sysmsg = data.find('td',attrs={'class':'alt1','align':'center'})
				if sysmsg:
					if sysmsg.text.strip() == 'You are not allowed to view this image due to the content filter settings.':
						r = ContentFilterError('You are not allowed to view this image due to the content filter settings.')
					elif sysmsg.find('p',{'class':'link-override'}):
						r = ContentHiddenError('The owner of this page has elected to make it available to registered users only.')
				else:
					content = data.find("img",attrs={"id":"submissionImg"})
					if not content:
						raise ContentError('Could not get submission image.')
					content_url = 'http:' + content.get('src')
					title = content.get('alt')
					by = data.find("td",attrs={"class":"cat","valign":"middle","align":"left"}).find("a").text
					prev_template = self.get_preview_template('http:'+content.get('data-preview-src'))
					stats = data.find("td",attrs={"valign":"top","align":"left","class":"alt1 stats-container"})
					rating = stats.find("img").get("alt").split(" ")[0].lower()
					if not id:
						id = re.search(r'\/(\d*[^/])\/')
						if id:
							id = id.group(0).replace("/","")
						else:
							id = None
					keywords = [kw.text for kw in data.find('div',attrs={'id':'keywords'}).findChildren()]
					return Post(title=title,id=id,content_url=content_url,preview_base=prev_template,source=url,keywords=keywords,by=by,rating=rating)
			else:
				return
		except Exception as e:
			print(e)
			return
		if r:
			raise r


#because FA has too many restrictions
class ContentFilterError(Exception): pass
class MissingDataError(Exception): pass
class ContentHiddenError(Exception): pass
class ContentError(Exception): pass

class SearchResult(FABaseObject):

	def __init__(self,**kwargs):
		super().__init__()
		self.title = kwargs.pop('title',None)
		self.id = kwargs.pop('id',None)
		self.type = kwargs.pop('type',None)
		self.rating = kwargs.pop('rating',None)
		self.author = kwargs.pop('by',None)
		self.source = kwargs.pop('source',None)
		self.preview_base = kwargs.pop('preview_base',None)

	def get_previews(self,sizes=None):
		if isinstance(sizes,list):
			return [self.preview_base.format(s) for s in sizes]
		elif sizes is None:
			return [self.preview_base.format(s) for s in (200,400,800)]
		else:
			return self.preview_base.format(sizes)

	async def get_post(self,view='view'):
		post = await FurAffinity().parse_post_page(id=self.id,type=view)
		return post

class Post(FABaseObject):

	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		self.title = kwargs.pop('title',None)
		self.id = kwargs.pop('id',None)
		self.author = kwargs.pop('by',None)
		self.content_url = kwargs.pop('content_url',None)
		self.preview_base = kwargs.pop('preview_base',None)
		self.rating = kwargs.pop('rating',None)
		self.source = kwargs.pop('source',None)
		self.keywords = kwargs.pop('keywords',())
		#self.type = kwargs.pop()

	def get_previews(self,sizes=None):
		if isinstance(sizes,list):
			return [self.preview_base.format(s) for s in sizes]
		elif sizes is None:
			return [self.preview_base.format(s) for s in (200,400,800)]
		else:
			return self.preview_base.format(sizes)

	def to_full(self,):
		return FurAffinity().parse_post_page(id=self.id,type=self.TYPES.FULL)

	def to_view(self,):
		return FurAffinity().parse_post_page(id=self.id,type=self.TYPES.DEFAULT)
