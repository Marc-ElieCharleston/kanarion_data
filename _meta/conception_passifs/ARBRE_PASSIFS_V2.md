# Arbre des passifs V2 (intégré le 2026-10-20)

Statut : **branché** (branche `feat/passive-tree-v2` des trois dépôts, commits locaux). `classes/passive_tree.json`
est l'arbre V2 que lisent economy, combat et le client ; il est **généré** par `gen_arbre_v2.py` (ne pas l'éditer à
la main). L'ancienne V1 (5 bras, 56 nœuds `pt_*`) est remboursée par la migration back 124.

- Bras Attaque : `arbre_v2_attaque.json`, écrit par le propriétaire (gabarit, inchangé).
- Les 5 autres bras et les 6 ponts reprennent **son gabarit** (mêmes rangs, coûts et arêtes, emplacement par
  emplacement), donc chaque notable tombe à la même distance.
- Simulation : `python -I _meta/conception_passifs/sim_arbre_v2.py classes/passive_tree.json`.
- Validation : `python scripts/validate_passive_tree.py` (refuse toute mécanique ou variante que le combat ne sait
  pas jouer : catalogue `mechanics` avec `variants` et `stacking`).
- Tables ci-dessous : `python -I _meta/conception_passifs/doc_arbre_v2.py`. Image : `render_arbre_v2.py`.

### Ce que l'intégration du 2026-10-20 a changé (tout est marqué `to_validate` dans la data)

Retour de test de la 0.20 : « il manque la 6e branche, et aucune des branches ne donne de la MAG ou un peu d'ATK au
début ».

1. **6e bras : Arcanes** (MAG, pénétration magique, Souffle, incantation, recharge), entre Soin et Soutien. Anneau :
   Attaque, Défense, Soin, Arcanes, Soutien, Affaiblissement. Les deux ponts d'Attaque du propriétaire ne bougent pas ;
   l'ancien pont Soin ↔ Soutien devient Soin ↔ Arcanes et Arcanes ↔ Soutien (Chant de guerre y est repris).
   Tout le contenu du bras est à valider.
2. **Graines** : Défense (+2 ATK par rang), Soin, Soutien et Affaiblissement (+2 MAG par rang), 3 rangs, reliées au
   centre seul (feuilles : les distances 15 / 30 / 50 / 75 ne bougent pas). Attaque (Force) et Arcanes (Savoir)
   commencent déjà par ATK / MAG.
3. **Uniquement des mécaniques déjà branchées en combat** : 24 nœuds dont la mécanique V2 n'existe pas encore sont
   passés en stats, gardent leur id et leur icône, et portent `v2_planned` (la mécanique prévue, à brancher plus tard).
4. Budget : **99 points** (règle actuelle du serveur, 1 par niveau du 2 au 100) ; la V2 en prévoit 100.
5. Le reset suit la règle actuelle (le reset payant progressif reste une proposition).

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

<!-- CONTENU-DEBUT (genere par doc_arbre_v2.py) -->

## Bras Attaque

