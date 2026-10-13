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

  // 5. Interactive 3D Animated Hero Particle Mesh Network Canvas
  initHero3DCanvas();

  // 6. Interactive 3D Card Tilt on Mouse Move
  init3DTiltCards();

  // 7. Interactive Button and Card Click Ripple Waves
  initClickRipples();

  // 8. Interactive 3D Video Media Tour Modal & Animation Player
  initVideoPlayerModal();

  // 9. Interactive 3D Consultant Showcase Stage & Holographic Controller
  initConsultantStage3D();
});

/**
 * Interactive 3D Particle Mesh & Undulating Terrain Canvas Engine
 * Renders an interactive 3D particle constellation, 3D undulating wave surface grid, 
 * rotating polyhedral crystal wireframes, mouse magnetic well, and click shockwaves.
 */
function initHero3DCanvas() {
  const canvas = document.getElementById('hero3DCanvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width, height, centerX, centerY;
  let particles = [];
  let shockwaves = [];
  let animationFrameId = null;
  let isMotionActive = true;
  const numParticles = window.innerWidth < 768 ? 35 : 75;
  const fov = 380;
  let animTime = 0;

  const mouse = {
    x: null,
    y: null,
    isActive: false,
    radius: 180
  };

  function resizeCanvas() {
    const rect = canvas.parentElement.getBoundingClientRect();
    width = canvas.width = rect.width;
    height = canvas.height = rect.height;
    centerX = width / 2;
    centerY = height / 2;
  }

  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);

  class Particle3D {
    constructor() {
      this.reset();
    }

    reset() {
      this.x = (Math.random() - 0.5) * width * 1.5;
      this.y = (Math.random() - 0.5) * height * 1.4;
      this.z = Math.random() * 500 - 150;
      this.vx = (Math.random() - 0.5) * 0.75;
      this.vy = (Math.random() - 0.5) * 0.75;
      this.vz = (Math.random() - 0.5) * 0.5;
      this.radius = Math.random() * 2.2 + 1.2;
      this.baseColor = Math.random() > 0.4 ? '15, 157, 149' : '45, 212, 191'; // Teal or Cyan
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;
      this.z += this.vz;

      // Wrap around 3D boundaries
      if (this.z < -200) this.z = 350;
      if (this.z > 350) this.z = -200;
      if (Math.abs(this.x) > width) this.vx *= -1;
      if (Math.abs(this.y) > height) this.vy *= -1;

      // Mouse interactive gravitational pull
      if (mouse.isActive && mouse.x !== null) {
        const scale = fov / (fov + this.z);
        const screenX = centerX + this.x * scale;
        const screenY = centerY + this.y * scale;
        const dx = mouse.x - screenX;
        const dy = mouse.y - screenY;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < mouse.radius) {
          const force = (1 - dist / mouse.radius) * 0.55;
          this.vx += (dx / dist) * force;
          this.vy += (dy / dist) * force;
        }
      }

      // Shockwave impact
      for (let sw of shockwaves) {
        const scale = fov / (fov + this.z);
        const screenX = centerX + this.x * scale;
        const screenY = centerY + this.y * scale;
        const dx = screenX - sw.x;
        const dy = screenY - sw.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (Math.abs(dist - sw.radius) < 25) {
          const push = (1 - sw.radius / sw.maxRadius) * 4.5;
          this.vx += (dx / dist) * push;
          this.vy += (dy / dist) * push;
        }
      }

      // Drag friction
      this.vx *= 0.98;
      this.vy *= 0.98;
    }

    draw() {
      const scale = fov / (fov + this.z);
      if (scale <= 0) return;

      const screenX = centerX + this.x * scale;
      const screenY = centerY + this.y * scale;
      const alpha = Math.min(Math.max((this.z + 200) / 500, 0.15), 0.95);
      const renderRadius = Math.max(this.radius * scale, 0.8);

      ctx.beginPath();
      ctx.arc(screenX, screenY, renderRadius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${this.baseColor}, ${alpha})`;
      ctx.shadowBlur = renderRadius * 4;
      ctx.shadowColor = `rgba(${this.baseColor}, 0.8)`;
      ctx.fill();
      ctx.shadowBlur = 0;
    }
  }

  // 3D Polyhedron Crystal Wireframe
  class Crystal3D {
    constructor(baseX, baseY, baseZ, size, rotSpeed) {
      this.baseX = baseX;
      this.baseY = baseY;
      this.baseZ = baseZ;
      this.size = size;
      this.rotSpeed = rotSpeed;
      this.rx = Math.random() * Math.PI;
      this.ry = Math.random() * Math.PI;
      this.rz = Math.random() * Math.PI;
      // Octahedron vertices
      this.vertices = [
        { x: 0, y: -1, z: 0 },
        { x: 1, y: 0, z: 0 },
        { x: 0, y: 0, z: 1 },
        { x: -1, y: 0, z: 0 },
        { x: 0, y: 0, z: -1 },
        { x: 0, y: 1, z: 0 }
      ];
      this.edges = [
        [0, 1], [0, 2], [0, 3], [0, 4],
        [5, 1], [5, 2], [5, 3], [5, 4],
        [1, 2], [2, 3], [3, 4], [4, 1]
      ];
    }

    update() {
      this.rx += this.rotSpeed.x;
      this.ry += this.rotSpeed.y;
      this.rz += this.rotSpeed.z;
    }

    draw() {
      const scale = fov / (fov + this.baseZ);
      if (scale <= 0) return;

      const screenCenterX = centerX + this.baseX * scale;
      const screenCenterY = centerY + this.baseY * scale;

      // Project vertices with rotation
      const projected = this.vertices.map(v => {
        let x = v.x * this.size;
        let y = v.y * this.size;
        let z = v.z * this.size;

        // Rotation around X
        let y1 = y * Math.cos(this.rx) - z * Math.sin(this.rx);
        let z1 = y * Math.sin(this.rx) + z * Math.cos(this.rx);

        // Rotation around Y
        let x2 = x * Math.cos(this.ry) + z1 * Math.sin(this.ry);
        let z2 = -x * Math.sin(this.ry) + z1 * Math.cos(this.ry);

        // Rotation around Z
        let x3 = x2 * Math.cos(this.rz) - y1 * Math.sin(this.rz);
        let y3 = x2 * Math.sin(this.rz) + y1 * Math.cos(this.rz);

        return {
          x: screenCenterX + x3 * scale,
          y: screenCenterY + y3 * scale
        };
      });

      // Draw edges
      ctx.beginPath();
      for (let edge of this.edges) {
        const p1 = projected[edge[0]];
        const p2 = projected[edge[1]];
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
      }
      ctx.strokeStyle = 'rgba(45, 212, 191, 0.28)';
      ctx.lineWidth = 1.2;
      ctx.stroke();
    }
  }

  // Create initial particles
  for (let i = 0; i < numParticles; i++) {
    particles.push(new Particle3D());
  }

  // Create 3D Crystals
  const crystals = [
    new Crystal3D(-width * 0.38, -height * 0.25, 80, 48, { x: 0.008, y: 0.012, z: 0.006 }),
    new Crystal3D(width * 0.42, -height * 0.18, 120, 56, { x: -0.01, y: 0.009, z: -0.007 }),
    new Crystal3D(width * 0.32, height * 0.32, 50, 42, { x: 0.007, y: -0.011, z: 0.008 })
  ];

  // Mouse Move Event Listener (3D Tracking)
  const heroSection = canvas.parentElement;
  heroSection.addEventListener('mousemove', function (e) {
    const rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
    mouse.isActive = true;

    // Gentle 3D parallax on floating stat badges
    const parallaxBadges = document.querySelectorAll('.floating-stat-badge');
    const tiltX = (mouse.x / width - 0.5) * 16;
    const tiltY = (mouse.y / height - 0.5) * 16;
    parallaxBadges.forEach(badge => {
      badge.style.transform = `translate3d(${tiltX}px, ${tiltY}px, 0)`;
    });
  });

  heroSection.addEventListener('mouseleave', function () {
    mouse.isActive = false;
    mouse.x = null;
    mouse.y = null;
  });

  // Mouse Click Event Listener (3D Shockwave Ripple Wave)
  heroSection.addEventListener('click', function (e) {
    const rect = canvas.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;

    shockwaves.push({
      x: clickX,
      y: clickY,
      radius: 5,
      maxRadius: Math.min(width, height) * 0.65,
      speed: 7,
      alpha: 0.9
    });
  });

  // Render Undulating 3D Perspective Wave Grid
  function render3DWaveTerrain() {
    const gridCols = window.innerWidth < 768 ? 16 : 28;
    const gridRows = 10;
    const spacingX = (width * 1.4) / gridCols;
    const spacingZ = 45;
    const startX = -width * 0.7;
    const startZ = 20;
    const baseY = height * 0.65;

    const points = [];

    for (let r = 0; r < gridRows; r++) {
      points[r] = [];
      const z = startZ + r * spacingZ;
      const scale = fov / (fov + z);

      for (let c = 0; c <= gridCols; c++) {
        const x = startX + c * spacingX;

        // Wave elevation math
        let waveY = Math.sin(animTime * 0.0022 + c * 0.35 + r * 0.28) * 18 +
                    Math.cos(animTime * 0.0018 + r * 0.45) * 12;

        // Mouse interactive terrain elevation
        if (mouse.isActive && mouse.x !== null) {
          const screenX = centerX + x * scale;
          const screenY = centerY + (baseY + waveY - centerY) * scale;
          const mDist = Math.sqrt((mouse.x - screenX) ** 2 + (mouse.y - screenY) ** 2);
          if (mDist < 160) {
            waveY += (1 - mDist / 160) * 28;
          }
        }

        const projX = centerX + x * scale;
        const projY = centerY + (baseY + waveY - centerY) * scale;

        points[r][c] = { x: projX, y: projY, alpha: (1 - r / gridRows) * 0.22 };
      }
    }

    // Draw horizontal grid wave lines
    for (let r = 0; r < gridRows; r++) {
      ctx.beginPath();
      ctx.moveTo(points[r][0].x, points[r][0].y);
      for (let c = 1; c <= gridCols; c++) {
        ctx.lineTo(points[r][c].x, points[r][c].y);
      }
      ctx.strokeStyle = `rgba(15, 157, 149, ${points[r][0].alpha})`;
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // Draw connecting longitudinal perspective lines
    for (let c = 0; c <= gridCols; c += 2) {
      ctx.beginPath();
      ctx.moveTo(points[0][c].x, points[0][c].y);
      for (let r = 1; r < gridRows; r++) {
        ctx.lineTo(points[r][c].x, points[r][c].y);
      }
      ctx.strokeStyle = 'rgba(45, 212, 191, 0.1)';
      ctx.lineWidth = 0.8;
      ctx.stroke();
    }
  }

  // Animation Loop (60 FPS)
  function render(timestamp) {
    if (!isMotionActive) return;

    animTime = timestamp || 0;
    ctx.clearRect(0, 0, width, height);

    // 1. Render 3D undulating terrain surface mesh
    render3DWaveTerrain();

    // 2. Render 3D rotating crystals
    for (let crystal of crystals) {
      crystal.update();
      crystal.draw();
    }

    // 3. Update and draw shockwaves
    for (let i = shockwaves.length - 1; i >= 0; i--) {
      const sw = shockwaves[i];
      sw.radius += sw.speed;
      sw.alpha = 1 - sw.radius / sw.maxRadius;

      if (sw.radius >= sw.maxRadius || sw.alpha <= 0) {
        shockwaves.splice(i, 1);
        continue;
      }

      ctx.beginPath();
      ctx.arc(sw.x, sw.y, sw.radius, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(45, 212, 191, ${sw.alpha * 0.8})`;
      ctx.lineWidth = 2.5;
      ctx.stroke();
    }

    // 4. Update particles
    for (let p of particles) {
      p.update();
      p.draw();
    }

    // 5. Draw connecting 3D constellation lines
    const maxDist = 135;
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const p1 = particles[i];
        const p2 = particles[j];

        const scale1 = fov / (fov + p1.z);
        const scale2 = fov / (fov + p2.z);

        const x1 = centerX + p1.x * scale1;
        const y1 = centerY + p1.y * scale1;
        const x2 = centerX + p2.x * scale2;
        const y2 = centerY + p2.y * scale2;

        const dx = x1 - x2;
        const dy = y1 - y2;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < maxDist) {
          const lineAlpha = (1 - dist / maxDist) * 0.35 * Math.min(scale1, scale2);
          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.lineTo(x2, y2);
          ctx.strokeStyle = `rgba(15, 157, 149, ${lineAlpha})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }
    }

    animationFrameId = requestAnimationFrame(render);
  }

  render();

  // Performance Optimization: Pause rendering when scrolled out of view
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          if (!isMotionActive) {
            isMotionActive = true;
            render();
          }
        } else {
          isMotionActive = false;
          if (animationFrameId) cancelAnimationFrame(animationFrameId);
        }
      });
    }, { threshold: 0.1 });
    observer.observe(heroSection);
  }

  // Interactive toggle button for 3D motion
  const toggleBtn = document.getElementById('toggle3DMotionBtn');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', function () {
      isMotionActive = !isMotionActive;
      if (isMotionActive) {
        toggleBtn.innerHTML = '<i class="bi bi-pause-circle me-1"></i> Pause 3D Mesh';
        toggleBtn.classList.add('active');
        render();
      } else {
        toggleBtn.innerHTML = '<i class="bi bi-play-circle me-1"></i> Resume 3D Mesh';
        toggleBtn.classList.remove('active');
        ctx.clearRect(0, 0, width, height);
      }
    });
  }
}

/**
 * 3D Tilt Micro-Interactions on Cards (Moving & Looking Style)
 * Calculates cursor coordinates relative to card center and smoothly applies 3D perspective rotation.
 */
function init3DTiltCards() {
  const cards = document.querySelectorAll('.tilt-card-3d, .job-card, .card-custom');
  if (!cards.length) return;

  // Add glare element if missing
  cards.forEach(card => {
    card.classList.add('tilt-card-3d');
    if (!card.querySelector('.tilt-glare-effect')) {
      const glare = document.createElement('div');
      glare.className = 'tilt-glare-effect';
      card.appendChild(glare);
    }

    card.addEventListener('mousemove', function (e) {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      // Limit tilt to +/- 8 degrees for elegant, restrained 3D look
      const rotateX = ((centerY - y) / centerY) * 7;
      const rotateY = ((x - centerX) / centerX) * 7;

      card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) scale3d(1.018, 1.018, 1.018)`;

      // Set glare coordinates for dynamic lighting reflection
      card.style.setProperty('--glare-x', `${((x / rect.width) * 100).toFixed(1)}%`);
      card.style.setProperty('--glare-y', `${((y / rect.height) * 100).toFixed(1)}%`);
    });

    card.addEventListener('mouseleave', function () {
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
    });
  });
}

