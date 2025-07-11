// perbandingan mahasiswa aktif, non aktif, dan totalnya
document.addEventListener("DOMContentLoaded", function() {
    const yearDropdown = document.getElementById("yearDropdown");
    const ctx = document.getElementById("stackedBarChart").getContext("2d");
    let stackedBarChart;

    async function fetchStatusData(angkatan = null) {
        let url = '/api/status-mahasiswa';
        if (angkatan && angkatan !== "ALL") {
            url += `?angkatan=${encodeURIComponent(angkatan)}`;
        }
        const response = await fetch(url);
        return await response.json();
    }

    function renderChart(dataObj) {
    const key = Object.keys(dataObj)[0];
    const data = dataObj[key];

    const labels = Object.keys(data);
    const aktifData = labels.map(prodi => data[prodi].aktif);
    const nonAktifData = labels.map(prodi => data[prodi].nonaktif);
    const totalData = labels.map(prodi => data[prodi].total);

    if (stackedBarChart) {
        stackedBarChart.destroy();
    }

    stackedBarChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Mahasiswa Aktif',
                    data: aktifData,
                    backgroundColor: 'blue',
                    stack: 'stack1',
                    datalabels: {
                        anchor: 'center',
                        align: 'center',
                        color: 'white',
                        formatter: (value, ctx) => {
                            const total = totalData[ctx.dataIndex];
                            if (total === 0 || value === 0) return '';
                            return ((value / total) * 100).toFixed(1) + '%';
                        }
                    }
                },
                {
                    label: 'Mahasiswa Non-Aktif',
                    data: nonAktifData,
                    backgroundColor: '#FF2929',
                    stack: 'stack1',
                    datalabels: {
                        anchor: 'center',
                        align: 'center',
                        color: 'white',
                        formatter: (value, ctx) => {
                            const total = totalData[ctx.dataIndex];
                            if (total === 0 || value === 0) return '';
                            return ((value / total) * 100).toFixed(1) + '%';
                        }
                    }
                }
            ]
        },
        options: {
            responsive: true,
            onClick: (e, elements) => {
            if (elements.length > 0) {
                const element = elements[0];
                const datasetIndex = element.datasetIndex;
                const datasetLabel = stackedBarChart.data.datasets[datasetIndex].label;

                let statusParam = '';
                if (datasetLabel.toUpperCase().includes('AKTIF')) {
                    statusParam = datasetLabel.toUpperCase().includes('NON') ? 'NON-AKTIF' : 'AKTIF';
                    window.location.href = `/detailaktifnon?status=${encodeURIComponent(statusParam)}`;
                }
            }
        },
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                callbacks: {
                    label: function (context) {
                        const value = context.parsed.y;
                        const label = `${context.dataset.label}: ${value} orang`;

                        const totalAktif = context.chart.data.datasets[0].data[context.dataIndex];
                        const totalNonAktif = context.chart.data.datasets[1].data[context.dataIndex];
                        const total = totalAktif + totalNonAktif;

                        return [
                            label,
                            `Total Mahasiswa: ${total} orang`
                        ];
                    }
                }
            },
                datalabels: {
                    display: true
                }
            },
            scales: {
                x: { stacked: true },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: "Jumlah Mahasiswa"
                    }
                }
            }
        },
        plugins: [ChartDataLabels]
    });
}

    function handleDropdownChange() {
        const selectedYear = yearDropdown.value;
        fetchStatusData(selectedYear).then(data => renderChart(data));
    }

    yearDropdown.addEventListener("change", handleDropdownChange);

    // Load awal semua angkatan
    fetchStatusData().then(data => renderChart(data));
});

// Perbandingan mahasiswa aktif, non aktif, dan cuti
const ctxBar = document.getElementById('statBarChart').getContext('2d');
let barChart;

// Fungsi untuk membuat konfigurasi label persentase
function getLabelOpts(data, total, color, anchor) {
    return {
        clip: false,
        anchor: anchor,
        align: 'end',
        color: "#000000",
        font: {
            weight: 'bold'
        },
        formatter: (value, ctx) => {
            const i = ctx.dataIndex;
            return total[i] ? ((value / total[i]) * 100).toFixed(1) + '%' : '';
        }
    };
}

