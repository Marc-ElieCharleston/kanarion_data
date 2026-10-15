# Souffle : coût par rang de sort

Statut : appliqué le 2026-10-15 sur les sorts de base et de tier 2 (branche `vac_souffle-scaling`).
Demande du propriétaire : « mettre du Souffle en fonction de la puissance du sort », sans qu'un sort
coûte tout le Souffle, et sans spam infini (sinon potions et régénération ne servent à rien).
Outil : `scripts/balance/souffle_per_level.py` (`--check`, `--report`, `--budget`).

## Le budget modélisé

Sources : Souffle max = base de classe + croissance + équipement attendu (`pve_matrix.Gear`, avec les
multiplicateurs de sous-stats par poids d'armure), régénération = `mp_regen` de classe (1/s, croissance
0) + `mp_regen` de l'équipement (le serveur l'ajoute par seconde, en combat comme hors combat).
Points de stats : 0 en Souffle (cas des builds de référence) ou 1 point sur 3 par niveau (+5 par point).
Rangs de sorts typiques (1 point par niveau) : niv 20 = base rang 4 ; niv 40 = base 6, tier 2 rang 2 ;
niv 60 = base 8, tier 2 rang 4 ; niv 100 = base 8, tier 2 et tier 3 rang 6. Équipement : commun +0
jusqu'au niv 20, rare +5 ensuite.

Durées de combat : PV des monstres (`monster_scaling_model.json`, médiane des 7 archétypes) divisés par
les dégâts du joueur de référence (`level_curve.calibration`, socle + passifs + équipement), 1 action
par GCD de 2 s. Pack = 2-3 monstres standard en solo ; élite = 1 élite + 2 standard en solo ;
boss = boss de donjon en groupe (3 sources de dégâts) ; 5★ = 1 boss + 3 élites + 5 standard (+25 % PV)
en groupe. Hypothèse prudente : sans familier ni mercenaire, qui raccourcissent les combats.

« Rotation » = Souffle par seconde d'une rotation soutenue : à chaque GCD, le sort prêt le plus cher
(fillers en dernier). C'est un plafond de dépense. « À sec » = temps avant que la rotation complète ne
soit plus finançable : le joueur retombe alors sur le filler et les sorts que la régénération paie.
Tous les chiffres sont des médianes sur les 8 spécialisations de chaque classe.

**Niveau 20** : pack 46 s, élite 77 s, boss 25 s, 5★ 120 s

| classe | Souffle (0 pt / 1 pt par niv) | regen /s | rotation /s avant → après | à sec (0 pt / 1 pt) | plein hors combat | plus gros sort / max |
|---|---|---|---|---|---|---|
| Guerrier | 80 / 175 | 3 | 5,4 → 5,7 | 29 s / 64 s | 27 s | 34 % |
| Mage | 286 / 381 | 4 | 8,7 → 9,5 | 52 s / 69 s | 72 s | 20 % |
| Soigneur | 279 / 374 | 4 | 10,5 → 11,8 | 36 s / 48 s | 70 s | 16 % |
| Archer | 133 / 228 | 2 | 5,7 → 6,1 | 32 s / 55 s | 66 s | 25 % |
| Voleur | 109 / 204 | 2 | 6,5 → 7,3 | 21 s / 39 s | 54 s | 28 % |
| Artisan | 133 / 228 | 2 | 5,4 → 6,5 | 30 s / 51 s | 66 s | 25 % |

**Niveau 40** : pack 80 s, élite 134 s, boss 43 s, 5★ 208 s

