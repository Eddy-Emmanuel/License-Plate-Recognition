import numpy as np
from PIL import Image
from fastapi import status
from ultralytics import YOLO
from jose import jwt, JWTError
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.responses import JSONResponse

import sys
sys.path.append("./")
from backend_config.config import Configurations
from database_folder.create_table import DataBaseTable

CONFIG = Configurations()
password_encoder = CryptContext(schemes="bcrypt",deprecated="auto")

class SERVICE:
    def __init__(self,db:Session):
        self.db = db
    
    async def UserIsAvailable(self, username, institute):
        return self.db.query(DataBaseTable).filter(DataBaseTable.username == username,
                                                   DataBaseTable.institute == institute).first()
        
    async def AddNewUser(self, form):
        new_user = DataBaseTable(**form.dict(exclude="password"),
                                    hashed_password=password_encoder.hash(secret=form.password))
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return JSONResponse(content={"message":"Sucessfully Added User"},
                            status_code=status.HTTP_200_OK)
        
    async def GetAccessToken(self, username, password):
        user = self.db.query(DataBaseTable).filter(DataBaseTable.username == username).first()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,  
                                 detail="User not in database", 
                                 headers={"WWW-Authenticate":"Bearer"})
        
        if not password_encoder.verify(secret=password, hash=user.hashed_password):
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,  
                                 detail="Incorrect password", 
                                 headers={"WWW-Authenticate":"Bearer"})
        data = {
            "username":user.username,
            "institute":user.institute,
            "exp":datetime.utcnow()+timedelta(days=1)
        }
        
        return {"access_token":jwt.encode(data, CONFIG.secret_key, algorithm=CONFIG.algorithm),
                "token_type":"bearer"}
    
    async def VerifyToken(self, token:str):
        try:
            data = jwt.decode(token, CONFIG.secret_key , algorithms=CONFIG.algorithm)
            username = data.get("username", None)
            institute = data.get("institute", None)
            return (True, username, institute)
            
        except JWTError:
            raise  HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,  
                                 detail="Invalid Accesss Token", 
                                 headers={"WWW-Authenticate":"Bearer"})
        
    async def DeleteUser(self, username, institute):
        user = self.db.query(DataBaseTable).filter(DataBaseTable.username == username,
                                                   DataBaseTable.institute == institute).first()
        self.db.delete(user)
        self.db.commit()
        
        return JSONResponse(status_code=status.HTTP_200_OK,  
                            content={"message":"Sucessfully Deleted User"})
        
    async def GetLicensePlateNumber(self, image):
        image = np.array(Image.open(image))
        pre_trained_yolo_model = YOLO(model_path)
    
        prediction = pre_trained_yolo_model(file_path)
    
        pred_info = prediction[0].boxes
    
        loaded_image = np.array(Image.open(file_path).convert("RGB"))
    
        if len(pred_info.xyxy.to("cpu").numpy()) == 1:
            pred_xmin, pred_ymin, pred_xmax, pred_ymax = pred_info.xyxy.to("cpu").numpy().flatten().astype(np.int32)
            
            roi = loaded_image[pred_ymin:pred_ymax, pred_xmin:pred_xmax]
            
            return JSONResponse(status_code=status.HTTP_200_OK,  
                            content={"PlateNumber":f"{pytesseract.image_to_string(roi)}"})
        else:
            for (xmin, ymin, xmax, ymax) in pred_info.xyxy.to("cpu").numpy().astype(np.int32):
                
                roi = loaded_image[ymin:ymax, xmin : xmax]
            
                return JSONResponse(status_code=status.HTTP_200_OK,  
                            content={"PlateNumber":f"{pytesseract.image_to_string(roi)}"})
            