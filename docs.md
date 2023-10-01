Module Supolo
===============
Classes
-------
`supolo(tokenType, token, skipOnRatelimit=False, ratelimitCooldown=1)`
:
### Methods
`add_guild_member_role(self, session, guild_id, user_id, role_id, added_member_roles={}, total_ratelimits=0)`
:Add a role to a member in a guild.

Args:
session: The aiohttp client session.
guild_id (int): The ID of the guild where the role should be added.
user_id (int): The ID of the user to whom the role should be added.
role_id (int): The ID of the role to be added.
added_member_roles (dict, optional): A dictionary to store added member roles. Default is an empty dictionary.
total_ratelimits (int, optional): The total number of rate limits encountered. Default is 0.

Returns:
dict: A dictionary containing the result of the operation, including added member roles.

Example Usage:
```python
# Add a role to a member in a guild.
guild_id = 123456789012345678  # Replace with the desired guild ID.
user_id = 987654321098765432  # Replace with the user's ID.
role_id = 123456789  # Replace with the role ID to be added.
result = await discord_utility.add_guild_member_role(session, guild_id, user_id, role_id)
if result["success"]:
   print(f"Role with ID {role_id} added to user with ID {user_id} in guild with ID {guild_id}")
else:
   print(f"Failed to add role to user: {result['message']}")
```
Note:
This method adds a specified role to a member in a guild and returns the added member roles.
`create_channel_webhook(self, session, channel_id, data_webhook)`
:Create a webhook in a channel.

Args:
session (aiohttp.ClientSession): The aiohttp session to use for the HTTP request.
channel_id (int): The ID of the channel in which to create the webhook.
data_webhook (dict): The JSON data for creating the webhook.

Returns:
dict: A dictionary containing information about the created webhook.

Example Usage:
```python
# Create a webhook in a channel.
session = aiohttp.ClientSession()
channel_id = 123456789012345678
data_webhook = {"name": "my-webhook"}
created_webhook = await discord_utility.create_channel_webhook(session, channel_id, data_webhook)
session.close()
if created_webhook:
   print(f"Created webhook: {created_webhook['name']} (ID: {created_webhook['id']})")
else:
   print("Failed to create webhook")
```
Note:
This method creates a webhook in a channel and returns information about the created webhook.
`create_guild_channel(self, session, guild_id, data, created_channels={}, total_ratelimits=0)`
:Creates a channel in a guild.

Args:
session (aiohttp.ClientSession): The aiohttp session to use for the HTTP request.
guild_id (int): The ID of the guild in which the channel will be created.
data (dict): The JSON data to be sent in the request body.
created_channels (dict): A dictionary to store information about created channels.
total_ratelimits (int): The total number of rate limits encountered.

Returns:
dict: A dictionary containing information about the created channel.

Example Usage:
```python
# Create a text channel in a guild.
session = aiohttp.ClientSession()
guild_id = 123456789012345678
data = {"name": "my-channel", "type": 0}
created_channel = await discord_utility.create_guild_channel(session, guild_id, data)
session.close()
if created_channel:
   print(f"Created channel: {created_channel['name']} (ID: {created_channel['id']})")
else:
   print("Failed to create channel")
```

Note:
This method creates a channel in a guild and returns information about the created channel.
`create_guild_emoji(self, session, guild_id, data_create, created_emojis={}, total_ratelimits=0)`
:Create a custom emoji in a guild.

Args:
session (aiohttp.ClientSession): An aiohttp ClientSession for making HTTP requests.
guild_id (int): The ID of the guild in which to create the emoji.
data_create (dict): A dictionary containing the data to create the emoji with.
Example:
{
"name": "my_emoji",
"image": "base64_image_data"
# Add more emoji data as needed.
}
created_emojis (dict, optional): A dictionary to store created emoji data. Used for aggregation.
total_ratelimits (int, optional): The total number of ratelimits encountered during the operation.

Returns:
dict: A dictionary containing the result of the operation, including created emoji data.

Example Usage:
```python
# Create a custom emoji in a guild.
guild_id = 123456789012345678  # Replace with the desired guild ID.
emoji_data = {
"name": "my_custom_emoji",
"image": "base64_encoded_image_data"
}  # Replace with emoji data.
create_result = await discord_utility.create_guild_emoji(session, guild_id, emoji_data)
if create_result["success"]:
   print("Created Emoji:")
   print(f"- Guild ID: {guild_id}, Created Emoji: {create_result['created_emoji']}")
else:
   print(f"Failed to create emoji: {create_result['message']}")
```

Note:
This method creates a custom emoji in a guild and returns the created emoji data.
`create_guild_role(self, session, guild_id, data_role, created_roles={}, total_ratelimits=0)`
:Create a role in a guild.

Args:
session (aiohttp.ClientSession): The aiohttp session to use for the HTTP request.
guild_id (int): The ID of the guild in which to create the role.
data_role (dict): The JSON data for the role to be created.
created_roles (dict): A dictionary to store information about created roles.
total_ratelimits (int): The total number of rate limits encountered.

Returns:
dict: A dictionary containing information about the created role.

Example Usage:
```python
# Create a role in a guild.
session = aiohttp.ClientSession()
guild_id = 123456789012345678
data_role = {"name": "my-role", "permissions": 0}
created_role = await discord_utility.create_guild_role(session, guild_id, data_role)
session.close()
if created_role:
   print(f"Created role: {created_role['name']} (ID: {created_role['id']})")
else:
   print("Failed to create role")
```