| classe | Souffle (0 pt / 1 pt) | regen /s | rotation /s | à sec (0 pt / 1 pt) | plein hors combat | plus gros sort / max |
|---|---|---|---|---|---|---|
| Guerrier | 145 / 340 | 5 | 11,1 → 12,0 | 21 s / 49 s | 29 s | 39 % |
| Mage | 555 / 750 | 11 | 13,8 → 15,1 | 135 s / 182 s | 50 s | 12 % |
| Soigneur | 548 / 743 | 11 | 16,9 → 19,1 | 67 s / 91 s | 50 s | 15 % |
| Archer | 236 / 431 | 5 | 11,3 → 12,4 | 32 s / 58 s | 47 s | 25 % |
| Voleur | 192 / 387 | 5 | 12,5 → 13,7 | 22 s / 45 s | 38 s | 33 % |
| Artisan | 236 / 431 | 5 | 10,5 → 12,5 | 31 s / 57 s | 47 s | 26 % |

**Niveau 60** : pack 98 s, élite 164 s, boss 52 s, 5★ 254 s

| classe | Souffle (0 pt / 1 pt) | regen /s | rotation /s | à sec (0 pt / 1 pt) | plein hors combat | plus gros sort / max |
|---|---|---|---|---|---|---|
| Guerrier | 176 / 471 | 8 | 11,1 → 12,7 | 37 s / 99 s | 22 s | 35 % |
| Mage | 724 / 1019 | 16 | 13,8 → 16,1 | jamais en pratique | 45 s | 10 % |
| Soigneur | 717 / 1012 | 16 | 16,9 → 20,4 | 162 s / 229 s | 45 s | 13 % |
| Archer | 316 / 611 | 6 | 11,3 → 13,2 | 44 s / 85 s | 53 s | 20 % |
| Voleur | 252 / 547 | 6 | 12,5 → 14,6 | 29 s / 63 s | 42 s | 27 % |
| Artisan | 316 / 611 | 6 | 10,5 → 13,6 | 42 s / 80 s | 53 s | 21 % |

**Niveau 100** : pack 260 s, élite 437 s, boss 139 s, 5★ 676 s

| classe | Souffle (0 pt / 1 pt) | regen /s | rotation /s | à sec (0 pt / 1 pt) | plein hors combat | plus gros sort / max |
|---|---|---|---|---|---|---|
| Guerrier | 300 / 795 | 12 | 16,5 → 18,4 | 47 s / 125 s | 25 s | 35 % |
| Mage | 1336 / 1831 | 29 | 18,5 → 20,5 | jamais | 46 s | 8 % |
| Soigneur | 1329 / 1824 | 29 | 20,6 → 23,8 | jamais | 46 s | 8 % |
| Archer | 548 / 1043 | 12 | 16,2 → 18,3 | 87 s / 166 s | 46 s | 19 % |
| Voleur | 444 / 939 | 12 | 16,7 → 19,0 | 64 s / 134 s | 37 s | 17 % |
| Artisan | 548 / 1043 | 12 | 15,6 → 18,8 | 81 s / 154 s | 46 s | 19 % |

Niveau 1 : Souffle 60 (guerrier) à 229 (mage), regen 2 à 4/s, tous les sorts au rang 1, donc la règle
ne change rien. La courbe de référence commence au niveau 10, les durées du niveau 1 ne sont pas
modélisées.

