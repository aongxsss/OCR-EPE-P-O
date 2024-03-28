import fitz
import os
import pytesseract
import re
from PIL import Image, ImageEnhance
from google.cloud import vision
import io
from google.oauth2 import service_account
def pdf_to_jpeg_and_ocr(pdf_path):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(0)
    pix = page.get_pixmap(dpi=300)
    print("Pix: ", pix)
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # Crop Positions
    crop_positions = [
        {"name": "Company", "left": 500, "top": 155, "right": 1840, "bottom": 245},
        {"name": "Address", "left": 500, "top": 305, "right": 1740, "bottom": 365},
        {"name": "P_O No.", "left": 1800, "top": 530, "right": 2600, "bottom": 600},
        {"name": "Quanlity", "left": 1340, "top": 920, "right": 1610, "bottom": 2300},
        {"name": "Unit_price", "left": 1620, "top": 920, "right": 1960, "bottom": 2300},
        {"name": "Code", "left": 95, "top": 980, "right": 320, "bottom": 2300}
    ]

    ocr_result = {}

    # Initialize the Google Cloud Vision client
    client = vision.ImageAnnotatorClient.from_service_account_json("OCR_service_acc.json")

    for crop_position in crop_positions:
        left = crop_position["left"]
        top = crop_position["top"]
        right = crop_position["right"]
        bottom = crop_position["bottom"]
        crop_box = (left, top, right, bottom)
        cropped_image = image.crop(crop_box)
        cropped_image = cropped_image.resize((cropped_image.width * 4, cropped_image.height * 4), Image.Resampling.LANCZOS)

        # Use Google Cloud Vision OCR for the "Code" region
        if crop_position["name"] == "Code":
            image_bytes = io.BytesIO()
            cropped_image.save(image_bytes, format='PNG')
            image_bytes = image_bytes.getvalue()
            gvision_image = vision.Image(content=image_bytes)
            response = client.text_detection(image=gvision_image)
            ocr_text = [text.description for text in response.text_annotations[1:]]   
            ocr_text = [text for text in ocr_text if text != "Code"]

            ocr_result[crop_position["name"]] = ocr_text
            cropped_image.show()
 
        else:
            ocr_text = pytesseract.image_to_string(cropped_image, lang='eng')

        

        if crop_position["name"] in ["Quanlity", "Unit_price"]:
            values = ocr_text.split('\n')
            cleaned_values = [re.sub(r'[^\d.,]', '', value) for value in values]
            ocr_result[crop_position["name"]] = [value for value in cleaned_values if value.strip()]
        else:
            ocr_result[crop_position["name"]] = ocr_text

    pdf_document.close()
    return ocr_result

pdf_file_path = 'EPE 03 143385.pdf'
# pdf_file_path = 'EPE 04 143463.pdf'
# pdf_file_path = 'EPE 05 143749.pdf'
# pdf_file_path = 'EPE 06 143849.pdf'
# pdf_file_path = 'PO.144327.pdf'
ocr_result = pdf_to_jpeg_and_ocr(pdf_file_path)
print(ocr_result)