# Icônes de l'arbre des passifs V2 : 40 à créer

Les 161 nœuds de `arbre_v2.json` ont un champ `icon`. 121 reprennent une icône qui existe déjà dans le
client (`kanarion_front/assets/icons/passives/tree/` et `common/`) : les 95 petits nœuds prennent l'icône de
leur stat, et 25 notables reprennent l'icône de leur version V1. **Il en manque 40**, listées ici
(source : `icones_v2_a_creer.json`, régénéré par `gen_arbre_v2.py`).

## Consigne pour l'agent graphique

- **Format** : PNG 128 × 128, entièrement opaque, fond noir, même rendu que les 42 icônes de
  `assets/icons/passives/tree/` (peinture dark fantasy détaillée, un sujet central, une lueur de la
  couleur du bras). Comparer avec `execution.png`, `iron_skin.png`, `rhythm.png`, `last_breath.png`.
- **Couleur de lueur par bras** : Attaque rouge `#e66b52`, Défense bleu `#5c99e6`, Soin vert `#5cc78f`,
  Soutien or `#f2b84d`, Affaiblissement violet `#a875e6`. Ponts : les deux couleurs des bras reliés.
- **Lisibilité mobile** : l'icône doit se reconnaître à **30 px** (petit écran, arbre dézoomé). Une
  silhouette forte, pas de détail fin qui disparaît. Vérifier un aperçu à 30 et 45 px avant de livrer.
- **Les 10 mégas** sont les icônes les plus importantes : sujet plus imposant, bord doré discret, et
  la contrepartie suggérée dans le dessin (ex. Forteresse : muraille immense mais épée brisée).
- **Fichier** : `assets/icons/passives/tree/<Fichier>.png` (nom exact dans la colonne Fichier : `v2_` + identifiant du nœud). Aucun commit
  de l'agent : livrer les fichiers, l'intégration se fait ensuite.

## Liste

| Bras | Type | Nom | Fichier | Sujet proposé |
|---|---|---|---|---|
| Attaque | notable 15 | Premier sang | `v2_atk_first_blood` | une goutte de sang qui jaillit d'une lame neuve, cible intacte derrière |
| Attaque | notable 30 | Brute : percée | `v2_atk_breach` | un marteau qui fend un bouclier en deux |
| Attaque | notable 30 | Cadence : élan | `v2_atk_momentum` | une lame entourée de trois anneaux d'énergie qui accélèrent |
| Attaque | notable 50 | Acharnement | `v2_atk_relentless` | cinq entailles successives sur la même cible, de plus en plus vives |
| Attaque | notable 50 | Brise-garde | `v2_atk_guardbreaker` | un éclat critique qui traverse une armure fissurée |
| Attaque | détour | Soif de sang | `v2_atk_bloodlust` | un crâne d'où s'élève une flamme rouge |
| Attaque | méga | Déchaînement | `v2_atk_mega_unleashed` | un guerrier en rage, aura rouge, sans armure ni bouclier |
| Défense | notable 30 | Garde : parade | `v2_def_guard` | une épée qui dévie un coup en étincelles, bouclier levé |
| Défense | notable 30 | Représailles : épines | `v2_def_retaliation` | une armure hérissée d'épines bleues qui renvoient un coup |
| Défense | notable 30 | Endurance : vampirisme | `v2_def_vampire` | un plastron d'où une traînée de vie remonte vers le porteur |
| Défense | notable 50 | Dernier rempart | `v2_def_last_stand` | un chevalier à genoux, bouclier planté, qui tient encore |
| Défense | détour | Mur vivant | `v2_def_living_wall` | un bouclier qui s'illumine au moment d'un blocage |
| Défense | méga | Forteresse | `v2_def_mega_fortress` | une muraille immense, une épée brisée à ses pieds |
| Défense | méga | Colère du titan | `v2_def_mega_titan` | un titan couvert de blessures, les coups reçus rejaillissent en épines |
| Soin | notable 15 | Soins préventifs | `v2_heal_prevention` | une main posée sur un cœur encore intact, halo vert doux |
| Soin | notable 30 | Vol de sort | `v2_heal_spell_vamp` | un sort violet aspiré et changé en lumière verte |
| Soin | notable 30 | Égide sacrée | `v2_heal_holy_shield` | un bouclier de lumière verte en forme de feuille |
| Soin | notable 50 | Ondée | `v2_heal_downpour` | une pluie de lumière qui tombe sur deux silhouettes |
| Soin | détour | Prière de combat | `v2_heal_prayer` | des mains jointes avec cinq perles de lumière autour |
| Soin | méga | Sanctuaire | `v2_heal_mega_sanctuary` | un cercle sacré au sol, colonnes de lumière, une arme posée et inutile |
| Soin | méga | Martyr | `v2_heal_mega_martyr` | une silhouette qui se vide de sa propre lumière pour soigner |
| Soutien | notable 15 | Protection | `v2_sup_protection` | une aile dorée qui couvre un allié |
| Soutien | notable 30 | Clairvoyance | `v2_sup_foresight` | un œil doré entouré d'un sablier |
| Soutien | notable 50 | Chef de file | `v2_sup_vanguard` | un étendard doré planté, épée et bouclier croisés devant |
| Soutien | notable 50 | Accélération | `v2_sup_acceleration` | une main qui lance un sort, entourée de traînées de vitesse |
| Soutien | détour | Élan partagé | `v2_sup_shared_drive` | deux mains qui se passent une flamme dorée |
| Soutien | méga | Maître de guerre | `v2_sup_mega_warmaster` | un cor de guerre doré, des lueurs sur une armée derrière |
| Soutien | méga | Hâte collective | `v2_sup_mega_haste` | des aiguilles d'horloge qui tournent autour de trois silhouettes |
| Affaiblissement | notable 15 | Fléau | `v2_deb_plague_touch` | une main griffue avec deux marques violettes |
| Affaiblissement | notable 30 | Venin profond | `v2_deb_deep_venom` | une fiole de poison violet qui déborde |
| Affaiblissement | notable 50 | Supplice | `v2_deb_torment` | une cible criblée de cinq sceaux violets |
| Affaiblissement | notable 50 | Étau | `v2_deb_vise` | un étau de chaînes qui se resserre sur une silhouette |
| Affaiblissement | détour | Brise-volonté | `v2_deb_will_breaker` | une couronne mentale qui se fissure |
| Affaiblissement | méga | Peste | `v2_deb_mega_plague` | un nuage violet qui passe d'une silhouette à sa voisine |
| Affaiblissement | méga | Seigneur des chaînes | `v2_deb_mega_chains` | un trône de chaînes, des chaînes qui partent dans toutes les directions |
| Pont Attaque ↔ Défense | hybride | Garde de fer | `v2_hyb_atk_def_side` | une épée et un bouclier soudés, moitié rouge moitié bleu |
| Pont Attaque ↔ Affaiblissement | hybride | Curée | `v2_hyb_atk_deb_side` | une lame rouge qui frappe une cible couverte de marques violettes |
| Pont Défense ↔ Soin | hybride | Second élan | `v2_hyb_def_heal_side` | un cœur protégé par un bouclier, bleu et vert |
| Pont Soin ↔ Soutien | hybride | Bénédiction | `v2_hyb_heal_sup_side` | une main qui bénit, lumière verte et dorée |
| Pont Soutien ↔ Affaiblissement | hybride | Marque du chef | `v2_hyb_sup_deb_side` | un étendard doré planté sur une cible marquée en violet |
