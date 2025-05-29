from PIL import Image         
from PIL.ExifTags import TAGS 
import piexif     
import gspread
import os
# from oauth2client.service_account import ServiceAccountCredentials   
image = Image.open('IMG_0154.jpg')  # Load the image  

client = gspread.service_account(filename='poopymapper_credentials.json')
working_sheet = client.open("PoopLocations").sheet1
print(working_sheet.cell(1,2).value)

#retrieve file name of the image
file_name = os.path.basename("IMG_0154.jpg")
print(file_name)
# --- Google Sheets Auth ---
# scope = [
#     "https://spreadsheets.google.com/feeds",
#     "https://www.googleapis.com/auth/drive"
# ]
# credentials = ServiceAccountCredentials.from_json_keyfile_name("poopymapper_credentials.json", scope)
# gc = gspread.authorize(credentials)
# worksheet = gc.open("PoopLocations").sheet1

# # load the image 
# image = Image.open('IMG_0154.jpg')

# def extract_gps_from_image(image_file):
#     try:
#         img = Image.open(image_file)
#         exif_data = piexif.load(img.info["exif"])
#         gps_data = exif_data.get("GPS", {})
#         if not gps_data:
#             return None, None

#         def convert_to_degrees(value):
#             d, m, s = value
#             return d[0]/d[1] + (m[0]/m[1])/60 + (s[0]/s[1])/3600

#         lat = convert_to_degrees(gps_data[2])
#         if gps_data[1] == b'S':
#             lat = -lat
#         lon = convert_to_degrees(gps_data[4])
#         if gps_data[3] == b'W':
#             lon = -lon

#         return lat, lon
#     except Exception:
#         return None, None



# gps_data = extract_gps_from_image('IMG_0154.jpg')
# print(gps_data[0])



# meta_data = piexif.load(image.info.get("exif", b""))

# gps_data = meta_data.get("GPS", {})
# print(f'gps data is : {gps_data}')



# meta_data = image.getexif()

# print(meta_data)

# for meta in meta_data:
    
#     metaname =  TAGS.get(meta, meta)
    
#     value = meta_data.get(meta)
#     print(f"{metaname:50}: {value}")

    
