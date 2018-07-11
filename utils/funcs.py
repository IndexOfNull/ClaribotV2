import asyncio
import aiohttp
import discord
import sys

from discord.ext.commands.view import StringView
from discord.ext.commands.context import Context

from io import BytesIO
import json

import async_timeout

from colorama import Fore, Back, Style

import datetime
from dateutil import tz


class Funcs():

	def __init__(self,bot):
		self.bot = bot
		self.misc = Misc(bot)
		self.main = MainFuncs(bot)
		self.overides = Overides(bot)
		self.command = CommandFuncs(bot)
		self.http = HTTP(bot)
		self.time = TimeBased()

class HTTP():

	def __init__(self,bot):
		self.bot = bot
		self.session = aiohttp.ClientSession()

	async def post(self,url,**kwargs):
		retjson = kwargs.pop('json',False)
		headers = kwargs.pop("headers",{})
		params = kwargs.pop("params",{})
		try:
			with async_timeout.timeout(10):
				async with self.session.post(url,headers=headers,data=params) as resp:
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
				async with self.session.get(url,headers=headers) as resp:
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

class TimeBased():

	def __init__(self):
		self.epoch = datetime.datetime.utcfromtimestamp(0)

	def get_formatted_time(self,dt):
		tzconverted = dt.astimezone(tz.tzlocal())
		return tzconverted.strftime("%Y-%m-%d %H:%M:%S {0}".format(tz.tzlocal().tzname(tzconverted)))

	def get_utc_seconds(self,dt):
		return int((dt - self.epoch).total_seconds())

	def get_utc_now(self,**kwargs):
		give_dt = kwargs.pop("datetime",False)
		if give_dt:
			return datetime.datetime.utcnow()
		else:
			return self.get_utc_seconds(datetime.datetime.utcnow())

	def seconds_to_utc(self,seconds):
		t = datetime.datetime.utcfromtimestamp(seconds)
		t = t.replace(tzinfo=tz.tzutc())
		tconverted = t.astimezone(tz.tzlocal())
		tconverted = tconverted.replace(tzinfo=None)
		return tconverted

class Overides():

	def __init__(self,bot):
		self.bot = bot

	@asyncio.coroutine
	def get_prefix(self, message, inputprefix):
		prefix = ret = inputprefix
		if callable(prefix):
			ret = prefix(self.bot, message)
			if asyncio.iscoroutine(ret):
				ret = yield from ret

		if isinstance(ret, (list, tuple)):
			ret = [p for p in ret if p]

		if not ret:
			raise discord.ClientException('invalid prefix (could be an empty string, empty list, or None)')

		return ret

	@asyncio.coroutine
	def get_context(self, message, prefix, *, cls=Context):
		view = StringView(message.content)
		ctx = cls(prefix=None, view=view, bot=self.bot, message=message)

		if self.bot._skip_check(message.author.id, self.bot.user.id):
			return ctx

		prefix = yield from self.get_prefix(message, prefix)
		invoked_prefix = prefix

		if isinstance(prefix, str):
			if not view.skip_string(prefix):
				return ctx
		else:
			invoked_prefix = discord.utils.find(view.skip_string, prefix)
			if invoked_prefix is None:
				return ctx

		invoker = view.get_word().lower()
		ctx.invoked_with = invoker
		ctx.prefix = invoked_prefix
		ctx.command = self.bot.all_commands.get(invoker)
		return ctx

	@asyncio.coroutine
	def process_commands(self, message, prefix):
		ctx = yield from self.get_context(message,prefix)
		if isinstance(ctx.message.channel,discord.TextChannel):
			ctx.personality = self.bot.data.DB.get_personality(ctx.guild)
		else:
			ctx.personality = 'normal'
		if ctx.command:
			ctx.responses = self.bot.funcs.main.get_responses(command_name=ctx.command.name,personality=ctx.personality)
			ctx.gresponses = ctx.responses['global']
			if 'command' in ctx.responses:
				ctx.cresponses = ctx.responses['command']
		else:
			ctx.responses = self.bot.funcs.main.get_responses(personality='default')
			ctx.gresponses = ctx.responses['global']
		yield from self.bot.invoke(ctx)

