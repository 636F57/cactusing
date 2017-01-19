# Copyright (c) 2016 636F57@GitHub
# This software is released under an MIT license.
# See LICENSE for full details.

import discord 
import asyncio
import time
from slackclient import SlackClient
from cactusconsts import CactusConsts


if not discord.opus.is_loaded():
	discord.opus.load_opus('libopus-0.dll')
print("opus dll is loaded = ", discord.opus.is_loaded())

CACTUSING_ID = CactusConsts.CACTUSING_ID
CactusBot_ID = CactusConsts.CactusBot_ID

client = discord.Client()

g_slack = SlackClient(CactusConsts.Slack_bot_Token)

g_bShouldEcho = True
g_bSlackChatOn = False
g_bNowPolling = False
g_strPrefix = "%"
g_discord_SlackChannel_ID = CactusConsts.Slack_Channel_ID
g_slack_channel_list = {}
g_slack_user_list = {}
g_slack_chat_channel = "test"
g_polling_hours = 3  # time interval for polling slack in hours
g_lastpolling = 0

##############################################################
# utils

async def set_status_string(client):
	global g_bShouldEcho
	global g_bSlackChatOn
	global g_bNowPolling
	strStatus = ""
	if g_bShouldEcho:
		strStatus += "Echo"
	if g_bNowPolling:
		if len(strStatus) > 0:
			strStatus += ", "
		strStatus += "Polling"
	if g_bSlackChatOn:
		if len(strStatus) > 0:
			strStatus += ", "
		strStatus += "SlackChat"
	await client.change_presence(game=discord.Game(name=strStatus),status=discord.Status.online)

def get_slack_channel_name(channel_ID):
	global g_slack_channel_list
	if len(g_slack_channel_list) == 0:
		g_slack_channel_list = g_slack.api_call("channels.list")
		#print(g_slack_channel_list)
		#g_slack.api_call("channels.join", channel=CactusConsts.slack_test_channelID)
	chan = "?"
	for channel in g_slack_channel_list['channels']:
		if channel['id'] == channel_ID:
			chan = channel['name']
			break
	return chan		

def get_slack_channel_ID(channel_name):
	global g_slack_channel_list
	if len(g_slack_channel_list) == 0:
		g_slack_channel_list = g_slack.api_call("channels.list")
	chan = 0
	for channel in g_slack_channel_list['channels']:
		if channel['name'] == channel_name:
			chan = channel['id']
			break
	return chan	
	
def get_slack_user_name(user_ID):
	global g_slack_user_list
	if len(g_slack_user_list) == 0:
		g_slack_user_list = g_slack.api_call("users.list")
		#print(g_slack_user_list)
	name = "?"
	for user in g_slack_user_list['members']:
		if user['id'] == user_ID:
			name = user['name']
			break
	return name		
	
# ts should be total sec since epoch time, like "1480832827.000006" as string
def format_time_output(ts):
	return 	time.strftime("%m/%d(%a) %H:%M:%S UTC", time.gmtime(int(ts.split('.')[0])))
	
# format and output JSON response from slack to discord channel
async def slack_output(client, dic, slackeventchannelid):
	global g_discord_SlackChannel_ID
	if 'type' in dic:
		strMsg = ""
		if dic['type'] == 'message':            
			user = "?"
			if 'user' in dic:
				user = get_slack_user_name(dic['user'])
			elif 'username' in dic:
				user = dic['username']
			#print(slackeventchannelid)
			channame = get_slack_channel_name(slackeventchannelid)
			tm = format_time_output(dic['ts'])
			print("user:",user,"in", channame, "at", tm)
			strMsg = "**" + user + "**" + " said in *#" + channame + "* at __" + tm + "__ :\n" + dic['text']
		elif dic['type'] == 'presence_change':
			strMsg = "**" + get_slack_user_name(dic['user']) + "** is now **" + dic['presence'] + "**"		
		if len(strMsg) > 0:
			await client.send_message(client.get_channel(g_discord_SlackChannel_ID), strMsg) 
		
# retrieve the channel history of the target time slot
async def slack_output_history(client, channel_ID, latest, oldest):
	listRes = g_slack.api_call("channels.history", channel=channel_ID, latest=latest, oldest=oldest)
	print(get_slack_channel_name(channel_ID),"new messages =", len(listRes['messages']))
	tmplistResMsgs = [listRes['messages']]
	while len(listRes['messages'])>0 and listRes['has_more']:
		listRes = g_slack.api_call("channels.history", channel=channel_ID, latest=listRes['messages'][-1]['ts'], oldest=oldest)
		tmplistResMsgs.append(listRes['messages'])
	for listResMsg in reversed(tmplistResMsgs):
		for dic in reversed(listResMsg):
			await slack_output(client, dic, channel_ID)

