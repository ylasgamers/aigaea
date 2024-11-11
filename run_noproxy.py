#https://github.com/ylasgamers || @ylasgamers
import aiohttp
import asyncio
import random
import json
import uuid
from loguru import logger
import requests
import time
from aiohttp import ClientSession, ClientTimeout
from fake_useragent import UserAgent

def get_uid(token):
    url = "https://api.aigaea.net/api/auth/session"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "http://app.aigaea.net",
        "Origin": "http://app.aigaea.net/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }
    
    response = requests.post(url, headers=headers)
    result = response.json()
    uid = result.get('data', {}).get('uid')
    return uid

async def connect_to_http(uid, token, delays, browserid):
    user_agent = UserAgent(os=['windows', 'macos', 'linux'], browsers='chrome')
    random_user_agent = user_agent.random
    rdm = str(uuid.uuid4())[8:]
    device_id = f"{browserid}{rdm}"
    logger.info(f"Device ID: {device_id}")
    
    async with aiohttp.ClientSession(
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": random_user_agent, "Connection": "keep-alive"},
        timeout=ClientTimeout(total=None, connect=10)
    ) as session:
        
        while True:
            try:
                await asyncio.sleep(random.randint(1, 10) / 10)
                uri = "https://api.aigaea.net/api/network/ping"
                logger.info(f"Connecting to {uri}...")

                # Data to send in the POST request
                data = {
                    "uid": uid,
                    "browser_id": device_id,
                    "timestamp": int(time.time()),
                    "version": "1.0.0",
                }

                async with session.post(uri, json=data) as response:
                    if response.status == 200:
                        # Parse the response if needed
                        response_data = await response.json()
                        logger.info(f"Received response: {response_data}")
                    else:
                        logger.error(f"Request failed with status {response.status}")
                
                # Simulate the periodic pinging
                print(f"Wait For {delays} Second To Pinging Again...")
                await asyncio.sleep(delays)  # Adjust this as needed to simulate "keep-alive"

            except Exception as e:
                logger.error(f"Error: {str(e)}")
                await asyncio.sleep(1)  # Sleep before retrying the connection

# For testing the function
async def main():
    delays = int(input('Input Delay Second Per Looping : '))
    tokenid = input('Input Token AIGAEA : ')
    browserid = str(input('Input First 8 Character BrowserId : '))
    await connect_to_http(get_uid(tokenid), tokenid, delays, browserid)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
