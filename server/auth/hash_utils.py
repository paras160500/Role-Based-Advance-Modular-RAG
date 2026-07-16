#----------------------------------------------------------------------------------------
#                                   Import Statements
#----------------------------------------------------------------------------------------
import bcrypt

#----------------------------------------------------------------------------------------
#                                   Logic Statements
#----------------------------------------------------------------------------------------

def hash_password(password : str) -> str:
    """
        For hash the password
        Args:
            password(str) : string password given by user
        Returns:
            will return a hashed password which can be stored on the mongo
    """
    return bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt()).decode('utf-8')

def verify_password(password : str , hashed : str)-> bool:
    """
        For verify the hashed password with the real password
        Args:
            password(str) : original password
            hashed(str) : hashed password
        Returns:
            if both arguments match it will return true or else false 
    """
    return bcrypt.checkpw(password.encode("utf-8") , hashed.encode("utf-8"))