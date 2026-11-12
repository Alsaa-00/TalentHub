/**
 * TalentHub – Centralized API & Authentication Client
 */

const API_BASE = '/api';

// Toast Notification Manager
function showToast(type, title, message) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <div class="toast-content">
      <div class="toast-title">${title}</div>
      <div class="toast-message">${message}</div>
    </div>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Token & User Storage
function setAuthSession(data) {
  localStorage.setItem('talenthub_token', data.access_token);
  localStorage.setItem('talenthub_user', JSON.stringify({
    user_id: data.user_id,
    email: data.email,
    role: data.role,
    name: data.name || data.email,
    profile_id: data.profile_id
  }));
}

function getAuthToken() {
  return localStorage.getItem('talenthub_token');
}

function getCurrentUser() {
  const userStr = localStorage.getItem('talenthub_user');
  try {
    return userStr ? JSON.parse(userStr) : null;
  } catch (e) {
    return null;
  }
}

function clearAuthSession() {
  localStorage.removeItem('talenthub_token');
  localStorage.removeItem('talenthub_user');
}

function logout() {
  clearAuthSession();
  window.location.href = '/login.html';
}

// Unified Fetch API Wrapper
async function apiFetch(endpoint, options = {}) {
  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers
  };

  try {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
    const response = await fetch(url, config);

    if (response.status === 401) {
      clearAuthSession();
      if (!window.location.pathname.includes('login.html') && !window.location.pathname.includes('register')) {
        showToast('error', 'Session Expired', 'Please log in again to continue.');
        setTimeout(() => { window.location.href = '/login.html'; }, 1200);
      }
      throw new Error('Unauthorized');
    }

    // Check for empty body / blob / csv
    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('text/csv')) {
      const blob = await response.blob();
      return blob;
    }

    const data = await response.json();

    if (!response.ok) {
      const errorMsg = data.detail || 'An unexpected error occurred.';
      throw new Error(errorMsg);
    }

    return data;
  } catch (error) {
    if (error.message !== 'Unauthorized') {
      showToast('error', 'Error', error.message);
    }
    throw error;
  }
}

// Route Protection Guard
function requireAuth(allowedRoles = []) {
  const token = getAuthToken();
  const user = getCurrentUser();

  if (!token || !user) {
    window.location.href = '/login.html';
    return null;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    // Redirect to their appropriate dashboard
    if (user.role === 'student') window.location.href = '/student/dashboard.html';
    else if (user.role === 'company') window.location.href = '/company/dashboard.html';
    else if (user.role === 'admin') window.location.href = '/admin/dashboard.html';
    else window.location.href = '/login.html';
    return null;
  }

  return user;
}

// Render dynamic user info in topbar and sidebar
function initUserNavbar() {
  const user = getCurrentUser();
  if (!user) return;

  const nameEls = document.querySelectorAll('.user-name');
  nameEls.forEach(el => el.textContent = user.name || user.email);

  const roleEls = document.querySelectorAll('.user-role');
  roleEls.forEach(el => {
    if (user.role === 'admin') el.textContent = 'Placement Coordinator';
    else if (user.role === 'student') el.textContent = 'Student Candidate';
    else if (user.role === 'company') el.textContent = 'Company Partner';
    else el.textContent = user.role;
  });

  const avatarEls = document.querySelectorAll('.user-avatar');
  avatarEls.forEach(el => {
    const initials = (user.name || user.email).split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
    el.textContent = initials || 'U';
  });

  const logoutBtns = document.querySelectorAll('.btn-logout');
  logoutBtns.forEach(btn => btn.addEventListener('click', (e) => {
    e.preventDefault();
    logout();
  }));

  // Toggle sidebar on mobile
  const toggleBtn = document.querySelector('.btn-sidebar-toggle');
  const sidebar = document.querySelector('.sidebar');
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
  }
}
