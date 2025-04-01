document.querySelectorAll("input[type='password']").forEach((e) => {
  e.parentElement
    .getElementsByClassName("input-group-text")[0]
    .addEventListener("click", () => {
      const type = e.getAttribute("type") === "password" ? "text" : "password";
      e.setAttribute("type", type);

      e.parentElement
        .getElementsByClassName("input-group-text")[0]
        .getElementsByClassName("bi")[0]
        .classList.toggle("bi-eye");
      e.parentElement
        .getElementsByClassName("input-group-text")[0]
        .getElementsByClassName("bi")[0]
        .classList.toggle("bi-eye-slash");
    });
});
