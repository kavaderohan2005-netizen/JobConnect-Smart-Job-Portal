// ===================================================================
// JobConnect – Chart.js Visualizations for Dashboards
// ===================================================================

function initStatusChart(canvasId, dataMap) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  const labels = Object.keys(dataMap);
  const data = Object.values(dataMap);

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: [
          '#2563eb', // Applied - Blue
          '#f59e0b', // Under Review - Amber
          '#8b5cf6', // Shortlisted - Purple
          '#06b6d4', // Interview - Cyan
          '#10b981', // Accepted - Green
          '#ef4444'  // Rejected - Red
        ],
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            boxWidth: 12,
            font: { family: 'Inter', size: 12 }
          }
        }
      },
      cutout: '68%'
    }
  });
}

function initCategoryChart(canvasId, catLabels, catCounts) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: catLabels,
      datasets: [{
        label: 'Active Job Postings',
        data: catCounts,
        backgroundColor: '#3b82f6',
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: { stepSize: 1 }
        },
        x: {
          ticks: {
            maxRotation: 45,
            minRotation: 25,
            font: { size: 11 }
          }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function initTrendsChart(canvasId) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
      datasets: [
        {
          label: 'Jobs Posted',
          data: [12, 19, 25, 32, 45, 58],
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37, 99, 235, 0.1)',
          fill: true,
          tension: 0.35,
          borderWidth: 2
        },
        {
          label: 'Applications Submitted',
          data: [28, 45, 70, 92, 135, 184],
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.08)',
          fill: true,
          tension: 0.35,
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { boxWidth: 12 }
        }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
}
