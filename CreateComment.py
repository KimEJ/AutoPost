# from bardapi import BardCookies
import asyncio
import jwt
import logging
import aiohttp
import json

    
async def on_request_start(session, context, params):
    logging.getLogger('aiohttp.client').debug(f'Starting request <{params}>')

class CreateComment:
    def __init__(self, token, id):
        self.loop = asyncio.get_event_loop()
        logging.basicConfig(level=logging.DEBUG)
        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(on_request_start)

        self.session = aiohttp.ClientSession(headers={"X-Wrtn-Id": id}, trace_configs=[trace_config])
        self.loop.run_until_complete(self._refresh_token(token))
        self.room = None

    async def _refresh_token(self, token):
        async with self.session.post('https://api.wow.wrtn.ai/auth/refresh', headers={"Refresh": token}) as request:
            response = await request.json()
            if response['result'] != "SUCCESS":
                raise Exception("Failed to refresh token")
            decoded = jwt.decode(response['data']['accessToken'], options={"verify_signature": False})
            print (decoded["email"])

            self.user=decoded["email"]
            self.session.headers.update({"Authorization": "Bearer "+response['data']['accessToken']})
            return response['data']['accessToken']
        
    async def create_chat(self):
        if(self.room):
            await self.delete_chat(self.room)
            self.room = None

        async with self.session.post(f'https://api.wow.wrtn.ai/chat') as request:
            response = await request.json()
            print(response)
            result = response['result']
            if result != "SUCCESS":
                raise Exception("Failed to create chat session")

            self.room = response['data']['_id']

            return self.room
    
    async def delete_chat(self, room):
        room = room or self.room
        async with self.session.delete(f'https://api.wow.wrtn.ai/chat/{room}') as request:
            response = await request.json()
            print(response)
            return response
        
    async def summary(self, target, text):
        text = text[:1500]
        print("=====================================")
        print(target, text)
        print("\r\n")
        async with self.session.post(url=f'https://studio-api.wow.wrtn.ai/store/tool/65368fcbde87e16e676544df/generate', 
                                     params={'model':'gpt-4', 'platform': 'web', 'user':self.user}, 
                                     json={"inputs": [{"name": "이름", "value": target }, {"name": "본문", "value": text }],"model": "gpt-4"}, 
                                     headers={'Host': 'studio-api.wow.wrtn.ai', }) as request:
            print('run')
            response = await request.read()
            # data: {"chunk":null}\n\ndata: {"chunk":""}\n\ndata: {"chunk":"I"}\n\ndata: {"chunk":"\'m"}\n\ndata: {"chunk":" sorry"}\n\ndata: {"chunk":","}\n\ndata: {"chunk":" but"}\n\ndata: {"chunk":" I"}\n\ndata: {"chunk":" cannot"}\n\ndata: {"chunk":" generate"}\n\ndata: {"chunk":" a"}\n\ndata: {"chunk":" response"}\n\ndata: {"chunk":" without"}\n\ndata: {"chunk":" a"}\n\ndata: {"chunk":" specific"}\n\ndata: {"chunk":" context"}\n\ndata: {"chunk":" or"}\n\ndata: {"chunk":" user"}\n\ndata: {"chunk":" input"}\n\ndata: {"chunk":"."}\n\ndata: {"chunk":" Please"}\n\ndata: {"chunk":" provide"}\n\ndata: {"chunk":" more"}\n\ndata: {"chunk":" information"}\n\ndata: {"chunk":" or"}\n\ndata: {"chunk":" a"}\n\ndata: {"chunk":" specific"}\n\ndata: {"chunk":" question"}\n\ndata: {"chunk":" for"}\n\ndata: {"chunk":" me"}\n\ndata: {"chunk":" to"}\n\ndata: {"chunk":" answer"}\n\ndata: {"chunk":"."}\n\ndata: {"chunk":""}\n\ndata: {"chunk":null}\n\ndata: {"content":"I\'m sorry, but I cannot generate a response without a specific context or user input. Please provide more information or a specific question for me to answer."}\n\ndata: {"end":"[DONE]"}\n\n
            response = response.decode('utf-8').split('\n')
            matching = [s for s in response if '"content"' in s]
            response = json.loads(matching[0].replace('data: ', ''))

            print(response['content'])
            print("=====================================")
            return response['content']
        
    async def post(self, id, target, tags, text):
        text = text[:1500]
        print("=====================================")
        print(text)
        print("\r\n")
        async with self.session.post(url=f'https://studio-api.wow.wrtn.ai/store/tool/6536602361e52940aa405a14/generate', 
                                     params={'model':'openai-gpt-3.5-turbo-16k', 'platform': 'web', 'user':self.user}, 
                                     json={"inputs": [{"name": "아이디", "value": id }, {"name": "가게 이름", "value": target }, {"name": "키워드", "value": tags }, {"name": "요약", "value": text }],"model": "openai-gpt-3.5-turbo-16k"}, 
                                     headers={'Host': 'studio-api.wow.wrtn.ai', }) as request:
            print('run')
            response = await request.read()
            # data: {"chunk":null}\n\ndata: {"chunk":""}\n\ndata: {"chunk":"I"}\n\ndata: {"chunk":"\'m"}\n\ndata: {"chunk":" sorry"}\n\ndata: {"chunk":","}\n\ndata: {"chunk":" but"}\n\ndata: {"chunk":" I"}\n\ndata: {"chunk":" cannot"}\n\ndata: {"chunk":" generate"}\n\ndata: {"chunk":" a"}\n\ndata: {"chunk":" response"}\n\ndata: {"chunk":" without"}\n\ndata: {"chunk":" a"}\n\ndata: {"chunk":" specific"}\n\ndata: {"chunk":" context"}\n\ndata: {"chunk":" or"}\n\ndata: {"chunk":" user"}\n\ndata: {"chunk":" input"}\n\ndata: {"chunk":"."}\n\ndata: {"chunk":" Please"}\n\ndata: {"chunk":" provide"}\n\ndata: {"chunk":" more"}\n\ndata: {"chunk":" information"}\n\ndata: {"chunk":" or"}\n\ndata: {"chunk":" a"}\n\ndata: {"chunk":" specific"}\n\ndata: {"chunk":" question"}\n\ndata: {"chunk":" for"}\n\ndata: {"chunk":" me"}\n\ndata: {"chunk":" to"}\n\ndata: {"chunk":" answer"}\n\ndata: {"chunk":"."}\n\ndata: {"chunk":""}\n\ndata: {"chunk":null}\n\ndata: {"content":"I\'m sorry, but I cannot generate a response without a specific context or user input. Please provide more information or a specific question for me to answer."}\n\ndata: {"end":"[DONE]"}\n\n
            response = response.decode('utf-8').split('\n')
            matching = [s for s in response if '"content"' in s]
            response = json.loads(matching[0].replace('data: ', ''))

            print(response['content'])
            print("=====================================")
            return response['content']