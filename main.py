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