/**
 * Interactive Ripple Waves on Button & Card Clicks
 */
function initClickRipples() {
  const rippleTargets = document.querySelectorAll('.btn, .job-card, .floating-stat-badge');

  rippleTargets.forEach(target => {
    target.classList.add('btn-ripple-container');
    target.addEventListener('click', function (e) {
      const rect = target.getBoundingClientRect();
      const ripple = document.createElement('span');
      ripple.className = 'ripple-circle';

      const diameter = Math.max(rect.width, rect.height);
      const radius = diameter / 2;

      ripple.style.width = ripple.style.height = `${diameter}px`;
      ripple.style.left = `${e.clientX - rect.left - radius}px`;
      ripple.style.top = `${e.clientY - rect.top - radius}px`;

      if (target.classList.contains('btn-outline-custom') || target.classList.contains('job-card')) {
        ripple.classList.add('ripple-teal');
      }

      const existingRipple = target.querySelector('.ripple-circle');
      if (existingRipple) {
        existingRipple.remove();
      }

      target.appendChild(ripple);

      setTimeout(() => {
        ripple.remove();
      }, 650);
    });
  });
}

/**
 * Interactive 3D Video Media Tour Modal & Animation Player
 * Renders an animated high-performance 3D corporate showcase with rotating HUD, audio visualizer,
 * dynamic scenario milestones, progress scrubber, and interactive playback controls.
 */
