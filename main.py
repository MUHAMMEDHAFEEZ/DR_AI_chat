from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

llm = OllamaLLM(model="llama3")

result = llm.invoke("Hello, world!")


print(result)


