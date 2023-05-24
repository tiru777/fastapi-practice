import datetime
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from starlette import status
from database import engine, SessionLocal
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import models
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import jwt, JWTError


SECURITY_KEY = "1Q2W3E1S2D3X4C5G3V8N0M8N7G5F7HC4CJI7VMDK63SGO9743WXCBJUTRESVBHU7643GOJKO997RDCVBNKKI87543S"
ALGORITHM = 'HS256'


class CreateUser(BaseModel):
    email: str
    username: str
    firstname: str
    lastname: str
    hashed_password: str
    is_active: bool
    role: str


models.Base.metadata.create_all(bind=engine)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token/user-validation")
router = APIRouter(
    prefix="/auth",
    tags=['Authentication API']
)


def get_db_connection():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def authenticate_user(user_name: str, password: str, db):
    user = db.query(models.User).filter(models.User.username == user_name).first()
    print("user details from authentication:", user)
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(user_name: str, user_id: int, user_role: str, expires_date: timedelta):
    encode = {"sub": user_name, "id": user_id, "role": user_role}
    expire = datetime.datetime.utcnow() + expires_date
    encode.update({'exp': expire})
    return jwt.encode(encode, SECURITY_KEY, algorithm=ALGORITHM)


async def get_current_user(request: Request, token: str = Depends(oauth2_bearer)): # token: str = Depends(oauth2_bearer
    try:
        token = request.cookies.get("token")
        if token is None:
            return None
        print("token is :",  token)
        # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJrcmlzaG5hMTIzIiwiaWQiOjksInJvbGUiOiJTU0UiLCJleHAiOjE2ODQ4OTM1MTN9.HWTe-TDryZsUl3yy9gWei7wjcOL1OzgCfjP6cjPsBW0"
        payload = jwt.decode(token, SECURITY_KEY, algorithms=[ALGORITHM])
        print("jwt payload:", payload)
        user_name: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get("role")
        if user_name is None and user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not valid")
        return {"user_name": user_name, "user_id": user_id, "user_role": user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not valid")


@router.post("/user-creation", status_code=status.HTTP_201_CREATED)
def create_user(create_user_request: CreateUser, db: Session = Depends(get_db_connection)):
    create_user_model = models.User(
        email=create_user_request.email,
        username=create_user_request.username,
        firstname=create_user_request.firstname,
        lastname=create_user_request.lastname,
        is_active=create_user_request.is_active,
        hashed_password=bcrypt_context.hash(create_user_request.hashed_password),
        role=create_user_request.role
    )
    db.add(create_user_model)
    db.commit()


@router.post("/token/user-validation")
def login_for_access_token(response:Response,form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_connection)):
    user = authenticate_user(form_data.username, form_data.password, db)
    print("user from login:", user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    response.set_cookie(key="token", value=token, httponly=True)

    return {"token": token}


"""
https://jwt.io/
"""
