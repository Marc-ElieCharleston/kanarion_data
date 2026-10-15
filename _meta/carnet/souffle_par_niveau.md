# Souffle : régénération et coût des sorts

Statut : appliqué le 2026-10-15 (branche `vac_souffle-scaling`).
Demandes du propriétaire : « mettre du Souffle en fonction de la puissance du sort », sans qu'un sort
coûte tout le Souffle, sans spam infini ; « corriger la stat de regen de souffle en combat (pas hors
combat ?) » ; « les skills de base coûtent forcément moins que les skills de spécialisation ».
Règles : `config/skill_system.json` `mana_cost_scaling` (coûts), `items/equipment_scaling.json`
`tier_system.rate_stats_no_tier_scaling` (régénération d'équipement).
Outil : `scripts/balance/souffle_per_level.py` (`--check` en CI, `--report`, `--budget`).
Régénération hors combat et pass : `stats/definitions.json` (`hp_regen_out_of_combat`, `mp_regen_out_of_combat`),
`systems/premium.json` `benefits.out_of_combat_regen_multiplier` (section 1 bis).

## 1. Les sources de régénération, en combat et hors combat

Code lu sur la branche back `vac_doublons-lot2`. En combat, la room ajoute `ManaComponent.regen_per_tick`
à chaque tick (`room.cpp` `process_cooldowns`). Hors combat, l'économie ajoute chaque seconde
`stats_profile_snapshot.stats.mp_regen` aux personnages connectés (`health_coordinator.cpp`
`apply_regen_tick`, SQL ligne 783) ; en fin de combat, `persist_post_combat` écrase le Souffle par la
valeur de la room, donc ce tick ne compte pas pendant un combat.

| source | data | en combat | hors combat |
|---|---|---|---|
| Base de classe | `class_base_stats.json` `mp_regen` (1/s, six classes) | oui (`combat_profile_builder.cpp:221`) | oui (`combat_stat_snapshot_builder.hpp:74`) |
| Croissance | `class_growth.json` `mp_regen` (0) | oui, × (niveau − 1) depuis le 2026-10-15 (avant : ignorée) | oui, × (niveau − 1) (avant : une seule fois) |
| Équipement : sous-stats, stat principale, affixes | `equipment_stats.json` plage `mp_regen`, `affixes.json` | oui (`room.cpp:7055`, `mp_regen_bonus`) | oui (même total) |
| Équipement : stat fixe des modèles (ceintures légères 1 à 2) et uniques (3 à 5) | `equipment.json`, `uniques.json` | oui | oui |
| Panoplies | `panoplies.json` (Nefesh +1, Neshamah +7, Refuah +3, tournoi +1) | oui | oui |
| Passifs | Souffle profond 0,05/rang, Respiration (arbre) 0,1/rang, Mélodie inspirante 0,4/rang, Voix harmonique 0,3/rang | oui, valeur exacte (`combat_profile_builder.cpp:326`) | oui, mais la part plate est **arrondie à l'entier inférieur** (`passive_materializer.hpp`) : Souffle profond et Respiration valent 0 hors combat |
| Keystones | `systems/keystones.json` : rendre un % du Souffle au kill ou à la cible d'un soin, prochain sort gratuit | oui (procs) | non |
| Familiers | Sérénité +2/s : Souffle **du familier** ; sorts de familier « Régen Souffle » sur les alliés (statut) | oui | non (le tick du familier ne remplit que sa propre réserve, `familiar_service.cpp:2528`) |
| Sorts | `mana_restore` (Partage de Souffle), statut `mana_regen` (Hymne de vigueur), `mana_steal` | oui | non |
| Potions de Souffle I à V | `consumables.json` | non (pas d'action objet en combat) | oui |

**Réponse à la question du propriétaire.** C'est **la même stat** (`mp_regen`) qui sert en combat et
hors combat : base, équipement, panoplies et passifs alimentent les deux. La PV, elle, ne se régénère
que hors combat (la room calcule `health.regen_per_tick` mais ne l'applique jamais). Baisser la
régénération de Souffle en combat allonge donc aussi l'attente entre deux combats (colonne « plein
hors combat » plus bas : 44 s → 107 s pour un mage niveau 100). Les potions servent justement à couper
cette attente.

## 1 bis. Régénération hors combat (décision du 2026-10-15, appliquée)

Le propriétaire : « de base c'est la même stat, mais si j'ajoute des buffs hors combat […] créer une stat
dédiée qui aura la regen souffle + la regen hors combat souffle ». `mp_regen` reste **la** stat de
régénération, en combat comme hors combat. Hors combat seulement, une stat dédiée par ressource s'y ajoute :

    regen hors combat = (regen + bonus plat hors combat) × (1 + bonus % hors combat / 100)
    gain par seconde  = regen hors combat × multiplicateur du pass (abonné seulement)

- Stats (`stats/definitions.json`, catégorie `resources`) : `hp_regen_out_of_combat` et
  `mp_regen_out_of_combat`, `bonus_type: both`. Le bonus plat et le bonus % sont les deux modes d'un buff
  monde sur cette stat (`stats/world_buffs.json`, `mode: flat | percent`) : nourriture, buffs futurs. Aucune
  source n'en donne encore ; sans bonus, la stat vaut `hp_regen` / `mp_regen`.
- Pass Kanarion : `systems/premium.json` `benefits.out_of_combat_regen_multiplier` = **2**, PV et Souffle
  (décision du carnet `pass_premium.md`, confirmée le 2026-10-15). Le fichier suit le schéma de
  `_meta/conception_systemes/PASS_PREMIUM.md` 3.1, réduit aux avantages qui ont une valeur décidée.
- Serveur (back `vac_doublons-lot2`) : la formule vit une fois dans `shared/gameplay/out_of_combat_regen.hpp`
  (lecture stricte de `premium.json`, refus au démarrage si la clé manque) ; le builder de stats l'écrit dans
  le profil (`stats.mp_regen_out_of_combat`) ; `HealthCoordinator::apply_regen_tick` lit ces deux clés
  (obligatoires, `health/regen_tick.hpp`) et applique le pass. Le combat ne lit rien de tout cela.
- **Le droit au pass n'existe pas encore côté serveur** (pas de `accounts.premium_until`) : la règle prend un
  booléen par personnage, et personne n'a le bonus tant que le droit n'est pas branché.
- Rejeté : un plancher de régénération en % du Souffle max (ancienne proposition de cette note) ; le
  propriétaire garde une seule stat.

## 2. La régénération corrigée

**Cause.** `mp_regen` prenait le multiplicateur des stats brutes (`level_curve.stat`, ×1 au niveau 10,
×4,6 au niveau 100), alors que c'est un taux par seconde. Les stats en taux ont déjà leur courbe douce
(`level_curve.rate`, ×1,65 au niveau 100), lue par `StatRoller` pour la stat principale, les sous-stats
et les affixes, à l'objet looté comme fabriqué.

**Correction (une ligne de data) :** `mp_regen` ajouté à `rate_stats_no_tier_scaling`. Régénération
d'un équipement attendu (commun +0 jusqu'au niveau 20, rare +5 ensuite) :

| armure | niv 1 | niv 20 | niv 40 | niv 60 | niv 100 |
|---|---|---|---|---|---|
| légère (mage, soigneur) | 3 → 3 | 3 → 3 | 11 → 7 | 17 → 10 | 31 → 12 |
| moyenne | 1 → 1 | 1 → 1 | 5 → 4 | 6 → 4 | 11 → 5 |
| lourde | 1 → 1 | 2 → 2 | 5 → 4 | 7 → 5 | 12 → 5 |

Les objets déjà tirés gardent leur valeur (stockée dans l'instance).

Le modèle de budget lisait les paliers en escalier ; il suit maintenant `level_curve` comme le serveur
(`pve_matrix.Gear.tier_mult`). Les chiffres « avant » ci-dessous sont recalculés avec ce modèle corrigé.

## 3. Le budget, avant et après

Souffle max = base de classe + croissance + équipement attendu ; régénération = base de classe +
équipement (sans passif, sans panoplie, sans unique). « Plein hors combat » = Souffle max divisé par
`mp_regen_out_of_combat` (sans buff hors combat, donc égal à la régénération), sans puis avec le pass. Points de stats : 0 en Souffle ou 1 point sur 3
par niveau (+5 par point). Rangs de sorts : niv 20 = base 4 ; niv 40 = base 6, tier 2 rang 2 ;
niv 60 = base 8, tier 2 rang 4 ; niv 100 = base 8, tier 2 et tier 3 rang 6.
Durées : PV des monstres (`monster_scaling_model.json`, médiane des 7 archétypes) divisés par les
dégâts du joueur de référence (`level_curve.calibration`), 1 action par GCD de 2 s. Pack = 2-3
monstres standard en solo ; élite = 1 élite + 2 standard en solo ; boss = boss de donjon en groupe de
3 ; 5★ = 1 boss + 3 élites + 5 standard (+25 % PV) en groupe. Sans familier ni mercenaire.
« Rotation » = Souffle par seconde quand on lance, à chaque GCD, le sort prêt le plus cher
(remplissages en dernier) : un plafond de dépense. « À sec » = temps avant que cette rotation ne soit
plus finançable ; on retombe alors sur les remplissages et ce que la régénération paie. « Tient un
pack » : à sec après la fin d'un pack (0 point). « Sec sur combat long » : à sec avant la fin d'un
élite ou d'un 5★. Médianes sur les 8 spécialisations de chaque classe. « Avant » = commit `59bbf97` ;
« après » = régénération en taux et coûts de la section 4.

**Niveau 20** (pack 46 s, élite 77 s, boss 25 s, 5★ 120 s)

| classe | Souffle (0 pt / 1 pt) | regen /s | rotation /s | à sec, 0 pt | à sec, 1 pt | tient un pack | sec sur combat long | plein hors combat |
|---|---|---|---|---|---|---|---|---|
| Guerrier | 79 / 174 | 3 → 3 | 5,7 → 5,7 | 29 s → 29 s | 64 s → 64 s | non → non | oui → oui | 26 s → 26 s |
| Mage | 305 / 400 | 4 → 4 | 9,5 → 8,6 | 55 s → 66 s | 72 s → 86 s | oui → oui | oui → oui | 76 s → 76 s |
| Soigneur | 298 / 393 | 4 → 4 | 11,8 → 11,8 | 38 s → 38 s | 50 s → 50 s | non → non | oui → oui | 74 s → 74 s |
| Archer | 134 / 229 | 2 → 2 | 6,1 → 6,1 | 33 s → 33 s | 56 s → 56 s | non → non | oui → oui | 67 s → 67 s |
| Voleur | 110 / 205 | 2 → 2 | 7,3 → 7,3 | 21 s → 21 s | 39 s → 39 s | non → non | oui → oui | 55 s → 55 s |
| Artisan | 134 / 229 | 2 → 2 | 6,5 → 6,5 | 30 s → 30 s | 52 s → 52 s | non → non | oui → oui | 67 s → 67 s |

**Niveau 40** (pack 80 s, élite 134 s, boss 43 s, 5★ 208 s)

| classe | Souffle (0 pt / 1 pt) | regen /s | rotation /s | à sec, 0 pt | à sec, 1 pt | tient un pack | sec sur combat long | plein hors combat |
|---|---|---|---|---|---|---|---|---|
| Guerrier | 147 / 342 | 6 → 5 | 12,0 → 12,0 | 25 s → 21 s | 58 s → 49 s | non → non | oui → oui | 25 s → 29 s |
| Mage | 586 / 781 | 12 → 8 | 15,1 → 14,2 | 190 s → 94 s | 252 s → 126 s | oui → oui | oui → oui | 49 s → 73 s |
| Soigneur | 579 / 774 | 12 → 8 | 19,1 → 18,9 | 82 s → 53 s | 109 s → 71 s | oui → non | oui → oui | 49 s → 72 s |
| Archer | 243 / 438 | 6 → 5 | 12,4 → 12,4 | 38 s → 33 s | 68 s → 59 s | non → non | oui → oui | 40 s → 49 s |
| Voleur | 199 / 394 | 6 → 5 | 13,7 → 13,2 | 26 s → 24 s | 51 s → 48 s | non → non | oui → oui | 33 s → 40 s |
| Artisan | 243 / 438 | 6 → 5 | 12,5 → 12,5 | 37 s → 32 s | 67 s → 58 s | non → non | oui → oui | 40 s → 49 s |

**Niveau 60** (pack 98 s, élite 164 s, boss 52 s, 5★ 254 s)

| classe | Souffle (0 pt / 1 pt) | regen /s | rotation /s | à sec, 0 pt | à sec, 1 pt | tient un pack | sec sur combat long | plein hors combat |
|---|---|---|---|---|---|---|---|---|
| Guerrier | 188 / 483 | 8 → 6 | 12,7 → 12,7 | 40 s → 28 s | 102 s → 72 s | non → non | oui → oui | 23 s → 31 s |
| Mage | 786 / 1081 | 18 → 11 | 16,1 → 15,0 | jamais → 196 s | jamais → 269 s | oui → oui | non → oui | 44 s → 71 s |
| Soigneur | 779 / 1074 | 18 → 11 | 20,4 → 20,6 | 322 s → 81 s | 444 s → 112 s | oui → non | non → oui | 43 s → 71 s |
| Archer | 322 / 617 | 7 → 5 | 13,2 → 13,2 | 52 s → 39 s | 100 s → 75 s | non → non | oui → oui | 46 s → 64 s |
| Voleur | 258 / 553 | 7 → 5 | 14,6 → 14,2 | 34 s → 28 s | 72 s → 60 s | non → non | oui → oui | 37 s → 52 s |
| Artisan | 322 / 617 | 7 → 5 | 13,6 → 13,6 | 49 s → 37 s | 93 s → 72 s | non → non | oui → oui | 46 s → 64 s |

**Niveau 100** (pack 260 s, élite 437 s, boss 139 s, 5★ 676 s)

| classe | Souffle (0 pt / 1 pt) | regen /s | rotation /s | à sec, 0 pt | à sec, 1 pt | tient un pack | sec sur combat long | plein hors combat |
|---|---|---|---|---|---|---|---|---|
| Guerrier | 303 / 798 | 13 → 6 | 18,4 → 17,6 | 57 s → 26 s | 149 s → 69 s | non → non | oui → oui | 23 s → 51 s |
| Mage | 1394 / 1889 | 32 → 13 | 20,5 → 19,4 | jamais → 218 s | jamais → 295 s | oui → non | non → oui | 44 s → 107 s |
| Soigneur | 1387 / 1882 | 32 → 13 | 23,8 → 23,3 | jamais → 135 s | jamais → 183 s | oui → non | non → oui | 43 s → 107 s |
| Archer | 558 / 1053 | 12 → 6 | 18,3 → 17,6 | 89 s → 48 s | 168 s → 91 s | non → non | oui → oui | 47 s → 93 s |
| Voleur | 454 / 949 | 12 → 6 | 19,0 → 17,7 | 65 s → 39 s | 136 s → 81 s | non → non | oui → oui | 38 s → 76 s |
| Artisan | 558 / 1053 | 12 → 6 | 18,7 → 18,1 | 83 s → 46 s | 157 s → 87 s | non → non | oui → oui | 47 s → 93 s |

Niveau 1 : Souffle 60 (guerrier) à 229 (mage), régénération 2 à 4/s, aucun changement.

Ce que dit le budget :
- **Plus aucune classe n'est inépuisable.** Mage et soigneur, « jamais à sec » aux niveaux 60 et 100,
  le sont maintenant en 1 à 4 minutes de rotation soutenue, avant la fin d'un élite ou d'un 5★, à
  tous les niveaux. Le mage tient encore un pack aux niveaux 20 à 60.
- **Classes martiales et soigneur : à sec avant la fin d'un pack**, déjà avant ce changement (sauf le
  soigneur aux niveaux 40-60). La correction l'aggrave aux niveaux 60-100 (le guerrier niveau 100 :
  57 s → 26 s). Ce n'est pas la régénération d'équipement qui peut le régler sans rendre les lanceurs
  inépuisables : pour tenir un pack de 260 s avec 303 de Souffle, un guerrier devrait régénérer 93 à
  96 % de sa rotation. Voir la question 1.