function initVideoPlayerModal() {
  const modalEl = document.getElementById('corporateVideoModal');
  const launchTriggers = document.querySelectorAll('.video-player-preview-card, #launchVideoTourBtn');
  if (!modalEl || !launchTriggers.length) return;

  const canvas = document.getElementById('videoSimCanvas');
  const playPauseBtn = document.getElementById('modalVideoPlayPauseBtn');
  const progressFill = document.getElementById('modalVideoProgressFill');
  const progressBar = document.getElementById('modalVideoProgressBar');
  const timerText = document.getElementById('modalVideoTimer');
  const soundBtn = document.getElementById('modalVideoSoundBtn');

  let ctx = canvas ? canvas.getContext('2d') : null;
  let isPlaying = true;
  let isSoundActive = true;
  let animId = null;
  let currentSecond = 0;
  const totalSeconds = 150; // 2 mins 30s
  let lastTimestamp = 0;
  let rotationAngle = 0;

  const milestones = [
    { start: 0, end: 30, title: "HALCON CAREER • Mohali Headquarters", subtitle: "Connecting High-Caliber Talent Across Tricity & Beyond" },
    { start: 30, end: 60, title: "Rigorous 3-Stage Screening Matrix", subtitle: "98.4% Role Calibration & Verified Credentials" },
    { start: 60, end: 95, title: "Executive Search & Board Advisory", subtitle: "Discreet Leadership Placement for Emerging & Enterprise Brands" },
    { start: 95, end: 125, title: "Pan-India Workforce Sourcing Corridor", subtitle: "Bridging 50+ Cities with Rapid 48-Hour Shortlists" },
    { start: 125, end: 151, title: "Ethical & Candidate-Centric Mission", subtitle: "Zero Hidden Fees, Complete Candidate Transparency" }
  ];

  function formatTime(sec) {
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }

  function resizeSimCanvas() {
    if (!canvas) return;
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
  }

  // Animation render loop
  function renderVideoScene(timestamp) {
    if (!isPlaying || !ctx) return;

    if (!lastTimestamp) lastTimestamp = timestamp;
    const delta = (timestamp - lastTimestamp) / 1000;
    lastTimestamp = timestamp;

    currentSecond += delta;
    if (currentSecond >= totalSeconds) currentSecond = 0;

    // Update progress bar
    if (progressFill) {
      progressFill.style.width = `${(currentSecond / totalSeconds) * 100}%`;
    }
    if (timerText) {
      timerText.textContent = `${formatTime(currentSecond)} / ${formatTime(totalSeconds)}`;
    }

    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    // Deep space gradient backdrop
    const grad = ctx.createLinearGradient(0, 0, w, h);
    grad.addColorStop(0, '#060E18');
    grad.addColorStop(0.5, '#0B1B2F');
    grad.addColorStop(1, '#08212D');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    // Subtle 3D perspective grid
    ctx.strokeStyle = 'rgba(15, 157, 149, 0.12)';
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 40) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += 40) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    rotationAngle += 0.015;

    // 3D Rotating Rings & Sphere Center
    const cx = w / 2;
    const cy = h / 2 - 25;
    const radius = Math.min(w, h) * 0.28;

    // Ring 1 (Horizontal tilt)
    ctx.beginPath();
    ctx.ellipse(cx, cy, radius, radius * Math.abs(Math.sin(rotationAngle)), rotationAngle, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(45, 212, 191, 0.6)';
    ctx.lineWidth = 2.5;
    ctx.stroke();

    // Ring 2 (Vertical tilt)
    ctx.beginPath();
    ctx.ellipse(cx, cy, radius * 1.15, radius * 1.15 * Math.abs(Math.cos(rotationAngle)), -rotationAngle, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(15, 157, 149, 0.4)';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Core Glowing Sphere
    const coreGrad = ctx.createRadialGradient(cx, cy, 10, cx, cy, radius * 0.5);
    coreGrad.addColorStop(0, 'rgba(45, 212, 191, 0.85)');
    coreGrad.addColorStop(0.5, 'rgba(15, 157, 149, 0.4)');
    coreGrad.addColorStop(1, 'transparent');
    ctx.fillStyle = coreGrad;
    ctx.beginPath();
    ctx.arc(cx, cy, radius * 0.5, 0, Math.PI * 2);
    ctx.fill();

    // Central Brand Stamp
    ctx.font = 'bold 16px Inter, sans-serif';
    ctx.fillStyle = '#FFFFFF';
    ctx.textAlign = 'center';
    ctx.fillText('HALCON CAREER', cx, cy - 5);
    ctx.font = '12px Inter, sans-serif';
    ctx.fillStyle = '#2DD4BF';
    ctx.fillText('3D TOUR • LIVE', cx, cy + 18);

    // Audio Visualizer Waveform at the Bottom
    const numBars = 36;
    const barWidth = 6;
    const startX = cx - (numBars * 10) / 2;
    for (let i = 0; i < numBars; i++) {
      const freq = isSoundActive ? Math.sin(timestamp * 0.008 + i * 0.4) * 0.5 + 0.5 : 0.08;
      const barHeight = Math.max(8, freq * 48);
      const bx = startX + i * 10;
      const by = h - 60 - barHeight;

      const barGrad = ctx.createLinearGradient(0, by, 0, by + barHeight);
      barGrad.addColorStop(0, '#2DD4BF');
      barGrad.addColorStop(1, '#0F9D95');
      ctx.fillStyle = barGrad;
      ctx.fillRect(bx, by, barWidth, barHeight);
    }

    // Dynamic Cinematic Subtitles
    const currentMilestone = milestones.find(m => currentSecond >= m.start && currentSecond < m.end) || milestones[0];
    ctx.textAlign = 'center';
    ctx.font = 'bold 20px Inter, sans-serif';
    ctx.fillStyle = '#FFFFFF';
    ctx.fillText(currentMilestone.title, cx, h - 90);

    ctx.font = '13px Inter, sans-serif';
    ctx.fillStyle = '#94A3B8';
    ctx.fillText(currentMilestone.subtitle, cx, h - 70);

    animId = requestAnimationFrame(renderVideoScene);
  }

  // Trigger modal display
  launchTriggers.forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        const bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
        bsModal.show();
      }
    });
  });

  // Modal events
  modalEl.addEventListener('shown.bs.modal', function () {
    resizeSimCanvas();
    isPlaying = true;
    lastTimestamp = 0;
    if (playPauseBtn) playPauseBtn.innerHTML = '<i class="bi bi-pause-fill"></i>';
    animId = requestAnimationFrame(renderVideoScene);
  });

  modalEl.addEventListener('hidden.bs.modal', function () {
    isPlaying = false;
    if (animId) cancelAnimationFrame(animId);
  });

  // Play / Pause controls
  if (playPauseBtn) {
    playPauseBtn.addEventListener('click', function () {
      isPlaying = !isPlaying;
      if (isPlaying) {
        playPauseBtn.innerHTML = '<i class="bi bi-pause-fill"></i>';
        lastTimestamp = 0;
        animId = requestAnimationFrame(renderVideoScene);
      } else {
        playPauseBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
        if (animId) cancelAnimationFrame(animId);
      }
    });
  }

  // Audio mute/unmute
  if (soundBtn) {
    soundBtn.addEventListener('click', function () {
      isSoundActive = !isSoundActive;
      if (isSoundActive) {
        soundBtn.innerHTML = '<i class="bi bi-volume-up-fill"></i>';
        soundBtn.classList.remove('text-secondary');
        soundBtn.classList.add('text-teal');
      } else {
        soundBtn.innerHTML = '<i class="bi bi-volume-mute-fill"></i>';
        soundBtn.classList.add('text-secondary');
        soundBtn.classList.remove('text-teal');
      }
    });
  }

  // Progress bar scrubbing
  if (progressBar) {
    progressBar.addEventListener('click', function (e) {
      const rect = progressBar.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const ratio = Math.max(0, Math.min(1, clickX / rect.width));
      currentSecond = ratio * totalSeconds;
    });
  }

  window.addEventListener('resize', resizeSimCanvas);
}

