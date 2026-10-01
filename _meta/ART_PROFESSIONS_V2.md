# Metiers V2 : liste des visuels a produire

Date : 2026-10-01. Source de verite des ids et des chemins : `items/profession_recipes.json` (`new_items`) et `world/gather_nodes.json`. Chemins relatifs a `kanarion_front/`. Le contrat icone du jeu s'applique : le fichier porte EXACTEMENT l'id de l'objet.

## A savoir avant de commencer

- **Les variantes de rarete (rare, epique, legendaire) ne demandent AUCUNE icone.** Elles reprennent l'icone de base ; le client dessine le cadre de rarete. Ne produire que les ids listes ici.
- Les icones deja livrees (minerais, bois, poissons, produits de la foret, Braise de Faille, carte Koro vierge, elixirs, parchemins, friandises) ne sont pas a refaire.
- Format : meme gabarit que les icones de materiaux existantes (`assets/icons/items/materials/`), fond transparent, lisible a 32 px. Le rang se lit a la matiere et a la lueur, pas a un chiffre dans l'image (le client affiche le rang I a V a part).
- Regle de lore : la vie, pas la mort. On montre ce que la terre redonne (bois mort, ecorce, herbe coupee au-dessus de la racine), jamais d'arbre abattu ni de creature depouillee.

Echelle de rang commune aux ressources et intermediaires :

- rang I : matiere simple, tons bruns et verts sourds
- rang II : un peu plus net, reflet clair
- rang III : couleur franche, premier eclat
- rang IV : veinures ou lueur bleu-blanc du Souffle
- rang V : lueur violette de Faille, contour plus marque

## 1. Icones de ressources et d'intermediaires

### Herbes (Herboriste)

Une plante coupee au-dessus de la racine, en petit bouquet ou en brin, lisible a 32 px.

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `mat_herb_sauge` | Sauge de Havreden | 1 | `assets/icons/items/materials/mat_herb_sauge.png` |
| `mat_herb_clairpre` | Clair-de-pré | 2 | `assets/icons/items/materials/mat_herb_clairpre.png` |
| `mat_herb_veilleuse` | Veilleuse des marais | 3 | `assets/icons/items/materials/mat_herb_veilleuse.png` |
| `mat_herb_souffle` | Feuille-de-Souffle | 4 | `assets/icons/items/materials/mat_herb_souffle.png` |
| `mat_herb_cicatrice` | Cicatrice-verte | 5 | `assets/icons/items/materials/mat_herb_cicatrice.png` |

### Ecorces (Bucheron)

Un lambeau d'ecorce roule, couleur de l'essence (frene clair, chene brun, if rougeatre, Souffle bleute, obscur presque noir).

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `mat_bark_frene` | Écorce de frêne | 1 | `assets/icons/items/materials/mat_bark_frene.png` |
| `mat_bark_chene` | Écorce de chêne | 2 | `assets/icons/items/materials/mat_bark_chene.png` |
| `mat_bark_if` | Écorce d'if | 3 | `assets/icons/items/materials/mat_bark_if.png` |
| `mat_bark_souffle` | Écorce de Souffle | 4 | `assets/icons/items/materials/mat_bark_souffle.png` |
| `mat_bark_obscur` | Écorce obscure | 5 | `assets/icons/items/materials/mat_bark_obscur.png` |

### Resines (Bucheron)

Une goutte ou un petit bloc de resine translucide, couleur ambre au rang I jusqu'a violet de Faille au rang V.

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `mat_resin_frene` | Résine de frêne | 1 | `assets/icons/items/materials/mat_resin_frene.png` |
| `mat_resin_chene` | Résine de chêne | 2 | `assets/icons/items/materials/mat_resin_chene.png` |
| `mat_resin_if` | Résine d'if | 3 | `assets/icons/items/materials/mat_resin_if.png` |
| `mat_resin_souffle` | Résine de Souffle | 4 | `assets/icons/items/materials/mat_resin_souffle.png` |
| `mat_resin_obscur` | Résine obscure | 5 | `assets/icons/items/materials/mat_resin_obscur.png` |

