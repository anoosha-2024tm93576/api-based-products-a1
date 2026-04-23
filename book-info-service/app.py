from flask import Flask, jsonify
import json

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

if __name__ == "__main__":
    app.run(debug=True, port=5000)
