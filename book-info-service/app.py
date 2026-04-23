from flask import Flask, jsonify, request
import json, re

app = Flask(__name__)

# Reading the books from the JSON file
with open("books.json") as file:
    data = json.load(file)
    books = data["books"]


# REST Endpoints

@app.route("/books", methods=["GET"])
def get_books():
    return jsonify(books), 200


@app.route("/books/<int:id>", methods=["GET"])
def get_book(id):
    book = next((b for b in books if b["id"] == id), None)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book), 200


# RPC Endpoints

@app.route("/getBook", methods=["POST"])
def get_book_rpc():
    body = request.get_json()
    if not body or "id" not in body:
        return jsonify({"error": "Missing id in request body"}), 400
    book = next((b for b in books if b["id"] == body["id"]), None)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book), 200


@app.route("/createBook", methods=["POST"])
def create_book_rpc():
    body = request.get_json()
    if not body or "title" not in body or "author" not in body:
        return jsonify({"error": "Missing title or author in request body"}), 400
    new_book = {
        "id": len(books) + 1,
        "title": body["title"],
        "author": body["author"]
    }
    books.append(new_book)
    return jsonify(new_book), 201


# GraphQL Endpoints

@app.route("/graphql", methods=["POST"])
def graphql():
    body = request.get_json()
    if not body or "query" not in body:
        return jsonify({"error": "Missing query"}), 400

    query = body["query"]

    match = re.search(r'book\(id\s*:\s*(\d+)\)', query)
    if not match:
        return jsonify({"error": "Invalid query format"}), 400

    id = int(match.group(1))
    book = next((b for b in books if b["id"] == id), None)
    if book is None:
        return jsonify({"errors": [{"message": "Book not found"}]}), 404

    fields_match = re.search(r'\{([^}]+)\}[^{]*$', query)
    if not fields_match:
        return jsonify({"error": "No fields specified"}), 400

    requested_fields = fields_match.group(1).split()
    result = {field: book[field] for field in requested_fields if field in book}

    return jsonify({"data": {"book": result}}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
