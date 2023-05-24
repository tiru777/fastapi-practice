from fastapi import APIRouter, Depends, HTTPException
from database import engine, SessionLocal
import models
from sqlalchemy.orm import Session
from starlette import status
from Level_2_Intermediate_Advance_FastAPI.auth_api import get_current_user
from passlib.context import CryptContext

models.Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/user",
    tags=['User']
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/get")
def get_user_details(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    # print("data:", user)
    user_details = db.query(models.User).filter(models.User.id == user.get('user_id')).first()
    if user_details:
        return user_details
    raise HTTPException(status_code=404, detail="Not found")


@router.get("/get-users")
def get_all_users(db: Session = Depends(get_db)):
    user_details = db.query(models.User).all()
    if user_details:
        return user_details
    raise HTTPException(status_code=404, detail="Not found")


@router.put("/update/{new_password}/{old_password}")
async def update_todo(new_password: str, old_password: str, user: dict = Depends(get_current_user),
                      db: SessionLocal = Depends(get_db)):
    try:
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

        user_details = db.query(models.User).filter(models.User.id == user.get('user_id')).first()
        if bcrypt_context.verify(old_password, user_details.hashed_password):
            user_details.hashed_password = bcrypt_context.hash(new_password)
            db.add(user_details)
            db.commit()
            return {"status_code": status.HTTP_200_OK, "Message": str(user.get('user_id')) + " updated"}
        return HTTPException(status_code=404, detail={"error": "verification failed"})
    except Exception as arg:
        return HTTPException(status_code=404, detail={"error": arg})
