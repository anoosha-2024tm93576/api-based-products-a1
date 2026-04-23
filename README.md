# API-Based Products — Assignment 1

---

## Repository Structure

```
api-based-products-a1/
├── openapi/
│   └── openapi.yaml
├── kong/
│   ├── kong.yaml
│   ├── docker-compose.yml
│   └── test-results.md
└── book-info-service/
    ├── app.py
    ├── books.json
    └── requirements.txt
```

---

## Record Label API — OpenAPI 3.1.1 Specification

### Overview

OpenAPI 3.1.1 specification for a Record Label API that manages
artists in a record label database. The spec defines all endpoints,
authentication, request/response schemas, and status codes.

### Authentication

All endpoints are secured using **Basic Authentication**.
Credentials must be included in every request header.

### Endpoints


| Method | Endpoint              | Description                       |
| ------ | --------------------- | --------------------------------- |
| GET    | /artists              | Get paginated list of all artists |
| POST   | /artists              | Add a new artist to the database  |
| GET    | /artists/{artistname} | Get a specific artist by username |


### Pagination

`GET /artists` supports pagination via query parameters:


| Parameter | Type    | Default | Description                |
| --------- | ------- | ------- | -------------------------- |
| offset    | integer | 0       | Page number to retrieve    |
| limit     | integer | 10      | Number of results per page |


### Data Model


| Field            | Type    | Description                                |
| ---------------- | ------- | ------------------------------------------ |
| username         | string  | Unique identifier for the artist           |
| name             | string  | Full name of the artist                    |
| genre            | string  | Music genre                                |
| albums_published | integer | Number of albums published under the label |


### Status Codes


| Code | Meaning                                       |
| ---- | --------------------------------------------- |
| 200  | Success                                       |
| 201  | Artist created successfully                   |
| 400  | Bad request — missing or invalid fields       |
| 401  | Unauthorized — invalid or missing credentials |
| 404  | Artist not found                              |
| 500  | Internal server error                         |


### How to View

1. Go to [https://editor.swagger.io](https://editor.swagger.io)
2. Paste the contents of `openapi/openapi.yaml`
3. The UI will render all endpoints interactively

---

## Kong API Gateway

### Overview

Rate limiting and request size limiting configured via Kong API Gateway
running in Docker (DB-less mode). Kong sits in front of the API and
enforces rules before traffic reaches the upstream service.

### Plugins Configured


| Plugin                | Configuration     | Response When Exceeded       |
| --------------------- | ----------------- | ---------------------------- |
| rate-limiting         | 5 requests/minute | 429 Too Many Requests        |
| request-size-limiting | 1MB max body      | 413 Request Entity Too Large |


### How to Run

Make sure Docker Desktop is running, then:

```bash
cd kong
docker-compose up -d
```


| Port | Description                                    |
| ---- | ---------------------------------------------- |
| 8000 | Kong proxy — all API traffic goes through here |
| 8001 | Kong admin — manage Kong configuration         |


### How to Test

**Rate Limiting:**

```bash
for i in {1..6}; do curl -si http://localhost:8000/api; done
```

Expected output:

```
If the upstream Flask service is NOT running:
Requests 1-5: 502 Bad Gateway
Request 6:    429 Too Many Requests ✅
```

**Request Size Limiting:**

```bash
python3 -c "print('x' * 2000000)" > bigfile.txt
curl -si -X POST http://localhost:8000/api -H "Content-Type: application/json" -d @bigfile.txt
```

Expected output:

```
HTTP/1.1 413 Request Entity Too Large
{"message": "Request size limit exceeded"} ✅
```

See`kong/test-results.md` for full test output.

---

## Book Info Service

### Overview

A Book Info Service demonstrating three API paradigms — REST, RPC,
and GraphQL — all serving identical data from a shared JSON data store.

### How to Run

```bash
cd book-info-service
python -m pip install -r requirements.txt
python app.py
```

Server runs on `http://localhost:5000`

### Endpoints


| Paradigm | Method | Endpoint    | Description                     |
| -------- | ------ | ----------- | ------------------------------- |
| REST     | GET    | /books      | Get all books                   |
| REST     | GET    | /books/{id} | Get book by id                  |
| RPC      | POST   | /getBook    | Get book by id in request body  |
| RPC      | POST   | /createBook | Create a new book               |
| GraphQL  | POST   | /graphql    | Query book with field selection |


### Sample Requests and Responses

**REST:**

```
GET http://localhost:5000/books/1
```

```json
{
  "id": 1,
  "title": "Harry Potter and the Sorcerer's Stone",
  "author": "J.K. Rowling"
}
```

**RPC:**

```
POST http://localhost:5000/getBook
```

```json
{
  "id": 1
}
```

```json
{
  "id": 1,
  "title": "Harry Potter and the Sorcerer's Stone",
  "author": "J.K. Rowling"
}
```

**GraphQL:**

```
POST http://localhost:5000/graphql
```

```json
{
  "query": "{ book(id:1) { title author } }"
}
```

```json
{
  "data": {
    "book": {
      "title": "Harry Potter and the Sorcerer's Stone",
      "author": "J.K. Rowling"
    }
  }
}
```

### Paradigm Comparison


| Feature       | REST                   | RPC                   | GraphQL                |
| ------------- | ---------------------- | --------------------- | ---------------------- |
| Style         | Resource-based         | Action-based          | Query-based            |
| HTTP Method   | GET, POST, PUT, DELETE | Mostly POST           | POST                   |
| Endpoints     | Multiple               | Multiple              | Single                 |
| Data Fetching | Fixed response fields  | Fixed response fields | Client selects fields  |
| Best For      | CRUD operations        | Specific actions      | Flexible data fetching |

