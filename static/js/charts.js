// ====================================================
// Bakery Management System - Chart.js Visualizations
// ====================================================

function initBakeryCharts(data) {
  if (!data) return;

  const palette = {
    caramel: '#D97706',
    caramelLight: 'rgba(217, 119, 6, 0.2)',
    chocolate: '#3E2723',
    amber: '#F59E0B',
    green: '#10B981',
    blue: '#3B82F6',
    purple: '#8B5CF6',
    red: '#EF4444',
    border: '#EADBCE'
  };

  // 1. Daily Sales Chart
  const dailyCanvas = document.getElementById('dailySalesChart');
  if (dailyCanvas && data.daily) {
    new Chart(dailyCanvas, {
      type: 'line',
      data: {
        labels: data.daily.labels,
        datasets: [{
          label: 'Daily Sales ($)',
          data: data.daily.data,
          borderColor: palette.caramel,
          backgroundColor: palette.caramelLight,
          fill: true,
          tension: 0.35,
          pointBackgroundColor: palette.caramel,
          pointRadius: 4,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => ` Sales: $${ctx.raw.toFixed(2)}`
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { callback: val => `$${val}` }
          }
        }
      }
    });
  }

  // 2. Weekly Sales Chart
  const weeklyCanvas = document.getElementById('weeklySalesChart');
  if (weeklyCanvas && data.weekly) {
    new Chart(weeklyCanvas, {
      type: 'bar',
      data: {
        labels: data.weekly.labels,
        datasets: [{
          label: 'Weekly Sales ($)',
          data: data.weekly.data,
          backgroundColor: palette.amber,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { callback: val => `$${val}` }
          }
        }
      }
    });
  }

  // 3. Monthly Sales Chart
  const monthlyCanvas = document.getElementById('monthlySalesChart');
  if (monthlyCanvas && data.monthly) {
    new Chart(monthlyCanvas, {
      type: 'bar',
      data: {
        labels: data.monthly.labels,
        datasets: [{
          label: 'Monthly Sales ($)',
          data: data.monthly.data,
          backgroundColor: palette.chocolate,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { callback: val => `$${val}` }
          }
        }
      }
    });
  }

  // 4. Orders by Status (Doughnut)
  const statusCanvas = document.getElementById('orderStatusChart');
  if (statusCanvas && data.status) {
    new Chart(statusCanvas, {
      type: 'doughnut',
      data: {
        labels: data.status.labels,
        datasets: [{
          data: data.status.data,
          backgroundColor: [
            '#F59E0B', // Pending
            '#3B82F6', // Confirmed
            '#8B5CF6', // Preparing
            '#06B6D4', // Ready
            '#10B981', // Delivered
            '#EF4444'  // Cancelled
          ]
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom' }
        }
      }
    });
  }

  // 5. Top Selling Products (Horizontal Bar)
  const topProdCanvas = document.getElementById('topProductsChart');
  if (topProdCanvas && data.top_products) {
    new Chart(topProdCanvas, {
      type: 'bar',
      data: {
        labels: data.top_products.labels,
        datasets: [{
          label: 'Units Sold',
          data: data.top_products.data,
          backgroundColor: palette.caramel,
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true } }
      }
    });
  }

  // 6. Sales by Category (Pie)
  const catCanvas = document.getElementById('salesCategoryChart');
  if (catCanvas && data.categories) {
    new Chart(catCanvas, {
      type: 'pie',
      data: {
        labels: data.categories.labels,
        datasets: [{
          data: data.categories.data,
          backgroundColor: ['#D97706', '#92400E', '#F59E0B', '#B45309', '#78350F']
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'bottom' } }
      }
    });
  }

  // 7. Inventory Stock vs Reorder Level (Bar)
  const invCanvas = document.getElementById('inventoryChart');
  if (invCanvas && data.inventory) {
    new Chart(invCanvas, {
      type: 'bar',
      data: {
        labels: data.inventory.labels,
        datasets: [
          {
            label: 'Current Stock',
            data: data.inventory.stock,
            backgroundColor: palette.blue,
            borderRadius: 4
          },
          {
            label: 'Reorder Level',
            data: data.inventory.reorder,
            backgroundColor: palette.red,
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'bottom' } },
        scales: { y: { beginAtZero: true } }
      }
    });
  }
}
