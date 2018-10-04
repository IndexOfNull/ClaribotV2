import aiohttp
import asyncio
import async_timeout

class HTTP():

	async def post(self,url,**kwargs):
		retjson = kwargs.pop('json',False)
		headers = kwargs.pop("headers",{})
		params = kwargs.pop("params",{})
		try:
			with async_timeout.timeout(10):
				async with aiohttp.ClientSession() as session:
					async with session.post(url,headers=headers,data=params) as resp:
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
							data = (await resp.json())
						else:
							data = await resp.read()
						return data
		except asyncio.TimeoutError:
			return False
		except Exception as e:
			print(e)
			return False

class Object(): pass

class SearchResult():

	def __init__(self,dictionary):
		for k, v in dictionary.items():
			setattr(self, k, v)

class Reddit():

	def __init__(self):
		self.http = HTTP()
		self.base_url = "https://api.pushshift.io"
		self.direction = Object()
		self.direction.descending = self.direction.desc = "desc"
		self.direction.asc = self.direction.ascending = "asc"
		self.search_type = Object()
		self.search_type.submission = "submission"
		self.search_type.subreddit = "subreddit"
		self.search_type.comment = "comment"
		self.endpoints = {"submission": "/reddit/submission/search","comment": "/reddit/comment/search","subreddit": "/reddit/subreddit/search"}

	async def search(self,**kwargs):
		type = kwargs.pop("search_type",self.search_type.submission)
		url = self.endpoints[type]
		for k,v in kwargs.items():
			if v is True:
				kwargs[k] = "true"
			if v is False:
				kwargs[k] = "false"
		results = await self.http.get(self.base_url + url,json=True,params=kwargs)
		a = []
		for r in results["data"]:
			ob = SearchResult(r)
			a.append(ob)
		return a
