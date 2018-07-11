import discord
from discord.ext import commands
from PIL import Image, ImageFont, ImageOps, ImageDraw, ImageFilter, ImageEnhance

from random import randint

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



def setup(bot):
	bot.add_cog(ImageCMD(bot))
