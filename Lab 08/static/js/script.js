const BASE_URL = "/api/grades";
const message = document.getElementById("message");

// Load all grades when page loads
document.addEventListener('DOMContentLoaded', function() {
  getAllGrades();
});

async function getAllGrades() {
  const tableBody = document.querySelector("#gradesTable tbody");
  if (!tableBody) return;
  
  tableBody.innerHTML = "";

  try {
    const res = await fetch(BASE_URL);
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    const data = await res.json();

    if (Object.keys(data).length === 0) {
      tableBody.innerHTML = '<tr><td colspan="3">No grades found</td></tr>';
      return;
    }

    Object.entries(data).forEach(([name, grade]) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${name}</td>
        <td>${grade}</td>
        <td>
          <button class="btn btn-warning btn-sm" onclick="editGrade('${name}', ${grade})">Edit</button>
          <button class="btn btn-danger btn-sm" onclick="deleteGrade('${name}')">Delete</button>
        </td>
      `;
      tableBody.appendChild(row);
    });
  } catch (err) {
    console.error('Error fetching grades:', err);
    if (message) message.textContent = "Failed to fetch students.";
  }
}

// Add student grade
async function addGrade() {
  const name = document.getElementById("newName").value.trim();
  const grade = parseFloat(document.getElementById("newGrade").value);

  if (!name || isNaN(grade)) {
    if (message) message.textContent = "Enter both name and grade.";
    return;
  }

  try {
    const response = await fetch(BASE_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, grade })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      if (message) message.textContent = `✅ Added ${name} with grade ${grade}`;
      getAllGrades();
      document.getElementById("newName").value = "";
      document.getElementById("newGrade").value = "";
    } else {
      if (message) message.textContent = `❌ ${data.error || 'Failed to add student.'}`;
    }
  } catch (err) {
    console.error('Error adding grade:', err);
    if (message) message.textContent = "❌ Failed to add student.";
  }
}

// Edit grade
async function editGrade(name, currentGrade) {
  const newGrade = prompt(`Enter new grade for ${name}:`, currentGrade);
  if (newGrade === null) return;

  try {
    const response = await fetch(`${BASE_URL}/${encodeURIComponent(name)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ grade: parseFloat(newGrade) })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      if (message) message.textContent = `✅ Updated ${name}'s grade to ${newGrade}`;
      getAllGrades();
    } else {
      if (message) message.textContent = `❌ ${data.error || 'Failed to update student.'}`;
    }
  } catch (err) {
    console.error('Error updating grade:', err);
    if (message) message.textContent = "❌ Failed to update student.";
  }
}

// Delete grade
async function deleteGrade(name) {
  if (!confirm(`Are you sure you want to delete ${name}'s grade?`)) return;

  try {
    const response = await fetch(`${BASE_URL}/${encodeURIComponent(name)}`, {
      method: "DELETE"
    });
    
    const data = await response.json();
    
    if (response.ok) {
      if (message) message.textContent = `✅ Deleted ${name}'s grade.`;
      getAllGrades();
    } else {
      if (message) message.textContent = `❌ ${data.error || 'Failed to delete student.'}`;
    }
  } catch (err) {
    console.error('Error deleting grade:', err);
    if (message) message.textContent = "❌ Failed to delete student.";
  }
}

// Get single student grade
async function getGrade() {
  const name = document.getElementById("studentName").value.trim();
  const result = document.getElementById("singleResult");

  if (!name) {
    if (result) result.textContent = "Please enter a student name.";
    return;
  }

  try {
    const res = await fetch(`${BASE_URL}/${encodeURIComponent(name)}`);
    const data = await res.json();
    
    if (res.status === 404) {
      if (result) result.textContent = `❌ Student "${name}" not found.`;
    } else if (data.error) {
      if (result) result.textContent = `❌ ${data.error}`;
    } else {
      if (result) result.textContent = `✅ ${name}'s grade: ${data[name]}`;
    }
  } catch (err) {
    console.error('Error fetching grade:', err);
    if (result) result.textContent = "❌ Failed to fetch grade.";
  }
}

// Make functions available globally
window.getAllGrades = getAllGrades;
window.addGrade = addGrade;
window.editGrade = editGrade;
window.deleteGrade = deleteGrade;
window.getGrade = getGrade;