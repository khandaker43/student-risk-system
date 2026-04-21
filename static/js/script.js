// ================= FILTER STUDENTS TABLE =================
function filterTable() {
  const subject = document.getElementById('subjectFilter')?.value || '';
  const status  = document.getElementById('statusFilter')?.value || '';
  const rows    = document.querySelectorAll('#studentsTable tbody tr');

  let visible = 0;

  rows.forEach(r => {
    const s = r.dataset.subject || '';
    const t = r.dataset.status  || '';

    const show = (!subject || s === subject) && (!status || t === status);

    r.style.display = show ? '' : 'none';
    if (show) visible++;
  });

  const el = document.getElementById('showingText');
  if (el) el.textContent = `Showing ${visible} of ${rows.length} students`;
}


// ================= FILTER AT-RISK TABLE =================
function filterAtRisk() {
  const subject = document.getElementById('subjectFilter')?.value || '';
  const rows    = document.querySelectorAll('#atRiskTable tbody tr');

  let visible = 0;

  rows.forEach(r => {
    const s = r.dataset.subject || '';
    const show = !subject || s === subject;

    r.style.display = show ? '' : 'none';
    if (show) visible++;
  });

  const el = document.getElementById('showingText');
  if (el) el.textContent = `Showing ${visible} students`;
}


// ================= FILE UPLOAD HANDLER =================
function handleFile(input) {
  if (input.files && input.files[0]) {
    const file = input.files[0];

    const preview = document.getElementById('filePreview');
    const nameEl  = document.getElementById('fileName');
    const sizeEl  = document.getElementById('fileSize');
    const uploadBtn = document.getElementById('uploadBtn');

    if (nameEl) nameEl.textContent = file.name;
    if (sizeEl) sizeEl.textContent = (file.size / 1024).toFixed(1) + ' KB';
    if (preview) preview.style.display = 'flex';
    if (uploadBtn) uploadBtn.disabled = false;
  }
}


// ================= DOM READY =================
document.addEventListener('DOMContentLoaded', function () {

  // ── Sidebar logout ──────────────────────────────────────
  const sideLogout = document.querySelector('.user-logout');
  if (sideLogout) {
    sideLogout.setAttribute('href', '/logout');
    sideLogout.addEventListener('click', (e) => {
      e.preventDefault();
      window.location.href = '/logout';
    });
  }

  // ── Bell icon → notifications page ─────────────────────
  const notifBtn = document.querySelector('.icon-btn');
  if (notifBtn) {
    notifBtn.addEventListener('click', () => {
      window.location.href = '/notifications';
    });
  }

  // ── Avatar → logout ─────────────────────────────────────
  const profileBtn = document.querySelector('.topbar-avatar');
  if (profileBtn) {
    profileBtn.style.cursor = 'pointer';
    profileBtn.addEventListener('click', () => {
      window.location.href = '/logout';
    });
  }

  // ── Drag & drop upload ──────────────────────────────────
  const dropZone  = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');

  if (dropZone) {
    dropZone.addEventListener('click', () => fileInput?.click());

    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.style.borderColor = '#3b5fc0';
    });

    dropZone.addEventListener('dragleave', () => {
      dropZone.style.borderColor = '';
    });

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.style.borderColor = '';
      if (e.dataTransfer.files.length && fileInput) {
        fileInput.files = e.dataTransfer.files;
        handleFile(fileInput);
      }
    });
  }

  if (fileInput) {
    fileInput.addEventListener('change', () => handleFile(fileInput));
  }

  // ── File remove button ──────────────────────────────────
  const fileRemove = document.getElementById('fileRemove');
  if (fileRemove && fileInput) {
    fileRemove.addEventListener('click', () => {
      fileInput.value = '';
      const preview   = document.getElementById('filePreview');
      const uploadBtn = document.getElementById('uploadBtn');
      if (preview)   preview.style.display = 'none';
      if (uploadBtn) uploadBtn.disabled = true;
    });
  }

  // ================= DRAW BAR CHART =================
  if (typeof subjectData !== 'undefined') {

    const canvas = document.getElementById('barChart');

    if (canvas) {
      const ctx = canvas.getContext('2d');

      const W = canvas.offsetWidth || 400;
      canvas.width  = W;
      canvas.height = 160;

      const subjects = Object.keys(subjectData);
      if (subjects.length === 0) return;

      const maxVal = Math.max(
        ...subjects.map(s => subjectData[s].at_risk + subjectData[s].safe)
      );

      const barW      = 18;
      const gap       = 6;
      const groupGap  = 24;
      const chartH    = 130;
      const offsetX   = 30;
      const offsetY   = 10;
      const groupW    = barW * 2 + gap + groupGap;

      ctx.font      = '11px Inter';
      ctx.fillStyle = '#6b7280';

      for (let i = 0; i <= 3; i++) {
        const y = offsetY + chartH - (i / 3) * chartH;
        ctx.fillText(i, 0, y + 4);
        ctx.beginPath();
        ctx.strokeStyle = '#e5e9f2';
        ctx.lineWidth   = 1;
        ctx.moveTo(offsetX - 4, y);
        ctx.lineTo(W, y);
        ctx.stroke();
      }

      subjects.forEach((subj, i) => {
        const x     = offsetX + i * groupW;
        const riskH = (subjectData[subj].at_risk / maxVal) * chartH;
        const safeH = (subjectData[subj].safe   / maxVal) * chartH;

        ctx.fillStyle = '#e53935';
        ctx.fillRect(x, offsetY + chartH - riskH, barW, riskH);

        ctx.fillStyle = '#43a047';
        ctx.fillRect(x + barW + gap, offsetY + chartH - safeH, barW, safeH);

        ctx.fillStyle = '#6b7280';
        ctx.fillText(subj, x - 4, offsetY + chartH + 16);
      });
    }
  }

});
