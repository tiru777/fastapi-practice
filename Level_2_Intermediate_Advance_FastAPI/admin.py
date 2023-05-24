from fastapi import APIRouter, Depends, HTTPException
from database import engine, SessionLocal
import models
from sqlalchemy.orm import Session
from starlette import status
from Level_2_Intermediate_Advance_FastAPI.auth_api import get_current_user

models.Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/admin",
    tags=['Admin']
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    except:
        db.close()


@router.get("/get")
def get_all_todos(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None or user.get("user_role") != "admin":
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    elements = db.query(models.Todo).all()
    if elements:
        return elements
    raise HTTPException(status_code=404, detail="Not found")


@router.delete("/user/{todo_id}")
def delete_sp_todo_based_user(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None or user.get("user_role") != "admin":
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail="Authentication or authorization failed credentials")

    elements = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if elements:
        db.query(models.Todo).filter(models.Todo.id == todo_id).delete()
        db.commit()
        return {"status_code": status.HTTP_200_OK, "Message": "Deleted"}

    raise HTTPException(status_code=404, detail={str(todo_id): "Not found"})
