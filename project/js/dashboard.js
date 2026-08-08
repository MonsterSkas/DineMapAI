/* =========================================================
   dashboard.js
   -----------------------------------------------------------
   Fetches dashboard data (mock or real, see api.js) and fills
   in every section of the page. Each section has its own small
   "update" function so it's easy to find and change later.
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
  loadDashboard();
  setupFilterBarButton();
});

/**
 * Main entry point for the dashboard page. Gets the data, then
 * hands it off to smaller functions that each update one part
 * of the screen.
 */
async function loadDashboard() {
  const data = await getDashboardData();

  if (!data.success) {
    console.error("Failed to load dashboard data:", data.message);
    return;
  }

  updateUserInfo(data.user);
  updateTimingPerformance(data.timingPerformance);
  updateDemandChart(data.demandTrend);
  updateTopLocations(data.topLocations);
  updateScoreBreakdown(data.scoreBreakdown);
  updateNotifications(data.keyInsights); // "notifications" = key insights panel on this page
  updateDataOverview(data.dataOverview);
}

// ---------------------------------------------------------
// Section: user info (topbar)
// ---------------------------------------------------------
function updateUserInfo(user) {
  const locationLabel = document.getElementById("userLocationLabel");
  const avatar = document.getElementById("userAvatar");

  if (locationLabel && user.location) {
    locationLabel.textContent = user.location;
  }
  if (avatar && user.name) {
    avatar.textContent = user.name;
  }
}

// ---------------------------------------------------------
// Section: timing performance rings
// ---------------------------------------------------------
const RING_COLORS = {
  green: "#22c55e",
  blue: "#3b82f6",
  purple: "#7c5cfc",
  orange: "#f5a524",
};

function updateTimingPerformance(slots) {
  const container = document.getElementById("timingGrid");
  if (!container) return;

  container.innerHTML = ""; // clear any placeholder content

  slots.forEach((slot) => {
    const color = RING_COLORS[slot.color] || RING_COLORS.purple;
    const percent = Math.max(0, Math.min(100, slot.score));
    const degrees = (percent / 100) * 360;

    const slotEl = document.createElement("div");
    slotEl.className = "timing-slot";
    slotEl.innerHTML = `
      <div class="slot-label">${slot.label}</div>
      <div class="slot-time">${slot.time}</div>
      <div class="ring" style="background: conic-gradient(${color} ${degrees}deg, rgba(255,255,255,0.08) ${degrees}deg)">
        <div class="ring-value">${slot.score}<small>/100</small></div>
      </div>
      <div class="ring-status" style="color:${color}">${slot.status}</div>
    `;
    container.appendChild(slotEl);
  });
}

// ---------------------------------------------------------
// Section: demand trend line chart (drawn as plain SVG so no
// charting library is required)
// ---------------------------------------------------------
function updateDemandChart(points) {
  const svgContainer = document.getElementById("demandChartSvg");
  const axisLabels = document.getElementById("demandChartLabels");
  if (!svgContainer || points.length === 0) return;

  const width = 500;
  const height = 160;
  const paddingX = 10;
  const maxValue = 100;

  // Convert each data point into an (x, y) pixel coordinate
  const stepX = (width - paddingX * 2) / (points.length - 1);
  const coords = points.map((point, index) => {
    const x = paddingX + stepX * index;
    const y = height - (point.value / maxValue) * height;
    return { x, y };
  });

  // Build the SVG path string, e.g. "M10,150 L90,120 L170,80 ..."
  const linePath = coords
    .map((coord, index) => `${index === 0 ? "M" : "L"}${coord.x},${coord.y}`)
    .join(" ");

  // Build a filled area under the line for the purple gradient look
  const areaPath = `${linePath} L${coords[coords.length - 1].x},${height} L${coords[0].x},${height} Z`;

  svgContainer.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svgContainer.innerHTML = `
    <defs>
      <linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#7c5cfc" stop-opacity="0.45" />
        <stop offset="100%" stop-color="#7c5cfc" stop-opacity="0" />
      </linearGradient>
    </defs>
    <path d="${areaPath}" fill="url(#areaFill)" stroke="none" />
    <path d="${linePath}" fill="none" stroke="#9c85ff" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round" />
    ${coords.map((c) => `<circle cx="${c.x}" cy="${c.y}" r="3.5" fill="#9c85ff" />`).join("")}
  `;

  if (axisLabels) {
    axisLabels.innerHTML = points.map((p) => `<span>${p.hour}</span>`).join("");
  }
}

// ---------------------------------------------------------
// Section: top recommended locations list
// ---------------------------------------------------------
function updateCards(locations) {
  // Kept as a separate, clearly named function per project spec
  // even though it currently shares logic with updateTopLocations.
  updateTopLocations(locations);
}

function updateTopLocations(locations) {
  const list = document.getElementById("topLocationsList");
  if (!list) return;

  list.innerHTML = "";

  locations.forEach((location) => {
    const item = document.createElement("li");
    item.className = "rank-item";
    item.innerHTML = `
      <span class="rank-number">${location.rank}</span>
      <span class="rank-avatar" style="background:${location.color}">${location.letter}</span>
      <span class="rank-info">
        <span class="rank-name">${location.name}</span>
        <span class="rank-desc">${location.desc}</span>
      </span>
      <span class="rank-score" style="color:${location.color}">${location.score}<br><small>/100</small></span>
    `;
    list.appendChild(item);
  });
}

