# the installation should only happen on the server once
# the pip instructions aren't part of the script itself
"""
!pip install llama-index -r requirements.txt
!pip install openai -r requirements.txt
!pip install langchain -r requirements.txt
!pip install fastapi nest-asyncio pyngrok uvicorn -r requirements.txt
"""
# - - -
import os
import openai
from llama_index import SimpleDirectoryReader, GPTVectorStoreIndex, LLMPredictor, ServiceContext
import pandas as pd
from langchain.chat_models import ChatOpenAI
# import ssl
from django.conf import settings


class Chatbot():
    KEY = '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'
    PATH = "./dataset/"
    DOCS_PATH = "./docs/"
    SHEET_NAME = "aufenthaltstitel.xlsx"

    query_engine = None
    # Only for local and demo environment
    # context = ssl._create_unverified_context()

    def start(self):
        # this should be part of the initialization routine for the server and can be called anytime you want to update the document database
        self.build_dataset()
        index = self.construct_index(self.DOCS_PATH)
        self.query_engine = index.as_query_engine()
        # os.environ["OPENAI_API_KEY"] = self.KEY

    # construct documents in a subfolder of current directory
    def build_dataset(self):
        if not os.path.exists(self.DOCS_PATH):
            os.makedirs(self.DOCS_PATH)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_file_path = os.path.join(
            current_dir, 'dataset', 'aufenthaltstitel.xlsx')
        df = pd.read_excel(data_file_path)
        for index, row in df.iterrows():
            doc = row["HTML Body"]
            if pd.isna(doc):
                break
            doc = doc.replace("\uf0b7", "\u2022").replace(
                "\uf0e0", "\u003e").replace("简体中文", "Chinese simplified")
            with open(self.DOCS_PATH + f"file_{index}.txt", "w") as f:
                f.write(doc)

    def construct_index(self, directory_path):
        num_outputs = 512
        openai.api_key = self.KEY
        print(openai.api_key)
        llm_predictor = LLMPredictor(llm=ChatOpenAI(
            temperature=0.5, model_name="gpt-3.5-turbo-16k", max_tokens=num_outputs, openai_api_key='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'))
        service_context = ServiceContext.from_defaults(
            llm_predictor=llm_predictor)
        docs = SimpleDirectoryReader(self.DOCS_PATH).load_data()
        index = GPTVectorStoreIndex.from_documents(
            docs, service_context=service_context, )
        return index

    def chatbot(self, input_text):
        response = self.query_engine.query(input_text)
        return response.response
# - - -
