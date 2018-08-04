import asyncio
import discord
from discord.ext import commands

from utils import checks

from PIL import Image

class Management():

	def __init__(self,bot):
		self.bot = bot
		self.funcs = self.bot.funcs
		self.data = self.bot.data


	@commands.group(invoke_without_command=True)
	@commands.guild_only()
	@commands.cooldown(1,10,commands.BucketType.guild)
	async def prefix(self,ctx,*,prefix:str=None): #Sets the server prefix, if no prefix is supplied, it fetches the server's prefix
		try:
			if not prefix: #If no prefix supplied, retrieve it
				prefix = self.data.DB.get_prefix(guild=ctx.guild)
				await ctx.send(ctx.cresponses['current_prefix'].format(prefix))
				return
			if prefix:
				can_execute = checks.is_admin_or_perm(ctx,manage_server=True)
				if can_execute:
					if self.data.DB.set_prefix(ctx.guild,prefix):
						await ctx.send(ctx.cresponses['set_prefix'].format(prefix))
					else:
						await ctx.send(ctx.cresponses['error'])
				else:
					raise checks.No_Admin()
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@prefix.command()
	@commands.guild_only()
	@commands.cooldown(1,10,commands.BucketType.guild)
	@checks.admin_or_perm(manage_server=True)
	async def reset(self,ctx):
		try:
			success = self.data.DB.set_prefix(ctx.guild,"$")
			if success:
				await ctx.send(ctx.cresponses['reset_prefix'])
			else:
				await ctx.send(ctx.cresponses['error'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.guild_only()
	@commands.cooldown(1,10,commands.BucketType.guild)
	@checks.admin_or_perm(manage_server=True)
	async def personality(self,ctx,personality:str=None):
		try:
			if not personality:
				personality = self.data.DB.get_personality(ctx.guild)
				if personality:
					await ctx.send(ctx.cresponses['current'].format(personality))
				else:
					await ctx.send(ctx.cresponses['error'])
			elif personality:
				personality = personality.lower()
				if not personality in self.bot.responses:
					personalities = []
					for p in self.bot.responses:
						personalities.append(p)
					await ctx.send(ctx.cresponses['invalid'].format(', '.join(personalities)))
					return
				success = self.data.DB.set_personality(ctx.guild,personality)
				if success:
					await ctx.send(ctx.cresponses['set'].format(personality))
				else:
					await ctx.send(ctx.cresponses['error'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['opt'],invoke_without_command=True)
	@commands.guild_only()
	@commands.cooldown(1,10,commands.BucketType.guild)
	@checks.admin_or_perm(manage_server=True)
	async def option(self,ctx,option:str,value:str=None):
		option = option.lower()
		options = ['nsfw_enabled','dad_mode']
		defaults = {'nsfw_enabled':'true','dad_mode':'false'}
		values = ('yes','y','no','n','false','true','on','off')
		if not option in options:
			await ctx.send(ctx.cresponses['invalid_option'].format(", ".join(options)))
			return
		if not value in values and not value is None:
			await ctx.send(ctx.cresponses['invalid_value'].format(", ".join(values)))
			return
		if value in ('yes','y','on'):
			value = 'true'
		elif value in ('no','n','off'):
			value = 'false'
		try:
			if value is None:
				val, success = self.data.DB.get_serveropt(ctx.guild,option,default=defaults[option],errors=True)
				if not success:
					await ctx.send(ctx.cresponses['error_retrieve'].format(option))
				else:
					await ctx.send(ctx.cresponses['current'].format(option,val))
			elif value:
				success = self.data.DB.set_serveropt(ctx.guild,option,value,default=defaults[option])
				if success:
					await ctx.send(ctx.cresponses['success'].format(option,value))
				else:
					await ctx.send(ctx.cresponses['error_set'].format(option))
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command(aliases=['nick'])
	@commands.guild_only()
	@commands.cooldown(1,10,commands.BucketType.guild)
	@checks.mod_or_perm(manage_nicknames=True)
	async def nickname(self,ctx,*,nickname:str=None):
		if nickname is None:
			nickname = ''
		try:
			if len(nickname) > 32:
				await ctx.send(ctx.cresponses['too_long'])
				return
			await ctx.guild.me.edit(nick=nickname)
			success = await ctx.send(ctx.cresponses['success'])
			await asyncio.sleep(5)
			await success.delete()
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

def setup(bot):
	bot.add_cog(Management(bot))
