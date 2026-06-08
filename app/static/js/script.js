/* CTI Protexion by Segark — interações da interface */
(() => {
  'use strict';

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const icon = (id) => `<svg class="icon" aria-hidden="true"><use href="#${id}"/></svg>`;

  /* Topbar: estado "scrolled" --------------------------------------------- */
  const topbar = $('#topbar');
  const onScroll = () => topbar && topbar.classList.toggle('scrolled', window.scrollY > 24);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* Navegação mobile ------------------------------------------------------ */
  const navToggle = $('#navToggle');
  const nav = $('#nav');
  if (navToggle && nav) {
    navToggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', String(open));
    });
    $$('.nav__link', nav).forEach((link) =>
      link.addEventListener('click', () => {
        nav.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
      })
    );
  }

  /* Contadores animados --------------------------------------------------- */
  const formatNum = (n) => n.toLocaleString('pt-BR');
  function animateCount(el) {
    const target = parseInt(el.dataset.count, 10) || 0;
    if (prefersReduced || target === 0) {
      el.textContent = formatNum(target);
      return;
    }
    const duration = 1200;
    let startTime = null;
    const step = (ts) => {
      if (startTime === null) startTime = ts;
      const p = Math.min((ts - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = formatNum(Math.floor(eased * target));
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = formatNum(target);
    };
    requestAnimationFrame(step);
  }

  const countObserver = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateCount(entry.target);
          obs.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.4 }
  );
  $$('[data-count]').forEach((el) => countObserver.observe(el));

  /* Reveal on scroll ------------------------------------------------------ */
  if (prefersReduced) {
    $$('.reveal').forEach((el) => el.classList.add('in-view'));
  } else {
    const revealObserver = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('in-view');
            obs.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );
    $$('.reveal').forEach((el) => revealObserver.observe(el));
  }

  /* Abas de código -------------------------------------------------------- */
  const tabs = $$('.code__tab');
  const panels = $$('.code__panel');
  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      const lang = tab.dataset.lang;
      tabs.forEach((t) => {
        const active = t === tab;
        t.classList.toggle('active', active);
        t.setAttribute('aria-selected', String(active));
      });
      panels.forEach((p) => p.classList.toggle('active', p.dataset.lang === lang));
    });
  });

  /* Botões de copiar ------------------------------------------------------ */
  $$('.copy-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const code = btn.parentElement.querySelector('pre code');
      if (!code) return;
      try {
        await navigator.clipboard.writeText(code.textContent.trim());
        const original = btn.textContent;
        btn.textContent = 'Copiado';
        btn.classList.add('copied');
        toast('Código copiado', 'ok');
        setTimeout(() => {
          btn.textContent = original;
          btn.classList.remove('copied');
        }, 1800);
      } catch (_) {
        toast('Não foi possível copiar', 'err');
      }
    });
  });

  /* Feed de URLs do honeypot --------------------------------------------- */
  const feedEl = $('#urlFeed');
  const countEl = $('#urlCount');

  function renderState(iconId, message) {
    if (feedEl) {
      feedEl.innerHTML = `<li class="url-feed__state">${icon(iconId)}<span>${message}</span></li>`;
    }
  }

  async function loadUrlFeed() {
    if (!feedEl) return;
    try {
      const res = await fetch('/honeypot-urls.txt', { headers: { Accept: 'text/plain' } });
      const text = await res.text();
      const urls = text.split('\n').map((l) => l.trim()).filter((l) => l && !l.startsWith('#'));

      if (urls.length === 0) {
        if (countEl) countEl.textContent = '0 URLs';
        renderState('i-inbox', 'Nenhuma URL maliciosa registrada no momento.');
        return;
      }

      const shown = urls.slice(0, 100);
      feedEl.innerHTML = shown
        .map((url, i) => `<li><span class="ix">${String(i + 1).padStart(2, '0')}</span><span>${escapeHtml(url)}</span></li>`)
        .join('');
      if (urls.length > shown.length) {
        const extra = urls.length - shown.length;
        feedEl.insertAdjacentHTML(
          'beforeend',
          `<li class="url-feed__state">${icon('i-download')}<span>+${formatNum(extra)} URLs na lista completa</span></li>`
        );
      }
      if (countEl) countEl.textContent = `${formatNum(urls.length)} URLs`;
    } catch (_) {
      if (countEl) countEl.textContent = 'indisponível';
      renderState('i-alert', 'Feed temporariamente indisponível. Tente novamente em instantes.');
    }
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  /* Status do serviço ----------------------------------------------------- */
  async function refreshStatus() {
    const textEl = $('#statusText');
    try {
      const res = await fetch('/status', { headers: { Accept: 'application/json' } });
      const data = await res.json();
      if (textEl) textEl.textContent = data.status === 'online' ? 'Operacional' : 'Degradado';
    } catch (_) {
      if (textEl) textEl.textContent = 'Sem conexão';
    }
  }

  /* Toast ----------------------------------------------------------------- */
  let toastTimer = null;
  function toast(message, kind = 'ok') {
    let el = $('#toast');
    if (!el) {
      el = document.createElement('div');
      el.id = 'toast';
      el.className = 'toast';
      document.body.appendChild(el);
    }
    const iconId = kind === 'err' ? 'i-alert' : 'i-check';
    el.className = `toast toast--${kind}`;
    el.innerHTML = `${icon(iconId)}<span></span>`;
    el.querySelector('span').textContent = message;
    requestAnimationFrame(() => el.classList.add('show'));
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove('show'), 2600);
  }

  /* Inicialização --------------------------------------------------------- */
  loadUrlFeed();
  refreshStatus();
  setInterval(refreshStatus, 60000);
  setInterval(loadUrlFeed, 300000);
})();
