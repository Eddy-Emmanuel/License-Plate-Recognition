from pydantic import BaseModel

class RegistrationForm(BaseModel):
    username : str
    password : str
    institute : str
    
class RegistrationSuccessResponse(BaseModel):
    message : str
    class Config:
        from_attributes = True
        
class Token(BaseModel):
    access_token : str
    token_type : str
    
class DeleteResponse(BaseModel):
    message : str
    class Config:
        from_attributes = True
        
class UserDetails(BaseModel):
    username : str
    institution : str
    class Config:
        from_attributes = True
        
class PlateNumber(BaseModel):
    plate_number : str
    class Config:
        from_attributes = True
        
