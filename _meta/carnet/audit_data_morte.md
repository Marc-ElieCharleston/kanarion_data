# Audit de la data morte, trompeuse ou en double (2026-10-14)

Lecture seule de data `vac_refactor-lot1` contre le serveur et les scripts du client (les `.tscn` / `.tres`
et un éventuel wiki externe n'ont pas été vus). Principes : [architecture_data.md](architecture_data.md).
Déjà traités : `config/combat.json`, `systems/social.json`, plafonds de stats, GCD (voir
[plafonds_stats.md](plafonds_stats.md)).

## Contradictions réelles (le plus urgent)

| # | Sujet | Ce qui se contredit |
|---|---|---|
| C1 | Taille de la banque | client 40 (`economy.json gold_sinks.storage`, bloc marqué mort) / serveur 200 (`storage.bank`) |
| C2 | Skills des monstres côté client | `monster_archetype_assignments.json` : les 19 entrées diffèrent de `monsters.json` ; 22 ids inexistants |
| C3 | `monster_skills_scaling.json` (47 Ko) | lu par le client, écrasé par `skills/monster_skills.json` : aucun effet |
| C4 | Bonus de groupe du loot | `loot_tables.multipliers` +5 %/joueur vs `rewards.json` 0,125 (le vrai) |
| C5 | Multiplicateurs élite / boss | `monster_variants` (« deprecated ») encore lus par presence si `MONSTER_SCALING_MODEL` est éteint ; contredisent le modèle |
| C6 | Récompenses élite | `monster_variants` xp 2 / or 2 / loot 1,7, non lus ; vrais : `rewards.json` |
| C7 | Composition des packs 5★ | `encounter_stars.composition_rules` vs `monster_variants.star_system` (le vrai) |
| C8 | Réapparition des monstres | `game.json` 90-180 s (non lu) vs config presence 60-180 s |
| C9 | Longueur du chat | client 200 (`game.json`) vs serveur 500 (config du service) |
| C10 | Nom / tag de guilde | data 24 / 4 (non lu), serveur 32 / 8, client 32 / 4 en dur |
| C11-12 | Rangs, XP, missions de guilde | `guilds.json` : ids de rang inversés, XP et missions périmées (vrais : `guild/*.json`) |
| C13 | Capture des familiers | table `familiar_balance.json` non lue, recopiée à la main dans `monsters.json` : 4 monstres divergent |
| C14-15 | Ancien équipement | `upgrade_system` 0,05/niv (vrai : 3 %) ; ancien modèle des pierres-clés dans `equipment.json` |
| C16-17 | Passifs innés, `status_effects.runtime` | constantes en dur dans `status_manager.cpp` ; `curse_dot` : formule de la data ≠ code |
| C18 | Effets de skills inexistants en jeu | `thorny_sprout`, `holy_strike` (effets vides), `counter_chance`, `reflects_damage`… |
| C19 | Croissance des stats | économie arrondit (`lround`), combat tronque : écarts (ex. guerrier atk +49 vs +39 au niv. 50) |
| C20 | 2 skills « maneuver » | sans `percent_per_level` : client +9 %/niv, serveur 0 |
| C21 | Classements | le client cherche des clés absentes de `leaderboards.json` |
| C22 | Onglet Reforge | `substat_crafting_system.json` (33 Ko) : schéma absent, onglet vide ; la sous-stat « Reflet » est là |

Valeurs en dur alors que la data les annonce : coût de téléportation (50 + **liste de zones en dur**), prix de
revente (0,35 écrit 3 fois, le serveur fait autrement), skills de départ, `combat_move`, commerce, duel.

## Fichiers morts

`config/balance_model.json` (69 Ko), `config/monster_archetypes.json`, `config/skill_templates.json`,
`entities/boss_mechanics.json` (chargé, jamais utilisé), `combat/los_abilities_ideas.json`, `systems/boutique.json`,
`systems/daily_rewards.json`, `ui/icons.json`, `items/currencies.json` (wiki ?), `config/monster_tiers.json`
(lu par le validateur seulement). Hors périmètre, à décider : `entities/x_companion.json` (lore).
Métiers (`professions*`, `profession_recipes`, `gather_nodes`) : conception, étiquetés honnêtement, gardés.

## Lots proposés (dans l'ordre)

1. Contradictions actives, petites et sûres : banque (C1), 2 skills maneuver (C20), taux de capture + contrôle
   (C13), `curse_dot` (C17).
2. Skills de monstres côté client : supprimer C2 et C3 (vérifier le chemin hors ligne).
3. Récompenses et loot : `loot_tables.multipliers`, `drop_chances_by_rarity` (rendre `chance` obligatoire),
   champs xp / or / loot de `monster_variants` (C4, C6).
4. Étoiles et variants (serveur) : vérifier `MONSTER_SCALING_MODEL` en prod, retirer le repli, fondre
   `encounter_stars.json` dans `monster_variants.star_system` (C5, C7).
5. Ancien équipement : C14, C15, C22 (avec l'onglet Reforge).
6. Guildes : `guilds.json` source des longueurs / niveau de création, service et client branchés (C10-12).
7. Valeurs de service → data (serveur) : réapparition, chat, téléportation, revente, duel.
8. Mécaniques en dur à brancher ou retirer : C16-C19, `combat_move`, `starter_loadouts`.
9. Fichiers morts (liste ci-dessus).
10. Clés mortes des fichiers vivants (`game.json`, `economy.json`, `pvp.json`, `skill_system.json`,
    `monster_ai.json`, `koro.json`, `enhancement_system.json`, `_summary` périmés…).
11. Classements : choisir un schéma (C21).

**Avancement (2026-10-14)** : lot 1, C1, C20 et C13 faits (data `vac_audit-lot1`) ; C13 : pas de jet de capture,
une empreinte lootée = le familier ; ce qui compte = % de loot du monstre + tirage de rareté. C17 fait : explosion de la malédiction =
50 % des dégâts infligés par ses ticks, à la fin naturelle (proprietaire). Lot 9 fait : 8 fichiers supprimés ;
restent `boss_mechanics` (client) et `currencies` (à décider).

Chaque lot se revérifie avant d'agir (lecteurs serveur + client) : les emplacements exacts sont dans le
rapport d'audit de la session du 2026-10-14.
