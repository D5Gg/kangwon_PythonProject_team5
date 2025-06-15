// 숫자 단축 함수
function formatEok(value) {
    if (Math.abs(value) >= 100000000) {
        // 소수점 없이 정수로만 억 단위
        return Math.round(value / 100000000).toLocaleString() + '억';
    }
    if (Math.abs(value) >= 10000) {
        return Math.round(value / 10000).toLocaleString() + '만';
    }
    return value.toLocaleString();
}

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
            tooltip: {
                enabled: true,
                callbacks: {
                    label: function(context) {
                        const label = context.dataset.label || '';
                        const value = context.parsed.y ?? context.parsed;
                        return label + ': ' + formatEok(value);
                    }
                }
            },
        },
        scales: {
            yAxes: [{
                ticks: {
                    callback: function (value) {
                        return formatEok(value);
                    },
                },
                beginAtZero: true,
            }],
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
                    tooltip: {
                        enabled: true,
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                return label + ': ' + formatEok(value);
                            }
                        }
                    },
                },
            },
        });
    }
}

// AREA CHART LOGIC (분포)
let areaChart = null;
function getAreaBinData(type) {
    const areaBinData = document.getElementById('areaBinData');
    if (!areaBinData) return { labels: [], counts: [] };
    const data = JSON.parse(areaBinData.textContent);
    console.log('areaBinData:', data[type]); // 데이터 콘솔 출력
    return data[type] || { labels: [], counts: [] };
}
function drawAreaChart(type) {
    const { labels, counts } = getAreaBinData(type);
    const ctx = document.getElementById('myAreaChart').getContext('2d');
    const color = type === 'money' ? 'rgba(52, 152, 219, 0.5)' : 'rgba(46, 204, 113, 0.5)';
    if (areaChart) {
        areaChart.data.labels = labels.length ? labels : ['구간1','구간2','구간3','구간4','구간5'];
        areaChart.data.datasets[0].data = counts.length ? counts : [0,0,0,0,0];
        areaChart.data.datasets[0].label = type === 'money' ? '거래대금 분포(개수)' : '거래량 분포(개수)';
        areaChart.options.plugins.title.text = type === 'money' ? '거래대금 분포(상위 5구간)' : '거래량 분포(상위 5구간)';
        areaChart.data.datasets[0].backgroundColor = color;
        areaChart.update();
    } else {
        areaChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels.length ? labels : ['구간1','구간2','구간3','구간4','구간5'],
                datasets: [
                    {
                        label: type === 'money' ? '거래대금 분포(개수)' : '거래량 분포(개수)',
                        data: counts.length ? counts : [0,0,0,0,0],
                        fill: true,
                        backgroundColor: color,
                        borderColor: color.replace('0.5', '1'),
                        tension: 0.4,
                        pointRadius: 5,
                        pointBackgroundColor: color.replace('0.5', '1'),
                    },
                ],
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: type === 'money' ? '거래대금 분포(상위 5구간)' : '거래량 분포(상위 5구간)',
                        font: { size: 22 },
                    },
                    tooltip: {
                        enabled: true,
                        callbacks: {
                            label: function(context) {
                                const label = context.dataset.label || '';
                                const value = context.parsed.y ?? context.parsed;
                                return label + ': ' + formatEok(value);
                            }
                        }
                    },
                },
                scales: {
                    yAxes: [{
                        ticks: {
                            callback: function (value) {
                                return formatEok(value);
                            },
                        },
                        beginAtZero: true,
                    }],
                },
            },
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
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
    // area chart
    const areaDefault = document.querySelector('input[name="areaType"]:checked');
    if (areaDefault) drawAreaChart(areaDefault.value);
    document.querySelectorAll('input[name="areaType"]').forEach((radio) => {
        radio.addEventListener('change', function () {
            drawAreaChart(this.value);
        });
    });
});