- Le pack du niveau 100 dure 260 s en solo (52 GCD par monstre standard) : à ce niveau, toute classe
  est à sec avant la fin d'un pack, quelle que soit la réserve. Voir la question 2.

### Hors combat et panoplie (`--budget`, 2026-10-15)

« Plein » : temps pour remplir le Souffle à vide hors combat, sans puis avec le pass (×2). « Panoplie » : la
panoplie de Souffle la plus forte que le niveau permet de porter, set complet (Nefesh +1/s jusqu'au niveau 80,
Neshamah +7/s ensuite), ajoutée à la régénération : régénération, à sec (0 pt), tient un pack.

| classe | plein, niv 20 | plein, niv 60 | plein, niv 100 | panoplie niv 40 | panoplie niv 60 | panoplie niv 100 |
|---|---|---|---|---|---|---|
| Guerrier | 26 s / 13 s | 31 s / 16 s | 51 s / 25 s | 10/s, 75 s, non | 11/s, 108 s, oui | 41/s, jamais, oui |
| Mage | 76 s / 38 s | 71 s / 36 s | 107 s / 54 s | 13/s, 484 s, oui | 16/s, jamais, oui | 48/s, jamais, oui |
| Soigneur | 74 s / 37 s | 71 s / 35 s | 107 s / 53 s | 13/s, 97 s, oui | 16/s, 169 s, oui | 48/s, jamais, oui |
| Archer | 67 s / 34 s | 64 s / 32 s | 93 s / 47 s | 10/s, 100 s, oui | 10/s, 101 s, oui | 41/s, jamais, oui |
| Voleur | 55 s / 28 s | 52 s / 26 s | 76 s / 38 s | 10/s, 62 s, non | 10/s, 61 s, non | 41/s, jamais, oui |
| Artisan | 67 s / 34 s | 64 s / 32 s | 93 s / 47 s | 10/s, 96 s, oui | 10/s, 89 s, non | 41/s, jamais, oui |

