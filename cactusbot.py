# Copyright (c) 2016 636F57@GitHub
# This software is released under an MIT license.
# See LICENSE for full details.

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
from cactusconsts import CactusConsts
import traceback

if not discord.opus.is_loaded():      #this is necessary for voice activities
	discord.opus.load_opus('libopus-0.dll')
print("opus dll is loaded = ", discord.opus.is_loaded())

description = '''Utility Bot custom-made for this server. :cactus:'''
bot = commands.Bot(command_prefix='#', description=description)
	
#global variants for music
g_listEcho = []
Mee6_ID = CactusConsts.Mee6_ID

fredboadPrefix = ";;play "
marshmallowPrefix = ":request "

#global variants for RSS
g_RSSdictkey = ["index", "url", "lastModified", "eTag", "lastcheck", "channel_ID", "userID"]
filenameRSS = "RSSdata"  #RSSdata format: "index","url","lastModified","eTag","lastcheck","channel_ID","userID"\n  for each entry
g_session = aiohttp.ClientSession()
g_intervalhours = 0.5 # RSS check interval in hours
		
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
			if CactusConsts.Mee6_notfound_msg in message.content:
				print("canceling 1 echo")
				g_listEcho.pop(0)
			elif 'youtu' in message.content:
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
	with open(strFile, "rt") as f:
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
# return the channel ID of the given name in the server
# return "" when not found
def get_channel_ID(bot, server_ID, channel_name):
	if channel_name == "":
		return ""
	for channel in bot.get_server(server_ID).channels:
		if channel.name == channel_name:
			return channel.id
	return ""
	
def read_rssfile():
	global g_RSSdictkey
	listRSSdict = []
	with open(filenameRSS, "rt") as f:
		for line in f:
			if len(line) > 1:
				line = line.lower()
				listRSSdict.append(dict(zip(g_RSSdictkey, line.strip().split(','))))
	return listRSSdict

def max_index_of_rssfile():
	max_index = 0
	listRSSdict = read_rssfile()
	if len(listRSSdict) > 0:
		max_index = listRSSdict[len(listRSSdict)-1]["index"]  #assume the last entry always has the max index
	return max_index

def write_rssfile(listRSSdict):
	global g_RSSdictkey
	with open(filenameRSS, "wt") as f:
		for rss in listRSSdict:
			line = ""
			for key in g_RSSdictkey:
				line += str(rss[key]) + ","
			f.write(line[:-1]+"\n")
		print("successfully wrote listRSSdict to the file.")
	return

@bot.command(pass_context=True)
async def rss_add_reddit(ctx):
	"""Specify the subreddit name and channel name. Add the subreddit to RSS check-list."""
	command,sub,channel_name = ctx.message.content.split(' ')
	line = str(int(max_index_of_rssfile())+1)+",https://www.reddit.com/r/"+ sub +"/.rss,,,"+str(int(time.time()))
	channelID = get_channel_ID(bot, ctx.message.server.id, channel_name)
	print("CACTUS ROOMS SERVER ID:",ctx.message.server.id)
	if channelID == "":
		channelID = ctx.message.channel.id
	line += ","+ channelID + "\n"
	with open(filenameRSS, "a+") as f:
		f.write(line)
	await bot.say(":cactus:"+sub+" was added to RSS list.:cactus:")

@bot.command(pass_context=True)
async def rss_add_github(ctx):
	"""Specify github repo URL and channel name. Add the repo to RSS check-list."""
	command,url,channel_name = ctx.message.content.split(' ')
	if not 'github' in url:
		await bot.say("It is not GitHub URL.")
		return		
	with open(filenameRSS, "a+") as f:
		if url[len(url)-1] != '/':
			url += '/'
		line = str(int(max_index_of_rssfile())+1)+","+url+"commits/master.atom,,,"+str(int(time.time()))
		channelID = get_channel_ID(bot, ctx.message.server.id, channel_name)
		if channelID == "":
			channelID = ctx.message.channel.id
		line += ","+ channelID + "\n"
		f.write(line)
	await bot.say(":cactus:"+url+" was added to RSS list.:cactus:")
	
@bot.command(pass_context=True)
async def rss_list(ctx):
	"""List all the RSS URLs requested by you."""
	bAll = False
	# only server owner can see all the URLs in the list
	if ctx.message.author.id == ctx.message.server.owner.id:
		bAll = True
	listRSSdict = read_rssfile()
	if len(listRSSdict) == 0:
		await bot.say("There is no URL in the list.")
	for rss in listRSSdict:
		if bAll or ctx.message.author.id == rss["userID"]:
			channel_name = bot.get_channel(rss["channel_ID"]).name
			await bot.say(rss["index"]+" : " + rss["url"] +" to #" + channel_name)  #list index, URL, and channel to cat
		
@bot.command()
async def rss_del(index):
	"""Delete the specified index entry from RSS check-list."""
	listRSSdict = read_rssfile()
	output = []
	for rss in listRSSdict:
		if rss["index"] != index:
			output.append(rss)
	write_rssfile(output)
	if len(output) < len(listRSSdict):
		await bot.say(index+" was deleted.")
	else:
		await bot.say(index+" was not found in the list.")

