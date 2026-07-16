#----------------------------------------------------------------------------------------
#                                   Import Statements
#----------------------------------------------------------------------------------------
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from .hash_utils import hash_password , verify_password
from .models import SignupRequest
from config.db import users_collection


#----------------------------------------------------------------------------------------
#                                   Logic Statements
#----------------------------------------------------------------------------------------

router = APIRouter()
security = HTTPBasic()

def authenticate(credentials : HTTPBasicCredentials = Depends(security)):
    """
        Autheticate the user before let access the other functionality
        Args:
            credentials(HTTPBasicCredentials) : The basic credentials can be pass via postman auth section
        Returns:
            - either give exception if the user is not found or the password is not match
            - or give the user info in dict format containing the username and role
    """
    user = users_collection.find_one({"username" : credentials.username})
    if not user or not verify_password(credentials.password , user['password']):
        raise HTTPException(status_code=401 , detail="Invalid Credentials")
    else:
        return {"username" : user['username'] , "role" : user['role']}


@router.post("/signup")
def signup(req : SignupRequest):
    """
        Signup to the Mongo DB for user
        Args:
            req(SignupRequest) : pydantic basemodel that have username role password in it
        Returns:
            - if the user is already there it will give exception
            - if user is not there it will return a simple confirmation message
    """
    if users_collection.find_one({"username" : req.username}):
        raise HTTPException(status_code=401 , detail = "User already exists")
    users_collection.insert_one({
        "username" : req.username,
        "password" : hash_password(req.password),
        "role" : req.role
    }) 
    return {
        "message" : "User Added Successfully."
    }

@router.get("/login")
def login(user=Depends(authenticate)):
    """
        Login to the MongoDB for user
        Args:
            user : this depends on the authenticate function which take HTTPBasicCredentials
        Returns:
            - if user verify then success message
            - else give error message
    """
    return {
        "message" : f"Welcome {user['username']}",
        "role" : user['role']
    }
