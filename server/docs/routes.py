#----------------------------------------------------------------------------------------
#                                   Import Statements
#----------------------------------------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from auth.routes import authenticate
from .vectorstore import load_vecorstore
import uuid

#----------------------------------------------------------------------------------------
#                                   Logical Statements
#----------------------------------------------------------------------------------------

router = APIRouter()

@router.post("/upload_docs")
async def upload_docs(
    user = Depends(authenticate),                   # Authenticate user first and save infor in user
    file : UploadFile = File(...),                  # File(...) because we can upload more than 1 file 
    role : str = Form(...)                          # Form(...) because we are collection from the form(postman)
):
    # Check if user rols is admin or not 
    if user['role'] != "admin":
        raise HTTPException(status_code=401 , detail = "Only admin can upload docs.")
    
    doc_id = str(uuid.uuid4())
    await load_vecorstore([file] , role , doc_id)

    return {
        "message" : f"{file.filename} added to pinecone.",
        "doc_id" : doc_id,
        "accessible_to" : role
    }
    