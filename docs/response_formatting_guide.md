# Global Response Formatting Guide

This guide explains how to use the global response formatting system to maintain consistent API responses across all endpoints.

## Standard Response Format

All API responses follow this consistent structure:

```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": [
        {
            "id": 1,
            "name": "Example Item",
            "description": "This is an example"
        }
    ]
}
```

## Components

### 1. Response Formatter (`utils/response_formatter.py`)

The main service for creating formatted responses.

#### Basic Usage

```python
from utils.response_formatter import success_response, error_response

# Success response
return success_response(
    message="Data retrieved successfully",
    data={"items": [1, 2, 3]},
    status_code=200
)

# Error response
return error_response(
    message="Resource not found",
    data={"error_code": "NOT_FOUND"},
    status_code=404
)
```

#### Available Functions

- `success_response(message, data, status_code=200)`
- `error_response(message, data, status_code=400)`
- `created_response(message, data)` - 201 status
- `updated_response(message, data)` - 200 status
- `deleted_response(message, data)` - 200 status
- `not_found_response(message, data)` - 404 status
- `unauthorized_response(message, data)` - 401 status
- `forbidden_response(message, data)` - 403 status
- `validation_error_response(message, data)` - 422 status
- `server_error_response(message, data)` - 500 status

### 2. Custom Response Classes (`utils/custom_response.py`)

Pre-built response classes for different scenarios.

```python
from utils.custom_response import SuccessResponse, CreatedResponse, NotFoundResponse

# Success response
return SuccessResponse(
    message="Operation completed",
    data={"result": "success"}
)

# Created response (201 status)
return CreatedResponse(
    message="Resource created",
    data={"id": 123, "name": "New Item"}
)

# Not found response (404 status)
return NotFoundResponse(
    message="Item not found",
    data={"item_id": 999}
)
```

### 3. Response Decorators (`utils/response_decorator.py`)

Decorators that automatically format endpoint responses.

```python
from utils.response_decorator import success_response, created_response, list_response

@router.get("/items")
@list_response("Items retrieved successfully")
async def get_items():
    return [{"id": 1, "name": "Item 1"}]

@router.post("/items")
@created_response("Item created successfully")
async def create_item(name: str):
    return {"id": 2, "name": name}
```

### 4. Response Middleware (`middleware/response_middleware.py`)

Automatically formats responses that aren't already formatted.

```python
# In main.py
from middleware.response_middleware import ResponseFormatMiddleware

app.add_middleware(ResponseFormatMiddleware)
```

## Usage Examples

### Example 1: Basic GET Endpoint

```python
from fastapi import APIRouter
from utils.response_formatter import success_response

router = APIRouter()

@router.get("/users")
async def get_users():
    users = [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
    return success_response(
        message="Users retrieved successfully",
        data=users
    )
```

**Response:**
```json
{
    "success": true,
    "message": "Users retrieved successfully",
    "data": [
        {"id": 1, "name": "John"},
        {"id": 2, "name": "Jane"}
    ]
}
```

### Example 2: POST Endpoint with Validation

```python
from fastapi import APIRouter, HTTPException
from utils.response_formatter import created_response, validation_error_response

router = APIRouter()

@router.post("/users")
async def create_user(name: str, email: str):
    if not name or not email:
        return validation_error_response(
            message="Name and email are required",
            data={"missing_fields": ["name" if not name else "email"]}
        )

    user = {"id": 3, "name": name, "email": email}
    return created_response(
        message="User created successfully",
        data=user
    )
```

### Example 3: Using Decorators

```python
from fastapi import APIRouter
from utils.response_decorator import list_response, detail_response

router = APIRouter()

@router.get("/products")
@list_response("Products retrieved successfully")
async def get_products():
    return [{"id": 1, "name": "Product 1"}]

@router.get("/products/{product_id}")
@detail_response("Product retrieved successfully")
async def get_product(product_id: int):
    if product_id == 999:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"id": product_id, "name": f"Product {product_id}"}
```

### Example 4: Error Handling

```python
from fastapi import APIRouter, HTTPException
from utils.response_formatter import not_found_response, server_error_response

router = APIRouter()

@router.get("/items/{item_id}")
async def get_item(item_id: int):
    try:
        item = find_item(item_id)
        if not item:
            return not_found_response(
                message=f"Item with ID {item_id} not found",
                data={"item_id": item_id}
            )

        return success_response(
            message="Item retrieved successfully",
            data=item
        )
    except Exception as e:
        return server_error_response(
            message="An error occurred while retrieving the item",
            data={"error": str(e)}
        )
```

## Migration Guide

### Before (Old Format)
```python
@router.get("/items")
async def get_items():
    return {
        "items": [{"id": 1, "name": "Item 1"}],
        "count": 1
    }
```

### After (New Format)
```python
@router.get("/items")
async def get_items():
    return success_response(
        message="Items retrieved successfully",
        data={
            "items": [{"id": 1, "name": "Item 1"}],
            "count": 1
        }
    )
```

## Testing the Implementation

### Test Endpoints

Visit these endpoints to see the new response format in action:

<!-- - `GET /example/items` - List items
- `GET /example/items/1` - Get single item
- `POST /example/items` - Create item
- `PUT /example/items/1` - Update item
- `DELETE /example/items/1` - Delete item
- `GET /example/decorated-items` - Using decorators
- `GET /example/error-example` - Error handling -->

### Example API Calls

```bash
# Get all items
curl -X GET "http://localhost:8000/example/items"

# Create a new item
curl -X POST "http://localhost:8000/example/items?name=New Item&description=Test item"

# Get specific item
curl -X GET "http://localhost:8000/example/items/1"

# Update item
curl -X PUT "http://localhost:8000/example/items/1?name=Updated Item"

# Delete item
curl -X DELETE "http://localhost:8000/example/items/1"
```

## Best Practices

1. **Always use the response formatter functions** instead of returning raw dictionaries
2. **Provide meaningful messages** that describe what happened
3. **Include relevant data** in the response
4. **Use appropriate status codes** for different scenarios
5. **Handle errors gracefully** with proper error responses
6. **Use decorators for simple endpoints** to reduce boilerplate code
7. **Test your endpoints** to ensure they return the expected format

## Benefits

- **Consistency**: All responses follow the same structure
- **Predictability**: Clients know what to expect from every endpoint
- **Maintainability**: Easy to update response format across the entire API
- **Documentation**: Clear success/error indicators
- **Flexibility**: Multiple ways to create responses based on your needs
