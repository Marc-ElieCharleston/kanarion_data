# Architecture : tout l'équilibrage dans la data

Statut : **validé par le propriétaire** (2026-10-13). Objectif : un jeu scalable, sans bugs de valeurs
codées en dur, sans replis silencieux (« fallbacks ») qui masquent une donnée manquante.

## Principes

1. **Le code ne connaît ni les lettres de rang ni le nombre de rangs.** Identifiants internes stables
   (`rank_1`, `rank_2`…) ; la lettre affichée (C-SS aujourd'hui, D-S demain) n'est qu'un libellé dans
   la data. Renommer C → D = changer l'affichage, sans migration ni objet renommé.
2. **Une seule table des rangs, ordonnée** (id, libellé, tranche de niveau, couleur, puissance…).
   Ajouter un rang = ajouter une ligne. Le code boucle sur la liste, jamais `if (rank == "SS")`.
3. **Une seule table des raretés** (fenêtre de stat principale, nombre de substats et d'affixes,
   multiplicateur de prix, poids de drop, couleur).
4. **Aucune copie** : tout le reste (courbe de niveau, forge, recettes, clés, grimoires, Koro) se réfère
   à ces tables. Aujourd'hui : bandes de rang recopiées dans 3 fichiers, multiplicateur de rareté dupliqué
   3 fois dans le code, points par niveau dupliqués 2 fois…
5. **Pas de repli silencieux** : une donnée manquante = erreur visible (validateur, refus au chargement),
   jamais une valeur par défaut codée en dur qui fait tourner le jeu avec de mauvais chiffres (exemple
   corrigé : la table de loot « default »).
6. **Validateurs** : cohérence des tables (rangs contigus, références existantes) ; ils ne doivent jamais
   épingler une constante C++ (exemple corrigé : le bonus de groupe).

Point de vigilance : des identifiants contiennent déjà la lettre (grimoires `book_*_rank_c`, cartes
Koro) : ils gardent leur identifiant, seul le nom affiché change. Branche de sauvegarde du 2026-10-01
`rank-display-ds` : début de l'affichage D..S.

## Plan

Audit des valeurs codées en dur en cours (2026-10-13) → plan en 3 lots : (1) doublons et contradictions,
(2) valeurs d'équilibrage les plus réglées, (3) le reste. La table des rangs et la table des raretés font
partie du lot 1.
