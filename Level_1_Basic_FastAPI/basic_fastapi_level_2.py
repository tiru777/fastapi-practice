from typing import Optional

from fastapi import FastAPI, Path, Query, HTTPException

from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()


# project 2
book_author_list = [
    {
        "author": "thirumala reddy",
        "technology": "python",
        "address": "bangalore",
        "cost": 10.0,
        "date": 2022
    },
    {
        "author": "Manu reddy",
        "technology": "accounts",
        "address": "bangalore",
        "cost": 11.0,
        "date": 2021
    }



]


class Book:

    def __init__(self, author, technology, address, cost, date):
        self.author = author
        self.technology = technology
        self.address = address
        self.cost = cost
        self.date = date


class DataHandle(BaseModel):
    """
    This pydantic class for schema and description of swagger API documentation
    Field attribute is used for adding description to parameter
    """
    author: str
    technology: str = Field(min_length=2)  # we can maintain min length using field gt>2, lt<4
    address: Optional[str] = Field(title="address is not mandatory")
    cost: float
    date: int = Field(gt=1999, lt=2029, title="date should be year only")

    class Config:
        schema_extra = {
            "example": {
                "author": "thirumala reddy",
                "technology": "python",
                "address": "bangalore",
                "cost": 10.0,
                "date": 2022

            }
        }


@app.get('/')
async def get_list_books():
    return book_author_list


# Path is for validation of path parameter

@app.get("/get-book/{date}")
async def get_book_by_date(date: int = Path(gt=0)):
    for name_dict in book_author_list:
        if name_dict.get('date') == date:
            return name_dict


# Query parameter validation by using Query
@app.get("/get-book/")
async def get_book_by_cost(cost: int = Query(gt=0, lt=50)):
    for name_dict in book_author_list:
        if name_dict.get('cost') == cost:
            return name_dict


@app.post("/create_book",status_code=status.HTTP_200_OK)
async def func_pydantic_post(book_object: DataHandle) -> list:
    # book_author_list.append(Book(**book_object.dict()))  # if you want store data in object you can use it
    book_author_list.append((book_object.dict()))
    return book_author_list


@app.put("/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def book_up(book_object: DataHandle):
    print(book_author_list)

    for i in range(len(book_author_list)):
        if book_author_list[i].get('author') == book_object.author:
            book_author_list[i] = book_object.dict()
            return book_author_list
    raise HTTPException(status_code=404, detail={"status": "No content"})


@app.delete("/update_book/{author}", status_code=status.HTTP_204_NO_CONTENT)
async def book_up(author: str = Path(title="minimum four characters")):
    for i in range(len(book_author_list)):
        if book_author_list[i].get('author') == author:
            book_author_list.pop(i)
            return {"status": "success", "message": str(author) + "is deleted"}
    raise HTTPException(status_code=404, detail={"status": "not found"})
