# import libraries for the yolov8 poop detection model
import streamlit as st
from PIL import Image      
import datetime                     
import ultralytics
from ultralytics import YOLO
import piexif
import boto3


# Load a COCO-pretrained YOLOv8n model
# using yolov8s gives a better result
# model = YOLO("yolov8m.pt")
# model.info()

# # Train the model on the COCO8 example dataset for 100 epochs
# results = model.train(data="poop.yaml", epochs=25, imgsz=640)

# s3_client = boto3.client('s3')
# bucket = 'doogie-model'


# Run inference with the YOLOv8n model on the 'poop.jpg' image
new_poop_model = YOLO("final_poop_model.pt")
# new_poop_model = YOLO("C:\\Users\\Owner\\poopy\\stl_poopytracker\\runs\\detect\\train7\\weights\\best.pt")
# results = new_poop_model("C:\\Users\\Owner\\poopy\\stl_poopytracker\\feature\\blue_poop_1.jpg", save=True)


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