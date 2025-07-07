document.addEventListener("DOMContentLoaded", function () {
    const ctxBar = document.getElementById("nilaiBarChart").getContext("2d");

    // Data awal (default)
    let chartDataBar = {
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

    let nilaiBarChart = new Chart(ctxBar, {
        type: "bar",
        data: chartDataBar,
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
    document.getElementById("angkatanDropdown").addEventListener("change", updateChart);
    document.getElementById("semesterDropdown").addEventListener("change", updateChart);

    function updateChart() {
        let selectedMataKuliah = document.getElementById("mataKuliahDropdown").value;
        let selectedPeriode = document.getElementById("periodeDropdown").value;
        let selectedAngkatan = document.getElementById("angkatanDropdown").value;
        let selectedSemester = document.getElementById("semesterDropdown").value;

        let newData = generateData(selectedMataKuliah, selectedPeriode, selectedAngkatan, selectedSemester);

        // Update data di setiap dataset untuk Bar Chart
        nilaiBarChart.data.datasets.forEach((dataset, index) => {
            dataset.data = newData.barData[index];
        });

        // Update data untuk Pie Chart berdasarkan perolehan nilai
        let totalData = newData.barData.reduce((acc, curr) => acc + curr.reduce((a, b) => a + b), 0);
        let pieData = newData.barData.map(dataset => {
            return dataset.reduce((a, b) => a + b, 0);
        });

        // Update Pie Chart data
        nilaiPieChart.data.datasets[0].data = pieData;
        nilaiPieChart.update();

        nilaiBarChart.update();
    }

    // function generateData(mataKuliah, periode, angkatan, semester) {
    //     // Data per mata kuliah, periode, angkatan dan semester
    //     const dataSet = {
    //         "sisdat": {
    //             "2024": {
    //                 "all": {
    //                     "ganjil": {
    //                         "barData": [[40, 30, 25, 35], [8, 12, 18, 10], [2, 5, 6, 12], [1, 1, 3, 2]],
    //                         "pieData": [40, 30, 25, 35]
    //                     },
    //                     "genap": {
    //                         "barData": [[35, 25, 20, 25], [5, 10, 15, 5], [0, 5, 3, 10], [0, 0, 2, 0]],
    //                         "pieData": [35, 25, 20, 25]
    //                     }
    //                 },
    //                 "2020": {
    //                     "ganjil": {
    //                         "barData": [[32, 22, 18, 20], [6, 9, 13, 7], [1, 4, 5, 8], [1, 2, 4, 1]],
    //                         "pieData": [32, 22, 18, 20]
    //                     },
    //                     "genap": {
    //                         "barData": [[30, 20, 16, 18], [7, 10, 12, 6], [2, 4, 5, 7], [1, 2, 3, 1]],
    //                         "pieData": [30, 20, 16, 18]
    //                     }
    //                 }
    //             }
    //         },
    //         "pbo": {
    //             // Similar structure for other mata kuliah
    //         },
    //         "rpl": {
    //             // Similar structure for other mata kuliah
    //         }
    //     };

    //     return dataSet[mataKuliah][periode][angkatan][semester];
    // }
});
