document.addEventListener('DOMContentLoaded', function () {
    const navbar = document.querySelector('.navbar');
    const cartIcon = document.querySelector('.cart-i');
    const cartIconLarge = document.querySelector('.cart-i-l');
    const loginIcon = document.querySelector('.login');
    const loginIconLarge = document.querySelector('.login-l .icon-l');

    if (!navbar) {
        console.error('Navbar not found!');
        return;
    }

    // Base path for static assets
    const staticBasePath = '/static/img/';

    // Function to update navbar and icon styles
    const updateNavbar = () => {
        const isHomepage = window.location.pathname === '/';
        const isScrolled = window.scrollY > 200;

        if (!isHomepage) {
            // For non-homepage, always solid
            navbar.classList.add('solid');
            updateIcons('solid');
        } else if (isScrolled) {
            // Homepage scrolled
            navbar.classList.add('scrolled');
            navbar.classList.remove('solid');
            updateIcons('scrolled');
        } else {
            // Homepage at the top
            navbar.classList.remove('scrolled', 'solid');
            updateIcons('default');
        }
    };

    // Function to update icons based on class
    const updateIcons = (state) => {
        if (state === 'solid' || state === 'scrolled') {
            if (cartIcon) cartIcon.style.backgroundImage = `url('${staticBasePath}header_cart-eed150 _green.svg')`;
            if (loginIcon) loginIcon.style.backgroundImage = `url('${staticBasePath}user-question-alt-1-svgrepo-com_green.svg')`;
            if (loginIconLarge) loginIconLarge.style.backgroundImage = `url('${staticBasePath}user-question-alt-1-svgrepo-com_green.svg')`;
            if (cartIconLarge) cartIcon.style.backgroundImage = `url('${staticBasePath}header_cart-eed150 _green.svg')`;
        } else {
            // Default (homepage top)
            if (cartIcon) cartIcon.style.backgroundImage = `url('${staticBasePath}cart.svg')`;
            if (loginIcon) loginIcon.style.backgroundImage = `url('${staticBasePath}user-question-alt-1-svgrepo-com_white.svg')`;
            if (loginIconLarge) loginIconLarge.style.backgroundImage = `url('${staticBasePath}user-question-alt-1-svgrepo-com_white.svg')`;
            if (cartIconLarge) cartIcon.style.backgroundImage = `url('${staticBasePath}cart.svg')`;
        }
    };

    // Event listener for scroll updates
    window.addEventListener('scroll', updateNavbar);

    // Initial check on page load
    updateNavbar();
});
// $(document).ready(function () {
//     $('#itemslider').carousel({ interval: 3000 });
  
//     $('.carousel-showmanymoveone .carousel-item').each(function () {
//       let itemToClone = $(this);
  
//       for (let i = 1; i < 6; i++) {
//         itemToClone = itemToClone.next();
  
//         // Wrap around to the first item if no more siblings exist
//         if (!itemToClone.length) {
//           itemToClone = $(this).siblings(':first');
//         }
  
//         itemToClone.children(':first-child').clone()
//           .addClass(`cloneditem-${i}`)
//           .appendTo($(this));
//       }
// //     });
//   });
  
