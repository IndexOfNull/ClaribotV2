import discord
import sqlalchemy
from pymysql.converters import escape_item, escape_string, encoders
import hashlib
import random
from random import randint

import traceback

class Data():

	def __init__(self,bot):
		self.DB = DB(bot)
		self.datasets = Datasets()

class Datasets():

	def __init__(self):
		pass

	def get_zalgo_chars(self):
		CHAR_DOWN = ['\u0316', '\u0317', '\u0318', '\u0319', '\u031C',
		'\u031D', '\u031E', '\u031F', '\u0320', '\u0324',
		'\u0325', '\u0326', '\u0329', '\u032A', '\u032B',
		'\u032C', '\u032D', '\u032E', '\u032F', '\u0330',
		'\u0331', '\u0332', '\u0333', '\u0339', '\u033A',
		'\u033B', '\u033C', '\u0345', '\u0347', '\u0348',
		'\u0349', '\u034D', '\u034E', '\u0353', '\u0354',
		'\u0355', '\u0356', '\u0359', '\u035A', '\u0323']
		CHAR_MID = ['\u0315', '\u031B', '\u0340', '\u0341', '\u0358',
		'\u0321', '\u0322', '\u0327', '\u0328', '\u0334',
		'\u0335', '\u0336', '\u034F', '\u035C', '\u035D',
		'\u035E', '\u035F', '\u0360', '\u0362', '\u0338',
		'\u0337', '\u0361', '\u0489']
		CHAR_UP = ['\u030D', '\u030E', '\u0304', '\u0305', '\u033F',
		'\u0311', '\u0306', '\u0310', '\u0352', '\u0357',
		'\u0351', '\u0307', '\u0308', '\u030A', '\u0342',
		'\u0343', '\u0344', '\u034A', '\u034B', '\u034C',
		'\u0303', '\u0302', '\u030C', '\u0350', '\u0300',
		'\u0301', '\u030B', '\u030F', '\u0312', '\u0313',
		'\u0314', '\u033D', '\u0309', '\u0363', '\u0364',
		'\u0365', '\u0366', '\u0367', '\u0368', '\u0369',
		'\u036A', '\u036B', '\u036C', '\u036D', '\u036E',
		'\u036F', '\u033E', '\u035B', '\u0346', '\u031A']
		return (CHAR_DOWN,CHAR_MID,CHAR_UP)


	def get_insult_templates(self):
		templates = [
		"You are <adjective>",
		"You look like <article target=id> <adjective id=id> <animal>",
		"Everyone thinks you are <animal> <animal_part>",
		"	You are as <adjective> as <article target=adj1> <adjective min=1 max=3 id=adj1> <amount> of <adjective min=1 max=3> <animal> <animal_part>"
		]
		return templates

	def get_8ball_responses(self):
		responses = [
		"It is certain",
		"It is decidedly so",
		"Without a doubt",
		"Yes, definitely",
		"You may rely on it",
		"As I see it, yes",
		"Most likely",
		"Outlook good",
		"Yes",
		"Signs point to yes",
		"Reply hazy, try again",
		"Ask again later",
		"Better not tell you now",
		"Cannot predict now",
		"Concentrate and ask again",
		"Don't count on it",
		"My reply is no",
		"My sources say no",
		"Outlook not so good",
		"Very doubtful",
		"The answer lies within",
		"That's a question for your parents",
		"Do you think I'm some kind of psychic?",
		"ERROR: Stupid Question Asked"
		]
		return responses

	def get_wholesome_responses(self):
		responses = [
			"You could open that jar of mayonnaise using only 3 fingers.",
			"Strangers all wanna sit next to you on the bus.",
			"Coworkers fantasizes about getting stuck in the elevator with you.",
			"If Einstein could meet you, he'd be \"mildly to moderately\" intimidated.",
			"At least two friends are going to name their child and/or goldfish after you.",
			"socks + sandals + you = I'm into it.",
			"You are freakishly good at thumb wars.",
			"A 3rd tier cable network would totally create a television show about you.",
			"The FBI tapped your phone just to hear the sound of your voice.",
			"You remind everyone of kiwis- delicious and surprisingly fuzzy.",
			"You never forget to fill the ice-cube tray.",
			"People enjoy you accidentally touching their butt while putting on your seat-belt.",
			"I’d give you the last piece of my gum even if I’d just ate garlic.",
			"There was a high school rumor that you are a distant relative of Abraham Lincoln.",
			"You could make up a weird religion or diet and everyone would follow it.",
			"Your siblings are pissed that your photo is the star of your parent's mantle.",
			"Everyone at sleepovers thought you were the bravest during thunderstorms.",
			"A doctor once saw your butt through the hospital gown. They approve!",
			"Someone almost got a tattoo of your name once, but their mom talked them out of it.",
			"You are your parent's greatest accomplishment, unless they invented the \"spork\".",
			"Some dudes hope you start a band so they can start a cover band of that band.",
			"Your principal would call you to the office just to look cool.",
			"Your allergies are some of the least embarrassing allergies.",
			"Your handshake conveys intelligence, confidence and minor claminess.",
			"Cops admire your ability to stay a perfect 3-5 miles above the speed limit.",
			"You rarely have to go to the bathroom when you fly in the window seat.",
			"Your roommate wants a lock of your hair but is afraid to ask.",
			"Cockroaches, mice and other pests avoid your place out of respect.",
			"Callers are intimidated by how funny your voicemail greeting is.",
			"Kids think you are the “cool old person”.",
			"People always think your jeggings are regular jeans.",
			"80% of motorcycle gangs think you’d be a delightful sidecar.",
			"Everyone at the laundromat thinks you have the cutest underwear.",
			"People behind you at movies think you are the perfect height.",
			"Your parents argue over which one of them you look like.",
			"Sushi chefs are wowed by your chopstick dexterity.",
			"You want the best for everyone...except Caden.",
			"You are someone's \"the one that got away\".",
			"Everybody wants to invite you to their Discord server.",
			"You are the pride of your home town.",
			"The world loves you.",
			"You light up the room.",
			"All of the school jocks are secretly jealous of you.",
			"Telemarketers think you are so nice, even when you don't have to be.",
			"Every day someone thinks of you and smiles.",
			"If it wasn't against the rules, everyone would copy your homework.",
			"Every cat is secretly afraid to admit they love you.",
		]
		return responses

	def get_upsidedown_text(self):
		rot180={
			' ' : ' ',
			'a' : '\u0250', # ɐ
			'b' : 'q',
			'c' : '\u0254', # ɔ
			'd' : 'p',
			'e' : '\u0258', # ǝ
			'f' : '\u025F', # ɟ
			'g' : '\u0183', # ƃ
			'h' : '\u0265', # ɥ
			'i' : '\u0131', # ı
			'j' : '\u027E', # ɾ
			'k' : '\u029E', # ʞ
			'l' : '\u0285', # ʅ
			'm' : '\u026F', # ɯ
			'n' : 'u', # u
			'o' : 'o',
			'p' : 'd',
			'q': 'p',
			'r' : '\u0279', # ɹ
			's' : 's',
			't' : '\u0287', # ʇ
			'u' : 'n',
			'v' : '\u028C', # ʌ
			'w' : '\u028D', # ʍ
			'x' : 'x',
			'y' : '\u028E', # ʎ
			'z' : 'z',
			'.' : '\u02D9', # ˙
			'[' : ']',
			'(' : ')',
			'{' : '}',
			'?' : '\u00BF', # ¿
			'!' : '\u00A1', # ¡
			"\'" : ',',
			'<' : '>',
			'_' : '\u203E', # ‾
			'"' : '\u201E', # „
			'\\' : '\\',
			';' : '\u061B', # ؛
			'\u203F' : '\u2040', # ‿ --> ⁀
			'\u2045' : '\u2046', # ⁅ --> ⁆
			'\u2234' : '\u2235', # ∴ --> ∵
		}
		return rot180

