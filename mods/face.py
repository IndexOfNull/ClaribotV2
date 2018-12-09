import discord
from discord.ext import commands

from utils import checks

from random import randint
import hashlib

from utils.api import msface

import datetime

from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageEnhance
from io import BytesIO

#We cannot use the Image proxy because the resized image values wouldn't match up with the values returned from the face API

class Face():

	def __init__(self,bot):
		self.bot = bot
		self.funcs = self.bot.funcs
		self.imaging = self.bot.imaging
		self.cursor = self.bot.mysql.cursor
		self.detector = msface.FaceDetector("9490a42f9a9849d5ba3bdec3dc261b25")
		self.get_images = self.funcs.misc.get_images
		self.bytes_download_images = self.funcs.misc.bytes_download_images

	@commands.command()
	async def facecrop(self,ctx,*urls):
		try:
			await ctx.trigger_typing()
			missing_faces = False
			max_res_err = False
			images = await self.get_images(ctx,urls=urls,limit=1)
			if images:
				for url in images:
					b = await self.bytes_download_images(ctx,url,images,False)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					if img.size > (2500,2500):
						max_res_err = True
						continue
					faces = await self.detector.detect(url)
					if not faces:
						missing_faces = True
						continue
					draw = ImageDraw.Draw(img)
					rect = faces[0]['faceRectangle']
					cropped = img.crop((rect['left'],rect['top'],rect['left']+rect['width'],rect['top']+rect['height']))
					if cropped.size < (img.size[0]/4,img.size[1]/4):
						cropped = cropped.resize((int(cropped.size[0]*2.5),int(cropped.size[1]*2.5)))
					final = BytesIO()
					cropped.save(final,"PNG")
					final.seek(0)
					await self.funcs.misc.handle_uploads(ctx,final,filename="test.png")
			if missing_faces:
				await ctx.send(ctx.gresponses['no_faces'])
			if max_res_err:
				await ctx.send(ctx.gresponses['generic_image_res'].format("below","2500x2500"))
		except discord.errors.Forbidden as e:
			await self.funcs.command.handle_error(ctx,e)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['dwi'])
	async def dealwithit(self,ctx,*urls):
		try:
			await ctx.trigger_typing()
			missing_faces = False
			max_res_err = False
			images = await self.get_images(ctx,urls=urls,limit=1)
			if images:
				for url in images:
					b = await self.bytes_download_images(ctx,url,images,False)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					if img.size > (2500,2500):
						max_res_err = True
						continue
					faces = await self.detector.detect(url)
					if not faces:
						missing_faces = True
						continue
					glasses = Image.open("resource/img/dealwithit.png").convert("RGBA")
					for face in faces:
						landmarks = face['faceLandmarks']
						attributes = face['faceAttributes']
						print("{0}".format(attributes['headPose']))
						mirrored = False
						if attributes['headPose']['yaw'] < -2:
							glasses = ImageOps.mirror(glasses)
							mirrored = True
						glasses.thumbnail((int(face['faceRectangle']['width']+50),int(face['faceRectangle']['height']+50)))
						gw, gh = glasses.size
						if mirrored:
							glasses = glasses.rotate(int(attributes['headPose']['roll']*-1),expand=True,center=(gw*0.44,gh*0.21))
						else:
							glasses = glasses.rotate(int(attributes['headPose']['roll']*-1),expand=True,center=(gw*0.66,gh*0.21))
						grw, grh = glasses.size
						wdiff, hdiff = (grw-gw,grh-gh)
						print(wdiff,hdiff)
						#print(int(landmarks['eyeLeftOuter']['x']-gw/1.5))
						r = Image.new("RGBA",(1,1),"red")
						noseX = (landmarks['noseRootLeft']['x']+landmarks['noseRootRight']['x'])/2
						noseY = (landmarks['noseRootLeft']['y']+landmarks['noseRootRight']['y'])/2
						if mirrored:
							glassesBridge = (int((grw+wdiff/2)*0.335), int((grh+hdiff/2)*0.60))
						else:
							glassesBridge = (int((grw+wdiff/2)*0.665), int((grh+hdiff/2)*0.34))

						#glasses.paste(r,glassesBridge,r)
						img.paste(glasses,(int(noseX-glassesBridge[0]),int((noseY-grh)+glassesBridge[1])),glasses)
						#img.paste(r,(int(noseX),int(noseY)),r)
						#img = glasses
						#img.paste(glasses,(int((noseX-(grw-wdiff/2)/1.55)),int((noseY-(grh-hdiff/2.2)/2))),glasses)
						#img.paste(glasses,(int((landmarks['noseRootLeft']['x']-gw/3)-wdiff),int((landmarks['noseRootLeft']['y']-gh/3)-hdiff)),glasses)
					final = self.imaging.toBytes(img)
					await ctx.send(file=discord.File(final,"dealwithit.png"))
			if missing_faces:
				await ctx.send(ctx.gresponses['no_faces'])
			if max_res_err:
				await ctx.send(ctx.gresponses['generic_image_res'].format("below","2500x2500"))
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

def setup(bot):
	bot.add_cog(Face(bot))
