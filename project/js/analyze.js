/* =========================================================
   analyze.js
   -----------------------------------------------------------
   Handles everything on the "Analyze New Location" page:
   - toggling the Morning/Afternoon/Evening/Night chips
   - filling the form from a Quick Preset card
   - submitting the form to the backend
   ========================================================= */

// Values used by the Quick Preset cards. Edit this object to
// change what each preset fills in.
const QUICK_PRESETS = {
  collegeCafe: {
    restaurantType: "cafe",
    targetAudience: "students",
    budgetRange: "low",
  },
  officeLunch: {
    restaurantType: "fast-food",
    targetAudience: "office-workers",
    budgetRange: "medium",
  },
  familyRestaurant: {
    restaurantType: "fine-dining",
    targetAudience: "families",
    budgetRange: "medium-high",
  },
  quickBites: {
    restaurantType: "fast-food",
    targetAudience: "general",
    budgetRange: "low",
  },
};

document.addEventListener("DOMContentLoaded", () => {
  setupTimingChips();
  setupPresetButtons();
  setupAnalyzeForm();
});

// ---------------------------------------------------------
// Loading overlay (shown while we wait for POST /analyze-location)
// ---------------------------------------------------------

// Friendlier labels for the raw <select> values, used only to build
// the status messages below.
const RESTAURANT_TYPE_LABELS = {
  cafe: "café",
  "fast-food": "fast food spot",
  "fine-dining": "fine dining restaurant",
  bakery: "bakery",
};

const TARGET_AUDIENCE_LABELS = {
  students: "students",
  "office-workers": "office workers",
  families: "families",
  general: "the general public",
};

let loadingMessageTimer = null;
let loadingProgressTimer = null;

/**
 * Builds the list of status lines the overlay cycles through,
 * personalized with whatever the user actually typed/selected so it
 * reads like the server is really working through their inputs.
 */
function buildLoadingMessages(formData) {
  const city = formData.cityArea || "your area";
  const type = RESTAURANT_TYPE_LABELS[formData.restaurantType] || "restaurant";
  const audience = TARGET_AUDIENCE_LABELS[formData.targetAudience] || "your target audience";
  const slotCount = formData.timingSlots.length;

  return [
    `Scanning ${city} for high-opportunity zones...`,
    `Mapping nearby competitors & existing ${type}s...`,
    `Analyzing foot traffic & demand for ${audience}...`,
    `Cross-referencing colleges, metro stations & landmarks...`,
    slotCount > 0
      ? `Modeling ${slotCount} timing slot${slotCount > 1 ? "s" : ""} for performance patterns...`
      : `Modeling timing performance across the day...`,
    `Weighing rent potential against local competition...`,
    `Ranking the top-scoring locations for ${city}...`,
  ];
}

/**
 * Shows the full-screen neon loading overlay and starts cycling the
 * status text + creeping the progress bar until finishAnalyzeLoadingOverlay
 * or hideAnalyzeLoadingOverlay is called.
 */
function showAnalyzeLoadingOverlay(formData) {
  const overlay = document.getElementById("analyzeLoadingOverlay");
  const statusText = document.getElementById("loadingStatusText");
  const progressBar = document.getElementById("loadingProgressBar");
  if (!overlay || !statusText || !progressBar) return;

  const messages = buildLoadingMessages(formData);
  let messageIndex = 0;
  let progress = 6;

  overlay.classList.remove("loading-complete");
  overlay.classList.add("show");
  overlay.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";

  statusText.textContent = messages[0];
  progressBar.style.width = progress + "%";

  loadingMessageTimer = setInterval(() => {
    messageIndex = (messageIndex + 1) % messages.length;
    statusText.classList.add("fade");
    setTimeout(() => {
      statusText.textContent = messages[messageIndex];
      statusText.classList.remove("fade");
    }, 220);
  }, 1900);

  // Progress bar creeps toward ~90% while we wait for the real
  // response — it only reaches 100% once the server actually replies.
  loadingProgressTimer = setInterval(() => {
    progress = Math.min(progress + Math.random() * 6, 90);
    progressBar.style.width = progress + "%";
  }, 650);
}

/** Immediately hides the overlay (used on error / retry). */
function hideAnalyzeLoadingOverlay() {
  const overlay = document.getElementById("analyzeLoadingOverlay");
  if (!overlay) return;

  clearInterval(loadingMessageTimer);
  clearInterval(loadingProgressTimer);

  overlay.classList.remove("show", "loading-complete");
  overlay.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}

