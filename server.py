from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
from psycopg2 import sql

app = FastAPI()

# ---- DATABASE CONFIG ----
USE_DB = True
conn = None
cur = None

try:
    conn = psycopg2.connect(
        dbname="rides_db",       # <-- Change to your DB name
        user="postgres",         # <-- Change to your DB user
        password="kashpatel", # <-- Change to your DB password
        host="localhost",        # <-- Change if DB not local
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ride_requests (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            source_location TEXT NOT NULL,
            dest_location TEXT NOT NULL
        );
    """)
    conn.commit()
    print("✅ Connected to Postgres and ensured table exists.")
except Exception as e:
    print("⚠️ Could not connect to Postgres. Falling back to print mode:", e)
    USE_DB = False

# ---- REQUEST MODEL ----
class RideRequest(BaseModel):
    user_id: int
    source_location: str
    dest_location: str

# ---- API ROUTE ----
@app.post("/request-ride/")
def request_ride(ride: RideRequest):
    if USE_DB and conn:
        try:
            cur.execute(
                sql.SQL("INSERT INTO ride_requests (user_id, source_location, dest_location) VALUES (%s, %s, %s)"),
                (ride.user_id, ride.source_location, ride.dest_location)
            )
            conn.commit()
            return {"status": "success", "message": "Ride stored in Postgres", "data": ride.dict()}
        except Exception as e:
            return {"status": "error", "message": f"Failed to store in Postgres: {e}", "data": ride.dict()}
    else:
        print("We will store this data in Postgres now →", ride.dict())
        return {"status": "success", "message": "Simulated Postgres storage", "data": ride.dict()}