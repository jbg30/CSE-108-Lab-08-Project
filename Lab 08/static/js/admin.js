function logoutAdmin() {
  window.location.href = '/logout';
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("admin.js loaded");

  // Update course name
  const courseNameInput = document.getElementById("courseName");
  const updateCourseBtn = document.getElementById("updateCourseName");
  updateCourseBtn.addEventListener("click", () => {
    const courseId = courseNameInput.dataset.courseId;
    const newName = courseNameInput.value.trim();
    if (!newName) return alert("Course name cannot be empty.");

    fetch(`/api/admin/courses/${courseId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: newName }),
    })
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
        alert("Course name updated!");
        location.reload();
      })
      .catch((err) => console.error(err));
  });

  // Update student grade
  document.querySelectorAll(".update-grade").forEach((btn) => {
    btn.addEventListener("click", () => {
      const row = btn.closest("tr");
      const enrollmentId = row.dataset.enrollmentId;
      const grade = row.querySelector(".grade-input").value.trim();

      fetch(`/api/admin/enrollments/${enrollmentId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ grade }),
      })
        .then((res) => res.json())
        .then((data) => {
          console.log(data);
          alert("Grade updated!");
        })
        .catch((err) => console.error(err));
    });
  });

  // Remove student from course
  document.querySelectorAll(".remove-student").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (!confirm("Are you sure you want to remove this student?")) return;

      const row = btn.closest("tr");
      const enrollmentId = row.dataset.enrollmentId;

      fetch(`/api/admin/enrollments/${enrollmentId}`, {
        method: "DELETE",
      })
        .then((res) => res.json())
        .then((data) => {
          console.log(data);
          alert("Student removed!");
          row.remove();
        })
        .catch((err) => console.error(err));
    });
  });
});
// Delete course

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

  window.logoutAdmin = logoutAdmin;