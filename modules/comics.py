
import json
import random
import re

from bs4 import BeautifulSoup
from discord.ext import commands
from utility import discordembed as dmbd


class Comics:
    def __init__(self, bot):
        self.bot = bot


    async def refreshxkcd(self):
        if self.bot.redis_db.get('xkcdmax') is not None:
            return True
        async with self.bot.session.get("http://xkcd.com/info.0.json") as r:
            if r.status != 200:
                self.bot.cogs['Log'].output("XKCD is down")
                return False
            j = await r.json()
            self.bot.redis_db.set('xkcdmax', j['num'], ex=86400)
            return True

    async def getxkcd(self, num, url):
        """ Num should be passed as an INT """
        num = int(num)
        result = self.bot.redis_db.hget('xkcd', num)
        if result is None:
            async with self.bot.session.get(url + "/info.0.json") as r:
                if not r.status == 200:
                    self.bot.cogs['Log'].output("Unable to get XKCD #" + str(num))
                    return
                j = await r.json()
                self.bot.redis_db.hmset('xkcd', {num: j})
                return j
        else:
            j = result.decode('utf-8')
            j = json.loads(j)
            return j

    @commands.command(pass_context=True)
    async def xkcd(self, ctx):
        """Gives a random XKCD Comic"""
        chk = await self.refreshxkcd()
        if not chk:
            return
        maxnum = int(self.bot.redis_db.get('xkcdmax').decode('utf-8'))
        number = random.randint(1, maxnum)
        url = "http://xkcd.com/" + str(number)
        j = await self.getxkcd(number, url)

        em = dmbd.newembed(ctx.message.author, j['safe_title'], u=url)
        em.set_image(url=j['img'])
        em.add_field(name=j['alt'], value="{0}/{1}/{2}".format(j['month'], j['day'], j['year']))
        await self.bot.say(embed=em)
        self.bot.cogs['Wordcount'].cmdcount('xkcd')

    async def refreshcyanide(self):
        if self.bot.redis_db.get('cyanidemax') is not None:
            return True
        async with self.bot.session.get("http://explosm.net/comics/latest") as r:
            if r.status != 200:
                self.bot.cogs['Log'].output("Cyanide&Happiness is down")
                return False
            soup = BeautifulSoup(await r.text(), 'html.parser')
            current = int(re.findall(r'\d+', soup.find(id="permalink", type="text").get("value"))[0])
            self.bot.redis_db.set('cyanidemax', current, ex=86400)
            return True

    async def getcyanide(self, num, url):
        num = int(num)
        result = self.bot.redis_db.hget('cyanide', num)
        if result is None:
            async with self.bot.session.get(url) as r:
                if not r.status == 200:
                    self.bot.cogs['Log'].output("Unable to get Cyanide #" + str(num))
                    return
                soup = BeautifulSoup(await r.text(), 'html.parser')
                if soup.prettify().startswith('Could not'):
                    await self.bot.say('Report this number as a dead comic: ' + str(num))
                    return
                img = 'http:' + str(soup.find(id="main-comic")['src'])
                self.bot.redis_db.hmset('xkcd', {num: img})
                return img
        else:
            img = result.decode('utf-8')
            return img


    @commands.command(pass_context=True)
    async def cyanide(self, ctx):
        """ Gives a random Cyanide & Happiness Comic"""
        chk = await self.refreshcyanide()
        if not chk:
            return

        # whatever reason, comics 1 - 38 don't exist.
        number = random.randint(39, int(self.bot.redis_db.get('cyanidemax').decode('utf-8')))
        link = 'http://explosm.net/comics/' + str(number)

        img = await self.getcyanide(number, link)
        if img is None:
            return
        em = dmbd.newembed(ctx.message.author, 'Cyanide and Happiness', str(number), u=link)
        em.set_image(url=img)
        await self.bot.say(embed=em)
        self.bot.cogs['Wordcount'].cmdcount('ch')

    @commands.command(pass_context=True)
    async def cyanidercg(self, ctx):
        """ Gives a randomly generated Cyanide & Happiness Comic"""

        async with self.bot.session.get('http://explosm.net/rcg') as r:
            if not r.status == 200:
                self.bot.cogs['Log'].output("Unable to get RCG for Cyanide")
                return
            soup = BeautifulSoup(await r.text(), 'html.parser')
            img = 'http:' + str(soup.find(id='rcg-comic').img['src'])
        print(img)
        em = dmbd.newembed(ctx.message.author, 'Cyanide and Happiness RCG', u=img)
        em.set_image(url=img)
        await self.bot.say(embed=em)
        self.bot.cogs['Wordcount'].cmdcount('chrng')


def setup(bot):
    bot.add_cog(Comics(bot))
