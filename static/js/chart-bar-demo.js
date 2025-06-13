document.addEventListener("DOMContentLoaded", function () {
  const scriptTag = document.getElementById("industryData");
  if (!scriptTag) {
    console.error("Error: 'industryData' script element not found!");
    return;
  }

  let chartData;
  try {
    chartData = JSON.parse(scriptTag.textContent);
  } catch (e) {
    console.error("Error parsing JSON data:", e);
    return;
  }

  console.log("chartData:", chartData);
  // 방어코드 예시
  if (!chartData.values || !Array.isArray(chartData.values)) {
    console.error("chartData.values is not iterable");
  } else {
    const minValue = Math.min(...chartData.values);
    console.log("Minimum value:", minValue);
  }

  // Get the canvas element context
  const ctx = document.getElementById("industryBarChart").getContext("2d");

  // Check if the canvas context was successfully retrieved
  if (!ctx) {
    console.error(
      "Error: Could not get 2D context for 'industryBarChart' canvas."
    );
    return; // Exit if canvas context is unavailable
  }

  // Create a new bar chart using Chart.js
  new Chart(ctx, {
    type: "bar", // Set chart type to bar
    data: {
      labels: chartData.labels, // Labels for the x-axis (industry names)
      datasets: [
        {
          label: "Change Rate (%)", // Label for the dataset
          backgroundColor: "rgba(2, 117, 216, 0.7)", // Bar fill color
          borderColor: "rgba(2, 117, 216, 1)", // Bar border color
          borderWidth: 1, // Border width
          data: chartData.values, // Data values for the bars
        },
      ],
    },
    options: {
      responsive: true, // Make the chart responsive
      maintainAspectRatio: false, // Allow canvas to resize freely based on container
      scales: {
        y: {
          beginAtZero: true, // Start y-axis at zero
          // Dynamically set min/max for y-axis based on data values
          min:
            Math.min(...chartData.values) < 0
              ? Math.min(...chartData.values) * 1.1
              : 0,
          max: Math.max(...chartData.values) * 1.1,
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
          display: true, // Display the legend
          position: "top", // Position the legend at the top
          labels: {
            font: {
              size: 14, // Adjust legend font size
            },
          },
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              return context.dataset.label + ": " + context.parsed.y + "%";
            },
          },
        },
      },
      // Add animation for a smoother appearance
      animation: {
        duration: 1500, // Animation duration in milliseconds
        easing: "easeInOutQuad", // Easing function for animation
      },
    },
  });
});
