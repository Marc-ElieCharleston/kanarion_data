#!/usr/bin/env python3
"""
Garde de traduction FR/EN (cree le 2026-10-17).

Le francais est la langue source, l'anglais la traduction. Un texte joueur qui
existe dans une langue et pas dans l'autre s'affiche vide (ou dans la mauvaise
langue) pour la moitie des joueurs, et rien ne le signalait : 20 descriptions
de ressources de metier etaient tronquees en anglais, 9 recettes speciales
n'avaient aucun texte anglais.

Ce qu'il verifie, sur tout le JSON du depot (hors _meta, scripts, dossiers caches) :
  1. paire presente : un `x_fr` non vide a son `x_en` non vide, et inversement.
     Deux conventions coexistent et sont acceptees : `x_fr` + `x_en`, et la cle
     nue `x` qui porte l'autre langue (`tagline` + `tagline_en` dans
     classes/_classes_index.json, `name` + `name_fr` dans ses tier3).
     Forme imbriquee {"fr": ..., "en": ...} : meme regle.
  2. listes (`lines_fr` / `lines_en`) : meme longueur, aucun element vide d'un
     seul cote.
  3. pas de copie non traduite : un EN identique au FR est refuse quand le FR
     est visiblement francais (accent ou au moins deux mots outils francais),
     sauf nom propre de la liste ALLOWED_IDENTICAL.

Cles ignorees : toute cle qui commence par `_`, et les champs de documentation
interne listes dans NON_PLAYER_KEYS / NON_PLAYER_FILES (jamais affiches en jeu).

Exit 0 = tout va bien, exit 1 = erreurs.
"""

import json
import os
import re
import sys

DB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {"_meta", "scripts", "node_modules"}

# Documentation interne : lue par les scripts ou les devs, jamais par le joueur.
NON_PLAYER_KEYS = {"doc", "note", "explanation", "base"}
NON_PLAYER_FILES = {
    "config/monster_scaling_model.json",   # noms d'archetypes internes (name_fr seul)
}
# Noms propres ou termes identiques dans les deux langues, mais ecrits avec un accent.
ALLOWED_IDENTICAL = {
    "Coup de Grâce",
}

FR_ACCENT = re.compile(r"[éèêàâçùûôîïœÉÈÀÇÊÎÔ]")
FR_WORDS = re.compile(
    r"\b(le|la|les|de|des|du|une|et|est|avec|pour|dans|sur|vos|votre|aux|au|ses|leur|chaque|pendant|qui|que|tu|ton|ta)\b",
    re.I)


def looks_french(text: str) -> bool:
    return bool(FR_ACCENT.search(text)) or len(FR_WORDS.findall(text)) >= 2


def is_blank(v) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())


def check_pair(errors, rel, path, base, fr, en):
    where = f"{rel} {path}.{base}"
    if isinstance(fr, list) or isinstance(en, list):
        if not isinstance(fr, list) or not isinstance(en, list):
            errors.append(f"{where} : liste d'un cote seulement")
            return
        if len(fr) != len(en):
            errors.append(f"{where} : {len(fr)} lignes FR pour {len(en)} lignes EN")
            return
        for i, (a, b) in enumerate(zip(fr, en)):
            if isinstance(a, str) or isinstance(b, str):
                check_pair(errors, rel, f"{path}.{base}", f"[{i}]", a, b)
        return
    if not isinstance(fr, (str, type(None))) or not isinstance(en, (str, type(None))):
        return
    if is_blank(fr) and is_blank(en):
        return
    if is_blank(en):
        errors.append(f"{where} : FR sans EN ({fr[:70]!r})")
    elif is_blank(fr):
        errors.append(f"{where} : EN sans FR ({en[:70]!r})")
    elif fr.strip() == en.strip() and looks_french(fr) and fr.strip() not in ALLOWED_IDENTICAL:
        errors.append(f"{where} : EN recopie le FR sans le traduire ({fr[:70]!r})")


def walk(errors, rel, node, path="$"):
    if isinstance(node, dict):
        keys = set(node)
        if "fr" in keys and "en" in keys and isinstance(node.get("fr"), str):
            check_pair(errors, rel, path, "{fr,en}", node["fr"], node["en"])
        done = set()
        for k in keys:
            if k.startswith("_"):
                continue
            for suf, other_suf in (("_fr", "_en"), ("_en", "_fr")):
                if not k.endswith(suf):
                    continue
                base = k[: -len(suf)]
                if base in done or base in NON_PLAYER_KEYS or base.startswith("_"):
                    continue
                done.add(base)
                other = base + other_suf
                if other in node:
                    pair_val = node[other]
                elif base in node:
                    pair_val = node[base]   # cle nue = l'autre langue
                else:
                    pair_val = None
                fr, en = (node[k], pair_val) if suf == "_fr" else (pair_val, node[k])
                check_pair(errors, rel, path, base, fr, en)
        for k, v in node.items():
            if k.startswith("_"):
                continue
            walk(errors, rel, v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            ident = v.get("id") if isinstance(v, dict) else None
            walk(errors, rel, v, f"{path}[{ident or i}]")


def main(argv) -> int:
    root = argv[1] if len(argv) > 1 else DB
    errors = []
    files = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        for fn in sorted(filenames):
            if not fn.endswith(".json"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            if rel in NON_PLAYER_FILES:
                continue
            try:
                with open(full, encoding="utf-8-sig") as fh:
                    data = json.load(fh)
            except (ValueError, UnicodeDecodeError) as exc:
                errors.append(f"{rel} : JSON illisible ({exc})")
                continue
            files += 1
            walk(errors, rel, data)
    for e in errors:
        print(f"ERROR {e}")
    if errors:
        print(f"VALIDATION FAILED - {len(errors)} texte(s) FR/EN incomplet(s) sur {files} fichiers")
        return 1
    print(f"VALIDATION PASSED - textes FR/EN complets ({files} fichiers)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