## 4. Le coût des sorts

### Règle par rang (inchangée, étendue au tier 3)

    mana_cost_per_level = arrondi( mana_cost × (G − 1) / 9 )

G est le gain de puissance du sort entre le rang 1 et le rang 10, lu dans ses propres champs par rang :
`percent_per_level` sur `scaling_percent` ou `heal_scaling_percent`, et pour chaque effet
`pct_per_level`, `value_per_level`, `duration_per_level` (multipliés entre eux) ; on garde le plus fort.
Au rang 10 le sort coûte `mana_cost × G` : le Souffle payé par unité d'effet est le même à tous les
rangs. Un rang rend le sort plus fort et plus gourmand, pas plus rentable.

Tier 3, ce qui a changé :
- **181 sorts reçoivent `rank_scaling_enabled`** : tous les sorts de spécialisation qui portent
  `percent_per_level`. Sans ce champ, le serveur ignorait le gain par rang (`room.cpp`
  `effective_scaling`, tant que `BE1_PER_LEVEL_SCALING` est coupé) alors qu'il faisait payer le rang,
  et le client affichait déjà ce gain. La base et le tier 2 l'avaient depuis la passe des classes.
  Gain au rang 10 : ×1,6 à ×1,7.
- **Les sorts hors signature suivent la règle** : +1 à +3 par rang au lieu de +2 à +4.
- **Les 16 sorts qui payaient par rang sans rien gagner** passent à 0. Les 2 sorts à 0
  (`fate_gambler_double_or_nothing`, `guitarist_clear_chorus`) n'ont aucun champ par rang : 0 est
  la bonne valeur.
