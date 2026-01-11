import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

print("Loading preprocessed data...")
movies = pd.read_csv('movies_cleaned.csv')

print(f"Dataset shape: {movies.shape}")
print(f"Columns: {list(movies.columns)}")

# Create feature vectors from tags
print("\nCreating feature vectors...")
cv = CountVectorizer(max_features=5000, stop_words='english')

# Handle any NaN values in tags
movies['tags'] = movies['tags'].fillna('')

# Create vectors (keep sparse)
vectors = cv.fit_transform(movies['tags'])
print(f"Vector shape: {vectors.shape}")

def get_recommendations(movie_title, n=10):
    """
    Get top N movie recommendations based on similarity
    """
    # Find the movie index
    try:
        movie_index = movies[movies['title'].str.lower() == movie_title.lower()].index[0]
    except IndexError:
        return f"Movie '{movie_title}' not found in database"
    
    # Calculate similarity on the fly for just this movie
    # This is much more memory efficient than storing the full N*N matrix
    similarity = cosine_similarity(vectors[movie_index], vectors).flatten()
    
    # Sort by similarity (excluding the movie itself)
    movies_list = sorted(list(enumerate(similarity)), reverse=True, key=lambda x: x[1])[1:n+1]
    
    # Get recommended movies
    recommendations = []
    for i in movies_list:
        movie_data = {
            'title': movies.iloc[i[0]].title,
            'similarity': round(float(i[1]), 3),
            'rating': movies.iloc[i[0]].vote_average,
            'popularity': movies.iloc[i[0]].popularity
        }
        recommendations.append(movie_data)
    
    return recommendations

# Test the recommendation system
print("\n" + "="*60)
print("TESTING RECOMMENDATION SYSTEM")
print("="*60)

test_movies = ['Avatar', 'The Dark Knight', 'Inception']

for test_movie in test_movies:
    if test_movie in movies['title'].values:
        print(f"\nRecommendations for '{test_movie}':")
        recs = get_recommendations(test_movie, 5)
        for idx, rec in enumerate(recs, 1):
            print(f"  {idx}. {rec['title']} (Similarity: {rec['similarity']}, Rating: {rec['rating']})")
    else:
        print(f"\n'{test_movie}' not found in dataset")

# Save the model
print("\n" + "="*60)
print("Saving model (optimized for serverless)...")
print("="*60)

# Save sparse vectors and movie data
pickle.dump(vectors, open('vectors.pkl', 'wb'))
pickle.dump(movies, open('movies_dict.pkl', 'wb'))

print("\nModel saved successfully!")
print("Files created:")
print("  - vectors.pkl (sparse feature vectors)")
print("  - movies_dict.pkl (movie data)")
print("\nModel building complete!")
