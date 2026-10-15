# Matrice de puissance des sorts

Statut : phase 1 sur 3, mesure seulement, aucune valeur de sort modifiée (2026-10-15, branche
`vac_skill-matrix`).
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
8. **5 novas posées à 5 cases** : `target: self_and_enemies` sans `range: 0` (Tempête de Lames,
   Présence Suffocante, Déchaînement, Tornade d'Acier, Choc Sismique). La règle nova du
   `CLAUDE.md` n'est pas appliquée, et un guerrier à portée 2 frappe « autour de lui » à 5 cases.
9. **Remplissages de spécialisation** : 40 sorts, cooldown 9 à 36 s (médiane 12 s), contre 3 à 5 s en
   base. La Coupe Épicée (Spice Master) fait 382 points pour 15 Souffle avec 36 s de recharge : un remplissage à 36 s n'en est plus un.

## 5. Règles proposées (non appliquées)

### Phase 2 : cooldowns et incantations

Le spam est un problème de **charge du kit**, pas de sort isolé : c'est la règle à poser en premier.

1. **Budget de charge** : Σ max(GCD, cast) / cooldown sur les sorts hors remplissage d'un kit
   ≤ 0,40 à CDR 0, soit ≤ 0,67 à CDR 40 % : au moins un GCD sur trois revient au remplissage, même
   avec la réduction maximale. Aujourd'hui : 1,12 et 1,86 de médiane.
2. **Cooldown par rôle, fonction de la puissance** : CD = clamp(puissance r1 / D, min, max).

   | rôle | D (points/s) | fourchette |
   |---|---|---|
   | ultime | 10 | **120-180 s** (demande du propriétaire) |
   | signature | 4 | 75-120 s |
   | courant | 6 | 30-90 s |
   | défensif, utilitaire | 4 | 45-120 s |
   | remplissage | inchangé | 3-6 s, et le tag `filler` réservé aux sorts sous 6 s |

   Simulé sur la data actuelle : courant 44 s de médiane, ultime 128 s ; charge 0,55 à CDR 0
   (54 % du temps hors remplissage) mais encore 0,91 au plafond de CDR (80 %). **Le budget du point 1
   n'est tenable qu'avec une réponse à la question 1** (plafond de CDR).
3. **Cast fonction de la puissance nette** (grille de `balance_model.json`, gardée) : ≤ 2 s sous
   300 points, 2,5 s à 300-700, 3 à 4 s au-delà, pour les lanceurs. Ultimes : ≥ 2,5 s pour toutes les
   classes, ou un autre contre-jeu (télégraphe) pour les classes physiques.
4. Garder les contrôles de `balance_model.json` : pas deux sorts au même cooldown dans un kit, au moins
   un sort sous 20 s par kit (hors remplissage).

### Phase 3 : coût en Souffle

1. **Coût r1 = a(rôle, palier) × (puissance nette r1 / 100)^β**, β ≈ 0,5 (sous-linéaire : le cooldown
   borne déjà le gros sort ; la pente mesurée aujourd'hui est 0,32). À rôle et palier égaux, deux sorts
   de puissance ×4 coûtent ×2.
2. **Autonomie croissante avec le rôle** (coût / (CD × régén)), cible de `balance_model.json` reprise :
   remplissage 0,6, courant 1,0-1,4, signature 1,6, ultime 2,0.
3. Garder `tier_order` (base < sous-classe < spé à rôle égal) et `per_rank_rule` (coût par rang = gain
   de puissance), qui existent déjà dans `skill_system.json mana_cost_scaling` ; remplacer les familles
   de `tier_order` par les rôles de la matrice, une seule classification.

## 6. Questions au propriétaire

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
6. **Novas à 5 cases** (point 8) : corriger les `range` (une donnée, pas une valeur d'équilibrage) ?
7. **Classes physiques** : sans incantation, quel coût pour leurs ultimes (télégraphe, immobilisation) ?
8. **Champs morts** (`power_per_level`, `effect_power_per_level`, `cooldown_per_level`,
   `heal_scaling_stat`, `cast_interruptible`) : les supprimer de la data ?
