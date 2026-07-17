#----------------------------------------------------------------------------------------
#                                   Import Statements
#----------------------------------------------------------------------------------------

import os, asyncio
from dotenv import load_dotenv
from pinecone import Pinecone 
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

#----------------------------------------------------------------------------------------
#                                   Env Setup
#----------------------------------------------------------------------------------------

load_dotenv()
openai_api_key = os.getenv("OPEN_AI_API")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")
pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
groq_api_key = os.getenv("GROQ_API_KEY")

# Openai embedding model
embed_model = OpenAIEmbeddings(
    api_key=os.getenv("OPEN_AI_API"),
    model="text-embedding-3-small"
)

#----------------------------------------------------------------------------------------
#                                   Logic statement
#----------------------------------------------------------------------------------------

# Defining the pinecone and groq
pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index(pinecone_index_name)
llm = ChatGroq(api_key=groq_api_key , temperature=0.1 , model = "llama-3.3-70b-versatile")

# prompt 
prompt = PromptTemplate.from_template("""
    You are a helful healthcare assistant.Answer the following question based only
    on the provided context.
    Question:{question}

    Context : {context}
    Include the document source if relevant in your answer                                
""")

# Defining RAG Chain
rag_chain = prompt | llm 

# Answer Query Func
async def answer_query(query : str , role : str):
    """
        Based on user query and the role of user fuction will retrive context from
        Pinecone and then send it to the ragchain for further process
        If user is not same as document user then he/she cant access
        Args:
            query(str) : User question
            role(str) : Will useful for checking that this user allow to ask question or not
        Returns:
            will return a dict either having only answer as key or answer and sources as key
    """
    # Getting embeddings of query
    embedding = await asyncio.to_thread(embed_model.embed_query , query)
    # Getting results
    results = await asyncio.to_thread(index.query , vector=embedding , top_k = 3 , include_metadata = True)

    filtered_context = []
    sources = set()

    # Iterate over the result
    for match in results['matches']:
        metadata = match['metadata']
        # Checking the access of the user to the document
        if metadata.get("role") == role:
            filtered_context.append(metadata['text'])
            sources.add(metadata.get("source"))
        else:
            return {"answer" : "You are not authorised to ask question"}

    # What if there is no relevant chunks
    if not filtered_context:
        return {"answer" : "No relevant info found"}
        
    # Combining the text for context
    all_text = "\n\n".join(
            "\n".join(doc) for doc in filtered_context
        )
    # Invoking the rag chain
    final_answer = await asyncio.to_thread(rag_chain.invoke , {"question" : query , "context" : all_text})

    # Return the final outcome
    return {
        "answer" : final_answer.content,
        "sources" : list(sources)
    }