# get all the channel history and then locally extract messages of the target time slot. (use when above method wont work)
async def slack_output_history2(client, channel_ID, latest, oldest):
	listRes = g_slack.api_call("channels.history", channel=channel_ID)
	print(get_slack_channel_name(channel_ID),"new messages =", len(listRes['messages']))
	tmplistResMsgs = [listRes['messages']]
	while len(listRes['messages'])>0 and listRes['has_more'] and float(listRes['messages'][-1]['ts']) > float(oldest):
		listRes = g_slack.api_call("channels.history", channel=channel_ID, latest=listRes['messages'][-1]['ts'])
		tmplistResMsgs.append(listRes['messages'])
	for listResMsg in reversed(tmplistResMsgs):
		for dic in reversed(listResMsg):
			f_ts = float(dic['ts'])
			if f_ts < float(latest) and f_ts > float(oldest):
				await slack_output(client, dic, channel_ID)
			
			
async def realtime_slack(client):
	global g_bSlackChatOn
	global g_discord_SlackChannel_ID
	global g_slack_user_list
	while True:
		if g_bSlackChatOn:
			if g_slack.rtm_connect():
				if len(g_slack_user_list) == 0:
					g_slack_user_list = g_slack.api_call("users.list")
				for user in g_slack_user_list['members']:
					res = g_slack.api_call("users.getPresence", user=user['id'])
					strMsg = "**" + user['name'] + "** is " + res['presence']
					await client.send_message(client.get_channel(g_discord_SlackChannel_ID), strMsg)
				while g_bSlackChatOn:
					try:
						listRes = g_slack.rtm_read()
						if len(listRes)>0:
							print(listRes)
						for dic in listRes:
							if 'type' in dic:
								if dic['type'] == 'hello':
									await client.send_message(client.get_channel(g_discord_SlackChannel_ID), "Slack chat is ready. :slight_smile:")
								elif 'channel' in dic:
									print(dic)
									await slack_output(client, dic, dic['channel'])
								else:
									await slack_output(client, dic, "")
					finally:
						await asyncio.sleep(1)
			else:
				print("rtm connection failed")
				await client.send_message(client.get_channel(g_discord_SlackChannel_ID), "Connection failed.")
				await asyncio.sleep(30)
		else:
			await asyncio.sleep(30)
		
# get slack history every g_polling_hours and output to discord channel of g_discord_SlackChannel_ID
async def watch_slack(client):
	global g_polling_hours
	while not client.is_closed:
		while client.is_logged_in:
			await check_slack(client)	
			await asyncio.sleep(g_polling_hours*3600)
		await asyncio.sleep(30)

async def check_slack(client):
	global g_polling_hours
	global g_lastpolling
	global g_slack_channel_list
	global g_bSlackChatOn
	global g_discord_SlackChannel_ID
	global g_bNowPolling

	if g_bSlackChatOn == False:
		g_bNowPolling = True
		await set_status_string(client)
		if g_slack.rtm_connect():   #need to login to get proper data. cant find other way to login...
			nTry = 1
			while nTry:
				listRes = g_slack.rtm_read()
				for dic in listRes:
					if 'type' in dic:
						if dic['type'] == 'hello':
							bTry = 0
							print("got 'hello' response.")
							break;
				else:
					await asyncio.sleep(2)
					nTry += 1
					if nTry > 10:
						nTry = 0     # wait 10 packets at maximum
						print("rtm_connect is not confirmed.")
			#try checking anyways
			if len(g_slack_channel_list) == 0:
				g_slack_channel_list = g_slack.api_call("channels.list")
			oldesttime = g_lastpolling
			if g_lastpolling == 0:
				oldesttime = time.time()-g_polling_hours*3600
			g_lastpolling = time.time()-100
			print("polling slack for latest=", time.time(), "oldest=", oldesttime)
			for channel in g_slack_channel_list['channels']:
				await slack_output_history(client, channel['id'], str(time.time()), str(oldesttime))
				#await client.send_message(client.get_channel(g_discord_SlackChannel_ID), "now re-try with method2...") #for debug
				#await slack_output_history2(client, channel['id'], str(time.time()), str(oldesttime)) #for debug
				#await client.send_message(client.get_channel(g_discord_SlackChannel_ID), "done")  #for debug
		g_bNowPolling = False
		await set_status_string(client)
		
##############################################################
# events 

