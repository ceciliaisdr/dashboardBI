// Line Chart prediksi (Mahasiswa Aktif vs Non-Aktif)
const ctxLine = document.getElementById('uktLineChart').getContext('2d');
const chart = new Chart(ctxLine, {
    type: 'line',
    data: {
        labels: ['2020/2021', '2021/2022', '2022/2023', '2023/2024', '2024/2025'],
        datasets: [
            {
                label: 'Mahasiswa Aktif',
                data: [400, 450, 500, 480, 300],
                borderColor: '#4e1246',
                backgroundColor: '#4e1246', // Warna latar belakang area (opsional)
                fill: false // Area di bawah garis terisi
            },
            {
                label: 'Mahasiswa Non Aktif',
                data: [200, 250, 300, 350, 200],
                borderColor: '#6f5ece',
                backgroundColor: '#6f5ece', // Warna latar belakang area (opsional)
                fill: false // Area di bawah garis terisi
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false, // Membolehkan grafik memanfaatkan ruang penuh
        scales: {
            y: {
                beginAtZero: true, // Dimulai dari nol
                ticks: {
                    maxTicksLimit: 6,
                    stepSize: 20,
                    callback: function(value) {
                        return value;
                    }
                }
            }
        },
        plugins: {
            legend: {
                position: 'right' // Posisi legenda di samping
            }
        }
    }
});

// Fungsi untuk memperbarui chart dengan prediksi
async function updateChartWithPrediction() {
    try {
        const response = await fetch('/predict_next'); // Memanggil Flask endpoint
        const data = await response.json(); // Menerima JSON dari Flask

        if (data.error) {
            console.error('Error:', data.error);
            alert(`Error saat memuat data prediksi: ${data.error}`);
            return;
        }

        const nextYear = data.next_year;
        const predAktif = data.aktif;
        const predNonaktif = data.nonaktif;

        // Log untuk debugging
        console.log(`Data prediksi diterima: Tahun ${nextYear}, Aktif ${predAktif}, Nonaktif ${predNonaktif}`);

        // Update data chart
        chart.data.labels.push(nextYear); // Tambahkan label tahun baru
        chart.data.datasets[0].data.push(predAktif); // Tambahkan data Mahasiswa Aktif
        chart.data.datasets[1].data.push(predNonaktif); // Tambahkan data Mahasiswa Non Aktif

        chart.update(); // Render ulang chart
    } catch (error) {
        console.error('Error fetching prediction data:', error);
        alert('Gagal memuat data prediksi. Coba lagi nanti.');
    }
}

// Panggil fungsi saat halaman dimuat
document.addEventListener('DOMContentLoaded', updateChartWithPrediction);

// KIPK
document.addEventListener('DOMContentLoaded', () => {
    // Data untuk diagram line
    const labels = ["2020/2021", "2021/2022", "2022/2023", "2023/2024", "2024/2025"];
    const data = {
        labels: labels,
        datasets: [
            {
                label: "Banyak Mahasiswa per Periode",
                data: [50, 60, 70, 65, 80, 90],
                borderColor: "#557C56",
                backgroundColor: "#557c56",
                tension: 0.4,
                fill: false,
            },
        ],
    };

    // Konfigurasi untuk diagram line
    const config = {
        type: "line",
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "top",
                },
                title: {
                    display: true,
                },
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Periode",
                    },
                },
                y: {
                    title: {
                        display: true,
                        text: "Jumlah Mahasiswa",
                    },
                    beginAtZero: true,
                    ticks: {
                        maxTicksLimit: 5, // Maksimal 5 garis horizontal pada sumbu Y
                        stepSize: 5,    // Interval antar garis (opsional)
                        callback: function(value) {
                            return `${value}`; // Menambahkan satuan label (opsional)
                        }
                    },
                },
            },
        },
    };

    // Render diagram line ke canvas
    const uktKIPKLineChart = document.getElementById("uktKIPKLineChart");
    if (uktKIPKLineChart) {
        new Chart(uktKIPKLineChart, config);
    }
});