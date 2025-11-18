const BASE_URL = "/api/grades";

const message = document.getElementById("message");

async function getAllGrades() {
    const tableBody = document.querySelector("#gradesTable tbody");
    tableBody.innerHTML = "";

    try {
        const res = await fetch(BASE_URL);
        const data = await res.json();

        Object.entries(data).forEach(([name, grade]) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${name}</td>
                <td>${grade}</td>
                <td>
                    <button onclick="editGrade('${name}', ${grade})">Edit</button>
                    <button onclick="deleteGrade('${name}')">Delete</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (err) {
        message.textContent = "Failed to fetch students.";
    }
}

// Add student
async function addGrade() {
    const name = document.getElementById("newName").value.trim();
    const grade = parseFloat(document.getElementById("newGrade").value);

    if (!name || isNaN(grade)) {
        message.textContent = "Enter both name and grade.";
        return;
    }

    try {
        await fetch(BASE_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, grade })
        });
        message.textContent = `Added ${name} with grade ${grade}`;
        getAllGrades();
        document.getElementById("newName").value = "";
        document.getElementById("newGrade").value = "";
    } catch (err) {
        message.textContent = "Failed to add student.";
    }
}

// Edit
async function editGrade(name, currentGrade) {
    const newGrade = prompt(`Enter new grade for ${name}:`, currentGrade);
    if (newGrade === null) return;

    try {
        await fetch(`${BASE_URL}/${encodeURIComponent(name)}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ grade: parseFloat(newGrade) })
        });
        message.textContent = `Updated ${name}'s grade to ${newGrade}`;
        getAllGrades();
    } catch (err) {
        message.textContent = "Failed to update student.";
    }
}

// Delete
async function deleteGrade(name) {
    if (!confirm(`Delete ${name}'s grade?`)) return;

    try {
        await fetch(`${BASE_URL}/${encodeURIComponent(name)}`, {
            method: "DELETE"
        });
        message.textContent = `Deleted ${name}'s grade.`;
        getAllGrades();
    } catch (err) {
        message.textContent = "Failed to delete student.";
    }
}

// Student Grades
async function getGrade() {
    const name = document.getElementById("studentName").value.trim();
    const result = document.getElementById("singleResult");

    if (!name) {
        result.textContent = "Please enter a student name.";
        return;
    }

    try {
        const res = await fetch(`${BASE_URL}/${encodeURIComponent(name)}`);
        const data = await res.json();
        if (res.status === 404) {
            result.textContent = `Student "${name}" not found.`;
        } else {
            result.textContent = `${name}'s grade: ${data[name]}`;
        }
    } catch (err) {
        result.textContent = "Failed to fetch grade.";
    }
}

getAllGrades();
