from fastapi import FastAPI
from Level_2_Intermediate_Advance_FastAPI import users, admin, todo, auth_api
from Level_3_Advance_Fullstack_TodoApp import auth, todo_ui

from database import engine
import models
from starlette.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Learning FastAPI")

app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(users.router)
app.include_router(admin.router)
app.include_router(todo.router)
app.include_router(auth_api.router)

app.include_router(auth.router)
app.include_router(todo_ui.router)


"""

For application running use 
uvicorn python_file_name:app --reload
"""