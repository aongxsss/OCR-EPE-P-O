# import fitz
# import os
# import pytesseract
# from PIL import Image, ImageEnhance
# import numpy as np
# # client = vision.ImageAnnotatorClient.from_service_account_json("OCR_service_acc.json")
# def pdf_to_jpeg_and_ocr(pdf_path):
#     pdf_document = fitz.open(pdf_path)
#     page = pdf_document.load_page(0)
#     pix = page.get_pixmap(dpi=300)
#     print("Pix: ", pix)
#     image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
#     left = 20
#     top = 890
#     right = 360
#     bottom = 2300
#     crop_box = (left, top, right, bottom)
#     cropped_image = image.crop(crop_box)
#     cropped_image = cropped_image.resize((cropped_image.width * 4, cropped_image.height * 4))
    
#     # Convert PIL image to OpenCV format
#     cv_image = cv2.cvtColor(np.array(cropped_image), cv2.COLOR_RGB2BGR)
    
#     # Convert the image to grayscale
#     gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    
#     # Apply edge detection to find the object contours
#     edges = cv2.Canny(gray_image, 100, 200)
#     contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
#     # Draw red borders around the detected objects
#     border_color = (0, 0, 255)  # Red color
#     border_thickness = 1
#     cv2.drawContours(cv_image, contours, -1, border_color, border_thickness)
    
#     # Convert the image back to PIL format
#     bordered_image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
    
#     ocr_text = pytesseract.image_to_string(bordered_image, lang='eng')
#     pdf_document.close()
#     bordered_image.show()
#     return ocr_text

# pdf_file_path = 'EPE 06 143849.pdf'
# ocr_result = pdf_to_jpeg_and_ocr(pdf_file_path)
# print(ocr_result)

#  elif crop_position["name"] == "Address":
#     address_match = re.search(r'\b700\b.*\b20000\b', ocr_text)
#     if address_match:
#         ocr_result[crop_position["name"].replace("/", "_")] = address_match.group()
#     else:
#         ocr_result[crop_position["name"].replace("/", "_")] = ""