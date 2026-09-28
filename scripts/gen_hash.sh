#!/bin/bash
# Regenere content_hash dans _meta/version.json.
#
# Ce script n'est plus qu'une facade : tout le calcul vit dans
# scripts/hash_content.py. Entretenir deux implementations du meme hash, une en
# shell et une en Python, a produit exactement le defaut qu'on corrige ici — elles
# ont divergé sans que personne le voie.
#
# CE QUI A CHANGE, ET POURQUOI L'ORDRE COMPTE MAINTENANT
# ------------------------------------------------------
# L'ancienne version lisait les fichiers du DISQUE (`find ... | cat`). Sous
# Windows git convertit les fins de ligne a l'extraction : le 2026-09-28, 51
# fichiers sur 123 etaient en CRLF sur le disque et en LF dans l'index. Le hash
# decrivait donc l'arbre local et non la livraison, et la CI Linux le rejetait.
#
# Le calcul porte desormais sur les octets de l'INDEX. Il faut donc avoir fait
# `git add` AVANT de lancer ce script, ce qui inverse l'ancien ordre :
#
#     git add .
#     ./scripts/gen_hash.sh
#     git add _meta/version.json
#     git commit
#
# Le resultat est identique a un calcul fait sur une extraction Linux, verifie
# contre le hash stocke sur origin/master.
#
# Sous Windows, prefere appeler Python directement : ce fichier .sh a des fins de
# ligne CRLF et bash peut echouer dessus avec « $'\r': command not found ».
#
#     python scripts/hash_content.py

set -e
cd "$(git rev-parse --show-toplevel)"
exec python scripts/hash_content.py "$@"
