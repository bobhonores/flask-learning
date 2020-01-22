from flask import Flask, jsonify, request, Response
import json

app = Flask(__name__)

books = [
    {
        'name': 'Green Eggs and Ham',
        'price': 7.99,
        'isbn': 9780394800165
    },
    {
        'name': 'The Cat in the Hat',
        'price': 6.99,
        'isbn': 9782394800166
    }
]

#GET /books
@app.route('/books')
def get_books():
    return jsonify({'books': books})


def valid_book(input, properties=["name", "price", "isbn"]):
    return all(item in input.keys() for item in properties)


@app.route('/books', methods=['POST'])
def add_book():
    request_data = request.get_json()
    if valid_book(request_data):
        new_book = {
            "name": request_data['name'],
            "price": request_data['price'],
            "isbn": request_data['isbn']
        }
        books.insert(0, new_book)
        response = Response("", 201, mimetype="application/json")
        response.headers['Location'] = f"/books/{str(new_book['isbn'])}"

        return response
    else:
        return error_message()


@app.route('/books/<int:isbn>')
def get_book_by_isbn(isbn):
    return_value = {}

    for book in books:
        if book["isbn"] == isbn:
            return_value = {
                'name': book["name"],
                'price': book["price"]
            }

    return jsonify(return_value)


def error_message(message={
    "error": "Invalid book object passed in request",
    "helpString": "Data passed doesn't have the proper format"
}, status=400):
    response = Response(json.dumps(message),
                        status=status, mimetype='application/json')

    return response


@app.route('/books/<int:isbn>', methods=['PUT'])
def replace_book(isbn):
    request_data = request.get_json()

    if not valid_book(request_data, properties=["name", "price"]):
        return error_message()

    new_book = {
        'name': request_data["name"],
        'price': request_data["price"],
        'isbn': isbn
    }

    for i, book in enumerate(books):
        if new_book["isbn"] == book["isbn"]:
            books[i] = new_book
            break

    response = Response("", status=204)

    return response


@app.route('/books/<int:isbn>', methods=['PATCH'])
def update_book(isbn):
    request_data = request.get_json()
    isvalid_name = valid_book(request_data, ["name"])
    isvalid_price = valid_book(request_data, ["price"])

    if not (isvalid_name or isvalid_price):
        return error_message()

    for _, book in enumerate(books):
        if book["isbn"] == isbn:
            update_book = {
                'name': request_data.get("name") or book["name"],
                'price': request_data.get("price") or book["price"]
            }

            book.update(update_book)
            break

    response = Response("", status=204)
    response.headers["Location"] = f"/books/{str(isbn)}"
    return response


@app.route('/books/<int:isbn>', methods=['DELETE'])
def delete_book(isbn):
    for i, book in enumerate(books):
        if book["isbn"] == isbn:
            books.pop(i)
            response = Response("", status=204)
            return response

    invalid_object_message = {
        "error": "Book with the ISBN number that aw provided was not found, so therefore unable to delete"
    }
    return error_message(invalid_object_message, 404)


app.run(port=5000)
