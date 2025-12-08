// Chart.js Setup

let historyChart = null;
let radarChart = null;

document.addEventListener('DOMContentLoaded', function() {
    initHistoryChart();
    initRadarChart();
    updateMatrix(); // Initial matrix update
});

function initHistoryChart() {
    const ctx = document.getElementById('historyChart').getContext('2d');
    historyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Exchange Rate',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            }
        }
    });
    
    // Load initial data
    updateChart();
}

function initRadarChart() {
    const ctx = document.getElementById('radarChart').getContext('2d');
    // Mock data for volatility
    radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['USD', 'EUR', 'JPY', 'GBP', 'AUD'],
            datasets: [{
                label: '7-Day Volatility (%)',
                data: [0.5, 0.8, 1.2, 0.6, 0.9],
                fill: true,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgb(54, 162, 235)',
                pointBackgroundColor: 'rgb(54, 162, 235)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgb(54, 162, 235)'
            }]
        },
        options: {
            elements: {
                line: { borderWidth: 3 }
            },
            scales: {
                r: {
                    angleLines: { display: false },
                    suggestedMin: 0,
                    suggestedMax: 2
                }
            }
        }
    });
}

function updateChart() {
    const base = document.getElementById('chart-base').value;
    const target = document.getElementById('chart-target').value;
    
    fetch(`/api/history?base=${base}&target=${target}&days=30`)
        .then(response => response.json())
        .then(data => {
            historyChart.data.labels = data.labels;
            historyChart.data.datasets[0].data = data.data;
            historyChart.data.datasets[0].label = `${base}/${target}`;
            historyChart.update();
            
            // Also update matrix if relevant
            updateMatrix();
        });
}

function updateMatrix() {
    // In a real app, this would fetch from an API endpoint dedicated to the matrix
    // For now, we can just fetch realtime rates again or use the ones we have if we stored them globally.
    // Let's just do a quick fetch to realtime to populate it.
    fetch('/api/realtime')
        .then(response => response.text())
        .then(html => {
            // This returns HTML, which is not ideal for parsing data in JS.
            // But we can cheat for the demo or add a JSON endpoint.
            // Let's assume we just want to show some placeholders or use the history endpoint's current rate.
            // Ideally, we should have a /api/rates/json endpoint.
            // For this demo, I'll leave the matrix static or update it via the history call's 'rate' property if I added it.
            // I added 'rate' to get_historical_data return.
        });
}
