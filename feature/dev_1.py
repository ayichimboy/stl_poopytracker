# import libraries
import pandas as pd             
import numpy as np                   
import seaborn as sns                          
import matplotlib.pyplot as plt       
import boto3
from io import BytesIO
from dotenv import load_dotenv
import os
import streamlit as st
from PIL import Image
from ultralytics import YOLO

load_dotenv()

# Access them using os.getenv()
aws_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_DEFAULT_REGION")

# Check if credentials were loaded
if not all([aws_key, aws_secret, aws_region]):
    raise EnvironmentError("Missing AWS credentials in .env file")

# Define S3 bucket info
bucket = 'doogie-model'
key = 'weights/best.pt'  # full key path inside the bucket

# Create a session with credentials
session = boto3.Session(
    aws_access_key_id=aws_key,
    aws_secret_access_key=aws_secret,
    region_name=aws_region
)

# Create an S3 client from the session
s3_client = session.client('s3')

# Download the model file into memory
f = BytesIO()
try:
    s3_client.download_fileobj(bucket, key, f)
    f.seek(0)  # Reset pointer to start of file
    print("File downloaded successfully. Size:", len(f.getvalue()), "bytes")
except Exception as e:
    print("Failed to download the file:", e)
# # print(aws_key, aws_secret, region)


new_poop_model = YOLO("final_poop_model.pt")


st.set_page_config(layout='centered', page_title="STL Poopy Tracker", page_icon="🐕💩")
st.title("Poop Detector in Action 🐕💩")

# upload an image
uploaded_file = st.file_uploader("Upload an image with GPS metadata", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    # detect poop in the image
    results = new_poop_model(image, save=True)
    
    # if dog poop is detected, extract the caption
    if results[0].boxes:
        caption = f"Detected {len(results[0].boxes)} poop(s) in the image. FYI, detection model is not perfect."
    else:
        caption = "No poop detected in the image 😟."
    
    # display image with detections
    st.image(results[0].plot(), caption=caption, use_container_width=True)