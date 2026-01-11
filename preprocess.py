import pandas as pd
import numpy as np
import json
import ast

def parse_json_column(column):
    """Parse JSON-like string columns and extract names"""
    if pd.isna(column):
        return []
    try:
        data = ast.literal_eval(column)
        return [item['name'] for item in data]
    except:
        return []

def get_director(crew_column):
    """Extract director name from crew data"""
    if pd.isna(crew_column):
        return ""
    try:
        crew = ast.literal_eval(crew_column)
        for member in crew:
            if member['job'] == 'Director':
                return member['name']
        return ""
    except:
        return ""

def get_top_actors(cast_column, n=3):
    """Extract top N actors from cast data"""
    if pd.isna(cast_column):
        return []
    try:
        cast = ast.literal_eval(cast_column)
        return [actor['name'] for actor in cast[:n]]
    except:
        return []

def clean_text(text):
    """Remove spaces from text for better matching"""
    if isinstance(text, list):
        return [str(item).replace(" ", "") for item in text]
    return str(text).replace(" ", "")

print("Loading datasets...")
# Load the datasets
movies = pd.read_csv('tmdb_5000_movies.csv/tmdb_5000_movies.csv')
credits = pd.read_csv('tmdb_5000_movies.csv/tmdb_5000_credits.csv')

print(f"Movies shape: {movies.shape}")
print(f"Credits shape: {credits.shape}")

# Merge datasets on movie id
print("\nMerging datasets...")
movies = movies.merge(credits, left_on='id', right_on='movie_id', how='left')

# Check available columns after merge
print(f"Columns after merge: {list(movies.columns)}")

# Select relevant columns (use title_x if title got duplicated in merge)
if 'title_x' in movies.columns:
    movies['title'] = movies['title_x']
    
columns_to_keep = ['id', 'title', 'overview', 'genres', 'keywords', 
                   'cast', 'crew', 'vote_average', 'vote_count', 
                   'popularity', 'release_date', 'runtime']
movies = movies[columns_to_keep]

# Drop rows with missing critical data
print("\nHandling missing values...")
movies.dropna(subset=['title', 'overview'], inplace=True)
movies['overview'] = movies['overview'].fillna('')

# Parse JSON columns
print("\nParsing JSON columns...")
movies['genres'] = movies['genres'].apply(parse_json_column)
movies['keywords'] = movies['keywords'].apply(parse_json_column)
movies['cast'] = movies['cast'].apply(lambda x: get_top_actors(x, 3))
movies['director'] = movies['crew'].apply(get_director)

# Drop the crew column as we've extracted director
movies.drop('crew', axis=1, inplace=True)

# Create tags for content-based filtering
print("\nCreating metadata tags...")
movies['overview_words'] = movies['overview'].apply(lambda x: x.split()[:50])  # Limit to 50 words

# Clean text (remove spaces for better matching)
movies['genres'] = movies['genres'].apply(clean_text)
movies['keywords'] = movies['keywords'].apply(clean_text)
movies['cast'] = movies['cast'].apply(clean_text)
movies['director'] = movies['director'].apply(clean_text)

# Combine all features into tags
movies['tags'] = (
    movies['overview_words'].apply(lambda x: ' '.join(x)) + ' ' +
    movies['genres'].apply(lambda x: ' '.join(x)) + ' ' +
    movies['keywords'].apply(lambda x: ' '.join(x)) + ' ' +
    movies['cast'].apply(lambda x: ' '.join(x)) + ' ' +
    movies['director']
)

# Convert tags to lowercase
movies['tags'] = movies['tags'].apply(lambda x: x.lower())

# Create a simplified dataset for the model
movies_final = movies[['id', 'title', 'overview', 'genres', 'keywords', 
                       'cast', 'director', 'vote_average', 'vote_count', 
                       'popularity', 'release_date', 'runtime', 'tags']]

# Save preprocessed data
print("\nSaving preprocessed data...")
movies_final.to_csv('movies_cleaned.csv', index=False)

print(f"\nPreprocessing complete!")
print(f"Final dataset shape: {movies_final.shape}")
print(f"\nSample movie tags:")
print(movies_final[['title', 'tags']].head(3))
print(f"\nData saved to 'movies_cleaned.csv'")
