import discord
from discord.ext import commands
import hashlib

from random import randint

from PIL import Image

import colorama
from colorama import Fore, Back, Style
import qrcode
pyzbar_imported = False
try:
	from pyzbar.pyzbar import decode
	pyzbar_imported = True
except:
	print(Fore.MAGENTA + 'Something went wrong while importing pyzbar. Please make sure you have the zbar shared libraries installed.')
	pyzbar_imported = False

from utils.api import reddit

import traceback

class Misc():

	def __init__(self,bot):
		self.bot = bot
		self.funcs = self.bot.funcs
		self.data = self.bot.data
		self.imaging = self.bot.imaging
		self.get_images = self.funcs.misc.get_images
		self.bytes_download_images = self.funcs.misc.bytes_download_images

	@commands.command()
	@commands.cooldown(1,2,commands.BucketType.user)
	async def help(self,ctx):
		await ctx.send("https://github.com/IndexOfNull/ClaribotV2/blob/master/Commands.txt")

	@commands.command()
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def crypto(self,ctx,fromcur:str,tocur:str):
		try:
			await ctx.trigger_typing()
			fromcur,tocur = (fromcur.upper(),tocur.upper())
			await ctx.trigger_typing()
			url = "https://min-api.cryptocompare.com/data/price?fsym=" + fromcur + "&tsyms=" + tocur
			resp = await self.funcs.http.get(url,json=True)
			if not resp:
				await ctx.send(ctx.gresponses['generic_api_error'])
				return
			if "Response" in resp:
				await ctx.send(ctx.cresponses['invalid_currency'])
				return
			if tocur in resp:
				if tocur.upper() == "BTC" and resp[tocur.upper()] < 0.00004:
					resp["SATOSHI"] = resp[tocur.upper()] * 100000000
					tocur = "SATOSHI"
				formatted_float = self.funcs.misc.format_float(resp[tocur],5)
				msg = "```md\nCryptocurrency Conversion\n====================\n1 {0} -> {1}\n====================\n\nData sourced from cryptocompare.com\n```".format(fromcur,formatted_float + " " + tocur)
				await ctx.send(msg)
		except Exception as e:
			print(e)
			await self.funcs.command.handle_error(ctx,e)

		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['colour'])
	@commands.cooldown(1,3,commands.BucketType.user)
	async def color(self,ctx,*color):
		try:
			await ctx.trigger_typing()
			non_random = False
			c = None
			title = 'Random Color'
			if color:
				if len(color) == 3:
					try:
						for n in color:
							if int(n) > 255:
								non_random = False
								break
							else:
								non_random = True
						if non_random:
							colors2 = ( int(x) for x in color )
							c = discord.Color.from_rgb(*colors2)
							title = 'RGB Color'
							non_random = True
					except:
						non_random = False
				elif len(color) == 1:
					if len(color[0]) == 7:
						h = color[0].strip('#')
						try:
							rgb = tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))
							c = discord.Color.from_rgb(*rgb)
							title = 'Hex Color'
							non_random = True
						except:
							non_random = False
			if not non_random:
				rgb = (randint(0,255),randint(0,255),randint(0,255))
				c = discord.Color.from_rgb(*rgb)
				title = 'Random Color'
			embed = discord.Embed(title=title,type='rich',color=c)
			embed.add_field(name='RGB',value='{0}, {1}, {2}'.format(*c.to_rgb()),inline=True)
			embed.add_field(name='Hex',value='#%02x%02x%02x' % c.to_rgb(),inline=True)
			await ctx.send(embed=embed)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def random(self,ctx,min:int,max:int):
		if min > max:
			min,max=max,min
		try:
			await ctx.trigger_typing()
			await ctx.send(randint(min,max))
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def upsidedown(self,ctx,*,text:str):
		try:
			await ctx.trigger_typing()
			data = self.data.datasets.get_upsidedown_text()
			final=""
			for char in text.lower():
				if char not in data:
					final += char
				final += data[char]
			await ctx.send(final)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.group(invoke_without_command=True)
	@commands.cooldown(1,3,commands.BucketType.user)
	async def avatar(self,ctx,user:discord.User=None):
		if not user:
			user = ctx.message.author
		try:
			await ctx.trigger_typing()
			embed = discord.Embed(title="User Avatar",type="rich",color=discord.Color.teal(),description="{0.name}#{0.discriminator}".format(user))
			embed.set_image(url=user.avatar_url)
			await ctx.send(embed=embed)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)



	@avatar.command()
	@commands.guild_only()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def server(self,ctx):
		try:
			await ctx.trigger_typing()
			embed = discord.Embed(title="Server Icon",type="rich",coclor=discord.Color.teal())
			if not ctx.guild.icon:
				await ctx.send('This server does not have an icon.')
				return
			icon = 'https://cdn.discordapp.com/icons/{0.id}/{0.icon}.png'.format(ctx.guild)
			embed.set_image(url=icon)
			await ctx.send(embed=embed)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.group()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def hash(self,ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send('Valid hash types are `md5, sha1, sha256, sha512, blake2b, blake2s`')

	@hash.command()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def sha256(self,ctx,*,input:str):
		try:
			await ctx.trigger_typing()
			m = hashlib.sha256()
			m.update(input.encode('utf-8'))
			msg = """```diff\n+ Hashing Algorithm: sha_256\n+ Input: {0}\n+ Output: {1}\n\n- WARNING: DO NOT USE FOR PRODUCTION USE!\n```"""
			await ctx.send(msg.format(input,m.hexdigest()))
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@hash.command()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def sha512(self,ctx,*,input:str):
		try:
			await ctx.trigger_typing()
			m = hashlib.sha512()
			m.update(input.encode('utf-8'))
			msg = """```diff\n+ Hashing Algorithm: sha_512\n+ Input: {0}\n+ Output: {1}\n\n- WARNING: DO NOT USE FOR PRODUCTION USE!\n```"""
			await ctx.send(msg.format(input,m.hexdigest()))
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@hash.command()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def sha1(self,ctx,*,input:str):
		try:
			await ctx.trigger_typing()
			m = hashlib.sha1()
			m.update(input.encode('utf-8'))
			msg = """```diff\n+ Hashing Algorithm: sha_1\n+ Input: {0}\n+ Output: {1}\n\n- WARNING: DO NOT USE FOR PRODUCTION USE!\n```"""
			await ctx.send(msg.format(input,m.hexdigest()))
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@hash.command()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def blake2b(self,ctx,*,input:str):
		try:
			await ctx.trigger_typing()
			m = hashlib.blake2b()
			m.update(input.encode('utf-8'))
			msg = """```diff\n+ Hashing Algorithm: blake2b\n+ Input: {0}\n+ Output: {1}\n\n- WARNING: DO NOT USE FOR PRODUCTION USE!\n```"""
			await ctx.send(msg.format(input,m.hexdigest()))
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@hash.command()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def blake2s(self,ctx,*,input:str):
		try:
			await ctx.trigger_typing()
			m = hashlib.blake2s()
			m.update(input.encode('utf-8'))
			msg = """```diff\n+ Hashing Algorithm: blake2s\n+ Input: {0}\n+ Output: {1}\n\n- WARNING: DO NOT USE FOR PRODUCTION USE!\n```"""
			await ctx.send(msg.format(input,m.hexdigest()))
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)


	@hash.command()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def md5(self,ctx,*,input:str):
		try:
			await ctx.trigger_typing()
			m = hashlib.md5()
			m.update(input.encode('utf-8'))
			msg = """```diff\n+ Hashing Algorithm: MD5\n+ Input: {0}\n+ Output: {1}\n\n- WARNING: DO NOT USE FOR PRODUCTION USE!\n```"""
			await ctx.send(msg.format(input,m.hexdigest()))
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,5,commands.BucketType.guild)
	@commands.bot_has_permissions(attach_files=True)
	async def qr(self,ctx,*data:str):
		try:
			await ctx.trigger_typing()
			limit = 3
			if data is None:
				await ctx.send(":warning: Please enter data to be encoded.")
				return
			def genQR(data):
				qr = qrcode.QRCode(version=1,box_size=8,border=4,error_correction=qrcode.constants.ERROR_CORRECT_L)
				qr.add_data(data)
				img = qr.make_image()
				return self.imaging.toBytes(img)
			for opt in data:
				if not (opt.startswith("https://") or opt.startswith("http://")):
					concat = True
			if concat:
				data = " ".join(data)
				await ctx.send("[ `{}` ]".format(data[:100]),file=discord.File(genQR(data),"qrcode.png"))
			else:
				if len(data) > limit:
					await ctx.send(ctx.gresponses['generic_limit'].format('less',str(limit)+'URLs'))
					return
				for i in data:
					await ctx.send("[ `{}` ]".format(i[:100]),file=discord.File(genQR(i),"qrcode.png"))
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	if pyzbar_imported:

		@commands.command()
		@commands.cooldown(1,5,commands.BucketType.guild)
		async def qrdecode(self,ctx,*urls):
			try:
				await ctx.trigger_typing()
				images = await self.get_images(ctx,urls=urls,limit=2)
				if images:
					embed = discord.Embed(type="rich",title="Decoded QR Data",color=discord.Color.green())
					count = 1
					for url in images:
						b = await self.bytes_download_images(ctx,url,images)
						if b is None:
							continue
						if b is False:
							return
						img = Image.open(b).convert("L")
						data = decode(img,scan_locations=True)
						if not data:
							await ctx.send(ctx.cresponses['no_data'])
							continue
						embed.add_field(name="QR Data [{}]".format(count),value=(data[0].data).decode("utf-8"),inline=False)
						count+=1
					await ctx.send(embed=embed)
			except Exception as e:
				await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,86400,commands.BucketType.user)
	async def complain(self,ctx,*,message:str):
		try:
			success = self.data.DB.add_user_message(ctx,message=message,type='complaint')
			if success:
				await ctx.send(ctx.gresponses['generic_sent_success'].format("complaint"))
			else:
				await ctx.send(ctx.gresponses['generic_database_error'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,86400,commands.BucketType.user)
	async def suggest(self,ctx,*,message:str):
		try:
			success = self.data.DB.add_user_message(ctx,message=message)
			if success:
				await ctx.send(ctx.gresponses['generic_sent_success'].format("suggestion"))
			else:
				await ctx.send(ctx.gresponses['generic_database_error'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['uwu'])
	@commands.guild_only()
	@commands.cooldown(1,5,commands.BucketType.user)
	async def owo(self,ctx,user:discord.Member=None):
		if user is None:
			user = ctx.author
		try:
			count = self.data.counters.get_owo_count(user,ctx.guild,default=False)
			if count is False:
				count = 0
			if isinstance(count, int):
				if count == 0:
					await ctx.send(ctx.cresponses['none'].format(user))
					return
				await ctx.send(ctx.cresponses['count'].format(user,count))
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,5,commands.BucketType.user)
	async def reddit(self,ctx,subreddit:str,*,query:str=""):
		try:
			await ctx.trigger_typing()
			r = reddit.Reddit()
			results = await r.search(q=query,is_video="false",subreddit=subreddit,domain="i.redd.it,i.imgur.com",over_18=("true" if ctx.channel.is_nsfw() else "false"))
			if len(results) <= 0:
				await ctx.send(ctx.cresponses['no_results'])
				return
			if results:
				num = randint(0,len(results)-1)
				result = results[num]
				embed = self.funcs.misc.get_image_embed(result.full_link,result.url)
				embed.set_footer(text="Posted by {0} on r/{1}.".format(result.author,result.subreddit))
				await ctx.send(embed=embed)
			else:
				await ctx.send(ctx.cresponses['no_results'])
		except Exception as e:
			traceback.print_exc()

def setup(bot):
	bot.add_cog(Misc(bot))
