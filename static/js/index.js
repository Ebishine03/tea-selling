(function ($) {
  "use strict";

  // Spinner
  var spinner = function () {
      setTimeout(function () {
          if ($('#spinner').length > 0) {
              $('#spinner').removeClass('show');
          }
      }, 1);
  };
  spinner();
  
  
  // Initiate the wowjs
  new WOW().init();


  // Sticky Navbar
  $(window).scroll(function () {
      if ($(this).scrollTop() > 300) {
          $('.sticky-top').addClass('shadow-sm').css('top', '0px');
      } else {
          $('.sticky-top').removeClass('shadow-sm').css('top', '-150px');
      }
  });
  
  
  // Back to top button
  $(window).scroll(function () {
      if ($(this).scrollTop() > 300) {
          $('.back-to-top').fadeIn('slow');
      } else {
          $('.back-to-top').fadeOut('slow');
      }
  });
  $('.back-to-top').click(function () {
      $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
      return false;
  });


  // Modal Video
 
  // Product carousel
  $(".product-carousel").owlCarousel({
      autoplay: true,
      smartSpeed: 1000,
      margin: 25,
      loop: true,
      center: true,
      dots: false,
      nav: true,
      navText : [
          '<i class="bi bi-chevron-left"></i>',
          '<i class="bi bi-chevron-right"></i>'
      ],
      responsive: {
    0:{
              items:1
          },
          576:{
              items:1
          },
          768:{
              items:2
          },
          992:{
              items:3
          }
      }
  });


  // Testimonial carousel
  $(".testimonial-carousel").owlCarousel({
      autoplay: true,
      smartSpeed: 1000,
      items: 1,
      loop: true,
      dots: true,
      nav: false,
  });
  
})(jQuery);

document.addEventListener("DOMContentLoaded", function() {
    var navbar = document.querySelector('.navbar');

    // Check if the current page is the homepage or another page
    if (window.location.pathname !== '/') {
        // If it's not the homepage, add the `scrolled` class immediately
        navbar.classList.add('scrolled');
    }

    // Add scroll listener to dynamically add or remove `scrolled` class on scroll
    window.addEventListener('scroll', function() {
        if (window.scrollY > 200) {
            navbar.classList.add('scrolled');
        } else if (window.location.pathname === '/') {
            // Only remove `scrolled` class on the homepage when scrolling up
            navbar.classList.remove('scrolled');
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.getElementById('navbar');
    
    function updateNavbarClass() {
        if (window.location.pathname === '/') {
            console.log('loaded');
            
            navbar.classList.add('transparent-navbar');
            
            
            navbar.classList.remove('solid-navbar');
        } else {
            console.log('diffff');
            
            navbar.classList.add('solid-navbar');
            navbar.classList.remove('transparent-navbar');
        }
    }

    // Initial check when page loads
    updateNavbarClass();

    // Listen for URL changes if using history navigation (like in single-page apps)
    window.addEventListener('popstate', updateNavbarClass);
    window.addEventListener('pushstate', updateNavbarClass);
    window.addEventListener('replacestate', updateNavbarClass);
});

