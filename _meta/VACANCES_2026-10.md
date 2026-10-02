# Vacances octobre 2026 — note de passation

Travail fait depuis le PC de la maison (2 → ~15 octobre 2026), pendant que le
travail en cours (quêtes, leveling, histoire, carte, Tanière des loups avec 5
nouveaux loups, lore) est resté NON POUSSÉ sur le PC du bureau.

Règles suivies :
- Une branche `vac_*` par sujet, partie de `master` / `main` au 2026-10-01
  (data `379afb4`, back `0318c5a`). **Rien n'est poussé, rien n'est fusionné.**
- Le PC de la maison n'a **pas de compilateur C++** : les branches `vac_*` du back
  sont écrites mais **jamais compilées ni testées**. Chaque message de commit dit
  quels tests lancer.
- Aucune modification des zones, quêtes, PNJ, carte, histoire, leveling (conflits
  avec le travail du bureau).

**La liste complète des tâches du retour est dans `_meta/TODO_RETOUR.md`** (tenue à jour).

À faire au retour : fusionner le travail du bureau, puis relire chaque branche
`vac_*`, compiler et lancer les tests du back, relancer les scripts de
`scripts/balance/` sur la version fusionnée.

## Branches

### Data (`kanarion_database`)

| Branche | Commit(s) | Contenu |
|---|---|---|
| `vac_koro` | `2ac06d9`, `3ae6682` | Cartes Koro tier 3 : `level_req` 60 (lu dans `config/skill_system.json`). Les compétences de familier sortent des Koro (`systems/koro.json` `excluded_skill_classes`), 2765 → 2100 cartes. À voir : joueurs qui possèdent déjà une carte Koro de familier. |
| `vac_familiar-ultimate-cd` | `c45ff74` | Les 9 ultimes de familier : recharge 12 → 30 s, incantation 2 s. |
| `vac_star-curve` | `3bb8a99` | Courbe des étoiles lissée (ATK par monstre 1 / 1.05 / 1.15 / 1.3 / 1.45 / 1.55, PV 5* 1.25, 4* = 5-6 monstres). Relancer le harness de taux de victoire du 2026-09-29. |
| `vac_balance-tools` | (cette branche) | Scripts d'analyse, tables, revue des 200 monstres (`_meta/refonte_monstres/`), cette note, `TODO_RETOUR.md`. |
| `vac_apply-monster-v2` | `e5c43b7` (script), `a0cab4b` (GÉNÉRÉ) | Branche de travail : tools + profils + `scripts/apply_monster_v2.py` et son résultat sur monsters.json / monster_skills.json / monster_species.json. Au retour : jeter le commit généré et relancer le script sur la data fusionnée. |
| `vac_archetype-profiles` | voir `git log` | Les 11 profils d'archétypes V2 dans `config/monster_scaling_model.json` : ATK et MAG séparés (le serveur doit lire `mag`), croissance des stats d'identité, défense raide x25 au niv. 100. |

### Back (`kanarion_back`) — NON COMPILÉ

| Branche | Commit | Contenu | Tests |
|---|---|---|---|
| `vac_familiar-xp-90` | `2feade31` | Familier : 90 % de l'XP de combat du joueur (100 % depuis le 2026-08-03). | ctest combat + familiar |
| `vac_poison-cap` | `1c45a99f` | Poison sur un MONSTRE plafonné à 50 % de max(ATK, MAG) de la source par stack et par tick (corrige `ks_util_venom_sting` sur les boss). Poison des monstres sur les joueurs inchangé (levier anti-tank). | `combat-tests --gtest_filter="*Poison*"` (nouveau test `PoisonDot_OnMonster_CappedBySourcePower`) |
| `vac_v2-monster-mag` | `3809a674` | Serveur V2, étape 1 : les monstres ont une puissance magique séparée de l'attaque (`mag` du profil d'archétype → `magic_power`) ; sans `mag` dans la data, comportement inchangé. Nouveau test `MonsterScalingModelMag`. | `ctest -R MonsterScaling` |
| `vac_defense-curve-test` | `06f3a72d` | Seuil du test `DefenseIsDecoupledFromOffense` adapté à la défense raide V2 (x25 au niv. 100). | `ctest -R MonsterScaling` |
| `vac_koro-shield-rank` | `09b388b1` | Bouclier d'une carte Koro proportionnel au rang. Les HoT ne bougent pas (leur durée porte déjà le rang). | `combat-tests --gtest_filter="*Koro*"` (nouveau test `KoroCard_ShieldAbsorbScalesWithRank`) |

