import asyncio

import aiohttp
from dotenv import dotenv_values

import yolink.exception
from AuthManager import AuthManager
from MsgListener import MsgListener
from yolink.home_manager import YoLinkHome


async def main():
    # Establish an asynchronous HTTP session

    async with aiohttp.ClientSession() as session:
        env = dotenv_values('../.env')
        auth_manager = AuthManager(session, id=env.get('UAID'), key=env.get('SECKEY'))
        auth_manager.set_region(US=True)  # Change URLs to the proper region
        await auth_manager.check_and_refresh_token()  # Ensure token is valid

        msg_listener = MsgListener()

        # auth_header = auth_manager.http_auth_header()
        # print(auth_header)  # Print the authentication header

        # Create a YoLink-Home Manager
        ylm = YoLinkHome()
        # Create required objects for home manager setup
        attempt_connection = True
        while attempt_connection:
            try:
                await ylm.async_setup(auth_mgr=auth_manager, listener=msg_listener)
            except yolink.exception.YoLinkClientError as e:
                if e.code != '010301':
                    raise e
                else:
                    print('Attempting to reconnect...')
                    await asyncio.sleep(10)
            else:
                attempt_connection = False

        result = await ylm.async_get_home_info()

        x = 10
        pass


if __name__ == "__main__":
    # Running the main function within an event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