// ---------------------------------------------------------
// Section: score breakdown radar chart
// ---------------------------------------------------------
function updateStatistics(scoreBreakdown) {
  // Alias kept for naming consistency with the project spec
  // (updateStatistics / updateScoreBreakdown do the same job).
  updateScoreBreakdown(scoreBreakdown);
}

function updateScoreBreakdown(scoreBreakdown) {
  const titleEl = document.getElementById("scoreBreakdownTitle");
  const svgContainer = document.getElementById("radarChartSvg");
  if (titleEl) {
    titleEl.textContent = `Score Breakdown (${scoreBreakdown.locationName})`;
  }
  if (!svgContainer) return;

  const axes = scoreBreakdown.axes;
  const size = 260;
  const center = size / 2;
  const maxRadius = 90;
  const angleStep = (Math.PI * 2) / axes.length;

  // Work out the (x, y) point for a given value on a given axis
  function pointFor(value, index, radius = maxRadius) {
    const angle = angleStep * index - Math.PI / 2; // start from the top
    const distance = (value / 100) * radius;
    return {
      x: center + distance * Math.cos(angle),
      y: center + distance * Math.sin(angle),
    };
  }

  // Draw 3 faint background rings (25%, 50%, 75%, 100%) for reference
  const gridRings = [0.25, 0.5, 0.75, 1].map((fraction) => {
    const ringPoints = axes.map((_, index) => pointFor(100 * fraction, index));
    const pointsAttr = ringPoints.map((p) => `${p.x},${p.y}`).join(" ");
    return `<polygon points="${pointsAttr}" fill="none" stroke="rgba(255,255,255,0.08)" />`;
  }).join("");

  // Draw the actual data shape
  const dataPoints = axes.map((axis, index) => pointFor(axis.value, index));
  const dataPointsAttr = dataPoints.map((p) => `${p.x},${p.y}`).join(" ");

  // Draw axis lines + labels
  const axisLines = axes.map((axis, index) => {
    const outerPoint = pointFor(100, index);
    const labelPoint = pointFor(122, index);
    return `
      <line x1="${center}" y1="${center}" x2="${outerPoint.x}" y2="${outerPoint.y}" stroke="rgba(255,255,255,0.1)" />
      <text x="${labelPoint.x}" y="${labelPoint.y}" text-anchor="middle" class="radar-label">${axis.label}</text>
      <text x="${labelPoint.x}" y="${labelPoint.y + 12}" text-anchor="middle" class="radar-value">${axis.value}</text>
    `;
  }).join("");

  svgContainer.setAttribute("viewBox", `0 0 ${size} ${size + 20}`);
  svgContainer.innerHTML = `
    ${gridRings}
    ${axisLines}
    <polygon points="${dataPointsAttr}" fill="rgba(124,92,252,0.35)" stroke="#9c85ff" stroke-width="2" />
    ${dataPoints.map((p) => `<circle cx="${p.x}" cy="${p.y}" r="3" fill="#9c85ff" />`).join("")}
  `;
}

// ---------------------------------------------------------
// Section: key insights (labelled "notifications" in the spec)
// ---------------------------------------------------------
const INSIGHT_COLORS = {
  green: { bg: "rgba(34,197,94,0.15)", fg: "#4ade80" },
  blue: { bg: "rgba(59,130,246,0.15)", fg: "#60a5fa" },
  orange: { bg: "rgba(245,165,36,0.15)", fg: "#fbbf24" },
  purple: { bg: "rgba(124,92,252,0.15)", fg: "#9c85ff" },
};

function updateNotifications(insights) {
  const list = document.getElementById("keyInsightsList");
  if (!list) return;

  list.innerHTML = "";

  insights.forEach((insight) => {
    const colors = INSIGHT_COLORS[insight.color] || INSIGHT_COLORS.purple;
    const item = document.createElement("li");
    item.className = "insight-item";
    item.innerHTML = `
      <span class="insight-icon" style="background:${colors.bg}; color:${colors.fg}">
        <i class="fa-solid ${insight.icon}"></i>
      </span>
      <p>${insight.text}</p>
    `;
    list.appendChild(item);
  });
}

// ---------------------------------------------------------
// Section: data overview stats
// ---------------------------------------------------------
function updateDataOverview(stats) {
  const container = document.getElementById("dataOverviewGrid");
  if (!container) return;

  container.innerHTML = "";

  stats.forEach((stat) => {
    const statEl = document.createElement("div");
    statEl.innerHTML = `
      <div class="stat-value">${stat.value}</div>
      <div class="stat-label">${stat.label}</div>
    `;
    container.appendChild(statEl);
  });
}

// ---------------------------------------------------------
// Filter bar "Analyze Location" button
// ---------------------------------------------------------
function setupFilterBarButton() {
  const analyzeButton = document.getElementById("analyzeLocationBtn");
  if (analyzeButton) {
    analyzeButton.addEventListener("click", goToAnalyzeLocation);
  }
}
