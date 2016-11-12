### NOTE: This is based on the example file "basic_bot.py" included in the discord.py project.
###  (https://github.com/Rapptz/discord.py/blob/master/examples/basic_bot.py)

import discord
from discord.ext import commands
import random
import glob
from os.path import basename
import time
import aiohttp
import re
import beautifulsoup

if not discord.opus.is_loaded():      #this is needed for voice activities
	discord.opus.load_opus('libopus-0.dll')
print("opus dll is loaded = ", discord.opus.is_loaded())

description = '''Utility Bot custom-made for this CACTUS ROOMS server. :slight_smile:'''
bot = commands.Bot(command_prefix='#', description=description)
	
#global variants for music
g_listEcho = []
Mee6_ID = "159985870458322944"
fredboadPrefix = ";;play "
marshmallowPrefix = ":request "

#global variants for RSS
g_listRSS = []
filenameRSS = "RSSdata"  #RSSdata format: "index","url","lastModified","eTag"\n  for each entry


async def getRSS(bot):
	global g_listRSS
	f = fopen(filenameRSS, "rt")
	g_listRSS.clear()
	for line in f:
		g_listRSS.append(line.split(','))
	f.close()
	
	if len(g_listRSS) == 0:
		print("no RSS urls found.")
		return
		
	header = {'User-Agent':'CactusBot'}
	async session = aiohttp.ClientSession()
	
	for rss in g_listRSS:
		if len(g_listRSS[2]) > 0:
			header['If-Modified-Since'] = g_listRSS[2]   #Last-Modified
		if len(g_listRSS[3]) > 0:
			header['If-None-Match'] = g_listRSS[3]	     #ETAG
		response = await session.get(rss[1], headers = header)
		if response.status == 304:
			print("no update for ", rss[1])
		elif response.status == 200:
			print(response.headers)
			matches = re.search(r"'LAST-MODIFIED':'.*?'", response.headers)
			if len(matches) > 0:
				g_listRSS[2] = matches.group(0)
			else:
				g_listRSS[2] = ""
			matches = re.search(r"'ETAG':'.*?'", response.headers)
			if len(matches) > 0:
				g_listRSS[3] = matches.group(0)
			else:
				g_listRSS[3] = ""
			body = await response.read()
			soup = beautifulsoup(body)
			await bot.say(body)
	
	f = fopen(filenameRSS, "wt")
	for line in g_listRSS:
		g_listRSS.append(line.split(','))
	f.close()

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')

####  For music utility  ####
@bot.event
async def on_message(message):	
	print("on message : ", message.content, message.author.name, message.author.id)
	global g_listEcho
	if (message.author.id == Mee6_ID):
		print("message by Mee6")
		if len(g_listEcho) > 0:
			print(message.content)
			if 'youtu' in message.content:
				print("in echo")
				await bot.send_message(message.channel, g_listEcho[0] + message.content)
				g_listEcho.pop(0)
				if (len(g_listEcho) > 0 ) & (g_listEcho[0] == marshmallowPrefix):
						time. sleep(10)       # since requests to marshmallow must have 10sec intervals
	else:				
		await bot.process_commands(message)
	
@bot.command()
async def songfiles():
	"""List the available songlist category options."""
	strList = ""
	fileList = glob.glob("./Songs/*.txt")
	if len(fileList) == 0:
		strList = "No file found."
	else:
		for file in fileList:
			strList += basename(file) + " "
	await bot.say(strList)	

@bot.command()
async def feeda(number : int, category='favorite'):
	"""Feed number of songs to Aethex, randomly selecting from the txt file."""
	if number > 5:
		await bot.say("Maximun queue is limited to 5 songs.")
		number = 5
	print("category = ", category)
	strFile = "./Songs/" + category + ".txt"
	f = open(strFile, "rt")
	listSongs = f.readlines()
	print("list length = ", len(listSongs))
	for i in range(number):
		strCommand = "-play " + listSongs[random.randint(0, len(listSongs)-1)] + "\n"
		await bot.say(strCommand)
	f.close()

@bot.command()
async def feedf(number : int, category='favorite'):
	"""Feed number of songs to FredBoat, randomly selecting from the txt file."""
	global g_listEcho
	if number > 5:
		await bot.say("Maximun queue is limited to 5 songs.")
		number = 5		
	print("category = ", category)
	strFile = "./Songs/" + category + ".txt"
	f = open(strFile, "rt")
	listSongs = f.readlines()
	print("list length = ", len(listSongs))
	for i in range(number):
		strCommand = "!youtube " + listSongs[random.randint(0, len(listSongs)-1)] + "\n"
		await bot.say(strCommand)
		g_listEcho.append(fredboadPrefix)
	f.close()

@bot.command()
async def feedm(number : int, category='favorite'):
	"""Feed number of songs to Marshmallow, randomly selecting from the txt file."""
	global g_listEcho
	if number > 5:
		await bot.say("Maximun queue is limited to 5 songs.")
		number = 5		
	print("category = ", category)
	strFile = "./Songs/" + category + ".txt"
	f = open(strFile, "rt")
	listSongs = f.readlines()
	print("list length = ", len(listSongs))
	for i in range(number):
		strCommand = "!youtube " + listSongs[random.randint(0, len(listSongs)-1)] + "\n"
		await bot.say(strCommand)
		g_listEcho.append(marshmallowPrefix)
	f.close()
	
