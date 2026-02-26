# 🎵 MelodiMatch

**MelodiMatch** is an AI-powered music genre prediction web application built with Django. Upload an audio file or record live from your microphone, and the app will analyze the audio features and predict the music genre using a pre-trained machine learning model.

---

## ✨ Features

- 🎤 **Live Recording** — Record audio directly from your browser microphone
- 📁 **File Upload** — Upload `.mp3`, `.wav`, or `.webm` audio files for analysis
- 🤖 **AI Genre Prediction** — Uses a pre-trained ML classifier to identify music genres
- 👤 **User Authentication** — Full signup, login, and logout system
- 🌟 **Community Reviews** — Authenticated users can leave text reviews on the homepage
- 📊 **Top Genres Dashboard** — Displays the most predicted genres across all users
- 👥 **Active Users Counter** — Shows the total number of registered users

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 5.1 (Python) |
| **Database** | SQLite3 |
| **Audio Processing** | `librosa`, `pydub`, `sounddevice` |
| **ML Model** | Scikit-learn (pre-trained, `joblib`-serialized) |
| **Frontend** | Django Templates, Vanilla CSS, Font Awesome, Google Fonts (Poppins) |

---

## 📁 Project Structure

```
melodi_match/
└── musicclassifier/           # Django project root
    ├── manage.py
    ├── db.sqlite3             # SQLite database
    ├── musicclassifier/       # Project-level configuration
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── asgi.py
    └── genreprediction/       # Main Django app
        ├── models.py          # Database models
        ├── views.py           # View logic & ML inference
        ├── forms.py           # Django forms
        ├── urls.py            # App-level URL routing
        ├── admin.py           # Django admin registration
        ├── apps.py
        ├── migrations/        # Database migrations
        ├── model/
        │   └── genre_classifier.pkl  # Pre-trained ML model
        └── templates/
            └── genreprediction/
                ├── home.html      # Landing/dashboard page
                ├── predict.html   # Genre prediction page
                ├── login.html     # Login page
                └── signup.html    # Signup page
```

---

## 🗃️ Data Models

### `Genre`
Stores music genre information.
- `name` — Unique genre name
- `description` — Optional description
- `color` — Hex color code for UI display
- `spotify_id` — Reserved for future Spotify integration

### `Prediction`
Logs each genre prediction made by a user.
- `user` — ForeignKey to Django's `User` model
- `audio_file` — Uploaded audio file path
- `predicted_genre` — ForeignKey to `Genre`
- `confidence` — Model confidence score (float)
- `features` — JSON blob of extracted audio features
- `feedback` — Optional boolean for user accuracy feedback

### `Review`
Stores user-written reviews shown on the homepage.
- `user` — ForeignKey to `User`
- `predicted_genre` — Optional linked genre
- `message` — Review text content

### `UserActivity`
Tracks per-user prediction activity.
- `last_prediction` — Timestamp of last prediction
- `total_predictions` — Count of total predictions made

### `TrendingGenre`
Stores calculated trend scores for genres over time.
- `genre` — ForeignKey to `Genre`
- `score` — Floating-point trend score
- `date` — Auto-set date of score calculation

---

## 🔀 URL Routes

| URL | View | Description |
|---|---|---|
| `/signup/` | `signup_view` | New user registration |
| `/login/` | `login_view` | User login |
| `/logout/` | `logout_view` | User logout |
| `/home/` | `home_view` | Dashboard (auth required) |
| `/predict/` | `predict_genre` | Genre prediction (auth required) |
| `/admin/` | Django Admin | Admin panel |

---

## 🤖 How the ML Prediction Works

1. **Input**: User uploads a `.mp3`, `.wav`, or `.webm` file, or records live audio (15 seconds).
2. **Conversion**: Audio is converted to mono WAV format at 22050 Hz using `pydub`.
3. **Feature Extraction** (via `librosa`):
   - **MFCCs** (13 coefficients) — Mel-Frequency Cepstral Coefficients
   - **Spectral Centroid** — Brightness of the audio signal
   - **Spectral Bandwidth** — Range of frequencies present
4. **Prediction**: The 15-dimensional feature vector is passed to `genre_classifier.pkl` (loaded via `joblib`), which returns the predicted genre label.
5. **Display**: The result is rendered on the prediction page.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- `ffmpeg` installed on your system (required by `pydub` for audio conversion)

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS (Homebrew)
brew install ffmpeg
```

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/melodi_match.git
   cd melodi_match/musicclassifier
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install django librosa pydub sounddevice joblib scikit-learn numpy
   ```

4. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional, for Django Admin)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Open in your browser**
   ```
   http://127.0.0.1:8000/home/
   ```

---

## ⚙️ Configuration

Key settings are located in `musicclassifier/settings.py`:

| Setting | Value | Description |
|---|---|---|
| `SECRET_KEY` | `django-insecure-...` | **Change this before deploying to production** |
| `DEBUG` | `True` | Disable in production |
| `DATABASES` | SQLite3 | Swap for PostgreSQL in production |
| `SESSION_COOKIE_AGE` | 1800s (30 min) | Session timeout duration |
| `SESSION_EXPIRE_AT_BROWSER_CLOSE` | `True` | Sessions expire on browser close |
| `LOGIN_REDIRECT_URL` | `home` | Post-login redirect target |

> ⚠️ **Security Warning:** The `SECRET_KEY` in the repository is for development only. Always generate a new secret key and use environment variables before deploying.

---

## 🔒 Authentication

- All prediction and dashboard features require a logged-in user (`@login_required`).
- Sessions expire after 30 minutes of inactivity or on browser close.
- Unauthenticated users are redirected to the login page.

---

## 🎨 UI Pages

| Page | Route | Description |
|---|---|---|
| **Home** | `/home/` | Hero section, top genres, how-it-works steps, user reviews, active users count |
| **Predict** | `/predict/` | Drag-and-drop file upload, microphone recording button, genre prediction result display |
| **Login** | `/login/` | Username + password form |
| **Signup** | `/signup/` | Username, email, and password registration form |

The frontend uses a purple-violet gradient theme (`#8E2DE2` → `#4A00E0`) with the **Poppins** typeface and Font Awesome icons.

---

## 🗺️ Roadmap / Future Ideas

- [ ] Spotify API integration (field already reserved on `Genre` model)
- [ ] Per-prediction confidence score stored to the database
- [ ] Trending genres calculation (`TrendingGenre.update_trends()` is implemented, pending a scheduler)
- [ ] User prediction history page
- [ ] Replace SQLite with PostgreSQL for production
- [ ] Deploy to a cloud platform (Heroku, Railway, Render, etc.)

---

## 📄 License

This project is open source. Feel free to fork, modify, and build upon it.

---

> Built with ❤️ using Django & my ML trained model


# ---- SENKS ----
