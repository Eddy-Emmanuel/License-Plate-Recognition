from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

import sys
sys.path.append("./")
from backend_config.service import SERVICE
from database_folder.create_session import GetDatabase
from backend_config.schema import RegistrationForm, RegistrationSuccessResponse,\
                                  Token, DeleteResponse, UserDetails

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

@router.post("/user_registration", 
             tags=["User Registration"],
             response_model=RegistrationSuccessResponse,
             status_code=status.HTTP_200_OK)

async def user_registration(form: RegistrationForm, 
                            db: Session = Depends(GetDatabase)):
    
    service = SERVICE(db=db)
    user_exists = await service.UserIsAvailable(username=form.username, institute=form.institute)
    
    if not user_exists:
        return await service.AddNewUser(form=form)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User already in database")

@router.post("/token", 
             tags=["Get Access Token"],
             response_model=Token, 
             status_code=status.HTTP_200_OK)
async def get_access_token(form: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(GetDatabase)):
    
    service = SERVICE(db=db)
    token = await service.GetAccessToken(username=form.username, password=form.password)
    if token:
        return token
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@router.get("/user_details", 
            tags=["Get user Details"],
            response_model=UserDetails,
            status_code=status.HTTP_200_OK)

async def get_user_details(token:Annotated[str, Depends(oauth2_scheme)],
                           db:Annotated[Session, Depends(GetDatabase)]):
    
    service = SERVICE(db=db)
    token_valid, username, institute = await service.VerifyToken(token=token)
    if token_valid:
        user = await service.UserIsAvailable(username=username, institute=institute)
        return JSONResponse(content={"username":user.username, "institution":user.institute})
    else:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, 
                            detail="Unable to delete user")
    
    

@router.delete("/delete_user", 
               tags=["Delete Current User"],
               response_model=DeleteResponse, 
               status_code=status.HTTP_200_OK)
async def delete_current_user(token: Annotated[str, Depends(oauth2_scheme)], 
                              db: Annotated[Session, Depends(GetDatabase)]):
    
    service = SERVICE(db=db)
    
    token_valid, username, institute = await service.VerifyToken(token=token)
    if token_valid:
        return await service.DeleteUser(username=username, institute=institute)
    else:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, 
                            detail="Unable to delete user")
