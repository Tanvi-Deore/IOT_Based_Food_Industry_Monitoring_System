import cv2
import numpy as np

# Convert RGB to HSV for better color detection
def convert_to_hsv(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Define the lower and upper bounds for the green color (ripe apples)
lower_green = np.array([23, 50, 50])
upper_green = np.array([90, 255, 255])

# Define the lower and upper bounds for the brown color (rotten apples)
lower_brown = np.array([0, 50, 50])
upper_brown = np.array([20, 255, 255])

# Apply morphological operations to remove noise and fill gaps
def preprocess_mask(mask):
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask

# Determine if the apple is fresh or rotten based on color, shape, and texture
def determine_freshness(contour, hsv_image, ripe_mask, rotten_mask):
    area = cv2.contourArea(contour)
    if area > 100:
        x, y, w, h = cv2.boundingRect(contour)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = float(area) / hull_area
        mean_intensity_ripe = cv2.mean(hsv_image[y:y+h, x:x+w], mask=ripe_mask[y:y+h, x:x+w])[2]
        mean_intensity_rotten = cv2.mean(hsv_image[y:y+h, x:x+w], mask=rotten_mask[y:y+h, x:x+w])[2]
        edges = cv2.Canny((ripe_mask + rotten_mask)[y:y+h, x:x+w], 30, 100)
        texture_variance = np.var(hsv_image[y:y+h, x:x+w, 1])
        if (mean_intensity_ripe > mean_intensity_rotten) and (solidity > 0.8) and (texture_variance > 100):
            return True
    return False

# Capture video from camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    hsv_frame = convert_to_hsv(frame)
    
    ripe_mask = cv2.inRange(hsv_frame, lower_green, upper_green)
    rotten_mask = cv2.inRange(hsv_frame, lower_brown, upper_brown)
    
    combined_mask = preprocess_mask(ripe_mask + rotten_mask)
    
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        if determine_freshness(contour, hsv_frame, ripe_mask, rotten_mask):
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green border for fresh apples
            cv2.putText(frame, "Fresh", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red border for rotten apples
            cv2.putText(frame, "Rotten", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    cv2.imshow('Camera Feed', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
