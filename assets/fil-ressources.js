/* La barre « mazeo / Ressources / <la ressource> » en haut de chaque ressource (23/10/2026).
   Chaque page l'appelle par une ligne posée juste après <body> :
     <script src="/assets/fil-ressources.js"></script>
   Elle se pose avant le reste de la page (aucun saut à l'affichage), suit la langue de la page
   (y compris quand la page change de langue sans recharger) et s'aligne sur l'en-tête de la page.
   Elle pose aussi --fil-h sur <html> : une page calée sur la hauteur de l'écran peut la retrancher. */
(function () {
  var moi = document.currentScript;
  if (!moi || !moi.parentNode || document.querySelector('.fil-mz')) return;

  var chemin = location.pathname.replace(/\.html$/, '').replace(/\/+$/, '') || '/';
  var ACADEMY = ['La growth academy', 'The growth academy'];
  var RESSOURCES = [
    { re: /^\/(en\/)?academy$/, fam: ['prospecter', 'prospecting'], nom: ACADEMY },
    { re: /^\/positionnement$|^\/en\/positioning$/, fam: ['prospecter', 'prospecting'], nom: ACADEMY,
      accueil: ['/academy', '/en/academy'], sous: ['Fiche 1 : votre positionnement', 'Guide 1: your positioning'] },
    { re: /^\/votre-profil-linkedin$/, fam: ['prospecter', 'prospecting'], nom: ACADEMY,
      accueil: ['/academy', '/en/academy'], sous: ['Fiche 4 : votre profil LinkedIn', 'Guide 4: your LinkedIn profile'] },
    { re: /^\/prise-de-rendez-vous$|^\/en\/booking-link$/, fam: ['prospecter', 'prospecting'], nom: ACADEMY,
      accueil: ['/academy', '/en/academy'], sous: ['Fiche 5 : votre lien de rendez-vous', 'Guide 5: your booking link'] },
    { re: /^\/village-des-etudes$|^\/en\/market-research-in-figures$/, fam: ['secteur', 'industry'],
      nom: ['Le Village des études', 'Le Village des études'] },
    { re: /^\/pitch-des-etudes$|^\/en\/market-research-positioning$/, fam: ['secteur', 'industry'],
      nom: ['Le Pitch des études', 'Le Pitch des études'] },
    { re: /^\/quiz$|^\/en\/quiz$/, fam: ['secteur', 'industry'],
      nom: ['Le Grand Quiz des Études', 'The Great Market Research Quiz'] },
    { re: /^\/salons$|^\/en\/market-research-conferences$/, fam: ['opportunites', 'opportunities'],
      nom: ['Les rencontres du market research', 'Market research events'] },
    { re: /^\/salons\/.+|^\/en\/market-research-conferences\/.+/, fam: ['opportunites', 'opportunities'],
      nom: ['Les rencontres du market research', 'Market research events'],
      accueil: ['/salons', '/en/market-research-conferences'] },
    { re: /^\/appels-offres$|^\/en\/public-tenders$/, fam: ['opportunites', 'opportunities'],
      nom: ['Dernier appel', 'Dernier appel'] },
    { re: /^\/bourse-emploi$|^\/en\/insight-jobs$/, fam: ['opportunites', 'opportunities'],
      nom: ["La Bourse de l'emploi insight", 'The insight job board'] }
  ];
  var r = null;
  for (var i = 0; i < RESSOURCES.length; i++) if (RESSOURCES[i].re.test(chemin)) { r = RESSOURCES[i]; break; }
  if (!r) return;

  var T = {
    ressources: ['Ressources', 'Resources'], toutes: ['Toutes les ressources', 'All resources'],
    page: ['/ressources', '/en/resources'], accueil: ['/', '/?lang=en'], aria: ["Fil d'Ariane", 'Breadcrumb']
  };

  var css = document.createElement('style');
  css.textContent =
    '.fil-mz{position:relative;z-index:40;background:#F8F9FA;border-bottom:1px solid #E5E7EB;' +
      "font:500 14px/1 'Hanken Grotesk',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;-webkit-font-smoothing:antialiased}" +
    '.fil-mz .fil-in{box-sizing:border-box;height:40px;display:flex;align-items:center;gap:10px;padding:0 32px;color:#6B7280;white-space:nowrap;min-width:0}' +
    '.fil-mz a{color:#3A4250;text-decoration:none;font-weight:600}' +
    '.fil-mz a:hover{color:#0A0A0A;text-decoration:underline;text-underline-offset:3px}' +
    ".fil-mz .fil-logo{font:800 17px/1 Inter,'Hanken Grotesk',-apple-system,sans-serif;letter-spacing:-.4px;color:#0A0A0A}" +
    '.fil-mz .fil-logo:hover{text-decoration:none}' +
    '.fil-mz .fil-logo span{color:#00EF8B}' +
    '.fil-mz i{font-style:normal;color:#C3C8D0}' +
    '.fil-mz .fil-ici{overflow:hidden;text-overflow:ellipsis;min-width:0}' +
    '.fil-mz .fil-tout{margin-left:auto;padding-left:16px;color:#0062CC}' +
    '.fil-mz .fil-tout:hover{color:#0062CC}' +
    '.fil-mz.nuit{background:#0B0D10;border-bottom-color:#1F2635}' +
    '.fil-mz.nuit .fil-in{color:#8A94A6}.fil-mz.nuit a{color:#C9D1DD}.fil-mz.nuit a:hover{color:#fff}' +
    '.fil-mz.nuit .fil-logo{color:#fff}.fil-mz.nuit i{color:#3A4250}.fil-mz.nuit .fil-tout{color:#7DBBFF}' +
    '@media (max-width:640px){.fil-mz .fil-tout{display:none}.fil-mz .fil-in{padding:0 20px}}' +
    '@media print{.fil-mz{display:none}}';
  (document.head || document.documentElement).appendChild(css);

  var nav = document.createElement('nav');
  nav.className = 'fil-mz';
  moi.parentNode.insertBefore(nav, moi);
  document.documentElement.style.setProperty('--fil-h', '41px');

  function langue() {
    var l = (document.documentElement.getAttribute('lang') || '').toLowerCase();
    if (l.indexOf('en') === 0) return 1;
    if (l.indexOf('fr') === 0) return 0;
    return /^\/en\//.test(chemin) ? 1 : 0;
  }
  function esc(t) { return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }

  function dessiner() {
    var k = langue(), h = '';
    h += '<a class="fil-logo" href="' + T.accueil[k] + '">mazeo<span>.</span></a><i aria-hidden="true">/</i>';
    h += '<a href="' + T.page[k] + '">' + T.ressources[k] + '</a><i aria-hidden="true">/</i>';
    if (r.accueil && r.sous) {
      h += '<a href="' + r.accueil[k] + '">' + esc(r.nom[k]) + '</a><i aria-hidden="true">/</i>';
      h += '<span class="fil-ici" aria-current="page">' + esc(r.sous[k]) + '</span>';
    } else if (r.accueil) {
      h += '<a class="fil-ici" href="' + r.accueil[k] + '">' + esc(r.nom[k]) + '</a>';
    } else {
      h += '<span class="fil-ici" aria-current="page">' + esc(r.nom[k]) + '</span>';
    }
    h += '<a class="fil-tout" href="' + T.page[k] + '#' + r.fam[k] + '">← ' + T.toutes[k] + '</a>';
    nav.setAttribute('aria-label', T.aria[k]);
    nav.innerHTML = '<div class="fil-in">' + h + '</div>';
    aligner();
  }

  // Le fil commence au bord gauche du logo de la page et finit au bord droit de son dernier bouton :
  // on prend les éléments visibles les plus fins de l'en-tête (textes, images, boutons), jamais ses enveloppes.
  function texte(e) {
    for (var n = e.firstChild; n; n = n.nextSibling) if (n.nodeType === 3 && n.nodeValue.trim()) return true;
    return false;
  }
  function aligner() {
    var marque = document.querySelector('.brand');
    var tete = document.querySelector('header') || (marque && marque.parentElement);
    var bloc = nav.firstChild;
    if (!tete || !bloc) return;
    var els = tete.querySelectorAll('*'), g = Infinity, d = -Infinity, large = document.documentElement.clientWidth;
    for (var j = 0; j < els.length; j++) {
      var e = els[j], t = e.tagName;
      if (e.childElementCount && t !== 'svg' && t !== 'A' && t !== 'BUTTON' && !texte(e)) continue;
      if (e.closest('svg') && t !== 'svg') continue;
      var b = e.getBoundingClientRect();
      if (!b.width || !b.height || b.width > large * 0.6 || getComputedStyle(e).visibility === 'hidden') continue;
      if (b.left < g) g = b.left;
      if (b.right > d) d = b.right;
    }
    if (g === Infinity) return;
    if (large <= 640) { bloc.style.paddingLeft = bloc.style.paddingRight = ''; return; }
    bloc.style.paddingLeft = Math.max(16, Math.round(g)) + 'px';
    bloc.style.paddingRight = Math.max(16, Math.round(large - d)) + 'px';
  }

  // Une page sombre (le quiz) reçoit la barre de nuit.
  function sombre() {
    var c = getComputedStyle(document.body).backgroundColor;
    if (!c || /rgba?\(0, 0, 0, 0\)|transparent/.test(c)) c = getComputedStyle(document.documentElement).backgroundColor;
    var m = c && c.match(/\d+(\.\d+)?/g);
    if (!m) return;
    var lum = (0.299 * m[0] + 0.587 * m[1] + 0.114 * m[2]) / 255;
    nav.classList.toggle('nuit', lum < 0.35);
  }

  dessiner();
  document.addEventListener('DOMContentLoaded', function () { sombre(); aligner(); });
  window.addEventListener('load', aligner);
  window.addEventListener('resize', aligner);
  if (window.MutationObserver) new MutationObserver(dessiner).observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
})();
