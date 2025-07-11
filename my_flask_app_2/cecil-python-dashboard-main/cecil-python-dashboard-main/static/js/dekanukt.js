//Pie perbandingan sudah bayar dan belum
const ctxPie = document.getElementById('uktPieChart').getContext('2d');
const uktPieChart = new Chart(ctxPie, {
    type: 'pie',
    data: {
        labels: ['Sudah Bayar', 'Belum Bayar'],
        datasets: [{
            data: [65, 35],
            backgroundColor: ['#3D3BF3', '#FF2929']
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                position: 'right'
            },
            datalabels: {
                formatter: (value, context) => {
                    const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                    const percentage = ((value / total) * 100).toFixed(1);
                    return `${percentage}%`;
                },
                color: '#fff',
                font: {
                    size: 14,
                    weight: 'bold'
                },
                align: 'center',
                anchor: 'center'
            }
        },
        onClick: (evt, elements) => {
            if (elements.length > 0) {
                const chart = elements[0];
                const label = uktPieChart.data.labels[chart.index];
                if (label === 'Belum Bayar') {
                    // Arahkan ke halaman mahasiswa yang BELUM membayar (mungkin label sebenarnya terbalik)
                    window.location.href = "/detail-belum-bayar";
                }
            }
        }
    },
    plugins: [ChartDataLabels]
});


// Bar Chart (Tunggakan UKT per Angkatan)
let uktBarChartInstance;

async function renderTunggakanPerAngkatan(prodi = "all") {
  try {
    const response = await fetch(`/api/tunggakan-ukt-angkatan?prodi=${encodeURIComponent(prodi)}`);
    const result = await response.json();

    const total = result.data.reduce((accumulator, currentValue) => accumulator + currentValue, 0);

    const ctx = document.getElementById("uktBarChart").getContext("2d");

    // Hapus chart lama jika ada
    if (uktBarChartInstance) uktBarChartInstance.destroy();

    uktBarChartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: result.labels,
        datasets: [{
          label: "Jumlah Mahasiswa Menunggak UKT",
          data: result.data,
          backgroundColor: "#CD5656",
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: "Jumlah Mahasiswa"
            }
          },
          x: {
            title: {
              display: true,
              text: "Angkatan"
            }
          }
        },
        plugins: {
          legend: { display: true },
          tooltip: {
            callbacks: {
              label: function(context) {
                let num = Intl.NumberFormat().format((context.raw/total)*100, 0, ',', '.');
                return num + '%';
              }
            }
          }
        }
      }
    });
  } catch (error) {
    console.error("Gagal memuat data tunggakan:", error);
  }
}

// Listener dropdown
document.getElementById("prodiSelect").addEventListener("change", function () {
  renderTunggakanPerAngkatan(this.value);
});

// Load awal
document.addEventListener("DOMContentLoaded", () => {
  renderTunggakanPerAngkatan(); // default semua prodi
});


// Line Chart (Mahasiswa Aktif vs Non-Aktif)
let uktLineChartInstance;

async function renderLineChartPerStatus(prodi = "all") {
  try {
    const response = await fetch(`/api/perbandingan-tunggakan-status?prodi=${encodeURIComponent(prodi)}`);
    const result = await response.json();

    const ctx = document.getElementById("uktLineChart").getContext("2d");

    if (uktLineChartInstance) {
      uktLineChartInstance.destroy();
    }

    uktLineChartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels: result.labels,
        datasets: result.datasets.map((ds, i) => ({
          label: ds.label,
          data: ds.data,
          borderWidth: 2,
          borderColor: ['#4CAF50', '#F44336', '#2196F3', '#9C27B0', '#FF9800', '#795548'][i % 6],
          fill: false
        }))
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "top" },
          title: {
            display: true,
            text: "Perbandingan Tunggakan UKT per Status Mahasiswa"
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: "Angkatan"
            }
          },
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: "Total Tunggakan (Juta Rupiah)"
            }
          }
        }
      }
    });
  } catch (err) {
    console.error("Gagal memuat chart status:", err);
  }
}

// Listener dropdown filter prodi
document.getElementById("Selectprodi").addEventListener("change", function () {
  renderLineChartPerStatus(this.value);
});

// Load awal
document.addEventListener("DOMContentLoaded", () => {
  renderLineChartPerStatus(); // default semua prodi
});

// <-- diagram tunggakan -->
// Mendapatkan elemen judul diagram
const diagramTitle = document.querySelector('.diagram1-card h2');

// Mendapatkan tanggal sistem
const currentDate = new Date();
const formattedDate = currentDate.toLocaleDateString('id-ID', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
});

// Memperbarui teks judul diagram dengan tanggal sistem
diagramTitle.textContent = `Total Mahasiswa yang Menunggak UKT (${formattedDate})`;

// /* Data untuk diagram batang total penerimaan ukt */
// const barData = {
//     labels: ['Ganjil', 'Genap'],
//     datasets: [{
//       label: 'Total Penerimaan UKT',
//       data: [900, 950],
//       backgroundColor: ['#4CAF50', '#FF9800'],
//       borderWidth: 1
//     }]
//   };
  
//   // Konfigurasi diagram batang
//   const barConfig = {
//     type: 'bar',
//     data: barData,
//     options: {
//       responsive: true,
//       plugins: {
//         legend: { display: false },
//       },
//       scales: {
//         y: { beginAtZero: true }
//       }
//     }
//   };
  
