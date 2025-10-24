import cv2
import numpy as np
from PIL import Image, ImageDraw

# Import face_recognition at the top of the file
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
    print("✓ face_recognition loaded successfully in face_utils")
except ImportError as e:
    print(f"✗ face_recognition not available: {e}")
    FACE_RECOGNITION_AVAILABLE = False

def draw_face_landmarks(image_path, output_path):
    """Draw facial landmarks on image for visualization"""
    if not FACE_RECOGNITION_AVAILABLE:
        return False, "face_recognition library not available"
        
    try:
        image = face_recognition.load_image_file(image_path)
        face_landmarks_list = face_recognition.face_landmarks(image)
        
        pil_image = Image.fromarray(image)
        draw = ImageDraw.Draw(pil_image)
        
        for face_landmarks in face_landmarks_list:
            # Draw each facial feature
            for facial_feature in face_landmarks.keys():
                points = face_landmarks[facial_feature]
                draw.line(points + [points[0]], fill='green', width=2)
        
        pil_image.save(output_path)
        return True, "Landmarks drawn successfully"
    except Exception as e:
        print(f"Error drawing landmarks: {str(e)}")
        return False, f"Error drawing landmarks: {str(e)}"

def enhance_image_quality(image_path):
    """Apply basic image enhancement techniques"""
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None
            
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        
        # Merge the CLAHE enhanced L channel back with A and B channels
        limg = cv2.merge((cl, a, b))
        
        # Convert back to BGR color space
        enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        
        return enhanced
    except Exception as e:
        print(f"Error enhancing image: {str(e)}")
        return None

def validate_face_pose(image_path):
    """Validate that face is in acceptable pose (frontal)"""
    if not FACE_RECOGNITION_AVAILABLE:
        # Fallback validation using OpenCV only
        return validate_face_pose_opencv(image_path)
        
    try:
        image = face_recognition.load_image_file(image_path)
        face_landmarks_list = face_recognition.face_landmarks(image)
        
        if len(face_landmarks_list) == 0:
            return False, "No face detected"
        
        face_landmarks = face_landmarks_list[0]
        
        # Simple pose validation using eye and nose landmarks
        if 'left_eye' not in face_landmarks or 'right_eye' not in face_landmarks or 'nose_tip' not in face_landmarks:
            return False, "Unable to detect facial features properly"
            
        left_eye = face_landmarks['left_eye']
        right_eye = face_landmarks['right_eye']
        
        # Calculate eye centers
        left_eye_center = np.mean(left_eye, axis=0)
        right_eye_center = np.mean(right_eye, axis=0)
        
        # Check if eyes are roughly horizontal
        eye_slope = abs((left_eye_center[1] - right_eye_center[1]) / 
                       (left_eye_center[0] - right_eye_center[0] + 1e-6))
        
        if eye_slope > 0.3:  # Too much rotation
            return False, "Face is not frontal. Please look directly at the camera."
        
        return True, "Pose is acceptable"
    except Exception as e:
        print(f"Error in pose validation with face_recognition: {str(e)}")
        # Fallback to OpenCV
        return validate_face_pose_opencv(image_path)

def validate_face_pose_opencv(image_path):
    """Fallback face pose validation using OpenCV only"""
    try:
        image = cv2.imread(image_path)
        if image is None:
            return False, "Unable to read image"
            
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces using OpenCV
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return False, "No face detected"
        
        # For OpenCV, we can only check if a face is detected
        # More sophisticated pose detection would require additional models
        x, y, w, h = faces[0]
        
        # Basic aspect ratio check
        aspect_ratio = w / h
        if aspect_ratio < 0.7 or aspect_ratio > 1.3:
            return False, "Face appears rotated. Please look directly at the camera."
        
        return True, "Face detected and appears frontal"
        
    except Exception as e:
        print(f"Error in OpenCV pose validation: {str(e)}")
        return False, f"Error validating face: {str(e)}"