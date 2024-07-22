import requests
import bs4
from bs4 import BeautifulSoup
from fastapi import FastAPI
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_aws import ChatBedrock
from langserve import add_routes
from mangum import Mangum
from langchain_aws import ChatBedrock, BedrockEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from pydantic import BaseModel
from langchain_core.runnables import RunnablePassthrough

url_list = [
    "https://applion.jp/android/rank/us/6014/",
    # "https://applion.jp/android/rank/us/6014/?start=20",
    # "https://applion.jp/android/rank/us/6014/?start=40",
    # "https://applion.jp/android/rank/us/6014/?start=60",
    # "https://applion.jp/android/rank/us/6014/?start=80",
    ]

# 抽出したリンクを格納するリスト
extracted_links = []

# User-Agentヘッダーを追加
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

for url in url_list:
    # URLの内容を取得
    response = requests.get(url, headers=headers)
    
    # BeautifulSoupオブジェクトを作成
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 'rownormal'クラスを持つ要素を検索
    elements = soup.find_all(class_='rownormal')

    # 各要素内のリンクを抽出
    for element in elements:
        links = element.find_all('a', href=True)
        for link in links:
            # リンクが相対パスの場合は絶対パスに変換
            if link['href'].startswith('/'):
                extracted_links.append('https://applion.jp' + link['href'])
            else:
                extracted_links.append(link['href'])

docs = []

# 抽出したリンクを表示
for link in extracted_links:
    print(link)
    loader = WebBaseLoader(
        link,
        bs_kwargs=dict(
            parse_only=bs4.SoupStrainer('div', class_='h1_title'),
        ),
    )
    docs.extend(loader.load())
    print(docs)

text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)
index = FAISS.from_documents(documents, BedrockEmbeddings())

prompt = hub.pull("rlm/rag-prompt")

# 2. Create model
model = ChatBedrock(
    region_name='us-east-1',
    model_id='anthropic.claude-3-haiku-20240307-v1:0',
)

def format_docs(docs):
    # docsのpage_contentと、metadataのsourceを返す
    return [doc.page_content for doc in docs], [doc.metadata['source'] for doc in docs]

# 3. Create chain
rag_chain = (
    {"context": index.as_retriever() | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

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
    rag_chain,
    path='/chat',
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)