class CommandFuncs():

	def __init__(self,bot):
		self.bot = bot

	async def confirm_command(self,ctx,**kwargs):
		try:
			target = kwargs.pop('target',None)
			message = ctx.message
			author = message.author
			channel = message.channel
			notice = await ctx.send(ctx.gresponses['confirmation_needed'])
			mstr = "```css\nConfirmation Needed\n====================\nCommand: {0}\n{1}\n====================\n{2}```"
			tstr = ""
			if target:
				if isinstance(target,discord.TextChannel):
					tstr = "Target: #{0.name}\n".format(target)
				elif isinstance(target,discord.User) or isinstance(target,discord.Member):
					tstr = "Target: {0.name}#{0.discriminator}\n".format(target)
				else:
					tstr = "Target: "+target+"\n"
			notif = await author.send(mstr.format(message.content,tstr,'(Type "yes" to confirm, or "no" to cancel)\nThis confirmation will timeout in 20 seconds.\n'))
			confirmed = False
			def check(message):
				nonlocal confirmed
				if message.author == author and message.content.lower() in ['yes','y']:
					confirmed = True
					return True
				elif message.author == author and message.content.lower() in ['no','n']:
					confirmed = False
					return True
			try:
				waitfor = await self.bot.wait_for('message',timeout=20,check=check)
			except asyncio.TimeoutError:
				str2 = mstr.format(message.content,tstr,'THIS CONFIRMATION HAS EXPIRED\n')
				await notif.edit(content=str2)
				await notice.delete()
				return False
			else:
				if confirmed:
					str2 = mstr.format(message.content,tstr,'THIS ACTION HAS BEEN CONFIRMED\n')
					await notif.edit(content=str2)
					await notice.delete()
					return True
				elif confirmed is False:
					str2 = mstr.format(message.content,tstr,'THIS ACTION HAS BEEN CANCELED\n')
					await notif.edit(content=str2)
					await notice.delete()
					return False
				elif confirmed is None:
					str2 = mstr.format(message.content,tstr,'SOMETHING WENT WRONG WHILE CONFIRMING THIS ACTION\n')
					await notif.edit(content=str2)
					await notice.delete()
					return False
			return False
		except Exception as e:
			return False

	async def handle_error(self,ctx,e): #A generic error handler, so that we can universally change how errors are handled
		if isinstance(e, discord.errors.Forbidden):
			print(e.text)
			await ctx.send(ctx.gresponses['forbidden_upload'])
			return
		await ctx.send("`{0}`\nIf this problem persists, you may consider sending a complaint with $complain".format(e))
		print(Fore.RED + e + Style.RESET_ALL)

class MainFuncs():

	def __init__(self,bot):
		self.bot = bot
		self.cursor = self.bot.mysql.cursor
		self.data = self.bot.data

	def get_responses(self,**kwargs):
		try:
			command = kwargs.pop('command_name',None)
			personality = kwargs.pop('personality')
			resp = {"global":self.bot.responses[personality]['global']}
			if command:
				resp['command'] = self.bot.responses[personality]['commands'][command]
			return resp
		except:
			return {"global":self.bot.responses['normal']['global']}

	def is_blacklisted(self,**kwargs): #If ANY of the parameters are in a blacklist, will return True. If not, returns False
		try:
			guild = kwargs.pop('guild')
			message = kwargs.pop('message',None)
			command = kwargs.pop('command',None)
			channel = kwargs.pop('channel',None)
			user = kwargs.pop('user',None)
			if not message and not command and not channel and not user: #if no params passed, assume its not blacklisted
				return False
			if isinstance(user, int):
				user = self.bot.get_user(user)
			if isinstance(command, str):
				command = self.bot.get_command(command)
			if message: #Auto-get blacklisted, while trying to make a few queries to the db as possible
				blacklisted = self.is_blacklisted(guild=guild,command=command,channel=message.channel,user=message.author)
				if blacklisted:
					return True
				else:
					return False
			if command:
				if command.name == 'blacklist': #Safeguard
					return False
				bl = self.data.DB.get_command_blacklisted(guild,command)
				if bl: return True
			if channel: #These are almost like "sub-functions" in a way.
				bl = self.data.DB.get_channel_blacklisted(channel)
				if bl: return True
			if user:
				bl = self.data.DB.get_user_blacklisted(guild,user)
				if bl: return True
			return False
		except Exception as e:
			self.cursor.rollback()
			print(e)
			return False

