/**
 * HALCON CAREER - Client-Side Interactivity & Form Utilities
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Auto-dismiss flash messages after 6 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      if (bootstrap && bootstrap.Alert) {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      }
    }, 6000);
  });

  // 2. Client-side Resume Upload Validation
  const resumeInputs = document.querySelectorAll('input[type="file"][name*="resume"]');
  resumeInputs.forEach(function (input) {
    input.addEventListener('change', function (e) {
      const file = e.target.files[0];
      if (!file) return;

      const allowedExtensions = /(\.pdf|\.docx|\.doc)$/i;
      const maxSize = 5 * 1024 * 1024; // 5 MB

      if (!allowedExtensions.exec(file.name)) {
        alert('Invalid file format. Please upload a PDF, DOCX, or DOC file.');
        e.target.value = '';
        return;
      }

      if (file.size > maxSize) {
        alert('File size exceeds the 5 MB limit. Please upload a smaller file.');
        e.target.value = '';
        return;
      }
    });
  });

  // 3. Copy Job Link feature
  const copyBtn = document.getElementById('copyJobLinkBtn');
  if (copyBtn) {
    copyBtn.addEventListener('click', function () {
      navigator.clipboard.writeText(window.location.href).then(function () {
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i class="bi bi-check-lg me-1"></i> Link Copied!';
        copyBtn.classList.remove('btn-outline-custom');
        copyBtn.classList.add('btn-success');
        setTimeout(function () {
          copyBtn.innerHTML = originalText;
          copyBtn.classList.remove('btn-success');
          copyBtn.classList.add('btn-outline-custom');
        }, 3000);
      });
    });
  }

  // 4. Form submission spinner feedback
  const forms = document.querySelectorAll('form[data-loading-feedback]');
  forms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Processing...';
      }
    });
  });
});

