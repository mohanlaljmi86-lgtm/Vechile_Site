
import uuid
from datetime import date, datetime

import pandas as pd
import streamlit as st

from database import (
    initialize_database, load_vehicles, save_vehicle, delete_vehicle,
    save_trip, load_trips, delete_trip, clear_trips,
    save_maintenance, load_maintenance, delete_maintenance
)

from calculator import (
    calculate_trip, calculate_budget_distance,
    compare_vehicle_costs
)

from analytics import monthly_expense_chart, vehicle_cost_chart

from reports import trips_to_csv, trips_to_excel, trip_pdf


st.set_page_config(
    page_title="VehicleSaathi",
    page_icon="🚗",
    layout="wide"
)


st.markdown("""
<style>
.stApp {
    background: #f4f7fb;
}

[data-testid="stSidebar"] {
    background: #101827;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

div[data-testid="stMetric"] {
    background: white;
    padding: 14px;
    border-radius: 12px;
    border: 1px solid #e6eaf0;
}

.stButton button {
    border-radius: 9px;
    font-weight: 600;
}

.block-container {
    padding-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)


def inr(value):
    return f"₹{float(value):,.2f}"


def db_call(function, *args, **kwargs):
    try:
        return function(*args, **kwargs), None
    except Exception as exc:
        return None, str(exc)


if "owner_id" not in st.session_state:
    st.session_state.owner_id = str(uuid.uuid4())

if "last_trip_result" not in st.session_state:
    st.session_state.last_trip_result = None


st.sidebar.title("🚗 VehicleSaathi")
st.sidebar.caption("Smart Vehicle Fuel & Travel Cost Assistant")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Fuel Calculator",
        "Vehicle Database",
        "Vehicle Comparison",
        "Budget Planner",
        "Trip History",
        "Maintenance Tracker",
        "Reports",
        "About"
    ]
)


try:
    initialize_database()
    vehicles = load_vehicles()
    db_error = None

except Exception as exc:
    vehicles = pd.DataFrame()
    db_error = str(exc)


if db_error:
    st.sidebar.error("Database disconnected")
else:
    st.sidebar.success("Database connected")


# =====================================================
# DASHBOARD
# =====================================================

if page == "Dashboard":

    st.title("🚗 VehicleSaathi")
    st.caption(
        "Plan your journey. Estimate your fuel. Control your travel cost."
    )

    trips, error = db_call(
        load_trips,
        st.session_state.owner_id
    )

    trips = trips if trips is not None else pd.DataFrame()

    maintenance, _ = db_call(
        load_maintenance,
        st.session_state.owner_id
    )

    maintenance = (
        maintenance
        if maintenance is not None
        else pd.DataFrame()
    )

    total_distance = (
        float(trips["distance_km"].sum())
        if not trips.empty else 0
    )

    total_spend = (
        float(trips["total_cost"].sum())
        if not trips.empty else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Vehicle Records", len(vehicles))
    c2.metric("Saved Trips", len(trips))
    c3.metric("Total Distance", f"{total_distance:,.1f} km")
    c4.metric("Recorded Trip Spend", inr(total_spend))

    if not trips.empty:
        st.subheader("Monthly Travel Expenses")
        st.pyplot(
            monthly_expense_chart(trips),
            use_container_width=True
        )

    st.subheader("Available Features")

    a, b, c = st.columns(3)

    a.info("⛽ Fuel and multi-stop trip calculator")
    b.info("⚖️ Compare vehicles and running costs")
    c.info("🛠️ Track maintenance and reminders")

    if db_error:
        st.warning(
            "Database is not connected. Configure PostgreSQL connection."
        )
        st.code(db_error)

    else:
        st.success("Supabase PostgreSQL is connected.")


# =====================================================
# FUEL CALCULATOR
# =====================================================

elif page == "Fuel Calculator":

    st.title("⛽ Fuel & Travel Cost Calculator")

    left, right = st.columns(2)

    with left:

        vehicle_type = st.selectbox(
            "Vehicle Type",
            ["Car", "Bike", "Scooter", "EV", "Other"]
        )

        if not vehicles.empty:
            subset = vehicles[
                vehicles["vehicle_type"] == vehicle_type
            ]
        else:
            subset = pd.DataFrame()

        labels = ["Enter manually"]

        if not subset.empty:
            labels += [
                f"{row.company} {row.model} "
                f"({int(row.model_year)}) - {row.fuel_type}"
                for row in subset.itertuples()
            ]

        selected = st.selectbox(
            "Select Company & Model",
            labels
        )

        vehicle_row = None

        if selected != "Enter manually":
            vehicle_row = subset.iloc[
                labels.index(selected) - 1
            ]

        fuel_options = [
            "Petrol",
            "Diesel",
            "CNG",
            "Electric"
        ]

        default_fuel = (
            str(vehicle_row["fuel_type"])
            if vehicle_row is not None
            else "Petrol"
        )

        fuel = st.selectbox(
            "Fuel / Energy Type",
            fuel_options,
            index=(
                fuel_options.index(default_fuel)
                if default_fuel in fuel_options else 0
            )
        )

        default_efficiency = (
            float(vehicle_row["mileage"])
            if vehicle_row is not None
            else (7.0 if fuel == "Electric" else 18.0)
        )

        if fuel == "Electric":
            efficiency_label = "Efficiency (km/kWh)"
            default_price = 8.0

        elif fuel == "CNG":
            efficiency_label = "Mileage (km/kg)"
            default_price = 80.0

        else:
            efficiency_label = "Mileage (km/litre)"
            default_price = 95.0

        efficiency = st.number_input(
            efficiency_label,
            min_value=0.1,
            max_value=1000.0,
            value=default_efficiency,
            step=0.5
        )

        price = st.number_input(
            "Fuel / Energy Price (₹ per unit)",
            min_value=0.0,
            value=default_price,
            step=1.0
        )

    with right:

        trip_name = st.text_input(
            "Trip Name",
            placeholder="Jawalamukhi to Dharamshala"
        )

        st.markdown("### Route Stops")

        stop_count = st.number_input(
            "Number of Route Legs",
            min_value=1,
            max_value=8,
            value=1,
            step=1
        )

        legs = []

        for i in range(int(stop_count)):

            col1, col2 = st.columns(2)

            with col1:
                origin = st.text_input(
                    f"Leg {i+1} From",
                    value="Start" if i == 0 else "",
                    key=f"origin_{i}"
                )

            with col2:
                destination = st.text_input(
                    f"Leg {i+1} To",
                    value="Destination" if i == 0 else "",
                    key=f"destination_{i}"
                )

            distance = st.number_input(
                f"Leg {i+1} Distance (KM)",
                min_value=0.1,
                value=50.0 if i == 0 else 10.0,
                key=f"distance_{i}"
            )

            legs.append({
                "origin": origin,
                "destination": destination,
                "distance": distance
            })

        round_trip = st.checkbox("Round Trip")

        passengers = st.number_input(
            "Number of Passengers",
            min_value=1,
            max_value=100,
            value=1
        )

        toll = st.number_input(
            "Toll Charges (₹)",
            min_value=0.0,
            value=0.0
        )

        parking = st.number_input(
            "Parking Charges (₹)",
            min_value=0.0,
            value=0.0
        )

        food = st.number_input(
            "Food / Other Expenses (₹)",
            min_value=0.0,
            value=0.0
        )

    if st.button(
        "Calculate Travel Cost",
        type="primary",
        use_container_width=True
    ):

        try:

            result = calculate_trip(
                sum(leg["distance"] for leg in legs),
                efficiency,
                price,
                passengers,
                round_trip,
                toll,
                parking,
                food
            )

            result.update({
                "trip_name": trip_name.strip() or "My Trip",
                "vehicle": selected,
                "vehicle_type": vehicle_type,
                "fuel_type": fuel,
                "route": " → ".join(
                    [leg["origin"] for leg in legs]
                    + [legs[-1]["destination"]]
                ),
                "created_at": datetime.now().isoformat(
                    timespec="seconds"
                )
            })

            st.session_state.last_trip_result = result

        except Exception as exc:
            st.error(str(exc))

    result = st.session_state.last_trip_result

    if result:

        st.divider()
        st.subheader("Your Estimated Trip Cost")

        m1, m2, m3, m4 = st.columns(4)

        m1.metric(
            "Total Distance",
            f'{result["total_distance"]:,.1f} km'
        )

        m2.metric(
            "Energy Required",
            f'{result["fuel_needed"]:,.2f} units'
        )

        m3.metric(
            "Fuel / Energy Cost",
            inr(result["fuel_cost"])
        )

        m4.metric(
            "Total Trip Cost",
            inr(result["total_cost"])
        )

        st.metric(
            "Cost Per Person",
            inr(result["per_person_cost"])
        )

        st.write(f'**Route:** {result["route"]}')
        st.write(f'**Vehicle:** {result["vehicle"]}')
        st.write(f'**Fuel:** {result["fuel_type"]}')

        if st.button(
            "Save This Trip to PostgreSQL",
            type="primary"
        ):

            payload = {
                "owner_id": st.session_state.owner_id,
                "trip_name": result["trip_name"],
                "vehicle": result["vehicle"],
                "vehicle_type": result["vehicle_type"],
                "fuel_type": result["fuel_type"],
                "route": result["route"],
                "distance_km": result["total_distance"],
                "fuel_needed": result["fuel_needed"],
                "fuel_cost": result["fuel_cost"],
                "toll": result["toll"],
                "parking": result["parking"],
                "extra_cost": result["extra_cost"],
                "total_cost": result["total_cost"],
                "per_person_cost": result["per_person_cost"],
                "passengers": passengers
            }

            _, error = db_call(save_trip, payload)

            if error:
                st.error(error)
            else:
                st.success("Trip saved successfully!")


# =====================================================
# VEHICLE DATABASE
# =====================================================

elif page == "Vehicle Database":

    st.title("🚘 Vehicle Database")

    if db_error:
        st.error(db_error)

    else:

        st.subheader("Vehicle Catalogue")

        if not vehicles.empty:

            col1, col2 = st.columns(2)

            types = (
                ["All"]
                + sorted(vehicles["vehicle_type"].dropna().unique())
            )

            companies = (
                ["All"]
                + sorted(vehicles["company"].dropna().unique())
            )

            selected_type = col1.selectbox(
                "Filter by Type",
                types
            )

            selected_company = col2.selectbox(
                "Filter by Company",
                companies
            )

            view = vehicles.copy()

            if selected_type != "All":
                view = view[
                    view["vehicle_type"] == selected_type
                ]

            if selected_company != "All":
                view = view[
                    view["company"] == selected_company
                ]

            st.dataframe(
                view.drop(columns=["id"], errors="ignore"),
                use_container_width=True,
                hide_index=True
            )

        st.divider()
        st.subheader("Add / Update Vehicle")

        with st.form("vehicle_form"):

            c1, c2, c3 = st.columns(3)

            vtype = c1.selectbox(
                "Vehicle Type",
                ["Car", "Bike", "Scooter", "EV", "Other"]
            )

            company = c2.text_input("Company")
            model = c3.text_input("Model")

            year = c1.number_input(
                "Model Year",
                min_value=1980,
                max_value=2100,
                value=2025
            )

            fuel = c2.selectbox(
                "Fuel Type",
                ["Petrol", "Diesel", "CNG", "Electric"]
            )

            mileage = c3.number_input(
                "Mileage / Efficiency",
                min_value=0.1,
                value=18.0
            )

            submitted = st.form_submit_button("Save Vehicle")

            if submitted:

                if not company.strip() or not model.strip():
                    st.error("Company and model are required.")

                else:

                    _, error = db_call(
                        save_vehicle,
                        {
                            "vehicle_type": vtype,
                            "company": company.strip(),
                            "model": model.strip(),
                            "model_year": int(year),
                            "fuel_type": fuel,
                            "mileage": float(mileage)
                        }
                    )

                    if error:
                        st.error(error)

                    else:
                        st.success("Vehicle saved successfully.")
                        st.cache_data.clear()
                        st.rerun()

        if not vehicles.empty:

            st.subheader("Delete Vehicle")

            vehicle_choices = {
                f"{row.company} {row.model} "
                f"({int(row.model_year)}) - {row.fuel_type}": int(row.id)
                for row in vehicles.itertuples()
            }

            selected_vehicle = st.selectbox(
                "Choose Vehicle",
                list(vehicle_choices.keys())
            )

            if st.button("Delete Selected Vehicle"):

                _, error = db_call(
                    delete_vehicle,
                    vehicle_choices[selected_vehicle]
                )

                if error:
                    st.error(error)
                else:
                    st.success("Vehicle deleted.")
                    st.rerun()

        st.caption(
            "Mileage figures are estimates. Verify the exact variant."
        )


# =====================================================
# VEHICLE COMPARISON
# =====================================================

elif page == "Vehicle Comparison":

    st.title("⚖️ Compare Vehicles")

    if vehicles.empty:

        st.info("Add vehicles or connect PostgreSQL first.")

    else:

        options = [
            f"{row.company} {row.model} "
            f"({int(row.model_year)}) - {row.fuel_type}"
            for row in vehicles.itertuples()
        ]

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Vehicle A")

            vehicle_a = st.selectbox(
                "Vehicle A",
                options,
                key="vehicle_a"
            )

            row_a = vehicles.iloc[options.index(vehicle_a)]

            mileage_a = st.number_input(
                "Vehicle A Mileage",
                min_value=0.1,
                value=float(row_a.mileage),
                key="mileage_a"
            )

            price_a = st.number_input(
                "Vehicle A Fuel Price",
                min_value=0.0,
                value=95.0,
                key="price_a"
            )

        with col2:

            st.subheader("Vehicle B")

            vehicle_b = st.selectbox(
                "Vehicle B",
                options,
                index=min(1, len(options)-1),
                key="vehicle_b"
            )

            row_b = vehicles.iloc[options.index(vehicle_b)]

            mileage_b = st.number_input(
                "Vehicle B Mileage",
                min_value=0.1,
                value=float(row_b.mileage),
                key="mileage_b"
            )

            price_b = st.number_input(
                "Vehicle B Fuel Price",
                min_value=0.0,
                value=95.0,
                key="price_b"
            )

        distance = st.number_input(
            "Distance (KM)",
            min_value=1.0,
            value=100.0
        )

        if st.button("Compare Vehicles", type="primary"):

            comparison = compare_vehicle_costs(
                distance,
                mileage_a,
                price_a,
                mileage_b,
                price_b
            )

            a, b = st.columns(2)

            a.metric(
                "Vehicle A Cost",
                inr(comparison["cost_a"])
            )

            b.metric(
                "Vehicle B Cost",
                inr(comparison["cost_b"])
            )

            st.success(comparison["message"])

            st.pyplot(
                vehicle_cost_chart(
                    comparison["cost_a"],
                    comparison["cost_b"],
                    vehicle_a,
                    vehicle_b
                ),
                use_container_width=True
            )


# =====================================================
# BUDGET PLANNER
# =====================================================

elif page == "Budget Planner":

    st.title("💰 Travel Budget Planner")

    budget = st.number_input(
        "Your Budget (₹)",
        min_value=0.0,
        value=500.0
    )

    efficiency = st.number_input(
        "Mileage / Efficiency",
        min_value=0.1,
        value=20.0
    )

    price = st.number_input(
        "Fuel / Energy Price",
        min_value=0.1,
        value=95.0
    )

    other = st.number_input(
        "Other Expenses (₹)",
        min_value=0.0,
        value=0.0
    )

    if st.button("Calculate Possible Distance", type="primary"):

        possible = calculate_budget_distance(
            budget,
            efficiency,
            price,
            other
        )

        st.metric(
            "Estimated Distance",
            f"{possible:,.1f} KM"
        )


# =====================================================
# TRIP HISTORY
# =====================================================

elif page == "Trip History":

    st.title("📚 My Trip History")

    trips, error = db_call(
        load_trips,
        st.session_state.owner_id
    )

    if error:
        st.error(error)

    elif trips.empty:

        st.info("No saved trips yet.")

    else:

        st.dataframe(
            trips.drop(columns=["owner_id"], errors="ignore"),
            use_container_width=True,
            hide_index=True
        )

        st.pyplot(
            monthly_expense_chart(trips),
            use_container_width=True
        )

        selected_trip = st.selectbox(
            "Select Trip to Delete",
            trips["id"].astype(int).tolist()
        )

        if st.button("Delete Selected Trip"):

            _, error = db_call(
                delete_trip,
                int(selected_trip),
                st.session_state.owner_id
            )

            if error:
                st.error(error)
            else:
                st.success("Trip deleted.")
                st.rerun()

        if st.button("Delete All My Trips"):

            _, error = db_call(
                clear_trips,
                st.session_state.owner_id
            )

            if error:
                st.error(error)
            else:
                st.success("Trips deleted.")
                st.rerun()

        st.download_button(
            "Download Trip History CSV",
            trips_to_csv(trips),
            "vehiclesaathi_trips.csv",
            "text/csv"
        )

        excel = trips_to_excel(trips)

        if excel:
            st.download_button(
                "Download Trip History Excel",
                excel,
                "vehiclesaathi_trips.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        pdf = trip_pdf(trips)

        if pdf:
            st.download_button(
                "Download Trip History PDF",
                pdf,
                "vehiclesaathi_trips.pdf",
                "application/pdf"
            )


# =====================================================
# MAINTENANCE TRACKER
# =====================================================

elif page == "Maintenance Tracker":

    st.title("🛠️ Vehicle Maintenance Tracker")

    with st.form("maintenance_form"):

        col1, col2 = st.columns(2)

        vehicle_name = col1.text_input(
            "Vehicle Name / Registration Label"
        )

        service_type = col2.selectbox(
            "Maintenance Type",
            [
                "Regular Service",
                "Engine Oil",
                "Tyre Replacement",
                "Battery",
                "Insurance",
                "PUC",
                "Repair",
                "Other"
            ]
        )

        service_date = col1.date_input(
            "Service / Due Date",
            value=date.today()
        )

        cost = col2.number_input(
            "Expense (₹)",
            min_value=0.0,
            value=0.0
        )

        notes = st.text_area("Notes")

        submitted = st.form_submit_button(
            "Save Maintenance Record"
        )

        if submitted:

            if not vehicle_name.strip():

                st.error("Enter a vehicle name.")

            else:

                _, error = db_call(
                    save_maintenance,
                    {
                        "owner_id": st.session_state.owner_id,
                        "vehicle_name": vehicle_name.strip(),
                        "service_type": service_type,
                        "service_date": service_date.isoformat(),
                        "cost": cost,
                        "notes": notes
                    }
                )

                if error:
                    st.error(error)
                else:
                    st.success("Maintenance record saved.")
                    st.rerun()

    records, error = db_call(
        load_maintenance,
        st.session_state.owner_id
    )

    if error:
        st.error(error)

    elif records.empty:

        st.info("No maintenance records yet.")

    else:

        records["service_date"] = pd.to_datetime(
            records["service_date"]
        ).dt.date

        st.dataframe(
            records.drop(columns=["owner_id"], errors="ignore"),
            use_container_width=True,
            hide_index=True
        )

        overdue = records[
            records["service_date"] <= date.today()
        ]

        if not overdue.empty:
            st.warning(
                f"{len(overdue)} maintenance record(s) are due or overdue."
            )

        record_id = st.selectbox(
            "Select Record to Delete",
            records["id"].astype(int).tolist()
        )

        if st.button("Delete Maintenance Record"):

            _, error = db_call(
                delete_maintenance,
                int(record_id),
                st.session_state.owner_id
            )

            if error:
                st.error(error)
            else:
                st.success("Record deleted.")
                st.rerun()


# =====================================================
# REPORTS
# =====================================================

elif page == "Reports":

    st.title("📄 Reports")

    trips, error = db_call(
        load_trips,
        st.session_state.owner_id
    )

    if error:
        st.error(error)

    elif trips.empty:

        st.info("Save trips to generate reports.")

    else:

        st.download_button(
            "Download CSV",
            trips_to_csv(trips),
            "vehiclesaathi_report.csv",
            "text/csv"
        )

        excel = trips_to_excel(trips)

        if excel:
            st.download_button(
                "Download Excel",
                excel,
                "vehiclesaathi_report.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        pdf = trip_pdf(trips)

        if pdf:
            st.download_button(
                "Download PDF",
                pdf,
                "vehiclesaathi_report.pdf",
                "application/pdf"
            )


# =====================================================
# ABOUT
# =====================================================

else:

    st.title("About VehicleSaathi")

    st.write("""
    VehicleSaathi is a vehicle fuel, travel cost and maintenance assistant.

    Features:

    - Fuel and EV energy estimation
    - Multi-stop route calculator
    - Round-trip calculation
    - Toll and parking expenses
    - Per-person cost calculation
    - Vehicle catalogue management
    - Vehicle comparison
    - Budget planner
    - PostgreSQL trip history
    - Maintenance tracker
    - CSV, Excel and PDF reports
    - Monthly expense analytics

    Technology Stack:

    Python, NumPy, Pandas, Matplotlib,
    Streamlit and Supabase PostgreSQL.
    """)

    st.warning(
        "This version does not include user login. "
        "Session-based trip separation is not permanent user identity."
    )
