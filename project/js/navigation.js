/* =========================================================
   navigation.js
   -----------------------------------------------------------
   All page-to-page navigation lives here. Keeping every
   window.location.href call in one file makes it easy to find
   and rename pages later.

   HOW TO ADD A NEW PAGE:
   1. Create the new .html file in the project root.
   2. Add a "goToYourPage()" function below.
   3. Connect a sidebar link or button to it (see dashboard.js
      or analyze.js for examples of addEventListener).
   ========================================================= */

function goToLogin() {
  window.location.href = "login.html";
}

function goToWelcome() {
  window.location.href = "welcome.html";
}

function goToDashboard() {
  window.location.href = "dashboard.html";
}

function goToAnalyzeLocation() {
  window.location.href = "analyze-location.html";
}

/**
 * Logs the user out. In a real app this would also call the
 * backend to destroy the session/token before redirecting.
 */
function logout() {
  // Example of where you would clear stored session info:
  // localStorage / cookies are intentionally NOT used here per
  // project requirements — wire this up to your auth solution.
  goToLogin();
}

/**
 * Highlights the current page's link in the sidebar.
 * Every sidebar link should have a "data-page" attribute that
 * matches the current HTML filename (see the sidebar markup in
 * dashboard.html / analyze-location.html).
 */
function highlightActiveNavLink() {
  const currentPage = window.location.pathname.split("/").pop() || "dashboard.html";
  const navLinks = document.querySelectorAll(".nav-link[data-page]");

  navLinks.forEach((link) => {
    if (link.getAttribute("data-page") === currentPage) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });
}

/**
 * Sets up the mobile hamburger button to show/hide the sidebar
 * on small screens. Safe to call even if the button isn't on
 * the page (it just does nothing).
 */
function setupMobileNavToggle() {
  const toggleButton = document.getElementById("mobileNavToggle");
  const sidebar = document.querySelector(".sidebar");

  if (!toggleButton || !sidebar) return;

  toggleButton.addEventListener("click", () => {
    sidebar.classList.toggle("open");
  });
}

// Run automatically on every page that includes this script
document.addEventListener("DOMContentLoaded", () => {
  highlightActiveNavLink();
  setupMobileNavToggle();
});
