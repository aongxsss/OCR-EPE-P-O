import fitz
import pytesseract
import re
from PIL import Image
from google.cloud import vision
import io
import cv2
import numpy as np

CROP_POSITIONS = [
    {"name": "Company", "left": 500, "top": 155, "right": 1840, "bottom": 245},
    {"name": "Address", "left": 500, "top": 305, "right": 1740, "bottom": 365},
    {"name": "P_O No.", "left": 1800, "top": 535, "right": 2600, "bottom": 630},
    {"name": "Quanlity", "left": 1340, "top": 990, "right": 1610, "bottom": 2300},
    {"name": "Unit_price", "left": 1620, "top": 990, "right": 1960, "bottom": 2300},
    {"name": "Code", "left": 100, "top": 980, "right": 370, "bottom": 2300}
]

def preprocess_image(image):
    """
    Preprocess the image for better OCR results.
    """
    opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 160, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 21, 10)
    return Image.fromarray(cv2.cvtColor(thresh, cv2.COLOR_BGR2RGB))



def ocr_with_tesseract(image):
    """
    Perform OCR using Tesseract on the given image.
    """
    return pytesseract.image_to_string(image, lang='eng')

def ocr_with_google_vision(image_bytes, client):
    """
    Perform OCR using Google Cloud Vision on the given image bytes.
    """
    gvision_image = vision.Image(content=image_bytes)
    response = client.text_detection(image=gvision_image)
    ocr_text = [text.description for text in response.text_annotations[1:]]
    return ocr_text

def clean_ocr_result(ocr_result):
    # Clean 'Company'
    ocr_result['Company'] = re.sub(r'\\n$', '', ocr_result['Company']).rstrip('\n')
    if 'CO.LTD.' in ocr_result['Company'] and 'CO.,LTD.' not in ocr_result['Company']:
        ocr_result['Company'] = re.sub(r'CO\.LTD\.$', 'CO.,LTD.', ocr_result['Company'])

    # Clean 'Address'
    address_lines = ocr_result['Address'].split('\n')
    cleaned_address = ' '.join(line.strip() for line in address_lines if re.match(r'^\d{3}/\d{3}', line))
    cleaned_address = re.sub(r'[^0-9]*$', '', cleaned_address)
    ocr_result['Address'] = cleaned_address
    
    # Clean 'P_O No.'
    po_number = re.search(r'\d{6}', ocr_result['P_O No.'])
    if po_number:
        ocr_result['P_O No.'] = po_number.group()
        
    # Clean 'Quanlity'
    quanlity = []
    i = 0
    while i < len(ocr_result['Quanlity']):
        price = ocr_result['Quanlity'][i]
        if price == ':':
            if i > 0 and i < len(ocr_result['Quanlity']) - 1:
                prev_price = ocr_result['Quanlity'][i - 1]
                next_price = ocr_result['Quanlity'][i + 1]
                if prev_price.isdigit() and next_price.isdigit():
                    del quanlity[-1]
                    combined_price = f"{prev_price}.{next_price}"
                    quanlity.append(combined_price)
                    i += 2  
                else:
                    quanlity.extend([price, next_price])
                    i += 2
            else:
                quanlity.append(price)
                i += 1
        else:
            quanlity.append(re.sub(r'[:;,\n]', '.', price))
            i += 1

    ocr_result['Quanlity'] = quanlity

    # Clean 'Unit_price'
    unit_prices = []
    i = 0
    while i < len(ocr_result['Unit_price']):
        price = ocr_result['Unit_price'][i]
        if price == ':':
            if i > 0 and i < len(ocr_result['Unit_price']) - 1:
                prev_price = ocr_result['Unit_price'][i - 1]
                next_price = ocr_result['Unit_price'][i + 1]
                if prev_price.isdigit() and next_price.isdigit():
                    del unit_prices[-1]
                    combined_price = f"{prev_price}.{next_price}"
                    unit_prices.append(combined_price)
                    i += 2 
                else:
                    unit_prices.extend([price, next_price])
                    i += 2
            else:
                unit_prices.append(price)
                i += 1
        else:
            unit_prices.append(re.sub(r'[:;,\n]', '.', price))
            i += 1

    ocr_result['Unit_price'] = unit_prices

    # Clean 'Code
    ocr_result['Code'] = [re.sub(r'[^0-9]*$', '', code) for code in ocr_result['Code']]

    return ocr_result


def pdf_to_jpeg_and_ocr(pdf_path):
    """
    Extract information from a PDF document using OCR.
    """
    # print("PDF flie name: ", pdf_path)
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(0) 
    pix = page.get_pixmap(dpi=300)
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    ocr_result = {}
    client = vision.ImageAnnotatorClient.from_service_account_json("OCR_service_acc.json")

    for crop_position in CROP_POSITIONS:
        left, top, right, bottom = crop_position["left"], crop_position["top"], crop_position["right"], crop_position["bottom"]
        crop_box = (left, top, right, bottom)
        cropped_image = image.crop(crop_box)
        cropped_image = cropped_image.resize((cropped_image.width * 3, cropped_image.height * 3), Image.Resampling.LANCZOS)

        if crop_position["name"] == "Code":
            preprocessed_image = preprocess_image(cropped_image)
            image_bytes = io.BytesIO()
            preprocessed_image.save(image_bytes, format='PNG')
            image_bytes = image_bytes.getvalue()
            ocr_text = ocr_with_google_vision(image_bytes, client)
            ocr_text = [text for text in ocr_text if text != "Code"]
            ocr_text = [text for text in ocr_text if len(text) > 3]
            ocr_result[crop_position["name"]] = ocr_text
        
        elif crop_position["name"] == "Quanlity" or crop_position["name"] == "Unit_price":
            preprocessed_image = preprocess_image(cropped_image)
            image_bytes = io.BytesIO()
            preprocessed_image.save(image_bytes, format='PNG')
            image_bytes = image_bytes.getvalue()
            ocr_text = ocr_with_google_vision(image_bytes, client)
            ocr_text = [text for text in ocr_text if text != "Code"]
            ocr_result[crop_position["name"]] = ocr_text
        
        elif crop_position["name"] == "Company":
            preprocessed_image = preprocess_image(cropped_image)
            ocr_text = ocr_with_tesseract(cropped_image)
            ocr_result[crop_position["name"]] = ocr_text

        else:
            ocr_text = ocr_with_tesseract(cropped_image)
            ocr_result[crop_position["name"]] = ocr_text
            
    ocr_result = clean_ocr_result(ocr_result)
    
    return str(ocr_result)