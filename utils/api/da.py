import asyncio
import aiohttp
import async_timeout

import xml.etree.ElementTree as ET

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
		headers = kwargs.pop("headers",{})
		try:
			with async_timeout.timeout(10):
				async with aiohttp.ClientSession() as session:
					async with session.get(url,headers=headers) as resp:
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

class SearchResult():

	def __init__(self,**kwargs):
		self.title = kwargs.pop('title',None)
		self.author = kwargs.pop('by',None)
		self.source = kwargs.pop('source',None)
		self.content = kwargs.pop('content',None)
		self.rating = kwargs.pop('rating',None)


class DeviantArt():

	def __init__(self):
		self.xml_url = 'https://backend.deviantart.com/rss.xml'
		self.media_dict = '{http://search.yahoo.com/mrss/}'
		self.http = HTTP()

	async def search(self,query='',**kwargs):
		try:
			nsfw = kwargs.pop('nsfw',False) #Filter For "Mature Content"
			sfw = kwargs.pop('sfw',True) #Filter out SFW content (for true nsfw bois)
			if not sfw: #If its not SFW, it has to be NSFW
				nsfw = True
			mediums = kwargs.pop('mediums',['image'])
			offset = kwargs.pop('offset',0)
			url = self.xml_url + '?type=deviation&offset={0}&q={1}'.format(offset,query)
			response = await self.http.get(url)
			if response:
				root = ET.fromstring(response)
				channel = root.find("channel")
				items = channel.findall("item")
				if not items:
					return []
				results = []
				for item in items:
					try:
						med = item.find(self.media_dict+'content').get('medium')
						rating = item.find(self.media_dict+'rating').text
						if not med in mediums or (nsfw is False and rating == 'adult') or (sfw is False and rating == 'nonadult'):
							continue
						content = item.find(self.media_dict+'content').get('url')
						source = item.find('link').text
						author = item.find(self.media_dict+'credit').text
						title = item.find('title').text
						results.append(SearchResult(title=title,by=author,source=source,content=content,rating=rating))
					except:
						pass
				return results
			else:
				return []
		except Exception as e:
			print(e)
			return