| Distance | Contenu |
|---|---|
| 0 → 12 | Force (+2 attaque et +2 magie par rang), Œil vif (+1 % de chance critique par rang), Tranchant (+5 dégâts critiques par rang), Visée (+3 précision par rang) |
| **15** | *Exécution* (+15 % de dégâts contre une cible sous 30 % de ses PV) **ou** *Premier sang* (+6 % de chance critique et +10 dégâts critiques) ⚠ à valider. Détour à 20 : *Allonge* (+1 portée à tes sorts offensifs dont la portée de base est d'au moins 3) |
| 15 → 30 | Poigne (+3 attaque et +3 magie par rang), Œil de lynx (+1 % de chance critique par rang) ; ou Vigueur (+2 % d'attaque et +2 % de magie par rang), Férocité (+1 % de dégâts infligés par rang) |
| **30** | 1 sur 3 : *Lame : instinct du tueur* (Après un coup critique : +10 % de chance critique pendant 3 s), *Brute : percée* (+10 pénétration d'armure et +10 pénétration magique), *Cadence : élan* (+8 % de vitesse d'incantation et +4 % de dégâts infligés) ⚠ à valider |
| 30 → 50 | Létalité (+4 dégâts critiques par rang), Point faible (+1 % de chance critique par rang), Main sûre (+3 précision par rang) ; ou Carnage (+1,2 % de dégâts infligés par rang), Puissance brute (+2 % d'attaque et +2 % de magie par rang), Perforation (+1,5 pénétration d'armure et +1,5 pénétration magique par rang) |
| **50** | *Acharnement* (+10 % de dégâts infligés) ⚠ à valider **ou** *Brise-garde* (+12 pénétration d'armure et +12 pénétration magique) ⚠ à valider. Détour à 55 : *Soif de sang* (+6 % de vol de vie et +6 % de vol de sort) ⚠ à valider |
| 50 → 75 | Maîtrise : carnage (+1,5 % de dégâts infligés par rang), Maîtrise : coup mortel (+1 % de chance critique et +3 dégâts critiques par rang), Maîtrise : puissance (+2 % d'attaque et +2 % de magie par rang) |
| **75 méga** | *Coup Fatal* (Tes coups critiques réduisent de 1 s la recharge du sort lancé. +50 dégâts critiques. Contrepartie : -10 % de dégâts infligés) ⚠ à valider **ou** *Déchaînement* (+35 % de dégâts infligés. Contrepartie : -30 % de soins reçus et -15 % de PV max) |
## Bras Défense

| Distance | Contenu |
|---|---|
| Graine (feuille du centre) | Bras armé (+2 attaque par rang) ⚠ à valider |
| 0 → 12 | Peau dure (+2 armure par rang), Constitution (+12 PV max par rang), Esprit calme (+2 résistance magique par rang), Pas léger (+1 esquive par rang) |
| **15** | *Peau de fer* (-15 % de dégâts reçus des attaques de zone) **ou** *Position tenue* (Si tu ne t'es pas déplacé depuis 3 s : -10 % de dégâts reçus). Détour à 20 : *Sang-froid* (-12 % de dégâts reçus des ennemis à plus de 3 cases) |
| 15 → 30 | Rempart (+3 armure et +3 résistance magique par rang), Robustesse (+15 PV max par rang) ; ou Bastion (+2 % de PV max par rang), Carapace (+2 % d'armure et +2 % de résistance magique par rang) |
| **30** | 1 sur 3 : *Garde : parade* (+8 % de chance de parade et +8 % de chance de blocage), *Représailles : épines* (Renvoie 15 % des dégâts subis à l'attaquant), *Endurance : vampirisme* (+6 % de vol de vie et +6 % de vol de sort) |
| 30 → 50 | Endurance (+1 % de réduction des dégâts subis par rang), Résilience (+2 résistance aux effets par rang), Ancrage (+2 ténacité par rang) ; ou Écailles (+2 % d'armure et +2 % de résistance magique par rang), Colosse (+2 % de PV max par rang), Régénération (+5 % de régénération de PV par rang) |
| **50** | *Inébranlable* (Sous 30 % de PV : bouclier égal à 20 % de tes PV max. Une fois toutes les 45 s) **ou** *Dernier rempart* (+6 % de réduction des dégâts subis) ⚠ à valider. Détour à 55 : *Mur vivant* (+6 % de chance de blocage et +4 % de chance de parade) ⚠ à valider |
| 50 → 75 | Maîtrise : bastion (+2 % de PV max par rang), Maîtrise : cuirasse (+2 % d'armure et +2 % de résistance magique par rang), Maîtrise : endurance (+1 % de réduction des dégâts subis par rang) |
| **75 méga** | *Forteresse* (+30 % de PV max et +15 % de réduction des dégâts subis. Contrepartie : -25 % de dégâts infligés) **ou** *Colère du titan* (Renvoie 30 % des dégâts subis à l'attaquant et +10 % de vol de vie. Contrepartie : +15 % de dégâts subis et -25 % de soins reçus) |
## Bras Soin

| Distance | Contenu |
|---|---|
| Graine (feuille du centre) | Prière ardente (+2 magie par rang) ⚠ à valider |
| 0 → 12 | Mains chaudes (+2 % de puissance de soin par rang), Sève (+10 Souffle max par rang), Grâce (+2 % de soins reçus par rang), Concentration (+2 magie par rang) |
| **15** | *Main secourable* (+20 % de soin sur un allié sous 40 % de ses PV) **ou** *Soins préventifs* (+6 % de puissance de soin et +6 % de puissance de bouclier) ⚠ à valider. Détour à 20 : *Soin étendu* (Tes soins mono-cible soignent aussi l'allié le plus proche de la cible, à 30 %) |
| 15 → 30 | Ferveur (+3 % de puissance de soin par rang), Réserve (+12 Souffle max par rang) ; ou Sagesse (+2 % de magie par rang), Art du bouclier (+2 % de puissance de bouclier par rang) |
| **30** | 1 sur 3 : *Transfusion* (10 % des soins que tu donnes te reviennent), *Vol de sort* (+8 % de vol de sort), *Égide sacrée* (+15 % de puissance de bouclier et +10 % de soins reçus) |
| 30 → 50 | Prière rapide (+2 % de vitesse d'incantation par rang), Persévérance (+1 % de réduction de recharge par rang), Recueillement (+2 % de soins reçus par rang) ; ou Grâce divine (+2 % de magie par rang), Fontaine (+3 % de Souffle max par rang), Rayonnement (+3 % de puissance de bouclier par rang) |
| **50** | *Dernier souffle* (Une fois par combat, un allié qui devrait mourir reste à 1 PV puis reçoit un soin de 25 % de ses PV max) **ou** *Ondée* (Tes soins mono-cible soignent aussi l'allié le plus proche de la cible, à 45 % (ne s'ajoute pas à Soin étendu : le plus fort compte)) ⚠ à valider. Détour à 55 : *Prière de combat* (+4 % de vitesse d'incantation et +6 % de puissance de soin) ⚠ à valider |
| 50 → 75 | Maîtrise : soins (+2 % de puissance de soin par rang), Maîtrise : sagesse (+2 % de magie par rang), Maîtrise : source (+3 % de Souffle max par rang) |
| **75 méga** | *Sanctuaire* (+30 % de puissance de soin et +25 % de durée des améliorations. Contrepartie : -30 % de dégâts infligés) **ou** *Martyr* (+40 % de puissance de soin et +20 % de soins reçus. Contrepartie : -20 % de PV max) |
## Bras Arcanes

| Distance | Contenu |
|---|---|
| 0 → 12 | Savoir (+3 magie par rang), Flux (+10 Souffle max par rang), Perce-arcane (+1,5 pénétration magique par rang), Focalisation (+1 % de chance critique par rang) |
| **15** | *Puissance arcanique* (+8 % de magie) **ou** *Incantation vive* (+8 % de vitesse d'incantation). Détour à 20 : *Esprit perçant* (+6 pénétration magique) |
| 15 → 30 | Érudition (+3 magie par rang), Source (+12 Souffle max par rang) ; ou Intellect (+2 % de magie par rang), Ferveur arcanique (+1 % de dégâts infligés par rang) |
| **30** | 1 sur 3 : *Siphon* (+8 % de vol de sort), *Torrent* (+8 pénétration magique et +6 % de dégâts infligés), *Maîtrise du temps* (+8 % de réduction de recharge) |
| 30 → 50 | Éclat (+4 dégâts critiques par rang), Lucidité (+1 % de chance critique par rang), Vélocité (+2 % de vitesse d'incantation par rang) ; ou Amplification (+2 % de magie par rang), Débordement (+3 % de Souffle max par rang), Perforation arcanique (+1,5 pénétration magique par rang) |
| **50** | *Archimage* (+12 % de magie et +10 dégâts critiques) **ou** *Surcharge* (+10 % de dégâts infligés). Détour à 55 : *Méditation* (+2 Souffle par seconde) |
| 50 → 75 | Maîtrise : arcanes (+2 % de magie par rang), Maîtrise : flux (+1 % de réduction de recharge par rang), Maîtrise : surcharge (+1,5 % de dégâts infligés par rang) |
| **75 méga** | *Archonte* (+30 % de magie et +15 pénétration magique. Contrepartie : -20 % de PV max) **ou** *Tempête arcanique* (+25 % de dégâts infligés et +15 % de vitesse d'incantation. Contrepartie : -30 % de Souffle max) |
## Bras Soutien

| Distance | Contenu |
|---|---|
| Graine (feuille du centre) | Verve (+2 magie par rang) ⚠ à valider |
| 0 → 12 | Persistance (+2 % de durée des améliorations par rang), Vivacité (+2 % de vitesse d'incantation par rang), Souffle long (+10 Souffle max par rang), Volonté (+2 résistance aux effets par rang) |
| **15** | *Inspiration* (Tes améliorations sur un allié lui donnent aussi +8 % de dégâts pendant leur durée) **ou** *Protection* (+12 % de puissance de bouclier et +4 % de durée des améliorations) ⚠ à valider. Détour à 20 : *Aura étendue* (Tes améliorations mono-cible touchent aussi un allié adjacent) |
| 15 → 30 | Esprit vif (+1 % de réduction de recharge par rang), Ténacité (+2 ténacité par rang) ; ou Clarté (+3 % de Souffle max par rang), Harmonie (+2 % de magie par rang) |
| **30** | 1 sur 3 : *Rythme* (Un sort sur 4 ne coûte pas de Souffle), *Chef d'orchestre* (Quand tu améliores un allié, ses recharges diminuent de 1 s. Une fois toutes les 5 s par allié), *Clairvoyance* (+15 % de durée des améliorations et +10 % de durée des affaiblissements) |
| 30 → 50 | Sérénité (+2 % de durée des améliorations par rang), Discipline (+1 % de réduction de recharge par rang), Fermeté (+2 résistance aux effets par rang) ; ou Éloquence (+2 % de vitesse d'incantation par rang), Ampleur (+3 % de Souffle max par rang), Présence (+2 % de PV max par rang) |
| **50** | *Chef de file* (Tes améliorations sur un allié lui donnent aussi +6 % de dégâts pendant leur durée (s'ajoute à Inspiration). +10 % de puissance de bouclier) ⚠ à valider **ou** *Accélération* (+10 % de vitesse d'incantation et +5 % de réduction de recharge) ⚠ à valider. Détour à 55 : *Élan partagé* (+5 % de dégâts infligés et +5 % de durée des améliorations) ⚠ à valider |
| 50 → 75 | Maîtrise : durée (+3 % de durée des améliorations par rang), Maîtrise : tempo (+1 % de réduction de recharge par rang), Maîtrise : clarté (+3 % de Souffle max par rang) |
| **75 méga** | *Maître de guerre* (Tes améliorations sur un allié lui donnent aussi +10 % de dégâts pendant leur durée. +50 % de durée des améliorations. Contrepartie : -25 % de dégâts infligés) **ou** *Hâte suprême* (+15 % de réduction de recharge et +15 % de vitesse d'incantation. Contrepartie : -20 % de PV max) ⚠ à valider |
## Bras Affaiblissement

| Distance | Contenu |
|---|---|
| Graine (feuille du centre) | Sombre savoir (+2 magie par rang) ⚠ à valider |
| 0 → 12 | Coup d'œil (+3 précision par rang), Venin (+2 % de chance d'effet par rang), Prolongation (+2 % de durée des affaiblissements par rang), Perce-esprit (+1,5 pénétration magique par rang) |
| **15** | *Emprise* (+10 % de dégâts contre une cible sous contrôle (étourdie, ralentie, réduite au silence...)) **ou** *Fléau* (+6 % de chance d'effet et +6 % de durée des affaiblissements) ⚠ à valider. Détour à 20 : *Contagion* (Quand une cible affaiblie meurt, ses affaiblissements passent à l'ennemi le plus proche) |
| 15 → 30 | Ténèbres (+2 % de chance d'effet par rang), Hâte (+1 % de réduction de recharge par rang) ; ou Malice (+2 % d'attaque et +2 % de magie par rang), Corruption (+2 % de durée des affaiblissements par rang) |
| **30** | 1 sur 3 : *Zone de contrôle* (Tes sorts de contrôle mono-cible touchent aussi une case adjacente), *Maître du tempo* (Quand tu contrôles une cible : -1 s de recharge sur tes autres sorts. Une fois toutes les 3 s), *Venin profond* (+15 % de chance d'effet et +10 % de durée des affaiblissements) |
| 30 → 50 | Fatalité (+2 % de chance d'effet par rang), Persistance noire (+2 % de durée des affaiblissements par rang), Brise-armure (+1,5 pénétration d'armure et +1,5 pénétration magique par rang) ; ou Malédiction (+2 % d'attaque et +2 % de magie par rang), Affliction (+1 % de dégâts infligés par rang), Maléfice (+3 % de durée des affaiblissements par rang) |
| **50** | *Supplice* (+8 % de dégâts infligés et +8 % de chance d'effet) ⚠ à valider **ou** *Étau* (+15 % de dégâts et +10 % de chance critique contre une cible sous contrôle (s'ajoute à Emprise)). Détour à 55 : *Brise-volonté* (+10 % de chance d'effet) ⚠ à valider |
| 50 → 75 | Maîtrise : emprise (+2 % de chance d'effet par rang), Maîtrise : persistance (+3 % de durée des affaiblissements par rang), Maîtrise : malice (+2 % d'attaque et +2 % de magie par rang) |
| **75 méga** | *Peste* (+20 % de dégâts infligés et +15 % de chance d'effet. Contrepartie : -15 % de PV max) ⚠ à valider **ou** *Seigneur des chaînes* (+40 % de durée des affaiblissements et +20 % de chance d'effet. Contrepartie : -25 % de dégâts infligés) |
## Ponts (les 6)

| Pont | Passage (×2, 1 pt) | Hybride sur le chemin | Hybride à côté |
|---|---|---|---|
| Attaque ↔ Défense | +4 armure et +4 résistance magique | *Riposte* (Après un blocage ou une parade, ta prochaine attaque inflige +40 % de dégâts) | *Garde de fer* (+6 % de dégâts infligés et +4 % de réduction des dégâts subis) ⚠ à valider |
| Attaque ↔ Affaiblissement | +4 armure et +4 résistance magique | *Opportuniste* (+20 % de chance critique contre une cible sous contrôle) | *Curée* (+6 % de dégâts infligés et +6 % de chance d'effet) ⚠ à valider |
| Défense ↔ Soin | +12 PV max et +2 % de soins reçus | *Rempart vivant* (10 % des soins que tu reçois deviennent du bouclier) | *Second élan* (+12 % de soins reçus et +3 % de réduction des dégâts subis) ⚠ à valider |
| Soin ↔ Arcanes | +2 magie et +2 % de puissance de soin | *Lumière arcanique* (+8 % de magie et +8 % de puissance de soin) ⚠ à valider | *Siphon vital* (+6 % de vol de sort et +6 % de soins reçus) ⚠ à valider |
| Arcanes ↔ Soutien | +10 Souffle max et +2 % de vitesse d'incantation | *Chant de guerre* (Tes améliorations sur un allié retirent un de ses affaiblissements) | *Résonance* (+8 % de durée des améliorations et +4 % de réduction de recharge) ⚠ à valider |
| Soutien ↔ Affaiblissement | +2 % de chance d'effet et +2 résistance aux effets | *Coordination* (Un allié que tu as amélioré inflige +8 % de dégâts aux cibles que tu as affaiblies) | *Marque du chef* (+6 % de chance critique et +6 % de chance d'effet) ⚠ à valider |

## Noeuds à valider

- `pt2_atk_first_blood` *Premier sang* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider). Prévu par la V2 : damage_vs_target_hp_above : +20 % de degats contre une cible au-dessus de 90 % de ses PV.
- `pt2_atk_momentum` *Cadence : élan* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider). Prévu par la V2 : stacking_stat_on_event : chaque sort lance donne +2 % de degats pendant 6 s, cumulable 5 fois.
- `pt2_atk_relentless` *Acharnement* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider). Prévu par la V2 : consecutive_hit_stacks : +4 % par coup sur la meme cible, 5 cumuls.
- `pt2_atk_guardbreaker` *Brise-garde* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider). Prévu par la V2 : crit_ignores_defense : les crits ignorent 30 % de l'armure et de la resistance magique.
- `pt2_atk_bloodlust` *Soif de sang* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider). Prévu par la V2 : stat_window_after_event kill : +15 % de degats pendant 5 s apres un ennemi tue.
- `pt2_atk_mega_fatal` *Coup Fatal* : contrepartie : -10 % de degats infliges au lieu de -15 % sur les coups non critiques (non_crit_damage_modifier pas branche). Prévu par la V2 : non_crit_damage_modifier : -15 % de degats sur les coups non critiques.
- `pt2_def_last_stand` *Dernier rempart* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider). Prévu par la V2 : damage_taken_reduction_conditional hp_below : sous 30 % de PV, -20 % de degats subis.
- `pt2_def_living_wall` *Mur vivant* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider). Prévu par la V2 : stat_window_after_event block_or_parry : -20 % de degats subis pendant 3 s.
- `pt2_def_seed_might` *Bras armé* : graine de debut ajoutee le 2026-10-20 (retour de test 0.20 : pas de MAG ni d'ATK au debut) : stat et valeur a valider.
- `pt2_heal_prevention` *Soins préventifs* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider). Prévu par la V2 : heal_bonus_target_hp_above : +15 % de soins sur une cible au-dessus de 70 % de ses PV.
- `pt2_heal_downpour` *Ondée* : un seul allie (la V2 en prevoyait 2 a 25 % : parametre count pas branche). Prévu par la V2 : heal_splash_nearest_ally count=2 ratio 25.
- `pt2_heal_prayer` *Prière de combat* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider). Prévu par la V2 : stacking_stat_on_event heal_cast : +3 % de puissance de soin par soin, 5 cumuls, 6 s.
- `pt2_heal_seed_prayer` *Prière ardente* : graine de debut ajoutee le 2026-10-20 (retour de test 0.20 : pas de MAG ni d'ATK au debut) : stat et valeur a valider.
- `pt2_sup_protection` *Protection* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider). Prévu par la V2 : buff_grants_stat damage_reduction : un allie que tu buffes subit -8 % de degats.
- `pt2_sup_vanguard` *Chef de file* : partie defensive (-6 % de degats subis pour l'allie) remplacee par +10 % de puissance de bouclier. Prévu par la V2 : buff_grants_stat damage_reduction 6.
- `pt2_sup_acceleration` *Accélération* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider). Prévu par la V2 : buff_grants_stat cast_speed : un allie que tu buffes a +15 % de vitesse d'incantation.
- `pt2_sup_shared_drive` *Élan partagé* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider). Prévu par la V2 : stacking_stat_on_event buff_applied_to_ally : +3 % de degats par buff donne, 5 cumuls, 6 s.
- `pt2_sup_mega_haste` *Hâte suprême* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider) ; l'effet porte sur toi, plus sur les allies (d'ou le nouveau nom). Prévu par la V2 : Hate collective, buff_grants_stat cooldown_reduction : un allie que tu buffes a -20 % de recharge.
- `pt2_sup_seed_verve` *Verve* : graine de debut ajoutee le 2026-10-20 (retour de test 0.20 : pas de MAG ni d'ATK au debut) : stat et valeur a valider.
- `pt2_deb_plague_touch` *Fléau* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider). Prévu par la V2 : damage_vs_target_debuff_count : +12 % de degats contre une cible a 2 affaiblissements ou plus.
- `pt2_deb_torment` *Supplice* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider). Prévu par la V2 : damage_vs_target_debuff_count per_debuff : +4 % par affaiblissement de la cible, jusqu'a 5.
- `pt2_deb_will_breaker` *Brise-volonté* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider). Prévu par la V2 : stat_window_after_event control_applied : +15 % de chance d'effet pendant 4 s.
- `pt2_deb_mega_plague` *Peste* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider). Prévu par la V2 : control_splash_adjacent harmful : un affaiblissement d'un sort cible touche aussi un ennemi adjacent ; contrepartie -25 % de duree des affaiblissements.
- `pt2_deb_seed_dark_lore` *Sombre savoir* : graine de debut ajoutee le 2026-10-20 (retour de test 0.20 : pas de MAG ni d'ATK au debut) : stat et valeur a valider.
- `pt2_hyb_atk_def_side` *Garde de fer* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider). Prévu par la V2 : stats_while_hp_above : au-dessus de 70 % de PV, +12 % de degats et -8 % de degats recus.
- `pt2_hyb_atk_deb_side` *Curée* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider). Prévu par la V2 : damage_vs_target_debuff_count : +20 % de degats contre une cible a 3 affaiblissements ou plus.
- `pt2_hyb_def_heal_side` *Second élan* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider) (un 2e bouclier sous les PV bas ecraserait Inebranlable : le composant n'en tient qu'un). Prévu par la V2 : shield_on_low_hp : sous 25 % de PV, bouclier de 15 % des PV max, une fois toutes les 60 s.
- `pt2_hyb_heal_arc` *Lumière arcanique* : pont du 6e bras, ajoute le 2026-10-20.
- `pt2_hyb_heal_arc_side` *Siphon vital* : pont du 6e bras, ajoute le 2026-10-20.
- `pt2_hyb_arc_sup_side` *Résonance* : pont du 6e bras, ajoute le 2026-10-20 (Chant de guerre vient de l'ancien pont Soin <-> Soutien).
- `pt2_hyb_sup_deb_side` *Marque du chef* : mecanique V2 pas encore branchee en combat : remplacee par des stats (valeurs a valider). Prévu par la V2 : ally_buffed_bonus_vs_debuffed crit : +10 % de chance critique pour un allie buffe contre tes cibles affaiblies.

<!-- CONTENU-FIN -->

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

**2026-10-20, 6 bras, 99 points** (`sim_arbre_v2.py classes/passive_tree.json`) : les 66 notables tombent tous à
15 / 30 / 50 / 75 ; pour chaque bras, all-in 75, + notable 15 du voisin 90, + notable 30 du voisin 105 (impossible) ;
hybride voisin 83 ou 89 avec les deux hybrides ; hybride éloigné (2 crans) 96 par les ponts ; 3 bras voisins 96.

## Budget de puissance (à vérifier en jeu)

- All-in : 4 notables dont le méga, + 25 points (un petit notable ailleurs, ou un détour).
- Hybride voisin : 8 notables (dont 2 hybrides), pas de méga.
- Cible : **méga ≈ 4 notables moyens**. Si les hybrides dominent, on monte les mégas ; sinon on monte
  les hybrides. Les contreparties des mégas gardent un vrai choix de style.

## Interface : ordinateur ET mobile (2026-10-17)

Constat sur l'écran actuel (arbre V1, `passive_tree_view.gd`) : il est pensé souris. Sur mobile, un
appui achète directement (+1), le retrait (clic droit) n'existe pas, le détail d'un nœud ne s'ouvre
jamais (le survol est coupé au tactile) et le zoom ne se fait qu'aux boutons (pas de pincement). À
corriger dès la V1, la V2 en hérite.

Règles proposées, identiques sur les deux supports :

- **Appui = sélection, jamais achat.** Le nœud choisi ouvre une fiche (panneau bas sur mobile,
  bulle sur ordinateur) : icône, effet, rang, coût, raison du refus éventuel, et deux gros boutons
  **+** / **−** (au moins 64 px). Sur ordinateur, clic gauche / clic droit restent des raccourcis.
- **Le chemin s'affiche** dès qu'un nœud est sélectionné (ou survolé à la souris) : la route la moins
  chère depuis ce que le joueur possède, surlignée, avec son coût total (« +13 pts par Riposte »). Pur
  affichage, le serveur reste seul juge.
- **Pincer pour zoomer, glisser pour déplacer**, double appui pour zoomer sur un point ; boutons de
  zoom gardés.
- **Niveaux de détail** : dézoomé, seuls les notables, les mégas et les noms des bras (lisible sur
  téléphone) ; zoomé, les petits nœuds et leurs rangs. Toute cible tactile fait au moins 44 px à
  l'écran au zoom où elle est cliquable.
- **Ponts lisibles** : un arc sur l'anneau 30, aux couleurs des deux bras, avec le coût écrit dessus.
  Anneaux 15 / 30 / 50 / 75 visibles en fond.
- **Barre fixe en bas** : points restants, Annuler, Appliquer ; le panneau Impact se replie.
- **Icônes** : chaque nœud a son champ `icon` ; les 40 manquantes sont commandées dans `ICONES_V2.md`
  avec une contrainte de lisibilité à 30 px.

## Reset des points (proposition)

- Gratuit jusqu'au niveau 20.
- Ensuite, le prix se pense **en temps de jeu**, pas en or : environ 1 heure de farm à son niveau pour
  le premier reset, puis +50 % par reset payant récent (le compteur baisse de 1 toutes les 2 semaines
  sans reset payant). Le prix en or = ces heures × l'or gagné par heure au niveau du joueur, une fois
  qu'on aura le calcul de l'or par heure (pas encore fait : 10 or durs à gagner ou 10 000, ça change
  tout).
- Pass : 1 reset gratuit par semaine, non cumulable.

## Ce qui est branché (2026-10-20) et ce qui reste

- Serveur (`shared/gameplay/passive_tree.hpp`, economy, aperçu Impact) et client (`passive_tree_rules.gd`) :
  coûts par sorte, passage d'un petit nœud au rang max seulement, groupes de choix à N options, 1 méga, ponts
  fermés par le méga, plus de slots par niveau. Stats des notables et des mégas (malus compris) appliquées par le
  même chemin que les petits nœuds.
- Reste (non fait, à décider) : 100e point (`starting_passive_points`), reset payant progressif, et les mécaniques
  listées dans les `v2_planned` (Premier sang, Élan, Acharnement, Brise-garde, Soif de sang, non-crits de Coup Fatal,
  Garde de fer, Curée, Dernier rempart, Mur vivant, Soins préventifs, Ondée à 2 cibles, Prière de combat,
  Protection, Chef de file défensif, Accélération, Élan partagé, Hâte collective, Fléau, Supplice, Brise-volonté,
  Peste, Second élan, Marque du chef).

## Questions ouvertes

Réglé le 2026-10-15 : Déchaînement garde +35 % **avec** sa contrepartie (−30 % soins reçus, −15 % PV
max) ; ponts passés de 10 à 8 points pour laisser 4 points de marge à l'hybride voisin.

1. Prix du reset : en attente du calcul de l'or gagné par heure selon le niveau.
2. **Bonus de points façon parchemins Dofus** (pas décidé). Si des objets donnent des points d'arbre
   en plus, l'all-in gagne vite le notable 30 d'un voisin par le centre (105 points aujourd'hui, donc
   5 points bonus suffisent). Les ponts restent fermés par le méga. Recommandation : les parchemins
   donnent des **stats** (comme dans Dofus), pas des points d'arbre ; sinon les plafonner à 3.
