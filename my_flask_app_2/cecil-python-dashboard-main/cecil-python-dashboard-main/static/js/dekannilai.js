// Perbandingan IPK
document.addEventListener('DOMContentLoaded', () => {
    const ctxBarPeriode = document.getElementById('ipkbandingBarChart').getContext('2d');

    const ipkBarChart = new Chart(ctxBarPeriode, {
        type: 'bar',
        data: {
            labels: ['S1 Sistem Informasi', 'S1 Informatika', 'D3 Sistem Informasi', 'S1 Sains Data'],
            datasets: [
                { 
                    label: 'IPK Tertinggi', 
                    data: [], 
                    backgroundColor: '#3300FF',
                    borderColor: '#3300FF',
                    borderWidth: 1
                },
                { 
                    label: 'IPK Terendah', 
                    data: [], 
                    backgroundColor: '#C80B70',
                    borderColor: '#C80B70',
                    borderWidth: 1
                },
                { 
                    label: 'Rata-Rata IPK', 
                    data: [], 
                    backgroundColor: '#FF885B',
                    borderColor: '#FF885B',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { 
                    beginAtZero: true,
                    max: 4.0,
                    ticks: {
                        stepSize: 0.5
                    }
                }
            },
            plugins: {
                legend: { 
                    position: 'top',
                    labels: {
                        font: {
                            size: 12
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'Perbandingan IPK Mahasiswa',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.raw.toFixed(2);
                        }
                    }
                }
            }
        }
    });

    function updateIpkChart(angkatan = '') {
        const queryParam = angkatan ? `?angkatan=${angkatan}` : '';
        fetch(`/api/ipk-mahasiswa${queryParam}`)
            .then(res => res.json())
            .then(data => {
                const prodis = ['S1 Sistem Informasi', 'S1 Informatika', 'D3 Sistem Informasi', 'S1 Sains Data'];
                const tertinggi = [], terendah = [], rataRata = [];

                prodis.forEach(prodi => {
                    const nilai = data[prodi] || { tertinggi: 0, terendah: 0, rata_rata: 0 };
                    tertinggi.push(nilai.tertinggi);
                    terendah.push(nilai.terendah);
                    rataRata.push(nilai.rata_rata);
                });

                ipkBarChart.data.datasets[0].data = tertinggi;
                ipkBarChart.data.datasets[1].data = terendah;
                ipkBarChart.data.datasets[2].data = rataRata;
                
                // Update chart title based on selection
                const title = angkatan 
                    ? `Perbandingan IPK Mahasiswa Angkatan ${angkatan}` 
                    : 'Perbandingan IPK Mahasiswa Semua Angkatan';
                
                ipkBarChart.options.plugins.title.text = title;
                ipkBarChart.update();
            })
            .catch(err => {
                console.error("Error fetching IPK data:", err);
            });
    }

    // Load data for all angkatan when page first loads
    updateIpkChart();

    // Event listener dropdown
    const yearDropdown = document.getElementById('ipkYearDropdown');
    yearDropdown.addEventListener('change', function() {
        updateIpkChart(this.value);
    });
});

// Perbandingan Rata-Rata IPS Per Semester
document.addEventListener("DOMContentLoaded", function () {
    const dropdown = document.getElementById("angkatanDropdown");
    const chartCanvas = document.getElementById("ipsChart");
    let ipsChart = null;
    let allData = null;

    const colors = {
        "S1 Sistem Informasi": '#3778bf',
        "S1 Informatika": '#f47920',
        "D3 Sistem Informasi": '#7b61ff',
        "S1 Sains Data": '#22aa44'
    };

    function showError(message) {
        if (ipsChart) {
            ipsChart.destroy();
            ipsChart = null;
        }
        chartCanvas.getContext('2d').clearRect(0, 0, chartCanvas.width, chartCanvas.height);
        const existingError = document.getElementById("errorMessage");
        if (!existingError) {
            chartCanvas.insertAdjacentHTML('afterend', `
                <div id="errorMessage" style="text-align:center; color:red; margin-top: 20px;">
                    <h3>${message}</h3>
                    <p>Silakan coba angkatan lain atau hubungi administrator</p>
                </div>
            `);
        }
    }

    function clearError() {
        const errMsg = document.getElementById("errorMessage");
        if (errMsg) errMsg.remove();
    }

    function renderChartForAngkatan(angkatan) {
        clearError();

        if (!allData) {
            showError("Data belum dimuat.");
            return;
        }

        const filteredData = {};
        const allowedProdis = Object.keys(colors);

        allowedProdis.forEach(prodi => {
            if (!allData[prodi]) return;
            filteredData[prodi] = allData[prodi].filter(item => angkatan === "" || item.semester.startsWith(angkatan));
        });

        if (Object.values(filteredData).every(arr => arr.length === 0)) {
            showError(`Tidak ada data untuk angkatan ${angkatan}`);
            return;
        }

        const allSemesters = new Set();
        Object.values(filteredData).forEach(prodiData => {
            prodiData.forEach(item => allSemesters.add(item.semester));
        });

        const sortedSemesters = Array.from(allSemesters).sort((a, b) => {
            const [yearA, semA] = a.split('-S');
            const [yearB, semB] = b.split('-S');
            return parseInt(yearA) - parseInt(yearB) || parseInt(semA) - parseInt(semB);
        });

        const datasets = [];

        allowedProdis.forEach(prodi => {
            if (!filteredData[prodi]) return;
            const semesterMap = {};
            filteredData[prodi].forEach(item => semesterMap[item.semester] = item.rata_rata_ips);
            const dataPoints = sortedSemesters.map(sem => semesterMap[sem] ?? null);

            datasets.push({
                label: prodi,
                data: dataPoints,
                borderColor: colors[prodi],
                backgroundColor: colors[prodi],
                borderWidth: 2,
                tension: 0.3,
                fill: false,
                pointRadius: 4,
                pointHoverRadius: 6
            });
        });

        if (ipsChart) ipsChart.destroy();

        const ctx = chartCanvas.getContext('2d');
        ipsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: sortedSemesters,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        min: 0,
                        max: 4,
                        ticks: { stepSize: 0.5, callback: val => val.toFixed(1) },
                        title: { display: true, text: 'Rata-Rata IPS' }
                    },
                    x: {
                        title: { display: true, text: 'Semester' }
                    }
                },
                plugins: {
                    legend: { position: 'top', labels: { font: { size: 12 }, padding: 15, usePointStyle: true } },
                    title: { display: true, text: `Rata-Rata IPS per Semester - Angkatan ${angkatan || "Semua"}`, font: { size: 18, weight: 'bold' }, padding: { top: 10, bottom: 20 } },
                    tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y?.toFixed(2) ?? 'N/A'}` } }
                },
                interaction: { mode: 'nearest', intersect: false }
            }
        });
    }

    fetch('/api/ipk-rerata-per-semester?angkatan=all')
        .then(res => {
            if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
            return res.json();
        })
        .then(data => {
            allData = data;
            renderChartForAngkatan(dropdown.value);
        })
        .catch(err => {
            showError("Gagal memuat data: " + err.message);
        });

    dropdown.addEventListener("change", () => {
        renderChartForAngkatan(dropdown.value);
    });
});