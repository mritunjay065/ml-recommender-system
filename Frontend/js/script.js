// API Configuration
const API_URL = '';

// State
let currentMovie = null;
let searchTimeout = null;
let allMovies = [];
let currentRatingFilter = 0;
let currentGenreFilter = 'all';

// DOM Elements
const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');
const moviesGrid = document.getElementById('moviesGrid');
const recommendationsGrid = document.getElementById('recommendationsGrid');
const recommendationsSection = document.getElementById('recommendationsSection');
const selectedMovieSpan = document.getElementById('selectedMovie');
const clearBtn = document.getElementById('clearBtn');
const movieModal = document.getElementById('movieModal');
const modalClose = document.getElementById('modalClose');
const modalTitle = document.getElementById('modalTitle');
const modalRating = document.getElementById('modalRating');
const modalPopularity = document.getElementById('modalPopularity');
const modalOverview = document.getElementById('modalOverview');
const getRecommendationsBtn = document.getElementById('getRecommendationsBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const movieCount = document.getElementById('movieCount');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadFeaturedMovies();
    setupEventListeners();
    setupFilterListeners();
});

// Event Listeners
function setupEventListeners() {
    searchInput.addEventListener('input', handleSearch);
    clearBtn.addEventListener('click', clearRecommendations);
    modalClose.addEventListener('click', closeModal);
    movieModal.querySelector('.modal-overlay').addEventListener('click', closeModal);
    getRecommendationsBtn.addEventListener('click', () => {
        if (currentMovie) {
            getRecommendations(currentMovie.title);
            closeModal();
        }
    });

    // Close search results when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.remove('active');
        }
    });
}

// Filter Listeners
function setupFilterListeners() {
    // Rating filter chips
    const ratingFilters = document.getElementById('ratingFilters');
    if (ratingFilters) {
        ratingFilters.addEventListener('click', (e) => {
            if (e.target.classList.contains('filter-chip')) {
                // Remove active from all
                ratingFilters.querySelectorAll('.filter-chip').forEach(chip => {
                    chip.classList.remove('active');
                });
                // Add active to clicked
                e.target.classList.add('active');
                currentRatingFilter = parseInt(e.target.dataset.rating) || 0;
                applyFilters();
            }
        });
    }

    // Genre filter chips
    const genreFilters = document.getElementById('genreFilters');
    if (genreFilters) {
        genreFilters.addEventListener('click', (e) => {
            if (e.target.classList.contains('filter-chip')) {
                // Remove active from all
                genreFilters.querySelectorAll('.filter-chip').forEach(chip => {
                    chip.classList.remove('active');
                });
                // Add active to clicked
                e.target.classList.add('active');
                currentGenreFilter = e.target.dataset.genre || 'all';
                applyFilters();
            }
        });
    }
}

// Apply Filters
function applyFilters() {
    let filtered = [...allMovies];

    // Apply rating filter
    if (currentRatingFilter > 0) {
        filtered = filtered.filter(movie => {
            const rating = movie.vote_average || movie.rating || 0;
            return rating >= currentRatingFilter;
        });
    }

    // Apply genre filter
    if (currentGenreFilter !== 'all') {
        filtered = filtered.filter(movie => {
            const genres = movie.genres || '';
            return genres.toLowerCase().includes(currentGenreFilter.toLowerCase());
        });
    }

    // Update display
    displayMovies(filtered);
    updateMovieCount(filtered.length);
}

function updateMovieCount(count) {
    if (movieCount) {
        movieCount.textContent = count;
        // Animate the count
        movieCount.style.animation = 'none';
        setTimeout(() => {
            movieCount.style.animation = 'countUp 0.5s ease-out';
        }, 10);
    }
}

// API Functions
async function fetchMovies() {
    try {
        const response = await fetch(`${API_URL}/api/movies`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching movies:', error);
        return [];
    }
}

async function searchMovies(query) {
    try {
        const response = await fetch(`${API_URL}/api/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error searching movies:', error);
        return [];
    }
}

async function getRecommendations(movieTitle) {
    showLoading();
    try {
        const response = await fetch(`${API_URL}/api/recommend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title: movieTitle, n: 12 })
        });
        const data = await response.json();

        if (data.recommendations) {
            displayRecommendations(data.recommendations, movieTitle);
        } else {
            alert('No recommendations found');
        }
    } catch (error) {
        console.error('Error getting recommendations:', error);
        alert('Error getting recommendations. Make sure the API server is running.');
    } finally {
        hideLoading();
    }
}

// Display Functions
function loadFeaturedMovies() {
    showLoading();
    fetchMovies().then(movies => {
        allMovies = movies;
        displayMovies(movies);
        updateMovieCount(movies.length);
        hideLoading();
    });
}

function displayMovies(movies) {
    moviesGrid.innerHTML = '';

    if (movies.length === 0) {
        moviesGrid.innerHTML = '<div class="no-movies">No movies found matching your filters</div>';
        return;
    }

    movies.forEach((movie, index) => {
        const card = createMovieCard(movie);
        card.style.animationDelay = `${index * 0.05}s`;
        moviesGrid.appendChild(card);
    });
}

