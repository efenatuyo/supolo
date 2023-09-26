from supolo import supolo
import asyncio
x = supolo(tokenType="bot", token="")


# get servers token is in
servers = asyncio.run(x.get_servers())
print(servers)

# get every user id
user_ids = asyncio.run(x.get_shared_user_ids())
print(user_ids)

# get user ids from specific servers
user_ids = asyncio.run(x.get_guilds_member(guild_ids=[1121185995354804314]))
print(user_ids)

# mass ban
mass_ban = asyncio.run(x.mass_ban(guild_ids=[1121185995354804314]))
print(mass_ban)

# get banned users
users = asyncio.run(x.get_guild_banned_users(1121185995354804314))
print(users)
# multiple_guilds
users = asyncio.run(x.get_guilds_banned_users([1121185995354804314]))
print(users)

# mass unban
unbanned_user = asyncio.run(x.mass_unban(guild_ids=[1121185995354804314]))
print(unbanned_user)

# mass kick
kicked_members = asyncio.run(x.mass_kick(guild_ids=[1121185995354804314]))
print(kicked_members)

# get guilds channels
guilds_channels = asyncio.run(x.get_guilds_channels(guild_ids=[1038575674899841044]))
print(guilds_channels)

# get guild channels
# need to create aiohttp session
guild_channels = asyncio.run(x.get_guild_channels(session, guild_id=1038575674899841044))
print(guild_channels)

# delete guilds channels
deleted_channels = asyncio.run(x.delete_guilds_channels(channel_ids=[1, 2]))
print(deleted_channels)

# delete guild channel
# need to create aiohttp session
deleted_channel = asyncio.run(x.delete_guild_channel(session, channel_id=1))
print(deleted_channel)

# create guilds channels
created_channels = asyncio.run(x.create_guilds_channels(guild_ids=[1141399067142926386], data={"name": "b", "type": 0}, amount=100))
print(created_channels)

# create guild channel
# need to create aiohttp session
created_channel = asyncio.run(x.create_guild_channel(session, guild_id=1141399067142926386, data={"name": "b", "type": 0}))
print(created_channel)
