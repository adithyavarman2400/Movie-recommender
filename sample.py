import streamlit as st
import pickle
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

# API Key (ideally, this should be stored securely, e.g., using environment variables)
API_KEY = '67af0a0494aad9e7d5b77c25f02e9898'


def fetch_movie_details(movie_id):
    try:
        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US', timeout=30)
        response.raise_for_status()
        data = response.json()
        poster_path = data['poster_path']
        poster_url = "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else "URL_TO_DEFAULT_IMAGE"
        return {
            "poster_url": poster_url,
            "title": data.get('title', 'N/A'),
            "release_date": data.get('release_date', 'N/A'),
            "rating": data.get('vote_average', 'N/A'),
            "overview": data.get('overview', 'No overview available.')
        }
    except requests.exceptions.RequestException as e:
        return None


def fetch_poster(movie_id):
    try:
        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US')
        response.raise_for_status()
        data = response.json()
        poster_path = data['poster_path']
        return "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else "URL_TO_DEFAULT_IMAGE"
    except requests.exceptions.RequestException as e:
        return None


def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:21]

        recommended_movies = []
        for i in movies_list:
            movie_id = movies.iloc[i[0]].movie_id
            movie_details = fetch_movie_details(movie_id)
            if movie_details:
                recommended_movies.append(movie_details)

        return recommended_movies
    except IndexError:
        st.error("Movie not found in the database.")
        return []


@st.cache_data
def load_data():
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity


movies, similarity = load_data()

st.title('Movie Recommender System')
st.write("Welcome to the Movie Recommender System. Select a movie and get recommendations!")

selected_movie_name = st.selectbox(
    'Select a movie you like:',
    movies['title'].values)

if selected_movie_name:
    movie_id = movies[movies['title'] == selected_movie_name].iloc[0].movie_id
    poster_url = fetch_poster(movie_id)
    if poster_url:
        st.image(poster_url, caption=selected_movie_name, width=200)

    with st.spinner('Fetching recommendations...'):
        recommended_movies = recommend(selected_movie_name)

    if recommended_movies:
        st.write(f"You may also like:")

        # Display 5 movies per row
        for i in range(0, len(recommended_movies), 5):
            cols = st.columns(5)  # Create 5 columns in each row
            for idx, movie in enumerate(recommended_movies[i:i + 5]):  # Slice the list for 5 movies per row
                with cols[idx]:  # Place each movie in its respective column
                    st.image(movie['poster_url'], width=150)  # Display the movie poster
                    st.write(movie['title'])  # Display the movie title











