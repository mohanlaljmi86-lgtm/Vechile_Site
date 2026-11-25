
-- =========================================
-- VEHICLESAATHI DATABASE
-- Supabase PostgreSQL
-- =========================================

CREATE TABLE IF NOT EXISTS public.vehicles (
    id BIGSERIAL PRIMARY KEY,
    vehicle_type TEXT NOT NULL
        CHECK (vehicle_type IN (
            'Car', 'Bike', 'Scooter', 'EV', 'Other'
        )),
    company TEXT NOT NULL,
    model TEXT NOT NULL,
    model_year INTEGER NOT NULL
        CHECK (model_year BETWEEN 1980 AND 2100),
    fuel_type TEXT NOT NULL
        CHECK (fuel_type IN (
            'Petrol', 'Diesel', 'CNG', 'Electric'
        )),
    mileage NUMERIC(10,2) NOT NULL
        CHECK (mileage > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(company, model, model_year, fuel_type)
);


CREATE TABLE IF NOT EXISTS public.trips (
    id BIGSERIAL PRIMARY KEY,
    owner_id TEXT NOT NULL,
    trip_name TEXT NOT NULL,
    vehicle TEXT,
    vehicle_type TEXT,
    fuel_type TEXT,
    route TEXT,
    distance_km NUMERIC(12,2) NOT NULL DEFAULT 0,
    fuel_needed NUMERIC(12,3) NOT NULL DEFAULT 0,
    fuel_cost NUMERIC(12,2) NOT NULL DEFAULT 0,
    toll NUMERIC(12,2) NOT NULL DEFAULT 0,
    parking NUMERIC(12,2) NOT NULL DEFAULT 0,
    extra_cost NUMERIC(12,2) NOT NULL DEFAULT 0,
    total_cost NUMERIC(12,2) NOT NULL DEFAULT 0,
    per_person_cost NUMERIC(12,2) NOT NULL DEFAULT 0,
    passengers INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS public.maintenance_records (
    id BIGSERIAL PRIMARY KEY,
    owner_id TEXT NOT NULL,
    vehicle_name TEXT NOT NULL,
    service_type TEXT NOT NULL,
    service_date DATE NOT NULL,
    cost NUMERIC(12,2) NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- =========================================
-- INDEXES
-- =========================================

CREATE INDEX IF NOT EXISTS idx_trips_owner_created
ON public.trips(owner_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_maintenance_owner_date
ON public.maintenance_records(owner_id, service_date DESC);


-- =========================================
-- STARTER VEHICLE DATA
-- Sample estimates only
-- =========================================

INSERT INTO public.vehicles
(vehicle_type, company, model, model_year, fuel_type, mileage)
VALUES

('Car', 'Maruti Suzuki', 'Swift', 2024, 'Petrol', 20.0),
('Car', 'Maruti Suzuki', 'Baleno', 2024, 'Petrol', 22.0),
('Car', 'Hyundai', 'i20', 2024, 'Petrol', 18.0),
('Car', 'Tata', 'Nexon', 2024, 'Petrol', 17.0),

('Bike', 'Hero', 'Splendor Plus', 2024, 'Petrol', 60.0),
('Bike', 'Honda', 'Shine', 2024, 'Petrol', 55.0),
('Bike', 'TVS', 'Apache RTR 160', 2024, 'Petrol', 45.0),

('Scooter', 'Honda', 'Activa 6G', 2024, 'Petrol', 47.0),
('Scooter', 'TVS', 'Jupiter', 2024, 'Petrol', 48.0),

('EV', 'Tata', 'Nexon EV', 2024, 'Electric', 7.0),
('EV', 'MG', 'Comet EV', 2024, 'Electric', 7.5)

ON CONFLICT (
    company,
    model,
    model_year,
    fuel_type
)
DO NOTHING;


-- Verify tables and records
SELECT * FROM public.vehicles ORDER BY company, model;

SELECT COUNT(*) AS total_vehicles
FROM public.vehicles;

SELECT COUNT(*) AS total_trips
FROM public.trips;

SELECT COUNT(*) AS total_maintenance_records
FROM public.maintenance_records;
