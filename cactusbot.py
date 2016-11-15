### NOTE: This is based on the example file "basic_bot.py" included in the discord.py project.
###  (https://github.com/Rapptz/discord.py/blob/master/examples/basic_bot.py)

import discord
from discord.ext import commands
import random
import glob
from os.path import basename
import time
import aiohttp
from bs4 import BeautifulSoup
import asyncio
import html
import calendar

if not discord.opus.is_loaded():      #this is needed for voice activities
	discord.opus.load_opus('libopus-0.dll')
print("opus dll is loaded = ", discord.opus.is_loaded())

description = '''Utility Bot custom-made for this CACTUS ROOMS server. :cactus:'''
bot = commands.Bot(command_prefix='#', description=description)
	
#global variants for music
g_listEcho = []
Mee6_ID = "159985870458322944"
fredboadPrefix = ";;play "
marshmallowPrefix = ":request "

#global variants for RSS
g_listRSS = []
filenameRSS = "RSSdata"  #RSSdata format: "index","url","lastModified","eTag"\n  for each entry
g_session = aiohttp.ClientSession()
g_interval = 2
		
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
						await asyncio.sleep(10)       # since requests to marshmallow must have 10sec intervals
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
	open(strFile, "rt") as f:
		listSongs = f.readlines()
		print("list length = ", len(listSongs))
		for i in range(number):
			strCommand = "-play " + listSongs[random.randint(0, len(listSongs)-1)] + "\n"
			await bot.say(strCommand)

@bot.command()
async def feedf(number : int, category='favorite'):
	"""Feed number of songs to FredBoat, randomly selecting from the txt file."""
	global g_listEcho
	if number > 5:
		await bot.say("Maximun queue is limited to 5 songs.")
		number = 5		
	print("category = ", category)
	strFile = "./Songs/" + category + ".txt"
	with open(strFile, "rt") as f:
		listSongs = f.readlines()
		print("list length = ", len(listSongs))
		for i in range(number):
			strCommand = "!youtube " + listSongs[random.randint(0, len(listSongs)-1)] + "\n"
			await bot.say(strCommand)
			g_listEcho.append(fredboadPrefix)

@bot.command()
async def feedm(number : int, category='favorite'):
	"""Feed number of songs to Marshmallow, randomly selecting from the txt file."""
	global g_listEcho
	if number > 5:
		await bot.say("Maximun queue is limited to 5 songs.")
		number = 5		
	print("category = ", category)
	strFile = "./Songs/" + category + ".txt"
	with open(strFile, "rt") as f:
		listSongs = f.readlines()
		print("list length = ", len(listSongs))
		for i in range(number):
			strCommand = "!youtube " + listSongs[random.randint(0, len(listSongs)-1)] + "\n"
			await bot.say(strCommand)
			g_listEcho.append(marshmallowPrefix)
	
@bot.command()
async def feedf_url(number : int):
	"""Feed number of URLs to FredBoat, randomly selecting from the FavoriteURLs file."""
	if number > 5:
		await bot.say("Maximun queue is limited to 5 songs.")
		number = 5		
	strFile = "./Songs/FavoriteURLs"
	with open(strFile, "rt") as f:
		listURLs = f.readlines()
		print("list length = ", len(listURLs))
		for i in range(number):
			strCommand = fredboadPrefix + listURLs[random.randint(0, len(listURLs)-1)] + "\n"
			await bot.say(strCommand)

@bot.command()
async def feedm_url(number : int):
	"""Feed number of URLs to Marshmallow, randomly selecting from the FavoriteURLs file."""
	if number > 5:
		await bot.say("Maximun queue is limited to 5 songs.")
		number = 5		
	strFile = "./Songs/FavoriteURLs"
	with open(strFile, "rt") as f:
		listURLs = f.readlines()
		print("list length = ", len(listURLs))
		for i in range(number):
			strCommand = marshmallowPrefix + listURLs[random.randint(0, len(listURLs)-1)] + "\n"
			await bot.say(strCommand)
			time. sleep(9)       # since requests to marshmallow must have 10sec intervals

@bot.command()
async def favor(song):
	"""Add the song to Favorite.txt file."""
	if song == "":
		await bot.say("You must specify the song to add.")
	with open("./Songs/Favorite.txt", "a+") as f:
		f.write(song + "\n")
	await bot.say(song + " is added. :cactus:")

@bot.command()
async def favor_url(url):
	"""Add the URL to FavoriteURLs file."""
	if url == "":
		await bot.say("You must specify the URL to add.")
	with open("./Songs/FavoriteURLs", "a+") as f:
		f.write(url + "\n")
	await bot.say(url + " is added. :cactus:")

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

#############################

####  For RSS utility   #####
@bot.command()
async def rss_add_reddit(sub):
	"""Specify the subreddit name. Add the subreddit to RSS check-list."""
	with open(filenameRSS, "a+") as f:
		lines = f.readlines()
		max_index = 0
		if len(lines) > 0:
			max_index = (lines[len(lines)-1].split(','))[0]
		print("maxindex was ", max_index)
		f.write(str(int(max_index)+1)+",https://www.reddit.com/r/"+sub+"/.rss,,\n")
	await bot.say(url+" was added to RSS list.:cactus:")

