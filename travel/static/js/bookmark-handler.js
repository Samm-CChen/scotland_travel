/**
 * Bookmark toggle handler for Scotland Travel project
 * Handles: add/remove bookmark AJAX requests
 */

/**
 * Toggle bookmark status for an attraction
 * @param {number} attractionId - ID of the attraction to bookmark/unbookmark
 * @param {HTMLElement} button - Button element to update UI
 */
async function toggleBookmark(attractionId, button) {
    // Check if user is authenticated
    if (!isUserAuthenticated()) {
        redirectToLogin();
        return;
    }

    try {
        // Prepare request data
        const formData = new FormData();
        formData.append('attraction', attractionId);

        // Send AJAX request
        const response = await fetch('/travel/api/attraction/bookmark/toggle/', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': window.csrfToken
            },
            body: formData
        });

        const data = await response.json();

        // Handle response
        if (response.ok) {
            // Update button UI
            updateBookmarkButtonUI(button, data.status);
            
            // Show success message
            const message = data.message || (data.status === 'bookmarked' ? 'Added to bookmarks!' : 'Removed from bookmarks');
            showToast('success', message);
            
            // If removing from bookmarks list, remove the card
            if (data.status === 'unbookmarked' && button.classList.contains('remove-bookmark-btn')) {
                const bookmarkCard = button.closest('.col-md-4');
                if (bookmarkCard) {
                    // Add fade out animation
                    bookmarkCard.style.opacity = '0';
                    bookmarkCard.style.transition = 'opacity 0.3s ease';
                    
                    // Remove after animation
                    setTimeout(() => {
                        bookmarkCard.remove();
                        
                        // Check if bookmarks list is now empty
                        checkEmptyBookmarksList();
                    }, 300);
                }
            }
        } else {
            // Show error message
            const errorMessage = data.message || 'Failed to update bookmark';
            showToast('error', errorMessage);
        }
    } catch (error) {
        console.error('Bookmark toggle error:', error);
        showToast('error', 'Network error: Could not update bookmark');
    }
}

/**
 * Update bookmark button UI
 * @param {HTMLElement} button - Button element to update
 * @param {string} status - Bookmark status ('bookmarked' or 'unbookmarked')
 */
function updateBookmarkButtonUI(button, status) {
    if (!button) return;

    // Remove all classes and reset content
    button.classList.remove('bookmarked', 'btn-outline-danger', 'btn-danger');
    
    if (status === 'bookmarked') {
        // Update to "Remove from Bookmarks" state
        button.classList.add('bookmarked', 'btn-danger');
        button.innerHTML = '<i class="fas fa-heart me-1"></i> Remove from Bookmarks';
    } else {
        // Update to "Add to Bookmarks" state
        button.classList.add('btn-outline-danger');
        button.innerHTML = '<i class="far fa-heart me-1"></i> Add to Bookmarks';
    }
}

/**
 * Check if bookmarks list is empty and show/hide empty state
 */
function checkEmptyBookmarksList() {
    const bookmarksGrid = document.querySelector('.bookmarks-grid');
    const emptyState = document.getElementById('empty-bookmarks');
    
    if (!bookmarksGrid || !emptyState) return;

    const bookmarkCards = bookmarksGrid.querySelectorAll('.col-md-4');
    if (bookmarkCards.length === 0) {
        emptyState.classList.remove('d-none');
        bookmarksGrid.classList.add('d-none');
    } else {
        emptyState.classList.add('d-none');
        bookmarksGrid.classList.remove('d-none');
    }
}

// Initialize bookmark handlers on DOM load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize main bookmark buttons (attraction detail page)
    const bookmarkButtons = document.querySelectorAll('#bookmark-btn');
    bookmarkButtons.forEach(button => {
        const attractionId = button.dataset.attractionId || document.querySelector('.attraction-main').dataset.attractionId;
        if (!attractionId) return;

        button.addEventListener('click', function() {
            toggleBookmark(attractionId, button);
        });
    });

    // Initialize remove bookmark buttons (bookmarks list page)
    const removeBookmarkButtons = document.querySelectorAll('.remove-bookmark-btn');
    removeBookmarkButtons.forEach(button => {
        const attractionId = button.dataset.attractionId;
        if (!attractionId) return;

        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Show confirmation dialog
            if (confirm('Are you sure you want to remove this attraction from your bookmarks?')) {
                toggleBookmark(attractionId, button);
            }
        });
    });

    // Initialize empty bookmarks check
    checkEmptyBookmarksList();
});
