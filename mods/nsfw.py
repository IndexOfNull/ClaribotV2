import asyncio
import discord
from discord.ext import commands

from utils import checks

from random import randint
import hashlib

from utils.api import fa, da, nekos
from utils.naughtyboi import crawl

import datetime

import traceback

class NSFW():

    def __init__(self,bot):
        self.bot = bot
        self.funcs = self.bot.funcs
        self.hash = '2822cae0a9d541e7291ba325c7b7a7ec'
        self.cursor = self.bot.mysql.cursor

    def naughtyboi(self,query):
        if not query:
            return query, False
        naughtyboi = False
        h = hashlib.md5()
        h.update(query[:3].encode('utf-8'))
        if h.hexdigest() == self.hash:
            naughtyboi = True
            query = query[3:].strip()
        return query, naughtyboi

    @commands.command(aliases=['fa2'])
    @checks.AdvChecks.nsfw()
    @commands.cooldown(1,20,commands.BucketType.guild)
    @checks.AdvChecks.is_special()
    async def fabomb(self,ctx,*,query:str=""):
        try:
            query, naughtyboi = self.naughtyboi(query)
            cookies = ()
            ratings = ['general']
            if naughtyboi:
                cookies = self.bot.fatokens
                ratings = ['general','mature']
            if len(query) == 0:
                query = None
            f = fa.FurAffinity(cookies=cookies)
            results = await f.random(query=query,ratings=ratings,results=5)
            if not results:
                await ctx.send(ctx.cresponses['no_results'])
                return
            embeds = []
            for result in results:
                embeds.append(self.funcs.misc.get_image_embed(result.url,result.get_preview(800)))
            await asyncio.wait([ctx.send(embed=i) for i in embeds])
        except Exception as e:
            await self.funcs.command.handle_error(ctx,e)

    """@commands.command()
    async def fascrape(self,ctx):
        try:
            results = []
            previews = []
            f = fa.FurAffinity()
            for i in range(1,17):
                await asyncio.sleep(1)
                print("Working on page {0}".format(i))
                results += await f.random(results=72,perpage=72,page=i)
            if results:
                for result in results:
                    previews.append(result.get_preview(800))
            for preview in previews:
                print(preview)
        except Exception as e:
            print(e)
            pass"""

    @commands.command(aliases=['fa'])
    async def furaffinity(self,ctx,*,query:str=""):
        try:
            #Finish this up
            query, naughtyboi = self.naughtyboi(query)
            cookies = ()
            ratings = ['general']
            if naughtyboi:
                cookies = self.bot.fatokens
                ratings = ['general','mature']
            if len(query) == 0:
                query = None
            f = fa.FurAffinity(cookies=cookies)
            results = await f.random(query=query,ratings=ratings,results=1)
            if not results:
                await ctx.send(ctx.cresponses['no_results'])
                return
            result = results[0]
            embed = self.funcs.misc.get_image_embed(result.url,result.get_preview(800))
            await ctx.send(embed=embed)
        except:
            await self.funcs.command.handle_error(ctx,e)

    async def do_da(self,ctx,query):
        try:
            await ctx.trigger_typing()
            query, naughtyboi = self.naughtyboi(query)
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

    @commands.command()
    @commands.cooldown(1,5,commands.BucketType.guild)
    @checks.AdvChecks.is_bot_owner() #Will come at a later date
    @checks.AdvChecks.nsfw()
    async def roulette(self,ctx):
        try:
            randomPost = self.cursor.execute("SELECT img_url, url FROM tumblr_crawl ORDER BY RAND() LIMIT 1;").fetchall()[0]
            embed = self.funcs.misc.get_image_embed(randomPost['url'],randomPost['img_url'])
            await ctx.send(embed=embed)
        except Exception as e:
            await self.funcs.command.handle_error(ctx,e)

    """@commands.command(aliases=['goback'])
    @commands.cooldown(1,30,commands.BucketType.guild)
    @checks.AdvChecks.nsfw()
    async def ohfuckgoback(self,ctx): #kinda broken sometimes, plus it doesn't work well
        try:
            last = await ctx.channel.history(before=ctx.message,limit=10,after=ctx.message.created_at - datetime.timedelta(minutes=2)).get(author=self.bot.user)
            print(last)
            if last:
                await last.delete()
                await ctx.send(ctx.cresponses['success'],delete_after=5)
            else:
                await ctx.send(ctx.cresponses['no_message'],delete_after=10)
        except Exception as e:
            await self.funcs.command.handle_error(ctx,e)"""

    """@commands.command()
    @checks.AdvChecks.is_bot_owner()
    @commands.cooldown(1,10000)
    async def crawl(self,ctx):
        try:
            crawler = crawl.TumblrCrawler(self.cursor)
            await crawler.crawl("URLHERE",1000) #Just some weird bizzare tumblr I found, mignt as well use it as an entry point to find more weird bizzare stuff.
        except Exception as e:
            await self.funcs.command.handle_error(ctx,e)"""

def setup(bot):
    bot.add_cog(NSFW(bot))
