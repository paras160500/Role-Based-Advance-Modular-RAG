#----------------------------------------------------------------------------------------
#                                   Import Statements
#----------------------------------------------------------------------------------------

from fastapi import APIRouter, Depends, Form, HTTPException
from auth.routes import authenticate
from .chat_query import answer_query

#----------------------------------------------------------------------------------------
#                                   Import Statements
#----------------------------------------------------------------------------------------

router = APIRouter()

@router.post("/chat")
async def chat(user=Depends(authenticate),message : str = Form(...)):
    """

    """
    return await answer_query(message , user['role'])
