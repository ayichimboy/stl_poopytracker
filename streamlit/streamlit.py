# import libraries for the poopy website                                  
import streamlit as st                 
from PIL import Image                          
import datetime
import piexif
import gspread
import pandas as pd
import time
import json
import os

# --- Google Sheets Auth ---
# Load credentials from GitHub/Streamlit secret environment variable
if "poopymapper_credentials.json" not in os.environ:
    raise EnvironmentError("Missing CREDENTIALS in environment variables")

gcp_credentials_dict = json.loads(os.environ["poopymapper_credentials.json"])
client = gspread.service_account(filename=gcp_credentials_dict)

# client = gspread.service_account(filename='poopymapper_credentials.json')
working_sheet = client.open("PoopLocations").sheet1

# functions that imports and extracts gps, time and data information
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


# Create the website 
st.set_page_config(layout='centered', page_title="STL Poopy Tracker", page_icon="🐕💩")

st.title("STL Poppy Mapper 🐕💩")
st.markdown(""" 
            Welcome to the STL Poppy Mapper!
            
            This app allows users to log the location of dog poop sighted in St. Louis City, 
            MO eventhough it is not limited to St. Louis City.
            
            Users can upload a photo with GPS metadata, and the app will log the location in a Google Sheet.
            The app also displays a map of all the logged locations where dog poop was sighted.
            
            Please Note that: We do not store any personal information or images aside the GPS data 
            and the file name of the uploaded image.
            
            Instructions:
            1. Take a photo of the poop with your phone camera.
            2. Ensure that GPS location is enabled in your camera settings.
            3. Upload the photo using the button below.
            4. The app will extract the GPS coordinates and log them in a Google Sheet.
            5. You can view the map of all logged locations below.
            
            """
            )

uploaded_file = st.file_uploader("Upload Photo (with GPS)📷💩", type=["JPEG","jpg","jpeg"])


if uploaded_file:
    st.image(uploaded_file, caption="Your Uploaded Image", use_container_width=True)
    # st.write("Extracting Meta Data...🚀")
    time.sleep(2)  # Simulate processing time
    
# Extract GPS data from the uploaded image
    lat, lon = extract_gps_from_image(uploaded_file)
    file_name = uploaded_file.name
    timestamp = datetime.datetime.now().isoformat()
    working_sheet.append_row([timestamp, file_name, lat, lon])
    st.success("Logged Location Successfully!✅")

else:
    st.warning("No Image Uploaded😟.")
    
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
st.map(df[['latitude', 'longitude']], 
       size=10, color="#ff0033",zoom=15, use_container_width=True)

