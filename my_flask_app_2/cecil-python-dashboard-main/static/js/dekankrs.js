document.addEventListener("DOMContentLoaded", function () {
    const chartCanvas = document.getElementById("krsBarChart");
    const angkatanDropdown = document.getElementById("angkatanDropdown");
    let krsChart = null;
    let globalData = {};

    fetch("/api/status-mahasiswa4")
        .then((res) => res.json())
        .then((data) => {
            globalData = data;

            // Render chart awal
            if (globalData["ALL"]) {
                renderChart(globalData["ALL"]);
            }

            angkatanDropdown.addEventListener("change", function () {
                const selected = this.value;
                const dataToRender = globalData[selected];
                if (dataToRender) {
                    renderChart(dataToRender);
                } else {
                    console.warn("Data tidak ditemukan untuk angkatan:", selected);
                }
            });
        })
        .catch((err) => console.error("Gagal ambil data:", err));

    function renderChart(dataPerProdi) {
        const labels = Object.keys(dataPerProdi);
        const aktifData = [];
        const nonAktifData = [];
        const belumIsiData = [];

        labels.forEach((prodi) => {
            const stat = dataPerProdi[prodi];
            aktifData.push(stat.aktif || 0);
            nonAktifData.push(stat.nonaktif || 0);
            belumIsiData.push(stat.belum_isi_krs || 0);
        });

        if (krsChart) {
            krsChart.destroy();
        }

        krsChart = new Chart(chartCanvas, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Aktif",
                        data: aktifData,
                        backgroundColor: "#3D3BF3",
                    },
                    {
                        label: "Non-Aktif",
                        data: nonAktifData,
                        backgroundColor: "#FF2929",
                    },
                    {
                        label: "Aktif Tidak Isi KRS",
                        data: belumIsiData,
                        backgroundColor: "#FFC107",
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: { display: true, text: "Program Studi" },
                    },
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: "Jumlah Mahasiswa" },
                    },
                },
                plugins: {
                    legend: { position: "top" },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const dataset = context.dataset;
                                const currentValue = context.raw;
                                const dataIndex = context.dataIndex;

                                // Hitung total semua dataset di bar yang sama
                                const total = context.chart.data.datasets
                                    .map(ds => ds.data[dataIndex])
                                    .reduce((sum, val) => sum + val, 0);

                                const percentage = total > 0 ? ((currentValue / total) * 100).toFixed(1) : 0;

                                return `${dataset.label}: ${currentValue} (${percentage}%)`;
                            }
                        }
                    }
                },
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const clickedElement = elements[0];
                        const datasetIndex = clickedElement.datasetIndex;
                        const label = krsChart.data.datasets[datasetIndex].label;

                        if (label === "Aktif Tidak Isi KRS") {
                            window.location.href = "/dekanbelumisikrs";
                        }
                    }
                }
            },
        });
    }
});