- Les signatures qui gagnent ×1,7 ne bougent pas (75 à +6, 52 à +4) ; celles à 68 passent de +6 à +5.
  Quatre signatures du guerrier (Dernier Bastion, Phalange, Appel à la Gloire, Règne de Terreur) et
  Riposte Parfaite du voleur gagnent ×1,22 à ×1,27 : +6 → +2 et +4 → +1. Forteresse Sylvestre et
  Forteresse Vivante ne gagnent rien : +6 → 0.
- 4 sorts dont le gain est trop faible pour un point entier passent de +2 à 0.

### Base < sous-classe < spécialisation, à rôle égal

Familles (`tier_order.families`) : **signature** ; **remplissage** (tier `filler`, ou tag `filler` :
les 40 sorts de spécialisation à 8-18 de Souffle et 9-15 s de recharge) ; **courant** (le reste). Il
n'y a pas de famille « ultime » dans la data : la signature en tient lieu.

**Règle (`tier_order`) :** au rang 1, un sort coûte strictement moins que le sort le plus cher de sa
famille au tier supérieur le plus proche qui en a un (un sort de base face à toute sa classe, un sort
de sous-classe face à ses deux spécialisations). Au-dessus, son `mana_cost` est ramené à ce plafond
moins 1 ; son coût par rang suit ensuite la règle de puissance. `--check` vérifie en plus que la
médiane de chaque famille croît strictement d'un tier à l'autre, au rang 1 et au rang 10.

