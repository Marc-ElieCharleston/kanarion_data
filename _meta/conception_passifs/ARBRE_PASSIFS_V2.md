# Arbre des passifs V2 (brouillon, 2026-10-15)

Statut : **proposition, les 5 bras et les 5 ponts** (2026-10-16). Rien n'est branché : la V1
(`classes/passive_tree.json`) reste celle que lisent le serveur et le client.

- Bras Attaque : `arbre_v2_attaque.json`, écrit par le propriétaire (référence, inchangé).
- Arbre complet : `arbre_v2.json`, **généré** par `gen_arbre_v2.py`. Attaque y est recopiée telle quelle ;
  Défense, Soin, Soutien et Affaiblissement reprennent **son gabarit** (mêmes rangs, coûts et arêtes,
  emplacement par emplacement), donc chaque notable tombe à la même distance. Pour retoucher un bras,
  modifier son contenu dans `gen_arbre_v2.py` puis relancer le script, pas le JSON à la main.
- Simulation : `python -I sim_arbre_v2.py arbre_v2.json` (vrais bras). Sur `arbre_v2_attaque.json`, le
  simulateur clone toujours les bras depuis Attaque, comme avant.

## Pourquoi une V2

Simulation de la V1 avec 100 points : un bras complet coûte 36 à 38 points, et 2 capstones tiennent
dans le budget (72 pts, 6 slots sur 6). Tout le monde finit avec 2 bras complets + des petits nœuds
d'un 3e : environ 40 variantes, et une seule vraiment bonne par rôle. Le all-in n'existe pas.

## Intention du propriétaire

- 100 points : 1 au niveau 1, puis 1 par niveau.
- Les notables sont placés **à distance du centre** : petits à 15 points, petits moyens à 30, moyens à
  50, **méga à 75**.
- **All-in** : le méga au bout d'un bras (75), il reste 25 points.
- **Hybride** : pas de méga, mais deux moyens à 50 ; et si les bras sont voisins, deux à 50 **et** un
  à 30. Gameplay différent, pas plus faible. Un all-in ne peut pas être hybride.
- Les doublons de stats entre bras ne gênent pas. Flat et % mélangés.
- Le reset coûte de plus en plus cher ; le pass peut offrir un reset gratuit par semaine.

## Règles (modèle à distance)

| Règle | Valeur |
|---|---|
| Points | 1 au niveau 1 + 1 par niveau = 100 |
| Coûts | petit nœud 1/rang ; notable 15 : 3 ; notable 30 : 5 ; notable 50 : 6 ; méga : 10 ; détour : 5 ; hybride : 6 |
| Chemin | un nœud s'achète s'il touche un nœud acquis ; un petit nœud ne laisse passer qu'**à son rang max** |
| Choix | à chaque notable, 1 option sur 2 ou 3 ; les deux routes entre deux notables ne sont pas exclusives (la 2e coûte ses points) |
| Méga | 1 seul ; avoir un méga **ferme les ponts** |
| Ponts | entre bras voisins, au niveau des notables 30 : petit (1) + hybride (6) + petit (1) = 8 points |

Il n'y a plus de seuils ni de slots : la profondeur se paie avec le chemin, et le niveau limite
naturellement (méga au plus tôt vers le niveau 75).

## Bras Attaque

| Distance | Contenu |
|---|---|
| 0 → 12 | Force, Œil vif, Tranchant, Visée (3 rangs, flat) |
| **15** | *Exécution* (+15 % sous 30 % PV) **ou** *Premier sang* (+20 % au-dessus de 90 % PV). Détour à 20 : *Allonge* (+1 portée) |
| 15 → 30 | 2 routes de 10 : flat (Poigne +atk/mag, Œil de lynx +crit) ou % (Vigueur +atk/mag %, Férocité +dégâts %) |
| **30** | Le style, 1 sur 3 : *Lame* (instinct du tueur), *Brute* (+10 pénétrations), *Cadence* (élan : +2 % par sort, 5 cumuls) |
| 30 → 50 | 2 routes de 14 : critique (Létalité, Point faible, Main sûre) ou puissance (Carnage, Puissance brute, Perforation) |
| **50** | *Acharnement* (+4 % par coup sur la même cible, 5 cumuls) **ou** *Brise-garde* (les crits ignorent 30 % armure/RM). Détour à 55 : *Soif de sang* |
| 50 → 75 | La route du all-in : 3 maîtrises en % (15) |
| **75 méga** | *Coup Fatal* : crits +50 dégâts crit et −1 s de recharge ; non-crits −15 %. **Ou** *Déchaînement* : +35 % de dégâts ; −30 % soins reçus, −15 % PV max |