@bot.command()
async def rss_add_github(url):
	"""Specify the URL of github repo. Add the repo to RSS check-list."""
	if not 'github' in url:
		await bot.say("It is not GitHub URL.")
		return		
	with open(filenameRSS, "a+") as f:
		lines = f.readlines()
		max_index = 0
		if len(lines) > 0:
			max_index = (lines[len(lines)-1].split(','))[0]
		print("maxindex was ", max_index)
		if url[len(url)-1] != '/':
			url += '/'
		f.write(str(int(max_index)+1)+","+url+"commits/master.atom,,\n")
	await bot.say(url+" was added to RSS list.:cactus:")
	
@bot.command()
async def rss_list():
	"""List all the URLs of RSS check-list."""
	with open(filenameRSS, "rt") as f:
		lines = f.readlines()
		if len(lines) == 0:
			await bot.say("There is no URL in the list.")
		for line in lines:
			items = line.split(',')
			await bot.say(items[0]+" : " + items[1])  #list index and URL
	
@bot.command()
async def rss_del(index):
	"""Delete the specified URL from RSS check-list."""
	with open(filenameRSS, "rt") as f:
		lines = f.readlines()
	output = []
	for line in lines:
		items = line.split(',')
		if items[0] != index:
			output.append(line)
	with open(filenameRSS, "wt") as f:
		for line in output:
			f.write(line)
	if len(output) < len(lines):
		await bot.say(index+" was deleted.")
	else:
		await bot.say(index+" was not found in the list.")

# function that is called as a task to fetch and report RSS updates
async def checkRSS(bot):
	global g_listRSS
	global g_session
	global g_interval
	with open(filenameRSS, "rt") as f:
		g_listRSS.clear()
		for line in f:
			g_listRSS.append(line.split(','))
	
	if len(g_listRSS) == 0:
		print("no RSS urls found.")
		return
		
	header = {'User-Agent':'CactusBot'}
	
	for rss in g_listRSS:
		if len(rss[2]) > 0:
			header['If-Modified-Since'] = rss[2]   #Last-Modified
		if len(rss[3]) > 0:
			header['If-None-Match'] = rss[3]	     #ETAG
		response = await g_session.get(rss[1], headers = header)
		print("response status=",response.status)
		if response.status == 304:
			print("no update for ", rss[1])
		elif response.status == 200:
			#print(response.headers)
			if 'LAST-MODIFIED' in response.headers:
				rss[2] = response.headers['LAST-MODIFIED']
			else:
				rss[2] = ""
			if 'ETAG' in response.headers:
				rss[3] = response.headers['ETAG']
			else:
				rss[3] = ""
			body = await response.read()
			soup = BeautifulSoup(body, 'lxml')
			entries = soup.find_all('entry')
			print (len(entries))
			if 'reddit' in g_listRSS[1]:
				process_reddit(bot, entries, g_interval)
			elif 'vbparadise' in g_listRSS[1]:

			elif 'github' in g_listRSS[1]:
				process_github(bot, entries, g_interval)
			
	with open(filenameRSS, "wt") as f:
		for line in g_listRSS:
			f.write(','.join(line))
			
	await asyncio.sleep(g_interval)

# functions which actrually parse the HTML and make the bot say the results
async def process_reddit(bot, entries, interval):
	for entry in entries:
		if is_updated(entry.find('updated').text, interval):
			postcat = entry.find('category')
			#print(postcat)
			strSay = "*New Post at " + postcat['term'] + ' (' + postcat['label'] + ')*\n\n'
			strSay += "**Title : " + entry.find('title').text + '**\n'
			#print(entry.find('content').text)
			postcontent = html.unescape(entry.find('content').text)
			print(postcontent)
			postcontent = BeautifulSoup(postcontent)
			urlcontent = postcontent.find_all('a')
			print(urlcontent)
			for url in urlcontent:
				if '[comments]' in url:
					strSay += url['href'] + "\n"
					break
			await bot.say(strSay)

async def process_github(bot, entries, interval):
	for entry in entries:
		#print(entry)
		if is_updated(entry.find('updated').text, interval) :
			strSay = "*New Commit at GitHub by " + entry.author.name.text + '*\n\n'
			strSay += "**Title : " + entry.find('title').text + '**\n'
			strSay += entry.find('link').text			
			await bot.say(strSay)

# updatedtime should be in the format like: 2016-11-11T12:38:34+02:00			
def is_updated(updatedtime, backhours):
	shiftsec = 0
	if '+' in updatetime:
		times = updatedtime.split('+')
		updatedtime = times[0]
		shifttimes = times[1].split(':')
		shiftsec = int(shifttimes[0]) * 360 + int(shifttimes[1]) * 60
	sttime = time.strptime(updatedtime, "%Y-%m-%dT%H:%M:%S")
	updated_insec = calendar.gmtime(sttime) - shiftsec
	since_insec = time.time() - backhours*360
	if updated_insec < since_insec:
		return false
	else
		return true
		
#######################

##### Others  #########
@bot.command()
async def test():
	"""command for test and debug"""
	await bot.say("RSS test started.")
	await checkRSS(bot)
	

	
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

######################################

loop = asyncio.get_event_loop()
try:
	#loop.create_task(checkRSS(bot))
	loop.run_until_complete(bot.start('MjQ1MzUyODMyNzEzMjI4Mjg5.CwK2Kg.kh-PkKal3nO8lA3cEEgGxZ4eBkA'))
except KeyboardInterrupt:
	loop.run_until_complete(bot.logout())
	# cancel all tasks lingering
	tasks = asyncio.all_tasks(loop)
	for task in tasks:
		task.cancel()
finally:
	loop.close()
	if g_session:
		g_session.close()
