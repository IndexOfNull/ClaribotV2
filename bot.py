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

#from apscheduler.schedulers.asyncio import AsyncIOScheduler

modules = [ #What "cogs" to load up
	"mods.management",
	"mods.fun",
	"mods.misc",
	"mods.owner",
	"mods.nsfw",
	"mods.image",
	"mods.admin",
	"mods.face"
]

if os.path.isfile("mods/mrmeme.py"):
	modules.append("mods.mrmeme")

class Object(object): pass

def get_responses(): #Get all the responses for different personalities and reconstruct any missing responses.
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

def setup_funcs(bot): #Initialize any variables and systems that we need later.
	#if bot.dev_mode is True:
	#	bot.db_name = bot.db_name + "_dev"
	db_user = 'claribot0'
	#Set up database stuff
	global session
	engine = create_engine('mysql+pymysql://{0}:{1}@{2}/{3}?charset=utf8mb4'.format(bot.db_username,bot.db_pass,bot.db_ip,bot.db_name),isolation_level="READ COMMITTED")
	session = sessionmaker(bind=engine)
	bot.mysql = Object()
	bot.mysql.engine = engine
	bot.mysql.cursor = bot.get_cursor
	#Setup functions and data.
	bot.data = data.Data(bot)
	bot.imaging = imaging.ImageManip()
	bot.funcs = funcs.Funcs(bot)
	bot.responses = get_responses()
	bot.AdvChecks = checks.AdvChecks(bot) #this is a bit of a cheat/hack to pass the bot instance to the checks.py file, but it works!
	bot.remove_command("help") #We will replace it with our own help command later
	bot.fatokens = ()

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
		self.db_ip = kwargs.pop('db_ip','localhost')
		self.db_name = kwargs.pop('db_name','claribot')
		self.db_username = kwargs.pop('db_username','claribot_user')


	async def command_help(self,ctx): #Format help for a command if needed
		if ctx.invoked_subcommand:
			cmd = ctx.invoked_subcommand
		else:
			cmd = ctx.command
		pages = await self.formatter.format_help_for(ctx, cmd)
		for page in pages:
			await ctx.message.channel.send(page.replace("\n", "fix\n", 1))

	async def on_ready(self): #When the bot has logged in and is ready
		setup_funcs(self) #Initialize functions
		for cog in modules: #Load cogs
			try:
				self.load_extension(cog)
			except Exception as e:
				msg = Fore.RED + '======COG ERROR======\nModule: {0}\n{1}: {2}\n====================='.format(cog,type(e).__name__,e)
				print(msg)
		playing = self.data.DB.get_bot_setting('playing')
		if not playing:
			playing = "Database Errors" #If there was an error getting the playing status, use this instead
		tokens = self.data.DB.get_bot_setting('fatokens')
		if tokens:
			self.fatokens = tokens.split(";")
		out = Fore.GREEN + "------\n{0}\n{1}\nPlaying: {2}\nDeveloper Mode: {3}\n------".format(self.user,("Shard: {0}/{1}".format(self.shard_id,self.shard_count-1)) if self.shard_id is not None else "Shard: ==AUTO SHARDED==",playing,"TRUE" if self.dev_mode else "FALSE") + Style.RESET_ALL
		print(out)
		await self.change_presence(activity=discord.Game(name=playing)) #Set playing status

	async def on_message(self,message): #Triggers whenever a message is sent.
		await self.wait_until_ready()
		if self.owner is None:
			app_info = await self.application_info()
			self.owner = app_info.owner
		if (self.dev_mode and message.author != self.owner) or message.author.bot:
			return
		prefix = self.data.DB.get_prefix(message=message) #Get the server's prefix
		handle_owo = True
		mentioned = message.content.startswith(self.user.mention)
		if (message.content.lower().startswith(prefix) or mentioned) and message.content.lower() != prefix: #Get if the message starts with the bot's mention or the guilds prefix
			if mentioned:
				message.content = "$" + message.content[len(self.user.mention):].strip()
				prefix = "$"
			context = await self.funcs.overides.get_context(message,prefix)
			blacklisted = self.funcs.main.is_blacklisted(guild=message.guild,message=message,command=context.command)
			if context.command:
				if context.command.name in ("owo","uwu"):
					handle_owo = False
			if blacklisted:
				return
			await self.funcs.overides.process_commands(message,prefix)
		else:
			dads = re.findall(r"\bI'?\s*a?m\s([^.|?|!]+)",message.content,re.IGNORECASE)
			if len(dads) >= 1:
				dad = dads[0]
				if self.data.DB.get_serveropt(message.guild,"dad_mode",default=False,errors=False):
					if len(dad) > 1900:
						dad = "Mr. Long Message"
					await message.channel.send("Hi \"{0}\", I'm {1}.".format(dad,message.guild.me.display_name))
		if handle_owo:
			owo_success = self.funcs.main.handle_owo(message)

	async def on_command_completion(self,ctx):
		if ctx.command.root_parent:
			self.data.counters.update_command_usage(ctx.command.root_parent.name+"_"+ctx.command.name)
		else:
			self.data.counters.update_command_usage(ctx.command.name)

	async def on_command_error(self,ctx,e): #If a command errors out, error names explain it all.
		#print("Command Error ({0}): `{1}`".format(type(e).__name__,e))
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
			return
		elif isinstance(e, discord.errors.Forbidden):
			await ctx.send(ctx.gresponses['no_perms'])
		elif isinstance(e, checks.No_NSFW):
			await ctx.send(ctx.gresponses['no_nsfw'])
		elif isinstance(e, checks.No_Admin):
			await ctx.send(ctx.gresponses['no_admin'])
		elif isinstance(e, checks.No_Mod):
			await ctx.send(ctx.gresponses['no_mod'])
		elif isinstance(e, checks.No_Special):
			await ctx.send(ctx.gresponses['no_special'])
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
		elif isinstance(e, checks.Not_E):
			pass
		else:
			#print("Command Error ({0}): `{1}`".format(type(e).__name__,e))
			#await ctx.send("Command Error ({0}): `{1}`".format(type(e).__name__,e))
			await self.funcs.command.handle_error(ctx,e)
		ctx.command.reset_cooldown(ctx)

	async def on_guild_join(self,guild):
		channel_names = ["entry","general","general-chat","general2","general-2","general-chat-2"]
		exclude = ["rules","announcements","major-announcements","important-announcements"]
		message = "Hi there!\n\nMy name is Claribot, and I'm here to add some fun features to your server! I have a variety of commands that can manipulate images, make decisions, count how many times you have said \"OwO\", and much more.\n\nMy default command prefix is `$`, but you can always change it with $prefix."
		for channel in guild.channels:
			if channel.name in channel_names and not channel.name in exclude:
				await channel.send(message)
				return
		for channel in guild.channels:
			if not channel.name in exclude:
				await channel.send(message)
				return

	@property
	def get_cursor(self): #DB stuff
		return session()

	def run(self): #Actually run the bot
		super().run(self.token)

	def die(self): #Gracefully shut the bot down
		try:
			self.loop.stop()
			self.mysql.cursor.close_all()
			self.mysql.engine.dispose()
			tasks = asyncio.gather(*asyncio.Task.all_tasks(), loop=self.loop)
			tasks.cancel()
			self.loop.run_forever()
			tasks.exception()
		except Exception as e:
			print(e)