Note:
This method creates a role in a guild and returns information about the created role.
`create_guilds_channels(self, guild_ids:�list, data:�dict, amount:�int�=�10)`
:Creates channels in multiple guilds.

Args:
guild_ids (list): A list of guild IDs in which channels will be created.
data (dict): The JSON data to be sent in the request body.
amount (int, optional): The number of channels to create in each guild. Default is 10.

Returns:
dict: A dictionary containing the result of the operation, including created channels.

Example Usage:
```python
# Create text channels in multiple guilds.
guild_ids = [123456789012345678, 234567890123456789]  # Replace with the desired guild IDs.
data = {"name": "my-channel", "type": 0}
create_result = await discord_utility.create_guilds_channels(guild_ids, data)
if create_result["success"]:
print("Created Channels:")
for guild_id, channels in create_result["created_channels"].items():
   print(f"- Guild ID: {guild_id}, Created Channels: {', '.join(channel['name'] for channel in channels)}")
else:
   print(f"Failed to create channels: {create_result['message']}")
```

Note:
This method creates channels in multiple guilds and returns information about the created channels.
`create_guilds_roles(self, guild_ids:�list, data_role:�dict�=�{}, amount:�int�=�10)`
:Creates roles in multiple guilds.

Args:
guild_ids (list): A list of guild IDs in which roles will be created.
data_role (dict): The JSON data for the role to be created.
amount (int, optional): The number of roles to create in each guild. Default is 10.

Returns:
dict: A dictionary containing the result of the operation, including created roles.

Example Usage:
```python
# Create roles in multiple guilds.
guild_ids = [123456789012345678, 234567890123456789]  # Replace with the desired guild IDs.
data_role = {"name": "my-role", "permissions": 0}
create_result = await discord_utility.create_guilds_roles(guild_ids, data_role)
if create_result["success"]:
print("Created Roles:")
for guild_id, roles in create_result["created_roles"].items():
   print(f"- Guild ID: {guild_id}, Created Roles: {', '.join(role['name'] for role in roles)}")
else:
   print(f"Failed to create roles: {create_result['message']}")
```

Note:
This method creates roles in multiple guilds and returns information about the created roles.
`delete_guild_channel(self, session, channel_id, deleted_channels=[], total_ratelimits=0)`
:Deletes a channel within a guild.

Args:
session (aiohttp.ClientSession): The aiohttp session to use for the HTTP request.
channel_id (int): The ID of the channel to be deleted.
deleted_channels (list, optional): A list to store the IDs of deleted channels. Default is an empty list.
total_ratelimits (int, optional): The total number of rate limits encountered. Default is 0.

Returns:
list: A list of deleted channel IDs or an empty list if the operation fails.

Example Usage:
# Delete a channel within a guild.
channel_id = 123456789012345678  # Replace with the desired channel ID.
session = aiohttp.ClientSession()
deleted_channels = await x.delete_guild_channel(session, channel_id)
session.close()
if deleted_channels:
print(f"Deleted channel with ID: {channel_id}")
else:
print(f"Failed to delete channel with ID: {channel_id}")

Note:
This method attempts to delete a channel within a guild and returns the ID of the deleted channel.
`delete_guild_emoji(self, session, guild_id, emoji_id, deleted_emojis={}, total_ratelimits=0)`
:Delete a guild emoji.

Args:
session: The aiohttp session for making HTTP requests.
guild_id (int): The ID of the guild where the emoji is located.
emoji_id (int): The ID of the emoji to be deleted.
deleted_emojis (dict, optional): A dictionary to store deleted emoji IDs (used for tracking multiple deletions).
total_ratelimits (int, optional): A counter to track the total number of ratelimit responses received.

Returns:
dict: A dictionary containing the result of the deletion operation, including the deleted emoji ID.

Note:
This method deletes a specific emoji from a guild and returns the deleted emoji ID.

Example Usage:
# Delete a guild emoji by emoji ID in a specific guild.
guild_id = 123456789012345678
emoji_id = 987654321098765432
result = await discord_utility.delete_guild_emoji(session, guild_id, emoji_id)

if guild_id in result and emoji_id in result[guild_id]:
print(f"Emoji {emoji_id} deleted successfully from guild {guild_id}")
else:
print(f"Failed to delete emoji {emoji_id} from guild {guild_id}")
`delete_guild_role(self, session, guild_id, role_id, deleted_roles={}, total_ratelimits=0)`
:Delete a role in a specific guild.

Args:
session (aiohttp.ClientSession): An aiohttp session for making HTTP requests.
guild_id (int): The ID of the guild in which the role should be deleted.
role_id (int): The ID of the role to be deleted.
deleted_roles (dict, optional): A dictionary to store deleted role IDs for each guild.
total_ratelimits (int, optional): The total number of rate limits encountered.

Returns:
dict: A dictionary containing the result of the operation, including the deleted role ID.

Note:
This method deletes a role from a specific guild.
`delete_guilds_channels(self, channel_ids:�list)`
:Deletes multiple channels within a guild.

Args:
channel_ids (list): A list of channel IDs to be deleted.

