from flask import request, jsonify
from app.db import load_data, save_data
from app.application import app


@app.route("/api/v1/users/<user_id>/reservations", methods=['GET'])
def get_reservations():
    data = load_data()
    return jsonify(data.get('reservations', [])), 200


@app.route("/api/v1/books/<book_id>/reserve", methods=['POST'])
def create_reservation():
    data = load_data()
    reservation = request.get_json()

    if "id" not in reservation or "user_id" not in reservation or "book_id" not in reservation:
        return jsonify({"error": "id, user_id and book_id are required"}), 400

    user_exists = any(u["id"] == reservation["user_id"]
                      for u in data.get("users", []))
    book_exists = any(b["id"] == reservation["book_id"]
                      for b in data.get("books", []))

    if not user_exists or not book_exists:
        return jsonify({"error": "User or Book not found"}), 400

    data.setdefault("reservations", []).append(reservation)
    save_data(data)
    return jsonify(reservation), 201


@app.route("/api/v1/users/<user_id>/reservations", methods=['GET'])
def get_reservation(reservation_id):
    data = load_data()
    reservation = next((r for r in data.get('reservations', [])
                       if r['id'] == reservation_id), None)
    if reservation:
        return jsonify(reservation), 200
    return jsonify({'error': 'Reservation not found'}), 404


@app.route("/api/v1/books/<book_id>/reserve", methods=["DELETE"])
def delete_reservation(reservation_id):
    data = load_data()
    reservations = data.get('reservations', [])
    new_reservations = [r for r in reservations if r['id'] != reservation_id]
    if len(reservations) == len(new_reservations):
        return jsonify({'error': 'Reservation not found'}), 404
    data['reservations'] = new_reservations
    save_data(data)
    return '', 204