### Sables et quartz (Mineur)

Petit tas de sable (rangs I-II) puis eclats de quartz de plus en plus purs (rangs III-V).

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `mat_sand_riviere` | Sable de rivière | 1 | `assets/icons/items/materials/mat_sand_riviere.png` |
| `mat_sand_blanc` | Sable blanc | 2 | `assets/icons/items/materials/mat_sand_blanc.png` |
| `mat_sand_quartz` | Sable de quartz | 3 | `assets/icons/items/materials/mat_sand_quartz.png` |
| `mat_sand_souffle` | Quartz de Souffle | 4 | `assets/icons/items/materials/mat_sand_souffle.png` |
| `mat_sand_faille` | Quartz de Faille | 5 | `assets/icons/items/materials/mat_sand_faille.png` |

### Sel (Mineur)

Un bloc de sel gemme rose pale, facettes nettes. Rang unique.

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `mat_salt_gemme` | Sel gemme | 1 | `assets/icons/items/materials/mat_salt_gemme.png` |

### Cuir tanne (Tanneur)

Un rouleau de cuir lie d'une ficelle ; la teinte fonce et la couture s'orne avec le rang.

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `mat_leather_r1` | Cuir tanné I | 1 | `assets/icons/items/materials/mat_leather_r1.png` |
| `mat_leather_r2` | Cuir tanné II | 2 | `assets/icons/items/materials/mat_leather_r2.png` |
| `mat_leather_r3` | Cuir tanné III | 3 | `assets/icons/items/materials/mat_leather_r3.png` |
| `mat_leather_r4` | Cuir tanné IV | 4 | `assets/icons/items/materials/mat_leather_r4.png` |
| `mat_leather_r5` | Cuir tanné V | 5 | `assets/icons/items/materials/mat_leather_r5.png` |

### Lingots (Runiste)

Un lingot trapeze : fer gris, argent, cuivre de Souffle (cuivre a reflets bleus), astral (bleu nuit etoile), Faille (violet sombre).

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `mat_ingot_r1` | Lingot de fer | 1 | `assets/icons/items/materials/mat_ingot_r1.png` |
| `mat_ingot_r2` | Lingot d'argent | 2 | `assets/icons/items/materials/mat_ingot_r2.png` |
| `mat_ingot_r3` | Lingot de cuivre de Souffle | 3 | `assets/icons/items/materials/mat_ingot_r3.png` |
| `mat_ingot_r4` | Lingot astral | 4 | `assets/icons/items/materials/mat_ingot_r4.png` |
| `mat_ingot_r5` | Lingot de Faille | 5 | `assets/icons/items/materials/mat_ingot_r5.png` |

### Fioles (Apothicaire)

Fiole VIDE bouchee de resine ; le verre passe de vert trouble a clair, quartz, bleu de Souffle, violet de Faille.

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `mat_vial_r1` | Fiole de verre | 1 | `assets/icons/items/materials/mat_vial_r1.png` |
| `mat_vial_r2` | Fiole de verre blanc | 2 | `assets/icons/items/materials/mat_vial_r2.png` |
| `mat_vial_r3` | Fiole de quartz | 3 | `assets/icons/items/materials/mat_vial_r3.png` |
| `mat_vial_r4` | Fiole de Souffle | 4 | `assets/icons/items/materials/mat_vial_r4.png` |
| `mat_vial_r5` | Fiole de Faille | 5 | `assets/icons/items/materials/mat_vial_r5.png` |

### Solvants (Apothicaire)

Fiole a demi pleine d'un liquide incolore a reflets ; bulles plus vives avec le rang.

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `mat_solvent_r1` | Solvant I | 1 | `assets/icons/items/materials/mat_solvent_r1.png` |
| `mat_solvent_r2` | Solvant II | 2 | `assets/icons/items/materials/mat_solvent_r2.png` |
| `mat_solvent_r3` | Solvant III | 3 | `assets/icons/items/materials/mat_solvent_r3.png` |
| `mat_solvent_r4` | Solvant IV | 4 | `assets/icons/items/materials/mat_solvent_r4.png` |
| `mat_solvent_r5` | Solvant V | 5 | `assets/icons/items/materials/mat_solvent_r5.png` |

