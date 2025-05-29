import streamlit as st
from PIL import Image
import piexif
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import pandas as pd

# --- Google Sheets Auth ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
credentials = ServiceAccountCredentials.from_json_keyfile_name("YOUR_CREDENTIALS.json", scope)
gc = gspread.authorize(credentials)
worksheet = gc.open("PoopLocations").sheet1

# --- EXIF GPS Extraction ---
def extract_gps_from_image(image_file):
    try:
        img = Image.open(image_file)
        exif_data = piexif.load(img.info["exif"])
        gps_data = exif_data.get("GPS", {})
        if not gps_data:
            return None, None

        def convert_to_degrees(value):
            d, m, s = value
            return d[0]/d[1] + (m[0]/m[1])/60 + (s[0]/s[1])/3600

        lat = convert_to_degrees(gps_data[2])
        if gps_data[1] == b'S':
            lat = -lat
        lon = convert_to_degrees(gps_data[4])
        if gps_data[3] == b'W':
            lon = -lon

        return lat, lon
    except Exception:
        return None, None

# --- UI ---
st.title("Poop Tracker - Animal Poop Location Mapper")

uploaded_file = st.file_uploader("Upload a photo (with GPS)", type=["jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    lat, lon = extract_gps_from_image(uploaded_file)

    if lat and lon:
        df_existing = pd.DataFrame(worksheet.get_all_records())
        filename = uploaded_file.name
        already_logged = (
            not df_existing.empty and
            ((df_existing['filename'] == filename) & 
             (df_existing['latitude'] == lat) & 
             (df_existing['longitude'] == lon)).any()
        )

        if already_logged:
            st.info("This image has already been logged.")
        else:
            timestamp = datetime.datetime.now().isoformat()
            worksheet.append_row([timestamp, filename, lat, lon])
            st.success(f"Logged location: Latitude = {lat}, Longitude = {lon}")
    else:
        st.warning("No GPS metadata found in this image.")

# --- View & Filter Data ---
st.subheader("Mapped Poop Locations")

data = worksheet.get_all_records()
if data:
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

    option = st.selectbox("Select Timeframe", ["All", "Today", "This Week", "This Month"])

    today = datetime.date.today()
    if option == "Today":
        df = df[df['timestamp'].dt.date == today]
    elif option == "This Week":
        df = df[df['timestamp'].dt.isocalendar().week == today.isocalendar().week]
    elif option == "This Month":
        df = df[df['timestamp'].dt.month == today.month]

    st.map(df[['latitude', 'longitude']])
else:
    st.info("No data yet.")