@client.event
async def on_message(message):	
	#print("on message : ", message.content, message.author.name, message.author.id)
	global g_bShouldEcho
	global g_bSlackChatOn
	global g_strPrefix
	global g_slack_chat_channel
	global g_polling_hours
	
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
	elif (message.author.id == CactusBot_ID):
		print("message by CactusBot")
		if g_bShouldEcho:
			if (message.content.startswith("-play")) | (message.content.startswith(":request")):
				print("in echo")
				await client.send_message(message.channel, message.content)
	
	### prefix + "voice" : join the voice channel which commander belongs to ###
	elif message.content.casefold() == (g_strPrefix+"voice").casefold():
		voiceclient = client.voice_client_in(message.server)
		print(message.server)
		if voiceclient == None:
			print(message.author.voice.voice_channel)
			await client.join_voice_channel(message.author.voice.voice_channel)
		elif voiceclient.channel != message.channel:
			await voiceclient.move_to(message.channel)
			
	### prefix + "test" : just for test and debug ###
	elif message.content.casefold() == (g_strPrefix+"test").casefold():
		await client.send_message(message.channel, ":music play")
	
	### prefix + "repeat" : repeat the sentence ###
	elif message.content.casefold().startswith((g_strPrefix+"repeat").casefold()):
		await client.send_message(message.channel, message.content[8:])
	
	### CactusBot said "Happy Birthday" : say "Happy Birthday" too. ###
	elif message.author.id == CactusConsts.CactusBot_ID:
		if message.content.casefold().startswith(("happy birthday").casefold()):		
			await client.send_message(message.channel, "Happy Birthday!!! :heart: :birthday: :tada:")
	### Repost the GitHub news to Slack's github channel ###
		elif "New Commit" in message.content:
			for repo in CactusConsts.listGitHubRepos_toSlack:
				if repo.casefold() in message.content.casefold():
					newmsg = message.content.replace(":cactus:", ":computer:")
					g_slack.api_call("chat.postMessage", channel="#github", text=newmsg)
					break
		
	### prefix + "slackchat_start" : start syncing with Slack ###
	elif message.content.casefold() == (g_strPrefix+"slackchat_start").casefold():
		if g_bSlackChatOn:
			await client.send_message(message.channel, "It's already connected to Slack. :slight_smile:")
			return
		else:
			g_bSlackChatOn = True
			await set_status_string(client)
			await client.send_message(message.channel, "Starting syncing with Slack...")
	
	### prefix + "slackchat_end" : end syncing with Slack ###
	elif message.content.casefold() == (g_strPrefix+"slackchat_end").casefold():
		if g_bSlackChatOn == False:
			await client.send_message(message.channel, "It's already disconnected from Slack. :slight_smile:")
			return
		else:
			g_bSlackChatOn = False
			await set_status_string(client)
			await client.send_message(message.channel, "Syncing with Slack ended. :slight_smile:")

	### prefix + "s" : send message to Slack ###
	elif message.content.casefold().startswith((g_strPrefix+"s ").casefold()):
		if g_bSlackChatOn:
			g_slack.rtm_send_message(g_slack_chat_channel, message.content[3:])
		else:
			g_slack.api_call("chat.postMessage", channel="#"+g_slack_chat_channel, text=message.content[3:])

	### prefix + "s_channel" : change the Slack's channel to send messages ###
	elif message.content.casefold().startswith((g_strPrefix+"s_channel").casefold()):
		channel_name = message.content[11:].strip()
		print(channel_name)
		if get_slack_channel_ID(channel_name) == 0:
			await client.send_message(message.channel, "No such channel was found. :cry:")
		else:
			g_slack_chat_channel = channel_name
	
	### prefix + "s_check" : get updated info of slack activities since last check ###
	elif message.content.casefold().startswith((g_strPrefix+"s_check").casefold()):
		if g_bSlackChatOn:
			await client.send_message(g_slack_chat_channel, "You cannot check history when realtime chatting. :(")
		else:
			await check_slack(client)

	### prefix + "s_interval" : set polling intervals in hours ###
	elif message.content.casefold().startswith((g_strPrefix+"s_interval").casefold()):
		cmd, interval = message.content.split()
		if isdigit(interval.remove('.')):
			f_interval = float(interval)
			if f_interval > 0:
				g_polling_hours = f_interval
				await client.send_message(message.channel, "polling interal was set to "+interval+"hours. :)")
				return
		await client.send_message(message.channel, "Please specify number (int or float) in hours for interval")
				
			
	### prefix + "s_whois" : print username from userID of Slack ###
	elif message.content.casefold().startswith((g_strPrefix+"s_whois").casefold()):
		await client.send_message(message.channel, get_slack_user_name(message.content[7:]))
	
	### prefix + "s_url" : print web client URL for the slack server ###
	elif message.content.casefold().startswith((g_strPrefix+"s_url").casefold()):
		await client.send_message(client.get_channel(g_discord_SlackChannel_ID), CactusConsts.Slack_webclient_URL)

@client.event
async def on_ready():
	global g_discord_SlackChannel_ID
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	if len(g_discord_SlackChannel_ID) == 0:
		for server in client.servers:
			if server.name == CactusConsts.Server_Name:
				for channel in server.channels:
					if channel.name.casefold() == ("slack").casefold():
						g_discord_SlackChannel_ID = channel.id
						print("slack channel ID: ", g_discord_SlackChannel_ID)  # better to add to CactusConsts
						break
				else:
					g_discord_SlackChannel_ID = server.default_channel.id
				break
		else:
			print("Failed to set slack output channel.")
	await set_status_string(client)
			
######################################


loop = asyncio.get_event_loop()
try:
	loop.create_task(realtime_slack(client))
	loop.create_task(watch_slack(client))
	loop.run_until_complete(client.run(CactusConsts.cacti_username, CactusConsts.cacti_password))
	
except KeyboardInterrupt:
	loop.run_until_complete(client.logout())
	# cancel all tasks lingering
	tasks = asyncio.Task.all_tasks(loop)
	for task in tasks:
		task.cancel()
finally:
	loop.close()
	




