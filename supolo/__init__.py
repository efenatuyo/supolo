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

    async def get_guilds_channels(self, guild_ids):
        start_time = time.perf_counter()
        assert isinstance(guild_ids, list), "Guild IDs should be a list"
        shared_channels = {}
        total_ratelimits = 0
        async with aiohttp.ClientSession(headers = {'Authorization': self.token}, connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = [self.get_guild_channels(session, guild_id, shared_channels, total_ratelimits) for guild_id in guild_ids]
            await asyncio.gather(*tasks)
        end_time = time.perf_counter() - start_time
        return {'success': True, 'time_taken': end_time, 'total_ratelimits': total_ratelimits, "channels": shared_channels}
        
    async def get_guild_channels(self, session, guild_id, shared_channels=None, total_ratelimits=None):
        logging.debug(f'Started fetching users in guild: {guild_id}')
        if shared_channels is None:
            shared_channels = {}
        if not total_ratelimits:
            total_ratelimits = 0
        
        while True:   
         async with session.get(f"{self.url}/guilds/{guild_id}/channels") as response:
            if response.status == 200:
                data = await response.json()
                shared_channels[guild_id] = data
                break
            elif response.status == 429:
                total_ratelimits += 1
                if not self.skipOnRatelimit:
                    await asyncio.sleep(self.ratelimitCooldown)
                else:
                    break

        return shared_channels
                     
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

    async def get_guild_members(self, session=None, url=None, shared_users=None, guild_id=None, total_ratelimits=0, method=None):
        assert guild_id, "Required guild_id value"
        assert method, "Reqired method value, Types: ['get_shared_user_ids', 'get_guild_members']"
        assert session, "Aiohttp session is requried for this function"
        assert session.headers.get('Authorization'), "Authorization is required in headers"
        logging.debug(f'Started fetching users in guild: {guild_id}')
        if url is None:
            url = f'{self.url}/guilds/{guild_id}/members?limit=1000'
        if shared_users is None:
            shared_users = {}
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
    
    async def mass_ban(self, guild_ids, timeout=5):
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
