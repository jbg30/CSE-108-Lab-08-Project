document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;

  if (path.includes('/student/login')) initStudentLogin();
  if (path.includes('/student/dashboard')) loadStudentDashboard();
  if (path.includes('/student/register')) loadClassRegistration();
});

// ---------- Login ----------
function initStudentLogin() {
  const loginForm = document.getElementById('studentLoginForm');
  const msg = document.getElementById('stuLoginMsg');

  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const email = document.getElementById('studentLoginEmail').value.trim();
      const password = document.getElementById('studentLoginPassword').value.trim();

      if (!email || !password) {
        if (msg) msg.textContent = 'Please enter email and password.';
        return;
      }

      // Submit the form to Flask backend (traditional form submission)
      loginForm.submit();
    });
  }
}

// ---------- Dashboard ----------
async function loadStudentDashboard() {
  const msg = document.getElementById('studentDashboardMsg');
  const enrolledTable = document.querySelector('#enrolledTable tbody');
  
  if (enrolledTable) {
    // Data is already populated by Flask template, no need to fetch via API
    console.log('Student dashboard loaded with template data');
  }

  // Register for classes button
  const registerBtn = document.getElementById('registerClassesBtn');
  registerBtn?.addEventListener('click', () => {
    window.location.href = '/student/register';
  });
}

// ---------- Class Registration ----------
function loadClassRegistration() {
  const table = document.querySelector('#classCatalog tbody');
  const msg = document.getElementById('classListMsg');
  
  if (table) {
    // Data is passed from Flask template, so the table is already populated
    // We just need to make the join buttons work with the backend
    console.log('Class registration page loaded with template data');
    
    // Add event listeners to all join buttons
    const joinButtons = document.querySelectorAll('.join-btn');
    joinButtons.forEach(button => {
      button.addEventListener('click', function() {
        const courseId = this.getAttribute('data-course-id');
        joinClass(parseInt(courseId));
      });
    });
  }
}

// Join class function - works with backend API
async function joinClass(courseId) {
  try {
    console.log(`🎯 Attempting to join course ID: ${courseId}`);
    
    const response = await fetch('/api/student/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ courseId: courseId })
    });

    const data = await response.json();
    
    if (response.ok) {
      alert('✅ Successfully enrolled in class!');
      window.location.reload(); // Refresh to update enrollment numbers
    } else {
      alert(`❌ ${data.error || 'Failed to enroll in class.'}`);
    }
  } catch (err) {
    console.error('Error joining class:', err);
    alert('❌ Error joining class. Please try again.');
  }
}

// ---------- Logout ----------
function logoutStudent() {
  window.location.href = '/logout';
}

// Make functions available globally
window.joinClass = joinClass;
window.logoutStudent = logoutStudent;