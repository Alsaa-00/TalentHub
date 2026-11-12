/**
 * TalentHub – Common UI Utility Helpers
 */

function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  } catch (e) {
    return dateStr;
  }
}

function formatDateTime(dateStr) {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    return d.toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (e) {
    return dateStr;
  }
}

function formatLPA(lpa) {
  if (lpa === undefined || lpa === null) return '—';
  return `₹${parseFloat(lpa).toFixed(2)} LPA`;
}

function getStatusBadge(status) {
  const map = {
    'APPLIED': { label: 'Applied', class: 'badge-APPLIED' },
    'SHORTLISTED': { label: 'Shortlisted', class: 'badge-SHORTLISTED' },
    'INTERVIEW_SCHEDULED': { label: 'Interview Scheduled', class: 'badge-INTERVIEW_SCHEDULED' },
    'INTERVIEWED': { label: 'Interviewed', class: 'badge-INTERVIEWED' },
    'OFFERED': { label: 'Offered', class: 'badge-OFFERED' },
    'ACCEPTED': { label: 'Offer Accepted', class: 'badge-ACCEPTED' },
    'REJECTED': { label: 'Rejected', class: 'badge-REJECTED' },
  };
  const s = map[status] || { label: status, class: 'badge-blue' };
  return `<span class="badge ${s.class}">${s.label}</span>`;
}

// Modal helper functions
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('active');
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
  }
}

// Close modals when clicking overlay background
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('active');
  }
});