/**
 * Interactive 3D Consultant Showcase Stage & Holographic Controller
 * Manages 3D multi-plane perspective tilt on cursor movement, 3D consultant slides,
 * autoplay timer, dot controls, and holographic depth interactions.
 */
function initConsultantStage3D() {
  const wrapper = document.querySelector('.consultant-3d-stage-wrapper');
  const videoStage = document.getElementById('stageVideoContainer');
  const consultantsStage = document.getElementById('stageConsultantsContainer');
  const consultantControls = document.getElementById('stageConsultantControls');
  const tabVideo = document.getElementById('tabVideoMode');
  const tabConsultants = document.getElementById('tabConsultantsMode');
  const modeStatusBadge = document.getElementById('modeStatusBadge');

  const slides = document.querySelectorAll('#stageConsultantsContainer .consultant-3d-slide');
  const dots = document.querySelectorAll('#stageConsultantControls .stage-dot');
  const nextBtn = document.getElementById('stageNextBtn');
  const prevBtn = document.getElementById('stagePrevBtn');
  const autoplayBtn = document.getElementById('stageAutoplayBtn');

  // Video Autoplay Guardian for all looping reels
  const loopVideos = document.querySelectorAll('.consultant-reel-video, .video-preview-reel');
  function ensureVideosPlaying() {
    loopVideos.forEach(v => {
      if (v) {
        v.muted = true;
        const playPromise = v.play();
        if (playPromise !== undefined) {
          playPromise.catch(() => {
            // Autoplay will resume on next user interaction
          });
        }
      }
    });
  }

  ensureVideosPlaying();
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) ensureVideosPlaying();
  });
  window.addEventListener('click', ensureVideosPlaying, { once: true });

  // Mode Switcher Tabs
  if (tabVideo && tabConsultants && videoStage && consultantsStage) {
    tabVideo.addEventListener('click', function () {
      tabVideo.classList.add('active');
      tabConsultants.classList.remove('active');
      videoStage.classList.remove('d-none');
      consultantsStage.classList.add('d-none');
      if (consultantControls) consultantControls.classList.add('d-none');
      if (modeStatusBadge) {
        modeStatusBadge.innerHTML = '<span class="live-dot-pulse"></span> CONTINUOUS REEL';
      }
      ensureVideosPlaying();
    });

    tabConsultants.addEventListener('click', function () {
      tabConsultants.classList.add('active');
      tabVideo.classList.remove('active');
      consultantsStage.classList.remove('d-none');
      videoStage.classList.add('d-none');
      if (consultantControls) consultantControls.classList.remove('d-none');
      if (modeStatusBadge) {
        modeStatusBadge.innerHTML = '<span class="live-dot-pulse" style="background-color: #2DD4BF;"></span> 4 CONSULTANTS';
      }
    });
  }

  // Consultant Slide Controller
  let currentIdx = 0;
  let isAutoplay = true;
  let autoplayTimer = null;

  function showSlide(index) {
    if (!slides.length) return;
    if (index < 0) index = slides.length - 1;
    if (index >= slides.length) index = 0;
    currentIdx = index;

    slides.forEach((s, i) => {
      s.classList.toggle('active', i === currentIdx);
    });

    dots.forEach((d, i) => {
      d.classList.toggle('active', i === currentIdx);
    });
  }

  function nextSlide() {
    showSlide(currentIdx + 1);
  }

  function prevSlide() {
    showSlide(currentIdx - 1);
  }

  if (nextBtn) nextBtn.addEventListener('click', nextSlide);
  if (prevBtn) prevBtn.addEventListener('click', prevSlide);

  dots.forEach(dot => {
    dot.addEventListener('click', function () {
      const idx = parseInt(this.getAttribute('data-index'), 10);
      if (!isNaN(idx)) showSlide(idx);
    });
  });

  // Autoplay loop for consultant slides
  function startAutoplay() {
    if (autoplayTimer) clearInterval(autoplayTimer);
    autoplayTimer = setInterval(() => {
      if (isAutoplay && consultantsStage && !consultantsStage.classList.contains('d-none')) {
        nextSlide();
      }
    }, 4500);
  }

  startAutoplay();

  if (autoplayBtn) {
    autoplayBtn.addEventListener('click', function () {
      isAutoplay = !isAutoplay;
      this.classList.toggle('active', isAutoplay);
      this.innerHTML = isAutoplay 
        ? '<i class="bi bi-arrow-repeat me-1"></i> Auto 3D' 
        : '<i class="bi bi-pause-circle me-1"></i> Paused';
    });
  }

  // Mouse hover & 3D Perspective Tilt on Mouse Movement
  if (wrapper) {
    wrapper.addEventListener('mouseenter', () => { isAutoplay = false; });
    wrapper.addEventListener('mouseleave', () => { 
      if (autoplayBtn && autoplayBtn.classList.contains('active')) {
        isAutoplay = true; 
      }
    });

    wrapper.addEventListener('mousemove', function (e) {
      const rect = wrapper.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;

      // Restrained elegant rotation (+/- 14 deg on Y, +/- 12 deg on X)
      const rotY = (x / (rect.width / 2)) * 14;
      const rotX = -(y / (rect.height / 2)) * 12;

      const activeStage = videoStage && !videoStage.classList.contains('d-none') ? videoStage : consultantsStage;
      if (activeStage) {
        activeStage.style.transform = `rotateX(${rotX.toFixed(2)}deg) rotateY(${rotY.toFixed(2)}deg) scale3d(1.025, 1.025, 1.025)`;
      }
    });

    wrapper.addEventListener('mouseleave', function () {
      if (videoStage) videoStage.style.transform = 'rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
      if (consultantsStage) consultantsStage.style.transform = 'rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
    });
  }
}




