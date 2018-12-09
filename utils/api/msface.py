
import asyncio
import aiohttp
import async_timeout
import re
import json
import urllib


class BadArgument(Exception): pass
class InvalidURL(Exception): pass
class InvalidImage(Exception): pass
class InvalidImageSize(Exception): pass
class UnspecifiedError(Exception): pass

class HTTP():

	async def post(self,url,**kwargs):
		retjson = kwargs.pop('json',False)
		params = kwargs.pop("params",{})
		try:
			with async_timeout.timeout(10):
				async with aiohttp.ClientSession() as session:
					async with session.post(url,data=params,**kwargs) as resp:
						if retjson:
							return (await resp.json()), resp
						return resp
		except asyncio.TimeoutError:
			return False
		except Exception as e:
			print(e)
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
							data = await resp
						return data
		except asyncio.TimeoutError:
			return False
		except Exception as e:
			print(e)
			return False

class FaceDetector():

	def __init__(self,key,location="westus"):
		self.key = key
		self.base_url = "https://{0}.api.cognitive.microsoft.com/face/v1.0".format(location)
		self.http = HTTP()

	async def detect(self,url,landmarks=True,attributes="age,gender,headPose"):
		headers = {"Ocp-Apim-Subscription-Key":self.key,"Content-Type":"application/json"}
		urlparams = {"returnFaceLandmarks":str(landmarks).lower(),"returnFaceAttributes":attributes}
		urlparams = "?" + urllib.parse.urlencode(urlparams)
		j, response = await self.http.post(self.base_url+"/detect"+urlparams,headers=headers,params=json.dumps({"url":url}),json=True)
		#j = await response.json()
		if "error" in j:
			if j["error"]["code"] == "BadArgument":
				raise BadArgument(j["error"]["message"])
			elif j["error"]["code"] == "InvalidURL":
				raise InvalidURL(j["error"]["message"])
			elif j["error"]["code"] == "InvalidImage":
				raise InvalidImage(j["error"]["message"])
			elif j["error"]["code"] == "InvalidImageSize":
				raise InvalidImageSize(j["error"]["message"])
		if response.status == 401:
			raise_error(UnspecifiedError(),j['error']['message'])
		return j
