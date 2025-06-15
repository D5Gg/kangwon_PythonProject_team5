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


});