Returns:
dict: A dictionary containing the result of the operation, including deleted channel IDs.

Raises:
AssertionError: If channel_ids is not a list.

Example Usage:
# Delete multiple channels within a guild.
channel_ids = [123456789012345678, 234567890123456789]  # Replace with the desired channel IDs.
deletion_result = asyncio.run(x.delete_guilds_channels(channel_ids))
if deletion_result["success"]:
print("Deleted Channels:")
for channel_id in deletion_result["deleted_channels"]:
print(f"- Deleted channel with ID: {channel_id}")
else:
print(f"Failed to delete channels: {deletion_result['message']}")

Note:
This method deletes multiple channels within a guild and returns the IDs of the deleted channels.
`delete_guilds_roles(self, role_ids:�dict)`
:Delete roles in multiple guilds.

Args:
role_ids (dict): A dictionary containing role IDs to be deleted for each guild.

Returns:
dict: A dictionary containing the result of the operation, including deleted role IDs.

Raises:
AssertionError: If role_ids is not a dictionary.

Example Usage:
# Delete roles in multiple guilds.
role_ids = {
123456789012345678: [987654321098765432, 876543210987654321],
234567890123456789: [765432109876543210]
}  # Replace with the desired role IDs.
delete_result = await discord_utility.delete_guilds_roles(role_ids)
if delete_result["success"]:
print("Deleted Roles:")
for guild_id, deleted_roles in delete_result["deleted_roles"].items():
print(f"- Guild ID: {guild_id}, Deleted Roles: {deleted_roles}")
else:
print(f"Failed to delete roles: {delete_result['message']}")

Note:
This method deletes roles from multiple guilds.
`get_guild_banned_users(self, guild_id, banned_users={}, total_ratelimits=0)`
:Fetches banned users from a specific guild.

Args:
guild_id (int): The ID of the guild for which banned users are to be fetched.
banned_users (dict, optional): A dictionary to store banned user information. Default is an empty dictionary.
total_ratelimits (int, optional): The total number of rate limits encountered. Default is 0.

Returns:
dict: A dictionary containing banned user information or an empty dictionary if the operation fails.

Example Usage:
# Fetch banned users from a specific guild.
guild_id = 123456789012345678  # Replace with the desired guild ID.
banned_users_result = await discord_utility.get_guild_banned_users(guild_id)
if banned_users_result["success"]:
print(f"Fetched Banned Users for Guild ID {guild_id}: {banned_users_result['users']}")
else:
print(f"Failed to fetch banned users for Guild ID {guild_id}: {banned_users_result['message']}")

Note:
This method fetches banned users from a specific guild and returns banned user information in a dictionary.
`get_guild_channels(self, session, guild_id, shared_channels={}, total_ratelimits=0)`
:Retrieves information about channels within a specific guild.

Args:
session (aiohttp.ClientSession): The aiohttp session to use for the HTTP request.
guild_id (int): The ID of the guild (server) for which channel information is to be retrieved.
shared_channels (dict, optional): A dictionary to store channel information. Default is an empty dictionary.
total_ratelimits (int, optional): The total number of rate limits encountered. Default is 0.

Returns:
dict: A dictionary containing channel information or an empty dictionary if the operation fails.

Example Usage:
# Fetch channel information for a specific guild.
guild_id = 123456789012345678  # Replace with the desired guild ID.
session = aiohttp.ClientSession()
channel_info = await x.get_guild_channels(session, guild_id)
session.close()
if channel_info:
print("Channels:")
for channel in channel_info.get(str(guild_id), []):
print(f"- Channel Name: {channel['name']} (ID: {channel['id']})")
else:
print("Failed to fetch channels.")

Note:
This method retrieves information about channels within the specified guild and returns it as a dictionary.
`get_guild_members(self, session=None, url=None, shared_users={}, guild_id=None, total_ratelimits=0, method=None)`
:Fetches members of a specific guild.

Args:
session (aiohttp.ClientSession): The aiohttp session to use for the HTTP request.
guild_id (int): The ID of the guild for which members are to be fetched.
shared_users (dict, optional): A dictionary to store user information. Default is an empty dictionary.
total_ratelimits (int, optional): The total number of rate limits encountered. Default is 0.
method (str, optional): The method name. Default is None.

Returns:
dict: A dictionary containing user information or an empty dictionary if the operation fails.

Raises:
AssertionError: If guild_id, method, or session is missing.

Example Usage:
# Fetch members from a specific guild.
guild_id = 123456789012345678  # Replace with the desired guild ID.
session = aiohttp.ClientSession()
member_info = await x.get_guild_members(session, guild_id)
session.close()
if member_info:
print("Fetched Members:")
for user_id, user_info in member_info.items():
print(f"- User ID: {user_id}, Shared Guilds: {user_info['shared_guilds']}")
else:
print("Failed to fetch members.")

Note:
This method fetches members from a specific guild and returns user information in a dictionary.
`get_guild_roles(self, session, guild_id, guilds_roles={}, total_ratelimits=0)`
:Get roles in a specific guild.

Args:
session (aiohttp.ClientSession): An aiohttp session for making HTTP requests.
guild_id (int): The ID of the guild in which roles should be retrieved.
guilds_roles (dict, optional): A dictionary to store retrieved roles for each guild.
total_ratelimits (int, optional): The total number of rate limits encountered.

