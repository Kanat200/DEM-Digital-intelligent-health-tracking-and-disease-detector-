//
// OWL-CAROUSAL
$(".owl-carousel").owlCarousel({
  items: 3,
  loop: true,
  nav: false,
  dot: true,
  autoplay: true,
  slideTransition: "linear",
  autoplayHoverPause: true,
  responsive: {
    0: {
      items: 1,
    },
    600: {
      items: 2,
    },
    1000: {
      items: 3,
    },
  },
});

// SCROLLSPY
$(document).ready(function () {
  $(".nav-link").click(function () {
    var t = $(this).attr("href");
    $("html, body").animate(
      {
        scrollTop: $(t).offset().top - 75,
      },
      {
        duration: 1000,
      }
    );
    $("body").scrollspy({ target: ".navbar", offset: $(t).offset().top });
    return false;
  });
});

// AOS
AOS.init({
  offset: 120,
  delay: 0,
  duration: 1200,
  easing: "ease",
  once: true,
  mirror: false,
  anchorPlacement: "top-bottom",
  disable: "mobile",
});