Les 19 écarts corrigés :

| sort | tier, famille | plafond | coût |
|---|---|---|---|
| Requiem (Cantor) | sous-classe, signature | Jugement Divin 75 | 98 → 74 |
| Vague Rédemptrice (Martyr) | sous-classe, signature | Frappe Rédemptrice 75 | 82 → 74 |
| Tempête Élémentaire, Bénédiction de la Nature, Absolution | sous-classe, signature | signatures de spécialisation 75 | 75 → 74 |
| Grande Arnaque, Raid Pirate, Coup de Grâce (voleur) | sous-classe, signature | signatures de spécialisation du voleur 52 | 68, 57, 54 → 51 |
| Cataclysme Arcanique (mage) | base, courant | Barrage de Cartes 42, lui-même ramené à 41 | 52 → 40 |
| Barrage de Cartes (Cardmaster) | sous-classe, courant | Carte Maîtresse 42 | 42 → 41 |
| Sanctuaire, Soin Radieux (Lightbringer) | sous-classe, courant | Sanctification 42 | 52, 45 → 41 |
| Régénération (Lifewarden) | sous-classe, courant | Réveil Naturel 45 | 45 → 44 |
| Frappe Ardente (Martyr) | sous-classe, courant | Voie du Martyr 42 | 42 → 41 |
| Disparition, Assassinat (Shadowblade) | sous-classe, courant | Brise-Sort 39 | 42 → 38 |
| Désarmement, Diversion (Trickster) | sous-classe, courant | Brise-Garde Sale 33 | 33, 38 → 32 |
| Riposte (Duelist) | sous-classe, courant | Tourbillon de Lames 33 | 33 → 32 |

