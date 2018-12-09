import asyncio
import aiohttp
import async_timeout
import re
import traceback
import random

try:
	from bs4 import BeautifulSoup
except Exception as e:
	raise ImportError('BeautifulSoup did not import properly ({0})'.format(e))


class Object(object):
	pass

class NotParsedError(Exception): pass
class ContentFilterError(Exception): pass
class PrivateError(Exception): pass

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def remove_keys(keys,dict):
	for k in keys:
		dict.pop(k,None)

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
		self.http = kwargs.pop('http',HTTP())

	def get_species(self,species,desired="number"):
		species_to_num = {'unspecified / any':'1','amphibian (other)': '1000', 'frog': '1001', 'newt': '1002', 'salamander': '1003', 'aquatic (other)': '2000', 'cephalopod': '2001', 'dolphin': '2002', 'whale': '2003', 'porpoise': '2004', 'fish': '2005', 'shark': '2006', 'avian (other)': '3000', 'corvid': '3001', 'crow': '3002', 'duck': '3003', 'eagle': '3004', 'falcon': '3005', 'goose': '3006', 'gryphon': '3007', 'hawk': '3008', 'owl': '3009', 'phoenix': '3010', 'swan': '3011', 'dragon (other)': '4000', 'eastern dragon': '4001', 'hydra': '4002', 'serpent': '4003', 'western dragon': '4004', 'wyvern': '4005', 'exotic (other)': '5000', 'alien (other)': '5001', 'argonian': '5002', 'chakat': '5003', 'chocobo': '5004', 'citra': '5005', 'crux': '5006', 'daemon': '5007', 'digimon': '5008', 'dracat': '5009', 'draenei': '5010', 'elf': '5011', 'gargoyle': '5012', 'iksar': '5013', 'langurhali': '5014', 'kaiju/monster': '5015', 'naga': '5016', 'moogle': '5017', 'orc': '5018', 'pokemon': '5019', 'satyr': '5020', 'sergal': '5021', 'tanuki': '5022', 'unicorn': '5023', 'xenomorph': '5024', 'mammals (other)': '6000', 'bat': '6001', 'bear': '6002', 'cows': '6003', 'antelope': '6004', 'gazelle': '6005', 'goat': '6006', 'bovines (general)': '6007', 'coyote': '6008', 'doberman': '6009', 'dog': '6010', 'dingo': '6011', 'german shepherd': '6012', 'jackal': '6013', 'husky': '6014', 'vulpine (other)': '6015', 'wolf': '6016', 'canine (other)': '6017', 'cervine (other)': '6018', 'donkey': '6019', 'domestic cat': '6020', 'cheetah': '6021', 'cougar': '6022', 'jaguar': '6023', 'leopard': '6024', 'lion': '6025', 'lynx': '6026', 'ocelot': '6027', 'panther': '6028', 'tiger': '6029', 'feline (other)': '6030', 'giraffe': '6031', 'hedgehog': '6032', 'hippopotamus': '6033', 'horse': '6034', 'hyena': '6035', 'llama': '6036', 'opossum': '6037', 'kangaroo': '6038', 'koala': '6039', 'quoll': '6040', 'wallaby': '6041', 'marsupial (other)': '6042', 'meerkat': '6043', 'mongoose': '6044', 'badger': '6045', 'ferret': '6046', 'otter': '6047', 'mink': '6048', 'weasel': '6049', 'wolverine': '6050', 'mustelid (other)': '6051', 'panda': '6052', 'pig/swine': '6053', 'gorilla': '6054', 'human': '6055', 'lemur': '6056', 'monkey': '6057', 'primate (other)': '6058', 'rabbit/hare': '6059', 'raccoon': '6060', 'rat': '6061', 'red panda': '6062', 'rhinoceros': '6063', 'beaver': '6064', 'mouse': '6065', 'rodent (other)': '6067', 'seal': '6068', 'skunk': '6069', 'squirrel': '6070', 'zebra': '6071', 'fennec': '6072', 'pony': '6073', 'camel': '6074', 'fox': '6075', 'reptilian (other)': '7000', 'alligator & crocodile': '7001', 'gecko': '7003', 'iguana': '7004', 'lizard': '7005', 'snakes & serpents': '7006', 'turtle': '7007', 'arachnid': '8000', 'dinosaur': '8001', 'insect (other)': '8003', 'mantid': '8004', 'scorpion': '8005'}
		num_to_species = {"1":"Unspecified / Any","1000":"Amphibian (Other)","1001":"Frog","1002":"Newt","1003":"Salamander","2000":"Aquatic (Other)","2001":"Cephalopod","2002":"Dolphin","2003":"Whale","2004":"Porpoise","2005":"Fish","2006":"Shark","3000":"Avian (Other)","3001":"Corvid","3002":"Crow","3003":"Duck","3004":"Eagle","3005":"Falcon","3006":"Goose","3007":"Gryphon","3008":"Hawk","3009":"Owl","3010":"Phoenix","3011":"Swan","4000":"Dragon (Other)","4001":"Eastern Dragon","4002":"Hydra","4003":"Serpent","4004":"Western Dragon","4005":"Wyvern","5000":"Exotic (Other)","5001":"Alien (Other)","5002":"Argonian","5003":"Chakat","5004":"Chocobo","5005":"Citra","5006":"Crux","5007":"Daemon","5008":"Digimon","5009":"Dracat","5010":"Draenei","5011":"Elf","5012":"Gargoyle","5013":"Iksar","5014":"Langurhali","5015":"Kaiju/Monster","5016":"Naga","5017":"Moogle","5018":"Orc","5019":"Pokemon","5020":"Satyr","5021":"Sergal","5022":"Tanuki","5023":"Unicorn","5024":"Xenomorph","6000":"Mammals (Other)","6001":"Bat","6002":"Bear","6003":"Cows","6004":"Antelope","6005":"Gazelle","6006":"Goat","6007":"Bovines (General)","6008":"Coyote","6009":"Doberman","6010":"Dog","6011":"Dingo","6012":"German Shepherd","6013":"Jackal","6014":"Husky","6015":"Vulpine (Other)","6016":"Wolf","6017":"Canine (Other)","6018":"Cervine (Other)","6019":"Donkey","6020":"Domestic Cat","6021":"Cheetah","6022":"Cougar","6023":"Jaguar","6024":"Leopard","6025":"Lion","6026":"Lynx","6027":"Ocelot","6028":"Panther","6029":"Tiger","6030":"Feline (Other)","6031":"Giraffe","6032":"Hedgehog","6033":"Hippopotamus","6034":"Horse","6035":"Hyena","6036":"Llama","6037":"Opossum","6038":"Kangaroo","6039":"Koala","6040":"Quoll","6041":"Wallaby","6042":"Marsupial (Other)","6043":"Meerkat","6044":"Mongoose","6045":"Badger","6046":"Ferret","6047":"Otter","6048":"Mink","6049":"Weasel","6050":"Wolverine","6051":"Mustelid (Other)","6052":"Panda","6053":"Pig/Swine","6054":"Gorilla","6055":"Human","6056":"Lemur","6057":"Monkey","6058":"Primate (Other)","6059":"Rabbit/Hare","6060":"Raccoon","6061":"Rat","6062":"Red Panda","6063":"Rhinoceros","6064":"Beaver","6065":"Mouse","6067":"Rodent (Other)","6068":"Seal","6069":"Skunk","6070":"Squirrel","6071":"Zebra","6072":"Fennec","6073":"Pony","6074":"Camel","6075":"Fox","7000":"Reptilian (Other)","7001":"Alligator &amp; Crocodile","7003":"Gecko","7004":"Iguana","7005":"Lizard","7006":"Snakes &amp; Serpents","7007":"Turtle","8000":"Arachnid","8001":"Dinosaur","8003":"Insect (Other)","8004":"Mantid","8005":"Scorpion"} #For display purposes
		try:
			if species.lower() == 'random':
				species = random.sample(num_to_species.keys(),1)[0]
			species = int(species) #Convert a species string into an int if possible, so we can differentiate an actual name from a number in a string form
		except:
			pass

		if desired == "number":
			if isinstance(species, int):
				if str(species) in species_to_num.values():
					return str(species)
			elif isinstance(species, str):
				if species.lower() in species_to_num:
					return species_to_num[species.lower()]
		elif desired == "name":
			if isinstance(species, int):
				if str(species) in num_to_species:
					return num_to_species[str(species)]
			if isinstance(species, str):
				vals = list(num_to_species.values())
				lowered = [ i.lower() for i in vals ]
				if species.lower() in lowered:
					return vals[lowered.index(species.lower())]
		return None

	def get_gender(self,gender,desired='number'):
		gender_to_num = {'any':'0','male':'2','female':'3','herm':'4','transgender':'5','multiple characters':'6','other / not specified':'7'}
		num_to_gender = {'0': 'Any', '2': 'Male', '3': 'Female', '4': 'Herm', '5': 'Transgender', '6': 'Multiple Characters', '7': 'Other / Not Specified'}

		try:
			if gender.lower() == 'random':
				gender = random.sample(num_to_gender.keys(),1)[0]
			gender = int(gender) #Convert a gender string into an int if possible, so we can differentiate an actual name from a number in a string form
		except:
			pass
		if desired == "number":
			if isinstance(gender, int): #If the gender is an integer, check if its valid and toss it back
				if str(gender) in gender_to_num.values():
					return str(gender)
			elif isinstance(gender, str): #If its a string, convert it into its appropriate value
				if gender.lower() in gender_to_num:
					return gender_to_num[gender.lower()]
		elif desired == "name":
			if isinstance(gender, int):
				if str(gender) in num_to_gender:
					return num_to_gender[str(gender)]
			if isinstance(gender, str):
				vals = list(num_to_gender.values())
				lowered = [ i.lower() for i in vals ]
				if gender.lower() in lowered:
					return vals[lowered.index(gender.lower())]
		return None

	def get_kink(self,kink, desired='number'):
		kink_to_num = {'all': '1', 'abstract': '2', 'animal related (non-anthro)': '3', 'anime': '4', 'comics': '5', 'doodle': '6', 'fanart': '7', 'fantasy': '8', 'human': '9', 'portraits': '10', 'scenery': '11', 'still life': '12', 'tutorials': '13', 'miscellaneous': '14', 'general furry art': '100', 'baby fur': '101', 'bondage': '102', 'digimon': '103', 'fat furs': '104', 'fetish other': '105', 'fursuit': '106', 'hyper': '107', 'inflation': '108', 'macro / micro': '109', 'muscle': '110', 'my little pony / brony': '111', 'paw': '112', 'pokemon': '113', 'pregnancy': '114', 'sonic': '115', 'transformation': '116', 'vore': '117', 'water sports': '118', 'gore / macabre art': '119', 'other music': '200', 'techno': '201', 'trance': '202', 'house': '203', '90s': '204', '80s': '205', '70s': '206', '60s': '207', 'pre-60s': '208', 'classical': '209', 'game music': '210', 'rock': '211', 'pop': '212', 'rap': '213', 'industrial': '214'}
		num_to_kink = {'1': 'All', '2': 'Abstract', '3': 'Animal related (non-anthro)', '4': 'Anime', '5': 'Comics', '6': 'Doodle', '7': 'Fanart', '8': 'Fantasy', '9': 'Human', '10': 'Portraits', '11': 'Scenery', '12': 'Still Life', '13': 'Tutorials', '14': 'Miscellaneous', '100': 'General Furry Art', '101': 'Baby fur', '102': 'Bondage', '103': 'Digimon', '104': 'Fat Furs', '105': 'Fetish Other', '106': 'Fursuit', '107': 'Hyper', '108': 'Inflation', '109': 'Macro / Micro', '110': 'Muscle', '111': 'My Little Pony / Brony', '112': 'Paw', '113': 'Pokemon', '114': 'Pregnancy', '115': 'Sonic', '116': 'Transformation', '117': 'Vore', '118': 'Water Sports', '119': 'Gore / Macabre Art', '200': 'Other Music', '201': 'Techno', '202': 'Trance', '203': 'House', '204': '90s', '205': '80s', '206': '70s', '207': '60s', '208': 'Pre-60s', '209': 'Classical', '210': 'Game Music', '211': 'Rock', '212': 'Pop', '213': 'Rap', '214': 'Industrial'}
		try:
			if kink.lower() == 'random':
				kink = random.sample(num_to_kink.keys(),1)[0]
			kink = int(kink) #Convert a kink string into an int if possible, so we can differentiate an actual name from a number in a string form
		except:
			pass

		if desired == "number":
			if isinstance(kink, int): #If the kink is an integer, check if its valid and toss it back
				if str(kink) in kink_to_num.values():
					return str(kink)
			elif isinstance(kink, str): #If its a string, convert it into its appropriate value
				if kink.lower() in kink_to_num:
					return kink_to_num[kink.lower()]
		elif desired == "name":
			if isinstance(kink, int):
				if str(kink) in num_to_kink:
					return num_to_kink[str(kink)]
			if isinstance(kink, str):
				vals = list(num_to_kink.values())
				lowered = [ i.lower() for i in vals ]
				if kink.lower() in lowered:
					return vals[lowered.index(kink.lower())]
		return None

	def get_category(self,category, desired='number'):
		category_to_num = {'all': '1', 'artwork (digital)': '2', 'artwork (traditional)': '3', 'cellshading': '4', 'crafting': '5', 'designs': '6', 'flash': '7', 'fursuiting': '8', 'icons': '9', 'mosaics': '10', 'photography': '11', 'sculpting': '12', 'story': '13', 'poetry': '14', 'prose': '15', 'music': '16', 'podcasts': '17', 'skins': '18', 'handhelds': '19', 'resources': '20', 'adoptables': '21', 'auctions': '22', 'contests': '23', 'current events': '24', 'desktops': '25', 'stockart': '26', 'screenshots': '27', 'scraps': '28', 'wallpaper': '29', 'ych / sale': '30', 'other': '31'}
		num_to_category = {'1': 'All', '2': 'Artwork (Digital)', '3': 'Artwork (Traditional)', '4': 'Cellshading', '5': 'Crafting', '6': 'Designs', '7': 'Flash', '8': 'Fursuiting', '9': 'Icons', '10': 'Mosaics', '11': 'Photography', '12': 'Sculpting', '13': 'Story', '14': 'Poetry', '15': 'Prose', '16': 'Music', '17': 'Podcasts', '18': 'Skins', '19': 'Handhelds', '20': 'Resources', '21': 'Adoptables', '22': 'Auctions', '23': 'Contests', '24': 'Current Events', '25': 'Desktops', '26': 'Stockart', '27': 'Screenshots', '28': 'Scraps', '29': 'Wallpaper', '30': 'YCH / Sale', '31': 'Other'}
		try:
			if category.lower() == 'random':
				category = random.sample(num_to_category.keys(),1)[0]
			category = int(category) #Convert a category string into an int if possible, so we can differentiate an actual name from a number in a string form
		except:
			pass

		if desired == "number":
			if isinstance(category, int): #If the category is an integer, check if its valid and toss it back
				if str(category) in category_to_num.values():
					return str(category)
			elif isinstance(category, str): #If its a string, convert it into its appropriate value
				if category.lower() in category_to_num:
					return category_to_num[category.lower()]
		elif desired == "name":
			if isinstance(category, int):
				if str(category) in num_to_category:
					return num_to_category[str(category)]
			if isinstance(category, str):
				vals = list(num_to_category.values())
				lowered = [ i.lower() for i in vals ]
				if category.lower() in lowered:
					return vals[lowered.index(category.lower())]
		return None

	def parse_figure(figure):
		fig = FAFigure(figure)
		fig.parse()
		return fig

