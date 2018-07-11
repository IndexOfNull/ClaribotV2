import asyncio
import discord
from discord.ext import commands
import datetime

from utils import checks

class Admin():

	def __init__(self,bot):
		self.bot = bot
		self.funcs = self.bot.funcs
		self.data = self.bot.data
		self.prune_limit = 200

	@commands.command(aliases=['hackban'])
	@commands.cooldown(1,10,commands.BucketType.guild)
	@commands.guild_only()
	@checks.admin_or_perm(ban_members=True)
	@commands.bot_has_permissions(ban_members=True)
	async def idban(self,ctx,id:int):
		try:
			confirmed = await self.funcs.command.confirm_command(ctx,target='User ({0})'.format(id))
			if not confirmed:
				return
			await ctx.trigger_typing()
			try:
				await ctx.guild.ban(discord.Object(id=id),delete_message_days=0,reason="ID-Banned by {0.name}#{0.discriminator}".format(ctx.author))
			except:
				await ctx.send(ctx.cresponses['no_user'])
				return
			await ctx.send(ctx.cresponses['success'].format("<@{0}>".format(id)))
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)


	@commands.group()
	@commands.cooldown(1,5,commands.BucketType.guild)
	@commands.guild_only()
	@checks.admin_or_perm(manage_server=True)
	async def blacklist(self,ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send("Valid subcommands are `list, user, channel, command`")
			ctx.command.reset_cooldown(ctx)

	@blacklist.command()
	@commands.cooldown(1,5,commands.BucketType.guild)
	@commands.guild_only()
	@checks.admin_or_perm(manage_server=True)
	async def command(self,ctx,command:str):
		command = self.bot.get_command(command)
		if not command:
			await ctx.send(ctx.cresponses['invalid_command'])
			return
		try:
			await ctx.trigger_typing()
			success = self.data.DB.toggle_command(ctx.guild,command)
			if success:
				await ctx.send(ctx.cresponses['command_toggled'])
			else:
				await ctx.send(ctx.cresponses['toggle_error'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@blacklist.command()
	@commands.cooldown(1,5,commands.BucketType.guild)
	@commands.guild_only()
	@checks.admin_or_perm(manage_server=True)
	async def user(self,ctx,user:discord.Member):
		try:
			await ctx.trigger_typing()
			success = self.data.DB.toggle_user(ctx.guild,user)
			if success:
				await ctx.send(ctx.cresponses['user_toggled'])
			else:
				await ctx.send(ctx.cresponses['toggle_error'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@blacklist.command()
	@commands.cooldown(1,5,commands.BucketType.guild)
	@commands.guild_only()
	@checks.admin_or_perm(manage_server=True)
	async def channel(self,ctx,channel:discord.TextChannel=None):
		try:
			await ctx.trigger_typing()
			if not channel:
				channel = ctx.channel
			success = self.data.DB.toggle_channel(ctx.guild,channel)
			if success:
				await ctx.send(ctx.cresponses['channel_toggled'])
			else:
				await ctx.send(ctx.cresponses['toggle_error'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@blacklist.command()
	@commands.cooldown(1,5,commands.BucketType.guild)
	@commands.guild_only()
	@checks.admin_or_perm(manage_server=True)
	async def list(self,ctx):
		try:
			await ctx.trigger_typing()
			mstr = "```md\nBlacklisted Channels\n--------------------\n{0}\nBlacklisted Commands\n--------------------\n{1}\nBlacklisted Users\n--------------------\n{2}\n```"
			channels_str2 = "- #{0.name}\n"
			users_str2 = "- {0.name}#{0.discriminator}\n"
			commands_str2 = "- {0.name}\n"
			channels_str = users_str = commands_str = ""
			blacklist = self.data.DB.get_blacklist(ctx.guild)
			if not blacklist['channels']:
				channels_str = 'None\n'
			if not blacklist['commands']:
				commands_str = 'None\n'
			if not blacklist['users']:
				users_str = 'None\n'
			for channel in blacklist['channels']:
				channels_str+=channels_str2.format(channel)
			for command in blacklist['commands']:
				commands_str+=commands_str2.format(command)
			for user in blacklist['users']:
				users_str+=users_str2.format(user)
			mstr = mstr.format(channels_str,commands_str,users_str)
			await ctx.send(mstr)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,10,commands.BucketType.guild)
	@checks.mod_or_perm(manage_messages=True)
	async def warn(self,ctx,user:discord.Member,*,reason:str):
		try:
			await ctx.trigger_typing()
			confirmed = await self.funcs.command.confirm_command(ctx,target=user)
			if not confirmed:
				return
			success = self.data.DB.add_warning(user=user,guild=ctx.guild,warner=ctx.author,reason=reason,return_data=True)
			if success:
				embed = self.funcs.misc.get_warning_embed(user=user.id,warner=ctx.author.id,guild=ctx.guild,reason=reason,timestamp=success['timestamp'],id=success['id'])
				await user.send(embed=embed)
				await ctx.send(ctx.cresponses['success'].format(user))
			else:
				await ctx.send(ctx.cresponses['error'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.group(invoke_without_command=True)
	@commands.cooldown(1,10,commands.BucketType.guild)
	@commands.guild_only()
	@checks.mod_or_perm(manage_messages=True)
	async def warning(self,ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send("Valid subcommands are `get, delete, history`")

	@warning.command()
	@commands.cooldown(1,10,commands.BucketType.guild)
	@commands.guild_only()
	@checks.mod_or_perm(manage_messages=True)
	async def get(self,ctx,id:str):
		try:
			await ctx.trigger_typing()
			warning = self.data.DB.get_warning(guild=ctx.guild,warning_id=id)
			if warning:
				embed = self.funcs.misc.get_warning_embed(user=warning['user_id'],warner=warning['warner'],guild=ctx.guild,reason=warning['reason'],timestamp=warning['timestamp'],id=warning['issue_id'])
				embed.set_footer(text="This is a warning for another user, and was retrieved by its warning id")
				await ctx.author.send(embed=embed)
				await ctx.send(ctx.cresponses['get_success'].format(warning['issue_id']))
			else:
				if isinstance(warning,list):
					await ctx.send(ctx.cresponses['invalid_id'])
					return
				await ctx.send(ctx.gresponses['generic_database_error'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@warning.command(aliases=['remove','del'])
	@commands.cooldown(1,10,commands.BucketType.guild)
	@commands.guild_only()
	@checks.mod_or_perm(mange_messages=True)
	async def delete(self,ctx,id:str):
		try:
			await ctx.trigger_typing()
			exists = self.data.DB.get_warning(guild=ctx.guild,warning_id=id)
			if not exists:
				await ctx.send(ctx.cresponses['invalid_id'])
				return
			confirmed = await self.funcs.command.confirm_command(ctx,target=id)
			if not confirmed:
				return
			success = self.data.DB.del_warning(guild=ctx.guild,id=id)
			if success:
				await ctx.send(ctx.cresponses['del_success'])
			else:
				await ctx.send(ctx.cresponses['del_error'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@warning.command()
	@commands.cooldown(1,10,commands.BucketType.guild)
	@commands.guild_only()
	@checks.mod_or_perm(manage_messages=True)
	async def list(self,ctx,user:discord.Member):
		try:
			await ctx.trigger_typing()
			msg = "```fix\nWarning List For {0.name}#{0.discriminator}\n========================================\n{1}\n```"
			msg2 = ""
			warnings,otherwarnings = self.data.DB.get_user_warnings(ctx.guild,user,others=True)
			limit = 30
			for i,warning in enumerate(warnings):
				if i > limit:
					break
				timestamp = self.funcs.time.seconds_to_utc(warning['timestamp'])
				msg2 += "[{0}] {1} | {2}\n".format(i+1,warning['issue_id'],self.funcs.time.get_formatted_time(timestamp))
			if len(warnings) == 0:
				msg2 += "No warnings to report\n\n"
			if otherwarnings:
				msg2 += "========================================\n{0}You can view more information about these warnings with $warning get <id>".format("! This user has warnings from other servers on record !\n\n")
			else:
				msg2 += "========================================\nYou can view more information about warnings with $warning get <id>"
			msg = msg.format(user,msg2)
			await ctx.author.send(msg)
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)



	@commands.group(invoke_without_command=True)
	@commands.cooldown(1,10,commands.BucketType.guild)
	@commands.guild_only()
	@commands.bot_has_permissions(manage_messages=True)
	@checks.mod_or_perm(manage_messages=True)
	async def prune(self,ctx,max_messages:int=None,user:discord.User=None):
		if ctx.invoked_subcommand is None and max_messages is None:
			await ctx.send('Valid subcommands are `bots, attachments, embeds, images, with`')
			return
		if max_messages > self.prune_limit:
			await ctx.send(ctx.gresponses['generic_limit'].format("less",str(self.prune_limit)+" messages"))
			return
		try:
			await ctx.trigger_typing()
			history = ctx.message.channel.history(limit=max_messages,before=ctx.message)
			if user:
				history = history.filter(lambda m: m.author == user)
			num = 0
			async for msg in history:
				await msg.delete()
				num+=1
			if num > 0:
				if user:
					await ctx.send(ctx.cresponses['by_success'].format(num,user.name+"#"+user.discriminator))
				else:
					await ctx.send(ctx.cresponses['generic_success'].format(num))
			else:
				await ctx.send(ctx.cresponses['none_pruned'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@commands.command()
	@commands.cooldown(1,10,commands.BucketType.guild)
	@commands.guild_only()
	@checks.mod_or_perm(manage_messages=True)
	async def clean(self,ctx,max_messages:int):
		if max_messages > self.prune_limit:
			await ctx.send(ctx.gresponses['generic_limit'].format("less",str(self.prune_limit)+" messages"))
			return
		try:
			await ctx.trigger_typing()
			history = ctx.message.channel.history(limit=max_messages,before=ctx.message)
			history = history.filter(lambda m: m.author == self.bot.user)
			num = 0
			async for msg in history:
				await msg.delete()
				num+=1
			if num > 0:
				await ctx.send(ctx.cresponses['generic_success'].format(num))
			else:
				await ctx.send(ctx.cresponses['none_pruned'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@prune.command(name="with")
	@commands.cooldown(1,10,commands.BucketType.guild)
	@commands.guild_only()
	@commands.bot_has_permissions(manage_messages=True)
	@checks.mod_or_perm(manage_messages=True)
	async def prune_with(self,ctx,max_messages:int,*,text:str):
		if max_messages > self.prune_limit:
			await ctx.send(ctx.gresponses['generic_limit'].format("less",str(self.prune_limit)+" messages"))
			return
		try:
			await ctx.trigger_typing()
			history = ctx.message.channel.history(limit=max_messages,before=ctx.message)
			history = history.filter(lambda m: text in m.content.lower())
			num = 0
			async for msg in history:
				await msg.delete()
				num+=1
			if num > 0:
				await ctx.send(ctx.cresponses['with_success'].format(num,'`{0}`'.format(text)))
			else:
				await ctx.send(ctx.cresponses['none_pruned'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@prune.command()
	@commands.cooldown(1,10,commands.BucketType.guild)
	@commands.guild_only()
	@commands.bot_has_permissions(manage_messages=True)
	@checks.mod_or_perm(manage_messages=True)
	async def bots(self,ctx,max_messages:int):
		if max_messages > self.prune_limit:
			await ctx.send(ctx.gresponses['generic_limit'].format("less",str(self.prune_limit)+" messages"))
			return
		try:
			await ctx.trigger_typing()
			history = ctx.message.channel.history(limit=max_messages,before=ctx.message)
			history = history.filter(lambda m: m.author.bot is True)
			num = 0
			async for msg in history:
				await msg.delete()
				num+=1
			if num > 0:
				await ctx.send(ctx.cresponses['by_success'].format(num,"bots"))
			else:
				await ctx.send(ctx.cresponses['none_pruned'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@prune.command()
	@commands.cooldown(1,10,commands.BucketType.guild)
	@commands.guild_only()
	@commands.bot_has_permissions(manage_messages=True)
	@checks.mod_or_perm(manage_messages=True)
	async def gifs(self,ctx,max_messages:int):
		if max_messages > self.prune_limit:
			await ctx.send(ctx.gresponses['generic_limit'].format("less",str(self.prune_limit)+" messages"))
			return
		try:
			await ctx.trigger_typing()
			async def check(msg):
				for attachment in msg.attachments:
					has_image = ((await self.funcs.misc.get_image_mime(attachment.url,type=True)) == "gif")
					if has_image: return True
			history = ctx.message.channel.history(limit=max_messages,before=ctx.message)
			history = history.filter(check)
			num = 0
			async for msg in history:
				await msg.delete()
				num+=1
			if num > 0:
				await ctx.send(ctx.cresponses['with_success'].format(num,"gifs"))
			else:
				await ctx.send(ctx.cresponses['none_pruned'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@prune.command()
	@commands.cooldown(1,10,commands.BucketType.guild)
	@commands.guild_only()
	@commands.bot_has_permissions(manage_messages=True)
	@checks.mod_or_perm(manage_messages=True)
	async def images(self,ctx,max_messages:int):
		if max_messages > self.prune_limit:
			await ctx.send(ctx.gresponses['generic_limit'].format("less",str(self.prune_limit)+" messages"))
			return
		try:
			await ctx.trigger_typing()
			async def check(msg):
				for attachment in msg.attachments:
					has_image = ((await self.funcs.misc.get_image_mime(attachment.url,type=True)) == "image")
					if has_image: return True
			history = ctx.message.channel.history(limit=max_messages,before=ctx.message)
			history = history.filter(check)
			num = 0
			async for msg in history:
				await msg.delete()
				num+=1
			if num > 0:
				await ctx.send(ctx.cresponses['with_success'].format(num,"images"))
			else:
				await ctx.send(ctx.cresponses['none_pruned'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@prune.command()
	@commands.cooldown(1,10,commands.BucketType.guild)
	@commands.guild_only()
	@commands.bot_has_permissions(manage_messages=True)
	@checks.mod_or_perm(manage_messages=True)
	async def embeds(self,ctx,max_messages:int):
		if max_messages > self.prune_limit:
			await ctx.send(ctx.gresponses['generic_limit'].format("less",str(self.prune_limit)+" messages"))
			return
		try:
			await ctx.trigger_typing()
			history = ctx.message.channel.history(limit=max_messages,before=ctx.message)
			history = history.filter(lambda m: len(m.embeds) > 0)
			num = 0
			async for msg in history:
				await msg.delete()
				num+=1
			if num > 0:
				await ctx.send(ctx.cresponses['with_success'].format(num,"embeds"))
			else:
				await ctx.send(ctx.cresponses['none_pruned'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)

	@prune.command()
	@commands.cooldown(1,10,commands.BucketType.guild)
	@commands.guild_only()
	@commands.bot_has_permissions(manage_messages=True)
	@checks.mod_or_perm(manage_messages=True)
	async def attachments(self,ctx,max_messages:int):
		if max_messages > self.prune_limit:
			await ctx.send(ctx.gresponses['generic_limit'].format("less",str(self.prune_limit)+" messages"))
			return
		try:
			await ctx.trigger_typing()
			history = ctx.message.channel.history(limit=max_messages,before=ctx.message)
			history = history.filter(lambda m: len(m.attachments) > 0)
			num = 0
			async for msg in history:
				await msg.delete()
				num+=1
			if num > 0:
				await ctx.send(ctx.cresponses['with_success'].format(num,"attachments"))
			else:
				await ctx.send(ctx.cresponses['none_pruned'])
		except Exception as e:
			await self.funcs.command.handle_error(ctx,e)


def setup(bot):
	bot.add_cog(Admin(bot))
