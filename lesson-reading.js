/* Reading navigation and end-of-lesson completion stay outside teaching content. */
(() => {
  const index = document.querySelector('.lesson-index');
  const details = index?.querySelector('details');
  const compact = matchMedia('(max-width: 1199px)');

  function fitIndex() {
    if (details) details.open = !compact.matches;
  }

  function highlightSection(id) {
    index?.querySelectorAll('a').forEach(link => {
      if (link.hash === `#${id}`) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }

  index?.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      highlightSection(link.hash.slice(1));
      if (compact.matches) details.open = false;
    });
  });
  compact.addEventListener('change', fitIndex);
  fitIndex();

  if ('IntersectionObserver' in window) {
    const sections = new IntersectionObserver(entries => {
      entries.filter(entry => entry.isIntersecting).forEach(entry => highlightSection(entry.target.id));
    }, { rootMargin: '-12% 0px -65% 0px' });
    index?.querySelectorAll('a').forEach(link => {
      const heading = document.getElementById(link.hash.slice(1));
      if (heading) sections.observe(heading);
    });
  }

  const end = document.querySelector('[data-lesson-end]');
  const progress = window.CourseProgress;
  if (!end || !progress || progress.has(end.dataset.lessonEnd)) return;
  let reached = false;
  let recorded = false;
  let observer;

  function recordEnd() {
    if (recorded || !reached || document.visibilityState === 'hidden') return;
    recorded = true;
    progress.set(end.dataset.lessonEnd, true);
    observer?.disconnect();
    document.removeEventListener('visibilitychange', recordEnd);
  }

  document.addEventListener('visibilitychange', recordEnd);
  if ('IntersectionObserver' in window) {
    observer = new IntersectionObserver(entries => {
      reached = entries.some(entry => entry.isIntersecting);
      recordEnd();
    }, { rootMargin: '0px 0px -16px 0px', threshold: 1 });
    observer.observe(end);
  } else {
    const checkEnd = () => {
      const top = end.getBoundingClientRect().top;
      reached = top >= 0 && top < innerHeight - 16;
      recordEnd();
    };
    window.addEventListener('scroll', checkEnd, { passive: true });
    window.addEventListener('resize', checkEnd);
    checkEnd();
  }
})();