Returns:
dict: A dictionary containing the guild's roles.

Note:
This method retrieves roles from a specific guild.
`get_guilds_banned_users(self, guild_ids:�list)`
:Fetches banned users from multiple guilds.

Args:
guild_ids (list): A list of guild IDs for which banned users are to be fetched.

Returns:
dict: A dictionary containing the result of the operation, including fetched banned user information.

Raises:
AssertionError: If guild_ids is not a list.

Example Usage:
# Fetch banned users from multiple guilds.
guild_ids = [123456789012345678, 234567890123456789]  # Replace with the desired guild IDs.
banned_users_result = await discord_utility.get_guilds_banned_users(guild_ids)
if banned_users_result["success"]:
print("Fetched Banned Users:")
for guild_id, banned_users in banned_users_result["banned_users"].items():
print(f"- Guild ID: {guild_id}, Banned Users: {banned_users}")
else:
print(f"Failed to fetch banned users: {banned_users_result['message']}")

Note:
This method fetches banned users from multiple guilds and returns banned user information in a dictionary.
`get_guilds_channels(self, guild_ids:�list)`
:Retrieves information about channels within specified guilds.

Args:
guild_ids (list): A list of guild (server) IDs for which channel information is to be retrieved.

Returns:
dict: A dictionary containing channel information or an error message if the operation fails.

Raises:
AssertionError: If guild_ids is not a list.

Example Usage:
# Retrieve information about channels in specified guilds.
guild_ids = [1141399067142926386, 123456789012345678]  # Replace with desired guild IDs.
channel_info = await x.get_guilds_channels(guild_ids)
if channel_info["success"]:
print("Channels:")
for guild_id, channels in channel_info["channels"].items():
print(f"Guild ID: {guild_id}")
for channel in channels:
print(f"- Channel Name: {channel['name']} (ID: {channel['id']})")
else:
print(f"Failed to fetch channels: {channel_info['message']}")

Note:
This method retrieves information about channels within the specified guilds and returns it as a dictionary.
It's important to pass a list of guild IDs in the 'guild_ids' parameter.
`get_guilds_members(self, guild_ids:�list)`
:Fetches members of multiple guilds.

Args:
guild_ids (list): A list of guild IDs for which members are to be fetched.

Returns:
dict: A dictionary containing the result of the operation, including fetched user information.

Raises:
AssertionError: If guild_ids is not a list.

Example Usage:
# Fetch members from multiple guilds.
guild_ids = [123456789012345678, 234567890123456789]  # Replace with the desired guild IDs.
member_result = asyncio.run(x.get_guilds_members(guild_ids))
if member_result["success"]:
print("Fetched Members:")
for user_id, user_info in member_result["users"].items():
print(f"- User ID: {user_id}, Shared Guilds: {user_info['shared_guilds']}")
else:
print(f"Failed to fetch members: {member_result['message']}")

Note:
This method fetches members from multiple guilds and returns user information in a dictionary.
`get_guilds_roles(self, guild_ids:�list)`
:Get roles in multiple guilds.

Args:
guild_ids (list): A list of guild IDs for which roles should be retrieved.

Returns:
dict: A dictionary containing the result of the operation, including guild roles.

Raises:
AssertionError: If guild_ids is not a list.

Example Usage:
# Get roles in multiple guilds.
guild_ids = [123456789012345678, 234567890123456789]  # Replace with the desired guild IDs.
roles_result = await discord_utility.get_guilds_roles(guild_ids)
if roles_result["success"]:
print("Guild Roles:")
for guild_id, roles in roles_result["guilds_roles"].items():
print(f"- Guild ID: {guild_id}, Roles: {roles}")
else:
print(f"Failed to get guild roles: {roles_result['message']}")

Note:
This method retrieves roles from multiple guilds.
`get_servers(self)`
:Retrieves a list of servers (guilds) that the bot is a member of.

Returns:
dict: A dictionary containing server information or an error message if the operation fails.

Args:
None

Raises:
None

Example Usage:
# Fetch information about servers (guilds) the bot is a member of.
server_info = await x.get_servers()
if server_info["success"]:
print("Servers:")
for server in server_info["servers"]:
print(f"- {server['name']} (ID: {server['id']})")
else:
print(f"Failed to fetch servers: {server_info['message']}")
`get_shared_user_ids(self)`
:Retrieves shared user IDs across all servers (guilds) the bot is a member of.

Returns:
dict: A dictionary containing shared user IDs or an error message if the operation fails.

Args:
None

Raises:
None

Example Usage:
# Retrieve shared user IDs across all servers.
shared_user_info = await x.get_shared_user_ids()
if shared_user_info["success"]:
shared_users = shared_user_info["users"]
print("Shared User IDs:")
for guild_id, user_ids in shared_users.items():
print(f"Guild ID: {guild_id}")
for user_id in user_ids:
print(f"- User ID: {user_id}")
else:
print(f"Failed to retrieve shared user IDs: {shared_user_info['message']}")

Note:
This method may involve multiple API requests to fetch user IDs from different guilds. It aggregates
shared user IDs across all guilds the bot is a member of.
`mass_add_guilds_members_roles(self, user_ids:�dict)`
:Mass-add roles to members in multiple guilds.