### Encres (Apothicaire)

Encrier rond : encre vert sauge, jaune des pres, bleu des marais, bleu de Souffle, vert profond de Cicatrice-verte.

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `mat_ink_r1` | Encre de sauge | 1 | `assets/icons/items/materials/mat_ink_r1.png` |
| `mat_ink_r2` | Encre des prés | 2 | `assets/icons/items/materials/mat_ink_r2.png` |
| `mat_ink_r3` | Encre des marais | 3 | `assets/icons/items/materials/mat_ink_r3.png` |
| `mat_ink_r4` | Encre de Souffle | 4 | `assets/icons/items/materials/mat_ink_r4.png` |
| `mat_ink_r5` | Encre de Cicatrice-verte | 5 | `assets/icons/items/materials/mat_ink_r5.png` |

### Papier (Scribe)

Feuilles pliees ou petite pile : papier d'ecorce brut, chene, parchemin d'if, velin de Souffle, velin obscur.

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `mat_paper_r1` | Papier d'écorce | 1 | `assets/icons/items/materials/mat_paper_r1.png` |
| `mat_paper_r2` | Papier de chêne | 2 | `assets/icons/items/materials/mat_paper_r2.png` |
| `mat_paper_r3` | Parchemin d'if | 3 | `assets/icons/items/materials/mat_paper_r3.png` |
| `mat_paper_r4` | Vélin de Souffle | 4 | `assets/icons/items/materials/mat_paper_r4.png` |
| `mat_paper_r5` | Vélin obscur | 5 | `assets/icons/items/materials/mat_paper_r5.png` |

### Epices (Cuisinier)

Petit sachet de toile ouvert sur un melange colore ; plus de couleurs avec le rang.

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `mat_spice_r1` | Épices I | 1 | `assets/icons/items/materials/mat_spice_r1.png` |
| `mat_spice_r2` | Épices II | 2 | `assets/icons/items/materials/mat_spice_r2.png` |
| `mat_spice_r3` | Épices III | 3 | `assets/icons/items/materials/mat_spice_r3.png` |
| `mat_spice_r4` | Épices IV | 4 | `assets/icons/items/materials/mat_spice_r4.png` |
| `mat_spice_r5` | Épices V | 5 | `assets/icons/items/materials/mat_spice_r5.png` |

### Farine (Cuisinier)

Petit sac de farine noue ; le sac s'ennoblit avec le rang (toile, lin, broderie).

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `mat_flour_r1` | Farine I | 1 | `assets/icons/items/materials/mat_flour_r1.png` |
| `mat_flour_r2` | Farine II | 2 | `assets/icons/items/materials/mat_flour_r2.png` |
| `mat_flour_r3` | Farine III | 3 | `assets/icons/items/materials/mat_flour_r3.png` |
| `mat_flour_r4` | Farine IV | 4 | `assets/icons/items/materials/mat_flour_r4.png` |
| `mat_flour_r5` | Farine V | 5 | `assets/icons/items/materials/mat_flour_r5.png` |

### Aiguilles d'os (Sculpteur d'os)

Deux aiguilles et un hamecon d'os croises ; os blanc puis grave, puis lueur.

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `mat_needle_r1` | Aiguilles d'os I | 1 | `assets/icons/items/materials/mat_needle_r1.png` |
| `mat_needle_r2` | Aiguilles d'os II | 2 | `assets/icons/items/materials/mat_needle_r2.png` |
| `mat_needle_r3` | Aiguilles d'os III | 3 | `assets/icons/items/materials/mat_needle_r3.png` |
| `mat_needle_r4` | Aiguilles d'os IV | 4 | `assets/icons/items/materials/mat_needle_r4.png` |
| `mat_needle_r5` | Aiguilles d'os V | 5 | `assets/icons/items/materials/mat_needle_r5.png` |

