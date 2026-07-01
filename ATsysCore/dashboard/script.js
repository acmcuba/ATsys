// Cambia esta IP por la IP de tu Raspberry Pi
 const API_URL = "http://10.0.0.87:8000/system/overview";
// fetch("http://10.0.0.87:8000/system/overview")

// Gráficos
let cpuData = [];
let gpuData = [];

let cpuChart = new Chart(document.getElementById("cpuChart"), {
    type: "line",
    data: {
        labels: [],
        datasets: [{
            label: "CPU Temp °C",
            data: cpuData,
            borderColor: "rgb(0, 150, 255)",
            borderWidth: 2
        }]
    },
    options: { responsive: true }
});

let gpuChart = new Chart(document.getElementById("gpuChart"), {
    type: "line",
    data: {
        labels: [],
        datasets: [{
            label: "GPU Temp °C",
            data: gpuData,
            borderColor: "rgb(255, 80, 80)",
            borderWidth: 2
        }]
    },
    options: { responsive: true }
});


// Actualización de datos
async function updateDashboard() {
    try {
        const response = await fetch(API_URL);
        const data = await response.json();

        // Datos básicos
        document.getElementById("sys_status").textContent = data.system_status;
        document.getElementById("predict_status").textContent = data.predictive;
        document.getElementById("uptime").textContent = data.uptime_minutes;

        document.getElementById("cpu_temp").textContent = data.cpu.temperature.toFixed(1);
        document.getElementById("cpu_usage").textContent = data.cpu.usage_percent;
        document.getElementById("cpu_freq").textContent = data.cpu.freq_mhz.toFixed(0);

        document.getElementById("gpu_temp").textContent = data.gpu.temperature.toFixed(1);
        document.getElementById("gpu_usage").textContent = data.gpu.usage_percent;
        document.getElementById("gpu_mem").textContent =
            `${data.gpu.memory_used_mb} / ${data.gpu.memory_total_mb} MB`;

        // Actualizar gráficos
        let timeLabel = new Date().toLocaleTimeString();

        cpuChart.data.labels.push(timeLabel);
        cpuChart.data.datasets[0].data.push(data.cpu.temperature);
        gpuChart.data.labels.push(timeLabel);
        gpuChart.data.datasets[0].data.push(data.gpu.temperature);

        cpuChart.update();
        gpuChart.update();

        // Mantener max 30 puntos
        if (cpuChart.data.labels.length > 30) {
            cpuChart.data.labels.shift();
            cpuChart.data.datasets[0].data.shift();
            gpuChart.data.labels.shift();
            gpuChart.data.datasets[0].data.shift();
        }

    } catch (error) {
        console.error("Error conectando a la API:", error);
    }
}

// Actualizar cada 2 segundos
setInterval(updateDashboard, 2000);
updateDashboard();
