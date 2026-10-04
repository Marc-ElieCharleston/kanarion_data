# Équipement : stats, rareté, rang, forge

Statut : **les 5 décisions sont validées** par le propriétaire (2026-10-04) et en cours d'implémentation
sur les branches `vac_equipment` (data et back). Inventaire fait sur data master `379afb4`, back `main`.

## Avancement (2026-10-04)

| # | Sujet | Data (`vac_equipment`) | Serveur | Test |
|---|---|---|---|---|
| 2 | Rareté resserrée (légendaire ~2× commun, ancrée sur l'épique) | `68ec258` | — | à lancer (loot) |
| 4 | Pénétration (épique T5 14-17 en substat, bijoux, affixes 3-6, panoplies B 8 → SS 20) | `f223a27` | — | à lancer (loot) |
| 1 | Courbe continue (`tier_system.level_curve`) | `9ba8e02` | `555df005` | `EquipmentLevelCurve.*` |
| 3 | Forge : or par tentative 50 / 200 / 600 / 1500 / 4000, règle +5 % morte marquée | `b14d04e` | `8bfef8ed` | `EnhancementRules.GoldCost*` |
| 5 | Artisanat : tirage comme le loot, plancher de rareté par rang de métier | `8543127` | en cours (`vac_craft-rolls`) | à venir |
| — | Recaler la courbe de référence du joueur | — | à faire | — |


## Ce qui est fait

- **130 modèles de base** (`items/equipment.json`, écrits à la main) : 30 armes (6 types × 5 bandes),
  90 armures (6 emplacements × 3 poids × 5 bandes), 10 bijoux. Bande `bN` = rang : b1 = C (1-20) …
  b5 = SS (81-100).
- **Tirage complet** au loot : stat principale + substats (pondérées par rôle) + affixes (14 préfixes,
  16 suffixes), fourchettes par rareté (`items/equipment_stats.json`), paliers T1-T5
  (`items/equipment_scaling.json`).
- **25 panoplies** par bande, **43 uniques** avec valeurs par rang, 150 keystones.
- **Forge +1 à +20** de bout en bout (`systems/enhancement_system.json`, serveur economy, testée) :
  +3 % par niveau, 4 pierres, taux 90 % → 20 %, l'échec ne coûte que la pierre.
- Toutes les stats arrivent au combat, avec plafonds (pénétration 70).

## Ce qui est partiel ou incohérent

1. **Escalier par bande** (×1 / 1,5 / 2 / 2,8 / 4) : un objet niv. 21 = un objet niv. 40. Entre T4 et
   T5, +43 % seulement, alors que les monstres prennent bien plus.
2. **La rareté** change fortement la stat principale (PV T1 : commun 25-28, légendaire 114-120), le
   nombre de substats et d'affixes, mais **pas la base de l'objet ni la valeur des affixes**. Le
   multiplicateur 1,0-2,0 codé en dur ne sert qu'au prix de revente.
3. **Forge** : seules base + stat principale montent ; substats et affixes jamais. Deux règles
   contradictoires (3 % lue, 5 % morte dans `equipment_stats.json` `upgrade_system`). Pas de coût en or.
4. **Pénétration** : max ≈ 14 % via l'équipement classique, **quasi nulle face à la défense V2**
   (×25 au niv. 100). Panoplie gevurah (B) 23 > toutes les SS.
5. **Équipement fabriqué** : créé **sans aucun tirage** (une épée b5 forgée = ATK 60, contre ~196 pour
   une légendaire lootée). Le rang de qualité C-SS des métiers V2 n'a pas de stats.
6. **Contenu** : recettes seulement b1, b3 (b5 armes), aucun bijou ni sceptre ; un seul modèle
   d'anneau et de collier par bande ; un seul unique d'arme ; 4 sets SS.
7. **Courbe de référence** (`test_player_reference_curve.cpp`) : ne compte que la stat principale et
   les substats (ni base, ni affixes, ni forge, ni sets) → les monstres sont calibrés sur un joueur
   sous-estimé.
8. Données mortes : `upgrade_system`, `substat_upgrade_chance`, `set_signatures`,
   `substat_crafting_system.json` (relance de substats, rien côté serveur). `CLAUDE.md:122` dit à tort
   que `base_stats` n'est jamais lu.

## Décisions à prendre (recommandations du 2026-10-04)

1. **Courbe** : escalier ou montée continue avec le niveau de l'objet ? *Recommandé* : continue
   (interpolée entre les bandes), pour suivre la courbe des monstres ; la bande garde le rang et le
   visuel.
2. **Rareté** : *recommandé* : ne PAS ajouter de multiplicateur sur la base (elle compte déjà
   énormément sur la stat principale : ×4,3 entre commun et légendaire) ; plutôt **resserrer l'écart**
   (progression horizontale) et sortir le 1,0-2,0 du code.
3. **Forge** : *recommandé* : garder 3 % (lu, testé), supprimer le 5 % mort ; **ajouter un coût en
   or** (puits d'économie) ; pas de casse (frustrant sur mobile).
4. **Pénétration face à V2** : *recommandé* : viser ~30-40 % au niv. 100 en cumulant arme, bijoux,
   sets, passifs et soutiens ; corriger gevurah ; **à régler avant de fusionner V2 sur master**.
5. **Craft** : *recommandé* : les objets fabriqués tirent leurs stats comme le loot, et **le rang du
   métier (C-SS) relève la rareté minimale ou la fenêtre de tirage** (pas un multiplicateur) : les
   artisans deviennent utiles à l'économie. Puis recaler la courbe de référence.

Lien : [loot.md](loot.md) (rythme : ne pas être équipé trop vite).
