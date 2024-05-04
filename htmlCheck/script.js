
$(function () {
  $(".menu-link").click(function () {
    $(".menu-link").removeClass("is-active");
    $(this).addClass("is-active");
  });
});

$(function () {
  $(".main-header-link").click(function () {
    $(".main-header-link").removeClass("is-active");
    $(this).addClass("is-active");
  });
});

const dropdowns = document.querySelectorAll(".dropdown");
dropdowns.forEach((dropdown) => {
  dropdown.addEventListener("click", (e) => {
    e.stopPropagation();
    dropdowns.forEach((c) => c.classList.remove("is-active"));
    dropdown.classList.add("is-active");
  });
});

$(".search-bar input")
  .focus(function () {
    $(".header").addClass("wide");
  })
  .blur(function () {
    $(".header").removeClass("wide");
  });

$(document).click(function (e) {
  var container = $(".status-button");
  var dd = $(".dropdown");
  if (!container.is(e.target) && container.has(e.target).length === 0) {
    dd.removeClass("is-active");
  }
});

$(function () {
  $(".dropdown").on("click", function (e) {
    $(".content-wrapper").addClass("overlay");
    e.stopPropagation();
  });
  $(document).on("click", function (e) {
    if ($(e.target).is(".dropdown") === false) {
      $(".content-wrapper").removeClass("overlay");
    }
  });
});

$(function () {
  $(".status-button:not(.open)").on("click", function (e) {
    $(".overlay-app").addClass("is-active");
  });
  $(".pop-up .close").click(function () {
    $(".overlay-app").removeClass("is-active");
  });
});

$(".status-button:not(.open)").click(function () {
  $(".pop-up").addClass("visible");
});

$(".pop-up .close").click(function () {
  $(".pop-up").removeClass("visible");
});

const toggleButton = document.querySelector(".dark-light");

toggleButton.addEventListener("click", () => {
  document.body.classList.toggle("light-mode");
});


document.addEventListener("DOMContentLoaded", function() {
    // References to buttons and content wrappers
    const allAppsButton = document.querySelector('.menu-link[href="#"]'); // Modify selector to target the "All Apps" button
    const photographyButton = document.querySelector('.side-menu a[href="#"]'); // Modify selector to target the "Photography" button
    const contentWrapper = document.querySelector('.content-wrapper');
    const cardsHtml = `
        <div class="cards">
            <div class="card charizard animated"></div>
            <div class="card pika animated"></div>
            <div class="card eevee animated"></div>
            <div class="card mewtwo animated"></div>
        </div>`;

    // Hide content and show cards on clicking "Photography"
    photographyButton.addEventListener('click', function() {
        contentWrapper.innerHTML = cardsHtml; // Insert the card HTML
        contentWrapper.style.display = 'block'; // Ensure it's visible
    });

    // Show default content on clicking "All Apps"
    allAppsButton.addEventListener('click', function() {
        contentWrapper.innerHTML = ''; // Clear the custom content
        // Ideally, you should restore the original content here, or reload it if it's dynamically generated
        contentWrapper.appendChild(generateDefaultContent()); // Function to restore original content
    });

    // Function to generate the default content dynamically (example structure, replace with your actual content generator)
    function generateDefaultContent() {
        const originalContent = document.createElement('div');
        originalContent.textContent = 'Original Content Here';
        return originalContent;
    }
});
