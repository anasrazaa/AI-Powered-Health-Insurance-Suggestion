import os
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
# Removed pandas import as it's no longer needed

# Set your API key (or pass it from ENV)
openai_key = os.environ.get("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("OPENAI_API_KEY is not set")

# Load markdown file
with open("sample_plan.md", "r", encoding="utf-8") as f:
    md_content = f.read()

# Create a single Document from the markdown content
documents = [Document(page_content=md_content)]

# Split text
splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
docs = splitter.split_documents(documents)

# Embed and store
embedding = OpenAIEmbeddings()
vectordb = Chroma.from_documents(docs, embedding, persist_directory="db")
print("----------------------------------------------------------------")
# Prompt
custom_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
you have the following insurance plan as a reference




{context}

ALWAYS use the following format:
Question: the input question you must answer by analyzing the document content.
Thought: Outline your thought process.
Final Answer: always include the deductable or the other files that are in the document Provide your answer to the user question as Final Response.


Begin! Reminder to always use the exact characters `Final Answer` when responding.
Question: {question}
"""
)

llm = ChatOpenAI(temperature=0.4,model="gpt-4o-mini")

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectordb.as_retriever(search_kwargs={"k": 8}),
    chain_type="stuff",
    chain_type_kwargs={"prompt": custom_prompt},
    return_source_documents=True
)

# Test question
query = "List all the avaiable plans"
result = qa_chain({"query": query})

# result is printed here
print("----------------------------------------------------------------")
print(result["result"])
print("----------------------------------------------------------------")