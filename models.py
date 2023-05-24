from sqlalchemy import Boolean, String, Integer, Column, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    firstname = Column(String)
    lastname = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    '''# todos = relationship("Todo", back_populates="owner")'''


class Todo(Base):
    __tablename__ = "todo"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(String)
    check = Column(Boolean)
    owner_id = Column(Integer, ForeignKey("user.id"))
    '''# owner = relationship("User", back_populates="todo")'''


"""
sqlite3 todo.db
.quit
.tables
.mod tables
.schema
"""