Args:
user_ids (dict): A dictionary containing guild IDs as keys and a list of user IDs and role IDs as values.
Example: {123456789012345678: {"user_ids": [123, 456], "role_ids": [789, 987]}}

Returns:
dict: A dictionary containing the result of the operation, including added member roles.

Raises:
AssertionError: If user_ids is not a dictionary.

Example Usage:
# Mass-add roles to members in multiple guilds.
user_ids = {
123456789012345678: {"user_ids": [123, 456], "role_ids": [789, 987]},
987654321098765432: {"user_ids": [789, 654], "role_ids": [321, 654]}
}
result = await discord_utility.mass_add_guilds_members_roles(user_ids)

if result["success"]:
print(f"Roles added to members in multiple guilds")
else:
print(f"Failed to add roles to members: {result['message']}")

Note:
This method adds specified roles to members in multiple guilds and returns the added member roles.
`mass_ban(self, guild_ids:�list, timeout:�int�=�5)`
:Mass bans users in multiple guilds.

Args:
guild_ids (list): A list of guild IDs in which users are to be banned.
timeout (int, optional): Timeout for the HTTP request. Default is 5 seconds.

Returns:
dict: A dictionary containing the result of the operation, including banned user IDs.

Raises:
AssertionError: If guild_ids is not a list.

Example Usage:
# Mass ban users in multiple guilds.
guild_ids = [123456789012345678, 234567890123456789]  # Replace with the desired guild IDs.
ban_result = await discord_utility.mass_ban(guild_ids)
if ban_result["success"]:
print("Banned Users:")
for guild_id, banned_users in ban_result["banned_users"].items():
print(f"- Guild ID: {guild_id}, Banned Users: {banned_users}")
else:
print(f"Failed to ban users: {ban_result['message']}")

Note:
This method bans users from multiple guilds and returns banned user IDs.
`mass_create_guilds_emojis(self, guild_ids:�list, data_create:�dict, amount:�int�=�10)`
:Mass create emojis in multiple guilds.

Args:
guild_ids (list): A list of guild IDs in which emojis are to be created.
data_create (dict): A dictionary containing the data to create emojis with.
Example:
{
"name": "my_emoji",
"image": "base64_image_data"
# Add more emoji data as needed.
}
amount (int, optional): The number of emojis to create in each guild. Default is 10.

Returns:
dict: A dictionary containing the result of the operation, including created emojis.

Example Usage:
# Mass create emojis in multiple guilds.
guild_ids = [123456789012345678, 234567890123456789]  # Replace with the desired guild IDs.
emoji_data = {
"name": "my_custom_emoji",
"image": "base64_encoded_image_data"
}  # Replace with emoji data.
create_result = await discord_utility.mass_create_guilds_emojis(guild_ids, emoji_data, amount=5)
if create_result["success"]:
print("Created Emojis:")
for guild_id, created_emojis in create_result["created_emojis"].items():
print(f"- Guild ID: {guild_id}, Created Emojis: {created_emojis}")
else:
print(f"Failed to create emojis: {create_result['message']}")

Note:
This method creates emojis in multiple guilds and returns created emoji data.
`mass_delete_guilds_emojis(self, emoji_ids:�dict)`
:Mass delete emojis from multiple guilds.

Args:
emoji_ids (dict): A dictionary where keys are guild IDs and values are lists of emoji IDs to be deleted.

Returns:
dict: A dictionary containing the result of the operation, including deleted emoji IDs.

Example Usage:
# Mass delete emojis from multiple guilds.
emoji_ids = {
123456789012345678: [987654321098765432, 876543210987654321],
234567890123456789: [765432109876543210]
}  # Replace with the desired guild and emoji IDs.
delete_result = await discord_utility.mass_delete_guilds_emojis(emoji_ids)
if delete_result["success"]:
print("Deleted Emojis:")
for guild_id, deleted_emoji_ids in delete_result["deleted_emojis"].items():
print(f"- Guild ID: {guild_id}, Deleted Emoji IDs: {deleted_emoji_ids}")
else:
print(f"Failed to delete emojis: {delete_result['message']}")

Note:
This method deletes emojis from multiple guilds and returns deleted emoji IDs.
`mass_kick(self, guild_ids:�list, timeout=5)`
:Mass kicks users from multiple guilds.

Args:
guild_ids (list): A list of guild IDs from which users are to be kicked.
timeout (int, optional): Timeout for the HTTP request. Default is 5 seconds.

Returns:
dict: A dictionary containing the result of the operation, including kicked user IDs.

Raises:
AssertionError: If guild_ids is not a list.

Example Usage:
# Mass kick users from multiple guilds.
guild_ids = [123456789012345678, 234567890123456789]  # Replace with the desired guild IDs.
kick_result = await discord_utility.mass_kick(guild_ids)
if kick_result["success"]:
print("Kicked Users:")
for guild_id, kicked_users in kick_result["kicked_users"].items():
print(f"- Guild ID: {guild_id}, Kicked Users: {kicked_users}")
else:
print(f"Failed to kick users: {kick_result['message']}")

Note:
This method kicks users from multiple guilds and returns kicked user IDs.
`mass_modify_guilds(self, guild_ids:�list, data_modify:�dict)`
:Mass modify properties of multiple guilds.

