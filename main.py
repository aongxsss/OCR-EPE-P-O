import fitz
import os
import pytesseract
from PIL import Image , ImageEnhance

def pdf_to_jpeg_and_ocr(pdf_path):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(0)
    pix = page.get_pixmap(dpi=300)
    print("Pix: ", pix)
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    #Company
    left = 500
    top = 305
    right = 1740
    bottom = 365
    
    crop_box = (left, top, right, bottom)
    cropped_image = image.crop(crop_box)
    cropped_image = cropped_image.resize((cropped_image.width * 4, cropped_image.height * 4), Image.Resampling.LANCZOS)
    ocr_text = pytesseract.image_to_string(cropped_image, lang='eng')
    
    pdf_document.close()
    cropped_image.show()
    return {"Company": ocr_text}


# pdf_file_path = 'EPE 03 143385.pdf'
# # pdf_file_path = 'EPE 04 143463.pdf'
# # pdf_file_path = 'EPE 05 143749.pdf'
# # pdf_file_path = 'EPE 06 143849.pdf'
# # pdf_file_path = 'PO.144327.pdf'

# ocr_result = pdf_to_jpeg_and_ocr(pdf_file_path)
# print(ocr_result)