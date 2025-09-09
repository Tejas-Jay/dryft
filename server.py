from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from client.py

# DB connection helper
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="rides_db",  # Change if your DB name is different
        user="postgres",      # Change if your username is different
        password="Kushi_2005" # Change if your password is different
    )

# Request a ride (User)
@app.route('/request_ride', methods=['POST'])
def request_ride():
    data = request.json
    source = data.get('source')
    destination = data.get('destination')
    client_lat = data.get('client_lat')
    client_lng = data.get('client_lng')

    if not source or not destination or client_lat is None or client_lng is None:
        return jsonify({"error": "Missing fields"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO rides (source, destination, availability, client_lat, client_lng) VALUES (%s, %s, %s, %s, %s)",
            (source, destination, 'pending', client_lat, client_lng)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Ride requested successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get all rides
@app.route('/get_rides', methods=['GET'])
def get_rides():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, source, destination, availability, client_lat, client_lng FROM rides ORDER BY id ASC")
        rides = cur.fetchall()
        cur.close()
        conn.close()

        rides_list = [
            {"id": r[0], "source": r[1], "destination": r[2], "availability": r[3], "lat": r[4], "lng": r[5]}
            for r in rides
        ]
        return jsonify(rides_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update ride status (Driver)
@app.route('/update_ride_status/<int:ride_id>', methods=['POST'])
def update_ride_status(ride_id):
    new_status = request.json.get("availability")
    if not new_status:
        return jsonify({"error": "Missing status"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE rides SET availability = %s WHERE id = %s", (new_status, ride_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Ride status updated", "ride_id": ride_id, "new_status": new_status})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Backend running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