### Eau-de-vie (Brasseur)

Petite flasque de terre puis de verre, liquide ambre a dore.

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `mat_spirit_r1` | Eau-de-vie I | 1 | `assets/icons/items/materials/mat_spirit_r1.png` |
| `mat_spirit_r2` | Eau-de-vie II | 2 | `assets/icons/items/materials/mat_spirit_r2.png` |
| `mat_spirit_r3` | Eau-de-vie III | 3 | `assets/icons/items/materials/mat_spirit_r3.png` |
| `mat_spirit_r4` | Eau-de-vie IV | 4 | `assets/icons/items/materials/mat_spirit_r4.png` |
| `mat_spirit_r5` | Eau-de-vie V | 5 | `assets/icons/items/materials/mat_spirit_r5.png` |

### Plumes taillees (Eleveur)

Une plume taillee en bec ; plume grise de corbeau, puis plus fournie, reflets bleus puis violets.

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `mat_quill_r1` | Plume taillée I | 1 | `assets/icons/items/materials/mat_quill_r1.png` |
| `mat_quill_r2` | Plume taillée II | 2 | `assets/icons/items/materials/mat_quill_r2.png` |
| `mat_quill_r3` | Plume taillée III | 3 | `assets/icons/items/materials/mat_quill_r3.png` |
| `mat_quill_r4` | Plume taillée IV | 4 | `assets/icons/items/materials/mat_quill_r4.png` |
| `mat_quill_r5` | Plume taillée V | 5 | `assets/icons/items/materials/mat_quill_r5.png` |

### Reliques restaurees (Collectionneur)

Une curiosite nettoyee et vernie (piece, insigne, medaillon) posee sur un petit coussin.

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `mat_relic_r1` | Relique restaurée I | 1 | `assets/icons/items/materials/mat_relic_r1.png` |
| `mat_relic_r2` | Relique restaurée II | 2 | `assets/icons/items/materials/mat_relic_r2.png` |
| `mat_relic_r3` | Relique restaurée III | 3 | `assets/icons/items/materials/mat_relic_r3.png` |
| `mat_relic_r4` | Relique restaurée IV | 4 | `assets/icons/items/materials/mat_relic_r4.png` |
| `mat_relic_r5` | Relique restaurée V | 5 | `assets/icons/items/materials/mat_relic_r5.png` |

## 2. Icones d'outils de recolte

Nouveau dossier `assets/icons/items/tools/`. Un outil par rang ; le rang se lit au metal et au manche :

- rang I : fer brut, manche de frene, lien de corde
- rang II : argent, manche de chene, poignee de cuir
- rang III : cuivre de Souffle, manche d'if, cuir clous
- rang IV : metal astral, manche de bois de Souffle, lueur bleue sur le tranchant
- rang V : metal de Faille, Bois Obscur, lueur violette discrete

### Pioches (Sculpteur d'os, pour le Mineur)

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `tool_pickaxe_r1` | Pioche I | 1 | `assets/icons/items/tools/tool_pickaxe_r1.png` |
| `tool_pickaxe_r2` | Pioche II | 2 | `assets/icons/items/tools/tool_pickaxe_r2.png` |
| `tool_pickaxe_r3` | Pioche III | 3 | `assets/icons/items/tools/tool_pickaxe_r3.png` |
| `tool_pickaxe_r4` | Pioche IV | 4 | `assets/icons/items/tools/tool_pickaxe_r4.png` |
| `tool_pickaxe_r5` | Pioche V | 5 | `assets/icons/items/tools/tool_pickaxe_r5.png` |

### Haches (Sculpteur d'os, pour le Bucheron)

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `tool_axe_r1` | Hache I | 1 | `assets/icons/items/tools/tool_axe_r1.png` |
| `tool_axe_r2` | Hache II | 2 | `assets/icons/items/tools/tool_axe_r2.png` |
| `tool_axe_r3` | Hache III | 3 | `assets/icons/items/tools/tool_axe_r3.png` |
| `tool_axe_r4` | Hache IV | 4 | `assets/icons/items/tools/tool_axe_r4.png` |
| `tool_axe_r5` | Hache V | 5 | `assets/icons/items/tools/tool_axe_r5.png` |

