# Matrice de puissance des sorts

Statut : phases 1 (mesure) et 2 (cooldowns, incantations, section 6) appliquées ; phase 3 (coût en
Souffle) à venir (2026-10-15, branche `vac_skill-matrix`).
Demande du propriétaire : « si deux sorts ont le même coût alors que l'un fait beaucoup de dégâts avec
beaucoup de temps de cast et que l'autre est un simple coup, c'est étrange de mettre la même valeur »,
« je ne veux pas qu'on lance un ulti toutes les 10 secondes, mais plutôt toutes les 2-3 minutes », et
« aujourd'hui il y a déjà beaucoup de spam avec des temps de cd courts, hors filler ».
Modèle et poids : `config/skill_power_model.json`, seul propriétaire. Outil :
`scripts/balance/skill_power_matrix.py` (sortie `scripts/balance/out/skill_power_matrix.json`,
`--check` en CI, `--report` pour les chiffres ci-dessous). Les phases 2 (cooldowns, incantations) et 3
(coût en Souffle) lisent la matrice.

## 1. Le modèle

**Unité** : 1 point = 1 % de la stat offensive du lanceur infligé en dégâts à une cible. Un coup à
100 % ATK vaut 100. **Débit de référence** = coup moyen d'un sort courant (120 %, banc de référence du
serveur) / GCD (2 s) = **60 points/s**. Tout ce qui n'est pas des dégâts est converti par ce débit
(une seconde de contrôle, de buff, d'incantation perdue) ou en PV (1 PV rendu ou absorbé = 1 PV infligé).

Ce que la matrice compte, tel que le serveur l'applique (`room.cpp`, lu sur `vac_doublons-lot2`) :

| composante | calcul | poids (data) |
|---|---|---|
| dégâts | `scaling_percent` (+ `percent_per_level` × (rang − 1) **seulement si `rank_scaling_enabled`**) × stat du `damage_type` / stat offensive de la classe × coups × cibles × bonus conditionnels × portée | exécution × 0,25 d'uptime, bonus conditionnels 0,3 à 0,5 |
| cibles | zone : √min(cases, 9) ; chaîne, rebond, aléatoire : min(N, 3), chaque rebond répété compte pour les dégâts directs, pas pour les effets | `targets` |
| DoT | coefficient de `status_effects.json` (`runtime` ou `formula`) × charges plafonnées × durée / tick | poison : 1 % PV cible = 0,5 pt |
| soin, HoT, bouclier | % de MAG, PV max, DEF ou Souffle max, converti par le rapport stat / stat offensive de la classe au niveau 60 | × 0,7 (débordement) |
| contrôle | durée (plafonnée au « max Ns ») × 60/s × efficacité ; `slow` = pénalité de GCD / GCD | dur 1,0 (`blocks_skills`), mou 0,4 |
| buffs, debuffs | magnitude (charges × `value_per_stack`) / 100 × 60 × durée × cibles × efficacité de la **clé `runtime.stat_mods`** | ATK/MAG/dégâts/dégâts subis 1,0, armure/RM 0,5, crit 0,5, dégâts crit 0,2… |
| verbes | par lancer (cleanse, purge 60 ; steal_buff 80 ; interrupt 60 ; cover, un coup intercepté, 120) ou par seconde (invulnérable 60, immunité aux contrôles 15…) | `special_effects` |
| Souffle rendu | converti au rendement médian mesuré : **7,6 points par Souffle** | mesuré, pas écrit |
| résurrection | 600 points à 100 % des PV (10 s de débit d'un allié) | |
| portée, LdV | (cases ennemies atteintes / cases au `base_range`)^0,25 ; × 0,85 si ligne de vue requise ; ×1 pour un sort bénéfique | `reach` |
| incantation | coût = (cast − GCD)⁺ × 60 + 0,03/s × cast² × 60 (interruption par étourdissement seulement, Souffle et cooldown remboursés) | `casting` |

Puissance brute = somme des composantes ; puissance nette = brute − coût d'incantation. Tout est calculé
aux rangs 1 à 10. Aucun id de sort dans le modèle : un effet est rangé par sa catégorie et son
`runtime` dans `stats/status_effects.json`.

**Repris de `config/balance_model.json`** (non lu par le code, supprimé ailleurs) : l'unité en % de
stat, la racine plafonnée à 9 cases, le contrôle à 60 et 25/s (désormais justifiés par le débit), la
règle du GCD (une incantation sous 2 s ne coûte rien), la densité puissance/cooldown comme outil de tri.
**Périmé** :
- ratios PV/MAG en dur, au niveau 1 → recalculés depuis `class_base_stats` + `class_growth` au niveau 60 ;
- « verbes non pricés » (cleanse, purge, interrupt, vol) → pricés ;
- résurrection à 1500 sans base → 600 ;
- debuffs à 4/s par charge → dérivés de la clé de stat (5 % × 60 = 3/s pour ATK) ;
- fourchettes `cooldown.par_tier` (spécialisation 36 s de médiane) → 42 s aujourd'hui ;
- `scaling_par_niveau_de_sort` (« le soin ne progresse pas par rang ») → le serveur applique
  `percent_per_level` au soin et `pct_per_level` aux boucliers ;
- le modèle `souffle` (autonomie par tier, dérive de régénération) → remplacé par
  `skill_system.json mana_cost_scaling` et `souffle_par_niveau.md`.

**Champs morts côté serveur encore en data** (le modèle les ignore) : `power_per_level` et
`effect_power_per_level` (150 sorts), `cooldown_per_level` (25), `heal_scaling_stat` (28 : le soin suit
toujours MAG), `cast_interruptible` (1). `scaling_stat: atk/mag` est aussi sans effet : c'est
`damage_type` qui choisit le stat. Trou de data : `exposed` n'a pas de `runtime.stat_mods` dans
`status_effects.json` (comblé dans le modèle, `implicit_stat_mods`).

**Limites** : un buff offensif suppose des alliés au débit de référence ; une zone suppose une meute
de 3 cibles au plus ; le poison et les DoT en PV de la cible sont grossiers ; la valeur d'un DoT
mesure un lancer (relancer rafraîchit). C'est un outil de tri.

## 2. Les rôles

Déduits de la data, sans champ nouveau (`skill_power_model.json roles`, première règle qui
s'applique) :

| rôle | règle | n | paliers | puissance r1 q1 / méd / q3 | r10 méd | CD méd | cast méd | Souffle r1 méd |
|---|---|---|---|---|---|---|---|---|
| remplissage | tier `filler` ou tag `filler` | 52 | base 6, sous-classe 6, spé 40 | 110 / 134 / 169 | 198 | 12 s | 0 | 12 |
| **ultime** | tier `signature` d'une spécialisation | 48 | spé (1 par kit) | 812 / 1278 / 1915 | 1828 | 84 s | 2,5 s | 75 |
| signature | tier `signature` de sous-classe | 24 | sous-classe | 180 / 264 / 433 | 344 | 40 s | 2,25 s | 60 |
| défensif | dominante soin, HoT, bouclier, buff défensif | 59 | | 84 / 134 / 201 | 164 | 36 s | 0 | 33 |
| utilitaire | dominante contrôle, buff offensif, verbes | 60 | | 83 / 150 / 212 | 183 | 28 s | 0 | 30 |
| courant | le reste (dégâts) | 147 | | 138 / 264 / 480 | 399 | 32 s | 0 | 33 |

**Ce qui joue l'« ulti » aujourd'hui** : les 48 signatures de spécialisation, une par kit, 36 à 90 s de
recharge (médiane 84 s ; 4 sous 60 s : Exécution, Tranchant Net, Émergence, Bordée). La signature de
sous-classe (médiane 264 points) n'est pas plus forte qu'un sort courant (264) : elle porte un nom de
gros sort sans en avoir la puissance.

**Champ explicite ?** Non nécessaire : `tier` + palier suffisent pour remplissage, signature et ultime,
et la dominante tranche le reste. Un champ `role` recopierait `tier` (deux propriétaires). Si la
phase 2 veut un ultime hors signature, c'est `tier` qu'il faut changer.

## 3. Le spam hors remplissage : cooldowns et enchaînement

Cooldowns des 338 sorts hors remplissage :

| groupe | n | q1 | médiane | q3 | < 6 s | < 10 s | < 20 s |
|---|---|---|---|---|---|---|---|
| tous, CDR 0 | 338 | 24 | 36 | 48 | 0 % | 2 % | 14 % |
| tous, CDR 40 % (plafond) | 338 | 14,4 | 21,6 | 28,8 | 2 % | 13 % | 42 % |
| base | 24 | 15 | 24 | 28 | 0 % | 8 % | 33 % |
| sous-classe | 114 | 20 | 26 | 32 | 0 % | 4 % | 23 % |
| spécialisation | 200 | 36 | 42 | 54 | 0 % | 1 % | 7 % |
| courant | 147 | 20 | 32 | 42 | 0 % | 3 % | 22 % |
| utilitaire | 60 | 20 | 28 | 36 | 0 % | 2 % | 18 % |
| défensif | 59 | 29 | 36 | 45 | 0 % | 3 % | 8 % |
| signature | 24 | 28 | 40 | 46 | 0 % | 0 % | 0 % |
| ultime | 48 | 78 | 84 | 84 | 0 % | 0 % | 0 % |
| tier `basic` | 33 | 11 | 16 | 24 | 0 % | 18 % | 58 % |

**Pris un par un, les cooldowns ne sont pas courts. Le spam vient du nombre de sorts.** Une barre de
12 cases porte 8 à 12 sorts hors remplissage ; chacun revient en 20 à 50 s, et à un GCD de 2 s il
suffit que la **charge** Σ max(GCD, cast) / cooldown dépasse 1 pour qu'il y ait toujours un sort hors
remplissage prêt. Part du temps de combat passée à lancer des sorts hors remplissage (lancer à chaque
GCD le plus puissant prêt, Souffle illimité, barre remplie avec les 12 cooldowns les plus courts) :

| kit | CDR | charge méd (min-max) | part du temps méd (q1-q3) | kits à 100 % |
|---|---|---|---|---|
| niveau 20-59 (base + sous-classe) | 0 % | 0,87 (0,63-1,25) | 76 % (71-87) | 0 / 48 |
| niveau 20-59 | 40 % | 1,46 (1,05-2,09) | 100 % (96-100) | 26 / 48 |
| niveau 60+ (15 sorts) | 0 % | 1,12 (0,78-1,55) | 91 % (84-97) | 7 / 48 |
| niveau 60+ | 40 % | 1,86 (1,30-2,59) | 100 % | 47 / 48 |

Au niveau 60 sans réduction de recharge, on lance un sort hors remplissage 9 GCD sur 10 ; avec la
réduction maximale, le remplissage ne sert plus jamais. Le Souffle est la seule limite restante
(`souffle_par_niveau.md` : à sec en 1 à 4 minutes de rotation soutenue).

## 4. Incohérences principales

Chiffres au rang 1 (`--report` donne les listes complètes).

1. **Même coût, puissance très différente.** 20 coûts sur 33 portent un écart ≥ ×3, et 24 groupes
   sur 43 **à rôle égal**. À 33 de Souffle : Vague de Cendres (Magma Sage, 1554 points, cast 4 s)
   contre Barrage Concentré (Ballmaster, 77). À 27 : Tornade d'Acier (999) contre Marquer la Cible
   (61). À 75, entre deux ultimes : Frappe Synchronisée (2902) contre Frappe Rédemptrice (330).
   Corrélation de rang coût / puissance : 0,34 sur la base, 0,36 sur la sous-classe, 0,68 sur la
   spécialisation.
2. **Le cooldown ne suit pas la puissance là où les joueurs passent le plus de temps.** Corrélation
   de rang cooldown / puissance : 0,01 sur la base, 0,30 sur la sous-classe, 0,68 sur la spé.
3. **Gros sorts courants plus denses que des ultimes.** Carnage (Bloodrage) 948 points toutes les
   24 s (39,5/s), Rugissement Affaiblissant (Warlord) 635 / 20 s, Vague de Cendres 1554 / 48 s ;
   Bordée (Gunslasher, ultime) 1521 / 42 s. Trois sorts non ultimes dépassent l'ultime médian.
4. **Ultimes sous la minute** : 4 sur 48 (36 à 42 s). Aucun n'est à 2-3 minutes.
5. **Ultimes très inégaux** : 252 (Riposte Parfaite) à 3454 points (Curée Sanglante), ×14.
6. **Incantation** : corrélation de rang puissance / cast 0,67 sur les 155 sorts incantés, mais 13 sorts
   du top 10 % ne paient rien au-delà du GCD, dont 10 ultimes (8 du guerrier et du voleur, classes
   physiques sans incantation par design), et 3 signatures faibles incantent 2,5 s.
7. **Souffle par 100 points** : 67 sorts hors de ×0,5-×2 de la médiane de leur palier et rôle. Le
   tier 3 courant paie 8,6 Souffle / 100 points, la sous-classe 20,4 : à rôle égal, la spécialisation
   est 2,4 fois plus rentable.
8. **5 novas posées à 5 cases** (corrigé en phase 2 : `range: 0`) : `target: self_and_enemies` sans `range: 0` (Tempête de Lames,
   Présence Suffocante, Déchaînement, Tornade d'Acier, Choc Sismique). La règle nova du
   `CLAUDE.md` n'est pas appliquée, et un guerrier à portée 2 frappe « autour de lui » à 5 cases.
9. **Remplissages de spécialisation** : 40 sorts, cooldown 9 à 36 s (médiane 12 s), contre 3 à 5 s en
   base. La Coupe Épicée (Spice Master) fait 382 points pour 15 Souffle avec 36 s de recharge : un remplissage à 36 s n'en est plus un.

## 5. Règles proposées (phase 3 non appliquée)

### Phase 2 : cooldowns et incantations

Appliquée, voir la section 6 (règle ajustée aux décisions du propriétaire : budget de charge 0,8,
bornes larges, identité de classe, incantations nombreuses).

### Phase 3 : coût en Souffle

1. **Coût r1 = a(rôle, palier) × (puissance nette r1 / 100)^β**, β ≈ 0,5 (sous-linéaire : le cooldown
   borne déjà le gros sort ; la pente mesurée aujourd'hui est 0,32). À rôle et palier égaux, deux sorts
   de puissance ×4 coûtent ×2.
2. **Autonomie croissante avec le rôle** (coût / (CD × régén)), cible de `balance_model.json` reprise :
   remplissage 0,6, courant 1,0-1,4, signature 1,6, ultime 2,0.
3. Garder `tier_order` (base < sous-classe < spé à rôle égal) et `per_rank_rule` (coût par rang = gain
   de puissance), qui existent déjà dans `skill_system.json mana_cost_scaling` ; remplacer les familles
   de `tier_order` par les rôles de la matrice, une seule classification.

## 6. Phase 2 appliquée : cooldowns et incantations

Appliqué le 2026-10-15 (branche `vac_skill-matrix`). Règle : `config/skill_power_model.json` `timing`,
seul propriétaire (la règle lit la puissance, les rôles et les dominantes de ce même fichier ; la
mettre dans `skill_system.json` couperait le modèle en deux). Outil : `scripts/balance/skill_timing.py`
(application, `--check` en CI, `--report` pour les chiffres ci-dessous), qui réutilise la matrice
(`build`, `bar`, `kit_load`, `spam_fraction`) et l'écriture textuelle de `souffle_per_level.py`
(`set_fields`, `rewrite_skills`). Les sorts ne portent que le résultat (`cooldown`, `cast_time`).

Décisions du propriétaire : allonger le cooldown d'un sort trop fort plutôt que baisser sa
puissance ; « pas de spam skill 1 », chaque sort a son moment ; des combats de 40 s plutôt que 10 s ;
les cooldowns repartent à zéro à chaque combat ; pas de moule unique entre les classes ; beaucoup de
sorts incantés, surtout les puissants, pour pouvoir interrompre ou attendre une immunité.

### Remise à zéro des cooldowns par combat (serveur vérifié)

Chaque rencontre crée une `Room` neuve (`combat_host.cpp handle_create_room` → `room_manager.cpp`
`std::make_shared<Room>`), avec des entités neuves : `SkillsComponent.cooldowns` (id → tick de
disponibilité, en ticks de la room) part vide, rien ne le recharge depuis le profil. Tous les sorts
sont prêts au premier tick : un ultime de 120 à 180 s se lance une fois par combat, au moment choisi.
À noter : le plafond de réduction de recharge est **écrit en dur** dans `room.cpp`
`apply_cooldown_reduction` (`std::clamp(cdr, 0, 40)`), copie de `combat.json`
`cooldown_reduction_cap` : changer la data ne suffirait pas.

### La règle des cooldowns

    cible = puissance nette r1 / (densité du rôle × identité), bornée par le rôle, arrondie vers le haut
    cooldown = max(actuel, cible)        (seul raccourcissement : au-dessus de la borne haute du rôle)

| rôle | densité (pts/s) | bornes |
|---|---|---|
| remplissage | 30 | 4-40 s |
| courant | 6 | 15-90 s |
| signature | 4 | 30-120 s |
| défensif | 4 | 12-120 s |
| utilitaire | 4 | 15-120 s |
| ultime | 10 | 120-180 s |

- **Identité** : un sort dont la dominante porte le rôle de sa classe (`roles.json` : tank → défense et
  contrôle, soigneur → défense et soutien, DPS → offense, soutien → soutien et défense) admet une
  densité ×2. Le soin d'un soigneur revient plus souvent que celui d'un guerrier.
- **Arrondi** : demi-secondes sous 10 s, secondes jusqu'à 30 s, multiples de 5 au-delà.
- **Budget de charge** : Σ max(GCD, cast) / cooldown sur la barre (12 sorts hors remplissage au
  cooldown le plus court) ≤ **0,8** sans réduction de recharge. Un kit au-dessus baisse la densité
  admise de toute sa barre (facteur k ≥ 0,5) : ce sont les sorts forts pour leur rôle qui s'allongent,
  les faibles restent sur leur plancher. 0,40 (phase 1) renvoyait 60 % des GCD au remplissage, et
  n'était tenable qu'en doublant tous les cooldowns. 9 kits restent au-dessus au niveau 60 (0,82 à
  0,95 : arcane dealer, fate gambler, covenant, sharpshooter, skirmisher, nightstalker, assassin,
  blade dancer, countermaster), listés par `--report`.
- Aucun cooldown n'a été raccourci : aucun n'était au-dessus de la borne haute de son rôle.

### La règle des incantations

Constat serveur (`room.cpp`) : au début d'une incantation, Souffle, GCD et cooldown partent
ensemble ; l'incantation court **pendant** le GCD et l'action suivante attend les deux. Un cast ≤ 2 s
ne retarde donc rien ; il interdit seulement de se déplacer (`validate_move` → `ACTOR_CASTING`, le
déplacement ayant déjà 8 s de recharge), il peut être interrompu, et sa zone est re-résolue à la fin.
Au-delà du GCD, chaque seconde est une action perdue : c'est ce que la matrice compte
(`(cast − GCD)⁺ × 60`), cohérent avec le serveur.

**Interruption, côté serveur** : un stun (`cc_type` stun : étourdissement, gel, peur) pendant le cast
l'annule, cooldown et Souffle remboursés, GCD perdu (`process_casting`) ; le verbe `interrupt` (2 sorts
d'archer) l'annule **sans** rembourser. `silence` ne l'interrompt pas (`interrupts_cast` n'est pas lu),
`cast_interruptible` non plus (champ mort : tout cast est interruptible). Pas de canalisation :
`CastingComponent.is_channeled` existe mais n'est jamais vrai. La vitesse d'incantation (plafond 50 %)
raccourcit le cast.

    c = le plus long palier tel que grille(puissance brute r1 − coût d'incantation(c)) ≥ c   (point fixe)

| puissance nette r1 | cast |
|---|---|
| < 250 | 0 |
| 250-600 | 2,5 s |
| 600-1200 | 3 s |
| 1200-2000 | 4 s |
| ≥ 2000 | 5 s |

- Planchers : ultime 2,5 s ; résurrection 8 s (par effet `resurrect`).
- **Réflexes**, toujours instantanés : remplissage, ripostes et rapprochements (tags `counter`,
  `gap_closer`), défensif d'urgence sur soi. 66 sorts, dont 13 qui incantaient.
- **Préparation des classes physiques** : le serveur ne connaît qu'un mécanisme, `cast_time`. Pour les
  sous-classes de contact (`roles.json` tags `melee`, `melee_dps`), le cast est une préparation
  lisible, interruptible, plafonnée à 2,5 s (ne pas rester planté au contact) : 57 sorts, dont 29
  instantanés avant, ultimes du guerrier et du voleur compris.
- Un cast au-dessus du GCD ne fait que s'allonger. Un cast ≤ 2 s (gratuit) prend la valeur de la
  grille, au moins 2,5 s : aucune valeur n'est plus produite entre 0 et 2 s.
- Les descriptions qui recopient le cast (« Après 2s d'incantation », « Cast time 4s ») suivent le
  champ (`timing.description_copies`) ; aucune ne cite son cooldown.

### Avant / après

Répartition des temps d'incantation (390 sorts) :

| | instantané | ≤ 2 s | 2-4 s | ≥ 4 s |
|---|---|---|---|---|
| avant | 235 | 98 | 41 | 16 |
| après | 191 | 0 | 173 | 26 |

Cooldowns par rôle (médiane) : ultime 84 → 167,5 s (120 à 180) ; signature 40 → 57,5 s ; courant
32 → 40 s ; utilitaire 28 → 46,5 s ; défensif 36 → 40 s ; remplissage 12 → 12 s (les remplissages de
base et de sous-classe prennent 0,5 à 2 s, un remplissage fort davantage : Trait Élémentaire 3,5 → 9,5 s).
250 cooldowns et 169 incantations changent, 290 sorts au total.

Part du temps de combat passée à lancer des sorts hors remplissage (barre de 12, Souffle illimité) :

| barre | réduction | charge méd (min-max) avant → après | part du temps méd avant → après |
|---|---|---|---|
| niveau 20-59 | 0 % | 0,87 (0,63-1,25) → 0,61 (0,47-0,74) | 76 % → 58 % |
| niveau 60+ | 0 % | 1,12 (0,78-1,55) → 0,76 (0,63-0,95) | 91 % → 71 % |
| niveau 20-59 | 40 % (plafond) | 1,46 → 1,02 | 100 % → 85 % |
| niveau 60+ | 40 % (plafond) | 1,86 → 1,27 | 100 % → 96 % |

Durées de combat (`souffle_par_niveau.md`) : pack 46 s, élite 77 s, 5★ 120 s au niveau 20 ; 98, 164
et 254 s au niveau 60. Un pack se joue en enchaînant ; un élite ou un 5★ voit chaque ultime une fois
et oblige à choisir le moment des sorts à 60-120 s.

Les plus gros changements (rapport des cooldowns) :

| sort | rôle | cooldown | cast |
|---|---|---|---|
| Purification (soigneur, base) | utilitaire | 12 → 95 s | |
| Siphon Arcanique (mage, base) | utilitaire | 21 → 120 s | 1,5 → 2,5 s |
| Vague Purificatrice (lightbringer) | utilitaire | 12 → 65 s | |
| Hymne de Vigueur (cantor) | utilitaire | 20 → 105 s | 0 → 2,5 s |
| Déchirure d'Âme (occultist) | utilitaire | 26 → 120 s | 2 → 2,5 s |
| Rugissement Affaiblissant (warlord) | courant | 20 → 90 s | 0 → 2,5 s |
| Lancer de Dague (voleur, base) | courant | 8 → 35 s | |
| Émergence (summoner) | ultime | 42 → 180 s | |
| Bordée (gunslasher) | ultime | 42 → 180 s | 0 → 2,5 s |
| Choc de Poivre (spice master) | courant | 15 → 60 s | 0 → 2,5 s |

Liste complète : `python -X utf8 scripts/balance/skill_timing.py --report` avant application, ou le
diff des `skills.json`.

### Réduction de recharge (non tranchée, plafond inchangé)

Au plafond de 40 %, la charge au niveau 60 repasse à 1,27 de médiane (96 % du temps hors
remplissage, 8 kits à 100 %) : la réduction annule l'essentiel de la passe. Options chiffrées par
`--report` (`timing.cdr_options`) sur les cooldowns de la règle, niveau 60 :

| option | charge méd | part du temps |
|---|---|---|
| sans réduction | 0,76 | 71 % |
| plafond 40 % (actuel) | 1,27 | 96 % |
| plafond 20 % | 0,95 | 83 % |
| 40 % hors ultimes et signatures | 1,23 | 95 % |
| 20 % hors ultimes et signatures | 0,94 | 81 % |

Exclure ultimes et signatures ne change presque rien à la charge (ils pèsent peu) mais garde « un
ultime par combat ». **Option proposée : plafond 20 %, ultimes et signatures exclus** ; elle se
change dans `combat.json` **et** dans `room.cpp` (plafond en dur).

### Points à trancher

1. Plafond de réduction de recharge (ci-dessus).
2. 9 kits au-dessus du budget au niveau 60 (barres de 12 sorts courts, voleur et archer surtout) :
   accepter, ou baisser `min_density_scale`.
3. Préparation de 2,5 s pour les sorts forts des sous-classes de contact, ultimes physiques compris :
   la garder, ou un autre contre-jeu. Contre-jeux possibles avec le serveur actuel : le cast lui-même
   (interruptible par stun), un télégraphe (la zone est re-résolue à la fin, une cible peut sortir) ;
   la canalisation demanderait du code (`is_channeled`).
4. Riposte parfaite (countermaster), ultime réflexe : reste instantanée.
5. Le plafond de CDR en dur dans `room.cpp`, et `silence` qui n'interrompt pas malgré
   `interrupts_cast`.
6. Les tableaux de `souffle_par_niveau.md` (rotation, « à sec ») ont été calculés avec les anciens
   cooldowns : la phase 3 les refera.

## 7. Questions au propriétaire

1. **Réduction de recharge** : au plafond de 40 %, toute règle de cooldown est divisée par 1,67 et le
   spam revient. Baisser le plafond (20-25 %), ou exclure ultimes et signatures de la CDR ?
2. **Ultime toutes les 2-3 minutes** : un combat de pack dure 46 s (niveau 20) à 260 s (niveau 100,
   `souffle_par_niveau.md`). À 150 s, l'ultime ne sort pas dans un combat sur deux au niveau 20. Est-ce
   voulu (ultime de boss), ou faut-il un cooldown qui commence à 0 en entrant en combat ?
3. **Signature de sous-classe** : un deuxième gros sort (75-120 s, plus fort qu'un courant), ou un sort
   courant comme les autres ?
4. **Remplissage de spécialisation** (40 sorts, 9 à 36 s) : vrais remplissages (sous 6 s, faibles),
   ou sorts courants légers ?
5. **Charge cible** : combien de GCD sur trois doivent revenir au remplissage en combat soutenu ?
6. **Novas à 5 cases** (point 8) : corrigé (phase 2). Le serveur recentre `self_and_enemies` sur le
   lanceur seulement sans cible ; avec une cible, il pose la zone sur elle jusqu'à `max(base_range, 5)`
   (`grid_distance.hpp aoe_placement_range`), et l'IA ne les traite en nova qu'à `range` 0-1.
7. **Classes physiques** : sans incantation, quel coût pour leurs ultimes (télégraphe, immobilisation) ?
8. **Champs morts** (`power_per_level`, `effect_power_per_level`, `cooldown_per_level`,
   `heal_scaling_stat`, `cast_interruptible`) : les supprimer de la data ?