class Misc():

	def __init__(self,bot):
		self.bot = bot
		self.image_mimes = ['image/png', 'image/pjpeg', 'image/jpeg', 'image/x-icon', 'image/webp']
		self.session = aiohttp.ClientSession()

	async def get_image_mime(self,url,**kwargs):
		get_type = kwargs.pop('type',False)
		try:
			with async_timeout.timeout(5):
				async with self.session.head(url) as resp:
					if resp.status == 200:
						mime = resp.headers.get('Content-type','').lower()
						if get_type:
							if any([mime == x for x in self.image_mimes]):
								return "image"
							elif mime == "image/gif":
								return "gif"
							else:
								return None
			return None
		except Exception as e:
			print(e)
			return None

	async def get_last_attachment(self,ctx,**kwargs):
		limit = kwargs.pop('limit',30)
		type = kwargs.pop('type',None)
		img_urls = []

		async for m in ctx.message.channel.history(before=ctx.message,limit=limit):
			check = False
			last_attachment = None
			if len(m.attachments) > 0:
				last_attachment = m.attachments[0].url
			elif len(m.embeds) > 0:
				last_attachment = m.embeds[0].url
			if last_attachment:
				if type:
					t = await self.get_image_mime(last_attachment,type=True)
					if t == type:
						check = True
					else:
						check = False
				if check:
					img_urls.append(last_attachment)
					break
		return img_urls

	async def get_images(self,ctx,**kwargs):
		try:
			message = ctx.message
			channel = message.channel
			msg = kwargs.pop('msg',True)
			urls = kwargs.pop('urls',None)
			limit = kwargs.pop('limit',3)
			gif = kwargs.pop('gif',False)
			if gif:
				type = "gif"
			else:
				type = "image"
			attachments = message.attachments
			mentions = message.mentions
			if urls is None:
				urls = []
			elif isinstance(urls, str):
				urls = urls.split(" ")
			elif not isinstance(urls, tuple):
				urls = [urls]
			else:
				urls = list(urls)
			img_count = len(urls) - len(mentions)
			for attachment in attachments:
				urls.append(attachment.url)
				img_count+=1
			if gif is False:
				for u in mentions:
					if u.avatar:
						urls.append('https://media.discordapp.net/avatars/{0.id}/{0.avatar}.png?size=512'.format(u))
					else:
						urls.append(u.default_avatar_url)
					img_count+=1
			if len(urls)-img_count > limit:
				if msg:
					await ctx.send(ctx.gresponses['file_count_limit'].format(limit))
				ctx.command.reset_cooldown(ctx)
				return False
			img_urls = []
			if len(urls) == 0:
				last_image = await self.get_last_attachment(ctx,type="gif" if gif else "image")
				if not last_image:
					if msg:
						await ctx.send(ctx.gresponses['missing_image_attachments'].format(', mention(s) ' if not gif else ' '))
					ctx.command.reset_cooldown(ctx)
					return False
				img_urls.extend([*last_image])
				return img_urls
			has_errored = False
			for url in urls:
				if url.startswith("<@"):
					continue
				if not url.startswith("http"):
					url = "http://" + url
				t = await self.get_image_mime(url,type=True)
				if t != type and not t is None:
					if type == "image":
						if msg:
							await ctx.send(ctx.gresponses['image_command'])
					elif type == "gif":
						if msg:
							await ctx.send(ctx.gresponses['gif_command'])
					has_errored = True
					ctx.command.reset_cooldown(ctx)
					continue
				if t is None:
					continue
				img_urls.append(url)
			if len(img_urls) == 0 and not has_errored:
				if msg:
					await ctx.send(ctx.gresponses['missing_image_attachments'].format(', mention(s)' if not gif else ' '))
				ctx.command.reset_cooldown(ctx)
				return False
			return img_urls
		except Exception as e:
			return False

	async def bytes_download(self,url:str):
		try:
			with async_timeout.timeout(10):
				async with self.session.get(url) as resp:
					data = await resp.read()
					b = BytesIO(data)
					b.seek(0)
					return b
		except:
			return False

	async def bytes_download_images(self,ctx,url,imgs=None):
		img = await self.bytes_download(url)
		has_failed = False
		if not img:
			if not has_failed:
				await ctx.send(ctx.gresponses['download_fail'])
			has_failed = True
			if imgs:
				return False
			else:
				return None
		return img

	def get_image_embed(self,srcurl,imgurl):
		embed = discord.Embed(title=":camera: **Source**",type="rich",url=srcurl,color=discord.Color.gold())
		embed.set_image(url=imgurl)
		return embed

	async def handle_uploads(self,ctx,uploads,**kwargs): #Upload the given bytes or list of bytes with a file name, while also checking for size errors
		try:
			filename = kwargs.pop('filename','upload.png')
			if isinstance(uploads, list):
				for upload in uploads:
					if sys.getsizeof(upload) > 8388608:
						await ctx.send(ctx.gresponses['response_too_big'])
						continue
					upload = discord.File(upload,filename)
					await ctx.send(file=upload)
			else:
				upload = uploads
				if sys.getsizeof(upload) > 8388608:
					await ctx.send(ctx.gresponses['response_too_big'])
					return
				upload = discord.File(upload,filename)
				await ctx.send(file=upload)
		except Exception as e:
			print(e)

	def get_warning_embed(self,**kwargs): #This behaves very strangely, but reason is we want to be able to get mentions from raw ids without calling self.bot.get_user()
		user = kwargs.pop('user')
		guild = kwargs.pop('guild')
		reason = kwargs.pop('reason')
		sender = kwargs.pop('warner')
		timestamp = kwargs.pop('timestamp')
		id = kwargs.pop('id')
		embed = discord.Embed(type="rich",title="User Warning",color=discord.Color.red())
		embed.add_field(name="User",value="<@"+str(sender)+">",inline=True)
		embed.add_field(name="Sender",value="<@"+str(user)+">",inline=True)
		embed.add_field(name="Guild",value="{0.name} ({0.id})".format(guild),inline=False)
		embed.add_field(name="Reason",value=reason,inline=False)
		embed.add_field(name="ID",value="`{}`".format(id),inline=False)
		embed.timestamp = datetime.datetime.utcfromtimestamp(timestamp)
		return embed

	"""async def send_game_invite(self,ctx,target,**kwargs):
		game = kwargs.pop('game','a game')
		try:
			invite_msg = '```fix\nGame Invite\n=====================\n{0.name}#{0.discriminator} wants to play {1} with you!\n\n=====================\nRespond with "accept" to accept the invite, or "deny" to deny it.\nThis invite will timeout in 1 minute.\n```'.format(ctx.message.author,game)
			await target.send(invite_msg)
		except Exception as e:
			print(e)
			return""" #May come at a later date


	def format_float(self,num,places,**kwargs):
		max_trailing = kwargs.pop('max_trailing',2)
		formatted = ("%."+str(places)+"f") % num
		reversed = formatted[::-1]
		trailing = 0
		delete_period = False
		if max_trailing == 0:
			delete_period = True
		for char in reversed:
			if delete_period and char == ".":
				trailing+=1
				break
			elif char != "0":
				break
			trailing+=1
		trailing-=max_trailing
		if trailing <= 0:
			return formatted
		else:
			final = formatted[:(trailing*-1)]
			return final
