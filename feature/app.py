# import libraries for the yolov8 poop detection model
import streamlit as st
from PIL import Image      
import datetime                     
import ultralytics
from ultralytics import YOLO
import piexif
import gspread
import pandas as pd
import json
import pydeck as pdk
import cv2

# --- Google Sheets Auth ---
# Load credentials from GitHub/Streamlit secret environment variable
if "poopymapper_credentials_json" not in st.secrets:
    raise EnvironmentError("Missing CREDENTIALS in environment variables")

# gcp_credentials_dict = json.loads(os.environ["poopymapper_credentials_json"])
gcp_credentials_dict = json.loads(st.secrets["poopymapper_credentials_json"])
client = gspread.service_account_from_dict(gcp_credentials_dict)

# client = gspread.service_account(filename='poopymapper_credentials.json')
working_sheet = client.open("PoopLocations").sheet1

# functions that imports and extracts gps, time and data information
def extract_gps_from_image(image):
    try:
        # img = Image.open(image_file)
        exif_data = piexif.load(image.info["exif"])
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

# Run inference with the YOLOv8n model on the 'poop.jpg' image
new_poop_model = YOLO("final_poop_model.pt")

# Configure Streamlit app
st.set_page_config(layout='centered', page_title="STL Poopy Tracker", page_icon="🐕💩")
st.title("Poop Detector in Action 🐕💩")
st.markdown(""" 
            **Welcome to the Neighborhood Poppy Mapper!**

            This app allows users to log the location of dog poop sighted in their neighborhood.

            **How it works:**
            1. The streamlit app uses image GPS metadata to log location where the poop was sighted.
            2. The streamlit app runs a YOLOv8 model trained on a custom dataset to detect dog poop.
            3. The streamlit app keeps track of GPS data and displays it but does not store any personal information or images.
            4. The streamlit app displays a map of all the logged locations where dog poop was sighted with a blue dot for the most recent log and red dots for previous logs.
            5. The app uses a Google Sheet to store the GPS data, time and image file names.
            6. The app uses the piexif library to extract GPS metadata from the uploaded image.
            7. The app uses the ultralytics library to run the YOLOv8 model on the uploaded image.
            
            Please Note: We do not store any personal information or images aside GPS and file name.

            **How to use the streamlit app:**
            1. Take a photo of the poop with your phone camera.
            2. Ensure that GPS location is enabled in your camera settings.
            3. Upload the photo using the button below.
            4. The streamlit app will extract the GPS coordinates and log them in a Google Sheet.
            5. The streamlit app will display an image with the detected dog poop and a caption indicating the number of poops detected.
            6. The streamlit app will display a map of all logged locations below.
        
            **FYI: The object detection model was trained on a small dataset and may not be perfect.**
            """
            )

# upload an image
uploaded_file = st.file_uploader("Upload Photo (with GPS)📷🐕💩", type=["JPEG","jpg","jpeg"])

if uploaded_file is not None:
    
    image = Image.open(uploaded_file)
    
    if image:
    
        lat, lon = extract_gps_from_image(image)
        file_name = uploaded_file.name
        timestamp = datetime.datetime.now().isoformat()
        working_sheet.append_row([timestamp, file_name, lat, lon])
        st.success("Logged Location Successfully!✅")
    else:
        st.warning("No Image Uploaded😔")
    
    # detect poop in the image
    results = new_poop_model(image, save=True)
    
    # if dog poop is detected, extract the caption
    if results[0].boxes:
        caption = f"Detected {len(results[0].boxes)} poop(s) in the image. FYI, detection model is not perfect."
    else:
        caption = "No poop detected in the image 😟."
    
    # display image with detections
    st.image(results[0].plot(), caption=caption, use_container_width=True)
    
# Plot the gps data on a map
st.subheader("Mapped Poop Locations")
st.write("Current number of Poop Logs: ", len(working_sheet.get_all_records()))

data = working_sheet.get_all_records()
df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df.iloc[:, 0])
df['latitude'] = pd.to_numeric(df.iloc[:,2], errors='coerce')
df['longitude'] = pd.to_numeric(df.iloc[:,3], errors='coerce')

# Filter out rows with NaN values in latitude or longitude
df = df.dropna(subset=['latitude', 'longitude'])

# Get latest log (most recent entry)
df_latest = df.iloc[-1:]
df_others = df.iloc[:-1]

# Create red layer for previous logs
previous_logs = pdk.Layer(
    "ScatterplotLayer",
    data=df_others,
    get_position='[longitude, latitude]',
    get_fill_color='[255, 0, 0]',  # red
    get_radius=30,
)

# Create blue layer for the most recent log
latest_log = pdk.Layer(
    "ScatterplotLayer",
    data=df_latest,
    get_position='[longitude, latitude]',
    get_fill_color='[0, 0, 255]',  # blue
    get_radius=35,
)

# Set initial view to latest log position
view_state = pdk.ViewState(
    latitude=df_latest.iloc[0]['latitude'],
    longitude=df_latest.iloc[0]['longitude'],
    zoom=15,
    pitch=0
)

# Combine both layers in one map
deck = pdk.Deck(
    initial_view_state=view_state,
    layers=[previous_logs, latest_log],
    map_style='mapbox://styles/mapbox/streets-v11',
    tooltip={"text": "Lat: {latitude}, Lon: {longitude}"}
)

# Render only once
st.pydeck_chart(deck)
st.write(f"Blue dot🔵: most recent log, Red dots 🔴: previous logs")