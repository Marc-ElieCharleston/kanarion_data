# Audit des valeurs de gameplay codées en dur (2026-10-13)

Lecture seule de back `vac_integration-all` et data `vac_integration-all`. Voir les principes dans
[architecture_data.md](architecture_data.md).

## Points marquants

- **Bug actuel** : economy (`reward_processor.cpp:74-83`) cherche `config/game.json` →
  `stat_point_values`, clé qui n'existe pas (la vraie : `stats_definition.<stat>.point_value`, lue par le
  combat). Economy retombe sur ses valeurs C++ : **1 point de MP = 3 au lieu de 5** dans le recalcul de
  `mp_max` à la montée de niveau, alors que le combat applique 5.
- **`stats/definitions.json` n'est lu par aucun code serveur** : sa table de plafonds n'est que de la doc.
- **`config/combat.json` de la data n'est pas lu par le serveur** (le serveur lit celui du dépôt back).

## Lot 1 : doublons et contradictions

| # | Quoi | Problème |
|---|---|---|
| 1 | Valeur d'un point de stat (PV / Souffle) | contradiction active : economy 3, combat 5 (bug) |
| 2 | Points par niveau (3 stats / 1 compétence / 1 passif) | 4 copies C++, data morte |
| 3 | Multiplicateur de rareté 1.0 → 2.0 | 3 copies (dont une morte) |
| 4 | Plafond de pénétration 70 | ~12 copies |
| 5 | Plafonds CDR 40, vitesse d'incantation 50 | dupliqués, deux implémentations de la CDR |
| 6 | Plafonds réduction de dégâts 75, double / triple frappe 50 / 30, vol de sort 50 | dupliqués |
| 7 | Plafonds contradictoires (durée buff/debuff 50 vs 100, parade 30 vs 100, esquive 100 puis 40, ténacité 50 vs 90 monstres) | contradictions code / data |
| 8 | Formule de résistance aux effets | 3 versions différentes |
| 9 | Rangs C → SS par tranches de 20 niveaux | 4 copies data + 2 formules C++ (+ une 5e cachée dans le validateur des métiers, bornes différentes) |
| 10 | Poids des étoiles | repli C++ ≠ data, data en double dont une annoncée « vivante » mais non lue |
| 11 | Guilde : coût de création, membres max | 4 coûts et 5 capacités différents ; la capacité par niveau de guilde est chargée mais jamais utilisée |
| 12 | Coût de respec | 3 copies, data fausse et morte |
| 13 | Cartes Koro équipées max = 2 | en dur à 4 endroits ; bloque un 3e emplacement |
| 14 | GCD | 2 / 3 / 5 selon l'endroit ; l'IA calcule avec 2 s même pour les monstres à 3 s |
| 15 | Niveau max 100 | 6 gardes en dur |
| 16 | Efficacité vol de vie / de sort (0,5 / 0,33) | data morte |
| 17 | Taille de groupe 10 | défauts divergents (9, 10, 20) |

## Lot 2 : valeurs les plus réglées

Part d'XP du familier (90 %, réglée 3 fois, en dur) ; nombre d'affixes par rareté ; coefficients des
DoT (poison, brûlure, saignement… en dur par id) ; modificateurs de statut par id ; dérivations RM /
PV / Souffle ; plafond de drop 0,95 (11 copies) ; coût de téléportation ; prix de vente.

## Lot 3 : le reste

Poids de l'IA de kit ; constantes d'économie diverses (courrier, emplacements de personnage, diamants
fondateur, renommage, or de départ) ; capacité du courrier (ignore les extensions de sac achetées) ;
uniques actifs max ; replis incohérents. Faire lire les plafonds au simulateur `kbal.cpp` et au
validateur des métiers depuis la data.

## Doit rester dans le code (technique)

Tick 10 Hz (à centraliser en une constante), anti-spam et sécurité, timings réseau / reprise / replay,
bornes de sécurité (clamps 0-100, dégâts ≥ 1), identités de format (libellés de rang côté protocole,
nombre d'emplacements d'équipement).

## Déjà propre

Multiplicateur hors rôle des familiers, bonus de groupe, courbe d'XP, phases de boss, bonus de forge,
limite de contrats, hôtel des ventes, stockage.
