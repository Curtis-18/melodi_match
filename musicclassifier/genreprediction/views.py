from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import HttpResponse
from .forms import SignUpForm, LoginForm
import librosa
import numpy as np
import tempfile
import os
from pydub import AudioSegment
import joblib
import sounddevice as sd
from django.db.models import Count
from django.contrib.auth.models import User
from .models import Prediction,Genre,Review
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required

# Load the pre-trained model
model = joblib.load('genreprediction/model/genre_classifier.pkl')  # Adjust the path to your model file

# Feature extraction function for music prediction
def extract_features(y, sr):
    """Extract features from audio signal."""
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    return np.concatenate([
        np.mean(mfcc, axis=1),
        np.mean(spectral_centroid, axis=1),
        np.mean(spectral_bandwidth, axis=1)
    ])

def record_audio(duration=5, fs=22050):
    """Record audio from the microphone."""
    print("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    return recording.flatten()


# Signup view

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the new user
            login(request, user)  # Log them in automatically
            messages.success(request, 'Account created successfully!')
            return redirect('home')  # Now they can access @login_required pages
    else:
        form = SignUpForm()
    return render(request, 'genreprediction/signup.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'You have logged in successfully.')
                return redirect('home')
            else:
                messages.error(request, 'Invalid credentials.')
    else:
        form = LoginForm()
    return render(request, 'genreprediction/login.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')
@login_required
def home_view(request):
    # Get most predicted genres with proper counts
    top_genres = Genre.objects.annotate(
        count=Count('prediction')
    ).order_by('-count')[:5]
    
    # Get total registered users
    active_users = User.objects.count()

    # Testimonials (reviews)
    testimonials = Review.objects.select_related('user')[:6]

    # Handle review form
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                # Set predicted_genre to None since we're not collecting it
                review.predicted_genre = None
                review.save()
                messages.success(request, 'Thank you for your review!')
                return redirect('home')
        else:
            messages.error(request, 'You must be logged in to submit a review.')
            return redirect('login')
    else:
        form = ReviewForm()

    context = {
        'top_genres': top_genres,
        'active_users': active_users,
        'testimonials': testimonials,
        'form': form,
    }
    
    return render(request, 'genreprediction/home.html', context)
@login_required
def predict_genre(request):
    """Handle genre prediction for uploaded or recorded audio."""
    context = {'prediction': None, 'error': None}
    
    if request.method == 'POST':
        try:
            # Initialize variables
            y, sr = None, None
            
            # Check if a file has been uploaded
            if 'file' in request.FILES:
                uploaded_file = request.FILES['file']
                
                # Validate file extension
                valid_extensions = ['.webm', '.mp3', '.wav']
                if not any(uploaded_file.name.lower().endswith(ext) for ext in valid_extensions):
                    raise ValueError("Invalid file format. Please upload .webm, .mp3, or .wav files.")
                
                # Save the uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_webm:
                    for chunk in uploaded_file.chunks():
                        temp_webm.write(chunk)
                    webm_path = temp_webm.name

                # Convert to WAV format
                wav_path = webm_path.replace('.webm', '.wav')
                try:
                    sound = AudioSegment.from_file(webm_path)
                    sound = sound.set_channels(1).set_frame_rate(22050)
                    sound.export(wav_path, format="wav")
                    
                    # Load and process audio
                    y, sr = librosa.load(wav_path, sr=22050)
                except Exception as e:
                    raise ValueError(f"Error processing audio file: {str(e)}")
                finally:
                    # Clean up temporary files
                    if os.path.exists(webm_path):
                        os.remove(webm_path)
                    if os.path.exists(wav_path):
                        os.remove(wav_path)

            # Check if recording was requested
            elif 'record' in request.POST:
                try:
                    y = record_audio(duration=15)
                    sr = 22050
                except Exception as e:
                    raise ValueError(f"Error recording audio: {str(e)}")

            # If we have audio data, extract features and predict
            if y is not None and sr is not None:
                features = extract_features(y, sr).reshape(1, -1)
                context['prediction'] = model.predict(features)[0]
                
        except Exception as e:
            context['error'] = str(e)
            print(f"Error during prediction: {str(e)}")

    return render(request, 'genreprediction/predict.html', context)