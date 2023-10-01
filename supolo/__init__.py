import logging
import aiohttp
import asyncio
import time

class supolo:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    def __init__(self, tokenType, token, skipOnRatelimit=False, ratelimitCooldown=1):
        self.url = "https://discord.com/api/v10"
        self.skipOnRatelimit = skipOnRatelimit
        self.ratelimitCooldown = ratelimitCooldown
        
        self.token = token if tokenType == "user" else f"Bot {token}" if tokenType == "bot" else None
        assert self.token, "Invalid token type given, Types: ['user', 'bot]"
        
        response = asyncio.run(self._check_token())
        assert response, "Invalid Token provided"
        
        
        logging.info(f"Logged in as {response.get('username')}#{response.get('discriminator')}")
    
    async def _check_token(self):
        async with aiohttp.ClientSession(headers = {'Authorization': self.token}, connector=aiohttp.TCPConnector(limit=None)) as session:
            async with session.get(f"{self.url}/users/@me") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return False
    
    async def get_servers(self):
        """
        Retrieves a list of servers (guilds) that the bot is a member of.

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
        """
        start_time = time.perf_counter()
        total_ratelimits = 0
        logging.debug(f'Starting scraping servers')
        async with aiohttp.ClientSession(headers = {'Authorization': self.token}, connector=aiohttp.TCPConnector(limit=None)) as session:
            async with session.get(f'{self.url}/users/@me/guilds') as response:
                if response.status == 200:
                    guilds_data = await response.json()
                    end_time = time.perf_counter() - start_time
                    return {'success': True, 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "servers": guilds_data}
                elif response.status == 429:
                    total_ratelimits += 1
                    if self.skipOnRatelimit:
                        end_time = time.perf_counter() - start_time
                        try:
                            error_message = (await response.json()).get("message")
                        except:
                            error_message = "Couldn't scrape error message"
                        return {"success": False, 'message': error_message, 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "servers": []}
                    else:
                        await asyncio.sleep(self.ratelimitCooldown)
                else:
                    end_time = time.perf_counter() - start_time
                    try:
                        error_message = (await response.json()).get("message")
                    except:
                        error_message = "Couldn't scrape error message"
                    return {"success": False, 'message': error_message, 'time_taken': end_time, 'total_ratelimits': total_ratelimits, 'servers': []}
            
    async def get_shared_user_ids(self):
        """
        Retrieves shared user IDs across all servers (guilds) the bot is a member of.

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
        """
        start_time = time.perf_counter()
        
        shared_users = {}
        total_ratelimits = 0
        
        logging.debug('Started fetching users')
        while True:
            async with aiohttp.ClientSession(headers = {'Authorization': self.token}, connector=aiohttp.TCPConnector(limit=None)) as session:
                guilds_data = await self.get_servers()
                if not guilds_data["success"]:
                    return {"success": False, 'message': guilds_data["error_message"], 'time_taken': guilds_data["end_time"], 'total_ratelimits': guilds_data["total_ratelimits"], 'users': {}}
                guild_tasks = []
                for guild in guilds_data['servers']:
                    guild_id = guild['id']
                    guild_url = f'{self.url}/guilds/{guild_id}/members?limit=1000'
                    guild_tasks.append(self.get_guild_members(session, guild_url, shared_users, guild_id, total_ratelimits, "get_shared_user_ids"))
                        
                await asyncio.gather(*guild_tasks)
                    
                end_time = time.perf_counter() - start_time
                return {'success': bool(shared_users), 'time_taken': end_time, 'total_ratelimits': total_ratelimits + guilds_data["total_ratelimits"], "users": shared_users}

    async def get_guilds_channels(self, guild_ids: list):
        """
        Retrieves information about channels within specified guilds.

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
        """
        start_time = time.perf_counter()
        assert isinstance(guild_ids, list), "Guild IDs should be a list"
        shared_channels = {}
        total_ratelimits = 0
        async with aiohttp.ClientSession(headers = {'Authorization': self.token}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = [self.get_guild_channels(session, guild_id, shared_channels, total_ratelimits) for guild_id in guild_ids]
            await asyncio.gather(*tasks)
        end_time = time.perf_counter() - start_time
        return {'success': bool(shared_channels), 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "channels": shared_channels}
        
    async def get_guild_channels(self, session, guild_id, shared_channels={}, total_ratelimits=0):
        """
        Retrieves information about channels within a specific guild.

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
        """
        logging.debug(f'Started fetching channels in guild: {guild_id}')
        
        while True:   
         async with session.get(f"{self.url}/guilds/{guild_id}/channels") as response:
            if response.status == 200:
                data = await response.json()
                shared_channels[str(guild_id)] = data
                break
            elif response.status == 429:
                total_ratelimits += 1
                if not self.skipOnRatelimit:
                    await asyncio.sleep(self.ratelimitCooldown)
                else:
                    break
            else:
                return shared_channels

        return shared_channels

    async def delete_guild_channel(self, session, channel_id, deleted_channels=[], total_ratelimits=0):
        """
        Deletes a channel within a guild.

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
        """
        logging.debug(f'Started deleting channel: {channel_id}')
        while True:   
         async with session.delete(f"{self.url}/channels/{channel_id}") as response:
            if response.status == 200:
                deleted_channels.append(channel_id)
                break
            elif response.status == 429:
                total_ratelimits += 1
                if not self.skipOnRatelimit:
                    await asyncio.sleep(self.ratelimitCooldown)
                else:
                    break
            else:
                break
        return deleted_channels
        
    async def delete_guilds_channels(self, channel_ids: list):
        """
        Deletes multiple channels within a guild.

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
        """
        start_time = time.perf_counter()
        assert isinstance(channel_ids, list), "channel_ids IDs should be a list"
        total_ratelimits = 0
        deleted_channels = []
        async with aiohttp.ClientSession(headers = {'Authorization': self.token}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = [self.delete_guild_channel(session, channel_id, deleted_channels, total_ratelimits) for channel_id in channel_ids]
            await asyncio.gather(*tasks)
        end_time = time.perf_counter() - start_time
        return {'success': bool(deleted_channels), 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "deleted_channels": deleted_channels}    
            
    async def get_guilds_members(self, guild_ids: list):
        """
        Fetches members of multiple guilds.

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
        """
        start_time = time.perf_counter()
        assert isinstance(guild_ids, list), "guild_ids has to be a list"
        logging.debug(f'Started fetching users in guilds {" ".join(str(guild_id) for guild_id in guild_ids)}')
        async with aiohttp.ClientSession(headers = {'Authorization': self.token}, connector=aiohttp.TCPConnector(limit=None)) as session:
            guild_tasks = []
            shared_users = {}
            total_ratelimits = 0
            
            for guild_id in guild_ids:
                guild_tasks.append(self.get_guild_members(session, f'{self.url}/guilds/{guild_id}/members?limit=1000', shared_users, guild_id, total_ratelimits, "get_shared_user_ids"))
            await asyncio.gather(*guild_tasks)
            
            return {"success": bool(shared_users), 'time_taken': time.perf_counter() - start_time, "total_ratelimits": total_ratelimits, 'users': shared_users}

    async def get_guild_members(self, session=None, url=None, shared_users={}, guild_id=None, total_ratelimits=0, method=None):
        """
        Fetches members of a specific guild.

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
        """
        assert guild_id, "Required guild_id value"
        assert method, "Reqired method value, Types: ['get_shared_user_ids', 'get_guild_members']"
        assert session, "Aiohttp session is requried for this function"
        assert session.headers.get('Authorization'), "Authorization is required in headers"
        logging.debug(f'Started fetching users in guild: {guild_id}')
        if url is None:
            url = f'{self.url}/guilds/{guild_id}/members?limit=1000'
        url_copy = url
        while True:
            async with session.get(url) as guild_response:
                if guild_response.status == 200:
                    members_data = await guild_response.json()
                    for member in members_data:
                        user_id = member['user']['id']
                        if user_id in shared_users:
                            shared_users[user_id]['shared_guilds'].append(guild_id)
                        else:
                            member['user']["shared_guilds"] = [guild_id]
                            shared_users[user_id] = member['user']
                    if len(members_data) < 1000:
                        return shared_users
                    else:
                        url = url_copy + f"&after={members_data[-1]['user']['id']}"
                            
                elif guild_response.status == 429:
                    total_ratelimits += 1
                    if not self.skipOnRatelimit:
                        await asyncio.sleep(self.ratelimitCooldown)
                    else:
                        break
                else:
                    return {}
    
    async def mass_unban(self, guild_ids: list, timeout=5):
        """
        Mass unbans users from multiple guilds.

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
        """
        start_time = time.perf_counter()
        assert isinstance(guild_ids, list), "guild_ids has to be a list"
        logging.debug(f'Started mass unban on guild_ids: {" ".join(str(guild_id) for guild_id in guild_ids)}')
        unbanned_users = {}
        total_ratelimit = [0]
        unban_tasks = []
        users = (await self.get_guilds_banned_users(guild_ids))['banned_users']
        async with aiohttp.ClientSession(headers={'Authorization': self.token}, connector=aiohttp.TCPConnector(limit=None)) as session:
            for guild in users:
                if str(guild) not in unbanned_users:
                    unbanned_users[str(guild)] = []
                    
                for user in users[str(guild)]:
                    unban_tasks.append(
                    self.single_unban(session=session, url=f"{self.url}/guilds/{guild}/bans/{user['id']}",
                                      user_id=user['id'], unbanned_users=unbanned_users,
                                      total_ratelimit=total_ratelimit, timeout=timeout, guild_id=guild))
            await asyncio.gather(*unban_tasks)
        return {"success": bool(unbanned_users), 'time_taken': time.perf_counter() - start_time, "total_ratelimits": total_ratelimit[0], 'unbanned_users': unbanned_users}
        
        
    async def single_unban(self, session, url, user_id, unbanned_users, total_ratelimit, timeout, guild_id):
        """
        Unbans a single user from a guild.

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
        """
        while True:
            try:
                async with session.delete(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                    print(response.status)
                    if response.status == 204:
                        unbanned_users[str(guild_id)].append(user_id)
                        return True
                    elif response.status == 429:
                        total_ratelimit[0] += 1
                        if not self.skipOnRatelimit:
                            await asyncio.sleep(self.ratelimitCooldown)
                        else:
                            return False
                    else:
                        return False
            except:
                return False

    async def mass_kick(self, guild_ids: list, timeout=5):
        """
        Mass kicks users from multiple guilds.

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
        """
        start_time = time.perf_counter()
        assert isinstance(guild_ids, list), "guild_ids has to be a list"
        logging.debug(f'Started mass kicking users in guilds {" ".join(str(guild_id) for guild_id in guild_ids)}')
        guilds = (await self.get_guilds_members(guild_ids))['users']
        kick_tasks = []
        total_ratelimit = [0]
        kicked_users = {}
        async with aiohttp.ClientSession(headers = {'Authorization': self.token}, connector=aiohttp.TCPConnector(limit=None)) as session:
            for user in guilds:
                for guild_id in guilds[user]["shared_guilds"]:
                    if str(guild_id) not in kicked_users:
                        kicked_users[str(guild_id)] = []
                    kick_tasks.append(self.single_kick(session, f"{self.url}/guilds/{guild_id}/members/{user}", user, kicked_users, total_ratelimit, timeout, guild_id))
            await asyncio.gather(*kick_tasks)
            return {"success": bool(kicked_users), 'time_taken': time.perf_counter() - start_time, "total_ratelimits": total_ratelimit[0], 'kicked_users': kicked_users}


    async def single_kick(self, session, url, user_id, kicked_users, total_ratelimit, timeout, guild_id):
        """
        Kicks a single user from a guild.

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
        """
        while True:
            try:
                async with session.delete(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                    if response.status == 204:
                        kicked_users[str(guild_id)].append(user_id)
                        return True
                    elif response.status == 429:
                        total_ratelimit[0] += 1
                        if not self.skipOnRatelimit:
                            await asyncio.sleep(self.ratelimitCooldown)
                        else:
                            return False
                    else:
                        return False
            except:
                return False

    async def get_guilds_banned_users(self, guild_ids: list):
        """
        Fetches banned users from multiple guilds.

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
        """
        start_time = time.perf_counter()
        assert isinstance(guild_ids, list), "guild_ids has to be a list"
        logging.debug(f'Started fetching banned users in guilds {" ".join(str(guild_id) for guild_id in guild_ids)}')
        async with aiohttp.ClientSession(headers = {'Authorization': self.token}, connector=aiohttp.TCPConnector(limit=None)) as session:
            guild_tasks = []
            banned_users = {}
            total_ratelimits = 0
            
            for guild_id in guild_ids:
                guild_tasks.append(self.get_guild_banned_users(guild_id, banned_users, total_ratelimits))
            await asyncio.gather(*guild_tasks)
            
            return {"success": bool(banned_users), 'time_taken': time.perf_counter() - start_time, "total_ratelimits": total_ratelimits, 'banned_users': banned_users}
        
    async def get_guild_banned_users(self, guild_id, banned_users={}, total_ratelimits=0):
        """
        Fetches banned users from a specific guild.

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
        """
        assert isinstance(banned_users, dict), "banned_users has to be a dict"
        after = None
        start_time = time.perf_counter()
        logging.debug(f'Started fetching banned users in guild: {guild_id}')
        if not str(guild_id) in banned_users:
            banned_users[str(guild_id)] = []
        async with aiohttp.ClientSession(headers={'Authorization': self.token}, connector=aiohttp.TCPConnector(limit=None)) as session:
            while True:
                url = f"{self.url}/guilds/{guild_id}/bans?limit=1000"
                if after:
                    url += f"&after={after}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        for ban in data:
                            banned_users[str(guild_id)].append(ban['user'])
                        if len(data) < 1000:
                            break
                        after = data[-1]['user']['id']
                    elif response.status == 429:
                        if not self.skipOnRatelimit:
                            await asyncio.sleep(self.ratelimitCooldown)
                        else:
                            break
                    else:
                        logging.error(f"Failed to fetch banned users for guild {guild_id}: {response.status}")
                        break
        return {"success": bool(banned_users[str(guild_id)]), 'time_taken': time.perf_counter() - start_time, 'total_ratelimits': total_ratelimits, "users": banned_users[str(guild_id)]}
    
    async def mass_ban(self, guild_ids: list, timeout: int =5):
        """
        Mass bans users in multiple guilds.

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
        """
        start_time = time.perf_counter()
        assert isinstance(guild_ids, list), "guild_ids has to be a list"
        logging.debug(f'Starting mass ban on guild_ids: {" ".join(str(guild_id) for guild_id in guild_ids)}')
        users = (await self.get_guilds_members(guild_ids))['users']
        async with aiohttp.ClientSession(headers={'Authorization': self.token}, connector=aiohttp.TCPConnector(limit=None)) as session:
            ban_tasks = []
            banned_users = {}
            total_ratelimit = [0]
            for user in users:
                for guild_id in users[user]["shared_guilds"]:
                    if str(guild_id) not in banned_users:
                        banned_users[str(guild_id)] = []
                    ban_tasks.append(self.single_ban(session, f"{self.url}/guilds/{guild_id}/bans/{user}", user, banned_users, total_ratelimit, timeout, guild_id))
            await asyncio.gather(*ban_tasks)
            return {'success': bool(banned_users), 'time_taken': time.perf_counter() - start_time, 'total_ratelimits': total_ratelimit[0], "banned_users": banned_users}

    async def single_ban(self, session, url, user_id, banned_users, total_ratelimit, timeout, guild_id):
        """
        Bans a single user from a guild.

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
        """
        while True:
            try:
                async with session.put(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                    if response.status == 204:
                        banned_users[str(guild_id)].append(user_id)
                        return True
                    elif response.status == 429:
                        total_ratelimit[0] += 1
                        if not self.skipOnRatelimit:
                            await asyncio.sleep(self.ratelimitCooldown)
                        else:
                            return False
                    else:
                        return False
            except:
                return False
    
    async def create_guild_channel(self, session, guild_id, data, created_channels={}, total_ratelimits=0):
        """
        Creates a channel in a guild.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the HTTP request.
            guild_id (int): The ID of the guild in which the channel will be created.
            data (dict): The JSON data to be sent in the request body.
            created_channels (dict): A dictionary to store information about created channels.
            total_ratelimits (int): The total number of rate limits encountered.

        Returns:
            dict: A dictionary containing information about the created channel.

        Example Usage:
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

        Note:
            This method creates a channel in a guild and returns information about the created channel.
        """
        logging.debug(f'Started creating channel in guild: {guild_id}')
        while True:   
         async with session.post(f"{self.url}/guilds/{guild_id}/channels", json=data) as response:
            if response.status == 201:
                if not str(guild_id) in created_channels:
                    created_channels[str(guild_id)] = []
                created_channels[str(guild_id)].append(await response.json())
                break
            elif response.status == 429:
                total_ratelimits += 1
                if not self.skipOnRatelimit:
                    await asyncio.sleep(self.ratelimitCooldown)
                else:
                    break
            else:
                break
        return created_channels
    
    async def create_guilds_channels(self, guild_ids: list, data: dict, amount: int =10):
        """
        Creates channels in multiple guilds.

        Args:
            guild_ids (list): A list of guild IDs in which channels will be created.
            data (dict): The JSON data to be sent in the request body.
            amount (int, optional): The number of channels to create in each guild. Default is 10.

        Returns:
            dict: A dictionary containing the result of the operation, including created channels.

        Example Usage:
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

        Note:
            This method creates channels in multiple guilds and returns information about the created channels.
        """
        start_time = time.perf_counter()
        assert isinstance(guild_ids, list), "guild_ids IDs should be a list"
        total_ratelimits = 0
        created_channels = {}
        async with aiohttp.ClientSession(headers = {'Authorization': self.token}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = []
            for guild_id in guild_ids:
                for i in range(amount):
                    tasks.append(self.create_guild_channel(session, guild_id, data, created_channels, total_ratelimits))
                    
            await asyncio.gather(*tasks)
        end_time = time.perf_counter() - start_time
        return {'success': bool(created_channels), 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "created_channels": created_channels} 
    
    async def spam_guilds_channels(self, channel_ids: list, amount: int =10, data_message: dict ={"content": "@everyone"}, data_webhook: dict ={"name": ":)"}, method: str ="bot"):
        """
        Spams channels in multiple guilds with messages.

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
        """
        start_time = time.perf_counter()
        assert method in ["bot", "webhook"], "Method has to be in ['bot', 'webhook']"
        assert isinstance(channel_ids, list), "Channel ids has to be a list"
        spammed_channels = []
        total_ratelimits = 0       
        async with aiohttp.ClientSession(headers = {'Authorization': self.token}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = [self.spam_guild_channel(session, channel_id, amount, data_message, method, data_webhook, spammed_channels, total_ratelimits) for channel_id in channel_ids]
            await asyncio.gather(*tasks)
        
        end_time = time.perf_counter() - start_time
        return {'success': bool(spammed_channels), 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "spammed_channels": spammed_channels}

    async def spam_guild_channel(self, session, channel_id, amount, data_message, method="bot", data_webhook={}, spammed_channels=[], total_ratelimits=0):
        """
        Spam a channel with messages.

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
        """
        logging.debug(f'Started spamming channel ID: {channel_id}')
        url = f"{self.url}/channels/{channel_id}/messages"
        if method == "webhook":
            webhook = await self.create_channel_webhook(session, channel_id, data_webhook)
            if webhook.get("token") and webhook.get("id"):
                url = f"{self.url}/webhooks/{webhook.get('id')}/{webhook.get('token')}"
        
        for i in range(amount):
         while True:   
          async with session.post(url, json=data_message) as response:
            if response.status in [201, 200, 204]:
                if not channel_id in spammed_channels:
                    spammed_channels.append(channel_id)
                break
            elif response.status == 429:
                total_ratelimits += 1
                if not self.skipOnRatelimit:
                    await asyncio.sleep(self.ratelimitCooldown)
                else:
                    break
            else:
                return spammed_channels
        return spammed_channels
    
    async def create_channel_webhook(self, session, channel_id, data_webhook):
        """
        Create a webhook in a channel.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the HTTP request.
            channel_id (int): The ID of the channel in which to create the webhook.
            data_webhook (dict): The JSON data for creating the webhook.

        Returns:
            dict: A dictionary containing information about the created webhook.

        Example Usage:
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

        Note:
            This method creates a webhook in a channel and returns information about the created webhook.
        """
        logging.debug(f'Started creating webhook in channel ID: {channel_id}')
        while True:   
         async with session.post(f"{self.url}/channels/{channel_id}/webhooks", json=data_webhook) as response:
            if response.status in [201, 200, 204]:
                return await response.json()
            elif response.status == 429:
                total_ratelimits += 1
                if not self.skipOnRatelimit:
                    await asyncio.sleep(self.ratelimitCooldown)
                else:
                    break
            else:
                break
        return {}
    
    async def create_guilds_roles(self, guild_ids: list, data_role: dict = {}, amount: int =10):
        """
        Creates roles in multiple guilds.

        Args:
            guild_ids (list): A list of guild IDs in which roles will be created.
            data_role (dict): The JSON data for the role to be created.
            amount (int, optional): The number of roles to create in each guild. Default is 10.

        Returns:
            dict: A dictionary containing the result of the operation, including created roles.

        Example Usage:
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

        Note:
            This method creates roles in multiple guilds and returns information about the created roles.
        """
        start_time = time.perf_counter()
        assert isinstance(guild_ids, list), "guild_ids has to be a list"
        created_roles = {}
        total_ratelimits = 0       
        async with aiohttp.ClientSession(headers = {'Authorization': self.token}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = []
            for guild_id in guild_ids:
                for i in range(amount):
                    tasks.append(self.create_guild_role(session, guild_id, data_role, created_roles, total_ratelimits))
            await asyncio.gather(*tasks)
        
        end_time = time.perf_counter() - start_time
        return {'success': bool(created_roles), 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "created_roles": created_roles}
    
    async def create_guild_role(self, session, guild_id, data_role, created_roles={}, total_ratelimits=0):
        """
        Create a role in a guild.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the HTTP request.
            guild_id (int): The ID of the guild in which to create the role.
            data_role (dict): The JSON data for the role to be created.
            created_roles (dict): A dictionary to store information about created roles.
            total_ratelimits (int): The total number of rate limits encountered.

        Returns:
            dict: A dictionary containing information about the created role.

        Example Usage:
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

        Note:
            This method creates a role in a guild and returns information about the created role.
        """
        logging.debug(f'Started creating role in guild ID: {guild_id}')
        while True:   
         async with session.post(f"{self.url}/guilds/{guild_id}/roles", json=data_role) as response:
            if response.status in [201, 200, 204]:
                if not str(guild_id) in created_roles:
                    created_roles[str(guild_id)] = []
                created_roles[str(guild_id)].append(await response.json())
                break
            elif response.status == 429:
                total_ratelimits += 1
                if not self.skipOnRatelimit:
                    await asyncio.sleep(self.ratelimitCooldown)
                else:
                    break
            else:
                break
        return created_roles

    async def modify_guilds_roles_position(self, guild_ids: list, data_role: dict = {}):
        """
    Modify the position of roles in multiple guilds.

    Args:
        guild_ids (list): A list of guild IDs where role positions will be modified.
        data_role (dict, optional): A dictionary containing the role data to be applied.

    Returns:
        dict: A dictionary containing the result of the modification operation, including modified role positions.

    Raises:
        AssertionError: If guild_ids is not a list.

    Example Usage:
        # Modify the position of roles in multiple guilds.
        guild_ids = [123456789012345678, 987654321098765432]
        data_role = {"name": "New Role", "position": 3}
        result = await discord_utility.modify_guilds_roles_position(guild_ids, data_role)

        if result["success"]:
            print(f"Role positions modified in multiple guilds")
        else:
            print(f"Failed to modify role positions: {result['message']}")

    Note:
        This method modifies the position of roles in multiple guilds and returns the modified role positions.
        """
        start_time = time.perf_counter()
        assert isinstance(guild_ids, list), "guild_ids has to be a list"
        modified_roles = {}
        total_ratelimits = 0       
        async with aiohttp.ClientSession(headers = {'Authorization': self.token}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = []
            for guild_id in guild_ids:
                    tasks.append(self.modify_guild_role_position(session, guild_id, data_role, modified_roles, total_ratelimits))
            await asyncio.gather(*tasks)
        
        end_time = time.perf_counter() - start_time
        return {'success': bool(modified_roles), 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "modified_roles": modified_roles}
    
    async def modify_guild_role_position(self, session, guild_id, data_role, modified_roles={}, total_ratelimits=0):
        """
    Modify the position of a role in a guild.

    Args:
        session: The aiohttp session for making HTTP requests.
        guild_id (int): The ID of the guild where the role is located.
        data_role (dict): A dictionary containing role data, including the role ID and the new position.
        modified_roles (dict, optional): A dictionary to store modified role data (used for tracking multiple modifications).
        total_ratelimits (int, optional): A counter to track the total number of ratelimit responses received.

    Returns:
        dict: A dictionary containing the result of the modification operation, including the modified role data.

    Note:
        This method modifies the position of a role in a guild and returns the modified role data.

    Example Usage:
        # Define the guild ID where you want to modify role positions
        guild_id = 123456789012345678  # Replace with your guild's ID

        # Define the role data that specifies the changes you want to make
        data_role = {
            "id": 123,  # Role ID to modify
            "position": 2  # New position for the role
        }

        # Call the modify_guild_role_position method to modify the role position
        result = await discord_utility.modify_guild_role_position(session, guild_id, data_role)

        if result["success"]:
            print(f"Role positions modified in guild {guild_id}")
        else:
            print(f"Failed to modify role positions: {result['message']}")
        """
        logging.debug(f'Started modifying role position in guild ID: {guild_id}')
        while True:   
         async with session.patch(f"{self.url}/guilds/{guild_id}/roles", json=data_role) as response:
            if response.status in [201, 200, 204]:
                if not str(guild_id) in modified_roles:
                    modified_roles[str(guild_id)] = []
                modified_roles[str(guild_id)].append(await response.json())
                break
            elif response.status == 429:
                total_ratelimits += 1
                if not self.skipOnRatelimit:
                    await asyncio.sleep(self.ratelimitCooldown)
                else:
                    break
            else:
                break
        return modified_roles

    async def modify_guilds_roles(self, role_ids: dict, data_role: dict = {}):
            """
    Modify roles in multiple guilds.

    Args:
        role_ids (dict): A dictionary containing guild IDs as keys and a list of role IDs as values.
            Example: {123456789012345678: [123, 456], 987654321098765432: [789, 987]}
        data_role (dict, optional): A dictionary containing role data to apply to all specified roles.

    Returns:
        dict: A dictionary containing the result of the modification operation, including the modified roles.

    Raises:
        AssertionError: If role_ids is not a dictionary.

    Example Usage:
        # Modify roles in multiple guilds.
        role_ids = {
            123456789012345678: [123, 456],
            987654321098765432: [789, 987]
        }
        data_role = {
            "color": 0xFF0000  # Change role color to red
        }
        result = await discord_utility.modify_guilds_roles(role_ids, data_role)

        if result["success"]:
            print(f"Roles modified in multiple guilds")
        else:
            print(f"Failed to modify roles: {result['message']}")

    Note:
        This method modifies specified roles in multiple guilds and returns the modified roles.
            """
            start_time = time.perf_counter()
            assert isinstance(role_ids, dict), "role_ids has to be a list"
            modified_roles = {}
            total_ratelimits = 0       
            async with aiohttp.ClientSession(headers = {'Authorization': self.token}, connector=aiohttp.TCPConnector(limit=None)) as session:
                tasks = []
                for guild_id in role_ids:
                    for role_id in role_ids[guild_id]:
                        tasks.append(self.modify_guild_role(session, guild_id, role_id, data_role, modified_roles, total_ratelimits))
                await asyncio.gather(*tasks)
            
            end_time = time.perf_counter() - start_time
            return {'success': bool(modified_roles), 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "modified_roles": modified_roles}
    
    async def modify_guild_role(self, session, guild_id, role_id, data_role, modified_roles={}, total_ratelimits=0):
        """
        Modify a role in a guild.

        Args:
            session: The aiohttp session for making HTTP requests.
            guild_id (int): The ID of the guild where the role is located.
            role_id (int): The ID of the role to be modified.
            data_role (dict): A dictionary containing role data to apply to the specified role.
            modified_roles (dict, optional): A dictionary to store modified role IDs (used for tracking multiple modifications).
            total_ratelimits (int, optional): A counter to track the total number of ratelimit responses received.

        Returns:
            dict: A dictionary containing the result of the modification operation, including the modified role ID.

        Example Usage:
            # Modify a role in a guild.
            guild_id = 123456789012345678  # Replace with the actual guild ID
            role_id = 987654321098765432  # Replace with the actual role ID
            data_role = {
                "color": 0xFF0000  # Change role color to red
            }
            result = await discord_utility.modify_guild_role(session, guild_id, role_id, data_role)

            if result["success"]:
                print(f"Role {role_id} modified in guild {guild_id}")
            else:
                print(f"Failed to modify role: {result['message']}")

        Note:
            This method modifies a specific role in a guild and returns the modified role ID.
        """
        logging.debug(f'Started modifying role in guild ID: {guild_id}')
        while True:   
         async with session.patch(f"{self.url}/guilds/{guild_id}/roles/{role_id}", json=data_role) as response:
            if response.status in [201, 200, 204]:
                if not str(guild_id) in modified_roles:
                    modified_roles[str(guild_id)] = []
                modified_roles[str(guild_id)].append(role_id)
                break
            elif response.status == 429:
                total_ratelimits += 1
                if not self.skipOnRatelimit:
                    await asyncio.sleep(self.ratelimitCooldown)
                else:
                    break
            else:
                break
        return modified_roles
    
    async def get_guilds_roles(self, guild_ids: list):
        """
        Get roles in multiple guilds.

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
        """
        start_time = time.perf_counter()
        assert isinstance(guild_ids, list), "guild_ids has to be a list"
        guilds_roles = {}
        total_ratelimits = 0       
        async with aiohttp.ClientSession(headers={'Authorization': f'{self.token}'}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = [self.get_guild_roles(session, guild_id, guilds_roles, total_ratelimits) for guild_id in guild_ids]
            await asyncio.gather(*tasks)
        
        end_time = time.perf_counter() - start_time
        return {'success': bool(guilds_roles), 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "guilds_roles": guilds_roles}
    
    async def get_guild_roles(self, session, guild_id, guilds_roles={}, total_ratelimits=0):
        """
        Get roles in a specific guild.

        Args:
            session (aiohttp.ClientSession): An aiohttp session for making HTTP requests.
            guild_id (int): The ID of the guild in which roles should be retrieved.
            guilds_roles (dict, optional): A dictionary to store retrieved roles for each guild.
            total_ratelimits (int, optional): The total number of rate limits encountered.

        Returns:
            dict: A dictionary containing the guild's roles.

        Note:
            This method retrieves roles from a specific guild.
        """
        logging.debug(f'Started scraping roles in guild ID: {guild_id}')
        while True:   
            async with session.get(f"{self.url}/guilds/{guild_id}/roles") as response:
                if response.status in [201, 200, 204]:
                    guilds_roles[str(guild_id)] = await response.json()
                    break
                elif response.status == 429:
                    total_ratelimits += 1
                    if not self.skipOnRatelimit:
                        await asyncio.sleep(self.ratelimitCooldown)
                    else:
                        break
                else:
                    break
        return guilds_roles
    
    async def delete_guilds_roles(self, role_ids: dict):
        """
        Delete roles in multiple guilds.

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
        """
        start_time = time.perf_counter()
        assert isinstance(role_ids, dict), "Role IDs must be a dictionary"
        deleted_roles = {}
        total_ratelimits = 0       
        async with aiohttp.ClientSession(headers={'Authorization': f'{self.token}'}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = []
            for guild_id in role_ids:
                for role_id in role_ids[guild_id]:
                    tasks.append(self.delete_guild_role(session, guild_id, role_id, deleted_roles, total_ratelimits))
            await asyncio.gather(*tasks) 
        end_time = time.perf_counter() - start_time
        return {'success': bool(deleted_roles), 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "deleted_roles": deleted_roles}
    
    async def delete_guild_role(self, session, guild_id, role_id, deleted_roles={}, total_ratelimits=0):
        """
        Delete a role in a specific guild.

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
        """
        logging.debug(f'Started deleting role ID: {role_id}, in guild ID: {guild_id}')
        while True:   
            async with session.delete(f"{self.url}/guilds/{guild_id}/roles/{role_id}") as response:
                if response.status in [201, 200, 204]:
                    if not str(guild_id) in deleted_roles:
                        deleted_roles[str(guild_id)] = []
                    deleted_roles[str(guild_id)].append(role_id)
                    break
                elif response.status == 429:
                    total_ratelimits += 1
                    if not self.skipOnRatelimit:
                        await asyncio.sleep(self.ratelimitCooldown)
                    else:
                        break
                else:
                    break
        return deleted_roles
    
    async def mass_modify_guilds_users(self, user_ids: dict, data_modify: dict): # https://discord.com/developers/docs/resources/guild#modify-guild-member
        """
        Mass modify users in multiple guilds.

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
        """
        start_time = time.perf_counter()
        assert isinstance(user_ids, dict), "user_ids IDs must be a dictionary"
        modified_users = {}
        total_ratelimits = 0       
        async with aiohttp.ClientSession(headers={'Authorization': f'{self.token}'}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = []
            for guild_id in user_ids:
                for user_id in user_ids[guild_id]:
                    tasks.append(self.modify_guild_user(session, guild_id, user_id, data_modify, modified_users, total_ratelimits))
            await asyncio.gather(*tasks) 
        end_time = time.perf_counter() - start_time
        return {'success': bool(modified_users), 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "modified_users": modified_users}
    
    async def modify_guild_user(self, session, guild_id, user_id, data_modify, modified_users={}, total_ratelimits=0):
        """
        Modify a user in a specific guild.

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
        """
        logging.debug(f'Started modifying user ID: {user_id}, in guild ID: {guild_id}')
        while True:   
            async with session.patch(f"{self.url}/guilds/{guild_id}/members/{user_id}", json=data_modify) as response:
                if response.status in [201, 200, 204]:
                    if not str(guild_id) in modified_users:
                        modified_users[str(guild_id)] = []
                    modified_users[str(guild_id)].append(user_id)
                    break
                elif response.status == 429:
                    total_ratelimits += 1
                    if not self.skipOnRatelimit:
                        await asyncio.sleep(self.ratelimitCooldown)
                    else:
                        break
                else:
                    break
        return modified_users
    
    async def mass_modify_guilds(self, guild_ids: list, data_modify: dict): # https://discord.com/developers/docs/resources/guild#modify-guild
        """
        Mass modify properties of multiple guilds.

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
        """
        start_time = time.perf_counter()
        assert isinstance(guild_ids, list), "guild_ids IDs must be a list"
        modified_guilds = []
        total_ratelimits = 0       
        async with aiohttp.ClientSession(headers={'Authorization': f'{self.token}'}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = [self.modify_guild(session, guild_id, data_modify, modified_guilds, total_ratelimits) for guild_id in guild_ids]
            await asyncio.gather(*tasks) 
        end_time = time.perf_counter() - start_time
        return {'success': bool(modified_guilds), 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "modified_guilds": modified_guilds}
    
    async def modify_guild(self, session, guild_id, data_modify, modified_guilds={}, total_ratelimits=0):
        """
        Modify properties of a specific guild.

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
        """
        logging.debug(f'Started modifying guild ID: {guild_id}')
        while True:   
            async with session.patch(f"{self.url}/guilds/{guild_id}", json=data_modify) as response:
                if response.status in [201, 200, 204]:
                    modified_guilds.append(guild_id)
                    break
                elif response.status == 429:
                    total_ratelimits += 1
                    if not self.skipOnRatelimit:
                        await asyncio.sleep(self.ratelimitCooldown)
                    else:
                        break
                else:
                    break
        return modified_guilds

    async def mass_create_guilds_emojis(self, guild_ids: list, data_create: dict, amount: int =10): # https://discord.com/developers/docs/resources/emoji#create-guild-emoji
        """
        Mass create emojis in multiple guilds.

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
        """
        start_time = time.perf_counter()
        assert isinstance(guild_ids, list), "guild_ids IDs must be a list"
        created_emojis = {}
        total_ratelimits = 0       
        async with aiohttp.ClientSession(headers={'Authorization': f'{self.token}'}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = [self.create_guild_emoji(session, guild_id, data_create, created_emojis, total_ratelimits) for i in range(amount) for guild_id in guild_ids]
            await asyncio.gather(*tasks) 
        end_time = time.perf_counter() - start_time
        return {'success': bool(created_emojis), 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "created_emojis": created_emojis}
    
    async def create_guild_emoji(self, session, guild_id, data_create, created_emojis={}, total_ratelimits=0):
        """
        Create a custom emoji in a guild.

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

        Note:
            This method creates a custom emoji in a guild and returns the created emoji data.
        """
        logging.debug(f'Started creating emoji in guild ID: {guild_id}')
        while True:   
            async with session.post(f"{self.url}/guilds/{guild_id}/emojis", json=data_create) as response:
                if response.status in [201, 200, 204]:
                    if not str(guild_id) in created_emojis:
                        created_emojis[str(guild_id)] = []
                    created_emojis[str(guild_id)].append(await response.json())
                    break
                elif response.status == 429:
                    total_ratelimits += 1
                    if not self.skipOnRatelimit:
                        await asyncio.sleep(self.ratelimitCooldown)
                    else:
                        break
                else:
                    break
        return created_emojis
    
    async def mass_modify_guilds_emojis(self, emoji_ids: dict, data_modify: dict): # https://discord.com/developers/docs/resources/emoji#modify-guild-emoji
        """
        Mass modify emojis in multiple guilds.

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
        """
        start_time = time.perf_counter()
        assert isinstance(emoji_ids, dict), "emoji_ids IDs must be a list"
        modified_emojis = {}
        total_ratelimits = 0       
        async with aiohttp.ClientSession(headers={'Authorization': f'{self.token}'}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = []
            for guild_id in emoji_ids:
                for emoji_id in emoji_ids[guild_id]:
                    tasks.append(self.modify_guild_emoji(session, guild_id, emoji_id, data_modify, modified_emojis, total_ratelimits))
            await asyncio.gather(*tasks) 
        end_time = time.perf_counter() - start_time
        return {'success': bool(modified_emojis), 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "created_emojis": modified_emojis}
    
    async def modify_guild_emoji(self, session, guild_id, emoji_id, data_modify, modified_emojis={}, total_ratelimits=0):
        """
        Modify a guild emoji.

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
        """
        logging.debug(f'Started modifying emoji ID: {emoji_id}, in guild ID: {guild_id}')
        while True:   
            async with session.patch(f"{self.url}/guilds/{guild_id}/emojis/{emoji_id}", json=data_modify) as response:
                if response.status in [201, 200, 204]:
                    if not str(modified_emojis) in modified_emojis:
                        modified_emojis[str(guild_id)] = []
                    modified_emojis[str(guild_id)].append(await response.json())
                    break
                elif response.status == 429:
                    total_ratelimits += 1
                    if not self.skipOnRatelimit:
                        await asyncio.sleep(self.ratelimitCooldown)
                    else:
                        break
                else:
                    break
        return modified_emojis

    async def mass_delete_guilds_emojis(self, emoji_ids: dict):
        """
        Mass delete emojis from multiple guilds.

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
        """
        start_time = time.perf_counter()
        assert isinstance(emoji_ids, dict), "emoji_ids IDs must be a list"
        deleted_emojis = {}
        total_ratelimits = 0       
        async with aiohttp.ClientSession(headers={'Authorization': f'{self.token}'}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = []
            for guild_id in emoji_ids:
                for emoji_id in emoji_ids[guild_id]:
                    tasks.append(self.delete_guild_emoji(session, guild_id, emoji_id, deleted_emojis, total_ratelimits))
            await asyncio.gather(*tasks) 
        end_time = time.perf_counter() - start_time
        return {'success': bool(deleted_emojis), 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "deleted_emojis": deleted_emojis}
    
    async def delete_guild_emoji(self, session, guild_id, emoji_id, deleted_emojis={}, total_ratelimits=0):
        """
    Delete a guild emoji.

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
        """
        logging.debug(f'Started deleting emoji ID: {emoji_id}, in guild ID: {guild_id}')
        while True:   
            async with session.delete(f"{self.url}/guilds/{guild_id}/emojis/{emoji_id}") as response:
                if response.status in [201, 200, 204]:
                    if not str(deleted_emojis) in deleted_emojis:
                        deleted_emojis[str(guild_id)] = []
                    deleted_emojis[str(guild_id)].append(emoji_id)
                    break
                elif response.status == 429:
                    total_ratelimits += 1
                    if not self.skipOnRatelimit:
                        await asyncio.sleep(self.ratelimitCooldown)
                    else:
                        break
                else:
                    break
        return deleted_emojis

    async def mass_add_guilds_members_roles(self, user_ids: dict):
        """
        Mass-add roles to members in multiple guilds.

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
        """
        start_time = time.perf_counter()
        assert isinstance(user_ids, dict), "user_ids IDs must be a list"
        added_member_roles = {}
        total_ratelimits = 0       
        async with aiohttp.ClientSession(headers={'Authorization': f'{self.token}'}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = []
            for guild_id in user_ids:
                for user_id in user_ids[guild_id]["user_ids"]:
                    for role_id in user_ids[guild_id]["role_ids"]:
                        tasks.append(self.add_guild_member_role(session, guild_id, user_id, role_id, added_member_roles, total_ratelimits))
            await asyncio.gather(*tasks) 
        end_time = time.perf_counter() - start_time
        return {'success': bool(added_member_roles), 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "added_member_roles": added_member_roles}
    
    async def add_guild_member_role(self, session, guild_id, user_id, role_id, added_member_roles={}, total_ratelimits=0):
        """
        Add a role to a member in a guild.

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
            # Add a role to a member in a guild.
            guild_id = 123456789012345678  # Replace with the desired guild ID.
            user_id = 987654321098765432  # Replace with the user's ID.
            role_id = 123456789  # Replace with the role ID to be added.
            result = await discord_utility.add_guild_member_role(session, guild_id, user_id, role_id)

            if result["success"]:
                print(f"Role with ID {role_id} added to user with ID {user_id} in guild with ID {guild_id}")
            else:
                print(f"Failed to add role to user: {result['message']}")

        Note:
            This method adds a specified role to a member in a guild and returns the added member roles.
        """
        logging.debug(f'Started adding role ID: {role_id}, to user ID: {user_id}, in guild ID: {guild_id}')
        while True:   
            async with session.patch(f"{self.url}/guilds/{guild_id}/members/{user_id}/roles/{role_id}") as response:
                if response.status in [201, 200, 204]:
                    if not str(added_member_roles) in added_member_roles:
                        added_member_roles[str(guild_id)][str(role_id)] = []
                    added_member_roles[str(guild_id)][str(role_id)].append(user_id)
                    break
                elif response.status == 429:
                    total_ratelimits += 1
                    if not self.skipOnRatelimit:
                        await asyncio.sleep(self.ratelimitCooldown)
                    else:
                        break
                else:
                    break
        return added_member_roles

    async def mass_remove_guilds_members_roles(self, user_ids: dict):
        """
    Mass-remove roles from members in multiple guilds.

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
        """
        start_time = time.perf_counter()
        assert isinstance(user_ids, dict), "user_ids IDs must be a list"
        removed_member_roles = {}
        total_ratelimits = 0       
        async with aiohttp.ClientSession(headers={'Authorization': f'{self.token}'}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = []
            for guild_id in user_ids:
                for user_id in user_ids[guild_id]["user_ids"]:
                    for role_id in user_ids[guild_id]["role_ids"]:
                        tasks.append(self.remove_guild_member_role(session, guild_id, user_id, role_id, removed_member_roles, total_ratelimits))
            await asyncio.gather(*tasks) 
        end_time = time.perf_counter() - start_time
        return {'success': bool(removed_member_roles), 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "added_member_roles": removed_member_roles}
    
    async def remove_guild_member_role(self, session, guild_id, user_id, role_id, removed_member_roles={}, total_ratelimits=0):
        """
    Mass-remove roles from members in multiple guilds.

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
        """
        logging.debug(f'Started removing role ID: {role_id}, to user ID: {user_id}, in guild ID: {guild_id}')
        while True:   
            async with session.delete(f"{self.url}/guilds/{guild_id}/members/{user_id}/roles/{role_id}") as response:
                if response.status in [201, 200, 204]:
                    if not str(removed_member_roles) in removed_member_roles:
                        removed_member_roles[str(guild_id)][str(role_id)] = []
                    removed_member_roles[str(guild_id)][str(role_id)].append(user_id)
                    break
                elif response.status == 429:
                    total_ratelimits += 1
                    if not self.skipOnRatelimit:
                        await asyncio.sleep(self.ratelimitCooldown)
                    else:
                        break
                else:
                    break
        return removed_member_roles
    