### Faucilles (Sculpteur d'os, pour l'Herboriste)

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `tool_sickle_r1` | Faucille I | 1 | `assets/icons/items/tools/tool_sickle_r1.png` |
| `tool_sickle_r2` | Faucille II | 2 | `assets/icons/items/tools/tool_sickle_r2.png` |
| `tool_sickle_r3` | Faucille III | 3 | `assets/icons/items/tools/tool_sickle_r3.png` |
| `tool_sickle_r4` | Faucille IV | 4 | `assets/icons/items/tools/tool_sickle_r4.png` |
| `tool_sickle_r5` | Faucille V | 5 | `assets/icons/items/tools/tool_sickle_r5.png` |

### Cannes a peche (Tanneur, pour le Pecheur)

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `tool_fishing_rod_r1` | Canne à pêche I | 1 | `assets/icons/items/tools/tool_fishing_rod_r1.png` |
| `tool_fishing_rod_r2` | Canne à pêche II | 2 | `assets/icons/items/tools/tool_fishing_rod_r2.png` |
| `tool_fishing_rod_r3` | Canne à pêche III | 3 | `assets/icons/items/tools/tool_fishing_rod_r3.png` |
| `tool_fishing_rod_r4` | Canne à pêche IV | 4 | `assets/icons/items/tools/tool_fishing_rod_r4.png` |
| `tool_fishing_rod_r5` | Canne à pêche V | 5 | `assets/icons/items/tools/tool_fishing_rod_r5.png` |

### Besaces de glaneur (Tanneur, pour le Glaneur)

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `tool_satchel_r1` | Besace de glaneur I | 1 | `assets/icons/items/tools/tool_satchel_r1.png` |
| `tool_satchel_r2` | Besace de glaneur II | 2 | `assets/icons/items/tools/tool_satchel_r2.png` |
| `tool_satchel_r3` | Besace de glaneur III | 3 | `assets/icons/items/tools/tool_satchel_r3.png` |
| `tool_satchel_r4` | Besace de glaneur IV | 4 | `assets/icons/items/tools/tool_satchel_r4.png` |
| `tool_satchel_r5` | Besace de glaneur V | 5 | `assets/icons/items/tools/tool_satchel_r5.png` |

### Lanternes de Faille (Runiste, pour le Chasseur de Failles)

| Id | Nom FR | Rang | Chemin |
|---|---|---|---|
| `tool_lantern_r1` | Lanterne de Faille I | 1 | `assets/icons/items/tools/tool_lantern_r1.png` |
| `tool_lantern_r2` | Lanterne de Faille II | 2 | `assets/icons/items/tools/tool_lantern_r2.png` |
| `tool_lantern_r3` | Lanterne de Faille III | 3 | `assets/icons/items/tools/tool_lantern_r3.png` |
| `tool_lantern_r4` | Lanterne de Faille IV | 4 | `assets/icons/items/tools/tool_lantern_r4.png` |
| `tool_lantern_r5` | Lanterne de Faille V | 5 | `assets/icons/items/tools/tool_lantern_r5.png` |

## 3. Harnais d'entrainement de familier (Eleveur)

Un petit harnais de cuir a boucle de metal, a la taille d'un familier ; cuir clair au I, plus orne au II, boucle lumineuse au III.

| Id | Nom FR | Chemin |
|---|---|---|
| `pet_harness_t1` | Harnais d'entraînement I | `assets/icons/items/consumables/pet/pet_harness_t1.png` |
| `pet_harness_t2` | Harnais d'entraînement II | `assets/icons/items/consumables/pet/pet_harness_t2.png` |
| `pet_harness_t3` | Harnais d'entraînement III | `assets/icons/items/consumables/pet/pet_harness_t3.png` |

**Total icones : 114.**

## 4. Sprites de points de recolte (carte)

