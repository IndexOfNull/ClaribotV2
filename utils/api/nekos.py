import asyncio
import aiohttp
import async_timeout
import json

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
		headers = kwargs.pop('headers',{})
		try:
			with async_timeout.timeout(10):
				async with aiohttp.ClientSession() as session:
					async with session.get(url,headers=headers) as resp:
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

class User():

    def __init__(self,**kwargs):
        self.id = kwargs.pop('id',None)
        self.username = kwargs.pop('username',None)

class NekosBase():

    def __init__(self):
        self.base_url = 'https://nekos.moe/api/v1/'
        self.main_url = 'https://nekos.moe/'

class SearchResult(NekosBase):

    def __init__(self,**kwargs):
        super().__init__()
        self.id = kwargs.pop('id',None)
        self.uploader = kwargs.pop('uploader',None)
        self.tags = kwargs.pop('tags',[])
        self.artist = kwargs.pop('artist',None)
        self.nsfw = kwargs.pop('nsfw',False)
        self.likes = kwargs.pop('likes',None)
        self.favorites = kwargs.pop('favorites')
        self.source = self.main_url + 'post/' + self.id + '/'

    def get_image_url(self):
        return self.main_url + 'image/' + self.id

class Nekos(NekosBase):

    def __init__(self):
        super().__init__()
        self.http = HTTP()


    async def search(self,**kwargs):
        try:
            id = kwargs.pop('id',None)
            nsfw = kwargs.pop('nsfw',None)
            uploader = kwargs.pop('uploader',None)
            artist = kwargs.pop('artist',None)
            tags = kwargs.pop('tags',None)
            sort = kwargs.pop('sort','likes')
            before = kwargs.pop('before',None)
            after = kwargs.pop('after',None)
            limit = kwargs.pop('limit',20)
            arg_table = {'id':id,'nsfw':nsfw,'uploader':uploader,'artist':artist,'tags':tags,'sort':sort,'posted_before':before,'posted_after':after,'limit':limit}
            args = {}
            for k,v in arg_table.items():
                if not v is None:
                    args[k] = v
            headers = {'Content-Type':'application/json'}
            response = await self.http.post(self.base_url+'images/search',params=json.dumps(args),headers=headers,json=True)
            if not response:
                return []
            results = []
            for post in response['images']:
                try:
                    results.append(SearchResult(id=post['id'],uploader=User(username=post['uploader']['username'],id=post['uploader']['id']),tags=post['tags'],artist=post['artist'],nsfw=post['nsfw'],likes=post['likes'],favorites=post['favorites']))
                except:
                    pass
            return results
        except Exception as e:
            print(e)
            return

    async def random(self,**kwargs):
        try:
            nsfw = kwargs.pop('nsfw',False)
            count = kwargs.pop('count',1)
            response = await self.http.get(self.base_url+'random/image?count={0}&nsfw={1}'.format(count,str(nsfw).lower()),json=True)
            results = []
            if response:
                for post in response['images']:
                    try:
                        results.append(SearchResult(id=post['id'],uploader=User(username=post['uploader']['username'],id=post['uploader']['id']),tags=post['tags'],artist=post['artist'],nsfw=post['nsfw'],likes=post['likes'],favorites=post['favorites']))
                    except Exception as e:
                        pass
            return results
        except Exception as e:
            return
