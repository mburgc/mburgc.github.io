/* Panel de margen: previsualización al pasar el cursor o enfocar.
   Sin dependencias. El contenido vive en un <script type="application/json">. */

(function () {
  'use strict';

  var dataEl = document.getElementById('previews');
  var panel = document.getElementById('margin-panel');
  var body = document.getElementById('margin-body');
  var idle = document.getElementById('margin-idle');
  var label = document.getElementById('margin-label-text');
  var sheet = document.getElementById('sheet');
  var sheetBody = document.getElementById('sheet-body');

  if (!dataEl || !panel) return;

  var PREVIEWS = {};
  try { PREVIEWS = JSON.parse(dataEl.textContent || '{}'); } catch (e) { return; }

  var labels = {
    now: panel.dataset.labelNow || 'Now',
    preview: panel.dataset.labelPreview || 'Preview',
    close: panel.dataset.labelClose || 'Close'
  };

  var canHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var current = null;
  var hideTimer = null;

  function esc(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  /* Los bullets del CV traen <b> deliberado; se permiten solo esas etiquetas. */
  function allowBold(html) {
    return String(html || '')
      .replace(/<(?!\/?b>)[^>]*>/gi, '')
      .replace(/&(?!(amp|lt|gt|quot|#\d+);)/g, '&amp;');
  }

  function render(item) {
    var html = '';
    html += '<h3 class="margin-title">' + esc(item.title) + '</h3>';
    if (item.meta) html += '<p class="margin-meta">' + esc(item.meta) + '</p>';

    if (item.bullets && item.bullets.length) {
      html += '<ul class="margin-list">';
      item.bullets.forEach(function (b) {
        html += '<li>' + allowBold(b) + '</li>';
      });
      html += '</ul>';
    } else if (item.text) {
      html += '<p class="margin-text">' + esc(item.text) + '</p>';
    }

    if (item.video) {
      html += '<a class="poster" href="' + esc(item.link ? item.link.href : '#') + '" data-video="' + esc(item.video) + '" target="_blank" rel="noopener">'
        + '<img src="https://i.ytimg.com/vi/' + esc(item.video) + '/hqdefault.jpg" alt="" loading="lazy" decoding="async">'
        + '<span class="poster-play"><span>&#9654;</span></span></a>';
    }

    if (item.link) {
      html += '<a class="margin-link" href="' + esc(item.link.href) + '">' + esc(item.link.label) + ' &rarr;</a>';
    }
    return html;
  }

  function show(id) {
    var item = PREVIEWS[id];
    if (!item || !body) return;
    window.clearTimeout(hideTimer);
    current = id;

    body.innerHTML = render(item);
    body.hidden = false;
    if (idle) idle.hidden = true;
    if (label) label.textContent = labels.preview;

    /* reinicia la animación de entrada */
    body.style.animation = 'none';
    void body.offsetWidth;
    body.style.animation = '';

    panel.classList.add('is-active');
    panel.setAttribute('data-state', id);
  }

  function showIdle() {
    current = null;
    if (body) { body.hidden = true; body.innerHTML = ''; }
    if (idle) idle.hidden = false;
    if (label) label.textContent = labels.now;
    panel.classList.remove('is-active');
    panel.removeAttribute('data-state');
  }

  function scheduleIdle() {
    window.clearTimeout(hideTimer);
    hideTimer = window.setTimeout(function () {
      if (!panel.contains(document.activeElement)) showIdle();
    }, 160);
  }

  /* ── Interacción de escritorio ─────────────────────────── */
  if (canHover && body) {
    document.querySelectorAll('[data-preview]').forEach(function (el) {
      var id = el.getAttribute('data-preview');

      el.addEventListener('mouseenter', function () { show(id); });
      el.addEventListener('mouseleave', scheduleIdle);

      el.addEventListener('focusin', function () { show(id); });
      el.addEventListener('focusout', function () {
        window.setTimeout(function () {
          if (!el.contains(document.activeElement)) scheduleIdle();
        }, 0);
      });
    });

    panel.addEventListener('mouseenter', function () { window.clearTimeout(hideTimer); });
    panel.addEventListener('mouseleave', scheduleIdle);
    panel.addEventListener('focusout', scheduleIdle);
  }

  /* ── Hoja inferior (móvil / teclado) ───────────────────── */
  function openSheet(id) {
    if (!sheet || !sheetBody) return;
    var item = PREVIEWS[id];
    if (!item) return;
    sheetBody.innerHTML = render(item);
    if (typeof sheet.showModal === 'function') sheet.showModal();
    else sheet.setAttribute('open', '');
  }

  document.querySelectorAll('[data-peek]').forEach(function (btn) {
    btn.addEventListener('click', function (event) {
      event.preventDefault();
      event.stopPropagation();
      openSheet(btn.getAttribute('data-peek'));
    });
  });

  if (sheet) {
    var closeBtn = sheet.querySelector('.sheet-close');
    if (closeBtn) closeBtn.addEventListener('click', function () { sheet.close(); });
    sheet.addEventListener('click', function (event) {
      if (event.target === sheet) sheet.close();
    });
  }

  /* ── Video diferido: el iframe entra recién al hacer click ── */
  document.addEventListener('click', function (event) {
    var poster = event.target.closest('.poster[data-video]');
    if (!poster) return;
    event.preventDefault();
    var id = poster.getAttribute('data-video');
    var frame = document.createElement('iframe');
    frame.src = 'https://www.youtube.com/embed/' + encodeURIComponent(id) + '?autoplay=1&rel=0';
    frame.title = 'YouTube';
    frame.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; picture-in-picture';
    frame.allowFullscreen = true;
    frame.loading = 'lazy';
    frame.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;border:0';
    poster.innerHTML = '';
    poster.appendChild(frame);
    poster.removeAttribute('href');
  });

  showIdle();
})();
