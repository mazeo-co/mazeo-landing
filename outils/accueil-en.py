#!/usr/bin/env python3
"""Fabrique en/index.html, l'accueil anglais servi à l'adresse /en, depuis index.html.

Usage : python3 outils/accueil-en.py          (écrit en/index.html)
        python3 outils/accueil-en.py --verifier   (échoue si en/index.html n'est pas à jour)

On ne tient qu'une page : index.html, en français, avec son dictionnaire anglais (var EN, var META).
Chrome sans fenêtre lit index.html sans exécuter son script, pose chaque texte anglais à sa place
(comme le fait setLang("en") dans la page), et rend le HTML. Le texte anglais est donc écrit dans
le fichier : Google et les robots qui n'exécutent pas le JavaScript le lisent tel quel.
À relancer après chaque modification de index.html (le contrôle SEO le vérifie).
"""
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DEPOT = Path(__file__).resolve().parent.parent
# Chrome du Mac, ou celui de la machine de GitHub (variable CHROME, ou google-chrome dans le PATH)
CHROME = os.environ.get("CHROME") or next((c for c in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",)
                                          if Path(c).exists()), None) or shutil.which("google-chrome") or "chromium"
SORTIE = DEPOT / "en" / "index.html"

TETE_EN = {
    "og:title": "The only prospecting tool built for market research",
    "og:description": "The entire industry, scored and updated in real time. Your next clients are on mazeo.",
    "og:image:alt": "mazeo, the only prospecting tool built for market research",
    "twitter:title": "The only prospecting tool built for market research",
    "twitter:description": "The entire industry, scored and updated in real time.",
    "twitter:image:alt": "mazeo, the only prospecting tool built for market research",
}

AIDE = r"""<!doctype html><meta charset="utf-8"><body><script>
(async function () {
  var src = await (await fetch(%(index)s)).text();
  var doc = new DOMParser().parseFromString(src, "text/html");
  function objet(code, nom) {                       // lit var <nom> = {...} sans exécuter la page
    var i = code.indexOf("var " + nom + " = {"); if (i < 0) throw new Error(nom + " introuvable");
    i = code.indexOf("{", i); var p = 0, q = null;
    for (var j = i; j < code.length; j++) {
      var c = code[j];
      if (q) { if (c === "\\") { j++; continue; } if (c === q) q = null; continue; }
      if (c === '"' || c === "'") { q = c; continue; }
      if (c === "{") p++; else if (c === "}") { p--; if (!p) return Function("return " + code.slice(i, j + 1))(); }
    }
    throw new Error(nom + " mal fermé");
  }
  var code = Array.prototype.map.call(doc.scripts, function (s) { return s.textContent; }).join("\n");
  var EN = objet(code, "EN"), META = objet(code, "META").en, TETE = %(tete)s;
  doc.documentElement.lang = "en";
  doc.querySelectorAll("[data-t]").forEach(function (n) { var k = n.getAttribute("data-t"); if (EN[k] !== undefined) n.innerHTML = EN[k]; });
  doc.querySelectorAll("[data-t-ph]").forEach(function (n) { var k = n.getAttribute("data-t-ph"); if (EN[k]) n.setAttribute("placeholder", EN[k]); });
  doc.querySelectorAll("[data-aria-en]").forEach(function (n) { n.setAttribute("aria-label", n.getAttribute("data-aria-en")); });
  doc.querySelectorAll(".chip[data-en]").forEach(function (n) { n.textContent = n.getAttribute("data-en"); });
  doc.querySelectorAll("[data-href-en]").forEach(function (n) { n.setAttribute("href", n.getAttribute("data-href-en")); });
  doc.querySelectorAll("[data-src-en]").forEach(function (n) { n.setAttribute("src", n.getAttribute("data-src-en")); });
  doc.querySelectorAll('a[href^="https://app.mazeo.co"]').forEach(function (n) { n.setAttribute("href", "https://app.mazeo.co/?hl=en"); });
  var film = doc.getElementById("film");
  if (film) { film.setAttribute("aria-label", "mazeo in one minute"); film.setAttribute("poster", "/assets/mazeo-film-poster-en.jpg");
    var so = film.querySelector("source"); if (so) so.setAttribute("src", "/assets/mazeo-film-en.mp4"); }
  var sw = doc.getElementById("lang-switch"); if (sw) { sw.setAttribute("hreflang", "fr"); sw.setAttribute("lang", "fr"); }
  doc.title = META.title;
  function meta(sel, v) { var m = doc.head.querySelector(sel); if (!m) throw new Error(sel + " introuvable"); m.setAttribute("content", v); }
  meta('meta[name="description"]', META.desc);
  meta('meta[property="og:url"]', "https://www.mazeo.co/en");
  meta('meta[property="og:locale"]', "en_GB");
  Object.keys(TETE).forEach(function (k) { meta(k.indexOf("twitter:") === 0 ? 'meta[name="' + k + '"]' : 'meta[property="' + k + '"]', TETE[k]); });
  doc.head.querySelector('link[rel="canonical"]').setAttribute("href", "https://www.mazeo.co/en");
  document.body.textContent = "<!DOCTYPE html>\n" + doc.documentElement.outerHTML + "\n";
  document.title = "fini";
})().catch(function (e) { document.body.textContent = "ERREUR " + e.message; document.title = "fini"; });
</script>"""


def fabriquer():
    import json
    with tempfile.TemporaryDirectory() as tmp:
        aide = Path(tmp) / "aide.html"
        aide.write_text(AIDE % {"index": json.dumps((DEPOT / "index.html").as_uri()), "tete": json.dumps(TETE_EN, ensure_ascii=False)}, encoding="utf-8")
        out = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--allow-file-access-from-files",
                              f"--user-data-dir={tmp}/profil", "--virtual-time-budget=10000", "--dump-dom", aide.as_uri()],
                             capture_output=True, text=True, timeout=120).stdout
    corps = re.search(r"<body>(.*)</body>", out, re.S)
    assert corps, "Chrome n'a rien rendu"
    page = html.unescape(corps.group(1))
    assert not page.startswith("ERREUR"), page[:300]
    assert page.startswith("<!DOCTYPE html>"), page[:200]
    return page


if __name__ == "__main__":
    page = fabriquer()
    if "--verifier" in sys.argv:
        if not SORTIE.exists() or SORTIE.read_text(encoding="utf-8") != page:
            sys.exit("en/index.html n'est pas à jour : lancer python3 outils/accueil-en.py")
        print("en/index.html à jour")
    else:
        SORTIE.parent.mkdir(exist_ok=True)
        SORTIE.write_text(page, encoding="utf-8")
        print(f"en/index.html écrit ({len(page) // 1024} Ko)")
