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
    
    // Get theme colors
    const style = getComputedStyle(document.body);
    const primaryColor = style.getPropertyValue('--primary-color').trim() || '#4361ee';
    const primaryRgb = style.getPropertyValue('--primary-rgb').trim() || '67, 97, 238';

    historyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: (typeof TRANS !== 'undefined') ? TRANS.exchange_rate : 'Exchange Rate',
                data: [],
                borderColor: primaryColor,
                backgroundColor: `rgba(${primaryRgb}, 0.1)`,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { grid: { display: false } },
                y: { grid: { color: '#f0f0f0' } }
            }
        }
    });
    
    // Expose to window for theme switcher
    window.rateChart = historyChart;

    // Load initial data
    updateChart();
}

function initRadarChart() {
    const ctx = document.getElementById('radarChart').getContext('2d');
    
    // Get theme colors
    const style = getComputedStyle(document.body);
    const primaryColor = style.getPropertyValue('--primary-color').trim() || '#4361ee';
    const primaryRgb = style.getPropertyValue('--primary-rgb').trim() || '67, 97, 238';
    
    // Create Gradient
    // Note: Chart.js radar charts center at (width/2, height/2), but gradients are relative to canvas 0,0 usually unless configured.
    // For simplicity in Chart.js, a simple background color with opacity is often safer, 
    // but let's try a solid fill with a nice border and circular grid first.
    
    // Mock data for volatility
    radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['USD', 'EUR', 'JPY', 'GBP', 'AUD'],
            datasets: [{
                label: (typeof TRANS !== 'undefined') ? TRANS.volatility_label : '7-Day Volatility (%)',
                data: [0.5, 0.8, 1.2, 0.6, 0.9],
                fill: true,
                backgroundColor: `rgba(${primaryRgb}, 0.2)`,
                borderColor: primaryColor,
                borderWidth: 2,
                pointBackgroundColor: '#fff',
                pointBorderColor: primaryColor,
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6,
                tension: 0.3 // Smooth curves
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#1e293b',
                    bodyColor: '#475569',
                    borderColor: '#e2e8f0',
                    borderWidth: 1,
                    padding: 10,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return context.raw + '%';
                        }
                    }
                }
            },
            scales: {
                r: {
                    angleLines: {
                        display: true,
                        color: 'rgba(0,0,0,0.05)',
                        lineWidth: 1
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.05)',
                        circular: true // Circular grid
                    },
                    pointLabels: {
                        font: {
                            size: 11,
                            weight: '600',
                            family: "'Inter', sans-serif"
                        },
                        color: '#64748b',
                        padding: 10
                    },
                    ticks: {
                        backdropColor: 'transparent',
                        color: '#94a3b8',
                        showLabelBackdrop: false,
                        z: 1
                    },
                    suggestedMin: 0,
                    suggestedMax: 1.5
                }
            }
        }
    });

    // Expose to window for theme switcher
    window.radarChart = radarChart;
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
    fetch('/api/rates/json')
        .then(response => response.json())
        .then(rates => {
            const cny = rates['CNY'] || 7.25;
            const tbody = document.getElementById('matrix-body');
            if (!tbody) return;
            
            tbody.innerHTML = '';
            
            // Use SUPPORTED_CURRENCIES if available, otherwise fallback
            const currencies = (typeof SUPPORTED_CURRENCIES !== 'undefined') ? SUPPORTED_CURRENCIES : ['USD', 'EUR', 'JPY', 'GBP'];
            
            currencies.forEach(curr => {
                if (curr === 'CNY') return; // Skip CNY/CNY
                
                // Calculate Rate: X/CNY = (USD/CNY) / (USD/X)
                // rates[curr] is USD/X
                let rateText = '-';
                if (rates[curr]) {
                    const val = cny / rates[curr];
                    rateText = val.toFixed(4);
                }
                
                const row = document.createElement('tr');
                row.innerHTML = `<td>${curr}/CNY</td><td>${rateText}</td>`;
                tbody.appendChild(row);
            });
        })
        .catch(err => console.error('Failed to load matrix rates:', err));
}
