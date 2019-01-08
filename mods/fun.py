import discord
from discord.ext import commands
from io import BytesIO

from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageEnhance

import random
from random import randint
import xml.etree.ElementTree as ET
import json

import traceback

from utils import checks
from utils.api import reddit

from time import strftime

class Fun():

	def __init__(self,bot):
		self.bot = bot
		self.data = self.bot.data
		self.funcs = self.bot.funcs
		self.imaging = self.bot.imaging
		self.get_images = self.funcs.misc.get_images
		self.bytes_download_images = self.funcs.misc.bytes_download_images

	#Image Commands

	@commands.command(aliases=['snapchat'])
	@commands.cooldown(1,5,commands.BucketType.guild)
	@commands.bot_has_permissions(attach_files=True)
	async def caption(self,ctx,*,text:str):
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx,urls=None,limit=1)
			if images:
				image = images[0]
				b = await self.bytes_download_images(ctx,image,images)
				if b is None or b is False:
					return
				total_lheight = 0
				img = Image.open(b).convert("RGBA")
				iw,ih = img.size
				font = ImageFont.truetype("resource/font/OpenSansEmoji.ttf",28)
				lines = self.imaging.text_wrap(text,font=font,max_pixels=iw-20,wrap="word")
				for line in lines:
					total_lheight += font.getsize(line)[1]
				blackbox_offset = (0,int(ih*0.75))
				blackbox = Image.new("RGBA",(iw,total_lheight+10),(0,0,0,127))
				d = ImageDraw.Draw(blackbox)
				yoffset = 0
				for line in lines:
					lw,lh = font.getsize(line)
					d.text((int(iw/2-lw/2),5+yoffset),line,font=font,fill="#fff")
					yoffset+=int(lh)
				#img.paste(blackbox,blackbox_offset,blackbox)
				final = self.imaging.paste(img,blackbox,offset=blackbox_offset,bytes=True)
				await self.funcs.misc.handle_uploads(ctx,final,filename="captioned.png")
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['banana'])
	@commands.cooldown(1,5,commands.BucketType.guild)
	@commands.bot_has_permissions(attach_files=True)
	async def bananaman(self,ctx,*,text:str):
		try:
				await ctx.trigger_typing()
				img = Image.open("resource/img/bananaman.jpg").convert("RGB")
				iw,ih = img.size
				font = ImageFont.truetype("resource/font/OpenSansEmoji.ttf",32)
				lines = self.imaging.text_wrap(text,font=font,max_pixels=430,wrap="word")
				d = ImageDraw.Draw(img)
				yoffset = 0
				for line in lines:
					lw,lh = font.getsize(line)
					d.text((480,int(163+yoffset)),line,font=font,fill="#000")
					yoffset+=int(lh)
				#img.paste(blackbox,blackbox_offset,blackbox)
				final = self.imaging.toBytes(img,"JPEG")
				await self.funcs.misc.handle_uploads(ctx,final,filename="bananaman.jpg")
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['gandalf'])
	@commands.cooldown(1,5,commands.BucketType.guild)
	@commands.bot_has_permissions(attach_files=True)
	async def run(self,ctx,*urls):
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx,urls=urls)
			if images:
				for url in images:
					b = await self.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					img = img.resize((447,335))
					g2 = Image.open("resource/img/run.png").convert("RGBA")
					final = self.imaging.paste(g2,img,offset=(0,422),resample=Image.LANCZOS,bytes=True)
					await self.funcs.misc.handle_uploads(ctx,final,filename="run.png")
		except discord.errors.Forbidden as e:
			await self.funcs.command.handle_error(ctx,e)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['cmm'])
	@commands.cooldown(1,5,commands.BucketType.guild)
	@commands.bot_has_permissions(attach_files=True)
	async def changemymind(self,ctx,*,text:str):
		try:
			await ctx.trigger_typing()
			cmm = Image.open("resource/img/changemymind.png").convert("RGBA")
			yoffset = 0
			total_lheight = 0
			font = ImageFont.truetype("resource/font/OpenSans-Semibold.ttf",22)
			lines = self.imaging.text_wrap(text,font=font,max_pixels=232,wrap='word')
			for line in lines:
				h = font.getsize(line)[1]
				total_lheight+= h
			img = Image.new("RGBA",(235,int(total_lheight)))
			d = ImageDraw.Draw(img)
			for line in lines:
				d.text((0,yoffset),line,font=font,fill="#000")
				yoffset += font.getsize(line)[1]
			img = img.rotate(22,expand=True)
			pasted = self.imaging.paste(cmm,img,offset=(380,225-int(total_lheight/2)),bytes=True)
			await self.bot.funcs.misc.handle_uploads(ctx,pasted,filename="changemymind.png")
		except discord.errors.Forbidden as e:
			await self.funcs.command.handle_error(ctx,e)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['captionbot'])
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def identify(self,ctx,*urls):
		try:
			images = await self.get_images(ctx,urls=urls,limit=2)
			if images:
				for url in images:
					await ctx.trigger_typing()
					resp = await self.funcs.http.post('https://captionbot.azurewebsites.net/api/messages',params=json.dumps({"Content": url,"Type": "CaptionRequest"}),headers={"Content-Type": "application/json; charset=utf-8"},json=True)
					if resp:
						await ctx.send(resp)
						return
					await ctx.send(ctx.gresponses['generic_api_error'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)



	@commands.command(aliases=['keynote'])
	@commands.bot_has_permissions(attach_files=True)
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def apple(self,ctx,*urls):
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx,urls=urls)
			if images:
				for url in images:
					b = await self.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					base = Image.new("RGBA",(780,449))
					img = Image.open(b).convert("RGBA")
					apple = Image.open('resource/img/apple.png').convert('RGBA')
					pasted = self.imaging.paste(base,img,offset=(159,3),resize=(447,264))
					pasted2 = self.imaging.paste(pasted,apple,offset=(0,0),bytes=True)
					await self.bot.funcs.misc.handle_uploads(ctx,pasted2,filename="apple.png")
		except discord.errors.Forbidden as e:
			await self.funcs.command.handle_error(ctx,e)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['victoryroyale'])
	@commands.bot_has_permissions(attach_files=True)
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def victory(self,ctx,*urls):
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx,urls=urls)
			if images:
				for url in images:
					b = await self.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					vr = Image.open('resource/img/victoryroyale.png').convert('RGBA')
					vr.thumbnail((int(img.size[0]/1.2), int(img.size[1]/4.5)))
					pasted = self.imaging.paste(img,vr,offset=(int(img.size[0]/2-vr.size[0]/2),int(img.size[1]/5)),bytes=True)
					await self.bot.funcs.misc.handle_uploads(ctx,pasted,filename="victoryroyale.png")
		except discord.errors.Forbidden as e:
			await self.funcs.command.handle_error(ctx,e)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	if strftime("%B") == "October":

		@commands.command(aliases=['skeleton','spook'])
		@commands.bot_has_permissions(attach_files=True)
		@commands.cooldown(1,5,commands.BucketType.guild)
		async def spooky(self,ctx):
			try:
				await ctx.trigger_typing()
				if randint(1,20) == 1:
					if randint(1,2) == 1:
						img = "resource/img/spooky/papyrus.png"
					else:
						img = "resource/img/spooky/sans.jpg"
				else:
					if isinstance(ctx.channel, discord.TextChannel):
						if ctx.channel.is_nsfw():
							if randint(1,20) == 1:
								img = "resource/img/spooky/nsfw.gif"
							else:
								img = "resource/img/spooky/{0}.gif".format(int(randint(100,1300)/100))
						else:
							img = "resource/img/spooky/{0}.gif".format(int(randint(100,1300)/100))
					else:
						img = "resource/img/spooky/{0}.gif".format(int(randint(100,1300)/100))
				await ctx.send(file=discord.File(img))
			except discord.errors.Forbidden as e:
				await self.funcs.command.handle_error(ctx,e)
			except Exception as e:
				await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['loganpaul'])
	@commands.bot_has_permissions(attach_files=True)
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def logan(self,ctx,*urls):
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx,urls=urls)
			if images:
				for url in images:
					b = await self.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					lp = Image.open('resource/img/loganpaul.png').convert('RGBA')
					lp.thumbnail((int(img.size[0]/1.8), int(img.size[1]/1.25)))
					pasted = self.imaging.paste(img,lp,offset=(img.size[0]-lp.size[0],img.size[1]-lp.size[1]),bytes=True)
					await self.bot.funcs.misc.handle_uploads(ctx,pasted,filename="logan.png")
		except discord.errors.Forbidden as e:
			await self.funcs.command.handle_error(ctx,e)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['gta'])
	@commands.bot_has_permissions(attach_files=True)
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def wasted(self,ctx,*urls):
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx,urls=urls)
			if images:
				for url in images:
					b = await self.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					img = ImageOps.grayscale(img)
					img = img.convert("RGBA")
					wasted = Image.open("resource/img/wasted.png").convert("RGBA")
					dimg = Image.new("RGBA",img.size)
					draw = ImageDraw.Draw(dimg)
					w,h = img.size
					rw,rh = (w,(int(h/2)+int(h/8))-(int(h/2)-int(h/8)))
					draw.rectangle([(0,int(h/2)-int(h/8)),(w,int(h/2)+int(h/8))],fill=(0,0,0,127))
					img.paste(dimg,(0,0),dimg)
					wasted.thumbnail((int(rw-20),int(rh/2)))
					ww,wh = wasted.size
					img.paste(wasted,(int(rw/2)-int(ww/2),int(h/2)-int(wh/2)),wasted)
					pasted = self.imaging.toBytes(img)
					await self.bot.funcs.misc.handle_uploads(ctx,pasted,filename="wasted.png")
		except discord.errors.Forbidden as e:
			await self.funcs.command.handle_error(ctx,e)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['supersharpen'])
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.bot_has_permissions(attach_files=True)
	async def sharpenbomb(self,ctx,*urls):
		if not urls:
			urls = None
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx,urls=urls)
			if images:
				for url in images:
					b = await self.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					img = ImageEnhance.Sharpness(img).enhance(80)
					final = self.imaging.toBytes(img)
					await self.funcs.misc.handle_uploads(ctx,final,filename="sharpened.png")
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['sickening','thisissickening','max'])
	@commands.bot_has_permissions(attach_files=True)
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def maxmoefoe(self,ctx,*urls):
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx,urls=urls)
			if images:
				for url in images:
					b = await self.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					max = Image.open('resource/img/OISTOP.png').convert('RGBA')
					max.thumbnail((int(img.size[0]/1.5), int(img.size[1]/1.25)))
					pasted = self.imaging.paste(img,max,offset=(10,img.size[1]-max.size[1]),bytes=True)
					await self.bot.funcs.misc.handle_uploads(ctx,pasted,filename="OISTOP.png")
		except discord.errors.Forbidden as e:
			await self.funcs.command.handle_error(ctx,e)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['itstimetostop','franku'])
	@commands.bot_has_permissions(attach_files=True)
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def frank(self,ctx,*urls):
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx,urls=urls)
			if images:
				for url in images:
					b = await self.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					franku = Image.open('resource/img/frank'+str(randint(1,5))+'.png').convert('RGBA')
					franku.thumbnail((int(img.size[0]/1.5), int(img.size[1]/1.25)))
					pasted = self.imaging.paste(img,franku,offset=(img.size[0]-franku.size[0]-randint(10,img.size[0]/2),img.size[1]-franku.size[1]),bytes=True)
					await self.bot.funcs.misc.handle_uploads(ctx,pasted,filename="itstimetostop.png")
		except discord.errors.Forbidden as e:
			await self.funcs.command.handle_error(ctx,e)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['newfunky','funkymode','newfunkymode'])
	@commands.bot_has_permissions(attach_files=True)
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def funky(self,ctx,*urls):
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx,urls=urls)
			if images:
				for url in images:
					b = await self.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					nfm = Image.open('resource/img/newfunkymode.png').convert('RGBA')
					nfm.thumbnail((int(img.size[0]/1.2),int(img.size[1]/1.4)))
					pasted = self.imaging.paste(img,nfm,offset=(img.size[0]-nfm.size[0],0),bytes=True)
					await self.bot.funcs.misc.handle_uploads(ctx,pasted,filename="funky.png")
		except discord.errors.Forbidden as e:
			await self.funcs.command.handle_error(ctx,e)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['sonic3','knuckles'])
	@commands.bot_has_permissions(attach_files=True)
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def andknuckles(self,ctx,*urls):
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx,urls=urls)
			if images:
				for url in images:
					b = await self.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					ak = Image.open('resource/img/andknuckles.png').convert('RGBA')
					ak.thumbnail((int(img.size[0]/1.6),int(img.size[1]/1.8)))
					pasted = self.imaging.paste(img,ak,offset=(int((img.size[0]-ak.size[0])-img.size[0]*0.05),int((img.size[1]-ak.size[1])-img.size[1]*0.05)),bytes=True)
					await self.bot.funcs.misc.handle_uploads(ctx,pasted,filename="andknuckles.png")
		except discord.errors.Forbidden as e:
			await self.funcs.command.handle_error(ctx,e)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['guyfieri'])
	@commands.bot_has_permissions(attach_files=True)
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def fieri(self,ctx,*urls):
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx,urls=urls)
			if images:
				for url in images:
					b = await self.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					guy = Image.open('resource/img/feelmyfieri.png').convert('RGBA')
					guy.thumbnail((int(img.size[0]/2),int(img.size[1]/1.3)))
					pasted = self.imaging.paste(img,guy,offset=(int(img.size[0]-guy.size[0]),int(img.size[1]-guy.size[1])),bytes=True)
					await self.bot.funcs.misc.handle_uploads(ctx,pasted,filename="fieri.png")
		except discord.errors.Forbidden as e:
			await self.funcs.command.handle_error(ctx,e)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.bot_has_permissions(attach_files=True)
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def bandicam(self,ctx,*urls):
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx,urls=urls)
			if images:
				for url in images:
					b = await self.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					cam = Image.open('resource/img/bandicam.png').convert('RGBA')
					cam.thumbnail((int(img.size[0]/2),int(img.size[1]/1.2)))
					pasted = self.imaging.paste(img,cam,offset=(int(img.size[0]/2-cam.size[0]/2),0),bytes=True)
					await self.bot.funcs.misc.handle_uploads(ctx,pasted,filename="bandicam.png")
		except discord.errors.Forbidden as e:
			await self.funcs.command.handle_error(ctx,e)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['thankskanye'])
	@commands.bot_has_permissions(attach_files=True)
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def kanye(self,ctx,*urls):
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx,urls=urls)
			if images:
				for url in images:
					b = await self.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					img = img.resize((446,347))
					kanye = Image.open('resource/img/thankyoukanye.png').convert('RGBA')
					pasted = self.imaging.paste(kanye,img,offset=(27,216),bytes=True)
					await self.bot.funcs.misc.handle_uploads(ctx,pasted,filename="bandicam.png")
		except discord.errors.Forbidden as e:
			await self.funcs.command.handle_error(ctx,e)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.bot_has_permissions(attach_files=True)
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def hacker(self,ctx,*urls):
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx,urls=urls)
			if images:
				for url in images:
					b = await self.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					hacker = Image.open('resource/img/hacker.png').convert('RGBA')
					bg = Image.new('RGBA',hacker.size,'black')
					img = img.resize((290,240))
					coeffs = self.imaging.find_coeffs([(0,0),(276,0),(276,210),(0,210)],[(0,0),(276,0),(276,300),(0,210)])
					img = img.transform(img.size, Image.PERSPECTIVE, coeffs)
					bg.paste(img,(80,209),img)
					bg.paste(hacker,(0,0),hacker)
					pasted = self.imaging.toBytes(bg)
					await self.bot.funcs.misc.handle_uploads(ctx,pasted,filename="hacker.png")
		except discord.errors.Forbidden as e:
			await self.funcs.command.handle_error(ctx,e)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['trophy'])
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def participation(self,ctx,user:discord.Member):
		try:
			await ctx.trigger_typing()
			trophy = Image.open("resource/img/trophy.png").convert("RGBA")
			#text = 'Thanks for participating,\n' + user.display_name
			text = 'You deserve a trophy not just cause, but because you are an awesome person.'
			offset = [315,720]
			font = ImageFont.truetype("resource/font/GenBasR.ttf",28)
			d = ImageDraw.Draw(trophy)
			for line in self.imaging.text_wrap(text,font=font,max_pixels=295,wrap='word'):
				d.text(offset,line,font=font,fill="#000")
				offset[1] += font.getsize(line)[1]
			final = self.imaging.toBytes(trophy)
			await self.funcs.misc.handle_uploads(ctx,final,filename='trophy.png')
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	#Text Commands

	@commands.command(aliases=['compliment'])
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def wholesome(self,ctx,user:discord.Member=None):
		if user is None:
			user = ctx.message.author
		try:
			await ctx.trigger_typing()
			responses = self.data.datasets.get_wholesome_responses()
			response = responses[randint(0,len(responses)-1)]
			await ctx.send(user.mention + ' ' + response)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def insult(self,ctx,user:discord.Member=None):
		if user is None:
			user = ctx.message.author
		try:
			await ctx.trigger_typing()
			templates = self.data.datasets.get_insult_templates()
			template = templates[randint(0,len(templates)-1)]
			resp = await self.funcs.http.get('https://insult.mattbas.org/api/insult.json',params={'template':template},json=True)
			if resp:
				await ctx.send(user.mention + ' ' + resp['insult'])
				return
			await ctx.send(ctx.gresponses['generic_api_error'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(name='8ball',aliases=['eightball'])
	@commands.cooldown(1,3,commands.BucketType.user)
	async def eball(self,ctx,*,question:str):
		try:
			await ctx.trigger_typing()
			responses = self.data.datasets.get_8ball_responses()
			response = responses[randint(0,len(responses)-1)]
			await ctx.send(ctx.message.author.mention + ' ' + response)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['dad'])
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def dadjoke(self,ctx):
		try:
			await ctx.trigger_typing()
			resp = await self.funcs.http.get('https://icanhazdadjoke.com',headers={"Accept": "application/json"},json=True)
			if resp:
				await ctx.send(ctx.message.author.mention + ' ' + resp['joke'])
				return
			await ctx.send(ctx.gresponses['generic_api_error'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def reverse(self,ctx,text:str):
		try:
			await ctx.trigger_typing()
			await ctx.send(text[::-1])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def zalgo(self,ctx,*,text:str): #Based off of https://gist.github.com/MetroWind/1401473/4631da7a4540a63e72701792a4aa0262acc7d397
		try:
			await ctx.trigger_typing()
			CHAR_DOWN,CHAR_MID,CHAR_UP = self.data.datasets.get_zalgo_chars()
			ZALGO_POS = ("up","down","mid")
			ZALGO_CHARS = {"up":CHAR_UP,"mid":CHAR_MID,"down":CHAR_DOWN}
			result = []
			for char in text:
				ZalgoCounts = {"up": 0, "down": 0, "mid": 0}
				for pos in ZALGO_POS:
					ZalgoCounts[pos] = random.randint(0, 7)
				result.append(char)
				for pos in ZALGO_POS:
					c = random.sample(ZALGO_CHARS[pos],ZalgoCounts[pos])
					result.append(''.join(c))
			await ctx.send(''.join(result))
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(alises=['catpic'])
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def cat(self,ctx):
		try:
			await ctx.trigger_typing()
			resp = await self.funcs.http.get('http://thecatapi.com/api/images/get?format=xml&results_per_page=1')
			if resp:
				url = ET.fromstring(resp.decode('utf-8')).find('data').find('images').find('image').find('url').text
				await ctx.send(embed=self.funcs.misc.get_image_embed(url,url))
				return
			await ctx.send(ctx.gresponses['generic_api_error'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['dogpic'])
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def dog(self,ctx):
		try:
			await ctx.trigger_typing()
			resp = await self.funcs.http.get('https://api.thedogapi.com/v1/images/search',json=True)
			if resp:
				url = resp[0]['url']
				await ctx.send(embed=self.funcs.misc.get_image_embed(url,url))
				return
			await ctx.send(ctx.gresponses['generic_api_error'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=["decide"])
	@commands.cooldown(1,3,commands.BucketType.user)
	async def choose(self,ctx,*,choices:str):
		try:
			await ctx.trigger_typing()
			choices = choices.split('|')
			choice = choices[randint(0,len(choices)-1)]
			await ctx.send(ctx.cresponses['selection'].format(choice.rstrip()))
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def pp(self,ctx,user:discord.Member=None):
		try:
			text = " has"
			if not user:
				user = ctx.message.author
				text = ", you have"
			big = ('large','massive','very large','huge')
			small = ('small','tiny','no','micro')
			sizes = big if randint(0,1) == 1 else small
			emb = discord.Embed(title="PP Guesser 9000",type="rich",color=discord.Color.gold(),description=user.mention+text+" `"+random.sample(sizes,1)[0]+" pp`")
			await ctx.send(embed=emb)
		except Exception as e:
			await self.funcs.command.handle_Error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def gay(self,ctx,user:discord.Member=None):
		try:
			text = " has"
			if not user:
				user = ctx.message.author
				text = ", you have"
			num = str(randint(0,100)) if user.id != 166206078164402176 else "0"
			emb = discord.Embed(title="Gay Guesser 6900",type="rich",color=discord.Color.gold(),description=user.mention+text+" `"+num+"% gay`")
			await ctx.send(embed=emb)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def coin(self,ctx):
		try:
			await ctx.trigger_typing()
			responses = ('Heads','Tails')
			random.seed(randint(0,100000))
			await ctx.send(':cd: '+responses[randint(0,1)]+'!')
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def rps(self,ctx,weapon:str):
		weapon = weapon.lower()
		valid_weapons = ('rock','paper','scissors','r','p','s')
		weapons = ('rock','paper','scissors')
		emojis = {'rock':':fist:','paper':':newspaper:','scissors':':scissors:'}
		if not weapon in valid_weapons:
			await ctx.send(ctx.cresponses['invalid_input'])
			return
		translation = {'r':'rock','p':'paper','s':'scissors'}
		if len(weapon) == 1:
			weapon = translation[weapon]
		try:
			await ctx.trigger_typing()
			choice = weapons[randint(0,2)]
			msg_prefix = emojis[choice] + ' ' + choice.upper()
			if choice == weapon:
				await ctx.send(ctx.cresponses['draw'].format(msg_prefix))
			elif (choice == 'rock' and weapon == 'paper') or (choice == 'paper' and weapon == 'scissors') or (choice == 'scissors' and weapon == 'rock'):
				await ctx.send(ctx.cresponses['lost'].format(msg_prefix))
			elif (choice == 'rock' and weapon == 'scissors') or (choice == 'scissors' and weapon == 'paper') or (choice == 'scissors' and weapon == 'paper'):
				await ctx.send(ctx.cresponses['won'].format(msg_prefix))
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['dice'])
	@commands.cooldown(1,3,commands.BucketType.user)
	async def roll(self,ctx,sides:int=6,count:int=1):
		if sides <= 0:
			await ctx.send(ctx.cresponses['min'].format("least","1 side"))
			return
		if count <= 0:
			await ctx.send(ctx.cresponses['min_dice'].format(1))
			return
		if count > 10:
			await ctx.send(ctx.cresponses['max'].format(10))
			return
		if sides > 1000000000:
			await ctx.send(ctx.cresponses['max_sides'].format(1000000000))
			return
		try:
			await ctx.trigger_typing()
			rolls = []
			for d in range(count):
				rolls.append(str(randint(1,sides)))
			if count > 1:
				await ctx.send(ctx.cresponses['rolls'].format(', '.join(rolls)))
			else:
				await ctx.send(ctx.cresponses['single_roll'].format(', '.join(rolls)))
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def freesmiley(self,ctx):
		try:
			await ctx.trigger_typing()
			url = "http://bilder-lustige-bilder.de/images/{0}_lustige_smiley_bilder.jpg".format(randint(1,20))
			embed = self.funcs.misc.get_image_embed("http://free-smiley.de",url)
			await ctx.send(embed=embed)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def meme(self,ctx):
		try:
			await ctx.trigger_typing()
			r = reddit.Reddit()
			subreddits = ("dankmemes","meirl","wholesomememes")
			subreddit = subreddits[randint(0,len(subreddits)-1)]
			results = await r.search(q="",is_video="false",subreddit=subreddit,domain="i.redd.it,i.imgur.com",over_18="false")
			if len(results) <= 0:
				await ctx.send(ctx.cresponses['no_results'])
				return
			if results:
				num = randint(0,len(results)-1)
				result = results[num]
				embed = self.funcs.misc.get_image_embed(result.full_link,result.url)
				embed.set_footer(text="Posted by {0} on r/{1}.".format(result.author,result.subreddit))
				await ctx.send(embed=embed)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def badmeme(self,ctx):
		try:
			await ctx.trigger_typing()
			r = reddit.Reddit()
			subreddits = ("comedycemetery","comedynecrophilia")
			subreddit = subreddits[randint(0,len(subreddits)-1)]
			results = await r.search(q="",is_video="false",subreddit=subreddit,domain="i.redd.it,i.imgur.com",over_18="false")
			if len(results) <= 0:
				await ctx.send(ctx.cresponses['no_results'])
				return
			if results:
				num = randint(0,len(results)-1)
				result = results[num]
				embed = self.funcs.misc.get_image_embed(result.full_link,result.url)
				embed.set_footer(text="Posted by {0} on r/{1}.".format(result.author,result.subreddit))
				await ctx.send(embed=embed)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def iq(self,ctx,user:discord.User=None):
		if user is None:
			user = ctx.author
		try:
			rand = randint(0,300)
			if rand >= 230:
				resp = ctx.cresponses['over230']
			else:
				resp = ctx.cresponses['response']
			resp = resp.format(user,rand)
			embed = discord.Embed(title="IQ Counter",type="rich",color=discord.Color.purple(),description=resp)
			await ctx.send(embed=embed)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

def setup(bot):
	bot.add_cog(Fun(bot))
