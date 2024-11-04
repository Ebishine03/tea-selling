
function searchProducts() {
    const  productSearchQuery=document.getElementById('product_search_query').value;
    fetch(`?product_search_query=${encodeURIComponent(productSearchQuery)}`, {
     headers: {
     'X-Requested-With': 'XMLHttpRequest'
   }
   })
   .then(response => response.json())
   .then(data => {
   document.getElementById('product-list').innerHTML = data.products_html;
   })
   .catch(error => console.error('Product Search Error:', error));
   }
   
   
   
   function searchOrders() {
       const orderSearchQuery = document.getElementById('order_search_query').value;
   
       fetch(`?order_search_query=${encodeURIComponent(orderSearchQuery)}`, {
           headers: {
               'X-Requested-With': 'XMLHttpRequest'  // Required for Django to recognize this as an AJAX request
           }
       })
       .then(response => response.json())
       .then(data => {
           document.getElementById('order-list').innerHTML = data.orders_html;
       })
       .catch(error => console.error('Error:', error));
   }
   
   
   document.getElementById('product_search_query').addEventListener('input', searchProducts);
   document.getElementById('order_search_query').addEventListener('input', searchOrders);
   