class DB():

	def __init__(self,bot):
		self.bot = bot
		self.cursor = self.bot.mysql.cursor

	def toggle_user(self,guild,user):
		try:
			bl = self.get_user_blacklisted(guild, user)
			if bl:
				sql = "DELETE FROM `blacklist_users` WHERE user_id={0} AND server_id={1}".format(user.id,guild.id)
			else:
				sql = "INSERT INTO `blacklist_users` (`server_id`, `user_id`) VALUES ('{0}', '{1}')".format(guild.id,user.id)
			result = self.cursor.execute(sql)
			self.cursor.commit()
			return True
		except Exception as e:
			print(e)
			self.cursor.rollback()
			return

	def toggle_channel(self,guild,channel):
		try:
			bl = self.get_channel_blacklisted(channel)
			if bl:
				sql = "DELETE FROM `blacklist_channels` WHERE channel_id={0}".format(channel.id)
			else:
				sql = "INSERT INTO `blacklist_channels` (`server_id`, `channel_id`) VALUES ('{0}', '{1}')".format(guild.id,channel.id)
			result = self.cursor.execute(sql)
			self.cursor.commit()
			return True
		except Exception as e:
			print(e)
			self.cursor.rollback()
			return

	def toggle_command(self,guild,command):
		try:
			bl = self.get_command_blacklisted(guild,command)
			if bl:
				sql = "DELETE FROM `blacklist_commands` WHERE server_id={0} AND command=:c".format(guild.id)
			else:
				sql = "INSERT INTO `blacklist_commands` (`server_id`, `command`) VALUES ('{0}', :c)".format(guild.id)
			result = self.cursor.execute(sql,{'c':command.name})
			self.cursor.commit()
			return True
		except Exception as e:
			print(e)
			self.cursor.rollback()
			return

	def get_command_blacklisted(self,guild,command):
		try:
			sql = "SELECT command FROM `blacklist_commands` WHERE server_id={0} AND command=:c".format(guild.id)
			result = self.cursor.execute(sql,{'c':command.name}).fetchall()
			if result:
				if result[0]["command"] == command.name:
					return True
			return False
		except:
			self.cursor.rollback()
			return False

	def get_channel_blacklisted(self,channel):
		try:
			sql = "SELECT channel_id FROM `blacklist_channels` WHERE channel_id={0}".format(channel.id)
			result = self.cursor.execute(sql).fetchall()
			if result:
				if result[0]["channel_id"] == channel.id:
					return True
			return False
		except Exception as e:
			self.cursor.rollback()
			return False

	def get_user_blacklisted(self,guild,user):
		try:
			sql = "SELECT user_id FROM `blacklist_users` WHERE user_id={0} AND server_id={1}".format(user.id,guild.id)
			result = self.cursor.execute(sql).fetchall()
			if result:
				if result[0]["user_id"] == user.id:
					return True
			return False
		except:
			self.cursor.rollback()
			return False

	def get_blacklist(self,guild,**kwargs):
		try:
			types = kwargs.pop('types',['user','channel','command'])
			blacklist = {'users':[],'channels':[],'commands':[]}
			if 'user' in types:
				sql = "SELECT user_id FROM `blacklist_users` WHERE server_id={0.id}".format(guild)
				result = self.cursor.execute(sql).fetchall()
				if result:
					for user in result:
						blacklist['users'].append(self.bot.get_user(user['user_id']))
			if 'channel' in types:
				sql = "SELECT channel_id FROM `blacklist_channels` WHERE server_id={0.id}".format(guild)
				result = self.cursor.execute(sql).fetchall()
				if result:
					for channel in result:
						blacklist['channels'].append(self.bot.get_channel(channel['channel_id']))
			if 'command' in types:
				sql = "SELECT command FROM `blacklist_commands` WHERE server_id={0.id}".format(guild)
				result = self.cursor.execute(sql).fetchall()
				if result:
					for command in result:
						blacklist['commands'].append(self.bot.get_command(command['command']))
			return blacklist
		except:
			self.cursor.rollback()
			return

	def get_serveropt(self,guild,opt,**kwargs):
		default = kwargs.pop('default',None)
		throw_errors = kwargs.pop('errors',False)
		try:
			sql = "SELECT value FROM `server_options` WHERE server_id={0.id} AND var=:o".format(guild)
			result = self.cursor.execute(sql,{'o':opt}).fetchall()
			if result:
				if throw_errors:
					return result[0]['value'], True
				else:
					return result[0]['value']
			else:
				if throw_errors:
					return default, True
				else:
					return default
		except Exception as e:
			print(e)
			self.cursor.rollback()
			if throw_errors:
				return default, False
			else:
				return default

	def set_serveropt(self,guild,opt,val,**kwargs):
		default = kwargs.pop('default',None)
		try:
			sql = "SELECT value FROM `server_options` WHERE server_id={0.id} AND var=:o".format(guild)
			exists = self.cursor.execute(sql,{'o':opt}).fetchall()
			if exists:
				if exists[0]['value'] == val:
					return True
				if val == default:
					sql = "DELETE FROM `server_options` WHERE server_id={0.id} AND var=:o".format(guild)
					result = self.cursor.execute(sql,{'o':opt})
					self.cursor.commit()
					return True
				else:
					sql = "UPDATE `server_options` SET value=:val WHERE server_id={0.id} AND var=:o".format(guild)
					result = self.cursor.execute(sql,{'val':val,'o':opt})
					self.cursor.commit()
					return True
			else:
				if val == default:
					return True
				sql = "INSERT INTO `server_options` (`server_id`,`var`,`value`) VALUES ('{0.id}',:o,:val)".format(guild)
				result = self.cursor.execute(sql,{'o':opt,'val':val})
				self.cursor.commit()
				return True
			return False
		except Exception as e:
			print(e)
			self.cursor.rollback()
			return False

	def get_personality(self,guild,**kwargs):
		throw_errors = kwargs.pop('errors',False)
		try:
			sql = "SELECT personality FROM `personality` WHERE server_id={0.id}".format(guild)
			result = self.cursor.execute(sql).fetchall()
			if result:
				return result[0]['personality']
			if throw_errors:
				return False
			else:
				return 'normal'
		except Exception as e:
			self.cursor.rollback()
			if throw_errors:
				return False
			else:
				return 'normal'

	def set_personality(self,guild,personality):
		try:
			sql = "SELECT personality FROM `personality` WHERE server_id={0.id}".format(guild)
			exists = self.cursor.execute(sql).fetchall()
			if exists:
				if exists[0]['personality'] == personality:
					return True
				if personality == 'normal':
					sql = "DELETE FROM `personality` WHERE server_id={0.id}".format(guild)
				else:
					sql = "UPDATE `personality` SET personality=:p WHERE server_id={0.id}".format(guild)
				result = self.cursor.execute(sql,{'p':personality})
				self.cursor.commit()
				return True
			else:
				sql = "INSERT INTO `personality` (`server_id`,`personality`) VALUES ('{0.id}',:p)".format(guild)
				result = self.cursor.execute(sql,{'p':personality})
				self.cursor.commit()
				return True
			return False
		except Exception as e:
			self.cursor.rollback()
			return False

	def get_prefix(self,**kwargs): #Get the prefix from the database for the guild/message.
		message = kwargs.pop('message',None)
		guild = kwargs.pop('guild',None)
		try:
			if self.bot.dev_mode is True:
				prefix = ","
			else:
				prefix = "$"
			if message is None and guild is None:
				return prefix
			if message: #If the message exists
				if not isinstance(message.channel, discord.TextChannel) is True: #Return the prefix
					return prefix
				guild = message.guild #We know the message should have a guild at this point, so we can derive the guild from it
			if guild: #The guild should be defined at this point, either derived from message or given by the invoker.
				sql = "SELECT prefix FROM `prefix` WHERE server_id={0.id}".format(guild)
				result = self.cursor.execute(sql).fetchall()
				if result:
					prefix = result[0]['prefix'].lower()
			return prefix
		except Exception as e:
			print(e)
			return "$"
			self.cursor.rollback()

	def set_prefix(self,guild,prefix:str): #Sets the command prefix for the guild
		try:
			sql = "SELECT prefix FROM `prefix` WHERE server_id={0.id}".format(guild) #See if the guild has an entry already.
			exists = self.cursor.execute(sql).fetchall()
			if exists:
				if prefix == "$": #If the prefix is the default prefix, delete the entry to keep the db cleaner and faster.
					sql = "DELETE FROM `prefix` WHERE server_id={0.id}".format(guild)
				else:
					sql = "UPDATE `prefix` SET prefix=:p WHERE server_id={0.id}".format(guild)
				result = self.cursor.execute(sql,{'p':prefix})
				self.cursor.commit()
				return True
			else:
				sql = "INSERT INTO `prefix` (`server_id`, `prefix`) VALUES ('{0.id}', :p);".format(guild)
				result = self.cursor.execute(sql,{'p':prefix})
				self.cursor.commit()
				return True
			return False
		except Exception as e:
			print(e)
			self.cursor.rollback()
			return False

	def get_bot_setting(self,setting:str): #Get a bot variable from bot_data, returns False if value is found or errors.
		try:
			sql = "SELECT value FROM `bot_data` WHERE var_name=:vn"
			result = self.cursor.execute(sql,{'vn':setting}).fetchall()
			if result:
				return result[0]['value']
			else:
				return False
		except Exception as e:
			print(e)
			self.cursor.rollback()
			return False

	def set_bot_setting(self,setting:str,value:str): #Update a bot_data variable, returns a success boolean.
		try:
			sql = "UPDATE `bot_data` SET value=:value WHERE var_name=:setting"
			result = self.cursor.execute(sql,{'setting':setting,'value':value})
			self.cursor.commit()
			return True
		except Exception as e:
			print(e)
			self.cursor.rollback()
			return False

	def get_special_users(self):
		try:
			sql = "SELECT `user_id` FROM `special_users`"
			results = self.cursor.execute(sql).fetchall()
			users = []
			if results:
				for user in results:
					users.append(self.bot.get_user(user['user_id']))
				return users
			return []
		except:
			self.cursor.rollback()
			return False

	def get_user_special(self,user):
		try:
			sql = "SELECT `user_id` FROM `special_users` WHERE user_id={0.id};".format(user)
			results = self.cursor.execute(sql).fetchall()
			if results:
				if results[0]["user_id"] == user.id:
					return True
				else:
					return False
			else:
				return False
		except Exception as e:
			print(e)
			self.cursor.rollback()
			return False

	def add_special_user(self,user):
		try:
			sql = "INSERT INTO `special_users` (`user_id`) VALUES ('{0.id}');".format(user)
			result = self.cursor.execute(sql)
			self.cursor.commit()
			return True
		except:
			self.cursor.rollback()
			return False

	def remove_special_user(self,user):
		try:
			sql = "DELETE FROM `special_users` WHERE user_id={0.id};".format(user)
			result = self.cursor.execute(sql)
			self.cursor.commit()
			return True
		except:
			self.cursor.rollback()
			return False

	def add_warning(self,**kwargs):
		user = kwargs.pop('user')
		guild = kwargs.pop('guild')
		reason = kwargs.pop('reason')
		sender = kwargs.pop('warner')
		now = self.bot.funcs.time.get_utc_now()
		timestamp = kwargs.pop('timestamp',now)
		return_data = kwargs.pop('return_data',False)
		r = "{0}|{1}|{2}".format(now,user.id,randint(0,696969))
		id = kwargs.pop('id',str(hashlib.sha1(r.encode('utf-8')).hexdigest())[:7])
		try:
			sql = "INSERT INTO `warnings` (`server_id`, `user_id`, `reason`, `warner`, `timestamp`, `issue_id`) VALUES ('{0.id}', '{1.id}', :reason, '{2.id}', '{3}', '{4}');".format(guild,user,sender,timestamp,id)
			result = self.cursor.execute(sql,{'reason':reason})
			self.cursor.commit()
			if return_data:
				return {'user':user,'guild':guild,'reason':reason,'warner':sender,'timestamp':timestamp,'id':id}
			else:
				return True
		except Exception as e:
			self.cursor.rollback()
			return False

	def del_warning(self,**kwargs):
		guild = kwargs.pop('guild')
		id = kwargs.pop('id')
		try:
			sql = "DELETE FROM `warnings` WHERE server_id={0.id} AND issue_id='{1}'".format(guild,id)
			result = self.cursor.execute(sql)
			self.cursor.commit()
			return True
		except Exception as e:
			self.cursor.rollback()
			return False

	def get_user_warnings(self,guild,user,**kwargs):
		get_others = kwargs.pop('others',False)
		try:
			if get_others:
				sql = "SELECT * FROM `warnings` WHERE user_id={0.id}".format(user)
			else:
				sql = "SELECT * FROM `warnings` WHERE user_id={0.id} AND server_id={0.id}".format()
			results = self.cursor.execute(sql).fetchall()
			if get_others:
				server = []
				others = []
				for row in results:
					if row['server_id'] == guild.id:
						server.append(row)
					else:
						others.append(row)
				return server,others
			else:
				return results
		except Exception as e:
			print(e)
			self.cursor.rollback()
			return False

	def get_warning(self,**kwargs):
		guild = kwargs.pop('guild')
		i = kwargs.pop('warning_id')
		try:
			sql = "SELECT * FROM `warnings` WHERE server_id={0.id} AND issue_id=:iss".format(guild)
			results = self.cursor.execute(sql,{"iss":i}).fetchall()
			if results:
				return results[0]
			return []
		except Exception as e:
			self.cursor.rollback()
			return

	def get_user_messages(self,**kwargs):
		count = kwargs.pop('count',10)
		read = kwargs.pop('read',0)
		type = kwargs.pop('type','suggestion')
		id = kwargs.pop('id',None)
		try:
			if id:
				sql = "SELECT * FROM `user_messages` WHERE id='{0}' AND type='{1}'".format(id,type)
			else:
				sql = "SELECT * FROM `user_messages` WHERE been_read={1} AND type='{2}' ORDER BY timestamp ASC LIMIT {0}".format(count,read,type,id)
			results = self.cursor.execute(sql).fetchall()
			if results:
				return results
			else:
				return []
		except Exception as e:
			print(e)
			self.cursor.rollback()
			return

	def set_user_message_read(self,ids,value):
		if not isinstance(ids,list):
			ids = [ids]
		try:
			sql = "UPDATE `user_messages` SET been_read={1} WHERE id='{0}'"
			for id in ids:
				self.cursor.execute(sql.format(id,value))
			self.cursor.commit()
			return True
		except:
			self.cursor.rollback()
			return

	def add_user_message(self,ctx,**kwargs):
		now = self.bot.funcs.time.get_utc_now()
		guild = kwargs.pop('guild',ctx.guild)
		user = kwargs.pop('user',ctx.message.author)
		message = kwargs.pop('message')
		r = "{0}|{1}|{2}".format(now,user.id,randint(0,696969))
		id = kwargs.pop('id',str(hashlib.sha1(r.encode('utf-8')).hexdigest())[:11])
		timestamp = kwargs.pop('timestamp',now)
		type = kwargs.pop('type','suggestion')
		try:
			sql = "INSERT INTO `user_messages` (`server_id`, `user_id`, `message`, `id`, `timestamp`, `type`, `been_read`) VALUES ('{0}', '{1}', :msg, '{2}', '{3}', '{4}', '0');".format(guild.id,user.id,id,timestamp,type)
			results = self.cursor.execute(sql,{'msg':message})
			self.cursor.commit()
			return True
		except:
			self.cursor.rollback()
			return False
