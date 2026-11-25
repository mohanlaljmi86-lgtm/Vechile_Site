# VehicleSaathi

Smart Vehicle Fuel & Travel Cost Assistant built with Python, NumPy, Pandas, Matplotlib, Streamlit and Supabase PostgreSQL.

## Features

- Fuel and travel cost calculator
- Car, Bike, Scooter, EV and other vehicle categories
- Company, model, year and fuel type selection
- Editable mileage / efficiency
- One-way and round-trip calculations
- Toll, parking and other expense inputs
- Per-person trip cost
- Vehicle catalogue stored in PostgreSQL
- Two-vehicle cost comparison
- Fuel budget distance planner
- Session-only trip history and CSV export
- Public access; no user login required

## 1. Create Supabase PostgreSQL database

1. Create a Supabase project.
2. Open **Project Settings -> Database -> Connection string**.
3. Copy a PostgreSQL connection string. For hosted Streamlit, use the Session Pooler connection string if your network requires it.
4. Add `sslmode=require` to the connection string.
5. Keep the database password private.

The app creates the `vehicles` table and inserts starter records on its first successful connection.

## 2. Configure secrets locally

Create `.streamlit/secrets.toml` and add:

```toml
[postgres]
url = "YOUR_POSTGRESQL_CONNECTION_STRING"
```

Do not upload `secrets.toml` to GitHub.

## 3. Install and run locally

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
streamlit run app.py
```

## 4. Deploy on Streamlit Community Cloud

1. Push the project folder to a GitHub repository.
2. Open Streamlit Community Cloud and create a new app.
3. Select the repository, branch and `app.py`.
4. Open the app's **Settings -> Secrets**.
5. Paste:

```toml
[postgres]
url = "YOUR_POSTGRESQL_CONNECTION_STRING"
```

6. Deploy the app.

## Database and public access safety

- The app is public and does not require user login.
- The PostgreSQL password must only be stored in Streamlit Secrets.
- Never place database credentials in Python source code or a public repository.
- This starter app only reads the vehicle catalogue after initialization. It does not expose public insert, update or delete controls.
- Trip history is held in the visitor's Streamlit session and is not stored in a shared table.
- For a production public service, use a restricted database role and review network access, backups, quotas and abuse controls.

## Notes

- Starter mileage values are indicative examples, not guaranteed manufacturer-certified or real-world values.
- Users can change mileage and fuel price before calculating.
- Automatic route distance, live fuel prices, PDF generation and user accounts are not included in this first version.
- EV efficiency is entered in km/kWh and electricity price in rupees/kWh. CNG efficiency is km/kg and price is rupees/kg.