class FAFigure(FABaseObject):

	def __init__(self,figure,**kwargs):
		super().__init__(**kwargs)
		self.figure = figure
		self.cookies = kwargs.pop('cookies',{})
		if self.figure.__class__.__module__ != "bs4.element": #Convert any input into a BeautifulSoup instance
			self.figure = BeautifulSoup(figure,"html.parser")

	def parse(self):
		fig = self.figure
		self.id = fig.get("id").split("-")[1] # 'sid-123456789' -> ['sid','123456789'] -> '123456789'
		self.rating = fig['class'][0].split("-")[1] # 'r-general' -> ['r','general'] -> 'general'
		self.type = fig['class'][1].split("-")[1] #pretty much same as above
		display_data = fig.find('figcaption').findAll('p')
		self.author = display_data[1].find('a').get('title')
		self.title = display_data[0].find('a').get('title')
		self.preview = 'http:' + fig.find('img').get('src')
		self.preview_template = re.sub(r"(?<=@).*.+?(?=-)",'{0}',self.preview)
		self.url = self.base_url + 'view/' + self.id
		self.full_url = self.base_url + 'full/' + self.id
		self.parsed = True

	def search_result(self):
		if self.parsed:
			opts = vars(self)
			remove_keys(('parsed','figure'),opts)
			r = FASearchResult(**opts)
			return r
		else:
			raise NotParsedError("You must parse a figure before you can convert it into a search result.")

