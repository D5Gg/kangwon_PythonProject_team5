window.addEventListener("DOMContentLoaded", (event) => {
  // Toggle the side navigation
  const sidebarToggle = document.body.querySelector("#sidebarToggle");
  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", (event) => {
      event.preventDefault();
      document.body.classList.toggle("sb-sidenav-toggled");
      localStorage.setItem(
        "sb|sidebar-toggle",
        document.body.classList.contains("sb-sidenav-toggled")
      );
    });
  }

    const form = document.querySelector("form"); // form 선택
  const button = document.getElementById("btnNavbarSearch");
  const input = document.getElementById("searchInput");

  if (!form || !button || !input) return;

  // 폼 제출 시 실행 (엔터 포함)
  form.addEventListener("submit", (event) => {
    event.preventDefault(); // 폼 기본 제출 막기
    button.click();         // 버튼 클릭 함수 트리거
  });

  button.addEventListener("click", async () => {
    const stockName = input.value.trim();
    if (!stockName) {
      alert("주식 이름을 입력해주세요.");
      return;
    }
    try {
      const response = await fetch(`/api/search-stock/?stock_name=${encodeURIComponent(stockName)}`);
      if (!response.ok) {
        const errorData = await response.json();
        alert(errorData.error || "검색 중 오류가 발생했습니다.");
        return;
      }
      const data = await response.json();
      if (data.code) {
        window.location.href = `/stock.html/?code=${data.code}`;
      } else {
        alert("해당 종목을 찾을 수 없습니다.");
      }
    } catch (err) {
      console.error("검색 중 오류 발생:", err);
      alert("검색 중 오류가 발생했습니다.");
    }
  });
});