//   // Render diagram batang
//   const barCtx = document.getElementById('barChart').getContext('2d');
//   new Chart(barCtx, barConfig);
  
// Golongan ukt
let pieChartInstance;

async function fetchAndRenderPieChart() {
  const angkatan = document.getElementById("uktYearSelect").value;

  try {
    const response = await fetch(`/api/ukt-distribusi${angkatan ? `?angkatan=${angkatan}` : ''}`);
    const result = await response.json();
    const data = result.distribusi;
    const total = result.total;

    const labels = Object.keys(data).map(k => `Kelompok ${k}`);
    const values = Object.values(data);

    const chartData = {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: ['#FF5722', '#F44336', '#9C27B0', '#3F51B5', '#4CAF50', '#8BC34A', '#FFC107', '#03A9F4']
      }]
    };

    const config = {
  type: 'pie',
  data: chartData,
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'right' },
      tooltip: {
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            const value = context.parsed;
            const percentage = ((value / total) * 100).toFixed(2);
            return `${label}: ${value} mahasiswa (${percentage}%)`;
          }
        }
      },
      datalabels: {
        color: '#fff',
          formatter: (value, context) => {
          if (value === 0) return ''; // ⛔ Jangan tampilkan jika data 0
          const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
          const percentage = ((value / total) * 100).toFixed(1);
          return `${percentage}%`;
        },
        font: {
          weight: 'bold',
          size: 14
        }
      }
    }
  },
  plugins: [ChartDataLabels]
};

    if (pieChartInstance) pieChartInstance.destroy();
    const ctx = document.getElementById('pieChart').getContext('2d');
    pieChartInstance = new Chart(ctx, config);
  } catch (err) {
    console.error("Gagal fetch data distribusi UKT:", err);
  }
}

document.addEventListener("DOMContentLoaded", fetchAndRenderPieChart);
document.getElementById("uktYearSelect").addEventListener("change", fetchAndRenderPieChart);

/* Banyak mahasiswa yang memperoleh KIPK dan KJMU */
document.addEventListener('DOMContentLoaded', () => {
    const labels = ["2020", "2021", "2022", "2023", "2024"];

    fetch("/api/beasiswa-data")
        .then(response => response.json())
        .then(result => {
            const kipkData = labels.map(label => {
                const period = `${label}/${parseInt(label) + 1}`;
                return result.KIPK[period] || 0;
            });

            const kjmuData = labels.map(label => {
                const period = `${label}/${parseInt(label) + 1}`;
                return result.KJMU[period] || 0;
            });

            const data = {
                labels: labels,
                datasets: [
                    {
                        label: "Penerima KIPK",
                        data: kipkData,
                        borderColor: "#4CAF50",
                        backgroundColor: "#4CAF50",
                        // tension: 0.4,
                        fill: false,
                    },
                    {
                        label: "Penerima KJMU",
                        data: kjmuData,
                        borderColor: "#3e95cd",
                        backgroundColor: "#3e95cd",
                        // tension: 0.4,
                        fill: false,
                    }
                ],
            };

            const config = {
                type: "line",
                data: data,
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: "top" },
                        title: {
                            display: true,
                            text: "Jumlah Penerima KIPK dan KJMU per Periode"
                        },
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: "Periode"
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: "Jumlah Mahasiswa"
                            },
                            beginAtZero: true,
                        },
                    },
                },
            };

            const chartCanvas = document.getElementById("uktKIPKLineChart");
            if (chartCanvas) {
                new Chart(chartCanvas, config);
            }
        })
        .catch(error => {
            console.error("Gagal memuat data beasiswa:", error);
        });
});

// Line Chart Perbandingan (Mahasiswa yang mengajukan cicilan, penurunan, dan pemotongan)
const uktBandingLabels = ["Cicilan UKT", "Penurunan UKT", "Pemotongan 50%"];
    const uktBandingData = {
        labels: uktBandingLabels,
        datasets: [
            {
                label: "S1 Sistem Informasi",
                data: [29, 43, 57],
                borderColor: "#3B82F6",
                backgroundColor: "#3B82F6",
                tension: 0.4,
                fill: false,
            },
            {
                label: "S1 Informatika",
                data: [20, 51, 30],
                borderColor: "#F97316",
                backgroundColor: "#F97316",
                tension: 0.4,
                fill: false,
            },
            {
                label: "D3 Sistem Informasi",
                data: [30, 15, 22],
                borderColor: "#8B5CF6",
                backgroundColor: "#8B5CF6",
                tension: 0.4,
                fill: false,
            },
            {
                label: "S1 Sains Data",
                data: [0, 30, 0],
                borderColor: "#22C55E",
                backgroundColor: "#22C55E",
                tension: 0.4,
                fill: false,
            },
        ],
    };

    const uktBandingConfig = {
        type: "line",
        data: uktBandingData,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "bottom",
                },
                title: {
                    display: true,
                },
            },
            scales: {
                x: {
                    title: {
                        display: true,
                    },
                },
                y: {
                    title: {
                        display: true,
                        text: "Jumlah Mahasiswa",
                    },
                    beginAtZero: true,
                    ticks: {
                        maxTicksLimit: 7,
                        stepSize: 5,
                        callback: function (value) {
                            return `${value}`;
                        },
                    },
                },
            },
        },
    };

    const uktBandingLineChart = document.getElementById("uktbandingLineChart");
    if (uktBandingLineChart) {
        new Chart(uktBandingLineChart, uktBandingConfig);
    }