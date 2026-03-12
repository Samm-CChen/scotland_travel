/**
 * Rating submission handler for Scotland Travel project
 * Handles: city rating, attraction rating AJAX submissions
 */

/**
 * Submit city rating via AJAX
 * @param {number} cityId - ID of the city to rate
 * @param {number} rating - Rating value (1-5)
 */
async function submitCityRating(cityId, rating) {
    // Validate rating
    if (!isValidRating(rating)) {
        showToast('error', 'Invalid rating: must be between 1 and 5 stars');
        return;
    }

    // Check if user is authenticated
    if (!isUserAuthenticated()) {
        redirectToLogin();
        return;
    }

    try {
        // Prepare request data
        const formData = new FormData();
        formData.append('city', cityId);
        formData.append('rating', rating);

        // Send AJAX request
        const response = await fetch('/travel/api/city/rating/submit/', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': window.csrfToken
            },
            body: formData
        });

        const data = await response.json();

        // Handle response
        if (response.ok && data.status === 'success') {
            // Update UI with new rating stats
            updateCityRatingUI(cityId, data.avg_rating, data.rating_count);
            showToast('success', data.message || 'Rating submitted successfully');
        } else {
            // Show error message
            const errorMessage = data.message || 'Failed to submit rating';
            const errorDetails = data.errors ? Object.values(data.errors).flat().join(', ') : '';
            showToast('error', `${errorMessage} ${errorDetails}`);
        }
    } catch (error) {
        console.error('Rating submission error:', error);
        showToast('error', 'Network error: Could not submit rating');
    }
}

/**
 * Submit attraction rating via AJAX
 * @param {number} attractionId - ID of the attraction to rate
 * @param {number} rating - Rating value (1-5)
 */
async function submitAttractionRating(attractionId, rating) {
    // Validate rating
    if (!isValidRating(rating)) {
        showToast('error', 'Invalid rating: must be between 1 and 5 stars');
        return;
    }

    // Check if user is authenticated
    if (!isUserAuthenticated()) {
        redirectToLogin();
        return;
    }

    try {
        // Prepare request data
        const formData = new FormData();
        formData.append('attraction', attractionId);
        formData.append('rating', rating);

        // Send AJAX request
        const response = await fetch('/travel/api/attraction/rating/submit/', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': window.csrfToken
            },
            body: formData
        });

        const data = await response.json();

        // Handle response
        if (response.ok && data.status === 'success') {
            // Update UI with new rating stats
            updateAttractionRatingUI(attractionId, data.avg_rating, data.rating_count);
            showToast('success', data.message || 'Rating submitted successfully');
        } else {
            // Show error message
            const errorMessage = data.message || 'Failed to submit rating';
            const errorDetails = data.errors ? Object.values(data.errors).flat().join(', ') : '';
            showToast('error', `${errorMessage} ${errorDetails}`);
        }
    } catch (error) {
        console.error('Attraction rating submission error:', error);
        showToast('error', 'Network error: Could not submit rating');
    }
}

/**
 * Update city rating UI elements
 * @param {number} cityId - City ID
 * @param {number} avgRating - New average rating
 * @param {number} ratingCount - New rating count
 */
function updateCityRatingUI(cityId, avgRating, ratingCount) {
    // Update average rating display
    const avgRatingElement = document.getElementById(`avg-rating-${cityId}`);
    if (avgRatingElement) {
        avgRatingElement.textContent = formatNumber(avgRating);
    }

    // Update rating count display
    const ratingCountElement = document.getElementById(`rating-count-${cityId}`);
    if (ratingCountElement) {
        ratingCountElement.textContent = `(${ratingCount} reviews)`;
    }
}

/**
 * Update attraction rating UI elements
 * @param {number} attractionId - Attraction ID
 * @param {number} avgRating - New average rating
 * @param {number} ratingCount - New rating count
 */
function updateAttractionRatingUI(attractionId, avgRating, ratingCount) {
    // Update average rating display
    const avgRatingElement = document.getElementById(`avg-rating-${attractionId}`);
    if (avgRatingElement) {
        avgRatingElement.textContent = formatNumber(avgRating);
    }

    // Update rating count display (if exists)
    const ratingCountElement = document.getElementById(`rating-count-${attractionId}`);
    if (ratingCountElement) {
        ratingCountElement.textContent = `(${ratingCount} reviews)`;
    }

    // Update star display
    const ratingContainer = document.getElementById(`attraction-rating-container`);
    if (ratingContainer) {
        const stars = ratingContainer.querySelectorAll('.star');
        const roundedRating = Math.round(avgRating);
        stars.forEach((star, i) => {
            star.classList.toggle('active', i < roundedRating);
        });
    }
}

// Initialize rating handlers on DOM load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize city rating containers
    const cityRatingContainers = document.querySelectorAll('#city-rating-container');
    cityRatingContainers.forEach(container => {
        const cityId = container.dataset.cityId || document.querySelector('.city-header').dataset.cityId;
        if (!cityId) return;

        const stars = container.querySelectorAll('.star');
        stars.forEach(star => {
            star.addEventListener('click', function() {
                const rating = parseInt(this.dataset.rating);
                submitCityRating(cityId, rating);
            });
        });
    });

    // Initialize attraction rating containers
    const attractionRatingContainers = document.querySelectorAll('#attraction-rating-container');
    attractionRatingContainers.forEach(container => {
        const attractionId = container.dataset.attractionId || document.querySelector('.attraction-main').dataset.attractionId;
        if (!attractionId) return;

        const stars = container.querySelectorAll('.star');
        stars.forEach(star => {
            star.addEventListener('click', function() {
                const rating = parseInt(this.dataset.rating);
                submitAttractionRating(attractionId, rating);
            });
        });
    });
});
