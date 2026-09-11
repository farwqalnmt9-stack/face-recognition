(() => {
  const root = document.documentElement;
  const button = document.querySelector('[data-theme-toggle]');
  let dark = localStorage.getItem('kajo-theme') === 'dark';

  root.lang = 'ar';
  root.dir = 'rtl';

  const applyTheme = () => {
    root.classList.toggle('theme-dark', dark);
    root.dataset.theme = dark ? 'dark' : 'light';
    document.body.classList.toggle('dark', dark);
    button?.setAttribute('aria-label', dark ? 'تفعيل الوضع الفاتح' : 'تفعيل الوضع الداكن');
    localStorage.setItem('kajo-theme', dark ? 'dark' : 'light');
  };

  button?.addEventListener('click', () => {
    dark = !dark;
    applyTheme();
  });

  applyTheme();
})();
