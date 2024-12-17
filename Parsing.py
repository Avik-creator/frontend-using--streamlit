#Importing Libraries
import io
import math
import torch
import cv2
import fitz
import os
import pandas as pd
from PIL import Image
import subprocess
import numpy as np

def pil_to_cv2(pil_image):
    """
    Convert PIL Image to OpenCV format (numpy array)
    
    Args:
        pil_image (PIL.Image): Input PIL Image
    
    Returns:
        numpy.ndarray: OpenCV-compatible image
    """
    # Convert PIL image to numpy array
    # OpenCV uses BGR color format, so we convert from RGB
    numpy_image = np.array(pil_image)
    
    # Convert RGB to BGR if needed
    opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
    
    return opencv_image

def cv2_to_pil(cv2_image):
    """
    Convert OpenCV image to PIL Image
    
    Args:
        cv2_image (numpy.ndarray): Input OpenCV image
    
    Returns:
        PIL.Image: PIL Image
    """
    # Convert BGR to RGB
    rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    
    # Convert to PIL Image
    pil_image = Image.fromarray(rgb_image)
    
    return pil_image

#Converting pdf to image
def pdf_to_image(resume_link): 
    if resume_link.endswith('.pdf'):
        print("File in pdf format")

        doc = fitz.open(resume_link)
    #     print(len(doc))

        # Loop through each page in the PDF
        for page_number in range(len(doc)):
        
            page = doc.load_page(page_number)  # Get the page
            pix = page.get_pixmap()  # Convert the page to an image
            if page_number == 0:
                output_image_path = r"Jobfit_Predictor/temp_files/original_image.png"
                # Save the image as a JPG file
                pix.save(output_image_path)
                return output_image_path
            else:
                pix.save(f"Jobfit_Predictor\temp_files\original_image(Page-{page_number}).png") # For multiple pages storing in uploads folder
                print(f"Re-run all below code by changing in image path of YOLO by Jobfit_Predictor\temp_files\original_image(Page-{page_number}).png")
        doc.close()
    elif resume_link.endswith('.jpg') or resume_link.endswith('jpeg') or resume_link.endswith('png'):
        print("File in image format")
        image1 = Image.open(resume_link)
        image = pil_to_cv2(image1)
        image2 = cv2_to_pil(image)
        image2.save("D:/Coding/Final Year/Jobfit Predictor/Jobfit_Predictor/temp_files/original.png",'PNG')
        return "D:/Coding/Final Year/Jobfit Predictor/Jobfit_Predictor/temp_files/original.png"
    else:
        print("File format not supported!! [Supported formats: .jpg/.png/.jpeg/.pdf]")

# Perform object detection using YOLOv5
def candidate_pic_detection(image_path):
    image1 = Image.open(image_path)
    im1 = pil_to_cv2(image1)
    fixed_size = (640,640)
    r_image = cv2.resize(im1, fixed_size)
    image = cv2_to_pil(r_image)
    
    #Save results in a custom directory
    image.save("D:/Coding/Final Year/Jobfit Predictor/Jobfit_Predictor/temp_files/resized_image.png",'PNG')
    # Perform object detection using YOLOv5
    print("1st resize done")

    # Load the YOLOv5 model
    model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt')
    source = "D:/Coding/Final Year/Jobfit Predictor/Jobfit_Predictor/temp_files/resized_image.png"
    # Perform inference
    results = model(source)
    actual_result = pd.DataFrame(results.pandas().xyxy[0])# Bounding box predictions
    print(actual_result)# Print results
    filtered_result = actual_result[actual_result['class'] == 0]

    path = "D:/Coding/Final Year/Jobfit Predictor/Jobfit_Predictor/temp_files/labels.txt"
    with open(path, 'w') as f:
        df_string = filtered_result.to_string(header=False, index=False)
        f.write(df_string)

    return path
def removing_candidate_pic(path):
    image_width = 640
    image_height = 640
    x1=x2=y1=y2 = 0.000000
    c = 0
    im1 = Image.open("D:/Coding/Final Year/Jobfit Predictor/Jobfit_Predictor/temp_files/resized_image.png")
    image = pil_to_cv2(im1)
    if os.path.isfile(path):
        with open(path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                values = line.split()
                class_id = int(values[5])
                if class_id == 0:
                    if c == 1:
                        height_norm1 = float(values[3])
                        if height_norm1 > height_norm:
                            break
                    c = c + 1
                    x_center_norm = float(values[0])
                    y_center_norm = float(values[1])
                    width_norm = float(values[2])
                    height_norm = float(values[3])

                    x1 = x_center_norm - (width_norm / 2)
                    y1 = y_center_norm - (height_norm / 2)
                    x2 = x_center_norm + (width_norm / 2)
                    y2 = y_center_norm + (height_norm / 2)

        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        print(f"Coordinates: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
    f.close()            
    cv2.rectangle(image, (x1, y1), (x2, y2), (255, 255, 255), -1)
    image2 = cv2_to_pil(image)
    image2.save('D:/Coding/Final Year/Jobfit Predictor/Jobfit_Predictor/temp_files/results_person_removed.png','PNG')
   

#Main function
def main():
    resume_link="D:/Coding/Final Year/Jobfit Predictor/Jobfit_Predictor/uploads/Test.jpg"
    img = pdf_to_image(resume_link)
    path = candidate_pic_detection(img)
    removing_candidate_pic(path)
if __name__ == "__main__":
    main()