Args:
guild_ids (list): A list of guild IDs to be modified.
data_modify (dict): A dictionary containing the data to modify the guilds with.
Example:
{
"name": "New Guild Name",
"region": "us-west",
"verification_level": 2
# Add more properties to modify as needed.
}

Returns:
dict: A dictionary containing the result of the operation, including modified guild IDs.

Raises:
AssertionError: If guild_ids is not a list.

Example Usage:
# Mass modify properties of multiple guilds.
guild_ids = [123456789012345678, 234567890123456789]  # Replace with the desired guild IDs.
modifications = {
"name": "My New Server Name",
"verification_level": 1,
"default_message_notifications": 1
}  # Replace with the properties you want to modify.
modify_result = await discord_utility.mass_modify_guilds(guild_ids, modifications)
if modify_result["success"]:
print("Modified Guilds:")
for guild_id in modify_result["modified_guilds"]:
print(f"- Guild ID: {guild_id}")
else:
print(f"Failed to modify guilds: {modify_result['message']}")

Note:
This method sends HTTP PATCH requests to modify properties of multiple guilds simultaneously.
`mass_modify_guilds_emojis(self, emoji_ids:�dict, data_modify:�dict)`
:Mass modify emojis in multiple guilds.

Args:
emoji_ids (dict): A dictionary containing guild IDs as keys and lists of emoji IDs as values.
Example:
{
123456789012345678: [987654321098765432, 876543210987654321],
234567890123456789: [765432109876543210]
}
data_modify (dict): A dictionary containing the data to modify emojis with.
Example:
{
"name": "new_name",
# Add more emoji data as needed.
}

Returns:
dict: A dictionary containing the result of the operation, including modified emoji data.

Raises:
AssertionError: If emoji_ids is not a dictionary.

Example Usage:
# Mass modify emojis in multiple guilds.
emoji_ids = {
123456789012345678: [987654321098765432, 876543210987654321],
234567890123456789: [765432109876543210]
}  # Replace with the desired guild and emoji IDs.
emoji_data = {
"name": "new_name",
# Modify emoji data as needed.
}  # Replace with the desired modifications.
modify_result = await discord_utility.mass_modify_guilds_emojis(emoji_ids, emoji_data)
if modify_result["success"]:
print("Modified Emojis:")
for guild_id, modified_emoji_ids in modify_result["modified_emojis"].items():
print(f"- Guild ID: {guild_id}, Modified Emoji IDs: {modified_emoji_ids}")
else:
print(f"Failed to modify emojis: {modify_result['message']}")

Note:
This method mass-modifies emojis in multiple guilds and returns modified emoji data.
`mass_modify_guilds_users(self, user_ids:�dict, data_modify:�dict)`
:Mass modify users in multiple guilds.

Args:
user_ids (dict): A dictionary containing user IDs to be modified for each guild.
data_modify (dict): The data to be used for modification.

Returns:
dict: A dictionary containing the result of the operation, including modified user IDs.

Raises:
AssertionError: If user_ids is not a dictionary.

Example Usage:
# Mass modify users in multiple guilds.
user_ids = {
123456789012345678: [987654321098765432, 876543210987654321],
234567890123456789: [765432109876543210]
}  # Replace with the desired user IDs and data_modify.
modify_result = await discord_utility.mass_modify_guilds_users(user_ids, data_modify)
if modify_result["success"]:
print("Modified Users:")
for guild_id, modified_users in modify_result["modified_users"].items():
print(f"- Guild ID: {guild_id}, Modified Users: {modified_users}")
else:
print(f"Failed to modify users: {modify_result['message']}")

Note:
This method mass modifies users in multiple guilds.
`mass_remove_guilds_members_roles(self, user_ids:�dict)`
:Mass-remove roles from members in multiple guilds.

Args:
user_ids (dict): A dictionary containing guild IDs as keys and a list of user IDs and role IDs as values.
Example: {123456789012345678: {"user_ids": [123, 456], "role_ids": [789, 987]}}

Returns:
dict: A dictionary containing the result of the operation, including removed member roles.

Raises:
AssertionError: If user_ids is not a dictionary.

Example Usage:
# Mass-remove roles from members in multiple guilds.
user_ids = {
123456789012345678: {"user_ids": [123, 456], "role_ids": [789, 987]},
987654321098765432: {"user_ids": [789, 654], "role_ids": [321, 654]}
}
result = await discord_utility.mass_remove_guilds_members_roles(user_ids)

if result["success"]:
print(f"Roles removed from members in multiple guilds")
else:
print(f"Failed to remove roles from members: {result['message']}")

Note:
This method removes specified roles from members in multiple guilds and returns the removed member roles.
`mass_unban(self, guild_ids:�list, timeout=5)`
:Mass unbans users from multiple guilds.

Args:
guild_ids (list): A list of guild IDs from which users are to be unbanned.
timeout (int, optional): Timeout for the HTTP request. Default is 5 seconds.

Returns:
dict: A dictionary containing the result of the operation, including unbanned user IDs.

Raises:
AssertionError: If guild_ids is not a list.

Example Usage:
# Mass unban users from multiple guilds.
guild_ids = [123456789012345678, 234567890123456789]  # Replace with the desired guild IDs.
unban_result = asyncio.run(x.mass_unban(guild_ids))
if unban_result["success"]:
print("Unbanned Users:")
for guild_id, unbanned_users in unban_result["unbanned_users"].items():
print(f"- Guild ID: {guild_id}, Unbanned Users: {unbanned_users}")
else:
print(f"Failed to unban users: {unban_result['message']}")

