import discord
from discord.ext import commands

bot_owner = 166206078164402176

class No_Role(commands.CommandError): pass
class No_Admin(commands.CommandError): pass
class No_Mod(commands.CommandError): pass
class No_NSFW(commands.CommandError): pass
class No_BotOwner(commands.CommandError): pass
class No_Special(commands.CommandError): pass
class NSFW_Disabled(commands.CommandError): pass

def check_perms(ctx,perms):
    msg = ctx.message
    if len(perms) == 0 or not perms:
        return False
    if msg.author.id == bot_owner:
        return True
    permissions = msg.channel.permissions_for(msg.author)
    return all(getattr(permissions, perm, None) == value for perm, value in perms.items())

def is_bot_owner():
    def predicate(ctx):
        if ctx.message.author == bot_owner:
            return True
        raise No_BotOwner
    return commands.check(predicate)

def role_or_perm(t,ctx,check,**perms):
    if check_perms(ctx,perms):
        return True
    if not isinstance(ctx.message.channel,discord.TextChannel):
        return False
    role = discord.utils.find(check,ctx.message.author.roles)
    if role is not None:
        return None
    if t:
        return False
    else:
        raise No_Role()



admin_roles = ("admin","administrator","boss","god","owner")
admin_perms = ['administrator','manage_guild']
def admin_or_perm(**perms):
    def predicate(ctx):
        if is_admin_or_perm(ctx,**perms):
            return True
        raise No_Admin()
    return commands.check(predicate)

mod_roles = ("mod","moderator","manager")
mod_perms = ['manage_messages','ban_members','kick_members']
def mod_or_perm(**perms):
    def predicate(ctx):
        if is_mod_or_perm(ctx,**perms):
            return True
        raise No_Mod()
    return commands.check(predicate)

def is_admin_or_perm(ctx,**perms):
    if not isinstance(ctx.message.channel, discord.TextChannel) or ctx.message.author.id == ctx.message.guild.owner.id: #If its not a server or its the server owner, return True
        return True
    if role_or_perm(True,ctx, lambda r: r.name.lower() in admin_roles,**perms): #If the user has a role that is named like an admin-like role.
        return True
    for role in ctx.message.author.roles: #Gather all of the users permissions
        role_perms = []
        for perm in role.permissions:
            role_perms.append(perm)
        for perm in role_perms: #Go through all the users permissions and compare them to the admin_perms, if there's a match, return True.
            for aperm in admin_perms:
                if perm[0] == aperm and perm[1] == True:
                    return True
    return False

def is_mod_or_perm(ctx,**perms):
    if not isinstance(ctx.message.channel, discord.TextChannel) or ctx.message.author.id == ctx.message.guild.owner.id: #If its not a server or its the server owner, return True
        return True
    if role_or_perm(True,ctx, lambda r: r.name.lower() in mod_roles,**perms): #If the user has a role that is named like an admin-like role.
        return True
    for role in ctx.message.author.roles: #Gather all of the users permissions
        role_perms = []
        for perm in role.permissions:
            role_perms.append(perm)
        for perm in role_perms: #Go through all the users permissions and compare them to the admin_perms, if there's a match, return True.
            for aperm in mod_perms:
                if perm[0] == aperm and perm[1] == True:
                    return True
    return False

class AdvChecks():

    def __init__(self,bot2):
        global bot
        bot = bot2

    def nsfw():
        def predicate(ctx):
            if not isinstance(ctx.message.channel,discord.TextChannel):
                return True
            enabled = bot.data.DB.get_serveropt(ctx.guild,'nsfw_enabled',default="true")
            if enabled == "false":
                raise NSFW_Disabled()
            if ctx.message.channel.is_nsfw():
                return True
            raise No_NSFW()
        return commands.check(predicate)

    def is_bot_owner():
        def predicate(ctx):
            if ctx.message.author == bot.owner:
                return True
            raise No_BotOwner()
        return commands.check(predicate)

    def is_special():
        def predicate(ctx):
            if bot.data.DB.get_user_special(ctx.message.author) or ctx.message.author == bot.owner:
                return True
            raise No_Special()
        return commands.check(predicate)
