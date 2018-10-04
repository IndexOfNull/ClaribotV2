import discord
from discord.ext import commands

from utils import checks

from random import randint
import hashlib

from utils.api import fa, da, nekos
from utils.naughtyboi import crawl

class NSFW():

    def __init__(self,bot):
        self.bot = bot
        self.funcs = self.bot.funcs
        self.hash = '2822cae0a9d541e7291ba325c7b7a7ec'
        self.cursor = self.bot.mysql.cursor

    @commands.command(aliases=['fa','furry2'])
    @checks.AdvChecks.nsfw()
    @commands.cooldown(1,5,commands.BucketType.guild)
    @checks.AdvChecks.is_special()
    async def furaffinity(self,ctx,*,query:str=None):
        try:
            await ctx.trigger_typing()
            f = fa.FurAffinity()
            if query:
                results = await f.search(query)
            else:
                results = None
            if results and query:
                result = results[randint(0,len(results)-1)]
                img = result.get_previews(800)
                src = result.source
                if img:
                    embed = self.funcs.misc.get_image_embed(src,img)
                    await ctx.send(embed=embed)
                    return
            else:
                if isinstance(results,list):
                    await ctx.send(ctx.cresponses['no_results'])
                    return
                else:
                    results = await f.get_front_page()
                    if results:
                        result = results[randint(0,len(results)-1)]
                        img = result.get_previews(800)
                        src = result.source
                        if img:
                            embed = self.funcs.misc.get_image_embed(src,img)
                            await ctx.send(embed=embed)
                            return
            await ctx.send(ctx.cresponses['error'])
        except Exception as e:
            await self.funcs.command.handle_error(ctx,e)

    async def do_da(self,ctx,query):
        try:
            await ctx.trigger_typing()
            naughtyboi = False
            h = hashlib.md5()
            h.update(query[:3].encode('utf-8'))
            if h.hexdigest() == self.hash:
                naughtyboi = True
                query = query[3:].strip()
            d = da.DeviantArt()
            if naughtyboi:
                offset = randint(0,360)
                for i in range(4): #10 attempts to get a pic
                    results = await d.search(query,offset=offset,sfw=False)
                    if not results:
                        offset+=60
                        results = []
                        continue
                    else:
                        break
            else:
                results = await d.search(query,offset=randint(0,360),nsfw=True)
                if not results:
                    results = await d.search(query,offset=0,nsfw=True)
            if not results:
                await ctx.send(ctx.cresponses['no_results'])
                return
            result = results[randint(0,len(results)-1)]
            embed = self.funcs.misc.get_image_embed(result.source,result.content)
            await ctx.send(embed=embed)
        except Exception as e:
            await self.funcs.command.handle_error(ctx,e)

    @commands.command(aliases=['neko','nekos'])
    @commands.cooldown(1,5,commands.BucketType.guild)
    @checks.AdvChecks.nsfw()
    async def catgirl(self,ctx,*,tags=None):
        naughtyboi = False
        if tags:
            h = hashlib.md5()
            h.update(tags[:3].encode('utf-8'))
            if h.hexdigest() == self.hash:
                naughtyboi = True
                tags = tags[3:].strip()
                if len(tags) == 0:
                    tags = None
        neko = nekos.Nekos()
        if tags:
            results = await neko.search(tags=tags,nsfw=naughtyboi)
            if not results:
                await ctx.send(ctx.gresponses['generic_no_results'])
                return
            result = results[randint(0,len(results)-1)]
        else:
            results = await neko.random(count=2,nsfw=naughtyboi)
            if not results:
                await ctx.send(ctx.gresponses['generic_no_results'])
                return
            result = results[0]
        img = result.get_image_url()
        embed = self.funcs.misc.get_image_embed(result.source,img)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1,5,commands.BucketType.guild)
    @checks.AdvChecks.nsfw()
    async def furry(self,ctx,*,query=''):
        query+=' tag:anthro'
        await self.do_da(ctx,query)

    @commands.command(aliases=['da'])
    @commands.cooldown(1,5,commands.BucketType.guild)
    @checks.AdvChecks.nsfw()
    async def deviantart(self,ctx,*,query=''):
        await self.do_da(ctx,query)

    """@commands.command()
    @checks.AdvChecks.is_bot_owner()
    @commands.cooldown(1,10000)
    async def crawl(self,ctx):
        try:
            crawler = crawl.TumblrCrawler(self.cursor)
            await crawler.crawl("http://axellycan.tumblr.com/",1000) #Just some weird bizzare tumblr I found, may as well use it as an entry point to find more weird bizzare stuff.
        except Exception as e:
            await self.funcs.command.handle_error(ctx,e)"""

def setup(bot):
    bot.add_cog(NSFW(bot))
