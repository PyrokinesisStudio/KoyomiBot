""" Overwatch API usage"""

import random

from discord.ext import commands
from utility import discordembed as dmbd


class Overwatch:
    def __init__(self, bot):
        self.bot = bot

        self.heroes = ['Genji', 'McCree', 'Pharrah', 'Reaper', 'Soldier 76',
                       'Tracer', 'Bastion', 'Hanzo', 'Junkrat', 'Mei',
                       'Torbjorn', 'Widowmaker', 'D.va', 'Reinhardt', 'Roadhog',
                       'Winston','Zarya', 'Lucio', 'Mercy',
                       'Symmetra', 'Zenyatta', 'Sombra', 'Orisa']

    @staticmethod
    def display(author, player, qp, comp):
        em = dmbd.newembed(author, player.replace('-', '#'), "Please let me know if you'd like to see more different stats.")
        em.set_thumbnail(url=qp['overall_stats']['avatar'])
        level = qp['overall_stats']['prestige'] * 100 + qp['overall_stats']['level']
        cmpwinrate = (
            str(comp['overall_stats']['win_rate']) + "(" +
            str(comp['overall_stats']['wins']) + "/" +
            str(comp['overall_stats']['games']) + ")"
        )
        em.add_field(name='Level', value=level)
        em.add_field(
            name='Competitive Rank',
            value=comp['overall_stats']['comprank']
        )
        em.add_field(name='Competitive Win Rate', value=cmpwinrate)
        em.add_field(name='Quickplay Wins', value=qp['overall_stats']['wins'])
        timeplayed = qp['game_stats']['time_played'] + comp['game_stats']['time_played']
        em.add_field(name='Total Playtime', value=str(int(timeplayed)) + " hours")

        return em


    @commands.command(pass_context=True)
    async def owstats(self, ctx, *, tag: str):
        """ Usage: owstats [region] [battletag]\nRegions: kr, eu, us"""
        splitstr = tag.split(sep=' ')
        print(splitstr)
        if len(splitstr) != 2:
            await self.bot.say("```Usage: owstats [region] [battletag]\nRegions: kr, eu, us```")
            return
        region = splitstr[0].lower()
        if len(region) != 2:
            await self.bot.say("```Usage: owstats [region] [battletag]\nRegions: kr, eu, us```")
            return
        tag = splitstr[1]
        if '#' in tag:
            tag = tag.replace('#', '-')

        headers = {
            'User-Agent': 'KoyomiBot for Discord.',
            'From': 'firefwing42@gmail.com'
        }

        async with self.bot.session.get('https://owapi.net/api/v3/u/' + tag + '/stats', headers=headers) as r:
            if r.status != 200:
                self.bot.cogs['Log'].output('OWApi.net failed to connect.')
                return
            profile = await r.json()
            profile = profile[region]['stats']
            quick = profile['quickplay']
            comp = profile['competitive']
            await self.bot.say(embed=self.display(ctx.message.author, tag, quick, comp))
        self.bot.cogs['Wordcount'].cmdcount('owstats')

    @commands.command()
    async def owrng(self):
        """ RNG OVERWATCH """
        await self.bot.say("Play {}!".format(random.choice(self.heroes)))
        self.bot.cogs['Wordcount'].cmdcount('owrng')

    @commands.command()
    async def owteam(self, num: int = 6):
        """ Get a random OW Team \nUsage: owteam [Optional: Teamsize]"""
        random.shuffle(self.heroes)
        result = self.heroes[:num]
        await self.bot.say("Here's your teamcomp! Good luck!\n" +
                           "{}".format(", ".join(result)))
        self.bot.cogs['Wordcount'].cmdcount('owteam')



def setup(bot):
    """ Setup OW Module"""
    bot.add_cog(Overwatch(bot))