class FASearchResult(FABaseObject):

	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		self.cookies = kwargs.pop('cookies',{})
		for k,v in kwargs.items():
			setattr(self,k,v)

	async def get_post(self,get_data=True):
		post = FAPost(id=self.id,cookies=self.cookies)
		if get_data: await post.get_data()
		return post

	def get_preview(self,size):
		if self.preview_template:
			return self.preview_template.format(size)
		else:
			raise NotParsedError("The preview template is missing, make sure that FASearchResult was passed the correct, parsed information.")

	def get_user():
		raise NotImplementedError("Add user scraping support for this to work lol")

class FAPost(FABaseObject):

	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		self.id = kwargs.pop('id')
		self.cookies = kwargs.pop('cookies',{})
		for arg in kwargs:
			for k,v in dictionary.items():
				setattr(self,k,v)

	def parse(self,data):
		data = BeautifulSoup(data,"html.parser")
		if data:
			notif_box = data.find('td',{'class':'alt1'})
			if notif_box:
				t = notif_box.text
				if t == "You are not allowed to view this image due to the content filter settings.":
					raise ContentFilterError(t)
				elif False: #Change false to whatever the text really is
					raise PrivateError()
			meta_box = data.find('td',{'class':'alt1 stats-container'})
			b = meta_box.findAll('b')
			self.url = self.base_url + 'view/'+str(self.id)
			self.full_url = self.base_url + 'full/'+str(self.id)
			self.category = b[2].next_sibling.strip()
			self.theme = b[3].next_sibling.strip()
			self.species = b[4].next_sibling.strip()
			self.gender = b[5].next_sibling.strip()
			self.favories = b[6].next_sibling.strip()
			self.comments = b[7].next_sibling.strip()
			self.views = b[8].next_sibling.strip()
			res = b[10].next_sibling.strip()
			self.resolution = res.split("x")

			keywords_a = data.find('div',{'id':'keywords'}).findAll('a')
			self.keywords = []
			for a in keywords_a:
				self.keywords.append(a.text)

			self.rating = meta_box.find('div',{'style':'padding-left: 6px;'}).find('img').get('alt').split(' ')[0].lower()
			i = data.find('img',{'id':'submissionImg'})
			self.img = 'http:' + i.get('data-fullview-src')
			self.preview = 'http:' + i.get('data-preview-src')
			self.preview_template = re.sub(r"(?<=@).*.+?(?=-)",'{0}',self.preview)
			post_data = data.find('td',{'class':'cat'})
			self.title = post_data.find('b').text
			self.author = post_data.find('a').text
		return None

	async def get_data(self,parse=True):
		resp = await self.http.get(self.base_url + 'view/'+str(self.id),cookies=self.cookies)
		if resp:
			if parse: return self.parse(resp)
			return resp
		return None


