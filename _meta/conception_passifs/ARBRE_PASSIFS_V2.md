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
| 0 → 12 | Peau dure, Constitution, Esprit calme, Pas leger (flat, 3 rangs) |
| **15** | *Peau de fer* (-15 % de degats subis des attaques de zone) **ou** *Position tenue* (Immobile depuis 3 s : -10 % de degats subis). Détour à 20 : *Sang-froid* (-12 % de degats subis d'un attaquant a plus de 3 cases) |
| 15 → 30 | Rempart, Robustesse ; ou Bastion, Carapace |
| **30** | 1 sur 3 : *Garde : parade* (+8 % de chance de parade et +8 % de chance de blocage), *Represailles : epines* (Renvoie 15 % des degats subis a l'attaquant), *Endurance : vampirisme* (+6 % de vol de vie et +6 % de vol de sort) |
| 30 → 50 | Endurance, Resilience, Ancrage ; ou Ecailles, Colosse, Regeneration |
| **50** | *Inebranlable* (Sous 30 % de PV : bouclier egal a 20 % de tes PV max. Une fois toutes les 45 s) **ou** *Dernier rempart* (Sous 30 % de PV : -20 % de degats subis). Détour à 55 : *Mur vivant* (Apres un blocage ou une parade : -20 % de degats subis pendant 3 s) |
| 50 → 75 | Maitrise : bastion, Maitrise : cuirasse, Maitrise : endurance |
| **75 méga** | *Forteresse* (+30 % de PV max et +15 % de reduction des degats subis. Contrepartie : -25 % de degats infliges) **ou** *Colere du titan* (Renvoie 30 % des degats subis et +10 % de vol de vie. Contrepartie : -25 % de soins recus) |

## Bras Soin (proposition)

| Distance | Contenu |
|---|---|
| 0 → 12 | Mains chaudes, Seve, Grace, Concentration (flat, 3 rangs) |
| **15** | *Aide salvatrice* (+20 % de soins sur une cible sous 40 % de ses PV) **ou** *Soins preventifs* (+15 % de soins sur une cible au-dessus de 70 % de ses PV). Détour à 20 : *Soin etendu* (Un soin cible soigne aussi l'allie blesse le plus proche de 30 % du soin) |
| 15 → 30 | Ferveur, Reserve ; ou Sagesse, Art du bouclier |
| **30** | 1 sur 3 : *Transfusion* (10 % des soins donnes a un allie te reviennent), *Vol de sort* (+8 % de vol de sort), *Egide sacree* (+15 % de puissance de bouclier et +10 % de soins recus) |
| 30 → 50 | Priere rapide, Perseverance, Recueillement ; ou Grace divine, Fontaine, Rayonnement |
| **50** | *Dernier souffle* (Une fois par combat, un allie qui devait mourir reste a 1 PV et recoit 25 % de ses PV max) **ou** *Ondee* (Un soin cible soigne aussi les 2 allies blesses les plus proches de 25 % du soin). Détour à 55 : *Priere de combat* (Chaque soin lance donne +3 % de puissance de soin pendant 6 s, cumulable 5 fois) |
| 50 → 75 | Maitrise : soins, Maitrise : sagesse, Maitrise : source |
| **75 méga** | *Sanctuaire* (+30 % de puissance de soin et +25 % de duree des buffs (soins sur la duree compris). Contrepartie : -30 % de degats infliges) **ou** *Martyr* (+40 % de puissance de soin et +20 % de soins recus. Contrepartie : -20 % de PV max) |

## Bras Soutien (proposition)

| Distance | Contenu |
|---|---|
| 0 → 12 | Persistance, Vivacite, Souffle long, Volonte (flat, 3 rangs) |
| **15** | *Inspiration* (Un allie que tu buffes inflige +8 % de degats pendant le buff) **ou** *Protection* (Un allie que tu buffes subit -8 % de degats pendant le buff). Détour à 20 : *Aura etendue* (Un buff cible touche aussi un allie adjacent) |
| 15 → 30 | Esprit vif, Tenacite ; ou Clarte, Harmonie |
| **30** | 1 sur 3 : *Rythme* (Un sort sur 4 qui coute du Souffle est gratuit), *Chef d'orchestre* (Buffer un allie reduit ses recharges de 1 s (une fois toutes les 5 s par allie)), *Clairvoyance* (+15 % de duree des buffs et +10 % de duree des affaiblissements) |
| 30 → 50 | Serenite, Discipline, Fermete ; ou Eloquence, Ampleur, Presence |
| **50** | *Chef de file* (Un allie que tu buffes inflige +6 % de degats et subit -6 % de degats pendant le buff) **ou** *Acceleration* (Un allie que tu buffes a +15 % de vitesse d'incantation pendant le buff). Détour à 55 : *Elan partage* (Chaque buff donne a un allie te donne +3 % de degats pendant 6 s, cumulable 5 fois) |
| 50 → 75 | Maitrise : duree, Maitrise : tempo, Maitrise : clarte |
| **75 méga** | *Maitre de guerre* (Tes buffs sur les allies durent 50 % plus longtemps et donnent +10 % de degats. Contrepartie : -25 % de tes propres degats) **ou** *Hate collective* (Un allie que tu buffes a -20 % de recharge pendant le buff. Contrepartie : -20 % de tes PV max) |

## Bras Affaiblissement (proposition)

| Distance | Contenu |
|---|---|
| 0 → 12 | Main sure, Venin, Prolongation, Perce-esprit (flat, 3 rangs) |
| **15** | *Emprise* (+10 % de degats contre une cible sous controle) **ou** *Fleau* (+12 % de degats contre une cible qui porte au moins 2 affaiblissements). Détour à 20 : *Contagion* (Quand une cible meurt, tes affaiblissements passent sur l'ennemi le plus proche) |
| 15 → 30 | Tenebres, Hate ; ou Malice, Corruption |
| **30** | 1 sur 3 : *Zone de controle* (Un controle cible touche aussi un ennemi adjacent), *Maitre du tempo* (Controler un ennemi reduit tes autres recharges de 1 s (une fois toutes les 3 s)), *Venin profond* (+15 % de chance d'effet et +10 % de duree des affaiblissements) |
| 30 → 50 | Fatalite, Persistance noire, Brise-armure ; ou Malediction, Affliction, Malefice |
| **50** | *Supplice* (+4 % de degats par affaiblissement que porte la cible, jusqu'a 5) **ou** *Etau* (+15 % de degats et +10 % de chance critique contre une cible sous controle). Détour à 55 : *Brise-volonte* (Apres avoir controle un ennemi : +15 % de chance d'effet pendant 4 s) |
| 50 → 75 | Maitrise : emprise, Maitrise : duree, Maitrise : malice |
| **75 méga** | *Peste* (Un affaiblissement pose par un sort cible touche aussi un ennemi adjacent (sans relance en chaine). Contrepartie : tes affaiblissements durent 25 % de moins) **ou** *Seigneur des chaines* (+40 % de duree des affaiblissements et +20 % de chance d'effet. Contrepartie : -25 % de degats infliges) |

## Ponts (les 5)

| Pont | Passage (×2, 1 pt) | Hybride sur le chemin | Hybride à côté |
|---|---|---|---|
| Attaque ↔ Défense | +4 armure et +4 resistance magique | *Riposte* (Apres un blocage ou une parade, ta prochaine attaque inflige +40 % de degats) | *Garde de fer* (Tant que tu es au-dessus de 70 % de tes PV : +12 % de degats infliges et -8 % de degats recus) |
| Attaque ↔ Affaiblissement | +4 armure et +4 resistance magique | *Opportuniste* (+20 % de chance critique contre une cible sous controle) | *Curee* (+20 % de degats contre une cible qui porte au moins 3 affaiblissements) |
| Défense ↔ Soin | +12 PV max et +2 % de soins recus | *Rempart vivant* (10 % des soins que tu recois deviennent un bouclier (5 s)) | *Second elan* (Sous 25 % de PV : bouclier egal a 15 % de tes PV max. Une fois toutes les 60 s) |
| Soin ↔ Soutien | +10 Souffle max et +2 % de duree des buffs | *Chant de guerre* (Un buff donne a un allie lui retire un affaiblissement) | *Benediction* (Un allie que tu buffes recoit +10 % de soins pendant le buff) |
| Soutien ↔ Affaiblissement | +2 % de chance d'effet et +2 resistance aux effets | *Coordination* (Un allie que tu buffes inflige +8 % de degats aux cibles que tu as affaiblies) | *Marque du chef* (Un allie que tu buffes a +10 % de chance critique contre les cibles que tu as affaiblies) |

Ces tables sont **générées depuis `arbre_v2.json`** par `doc_arbre_v2.py` : modifier le contenu dans `gen_arbre_v2.py`,
relancer les deux scripts. Rendu en image : `python -I render_arbre_v2.py arbre_v2.json arbre_v2.png`.

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
- Pour les 4 bras proposés : **aucune mécanique entièrement nouvelle**, seulement 9 extensions d'une
  mécanique déjà codée (un paramètre, un événement ou une stat de plus), listées dans
  `arbre_v2.json` `_meta.new_mechanics`. Les notables sans effet spécial sont en stats (comme *Brute*).
- Migration : rembourser tous les points de l'arbre V1 au passage en V2.

## Questions ouvertes

Réglé le 2026-10-15 : Déchaînement garde +35 % **avec** sa contrepartie (−30 % soins reçus, −15 % PV
max) ; ponts passés de 10 à 8 points pour laisser 4 points de marge à l'hybride voisin.

1. Prix du reset : en attente du calcul de l'or gagné par heure selon le niveau.
2. **Bonus de points façon parchemins Dofus** (pas décidé). Si des objets donnent des points d'arbre
   en plus, l'all-in gagne vite le notable 30 d'un voisin par le centre (105 points aujourd'hui, donc
   5 points bonus suffisent). Les ponts restent fermés par le méga. Recommandation : les parchemins
   donnent des **stats** (comme dans Dofus), pas des points d'arbre ; sinon les plafonner à 3.