## Décisions de design (avec le propriétaire, 2026-10-02)

**Rythme et but du jeu**
- Le but : descendre au sud vers la cause des Fissures. La carte est petite : le danger
  doit monter fort vers le sud, et pousser à s'optimiser avant d'avancer.
- Niveau max en 2 semaines à 1 mois, sans énergie ni mécanique mobile abusive.
- Niveaux 1-10 faisables sans équipement ; ensuite il faut regarder le butin et
  l'hôtel des ventes. Si on tue trop vite, on ne regarde jamais les objets.
- Un monstre du même niveau peut être "trop dur" plutôt que trop facile. Un niveau 80
  bien équipé peut battre un niveau 100 ; un niveau 10 ne bat pas un niveau 30.
- Contenu horizontal : tout est disponible dès le niveau 10. Équipement plafonné au rang V.
  Le Paragon prévu après 100 est vertical : chercher une alternative horizontale.

**Puissance du joueur** (audit 2026-10-02, M = sqrt(dégâts × survie))
- Déblocages confirmés : keystones 30/50/70/100, Koro 40/80, emplacements de
  compétence du familier 2/3/4/5 aux niveaux 1/20/50/100.
- Passifs ≈ x1,3 max. Keystones typique x1,02-1,11, optimisé x1,1-1,6. Koro typique
  x1,1, 2 SS x1,7-1,9. Familier x1,5-2,0 (surtout des PV ; ses dégâts = 16-31 % d'un joueur).
- Les mercenaires sont faibles par design : budget = joueur + familier.
- Les familiers sont centraux (façon Canaan Online) : on choisit l'espèce à capturer
  selon le rôle voulu (un golem pour un tank).
- À FAIRE : aujourd'hui les 134 familiers (`entities/familiars.json`) ont un champ
  `species` (65 espèces fines) mais des stats identiques par rôle. Voulu : le familier
  hérite de l'identité de son espèce (`SPECIES_IDENTITY` de `species_table.py`) — une
  espèce à forte RM se capture pour jouer contre des mages. Il faut une table espèce de
  familier → espèce de monstre et un changement dans le service des familiers.
- PixelLab est disponible pour créer de nouveaux monstres (archétypes ou espèces manquants).

**Monstres — formule**
```
stat = stats de base de l'ESPÈCE (niv. 1, archétype compris)
     × croissance par niveau (courbes de config/monster_scaling_model.json)
     × palier (fodder / standard / tough / élite / boss)
     × étoiles (entities/monster_variants.json)
     × contenu (tour : +6 %/étage après 40 ; faille : +1 étoile ; donjon : niveau de l'étage)
```
- Monstre = espèce × stade (préfixe : jeune/larve x0,7, alpha x1,3, géant x1,5…) ×
  archétype du rôle (rat mage, rat soigneur…).
- Les stats d'identité (crit, dégâts crit, pénétrations, perce-bouclier, esquive,
  blocage, parade, ténacité, vol de vie, renvoi) ne suivent pas la courbe : elles
  montent par l'archétype, tous les 10 niveaux, plafonnées.
- On garde la GROSSE courbe (PV x800 au niveau 100) ; on nerfera si c'est trop dur.
- Souffle des monstres : infini (ou retiré). Pas de plafond de composition de pack :
  les joueurs s'adaptent (anti-soin, assassins qui plongent sur la ligne arrière).
