# Audit assets décor — Kanarion Online (sols, chemins, props) — 2026-10-13

Audit en lecture seule. Rien n'a été modifié dans les dépôts ni dans PixelLab.
Toutes les planches citées sont dans ce dossier (`assets_audit/`).

---

## 0. Ce qu'il faut savoir avant tout (projection et échelle)

**Le jeu est en isométrique 2:1, pas en vue de dessus.** C'est ce que montrent `tools/build_havreden_tileset.gd` et `havreden_terrain_v2.tres` :

- `tile_shape = ISOMETRIC`, `layout = DIAMOND_DOWN`, **`tile_size = 64 × 30`**. La maille du sol est un losange de 64 px de large et 30 px de haut.
- **Les « tuiles de 30×30 » dont parle Charleston, c'est ce 64×30.** Le 30 correspond à la hauteur du losange. Il n'existe aucune tuile carrée de 30×30 dans le TileSet de la carte.
- Chaque tuile fait 64×42 px : la face du dessus (64×30) plus un flanc de 12 px. Les herbes hautes vont jusqu'à 64×47 (`grass_lush`, `forest_grass`) ou 64×45 (`swamp_grass`).
- Atlas `fill/*.png` : 259×259, grille de 4×4, donc 16 variantes. Le script mesure la grille à partir de l'image : marge (0,11), séparation (1,23).
- Le `_art_reference/README.md` impose l'isométrie 2:1, la lumière en haut à gauche et un contour brun coloré (jamais noir). Les objets allongés doivent suivre une empreinte 2:1, orientée SE ou SW.

**Les tuiles PixelLab « isometric 64px » sont déjà le bon format.** Le losange y occupe 64×30, plus le flanc, à y=11..53 dans le canevas de 64×64. Les 31 sols du client en viennent tous, sauf `mud_trampled`. Pour les utiliser, il suffit de recadrer la boîte englobante (64×42, ou 64×47 avec des brins d'herbe) et de les ranger en atlas 4×4. **Aucune mise à l'échelle n'est nécessaire.** Ensuite, on ajoute le nom à la FIN de `MATERIALS` dans le build (l'ordre est contractuel).

Conversions selon le type d'asset PixelLab :

| Type PixelLab | Utilisable ? | Conversion |
|---|---|---|
| tiles_pro isometric 64 px, 16 var. (≈ 30 tuiles de sol) | **Oui, tel quel** | Recadrer à 64×42 ou 64×47, ranger en atlas 4×4, pas de redimensionnement |
| tiles_pro isometric 128 px (1dc07169, 35d5c95b, 1cbbad22, 38aa3625, 1d460e50) | Non | Densité ×2 : il faudrait réduire de 50 %, ce qui détruit le pixel art. Mieux vaut les régénérer en 64 |
| tiles_pro square_topdown (32/48/128) | Non | Ce sont des icônes d'objets et des portraits, pas du sol |
| Tileset top-down Wang 033bc546 « stone ground » (32×32, carré) | **Non** | Mauvaise projection : une reprojection carré → losange déforme tout. À régénérer en isométrique |
| Objets 1 direction (props_library, ≈ 70 objets de décor) | Oui, au cas par cas | Pas de mise à l'échelle (les pixels sont 1:1 avec les sprites). Mais beaucoup ont **un socle d'herbe incrusté** (rock_formation_huge, fountain, lavoir, wooden_bridge, hay_bales…) : on ne peut les poser que sur de l'herbe, ou il faut détourer le socle. `asher_tower` et `chapel` ont **un fond opaque** à détourer |

**Densité de pixels.** Partout 1:1, ce qui est cohérent avec les sprites. Zone visible mesurée : guerrier 26×51, sanglier 59×40, loup 61×48, golem 27×57, sur des canevas de 104 à 124. Un sanglier fait donc environ une tuile de large. Les sols ont la même taille de pixel que les monstres. Le seul écart vient des objets PixelLab historiques (props_library), au rendu plus « lisse » et au contour plus sombre. Le README les classe déjà comme contre-références pour Havreden.

**Zones déjà tracées sur `havreden_map.tscn`** (polygones `mz_*`) : rats_1_8, scarabees_3_8, sangliers-loups_6_15, sanglier_8_15, hyene_9_20, prairie_10_20, foret_12_26, loup_13_23, taureaux_16-25_elite, ours_20_28, marecage_20_30, spider_25_30, wolf_25-32, brigand_35-45, rats_corrompu_40-50, fanatique_45_60_elite, gobelins_50_60, marais_corrompu_60_70, low_demon_61_70, low_abyssal_70_80, demon_80_100, abyssal_85_100. Il y a aussi les aires havreden_area et rochebourg_area.

---

## 1. Inventaire

### 1.1 Sols du client — `assets/tilesets/havreden/terrain_v2/`

**`fill/`** : 31 fichiers, dont 30 atlas valides de 16 variantes. Montés dans `havreden_terrain_v2.tres`.

| Matériau | Ce qu'il représente | Bloquant |
|---|---|---|
| grass | herbe vert pastel très plate (1er lot) | |
| grass_lush | herbe dense mi-saturée, touffes, quelques mottes (matériau dominant de la carte, ~128 000 cases) | |
| grass_flowers | herbe vive avec fleurs blanches, rouges, jaunes et bleues | |
| forest_grass | sous-bois vert très saturé, trèfles, cailloux, brindilles | |
| dry_grass | herbe sèche paille pâle | |
| swamp_grass | herbe de marais olive, petites flaques | |
| dirt | terre gris-beige (1er lot) | |
| dirt_pebbles | terre orangée avec cailloux gris | |
| mud | boue brun foncé à plaques claires | |
| mud_trampled | **pas un atlas** : texture carrée RVB peinte (non pixel art), absente du build | |
| swamp_mud | boue de marais olive foncé | |
| farm_soil_dark | terre de culture foncée avec grosses pousses vertes (malgré son nom) | |
| farm_soil_sprouts | terre labourée, petites pousses | |
| sand | sable pêche pâle (1er lot) | |
| sand_golden | sable doré, rides, touffes sèches | |
| sand_earth | terre sableuse, variantes craquelées foncées | |
| sand_earth_pebbles | terre sableuse et galets | |
| arena_sand | sable d'arène, os, traces de pas | |
| gravel_coarse / gravel_fine | gravier gros / fin | |
| rock | roche grise fissurée (1er lot) | |
| cobble | pavés beiges réguliers | |
| city_road | pavés de ville bleu-gris, grilles, bouches d'égout | |
| stone_slab | dalles grises à joints moussus | |
| stone_ruin | dalles de ruine fissurées et noircies | |
| arena_stone | dalles d'arène éclatées, fissures sombres | |
| wood_plank | plancher en diagonale | |
| water | eau turquoise à vaguelettes | oui |
| water_shallow | eau peu profonde bleu clair | oui |
| swamp_water | eau de marais verte, nénuphars, bois flotté | oui |
| magma | lave jaune-orange, croûtes | oui |

**`transitions/`** : 8 atlas de 16 pièces Wang en quarts de coin. Pour cobble, dirt, dry_grass, grass, mud, rock, sand et water. Chaque atlas associe **deux teintes d'une même famille** (cobble : sable/pavé gris ; grass : terre/herbe ; sand : pâle/orange ; water : profonde/claire). Ce sont les seules pièces qui portent des bits de terrain.

**`paths/`** : 21 atlas de routes. Toutes sont du pavé gris clair, posé sur grass, grass_lush ou sand. Il y en a de trois formes : `wNN` (route droite de largeur 40, 55 ou 75 %), `cut` (coupe diagonale) et `disc_rNN` (placettes circulaires en grilles de 7×7, 11×11 et 13×13). Ce sont des masques géométriques appliqués à deux matériaux.

**Autres dossiers de `tilesets/`** :
- `havreden/terrain/` : ancien jeu en 64×32 (cobblestone_gray ×5, grass_001, sand_001), avec les transitions `grass_to_cobblestone_gray_large` (16) et `grass_to_sand` (16). Non utilisé par terrain_v2.
- `combat_v3/` : copies 259×259 de arena_stone, city_road, lush_grass, magma et stone_ruin, plus `transitions/grass_to_city_road`. Sert au labo de grille de combat.
- `havreden/_art_reference/` : README canonique, `reference_assets.json`, candidats, revues d'arbres, et **`prairie_ground_study/`**. Cette étude avant/après n'est pas encore intégrée : herbe désaturée, chemins de terre organiques, empreintes. C'est la bonne direction pour corriger les problèmes du §2.
- `world/props_library/` : 74 PNG historiques PixelLab (voir 1.3).

