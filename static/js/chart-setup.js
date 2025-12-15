// Chart.js 图表初始化与配置脚本

let historyChart = null; // 历史趋势图实例
let radarChart = null;   // 波动雷达图实例

// 当页面加载完成后执行初始化
document.addEventListener('DOMContentLoaded', function() {
    initHistoryChart(); // 初始化折线图
    initRadarChart();   // 初始化雷达图
    updateMatrix();     // 初始化汇率矩阵
});

/**
 * 初始化历史趋势折线图
 */
function initHistoryChart() {
    const ctx = document.getElementById('historyChart').getContext('2d');
    
    // 获取当前主题的颜色变量 (从 CSS 变量中读取)
    const style = getComputedStyle(document.body);
    const primaryColor = style.getPropertyValue('--primary-color').trim() || '#4361ee';
    const primaryRgb = style.getPropertyValue('--primary-rgb').trim() || '67, 97, 238';

    historyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // X轴标签（日期）
            datasets: [{
                label: (typeof TRANS !== 'undefined') ? TRANS.exchange_rate : 'Exchange Rate',
                data: [], // Y轴数据（汇率）
                borderColor: primaryColor, // 线条颜色跟随主题
                backgroundColor: `rgba(${primaryRgb}, 0.1)`, // 填充颜色跟随主题
                tension: 0.3, // 曲线平滑度
                fill: true // 填充曲线下方区域
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false } // 隐藏图例
            },
            scales: {
                x: { grid: { display: false } }, // 隐藏X轴网格
                y: { grid: { color: '#f0f0f0' } } // Y轴网格颜色
            }
        }
    });
    
    // 将图表实例暴露给全局 window 对象，以便主题切换时可以访问并更新颜色
    window.rateChart = historyChart;

    // 加载初始数据
    updateChart();
}

/**
 * 初始化波动率雷达图
 */
function initRadarChart() {
    const ctx = document.getElementById('radarChart').getContext('2d');
    
    // 获取当前主题颜色
    const style = getComputedStyle(document.body);
    const primaryColor = style.getPropertyValue('--primary-color').trim() || '#4361ee';
    const primaryRgb = style.getPropertyValue('--primary-rgb').trim() || '67, 97, 238';
    
    // 模拟的波动率数据
    radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['USD', 'EUR', 'JPY', 'GBP', 'AUD'], // 雷达图的五个维度
            datasets: [{
                label: (typeof TRANS !== 'undefined') ? TRANS.volatility_label : '7-Day Volatility (%)',
                data: [0.5, 0.8, 1.2, 0.6, 0.9], // 模拟数据
                fill: true,
                backgroundColor: `rgba(${primaryRgb}, 0.2)`,
                borderColor: primaryColor,
                borderWidth: 2,
                pointBackgroundColor: '#fff',
                pointBorderColor: primaryColor,
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6,
                tension: 0.3 // 平滑曲线
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    // 自定义提示框样式
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
                        circular: true // 使用圆形网格
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

    // 暴露给全局，供主题切换使用
    window.radarChart = radarChart;
}

/**
 * 更新历史趋势图表数据
 * 根据用户选择的基准货币和目标货币，从后端 API 获取数据
 */
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
            
            // 同时更新矩阵（如果需要）
            updateMatrix();
        });
}

/**
 * 更新人民币汇率矩阵
 * 计算主要货币对人民币的汇率
 */
function updateMatrix() {
    fetch('/api/rates/json')
        .then(response => response.json())
        .then(rates => {
            const cny = rates['CNY'] || 7.25;
            const tbody = document.getElementById('matrix-body');
            if (!tbody) return;
            
            tbody.innerHTML = '';
            
            // 使用全局定义的货币列表，如果没有则使用默认列表
            const currencies = (typeof SUPPORTED_CURRENCIES !== 'undefined') ? SUPPORTED_CURRENCIES : ['USD', 'EUR', 'JPY', 'GBP'];
            
            currencies.forEach(curr => {
                if (curr === 'CNY') return; // 跳过 CNY/CNY
                
                // 计算交叉汇率: X/CNY = (USD/CNY) / (USD/X)
                // rates[curr] 是 USD/X
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
