#!/usr/bin/env python3
"""Fabrique sitemap.xml, le plan du site donné à Google, à partir des pages elles-mêmes.

Usage : python3 outils/plan-du-site.py              (écrit sitemap.xml)
        python3 outils/plan-du-site.py --verifier   (échoue si sitemap.xml n'est pas à jour)

Une page y entre si git la suit, si elle n'est pas en noindex et si elle a son adresse de référence
(balise canonical). Ses versions dans l'autre langue (balises hreflang) y sont jointes. La date est
celle du dernier commit qui a touché la page. Plus de liste tenue à la main : une nouvelle page
entre seule dans le plan du site (la fiche 6 en avait été oubliée).
"""
import html
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

DEPOT = Path(__file__).resolve().parent.parent
SORTIE = DEPOT / "sitemap.xml"


def pages():
    suivies = subprocess.run(["git", "ls-files", "*.html"], cwd=DEPOT, capture_output=True, text=True, check=True).stdout.split()
    modifiees = set(subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "--", "*.html"], cwd=DEPOT,
                                   capture_output=True, text=True, check=True).stdout.split()[1::2])
    nouvelles = [f for f in modifiees if f.endswith(".html") and (DEPOT / f).exists()]
    for f in sorted(set(suivies) | set(nouvelles)):
        if not (DEPOT / f).exists():
            continue
        tete = (DEPOT / f).read_text(encoding="utf-8").split("</head>")[0]
        if re.search(r'<meta name="robots" content="[^"]*noindex', tete) or f == "404.html":
            continue
        canon = re.search(r'<link rel="canonical" href="([^"]*)"', tete)
        if not canon:
            raise SystemExit(f"{f} : pas de balise canonical (adresse de référence). L'ajouter, ou mettre la page en noindex.")
        langues = re.findall(r'<link rel="alternate" hreflang="([^"]*)" href="([^"]*)"', tete)
        if f in modifiees:
            jour = date.today().isoformat()
        else:
            jour = subprocess.run(["git", "log", "-1", "--format=%cs", "--", f], cwd=DEPOT, capture_output=True, text=True).stdout.strip() or date.today().isoformat()
        yield canon.group(1), jour, langues


def plan():
    vus = {}
    for url, jour, langues in pages():
        if url in vus:  # deux fichiers pour une adresse (ex. conditions-de-vente) : la date la plus récente
            vus[url] = (max(vus[url][0], jour), vus[url][1] or langues)
        else:
            vus[url] = (jour, langues)
    lignes = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for url in sorted(vus, key=lambda u: (u.count("/"), u)):
        jour, langues = vus[url]
        lignes.append(f"  <url><loc>{html.escape(url)}</loc><lastmod>{jour}</lastmod>"
                      + "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{html.escape(h)}"/>' for l, h in langues)
                      + "</url>")
    lignes.append("</urlset>")
    return "\n".join(lignes) + "\n", len(vus)


if __name__ == "__main__":
    texte, n = plan()
    if "--verifier" in sys.argv:
        ancien = SORTIE.read_text(encoding="utf-8") if SORTIE.exists() else ""
        strip = lambda t: re.sub(r"<lastmod>[^<]*</lastmod>", "", t)
        if strip(ancien) != strip(texte):
            sys.exit("sitemap.xml n'est pas à jour : lancer python3 outils/plan-du-site.py")
        print(f"sitemap.xml à jour ({n} adresses)")
    else:
        SORTIE.write_text(texte, encoding="utf-8")
        print(f"sitemap.xml écrit ({n} adresses)")
