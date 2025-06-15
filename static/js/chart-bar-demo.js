document.addEventListener("DOMContentLoaded", function () {
  const ctx = document.getElementById("industryBarChart"); // Get the canvas element

  // JSON 텍스트를 가져와서 파싱
  const jsonDataElement = document.getElementById("industryData");
  if (!jsonDataElement) {
    console.error("Element with ID 'industryData' not found.");
    return;
  }
  const jsonData = jsonDataElement.textContent;

  let chartData;
  try {
    chartData = JSON.parse(jsonData);
  } catch (e) {
    console.error("JSON 파싱 실패:", e);
    return;
  }

  console.log("chartData (parsed from Django context):", chartData);

  // Check if 'groups' array exists within the parsed data
  if (!chartData || !Array.isArray(chartData.groups)) {
    console.error("chartData.groups is not an array or chartData is null/undefined.");
    return;
  }

  // Extract labels (industry names) and values (change rates) from the 'groups' array
  const labels = chartData.groups.map(g => g.name);
  const values = chartData.groups.map(g => parseFloat(g.changeRate)); // Convert string to float

  // Ensure there's data to chart
  if (labels.length === 0 || values.length === 0) {
    console.warn("No data available for the bar chart.");
    return;
  }

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Change Rate (%)",
        backgroundColor: "rgba(2, 117, 216, 0.7)",
        borderColor: "rgba(2, 117, 216, 1)",
        borderWidth: 1,
        data: values,
      }],
    },
    options: {

      scales: {
        y: {
          beginAtZero: true,
          // Dynamically set min/max for better visualization, handling negative values
          min: Math.min(...values) < 0 ? Math.min(...values) * 1.1 : 0,
          max: Math.max(...values) > 0 ? Math.max(...values) * 1.1 : 0, // Adjust max if all values are zero or negative
          title: {
            display: true,
            text: "Change Rate (%)",
          },
        },
        x: {
          title: {
            display: true,
            text: "Industry",
          },
        },
      },
      plugins: {
        legend: {
          display: true,
          position: "top",
          labels: { font: { size: 14 } },
        },
        tooltip: {
          callbacks: {
            label: context => `${context.dataset.label}: ${context.parsed.y}%`,
          },
        },
      },
      animation: {
        duration: 1500,
        easing: "easeInOutQuad",
      },
      responsive: true, // Make the chart responsive
      maintainAspectRatio: false, // Allow the chart to resize based on parent container
    },
  });
});