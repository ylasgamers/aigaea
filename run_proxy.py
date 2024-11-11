#https://github.com/ylasgamers || @ylasgamers
import aiohttp
import asyncio
import json
import uuid
import time
from loguru import logger
import requests
from aiohttp import ClientSession, ClientTimeout
from fake_useragent import UserAgent
import itertools
import sys

# Function to read proxies from the local file
def load_proxies(file_path='local_proxies.txt'):
    with open(file_path, 'r') as f:
        proxies = [line.strip() for line in f.readlines()]
    return proxies  # Return all proxies if there are 100 or more

# Function to get the UID using the provided token
def get_uid(token):
    url = "https://api.aigaea.net/api/auth/session"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "http://app.aigaea.net",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }
    
    response = requests.post(url, headers=headers)
    result = response.json()
    uid = result.get('data', {}).get('uid')
    return uid

# Function to connect to the API using a proxy from the list
async def connect_to_http(uid, token, proxy, device_id):
    user_agent = UserAgent(os=['windows', 'macos', 'linux'], browsers='chrome')
    random_user_agent = user_agent.random
    logger.info(f"Using proxy: {proxy}")

    async with aiohttp.ClientSession(
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": random_user_agent, "Connection": "keep-alive"},
        timeout=ClientTimeout(total=None, connect=10),
    ) as session:
        try:
            uri = "https://api.aigaea.net/api/network/ping"
            logger.info(f"Browser Id : {device_id}")
            logger.info(f"Connecting to {uri} using proxy: {proxy}...")

            # Data to send in the POST request
            data = {
                "uid": uid,
                "browser_id": device_id,
                "timestamp": int(time.time()),
                "version": "1.0.0",
            }

            # Use the current proxy for the request
            async with session.post(uri, json=data, proxy=f"{proxy}") as response:
                if response.status == 200:
                    # Parse the response if needed
                    response_data = await response.json()
                    logger.info(f"Received response: {response_data}")
                else:
                    logger.error(f"Request failed with status {response.status}")
        except Exception as e:
            logger.error(f"Error using proxy {proxy}: {str(e)}")

# Function to run all proxies concurrently
async def run_all_proxies(uid, token, proxies):
    tasks = []
    rdm = str(uuid.uuid4())[8:]
    device_id = f"17c9bbe4{rdm}"
    
    # Create a task for each proxy
    for proxy in proxies:
        task = asyncio.create_task(connect_to_http(uid, token, proxy, device_id))
        tasks.append(task)
    
    # Run all tasks concurrently
    await asyncio.gather(*tasks)

# Function to loop through proxies continuously
async def loop_proxies(uid, token, proxies, delays, loop_count=None):
    count = 0
    while True:
        logger.info(f"Starting loop {count + 1}...")
        await run_all_proxies(uid, token, proxies)
        
        # Optional: add a delay between each cycle
        print(f"Cycle {count + 1} completed. Waiting before next cycle in {delays} seconds...")
        await asyncio.sleep(delays)  # Delay between cycles (in seconds)
        
        # Increment loop counter and check if we should stop after certain iterations
        count += 1
        if loop_count and count >= loop_count:
            logger.info(f"Completed {loop_count} loops. Exiting.")
            break

# For testing the function
async def main():
    delays = int(input('Input Delay Second Per Looping : '))
    tokenid = input('Input Token AIGAEA : ')
    proxies = load_proxies()  # Load proxies from the local file
    loop_count = None  # Set a specific number of loops, or None for infinite looping
    await loop_proxies(get_uid(tokenid), tokenid, proxies, delays, loop_count)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
