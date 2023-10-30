from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import chromadb
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain import HuggingFacePipeline
import os
import sys
from tqdm import tqdm
import pandas as pd
os.environ ['CUDA_VISIBLE_DEVICES'] = "1"


sys.path.append(os.path.dirname(os.path.realpath('__file__'))+"/../../")
import config.conf as cfg
from chromadb.config import Settings

replace_str = "/spider/mit_spider"

# Define the folder for storing database
PERSIST_DIRECTORY = cfg.PERSIST_DIRECTORY.replace(replace_str,"")
# Define the Chroma settings
CHROMA_SETTINGS = Settings(
        persist_directory=PERSIST_DIRECTORY,
        anonymized_telemetry=False
)

embeddings_model_name = cfg.EMBEDDINGS_MODEL_NAME.replace(replace_str,"")
persist_directory = cfg.PERSIST_DIRECTORY.replace(replace_str,"")
model_path = cfg.MODEL_PATH.replace(replace_str,"")
model_n_ctx = cfg.MODEL_N_CTX
model_n_batch = cfg.MODEL_N_BATCH
target_source_chunks = 4
embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
chroma_client = chromadb.PersistentClient(settings=CHROMA_SETTINGS , path=persist_directory)
db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, client_settings=CHROMA_SETTINGS, client=chroma_client)


embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
model = HuggingFacePipeline.from_model_id(model_id=model_path,
        task="text-generation",
        device=0,
        pipeline_kwargs={
            "max_new_tokens": 16384, 
            "do_sample": True,
            "temperature": 0.2,
            "top_k": 50,
            "top_p": 0.9,
            "repetition_penalty": 1.1},
        model_kwargs={
            "torch_dtype": "auto",
            "low_cpu_mem_usage": True}
        )

mit_info = pd.read_excel("./mit_structure_info.xlsx")
lst1 = []
lst2 = []
for i in range(100):
    try:
        item = mit_info.iloc[i].to_dict()
        item.pop("id")
        item = {
            '标题': item['name'],
            '简介': item['summary'],
            '文章类别': item['typeName'],
            '文章内容': item['content']
        }


        que = str(item)

        # 回答模板 将summary_query的输出格式化为对象
        response_schemas = [
            ResponseSchema(name="核心任务", description="给出文章的核心任务, 是有关于公司的主要职责，包括产品开发、市场营销和客户支持等"),
            ResponseSchema(name="创新文化", description="给出项目的创新文化部分,是有关于鼓励提出新点子和方法，以不断改进和发展公司"),
            ResponseSchema(name="激励机制", description="给出激励机制,包括奖励创新和负反馈等方式，以激励创新绩效"),
            ResponseSchema(name="原创技巧", description="给出原创技巧,指对项目的成功至关重要的技巧"),
            ResponseSchema(name="科研兴趣", description="给出科研兴趣,是以推动创新的兴趣部分"),
            ResponseSchema(name="团队协作", description="给出团队协作,是有关该任务由哪些团队协作完成,可以给出具体名字"),
            ResponseSchema(name="发生时间", description="给出文章发生的大概时间"),
            
        ]

        summary_query = """
        "
        1. 核心任务：文章中涉及到公司的主要职责，包括产品开发、市场营销、客户支持等，以确定文章的核心任务是什么。

        2. 创新文化：查找有关鼓励新点子和方法，以不断改进和发展公司的部分，以便了解文章中提到的创新文化。

        3. 激励机制：寻找文章中提及的激励机制，包括奖励创新和负反馈等方式，以激励创新绩效。

        4. 原创技巧：识别文章中强调的成功至关重要的技巧，这些技巧对项目的成功有何关联。

        5. 科研兴趣：分析文章中提到的科研兴趣，以了解它们如何推动创新。

        6. 团队协作：查找文章中涉及的团队协作情况，可以提供具体团队的名称或信息。

        7. 团队协作：给出文章发生的大概时间。

        阅读上面文章，然后提取并分析七个关键信息，每个信息需要包括方法、人名、机构等的具体名字，可以通过全文推理得出。按照要求执行这个任务，返回一个包含七个关键信息的纯Python字典。
        """
        initial_qa_template = (
            "[INST] <<SYS>>\n"
            "You are an article reading analyst. 你是一个文章阅读分析者。\n"
            "<</SYS>>\n\n"
            "以下为文章的主要细节：\n"
            "{context_str}"
            "\n"
            "{format_instructions}"
            "\n"
            "请根据以上背景知识, 回答这个问题：{question}。"
            " [/INST]"
        )


        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()
        prompt = PromptTemplate(
            template=initial_qa_template,
            input_variables=["question"],
            partial_variables={"format_instructions": format_instructions,"context_str":que}
        )
        _input = prompt.format_prompt(question=summary_query)
        output = model(_input.to_string())
        lst1.append((i,output))
        print(output)
        rjs = output_parser.parse(output.replace("```","").replace(" python\n","").replace("\n",""))
        print(rjs)
        lst2.append((i,rjs))
    except:
        continue
import pickle

# 将对象保存到文件
with open('data1.pkl', 'wb') as file:
    pickle.dump(lst1, file)
with open('data2.pkl', 'wb') as file:
    pickle.dump(lst2, file)
