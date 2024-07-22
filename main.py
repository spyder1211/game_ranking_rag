from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_aws import ChatBedrock
from langserve import add_routes
from mangum import Mangum

# 1. Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ('system',"Hello, I'm a chatbot. What's your name? conversation in japanese"),
    ('user',"My name is {name}"),
])

# 2. Create model
model = ChatBedrock(
    region_name='us-east-1',
    model_id='anthropic.claude-3-haiku-20240307-v1:0',
)

# 3. Create chain
chain = prompt | model | StrOutputParser()

# 4. Create FastAPI app
app = FastAPI(
    title="LangChain",
    description="A simple language model API",
    version="1.0.0",
)

# 5. Create Mangum handler
handler = Mangum(app)

# 6. Add routes
add_routes(
    app, 
    chain,
    path='/chat',
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)

