from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from database import engine, SessionLocal
import models
from sqlalchemy.orm import Session
from pydantic import Field, BaseModel
from starlette import status
from Level_2_Intermediate_Advance_FastAPI.auth_api import get_current_user

models.Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/todo",
    tags=['Todo']
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class TodoRequest(BaseModel):
    title: str
    description: Optional[str]
    priority: str = Field(title="priority must be in between 1 to 5")
    check: bool

    class Config:
        schema_extra = {
            "example": {
                "title": "book name",
                "description": " book description",
                "priority": '1',
                "check": True

            }

        }


@router.get("/get/{todo_id}")
def get_sp_todo(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    elements = db.query(models.Todo).filter(models.Todo.id == todo_id) \
        .filter(models.Todo.owner_id == user.get('user_id')).all()
    if elements:
        return elements
    raise HTTPException(status_code=404, detail={str(todo_id): "Not found"})


@router.get("/get/user/")
def get_sp_todo_based_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    print("user data:",user.get("user_name"))
    elements = db.query(models.Todo).filter(models.Todo.owner_id == user.get('user_id')).all()
    if elements:
        return elements
    raise HTTPException(status_code=404, detail={str(user.get('user_id')): "Not found"})


@router.post("/post", status_code=status.HTTP_201_CREATED)
def post_todo(todo_request: TodoRequest, user: dict = Depends(get_current_user), db: SessionLocal = Depends(get_db)):
    try:
        print("user details from post todo:",user)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
        todo_model = models.Todo(**todo_request.dict(), owner_id=user.get('user_id'))
        # model = models.Todo()
        # model.title = todo_request.title
        # model.description = todo_request.description
        # model.priority = todo_request.priority
        # model.check = todo_request.check
        db.add(todo_model)
        db.commit()

        return {"Message": str(todo_model.title) + "created"}

    except Exception as arg:
        print("error is:",arg)
        return HTTPException(status_code=404, detail={"error": arg})


@router.put("/update/{todo_id}")
def update_todo(todo_id: int, todo: TodoRequest, user: dict = Depends(get_current_user),
                db: SessionLocal = Depends(get_db)):
    try:
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

        model_data = db.query(models.Todo).filter(models.Todo.id == todo_id).filter \
            (models.Todo.owner_id == user.get("user_id")).first()

        model_data.title = todo.title
        model_data.description = todo.description
        model_data.priority = todo.priority
        model_data.check = todo.check
        db.add(model_data)
        db.commit()

        return {"status_code": status.HTTP_200_OK, "Message": str(model_data.title) + " updated"}
    except Exception as arg:
        return HTTPException(status_code=404, detail={"error": arg})


@router.delete("/delete/{todo_id}")
def delete_todo(todo_id: int, user: dict = Depends(get_current_user), db: SessionLocal = Depends(get_db)):
    try:
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

        model_data = db.query(models.Todo).filter(models.Todo.id == todo_id). \
            filter(models.Todo.owner_id == user.get("user_id")).first()
        if model_data is not None:
            db.query(models.Todo).filter(models.Todo.id == todo_id).delete()
            db.commit()
            return {"status_code": status.HTTP_200_OK, "Message": "Deleted"}

        return HTTPException(status_code=404, detail={"error": "NOt found"})
    except Exception as arg:
        return HTTPException(status_code=404, detail={"error": arg})
