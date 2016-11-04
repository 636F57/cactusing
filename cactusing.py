import discord
from discord.ext import commands
import random
import glob
from os.path import basename
 
description = '''An example bot to showcase the discord.ext.commands extension module. \
There are a number of utility commands being showcased here.'''
bot = commands.Bot(command_prefix='!', description=description)
	
@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')

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
async def feed(number : int, category='favorite'):
	"""Feed number of song titles to Aethex, randomly selecting from the txt file."""
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
async def favor(song):
	"""Add the song to Favorite.txt file."""
	if song == "":
		await bot.say("You must specify the song to add.")
	
	f = open("./Songs/Favorite.txt", "a+")
	f.write(song)
	f.close()
	await bot.say(song + " is added. :smile:")
	
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

bot.run('MjQzNzg3MDE0NTQ4MjI2MDQ4.Cv0EAg.-rxlocwCfEHpD8gTlQQrXqJZwzg')
