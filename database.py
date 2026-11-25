
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd


def get_connection():
    try:
        url = st.secrets["postgres"]["url"]
    except Exception as exc:
        raise RuntimeError(
            "Add [postgres] url to .streamlit/secrets.toml "
            "or Streamlit Cloud Secrets."
        ) from exc

    if not url.startswith(("postgres://", "postgresql://")):
        raise RuntimeError(
            "Invalid PostgreSQL URL. Use the connection URI from Supabase."
        )

    return psycopg2.connect(
        url,
        connect_timeout=15,
        sslmode="require"
    )


def execute(query, params=None, fetch=False):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or ())
            return cur.fetchall() if fetch else None


def initialize_database():
    execute("SELECT 1")


def load_vehicles():
    rows = execute("""
        SELECT id, vehicle_type, company, model,
               model_year, fuel_type, mileage
        FROM vehicles
        ORDER BY company, model
    """, fetch=True)

    return pd.DataFrame(rows)


def save_vehicle(v):
    execute("""
        INSERT INTO vehicles
        (vehicle_type, company, model, model_year, fuel_type, mileage)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (company, model, model_year, fuel_type)
        DO UPDATE SET
            vehicle_type = EXCLUDED.vehicle_type,
            mileage = EXCLUDED.mileage
    """, (
        v["vehicle_type"],
        v["company"],
        v["model"],
        v["model_year"],
        v["fuel_type"],
        v["mileage"]
    ))


def delete_vehicle(vehicle_id):
    execute(
        "DELETE FROM vehicles WHERE id = %s",
        (vehicle_id,)
    )


def save_trip(t):
    execute("""
        INSERT INTO trips (
            owner_id, trip_name, vehicle, vehicle_type,
            fuel_type, route, distance_km, fuel_needed,
            fuel_cost, toll, parking, extra_cost,
            total_cost, per_person_cost, passengers
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s
        )
    """, (
        t["owner_id"],
        t["trip_name"],
        t["vehicle"],
        t["vehicle_type"],
        t["fuel_type"],
        t["route"],
        t["distance_km"],
        t["fuel_needed"],
        t["fuel_cost"],
        t["toll"],
        t["parking"],
        t["extra_cost"],
        t["total_cost"],
        t["per_person_cost"],
        t["passengers"]
    ))


def load_trips(owner_id):
    rows = execute("""
        SELECT *
        FROM trips
        WHERE owner_id = %s
        ORDER BY created_at DESC
    """, (owner_id,), fetch=True)

    return pd.DataFrame(rows)


def delete_trip(trip_id, owner_id):
    execute("""
        DELETE FROM trips
        WHERE id = %s AND owner_id = %s
    """, (trip_id, owner_id))


def clear_trips(owner_id):
    execute("""
        DELETE FROM trips
        WHERE owner_id = %s
    """, (owner_id,))


def save_maintenance(m):
    execute("""
        INSERT INTO maintenance_records (
            owner_id, vehicle_name, service_type,
            service_date, cost, notes
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        m["owner_id"],
        m["vehicle_name"],
        m["service_type"],
        m["service_date"],
        m["cost"],
        m["notes"]
    ))


def load_maintenance(owner_id):
    rows = execute("""
        SELECT *
        FROM maintenance_records
        WHERE owner_id = %s
        ORDER BY service_date DESC
    """, (owner_id,), fetch=True)

    return pd.DataFrame(rows)


def delete_maintenance(record_id, owner_id):
    execute("""
        DELETE FROM maintenance_records
        WHERE id = %s AND owner_id = %s
    """, (record_id, owner_id))
