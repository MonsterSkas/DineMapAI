/* =========================================================
   api.js
   -----------------------------------------------------------
   This file is the ONLY place that talks to the Python/Flask
   backend. Every other JS file should call the functions in
   here instead of using fetch() directly.

   HOW TO CONNECT YOUR FLASK BACKEND:
   1. Change API_BASE_URL below to your server address.
   2. Set USE_MOCK_DATA to false.
   3. Make sure your Flask routes match the endpoint strings
      used in the functions below (e.g. "/login", "/dashboard-data").
   ========================================================= */

// ---------------------------------------------------------
// CONFIGURATION — change these two lines to connect a real backend
// ---------------------------------------------------------
const API_BASE_URL = "http://127.0.0.1:5000"; // <-- your Flask server address
const USE_MOCK_DATA = true; // <-- set to false once your backend is running

// ---------------------------------------------------------
// GENERIC REQUEST HELPERS
// Every POST and GET call in the app goes through these two
// functions, so error handling only has to be written once.
// ---------------------------------------------------------

/**
 * Send a POST request with a JSON body to the backend.
 * @param {string} endpoint - e.g. "/login"
 * @param {object} data - the JSON body to send
 * @returns {Promise<object>} the parsed JSON response
 */
async function postData(endpoint, data) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Server responded with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error (POST ${endpoint}):`, error);
    // Return a consistent error shape so calling code doesn't crash
    return { success: false, message: "Could not reach the server. Please try again." };
  }
}

/**
 * Send a GET request to the backend.
 * @param {string} endpoint - e.g. "/dashboard-data"
 * @returns {Promise<object>} the parsed JSON response
 */
async function fetchData(endpoint) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);

    if (!response.ok) {
      throw new Error(`Server responded with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error (GET ${endpoint}):`, error);
    return { success: false, message: "Could not reach the server. Please try again." };
  }
}

// ---------------------------------------------------------
// AUTH ENDPOINTS
// ---------------------------------------------------------

/**
 * Log a user in. Talks to POST /login on the Flask backend.
 * The backend (not this file) is responsible for checking the
 * password and creating a session/token.
 */
async function loginUser(username, password) {
  if (USE_MOCK_DATA) {
    // Fake network delay so the UI feels realistic while testing
    await mockDelay();
    if (username.trim() !== "" && password.trim() !== "") {
      return { success: true, message: "Login successful (mock data)." };
    }
    return { success: false, message: "Invalid username or password (mock data)." };
  }

  return await postData("/login", { username, password });
}

// ---------------------------------------------------------
// DASHBOARD ENDPOINTS
// ---------------------------------------------------------

/**
 * Get all data needed to render the dashboard page.
 * Talks to GET /dashboard-data on the Flask backend.
 */
async function getDashboardData() {
  if (USE_MOCK_DATA) {
    await mockDelay();
    return getMockDashboardData();
  }

  return await fetchData("/dashboard-data");
}

/**
 * Send a new "Analyze Location" request to the backend.
 * Talks to POST /analyze-location on the Flask backend.
 */
async function analyzeLocation(formData) {
  if (USE_MOCK_DATA) {
    await mockDelay();
    return { success: true, message: "Analysis started (mock data)." };
  }

  return await postData("/analyze-location", formData);
}

// ---------------------------------------------------------
// MOCK DATA
// Used only while USE_MOCK_DATA is true. This lets the frontend
// be built and demoed before the Flask backend exists.
// Everything below is clearly fake placeholder data.
// ---------------------------------------------------------

function mockDelay(ms = 400) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function getMockDashboardData() {
  return {
    success: true,
    user: {
      name: "DR",
      location: "Kolkata, West Bengal",
    },
    timingPerformance: [
      { label: "Morning", time: "6 AM - 11 AM", score: 72, status: "Good", color: "green" },
      { label: "Afternoon", time: "11 AM - 4 PM", score: 85, status: "Very Good", color: "blue" },
      { label: "Evening", time: "4 PM - 10 PM", score: 94, status: "Excellent", color: "purple" },
      { label: "Night", time: "10 PM - 2 AM", score: 68, status: "Moderate", color: "orange" },
    ],
    demandTrend: [
      { hour: "12 AM", value: 8 },
      { hour: "4 AM", value: 4 },
      { hour: "8 AM", value: 52 },
      { hour: "12 PM", value: 48 },
      { hour: "4 PM", value: 78 },
      { hour: "8 PM", value: 92 },
      { hour: "12 AM", value: 30 },
    ],
    topLocations: [
      { rank: 1, letter: "A", name: "Lake Gardens", score: 91, desc: "High college density • Good connectivity • Low competition", color: "#7c5cfc" },
      { rank: 2, letter: "B", name: "Jadavpur", score: 87, desc: "High footfall • Near universities • Good transport", color: "#3b82f6" },
      { rank: 3, letter: "C", name: "Salt Lake Sector V", score: 82, desc: "Office crowd • High demand • Moderate competition", color: "#22c55e" },
      { rank: 4, letter: "D", name: "Gariahat", score: 78, desc: "Shopping area • Good footfall • Moderate competition", color: "#f5a524" },
      { rank: 5, letter: "E", name: "New Town Action Area 1", score: 74, desc: "Upcoming area • Growing population • Good roads", color: "#22c55e" },
    ],
    scoreBreakdown: {
      locationName: "Location A",
      axes: [
        { label: "Demand", value: 95 },
        { label: "Accessibility", value: 85 },
        { label: "Target Audience", value: 90 },
        { label: "Competition (Inverted)", value: 80 },
        { label: "Nearby Facilities", value: 88 },
      ],
    },
    keyInsights: [
      { icon: "fa-arrow-trend-up", color: "green", text: "Evening performance is strongest (4 PM - 10 PM). Ideal for dinner & hangout crowds." },
      { icon: "fa-circle-info", color: "blue", text: "College proximity is a major demand driver in this area." },
      { icon: "fa-triangle-exclamation", color: "orange", text: "Competition is moderate compared to popular commercial zones." },
      { icon: "fa-subway", color: "purple", text: "Areas near metro stations show 18% higher footfall potential." },
    ],
    dataOverview: [
      { label: "Total Restaurants", value: "1,248" },
      { label: "Cafés", value: "432" },
      { label: "Colleges", value: "35" },
      { label: "Metro Stations", value: "28" },
      { label: "Avg. Population", value: "12.4 L" },
    ],
  };
}
