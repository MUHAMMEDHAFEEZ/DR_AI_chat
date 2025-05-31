import json
from channels.generic.websocket import AsyncWebsocketConsumer
from langchain_ollama import OllamaLLM
import asyncio

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        # Initialize the Llama model
        llm = OllamaLLM(model="medllama2")
        
        try:
            # Get response from the model
            response = llm.invoke(message)
            
            # Split response into words and send them one by one
            words = response.split()
            for word in words:
                await self.send(text_data=json.dumps({
                    'message': word + ' ',
                    'type': 'word'
                }))
                await asyncio.sleep(0.1)  # Small delay between words
            
            # Send completion message
            await self.send(text_data=json.dumps({
                'message': '',
                'type': 'complete'
            }))
            
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e),
                'type': 'error'
            }))