/**
 * City list renderer for Scotland Travel project
 * Handles: dynamic filtering, AJAX-based city list updates
 */

/**
 * Fetch filtered cities via AJAX
 * @param {FormData} formData - Filter form data
 * @returns {Promise<Object>} Filtered cities data
 */
async function fetchFilteredCities(formData) {
    try {
        // Convert FormData to URL parameters
        const params = new URLSearchParams(formData);
        
        // Send AJAX request
        const response = await fetch(`/travel/api/cities/filter/?${params}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching filtered cities:', error);
        showToast('error', 'Failed to load filtered cities');
        return { cities: [] };
    }
}

/**
 * Render cities list from API response
 * @param {Array} cities - Array of city objects from API
 */
function renderCitiesList(cities) {
    const citiesGrid = document.querySelector('.city-grid');
    if (!citiesGrid) return;

    // Clear existing content
    citiesGrid.innerHTML = '';

    // Check if no cities found
    if (!cities || cities.length === 0) {
        const emptyState = createElementFromHTML(`
            <div class="col-12">
                <div class="alert alert-info">
                    <i class="fas fa-search me-2"></i> No cities found matching your criteria.
                </div>
            </div>
        `);
        citiesGrid.appendChild(emptyState);
        return;
    }

    // Render each city card
    cities.forEach(city => {
        const cityCard = createElementFromHTML(`
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    ${city.cover_image ? `<img src="${city.cover_image}" class="card-img-top" alt="${city.name}">` : ''}
                    <div class="card-body">
                        <h5 class="card-title">
                            <a href="/travel/city/${city.id}/" class="text-decoration-none">${city.name}</a>
                        </h5>
                        <p class="card-text">${city.description ? city.description.substring(0, 100) + '...' : ''}</p>
                        
                        <div class="mb-2">
                            <div class="d-flex align-items-center">
                                <span class="h5 me-2" id="avg-rating-${city.id}">${formatNumber(city.avg_rating)}</span>
                                <div class="star-rating" data-readonly="true">
                                    ${Array.from({length: 5}, (_, i) => 
                                        `<span class="star ${i < Math.round(city.avg_rating) ? 'active' : ''}">★</span>`
                                    ).join('')}
                                </div>
                                <span class="text-muted ms-2" id="rating-count-${city.id}">(${city.rating_count} reviews)</span>
                            </div>
                        </div>
                        
                        <a href="/travel/city/${city.id}/" class="btn btn-outline-primary">
                            <i class="fas fa-info-circle me-1"></i> View Attractions
                        </a>
                    </div>
                </div>
            </div>
        `);
        citiesGrid.appendChild(cityCard);
    });
}

// Initialize city filter on DOM load
document.addEventListener('DOMContentLoaded', function() {
    const filterForm = document.getElementById('city-filter-form');
    if (!filterForm) return;

    // Handle form submission (AJAX)
    filterForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Validate form first
        if (!validateFilterForm(filterForm)) return;

        // Show loading state
        const submitButton = filterForm.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Filtering...';

        try {
            // Fetch filtered cities
            const formData = new FormData(filterForm);
            const data = await fetchFilteredCities(formData);
            
            // Render filtered cities
            renderCitiesList(data.cities);
        } finally {
            // Restore button state
            submitButton.disabled = false;
            submitButton.innerHTML = originalButtonText;
        }
    });

    // Add debounced search (filter as user types)
    const cityNameInput = filterForm.querySelector('#id_city_name');
    if (cityNameInput) {
        let debounceTimeout;
        cityNameInput.addEventListener('input', function() {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(async () => {
                const formData = new FormData(filterForm);
                const data = await fetchFilteredCities(formData);
                renderCitiesList(data.cities);
            }, 500); // 500ms debounce delay
        });
    }

    // Initialize with default cities
    fetchFilteredCities(new FormData(filterForm))
        .then(data => renderCitiesList(data.cities));
});

/**
 * Validate filter form before submission
 * @param {HTMLElement} form - Filter form element
 * @returns {boolean} True if valid
 */
function validateFilterForm(form) {
    let isValid = true;
    
    // Validate minimum rating
    const minRatingInput = form.querySelector('#id_min_rating');
    if (minRatingInput.value.trim()) {
        const minRating = parseFloat(minRatingInput.value);
        if (isNaN(minRating) || minRating < 0 || minRating > 5) {
            showFormError(minRatingInput, 'Minimum rating must be between 0 and 5');
            isValid = false;
        } else {
            // Clear error if valid
            minRatingInput.classList.remove('is-invalid');
            const errorElement = minRatingInput.nextElementSibling;
            if (errorElement && errorElement.classList.contains('invalid-feedback')) {
                errorElement.remove();
            }
        }
    }

    return isValid;
}
