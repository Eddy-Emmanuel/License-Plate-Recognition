import streamlit as st
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
import pytesseract

# Load the YOLO model
pre_trained_yolo_model = YOLO(r"model/best.pt")

def detect_license_plate(image):
    prediction = pre_trained_yolo_model(image)
    pred_info = prediction[0].boxes
    return pred_info

def recognize_characters(roi):
    plate_number = pytesseract.image_to_string(roi).replace("\n", "").replace(" ", "")
    return plate_number

def main():
    st.title("License Plate Detection and Recognition")

    uploaded_file = st.file_uploader("Upload a car image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        image_np = np.array(image)

        # Detect license plate
        pred_info = detect_license_plate(image_np)

        if len(pred_info.xyxy.numpy()) == 1:
            pred_xmin, pred_ymin, pred_xmax, pred_ymax = pred_info.xyxy.numpy().flatten().astype(np.int32)
            roi = image_np[pred_ymin:pred_ymax, pred_xmin:pred_xmax]

            # Recognize characters
            plate_number = recognize_characters(roi)

            # Draw bounding box and recognized text on image
            detected_image = cv2.rectangle(image_np.copy(), (pred_xmin, pred_ymin), (pred_xmax, pred_ymax), (255, 0, 0), 2)
            
            col1, col2 = st.columns(2)
            with col1:
                st.image(image, caption="Uploaded Image (Resized)", width=220)
            with col2:
                st.image(detected_image, caption="Detected License Plate", width=220)
            
            st.markdown("## Detected Plate")
            center_placeholder = st.empty()
            with center_placeholder:
                st.image(roi, caption="License Plate Region", width=220)
            
            st.markdown(f"#### Recognized License Plate Characters: {plate_number}")
            st.write(f"#### Coordinates: x_min={pred_xmin}, y_min={pred_ymin}, x_max={pred_xmax}, y_max={pred_ymax}")
            
        else:
            plate_numbers = []
            coordinates = []
            detected_image = image_np.copy()

            for (xmin, ymin, xmax, ymax) in pred_info.xyxy.numpy().astype(np.int32):
                roi = image_np[ymin:ymax, xmin:xmax]
                plate_number = recognize_characters(roi)
                plate_numbers.append(plate_number)
                coordinates.append((xmin, ymin, xmax, ymax))

                # Draw bounding box on image
                detected_image = cv2.rectangle(detected_image, (xmin, ymin), (xmax, ymax), (255, 0, 0), 2)

            st.image(detected_image, caption="Detected License Plates", use_column_width=True)
            for i, (plate_number, (xmin, ymin, xmax, ymax)) in enumerate(zip(plate_numbers, coordinates)):
                col1, col2 = st.columns(2)
                with col1:
                    st.image(image_np[ymin:ymax, xmin:xmax], caption=f"License Plate Region {i+1}", use_column_width=True)
                with col2:
                    st.markdown(f"**Recognized License Plate Characters {i+1}:** {plate_number}")
                    st.write(f"Coordinates {i+1}: x_min={xmin}, y_min={ymin}, x_max={xmax}, y_max={ymax}")

if __name__ == "__main__":
    main()