Coût par famille et par tier, médiane (min-max), après :

| famille | rang | base | sous-classe | spécialisation |
|---|---|---|---|---|
| remplissage | 1 | 6,5 (6-8) | 9 (6-10) | 15 (8-18) |
| remplissage | 10 | 6,5 (6-8) | 9 (6-10) | 21 (15-27) |
| courant | 1 | 27 (18-40) | 30 (15-44) | 33 (12-45) |
| courant | 10 | 36 (18-63) | 39 (15-65) | 51 (15-72) |
| signature | 1 | | 60 (51-74) | 75 (52-75) |
| signature | 10 | | 78 (57-141) | 129 (61-129) |

Au rang 10, 23 sorts restent plus chers que tout leur tier supérieur dans un kit (`--report`) : la
règle de puissance l'emporte, ce sont des sorts qui gagnent beaucoup par rang (Floraison Mortelle
×2,35, Partage de Souffle ×3,25) face à des sorts de spécialisation qui ne gagnent rien par rang
(Forteresse Sylvestre, Forteresse Vivante, Forge Vivante). Voir la question 6.

Exemples :

| sort | tier, famille | G | coût rang 1 → rang 10 |
|---|---|---|---|
| Frappe lourde (guerrier) | base, remplissage | ×1,30 | 6 → 6 |
| Clivage (guerrier) | base, courant | ×1,32 | 21 → 30 |
| Soin (soigneur) | base, courant | ×1,41 | 27 → 36 |
| Cataclysme Arcanique (mage) | base, courant | ×1,27 | 40 → 49 |
| Trait de Givre (Invocateur de Givre) | spécialisation, remplissage | ×1,60 | 15 → 24 |
| Requiem (Cantor) | sous-classe, signature | ×1,45 | 74 → 110 |
| Zéro Absolu (Invocateur de Givre) | spécialisation, signature | ×1,70 | 75 → 129 |
| Demantelement Total (Affaiblisseur) | spécialisation, signature | ×1,70 | 52 → 88 |

