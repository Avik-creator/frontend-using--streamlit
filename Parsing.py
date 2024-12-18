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
from gradio_client import Client, handle_file

temp_fil_loc = "D:/Coding/Final Year/Jobfit Predictor/Jobfit_Predictor/temp_files"
best_x = -1
c = 0 

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
                output_image_path = temp_fil_loc + "/original_image.png"
                # Save the image as a JPG file
                pix.save(output_image_path)
                return output_image_path
            else:
                pix.save(temp_fil_loc + f"/original_image(Page-{page_number}).png") # For multiple pages storing in uploads folder
                print("Re-run all below code by changing in image path of YOLO by "+temp_fil_loc+f"original_image(Page-{page_number}).png")
        doc.close()
    elif resume_link.endswith('.jpg') or resume_link.endswith('jpeg') or resume_link.endswith('png'):
        print("File in image format")
        image1 = Image.open(resume_link)
        image = pil_to_cv2(image1)
        image2 = cv2_to_pil(image)
        image2.save(temp_fil_loc + "/original.png",'PNG')
        return temp_fil_loc + "/original.png"
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
    image.save(temp_fil_loc+"/resized_image.png",'PNG')
    # Perform object detection using YOLOv5
    print("1st resize done")

    # Load the YOLOv5 model
    model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt')
    source = temp_fil_loc+"/resized_image.png"
    # Perform inference
    results = model(source)
    actual_result = pd.DataFrame(results.pandas().xyxy[0])# Bounding box predictions
    print(actual_result)# Print results
    filtered_result = actual_result[actual_result['class'] == 0]

    path = temp_fil_loc +"/labels.txt"
    with open(path, 'w') as f:
        df_string = filtered_result.to_string(header=False, index=False)
        f.write(df_string)
    return path

