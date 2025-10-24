from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

from config import Config, allowed_file
from models.face_recognizer import FaceRecognizer
from models.anomaly_detector import AnomalyDetector
from utils.face_utils import validate_face_pose, enhance_image_quality
import cv2

app = Flask(__name__)
app.config.from_object(Config)

# Initialize components
face_recognizer = FaceRecognizer(app.config['KNOWN_FACES_FOLDER'])
anomaly_detector = AnomalyDetector()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'face_image' not in request.files:
            return render_template('register.html', error='No file selected')
        
        file = request.files['face_image']
        if file.filename == '':
            return render_template('register.html', error='No file selected')
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            
            # Get form data
            user_data = {
                'application_id': request.form.get('application_id'),
                'full_name': request.form.get('full_name'),
                'age': int(request.form.get('age', 0)),
                'exam_type': request.form.get('exam_type'),
                'location': request.form.get('location'),
                'timestamp': datetime.now()
            }
            
            # Validate face pose
            pose_valid, pose_message = validate_face_pose(filepath)
            if not pose_valid:
                os.remove(filepath)
                return render_template('register.html', error=pose_message)
            
            # Check image quality
            quality_score, quality_feedback = face_recognizer.get_face_quality_score(filepath)
            if quality_score < 0.5:
                os.remove(filepath)
                return render_template('register.html', 
                                     error=f'Poor image quality: {quality_feedback}. Please upload a clearer image.')
            
            # Register face
            success, message = face_recognizer.register_face(filepath, user_data)
            
            # Clean up temporary file
            os.remove(filepath)
            
            if success:
                return render_template('register.html', 
                                     success=f'Registration successful! Quality score: {quality_score:.2f}')
            else:
                return render_template('register.html', error=message)
    
    return render_template('register.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        if 'face_image' not in request.files:
            return render_template('verify.html', error='No file selected')
        
        file = request.files['face_image']
        if file.filename == '':
            return render_template('verify.html', error='No file selected')
        
        if file and allowed_file(file.filename):
            # Save uploaded file
            filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            
            # Verify face
            is_verified, matches, message = face_recognizer.verify_face(
                filepath, 
                threshold=app.config['FACE_MATCH_THRESHOLD']
            )
            
            # Check image quality
            quality_score, quality_feedback = face_recognizer.get_face_quality_score(filepath)
            
            # Clean up
            os.remove(filepath)
            
            return render_template('results.html', 
                                 verified=is_verified,
                                 matches=matches,
                                 message=message,
                                 quality_score=quality_score,
                                 quality_feedback=quality_feedback)
    
    return render_template('verify.html')

@app.route('/demo_register', methods=['POST'])
def demo_register():
    """Demo endpoint that simulates registration without face_recognition"""
    user_data = {
        'application_id': request.form.get('application_id'),
        'full_name': request.form.get('full_name'),
        'age': int(request.form.get('age', 0)),
        'exam_type': request.form.get('exam_type'),
        'location': request.form.get('location'),
        'timestamp': datetime.now()
    }
    
    # Simulate successful registration
    return jsonify({
        'success': True,
        'message': 'Demo registration successful (face_recognition not available)',
        'user_data': user_data
    })

@app.route('/api/verify', methods=['POST'])
def api_verify():
    """API endpoint for programmatic face verification"""
    if 'face_image' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['face_image']
    if file and allowed_file(file.filename):
        filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        
        # Verify face
        is_verified, matches, message = face_recognizer.verify_face(
            filepath, 
            threshold=app.config['FACE_MATCH_THRESHOLD']
        )
        
        # Clean up
        os.remove(filepath)
        
        return jsonify({
            'verified': is_verified,
            'matches': matches,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/admin/analytics')
def admin_analytics():
    """Admin panel for system analytics"""
    total_registrations = len(face_recognizer.known_face_metadata)
    
    # Basic statistics
    exams = {}
    locations = {}
    for metadata in face_recognizer.known_face_metadata:
        exam_type = metadata.get('exam_type', 'Unknown')
        location = metadata.get('location', 'Unknown')
        
        exams[exam_type] = exams.get(exam_type, 0) + 1
        locations[location] = locations.get(location, 0) + 1
    
    return render_template('admin_analytics.html',
                         total_registrations=total_registrations,
                         exams=exams,
                         locations=locations)

@app.route('/system_status')
def system_status():
    """Check system status and dependencies"""
    status = {
        'face_recognition_available': hasattr(face_recognizer, 'FACE_RECOGNITION_AVAILABLE') and face_recognizer.FACE_RECOGNITION_AVAILABLE,
        'registered_faces': len(face_recognizer.known_face_metadata),
        'database_path': face_recognizer.model_path
    }
    return jsonify(status)

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data/temp', exist_ok=True)
    os.makedirs('data/known_faces', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("Starting Identity Integrity Platform...")
    print("Access the application at: http://localhost:8502")
    print("Check system status at: http://localhost:8502/system_status")
    
    app.run(debug=True, host='0.0.0.0', port=8502)