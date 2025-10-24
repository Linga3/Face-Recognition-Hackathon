// Identity Integrity Platform - Main JavaScript
class IdentityPlatform {
    constructor() {
        this.initializeEventListeners();
        this.initializeWebcam();
        this.setupRealTimeValidation();
    }

    initializeEventListeners() {
        // Form validation and enhancement
        this.setupFormValidation();
        this.setupImageProcessing();
        this.setupRealTimeFeedback();
    }

    setupFormValidation() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    this.showFormError('Please fix the errors before submitting.');
                }
            });

            // Real-time input validation
            const inputs = form.querySelectorAll('input, select');
            inputs.forEach(input => {
                input.addEventListener('blur', () => this.validateField(input));
                input.addEventListener('input', () => this.clearFieldError(input));
            });
        });
    }

    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[required], select[required]');
        
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        // Special validation for file inputs
        const fileInputs = form.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            if (input.files.length === 0) {
                this.showFieldError(input, 'This field is required');
                isValid = false;
            } else if (!this.validateImageFile(input.files[0])) {
                this.showFieldError(input, 'Please upload a valid image file (JPEG, PNG)');
                isValid = false;
            }
        });

        return isValid;
    }

    validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';

        switch (field.type) {
            case 'text':
                if (field.name === 'full_name') {
                    if (value.length < 2) {
                        errorMessage = 'Name must be at least 2 characters long';
                        isValid = false;
                    } else if (!/^[a-zA-Z\s]+$/.test(value)) {
                        errorMessage = 'Name can only contain letters and spaces';
                        isValid = false;
                    }
                } else if (field.name === 'application_id') {
                    if (value.length < 3) {
                        errorMessage = 'Application ID must be at least 3 characters long';
                        isValid = false;
                    }
                }
                break;

            case 'number':
                if (field.name === 'age') {
                    const age = parseInt(value);
                    if (isNaN(age) || age < 16 || age > 100) {
                        errorMessage = 'Age must be between 16 and 100';
                        isValid = false;
                    }
                }
                break;

            case 'file':
                if (field.files.length > 0) {
                    isValid = this.validateImageFile(field.files[0]);
                    if (!isValid) {
                        errorMessage = 'Please upload a valid image file (JPEG, PNG) under 5MB';
                    }
                }
                break;

            case 'select-one':
                if (!value) {
                    errorMessage = 'Please select an option';
                    isValid = false;
                }
                break;
        }

        if (!isValid) {
            this.showFieldError(field, errorMessage);
        } else {
            this.clearFieldError(field);
        }

        return isValid;
    }

    validateImageFile(file) {
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        const maxSize = 5 * 1024 * 1024; // 5MB

        if (!validTypes.includes(file.type)) {
            return false;
        }

        if (file.size > maxSize) {
            return false;
        }

        return true;
    }

    showFieldError(field, message) {
        this.clearFieldError(field);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            color: #e74c3c;
            font-size: 0.8rem;
            margin-top: 5px;
            padding: 5px;
            background: #ffeaea;
            border-radius: 4px;
        `;

        field.parentNode.appendChild(errorDiv);
        field.style.borderColor = '#e74c3c';
    }

    clearFieldError(field) {
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        field.style.borderColor = '';
    }

    showFormError(message) {
        // Remove existing error
        const existingError = document.querySelector('.form-error-message');
        if (existingError) {
            existingError.remove();
        }

        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error-message';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            background: #e74c3c;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: 500;
        `;

        const form = document.querySelector('form');
        form.insertBefore(errorDiv, form.firstChild);

        // Auto remove after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    setupImageProcessing() {
        const fileInputs = document.querySelectorAll('input[type="file"]');
        
        fileInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                this.handleImageUpload(e.target);
            });
        });
    }

    handleImageUpload(input) {
        const file = input.files[0];
        if (!file) return;

        // Validate file
        if (!this.validateImageFile(file)) {
            this.showFieldError(input, 'Please upload a valid image file (JPEG, PNG) under 5MB');
            input.value = '';
            return;
        }

        // Show preview
        this.showImagePreview(input, file);

        // Analyze image quality (simulated)
        this.analyzeImageQuality(file).then(quality => {
            this.showQualityFeedback(quality);
        });

        this.clearFieldError(input);
    }

    showImagePreview(input, file) {
        // Remove existing preview
        const existingPreview = input.parentNode.querySelector('.image-preview');
        if (existingPreview) {
            existingPreview.remove();
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const previewDiv = document.createElement('div');
            previewDiv.className = 'image-preview';
            previewDiv.style.cssText = `
                margin-top: 10px;
                text-align: center;
            `;

            const img = document.createElement('img');
            img.src = e.target.result;
            img.style.cssText = `
                max-width: 200px;
                max-height: 200px;
                border-radius: 8px;
                border: 2px solid #3498db;
            `;

            previewDiv.appendChild(img);
            input.parentNode.appendChild(previewDiv);
        };

        reader.readAsDataURL(file);
    }

    async analyzeImageQuality(file) {
        // Simulate image quality analysis
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);

                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const quality = this.calculateImageQuality(imageData);
                
                resolve({
                    score: quality,
                    feedback: this.generateQualityFeedback(quality),
                    dimensions: { width: img.width, height: img.height }
                });
            };
            img.src = URL.createObjectURL(file);
        });
    }

    calculateImageQuality(imageData) {
        // Simplified image quality calculation
        const data = imageData.data;
        let brightness = 0;
        let contrast = 0;

        // Calculate brightness
        for (let i = 0; i < data.length; i += 4) {
            brightness += (data[i] + data[i + 1] + data[i + 2]) / 3;
        }
        brightness /= (data.length / 4);

        // Simple contrast estimation (standard deviation approximation)
        let sumSquaredDiff = 0;
        for (let i = 0; i < data.length; i += 4) {
            const pixelBrightness = (data[i] + data[i + 1] + data[i + 2]) / 3;
            sumSquaredDiff += Math.pow(pixelBrightness - brightness, 2);
        }
        contrast = Math.sqrt(sumSquaredDiff / (data.length / 4));

        // Normalize scores
        const brightnessScore = 1 - Math.abs(brightness - 127) / 127;
        const contrastScore = Math.min(contrast / 64, 1);
        
        return (brightnessScore * 0.4 + contrastScore * 0.6);
    }

    generateQualityFeedback(qualityScore) {
        if (qualityScore >= 0.8) {
            return 'Excellent image quality';
        } else if (qualityScore >= 0.6) {
            return 'Good image quality';
        } else if (qualityScore >= 0.4) {
            return 'Fair image quality - consider retaking with better lighting';
        } else {
            return 'Poor image quality - please retake with better lighting and focus';
        }
    }

    showQualityFeedback(quality) {
        // Remove existing feedback
        const existingFeedback = document.querySelector('.quality-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'quality-feedback';
        feedbackDiv.style.cssText = `
            margin-top: 10px;
            padding: 10px;
            border-radius: 6px;
            font-size: 0.9rem;
            text-align: center;
            background: ${quality.score >= 0.6 ? '#e8f5e8' : '#fff3cd'};
            border: 1px solid ${quality.score >= 0.6 ? '#d4edda' : '#ffeaa7'};
            color: ${quality.score >= 0.6 ? '#155724' : '#856404'};
        `;

        feedbackDiv.innerHTML = `
            <strong>Quality Score: ${Math.round(quality.score * 100)}%</strong><br>
            ${quality.feedback}<br>
            <small>Dimensions: ${quality.dimensions.width} × ${quality.dimensions.height}px</small>
        `;

        const fileInput = document.querySelector('input[type="file"]');
        fileInput.parentNode.appendChild(feedbackDiv);
    }

    initializeWebcam() {
        this.video = document.getElementById('webcam');
        this.canvas = document.getElementById('canvas');
        this.captureBtn = document.getElementById('captureBtn');
        this.fileInput = document.querySelector('input[type="file"][accept="image/*"]');

        if (this.video && this.captureBtn) {
            this.setupWebcam();
        }
    }

    async setupWebcam() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'user'
                },
                audio: false
            });

            this.video.srcObject = stream;
            this.captureBtn.disabled = false;

            // Add face detection overlay
            this.setupFaceDetectionOverlay();

        } catch (error) {
            console.error('Error accessing webcam:', error);
            this.showWebcamError('Unable to access webcam. Please check permissions.');
        }
    }

    setupFaceDetectionOverlay() {
        // This would integrate with a face detection API
        // For now, we'll simulate face detection feedback
        this.video.addEventListener('play', () => {
            this.simulateFaceDetection();
        });
    }

    simulateFaceDetection() {
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 200px;
            height: 250px;
            border: 3px solid #3498db;
            border-radius: 10px;
            pointer-events: none;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #3498db;
            font-weight: bold;
            background: rgba(52, 152, 219, 0.1);
        `;
        overlay.textContent = 'Position face here';

        const webcamContainer = document.getElementById('webcamContainer');
        webcamContainer.style.position = 'relative';
        webcamContainer.appendChild(overlay);
    }

    captureWebcamPhoto() {
        if (!this.video || !this.canvas) return;

        const context = this.canvas.getContext('2d');
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
        context.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);

        this.canvas.toBlob((blob) => {
            const file = new File([blob], 'webcam_capture.jpg', { type: 'image/jpeg' });
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            
            if (this.fileInput) {
                this.fileInput.files = dataTransfer.files;
                
                // Trigger change event
                const event = new Event('change', { bubbles: true });
                this.fileInput.dispatchEvent(event);
            }

            this.showCaptureSuccess();
        }, 'image/jpeg', 0.9);
    }

    showCaptureSuccess() {
        const successMsg = document.createElement('div');
        successMsg.style.cssText = `
            color: #27ae60;
            background: #e8f5e8;
            padding: 10px;
            border-radius: 6px;
            margin-top: 10px;
            text-align: center;
            font-weight: 500;
        `;
        successMsg.textContent = '✓ Photo captured successfully!';

        this.captureBtn.parentNode.appendChild(successMsg);

        setTimeout(() => {
            successMsg.remove();
        }, 3000);
    }

    showWebcamError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            color: #e74c3c;
            background: #ffeaea;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            text-align: center;
        `;
        errorDiv.textContent = message;

        const webcamSection = document.querySelector('.webcam-section');
        if (webcamSection) {
            webcamSection.appendChild(errorDiv);
        }
    }

    setupRealTimeValidation() {
        // Add input masks and formatting
        this.setupInputMasks();
        this.setupCharacterCounters();
    }

    setupInputMasks() {
        const nameInput = document.querySelector('input[name="full_name"]');
        if (nameInput) {
            nameInput.addEventListener('input', (e) => {
                e.target.value = e.target.value.replace(/[^a-zA-Z\s]/g, '');
            });
        }

        const appIdInput = document.querySelector('input[name="application_id"]');
        if (appIdInput) {
            appIdInput.addEventListener('input', (e) => {
                e.target.value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
            });
        }
    }

    setupCharacterCounters() {
        const textInputs = document.querySelectorAll('input[type="text"], textarea');
        
        textInputs.forEach(input => {
            const counter = document.createElement('div');
            counter.className = 'character-counter';
            counter.style.cssText = `
                font-size: 0.8rem;
                color: #7f8c8d;
                text-align: right;
                margin-top: 5px;
            `;

            input.parentNode.appendChild(counter);

            input.addEventListener('input', () => {
                const maxLength = input.maxLength || 100;
                const currentLength = input.value.length;
                counter.textContent = `${currentLength}/${maxLength}`;
                
                if (currentLength > maxLength * 0.8) {
                    counter.style.color = '#e74c3c';
                } else {
                    counter.style.color = '#7f8c8d';
                }
            });

            // Trigger initial count
            input.dispatchEvent(new Event('input'));
        });
    }

    setupRealTimeFeedback() {
        // Add loading states for form submissions
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', () => {
                this.showLoadingState(form);
            });
        });
    }

    showLoadingState(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (!submitBtn) return;

        const originalText = submitBtn.textContent;
        submitBtn.innerHTML = `
            <div class="loading-spinner"></div>
            Processing...
        `;
        submitBtn.disabled = true;

        // Add spinner styles
        const style = document.createElement('style');
        style.textContent = `
            .loading-spinner {
                display: inline-block;
                width: 16px;
                height: 16px;
                border: 2px solid #ffffff;
                border-radius: 50%;
                border-top-color: transparent;
                animation: spin 1s ease-in-out infinite;
                margin-right: 8px;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);

        // Store original state for potential reset
        submitBtn.dataset.originalText = originalText;
    }

    resetLoadingState(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (!submitBtn || !submitBtn.dataset.originalText) return;

        submitBtn.innerHTML = submitBtn.dataset.originalText;
        submitBtn.disabled = false;
    }

    // Utility methods for API interactions
    async verifyFaceAPI(imageFile) {
        const formData = new FormData();
        formData.append('face_image', imageFile);

        try {
            const response = await fetch('/api/verify', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Verification failed');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Error handling utility
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            transform: translateX(400px);
            transition: transform 0.3s ease;
            max-width: 300px;
        `;

        const colors = {
            success: '#27ae60',
            error: '#e74c3c',
            warning: '#f39c12',
            info: '#3498db'
        };

        notification.style.background = colors[type] || colors.info;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Auto remove
        setTimeout(() => {
            notification.style.transform = 'translateX(400px)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }
}

// Additional utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize the platform when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.identityPlatform = new IdentityPlatform();

    // Add global error handler
    window.addEventListener('error', (event) => {
        console.error('Global error:', event.error);
        if (window.identityPlatform) {
            window.identityPlatform.showNotification('An unexpected error occurred', 'error');
        }
    });

    // Add beforeunload handler for form protection
    window.addEventListener('beforeunload', (event) => {
        const forms = document.querySelectorAll('form');
        const hasData = Array.from(forms).some(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            return Array.from(inputs).some(input => {
                if (input.type === 'file') return input.files.length > 0;
                return input.value.trim() !== '';
            });
        });

        if (hasData) {
            event.preventDefault();
            event.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
        }
    });
});

// Webcam capture handler
document.addEventListener('DOMContentLoaded', () => {
    const captureBtn = document.getElementById('captureBtn');
    if (captureBtn) {
        captureBtn.addEventListener('click', () => {
            if (window.identityPlatform) {
                window.identityPlatform.captureWebcamPhoto();
            }
        });
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IdentityPlatform;
}