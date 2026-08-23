/* =========================================================
   login.js
   -----------------------------------------------------------
   Handles the login form only. Real authentication (checking
   the password) happens on the Python backend — this file just
   collects the input, does simple checks, and calls the API.
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  const usernameInput = document.getElementById("username");
  const passwordInput = document.getElementById("password");
  const formMessage = document.getElementById("formMessage");
  const loginButton = document.getElementById("loginButton");

  loginForm.addEventListener("submit", handleLoginSubmit);

  async function handleLoginSubmit(event) {
    event.preventDefault(); // stop the browser from reloading the page

    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    // 1. Basic frontend validation (never do real auth checks here)
    if (username === "" || password === "") {
      showMessage("Please enter both a username/email and a password.", "error");
      return;
    }

    // 2. Show a loading state while we wait for the backend
    setLoading(true);

    // 3. Call the login function from api.js, which sends the
    //    request to the Flask backend (or returns mock data)
    const result = await loginUser(username, password);

    setLoading(false);

    // 4. Handle the backend's response
    if (result.success) {
      showMessage(result.message || "Login successful!", "success");
      // Small delay so the user can see the success message
      setTimeout(goToWelcome, 500);
    } else {
      showMessage(result.message || "Login failed. Please try again.", "error");
    }
  }

  function showMessage(text, type) {
    formMessage.textContent = text;
    formMessage.className = `form-message show ${type}`;
  }

  function setLoading(isLoading) {
    loginButton.disabled = isLoading;
    loginButton.textContent = isLoading ? "Logging in..." : "Log In";
  }
});
