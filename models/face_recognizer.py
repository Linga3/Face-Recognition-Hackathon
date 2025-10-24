import numpy as np
import os
import pickle
import cv2

# Import face_recognition at the top
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
    print("✓ face_recognition loaded successfully in face_recognizer")
except ImportError as e:
    print(f"✗ face_recognition not available: {e}")
    FACE_RECOGNITION_AVAILABLE = False

class FaceRecognizer:
    def __init__(self, known_faces_folder):
        self.known_faces_folder = known_faces_folder
        self.known_face_encodings = []
        self.known_face_metadata = []
        self.model_path = os.path.join(known_faces_folder, 'face_model.pkl')
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load known face encodings from disk or create new database"""
        if os.path.exists(self.model_path):
            print("Loading existing face database...")
            try:
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data['encodings']
                    self.known_face_metadata = data['metadata']
                print(f"Loaded {len(self.known_face_encodings)} known faces")
            except Exception as e:
                print(f"Error loading face database: {e}")
                self.known_face_encodings = []
                self.known_face_metadata = []
        else:
            print("No existing face database found. Creating new one.")
            self.known_face_encodings = []
            self.known_face_metadata = []
    
    def save_known_faces(self):
        """Save current face database to disk"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            data = {
                'encodings': self.known_face_encodings,
                'metadata': self.known_face_metadata
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(data, f)
            print(f"Saved {len(self.known_face_encodings)} faces to database")
        except Exception as e:
            print(f"Error saving face database: {e}")
    
    def register_face(self, image_path, user_data):
        """Register a new face in the system"""
        print(f"Registering face for {user_data['full_name']}...")
        
        if not FACE_RECOGNITION_AVAILABLE:
            return False, "Face recognition library not available. Please install face-recognition."
        
        try:
            # Load and encode the image
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if len(face_encodings) == 0:
                return False, "No face detected in the image"
            
            if len(face_encodings) > 1:
                return False, "Multiple faces detected. Please upload an image with only one face."
            
            # Check if face already exists
            if len(self.known_face_encodings) > 0:
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, 
                    face_encodings[0],
                    tolerance=0.5
                )
                
                if True in matches:
                    return False, "This face is already registered in the system"
            
            # Add to known faces
            self.known_face_encodings.append(face_encodings[0])
            self.known_face_metadata.append(user_data)
            self.save_known_faces()
            
            return True, "Face registered successfully"
            
        except Exception as e:
            print(f"Error during face registration: {str(e)}")
            return False, f"Error during face registration: {str(e)}"
    
    def verify_face(self, image_path, threshold=0.6):
        """Verify if a face matches any in the database"""
        print("Verifying face...")
        
        if not FACE_RECOGNITION_AVAILABLE:
            return False, [], "Face recognition library not available. Please install face-recognition."
        
        try:
            # Load and encode the image
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if len(face_encodings) == 0:
                return False, [], "No face detected in the image"
            
            if len(face_encodings) > 1:
                return False, [], "Multiple faces detected. Please upload an image with only one face."
            
            # If no faces in database
            if len(self.known_face_encodings) == 0:
                return False, [], "No registered faces in the system"
            
            # Compare with known faces
            face_distances = face_recognition.face_distance(
                self.known_face_encodings, 
                face_encodings[0]
            )
            
            # Find best match
            best_match_index = np.argmin(face_distances)
            best_distance = face_distances[best_match_index]
            
            matches = []
            for i, distance in enumerate(face_distances):
                if distance <= threshold:
                    matches.append({
                        'user_data': self.known_face_metadata[i],
                        'confidence': 1 - distance,
                        'distance': distance
                    })
            
            # Sort by confidence (highest first)
            matches.sort(key=lambda x: x['confidence'], reverse=True)
            
            if best_distance <= threshold:
                return True, matches, f"Face verified with confidence: {1 - best_distance:.2f}"
            else:
                return False, matches, f"No match found. Best distance: {best_distance:.2f}"
                
        except Exception as e:
            print(f"Error during face verification: {str(e)}")
            return False, [], f"Error during face verification: {str(e)}"
    
    def get_face_quality_score(self, image_path):
        """Evaluate the quality of the face image"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return 0.0, "Unable to read image"
                
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces using OpenCV
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                return 0.0, "No face detected"
            
            # Calculate quality metrics
            x, y, w, h = faces[0]
            face_region = gray[y:y+h, x:x+w]
            
            # Brightness score
            brightness = np.mean(face_region)
            brightness_score = 1.0 - abs(brightness - 127) / 127
            
            # Contrast score
            contrast = np.std(face_region)
            contrast_score = min(contrast / 64, 1.0)
            
            # Sharpness score (using Laplacian variance)
            sharpness = cv2.Laplacian(face_region, cv2.CV_64F).var()
            sharpness_score = min(sharpness / 1000, 1.0)
            
            # Overall quality score
            quality_score = (brightness_score + contrast_score + sharpness_score) / 3
            
            feedback = []
            if brightness_score < 0.7:
                feedback.append("Poor lighting")
            if contrast_score < 0.7:
                feedback.append("Low contrast")
            if sharpness_score < 0.7:
                feedback.append("Blurry image")
            
            feedback_text = "Good quality" if not feedback else ", ".join(feedback)
            
            return quality_score, feedback_text
            
        except Exception as e:
            print(f"Error in quality assessment: {str(e)}")
            return 0.5, "Quality assessment failed"