from PIL import Image
from io import BytesIO
import numpy

class ImageManip():

	def __init__(self):
	  pass

	def paste(self,baseimg,overlay,**kwargs):
		offset = kwargs.pop("offset",(0,0))
		scale = kwargs.pop("resize",None)
		resample = kwargs.pop("resample",Image.BICUBIC)
		thumbnail = kwargs.pop("thumbnail",None)
		returnbytes = kwargs.pop('bytes',False)
		if scale:
			overlay = overlay.resize(scale,resample=resample)
		elif thumbnail:
			overlay.thumbnail(thumbnail)
		baseimg.paste(overlay,offset,overlay)
		if returnbytes:
			return self.toBytes(baseimg)
		else:
			return baseimg

	def find_coeffs(self, pa, pb): #https://stackoverflow.com/questions/14177744/how-does-perspective-transformation-work-in-pil, thanks mmgp
		matrix = []
		for p1, p2 in zip(pa, pb):
			matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
			matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])

		A = numpy.matrix(matrix, dtype=numpy.float)
		B = numpy.array(pb).reshape(8)

		res = numpy.dot(numpy.linalg.inv(A.T * A) * A.T, B)
		return numpy.array(res).reshape(8)

	def text_wrap(self,text,**kwargs): #Wrap text, break by word or letter
		font = kwargs.pop('font')
		count_width = kwargs.pop('width',None)
		max_pixels = kwargs.pop('max_pixels',None)
		br = kwargs.pop('wrap',None)
		if not count_width and not max_pixels:
			return text
		lines = []
		cur_len = 0
		cur_text = ''
		for i,char in enumerate(text):
			if char == "\n":
				lines.append(cur_text)
				cur_len = 0
				cur_text = ''
				continue
			cur_text += char
			cur_len = font.getsize(cur_text)[0]
			next_len = font.getsize(cur_text + text[i])[0]
			if next_len > max_pixels:
				if br == 'letter' or br is None:
					lines.append(cur_text)
					cur_len = 0
					cur_text = ''
				elif br == 'word':
					lastword = cur_text.split(' ')
					if len(lastword) == 1:
						lines.append(cur_text)
						cur_len = 0
						cur_text = ''
					else:
						lines.append(' '.join(lastword[:-1]))
						cur_text = lastword[-1:][0]
						cur_len = font.getsize(cur_text)[0]
		lines.append(cur_text)
		return lines

	def aware_resize(self,img,size,resample=Image.BICUBIC): #Aspect aware image resizing
		x, y = size #Get the current size
		if x > size[0]:
			print("BEFORE AWARE_SCALE X:",x,y)
			y = int(max(y * size[0] / x, 1))
			x = int(size[0])
			print("AFTER AWARE_SCALE X:",x,y)
		if y > size[1]:
			print("BEFORE AWARE_SCALE Y:",x,y)
			x = int(max(x * size[1] / y, 1))
			y = int(size[1])
			print("AFTER AWARE_SCALE Y:",x,y)
		size = x, y
		im = img.resize(size,resample)
		return im


	def toBytes(self,img,type="png",**kwargs):
		final = BytesIO()
		img.save(final,"png",**kwargs)
		final.seek(0)
		return final

	def preprocess_image_bytes(self,bytes,rimg=False):
		img = Image.open(bytes)
		if img.size > (2500,2500):
			if hasattr(img, '_getexif'):
				exif = img._getexif()
				if exif is not None:
					orientation = exif[0x0112]
					rotations = {
						3: Image.ROTATE_180,
						6: Image.ROTATE_270,
						8: Image.ROTATE_90
					}
					if orientation in rotations:
						img = img.transpose(rotations[orientation])
			img.thumbnail((2000,2000))
		if not rimg:
			b = self.toBytes(img,img.format)
			return b
		else:
			return img

	def image_open_proxy(self,bytes):
		img = self.preprocess_image_bytes(bytes,True)
		return img
