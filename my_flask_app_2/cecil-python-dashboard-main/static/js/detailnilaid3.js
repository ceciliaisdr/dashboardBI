// IPK per Semester
document.addEventListener("DOMContentLoaded", function () {
    // Mengambil data IPK yang dikirimkan dalam format JSON dari Flask
    const ipkHistori = JSON.parse(document.getElementById('histori-data').textContent);

    // Persiapkan data untuk grafik IPK
    const ipkData = ipkHistori.map(item => item.ipk);
    const semesterLabels = ipkHistori.map(item => item.semester);

    // Membuat grafik IPK per Semester
    const ctxIPK = document.getElementById("ipkLineChart");
    if (ctxIPK) {
        new Chart(ctxIPK, {
            type: 'line',
            data: {
                labels: semesterLabels,  // Label semester
                datasets: [{
                    label: 'IPK Mahasiswa',
                    data: ipkData,  // Data IPK
                    borderColor: '#3B82F6',
                    backgroundColor: '#3B82F6',
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
                            stepSize: 1,  // Interval antara nilai
                            callback: function (value) { return `${value}`; }  // Format nilai sumbu Y
                        }
                    }
                }
            }
        });
    }

    // Persiapkan data untuk grafik IPS
    const ipsData = ipkHistori.map(item => item.ips);
    
    // Membuat grafik IPS per Semester
    const ctxIPS = document.getElementById("ipsLineChart");
    if (ctxIPS) {
        new Chart(ctxIPS, {
            type: 'line',
            data: {
                labels: semesterLabels,  // Label semester
                datasets: [{
                    label: 'IPS Mahasiswa',
                    data: ipsData,  // Data IPS
                    borderColor: '#557C56',
                    backgroundColor: '#557C56',
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
                            stepSize: 1,  // Interval antara nilai
                            callback: function (value) { return `${value}`; }  // Format nilai sumbu Y
                        }
                    }
                }
            }
        });
    }

    // Persiapkan data untuk grafik Nilai Mahasiswa
    const nilaiData = [42, 5, 2, 2, 0, 0, 0, 0, 0, 0]; // Data contoh
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


    // Anda dapat menambahkan grafik IPS dan lainnya dengan cara yang sama



// // IPK per Semester
// document.addEventListener("DOMContentLoaded", function () {
//     const ctx = document.getElementById("ipkLineChart");

//     if (ctx) { // Pastikan elemen ada sebelum membuat chart
//         new Chart(ctx, {
//             type: 'line',
//             data: {
//                 labels: ['Semester 1', 'Semester 2', 'Semester 3', 'Semester 4', 'Semester 5', 'Semester 6', 'Semester 7', 'Semester 8'],
//                 datasets: [{
//                     label: 'IPK Mahasiswa',
//                     data: [3.5, 3.6, 3.7, 3.65, 3.8, 3.85, 3.9, 0], // Ganti dengan data yang dinamis jika perlu
//                     borderColor: '#3B82F6',
//                     backgroundColor: '#3B82F6',
//                     fill: false
//                     // tension: 0.4
//                 }]
//             },
//             options: {
//                 responsive: true,
//                 maintainAspectRatio: false,
//                 scales: {
//                     x: {
//                         grid: {
//                         display: false
//                         }
//                     },

//                     y: {
//                         beginAtZero: true,
//                         // suggestedMax: 4.0,
//                         ticks: {
//                             // maxTicksLimit: 7,
//                             stepSize: 4,
//                             callback: function (value) {
//                                 return `${value}`; },
//                             }
//                     }
//                 }
//             }
//         });
//     } else {
//         console.error("Canvas dengan ID 'ipkLineChart' tidak ditemukan.");
//     }
// });

// // IPS per Semester
// document.addEventListener("DOMContentLoaded", function () {
//     const ctx = document.getElementById("ipsLineChart");

//     if (ctx) { // Pastikan elemen ada sebelum membuat chart
//         new Chart(ctx, {
//             type: 'line',
//             data: {
//                 labels: ['Semester 1', 'Semester 2', 'Semester 3', 'Semester 4', 'Semester 5', 'Semester 6', 'Semester 7', 'Semester 8'],
//                 datasets: [{
//                     label: 'IPK Mahasiswa',
//                     data: [3.70, 3.5, 3.93, 3.88, 3.80, 3.89, 3.91, 0], // Ganti dengan data yang dinamis jika perlu
//                     borderColor: '#557C56',
//                     backgroundColor: '#557C56',
//                     fill: false
//                     // tension: 0.4
//                 }]
//             },
//             options: {
//                 responsive: true,
//                 maintainAspectRatio: false,
//                 scales: {
//                     x: {
//                         grid: {
//                         display: false
//                         }
//                     },

//                     y: {
//                         beginAtZero: true,
//                         // suggestedMax: 4.0,
//                         ticks: {
//                             // maxTicksLimit: 7,
//                             stepSize: 4,
//                             callback: function (value) {
//                                 return `${value}`; },
//                             }
//                     }
//                 }
//             }
//         });
//     } else {
//         console.error("Canvas dengan ID 'ipkLineChart' tidak ditemukan.");
//     }
// });

// const ctxBar = document.getElementById('nilaiBarChart').getContext('2d');
// new Chart(ctxBar, {
//     type: 'bar',
//     data: {
//         labels: ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'E'],
//         datasets: [{
//             label: 'Tunggakan UKT',
//             data: [42, 5, 2, 2, 0, 0, 0, 0, 0, 0],
//             backgroundColor: ['#33372C', '#33372C', '#33372C', '#33372C', '#33372C', '#33372C', '#33372C', '#33372C', '#33372C', '#33372C']
//         }]
//     },
//     options: {
//         responsive: true,
//         maintainAspectRatio: false,
//         scales: {
//             y: {
//                 beginAtZero: true,
//                 suggestedMin: 10,
//                 suggestedMax: 50,
//                 ticks: {
//                     stepSize: 10,
//                     callback: function (value) {
//                         return `${value}`;
//                     }
//                 },
//                 grid: {
//                     display: false // **Menghilangkan grid di sumbu Y**
//                 }
//             },
//             x: {
//                 grid: {
//                     display: false // **Menghilangkan grid di sumbu X**
//                 }
//             }
//         },
//         plugins: {
//             legend: {
//                 display: false
//             }
//         }
//     }
// });
