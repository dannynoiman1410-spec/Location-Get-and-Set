import streamlit as st
import requests
import pandas as pd
from pathlib import Path

API_KEY = "ZjFiMzlhOTUtOTI0NC00N2U2LWI5YjAtZjQxZDQwNGUwZWQxOk9YZlc1Z1NJRVBrckRxTWxMWGRJdUJRYnVvcnp2NWhybUZFRzA5aVd0WUE="
OWNER_ID = "406173299960"

st.set_page_config(page_title="Wiliot Location Manager", layout="centered")

st.title("Wiliot Location Manager")
st.write("Create a new location, refresh the location list, and export results to Excel.")

if "bearer_token" not in st.session_state:
    st.session_state.bearer_token = None
if "locations_data" not in st.session_state:
    st.session_state.locations_data = []
if "status" not in st.session_state:
    st.session_state.status = "Ready"

col1, col2 = st.columns(2)
with col1:
    location_id = st.text_input("Location ID", value="Location1")
    location_name = st.text_input("Name", value="My Location")
    city = st.text_input("City", value="Tel Aviv")
with col2:
    country = st.text_input("Country", value="Israel")
    address = st.text_input("Address", value="Main Street")
    st.write("\n")

status_placeholder = st.empty()
status_placeholder.info(st.session_state.status)

@st.cache_data(show_spinner=False)
def get_bearer_token():
    auth_url = "https://api.wiliot.com/v1/auth/token/api"
    headers = {
        "Content-Type": "application/json",
        "Authorization": API_KEY,
    }
    auth_resp = requests.post(auth_url, headers=headers, timeout=30)
    auth_resp.raise_for_status()
    auth_data = auth_resp.json()
    bearer_token = auth_data.get("access_token")
    if not bearer_token:
        raise RuntimeError("No access token received from authentication.")
    return bearer_token


def create_location():
    try:
        st.session_state.status = "Authenticating..."
        status_placeholder.info(st.session_state.status)
        if not st.session_state.bearer_token:
            st.session_state.bearer_token = get_bearer_token()

        st.session_state.status = "Creating location..."
        status_placeholder.info(st.session_state.status)

        create_url = f"https://api.wiliot.com/v1/traceability/owner/{OWNER_ID}/location"
        location_payload = {
            "id": location_id,
            "name": location_name,
            "planStrategy": "ZONE_BASED",
            "locationType": "SITE",
            "lat": "32.22",
            "lng": "32.22",
            "address": address,
            "country": country,
            "city": city,
            "isSoftAssetCreate": True,
        }

        headers = {
            "Authorization": f"Bearer {st.session_state.bearer_token}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }

        post_resp = requests.post(create_url, json=location_payload, headers=headers, timeout=30)
        post_resp.raise_for_status()

        st.session_state.status = "Location created successfully!"
        status_placeholder.success(st.session_state.status)
        st.experimental_rerun()
    except Exception as e:
        st.session_state.status = f"Error: {str(e)}"
        status_placeholder.error(st.session_state.status)


def fetch_locations():
    try:
        st.session_state.status = "Authenticating..."
        status_placeholder.info(st.session_state.status)
        if not st.session_state.bearer_token:
            st.session_state.bearer_token = get_bearer_token()

        st.session_state.status = "Fetching locations..."
        status_placeholder.info(st.session_state.status)

        list_url = f"https://api.wiliot.com/v1/traceability/owner/{OWNER_ID}/location"
        headers = {
            "Authorization": f"Bearer {st.session_state.bearer_token}",
            "accept": "application/json",
        }

        list_resp = requests.get(list_url, headers=headers, timeout=30)
        list_resp.raise_for_status()

        st.session_state.locations_data = list_resp.json().get("data", [])
        st.session_state.status = f"Found {len(st.session_state.locations_data)} locations"
        status_placeholder.success(st.session_state.status)
    except Exception as e:
        st.session_state.status = f"Error: {str(e)}"
        status_placeholder.error(st.session_state.status)


def export_to_excel():
    try:
        if not st.session_state.locations_data:
            st.warning("No locations to export. Please refresh locations first.")
            return

        df = pd.DataFrame(st.session_state.locations_data)
        preferred = ["id", "name", "locationType", "city", "country", "address", "planStrategy"]
        cols = [c for c in preferred if c in df.columns]

        save_path = Path(r"C:\Users\danny\OneDrive\Desktop") / "locations.xlsx"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        df[cols].to_excel(save_path, index=False, sheet_name="Locations")

        st.success(f"Exported to {save_path}")
        with open(save_path, "rb") as f:
            st.download_button("Download Excel", data=f, file_name="locations.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        st.error(f"Export failed: {str(e)}")


button_col1, button_col2, button_col3 = st.columns(3)
with button_col1:
    if st.button("Create Location"):
        create_location()
with button_col2:
    if st.button("Refresh Locations"):
        fetch_locations()
with button_col3:
    if st.button("Export to Excel"):
        export_to_excel()

st.divider()

if st.session_state.locations_data:
    df = pd.DataFrame(st.session_state.locations_data)
    preferred = ["id", "name", "locationType", "city", "country", "address"]
    cols = [c for c in preferred if c in df.columns]
    st.dataframe(df[cols])
else:
    st.info("No location data loaded yet. Click 'Refresh Locations' to fetch locations.")