Les cinq descriptions du guerrier ne redisent plus leur coût (« Coût : N Souffle… ») : c'était une
copie des champs de coût, que le client affiche déjà ; `--check` refuse une telle phrase.

## 5. Ce qui demande du code (non écrit)

- ~~Serveur, régénération hors combat~~ : fait le 2026-10-15 (section 1 bis).
- **Serveur, `rank_scaling_enabled` devenu redondant** : tous les sorts de classe qui portent
  `percent_per_level` l'ont. Supprimer la porte (`room.cpp` `effective_scaling` ligne 8064,
  `content_loader.cpp:451`, `skill.hpp:152`, `BE1_PER_LEVEL_SCALING`) pour que `percent_per_level`
  s'applique toujours ; puis retirer le champ de la data et de la règle du script.
- ~~Serveur, croissance de régénération~~ : fait le 2026-10-15. Le combat lit `class_growth.mp_regen` et
  `hp_regen` (clés obligatoires) × (niveau − 1) ; l'économie multiplie aussi `mp_regen` par (niveau − 1)
  (`CombatStatSnapshotBuilder::scale_growth`, une seule copie au lieu de trois). Reste : l'économie arrondit
  chaque croissance à l'entier au chargement (`stat_block_json.hpp`, 0,06 → 0, 0,8 → 1) quand le combat
  garde le flottant.
- **Économie, passifs de régénération** : la part plate est arrondie à l'entier inférieur hors combat
  (`passive_materializer.hpp`, `flat()`), puis le profil est stocké en entiers : Souffle profond
  (0,5/s au rang 10) et Respiration (0,5/s au rang 5) ne régénèrent rien hors combat. **Toujours ouvert**
  (pas local) : tout le profil est en entiers (`CombatStatSnapshot`, JSON, tick). Correction : porter
  `hp_regen`, `mp_regen` et leurs variantes hors combat en centièmes (comme `attack_speed`, ×100), sans
  arrondi dans `passive_materializer.hpp`, et faire garder au tick le reste fractionnaire de chaque
  personnage (accumulateur en mémoire dans `HealthCoordinator`).
- **Objets déjà tirés** : ils gardent leur `mp_regen` au multiplicateur ×4,6. Migration ou non.