Ponts côté Attaque :
- Attaque ↔ Défense : *Riposte* (sur le chemin, +40 % après blocage/parade), *Garde de fer* (à côté).
- Attaque ↔ Affaiblissement : *Opportuniste* (sur le chemin, +20 % crit sous contrôle), *Curée* (à côté).

## Bras Défense (proposition)

| Distance | Contenu |
|---|---|
| 0 → 12 | Peau dure (+armure), Constitution (+PV), Esprit calme (+RM), Pas léger (+esquive), en flat |
| **15** | *Peau de fer* (−15 % dégâts de zone) **ou** *Position tenue* (immobile 3 s : −10 %). Détour à 20 : *Sang-froid* (−12 % d'un attaquant à plus de 3 cases) |
| 15 → 30 | Flat (Rempart +armure/RM, Robustesse +PV) ou % (Bastion +PV %, Carapace +armure/RM %) |
| **30** | Le style, 1 sur 3 : *Garde* (+8 parade, +8 blocage), *Représailles* (15 % d'épines), *Vampirisme* (+6 vol de vie, +6 vol de sort) |
| 30 → 50 | Endurance (réduction des dégâts), Résilience (résistance aux effets), Ancrage (ténacité) ; ou Écailles (armure/RM %), Colosse (PV %), Régénération (regen PV %) |
| **50** | *Inébranlable* (bouclier de 20 % sous 30 % de PV, 45 s) **ou** *Garde du corps* (tu prends 20 % des dégâts d'un allié adjacent). Détour à 55 : *Dernier rempart* (sous 30 % de PV : −20 %) |
| 50 → 75 | Maîtrises : bastion (PV %), cuirasse (armure/RM %), endurance (réduction) |
| **75 méga** | *Forteresse* : +30 % PV, +15 % réduction ; −25 % dégâts infligés. **Ou** *Colère du titan* : 30 % d'épines, +10 vol de vie ; −25 % soins reçus |

## Bras Soin (proposition)

| Distance | Contenu |
|---|---|
| 0 → 12 | Mains chaudes (+puissance de soin), Sève (+Souffle), Grâce (+soins reçus), Concentration (+magie) |
| **15** | *Aide salvatrice* (+20 % de soins sous 40 % de PV) **ou** *Soins préventifs* (+15 % au-dessus de 70 %). Détour à 20 : *Soin étendu* (30 % sur l'allié blessé le plus proche) |
| 15 → 30 | Flat (Ferveur +puissance de soin, Réserve +Souffle) ou % (Sagesse +magie %, Art du bouclier +puissance de bouclier) |
| **30** | *Transfusion* (10 % des soins donnés te reviennent), *Vol de sort* (+8), *Débordement* (le surplus de soin devient un bouclier, 50 %, 5 s) |
| 30 → 50 | Prière rapide (incantation), Persévérance (recharge), Recueillement (soins reçus) ; ou Grâce divine (magie %), Fontaine (Souffle %), Rayonnement (puissance de bouclier) |
| **50** | *Dernier souffle* (sauve un allié une fois par combat) **ou** *Ondée* (1 soin sur 4 soigne aussi à 2 cases, 30 %). Détour à 55 : *Sacrifice* (un allié sous 20 % reçoit 10 % de tes PV, 30 s) |
| 50 → 75 | Maîtrises : soins, sagesse (magie %), source (Souffle %) |
| **75 méga** | *Sanctuaire* : +30 % puissance de soin, soins sur la durée +50 % de durée ; −30 % dégâts infligés. **Ou** *Martyr* : les soins coûtent 5 % de tes PV au lieu du Souffle, +25 % de soins |

## Bras Soutien (proposition)

| Distance | Contenu |
|---|---|
| 0 → 12 | Persistance (durée des buffs), Vivacité (incantation), Souffle long (+Souffle), Volonté (résistance aux effets) |
| **15** | *Inspiration* (allié buffé : +8 % de dégâts) **ou** *Protection* (allié buffé : −8 % de dégâts subis). Détour à 20 : *Aura étendue* (un buff ciblé touche un allié adjacent) |
| 15 → 30 | Flat (Esprit vif recharge, Ténacité) ou % (Clarté Souffle %, Harmonie magie %) |
| **30** | *Rythme* (1 sort sur 4 gratuit), *Chef d'orchestre* (buff : −1 s de recharge à l'allié), *Clairvoyance* (+15 % durée des buffs, +10 % des affaiblissements) |
| 30 → 50 | Sérénité (durée buffs), Discipline (recharge), Fermeté (résistance) ; ou Éloquence (incantation), Ampleur (Souffle %), Présence (PV %) |
| **50** | *Bannière* (aura à 2 cases : +6 % dégâts, −6 % subis) **ou** *Second souffle* (buff : rend 5 % du Souffle max de l'allié). Détour à 55 : *Élan partagé* (chaque buff donné : +3 % de dégâts, 5 cumuls) |
| 50 → 75 | Maîtrises : durée, tempo (recharge), clarté (Souffle %) |
| **75 méga** | *Maître de guerre* : buffs +50 % de durée et +10 % de dégâts aux alliés ; −25 % de tes dégâts. **Ou** *Hâte collective* : allié buffé −20 % de recharge ; tes buffs coûtent +50 % de Souffle |

## Bras Affaiblissement (proposition)

| Distance | Contenu |
|---|---|
| 0 → 12 | Main sûre (précision), Venin (chance d'effet), Prolongation (durée des affaiblissements), Perce-esprit (pénétration magique) |
| **15** | *Emprise* (+10 % contre une cible contrôlée) **ou** *Fléau* (+12 % contre une cible qui porte 2 affaiblissements). Détour à 20 : *Contagion* |
| 15 → 30 | Flat (Ténèbres chance d'effet, Hâte recharge) ou % (Malice atk/mag %, Corruption durée) |
| **30** | *Zone de contrôle* (contrôle propagé à un adjacent), *Maître du tempo* (contrôle : −1 s aux autres recharges), *Lacération* (+20 % aux dégâts sur la durée) |
| 30 → 50 | Fatalité (chance d'effet), Persistance noire (durée), Brise-armure (pénétrations) ; ou Malédiction (atk/mag %), Affliction (dégâts %), Maléfice (durée) |
| **50** | *Supplice* (+4 % par affaiblissement porté, 5 max) **ou** *Entrave* (contrôles +1 s). Détour à 55 : *Brise-volonté* (cible contrôlée −15 résistance aux effets) |
| 50 → 75 | Maîtrises : emprise (chance d'effet), durée, malice (atk/mag %) |
| **75 méga** | *Peste* : chaque affaiblissement touche aussi un ennemi adjacent ; durée −25 %. **Ou** *Seigneur des chaînes* : contrôles +50 % de durée ; −25 % dégâts infligés |

## Ponts (les 5)

| Pont | Passage (×2, 1 pt) | Hybride sur le chemin | Hybride à côté |
|---|---|---|---|
| Attaque ↔ Défense | +4 armure, +4 RM | *Riposte* | *Garde de fer* |
| Attaque ↔ Affaiblissement | +4 armure, +4 RM | *Opportuniste* | *Curée* |
| Défense ↔ Soin | +12 PV, +2 soins reçus | *Rempart vivant* (10 % des soins reçus en bouclier) | *Second élan* (une fois, sous 25 % : +25 % PV) |
| Soin ↔ Soutien | +10 Souffle, +2 durée des buffs | *Chant de guerre* (un buff retire un affaiblissement) | *Bénédiction* (un buff soigne 3 % des PV max) |
| Soutien ↔ Affaiblissement | +2 chance d'effet, +2 résistance aux effets | *Coordination* (+8 % contre tes cibles affaiblies) | *Marque du chef* (+10 % crit contre tes cibles affaiblies) |

Les mécaniques de la V1 sont reprises là où elles collent (Peau de fer, Position tenue, Sang-froid,
Inébranlable, Aide salvatrice, Soin étendu, Transfusion, Dernier souffle, Inspiration, Aura étendue,
Rythme, Chef d'orchestre, Emprise, Contagion, Zone de contrôle, Maître du tempo, Rempart vivant, Chant de
guerre, Coordination) : elles sont déjà codées et testées en combat réel (gate du 2026-10-01).

## Ce que donne la simulation (100 points)

| Build | Coût | Notables |
|---|---|---|
| All-in Attaque | 75 (reste 25) | 15, 30, 50, méga |
| All-in + notable 15 d'un voisin | 90 | + 1 petit notable |
| All-in + notable 30 d'un voisin | 105 | **impossible** (et les ponts sont fermés) |
| Hybride éloigné : Attaque 50 + Soutien 50 | 100 | 2 × (15, 30, 50) |
| Hybride voisin : Attaque 50 + Défense 50 + Affaiblissement 30 | 96 (reste 4) | 15, 30, 50 + 30, 50 + 30 + 2 hybrides |
| Hybride voisin : Attaque 50 + Défense 50 + les 2 hybrides du pont | 89 | 15, 30, 50 + 30, 50 + 2 hybrides |

Chaque notable tombe exactement à sa distance cible (15 / 30 / 50 / 75).

Nombre de variantes : par bras, 2 × 3 × 2 × 2 = 24 all-in (sans compter les routes et les 25 points
restants) ; hybrides : 10 paires de bras, 5 paires voisines avec ponts, et les formes à 3 bras.

Avec les 5 vrais bras (`sim_arbre_v2.py arbre_v2.json`, 2026-10-16) : tous les notables tombent à
15 / 30 / 50 / 75 (détours à 20 et 55) ; pour chaque bras, all-in 75, + notable 15 du voisin 90,
+ notable 30 du voisin 105 (impossible) ; hybride voisin 83, ou 89 avec les deux hybrides du pont.
**Nouveau :** un hybride *éloigné* (bras à 2 crans) coûte **96** en passant par les deux ponts, au lieu
de 100 par le centre : les ponts servent aussi aux hybrides éloignés, et rapportent 2 hybrides en route.
À décider : on le garde (récompense le hybride à 3 bras) ou on monte le coût des passages.

## Budget de puissance (à vérifier en jeu)

- All-in : 4 notables dont le méga, + 25 points (un petit notable ailleurs, ou un détour).
- Hybride voisin : 8 notables (dont 2 hybrides), pas de méga.
- Cible : **méga ≈ 4 notables moyens**. Si les hybrides dominent, on monte les mégas ; sinon on monte
  les hybrides. Les contreparties des mégas gardent un vrai choix de style.

## Reset des points (proposition)

- Gratuit jusqu'au niveau 20.
- Ensuite, le prix se pense **en temps de jeu**, pas en or : environ 1 heure de farm à son niveau pour
  le premier reset, puis +50 % par reset payant récent (le compteur baisse de 1 toutes les 2 semaines
  sans reset payant). Le prix en or = ces heures × l'or gagné par heure au niveau du joueur, une fois
  qu'on aura le calcul de l'or par heure (pas encore fait : 10 or durs à gagner ou 10 000, ça change
  tout).
- Pass : 1 reset gratuit par semaine, non cumulable.

## Ce que la V2 demande au code (après validation de la data)

- Serveur (economy + `passive_draft`) et client (`passive_tree_rules.gd`) : passage seulement au rang
  max, groupes de choix à N options, 1 méga, ponts fermés par le méga, plus de slots par niveau, reset
  payant progressif.
- `systems/progression.json` : `starting_passive_points: 1`, lu par `level_calc`.
- Nouvelles mécaniques de combat : `damage_vs_target_hp_above` (Premier sang), `stacking_stat_on_event`
  (Élan), `consecutive_hit_stacks` (Acharnement), `crit_ignores_defense` (Brise-garde),
  `non_crit_damage_modifier` (Coup Fatal), `stats_while_hp_above` (Garde de fer),
  `damage_vs_target_debuff_count` (Curée, Fléau), événement `kill` pour `stat_window_after_event`.
- Pour les 4 bras proposés, en plus : `damage_redirect_from_adjacent_ally` (Garde du corps),
  condition `hp_below` de `damage_taken_reduction_conditional` (Dernier rempart),
  `heal_bonus_target_hp_above` (Soins préventifs), `overheal_to_shield` (Débordement),
  `heal_every_n_splash_area` (Ondée), `give_hp_to_ally_below` (Sacrifice), `hot_duration_bonus`
  (Sanctuaire), `heal_cost_hp_instead_of_breath` (Martyr), `buff_grants_stat` sur
  `damage_reduction` / `cooldown_reduction` (Protection, Hâte collective), `ally_aura_stats` (Bannière),
  `buff_restores_mp` (Second souffle), `stacking_stat_on_event` sur `buff_applied_to_ally` (Élan
  partagé), `buff_cost_modifier` (Hâte collective), `dot_damage_bonus` (Lacération),
  `damage_per_target_debuff` (Supplice), `control_duration_bonus` / `control_duration_pct` (Entrave,
  Seigneur des chaînes), `target_stat_while_controlled` (Brise-volonté), `debuff_splash_adjacent`
  (Peste), `self_heal_once_below` (Second élan), `buff_heals_ally` (Bénédiction),
  `ally_buffed_crit_vs_debuffed` (Marque du chef). Liste tenue dans `arbre_v2.json` `_meta.new_mechanics`.
- Migration : rembourser tous les points de l'arbre V1 au passage en V2.

## Questions ouvertes

Réglé le 2026-10-15 : Déchaînement garde +35 % **avec** sa contrepartie (−30 % soins reçus, −15 % PV
max) ; ponts passés de 10 à 8 points pour laisser 4 points de marge à l'hybride voisin.

1. Prix du reset : en attente du calcul de l'or gagné par heure selon le niveau.
2. **Bonus de points façon parchemins Dofus** (pas décidé). Si des objets donnent des points d'arbre
   en plus, l'all-in gagne vite le notable 30 d'un voisin par le centre (105 points aujourd'hui, donc
   5 points bonus suffisent). Les ponts restent fermés par le méga. Recommandation : les parchemins
   donnent des **stats** (comme dans Dofus), pas des points d'arbre ; sinon les plafonner à 3.
