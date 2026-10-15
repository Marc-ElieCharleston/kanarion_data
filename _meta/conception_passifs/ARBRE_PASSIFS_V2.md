# Arbre des passifs V2 (brouillon, 2026-10-15)

Statut : **proposition, bras Attaque seul**. Rien n'est branché : la V1 (`classes/passive_tree.json`)
reste celle que lisent le serveur et le client. Data du brouillon : `arbre_v2_attaque.json`.
Simulation : `python -I sim_arbre_v2.py arbre_v2_attaque.json` (les bras voisins sont clonés depuis
Attaque pour tester la géométrie).

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
| Ponts | entre bras voisins, au niveau des notables 30 : petit (2) + hybride (6) + petit (2) = 10 points |

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

## Ce que donne la simulation (100 points)

| Build | Coût | Notables |
|---|---|---|
| All-in Attaque | 75 (reste 25) | 15, 30, 50, méga |
| All-in + notable 15 d'un voisin | 90 | + 1 petit notable |
| All-in + notable 30 d'un voisin | 105 | **impossible** (et les ponts sont fermés) |
| Hybride éloigné : Attaque 50 + Soutien 50 | 100 | 2 × (15, 30, 50) |
| Hybride voisin : Attaque 50 + Défense 50 + Affaiblissement 30 | 100 | 15, 30, 50 + 30, 50 + 30 + 2 hybrides |
| Hybride voisin : Attaque 50 + Défense 50 + les 2 hybrides du pont | 91 | 15, 30, 50 + 30, 50 + 2 hybrides |

Chaque notable tombe exactement à sa distance cible (15 / 30 / 50 / 75).

Nombre de variantes : par bras, 2 × 3 × 2 × 2 = 24 all-in (sans compter les routes et les 25 points
restants) ; hybrides : 10 paires de bras, 5 paires voisines avec ponts, et les formes à 3 bras.

## Budget de puissance (à vérifier en jeu)

- All-in : 4 notables dont le méga, + 25 points (un petit notable ailleurs, ou un détour).
- Hybride voisin : 8 notables (dont 2 hybrides), pas de méga.
- Cible : **méga ≈ 4 notables moyens**. Si les hybrides dominent, on monte les mégas ; sinon on monte
  les hybrides. Les contreparties des mégas gardent un vrai choix de style.

## Reset des points (proposition)

- Gratuit jusqu'au niveau 20.
- Ensuite : `base_gold × niveau × (1 + 0,5 × resets payants récents)` ; le compteur baisse de 1 toutes
  les 2 semaines sans reset payant. `base_gold` à chiffrer avec l'économie.
- Pass : 1 reset gratuit par semaine, non cumulable.

## Ce que la V2 demande au code (après validation de la data)

- Serveur (economy + `passive_draft`) et client (`passive_tree_rules.gd`) : passage seulement au rang
  max, groupes de choix à N options, 1 méga, ponts fermés par le méga, plus de slots par niveau, reset
  payant progressif.
- `systems/progression.json` : `starting_passive_points: 1`, lu par `level_calc`.
- Nouvelles mécaniques de combat : `damage_vs_target_hp_above` (Premier sang), `stacking_stat_on_event`
  (Élan), `consecutive_hit_stacks` (Acharnement), `crit_ignores_defense` (Brise-garde),
  `non_crit_damage_modifier` (Coup Fatal), `stats_while_hp_above` (Garde de fer),
  `damage_vs_target_debuff_count` (Curée), événement `kill` pour `stat_window_after_event`.
- Migration : rembourser tous les points de l'arbre V1 au passage en V2.

## Questions ouvertes

1. Valeurs des mégas : Déchaînement +35 % est-il « extrêmement puissant » assez ?
2. Ponts à 10 points : l'hybride voisin tombe pile à 100. On garde, ou on laisse un peu de marge ?
3. Prix de base du reset.
