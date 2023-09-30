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
                return {'success': True, 'time_taken': end_time, 'total_ratelimits': total_ratelimits + guilds_data["total_ratelimits"], "users": shared_users}

    async def get_guilds_channels(self, guild_ids: list):
        start_time = time.perf_counter()
        assert isinstance(guild_ids, list), "Guild IDs should be a list"
        shared_channels = {}
        total_ratelimits = 0
        async with aiohttp.ClientSession(headers = {'Authorization': self.token}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = [self.get_guild_channels(session, guild_id, shared_channels, total_ratelimits) for guild_id in guild_ids]
            await asyncio.gather(*tasks)
        end_time = time.perf_counter() - start_time
        return {'success': True, 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "channels": shared_channels}
        
    async def get_guild_channels(self, session, guild_id, shared_channels={}, total_ratelimits=0):
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

        return shared_channels

    async def delete_guild_channel(self, session, channel_id, deleted_channels=[], total_ratelimits=0):
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
        start_time = time.perf_counter()
        assert isinstance(channel_ids, list), "channel_ids IDs should be a list"
        total_ratelimits = 0
        deleted_channels = []
        async with aiohttp.ClientSession(headers = {'Authorization': self.token}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = [self.delete_guild_channel(session, channel_id, deleted_channels, total_ratelimits) for channel_id in channel_ids]
            await asyncio.gather(*tasks)
        end_time = time.perf_counter() - start_time
        return {'success': True, 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "deleted_channels": deleted_channels}    
            
    async def get_guilds_members(self, guild_ids: list):
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
            
            return {"success": True, 'time_taken': time.perf_counter() - start_time, "total_ratelimits": total_ratelimits, 'users': shared_users}

    async def get_guild_members(self, session=None, url=None, shared_users={}, guild_id=None, total_ratelimits=0, method=None):
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
        return {"success": True, 'time_taken': time.perf_counter() - start_time, "total_ratelimits": total_ratelimit[0], 'unbanned_users': unbanned_users}
        
        
    async def single_unban(self, session, url, user_id, unbanned_users, total_ratelimit, timeout, guild_id):
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
            return {"success": True, 'time_taken': time.perf_counter() - start_time, "total_ratelimits": total_ratelimit[0], 'kicked_users': kicked_users}


    async def single_kick(self, session, url, user_id, kicked_users, total_ratelimit, timeout, guild_id):
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
            
            return {"success": True, 'time_taken': time.perf_counter() - start_time, "total_ratelimits": total_ratelimits, 'banned_users': banned_users}
        
    async def get_guild_banned_users(self, guild_id, banned_users={}, total_ratelimits=0):
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
        return {"success": True, 'time_taken': time.perf_counter() - start_time, 'total_ratelimits': total_ratelimits, "users": banned_users[str(guild_id)]}
    
    async def mass_ban(self, guild_ids: list, timeout: int =5):
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
            return {'success': True, 'time_taken': time.perf_counter() - start_time, 'total_ratelimits': total_ratelimit[0], "banned_users": banned_users}

    async def single_ban(self, session, url, user_id, banned_users, total_ratelimit, timeout, guild_id):
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
        return {'success': True, 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "created_channels": created_channels} 
    
    async def spam_guilds_channels(self, channel_ids: list, amount: int =10, data_message: dict ={"content": "@everyone"}, data_webhook: dict ={"name": ":)"}, method: str ="bot"):
        """
        method = ["bot", "webhook"]
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
        return {'success': True, 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "spammed_channels": spammed_channels}

    async def spam_guild_channel(self, session, channel_id, amount, data_message, method="bot", data_webhook={}, spammed_channels=[], total_ratelimits=0):
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
                break
        return spammed_channels
    
    async def create_channel_webhook(self, session, channel_id, data_webhook):
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
        return {'success': True, 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "created_roles": created_roles}
    
    async def create_guild_role(self, session, guild_id, data_role, created_roles={}, total_ratelimits=0):
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
    
    async def get_guilds_roles(self, guild_ids: list):
        start_time = time.perf_counter()
        assert isinstance(guild_ids, list), "guild_ids has to be a list"
        guilds_roles = {}
        total_ratelimits = 0       
        async with aiohttp.ClientSession(headers={'Authorization': f'{self.token}'}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = [self.get_guild_roles(session, guild_id, guilds_roles, total_ratelimits) for guild_id in guild_ids]
            await asyncio.gather(*tasks)
        
        end_time = time.perf_counter() - start_time
        return {'success': True, 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "guilds_roles": guilds_roles}
    
    async def get_guild_roles(self, session, guild_id, guilds_roles={}, total_ratelimits=0):
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
        return {'success': True, 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "deleted_roles": deleted_roles}
    
    async def delete_guild_role(self, session, guild_id, role_id, deleted_roles={}, total_ratelimits=0):
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
        return {'success': True, 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "modified_users": modified_users}
    
    async def modify_guild_user(self, session, guild_id, user_id, data_modify, modified_users={}, total_ratelimits=0):
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
        start_time = time.perf_counter()
        assert isinstance(guild_ids, list), "guild_ids IDs must be a list"
        modified_guilds = []
        total_ratelimits = 0       
        async with aiohttp.ClientSession(headers={'Authorization': f'{self.token}'}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = [self.modify_guild(session, guild_id, data_modify, modified_guilds, total_ratelimits) for guild_id in guild_ids]
            await asyncio.gather(*tasks) 
        end_time = time.perf_counter() - start_time
        return {'success': True, 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "modified_guilds": modified_guilds}
    
    async def modify_guild(self, session, guild_id, data_modify, modified_guilds={}, total_ratelimits=0):
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
        start_time = time.perf_counter()
        assert isinstance(guild_ids, list), "guild_ids IDs must be a list"
        created_emojis = {}
        total_ratelimits = 0       
        async with aiohttp.ClientSession(headers={'Authorization': f'{self.token}'}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = [self.create_guild_emoji(session, guild_id, data_create, created_emojis, total_ratelimits) for i in range(amount) for guild_id in guild_ids]
            await asyncio.gather(*tasks) 
        end_time = time.perf_counter() - start_time
        return {'success': True, 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "created_emojis": created_emojis}
    
    async def create_guild_emoji(self, session, guild_id, data_create, created_emojis={}, total_ratelimits=0):
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
        return {'success': True, 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "created_emojis": modified_emojis}
    
    async def modify_guild_emoji(self, session, guild_id, emoji_id, data_modify, modified_emojis={}, total_ratelimits=0):
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
        return {'success': True, 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "deleted_emojis": deleted_emojis}
    
    async def delete_guild_emoji(self, session, guild_id, emoji_id, deleted_emojis={}, total_ratelimits=0):
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
        return {'success': True, 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "added_member_roles": added_member_roles}
    
    async def add_guild_member_role(self, session, guild_id, user_id, role_id, added_member_roles={}, total_ratelimits=0):
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
        return {'success': True, 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "added_member_roles": removed_member_roles}
    
    async def remove_guild_member_role(self, session, guild_id, user_id, role_id, removed_member_roles={}, total_ratelimits=0):
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
