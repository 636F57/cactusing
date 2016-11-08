import discord
from discord.ext import commands
import random
import glob
from os.path import basename
import time

if not discord.opus.is_loaded():
	discord.opus.load_opus('libopus-0.dll')
print("opus dll is loaded = ", discord.opus.is_loaded())

description = '''Utility Bot custom-made for this CACTUS ROOMS server. :slight_smile:'''
bot = commands.Bot(command_prefix='#', description=description)
	
nShouldEchoNum = 0
cmdPrefix = ""
Mee6_ID = "159985870458322944"

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')

@bot.event
async def on_message(message):	
	print("on message : ", message.content, message.author.name, message.author.id)
	global nShouldEchoNum
	global cmdPrefix
	if (message.author.id == Mee6_ID):
		print("message by Mee6")
		if nShouldEchoNum > 0:
			print(message.content)
			if 'youtu' in message.content:
				print("in echo")
				await bot.send_message(message.channel, cmdPrefix +' '+ message.content)
				nShouldEchoNum -= 1
				if nShouldEchoNum < 0:
					nShouldEchoNum = 0
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
	global nShouldEchoNum
	global cmdPrefix
	if number > 5:
		await bot.say("Maximun queue is limited to 5 songs.")
		number = 5		
	nShouldEchoNum += number
	cmdPrefix = ";;play"
	print("category = ", category)
	strFile = "./Songs/" + category + ".txt"
	f = open(strFile, "rt")
	listSongs = f.readlines()
	print("list length = ", len(listSongs))
	for i in range(number):
		strCommand = "!youtube " + listSongs[random.randint(0, len(listSongs)-1)] + "\n"
		await bot.say(strCommand)
	f.close()

@bot.command()
async def feedm(number : int, category='favorite'):
	"""Feed number of songs to Marshmallow, randomly selecting from the txt file."""
	global nShouldEchoNum
	global cmdPrefix
	if number > 5:
		await bot.say("Maximun queue is limited to 5 songs.")
		number = 5		
	nShouldEchoNum += number
	cmdPrefix = ":request"
	print("category = ", category)
	strFile = "./Songs/" + category + ".txt"
	f = open(strFile, "rt")
	listSongs = f.readlines()
	print("list length = ", len(listSongs))
	for i in range(number):
		strCommand = "!youtube " + listSongs[random.randint(0, len(listSongs)-1)] + "\n"
		await bot.say(strCommand)
		time. sleep(8)       # since requests to marshmallow must have 10sec intervals
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
		strCommand = ";;play " + listURLs[random.randint(0, len(listURLs)-1)] + "\n"
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
		strCommand = ":request " + listURLs[random.randint(0, len(listURLs)-1)] + "\n"
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
	await bot.say("!youtube " + text)

@bot.command()
async def ytf(text):
	"""Feed search result to FredBoat."""
	global nShouldEchoNum
	await bot.say("!youtube " + text)
	nShouldEchoNum += 1
	
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
