import discord
import asyncio
import random

TOKEN = ''

client = discord.Client()

pugs = {}

EMOJI_CHECK = '✅'
escapes = ['_', '*', '~']

def escape(s):
	for c in escapes:
		s = s.replace(c, '\\'+c)
	return s

def manage_pug(func):
	async def wrapper(message):
		channel = message.channel
		if pugs.get(channel) is not None:
			await func(channel, message, pugs[channel])
	return wrapper

async def on_create(message):
	pugs[message.channel] = set()
	await client.send_message(message.channel, '`Started PUG Queue`')


@manage_pug
async def on_join(channel, message, pug):
	print('on_join')
	pug.add(message.author)
	await client.add_reaction(message, EMOJI_CHECK)


@manage_pug
async def on_quit(channel, message, pug):
	pug.remove(message.author)
	await client.add_reaction(message, EMOJI_CHECK)

@manage_pug
async def on_add(channel, message, pug):
	for user in message.mentions:
		if user != client.user:
			pug.add(user)
	await client.add_reaction(message, EMOJI_CHECK)

@manage_pug
async def on_remove(channel, message, pug):
	for user in message.mentions:
		if user in pug:
			pug.remove(user)
	await client.add_reaction(message, EMOJI_CHECK)


@manage_pug
async def on_list(channel, message, pug):
	usernames = list(map(escape, map(lambda u: u.name, pug)))
	await client.send_message(channel, 
		'**Queue ({})**:\n'.format(len(pug)) +
		'\n'.join(sorted(usernames, key=lambda s: s.lower()))
	)


@manage_pug
async def on_assign(channel, message, pug):
	queue = list(map(lambda u: u.name, pug))

	if len(queue) < 2:
		await client.send_message(message.channel, '`Need at least 2 people.`')
		return

	queue = list(map(escape, queue))
	random.shuffle(queue)
	pivot = int(len(queue)/2)
	red = queue[pivot:]
	blue = queue[:pivot]

	await client.send_message(channel, embed=discord.Embed(
		color=discord.Colour.red(),
		title='Red ({})'.format(len(red)),
		description='\n'.join(
			['^' + red[0]] +
			sorted(red[1:], key=lambda s: s.lower())
		)
	))

	await client.send_message(channel, embed=discord.Embed(
		color=discord.Colour.blue(),
		title='Blue ({})'.format(len(blue)),
		description='\n'.join(
			['^' + blue[0]] +
			sorted(blue[1:], key=lambda s: s.lower())
		)
	))

	await client.send_message(channel,
		'{} picks map'.format(random.choice(['RED', 'BLUE']))
	)


@manage_pug
async def on_end(channel, message, pug):
	pugs[channel] = None
	await client.add_reaction(message, EMOJI_CHECK)


async def on_help(message):
	await client.send_message(message.channel, """
		Help - @pug <command>
		**create**: Start a new queue in this channel
		**join**: Add yourself to the queue
		**quit**: Leave the queue
		**add**: Add @ mentioned members
		**remove**: Remove @ mentioned members
		**list**: See who's in the queue
		**assign**: Assigns teams & captains
		**end**: End pug
		**help**: this
		"""
	)

routes = {
	'create': on_create,
	'join': on_join,
	'quit': on_quit,
	'add': on_add,
	'remove': on_remove,
	'assign': on_assign,
	'list': on_list,
	'endpug': on_end,
	'help': on_help
}

@client.event
async def on_ready():
	print('Logged in as {}'.format(client.user.name))
	print(client.user.mention)

@client.event
async def on_message(message):
	print('[{}] @{}: {}'.format(
		message.channel, message.author.name, message.content))

	tokens = message.content.split(' ')
	if len(tokens) < 2:
		return

	if tokens[0] == client.user.mention:
		command = tokens[1]
		if routes.get(command):
			await routes[command](message)



def main():
	client.run(TOKEN)

if __name__ == '__main__':
	main()