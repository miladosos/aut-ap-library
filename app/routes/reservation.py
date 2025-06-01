from flask import jsonify, request
from app.application import app
from database import reserve_book, cancel_reservation, get_user_reservations

@app.route("/api/v1/books/<book_id>/reserve", methods=["POST"])
def reserve_book_route(book_id: str):
    user_id = request.headers.get("user_id")
    if not user_id:
        return jsonify({"error": "Invalid input"}), 400
    try:
        reservation = reserve_book(book_id, user_id)
        return jsonify(reservation), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404 if "not found" in str(e) else 400

@app.route("/api/v1/books/<book_id>/reserve", methods=["DELETE"])
def cancel_reservation_route(book_id: str):
    user_id = request.headers.get("user_id")
    if not user_id:
        return jsonify({"error": "Invalid input"}), 400
    try:
        cancel_reservation(book_id, user_id)
        return jsonify({"message": "Reservation cancelled successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404 if "not found" in str(e) else 400

@app.route("/api/v1/users/<user_id>/reservations")
def get_user_reservations_route(user_id: str):
    try:
        reservations = get_user_reservations(user_id)
        return jsonify(reservations), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
