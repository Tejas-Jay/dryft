from flask import Flask, request, jsonify, render_template_string
import psycopg2

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        dbname="rides_db",
        user="postgres",          
        password="kashpatel", 
        host="localhost",
        port="5432"
    )
    return conn

# ---- Frontend Page ----
@app.route('/')
def home():
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ride Request</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 30px; }
            h2 { color: #333; }
            form { margin-bottom: 20px; }
            input, button { padding: 8px; margin: 5px; }
            #rides { margin-top: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        </style>
    </head>
    <body>
        <h2>Request a Ride</h2>
        <form id="rideForm">
            <input type="text" id="source" placeholder="Enter Source" required>
            <input type="text" id="destination" placeholder="Enter Destination" required>
            <button type="submit">Request Ride</button>
        </form>

        <h2>All Rides</h2>
        <button onclick="loadRides()">Refresh Rides</button>
        <div id="rides"></div>

        <script>
            document.getElementById('rideForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                let source = document.getElementById('source').value;
                let destination = document.getElementById('destination').value;

                let response = await fetch('/request_ride', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ source: source, destination: destination })
                });

                let result = await response.json();
                alert(result.message);
                loadRides();
            });

            async function loadRides() {
                let response = await fetch('/rides');
                let rides = await response.json();
                let html = "<table><tr><th>ID</th><th>Source</th><th>Destination</th><th>Availability</th></tr>";
                rides.forEach(r => {
                    html += `<tr><td>${r.id}</td><td>${r.source}</td><td>${r.destination}</td><td>${r.availability}</td></tr>`;
                });
                html += "</table>";
                document.getElementById('rides').innerHTML = html;
            }

            // load rides automatically on page load
            loadRides();
        </script>
    </body>
    </html>
    """
    return render_template_string(html_code)

# ---- API Endpoints ----
@app.route('/request_ride', methods=['POST'])
def request_ride():
    data = request.get_json()
    source = data.get('source')
    destination = data.get('destination')

    if not source or not destination:
        return jsonify({"error": "Source and destination are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO rides (source, destination) VALUES (%s, %s) RETURNING id, source, destination, availability;",
        (source, destination)
    )
    new_ride = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "message": "Ride request stored successfully",
        "ride": {
            "id": new_ride[0],
            "source": new_ride[1],
            "destination": new_ride[2],
            "availability": new_ride[3]
        }
    }), 201

@app.route('/rides', methods=['GET'])
def get_rides():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, source, destination, availability FROM rides;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    rides = []
    for row in rows:
        rides.append({
            "id": row[0],
            "source": row[1],
            "destination": row[2],
            "availability": row[3]
        })

    return jsonify(rides)

if __name__ == '__main__':
    app.run(debug=True)
