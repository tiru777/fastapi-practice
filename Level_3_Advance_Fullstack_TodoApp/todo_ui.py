from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from starlette import status
from Level_3_Advance_Fullstack_TodoApp.auth import get_current_user
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import models

router = APIRouter(
    prefix="/todo_ui",
    tags=['Todo UI']
)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/home", response_class=HTMLResponse)
async def todo_home(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todos = db.query(models.Todo).filter(models.User.id == user.get('id')).all()

    return templates.TemplateResponse("home.html", context={"request": request, "todos": todos,"user":user})


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("add-todo.html", context={"request": request})


@router.post("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request, title: str = Form(...), description: str = Form(...),
                       priority: int = Form(...),
                       db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo_model = models.Todo()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.check = False
    todo_model.owner_id = user.get('id')
    db.add(todo_model)
    db.commit()
    return RedirectResponse(url="/todo_ui/home", status_code=status.HTTP_302_FOUND)


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    return templates.TemplateResponse("edit-todo.html", context={"request": request, "todo": todo,"user":user})


@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, title: str = Form(...), description: str = Form(...),
                    priority: int = Form(...), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo_model = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    # todo_model.check = False
    todo_model.owner_id = user.get('id')
    db.add(todo_model)
    db.commit()
    return RedirectResponse(url="/todo_ui/home", status_code=status.HTTP_302_FOUND)


@router.get("/delete/{todo_id}", response_class=HTMLResponse)
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    try:
        user = await get_current_user(request)
        if user is None:
            return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

        todo_data = db.query(models.Todo).filter(models.Todo.id == todo_id)\
            .filter(models.Todo.owner_id == user.get('id')).first()
        if todo_data is None:
            return RedirectResponse(url="/todo_ui/home", status_code=status.HTTP_302_FOUND)

        db.query(models.Todo).filter(models.Todo.id == todo_id).delete()
        db.commit()
        return RedirectResponse(url="/todo_ui/home", status_code=status.HTTP_302_FOUND)

    except Exception as error:
        print("error is ", error)
        return RedirectResponse(url="/todo_ui/home", status_code=status.HTTP_302_FOUND)

