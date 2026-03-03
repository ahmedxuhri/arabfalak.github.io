/* === TOC ACTIVE HIGHLIGHT === */
(function() {
  const toc = document.querySelector('.toc');
  if (!toc) return;
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        if (!id) return;
        
        document.querySelectorAll('.toc a').forEach(link => {
          link.classList.remove('active');
        });
        
        const activeLink = document.querySelector(`.toc a[href="#${id}"]`);
        if (activeLink) {
          activeLink.classList.add('active');
        }
      }
    });
  }, { rootMargin: '-50% 0px -50% 0px' });
  
  document.querySelectorAll('.post-content h2, .post-content h3').forEach(heading => {
    if (heading.id) observer.observe(heading);
  });
})();

/* === FAQ ACCORDION SMOOTH HEIGHT === */
(function() {
  document.querySelectorAll('details').forEach(details => {
    const summary = details.querySelector('summary');
    if (!summary) return;
    
    summary.addEventListener('click', () => {
      if (!details.hasAttribute('open')) {
        const allDetails = document.querySelectorAll('details[open]');
        allDetails.forEach(d => d.removeAttribute('open'));
      }
    });
  });
})();

/* === SMOOTH SCROLL FOR ANCHOR LINKS === */
(function() {
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href === '#') return;
      
      const target = document.querySelector(href);
      if (!target) return;
      
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    });
  });
})();

/* === MOBILE NAV TOGGLE === */
(function() {
  const navToggle = document.querySelector('.nav-toggle');
  const siteNav = document.querySelector('.site-nav');
  
  if (!navToggle || !siteNav) return;
  
  navToggle.addEventListener('click', () => {
    siteNav.classList.toggle('active');
  });
  
  document.querySelectorAll('.site-nav a').forEach(link => {
    link.addEventListener('click', () => {
      siteNav.classList.remove('active');
    });
  });
})();

/* === LAZY LOAD IMAGES === */
(function() {
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
          }
          imageObserver.unobserve(img);
        }
      });
    }, {
      rootMargin: '50px'
    });
    
    document.querySelectorAll('img[data-src]').forEach(img => {
      imageObserver.observe(img);
    });
  }
})();