// Fungsi utama untuk memuat data dan render chart
async function loadStatusMahasiswa(angkatan = null) {
    try {
        let url = '/api/status-mahasiswa2';
        if (angkatan) {
            url += `?angkatan=${angkatan}`;
        }

        const response = await fetch(url);
        const data = await response.json();
        const dataset = angkatan ? data[angkatan] : data.ALL;

        const prodiNames = ['S1 Sistem Informasi', 'S1 Informatika', 'D3 Sistem Informasi', 'S1 Sains Data'];

        const aktif = prodiNames.map(prodi => dataset[prodi]?.aktif || 0);
        const nonaktif = prodiNames.map(prodi => dataset[prodi]?.nonaktif || 0);
        const cuti = prodiNames.map(prodi => dataset[prodi]?.cuti || 0);
        const keluar = prodiNames.map(prodi => dataset[prodi]?.keluar || 0);
        const dropout = prodiNames.map(prodi => dataset[prodi]?.dropout || 0);
        const total = prodiNames.map((_, i) =>
            aktif[i] + nonaktif[i] + cuti[i] + keluar[i] + dropout[i]
        );

        if (barChart) barChart.destroy();

        barChart = new Chart(ctxBar, {
            type: 'bar',
            data: {
                labels: prodiNames,
                datasets: [
                    {
                        label: 'Mahasiswa Aktif',
                        data: aktif,
                        backgroundColor: '#3300FF',
                        datalabels: getLabelOpts(aktif, total, 'white', 'end')
                    },
                    {
                        label: 'Mahasiswa Non-Aktif',
                        data: nonaktif,
                        backgroundColor: '#FF2929',
                        datalabels: getLabelOpts(nonaktif, total, 'white', 'end')
                    },
                    {
                        label: 'Mahasiswa Cuti',
                        data: cuti,
                        backgroundColor: '#FF885B',
                        datalabels: getLabelOpts(cuti, total, 'white', 'end')
                    },
                    {
                        label: 'Mahasiswa Keluar',
                        data: keluar,
                        backgroundColor: '#999999',
                        datalabels: getLabelOpts(keluar, total, 'white', 'end')
                    },
                    {
                        label: 'Mahasiswa Drop Out',
                        data: dropout,
                        backgroundColor: '#000000',
                        datalabels: getLabelOpts(dropout, total, 'white', 'end')
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return `${context.dataset.label}: ${context.parsed.y}`;
                            }
                        }
                    },
                    datalabels: {
                        display: true
                    }
                },
                onClick: function (e, elements) {
                    if (elements.length > 0) {
                        const index = elements[0].datasetIndex;
                        const label = this.data.datasets[index].label;

                        if (label.includes("Aktif") || label.includes("Non-Aktif")) {
                            window.location.href = "/detailaktifnon";
                        } else if (label.includes("Cuti")) {
                            window.location.href = "/detailajuancuti";
                        } else if (label.includes("Keluar") || label.includes("Drop")) {
                            window.location.href = "/detaildokeluar";
                        }
                    }
                },
                scales: {
                    x: {
                        stacked: false,
                        grid: { display: false }
                    },
                    y: {
                        stacked: false,
                        beginAtZero: true,
                        ticks: {
                            stepSize: 100,
                            callback: function (value) {
                                return value.toLocaleString();
                            }
                        },
                        title: {
                            display: true,
                            text: 'Jumlah Mahasiswa'
                        },
                        max: (Math.ceil(Math.max(...total) / 100) * 100) + 100
                    }
                },
                barPercentage: 0.7,
                categoryPercentage: 0.8
            },
            plugins: [ChartDataLabels]
        });

    } catch (error) {
        console.error('Error loading status mahasiswa:', error);
    }
}

// Load pertama kali
loadStatusMahasiswa();

// Dropdown filter angkatan
document.getElementById('yearSelect').addEventListener('change', function () {
    const selectedAngkatan = this.value;
    loadStatusMahasiswa(selectedAngkatan || null);
});


