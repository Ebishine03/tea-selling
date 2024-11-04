function searchAllProducts() {
    const productAllSearchQuery = document.getElementById('all_product_search_query').value;
    const categoryFilter = document.getElementById('category_filter').value;
    const priceRange = document.getElementById('price_range').value;
    const sortBy = document.getElementById('sort_by').value;

    // Construct the query string for filters
    const queryParams = new URLSearchParams({
        all_product_search_query: productAllSearchQuery,
        category: categoryFilter,
        'price_range': priceRange,
        'sort_by': sortBy
    });

    fetch(`?${queryParams.toString()}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('all-product-list').innerHTML = data.products_html;
    })
    .catch(error => console.error('Product Search Error:', error));
}

// Attach event listeners to filters
document.getElementById('all_product_search_query').addEventListener('input', searchAllProducts);
document.getElementById('category_filter').addEventListener('change', searchAllProducts);
document.getElementById('price_range').addEventListener('change', searchAllProducts);
document.getElementById('sort_by').addEventListener('change', searchAllProducts);
