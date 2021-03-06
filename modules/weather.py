""" Weather Module"""

from discord.ext import commands

from utility import discordembed as dmbd

class Weather:
    """ Get the Weather"""
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def discordicon(icon):
        """ Return the correlating Discord Emote"""
        icons = {
            'clear-day': ':sunny:',
            'clear-night': ':crescent_moon:',
            'rain': ':cloud_rain:',
            'snow': ':cloud_snow:',
            'sleet': ':snowflake:',
            'wind': ':dash:',
            'fog': ':cloud:',
            'cloudy': ':cloud:',
            'partly-cloudy-day': ':partly_sunny:',
            'partly-cloudy-night': ':partly_sunny:'
        }
        if icon in icons:
            return icons[icon]
        else:
            return ""

    async def getgoogle(self, search):
        key = self.bot.redis_db.get('GoogleMapsAPI').decode('utf-8')
        url = (
            "https://maps.googleapis.com/maps/api/geocode/json?address=" +
            search.replace(" ", "+") + "&key=" + key
        )

        async with self.bot.session.get(url) as r:
            if r.status != 200:
                await self.bot.say("GoogleGeoCode is down")
                return
            return await r.json()

    async def getdarksky(self, lat, lng):
        key = self.bot.redis_db.get('DarkSkyAPI').decode('utf-8')
        url = (
            "https://api.darksky.net/forecast/" + key +
            "/" + str(lat) + "," + str(lng) + "?exclude=minutely,hourly,daily,alerts,flags"
        )

        async with self.bot.session.get(url) as r:
            if r.status != 200:
                await self.bot.say('DarkSky is down')
                return
            return await r.json()

    def display(self, author, place, darksky):
        curr = darksky["currently"]
        title = "Powered by GoogleGeoCode and DarkSky"
        desc = (
            self.discordicon(curr['icon']) + " It is " + curr['summary'] +
            " in " + place
        )
        deg = u' \N{DEGREE SIGN}F'
        em = dmbd.newembed(author, title, desc)
        em.add_field(name='Temperature', value=str(curr['temperature']) + deg)
        em.add_field(name='Feels Like', value=str(curr['apparentTemperature']) + deg)
        em.add_field(
            name='Precipitation', value=str(
                curr['precipProbability'] * 100
            ) + "% chance of " + (
                curr['precipType'] if 'precipType' in curr else "rain"
            )
        )

        em.add_field(name='Humidity', value=str(curr['humidity'] * 100)[:4] + "%")

        return em


    @commands.command(pass_context=True)
    async def weather(self, ctx, *, search: str):
        """ Grab the weather using GoogleGeoCodeAPI and DarkSkyAPI"""

        location = await self.getgoogle(search)

        if location["status"] == "OK":
            lat = location["results"][0]["geometry"]["location"]["lat"]
            lng = location["results"][0]["geometry"]["location"]["lng"]
            place = location["results"][0]["address_components"][0]["long_name"]
            darksky = await self.getdarksky(lat, lng)

            await self.bot.say(embed=self.display(ctx.message.author, place, darksky))
            self.bot.cogs['Wordcount'].cmdcount('weather')
            return
        else:
            self.bot.cogs['Log'].output("Status Error: " + location["status"])
            return

def setup(bot):
    bot.add_cog(Weather(bot))