/**
 * Called once the server responds successfully with the analysis
 * data: fills the progress bar, flips the overlay to its "complete"
 * (green/neon) look, then runs `callback` (the dashboard redirect)
 * after a short beat so the finish is visible instead of instant.
 */
function finishAnalyzeLoadingOverlay(callback) {
  const overlay = document.getElementById("analyzeLoadingOverlay");
  const statusText = document.getElementById("loadingStatusText");
  const progressBar = document.getElementById("loadingProgressBar");

  clearInterval(loadingMessageTimer);
  clearInterval(loadingProgressTimer);

  if (statusText) statusText.textContent = "Analysis complete! Redirecting to dashboard...";
  if (progressBar) progressBar.style.width = "100%";
  if (overlay) overlay.classList.add("loading-complete");

  setTimeout(() => {
    if (overlay) {
      overlay.classList.remove("show", "loading-complete");
      overlay.setAttribute("aria-hidden", "true");
    }
    document.body.style.overflow = "";
    if (callback) callback();
  }, 550);
}

// ---------------------------------------------------------
// Timing chips (Morning / Afternoon / Evening / Night)
// Clicking a chip toggles it on/off. Selected chips are sent
// with the form as an array of strings.
// ---------------------------------------------------------
function setupTimingChips() {
  const chips = document.querySelectorAll(".timing-chip");

  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      chip.classList.toggle("chip-selected");
    });
  });
}

function getSelectedTimingSlots() {
  const selected = document.querySelectorAll(".timing-chip.chip-selected");
  return Array.from(selected).map((chip) => chip.dataset.slot);
}

// ---------------------------------------------------------
// Quick Presets — fills the form with common combinations
// ---------------------------------------------------------
function setupPresetButtons() {
  const presetButtons = document.querySelectorAll("[data-preset]");

  presetButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const presetKey = button.dataset.preset;
      applyPreset(presetKey);
    });
  });
}

function applyPreset(presetKey) {
  const preset = QUICK_PRESETS[presetKey];
  if (!preset) return;

  document.getElementById("restaurantType").value = preset.restaurantType;
  document.getElementById("targetAudience").value = preset.targetAudience;
  document.getElementById("budgetRange").value = preset.budgetRange;
}

// ---------------------------------------------------------
// Form submission
// ---------------------------------------------------------
function setupAnalyzeForm() {
  const form = document.getElementById("analyzeForm");
  const formMessage = document.getElementById("analyzeFormMessage");
  const submitButton = document.getElementById("analyzeSubmitBtn");

  if (!form) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const cityArea = document.getElementById("cityArea").value.trim();
    const restaurantType = document.getElementById("restaurantType").value;

    // Basic frontend validation — the two required fields
    if (cityArea === "" || restaurantType === "") {
      showAnalyzeMessage("Please fill in the City / Area and Restaurant Type fields.", "error");
      return;
    }

    const formData = {
      cityArea: cityArea,
      restaurantType: restaurantType,
      targetAudience: document.getElementById("targetAudience").value,
      budgetRange: document.getElementById("budgetRange").value,
      businessGoals: document.getElementById("businessGoals").value.trim(),
      additionalPreferences: document.getElementById("additionalPreferences").value.trim(),
      timingSlots: getSelectedTimingSlots(),
    };

    submitButton.disabled = true;
    submitButton.textContent = "Analyzing...";
    showAnalyzeLoadingOverlay(formData);

    const result = await analyzeLocation(formData);

    submitButton.disabled = false;
    submitButton.innerHTML = '<i class="fa-solid fa-arrow-trend-up"></i> Analyze Location';

    if (result.success) {
      // Loading overlay stays up until the server has actually replied
      // with the analysis data, then hands off to the dashboard.
      finishAnalyzeLoadingOverlay(() => {
        showAnalyzeMessage(result.message || "Analysis started!", "success");
        goToDashboard();
      });
    } else {
      hideAnalyzeLoadingOverlay();
      showAnalyzeMessage(result.message || "Something went wrong. Please try again.", "error");
    }
  });

  function showAnalyzeMessage(text, type) {
    formMessage.textContent = text;
    formMessage.className = `form-message show ${type}`;
  }
}
