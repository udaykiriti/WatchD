// Chart Configuration
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        y: {
            beginAtZero: true,
            max: 100,
            grid: {
                color: '#333333',
                drawBorder: true
            },
            ticks: {
                color: '#999999',
                font: { family: "'Courier New', monospace", size: 10 }
            }
        },
        x: {
            grid: { display: false },
            ticks: { 
                color: '#999999',
                font: { family: "'Courier New', monospace" }
            }
        }
    },
    plugins: {
        legend: { display: false }
    },
    animation: { duration: 0 }
};

const ctxCpu = document.getElementById('cpuChart').getContext('2d');
const ctxMem = document.getElementById('memChart').getContext('2d');

const cpuChart = new Chart(ctxCpu, {
    type: 'line',
    data: {
        labels: Array(30).fill(''),
        datasets: [{
            label: 'CPU %',
            data: Array(30).fill(0),
            borderColor: '#00ff00',
            backgroundColor: 'rgba(0, 255, 0, 0.1)',
            borderWidth: 2,
            tension: 0.3,
            pointRadius: 0,
            fill: true
        }]
    },
    options: chartOptions
});

const memChart = new Chart(ctxMem, {
    type: 'line',
    data: {
        labels: Array(30).fill(''),
        datasets: [{
            label: 'Memory %',
            data: Array(30).fill(0),
            borderColor: '#ffaa00',
            backgroundColor: 'rgba(255, 170, 0, 0.1)',
            borderWidth: 2,
            tension: 0.3,
            pointRadius: 0,
            fill: true
        }]
    },
    options: chartOptions
});

function updateChart(chart, value) {
    const data = chart.data.datasets[0].data;
    data.shift();
    data.push(Math.min(100, Math.max(0, value)));
    chart.update();
}

function getValueColor(percent) {
    if (percent > 90) return 'danger';
    if (percent > 75) return 'warning';
    return '';
}

function updateTimestamp() {
    const now = new Date();
    document.getElementById('timestamp').textContent = now.toLocaleTimeString();
    document.getElementById('footer-time').textContent = now.toLocaleString();
}

function connect() {
    const ws = new WebSocket(`ws://${location.host}/ws`);
    const statusEl = document.getElementById('status-text');
    const statusDot = document.getElementById('connection-status');

    ws.onopen = () => {
        statusEl.textContent = '● Connected';
        statusDot.classList.add('connected');
        console.log('[SysGuard] WebSocket connected');
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);

            // CPU
            const cpuVal = Math.round(data.cpu.usage_percent * 10) / 10;
            const cpuEl = document.getElementById('cpu-val');
            cpuEl.textContent = cpuVal + '%';
            cpuEl.className = 'metric-value ' + getValueColor(cpuVal);

            // Memory
            const memVal = Math.round(data.memory.percent * 10) / 10;
            const memEl = document.getElementById('mem-val');
            memEl.textContent = memVal + '%';
            memEl.className = 'metric-value ' + getValueColor(memVal);

            // Disk
            const diskVal = Math.round(data.disk.percent * 10) / 10;
            const diskEl = document.getElementById('disk-val');
            diskEl.textContent = diskVal + '%';
            diskEl.className = 'metric-value ' + getValueColor(diskVal);

            // Disk Bar
            const diskBar = document.getElementById('disk-bar');
            diskBar.style.width = diskVal + '%';
            diskBar.className = 'progress-fill ' + getValueColor(diskVal);

            // Disk Text
            document.getElementById('disk-usage-text').textContent = 
                `${data.disk.used_gb} GB / ${data.disk.total_gb} GB`;

            // Update Charts
            updateChart(cpuChart, cpuVal);
            updateChart(memChart, memVal);

        } catch (e) {
            console.error('[SysGuard] Error parsing message:', e);
        }
    };

    ws.onclose = () => {
        statusEl.textContent = '● Reconnecting...';
        statusDot.classList.remove('connected');
        console.log('[SysGuard] WebSocket disconnected');
        setTimeout(connect, 3000);
    };

    ws.onerror = (error) => {
        console.error('[SysGuard] WebSocket error:', error);
    };
}

// Initialize
updateTimestamp();
setInterval(updateTimestamp, 1000);
connect();
