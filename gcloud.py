import fitz
import os
from PIL import Image
from google.cloud import vision
import io
from google.oauth2 import service_account

def pdf_to_jpeg_and_ocr(pdf_path):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(0)
    pix = page.get_pixmap(dpi=300)
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    left = 20
    top = 890
    right = 360
    bottom = 2300
    crop_box = (left, top, right, bottom)
    cropped_image = image.crop(crop_box)
    cropped_image = cropped_image.resize((cropped_image.width * 4, cropped_image.height * 4), Image.Resampling.LANCZOS)

    client = vision.ImageAnnotatorClient.from_service_account_json("OCR_service_acc.json")
    image_bytes = io.BytesIO()
    cropped_image.save(image_bytes, format='PNG')
    image_bytes = image_bytes.getvalue()
    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)
    ocr_text = response.text_annotations[0].description

    pdf_document.close()
    cropped_image.show()
    return ocr_text


pdf_file_path = 'EPE 06 143849.pdf'
ocr_result = pdf_to_jpeg_and_ocr(pdf_file_path)
print(ocr_result)