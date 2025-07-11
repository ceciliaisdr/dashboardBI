document.addEventListener("DOMContentLoaded", function () {
    // Mengambil data histori mahasiswa yang dikirimkan dalam format JSON dari Flask
    const ipkHistori = JSON.parse(document.getElementById('histori-data').textContent);

    // Persiapkan data untuk grafik IPS
    const ipsData = ipkHistori.map(item => item.ips);  // Ambil data IPS dari histori
    const semesterLabels = ipkHistori.map(item => item.semester);  // Ambil label semester

    // Membuat grafik IPS per Semester
    const ctxIPS = document.getElementById("ipsLineChart");
    if (ctxIPS) {
        new Chart(ctxIPS, {
            type: 'line',
            data: {
                labels: semesterLabels,  // Label semester
                datasets: [{
                    label: 'IPS Mahasiswa',  // Label untuk grafik
                    data: ipsData,  // Data IPS
                    borderColor: '#557C56',  // Warna garis
                    backgroundColor: '#557C56',  // Warna background garis
                    fill: false  // Tidak ada pengisian warna di bawah garis
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { display: false }  // Menghilangkan grid pada sumbu X
                    },
                    y: {
                        beginAtZero: true,  // Mulai dari 0
                        ticks: {
                            stepSize: 1,  // Interval nilai sumbu Y
                            callback: function (value) { return `${value}`; }  // Format nilai sumbu Y
                        }
                    }
                }
            }
        });
    }

    // Persiapkan data untuk grafik Nilai Mahasiswa
    const nilaiData = [42, 5, 2, 2, 0, 0, 0, 0, 0, 0];  // Data contoh nilai (seperti yang diberikan sebelumnya)
    const nilaiLabels = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'E'];

    // Membuat grafik perolehan Nilai Mahasiswa
    const ctxBar = document.getElementById('nilaiBarChart').getContext('2d');
    if (ctxBar) {
        new Chart(ctxBar, {
            type: 'bar',
            data: {
                labels: nilaiLabels,  // Label nilai
                datasets: [{
                    label: 'Perolehan Nilai Mahasiswa',
                    data: nilaiData,  // Data Nilai
                    backgroundColor: ['#33372C', '#33372C', '#33372C', '#33372C', '#33372C', '#33372C', '#33372C', '#33372C', '#33372C', '#33372C']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,  // Mulai dari 0
                        suggestedMin: 10,
                        suggestedMax: 50,
                        ticks: {
                            stepSize: 10,  // Interval nilai sumbu Y
                            callback: function (value) { return `${value}`; }
                        },
                        grid: { display: false }  // Menghilangkan grid di sumbu Y
                    },
                    x: {
                        grid: { display: false }  // Menghilangkan grid di sumbu X
                    }
                },
                plugins: {
                    legend: {
                        display: false  // Menyembunyikan legenda
                    }
                }
            }
        });
    }
});
