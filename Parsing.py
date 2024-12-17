def pdf_to_image():
    import io
    import fitz
    import os
    import cv2
    import numpy as np


    resume_link = '/kaggle/input/resume-dataset/Resumes/DUAL_COLUMN_ENGLISH_DATASETS/Resume129.pdf'
    if resume_link.endswith('.pdf'):
        print("File in pdf format")

        doc = fitz.open(resume_link)
    #     print(len(doc))

        # Loop through each page in the PDF
        for page_number in range(len(doc)):
        
            page = doc.load_page(page_number)  # Get the page
            pix = page.get_pixmap()  # Convert the page to an image
            if page_number == 0:
                output_image_path = "/kaggle/working/original_image.jpg"
                # Save the image as a JPG file
                pix.save(output_image_path)
            else:
                pix.save(f"/kaggle/working/original_image(Page-{page_number}).jpg")
                print(f"Re-run all below code by changing in image path of YOLO by /kaggle/working/original_image_(Page-{page_number}).jpg")
    #     if len(doc) > 1:
    #         print("Still only one page resume is taken into account")
        # Close the document
        doc.close()
    elif resume_link.endswith('.jpg') or resume_link.endswith('jpeg') or resume_link.endswith('png'):
        print("File in image format")
        img = cv2.imread(resume_link)
        cv2.imwrite('/kaggle/working/original_image.jpg', img)
    else:
        print("File format not supported!! [Supported formats: .jpg/.png/.jpeg/.pdf]")