Note:
This method unbans users from multiple guilds and returns unbanned user IDs.
`modify_guild(self, session, guild_id, data_modify, modified_guilds={}, total_ratelimits=0)`
:Modify properties of a specific guild.

Args:
session (aiohttp.ClientSession): An aiohttp client session.
guild_id (int): The ID of the guild to modify.
data_modify (dict): A dictionary containing the data to modify the guild with.
Example:
{
"name": "New Guild Name",
"region": "us-west",
"verification_level": 2
# Add more properties to modify as needed.
}
modified_guilds (list, optional): A list to store modified guild IDs.
total_ratelimits (int, optional): A counter for tracking rate limits.

Returns:
list: A list containing the modified guild IDs.

Example Usage:
# Modify properties of a specific guild.
guild_id = 123456789012345678  # Replace with the desired guild ID.
modifications = {
"name": "My New Server Name",
"verification_level": 1,
"default_message_notifications": 1
}  # Replace with the properties you want to modify.
modified_guilds = await discord_utility.modify_guild(session, guild_id, modifications)
if guild_id in modified_guilds:
print(f"Modified Guild ID: {guild_id}")
else:
print(f"Failed to modify guild ID: {guild_id}")

Note:
This method sends an HTTP PATCH request to modify properties of a specific guild.
`modify_guild_emoji(self, session, guild_id, emoji_id, data_modify, modified_emojis={}, total_ratelimits=0)`
:Modify a guild emoji.

Args:
session (aiohttp.ClientSession): The aiohttp session for making HTTP requests.
guild_id (int): The ID of the guild where the emoji belongs.
emoji_id (int): The ID of the emoji to be modified.
data_modify (dict): A dictionary containing the data to modify the emoji with.
modified_emojis (dict, optional): A dictionary to store the modified emoji data. Defaults to an empty dictionary.
total_ratelimits (int, optional): The total number of rate limits encountered. Defaults to 0.

Returns:
dict: A dictionary containing the result of the operation, including the modified emoji data.

Example Usage:
# Modify a guild emoji.
guild_id = 123456789012345678  # Replace with the desired guild ID.
emoji_id = 987654321098765432  # Replace with the desired emoji ID.
emoji_data = {
"name": "new_name",
# Modify emoji data as needed.
}  # Replace with the desired modifications.
modify_result = await discord_utility.modify_guild_emoji(session, guild_id, emoji_id, emoji_data)
if modify_result["success"]:
print("Modified Emoji Data:")
print(modify_result["modified_emoji"])
else:
print(f"Failed to modify emoji: {modify_result['message']}")

Note:
This method modifies a guild emoji and returns the modified emoji data.
`modify_guild_user(self, session, guild_id, user_id, data_modify, modified_users={}, total_ratelimits=0)`
:Modify a user in a specific guild.

Args:
session (aiohttp.ClientSession): An aiohttp session for making HTTP requests.
guild_id (int): The ID of the guild in which the user should be modified.
user_id (int): The ID of the user to be modified.
data_modify (dict): The data to be used for modification.
modified_users (dict, optional): A dictionary to store modified user IDs for each guild.
total_ratelimits (int, optional): The total number of rate limits encountered.

Returns:
dict: A dictionary containing the result of the operation, including the modified user ID.

Note:
This method modifies a user in a specific guild.
`remove_guild_member_role(self, session, guild_id, user_id, role_id, removed_member_roles={}, total_ratelimits=0)`
:Mass-remove roles from members in multiple guilds.

Args:
user_ids (dict): A dictionary containing guild IDs as keys and a list of user IDs and role IDs as values.
Example: {123456789012345678: {"user_ids": [123, 456], "role_ids": [789, 987]}}

Returns:
dict: A dictionary containing the result of the operation, including removed member roles.

Raises:
AssertionError: If user_ids is not a dictionary.

Example Usage:
# Mass-remove roles from members in multiple guilds.
user_ids = {
123456789012345678: {"user_ids": [123, 456], "role_ids": [789, 987]},
987654321098765432: {"user_ids": [789, 654], "role_ids": [321, 654]}
}
result = await discord_utility.mass_remove_guilds_members_roles(user_ids)

if result["success"]:
print(f"Roles removed from members in multiple guilds")
else:
print(f"Failed to remove roles from members: {result['message']}")

Note:
This method removes specified roles from members in multiple guilds and returns the removed member roles.
`single_ban(self, session, url, user_id, banned_users, total_ratelimit, timeout, guild_id)`
:Bans a single user from a guild.

Args:
session (aiohttp.ClientSession): The aiohttp session to use for the HTTP request.
url (str): The URL to ban the user.
user_id (int): The ID of the user to be banned.
banned_users (dict): A dictionary to store banned user IDs.
total_ratelimit (list): A list to store the total rate limits encountered.
timeout (int): Timeout for the HTTP request.
guild_id (int): The ID of the guild.

Returns:
bool: True if the user was banned successfully, False otherwise.

