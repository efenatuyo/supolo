from supolo import supolo
import asyncio
x = supolo(tokenType="bot", token="") # bot / user


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

# spam guilds channels
spammed_channels = asyncio.run(x.spam_guilds_channels(channel_ids=[1156359267503308864], data_message={"content": "@everyone"}, data_webhook={"name": "cool"}, amount=20, method="bot or webhook"))
print(spammed_channels)

# spam guild channel
# need to create aiohttp session
spammed_channel = asyncio.run(x.spam_guilds_channels(session, channel_id=1156359267503308864, data_message={"content": "@everyone"}, data_webhook={"name": "cool"}, amount=20, method="bot or webhook"))
print(spammed_channel)

# create channel webhook
# need to create aiohttp session
webhook = asyncio.run(x.create_channel_webhook(session, channel_id=1156359267503308864, data_webhook={"name": "cool"}))
print(webhook)

# create guilds roles
created_roles = asyncio.run(x.create_guilds_roles(guild_ids=[1141399067142926386], data_role={"name": "test"}, amount=100))
print(created_roles)

# create guild role
# need to create aiohttp session
created_role = asyncio.run(x.create_guild_role(session, guild_id=1141399067142926386, data_role={"name": "ok"}))
print(created_role)

# get guilds roles
guilds_roles = asyncio.run(x.get_guilds_roles(guild_ids=[1141399067142926386]))
print(guilds_roles)

# get guild roles
# need to create aiohttp session
guild_roles = asyncio.run(x.get_guild_roles(session, guild_id=1141399067142926386))
print(guild_roles)

# delete guilds roles
deleted_roles = asyncio.run(x.delete_guilds_roles(role_ids={"server_id": ["role_id"]}))
print(deleted_roles)

# delete guild role
# need aiohttp session
deleted_role = asyncio.run(x.delete_guild_role(session, guild_id=1141399067142926386, role_id=1156919420862611506))
print(deleted_role)

# modify guilds users
# see json at https://discord.com/developers/docs/resources/guild#modify-guild-member 
modified_users = asyncio.run(x.mass_modify_guilds_users(user_ids={"guild_id": ["user_ids"]}))
print(modified_users)

# modify guild user
# need aiohttp session
modified_user = asyncio.run(x.modify_guild_user(session, guild_id=1141399067142926386, user_id=1136830212009644103, data_modify={}))
print(modified_user)

# modify guilds
# see json at https://discord.com/developers/docs/resources/guild#modify-guild
modified_guilds = asyncio.run(x.mass_modify_guilds(guild_ids=[1141399067142926386], data_modify={"name": "test"}))
print(modified_guilds)

# modify guild
# need aiohttp session 
modified_guild = asyncio.run(x.modify_guild(session, guild_id=1141399067142926386, data_modify={}))
print(modified_guild)

# mass create guilds emojis
# see json at https://discord.com/developers/docs/resources/emoji#create-guild-emoji
created_guilds_emojis = asyncio.run(x.mass_create_guilds_emojis(guild_ids=[1141399067142926386], data_create={}, amount=20))
print(created_guilds_emojis)

# create guild emoji
# need aiohttp session
created_guild_emoji = asyncio.run(x.create_guild_emoji(session, guild_id=1141399067142926386, data_create={}))
print(created_guild_emoji)

# mass modify guilds emojis
# see json at https://discord.com/developers/docs/resources/emoji#modify-guild-emoji
modified_emojis = asyncio.run(x.mass_modify_guilds_emojis(emoji_ids={"guild_id": ["emoji_id"]}, data_modify={}))
print(modified_emojis)

# modify guild emoji
# need aiohttp session
modified_emoji = asyncio.run(x.modify_guild_emoji(session, guild_id=1141399067142926386, emoji_id=1129929174090514552, data_modify={}))
print(modified_emoji)

# mass delete guilds emojis
deleted_emojis = asyncio.run(x.mass_delete_guilds_emojis(emoji_ids={"guild_id": ["emoji_id"]}))
print(deleted_emojis)

# delete guild emoji
# need aiohttp session
deleted_emoji = asyncio.run(x.delete_guild_emoji(session, guild_id=1141399067142926386, emoji_id=1129929174090514552))
print(deleted_emoji)

# mass add guilds members roles
added_member_roles = asyncio.run(x.mass_add_guilds_members_rolesles(user_ids={"guild_ids": {"user_ids": ["user_id"], "role_ids": ["role_id"]}}))
print(added_member_roles)

# add guild member role
# need aiohttp session
added_member_role = asyncio.run(x.add_guild_member_role(session, guild_id=123, user_id=123, role_id=123))
print(added_member_role)

# mass remove guilds members roles
added_member_roles = asyncio.run(x.mass_remove_guilds_members_rolesles(user_ids={"guild_ids": {"user_ids": ["user_id"], "role_ids": ["role_id"]}}))
print(added_member_roles)

# remove guild member role
# need aiohttp session
added_member_role = asyncio.run(x.remove_guild_member_role(session, guild_id=123, user_id=123, role_id=123))
print(added_member_role)

# modify guilds roles positions
modified_guilds_roles_positions = asyncio.run(x.modify_guilds_roles_position(guild_ids=[1141399067142926386], data_role={}))
print(modified_guilds_roles_positions)

# modify guild role position
# need aiohttp session
modified_guild_role_position = asyncio.run(x.modify_guild_role_position(session, guild_id=1141399067142926386, data_role={}))
print(modified_guild_role_position)

# modify guilds roles
modified_guilds_roles = asyncio.run(x.modify_guilds_roles(guild_ids=[1141399067142926386], data_role={}))
print(modified_guilds_roles)

# modify guild role
# need aiohttp session
modified_guild_role = asyncio.run(x.modify_guild_role(session, guild_id=1141399067142926386, data_role={}))
print(modified_guild_role)
