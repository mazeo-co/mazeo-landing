#!/usr/bin/env python3
"""Contrôle SEO de mazeo.co : tout ce qui a déjà mal tourné, vérifié sur chaque page.

Usage : python3 outils/controle-seo.py            (toutes les vérifications)
        python3 outils/controle-seo.py --rapide   (sans Chrome : saute la vérification de /en)

Lancé par GitHub à chaque PR et chaque lundi (.github/workflows/controle-seo.yml).
Sort en erreur (code 1) au premier défaut trouvé, avec la liste de tous les défauts.

Ce qui est vérifié, page par page (pages indexables : pas de noindex) :
  - un titre de 65 signes au plus, une description de 50 à 165 signes ;
  - une adresse de référence (canonical), et la langue de la page qui suit son adresse (/en/… = anglais) ;
  - des balises de langue (hreflang) qui se répondent : si A annonce B en anglais, B annonce A ;
  - un seul titre principal (h1), hors bloc anglais d'une page bilingue (data-lang="en") ;
  - une image de partage (og:image) ;
  - chaque lien interne mène à une page qui existe, sans .html ;
  - chaque événement (balisage Event) est à venir et complet : organisateur, intervenant, offre.
Et pour le site : le plan du site, /en et les copies anglaises sont à jour de leurs sources.
"""
import html
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

DEPOT = Path(__file__).resolve().parent.parent
ORIGINE = "https://www.mazeo.co"
AUJ = date.today().isoformat()
defauts = []


def defaut(page, texte):
    defauts.append(f"{page} : {texte}")


def fichiers_html():
    suivis = subprocess.run(["git", "ls-files", "*.html"], cwd=DEPOT, capture_output=True, text=True, check=True).stdout.split()
    nouveaux = subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "*.html"], cwd=DEPOT, capture_output=True, text=True, check=True).stdout.split()
    return sorted(f for f in set(suivis) | set(nouveaux) if (DEPOT / f).exists())


def adresses_servies(fichiers):
    """Les adresses que Vercel sert : chaque fichier sans .html (cleanUrls), plus les réécritures de vercel.json."""
    servies = set()
    for f in fichiers:
        chemin = "/" + f[:-5]
        servies.add("/" if chemin == "/index" else chemin[:-6] if chemin.endswith("/index") else chemin)
    config = json.loads((DEPOT / "vercel.json").read_text(encoding="utf-8"))
    servies |= {r["source"] for r in config.get("rewrites", [])}
    servies |= {r["source"] for r in config.get("redirects", [])}
    return servies


def texte_balise(tete, motif):
    m = re.search(motif, tete, re.S)
    return html.unescape(m.group(1)).strip() if m else None


