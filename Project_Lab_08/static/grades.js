// grades.js - Handles all frontend API calls for Lab 7
// This file connects to your Flask REST API and performs:
// 1. Fetch all grades
// 2. Add a new student
// 3. Update a student's grade
// 4. Delete a student
// 5. Search for a student's grade

// ============================================================
// Show a temporary message in the #msg element
// Used for success/error feedback like "Student added"
// ============================================================
function showMessage(text, timeout = 2500) {
  const el = document.getElementById("msg");
  if (!el) return;
  el.textContent = text;
  clearTimeout(el._t);
  el._t = setTimeout(() => (el.textContent = ""), timeout);
}

// ============================================================
// Fetch and display all students and their grades
// Calls GET /api/grades
// ============================================================
async function fetchGrades() {
  try {
    const response = await fetch("/api/grades");
    if (!response.ok) throw new Error("Failed to load grades");
    const data = await response.json();
    const list = document.getElementById("gradeList");
    if (!list) return;
    list.innerHTML = "";
    if (Object.keys(data).length === 0) {
      list.innerHTML = "<li>No students yet.</li>";
      return;
    }
    for (const [name, grade] of Object.entries(data)) {
      const item = document.createElement("li");
      item.textContent = `${name}: ${grade}`;
      list.appendChild(item);
    }
  } catch (err) {
    console.error(err);
    showMessage("Error loading grades");
  }
}

// ============================================================
// Add a new student to the database
// Calls POST /api/grades
// ============================================================
async function addStudent() {
  const name = document.getElementById("newName")?.value?.trim();
  const grade = document.getElementById("newGrade")?.value?.trim();
  if (!name || !grade) return showMessage("Please enter name and grade");

  try {
    const res = await fetch("/api/grades", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, grade })
    });
    const body = await res.json();
    if (!res.ok) return showMessage(body.error || "Failed to add student");
    showMessage("Student added");
    document.getElementById("newName").value = "";
    document.getElementById("newGrade").value = "";
    await fetchGrades();
  } catch (err) {
    console.error(err);
    showMessage("Network error adding student");
  }
}

// ============================================================
// Update an existing student's grade
// Calls PUT /api/grades/<name>
// ============================================================
async function updateStudent() {
  const name = document.getElementById("updateName")?.value?.trim();
  const grade = document.getElementById("updateGrade")?.value?.trim();
  if (!name || !grade) return showMessage("Please enter name and new grade");

  try {
    const res = await fetch(`/api/grades/${encodeURIComponent(name)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ grade })
    });
    const body = await res.json();
    if (!res.ok) return showMessage(body.error || "Failed to update");
    showMessage("Grade updated");
    document.getElementById("updateName").value = "";
    document.getElementById("updateGrade").value = "";
    await fetchGrades();
  } catch (err) {
    console.error(err);
    showMessage("Network error updating grade");
  }
}

// ============================================================
// Delete a student from the database
// Calls DELETE /api/grades/<name>
// ============================================================
async function deleteStudent() {
  const name = document.getElementById("deleteName")?.value?.trim();
  if (!name) return showMessage("Please enter name to delete");
  if (!confirm(`Delete student "${name}"?`)) return;

  try {
    const res = await fetch(`/api/grades/${encodeURIComponent(name)}`, {
      method: "DELETE"
    });
    const body = await res.json();
    if (!res.ok) return showMessage(body.error || "Failed to delete");
    showMessage("Student deleted");
    document.getElementById("deleteName").value = "";
    await fetchGrades();
  } catch (err) {
    console.error(err);
    showMessage("Network error deleting student");
  }
}

// ============================================================
// Search for a student's grade by name
// Calls GET /api/grades/<name>
// ============================================================
async function searchGrade() {
  const name = document.getElementById("searchName")?.value?.trim();
  const resultEl = document.getElementById("searchResult");
  if (!name) return showMessage("Please enter a name to search");

  try {
    const response = await fetch(`/api/grades/${encodeURIComponent(name)}`);
    if (response.ok) {
      const data = await response.json();
      resultEl.textContent = `${name}: ${data[name]}`;
    } else {
      resultEl.textContent = "Student not found.";
    }
  } catch (err) {
    console.error(err);
    resultEl.textContent = "Error searching for student.";
  }
}

// ============================================================
// Attach button event listeners based on page content
// This avoids using inline onclick attributes
// ============================================================
function attachHandlers() {
  const addBtn = document.getElementById("addBtn");
  if (addBtn) addBtn.addEventListener("click", addStudent);

  const updateBtn = document.getElementById("updateBtn");
  if (updateBtn) updateBtn.addEventListener("click", updateStudent);

  const deleteBtn = document.getElementById("deleteBtn");
  if (deleteBtn) deleteBtn.addEventListener("click", deleteStudent);

  const searchBtn = document.getElementById("searchBtn");
  if (searchBtn) searchBtn.addEventListener("click", searchGrade);

  const reloadBtn = document.getElementById("reloadBtn");
  if (reloadBtn) reloadBtn.addEventListener("click", fetchGrades);
}

// ============================================================
// When the page loads:
// - Attach button handlers
// - Optionally fetch grades (only works on index.html)
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
  attachHandlers();
  fetchGrades(); // Only affects pages with a grade list
});

// ============================================================
// Auto-refresh homepage when returning to it
// This ensures the grade list is always up to date
// ============================================================
window.addEventListener("pageshow", () => {
  const list = document.getElementById("gradeList");
  if (list) fetchGrades(); // Only reload if on homepage
});