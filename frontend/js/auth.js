/**
 * TalentHub – Auth Page Scripts & Demo Quick-Login Handlers
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Handle Login Form
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const submitBtn = loginForm.querySelector('button[type="submit"]');

      try {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Signing in...';

        const data = await apiFetch('/auth/login', {
          method: 'POST',
          body: JSON.stringify({ email, password })
        });

        setAuthSession(data);
        showToast('success', 'Login Successful', `Welcome back, ${data.name || data.email}!`);

        // Redirect based on role
        setTimeout(() => {
          if (data.role === 'student') window.location.href = '/student/dashboard.html';
          else if (data.role === 'company') window.location.href = '/company/dashboard.html';
          else if (data.role === 'admin') window.location.href = '/admin/dashboard.html';
          else window.location.href = '/index.html';
        }, 800);
      } catch (err) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Sign In';
      }
    });
  }

  // 2. Demo Quick-Fill Buttons
  const demoAccounts = {
    'student-rahul': { email: 'rahul.sharma@talenthub.edu', pass: 'StudentPass123!' },
    'student-priya': { email: 'priya.nair@talenthub.edu', pass: 'StudentPass123!' },
    'student-amit': { email: 'amit.verma@talenthub.edu', pass: 'StudentPass123!' },
    'company-tcs': { email: 'campus@tcs.com', pass: 'CompanyPass123!' },
    'company-msft': { email: 'university@microsoft.com', pass: 'CompanyPass123!' },
    'admin-coord': { email: 'admin@talenthub.edu', pass: 'AdminPassword123!' },
  };

  document.querySelectorAll('.btn-demo').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const key = btn.getAttribute('data-demo');
      const creds = demoAccounts[key];
      if (creds) {
        const emailInput = document.getElementById('email');
        const passInput = document.getElementById('password');
        if (emailInput && passInput) {
          emailInput.value = creds.email;
          passInput.value = creds.pass;
          // Auto submit if available
          if (loginForm) {
            loginForm.dispatchEvent(new Event('submit'));
          }
        }
      }
    });
  });

  // 3. Handle Student Registration Form
  const studentRegForm = document.getElementById('student-register-form');
  if (studentRegForm) {
    studentRegForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = studentRegForm.querySelector('button[type="submit"]');

      const payload = {
        full_name: document.getElementById('full_name').value.trim(),
        usn: document.getElementById('usn').value.trim().toUpperCase(),
        email: document.getElementById('email').value.trim(),
        branch: document.getElementById('branch').value,
        cgpa: parseFloat(document.getElementById('cgpa').value),
        active_backlogs: parseInt(document.getElementById('active_backlogs').value || 0),
        cleared_backlogs: parseInt(document.getElementById('cleared_backlogs').value || 0),
        phone: document.getElementById('phone').value.trim() || null,
        skills: document.getElementById('skills').value.trim() || null,
        password: document.getElementById('password').value,
        consent_given: document.getElementById('consent_given').checked
      };

      try {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Registering Student...';

        const data = await apiFetch('/auth/register/student', {
          method: 'POST',
          body: JSON.stringify(payload)
        });

        setAuthSession(data);
        showToast('success', 'Registration Successful', 'Welcome to TalentHub! Redirecting to student dashboard...');

        setTimeout(() => {
          window.location.href = '/student/dashboard.html';
        }, 1000);
      } catch (err) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Complete Student Registration';
      }
    });
  }

  // 4. Handle Company Registration Form
  const companyRegForm = document.getElementById('company-register-form');
  if (companyRegForm) {
    companyRegForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = companyRegForm.querySelector('button[type="submit"]');

      const payload = {
        name: document.getElementById('company_name').value.trim(),
        email: document.getElementById('email').value.trim(),
        password: document.getElementById('password').value,
        contact_email: document.getElementById('contact_email').value.trim() || document.getElementById('email').value.trim(),
        website: document.getElementById('website').value.trim() || null,
        location: document.getElementById('location').value.trim() || null,
        industry: document.getElementById('industry').value.trim() || null,
        description: document.getElementById('description').value.trim() || null
      };

      try {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Registering Company...';

        const data = await apiFetch('/auth/register/company', {
          method: 'POST',
          body: JSON.stringify(payload)
        });

        setAuthSession(data);
        showToast('success', 'Registration Successful', 'Welcome to TalentHub! Redirecting to company portal...');

        setTimeout(() => {
          window.location.href = '/company/dashboard.html';
        }, 1000);
      } catch (err) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Register Company Profile';
      }
    });
  }
});
