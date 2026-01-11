# 🎬 CineMatch - AI Movie Recommendation System

A personalized movie recommendation system with **real-time engagement features**, powered by machine learning and a modern web interface.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.1-green)
![scikit--learn](https://img.shields.io/badge/scikit--learn-1.8-orange)

## ✨ Features

### Core Features
- **AI-Powered Recommendations**: Content-based filtering using cosine similarity
- **5000+ Movies**: Comprehensive TMDB dataset
- **Real-time Search**: Live search with autocomplete

### 🔥 Real-Time Engagement
- **Hover Preview**: See 3 similar movies instantly when hovering over any card
- **Rating Filters**: Filter by rating (6+, 7+, 8+, 9+ 🔥)
- **Genre Filters**: Action, Comedy, Drama, Horror, Romance, Sci-Fi, Thriller, Animation, Adventure
- **Trending Badges**: Animated badges for popular movies
- **Live Movie Count**: Real-time filter count display
- **Color-Coded Ratings**: Visual feedback for high-rated movies

### UI/UX
- **Modern Dark Theme**: Glassmorphism design with gradient accents
- **Smooth Animations**: Fade-in, hover effects, tooltips
- **Responsive Design**: Works on all devices

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Preprocess data** (first time only)
```bash
python preprocess.py
```

3. **Build the model** (first time only)
```bash
python model.py
```

4. **Run the application**
```bash
python app.py
```

5. **Open in browser**
```
http://localhost:5000
```

## 📁 Project Structure

```
Recommender system/
├── app.py                 # Flask API + Frontend server
├── model.py               # ML recommendation model
├── preprocess.py          # Data preprocessing script
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   └── index.html
├── static/                # Static assets
│   ├── css/style.css
│   └── js/script.js
├── vectors.pkl            # Sparse feature vectors (1.4MB)
├── movies_dict.pkl        # Movie data
├── movies_cleaned.csv     # Processed dataset
└── tmdb_5000_movies.csv/  # Raw dataset folder
    ├── tmdb_5000_movies.csv
    └── tmdb_5000_credits.csv
```

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application |
| `/api/movies` | GET | Get all movies (100) |
| `/api/search?q=query` | GET | Search movies |
| `/api/recommend` | POST | Get recommendations |
| `/api/quick-preview/<id>` | GET | Hover preview (3 movies) |
| `/api/trending` | GET | Top 10 trending |
| `/api/top-rated` | GET | Top 10 rated (8+) |

### Example: Get Recommendations
```bash
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"title": "Avatar", "n": 5}'
```

## 🎯 How It Works

1. **Data Preprocessing**: Extracts features from genres, keywords, cast, crew, overview
2. **Vectorization**: CountVectorizer creates 5000-dimensional feature vectors
3. **Similarity**: Cosine similarity computed on-the-fly for each request
4. **Real-Time**: All recommendations calculated dynamically, not pre-computed

## 🛠️ Technologies

**Backend**: Python, Flask, pandas, scikit-learn, pickle  
**Frontend**: HTML5, CSS3 (Glassmorphism), Vanilla JavaScript  
**Design**: Inter font, Dark theme, Gradient accents

## 📊 Dataset

TMDB 5000 Movie Dataset:
- 4800+ movies with metadata
- Genres, keywords, cast, crew
- Ratings and popularity scores

---

**Made with ❤️ using Python and Machine Learning**
