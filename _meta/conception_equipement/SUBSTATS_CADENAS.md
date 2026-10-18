# Substats : relance à cadenas et pools par emplacement (proposition, 2026-10-18)

Statut : **proposition**, rien n'est codé. Base actuelle : `items/equipment_stats.json` (lu par le serveur,
`server-combat/src/loot/stat_roller.cpp`) et `systems/equipment_upgrade.json` (améliorations).

## Décisions du propriétaire (2026-10-18)

- La **relance à cadenas remplace « changer une substat »** : on cadenasse les substats qui plaisent, on relance
  toutes les autres d'un coup.
- **Le prix monte avec le nombre de cadenas**, en or seulement (pas de ressource). Le prix ne monte pas avec le
  nombre de tentatives (règle déjà posée dans `equipment_upgrade.json`).
- **4 substats au plus par pièce**, 10 pièces : arme, casque, torse, jambes, bottes, ceinture, cape, collier,
  anneau 1, anneau 2.
- Les substats dépendent de la pièce : une arme a des substats plutôt offensives.
- Les valeurs doivent rester raisonnables : 10 pièces × 4 lignes = 40 lignes, le total ne doit pas exploser.
- **Retirer les doublons de stats, surtout le code mort** (voir plus bas).

## Règles proposées

- Cadenas : au plus `substats de la pièce − 1`. Une relance retire au hasard le type ET la valeur de chaque ligne
  non cadenassée, dans le pool de la pièce, dans la fourchette de sa rareté (la même qu'au loot : on n'atteint
  jamais mieux qu'un objet parfait trouvé).
- Une stat n'apparaît **jamais deux fois sur la même pièce**.
- **Listes fermées par emplacement**, plus de poids « hors rôle » : avec la relance, une stat rare (poids ×0,25)
  devient une stat qu'on obtient en relançant ; seul l'interdit tient.
- Prix : `prix_de_base(palier) × multiplicateur(nombre de cadenas)`, proposé ×1 / ×2 / ×4 / ×8 pour 0 / 1 / 2 / 3
  cadenas, sur la base actuelle de « changer une substat » (100 / 400 / 1 200 / 3 000 / 8 000 or).

## Pourquoi pas un pool de 40 stats

- Le moteur connaît 38 stats (`stats/definitions.json`), dont plusieurs inertes ou non branchées (vitesse
  d'attaque, perce-bouclier, bouclier) : il en reste ~30 utilisables.
- Un pool énorme sur chaque pièce efface les rôles : n'importe quelle stat partout, retour au « même build pour
  tous ».
- La difficulté se règle mieux avec **la taille du pool d'une pièce** et **le prix du cadenas** :

| Pool de la pièce | Viser 1 stat précise (1 ligne libre) | Viser 2 stats précises (2 lignes libres) |
|---|---|---|
| 8 | ~8 relances | ~28 relances |
| 10 | ~10 relances | ~45 relances |
| 12 | ~12 relances | ~66 relances |

(stats à poids égal, sans doublon sur la pièce). Proposé : **8 à 12 stats par pièce**.

## Pools proposés par emplacement (brouillon à valider)

| Emplacement | Rôle | Pool proposé |
|---|---|---|
| Arme | offensif | attaque, magie, attaque %, magie %, crit, dégâts crit, pén. armure, pén. magique, dégâts %, puissance de soin, puissance de bouclier, vol de vie |
| Casque | protection, Souffle | PV, Souffle, armure, résistance magique, résistance aux effets, régénération de Souffle, vitesse d'incantation, précision |
| Torse | encaisser | PV, armure, résistance magique, réduction de dégâts, soins reçus, régénération PV, défense %, épines |
| Jambes | tenir la ligne | PV, armure, résistance magique, ténacité, parade, blocage, régénération PV, esquive |
| Bottes | mobilité, précision | PV, esquive, précision, armure, résistance magique, ténacité, vitesse d'incantation, résistance aux effets |
| Ceinture | ressources | PV, Souffle, régénération PV, régénération de Souffle, soins reçus, puissance de bouclier, durée des buffs, réduction de dégâts |
| Cape | contrôle subi | esquive, résistance magique, résistance aux effets, ténacité, durée des debuffs, PV, réduction de dégâts, épines |
| Collier | rythme | réduction de recharge, vitesse d'incantation, chance d'effet, durée des buffs, durée des debuffs, Souffle, puissance de soin, dégâts % |
| Anneaux (×2, même pool) | précision offensive | attaque, magie, crit, dégâts crit, précision, chance d'effet, vol de vie, vampirisme magique, pén. armure, pén. magique |

Conséquence : une stat en % n'existe que sur 2 à 4 pièces. Le crit, par exemple, est sur l'arme et les deux
anneaux : 3 lignes au plus.

## Valeurs : partir du plafond « tout-en-un »

Pour chaque stat : ce qu'un joueur qui met tout dedans doit atteindre au plus, divisé par le nombre de pièces
qui la portent = la ligne légendaire au maximum de sa fourchette.

| Stat | Tout-en-un visé | Pièces | Ligne légendaire max |
|---|---|---|---|
| Crit | +15 % | 3 | 5 % |
| Dégâts crit | +30 | 3 | 10 |
| Réduction de recharge | +10 % (plafond 40) | 1 | 10 % |
| Pénétration (armure ou magique) | +15 | 3 | 5 |
| Vol de vie | +6 % | 3 | 2 % |
| PV, armure, attaque, magie (flat) | suit le niveau de l'objet | 4 à 8 | à chiffrer par palier |

Les stats en % restent faibles par ligne et rares en emplacements (elles multiplient le reste) ; les stats flat
sont plus généreuses et montent avec le niveau de l'objet. Les plafonds de stats déjà posés restent le filet.

## Doublons à retirer (code rule : pas de doublon, pas de code mort)

- `items/substat_crafting_system.json` (`substat_pools` par palier avec `allowed_slots`) : **le serveur ne le
  lit pas** (il n'apparaît qu'en commentaire dans `services/economy/src/inventory/stat_calculator.hpp`). Seul le
  client le charge, pour l'onglet « Reforge » de la forge (`scripts/ui/popups/forge_window.gd`, ancien système
  de cristaux). À retirer avec l'onglet, remplacé par la relance à cadenas.
- `equipment_stats.json` : `substat_weight_multipliers` (poids hors rôle) devient inutile avec les listes
  fermées.
- `equipment_stats.json` `stat_ranges_by_rarity.substats` et les fourchettes de `equipment_scaling.json`
  `rarity_system.roll_range_percent` : vérifier qu'une seule source fixe la valeur d'une ligne.
- `equipment_upgrade.json` `change_substat` : remplacé par la relance à cadenas.

## Questions ouvertes

1. Valider les pools par emplacement (une stat à ajouter ou retirer ?).
2. Valider les plafonds « tout-en-un » du tableau des valeurs.
3. Multiplicateur du cadenas : ×1 / ×2 / ×4 / ×8 ?
