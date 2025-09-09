from flask import Flask, render_template_string

app = Flask(__name__)
BASE_URL = "http://127.0.0.1:5000"

# Home page
@app.route('/')
def home():
    html = """
    <h1>🚖 Mini Uber Client</h1>
    <button onclick="location.href='/user'">User Client</button>
    <button onclick="location.href='/driver'">Driver Client</button>
    """
    return render_template_string(html)

# User view
@app.route('/user')
def user_view():
    html = """
    <h2>🚖 User Menu</h2>
    <button onclick="location.href='/'">Switch to Home</button>
    <button onclick="location.href='/driver'">Switch to Driver Client</button>
    <br><br>
    <input type="text" id="source" placeholder="Source">
    <input type="text" id="destination" placeholder="Destination">
    <input type="number" id="lat" placeholder="Lat" step="0.000001">
    <input type="number" id="lng" placeholder="Lng" step="0.000001">
    <button onclick="requestRide()">Request Ride</button>
    <button onclick="loadRides()">Refresh Table</button>

    <h2>Active Rides</h2>
    <table id="ridesTable" border="1" cellpadding="5"></table>

    <script>
        const BASE_URL = "{{ BASE_URL }}";
        const STATUS_COLORS = {
            "pending": "yellow",
            "accepted": "lightgreen",
            "completed": "green",
            "rejected": "red"
        };

        async function requestRide() {
            const source = document.getElementById("source").value;
            const destination = document.getElementById("destination").value;
            const lat = parseFloat(document.getElementById("lat").value);
            const lng = parseFloat(document.getElementById("lng").value);

            if(!source || !destination || isNaN(lat) || isNaN(lng)){
                alert("Please fill all fields!");
                return;
            }

            try {
                const res = await fetch(`${BASE_URL}/request_ride`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ source, destination, client_lat: lat, client_lng: lng })
                });
                const data = await res.json();
                console.log(data.message);
                setTimeout(loadRides, 200); // reload table after insert
            } catch(err) {
                console.error("Error requesting ride:", err);
            }
        }

        async function loadRides() {
            try {
                const response = await fetch(`${BASE_URL}/get_rides`);
                const rides = await response.json();
                const table = document.getElementById("ridesTable");
                table.innerHTML = `<tr>
                    <th>ID</th><th>Source</th><th>Destination</th><th>Status</th><th>Lat</th><th>Lng</th>
                </tr>`;
                rides.forEach(r => {
                    const row = document.createElement("tr");
                    row.innerHTML = `<td>${r.id}</td>
                                     <td>${r.source}</td>
                                     <td>${r.destination}</td>
                                     <td style="background-color: ${STATUS_COLORS[r.availability] || 'white'}">${r.availability}</td>
                                     <td>${r.lat}</td>
                                     <td>${r.lng}</td>`;
                    table.appendChild(row);
                });
            } catch(err) {
                console.error("Error loading rides:", err);
            }
        }

        // Auto-refresh every 3 seconds
        setInterval(loadRides, 3000);
        window.onload = loadRides;
    </script>
    """
    return render_template_string(html, BASE_URL=BASE_URL)


# Driver view
@app.route('/driver')
def driver_view():
    html = """
    <h2>🚕 Driver Menu</h2>
    <button onclick="location.href='/'">Switch to Home</button>
    <button onclick="location.href='/user'">Switch to User Client</button>
    <br><br>
    <p>Drivers can see rides below and Accept / Complete / Reject them.</p>
    <button onclick="loadRides()">Refresh Table</button>

    <h2>All Rides</h2>
    <table id="ridesTable" border="1" cellpadding="5"></table>

    <script>
        const BASE_URL = "{{ BASE_URL }}";
        const STATUS_COLORS = {
            "pending": "yellow",
            "accepted": "lightgreen",
            "completed": "green",
            "rejected": "red"
        };

        async function loadRides() {
            try {
                const response = await fetch(`${BASE_URL}/get_rides`);
                const rides = await response.json();
                const table = document.getElementById("ridesTable");
                table.innerHTML = `<tr>
                    <th>ID</th><th>Source</th><th>Destination</th><th>Status</th><th>Lat</th><th>Lng</th><th>Actions</th>
                </tr>`;
                rides.forEach(r => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${r.id}</td>
                        <td>${r.source}</td>
                        <td>${r.destination}</td>
                        <td style="background-color: ${STATUS_COLORS[r.availability] || 'white'}">${r.availability}</td>
                        <td>${r.lat}</td>
                        <td>${r.lng}</td>
                        <td>
                            <button onclick="updateRide(${r.id}, 'accepted')">Accept</button>
                            <button onclick="updateRide(${r.id}, 'completed')">Complete</button>
                            <button onclick="updateRide(${r.id}, 'rejected')">Reject</button>
                        </td>
                    `;
                    table.appendChild(row);
                });
            } catch(err) {
                console.error("Error loading rides:", err);
            }
        }

        async function updateRide(rideId, status) {
            try {
                const res = await fetch(`${BASE_URL}/update_ride_status/${rideId}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ availability: status })
                });
                const data = await res.json();
                console.log(data.message);
                setTimeout(loadRides, 200);
            } catch(err) {
                console.error("Error updating ride:", err);
            }
        }

        // Auto-refresh every 3 seconds
        setInterval(loadRides, 3000);
        window.onload = loadRides;
    </script>
    """
    return render_template_string(html, BASE_URL=BASE_URL)


if __name__ == '__main__':
    app.run(port=5500, debug=True)