Potions de Souffle : I à V rendent 30 / 90 / 200 / 380 / 600 (10 à 500 or). Elles ne s'utilisent
**que hors combat** (le serveur de combat n'a pas d'action objet ; elles passent par l'économie). Leur
rôle est donc d'éviter d'attendre 20 à 70 s de régénération entre deux combats.

Ce que dit le budget :
- **Guerrier, voleur, archer, artisan** : la rotation complète est à sec avant la fin d'un pack solo
  à tous les niveaux, **déjà avant ce changement**. Avec 1 point sur 3 en Souffle, ils tiennent à peu
  près un pack au niveau 60. Le Souffle les contraint déjà fortement.
- **Mage et soigneur** : grosse réserve (armure légère) et régénération d'équipement de 16 à 29/s à
  partir du niveau 60. La rotation ne coûte plus rien en net : c'est là qu'est le « spam infini ».
  Aucun coût par rang raisonnable ne le corrige : même la régression du tier 3 (`1 + coût/15`, environ
  deux fois plus chère) laisse le mage à 180 s au niveau 60 et jamais à sec au niveau 100. Le levier
  est la régénération d'équipement (voir questions).

## La règle retenue

    mana_cost_per_level = arrondi( mana_cost × (G − 1) / 9 )

G est le gain de puissance **effectif** du sort entre le rang 1 et le rang 10, lu dans ses propres
champs par rang, ceux que le serveur applique : `percent_per_level` sur `scaling_percent` ou
`heal_scaling_percent` (seulement si `rank_scaling_enabled`), et pour chaque effet `pct_per_level`,
`value_per_level`, `duration_per_level` (multipliés entre eux pour un même effet). On prend la plus
forte de ces progressions : c'est là que le rang investit.

Conséquence : au rang 10, le sort coûte `mana_cost × G`. **Le Souffle payé par unité d'effet est le
même à tous les rangs.** Un rang ne rend plus le sort plus rentable, il le rend plus fort et plus
gourmand par GCD, ce qui vide la réserve plus vite.

Pourquoi cette règle :
- c'est la demande telle quelle : le coût suit la puissance du sort. Le coût de base porte déjà le
  rôle (filler 6-10, sort courant 18-33, signature 52-98) ; le coût par rang suit ce que le rang ajoute ;
- c'est **exactement la façon dont les signatures du tier 3 sont tarifées** : coût ×1,72 au rang 10
  pour une puissance ×1,70 (+6 sur 75, +4 sur 52) ;
- la note « +3/niv, +6/niv, +7-8/niv » de `skill_system.json` correspond au tier 3, dont la puissance
  fait ×1,6 à ×1,7 au rang 10. Les sorts de base et de tier 2 gagnent pour la plupart ×1,23 à ×1,45
  (médiane ×1,30). Leur appliquer +3/+6 ferait payer chaque rang deux à trois fois ce
  qu'il rapporte, et le budget montre que les quatre classes martiales sont déjà à sec ;
- une règle plus forte (×1,7 partout, ou la régression du tier 3 `1 + coût/15`) enlève jusqu'à 40 %
  du temps avant d'être à sec aux classes martiales au niveau 60 (guerrier 37 s → 22 s), sans faire tomber le mage à sec.

Ce qui en sort, sur 150 sorts (5 base + 5 tier 2 par sous-classe, payants, `max_level` ≠ 1) :
92 à +1, 29 à +2, 5 à +3, 2 à +4, 2 à +5, 1 à +9, et 19 à 0. Les 19 à 0 : les 12 fillers (gain ×1,25 à
×1,30 sur 6 à 10 de Souffle, moins d'un demi-point par rang), 4 sorts dont le gain est faible
(Coup de bouclier : étourdissement +10 % ; Cri de provocation ; Fiole toxique ; Fracas d'enclume)
et 3 sorts qui ne gagnent rien par rang (Tirage chanceux, Malchance, Intercession). Le plus gros sort,
au rang typique, reste sous 26 % de la réserve partout sauf chez le guerrier (34 à 45 %) et le voleur
(jusqu'à 33 %), ce qui tient à leur petite réserve et existait avant (voir questions). Les 5 sorts du Gardien qui n'avaient pas le champ l'ont maintenant (le client prenait 4
par défaut). La phrase « Coût : N Souffle à tous les rangs » de 2 descriptions du guerrier devient
« Coût : N Souffle (+1 par rang) » ; elle reste vraie pour les 3 autres.

## Exemples

| sort | rôle | gain au rang 10 | +/rang | coût rang 1 → rang 10 |
|---|---|---|---|---|
| Frappe lourde (guerrier) | filler | ×1,30 | 0 | 6 → 6 |
| Coup de bouclier (guerrier) | basique, CC | ×1,10 | 0 | 18 → 18 |
| Clivage (guerrier) | basique | ×1,32 | 1 | 21 → 30 |
| Soin (soigneur) | soin | ×1,41 | 1 | 27 → 36 |
| Volée de flèches (archer) | zone | ×1,26 | 1 | 30 → 39 |
| Cataclysme arcanique (mage) | fort | ×1,27 | 2 | 52 → 70 |
| Égide du Royaume (gardien) | signature, bouclier | ×1,28 | 2 | 60 → 78 |
| Tempête élémentaire (élémentaliste) | signature | ×1,30 | 3 | 75 → 102 |
| Requiem (chantre) | signature, résurrection | ×1,45 | 5 | 98 → 143 |
| Floraison mortelle (lame de l'ombre) | signature | ×2,35 | 9 | 60 → 141 |
| Partage de Souffle (artisan) | rend du Souffle | ×3,25 | 5 | 18 → 63 |

Les deux derniers montent fort parce que leur effet monte fort (100 % +15 par rang ; 4 % +1 par rang
du Souffle rendu).

## Le tier 3 face à la règle (non modifié)

- **179 sorts paient par rang une puissance inerte en production** : leur seul gain est
  `percent_per_level`, mais ils n'ont pas `rank_scaling_enabled`. Le serveur ignore alors ce gain tant
  que la variable d'environnement `BE1_PER_LEVEL_SCALING` n'est pas activée (désactivée par défaut,
  `room.cpp effective_scaling`), alors que `mana_cost_per_level` s'applique toujours.
- **16 sorts paient par rang sans aucun gain par rang**, même avec BE1 : 3 sorts de la sentinelle,
  2 du chevalier runique, 3 du gardien du bosquet, 1 du maître de chœur, 2 de l'alliance, 5 du maître
  forgeron (liste par `--report`).
- **2 sorts payants sont à 0** : `skill_mage_fate_gambler_double_or_nothing`,
  `skill_artisan_guitarist_clear_chorus`.
- **Les sorts non signature sont plus chers que leur puissance** (même avec BE1) : à coût 8-18, +2 par
  rang pour ×1,6 de puissance (coût ×2,0 à ×3,25) ; à 21-45, +3 ou +4 (coût ×1,8 à ×2,3). La règle
  donnerait +1 à +3. Les signatures (52, 68, 75) sont conformes.

## Questions ouvertes

1. **Régénération d'équipement.** `mp_regen` n'est pas dans `rate_stats_no_tier_scaling` : une
   sous-stat vaut 2/s au niveau 1 et 8/s au niveau 100. Avec un équipement rare +5, un mage régénère
   16/s au niveau 60 et 29/s au niveau 100, 16 à 29 fois la base. C'est la vraie cause du spam infini.
   Passer `mp_regen` en stat de taux (×1 à ×1,55), ou diviser sa plage ?
2. **Guerrier (et voleur).** Réserve 45 + 1 par niveau, armure lourde qui tire peu de Souffle : le plus
   gros sort pèse 34 à 45 % de la réserve et la rotation est à sec en 20 à 50 s, avant la fin d'un pack.
   Relever la base ou la croissance de Souffle du guerrier, ou assumer que les points de Souffle sont
   obligatoires pour les classes martiales ?
3. **Fillers à 0.** La règle donne 0 (gain trop faible pour un point entier). Les mettre à +1 par rang
   ferait un filler à 15 au rang 10 (×2,5 pour ×1,3 de puissance). On garde 0 ?
4. **Tier 3** : activer `rank_scaling_enabled` sur les 179 sorts (ou BE1 en production), et aligner les
   non-signatures sur la règle (+1 à +3 au lieu de +2 à +4) ? À faire dans une passe dédiée.
5. **Potions en combat.** Elles ne servent qu'entre deux combats. Si on veut qu'elles servent pendant un
   boss, il faut une action objet côté serveur de combat (avec une recharge).
6. Mettre à jour la note de `skill_system.json` (`mana_cost_scaling.design_note`) et la règle « ×1,7 au
   rang 10 » de `config/balance_model.json` (`souffle.cout_par_niveau_de_sort`), qui ne correspondent
   plus qu'au tier 3 ?
