from typing import Optional

from fastapi import FastAPI, Body, Path, Query, HTTPException

from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()

data = [
    {"name": "thirumala reddy", "salary": 1, "height": 5.10},
    {"name": "madhu reddy", "salary": 1, "height": 5.9},
    {"name": "manu reddy", "salary": 5000, "address": "bangalore", "height": 5.3}
]


@app.get("/", status_code=status.HTTP_200_OK)
def first_fast_api():
    return {"god": "sadguruvenamha"}


@app.get("/list-data", status_code=status.HTTP_200_OK)
def list_of_get_data():
    return data


"""
# Dynamic path parameter
I want to pass thirumala reddy as input from url. you can't pass directly in url  https://120.0.0.1/thirumala reddy/

:parameter while passing in url you should use => https://120.0.0.1/thirumala%20reddy

%20 is behave like space thirumala reddy
"""


@app.get("/god/{parameter}")
def hello_path_parameter(parameter):
    return {"godname": parameter}


@app.get("/gurudeva/{parameter}")
def path_parameter(parameter: str):
    for dictt in data:
        if dictt.get("name") == parameter:
            return dictt
    return data


@app.get("/guruvu/{parameter}/{paramter_two}")
async def multiple_path_parameter(parameter: str, paramter_two: int):
    for dictt in data:
        if dictt.get("name") == parameter and dictt.get("salary") == paramter_two:
            return dictt
    return data


"""
# Query parameter
/?category=value
https://120.0.0.1/?category=value

It is basically we can pass directly key value to our api function without mention any parameter in function 
check example

"""


@app.get("/eruka")
async def func_query_parameter(height: float):
    return {"height": height}


@app.get("/eruka/{parameter}/")
async def func_query_get(parameter: str, height: float):
    data_up = []
    for dictt in data:
        if dictt.get("name") == parameter and dictt.get("height") == height:
            data_up.append(dictt)
    return data_up


@app.post("/eruka/create", status_code=status.HTTP_201_CREATED)
async def func_query_post(request_data=Body()):
    data.append(request_data)
    return data


@app.put("/eruka/update")
async def func_query_put(request_data=Body()):
    for i in range(len(data)):
        if data[i].get("name") == request_data.get("name"):
            data[i] = request_data
            return data


@app.delete("/eruka/delete/{delete_parameter}")
async def func_query_delete(delete_parameter: str):
    for dictt in data:
        if delete_parameter in dictt.values():
            data.remove(dictt)
    return data


# project 2
book_author_list = []


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


# Path is for validation of path parameter

@app.get("/get-book/{date}")
async def book_get(date: int = Path(gt=0)):
    for name_dict in book_author_list:
        if name_dict.date == date:
            return name_dict


# Query parameter validation by using Query
@app.get("/get-book/")
async def book_get(cost: int = Query(gt=0, lt=50)):
    for name_dict in book_author_list:
        if name_dict.cost == cost:
            return name_dict


@app.post("/createbook")
async def func_pydantic_post(book_object: DataHandle) -> list:
    book_author_list.append(Book(**book_object.dict()))
    return book_author_list


@app.put("/updatebook", status_code=status.HTTP_204_NO_CONTENT)
async def book_up(book_object: DataHandle):
    for i in range(len(book_author_list)):
        if book_author_list[i].author == book_object.author:
            book_author_list[i] = book_object
            return book_author_list
    raise HTTPException(status_code=404, detail={"status": "no content"})


@app.delete("/updatebook/{author}", status_code=status.HTTP_204_NO_CONTENT)
async def book_up(author: str = Path(title="minimum four charectors")):
    for i in range(len(book_author_list)):
        if book_author_list[i].author == author:
            book_author_list.pop(i)
            return {"status": "success", "message": str(author) + "is deleted"}
    raise HTTPException(status_code=404, detail={"status": "not found"})
