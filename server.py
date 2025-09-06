from flask import Flask, request, jsonify, render_template_string
import psycopg2

app = Flask(__name__)

# DB connection helper
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="rides_db",
        user="postgres",
        password="Kushi_2005"
    )

# Home (frontend)
@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mini Uber</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            input, button { margin: 5px; padding: 5px; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
            th { background-color: #f2f2f2; }
            .pending { background-color: #ffffcc; }
            .accepted { background-color: #ccffcc; }
        </style>
        <script>
            async function requestRide() {
                const source = document.getElementById("source").value;
                const destination = document.getElementById("destination").value;
                const lat = parseFloat(document.getElementById("lat").value);
                const lng = parseFloat(document.getElementById("lng").value);

                await fetch("/request_ride", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ source, destination, client_lat: lat, client_lng: lng })
                });
                loadRides();
            }

            async function loadRides() {
                const response = await fetch("/get_rides");
                const rides = await response.json();

                const table = document.getElementById("ridesTable");
                table.innerHTML = `
                    <tr>
                        <th>ID</th>
                        <th>Source</th>
                        <th>Destination</th>
                        <th>Status</th>
                        <th>Lat</th>
                        <th>Lng</th>
                        <th>Actions</th>
                    </tr>
                `;

                rides.forEach(r => {
                    const row = document.createElement("tr");
                    row.className = r.availability; // pending / accepted
                    row.innerHTML = `
                        <td>${r.id}</td>
                        <td>${r.source}</td>
                        <td>${r.destination}</td>
                        <td>${r.availability}</td>
                        <td>${r.lat ?? "null"}</td>
                        <td>${r.lng ?? "null"}</td>
                        <td>
                            <button onclick="updateRide(${r.id}, 'accepted')">Accept</button>
                            <button onclick="updateRide(${r.id}, 'completed')">Complete</button>
                            <button onclick="updateRide(${r.id}, 'rejected')">Reject</button>
                        </td>
                    `;
                    table.appendChild(row);
                });
            }

            async function updateRide(rideId, status) {
                await fetch(`/update_ride_status/${rideId}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ availability: status })
                });
                loadRides();
            }

            window.onload = loadRides;
        </script>
    </head>
    <body>
        <h2>Request a Ride</h2>
        <input type="text" id="source" placeholder="Source">
        <input type="text" id="destination" placeholder="Destination">
        <input type="number" id="lat" placeholder="Lat" step="0.000001">
        <input type="number" id="lng" placeholder="Lng" step="0.000001">
        <button onclick="requestRide()">Request Ride</button>

        <h2>All Active Rides</h2>
        <table id="ridesTable"></table>
    </body>
    </html>
    """
    return render_template_string(html)

# Request a new ride
@app.route('/request_ride', methods=['POST'])
def request_ride():
    data = request.json
    source = data['source']
    destination = data['destination']
    client_lat = data.get('client_lat')
    client_lng = data.get('client_lng')

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

# Fetch all active rides
@app.route('/get_rides', methods=['GET'])
def get_rides():
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

# Update ride status
@app.route('/update_ride_status/<int:ride_id>', methods=['POST'])
def update_ride_status(ride_id):
    new_status = request.json.get("availability")

    conn = get_db_connection()
    cur = conn.cursor()

    if new_status in ("completed", "rejected"):
        # Move to archive
        cur.execute("SELECT id, source, destination, availability, client_lat, client_lng FROM rides WHERE id = %s", (ride_id,))
        ride = cur.fetchone()
        if ride:
            cur.execute(
                "INSERT INTO rides_archive (id, source, destination, availability, client_lat, client_lng) VALUES (%s, %s, %s, %s, %s, %s)",
                (ride[0], ride[1], ride[2], new_status, ride[4], ride[5])
            )
            cur.execute("DELETE FROM rides WHERE id = %s", (ride_id,))
    else:
        # Just update availability
        cur.execute("UPDATE rides SET availability = %s WHERE id = %s", (new_status, ride_id))

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Ride status updated", "ride_id": ride_id, "new_status": new_status})

if __name__ == '__main__':
    app.run(debug=True)