**Cartes peintes** — `assets/maps/` (et non `assets/world/`) : `asher_tower_floor1/5/15.png` en 1024², `floor12.jpg` en 2048², `desert_map.png` en 2560² (gris). Les donjons du repaire des rats utilisent des sols peints (`scenes/world/donjons/rat_den/rat_den_floor_0X.png`).

### 1.2 Sols PixelLab (85 tiles_pro)

- **Déjà dans le client** (même contenu que les fill) : forest grass 423cad48, grass flowers 940bbfd8/7add4dda, swamp water d5492e60, swamp grass 9ecfe7c2, swamp mud 4827ca95, shallow water 0cec0021, arena sand 14f9f287, stone slab c48a98c5, wood plank b163b556, gravel coarse dc9ded19, gravel fine cc019013, farm soil f9058b85/c3911b6d, dirt pebbles 989462a1, sand earth (pebbles) 2822d7be/5ba580ef, sand golden 1d91565a, city road ca77c244, arena stone e7c512af, stone ruin 776c05f3, magma 123aa232, lush grass e68a3364, ainsi que les doublons du 1er lot (grass 8b291f8d/efd0221b, dirt 0384f7d9/fffee686, sand 3fae26f7/824d9b24, rock dbec5cc1/d4da80d8, mud 423db9f0/2b8c9ade, dry grass d9ec906d/628137e0, cobble 1eccf940/0d718bba, water 5986f103/fc0f1a50).
- **Pas encore dans le client** (testés, voir `sheet_pixellab_0*.png`) :

