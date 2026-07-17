#----------------------------------------------------------------------------------------
#                                   Import Statements
#----------------------------------------------------------------------------------------

import os 
import time 
from pathlib import Path 
from dotenv import load_dotenv
from tqdm.auto import tqdm
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import asyncio

#----------------------------------------------------------------------------------------
#                                   Env Setup and init Statements
#----------------------------------------------------------------------------------------

load_dotenv()
openai_api_key = os.getenv("OPEN_AI_API")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")
pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")

# Openai embedding model
embed_model = OpenAIEmbeddings(
    api_key=os.getenv("OPEN_AI_API"),
    model="text-embedding-3-small"
)

# Where to upload the files
UPLOAD_DIR = "./upload_docs"
os.makedirs(UPLOAD_DIR , exist_ok=True)

#----------------------------------------------------------------------------------------
#                                   Logic Statements
#----------------------------------------------------------------------------------------

# Setting up the pinecone
pc = Pinecone(api_key=pinecone_api_key)
spec = ServerlessSpec(cloud = "aws" , region=pinecone_environment)

# Check if the index available or not
existing_index = [i['name'] for i in pc.list_indexes()]
if pinecone_index_name not in existing_index:
    pc.create_index(
        name = pinecone_index_name , 
        dimension = 1536,
        metric = "dotproduct",
        spec=spec 
    )

    while not pc.describe_index(pinecone_index_name).status['ready']:
        time.sleep(1)

index = pc.Index(pinecone_index_name)


async def load_vecorstore(uploaded_files , role : str , doc_id : str):
    """ 
        From uploaded files extract the text and then store that on pinecone
        Args:
            uploaded_files(list) : List of files passed by user
            role(str) : Role of the user
            doc_id(str) : Id of the document
    """
    # Iterate through the file list
    for file in uploaded_files:
        save_path = Path(UPLOAD_DIR)/file.filename
        # Write file for temp in another file
        with open(save_path , "wb") as f:
            f.write(file.file.read())
        # Load the file in the PyPDF Loader
        loader = PyPDFLoader(str(save_path))
        documents = loader.load()
        # Working on making chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size = 500 , chunk_overlap = 100)
        chunks = splitter.split_documents(documents)
        # Saving page content 
        texts = [chunk.page_content for chunk in chunks]
        ids = [f"{doc_id}-{id}" for id in range(len(chunks))]
        # Generating metadata
        metadata = [{
            "source" : file.filename,
            "doc_id" : doc_id,
            "role" : role,
            "page" : chunk.metadata.get("page" , 0),
            "text" : texts
        }
            for _, chunk in enumerate(chunks)
        ]
        # Generate Embeddings
        embeddings = await asyncio.to_thread(embed_model.embed_documents , texts)
        # Insert data into pinecone db
        print("Uploading to Pinecone...")
        index.upsert(vectors = zip(ids,embeddings,metadata))

        print(f"File :- {file.filename} uploaded.")