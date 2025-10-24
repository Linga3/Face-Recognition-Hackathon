import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

class AnomalyDetector:
    def __init__(self, model_path='models/anomaly_detector.pkl'):
        self.model_path = model_path
        self.scaler = StandardScaler()
        self.model = None
        self.is_fitted = False
        
        if os.path.exists(model_path):
            self.load_model()
        else:
            self.model = IsolationForest(contamination=0.1, random_state=42)
    
    def load_model(self):
        """Load trained anomaly detection model"""
        try:
            data = joblib.load(self.model_path)
            self.model = data['model']
            self.scaler = data['scaler']
            self.is_fitted = data['is_fitted']
        except:
            self.model = IsolationForest(contamination=0.1, random_state=42)
            self.is_fitted = False
    
    def save_model(self):
        """Save trained anomaly detection model"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        data = {
            'model': self.model,
            'scaler': self.scaler,
            'is_fitted': self.is_fitted
        }
        joblib.dump(data, self.model_path)
    
    def extract_features(self, face_encoding, user_data):
        """Extract features for anomaly detection"""
        features = []
        
        # Face encoding features (first 10 dimensions)
        features.extend(face_encoding[:10])
        
        # Demographic features (if available)
        if 'age' in user_data:
            features.append(user_data['age'])
        else:
            features.append(30)  # Default age
        
        # Add timestamp-based features
        import time
        current_hour = time.localtime().tm_hour
        features.append(current_hour)
        
        return np.array(features)
    
    def detect_anomalies(self, face_encodings, user_data_list, threshold=0.8):
        """Detect anomalous registration attempts"""
        if len(face_encodings) < 10:  # Need minimum samples for meaningful detection
            return [], "Insufficient data for anomaly detection"
        
        # Extract features
        features = []
        for encoding, user_data in zip(face_encodings, user_data_list):
            features.append(self.extract_features(encoding, user_data))
        
        features = np.array(features)
        
        # Fit scaler and model if not fitted
        if not self.is_fitted:
            features_scaled = self.scaler.fit_transform(features)
            self.model.fit(features_scaled)
            self.is_fitted = True
            self.save_model()
        else:
            features_scaled = self.scaler.transform(features)
        
        # Predict anomalies
        anomaly_scores = self.model.decision_function(features_scaled)
        predictions = self.model.predict(features_scaled)
        
        anomalies = []
        for i, (score, pred) in enumerate(zip(anomaly_scores, predictions)):
            if pred == -1 or score < -threshold:
                anomalies.append({
                    'index': i,
                    'user_data': user_data_list[i],
                    'anomaly_score': score,
                    'is_anomaly': True
                })
        
        return anomalies, f"Found {len(anomalies)} potential anomalies"
    
    def check_registration_pattern(self, current_application, previous_applications):
        """Check for suspicious registration patterns"""
        warnings = []
        
        # Check for rapid successive registrations
        if len(previous_applications) > 0:
            time_diff = (current_application['timestamp'] - 
                        previous_applications[-1]['timestamp']).total_seconds()
            if time_diff < 3600:  # Less than 1 hour
                warnings.append("Rapid successive registration detected")
        
        # Check for similar demographic information
        similar_demographics = 0
        for prev_app in previous_applications[-5:]:  # Check last 5 applications
            if (prev_app.get('age', 0) == current_application.get('age', 1) and
                prev_app.get('location', '') == current_application.get('location', '')):
                similar_demographics += 1
        
        if similar_demographics >= 2:
            warnings.append("Multiple registrations with similar demographics")
        
        return warnings