// Line Chart Perbandingan Pengajuan Cuti (Per Prodi)
document.addEventListener("DOMContentLoaded", function () {
    // Ambil data mahasiswa yang mengajukan cuti tanpa filter angkatan
    fetchCutiData();

    // Fungsi untuk mengambil data mahasiswa cuti
    function fetchCutiData() {
        // Mengambil data dari API tanpa filter angkatan
        fetch('/api/status-mahasiswa3') // Memanggil endpoint tanpa parameter angkatan
            .then(response => response.json())
            .then(data => {
                console.log('Data yang diterima:', data);  // Periksa data yang diterima
                if (data && data.ALL) {
                    updateLineChart(data.ALL);  // Update grafik dengan data yang diterima
                } else {
                    alert('Data tidak ditemukan atau format salah.');
                }
            })
            .catch(error => {
                console.error("Error fetching data:", error);
            });
    }

    // Fungsi untuk memperbarui grafik garis dengan data yang baru
    function updateLineChart(data) {
        console.log('Data untuk chart:', data);  // Periksa data yang akan digunakan untuk chart

        let total = 0;

        Object.values(data).forEach(item => {
            Object.values(item).forEach(value => {
                total += value.cuti;
            })
        })

        console.log('total cuti:', total);
        // Menyiapkan struktur data untuk grafik
        const chartData = {
    labels: ['2020', '2021', '2022', '2023', '2024'],
    datasets: [
        {
            label: "S1 Sistem Informasi",
            data: [
                data['2020/2021']?.['S1 Sistem Informasi']?.cuti || 0,
                data['2021/2022']?.['S1 Sistem Informasi']?.cuti || 0,
                data['2022/2023']?.['S1 Sistem Informasi']?.cuti || 0,
                data['2023/2024']?.['S1 Sistem Informasi']?.cuti || 0,
                data['2024/2025']?.['S1 Sistem Informasi']?.cuti || 0
            ],
            borderColor: "#3B82F6",
            backgroundColor: "#3B82F6",
            tension: 0.1,
            fill: false,
        },
        {
            label: "S1 Informatika",
            data: [
                data['2020/2021']?.['S1 Informatika']?.cuti || 0,
                data['2021/2022']?.['S1 Informatika']?.cuti || 0,
                data['2022/2023']?.['S1 Informatika']?.cuti || 0,
                data['2023/2024']?.['S1 Informatika']?.cuti || 0,
                data['2024/2025']?.['S1 Informatika']?.cuti || 0
            ],
            borderColor: "#F97316",
            backgroundColor: "#F97316",
            tension: 0.1,
            fill: false,
        },
        {
            label: "D3 Sistem Informasi",
            data: [
                data['2020/2021']?.['D3 Sistem Informasi']?.cuti || 0,
                data['2021/2022']?.['D3 Sistem Informasi']?.cuti || 0,
                data['2022/2023']?.['D3 Sistem Informasi']?.cuti || 0,
                data['2023/2024']?.['D3 Sistem Informasi']?.cuti || 0,
                data['2024/2025']?.['D3 Sistem Informasi']?.cuti || 0
            ],
            borderColor: "#8B5CF6",
            backgroundColor: "#8B5CF6",
            tension: 0.1,
            fill: false,
        },
        {
            label: "S1 Sains Data",
            data: [
                data['2020/2021']?.['S1 Sains Data']?.cuti || 0,
                data['2021/2022']?.['S1 Sains Data']?.cuti || 0,
                data['2022/2023']?.['S1 Sains Data']?.cuti || 0,
                data['2023/2024']?.['S1 Sains Data']?.cuti || 0,
                data['2024/2025']?.['S1 Sains Data']?.cuti || 0
            ],
            borderColor: "#22C55E",
            backgroundColor: "#22C55E",
            tension: 0.1,
            fill: false,
        },
    ]
};


        const config = {
            type: "line",
            data: chartData,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: "bottom",
                    },
                    title: {
                        display: true,
                        text: 'Grafik Mahasiswa Mengajukan Cuti'
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                let num = Intl.NumberFormat().format((context.raw/total) * 100, 0, ',', '.');
                                return context.dataset.label + ': ' + num + '%';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Tahun Angkatan'
                        },
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Jumlah Mahasiswa Cuti'
                        },
                        beginAtZero: true,
                        ticks: {
                            maxTicksLimit: 5,
                            stepSize: 1,  // Atur langkah untuk sumbu Y
                        },
                    },
                },
            }
        };

        const statbandingLineChart = document.getElementById("statbandingLineChart");
        if (statbandingLineChart) {
            new Chart(statbandingLineChart, config);  // Membuat chart dengan konfigurasi
        }
    }
});


// Mahasiswa melebihi periode
document.addEventListener("DOMContentLoaded", function () {
    const ctx = document.getElementById("statBarChartPeriode").getContext("2d");
    let barChart;

    async function fetchLebihPeriodeData() {
        try {
            const response = await fetch("/api/lebih-periode");
            if (!response.ok) throw new Error("Gagal ambil data");
            const json = await response.json();
            console.log("Data diterima:", json); // Untuk debug
            return json;
        } catch (error) {
            console.error("Error fetch:", error);
            return null;
        }
    }

function renderChart(data) {
    if (!data) {
        console.error("Data tidak tersedia untuk chart.");
        return;
    }

    const labels = Object.keys(data); // daftar prodi
    const semesterSet = new Set();

    // Ambil semua semester unik dari API
    labels.forEach(label => {
        Object.keys(data[label]).forEach(sem => semesterSet.add(sem));
    });

    const semesters = Array.from(semesterSet).sort((a, b) => Number(a) - Number(b));

    const colors = [
        "#B21F3D", "#FF2929", "#6B021B", "#DA8C8C", "#FF8C00", "#FFD700", "#8A2BE2"
    ];

    const totalPerProdi = labels.map(label =>
        semesters.reduce((sum, s) => sum + (data[label][s] || 0), 0)
    );

    const datasets = semesters.map((semester, i) => {
        return {
            label: `Semester ${semester}`,
            data: labels.map((label) => data[label][semester] || 0),
            backgroundColor: colors[i % colors.length],
        };
    });

    if (barChart) {
        barChart.destroy();
    }

    barChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Mahasiswa Melebihi Masa Studi Normal'
                },
                legend: {
                    position: 'top'
                },
                datalabels: {
                    formatter: function (value, context) {
                        const prodiIndex = context.dataIndex;
                        const total = totalPerProdi[prodiIndex];
                        if (total === 0) return '';
                        const percentage = (value / total * 100).toFixed(1);
                        return `${percentage}%`;
                    },
                    color: '#fff',
                    anchor: 'center',
                    align: 'center'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        },
        plugins: [ChartDataLabels]
    });
}

    fetchLebihPeriodeData().then(renderChart);
});