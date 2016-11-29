import discord 
from slackclient import SlackClient
from cactusconsts import CactusConsts

if not discord.opus.is_loaded():
	discord.opus.load_opus('libopus-0.dll')
print("opus dll is loaded = ", discord.opus.is_loaded())

CACTUSING_ID = cactusconsts.CACTUSING_ID
CactusBot_ID = cactusconsts.CactusBot_ID

client = discord.Client()

g_slack = SlackClient(CactusConsts.Slack_Token)

g_bShouldEcho = True
g_bSlackChatOn = False
g_strPrefix = "%"
g_strSlackChannel_ID = CactusConsts.Slack_Channel_ID
g_slack_channel_list = {}
g_slack_user_list = {}

##############################################################
# utils

async def set_status_string(client):
	global g_bShouldEcho
	global g_bSlackChatOn
	strStatus = ""
	if g_bShouldEcho:
		strStatus += "Echo"
	if g_bSlackChatOn:
		if len(strStatus) > 0:
			strStatus += ", "
		strStatus += "SlackChat"
	await client.change_presence(game=discord.Game(name=strStatus),status=discord.Status.idle)

def get_slack_channel_name(channel_ID):
	global g_slack_channel_list
	if len(g_slack_channel_list) == 0:
		g_slack_channel_list = g_slack.api_call("channels.list")
	chan = "?"
	for channel in g_slack_channel_list['channels']:
		if channel['id'] == channel_ID
			chan = channel['name']
			break
	return chan		
	
def get_slack_user_name(user_ID):
	global g_slack_user_list
	if len(g_slack_user_list) == 0:
		g_slack_user_list = g_slack.api_call("channels.list")
	name = "?"
	for user in g_slack_user_list['users']:
		if user['id'] == user_ID
			name = user['name']
			break
	return name		
	
					
async def realtime_slack(client):
	global g_bSlackChatOn
	global g_strSlackChannel_ID
	while g_bSlackChatOn:
		if g_slack.rtm_connect():
			dicRes = g_slack.rtm_read()
			if dicRes['type'] == 'message':            # support only message for now
				strMsg = get_slack_user_name(dicRes['user'])+"said in "+get_slack_channel_name(dicRes['channel'])+" : "+dicRes['text']
				await client.send_message(client.get_channel(g_strSlackChannel_ID), strMsg)  
		else:
			await client.send_message(client.get_channel(g_strSlackChannel_ID), "Connection failed.")
		time.sleep(2)

##############################################################
# events 

@client.event
async def on_message(message):	
	print("on message : ", message.content, message.author.name, message.author.id)
	global g_bShouldEcho
	global g_bSlack
	global g_strPrefix
	
	### prefix + "echo" : toggle echoing CactusBot ###
	if message.content.casefold() ==  (g_strPrefix+"echo").casefold():
		if g_bShouldEcho:
			g_bShouldEcho = False
			await client.send_message(message.channel, "Echoing stopped. :slight_smile:")
			await set_status_string(client)
		else:
			g_bShouldEcho = True
			await client.send_message(message.channel, "Echoing started. :slight_smile:")
			await set_status_string(client)

	### automatic echoing ###
	if (message.author.id == CactusBot_ID):
		print("message by CactusBot")
		if g_bShouldEcho:
			if (message.content.startswith("-play")) | (message.content.startswith(":request")):
				print("in echo")
				await client.send_message(message.channel, message.content)
	
	### prefix + "voice" : join the voice channel which commander belongs to ###
	if message.content.casefold() == (g_strPrefix+"voice").casefold():
		voiceclient = client.voice_client_in(message.server)
		print(message.server)
		if voiceclient == None:
			print(message.author.voice.voice_channel)
			await client.join_voice_channel(message.author.voice.voice_channel)
		elif voiceclient.channel != message.channel:
			await voiceclient.move_to(message.channel)
			
	### prefix + "test" : just for test and debug ###
	if message.content.casefold() == (g_strPrefix+"test").casefold():
		await client.send_message(message.channel, ":music play")
	
	### prefix + "repeat" : repeat the sentence ###
	if message.content.casefold().startwith((g_strPrefix+"repeat").casefold()):
		await client.send_message(message.channel, message.content[6:])
	
	### prefix + "slackchat_start" : start syncing with Slack ###
	if message.content.casefold() == (g_strPrefix+"slack_start").casefold():
		if g_bSlackChatOn:
			await client.send_message(message.channel, "It's already connected to Slack. :slight_smile:")
			return
		else:
			g_bSlackChatOn = True
			set_status_string(client)
			await client.send_message(message.channel, "Syncing with Slack started. :slight_smile:")
	
	### prefix + "slackchat_end" : end syncing with Slack ###
	if message.content.casefold() == (g_strPrefix+"slack_end").casefold():
		if g_bSlackChatOn == False:
			await client.send_message(message.channel, "It's already disconnected from Slack. :slight_smile:")
			return
		else:
			g_bSlackChatOn = False
			set_status_string(client)
			await client.send_message(message.channel, "Syncing with Slack ended. :slight_smile:")

	### prefix + "s" : send message to Slack ###
	if message.content.casefold().startwith((g_strPrefix+"s ").casefold()):
		g_slack.api_call("chat.postMessage", channel="#test", text=message.content[2:])

	### 
	if message.content.casefold() == (g_strPrefix+"createinvite").casefold():
		invite = client.create_invite(destination = message.channel, xkcd = True, max_uses = 1)
		if invite is not None:
			client.send_message(message.channel, "Invite is:\n{}\nThe invite can only be used once.".format(invite.url))
		else:
			client.send_message(message.channel, "Unable to create invite. Sorry for the inconvenience.")

@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	if len(g_strSlackChannel_ID) == 0:
		for server in client.servers:
			if server.name == CactusConsts.Server_Name:
				for channel in server.channels:
					if channel.name.casefold() == ("slack").casefold():
						g_strSlackChannel_ID = channel.id
						print("slack channel ID: ", g_strSlackChannel_ID)  # better to add to CactusConsts
						break
				else:
					g_strSlackChannel_ID = server.default_channel.id
				break
		else:
			print("Failed to set slack output channel.")
			
######################################


loop = asyncio.get_event_loop()
try:
	loop.create_task(realtime_slack(client))
	loop.run_until_complete(client.run(CactusConsts.cacti_username, CactusConsts.cacti_password))
	
except KeyboardInterrupt:
	loop.run_until_complete(client.logout())
	# cancel all tasks lingering
	tasks = asyncio.Task.all_tasks(loop)
	for task in tasks:
		task.cancel()
finally:
	loop.close()
	if g_session:
		g_session.close()