Example Usage:
# Ban a single user from a guild.
session = aiohttp.ClientSession()
url = "https://discord.com/api/v10/guilds/123456789012345678/members/987654321098765432"
user_id = 987654321098765432
banned = await discord_utility.single_ban(session, url, user_id, banned_users, total_ratelimit, timeout=5, guild_id=123456789012345678)
session.close()
if banned:
print(f"Successfully banned user with ID: {user_id}")
else:
print(f"Failed to ban user with ID: {user_id}")

Note:
This method bans a single user from a guild and returns True if successful.
`single_kick(self, session, url, user_id, kicked_users, total_ratelimit, timeout, guild_id)`
:Kicks a single user from a guild.

Args:
session (aiohttp.ClientSession): The aiohttp session to use for the HTTP request.
url (str): The URL to kick the user.
user_id (int): The ID of the user to be kicked.
kicked_users (dict): A dictionary to store kicked user IDs.
total_ratelimit (list): A list to store the total rate limits encountered.
timeout (int): Timeout for the HTTP request.
guild_id (int): The ID of the guild.

Returns:
bool: True if the user was kicked successfully, False otherwise.

Example Usage:
# Kick a single user from a guild.
session = aiohttp.ClientSession()
url = "https://discord.com/api/v10/guilds/123456789012345678/members/987654321098765432"
user_id = 987654321098765432
kicked = await discord_utility.single_kick(session, url, user_id, kicked_users, total_ratelimit, timeout=5, guild_id=123456789012345678)
session.close()
if kicked:
print(f"Successfully kicked user with ID: {user_id}")
else:
print(f"Failed to kick user with ID: {user_id}")

Note:
This method kicks a single user from a guild and returns True if successful.
`single_unban(self, session, url, user_id, unbanned_users, total_ratelimit, timeout, guild_id)`
:Unbans a single user from a guild.

Args:
session (aiohttp.ClientSession): The aiohttp session to use for the HTTP request.
url (str): The URL to unban the user.
user_id (int): The ID of the user to be unbanned.
unbanned_users (dict): A dictionary to store unbanned user IDs.
total_ratelimit (list): A list to store the total rate limits encountered.
timeout (int): Timeout for the HTTP request.
guild_id (int): The ID of the guild.

Returns:
bool: True if the user was unbanned successfully, False otherwise.

Example Usage:
# Unban a single user from a guild.
session = aiohttp.ClientSession()
url = "https://discord.com/api/v10/guilds/123456789012345678/bans/987654321098765432"
user_id = 987654321098765432
unbanned = await x.single_unban(session, url, user_id, unbanned_users, total_ratelimit, timeout=5, guild_id=123456789012345678)
session.close()
if unbanned:
print(f"Successfully unbanned user with ID: {user_id}")
else:
print(f"Failed to unban user with ID: {user_id}")

Note:
This method unbans a single user from a guild and returns True if successful.
`spam_guild_channel(self, session, channel_id, amount, data_message, method='bot', data_webhook={}, spammed_channels=[], total_ratelimits=0)`
:Spam a channel with messages.

Args:
session (aiohttp.ClientSession): The aiohttp session to use for the HTTP request.
channel_id (int): The ID of the channel to spam.
amount (int): The number of messages to send in the channel.
data_message (dict): The JSON data for the message to be sent.
method (str): The spam method, either "bot" or "webhook."
data_webhook (dict): The JSON data for creating a webhook if method is "webhook."
spammed_channels (list): A list to store IDs of channels that have been spammed.
total_ratelimits (int): The total number of rate limits encountered.

Returns:
list: A list of channel IDs that have been spammed.

Example Usage:
# Spam a channel with messages using bot accounts.
session = aiohttp.ClientSession()
channel_id = 123456789012345678
amount = 5
data_message = {"content": "Hello, world!"}
method = "bot"
spammed = await discord_utility.spam_guild_channel(session, channel_id, amount, data_message, method)
session.close()
if spammed:
print(f"Successfully spammed channel ID: {channel_id}")
else:
print(f"Failed to spam channel ID: {channel_id}")

Note:
This method spams a channel with messages using bot accounts or webhooks.
`spam_guilds_channels(self, channel_ids:�list, amount:�int�=�10, data_message:�dict�=�{'content': '@everyone'}, data_webhook:�dict�=�{'name': ':)'}, method:�str�=�'bot')`
:Spams channels in multiple guilds with messages.

Args:
channel_ids (list): A list of channel IDs to spam with messages.
amount (int, optional): The number of messages to send in each channel. Default is 10.
data_message (dict, optional): The JSON data for the message to be sent. Default mentions "@everyone."
data_webhook (dict, optional): The JSON data for creating a webhook if method is "webhook."
method (str, optional): The spam method, either "bot" or "webhook." Default is "bot."

Returns:
dict: A dictionary containing the result of the operation, including the spammed channels.

Example Usage:
# Spam channels in multiple guilds with messages using bot accounts.
channel_ids = [123456789012345678, 234567890123456789]  # Replace with the desired channel IDs.
spam_result = await discord_utility.spam_guilds_channels(channel_ids, amount=5)
if spam_result["success"]:
print("Spammed Channels:")
for channel_id in spam_result["spammed_channels"]:
print(f"- Channel ID: {channel_id}")
else:
print(f"Failed to spam channels: {spam_result['message']}")

Note:
This method spams channels in multiple guilds with messages using bot accounts or webhooks.