| id | Ce que c'est | Verdict |
|---|---|---|
| 424a82bc Dark wolf den terrain | roche sombre, gueules de grotte avec yeux, os, boue, herbe morte | **Patchwork** : chaque variante est une scène différente (grottes dans la tuile). La variante 0, roche sombre, est utilisable seule. Les autres sont à garder comme « décals » isolés |
| e412cd20 Dark swamp terrain | eau sombre, racines, rochers moussus | Patchwork racines/eau/boue, mais l'ambiance colle au **Marais de la Faille**. À filtrer : garder 6 à 8 variantes homogènes |
| 14537975 dark swamp water, floating… | eau verte sombre, algues | Contrastes forts entre variantes (damier). Ne garder que les variantes claires |
| aa081a08 rich muddy brown dirt | terre brune, craquelures, tas de sable | Damier de variantes. Médiocre |
| 1fc547a5 packed dirt path | terre tassée striée en diagonale | **OK**, bonne base de chemin de terre (Route, Mines) |
| 1f4e3b31 packed dirt ground (#50423A) | terre brune fine, mottes | **OK**, meilleur remplaçant de `dirt` (brun chaud homogène) |
| bb354876 flat packed dirt, warm | terre orangée lisse, galets réguliers | Acceptable, un peu plat |
| 4d8a3aa6 sol terreux dans un village | terre beige pâle, fissures fines | Acceptable (place de village, Rochebourg) |
| e83ce12b farmer ground | sillons orange, flaques, foin | Patchwork très orangé. Médiocre |
| a5784990 beautiful water | eau en damier de bleus | **Mauvais** (damier) |
| tuiles 128 px (×5) | herbe, eau, pavés | Inutilisables tels quels (voir §0) |

- Tileset top-down 033bc546 « stone ground » en 32×32 carré : mauvaise projection.
- Aucune « isometric tile » (liste vide).

### 1.3 Props

**Client — `assets/tilesets/havreden/props/`** (style canonique : iso 2:1, contour brun, lumière haut-gauche) :

| Dossier | Contenu |
|---|---|
| buildings/ (auction_house_silas, ezra_field_workshop, fisher_house_havel, inn_rona_bran, magic_shop_petra_lyr, owen_rosine_farm, pasture ×3, prototypes ×23) | bâtiments de Havreden en SE/SW ; chaumière de berger, appentis, abri effondré |
| crafts/sana_gorik | atelier d'artisanat |
| facade_decor/ (planters ×3, signs ×5) | pots, jardinières, enseignes suspendues |
| fences/ (low ×2, arena_style ×8, prairie_2to1 ×16 avec connections.json) | barrières basses, arène, clôture de prairie intacte/cassée/portail ×4 directions |
| fissures/ (static ×5 + near_village ×12, animated ×12 en feuilles de 8 frames) | fissures violettes graduées 01 micro → 05 massive |
| infrastructure/ | grille d'égout, puits |
| market/ (+gabin, material_exchange) | étals vert et rouge, charrette de nourriture, comptoir d'échange |
| marsh/decor (20) | camp de pêcheur abandonné, plateforme, barques ×2, nasse, séchoir, fumoir, hutte sur pilotis, quai, passerelles SE/SW/coin, lanterne de marais, panneau d'avertissement, filets, rochers |
| marsh/trees (10) | cyprès chauves ×2, arbre mort, racines, tronc couché, souche creuse, saules ×2, aulnes tordus ×2 |
| marsh/vegetation (7) | massettes, nénuphars, champignons, bulles de boue, roseaux, herbe, fougère |
| pature/decor (28) + fences (4) | nichoir, cloche, chariot, poulailler, abreuvoir, moulin, ruche, meules, bidons de lait, pompe, enclos, empreintes de sabots, barrières défoncées |
| plaza/ (+prototypes ×7) | fontaine cristal, banc, tableau des contrats, panneau, lampadaire, charrette marchande |
| rework_2026_09 (6) | versions pixel v2 du banc, de la jardinière, de la guilde, de la maison, de la taverne, de l'arbuste |
| teleport | pierre de téléport (ellipse au sol) |
| training (4 + sources) | arènes PvP et d'entraînement |
| vegetation/approved_no_outline (4) | chênes (nu, pommes, oranges), pin clair (validés) |
| vegetation/aseprite_trees (3), forest (13), prototypes (8), village (3) | arbres : ancien, grand, ouvert, rond, élancé, battu par le vent, mort ; jeunes pousses, fougères, buissons, souche, haie taillée (petite), fleurs |
| village_life/ (carts, clotheslines, hay, seating) | charrettes, cordes à linge, meules, bancs, chaises, chaises de pêche |
| walls/ (+generated) | murs de ville beige propres : faces, coins, portes SE/SW |

**Client — `assets/tilesets/world/props_library/`** (= les objets d'environnement PixelLab ; même liste que ceux du compte) :

- **01_buildings** : defensive_wall, watchtower (56294f22), asher_tower (aac92015, *fond opaque*), chapel (a1a148df, *fond opaque*), guild_hall, peasant_house, rochebourg_house, rochebourg_inn, stone_house, swamp_stilt_house (5ba5aa1b), tavern_inn, blacksmith_forge, herbalist_shop.
- **02_nature** :
  - rochers : rock_cluster (be7ae512), rock_formation_huge (18aee328), rock_large_boulder (2fdf820f), rock_medium (a0df225f), rock_moss (c14b36da), rock_pebbles (7cc79d33), rock_small (00152bcf) ;
  - arbres : oak_tree_v1 (a9b86a35), oak_tree_v2_iso (5c3983f0), pine_tree (ece02a5c), willow_tree (8c5988aa) ;
  - végétation : bush_flowers (93b1712d), mushrooms, tall_grass, wildflowers.
- **03_village** : fence, hay_bales, scarecrow, wheat_field, market_stall, merchant_cart, barrel, bench, brazier, crates_sacks, fountain, lamp_post (707598df), lavoir, well.
- **04_routes** : rickety_bridge (2fe69b7e), wooden_bridge (b25b3727), 11 panneaux, abandoned_wagon, boat.
- **05_adventure** : bandit_camp (7f1cb78d), barricade (7c01b7bf), cage, campfire (b2cc97ca), cave_entrance (0503ff3b), ritual_altar, ruin (f716146c), treasure_chest.
- **06_corruption** :
  - fissure_lv1..lv5 (7d1b94c2, 59bbd942, bfecf844…) ;
  - crystal_corrupted (2729b254), crystal_tree_vitrified (88aa5e41), dead_tree_corrupted (2206f10e) ;
  - zealot_banner (d4bb3338).

**PixelLab (≈ 996 objets)** : en dehors de ces ≈ 70 objets de décor, ce sont des icônes d'objets, des emblèmes, des icônes de compétences et des portraits. **Aucun objet d'environnement PixelLab n'est absent du client.** Planches : `props_*.png`.

---

## 2. Contrôle qualité des sols (montages)

Méthode : chaque atlas est découpé comme dans Godot (même mesure de grille, même `texture_origin`) et reposé en losanges 64×30.
- `montage_<nom>.png` : à gauche, une seule variante répétée en 3×3 (contrôle des raccords) ; à droite, un champ de 8×8 en variantes aléatoires avec le guerrier et le sanglier (lisibilité et échelle). Zoom ×2.
- `sheet_fill_01..08.png` : vue rectangulaire de 14×14 tuiles. À gauche, variantes aléatoires et sprites ; à droite, variante 0 répétée. C'est la meilleure vue pour juger la répétition.
- `overview_fills_1x.png` : les 30 sols à l'échelle 1:1 du jeu, pour comparer palette et luminosité.
- `sheet_transitions_atlases.png` et `sheet_paths_atlases.png` : les pièces de lisière et de route.
- `sheet_pixellab_01..05.png` : sols PixelLab non intégrés (et doublons pour comparaison).

Constat général : **deux générations de tuiles cohabitent.** Le 1er lot (grass, dirt, sand, rock, mud, dry_grass, water, cobble) est plat, pâle, avec un motif centré par tuile. Les lots du 16/08 et du 29/08 sont plus riches. Il existe aussi **trois verts incompatibles** : grass (pastel), grass_lush (moyen), forest_grass et grass_flowers (vert presque pur). Défaut récurrent dans PixelLab : le générateur dessine souvent un **bord ou un « coussin » par tuile** (bord plus sombre, centre plus clair). La grille de losanges reste alors visible en jeu.

| Tuile | Verdict | Détail |
|---|---|---|
| grass | **Problème** | vert pastel délavé, hors palette, presque sans texture ; grille de losanges légère. À remplacer par grass_lush désaturée (cf. prairie_ground_study) |
| grass_lush | OK (référence) | raccords invisibles, bonne densité, lisible sous les persos. Losange 5 px plus bas que les tuiles 42 px (origine figée, cf. commentaire du build) : petite marche aux jonctions avec les autres herbes |
| grass_flowers | OK | légère répétition des fleurs sur une variante unique, aucune avec l'aléatoire ; vert plus vif que grass_lush |
| forest_grass | **Problème modéré** | vert trop saturé (≈ #2A9A1A), contours noirs des touffes ; grille visible au bord des tuiles ; chargé sous les monstres. À désaturer ou régénérer |
| dry_grass | **Problème** | « coussin » clair au centre de chaque tuile, donc une grille de taches ; très pâle |
| swamp_grass | OK | |
| dirt | **Problème** | gris-beige (pas brun), bord sombre et centre clair par tuile, grille de losanges très visible. Remplacer par PixelLab 1f4e3b31 |
| dirt_pebbles | OK | légère diagonale ; orange saturé, ne raccorde pas avec dirt |
| mud | **Problème** | plaques en motif répété, grille nette |
| mud_trampled | **Rejet** | texture peinte (3 019 couleurs, floue, RVB), pas en iso. Hors build : ne pas utiliser |
| swamp_mud | **Problème** | bord sombre par tuile, grille losange marquée |
| farm_soil_dark | OK | (nom trompeur : ce sont les grosses pousses) |
| farm_soil_sprouts | OK | |
| sand | OK (faible) | variante 0 parfaitement unie ; plat mais propre (plage) |
| sand_golden | OK | le plus réussi des sables |
| sand_earth | **Problème** | variantes de luminosité très différentes (écart de 55 niveaux) : damier clair/foncé craquelé. Garder les variantes claires |
| sand_earth_pebbles | Problème léger | certaines variantes ont des carrés tramés visibles ; galet isolé répété en grille sur la variante 0 |
| arena_sand | Problème léger | liseré de losange sur chaque tuile, la grille se voit (acceptable pour une arène) |
| gravel_coarse | OK | |
| gravel_fine | Problème léger | trame en losanges et variantes « hachurées » qui jurent avec celles à graviers |
| rock | Problème léger | fissures alignées sur les bords de tuile : rend comme un carrelage. Acceptable en sol de grotte ou de carrière |
| cobble | OK | régulier, raccords invisibles, un peu fade |
| city_road | **Problème** | variantes incohérentes (dalles, pavés carrés, caniveaux, plaque ronde) : patchwork chargé ; palette bleutée différente du pavé des routes `paths/` |
| stone_slab | OK | joints de dalles = grille voulue |
| stone_ruin | OK | bon pour ruines |
| arena_stone | OK (chargé) | grandes fissures sombres, grille voulue |
| wood_plank | Problème léger | variantes de teinte différentes (damier clair/foncé) |
| water | OK | bonne eau, raccords invisibles |
| water_shallow | **Problème** | bandes plus sombres au bord de chaque tuile : grille de losanges très visible |
| swamp_water | **Problème modéré** | variantes « nénuphars verts » et « eau grise » mélangées (damier) ; se lit comme de l'herbe, pas comme de l'eau bloquante |
| magma | **Problème** | variantes totalement différentes (croûte noire, bulles, tourbillons, plaques) : damier violent ; jaune aveuglant. Inutilisable en grande surface |

**Transitions** (`sheet_transitions_atlases.png`) : **problème de style.**
- Les pièces sont des quarts de losange à bord droit, sans dentelure : on voit des blocs.
- Leurs palettes ne correspondent pas aux fill. Le vert de `transitions/grass` n'est ni grass ni grass_lush ; le brun de `transitions/dirt` n'est pas `dirt`.
- Elles ne marient que deux teintes d'une même famille. Il n'existe **aucune** transition inter-matières utile (herbe→boue, herbe→roche, herbe→marais, sable→eau…). 22 matériaux n'en ont aucune.

**Routes** (`sheet_paths_atlases.png`) : raccords propres et cohérents entre eux. En revanche :
1. bords rectilignes géométriques, une route de ville sur la prairie ;
2. pavé gris clair différent de `city_road` ;
3. seulement 3 supports (grass, grass_lush, sand) ;
4. **aucun chemin de terre** alors que 90 % de la carte est sauvage.

Ces routes sont des masques appliqués à deux matériaux. On peut donc fabriquer **sans génération** des chemins `dirt_on_grass_lush`, `dirt_on_forest_grass`, etc. avec les mêmes masques. Il faudrait un masque à bord irrégulier (2-3 px de dents) plutôt que droit.

**PixelLab non intégrés** : voir le tableau du §1.2. À retenir : 1f4e3b31 (terre) et 1fc547a5 (chemin de terre) sont bons ; e412cd20 (marais sombre) est bon après filtrage ; 424a82bc n'est bon qu'en variante 0.

**Cartes peintes** (`sheet_maps_tower_desert.png`) : les étages de la Tour d'Asher sont des **illustrations HD non pixel art**. **floor5, floor12 et floor15 portent un filigrane (étoile de Gemini, coin bas-droit, voir `_wm_*.png`).** C'est contraire à la règle 7 du README : à recadrer ou repeindre avant la sortie.

---

## 3. Par zone

Légende : **P** = principal, **S** = secondaire, **T** = transitions, **Ch** = chemins, **D** = décor existant, **L** = landmark proposé, **Dj** = entrée de donjon, **M** = manquant (le n° renvoie aux prompts du §3bis).
Chemins pour les props : `hv/` = `havreden/props/`, `lib/` = `world/props_library/`.

### Assets transverses (à faire une fois, réutilisés partout)
- **X1 Chemin de terre organique** : se compose à partir de 1f4e3b31 ou 1fc547a5 avec les masques existants, version à bord irrégulier. Pas de génération si on recompose. Sert à Fourrés, Lisière, Abords, Prairie, Bocage, Bois, Forêts, Clairière, Ours, Route.
- **X2 Fill « mixte » de lisière** : 16 variantes « herbe avec plaques de X ». Elles font tampon sur 1-2 cases entre deux matériaux, sans autotile : grass_lush/terre, grass_lush/roche, grass_lush/marais, forest/sol flétri, roche/neige, sable/herbe.
- **X3 Touffes et décals de sol** (props 1 direction, petits) : herbe haute, cailloux, flaques, feuilles mortes, os.
- **X4 Falaise modulaire** iso 2:1 : segment SE, segment SW, coin, bout. Utilisée par Ours, Col d'Asher, Élite Humanoïde, Plaine Fendue et l'Abîme.
- **X5 Tas d'os et carcasse** : Bois des Loups, Ours, Élite, Nécropole, Terres Déchirées.

### Nord

**Marécage 20-30 (+1 élite)** — `mz_marecage_20_30`
- P swamp_grass · S swamp_mud, swamp_water (bloquante), mud · T vers Fourrés/Lisière : X2 grass_lush↔swamp_grass · Ch : passerelles `hv/marsh/decor/marsh_walkway_*`
- D : tout `hv/marsh/` (38 assets), `lib/swamp_stilt_house`, `lib/rock_moss`, `lib/willow_tree`
- L : « le Cyprès-Pendu », un cyprès géant creux d'où pendent cages et lanternes (arène de l'élite)
- M (3) : M1 cyprès géant landmark ; M2 cercle de pieux et cages de l'élite ; X2 lisière herbe/marais. Corriger swamp_mud et swamp_water (retirer les variantes damier, sans rien générer).

**Fourrés des Sangliers 8-15** — `mz_sanglier_8_15`, `mz_sangliers-loups_6_15`
- P grass_lush · S mud (petites flaques), dirt_pebbles · T X2 · Ch X1
- D : `hv/vegetation/forest/` (shrub_cluster, fern_cluster, stump, saplings), `lib/bush_flowers`, `hv/pature/fences/fence_broken_by_animals_*`, `hv/pature/decor/hoofprint_decal_001`, `hv/marsh/trees/fallen_swamp_log_001`
- L : la Grande Bauge, une mare de boue autour d'un chêne déraciné
- M (4) : M3 fourré de ronces infranchissable (×2 variantes) ; M4 bauge de boue (prop au sol) ; M5 décal de sol retourné par les groins ; M6 chêne déraciné couché.

**Lisière d'Havreden 3-8 (insectes)** — `mz_scarabees_3_8`
- P grass_lush · S grass_flowers, dry_grass (à corriger) · T X2 · Ch X1
- D : `hv/vegetation/approved_no_outline/`, `hv/vegetation/village/`, `hv/pature/decor/straw_beehive_001`, `lib/wildflowers`, `lib/tall_grass`, `hv/fissures/static/near_village_micro_*`
- L : un vieux tronc creux transformé en nid de frelons géants (lien avec `giant_hornet`)
- M (3) : M7 nid de frelons géant sur tronc ; M8 monticule de scarabées / fourmilière ; X3 touffes d'herbe haute.

**Havreden (ville)** — havreden_area
- P cobble, city_road, grass_lush · S stone_slab, farm_soil_*, wood_plank · Ch : `paths/city_road_on_*`
- D : tout `hv/buildings`, `plaza`, `market`, `walls`, `village_life`, `facade_decor`, `training`, `teleport`
- L : la fontaine de cristal (existe)
- M (1) : X1 chemins de terre organiques dans les rues secondaires et les jardins (et intégrer l'étude `prairie_ground_study`). Remplacer `grass` partout où il reste.

**Abords d'Havreden 1-8 (rats)** — `mz_rats_1_8`
- P grass_lush · S dirt (→1f4e3b31), farm_soil_sprouts, cobble près des murs · T X2 · Ch X1, routes pavées existantes
- D : `hv/pature/`, `hv/village_life/`, `hv/infrastructure/sewer_grate_closed_001`, `hv/walls/generated/`
- Dj : **Égouts de Havreden** (rat_den, déjà en jeu) → il manque une vraie entrée visible
- L : la bouche d'égout voûtée sous le rempart, d'où sortent les rats
- M (3) : M9 sortie d'égout voûtée dans le talus et le mur (entrée de donjon) ; M10 trous de terriers de rats (décal) ; M11 tas d'ordures et de compost.

**Prairie 10-20** — `mz_prairie_10_20`, `mz_hyene_9_20`, `mz_taureaux_16-25_elite`
- P grass_lush · S dry_grass (à refaire), grass_flowers · T X2 · Ch X1
- D : `hv/pature/` (28), `hv/fences/prairie_2to1/` (16), `hv/buildings/pasture/`, `lib/hay_bales`, `lib/scarecrow`, `lib/wheat_field`
- L : le moulin de pâture (`pasture_windmill_001`, existe)
- M (2) : M12 nouvelle herbe sèche dorée sans « coussin » (remplace dry_grass) ; M13 sol piétiné par les taureaux (enclos élite).

**Bois Flétri 25-35 (forêt flétrie et corrompue, donjon)**
- P MF1 sol de forêt flétri · S M25 sol touché, forest_grass grisé en lisière · T X2 forest_grass↔MF1 · Ch X1 grisé
- D : `lib/dead_tree_corrupted` (2206f10e), `lib/crystal_tree_vitrified` (88aa5e41), `lib/crystal_corrupted` (2729b254), `hv/vegetation/forest/forest_dead_tree_001`, `hv/marsh/trees/dead_swamp_tree_001`, `hollow_stump_001`, `exposed_roots_001`, `fallen_swamp_log_001`, `hv/fissures/static/fissure_02/03` et `animated/02_small`
- Dj : une grotte de racines sous le grand arbre mort
- L : le Grand Flétri, un arbre géant mort, gris, avec une lueur violette entre ses racines (= entrée du donjon)
- M (6) : MF1 sol flétri ; MF2 grand arbre mort et entrée de donjon ; MF3 arbres de forêt flétris (2 variantes grises des `forest_tree_*`) ; MF4 buisson épineux mort ; MF5 touffes d'herbe morte (X3 grisé) ; M25 (partagé avec la Forêt Sud).

**Bocage 9-20 (haies, chats sauvages, hérisson)**
- P grass_lush · S grass_flowers, farm_soil · T X2 · Ch X1 en chemin creux
- D : `hv/vegetation/prototypes/trimmed_hedge_001` (trop petit, non 2:1), `hv/fences/prairie_2to1/`, chênes approuvés, `hv/pature/decor/`
- L : un calvaire de carrefour, croix de pierre moussue sous un vieux chêne, au croisement de deux haies
- M (6) : M14 haie bocagère SE ; M15 haie bocagère SW ; M16 coin et trouée de haie ; M17 muret de pierres sèches bas ; M18 tas de feuilles et de branches (gîte du hérisson) ; M19 calvaire de carrefour.

**Bois des Loups 13-23** — `mz_loup_13_23`, `mz_wolf_25-32`
- P forest_grass (désaturé) · S variante 0 de PixelLab 424a82bc (roche sombre), gravel_coarse · T X2 · Ch X1
- D : `hv/vegetation/forest/`, `lib/pine_tree`, `hv/vegetation/approved_no_outline/pine_light`, `lib/rock_*`, `lib/cave_entrance`
- L : la Tanière, un tertre rocheux creusé, os à l'entrée, griffures sur les troncs
- M (4) : M20 sol de forêt d'aiguilles de pin ; M21 tanière de loups (landmark) ; M22 tronc griffé ; X5 os et carcasse.

**Forêt Nord 12-26** — `mz_foret_12_26`
- P sol de forêt (M20 / M23) · S grass_lush, forest_grass · T X2 · Ch X1
- D : `hv/vegetation/forest/` (13 arbres et végétaux, dont `forest_tree_ancient_001`), `lib/mushrooms`, `hv/marsh/trees/hollow_stump_001`
- L : l'Arbre Ancien (`forest_tree_ancient_001`) au milieu d'un cercle de champignons
- M (2) : M23 litière de feuilles (feuillus) ; M24 cercle de champignons.

**Forêt Sud 25-35 (premières bêtes touchées par la Fissure, hameau de Mournelle)** — `mz_spider_25_30`
- P litière (M23) · S M25 sol « touché » · T M23↔M25 avec X2 · Ch X1
- D : forêt, `hv/fissures/static/fissure_02/03`, `lib/crystal_corrupted`, `lib/dead_tree_corrupted`. Hameau : `hv/buildings/pasture/` (chaumière, appentis), `prototypes/peasant_house_*`, `infrastructure/well_village_001`, `village_life/*`, `lib/chapel` (à détourer)
- L : **Mournelle**, hameau barricadé à l'orée, et le Chêne Fendu, un chêne immense coupé en deux par une fissure violette
- M (5) : M25 sol de forêt touché par la Fissure ; M26 palissade de hameau en rondins (SE/SW + portail) ; M27 Chêne Fendu ; M28 petits champignons et flore corrompus ; M29 lanterne de veille de Mournelle.

**Clairière 15-25**
- P grass_flowers · S grass_lush, water (petit étang : transitions water existantes) · Ch X1
- D : approved oaks, `lib/wildflowers`, `lib/rock_moss`, `hv/marsh/vegetation/reeds_001`, `lily_pads_001`
- L : un cercle de pierres levées autour d'une source
- M (2) : M30 pierres levées (×3 tailles) ; M31 source dans un bassin naturel.

**Zone de l'Ours 20-28 (rocheuse, grottes)** — `mz_ours_20_28`
- P rock (accepté) · S gravel_coarse, dirt_pebbles, forest_grass · T X2 roche↔herbe · Ch X1
- D : `lib/rock_*` (7), `lib/rock_formation_huge` (18aee328), `lib/cave_entrance` (0503ff3b), `hv/marsh/decor/swamp_rocks_001`, pins
- Dj : grotte de l'ours
- L : le Rocher-Ours, un grand rocher en forme d'ours couché, au-dessus de la grotte
- M (6) : X4 falaise modulaire (4 pièces) ; M32 sol rocheux moussu (mixte roche/herbe) ; M33 tanière d'ours (grotte et griffures) ; M34 buisson de baies sauvages ; M35 Rocher-Ours ; X5 os.

**Élite Humanoïde 35-45 (hommes-loups et hommes-rats, ruines, ravin)** — `mz_brigand_35-45`, `mz_rats_corrompu_40-50`
- P stone_ruin · S rock, gravel_coarse, dirt (1f4e3b31) · T X2 · Ch : ancienne voie, stone_ruin
- D : `lib/ruin`, `lib/barricade`, `lib/cage`, `lib/campfire`, `lib/ritual_altar`, `lib/bandit_camp`
- L : une tour de guet effondrée en travers du ravin
- M (5) : M36 mur en ruine SE/SW + coin ; M37 totem de guerre (crânes de bêtes) ; M38 tente en peaux ; M39 tour effondrée (landmark) ; X4 bord de ravin.

### Centre

**Route de Rochebourg 40-50 (brigands)**
- P chemin de terre 1fc547a5 en ornières · S grass_lush, dry_grass · Ch : `paths/city_road_on_*` près de la ville, X1 ailleurs
- D : `lib/04_routes/` (11 panneaux, wagon, cart), `lib/watchtower`, `lib/barricade`, `lib/bandit_camp`, `lib/campfire`, `hv/village_life/carts/`
- L : la caravane prise en embuscade (chariots renversés, caisses éventrées)
- M (3) : M40 borne milliaire et petit oratoire de route ; M41 panneau d'avis de recherche ; M42 chariot renversé et éventré.

**Tour d'Asher 60+**
- Extérieur : stone_ruin, rock. Intérieur : sols peints actuels.
- D : `lib/asher_tower` (fond opaque, style historique), `assets/maps/asher_tower_floor*`
- M (2) : M43 tour d'Asher extérieure dans le style canonique (détourée) ; M44 sol iso de dalles noires veinées de violet, pour monter des étages en TileMap ou remplacer les illustrations à filigrane.

**Chemin des Pèlerins 45-60 (fanatiques, sanctuaires)** — `mz_fanatique_45_60_elite`
- P stone_slab (voie) · S dry_grass (M12), gravel_fine · Ch : stone_slab
- D : `lib/zealot_banner`, `lib/ritual_altar`, `lib/brazier`, `lib/chapel` (détourer)
- L : la Statue Voilée, statue colossale d'un saint au visage couvert, entourée de cierges
- M (4) : M45 oratoire et cairn de pèlerin ; M46 rangée de bannières et cordes de prière ; M47 Statue Voilée ; M48 campement de pèlerins (tentes).

**Mines Basses 50-60 (gobelins, donjon)** — `mz_gobelins_50_60`
- P gravel_coarse · S dirt_pebbles, rock · Ch : M50 rails
- D : `lib/crates_sacks`, `lib/barrel`, `lib/campfire`, `lib/abandoned_wagon`
- Dj : entrée de mine boisée
- L : un chevalement de bois branlant au-dessus du puits principal
- M (4) : M49 entrée de mine boisée ; M50 rails de wagonnet (droit SE/SW, courbe) ; M51 wagonnet de minerai ; M52 terril et échafaudage gobelin.

**Abords de Rochebourg 45-50 (corrompus et humanoïdes)**
- P grass_lush · S farm_soil, M25 (sol touché) · Ch : `paths/city_road_on_grass*`
- D : `lib/rochebourg_house`, `lib/defensive_wall`, `lib/watchtower`, fissures 03
- L : une ferme incendiée, toit effondré, au pied des remparts
- M (2) : M53 ruines de ferme brûlée ; M54 champ corrompu (blé noirci, sol veiné).

**Rochebourg (ville)** — rochebourg_area
- P city_road (à filtrer), cobble · S stone_slab, 4d8a3aa6 (terre de village)
- D : `lib/rochebourg_house`, `lib/rochebourg_inn`, `lib/defensive_wall`, et les bâtiments de Havreden réutilisables
- L : la grande porte fortifiée
- M (3) : M55 porte de ville monumentale ; M56 segment de rempart haut SE/SW ; M57 maisons à colombages de Rochebourg (2 variantes SE/SW).

### Sud-froid

**Terres de Givre 60-66**
- P M58 neige · S M59 neige tassée (chemin), rock · T X2 roche/neige · Ch M59
- D : (rien de spécifique) `lib/rock_*` en recolorant
- L : la cage thoracique d'un géant prise dans la glace
- M (6) : M58 neige ; M59 neige tassée ; M60 sapin enneigé ; M61 rochers enneigés ; M62 squelette de géant gelé ; X2 neige/roche.

**Col d'Asher 60-68 (golems de pierre, Béhémoth)** — `mz_low_demon_61_70`
- P rock · S gravel_coarse, M58 en plaques · Ch M59
- D : `lib/rock_formation_huge`, `lib/rock_*`
- L : l'arène du Béhémoth, un pont de pierre effondré et un cratère d'empreinte
- M (3) : X4 falaises ; M63 monolithes runiques brisés (restes de golems) ; M64 pont de pierre effondré.

**Lac Gelé 64-70 (donjon de glace)**
- P M65 glace (marchable) · S M66 glace fissurée, M58 · T M67 rive gelée
- D : `hv/marsh/decor/marsh_rowboat_001` (à recolorer en barque prise dans la glace)
- Dj : grotte de glace
- L : une cascade gelée et l'ombre d'une bête prise sous la glace
- M (5) : M65, M66, M67 ; M68 entrée de grotte de glace ; M69 cascade gelée.

**La Rivière (rivière fine et pont)**
- P water · S water_shallow (à corriger), sand_golden, grass_lush · T M70 berge
- D : `lib/wooden_bridge`, `lib/rickety_bridge` (socles incrustés, non 2:1), `hv/marsh/decor/fishing_dock_001`, `hv/marsh/vegetation/reeds_001`
- L : le pont de pierre à une arche
- M (3) : M71 pont iso SE ; M72 pont iso SW ; M70 berge eau/herbe.

**Marais de la Faille 65-72 et Lanternfen** — `mz_marais_corrompu_60_70`
- P e412cd20 (filtré) · S swamp_mud, M73 eau corrompue · Ch : `hv/marsh/decor/marsh_walkway_*`
- D : tout `hv/marsh/`, notamment fisher_stilt_hut, fishing_dock, rowboat, marsh_lantern ; `lib/swamp_stilt_house` ; fissures
- L : **Lanternfen**, village sur pilotis dont les lanternes sur perche balisent, dans la brume, la route des barques vers l'Île
- M (4) : M73 eau de marais corrompue (reflets violets) ; M74 lanterne-balise sur perche plantée dans l'eau ; M75 maison sur pilotis de Lanternfen (2 variantes) ; M76 bac / grande barque du passeur.

### Sud-feu et Vide

**Terres de Braise 63-70 (cendres, braises)**
- P M77 cendre · S M78 sol à braises, rock
- D : `lib/brazier`, fissures (non)
- L : la souche colossale qui couve encore
- M (5) : M77, M78 ; M79 arbre calciné ; M80 rochers fumants ; M81 souche colossale.

**Chemin de lave 66-72 (étroit, bord est)**
- P M82 basalte · S magma (sous-ensemble filtré) · T M83 bord basalte/lave
- M (3) : M82, M83 ; M84 obsidienne et basalte en orgues.

**Plaine Fendue 72-80 (sol déchiré par le Vide)** — `mz_low_abyssal_70_80`
- P M85 terre fendue violette · S dry_grass grisée, rock · T X2
- D : `hv/fissures/static/04-05`, `animated/03-04`, `lib/fissure_lv4/lv5`, `lib/crystal_corrupted`, `lib/crystal_tree_vitrified`
- L : `fissure_05_massive` (existe), une colonne de lumière violette
- M (3) : M85 ; M86 plaques de sol soulevées ; M87 débris rocheux flottants.

**Nécropole 70-78 (cimetière, os)**
- P M88 terre de cimetière · S gravel_fine, stone_ruin · Ch stone_slab
- D : `lib/dead_tree_corrupted`, `hv/vegetation/forest/forest_dead_tree_001`, `lib/ritual_altar`
- L : l'ossuaire, une porte monumentale en crânes
- M (5) : M88 ; M89 pierres tombales (×4 variantes) ; M90 mausolée ; M91 grille de cimetière en fer SE/SW ; X5 os.

**Chaussée Brisée 78-88 (ancienne chaussée vers la ville en ruine)**
- P stone_ruin · S rock, water (de part et d'autre)
- D : `lib/ruin`, stone_ruin
- L : un arc de triomphe à moitié effondré sur la chaussée
- M (4) : M92 bord de chaussée surélevée SE/SW ; M93 tronçon effondré ; M94 colonnes tombées ; M95 arc brisé.

**Île / Anse des Naufragés 1-100 (plage, hautes herbes, cratère)**
- P sand_golden · S sand, water_shallow (à corriger), swamp_grass / dry_grass (hautes herbes) · T M70 rive
- D : `hv/marsh/decor/broken_rowboat_001`, `marsh_rowboat_001`, `lib/boat`, `lib/crates_sacks`, `lib/barrel`
- L : l'épave d'un grand navire échoué ; au centre, le cratère
- M (5) : M96 épave (landmark) ; M97 arbres côtiers penchés ; M98 bois flotté et coquillages ; M99 bord de cratère ; M100 fond de cratère vitrifié.

**Terres Déchirées 85-95 (désert démoniaque, donjon)** — `mz_demon_80_100`
- P M101 sol noir veiné de rouge · S M77 cendre, rock
- Dj : porte infernale
- L : la porte infernale encadrée de flèches d'os
- M (3) : M101 ; M102 flèches d'os et pics démoniaques ; M103 porte infernale (entrée de donjon).

**Caer Isthrel (ville en ruine) 80-100** — `mz_abyssal_85_100`
- P stone_ruin · S city_road filtré, M104 dalles envahies · Ch stone_slab
- D : `lib/ruin`, `hv/walls/generated/` (trop propres)
- L : la porte royale effondrée de Caer Isthrel
- M (5) : M104 dalles envahies de végétation ; M105 maisons en ruine (2 variantes) ; M106 statues brisées ; M107 porte royale en ruine ; M36 murs en ruine (réutilisés).

**L'Abîme 90-100 (gouffre final, donjon)**
- P M108 roche du Vide · T M109 bord du gouffre
- Dj : l'entrée de l'Abîme
- M (3) : M108, M109 ; M110 entrée de l'Abîme (escalier taillé qui plonge dans le noir violet).

### Décompte des manques

| Zone | Manques |
|---|---|
| Transverses X1–X5 | 5 (X1 sans génération) |
| Marécage | 3 |
| Fourrés | 4 |
| Lisière | 3 |
| Havreden | 1 |
| Abords d'Havreden | 3 |
| Prairie | 2 |
| Bois Flétri | 6 |
| Bocage | 6 |
| Bois des Loups | 4 |
| Forêt Nord | 2 |
| Forêt Sud / Mournelle | 5 |
| Clairière | 2 |
| Ours | 6 |
| Élite Humanoïde | 5 |
| Route de Rochebourg | 3 |
| Tour d'Asher | 2 |
| Chemin des Pèlerins | 4 |
| Mines Basses | 4 |
| Abords de Rochebourg | 2 |
| Rochebourg | 3 |
| Terres de Givre | 6 |
| Col d'Asher | 3 |
| Lac Gelé | 5 |
| La Rivière | 3 |
| Marais de la Faille / Lanternfen | 4 |
| Terres de Braise | 5 |
| Chemin de lave | 3 |
| Plaine Fendue | 3 |
| Nécropole | 5 |
| Chaussée Brisée | 4 |
| Île des Naufragés | 5 |
| Terres Déchirées | 3 |
| Caer Isthrel | 5 |
| L'Abîme | 3 |
| **Total** | **≈ 125 items** (dont ≈ 30 sols et ≈ 95 props), certains partagés |

---

## 3bis. Prompts PixelLab

### Gabarit SOL — `tiles_pro`
Réglages : type **isometric**, taille **64**, **16 variations**, vue **high top-down**. C'est le format du gros des sols du client.

Le format suit celui de 1f4e3b31 : matière, « clean crisp pixel art », couleur principale en hex, détails en hex, « crisp dithering », « readable surface ». **Ajout obligatoire** contre les défauts relevés au §2 : `uniform even brightness across the whole tile, texture continues seamlessly to every edge, no border, no rim, no vignette, no centered motif, all variations same base color`.

> Suffixe commun (noté [S] dans la suite) : `, clean crisp pixel art, crisp dithering, readable surface under characters, uniform even brightness across the whole tile, texture continues seamlessly to every edge, no border, no rim, no vignette, no centered motif, all variations same base color and value`

### Gabarit PROP — objet 1 direction
Canevas 64, 96, 128 ou 192. Garder l'échelle : personnage de 25×50 px, une tuile = losange 64×30.

> Préfixe commun (noté [P] dans la suite) : `isometric 2:1 pixel art game prop, high top-down three-quarter view, warm light from top-left, soft cool shadows, dark warm-brown colored outline (never pure black), muted earthy medieval fantasy palette, transparent background, no ground tile, no grass base, sized for a 25x50 px character,`

Pour un objet allongé, ajouter `footprint aligned to the isometric 2:1 diagonal (north-east to south-west)` ; la version SW s'obtient par une 2e génération, pas par un flip (lumière).

### Transverses
- **X1 chemin de terre** : pas de génération. Composer 1fc547a5 ou 1f4e3b31 sur grass_lush / forest_grass avec les masques `w40/w55/cut/disc`, version à bord irrégulier. Si on préfère générer : `isometric worn dirt footpath ground tile, packed warm brown earth #6B5440 with faint wheel ruts and footprints, #7D6450 highlights, #54412F depressions, small pebbles[S]`.
- **X2 lisières mixtes** (une génération par paire) :
  - `isometric grass ground tile with irregular bare earth patches, lush grass #4E8A2E covering 60 percent, packed brown earth #5E4A38 patches, small clods[S]`
  - `isometric rocky grass ground tile, lush grass #4E8A2E between flat grey stones #7C7A76, moss on stones[S]`
  - `isometric marsh edge ground tile, olive marsh grass #6E7C46 with dark wet mud puddles #3E3A28, reeds stubs[S]`
  - `isometric snowy rock ground tile, grey rock #7A7C80 half covered by patches of snow #E6ECF2, blue shadows #B4C2D2[S]`
- **X3** : [P] `small clump of tall wild grass blades, green #5A8A34 with yellowed tips`, canevas 48 (faire aussi `scattered small grey pebbles`, `small muddy puddle`, `pile of fallen brown oak leaves`).
- **X4 falaise** : [P] `modular rocky cliff wall segment, grey-brown layered stone #6E665C with moss on top edge, vertical face 96 px tall, footprint aligned to the isometric 2:1 diagonal (north-east to south-west)`, canevas 128 ; puis une version south-east, `outer corner` et `end piece crumbling into boulders`.
- **X5** : [P] `scattered animal bones and a picked ribcage on the ground, bleached ivory #D8CFB8 with brown stains`, canevas 64.

### Nord
- **M1** [P] `giant hollow bald cypress tree in a swamp, flared buttress roots, hanging rusty iron cages and small dim lanterns from its branches, olive moss`, canevas 192.
- **M2** [P] `ring of sharpened wooden stakes driven into marsh mud with two empty hanging cages, rotten rope`, canevas 128.
- **M3** [P] `dense impassable bramble thicket, dark green thorny bushes #3E5A2A with red berries, tangled`, canevas 128 (2 variantes).
- **M4** [P] `flat muddy wallow pool on the ground, churned dark mud #4A3A2A with water puddles and hoof marks, flat decal`, canevas 128.
- **M5** [P] `flat ground decal of soil torn up by boars, overturned clods of brown earth and uprooted grass tufts`, canevas 96.
- **M6** [P] `huge uprooted oak tree lying on its side, root ball with earth clods, broken branches, lush green leaves`, canevas 192.
- **M7** [P] `giant hornet nest built into a hollow tree trunk, grey papery layered nest #A89E8A, entrance holes, broken bark`, canevas 128.
- **M8** [P] `large beetle mound of packed earth with tunnels and small holes, dry brown soil #7A5E40`, canevas 96.
- **M9** [P] `arched stone sewer outlet set into a grassy embankment below a town wall, rusty iron grate half open, dirty water trickling out`, canevas 128. *Entrée des Égouts.*
- **M10** [P] `flat ground decal, three small rat burrow holes in the dirt with scattered gnawed debris`, canevas 64.
- **M11** [P] `village refuse heap, broken crates, rotten vegetables, straw and a cracked barrel`, canevas 96.
- **M12** tuile `isometric dry golden meadow grass ground tile, sun-dried grass #B49A52 with #C9B26A highlights and #8E7A40 shadows, short dense blades[S]`.
- **M13** tuile `isometric trampled pasture ground tile, flattened dry grass #9C8A4E over hoof-churned brown earth #6A523A, hoof prints[S]`.
- **M14** [P] `bocage hedgerow segment, dense living hedge of hawthorn and hazel #3F6A2C on a low earth bank, footprint aligned to the isometric 2:1 diagonal (north-east to south-west)`, canevas 128.
- **M15** idem, `(north-west to south-east)`.
- **M16** [P] `bocage hedgerow corner piece and a separate hedge end with a gap for a path`, canevas 128.
- **M17** [P] `low dry-stone field wall, stacked flat grey stones #8A8478 with moss, footprint aligned to the isometric 2:1 diagonal`, canevas 96.
- **M18** [P] `small pile of dead leaves and twigs under a bush, cozy hedgehog nest`, canevas 48.
- **M19** [P] `old mossy stone wayside calvary cross on a stepped base, under a small oak, wildflowers at its foot`, canevas 128.
- **M20** tuile `isometric pine forest floor ground tile, brown pine needles #6A5034 over dark soil #4A3828, few small cones and twigs, sparse dark green moss #3E5A2E[S]`.
- **M21** [P] `wolf den, low rocky mound with a dark burrow entrance, scattered bones, claw marks, trampled earth`, canevas 192.
- **M22** [P] `pine tree trunk stump with deep fresh claw marks in the bark`, canevas 96.
- **M23** tuile `isometric deciduous forest floor ground tile, fallen brown and ochre leaves #7A5A34 over dark soil #4C3A2A, small green sprouts #4E7A34[S]`.
- **M24** [P] `fairy ring of small pale mushrooms in a circle on the forest floor, flat`, canevas 96.

### Bois Flétri
- **MF1** tuile `isometric withered forest floor ground tile, dry grey-brown dead leaves #6E6050 over ashen soil #4A4440, dead grass tufts #7A7258, a few bare twigs[S]`.
- **MF2** [P] `giant withered dead tree, grey bleached trunk and bare twisted branches, huge roots arching over a dark hollow cave entrance with faint violet glow inside`, canevas 192 ×2. *Entrée de donjon et landmark.*
- **MF3** [P] `withered forest tree, grey-brown bark, sparse dry brown leaves, drooping branches, sickly`, canevas 128×160 (2 variantes : rond, élancé, à rapprocher des silhouettes de `forest_tree_*`).
- **MF4** [P] `dead thorny bush, grey-brown tangled branches with long thorns, no leaves`, canevas 64.
- **MF5** [P] `small clump of dead grey-yellow grass blades`, canevas 48.

### Forêt Sud, Ours, Élite
- **M25** tuile `isometric forest floor touched by corruption, greyed leaves #6A6460 over dark soil #3E3438, faint thin glowing violet veins #8A4AC8 in cracks[S]`.
- **M26** [P] `log palisade wall of sharpened timber posts lashed with rope, footprint aligned to the isometric 2:1 diagonal`, canevas 128, puis `palisade gate with wooden doors and a lantern`. *Mournelle.*
- **M27** [P] `enormous ancient oak split in two by a glowing violet crack running from roots to crown, half of it greyed and dead`, canevas 192.
- **M28** [P] `small cluster of corrupted mushrooms, grey caps with glowing violet spots`, canevas 48.
- **M29** [P] `wooden watch lantern post of a forest hamlet, iron lantern with warm light, small shingle roof`, canevas 96.
- **M30** [P] `ancient standing stone, tall weathered grey menhir #8A8680 with lichen and faint carved spirals`, canevas 96 (3 tailles).
- **M31** [P] `small natural spring pool in a ring of mossy stones, clear water, ferns`, canevas 128.
- **M32** tuile `isometric mossy rocky ground tile, flat grey stones #7C7A76 with green moss #4E6E34 in the gaps, small pebbles[S]`.
- **M33** [P] `bear cave entrance in a rocky hillside, big dark opening, deep claw scratches on the rock, bones and broken branches at the entrance`, canevas 192. *Entrée de donjon.*
- **M34** [P] `wild berry bush, dark green leaves with clusters of red and blue berries`, canevas 64.
- **M35** [P] `large granite boulder naturally shaped like a sleeping bear, moss on its back`, canevas 192.
- **M36** [P] `ruined stone wall segment, broken top, fallen blocks at its base, ivy, footprint aligned to the isometric 2:1 diagonal`, canevas 128 (+ version opposée + coin).
- **M37** [P] `crude beastmen war totem, wooden pole with wolf and rat skulls, tattered hide strips`, canevas 96.
- **M38** [P] `crude hide tent on bent poles, patched animal skins, bones hanging at the entrance`, canevas 128.
- **M39** [P] `collapsed stone watchtower lying across a rocky ravine, broken top and scattered blocks`, canevas 192.

### Centre
- **M40** [P] `old roadside milestone and tiny stone shrine with a candle niche`, canevas 64.
- **M41** [P] `wooden notice board with wanted posters nailed on it`, canevas 64.
- **M42** [P] `overturned merchant wagon on its side, broken wheel, spilled crates and sacks`, canevas 192.
- **M43** [P] `tall dark stone wizard tower, black-violet bricks with a glowing violet crack spiraling up, pointed roof`, canevas 192×256, **fond transparent**.
- **M44** tuile `isometric dark tower floor tile, black-grey stone flagstones #3E3A44 with thin glowing violet cracks #8A4AC8, worn edges[S]`.
- **M45** [P] `pilgrim cairn of stacked stones with small votive candles and ribbons`, canevas 64.
- **M46** [P] `row of tall red fanatic banners on wooden poles with prayer cords between them, footprint aligned to the isometric 2:1 diagonal`, canevas 128.
- **M47** [P] `colossal stone statue of a hooded saint with a veiled face, hands joined, candles at its pedestal`, canevas 192.
- **M48** [P] `pilgrim camp, two small canvas tents, bedrolls, campfire and walking staffs`, canevas 192.
- **M49** [P] `timber-framed mine entrance dug into a rocky hillside, wooden beams, lantern, mine rails going in`, canevas 192. *Entrée de donjon.*
- **M50** [P] `straight mine cart rail track segment on gravel, footprint aligned to the isometric 2:1 diagonal`, canevas 64 (+ version opposée + courbe).
- **M51** [P] `wooden mine cart full of ore with glints of copper`, canevas 64.
- **M52** [P] `goblin spoil heap of grey rubble with rickety wooden scaffolding and a crude ladder`, canevas 128.
- **M53** [P] `burned farmhouse ruin, charred timber frame, collapsed roof, blackened stone chimney`, canevas 192.
- **M54** tuile `isometric corrupted wheat field ground tile, blackened wheat stalks #3E3428 on dark soil, faint violet veins[S]`.
- **M55** [P] `monumental fortified city gate, two round stone towers, portcullis, red banners`, canevas 192 ×2.
- **M56** [P] `tall grey stone city rampart segment with crenellations, footprint aligned to the isometric 2:1 diagonal`, canevas 128.
- **M57** [P] `two-storey half-timbered town house, dark slate roof, plaster and dark beams, south-east facing`, canevas 192 (+ SW).

### Froid
- **M58** tuile `isometric fresh snow ground tile, soft white snow #E6ECF2 with pale blue shadows #B4C2D2, subtle wind ripples[S]`.
- **M59** tuile `isometric packed snow path ground tile, trampled grey-white snow #C8CED6 with boot prints and slush #9AA4AE[S]`.
- **M60** [P] `snow-covered pine tree, dark green #2E4A3A branches heavy with snow`, canevas 128×192.
- **M61** [P] `cluster of grey rocks capped with snow and icicles`, canevas 96.
- **M62** [P] `giant skeleton ribcage half buried in snow and ice, huge curved bones, frost`, canevas 192.
- **M63** [P] `broken runic stone monoliths, cracked grey slabs with faintly glowing blue runes, rubble`, canevas 128.
- **M64** [P] `collapsed stone arch bridge over a chasm, broken middle, fallen blocks`, canevas 192.
- **M65** tuile `isometric frozen lake ice ground tile, smooth pale blue ice #A8C8DA with white frost streaks #E0EEF6 and faint deep blue #6A94B4 under it[S]`.
- **M66** tuile identique `with thin white cracks spreading`.
- **M67** tuile `isometric frozen shore ground tile, frosted pebbles and snow #D6DEE6 over grey earth[S]`.
- **M68** [P] `ice cave entrance in a frozen cliff, translucent blue ice arch, icicles, cold mist`, canevas 192. *Entrée de donjon.*
- **M69** [P] `frozen waterfall cascading down a rock face, solid blue-white ice`, canevas 192.
- **M70** tuile `isometric riverbank ground tile, wet dark sand #8A7A5A meeting short grass, small reeds and pebbles[S]`.
- **M71/M72** [P] `small single-arch stone bridge spanning a narrow river, mossy stones, footprint aligned to the isometric 2:1 diagonal (north-east to south-west)` / `(north-west to south-east)`, canevas 192, sans eau.
- **M73** tuile `isometric dark corrupted swamp water tile, murky black-green water #1E2A26 with faint violet glints #6A3A8A and floating debris[S]`.
- **M74** [P] `tall wooden pole planted in swamp water with a hanging glowing lantern, rope and small bell, guiding light in the mist`, canevas 64×128. *Landmark de Lanternfen.*
- **M75** [P] `stilt house of a misty swamp village, weathered planks, reed roof, lantern at the door, ladder to the water`, canevas 192 (2 variantes).
- **M76** [P] `long flat ferry boat with a pole and a lantern on its prow, weathered wood`, canevas 192.

### Feu et Vide
- **M77** tuile `isometric ash ground tile, grey volcanic ash #5A5654 with darker #3E3A38 soot and scattered tiny embers #C85A28[S]`.
- **M78** tuile `isometric ember ground tile, cracked black crust #2E2626 with glowing orange cracks #E07028, low glow[S]`.
- **M79** [P] `charred dead tree, black burnt trunk with a few glowing embers in cracks`, canevas 128.
- **M80** [P] `cluster of dark rocks with smoke wisps rising and orange glowing cracks`, canevas 96.
- **M81** [P] `colossal burnt tree stump still smoldering, glowing core, ash around`, canevas 192.
- **M82** tuile `isometric dark basalt ground tile, black-grey basalt #3A3638 with hexagonal joints and faint red reflections[S]`.
- **M83** tuile `isometric basalt edge over lava tile, basalt crust #3A3638 broken by thin bright lava channels #F08A28[S]`. Régénérer aussi `magma` en homogène : `isometric molten lava ground tile, orange lava #E06A1E with slow darker crust #8A2E14 swirls, no yellow patches[S]`.
- **M84** [P] `cluster of black obsidian shards and basalt columns, glossy edges`, canevas 96.
- **M85** tuile `isometric torn earth ground tile, dry grey soil #6A6460 split by thin glowing violet cracks #9A4ADA[S]`.
- **M86** [P] `tilted slab of earth torn up from the ground, raw soil underside, violet glow beneath`, canevas 128.
- **M87** [P] `small rocks and earth clods floating in the air above a crack, violet glow`, canevas 96.
- **M88** tuile `isometric graveyard soil ground tile, dark grey-brown earth #4A4440 with sparse dead grass #6A6650 and small bone fragments[S]`.
- **M89** [P] `weathered stone tombstone, tilted, moss and cracks`, canevas 64 (4 variantes : croix, stèle arrondie, stèle brisée, dalle).
- **M90** [P] `small gothic stone mausoleum with iron door and broken angel statue on the roof`, canevas 192.
- **M91** [P] `wrought iron cemetery fence segment with spikes, rusty, footprint aligned to the isometric 2:1 diagonal`, canevas 96 (+ version opposée + portail).
- **M92** [P] `edge of a raised ancient stone causeway, large worn flagstones on top, stone retaining side, footprint aligned to the isometric 2:1 diagonal`, canevas 128 (+ opposée).
- **M93** [P] `collapsed section of an ancient stone causeway, broken flagstones falling into water`, canevas 192.
- **M94** [P] `fallen marble column pieces, fluted drums and a broken capital`, canevas 128.
- **M95** [P] `half-collapsed ancient triumphal stone arch, carved reliefs, one pillar broken`, canevas 192.
- **M96** [P] `large wrecked sailing ship beached on its side, broken mast, torn sail, hull planks missing`, canevas 192 ×2.
- **M97** [P] `leaning coastal tree bent by the wind, sparse foliage, exposed roots in sand`, canevas 128.
- **M98** [P] `driftwood log with shells and seaweed on sand`, canevas 64.
- **M99** [P] `rim of an impact crater, raised scorched earth and rocks, footprint aligned to the isometric 2:1 diagonal`, canevas 128.
- **M100** tuile `isometric crater floor ground tile, glassy vitrified dark earth #3A3436 with faint violet sheen[S]`.
- **M101** tuile `isometric demonic wasteland ground tile, cracked black rock #2A2224 with thin glowing red veins #C82828[S]`.
- **M102** [P] `cluster of jagged bone spires and black demonic spikes rising from the ground`, canevas 128.
- **M103** [P] `infernal gate, huge arch of black stone and horns, glowing red portal inside, chains`, canevas 192. *Entrée de donjon.*
- **M104** tuile `isometric overgrown ruined flagstone ground tile, cracked pale stone #8A8680 with grass and ivy #4E6E34 in the cracks[S]`.
- **M105** [P] `ruined stone house of a fallen city, roofless, broken walls, ivy, south-east facing`, canevas 192 (2 variantes).
- **M106** [P] `broken statue of a knight, headless, fallen sword at its feet, cracked pedestal`, canevas 128.
- **M107** [P] `ruined royal city gate, two broken towers, collapsed archway, torn faded banners`, canevas 192 ×2.
- **M108** tuile `isometric void rock ground tile, dark purple-black stone #24202E with faint starry violet specks #8A6AC8[S]`.
- **M109** [P] `edge of a bottomless chasm, crumbling dark rock lip falling into violet darkness, footprint aligned to the isometric 2:1 diagonal`, canevas 128 (+ opposée + coin).
- **M110** [P] `ancient stair carved into rock descending into a glowing violet abyss, broken pillars on each side`, canevas 192. *Entrée de donjon.*

---

## 4. Priorités

**0. Correctifs sans génération (à faire d'abord, gratuits)**
1. Retirer `mud_trampled.png` des choix. Filtrer les variantes en damier de `sand_earth`, `swamp_water`, `swamp_mud`, `magma` et `city_road` (garder 6 à 10 variantes homogènes par atlas ; le build tolère les trous).
2. Composer X1 (chemin de terre) à partir de 1fc547a5 / 1f4e3b31 avec les masques de `paths/`, bords irréguliers.
3. Intégrer 1f4e3b31 comme nouveau `dirt` (ajout en fin de `MATERIALS`) et e412cd20 filtré pour le Marais de la Faille.
4. Détourer `lib/asher_tower` et `lib/chapel`. Enlever le filigrane des étages 5, 12 et 15 de la Tour.

**1. Zones aux monstres validés**
1. **Bois Flétri** : MF1 (sol), MF2 (grand arbre mort et entrée de donjon), M25, MF3, MF4, MF5.
2. **Bocage** : M14, M15, M16 (haies), M17, M19, M18.
3. **Forêt Sud / Mournelle** : M23, M25, M26, M27, M28, M29.
4. **Ours** : X4 falaise (sert à 5 zones), M33 (Dj), M32, M35, M34, X5.

**2. Sols de base à refaire** (visibles partout au nord) : M12 herbe sèche, désaturation ou régénération de forest_grass, remplacement de `grass` par grass_lush, water_shallow homogène. Puis X2 lisières mixtes (herbe/terre, herbe/roche, herbe/marais).

**3. Nord restant** : Fourrés (M3–M6), Lisière (M7, M8), Abords (M9 entrée des égouts), Bois des Loups (M20, M21), Marécage (M1).

**4. Centre** : Élite Humanoïde (M36 murs en ruine, réutilisés à Caer Isthrel), Route (M42), Mines (M49, M50), Pèlerins (M47), Rochebourg.

**5. Sud** : dans l'ordre de progression. Givre et Col (M58/M59, réutilisés au Lac), Lac Gelé, Rivière (M71/M72), **Lanternfen (M74 en priorité : c'est le landmark)**, Braise et lave (M77, M82 ; M77 resservira aux Terres Déchirées), Plaine Fendue, Nécropole, Chaussée, Île, Terres Déchirées, Caer Isthrel, Abîme.

Réutilisation maximale :
- **sols** : M25 (Forêt Sud, Abords de Rochebourg, Bois Flétri), M58 (Givre, Col, Lac), M77 (Braise, Terres Déchirées) ;
- **falaises et ruines** : X4 (Ours, Col, Élite, Plaine, Abîme), M36 (Élite, Caer Isthrel, Chaussée) ;
- **décor** : X5 os (5 zones), marsh/* (Marécage, Faille, Île, Rivière).