def controler_page(f, s, servies, langues_par_url):
    tete = s.split("</head>")[0]
    corps = s.split("</head>", 1)[1] if "</head>" in s else ""
    indexable = not re.search(r'<meta name="robots" content="[^"]*noindex', tete) and f != "404.html"
    titre = texte_balise(tete, r"<title>(.*?)</title>")
    if not titre:
        defaut(f, "pas de titre")
    if not indexable:
        return
    desc = texte_balise(tete, r'<meta name="description" content="([^"]*)"')
    canon = texte_balise(tete, r'<link rel="canonical" href="([^"]*)"')
    if titre and len(titre) > 65:
        defaut(f, f"titre de {len(titre)} signes (65 au plus) : « {titre} »")
    if not desc:
        defaut(f, "pas de description")
    elif not 50 <= len(desc) <= 165:
        defaut(f, f"description de {len(desc)} signes (50 à 165)")
    if not canon:
        defaut(f, "pas d'adresse de référence (canonical)")
    elif not canon.startswith(ORIGINE) or canon.removeprefix(ORIGINE) not in servies:
        defaut(f, f"canonical vers une adresse que le site ne sert pas : {canon}")
    if "og:image" not in tete:
        defaut(f, "pas d'image de partage (og:image)")
    langue = texte_balise(s, r'<html[^>]*\blang="([^"]*)"')
    attendue = "en" if f.startswith("en/") else "fr"
    if langue != attendue:
        defaut(f, f'langue « {langue} » au lieu de « {attendue} » (la langue suit l\'adresse)')
    # un seul h1, hors bloc anglais d'une page bilingue
    sans_en = re.sub(r'<div[^>]*data-lang="en".*?(?=<div[^>]*data-lang="fr"|</main>|<footer|$)', "", corps, flags=re.S)
    n = len(re.findall(r"<h1[\s>]", sans_en))
    if n != 1:
        defaut(f, f"{n} titres principaux (h1) au lieu d'un")
    if canon:
        langues_par_url[canon] = (f, dict(re.findall(r'<link rel="alternate" hreflang="([^"]*)" href="([^"]*)"', tete)))
    # liens internes : la page existe, sans .html
    for lien in re.findall(r'\bhref="([^"]+)"', re.sub(r"<script\b.*?</script>", "", corps, flags=re.S)):
        lien = re.sub(r"^https://(www\.)?mazeo\.co", "", lien) or "/"
        if not lien.startswith("/") or lien.startswith("//"):
            continue
        chemin = lien.split("#")[0].split("?")[0] or "/"
        if chemin.startswith(("/assets/", "/_vercel/")) or re.search(r"\.(png|jpe?g|webp|svg|pdf|mp4|ico|js|css|xml|txt)$", chemin):
            if not (DEPOT / chemin.lstrip("/")).exists() and not chemin.startswith("/_vercel/"):
                defaut(f, f"lien vers un fichier absent : {lien}")
            continue
        if chemin.endswith(".html"):
            defaut(f, f"lien en .html (redirigé à chaque clic) : {lien}")
        elif chemin.rstrip("/") not in servies and chemin not in servies:
            defaut(f, f"lien vers une page qui n'existe pas : {lien}")
    # événements
    for bloc in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            d = json.loads(bloc)
        except json.JSONDecodeError as e:
            defaut(f, f"balisage JSON-LD illisible : {e}")
            continue
        if d.get("@type") != "Event":
            continue
        if (d.get("endDate") or d.get("startDate") or "") < AUJ:
            defaut(f, f"événement passé : {d.get('name')} ({d.get('endDate')}) — relancer ~/dev/salons-etudes/site.py")
        for champ in ("organizer", "performer", "offers", "location", "startDate", "image", "description"):
            if champ not in d:
                defaut(f, f"événement sans « {champ} » : {d.get('name')}")
        if "offers" in d and "availability" not in d["offers"]:
            defaut(f, f"offre sans disponibilité : {d.get('name')}")


def controler_langues(langues_par_url):
    for url, (f, langues) in langues_par_url.items():
        for code, cible in langues.items():
            if code == "x-default" or cible == url:
                continue
            if cible not in langues_par_url:
                defaut(f, f"hreflang {code} vers {cible}, qui n'est pas une page indexable du site")
            elif url not in langues_par_url[cible][1].values():
                defaut(f, f"hreflang {code} vers {cible}, qui ne renvoie pas vers cette page")


def controler_sources(rapide):
    outils = [("plan-du-site.py", "le plan du site"), ("pages-en.py", "les copies anglaises")]
    if not rapide:
        outils.append(("accueil-en.py", "l'accueil anglais /en"))
    for outil, quoi in outils:
        r = subprocess.run([sys.executable, str(DEPOT / "outils" / outil), "--verifier"], cwd=DEPOT, capture_output=True, text=True)
        if r.returncode:
            defaut("site", f"{quoi} n'est pas à jour : {(r.stderr or r.stdout).strip()}")


if __name__ == "__main__":
    rapide = "--rapide" in sys.argv
    fichiers = fichiers_html()
    servies = adresses_servies(fichiers)
    langues_par_url = {}
    for f in fichiers:
        controler_page(f, (DEPOT / f).read_text(encoding="utf-8"), servies, langues_par_url)
    controler_langues(langues_par_url)
    controler_sources(rapide)
    if defauts:
        print(f"{len(defauts)} défaut(s) SEO :")
        print("\n".join("  - " + d for d in defauts))
        sys.exit(1)
    print(f"contrôle SEO : {len(fichiers)} pages, aucun défaut")
