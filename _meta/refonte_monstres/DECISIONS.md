# Décisions de la revue lot par lot (propriétaire)

Base : `kits_tous.csv`. Ce fichier fait foi quand il contredit le CSV.

## Règles générales (2026-10-02)

- Le niveau d'un monstre n'est pas fixe dans une aire : il est tiré dans la tranche de l'aire
  (ex. rats niv. 1 à 8 au début). Stats = stats de base de l'espèce × niveau d'apparition, et le
  kit suit aussi le niveau d'apparition (3e compétence à partir de 40).
- Un nom propre avec son propre sprite (« Molosse Corrompu », « Rat Corrompu »…) = sa propre espèce
  avec ses propres stats de base. Un affixe de stade (jeune, alpha, géant…) = même espèce.
- Ce système sert aussi à remplir la tour infinie et les zones de faille avec des monstres aléatoires.
- MAG : tous les monstres ont un MAG dans leurs stats de base V2 (fini le repli ATK ÷ 2).
- Tout ce qui n'est pas un animal « normal » (hybrides, créatures du lore) vit APRÈS le niveau 60,
  dans les zones « corrompues » — sauf dans les donjons et les failles.
- Boss terminés aujourd'hui : Égouts (Le Rongeur) et Tanière des loups. Tour d'Asher, doublons de
  boss : gérés par le propriétaire.
- PixelLab gère bien les humanoïdes et les quadrupèdes, pas les créatures à 8 pattes.
- **Sprite différent = monstre différent** (ex. Cerf et Cerf Gardien).
- **Une attaque à recharge courte (filler, attaque d'espèce, rôle de base) ne contrôle JAMAIS** :
  4 s de recharge + 2 s d'étourdissement = le joueur ne joue plus. Elle applique un débuff à la place
  (armure −, attaque −, dégâts infligés −, réduction de soin, DoT…). Les contrôles durs (étourdissement,
  peur, silence…) sont réservés aux compétences d'identité / ultimes à longue recharge. Corrigés :
  Coup de tête (étourdissement → armure −10 % 4 s) et Hurlement d'Effroi (peur → dégâts infligés
  −10 % 4 s), dans `new_skills.json`. Ralentissement, aveuglement et gel restent pour l'instant
  (le joueur continue d'agir) : à confirmer.
- Les coins de la carte sont plus ou moins infestés : des familles entières peuvent y vivre
  (ex. une famille de tortues dans un lac).

## Lot 1 — bêtes du départ (38) : VALIDÉ le 2026-10-02

- Kits et archétypes du CSV validés.
- **Araignées supprimées** (Petite Araignée, Reine Araignée, Reine Araignée des Cavernes) : une
  autre famille de monstres les remplacera (à créer avec PixelLab, humanoïde ou quadrupède).
- **Scarabée : une seule espèce, un seul sprite, au début.** Larve et Géant = stades du même
  scarabée. Scarabée de Poussière : doublon, à retirer (à confirmer au retour).
- **Corbeau Charognard → après le niveau 60** (4 pattes : un monstre du lore, pas un oiseau).
- Après le niveau 60 aussi (créatures non normales) : Hybride Sanglier-Loup, Traqueur de Poussière,
  Molosse Corrompu, Chacal de la Faille. Loup-Garou : à confirmer.
- Tanière des loups (Loup Alpha, 5 nouveaux loups) : à voir au retour.

## Lot 2 — autres bêtes (26) : VALIDÉ le 2026-10-02

- Kits et archétypes du CSV validés.
- Cerf Gardien conservé (sprite différent de la Biche et du Cerf).
- Tortue de Pierre conservée ; idée : créer la famille des tortues dans un lac.
- Coup de corne de la Chèvre : saignement conservé (ce n'est pas un contrôle).
- Les 4 créatures Faille / Vide mises de côté (Meute de la Faille, Chasseur du Vide, Béhémoth de la
  Faille, Matriarche Corrompue) : à réactiver après le niveau 60 dans les zones corrompues.
