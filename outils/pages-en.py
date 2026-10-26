#!/usr/bin/env python3
"""Fabrique les copies anglaises des pages qui se traduisent seules : bourse-emploi.html → en/insight-jobs.html,
appels-offres.html → en/public-tenders.html.

Usage : python3 outils/pages-en.py              (écrit les copies)
        python3 outils/pages-en.py --verifier   (échoue si une copie n'est pas à jour)

Chaque page française porte un script qui, sous /en/, passe la page en anglais (langue, titre, description).
La copie anglaise est la même page, avec cette tête déjà en anglais dans le HTML : Google n'a plus besoin
d'exécuter le script pour savoir que l'adresse anglaise est en anglais. On ne modifie que la page française.
"""
import re
import sys
from pathlib import Path

DEPOT = Path(__file__).resolve().parent.parent
PAGES = [("bourse-emploi.html", "en/insight-jobs.html", "https://www.mazeo.co/en/insight-jobs"),
         ("appels-offres.html", "en/public-tenders.html", "https://www.mazeo.co/en/public-tenders")]


def lu(script, motif, quoi, src):
    m = re.search(motif, script)
    assert m, f"{src} : {quoi} anglais introuvable dans le script de tête"
    return m.group(1)


def copie(src, url):
    s = (DEPOT / src).read_text(encoding="utf-8")
    script = s[s.index("<script>"):s.index("</script>")]  # le premier script : celui qui pose la tête anglaise
    titre = lu(script, r'document\.title = "([^"]*)"', "titre", src)
    desc = lu(script, r'meta\[name="description"\]\'\)\.content = "([^"]*)"', "description", src)
    og_t = lu(script, r'meta\[property="og:title"\]\'\)\.content = "([^"]*)"', "og:title", src)
    og_d = lu(script, r'meta\[property="og:description"\]\'\)\.content = "([^"]*)"', "og:description", src)
    remplacements = [
        (r'<html lang="fr">', '<html lang="en">'),
        (r"<title>[^<]*</title>", f"<title>{titre}</title>"),
        (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">'),
        (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">'),
        (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">'),
        (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{og_t}">'),
        (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{og_d}">'),
    ]
    for motif, nouveau in remplacements:
        s, n = re.subn(motif, lambda _: nouveau, s, count=1)
        assert n == 1, f"{src} : {motif} introuvable"
    return s


if __name__ == "__main__":
    verifier = "--verifier" in sys.argv
    faux = []
    for src, dst, url in PAGES:
        page = copie(src, url)
        if verifier:
            if not (DEPOT / dst).exists() or (DEPOT / dst).read_text(encoding="utf-8") != page:
                faux.append(dst)
        else:
            (DEPOT / dst).write_text(page, encoding="utf-8")
            print(f"{dst} écrit")
    if faux:
        sys.exit("pas à jour : " + ", ".join(faux) + " — lancer python3 outils/pages-en.py")
    if verifier:
        print("copies anglaises à jour")
