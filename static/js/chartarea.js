document.addEventListener("DOMContentLoaded", function () {
  // 기본 Chart.js 스타일 설정 (SB Admin 테마와 유사하게)
  Chart.defaults.font.family =
    '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif,"Noto Sans KR"';
  Chart.defaults.color = "#212529";

  // 예시: basicData가 날짜별 지수 배열이라고 가정
  const basicData = JSON.parse(
    document.getElementById("basicData").textContent
  );
  console.log("기본 데이터:", basicData);

  // 차트 인스턴스 가져오기 ('kospiChart' ID를 사용)
  const ctx = document.getElementById("kospiChart").getContext("2d");

  // Chart.js 객체 생성
  const kospiChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: basicData.labels,
      datasets: [
        {
          label: "KOSPI 지수",
          data: basicData.values,
          borderColor: "rgba(2,117,216,1)",
          backgroundColor: "rgba(2,117,216,0.1)",
          fill: true,
          tension: 0.2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        x: {
          ticks: {
            maxTicksLimit: 10, // x축에 표시될 최대 시간 레이블 수
          },
        },
        y: {
          beginAtZero: false,
        },
      },
      plugins: {
        legend: {
          display: false, // 카드 헤더에 제목이 있으므로 범례는 숨김
        },
      },
      interaction: {
        intersect: false,
        mode: "index",
      },
    },
  });

  // --- MODIFIED CODE STARTS HERE ---

  // ✅ 1. 먼저 정의되어야 함
  async function fetchKOSPIRealtimeData() {
    try {
      const response = await fetch("/api/kospi_realtime/");
      if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
      return await response.json();
    } catch (err) {
      console.error("Error fetching KOSPI realtime data:", err);
      return null;
    }
  }

  // ✅ 2. 그 다음 정의되어야 함
  async function updateChartData() {
    try {
      const data = await fetchKOSPIRealtimeData();
      console.log("실시간 응답:", data);

      if (!data?.datas?.length) {
        console.warn("KOSPI 'datas' 비어 있음:", data);
        return;
      }

      console.log("datas[0] 구조:", data.datas[0]);

      const rawValue = data.datas[0]?.closePrice; // '2,894.62' 형태 문자열

      if (typeof rawValue === "string") {
        const currentValue = parseFloat(rawValue.replace(/,/g, ""));
        const now = new Date().toLocaleTimeString("ko-KR", { hour12: false });

        if (kospiChart.data.labels.length >= 20) {
          kospiChart.data.labels.shift();
          kospiChart.data.datasets[0].data.shift();
        }

        kospiChart.data.labels.push(now);
        kospiChart.data.datasets[0].data.push(currentValue);
        kospiChart.update("none");
      } else {
        console.warn("rawValue가 문자열이 아닙니다:", rawValue);
      }
    } catch (err) {
      console.error("KOSPI 데이터 처리 중 오류 발생:", err);
    }
  }

  // ✅ 3. 마지막에 호출
  setInterval(updateChartData, 5000);
  updateChartData();
});
