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

## Type d'armure (propriétaire, 2026-10-18)

Les valeurs des substats dépendent aussi du type d'armure : **tissu** (`light`), **cuir** (`medium`), **plaque**
(`heavy`). La data a déjà `main_stat_by_armor_type` (stat principale) et `substat_weight_multipliers` (poids hors
rôle x0,25) dans `equipment_stats.json` `equipment_categories.armor`. À faire : remplacer les poids par des
**multiplicateurs de valeur** par type (ex. plaque : armure/PV x1,2, Souffle x0,6 ; tissu l'inverse), pools
fermés par emplacement.

## Stats inertes ou pas branchées (audit du 2026-10-18, code de `vac_contracts-v2`)

Audit en lecture seule, stat par stat : tirée sur l'objet (`server-combat/src/loot/stat_roller.cpp`), transportée
(`services/economy/src/inventory/stat_calculator.hpp`, `shared/flatbuffers/builders/character_stats_builder.hpp`,
`server-combat/src/domain/combat_profile_resolver.cpp`), chargée en combat (`combat_profile_builder.cpp`,
`room.cpp:7043-7141`), puis utilisée dans une formule (`damage_calculator.cpp`, `status_manager.cpp`, `room.cpp`).
À revérifier sur `main` une fois l'intégration faite (numéros de ligne de la branche).

**Branchées et utilisées** : hp, mp, mp_regen, atk, mag, atk_percent, mag_percent, crit, crit_dmg,
damage_percent, armor_pen, magic_pen, debuff_duration, def_percent, armor, magic_resist, damage_reduction,
block_chance, parry_chance (passifs seulement), effect_resist, flee, heal_power, shield_power, healing_received,
buff_duration, lifesteal, spell_vamp, thorns, cast_speed, cooldown_reduction.

### À corriger, par impact (ce qu'un joueur tire ou investit et qui ne fait rien)

1. **`attack_speed` : INERTE.** Lue seulement par l'intervalle d'attaque automatique, et les attaques automatiques
   sont coupées (`server-combat/config/combat.json:65`). Source : passifs de familier, procs, statuts. Bug d'unité
   en plus : `lround(attack_speed)` met 0,1 à 0 (`stat_calculator.hpp:157`). Brancher `haste` sur la recharge
   globale ou l'incantation, ou retirer la stat.
2. **`hit` (précision) : INERTE.** Vérifiée seulement quand la précision est sous 100, et la base vaut 100 ; pas de
   duel précision contre esquive (`damage_calculator.cpp:85-92`). Plus de 10 nœuds de passifs investissent dedans
   pour rien (ex. « précision +1,5 par niveau »). Coder la formule de definitions.json `80 + hit - flee`, ou retirer
   la précision des passifs et de la liste des uniques.
3. **`effect_chance` : sans effet en PvE.** Elle ne fait que baisser la `effect_resist` de la cible, et les monstres
   n'en ont pas (`status_manager.cpp:2036-2045`). Pourtant elle tombe en stat principale de collier (poids 15 %),
   en substat de bijou et en affixe. Donner une résistance aux effets aux monstres, ou en faire un bonus sur la
   chance d'appliquer. La borne 15-85 de la data n'est pas codée.
4. **`hp_regen` : inerte EN COMBAT.** Écrite dans `HealthComponent.regen_per_tick` sans lecteur pendant le combat
   (seul le Souffle a son tick, `room.cpp:1392`) ; elle marche hors combat (`health_coordinator.cpp:782`). Ajouter
   un tick de PV à côté du Souffle, ou l'afficher « hors combat ».
5. **`def` (flat) : presque inerte.** Le modèle de dégâts ignore `defense` (`damage_calculator.cpp:125-131`) ; elle
   ne sert qu'aux compétences qui scalent sur la défense. Elle est sur 48 objets du tournoi et 8 bonus de
   panoplie (35 à 75). Le point d'allocation, lui, marche (il va dans l'armure). Convertir en `armor` et étendre la
   garde de `test_fight_loot.cpp:735` aux panoplies et aux uniques.
6. **Passifs Restauration et Protection à moitié morts** (`p_common_restoration`, `p_common_warding`, familier
   `fp_mender`) : `add_percent` sur `heal_power` / `shield_power`, qui partent de 0, et le % est appliqué avant le
   flat (`shared/gameplay/passive_bonuses.hpp:70-95`) : la moitié en % ajoute toujours 0. Passer en `add_flat`.
7. **`double_hit_chance`** : ne se déclenche que sur `basic_attack`, que plus rien ne lance tout seul
   (`room.cpp:4515-4535`). L'étendre aux compétences ou l'assumer. `triple_hit_chance` : suivie mais aucune source.
8. **Plafonds de la data non appliqués au moment de l'utiliser** : cast_speed 50 (hors statut), lifesteal 50,
   blocage 75, parade 30, damage_percent 200. Durées des buffs et debuffs : 50 dans le code, 100 dans la data.
9. **Nettoyage** :
   - `tenacity` : champ 42 écrit mais jamais lu par le combat, pas de champ dans `ItemStatBonus`.
   - `shield_break` et `reflect` (stat plate) : aucun chemin depuis un objet (seulement le fichier mort de
     cristaux) ; `reflect_percent` passe par les procs uniquement.
   - `shield_pierce` : marquée « pending » dans definitions.json mais branchée en combat ; aucune source joueur.
   - Fiche de stats : n'affiche pas les épines, la réduction de dégâts ni le perce-bouclier de l'équipement
     (`economy_service.cpp:2823-2853`).
   - Copie `scaled_base` (`stat_calculator.hpp:432-467`) : oublie lifesteal, damage_percent et les % de base.
   - Bonus de monde (nourriture) : n'arrivent jamais en combat (seulement la fiche) : à décider.
   - Bloc `keystones` de `items/equipment.json` : lu par personne.
   - Sémantique : `heal_power` et `shield_power` agissent en multiplicateur %, pas en flat comme le dit
     definitions.json ; `hp_percent` est branché mais rien ne le tire.

## Proposition : 3 substats max au lieu de 4 (2026-10-18, à valider)

30 lignes au lieu de 40 sur les 10 pièces, chaque ligne compte plus et reste lisible ; cadenas 0 / 1 / 2.
Rareté : commun 1, peu commun 1, rare 2, épique 2-3, légendaire 3 (le légendaire se distingue par ses fourchettes
et ses affixes). L'objet parfait vient plus vite : compensé par la taille du pool (8 à 12) et le prix du cadenas.

## Questions ouvertes (à discuter en partant du principe que toutes les stats fonctionnent)

1. Valider les pools par emplacement (une stat à ajouter ou retirer ?).
2. Valider les plafonds « tout-en-un » du tableau des valeurs.
3. Multiplicateur du cadenas : ×1 / ×2 / ×4 / ×8 ?