function displayRecommendations(recommendations, movieTitle) {
    recommendationsGrid.innerHTML = '';
    selectedMovieSpan.textContent = movieTitle;
    recommendationsSection.classList.remove('hidden');

    recommendations.forEach((movie, index) => {
        const card = createMovieCard(movie, true);
        card.style.animationDelay = `${index * 0.05}s`;
        recommendationsGrid.appendChild(card);
    });

    // Scroll to recommendations
    recommendationsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function createMovieCard(movie, showSimilarity = false) {
    const card = document.createElement('div');
    card.className = 'movie-card';
    card.dataset.movieId = movie.id;

    const rating = movie.rating || movie.vote_average || 0;
    const popularity = Math.round(movie.popularity || 0);

    // Determine rating color class
    let ratingClass = '';
    if (rating >= 8) ratingClass = 'rating-high';
    else if (rating >= 7) ratingClass = 'rating-medium';

    // Trending badge for high popularity
    let trendingBadge = '';
    if (popularity > 100) {
        trendingBadge = '<span class="trending-badge">🔥 Trending</span>';
    }

    card.innerHTML = `
        <div class="movie-card-content">
            ${showSimilarity && movie.similarity ?
            `<div class="similarity-badge">${Math.round(movie.similarity * 100)}% Match</div>` :
            trendingBadge}
            <h3 class="movie-title">${movie.title}</h3>
            <div class="movie-info">
                <span class="rating ${ratingClass}">⭐ ${rating.toFixed(1)}</span>
                <span class="popularity">🔥 ${popularity}</span>
            </div>
            <p class="movie-overview">${movie.overview || 'No description available.'}</p>
            <div class="hover-preview" id="preview-${movie.id}">
                <div class="preview-loading">Loading similar movies...</div>
            </div>
        </div>
    `;

    // Hover preview functionality
    let hoverTimeout;
    card.addEventListener('mouseenter', () => {
        hoverTimeout = setTimeout(() => {
            loadQuickPreview(movie.id);
        }, 500); // 500ms delay before loading
    });

    card.addEventListener('mouseleave', () => {
        clearTimeout(hoverTimeout);
        const preview = card.querySelector('.hover-preview');
        if (preview) {
            preview.classList.remove('active');
        }
    });

    card.addEventListener('click', () => openMovieModal(movie));

    return card;
}

// Quick preview on hover
async function loadQuickPreview(movieId) {
    const preview = document.getElementById(`preview-${movieId}`);
    if (!preview) return;

    preview.classList.add('active');

    try {
        const response = await fetch(`${API_URL}/api/quick-preview/${movieId}`);
        const data = await response.json();

        if (data.recommendations && data.recommendations.length > 0) {
            preview.innerHTML = `
                <div class="preview-header">
                    <span class="preview-title">⚡ Similar Movies</span>
                </div>
                <div class="preview-movies">
                    ${data.recommendations.map(m => `
                        <div class="preview-movie">
                            <span class="preview-movie-title">${m.title}</span>
                            <span class="preview-match">${Math.round(m.similarity * 100)}%</span>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            preview.innerHTML = '<div class="preview-empty">No similar movies found</div>';
        }
    } catch (error) {
        preview.innerHTML = '<div class="preview-error">Could not load preview</div>';
    }
}

function handleSearch(e) {
    const query = e.target.value.trim();

    clearTimeout(searchTimeout);

    if (query.length < 2) {
        searchResults.classList.remove('active');
        return;
    }

    searchTimeout = setTimeout(async () => {
        const results = await searchMovies(query);
        displaySearchResults(results);
    }, 300);
}

function displaySearchResults(results) {
    searchResults.innerHTML = '';

    if (results.length === 0) {
        searchResults.innerHTML = '<div class="search-result-item">No movies found</div>';
        searchResults.classList.add('active');
        return;
    }

    results.forEach(movie => {
        const item = document.createElement('div');
        item.className = 'search-result-item';
        const rating = movie.vote_average || 0;
        let ratingBadge = '';
        if (rating >= 8) ratingBadge = '🔥';
        else if (rating >= 7) ratingBadge = '⭐';

        item.innerHTML = `
            <div class="search-result-title">${movie.title}</div>
            <div class="search-result-rating">${ratingBadge} ${rating.toFixed(1)}</div>
        `;
        item.addEventListener('click', () => {
            openMovieModal(movie);
            searchResults.classList.remove('active');
            searchInput.value = '';
        });
        searchResults.appendChild(item);
    });

    searchResults.classList.add('active');
}

function openMovieModal(movie) {
    currentMovie = movie;
    modalTitle.textContent = movie.title;
    modalRating.textContent = `⭐ ${(movie.rating || movie.vote_average || 0).toFixed(1)}`;
    modalPopularity.textContent = `🔥 ${Math.round(movie.popularity || 0)}`;
    modalOverview.textContent = movie.overview || 'No description available.';
    movieModal.classList.add('active');
}

function closeModal() {
    movieModal.classList.remove('active');
}

function clearRecommendations() {
    recommendationsSection.classList.add('hidden');
    recommendationsGrid.innerHTML = '';
}

function showLoading() {
    loadingSpinner.classList.remove('hidden');
}

function hideLoading() {
    loadingSpinner.classList.add('hidden');
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
        searchResults.classList.remove('active');
    }
    if (e.key === '/' && document.activeElement !== searchInput) {
        e.preventDefault();
        searchInput.focus();
    }
});
