import asyncio
import discord
from discord.ext import commands
from PIL import Image, ImageFont, ImageOps, ImageDraw, ImageFilter, ImageEnhance

from random import randint

from utils import checks

class ImageCMD():

	def __init__(self,bot):
		self.bot = bot
		self.funcs = self.bot.funcs
		self.imaging = self.bot.imaging
		self.get_images = self.funcs.misc.get_images
		self.bytes_download_images = self.funcs.misc.bytes_download_images

	@commands.command(aliases=['greyscale'])
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.bot_has_permissions(attach_files=True)
	async def grayscale(self,ctx,*urls):
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
					img = ImageOps.grayscale(img)
					final = self.imaging.toBytes(img)
					await self.funcs.misc.handle_uploads(ctx,final,filename="mirrored.png")
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	"""@commands.command()
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.bot_has_permissions(attach_files=True)
	async def preprocess(self,ctx,*urls):
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
					final = self.imaging.toBytes(img)
					await self.funcs.misc.handle_uploads(ctx,final,filename="processed.png")
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)"""

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.bot_has_permissions(attach_files=True)
	async def flip(self,ctx,*urls):
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
					img = ImageOps.flip(img)
					final = self.imaging.toBytes(img)
					await self.funcs.misc.handle_uploads(ctx,final,filename="flipped.png")
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.bot_has_permissions(attach_files=True)
	async def mirror(self,ctx,*urls):
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
					img = ImageOps.mirror(img)
					final = self.imaging.toBytes(img)
					await self.funcs.misc.handle_uploads(ctx,final,filename="mirrored.png")
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.bot_has_permissions(attach_files=True)
	async def rotate(self,ctx,*urls):
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
					img = img.rotate(90,expand=True)
					final = self.imaging.toBytes(img)
					await self.funcs.misc.handle_uploads(ctx,final,filename="rotated.png")
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.bot_has_permissions(attach_files=True)
	async def sharpen(self,ctx,*urls):
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
					img = ImageEnhance.Sharpness(img).enhance(4)
					final = self.imaging.toBytes(img)
					await self.funcs.misc.handle_uploads(ctx,final,filename="sharpened.png")
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.bot_has_permissions(attach_files=True)
	async def blur(self,ctx,*urls):
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
					img = ImageEnhance.Sharpness(img).enhance(-2)
					final = self.imaging.toBytes(img)
					await self.funcs.misc.handle_uploads(ctx,final,filename="blurred.png")
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.bot_has_permissions(attach_files=True)
	async def posterize(self,ctx,*urls):
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
					r,g,b,a = img.split()
					img = img.convert("RGB")
					img = ImageOps.posterize(img,1)
					r,g,b = img.split()
					img = Image.merge("RGBA",(r,g,b,a))
					final = self.imaging.toBytes(img)
					await self.funcs.misc.handle_uploads(ctx,final,filename="posterized.png")
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.bot_has_permissions(attach_files=True)
	async def solarize(self,ctx,*urls):
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
					r,g,b,a=img.split()
					img = img.convert("RGB")
					img = ImageOps.solarize(img,threshold=randint(100,200))
					r,g,b = img.split()
					img = Image.merge("RGBA",(r,g,b,a))
					final = self.imaging.toBytes(img)
					await self.funcs.misc.handle_uploads(ctx,final,filename="solarized.png")
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.bot_has_permissions(attach_files=True)
	async def invert(self,ctx,*urls):
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
					r,g,b,a = img.split()
					def invert(image):
						return image.point(lambda p: 255 - p)
					r,g,b = map(invert,(r,g,b))
					img = Image.merge(img.mode,(r,g,b,a))
					final = self.imaging.toBytes(img)
					await self.funcs.misc.handle_uploads(ctx,final,filename="inverted.png")
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,20,commands.BucketType.guild)
	@commands.bot_has_permissions(attach_files=True)
	@checks.AdvChecks.is_special()
	async def vsplit(self,ctx,segments:int,*urls):
		if segments > 5:
			await ctx.send(ctx.cresponses['limit'].format(5))
			return
		if not urls:
			urls = None
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx,urls=urls,limit=1)
			if images:
				for url in images:
					b = await self.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b)
					w, h = img.size
					seg_height = h / segments
					final_height = seg_height
					if seg_height % 1 != 0:
						seg_height = int(seg_height)
						final_height = seg_height + 1
					imgs = []
					cury = 0
					for i in range(segments):
						tup = (0,cury,w,int(cury+seg_height))
						if i+1 == segments:
							tup = (0,int(cury),w,int(cury+final_height))
						cury += seg_height
						cropped = img.crop(tup)
						imgs.append(discord.File(self.imaging.toBytes(cropped),"split{0}.png".format(i+1)))
					#await asyncio.wait([ctx.send(file=i) for i in imgs])
					await ctx.send(files=imgs)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.bot_has_permissions(attach_files=True)
	async def palette(self,ctx,*urls): #Special thanks to makkoncept and his colorpalette repo on GitHub, check it out.
		numcolors = 8
		if not urls:
			urls = None
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx,urls=urls,limit=1)
			if images:
				for url in images:
					b = await self.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					small = img.resize((80,80))
					result = small.convert("P",palette=Image.ADAPTIVE,colors=numcolors)
					result.putalpha(0)
					colors = result.getcolors(80*80)

					#Draw rectangles
					w,h = img.size
					swatchwidth = int(w/numcolors)
					swatchheight = int(min(swatchwidth*2,h/3))
					final = Image.new("RGBA",(w,int(h+swatchheight)))
					margin = 3
					canvas = Image.new("RGBA",(w,swatchheight))
					palette_height = canvas.size[1]
					draw = ImageDraw.Draw(canvas)
					posx = 0
					for count, color in colors:
						draw.rectangle([posx+margin, 0, posx + swatchwidth - margin, palette_height], fill=color[:3])
						posx = posx + swatchwidth
					final.paste(img,(0,0),img)
					final.paste(canvas,(0,h),canvas)
					final = self.imaging.toBytes(final)
					await self.funcs.misc.handle_uploads(ctx,final,filename="palette.png")
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

def setup(bot):
	bot.add_cog(ImageCMD(bot))
