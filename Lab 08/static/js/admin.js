document.addEventListener("DOMContentLoaded", () => {
  console.log("admin.js loaded");

  document.querySelectorAll(".edit-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const courseId = btn.dataset.courseId;
      const newName = prompt("New class name:");
      if (!newName) return;

      fetch(`/api/admin/courses/${courseId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newName }),
      })
        .then((res) => res.json())
        .then((data) => {
          console.log(data);
          window.location.reload();
        })
        .catch((err) => console.error(err));
    });
  });

  document.querySelectorAll(".delete-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const courseId = btn.dataset.courseId;
      if (!confirm("Delete this class?")) return;

      fetch(`/api/admin/courses/${courseId}`, {
        method: "DELETE",
      })
        .then((res) => res.json())
        .then((data) => {
          console.log(data);
          window.location.reload();
        })
        .catch((err) => console.error(err));
    });
  });
});