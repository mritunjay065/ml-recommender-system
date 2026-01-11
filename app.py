from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import os

# Set Frontend folder for templates and static files
app = Flask(__name__, 
            template_folder='Frontend/templates',
            static_folder='Frontend')
CORS(app)  # Enable CORS for frontend

# Load the model and data
print("Loading model and data...")
try:
    vectors = pickle.load(open('vectors.pkl', 'rb'))
    movies = pickle.load(open('movies_dict.pkl', 'rb'))
except FileNotFoundError:
    print("Error: Model files not found. Please run model.py first.")
    vectors = None
    movies = pd.DataFrame()

def get_recommendations(movie_title, n=10):
    """Get movie recommendations"""
    if movies.empty or vectors is None:
        return []
    try:
        movie_index = movies[movies['title'].str.lower() == movie_title.lower()].index[0]
    except IndexError:
        return None
    
    # Calculate similarity on the fly using sparse matrices
    # vectors[movie_index] is 1xN, vectors is MxN
    similarity = cosine_similarity(vectors[movie_index], vectors).flatten()
    
    # Get top N indices
    movies_list = sorted(list(enumerate(similarity)), reverse=True, key=lambda x: x[1])[1:n+1]
    
    recommendations = []
    for i in movies_list:
        movie_data = {
            'id': int(movies.iloc[i[0]].id),
            'title': movies.iloc[i[0]].title,
            'similarity': round(float(i[1]), 3),
            'rating': float(movies.iloc[i[0]].vote_average),
            'popularity': float(movies.iloc[i[0]].popularity),
            'overview': movies.iloc[i[0]].overview
        }
        recommendations.append(movie_data)
    
    return recommendations

@app.route('/')
def home():
    """Serve the frontend application"""
    return render_template('index.html')

@app.route('/api/movies', methods=['GET'])
def get_movies():
    """Return list of all movies"""
    # Include genres for filtering
    cols = ['id', 'title', 'vote_average', 'popularity', 'overview']
    if 'genres' in movies.columns:
        cols.append('genres')
    movies_list = movies[cols].to_dict('records')
    # Convert numpy types to Python types
    for movie in movies_list:
        movie['id'] = int(movie['id'])
        movie['vote_average'] = float(movie['vote_average'])
        movie['popularity'] = float(movie['popularity'])
        if 'genres' not in movie:
            movie['genres'] = ''
    return jsonify(movies_list[:100])  # Return first 100 movies


@app.route('/api/movie/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    """Return detailed movie information"""
    movie = movies[movies['id'] == movie_id]
    if movie.empty:
        return jsonify({'error': 'Movie not found'}), 404
    
    movie_data = movie.iloc[0].to_dict()
    # Convert numpy types to Python types
    for key, value in movie_data.items():
        if pd.isna(value):
            movie_data[key] = None
        elif isinstance(value, (pd.Int64Dtype, int)):
            movie_data[key] = int(value)
        elif isinstance(value, float):
            movie_data[key] = float(value)
    
    return jsonify(movie_data)

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """Return movie recommendations"""
    data = request.get_json()
    movie_title = data.get('title', '')
    n = data.get('n', 10)
    
    if not movie_title:
        return jsonify({'error': 'Movie title is required'}), 400
    
    recommendations = get_recommendations(movie_title, n)
    
    if recommendations is None:
        return jsonify({'error': f'Movie "{movie_title}" not found'}), 404
    
    return jsonify({
        'query': movie_title,
        'recommendations': recommendations
    })

@app.route('/api/search', methods=['GET'])
def search():
    """Search movies by title"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    # Search for movies containing the query
    results = movies[movies['title'].str.lower().str.contains(query)]
    
    movies_list = results[['id', 'title', 'vote_average', 'popularity', 'overview']].head(20).to_dict('records')
    
    # Convert numpy types to Python types
    for movie in movies_list:
        movie['id'] = int(movie['id'])
        movie['vote_average'] = float(movie['vote_average'])
        movie['popularity'] = float(movie['popularity'])
    
    return jsonify(movies_list)

@app.route('/api/quick-preview/<int:movie_id>', methods=['GET'])
def quick_preview(movie_id):
    """Get quick preview recommendations for hover (fast, returns 3 movies)"""
    movie = movies[movies['id'] == movie_id]
    if movie.empty:
        return jsonify({'error': 'Movie not found'}), 404
    
    movie_title = movie.iloc[0]['title']
    recommendations = get_recommendations(movie_title, n=3)
    
    if recommendations is None:
        return jsonify({'recommendations': []})
    
    return jsonify({
        'movie_id': movie_id,
        'movie_title': movie_title,
        'recommendations': recommendations
    })

@app.route('/api/trending', methods=['GET'])
def get_trending():
    """Get trending movies based on popularity (real-time sorted)"""
    trending = movies.nlargest(10, 'popularity')[['id', 'title', 'vote_average', 'popularity', 'overview']]
    movies_list = trending.to_dict('records')
    
    for movie in movies_list:
        movie['id'] = int(movie['id'])
        movie['vote_average'] = float(movie['vote_average'])
        movie['popularity'] = float(movie['popularity'])
        movie['trending_rank'] = movies_list.index(movie) + 1
    
    return jsonify(movies_list)

@app.route('/api/top-rated', methods=['GET'])
def get_top_rated():
    """Get top rated movies (8+ rating)"""
    top_rated = movies[movies['vote_average'] >= 8].nlargest(10, 'vote_average')[['id', 'title', 'vote_average', 'popularity', 'overview']]
    movies_list = top_rated.to_dict('records')
    
    for movie in movies_list:
        movie['id'] = int(movie['id'])
        movie['vote_average'] = float(movie['vote_average'])
        movie['popularity'] = float(movie['popularity'])
    
    return jsonify(movies_list)

if __name__ == '__main__':
    print("Starting Flask server...")
    print("API will be available at http://localhost:5000")
    app.run(debug=True, port=5000)