- Interrupteur `MONSTER_SCALING_MODEL` (désactivé par défaut, absent des dépôts) :
  désactivé = `base_stats` faits main sans montée en niveau ; activé = archétype seul
  (toutes les brutes identiques). La V2 lit les stats d'espèce : changement serveur à faire.

**11 archétypes** : tank, gardien (bouclier de zone, réduction de dégâts en zone),
brute (frappe très fort, pénètre), berserker (vol de vie, enrage), assassin (plonge sur
la ligne arrière), archer, mage (burst, longues incantations à interrompre), contrôleur
(contrôles, anti-soin, dissipation), soigneur, invocateur (monstres temporaires
seulement), enchanteur (buffs, ex-support).

**Compétences des monstres**
- Avant le niveau 40 : normal (fodder/standard/tough) 2, élite 3, boss 4.
- À partir du niveau 40 : normal 3 (la 3e = effet d'identité de l'archétype, longue
  recharge, incantation visible), élite 4, boss 4 + une mécanique de phase.
- Donner aux monstres les outils anti-sustain que les joueurs ont déjà : réduction de
  soin, dissipation, vol de buff, brise-bouclier, silence, drain de Souffle, coups en
  % de PV max. L'érosion demande du code serveur.

**Familiers**
- 90 % de l'XP de combat du joueur, pas l'XP de quête ni de succès, doit être en combat.
- Ultimes : 30 s de recharge, 2 s d'incantation. Les autres compétences gardent 4-5 s
  (le familier n'a pas d'attaque de base).

## Bugs et abus repérés, pas encore corrigés

- Familiers : 21 des 31 passifs sans effet en combat ; compétences sans montée par
  niveau ; deux espèces du même rôle ont les mêmes stats.
- Keystones : `ks_support_harmony_*` (recharge 0, boucliers/soins de groupe sans plafond).
- Koro : boucliers `shield_def` décrits en "% PV max" alors que le serveur calcule
  sur la DEF.
- `entities/boss_mechanics.json` n'est lu par aucun serveur (données mortes).
- Test du back `test_player_reference_curve.cpp` : n'applique jamais les passifs communs
  (cherche la clé `passives`, le fichier utilise `common_passives`).
- Pré-existant sur `master` : `validate_skills.py` → 129 erreurs de liste blanche ;
  `gen_pet_books.py --check` → descriptions périmées.

## Scripts (`scripts/balance/`)

| Script | Sortie | Rôle |
|---|---|---|
| `pve_matrix.py` | `out/pve_matrix.csv` | Joueur de base (stats + équipement mal / moyen / ultra) contre monstres du modèle, niveaux 10-100 : temps pour tuer / pour mourir, puissance manquante M, pression de pack. |
| `monster_stats_v2.py` | `out/monster_stats_v2.csv` | Proposition V2 : stats niveau 1 par espèce (facteur d'espèce vs archétype et palier), croissance des stats d'identité par archétype, ratio par niveau. |
| `monster_review.py` | `out/monster_review.csv` | Revue des 200 monstres : espèce, stade, rôle, archétype proposé (11), nombre de compétences visé, alertes. Vérifié sur les portraits du client pour 6 cas. |
| `species_table.py` | `out/species_table.csv`, `out/species_monsters.csv` | 45 espèces (liste écrite à la main), identité PROPOSÉE par espèce (`SPECIES_IDENTITY` : PV / ATK / armure / RM + bonus d'identité, ex. golem armure x1,5 blocage +10, spectre armure x0,5 RM x1,5), avec les valeurs mesurées sur la data actuelle à côté, puis stats niveau 1 et PV aux niveaux 1/10/40/70/100 de chaque monstre. Les 4 nouveaux archétypes utilisent provisoirement le profil le plus proche (gardien→tank, berserker→brute, soigneur/enchanteur→support, invocateur→mage). |

Démarche : on relit les tableaux, puis un script appliquera les décisions à
`entities/monsters.json` — relançable après la fusion du travail du bureau, plutôt que
de fusionner 200 monstres à la main.