## 6. Questions ouvertes

1. **Classes martiales et soigneur à sec avant la fin d'un pack** (avant comme après). Leviers : la
   réserve (base 45 à 55 et croissance 1 à 2 par niveau des classes martiales), un point sur trois en
   Souffle assumé comme obligatoire, ou une régénération différente par rôle (la piste de
   `balance_model.json` : un lanceur régénère peu mais porte une grande réserve, un combattant
   l'inverse). Le modèle chiffre la cible : un guerrier niveau 60 tient un pack de 98 s avec 188 de
   Souffle et reste à sec sur un élite s'il régénère 10,8 à 11,5/s (aujourd'hui 6).
2. **Durée des combats au niveau 100** : 260 s pour un pack solo, 52 GCD par monstre standard. Si c'est
   voulu, aucune réserve ne tient un pack ; sinon c'est la calibration (`player_ref_equilibre`) qui
   est à revoir avant d'ajuster le Souffle de haut niveau.
3. ~~Régénération hors combat~~ : tranché le 2026-10-15, section 1 bis (une stat, bonus hors combat
   dédiés, pass ×2).
4. **Panoplies de Souffle** (décision du 2026-10-15) : progression régulière du rang I au rang V, Nefesh
   5 → 15/s (I 5, II 7,5, III 10, IV 12,5, V 15), Neshamah 7 → 35/s (7, 14, 21, 28, 35). Mais une
   panoplie ne vit que dans **une** bande (`band`, modèle du 2026-09-28) : chaque set prend la valeur de
   sa bande, Nefesh (C, rang I) **15 → 5**, Neshamah (SS, rang V) **35** (inchangé, 14 au palier 4 et 21
   au palier 8). Les autres valeurs n'ont pas de porteur. Si Nefesh doit exister à chaque rang, c'est un
   changement de modèle (un set par bande, ou des bonus par bande lus par `PanoplieRegistry`). Budget
   (`--budget`, colonne panoplie) : Nefesh suffit à rendre le mage inépuisable au niveau 60 et fait tenir
   un pack à presque toutes les classes jusqu'au niveau 60 ; Neshamah (+35/s) rend **toutes** les classes
   inépuisables au niveau 100 (41 à 48/s de régénération pour 18 à 23/s de rotation). À revoir si ce
   n'est pas voulu.
5. **`hp_regen`** prend aussi le ×4,6 des stats brutes. Elle ne joue que hors combat ; la passer en
   taux aussi ?
6. **Sorts de spécialisation sans gain par rang** (Forteresse Sylvestre, Forge Vivante, etc.) : ils
   coûtent maintenant le même prix à tous les rangs, et des sorts de base les dépassent au rang 10.
   Leur donner un gain par rang est un choix d'effet.
7. **Voleur** : ses sorts de spécialisation coûtent 52 (signatures) et 27 (courant, médiane) contre 75
   et 33 ailleurs. Voulu (petite réserve) ? Avec la règle, ses signatures de sous-classe passent à 51.
8. **Remplissages de base et de sous-classe à +0 par rang** : leur gain (×1,25 à ×1,30 sur 6 à 10 de
   Souffle) fait moins d'un demi-point par rang. On garde 0 ?
9. **Potions en combat** : il faudrait une action objet côté serveur de combat (avec une recharge).
10. **Plus gros sort / réserve** : 29 à 45 % chez le guerrier, jusqu'à 31 % chez le voleur et l'archer
    au niveau 1. Lié à la question 1.

**Révision du 2026-10-15 (propriétaire)** : 35/s pour une panoplie était trop. Valeurs « par 5 s » : Nefesh 5 par 5 s = **1/s**,
Neshamah 35 par 5 s = **7/s** (3 au palier 4, 4 au palier 8). Au niveau 100, le mage en Neshamah régénère 20/s pour une rotation
de 19,4/s (encore à la limite) ; le guerrier passe de 26 à 65 s avant d'être à sec.
