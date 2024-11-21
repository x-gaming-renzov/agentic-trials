from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool

def get_retriever_tool(docs, model_name='openai-gpt'):
    
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                        chunk_size=100, chunk_overlap=50
                    )
    doc_splits = text_splitter.split_documents(docs)

    vectorstore = Chroma.from_documents(doc_splits, model=OpenAIEmbeddings(model_name))
    retriever = vectorstore.as_retriever()
    retriever_tool = create_retriever_tool(
        retriever,
        "retrieve_knowledge_from_docs",
        "Retrieve knowledge from documents provided by the user",
    )
    return retriever_tool


    