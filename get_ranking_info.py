import requests
from bs4 import BeautifulSoup
from langchain_aws import ChatBedrock
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

url_list = [
    "https://applion.jp/android/rank/us/6014/",
    "https://applion.jp/android/rank/us/6014/?start=20",
    # "https://applion.jp/android/rank/us/6014/?start=40",
    # "https://applion.jp/android/rank/us/6014/?start=60",
    # "https://applion.jp/android/rank/us/6014/?start=80",
]

# 抽出したリンクを格納するリスト
my_dict = {
    'link': [],
    'summary': [],
}

# User-Agentヘッダーを追加
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

for url in url_list:
    # URLの内容を取得
    response = requests.get(url, headers=headers)
    
    # BeautifulSoupオブジェクトを作成
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 'rownormal'クラスの中のliタグを検索
    elements = soup.find_all(class_='rownormal')

    # 各要素内のリンクを抽出
    for element in elements:
        datas = element.find_all('li')
        for data in datas:
            # data.text内の改行を削除
            str = data.text.replace('\n', '')
            my_dict['summary'].append(str)
            link = data.find('a', href=True)
            if link:
                # リンクが相対パスの場合は絶対パスに変換
                if link['href'].startswith('/'):
                    my_dict['link'].append('https://applion.jp' + link['href'])
                else:
                    my_dict['link'].append(link['href'])

# プロンプトを作成
prompt = """
You will be given a context containing information about various articles. Your task is to analyze this context and output data for 20 articles in a specific format and in Japanese. Here is the context:

<context>

{{CONTEXT}}

</context>

Parse the given context to extract information about articles. For each article, you need to provide the following information in the specified order:

1. Link to the detailed page

2. Title

3. Summary

4. Publisher

5. Category

Format your output for each article as follows:

<article>

<link>[Link to the detailed page]</link>

<title>[Title of the article]</title>

<summary>[Summary of the article]</summary>

<publisher>[Publisher of the article]</publisher>

<category>[Category of the article]</category>

</article>

Important notes:

- Provide information for exactly 20 articles.

- Ensure that the links and summaries correspond to each other in the order they appear in the context.

- If any information is not available or cannot be determined from the context, use "N/A" for that field.

- Do not include any additional commentary or explanations outside of the specified format.

Begin your output immediately without any preamble. Ensure you provide data for all 40 articles in the format specified above.
"""

# {{CONTEXT}}を実際のコンテキストに置き換える
# ここで、my_dictを使ってリンクとサマリーを表示
context = ""
for i in range(40):
    context += f"{my_dict['link'][i]}\n{my_dict['summary'][i]}\n\n"

prompt = prompt.replace("{{CONTEXT}}", context)

# プロンプトを表示
print(prompt)

prompt = PromptTemplate.from_template(prompt)

# モデルを作成
# model = ChatBedrock(
#     region_name='us-east-1',
#     model_id='anthropic.claude-3-haiku-20240307-v1:0',
# )

# モデルを作成
model = ChatOpenAI(model="gpt-4o")

# chainを作成
chain = {"question": RunnablePassthrough()} | prompt | model | StrOutputParser()

# chainを実行
rank_info = chain.invoke("start")

# 解析用プロンプトの作成
prompt = """
あなたは、スマホゲームアプリのアナリストとして働いています。以下に提供されるゲームのランキング情報を分析し、その傾向についてレポートを作成する任務があります。

以下がゲームのランキングデータです：

<game_ranking_data>
{{GAME_RANKING_DATA}}
</game_ranking_data>

このデータを注意深く分析し、以下の点に注目してください：

1. トップランクのゲームの特徴
2. ジャンルの傾向
3. 新規参入と長期滞在のゲームの比較
4. 特筆すべき上昇や下降のトレンド

あなたのレポートは以下の構造に従ってください：

<report_structure>
1. 概要：主要な発見や全体的な傾向を簡潔に述べる
2. 詳細分析：上記の4つの点について詳しく説明する
3. 結論：データから導き出される重要なインサイトをまとめる
</report_structure>

レポート全体を日本語で作成してください。専門用語は適切に使用し、データに基づいた客観的な分析を心がけてください。

それでは、分析結果を以下のタグ内に記述してください：

<analysis_report>

</analysis_report>
"""

# {{GAME_RANKING_DATA}}を実際のランキングデータに置き換える
prompt = prompt.replace("{{GAME_RANKING_DATA}}", rank_info)

# プロンプトを表示
print(prompt)

prompt = PromptTemplate.from_template(prompt)

# chainを作成
chain = {"question": RunnablePassthrough()} | prompt | model | StrOutputParser()

# chainを実行
analysis_report = chain.invoke("start")

# 解析結果を表示
print(analysis_report)