/* KOI Risk System — script.js */
document.addEventListener('DOMContentLoaded', () => {

  /* ── Upload drag & drop ── */
  const dropZone   = document.getElementById('dropZone');
  const fileInput  = document.getElementById('fileInput');
  const filePreview= document.getElementById('filePreview');
  const fileName   = document.getElementById('fileName');
  const fileSize   = document.getElementById('fileSize');
  const fileRemove = document.getElementById('fileRemove');
  const uploadBtn  = document.getElementById('uploadBtn');

  if (dropZone && fileInput) {
    dropZone.addEventListener('click', () => fileInput.click());
    ['dragenter','dragover'].forEach(e => dropZone.addEventListener(e, ev => { ev.preventDefault(); dropZone.classList.add('drag-over'); }));
    ['dragleave','drop'].forEach(e => dropZone.addEventListener(e, () => dropZone.classList.remove('drag-over')));
    dropZone.addEventListener('drop', e => { e.preventDefault(); if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]); });
    fileInput.addEventListener('change', () => { if (fileInput.files[0]) handleFile(fileInput.files[0]); });
    fileRemove?.addEventListener('click', e => {
      e.stopPropagation();
      fileInput.value = '';
      filePreview.style.display = 'none';
      dropZone.style.display = 'flex';
      if (uploadBtn) uploadBtn.disabled = true;
    });

    function handleFile(file) {
      if (fileName) fileName.textContent = file.name;
      if (fileSize) fileSize.textContent = fmtBytes(file.size);
      if (filePreview) filePreview.style.display = 'flex';
      dropZone.style.display = 'none';
      if (uploadBtn) uploadBtn.disabled = false;
    }
    function fmtBytes(b) {
      if (b < 1024) return b + ' B';
      if (b < 1048576) return (b/1024).toFixed(1) + ' KB';
      return (b/1048576).toFixed(1) + ' MB';
    }
  }

  /* ── Results table filter ── */
  const tableSearch   = document.getElementById('tableSearch');
  const statusFilter  = document.getElementById('statusFilter');
  const subjectFilter = document.getElementById('subjectFilter');
  const resultsTable  = document.getElementById('resultsTable');
  const tableInfo     = document.getElementById('tableInfo');

  if (resultsTable) {
    const filter = () => {
      const q   = (tableSearch?.value||'').toLowerCase();
      const st  = statusFilter?.value||'all';
      const sub = subjectFilter?.value||'all';
      let vis = 0;
      resultsTable.querySelectorAll('tbody tr').forEach(row => {
        const show = row.textContent.toLowerCase().includes(q)
          && (st==='all'||row.dataset.status===st)
          && (sub==='all'||row.dataset.subject===sub);
        row.style.display = show ? '' : 'none';
        if (show) vis++;
      });
      if (tableInfo) tableInfo.textContent = `Showing ${vis} record${vis!==1?'s':''}`;
    };
    tableSearch?.addEventListener('input', filter);
    statusFilter?.addEventListener('change', filter);
    subjectFilter?.addEventListener('change', filter);
  }

  /* ── At-risk table filter ── */
  const riskSearch   = document.getElementById('riskSearch');
  const reasonFilter = document.getElementById('reasonFilter');
  const riskTable    = document.getElementById('riskTable');
  const riskInfo     = document.getElementById('riskInfo');

  if (riskTable) {
    const filterRisk = () => {
      const q = (riskSearch?.value||'').toLowerCase();
      const r = reasonFilter?.value||'all';
      let vis = 0;
      riskTable.querySelectorAll('tbody tr').forEach(row => {
        const show = row.textContent.toLowerCase().includes(q)
          && (r==='all'||row.dataset.reason===r);
        row.style.display = show ? '' : 'none';
        if (show) vis++;
      });
      if (riskInfo) riskInfo.textContent = `Showing ${vis} at-risk student${vis!==1?'s':''}`;
    };
    riskSearch?.addEventListener('input', filterRisk);
    reasonFilter?.addEventListener('change', filterRisk);
  }

  /* ── Animate bars on load ── */
  document.querySelectorAll('.subject-bar-fill, .reason-bar-fill, .score-fill').forEach(el => {
    const w = el.style.width;
    el.style.width = '0';
    requestAnimationFrame(() => setTimeout(() => el.style.width = w, 100));
  });

  /* ── Global search redirect ── */
  document.getElementById('globalSearch')?.addEventListener('keydown', e => {
    if (e.key === 'Enter' && e.target.value.trim())
      window.location.href = `/results?q=${encodeURIComponent(e.target.value.trim())}`;
  });

  /* ══════════════════════════════════════════
     NOTIFICATION DROPDOWN
  ══════════════════════════════════════════ */
  const notifBtn = document.querySelector('.icon-btn');

  const notifDropdown = document.createElement('div');
  notifDropdown.id = 'notifDropdown';
  notifDropdown.innerHTML = `
    <div class="dropdown-header">
      <span class="dropdown-title">Notifications</span>
      <span class="dropdown-badge">3 new</span>
    </div>
    <div class="notif-list">
      <div class="notif-item notif-unread">
        <div class="notif-icon notif-red"><i class="fa-solid fa-triangle-exclamation"></i></div>
        <div class="notif-body">
          <div class="notif-text">New at-risk students detected</div>
          <div class="notif-time">Just now</div>
        </div>
      </div>
      <div class="notif-item notif-unread">
        <div class="notif-icon notif-blue"><i class="fa-solid fa-upload"></i></div>
        <div class="notif-body">
          <div class="notif-text">File uploaded successfully</div>
          <div class="notif-time">2 minutes ago</div>
        </div>
      </div>
      <div class="notif-item notif-unread">
        <div class="notif-icon notif-orange"><i class="fa-solid fa-chart-bar"></i></div>
        <div class="notif-body">
          <div class="notif-text">Weekly report is ready</div>
          <div class="notif-time">1 hour ago</div>
        </div>
      </div>
      <div class="notif-item">
        <div class="notif-icon notif-green"><i class="fa-solid fa-circle-check"></i></div>
        <div class="notif-body">
          <div class="notif-text">System check completed</div>
          <div class="notif-time">Yesterday</div>
        </div>
      </div>
    </div>
    <div class="dropdown-footer">
      <a href="#">View all notifications</a>
    </div>
  `;
  notifDropdown.style.cssText = `
    display:none;position:fixed;top:72px;right:80px;
    width:320px;background:#fff;border-radius:12px;
    box-shadow:0 8px 40px rgba(0,0,0,0.15);
    border:1px solid #e2e8f0;z-index:9999;overflow:hidden;
    animation:dropIn .2s ease;
  `;
  document.body.appendChild(notifDropdown);

  notifBtn?.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = notifDropdown.style.display === 'block';
    notifDropdown.style.display = isOpen ? 'none' : 'block';
    profileDropdown.style.display = 'none';
  });

  /* ══════════════════════════════════════════
     PROFILE DROPDOWN
  ══════════════════════════════════════════ */
  const profileBtn = document.querySelector('.topbar-avatar');

  const profileDropdown = document.createElement('div');
  profileDropdown.id = 'profileDropdown';
  profileDropdown.innerHTML = `
    <div class="dropdown-header profile-header">
      <div class="profile-avatar-lg"><i class="fa-solid fa-user"></i></div>
      <div>
        <div class="dropdown-title">Admin User</div>
        <div class="profile-email">admin@koi.edu</div>
      </div>
    </div>
    <div class="profile-menu">
      <a href="#" class="profile-menu-item">
        <i class="fa-solid fa-user"></i> My Profile
      </a>
      <a href="#" class="profile-menu-item">
        <i class="fa-solid fa-gear"></i> Settings
      </a>
      <a href="#" class="profile-menu-item">
        <i class="fa-solid fa-shield-halved"></i> Security
      </a>
      <div class="profile-divider"></div>
      <a href="/logout" class="profile-menu-item profile-logout">
        <i class="fa-solid fa-right-from-bracket"></i> Sign Out
      </a>
    </div>
  `;
  profileDropdown.style.cssText = `
    display:none;position:fixed;top:72px;right:24px;
    width:240px;background:#fff;border-radius:12px;
    box-shadow:0 8px 40px rgba(0,0,0,0.15);
    border:1px solid #e2e8f0;z-index:9999;overflow:hidden;
  `;
  document.body.appendChild(profileDropdown);

  profileBtn?.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = profileDropdown.style.display === 'block';
    profileDropdown.style.display = isOpen ? 'none' : 'block';
    notifDropdown.style.display = 'none';
  });

  /* Close on outside click */
  document.addEventListener('click', () => {
    notifDropdown.style.display = 'none';
    profileDropdown.style.display = 'none';
  });

  /* ── Inject dropdown styles ── */
  const style = document.createElement('style');
  style.textContent = `
    @keyframes dropIn { from{opacity:0;transform:translateY(-8px)} to{opacity:1;transform:translateY(0)} }
    .dropdown-header {
      display:flex;align-items:center;justify-content:space-between;
      padding:16px 18px;border-bottom:1px solid #e2e8f0;
    }
    .dropdown-title { font-size:.9rem;font-weight:700;color:#0f172a; }
    .dropdown-badge {
      background:#ef4444;color:#fff;
      font-size:.68rem;font-weight:700;
      padding:2px 8px;border-radius:99px;
    }
    .notif-list { max-height:280px;overflow-y:auto; }
    .notif-item {
      display:flex;align-items:flex-start;gap:12px;
      padding:14px 18px;border-bottom:1px solid #f1f5f9;
      transition:background .15s;cursor:pointer;
    }
    .notif-item:hover { background:#f8fafc; }
    .notif-unread { background:#fafbff; }
    .notif-icon {
      width:34px;height:34px;border-radius:50%;
      display:flex;align-items:center;justify-content:center;
      font-size:13px;flex-shrink:0;
    }
    .notif-red    { background:#fee2e2;color:#ef4444; }
    .notif-blue   { background:#eff6ff;color:#2563eb; }
    .notif-orange { background:#fef3c7;color:#f59e0b; }
    .notif-green  { background:#dcfce7;color:#22c55e; }
    .notif-body { flex:1; }
    .notif-text { font-size:.82rem;font-weight:500;color:#0f172a;margin-bottom:3px; }
    .notif-time { font-size:.72rem;color:#94a3b8; }
    .dropdown-footer {
      padding:12px 18px;border-top:1px solid #e2e8f0;text-align:center;
    }
    .dropdown-footer a { font-size:.8rem;font-weight:600;color:#2563eb; }
    .profile-header { gap:12px; }
    .profile-avatar-lg {
      width:42px;height:42px;background:#1e3a8a;border-radius:50%;
      display:flex;align-items:center;justify-content:center;
      color:#fff;font-size:17px;flex-shrink:0;
    }
    .profile-email { font-size:.72rem;color:#94a3b8;margin-top:2px; }
    .profile-menu { padding:8px 0; }
    .profile-menu-item {
      display:flex;align-items:center;gap:10px;
      padding:10px 18px;font-size:.85rem;color:#475569;
      transition:background .15s;cursor:pointer;text-decoration:none;
    }
    .profile-menu-item:hover { background:#f8fafc;color:#0f172a; }
    .profile-menu-item i { width:16px;text-align:center;color:#94a3b8; }
    .profile-divider { height:1px;background:#e2e8f0;margin:4px 0; }
    .profile-logout { color:#ef4444 !important; }
    .profile-logout i { color:#ef4444 !important; }
    .profile-logout:hover { background:#fee2e2 !important; }
  `;
  document.head.appendChild(style);

});