Un jeu de sprites par TYPE et par RANG (6 types x 5 rangs = 30 jeux). Chaque jeu contient :

- **plein** : 1 image, le point pret a recolter ;
- **coup** : animation de 3 a 4 images jouee a chaque coup d'outil (secousse, eclats, feuilles ou eclaboussure) ;
- **epuise** : 1 image, le point vide en attente de reapparition (souche, roche nue, herbe rase, eau calme).

La rarete du point (rare, epique, legendaire) ne demande PAS de sprite par rarete : une lueur coloree commune posee par-dessus (bleu, violet, or), a produire une seule fois en 3 couleurs, animee en boucle lente (4 images).

Chemin propose : `assets/sprites/gather_nodes/<type>/<type>_r<rang>_<etat>.png` (etat = full, hit_0..hit_3, depleted) et `assets/sprites/gather_nodes/rarity_glow_<rarete>_0..3.png`.

| Type | Metier | Placement | Ce qu'on voit |
|---|---|---|---|
| `tree` | lumberjack | terre ferme | arbre vivant avec bois mort au pied et entaille de resine ; essence par rang : frene, chene, if, arbre de Souffle (feuillage bleute), arbre obscur (feuillage violet sombre). Epuise : l'arbre reste, sans bois mort ni resine. |
| `rock` | miner | terre ferme | rocher avec filon visible : fer (gris), argent, cuivre de Souffle, astral, metal de Faille ; quelques cristaux de sel. Epuise : roche nue fendue. |
| `sand_bank` | miner | rive (bord de l eau) | banc de sable au bord de l'eau, tache claire sur la rive ; quartz qui affleure aux rangs III-V. Toujours pose sur une rive : prevoir un bord d'eau dans le cadrage. Epuise : sable lisse. |
| `herb_patch` | herbalist | terre ferme | touffe d'herbes au sol, une espece par rang (Sauge de Havreden, Clair-de-pre, Veilleuse des marais qui luit, Feuille-de-Souffle, Cicatrice-verte qui pousse sur une cicatrice de Faille refermee). Epuise : herbe rase qui repousse. |
| `wild_bush` | herbalist | terre ferme | buisson sauvage : baies (I), champignons au pied (II), ruche sauvage dans les branches (III), racines apparentes (IV), Fleur de Faille (V). Epuise : buisson nu. |
| `fishing_spot` | fisher | rive (bord de l eau) | remous et bulles a la surface de l'eau, cadre depuis la rive ; plus de reflets et de poissons qui sautent avec le rang, lueur violette au V. Epuise : eau calme. Le coup = eclaboussure du flotteur. |

Total : 30 jeux (30 pleins, 30 animations de coup, 30 epuises) + 3 lueurs de rarete.

## 5. Animations du joueur (outils)

A produire pour chaque modele de personnage joueur, en **4 directions** (nord, sud, est, ouest ; ouest peut etre le miroir de l'est), en boucle pendant la barre d'extraction envoyee par le serveur (3 a 7,5 s) :

| Animation | Outil tenu | Images par direction | Boucle |
|---|---|---|---|
| `gather_axe` | Hache | 4 a 6 (lever, frapper, rebond) | oui |
| `gather_pickaxe` | Pioche | 4 a 6 (lever, frapper, rebond) | oui |
| `gather_sickle` | Faucille | 4 (pencher, couper, se relever) | oui |
| `gather_fish` | Canne a peche | 3 (lancer) + 2 (attente) + 3 (ferrer) | attente en boucle |

L'outil peut etre un calque separe, commun a toutes les classes, pour ne pas dessiner 4 outils x 5 rangs x chaque classe : un seul outil generique par type suffit a l'animation, le rang ne se voit que sur l'icone.

## Recapitulatif

- 114 icones d'objets (21 ressources, 60 intermediaires, 30 outils, 3 harnais).
- 30 jeux de sprites de points de recolte + 3 lueurs de rarete.
- 4 animations joueur x 4 directions.
- 0 icone pour les variantes de rarete.
