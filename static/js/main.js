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
});

/**
 * Interactive 3D Particle Mesh Canvas Engine
 * Recreates high-end 8K futuristic recruitment network visualization with mouse attraction and click shockwaves.
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
  const numParticles = window.innerWidth < 768 ? 40 : 85;
  const fov = 350;

  const mouse = {
    x: null,
    y: null,
    isActive: false,
    radius: 160
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
      this.y = (Math.random() - 0.5) * height * 1.5;
      this.z = Math.random() * 500 - 150;
      this.vx = (Math.random() - 0.5) * 0.8;
      this.vy = (Math.random() - 0.5) * 0.8;
      this.vz = (Math.random() - 0.5) * 0.6;
      this.radius = Math.random() * 2.2 + 1.2;
      this.baseColor = Math.random() > 0.4 ? '15, 157, 149' : '77, 208, 225'; // Teal or Cyan
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
          const force = (1 - dist / mouse.radius) * 0.5;
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
          const push = (1 - sw.radius / sw.maxRadius) * 4;
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
      ctx.shadowBlur = 0; // reset
    }
  }

  // Create initial particles
  for (let i = 0; i < numParticles; i++) {
    particles.push(new Particle3D());
  }

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
      maxRadius: Math.min(width, height) * 0.6,
      speed: 7,
      alpha: 0.9
    });
  });

  // Animation Loop (60 FPS)
  function render() {
    if (!isMotionActive) return;

    ctx.clearRect(0, 0, width, height);

    // Update and draw shockwaves
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
      ctx.strokeStyle = `rgba(15, 157, 149, ${sw.alpha * 0.7})`;
      ctx.lineWidth = 2.5;
      ctx.stroke();
    }

    // Update particles
    for (let p of particles) {
      p.update();
      p.draw();
    }

    // Draw connecting 3D constellation lines
    const maxDist = 130;
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



