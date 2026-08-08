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

    const result = await analyzeLocation(formData);

    submitButton.disabled = false;
    submitButton.innerHTML = '<i class="fa-solid fa-arrow-trend-up"></i> Analyze Location';

    if (result.success) {
      showAnalyzeMessage(result.message || "Analysis started!", "success");
      setTimeout(goToDashboard, 700);
    } else {
      showAnalyzeMessage(result.message || "Something went wrong. Please try again.", "error");
    }
  });

  function showAnalyzeMessage(text, type) {
    formMessage.textContent = text;
    formMessage.className = `form-message show ${type}`;
  }
}
