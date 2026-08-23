# DineMapAI — Frontend

A complete HTML/CSS/vanilla-JS frontend for the DineMapAI dashboard, built to match the provided Canva design and ready to connect to a Python/Flask backend.

## How the Code Works

**1. Entry point:** `index.html` is the first page. It immediately redirects to `login.html`.

**2. Login logic:** `js/login.js` handles the login form — reading the input, doing basic validation, and calling the API.

**3. API functions:** `js/api.js` is the *only* file that talks to the backend. Every other page calls functions from this file instead of using `fetch()` directly.

**4. How GET requests work:** call `fetchData("/your-endpoint")` (or a wrapper like `getDashboardData()`), which sends a GET request to `API_BASE_URL + endpoint` and returns the parsed JSON.

**5. How POST requests work:** call `postData("/your-endpoint", data)` (or a wrapper like `loginUser()`), which sends a JSON body via POST and returns the parsed JSON response.

**6. Changing the Flask server URL:** open `js/api.js` and edit the `API_BASE_URL` constant at the top. Set `USE_MOCK_DATA = false` once your Flask server is running so the app stops using fake data.

**7. Adding a new page:**
   - Create `your-page.html` in the project root (copy the sidebar/topbar markup from `dashboard.html`).
   - Add a `goToYourPage()` function in `js/navigation.js`.
   - Add a `<li><a>` link in the sidebar with `data-page="your-page.html"` so it highlights correctly.

**8. Adding a new API endpoint:**
   - Add a new function in `js/api.js`, e.g. `async function getReports() { return await fetchData("/reports"); }`.
   - Add matching mock data in `getMockDashboardData()` (or a new mock function) so the page still works before the backend exists.

**9. Connecting a button to a JavaScript function:** avoid inline `onclick="..."` in HTML. Instead, give the element an `id` and attach a listener in JS:
```js
document.getElementById("myButton").addEventListener("click", myFunction);
```

## Project Structure
```
index.html              entry point, redirects to login.html
login.html               login page
welcome.html             post-login onboarding screen
dashboard.html           main dashboard (map, timing, top locations, insights)
analyze-location.html    "Analyze New Location" form + quick presets

css/style.css            all styles (design tokens + layout + components)

js/api.js                all backend communication (GET/POST) + mock data
js/navigation.js         page-to-page navigation + active nav-link highlighting
js/login.js              login form logic
js/dashboard.js          loads + renders all dashboard sections
js/analyze.js            Analyze Location form, timing chips, quick presets
```

## Mock Data Mode
While your Flask backend isn't ready, `USE_MOCK_DATA = true` in `js/api.js` makes every page work with realistic placeholder data. Flip it to `false` and point `API_BASE_URL` at your server whenever you're ready — no other files need to change.

## Backend Endpoints Expected
| Method | Endpoint            | Used by                          |
|--------|----------------------|-----------------------------------|
| POST   | `/login`             | `loginUser()` in login.html       |
| GET    | `/dashboard-data`    | `getDashboardData()` in dashboard.html |
| POST   | `/analyze-location`  | `analyzeLocation()` in analyze-location.html |