def removing_candidate_pic(path):
    image_width = 640
    image_height = 640
    x1=x2=y1=y2 = 0.000000
    c = 0
    im1 = Image.open(temp_fil_loc +"/resized_image.png")
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
                    x1 = float(values[0])
                    y1 = float(values[1])
                    x2 = float(values[2])
                    y2 = float(values[3])

        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        print(f"Coordinates: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
    f.close()            
    cv2.rectangle(image, (x1, y1), (x2, y2), (255, 255, 255), -1)
    image2 = cv2_to_pil(image)
    image2.save(temp_fil_loc+'/results_person_removed.png','PNG')
    return temp_fil_loc+'/results_person_removed.png'

def check_grayscale(image_path):
    def is_grayscale(image_path):
        # Load the image
        im1 = Image.open(image_path)
        image = pil_to_cv2(im1)
        # Check if the image is single channel (grayscale)
        if len(image.shape) == 2:  # Grayscale image will have shape (height, width)
            return True
        
        # If the image has 3 channels, check if all channels are the same
        if len(image.shape) == 3 and image.shape[2] == 3:  # RGB image will have shape (height, width, 3)
            # Split the image into its three channels
            b, g, r = cv2.split(image)
            # Check if all channels are equal (grayscale has equal R, G, B values)
            if np.array_equal(b, g) and np.array_equal(g, r):
                return True
        return False
    
    if is_grayscale(image_path):
        print("Image is grayscale")
        grayscale_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        # Increase the brightness and contrast of the image (if needed)
        alpha = 1  # Contrast control (1.0-3.0)
        beta = 0    # Brightness control (0-100)

        # Adjust brightness and contrast
        brightened_image = cv2.convertScaleAbs(grayscale_image, alpha=alpha, beta=beta)

        # Apply a threshold to turn gray background to white
        _, thresholded_image = cv2.threshold(brightened_image, 200, 255, cv2.THRESH_BINARY)

        # Convert the resulting image to RGB
        rgb_image = cv2.cvtColor(thresholded_image, cv2.COLOR_GRAY2RGB)

        # Save or display the RGB image
        rgb_im1 = cv2_to_pil(rgb_image)
        rgb_im1.save(temp_fil_loc + '/results_image.jpg', 'PNG')
    else:
        im1 = Image.open(image_path)
        im1.save(temp_fil_loc + '/results_image.jpg', 'PNG')
        print("The image is not grayscale.")
    return temp_fil_loc + '/results_image.jpg'
        
def dual_column_segregate(image_path):

    # Load the image
    image = Image.open(image_path)
    r_image = pil_to_cv2(image)
    fixed_size = (1250,1563)
    image = cv2.resize(r_image, fixed_size)
    im1 = cv2_to_pil(image)
    im1.save(temp_fil_loc + "/2nd_resized_image.png",'PNG')

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    a = 0
    for i in range(70,150,5):
        # Apply binary thresholding to get a binary image
        _, binary = cv2.threshold(gray, i, 255, cv2.THRESH_BINARY_INV)

        # Find the contours of the text regions
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Create a mask for the text regions
        mask = np.zeros_like(binary)

        # Draw filled contours on the mask (text regions become white)
        cv2.drawContours(mask, contours, -1, 255, thickness=cv2.FILLED)

        # Invert the mask to get the non-text areas (non-text areas become white)
        mask_inv = cv2.bitwise_not(mask)
      
        converted_image = cv2.cvtColor(r_image, cv2.COLOR_BGR2RGB)

        # Reshape the image to a 2D array of pixels
        pixels = converted_image.reshape(-1, 3)

        # Convert to a set of unique colors
        unique_colors = set(map(tuple, pixels))

        # Convert the set back to an array and sort it by the first channel (Hue)
        unique_colors_array = np.array(list(unique_colors))
        unique_colors_array = unique_colors_array[unique_colors_array[:, 0].argsort()]

        # Initialize the colors list with the first unique color's first channel value
        colors = [unique_colors_array[0]]

        # Iterate through the unique colors (sorted)
        for i in range(1, len(unique_colors_array)):
            # Only add the color if the difference with the last color is greater than 55
            if abs(unique_colors_array[i][0] - colors[-1][0]) > 55:
                colors.append(unique_colors_array[i])

        # Print the selected colors
        print(colors)
        if len(colors)> 2:
            unique_background_colors = 1
            # Draw filled contours on the mask (text regions become white)
        #     cv2.drawContours(mask_inv, contours, 1, 255, thickness=cv2.FILLED)
        else:
            unique_background_colors = 0 
        cv2.drawContours(mask_inv, contours, 0, 255, thickness=cv2.FILLED)

    # unique_background_colors = 0 # 0/1
    # cv2.drawContours(mask_inv, contours, -1, 255, thickness=cv2.FILLED)

        prev_contour = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if h > 1000 and w > 80 and w < 1200 :#h =800
    #             print(h)
                a = 1
    #             cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 3)
                unique_background_colors = unique_background_colors + 1
            
        if a==1:
            break
    print("No. of background parts with different colour found: ",unique_background_colors)

        
    if unique_background_colors > 1:  # Two background colors detected
        print("Two background colors detected. Keeping the image unchanged.")
    else:

    # Parameters
        height, width = mask_inv.shape
        line_thickness = 2
        required_non_text_percentage = 0.1
        # 98% non-text space requirement(0.9780 - 0.98)
        required_consecutive_columns =  40
        #Number of consecutive columns that need to meet the non-text requirement(40-25)
    
        initial_skip_percentage = 0.2      # Skip the first 20% of the x-axis#@@@@@@@@@@@@@@@@@
        f = 0
        c = 0
        best_x = -1
        for required_consecutive_columns in range(65,25,-1):
            y = required_consecutive_columns
            for required_non_text_percentage1 in range (1000,949,-1):####1000000- to be precise
                required_non_text_percentage = required_non_text_percentage1 / 1000.00
                x = required_non_text_percentage
                if required_non_text_percentage > 0.99 and c==0:
                    c = 1
                    for required_consecutive_columns in range(200,10,-1):
                            non_text_threshold = int(height * required_non_text_percentage)
                            # Calculate the starting point after skipping the initial part
                            start_x = int(width * initial_skip_percentage)

                            # Initialize flag and counters
                            consecutive_non_text_columns = 0

                            # Scan across the x-axis starting after the initial skip
                            for x in range(start_x, width):
                                # Calculate the number of non-text pixels along the y-axis at this x position
                                non_text_pixels = np.sum(mask_inv[:, x]) / 255

                                # Check if this position meets the non-text requirement
                                if non_text_pixels >= non_text_threshold:
                                    consecutive_non_text_columns += 1
                                    # If we have enough consecutive columns, we can consider this position
                                    if consecutive_non_text_columns >= required_consecutive_columns:
                                        best_x = x - (consecutive_non_text_columns // 2)  
                                        break
                                else:
                                    # Reset the counter if the requirement is not met
                #                     print(x)
                                    consecutive_non_text_columns = 0
                            if best_x < 900 and best_x!= -1:
                                f = 1
                                break
                
                            
                else: 
                    required_non_text_percentage = x
                    required_consecutive_columns = y
                    non_text_threshold = int(height * required_non_text_percentage)
                    # Calculate the starting point after skipping the initial part
                    start_x = int(width * initial_skip_percentage)
                    # Initialize flag and counters
                    consecutive_non_text_columns = 0

                    # Scan across the x-axis starting after the initial skip
                    for x in range(start_x, width):
                        # Calculate the number of non-text pixels along the y-axis at this x position
                        non_text_pixels = np.sum(mask_inv[:, x]) / 255

                        # Check if this position meets the non-text requirement
                        if non_text_pixels >= non_text_threshold:
                            
                            consecutive_non_text_columns += 1
                            # If we have enough consecutive columns, we can consider this position
                            if consecutive_non_text_columns >= required_consecutive_columns:
    #                             print(non_text_pixels)
                                best_x = x - (consecutive_non_text_columns // 2)
                                break
                        else:
                            # Reset the counter if the requirement is not met
    #                         print(x)
                            consecutive_non_text_columns = 0
                            
                        if best_x < 1000 and best_x != -1:
    #                         print(best_x)
                            f = 1
                            break
            
                    
                if f == 1:
                    # Define the background color (e.g., light blue)
                    background_color = [255, 100, 255]  # BGR format for light blue

                    # Create a colored rectangle for the background change
                    background = np.full_like(image, background_color)# BGR format for light blue

                    # Convert the mask to a three-channel image to match the color image
                    mask_3channel = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
                    # Apply the background color only to the area before the line, ignoring text
                    image[:, :best_x] = np.where(mask_3channel[:, :best_x] == [0, 0, 0], background[:, :best_x], image[:, :best_x])
                    cv2.line(image, (best_x, 0), (best_x, height), (0,0,0), thickness=line_thickness)
                    required_non_text_percentage = required_non_text_percentage*100
                    print(f"Line drawn at x={best_x} with {required_consecutive_columns} consecutive columns with {required_non_text_percentage}% of non-text")
                    break
            if f == 1:
                break
        if best_x == -1 or f==0:#
    #         print(best_x)
            print("No suitable vertical space found for drawing the line.")
        c == f
    # Save or display the result
    img2 = cv2_to_pil(image)
    img2.save(temp_fil_loc + '/output_image_with_line.png','PNG')
    try:
        print(best_x)
    except:
        best_x = -1
    return [temp_fil_loc + '/output_image_with_line.png',best_x]

def grayscaling_threshold_merging_images(image_path):
    im1 = Image.open(image_path)
    image = pil_to_cv2(im1)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh_black = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    _, thresh_white = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # Combine both thresholds

    thresh1 = cv2.bitwise_or(thresh_black, thresh_white)
    thresh1_pil = cv2_to_pil(thresh1)
    thresh1_pil.save(temp_fil_loc+"/temp_thres_white.png",'PNG')
    return temp_fil_loc+"/temp_thres_white.png"

def dual_column_color_div_and_crop(image_path,best_x):
    im1 = Image.open(temp_fil_loc + '/2nd_resized_image.png')
    o1 = original_image = pil_to_cv2(im1)
    # Load the image
    im2 = Image.open(image_path)
    image = pil_to_cv2(im2)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Threshold the image to get binary image (assuming black is 0 and white is 255)
    _, binary_image = cv2.threshold(image, 1, 255, cv2.THRESH_BINARY_INV)

    # Find contours in the binary image
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Initialize a variable to store the minimum x-coordinate of the green line
    min_x = max_x = min_x_w = original_image.shape[1]  # Start with the width of the image
    # Convert grayscale image to BGR to draw colored rectangles
  
    f = max_y = prev_x = 0
    if best_x != -1:
        # Attempt to access the variable
        print(best_x)
        min_x = best_x
    else:
        # Handle the case where the variable is not defined
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # print(contour)
            # print(h)
            if h > 500:
                for point in contour:
                    print(point)
                    current_y = point[0][1]
                    if current_y >= max_y and point[0][1]< 1100:
                        # print(point[0][0])
                        max_y = current_y
                        prev_x = point[0][0]
                    else:
                        if point[0][0] < 1100 and (prev_x > 0 or point[0][0] > 0):
                            if prev_x != 0:
                                
                                w1 = prev_x
                            else:
                                w1 = point[0][0]
                            
                    
                            # We've found the highest point, so we can stop searching  
                            f = 1
                            break
                        
            if f==1:
                break
                        
        min_x = min(min_x, x) # Update min_x with the smallest x-coordinate
        min_x_w =  min(min_x_w, x+w,w1)
        print(w1)
        # print(min_x_w)
        max_x = max(max_x,x+w)
        cv2.rectangle(original_image, (x, y), (w1, max_y), (0, 255, 0), 3)
                    
        print(min_x_w)
        print(x+w)
        print(min_x)
        print(max_x)
    # print(best_x)
    # Save or display the resulting image
    if min_x > 500 or min_x_w > min_x:
        if min_x < 20:
            min_x = min_x_w
        cropped_image_left = original_image[:,:min_x]
        cropped_image_right = original_image[:,min_x:max_x]
    elif min_x_w < 0 and min_x < 0 and x+w < original_image.shape[1]:
        max_x = x+w
        cropped_image_left = original_image[:,:max_x]
        cropped_image_right = original_image[:,max_x:]
    
    else:
        cropped_image_left = original_image[:, :min_x_w]
        cropped_image_right = original_image[:,min_x_w:]
        
    # Save the cropped image(s)
   
    if cropped_image_left is not None and cropped_image_left.any():
        cropped_image_left_pil = cv2_to_pil(cropped_image_left)
        cropped_image_left_pil.save(temp_fil_loc+'/cropped_image_left.png','PNG' )
        if cropped_image_right is not None and cropped_image_right.any():
            cropped_image_right_pil = cv2_to_pil(cropped_image_right)
            cropped_image_right_pil.save(temp_fil_loc+'/cropped_image_right.png','PNG' )
        else:
            print("Single column so no right part found!!")
    else:
        print("Single column")
        o1_pil = cv2_to_pil(o1)
        o1_pil.save(temp_fil_loc+'/cropped_image_left.png','PNG')
    return temp_fil_loc+'/cropped_image_left.png'
    
def extraction_of_text(left_image):
    left_text=right_text=''
    
    #Left part extract
    client = Client("artificialguybr/Surya-OCR")
    result = client.predict(
            image=handle_file(left_image),
            langs="en",
            api_name="/ocr_workflow"
        )
    result1= list(result)
    left_text = result1[-1]
        
    #right part extract
    right_image = temp_fil_loc + '/cropped_image_right.png'
    if os.path.exists(right_image):
        client = Client("artificialguybr/Surya-OCR")
        result_r = client.predict(
            image=handle_file(right_image),
            langs="en",
            api_name="/ocr_workflow"
        )
      
        result2= list(result_r)
        right_text = result2[-1]
        # print(result1[-1])
        
    text = ''
    text = text + str("First column: " )+"\n" 
    text = text + left_text + '\n'
    text = text + str("Second column: " )+"\n"
    text = text + right_text + '\n' + "==================================================================" + "\n"
    
    white_page = Image.open('D:\Coding\Final Year\Jobfit Predictor\Jobfit_Predictor\White_page.png')
    white_page.save(left_image,'PNG')
    white_page.save(right_image,'PNG')
    return text
        
          
#Main function
def main_parse(resume_link):
    # resume_link="D:/Coding/Final Year/Jobfit Predictor/Jobfit_Predictor/uploads/Test.jpg"
    img = pdf_to_image(resume_link)
    cpd_path = candidate_pic_detection(img)
    rcp_path = removing_candidate_pic(cpd_path)
    cg_path = check_grayscale(rcp_path)
    path = dual_column_segregate(cg_path)
    dcs_path = path[0]
    best_x = path[1]
    gtmi_path =grayscaling_threshold_merging_images(dcs_path)
    left_part  = dual_column_color_div_and_crop(gtmi_path,best_x)
    text = extraction_of_text(left_part)
    # print(text)
    return text
    
if __name__ == "__main__":
    main_parse("D:/Coding/Final Year/Jobfit Predictor/Jobfit_Predictor/uploads/Test.jpg")