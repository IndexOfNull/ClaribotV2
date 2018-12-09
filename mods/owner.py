import asyncio
import discord
from discord.ext import commands
import datetime

from utils import checks

class Owner():

	def __init__(self,bot):
		self.bot = bot
		self.funcs = self.bot.funcs
		self.data = self.bot.data
		self.cursor = self.bot.mysql.cursor

	@commands.command()
	@checks.AdvChecks.is_bot_owner()
	@commands.cooldown(1,5)
	async def eval(self,ctx,*,code:str):
		code = code.strip('` ')
		python = '```py\n{}\n```'
		result = None
		variables = {
			'bot': self.bot,
			'ctx': ctx,
			'message': ctx.message,
			'server': ctx.message.guild,
			'channel': ctx.message.channel,
			'author': ctx.message.author
		}
		try:
			result = eval(code, variables)
		except Exception as e:
			await ctx.send(python.format(type(e).__name__ + ': ' + str(e)))
			return
		if asyncio.iscoroutine(result):
			result = await result
		#"```markdown\nUSE THIS WITH EXTREME CAUTION\n\nEval() Results\n=========\n\n> " + python.format(result)) + "\n```"
		await ctx.send(python.format(result))

	@commands.command()
	@checks.AdvChecks.is_bot_owner()
	@commands.cooldown(1,30)
	async def botavatar(self,ctx,*urls):
		if not urls:
			urls = None
		try:
			image = await self.funcs.misc.get_images(ctx, urls=urls, limit=1)
			if image:
				bytes = await self.funcs.misc.bytes_download(image[0])
				await self.bot.user.edit(avatar=bytes.read())
				await ctx.send(":white_check_mark: My avatar has been updated successfully!")
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@checks.AdvChecks.is_bot_owner()
	@commands.cooldown(1,5)
	async def playing(self,ctx,*,message:str):
		try:
			await self.bot.change_presence(activity=discord.Game(name=message))
			success = self.data.DB.set_bot_setting('playing',message)
			if success:
				await ctx.send(':white_check_mark: My playing status has been updated successfully!')
			else:
				await ctx.send(ctx.gresponses['generic_database_error'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.group(invoke_without_command=True)
	@checks.AdvChecks.is_bot_owner()
	@commands.cooldown(1,3)
	async def special(self,ctx,user:discord.User):
		try:
			special = self.data.DB.get_user_special(user)
			await ctx.send((":sparkles:" if special else ":thumbsdown:") + " ***{0.name}#{0.discriminator}*** ".format(user) + ("has" if special else "does not have") + " SpecialBot perms.")
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@special.command(aliases=['users'])
	@checks.AdvChecks.is_bot_owner()
	@commands.cooldown(1,3)
	async def list(self,ctx):
		try:
			users = self.data.DB.get_special_users()
			str = "```md\nSpecialBot Users\n--------------------\n{0}\n\n```"
			str2 = "+ {0.name}#{0.discriminator} ({0.id})\n"
			final = ""
			if users or len(users) == 0:
				if len(users) == 0:
					final = "None"
				else:
					for user in users:
						if isinstance(user, discord.User):
							final += str2.format(user)
						elif isinstance(user, int):
							final += "+ Unknown User ({0})".format(user)
						else:
							final += "+ Unknown User".format(user)
				await ctx.send(str.format(final))
			else:
				if users is False:
					await ctx.send(":fire: Something went wrong while getting SpecialBot users.")
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@special.command(aliases=['give'])
	@checks.AdvChecks.is_bot_owner()
	@commands.cooldown(1,3)
	async def add(self,ctx,user:discord.User):
		try:
			success = self.data.DB.add_special_user(user)
			if success:
				await ctx.send(":sparkles: I successfully gave ***{0.name}#{0.discriminator}*** SpecialBot perms.".format(user))
			else:
				await ctx.send(":fire: There was a problem giving that user SpecialBot perms.")
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@special.command(aliases=['delete'])
	@checks.AdvChecks.is_bot_owner()
	@commands.cooldown(1,3)
	async def remove(self,ctx,user:discord.User):
		try:
			success = self.data.DB.remove_special_user(user)
			if success:
				await ctx.send(":door: ***{0.name}#{0.discriminator}*** has been stripped of their SpecialBot permissions".format(user))
			else:
				await ctx.send(":fire: There was a problem revoking that user's SpecialBot perms.")
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3)
	@checks.AdvChecks.is_bot_owner()
	async def complaints(self,ctx,count:int=10,id:str=None):
		try:
			msgs = self.data.DB.get_user_messages(count=count,id=id,type='complaint')
			def get_embed(uid,sid,msg,id,ts):
				embed = discord.Embed(type="rich",title="User Complaint",color=discord.Color.purple())
				embed.add_field(name="From",value="<@"+str(uid)+">",inline=True)
				embed.add_field(name="Server",value=str(sid),inline=True)
				embed.add_field(name="Message",value="`{0}`".format(msg),inline=False)
				embed.add_field(name="ID",value="`{0}`".format(id),inline=True)
				embed.timestamp =  datetime.datetime.utcfromtimestamp(ts)
				return embed
			ids = []
			if not msgs:
				await ctx.send(ctx.cresponses['none'])
				return
			for msg in msgs:
				embed = get_embed(msg['user_id'],msg['server_id'],msg['message'],msg['id'],msg['timestamp'])
				ids.append(msg['id'])
				await ctx.send(embed=embed)
			self.data.DB.set_user_message_read(ids,1)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,3)
	@checks.AdvChecks.is_bot_owner()
	async def suggestions(self,ctx,count:int=10,id:str=None):
		try:
			msgs = self.data.DB.get_user_messages(count=count,id=id)
			def get_embed(uid,sid,msg,id,ts):
				embed = discord.Embed(type="rich",title="User Suggestion",color=discord.Color.purple())
				embed.add_field(name="From",value="<@"+str(uid)+">",inline=True)
				embed.add_field(name="Server",value=str(sid),inline=True)
				embed.add_field(name="Message",value="`{0}`".format(msg),inline=False)
				embed.add_field(name="ID",value="`{0}`".format(id),inline=True)
				embed.timestamp =  datetime.datetime.utcfromtimestamp(ts)
				return embed
			ids = []
			if not msgs:
				await ctx.send(ctx.cresponses['none'])
				return
			for msg in msgs:
				embed = get_embed(msg['user_id'],msg['server_id'],msg['message'],msg['id'],msg['timestamp'])
				ids.append(msg['id'])
				await ctx.send(embed=embed)
			self.data.DB.set_user_message_read(ids,1)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,10)
	@checks.AdvChecks.is_bot_owner()
	async def fatokens(self,ctx,a:str,b:str):
		try:
			token = a + ";" + b
			if a.lower() == "n" and b.lower() == "n":
				token = ""
			r = self.data.DB.set_bot_setting('fatokens',token)
			if r:
				self.bot.fatokens = (a,b)
				await ctx.send(":white_check_mark: My FA tokens have been successfully updated")
			else:
				await ctx.send(ctx.gresponses['generic_database_error'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

def setup(bot):
	bot.add_cog(Owner(bot))