# function that is called as a task to fetch and report RSS updates
async def checkRSS(bot):
	global g_RSSdictkey
	global g_session
	while not bot.is_closed:
		print("now in checkRSS.")
		while bot.is_logged_in:
			print("now start checking RSS updates...")
			listRSSdict = read_rssfile()
			if len(listRSSdict) == 0:
				print("no RSS urls found.")
			else:				
				header = {'User-Agent':CactusConsts.UserAgentName}
				
				for rss in listRSSdict:
					rss_backup = rss
					try:
						print("checking RSS of ", rss["url"])
						if len(rss["lastModified"]) > 0:
							header['If-Modified-Since'] = rss["lastModified"]   #Last-Modified
						if len(rss["eTag"]) > 0:
							header['If-None-Match'] = rss["eTag"]	     		#ETAG
						response = await g_session.get(rss["url"], headers = header)
						print("response status=",response.status)
						if response.status == 304:
							print("no update for ", rss["url"])
						elif response.status == 200:
							#print(response.headers)
							if 'LAST-MODIFIED' in response.headers:
								rss["lastModified"] = response.headers['LAST-MODIFIED']
							else:
								rss["lastModified"] = ""
							if 'ETAG' in response.headers:
								rss["eTag"] = response.headers['ETAG']
							else:
								rss["eTag"] = ""
							body = await response.read()
							soup = BeautifulSoup(body, 'lxml')
							entries = soup.find_all('entry')
							if 'reddit' in rss["url"]:
								await process_reddit(bot, entries, rss["lastcheck"], bot.get_channel(rss["channel_ID"]))
							elif 'github' in rss["url"]:
								await process_github(bot, entries, rss["lastcheck"], bot.get_channel(rss["channel_ID"]))
						else:
							await bot.say("Failed to get RSS feed from the server. " + rss["url"])
						response.close()
						rss["lastcheck"] = int(time.time())
					except:
						rss = rss_backup
						print("error in checkRSS:",rss["url"])
						print(traceback.format_exc())
			write_rssfile(listRSSdict)		
			await asyncio.sleep(g_intervalhours*3600)
		await asyncio.sleep(30) #wait 30 seconds then retry

# functions which actrually parse the HTML and make the bot say the results
async def process_reddit(bot, entries, lastcheck, channel):
	for entry in entries:
		if is_updated(entry.find('updated').text, lastcheck):
			postcat = entry.find('category')
			#print(postcat)
			strSay = ":cactus:*New Post at " + postcat['term'] + ' (' + postcat['label'] + ')*:cactus:\n\n'
			strSay += "**Title : " + entry.find('title').text + '**\n'
			#print(entry.find('content').text)
			postcontent = html.unescape(entry.find('content').text)
			#print(postcontent)
			postcontent = BeautifulSoup(postcontent, 'lxml')
			urlcontent = postcontent.find_all('a')
			#print(urlcontent)
			for url in urlcontent:
				if '[comments]' in url:
					strSay += url['href'] + "\n"
					break
			print(strSay)
			await bot.send_message(channel, strSay)

async def process_github(bot, entries, lastcheck, channel):
	for entry in entries:
		#print(entry)
		if is_updated(entry.find('updated').text, lastcheck) :
			author = entry.find('author')
			strSay = ":cactus:*New Commit at GitHub by " + author.find('name').text + '*:cactus:\n\n'
			strSay += "**Comment : " + entry.find('title').text + '**\n'
			strSay += entry.find('link')['href']
			print(strSay)
			await bot.send_message(channel, strSay)

# updatedtime should be in the format like: 2016-11-11 12:38:34 +0200  #changed 3rd.dec.2016
# lastcheck is the string which is stored in RSSfile		
def is_updated(updatedtime, lastcheck):
	print(updatedtime)
	shiftsec = 0
	if '+' in updatedtime:
		times = updatedtime.split('+')
		updatedtime = times[0]
		shifttimes = times[1][:2]
		shiftsec = int(shifttimes[0]) * 3600 + int(shifttimes[1]) * 60
	sttime = time.strptime(updatedtime, "%Y-%m-%d %H:%M:%S ")
	updated_insec = calendar.timegm(sttime) - shiftsec
	print ("updated, since = ",updated_insec, lastcheck)
	if updated_insec < int(lastcheck):
		return False
	else:
		return True
		
#######################

##### Others  #########
@bot.command()
async def test():
	"""command for test and debug"""
	await bot.say("RSS test started.")
	await checkRSS(bot)

######################################

loop = asyncio.get_event_loop()
try:
	loop.create_task(checkRSS(bot))
	loop.run_until_complete(bot.start(CactusConsts.CactusBot_Token))
	
except KeyboardInterrupt:
	loop.run_until_complete(bot.logout())
	# cancel all tasks lingering
	tasks = asyncio.Task.all_tasks(loop)
	for task in tasks:
		task.cancel()
finally:
	loop.close()
	if g_session:
		g_session.close()
