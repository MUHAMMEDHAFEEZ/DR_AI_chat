from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ChatMessageSerializer
from .models import ChatMessage
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Create your views here.

class ChatView(APIView):
    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            # Initialize the Llama model
            llm = OllamaLLM(model="llama3")
            
            # Get user input from the request
            user_input = serializer.validated_data['user_input']
            
            try:
                # Get response from the model
                ai_response = llm.invoke(user_input)
                
                # Save both the input and response
                chat_message = serializer.save(ai_response=ai_response)
                
                return Response(ChatMessageSerializer(chat_message).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        messages = ChatMessage.objects.all().order_by('-created_at')
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
