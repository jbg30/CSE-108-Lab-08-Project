function logoutTeacher() {
  window.location.href = '/logout';
}


// Enters grade and saves, then requests backend to update (flask API)
async function updateGrade(courseId, studentId) {
  const gradeInput = document.getElementById(`grade-${studentId}`);
  const grade = gradeInput.value;

  try {
    const response = await fetch(`/api/course/${courseId}/student/${studentId}/grade`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ grade: parseFloat(grade) })
    });

    const data = await response.json();
    if (response.ok) {
      alert('✅ Grade updated successfully!');
    } else {
      alert(`❌ ${data.error}`);
    }
  } catch (err) {
    console.error(err);
    alert('❌ Error updating grade');
  }
}

window.updateGrade = updateGrade;
window.logoutTeacher = logoutTeacher;