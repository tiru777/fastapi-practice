# Level 1: Basic FastAPI

This directory contains foundational FastAPI examples demonstrating core concepts and best practices for building RESTful APIs.

## File: `basic_fastapi_level_1.py`

A comprehensive FastAPI application with two projects showcasing CRUD operations, parameter validation, and Pydantic schema integration.

---

## Project 1: Employee Data Management API

### Overview
A simple CRUD API for managing employee information with basic data operations.

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Returns a welcome message |
| GET | `/list-data` | Retrieves all employee records |
| GET | `/god/{parameter}` | Returns path parameter as-is |
| GET | `/gurudeva/{parameter}` | Search employee by name |
| GET | `/guruvu/{parameter}/{paramter_two}` | Search employee by name and salary |
| GET | `/eruka` | Query employee by height |
| GET | `/eruka/{parameter}/` | Search employee by name and height |
| POST | `/eruka/create` | Create new employee record |
| PUT | `/eruka/update` | Update existing employee record |
| DELETE | `/eruka/delete/{delete_parameter}` | Delete employee record |

### Example Data
```json
{
  "name": "thirumala reddy",
  "salary": 1,
  "height": 5.10
}
```

---

## Project 2: Book Inventory API

### Overview
A structured book management API with Pydantic schema validation and comprehensive error handling.

### Data Model: `DataHandle`

```python
{
  "author": "string",
  "technology": "string (min 2 chars)",
  "address": "string (optional)",
  "cost": "float (0 < cost < 50)",
  "date": "integer (1999 < date < 2029)"
}
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/get-book/{date}` | Retrieve book by year (validated: > 0) |
| GET | `/get-book/` | Retrieve book by cost (validated: 0 < cost < 50) |
| POST | `/createbook` | Create new book record |
| PUT | `/updatebook` | Update existing book record |
| DELETE | `/updatebook/{author}` | Delete book by author |

### Example Request Body
```json
{
  "author": "thirumala reddy",
  "technology": "python",
  "address": "bangalore",
  "cost": 10.0,
  "date": 2022
}
```

---

## Key Concepts Demonstrated

### 1. **Path Parameters**
Dynamic URL segments passed directly in the endpoint path.
```python
@app.get("/gurudeva/{parameter}")
def path_parameter(parameter: str):
    # parameter is extracted from URL
```

### 2. **Query Parameters**
Key-value pairs passed after `?` in the URL.
```python
@app.get("/eruka")
async def func_query_parameter(height: float):
    # height is passed as ?height=5.10
```

### 3. **Request Body**
JSON data sent in POST/PUT requests.
```python
@app.post("/createbook")
async def func_pydantic_post(book_object: DataHandle):
    # book_object is automatically validated by Pydantic
```

### 4. **Parameter Validation**
Using `Path()`, `Query()`, and Pydantic `Field()` for validation rules.
```python
date: int = Path(gt=0)  # Path parameter must be > 0
cost: int = Query(gt=0, lt=50)  # Query parameter: 0 < cost < 50
technology: str = Field(min_length=2)  # Minimum length validation
```

### 5. **HTTP Status Codes**
Explicit status codes for different operations.
```python
@app.get("/", status_code=status.HTTP_200_OK)
@app.post("/createbook", status_code=status.HTTP_201_CREATED)
@app.put("/updatebook", status_code=status.HTTP_204_NO_CONTENT)
```

### 6. **Error Handling**
HTTPException for returning custom error responses.
```python
raise HTTPException(status_code=404, detail={"status": "not found"})
```

### 7. **Pydantic Models**
Schema definition and automatic validation using BaseModel.
```python
class DataHandle(BaseModel):
    author: str
    technology: str = Field(min_length=2)
    address: Optional[str] = Field(title="address is not mandatory")
    cost: float
    date: int = Field(gt=1999, lt=2029)
```

### 8. **Swagger Documentation**
Automatic API documentation using Pydantic schema and Config.
```python
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
```

---

## How to Run

### Prerequisites
```bash
pip install fastapi
pip install uvicorn
```

### Start the Server
```bash
uvicorn basic_fastapi_level_1:app --reload
```

### Access the API
- **API Documentation (Swagger UI)**: `http://localhost:8000/docs`
- **Alternative Documentation (ReDoc)**: `http://localhost:8000/redoc`

---

## Testing Examples

### Project 1: Employee API

**Get all employees:**
```bash
curl http://localhost:8000/list-data
```

**Search employee by name:**
```bash
curl http://localhost:8000/gurudeva/thirumala%20reddy
```

**Create employee:**
```bash
curl -X POST http://localhost:8000/eruka/create \
  -H "Content-Type: application/json" \
  -d '{"name":"john doe","salary":5000,"height":6.0}'
```

### Project 2: Book API

**Create book:**
```bash
curl -X POST http://localhost:8000/createbook \
  -H "Content-Type: application/json" \
  -d '{
    "author":"thirumala reddy",
    "technology":"python",
    "address":"bangalore",
    "cost":10.0,
    "date":2022
  }'
```

**Get book by cost:**
```bash
curl "http://localhost:8000/get-book/?cost=10"
```

**Delete book:**
```bash
curl -X DELETE http://localhost:8000/updatebook/thirumala%20reddy
```

---

## Notes

- **URL Encoding**: Special characters like spaces must be URL-encoded (`%20` for space)
- **In-Memory Storage**: Data is stored in Python lists and will be reset on server restart
- **Async Functions**: Some endpoints use `async` for demonstrating async capabilities
- **Validation**: Both path and query parameters support validation constraints

---

## Next Steps

Explore Level 2 for advanced topics like:
- Database integration
- Authentication & Authorization
- Middleware
- Custom responses
- File uploads
- WebSockets

