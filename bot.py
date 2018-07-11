import asyncio
import discord
from discord.ext import commands

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import sys,os

import re
import json


import colorama
from colorama import Fore, Back, Style
colorama.init()

from utils import data
from utils import imaging
from utils import funcs
from utils import checks

modules = [ #What "cogs" to load up
	"mods.management",
	"mods.fun",
	"mods.misc",
	"mods.owner",
	"mods.nsfw",
	"mods.image",
	"mods.admin"
]

class Object(object):
	pass

def get_responses(): #Get all the responses for different personalities and reconstruct any damaged or missing responses.
	with open("messages.json","r") as f:
		responses = json.loads(f.read())
	defaults = responses['normal']
	responses.pop('default',None)
	non_defaults = responses
	for nd in non_defaults: #Go through all message sets, except for the default one.
		for msg in defaults['global']:
			if not msg in responses[nd]['global']: #If the current non_default doesn't have the global message, add it.
				responses[nd]['global'][msg] = defaults['global'][msg]
		for group in defaults['commands']: #Go through all the command message groups.
			if not group in responses[nd]['commands']: #If the command group is missing, add it from defaults.
				responses[nd]['commands'][group] = defaults['commands'][group]
				continue
			if group in responses[nd]['commands']: #If the command group exists, look for missing messages and add them.
				for msg in defaults['commands'][group]:
					if not msg in responses[nd]['commands'][group]:
						responses[nd]['commands'][group][msg] = defaults['commands'][group][msg]
	responses['normal'] = defaults
	return responses



def setup_funcs(bot):
	if bot.dev_mode is True:
		db_name = "Claribot_dev"
	else:
		db_name = "Claribot"
	db_user = 'claribot0'
	#Set up database stuff
	global session
	engine = create_engine('mysql+pymysql://{0}:{1}@localhost/{2}?charset=utf8mb4'.format(db_user,bot.db_pass,db_name),isolation_level="READ COMMITTED")
	session = sessionmaker(bind=engine)
	bot.mysql = Object()
	bot.mysql.engine = engine
	bot.mysql.cursor = bot.get_cursor
	bot.data = data.Data(bot)
	bot.imaging = imaging.ImageManip()
	bot.funcs = funcs.Funcs(bot)
	bot.responses = get_responses()
	bot.AdvChecks = checks.AdvChecks(bot) #this is a bit of a cheat/hack, but it works!
	bot.remove_command("help")

class Claribot(commands.AutoShardedBot):

	def __init__(self,*args,**kwargs):
		#Deal with asyncio platform differences
		if sys.platform == "win32":
			self.loop = kwargs.pop('loop', asyncio.ProactorEventLoop())
			asyncio.set_event_loop(self.loop)
		else:
			self.loop = kwargs.pop('loop', asyncio.get_event_loop())
			asyncio.get_child_watcher().attach_loop(self.loop)
		command_prefix = kwargs.pop('commandPrefix', commands.when_mentioned_or('$'))
		#Initialize the bot with all the parameters
		super().__init__(command_prefix=command_prefix,*args,**kwargs)
		#Deal with variables
		self.token = kwargs.pop('token')
		self.owner = None #will be automatically retrieved later
		self.dev_mode = kwargs.pop('dev_mode',False)
		self.db_pass = kwargs.pop('dbPass')

	async def command_help(self,ctx):
		if ctx.invoked_subcommand:
			cmd = ctx.invoked_subcommand
		else:
			cmd = ctx.command
		pages = await self.formatter.format_help_for(ctx, cmd)
		for page in pages:
			await ctx.message.channel.send(page.replace("\n", "fix\n", 1))

	async def on_ready(self):
		setup_funcs(self)
		for cog in modules:
			try:
				self.load_extension(cog)
			except Exception as e:
				msg = Fore.RED + '======COG ERROR======\nModule: {0}\n{1}: {2}\n====================='.format(cog,type(e).__name__,e)
				print(msg)
		playing = self.data.DB.get_bot_setting('playing')
		if not playing:
			playing = "Database Errors"
		out = Fore.GREEN + "------\n{0}\n{1}\nPlaying: {2}\nDeveloper Mode: {3}\n------".format(self.user,("Shard: {0}/{1}".format(self.shard_id,self.shard_count-1)) if self.shard_id is not None else "Shard: ==AUTO SHARDED==",playing,"TRUE" if self.dev_mode else "FALSE") + Style.RESET_ALL
		print(out)
		await self.change_presence(activity=discord.Game(name=playing))

	async def on_message(self,message):
		await self.wait_until_ready()
		if self.owner is None:
			app_info = await self.application_info()
			self.owner = app_info.owner
		if (self.dev_mode and message.author != self.owner) or message.author.bot:
			return
		prefix = self.data.DB.get_prefix(message=message)
		if (message.content.lower().startswith(prefix) or message.content.startswith("<@!{0}>".format(self.user.id))) and message.content.lower() != prefix: #Get if the message starts with the bot's mention or the guilds prefix
			context = await self.funcs.overides.get_context(message,prefix)
			blacklisted = self.funcs.main.is_blacklisted(guild=message.guild,message=message,command=context.command)
			if blacklisted:
				print('Blacklisted')
				return
			await self.funcs.overides.process_commands(message,prefix)

	async def on_command_error(self,ctx,e):
		if isinstance(e, commands.CommandNotFound):
			return
		elif isinstance(e, commands.CommandOnCooldown):
			s = e.retry_after
			h, rm = divmod(s,3600)
			m, seconds = divmod(rm,60)
			h,m = (round(h),round(m))
			m1 = m2 = ""
			if h > 0:
				m1 = "{0}h".format(h)
			if m > 0:
				m2 = "{0}h".format(m)
			after = "{0} {1} {2}s".format(m1,m2,round(seconds,1))
			after = after.strip()
			await ctx.send(ctx.gresponses['cooldown'].format(after))
		elif isinstance(e, discord.errors.Forbidden):
			await ctx.send(ctx.gresponses['no_perms'])
		elif isinstance(e, checks.No_NSFW):
			await ctx.send(ctx.gresponses['no_nsfw'])
		elif isinstance(e, checks.No_Admin):
			await ctx.send(ctx.gresponses['no_admin'])
		elif isinstance(e, checks.No_Mod):
			await ctx.send(ctx.gresponses['no_mod'])
		elif isinstance(e, checks.NSFW_Disabled):
			await ctx.send(ctx.gresponses['nsfw_disabled'])
		elif isinstance(e, checks.No_BotOwner):
			await ctx.send(ctx.gresponses['no_bot_owner'])
		elif isinstance(e, commands.BotMissingPermissions):
			await ctx.send(ctx.gresponses['bot_missing_perms'].format(', '.join(e.missing_perms)))
		elif isinstance(e, commands.NoPrivateMessage):
			await ctx.send(ctx.gresponses['guild_only'])
		elif isinstance(e, commands.MissingRequiredArgument) or isinstance(e, commands.BadArgument):
			await self.command_help(ctx)
		else:
			print("ERROR: " + str(e))
			await ctx.send("Command Error: `{0}`".format(e))
		ctx.command.reset_cooldown(ctx)

	@property
	def get_cursor(self):
		return session()

	def run(self):
		super().run(self.token)

	def die(self):
		try:
			self.loop.stop()
			self.loop.run_forever()
		except Exception as e:
			print(e)
