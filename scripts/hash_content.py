#!/usr/bin/env python3
"""Calcule le content_hash de la base de donnees de jeu.

POURQUOI CE FICHIER EXISTE
--------------------------
Le hash doit decrire les octets que git STOCKE, pas ceux du repertoire de
travail. Sous Windows, git convertit les fins de ligne a l'extraction : le
2026-09-28, 51 fichiers sur 123 etaient en CRLF sur le disque et en LF dans
l'index. Un hash calcule avec `cat` decrivait donc l'arbre local et non la
livraison, et la CI Linux le rejetait.

Le piege etait double : le hook de pre-commit lisait AUSSI le disque, donc il
validait un hash que la CI refusait. Sur ce poste il etait impossible de
satisfaire les deux.

La correction n'est pas de renormaliser les fichiers — 73 des 128 blobs commites
contiennent du CRLF, les reecrire ferait un diff de fichier entier sur chacun et
changerait le hash de toute la base. On lit simplement les octets de git.

USAGE
-----
    git add .                          # les modifications entrent dans l'index
    python scripts/hash_content.py     # ecrit _meta/version.json
    git add _meta/version.json
    git commit

L'ORDRE COMPTE : ce script lit l'INDEX, donc les modifications doivent y etre
avant. C'est l'inverse de l'ancien gen_hash.sh, qui lisait le disque et pouvait
donc tourner avant `git add`.

Le resultat est identique a un calcul fait sur une extraction Linux, ce qui a ete
verifie contre le hash stocke sur origin/master.
"""
from __future__ import annotations

import datetime
import hashlib
import io
import json
import os
import subprocess
import sys

# Metadonnees exclues du hash : elles CONTIENNENT le hash ou en derivent.
FICHIERS_EXCLUS = {
    "_meta/version.json",
    "_meta/statistics.json",
    "_meta/index.json",
    "_meta/changelog.json",
    "_meta/ideas_to_integrate.json",
}
DOSSIERS_EXCLUS = (".claude/", "kanarion-editor/", "scripts/")


def racine() -> str:
    return subprocess.run(["git", "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True, check=True).stdout.strip()


def fichiers_haches(repo: str) -> list[str]:
    sortie = subprocess.run(["git", "-C", repo, "ls-files"],
                            capture_output=True, text=True, check=True).stdout.splitlines()
    retenus = [
        p for p in sortie
        if p.endswith(".json")
        and p not in FICHIERS_EXCLUS
        and not p.startswith(DOSSIERS_EXCLUS)
        and "/.claude/" not in p
    ]
    return sorted("./" + p for p in retenus)


def calculer(repo: str, fichiers: list[str]) -> str:
    """Hash du chemin puis du contenu de chaque fichier, dans l'ordre trie.

    Les octets viennent de l'index (`git show :chemin`), jamais du disque.
    """
    acc = hashlib.sha256()
    for chemin in fichiers:
        acc.update((chemin + "\n").encode())
        octets = subprocess.run(["git", "-C", repo, "show", ":" + chemin[2:]],
                                capture_output=True, check=True).stdout
        acc.update(octets)
    return acc.hexdigest()


def main() -> int:
    repo = racine()
    fichiers = fichiers_haches(repo)
    if not fichiers:
        print("ERREUR : aucun fichier JSON a hacher", file=sys.stderr)
        return 2
    h = calculer(repo, fichiers)

    if "--check" in sys.argv:
        chemin = os.path.join(repo, "_meta", "version.json")
        stocke = json.load(io.open(chemin, encoding="utf-8")).get("content_hash", "")
        attendu = "sha256:" + h
        if stocke != attendu:
            print("content_hash perime : %s stocke, %s attendu" % (stocke[:23], attendu[:23]),
                  file=sys.stderr)
            return 1
        print("content_hash a jour : %s (%d fichiers)" % (attendu[:23], len(fichiers)))
        return 0

    chemin = os.path.join(repo, "_meta", "version.json")
    v = json.load(io.open(chemin, encoding="utf-8"))
    v["content_hash"] = "sha256:" + h
    v["last_updated"] = datetime.date.today().isoformat()
    with io.open(chemin, "w", encoding="utf-8", newline="\n") as f:
        json.dump(v, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("content_hash: sha256:%s  (%d fichiers)" % (h, len(fichiers)))
    print("Pense a : git add _meta/version.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
