function getTop10(type) {
    let sorted = [...stockData];
    if (type === 'money') {
        sorted.sort((a, b) => b.money - a.money);
    } else {
        sorted.sort((a, b) => b.volume - a.volume);
    }
    return sorted.slice(0, 10);
}

function drawChart(type) {
    const top10 = getTop10(type);
    const labels = top10.map((s) => s.name);
    const data =
        type === 'money'
            ? top10.map((s) => s.money)
            : top10.map((s) => s.volume);
    barChart.data.labels = labels;
    barChart.data.datasets[0].data = data;
    barChart.data.datasets[0].label = type === 'money' ? '거래대금' : '거래량';
    barChart.options.plugins.title.text =
        type === 'money' ? '거래대금 TOP10' : '거래량 TOP10';
    barChart.update();
}

const ctx = document.getElementById('barChart').getContext('2d');
const barChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [
            {
                label: '거래대금',
                data: [],
                backgroundColor: [
                    '#36d1c4',
                    '#5b86e5',
                    '#f7b731',
                    '#eb3b5a',
                    '#20bf6b',
                    '#8854d0',
                    '#fd9644',
                    '#4b6584',
                    '#a5b1c2',
                    '#778ca3',
                ],
                borderRadius: 8,
            },
        ],
    },
    options: {
        responsive: true,
        plugins: {
            legend: { display: true },
            title: {
                display: true,
                text: '거래대금 TOP10',
                font: { size: 22 },
            },
            tooltip: { enabled: true },
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function (value) {
                        return value.toLocaleString();
                    },
                },
            },
        },
    },
});

// PIE CHART LOGIC
let pieChart = null;

function drawPieChart(type) {
    const top10 = getTop10(type);
    const labels = top10.map((s) => s.name);
    const data = type === 'money' ? top10.map((s) => s.money) : top10.map((s) => s.volume);
    const backgroundColors = [
        '#36d1c4', '#5b86e5', '#f7b731', '#eb3b5a', '#20bf6b',
        '#8854d0', '#fd9644', '#4b6584', '#a5b1c2', '#778ca3',
    ];
    if (pieChart) {
        pieChart.data.labels = labels;
        pieChart.data.datasets[0].data = data;
        pieChart.data.datasets[0].backgroundColor = backgroundColors;
        pieChart.data.datasets[0].label = type === 'money' ? '거래대금' : '거래량';
        pieChart.options.plugins.title.text = type === 'money' ? '거래대금 TOP10' : '거래량 TOP10';
        pieChart.update();
    } else {
        const pieCtx = document.getElementById('pieChart');
        if (!pieCtx) return;
        pieChart = new Chart(pieCtx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: type === 'money' ? '거래대금' : '거래량',
                        data: data,
                        backgroundColor: backgroundColors,
                        borderWidth: 1,
                    },
                ],
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: true, position: 'bottom' },
                    title: {
                        display: true,
                        text: type === 'money' ? '거래대금 TOP10' : '거래량 TOP10',
                        font: { size: 22 },
                    },
                    tooltip: { enabled: true },
                },
            },
        });
    }
}

// 최초 실행 (bar + pie)
drawChart('money');
drawPieChart('money');

// 독립적인 라디오 그룹 처리 (HTML과 name 일치)
const barDefault = document.querySelector('input[name="sortType"]:checked');
const pieDefault = document.querySelector('input[name="pieSortType"]:checked');
if (barDefault) drawChart(barDefault.value);
if (pieDefault) drawPieChart(pieDefault.value);

document.querySelectorAll('input[name="sortType"]').forEach((radio) => {
    radio.addEventListener('change', function () {
        drawChart(this.value);
    });
});
document.querySelectorAll('input[name="pieSortType"]').forEach((radio) => {
    radio.addEventListener('change', function () {
        drawPieChart(this.value);
    });
});