// ===================================================================
// JobConnect – Main Client-Side Interactivity
// ===================================================================

document.addEventListener('DOMContentLoaded', function () {
  // 1. Initialize Bootstrap Tooltips & Popovers
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // 2. Auto-dismiss flash alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // 3. Live Salary Slider updates
  const salaryRange = document.getElementById('salaryRange');
  const salaryValDisplay = document.getElementById('salaryValueDisplay');
  if (salaryRange && salaryValDisplay) {
    salaryRange.addEventListener('input', function (e) {
      const val = parseInt(e.target.value, 10);
      if (val === 0) {
        salaryValDisplay.textContent = 'Any Salary';
      } else {
        const lpa = (val / 100000).toFixed(0);
        salaryValDisplay.textContent = `₹${lpa} LPA+`;
      }
    });
  }

  // 4. AJAX Bookmark / Save Job Toggle
  const saveButtons = document.querySelectorAll('.btn-save-job');
  saveButtons.forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const jobId = this.getAttribute('data-job-id');
      const icon = this.querySelector('i');

      fetch(`/jobs/${jobId}/save`, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        if (response.redirected) {
          window.location.href = response.url;
          return null;
        }
        return response.json();
      })
      .then(data => {
        if (!data) return;
        if (data.status === 'saved') {
          if (icon) {
            icon.classList.remove('far');
            icon.classList.add('fas', 'text-danger');
          }
          showToast('Success', data.message, 'success');
        } else if (data.status === 'unsaved') {
          if (icon) {
            icon.classList.remove('fas', 'text-danger');
            icon.classList.add('far');
          }
          showToast('Updated', data.message, 'info');
        }
      })
      .catch(err => {
        console.error('Error saving job:', err);
      });
    });
  });

  // 5. Notification Mark-as-Read
  const notifLinks = document.querySelectorAll('.notification-item-link');
  notifLinks.forEach(function (item) {
    item.addEventListener('click', function (e) {
      const notifId = this.getAttribute('data-notif-id');
      if (notifId) {
        fetch(`/notifications/mark-read/${notifId}`, {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
      }
    });
  });
});

// Toast notification helper
function showToast(title, message, type = 'info') {
  let toastContainer = document.getElementById('toastContainer');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toastContainer';
    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    toastContainer.style.zIndex = '9999';
    document.body.appendChild(toastContainer);
  }

  const bgClass = type === 'success' ? 'text-bg-success' : (type === 'danger' ? 'text-bg-danger' : 'text-bg-primary');
  const toastId = 'toast_' + Date.now();
  const toastHtml = `
    <div id="${toastId}" class="toast align-items-center ${bgClass} border-0 shadow-lg" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          <strong>${title}:</strong> ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;
  toastContainer.insertAdjacentHTML('beforeend', toastHtml);
  const toastEl = document.getElementById(toastId);
  const bsToast = new bootstrap.Toast(toastEl, { delay: 3500 });
  bsToast.show();
}