class FurAffinity(FABaseObject):

	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		self.cookies = kwargs.pop("cookies",()) #Session cookies, should be in the format of (a cookie, b cookie)
		if self.cookies:
			if len(self.cookies) >= 2:
				self.a_cookie = self.cookies[0]
				self.b_cookie = self.cookies[1]
				self.cookies = {'a':self.a_cookie,'b':self.b_cookie}

	async def browse(self,**kwargs):
		cat = self.get_category(kwargs.pop('cat','1'))
		atype = self.get_kink(kwargs.pop('atype','1'))
		species = self.get_species(kwargs.pop('species','1'))
		gender = self.get_gender(kwargs.pop('gender','0'))
		ratings = kwargs.pop('ratings',['general'])
		perpage = kwargs.pop('perpage',48)
		result_count = kwargs.pop('results',perpage)
		page = kwargs.pop('page','1')
		form_data = {
			'cat': cat,
			'atype': atype,
			'species': species,
			'gender': gender,
			'perpage': perpage,
		}
		for rating in ('general','mature','adult'):
			val = ''
			if rating in ratings:
				val = '1'
			form_data['rating_'+rating] = val
		resp = await self.http.post(self.base_url + 'browse/'+str(page), params=form_data, cookies=self.cookies)
		if resp:
			results = []
			data = BeautifulSoup(resp,'html.parser')
			figures = data.findAll("figure")
			if figures:
				for fig in figures:
					c = FAFigure(fig,cookies=self.cookies,http=self.http)
					c.parse()
					results.append(c.search_result())
				if len(results) > result_count:
					results = random.sample(results,result_count)
				return results


	async def search(self,query,**kwargs):
		try:
			ratings = kwargs.pop("ratings",['general'])
			types = kwargs.pop('types',['art'])
			order = kwargs.pop('order','relevancy')
			page = kwargs.pop('page',1)
			order_dir = kwargs.pop('direction','desc')
			perpage = kwargs.pop('perpage',48)
			result_count = kwargs.pop('results',perpage)
			form_data = {
				'q': query,
				'page': page,
				'perpage': perpage,
				'order-by': order,
				'order-direction': order_dir,
				'do_search': 'Search',
				'range': 'all',
				'mode': 'extended'
			}
			for rating in ratings:
				form_data['rating-'+rating] = 'on'
			for type in types:
				form_data['type-'+type] = 'on'
			resp = await self.http.post(self.base_url + '/search', params=form_data, cookies=self.cookies)
			if resp:
				results = []
				data = BeautifulSoup(resp,'html.parser')
				figures = data.findAll("figure")
				if figures:
					for fig in figures:
						c = FAFigure(fig,cookies=self.cookies,http=self.http)
						c.parse()
						results.append(c.search_result())
					if len(results) > result_count:
						results = random.sample(results,result_count)
					return results
			return None
		except:
			traceback.print_exc()

	async def random(self,**kwargs): #Pull random pictures from a query, im a fucking idiot, i need to make this use self.search and self.browse
		try:
			oldkwargs = kwargs
			query = kwargs.pop('query',None)
			dry = kwargs.pop('dry',True)
			if query:
				kwargs['direction'] = random.sample(['desc','asc'],1)
				kwargs['order'] = random.sample(['relevancy','date','popularity'],1)
				results = await self.search(query,**kwargs)
			else:
				results = await self.browse(**kwargs)
			if not results and dry:
				oldkwargs['page'] = 1
				oldkwargs['dry'] = False
				results = await self.random(**oldkwargs)
			return results
		except:
			traceback.print_exc()
