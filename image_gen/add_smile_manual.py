#!/usr/bin/env python3
"""Add smile with teeth to reference portrait using OpenCV DNN face detector."""
import cv2
import numpy as np
from PIL import Image
from pathlib import Path

SRC = Path(r"D:\OpenCode\ai-blogger\image_gen\output\reference_portrait.png")
OUT = Path(r"D:\OpenCode\ai-blogger\image_gen\output\reference_portrait_smile.png")

img = cv2.imread(str(SRC))
h, w = img.shape[:2]
print(f"Image: {w}x{h}")

# Try simple Haar with lower min size
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(100, 100))

if len(faces) == 0:
    print("No face with default params, trying adjusted...")
    faces = face_cascade.detectMultiScale(gray, 1.05, 3, minSize=(80, 80))

if len(faces) == 0:
    print("Still no face. Using DNN approach...")
    # Use DNN face detector
    net = cv2.dnn.readNetFromCaffe(
        cv2.data.dnn + "deploy.prototxt",  # doesn't exist as dependency
        cv2.data.dnn + "res10_300x300_ssd_iter_140000.caffemodel"
    )
    blob = cv2.dnn.blobFromImage(img, 1.0, (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()
    
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            fx, fy, fx2, fy2 = box.astype(int)
            fw, fh = fx2 - fx, fy2 - fy
            if fw > 100 and fh > 100:
                faces = [(fx, fy, fw, fh)]
                break

print(f"Detected {len(faces)} faces")
if len(faces) > 0:
    fx, fy, fw, fh = max(faces, key=lambda r: r[2]*r[3])
    print(f"Main face: x={fx}, y={fy}, w={fw}, h={fh}")
    
    # mouth region: lower-middle of face
    mouth_y1 = fy + int(fh * 0.6)
    mouth_y2 = fy + int(fh * 0.85)
    mouth_x1 = fx + int(fw * 0.15)
    mouth_x2 = fx + int(fw * 0.85)
    
    roi = img[mouth_y1:mouth_y2, mouth_x1:mouth_x2]
    roi_h, roi_w = roi.shape[:2]
    print(f"Mouth ROI: {mouth_x1},{mouth_y1} to {mouth_x2},{mouth_y2} ({roi_w}x{roi_h})")
    
    if roi_h > 10 and roi_w > 10:
        # Create teeth ellipse
        teeth_mask = np.zeros((roi_h, roi_w), dtype=np.uint8)
        cx, cy = roi_w // 2, roi_h // 2
        ax, ay = roi_w // 3, roi_h // 4
        cv2.ellipse(teeth_mask, (cx, cy), (ax, ay), 0, 0, 360, 255, -1)
        
        # Slightly open mouth - darken the area behind teeth
        inner_mask = np.zeros((roi_h, roi_w), dtype=np.uint8)
        cv2.ellipse(inner_mask, (cx, cy), (ax-5, ay-5), 0, 0, 360, 255, -1)
        
        teeth = np.full((roi_h, roi_w, 3), (220, 215, 200), dtype=np.uint8)  # BGR
        # Add vertical lines for tooth separation
        for t in range(-2, 3):
            tx = cx + t * (roi_w // 8)
            cv2.line(teeth, (tx, cy-ay+2), (tx, cy+ay-2), (200, 195, 180), 1)
        
        teeth_mask = cv2.GaussianBlur(teeth_mask, (11, 11), 3)
        teeth_mask_3ch = cv2.cvtColor(teeth_mask, cv2.COLOR_GRAY2BGR) / 255.0
        
        # dark mouth interior behind teeth
        inner = np.full((roi_h, roi_w, 3), (30, 20, 15), dtype=np.uint8)
        inner_mask = cv2.GaussianBlur(inner_mask, (11, 11), 3)
        inner_mask_3ch = cv2.cvtColor(inner_mask, cv2.COLOR_GRAY2BGR) / 255.0
        
        roi_float = roi.astype(np.float32)
        # first darken interior (behind teeth)
        roi_float = roi_float * (1 - inner_mask_3ch * 0.7) + inner.astype(np.float32) * (inner_mask_3ch * 0.7)
        # then add teeth on top
        roi_float = roi_float * (1 - teeth_mask_3ch * 0.5) + teeth.astype(np.float32) * (teeth_mask_3ch * 0.5)
        
        roi[:] = np.clip(roi_float, 0, 255).astype(np.uint8)
        
        # Mark mouth area on original
        cv2.rectangle(img, (mouth_x1, mouth_y1), (mouth_x2, mouth_y2), (0, 255, 0), 1)
        
        # Draw smile curve using lip corners
        lip_y = mouth_y1 + roi_h // 2
        for x_offset in range(0, roi_w, 5):
            rel_x = x_offset / roi_w
            smile_offset = int(5 * np.sin(rel_x * np.pi))
            pt = (mouth_x1 + x_offset, lip_y - smile_offset)
            cv2.circle(img, pt, 1, (0, 0, 255), -1)
    
    cv2.imwrite(str(OUT), img)
    print(f"Saved: {OUT}")
else:
    print("No face detected at all!")
    Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).save(str(OUT))