@bot.command()
async def feedf_url(number : int):
	"""Feed number of URLs to FredBoat, randomly selecting from the FavoriteURLs file."""
	if number > 5:
		await bot.say("Maximun queue is limited to 5 songs.")
		number = 5		
	strFile = "./Songs/FavoriteURLs"
	f = open(strFile, "rt")
	listURLs = f.readlines()
	print("list length = ", len(listURLs))
	for i in range(number):
		strCommand = fredboadPrefix + listURLs[random.randint(0, len(listURLs)-1)] + "\n"
		await bot.say(strCommand)
	f.close()

@bot.command()
async def feedm_url(number : int):
	"""Feed number of URLs to Marshmallow, randomly selecting from the FavoriteURLs file."""
	if number > 5:
		await bot.say("Maximun queue is limited to 5 songs.")
		number = 5		
	strFile = "./Songs/FavoriteURLs"
	f = open(strFile, "rt")
	listURLs = f.readlines()
	print("list length = ", len(listURLs))
	for i in range(number):
		strCommand = marshmallowPrefix + listURLs[random.randint(0, len(listURLs)-1)] + "\n"
		await bot.say(strCommand)
		time. sleep(9)       # since requests to marshmallow must have 10sec intervals
	f.close()

@bot.command()
async def favor(song):
	"""Add the song to Favorite.txt file."""
	if song == "":
		await bot.say("You must specify the song to add.")
	f = open("./Songs/Favorite.txt", "a+")
	f.write(song + "\n")
	f.close()
	await bot.say(song + " is added. :smile:")

@bot.command()
async def favor_url(url):
	"""Add the URL to FavoriteURLs file."""
	if url == "":
		await bot.say("You must specify the URL to add.")
	f = open("./Songs/FavoriteURLs", "a+")
	f.write(url + "\n")
	f.close()
	await bot.say(url + " is added. :smile:")

#############################

####  For RSS utility   #####
@bot.command()
async def rss_add(url):
	"""Add URL to RSS check-list."""
	f = fopen(filenameRSS, "a+")
	lines = f.readlines()
	max_index = lines[len(lines)-1].split(').[0]
	print("maxindex was ", max_index)
	f.write(str(int(max_index)+1)+url+",,")
	f.close()
	await bot.say(url+" was added to RSS list.:slight_smile:")

@bot.command()
async def rss_list():
	"""List all the URLs of RSS check-list."""
	f = fopen(filenameRSS, "rt")
	lines = f.readlines()
	for line in lines:
		items = line.split(',')
		await bot.say(items[0]+": " + items[1])  #list index and URL
	f.close()
	
@bot.command()
async def rss_del(index):
	"""Delete the specified URL from RSS check-list."""
	f = fopen(filenameRSS, "rt")
	lines = f.readlines()
	f.close()
	output = []
	for line in lines:
		items = line.split(',')
		if items[0] != index:
			output.append(line)
	f = fopen(filenameRSS, "wt")
	for line in output:
		f.write(line)
	f.close()
	if len(output) < len(lines):
		await bot.say(index+" was deleted.")
	else
		await bot.say(index+" was not found in the list.")

#######################

##### Others  #########
@bot.command()
async def test():
	"""command for test and debug"""
	await bot.say("!rank")
	await bot.say(":help")
	await bot.say(";;help")

@bot.command(pass_context=True)
async def join(ctx):
	"""Let CactusBot to join the voice channel."""
	print(ctx.message.author)
	voiceclient = bot.voice_client_in(ctx.message.server)
	print(ctx.message.server)
	if voiceclient == None:
		print(ctx.message.author.voice.voice_channel)
		await bot.join_voice_channel(ctx.message.author.voice.voice_channel)
	elif voiceclient.channel != ctx.message.channel:
		await voiceclient.move_to(ctx.message.channel)
		

@bot.command()
async def ytm(text):
	"""Feed search result to Marshmallow."""
	global g_listEcho
	await bot.say("!youtube " + text)
	g_listEcho.append(marshmallowPrefix)
	
@bot.command()
async def ytf(text):
	"""Feed search result to FredBoat."""
	global g_listEcho
	await bot.say("!youtube " + text)
	g_listEcho.append(fredboadPrefix)
	
@bot.command()
async def add(left : int, right : int):
	"""Adds two numbers together."""
	await bot.say(left + right)

@bot.command()
async def roll(dice : str):
	"""Rolls a dice in NdN format."""
	try:
		rolls, limit = map(int, dice.split('d'))
	except Exception:
		await bot.say('Format has to be in NdN!')
		return

	result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
	await bot.say(result)

@bot.command(description='For when you wanna settle the score some other way')
async def choose(*choices : str):
	"""Chooses between multiple choices."""
	await bot.say(random.choice(choices))

@bot.command()
async def repeat(times : int, content='repeating...'):
	"""Repeats a message multiple times."""
	for i in range(times):
		await bot.say(content)

@bot.command()
async def joined(member : discord.Member):
	"""Says when a member joined."""
	await bot.say('{0.name} joined in {0.joined_at}'.format(member))

@bot.group(pass_context=True)
async def cool(ctx):
	"""Says if a user is cool.
	In reality this just checks if a subcommand is being invoked.
	"""
	if ctx.invoked_subcommand is None:
		await bot.say('No, {0.subcommand_passed} is not cool'.format(ctx))

@cool.command(name='bot')
async def _bot():
	"""Is the bot cool?"""
	await bot.say('Yes, the bot is cool.')

bot.run('MjQ1MzUyODMyNzEzMjI4Mjg5.CwK2Kg.kh-PkKal3nO8lA3cEEgGxZ4eBkA')
