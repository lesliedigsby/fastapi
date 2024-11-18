from fastapi import Depends, status, HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app import schemas
from fastapi.security import OAuth2PasswordBearer
import pytz
from sqlalchemy.orm import Session
from . import models
from app.database import get_db
from app.config import settings

oath2_scheme = OAuth2PasswordBearer(tokenUrl='login')

utc_timezone = pytz.utc

# secret_key
# algorithm
# expiration_time of token

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(utc_timezone) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        if user_id is None:
            raise credentials_exception

        token_data = schemas.TokenData(id=str(user_id))
    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user(token: str = Depends(oath2_scheme),
                     db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user
