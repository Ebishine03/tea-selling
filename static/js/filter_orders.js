document.getElementById('order_search_query').addEventListener('input', function() {
    filterOrders();
});

document.getElementById('order_status').addEventListener('change', function() {
    filterOrders();
});

document.getElementById('order_category').addEventListener('change', function() {
    filterOrders();
});

function filterOrders() {
    const searchQuery = document.getElementById('order_search_query').value;
    const orderStatus = document.getElementById('order_status').value;
    const orderCategory = document.getElementById('order_category').value;

    fetch(`?order_search_query=${searchQuery}&order_status=${orderStatus}&order_category=${orderCategory}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('order-list').innerHTML = data.orders_html;
    });
}
