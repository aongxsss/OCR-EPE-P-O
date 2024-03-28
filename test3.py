from PIL import Image
import pytesseract

def ocr(jpeg_file):
    with Image.open(jpeg_file) as image:
        left = 460
        top = 240
        right = 1560
        bottom = 300
        
        crop_box = (left, top, right, bottom)
        cropped_image = image.crop(crop_box)

        cropped_image = cropped_image.resize((cropped_image.width * 4, cropped_image.height * 4), Image.LANCZOS)
        
        ocr_text = pytesseract.image_to_string(cropped_image, lang='eng')
        
        cropped_image.show()
        
        return {"Company": ocr_text}

jpeg_file = "pdfAsImg.jpeg"
ocr_result = ocr(jpeg_file)
print(ocr_result)
