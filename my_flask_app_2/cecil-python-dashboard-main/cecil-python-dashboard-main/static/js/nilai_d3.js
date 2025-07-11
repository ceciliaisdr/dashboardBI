document.addEventListener("DOMContentLoaded", function () {
    const ctx = document.getElementById("nilaiBarChart").getContext("2d");

    // Data awal (default)
    let chartData = {
        labels: ["Kelas A", "Kelas B", "Kelas C", "Kelas D"],
        datasets: [
            { label: "A", data: [35, 25, 20, 25], backgroundColor: "#4CAF50" },
            { label: "A-", data: [5, 10, 15, 5], backgroundColor: "#8BC34A" },
            { label: "B+", data: [0, 5, 3, 10], backgroundColor: "#FFC107" },
            { label: "B", data: [0, 0, 2, 0], backgroundColor: "#FF9800" },
            { label: "B-", data: [0, 0, 0, 0], backgroundColor: "#FF5722" },
            { label: "C+", data: [0, 0, 0, 0], backgroundColor: "#2196F3" },
            { label: "C", data: [0, 0, 0, 0], backgroundColor: "#3F51B5" },
            { label: "C-", data: [0, 0, 0, 0], backgroundColor: "#9C27B0" },
            { label: "D", data: [0, 0, 0, 0], backgroundColor: "#E91E63" },
            { label: "E", data: [0, 0, 0, 0], backgroundColor: "#795548" }
        ]
    };

    let nilaiBarChart = new Chart(ctx, {
        type: "bar",
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { stacked: false },
                y: { stacked: false }
            }
        }
    });

    // Event listener untuk dropdown
    document.getElementById("mataKuliahDropdown").addEventListener("change", updateChart);
    document.getElementById("periodeDropdown").addEventListener("change", updateChart);

    function updateChart() {
        let selectedMataKuliah = document.getElementById("mataKuliahDropdown").value;
        let selectedPeriode = document.getElementById("periodeDropdown").value;

        let newData = generateData(selectedMataKuliah, selectedPeriode);

        // Update data di setiap dataset
        nilaiBarChart.data.datasets.forEach((dataset, index) => {
            dataset.data = newData[index];
        });

        nilaiBarChart.update();
    }

    function generateData(mataKuliah, periode) {
        // Data per mata kuliah dan periode
        const dataSet = {
            "sisdat": {
                "2024": [[40, 30, 25, 35], [8, 12, 18, 10], [2, 5, 6, 12], [1, 1, 3, 2], [0, 0, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                "2023": [[35, 25, 20, 25], [5, 10, 15, 5], [0, 5, 3, 10], [0, 0, 2, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                "2022": [[30, 22, 18, 20], [8, 12, 10, 8], [2, 5, 5, 10], [0, 3, 4, 0], [0, 0, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                "2021": [[28, 20, 16, 18], [10, 15, 12, 10], [3, 4, 6, 9], [2, 1, 2, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                "2020": [[32, 22, 18, 20], [6, 9, 13, 7], [1, 4, 5, 8], [1, 2, 4, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
            },
            "pbo": {
                "2024": [[38, 28, 22, 30], [9, 14, 16, 8], [3, 6, 7, 10], [2, 1, 2, 3], [0, 0, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                "2023": [[33, 23, 18, 22], [6, 9, 13, 7], [2, 6, 4, 9], [0, 1, 3, 2], [0, 0, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                "2022": [[29, 20, 17, 19], [7, 10, 12, 6], [1, 5, 4, 7], [0, 2, 3, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                "2021": [[26, 18, 15, 16], [8, 12, 10, 5], [3, 4, 5, 6], [2, 1, 2, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                "2020": [[30, 20, 15, 18], [7, 12, 10, 5], [2, 4, 5, 7], [1, 2, 3, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
            },
            "rpl": {
                "2024": [[39, 27, 24, 32], [10, 12, 15, 9], [3, 5, 6, 8], [1, 1, 3, 2], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                "2023": [[32, 22, 17, 21], [7, 10, 14, 6], [1, 5, 3, 8], [0, 2, 3, 1], [0, 0, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                "2022": [[28, 19, 16, 18], [9, 11, 11, 7], [2, 4, 5, 6], [1, 1, 2, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                "2021": [[27, 18, 14, 15], [10, 13, 9, 8], [3, 3, 4, 5], [2, 1, 1, 2], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                "2020": [[28, 19, 16, 18], [9, 11, 11, 7], [2, 4, 5, 6], [1, 1, 2, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
            }
        };
        return dataSet[mataKuliah][periode];
    }
});
