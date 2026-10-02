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
- **Progression de la carte (2026-10-02)**, à appliquer avec la nouvelle carte du bureau :
  - niv. 1-40 : ANIMAUX ;
  - niv. 45-55 : HUMAINS touchés par les failles (voleurs, brigands, hors-la-loi) ;
  - niv. ~55-60 : FANATIQUES qui ont perdu la raison, près de la Tour ;
  - niv. 60 : la TOUR D'ASHER ;
  - après 60 : les CRÉATURES (ni animaux ni humains : golems, squelettes, spectres, élémentaires,
    Faille, Vide, Abîme, Effroi, démons, archontes) et les animaux non normaux (hybrides, Corbeau
    Charognard…). Exceptions : donjons et failles.
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
- **Familiers : les HUMAINS ne peuvent pas être des familiers** (bandits, hors-la-loi, convertis,
  zélotes, Edric, chevaliers déchus, culte obscur, tribaux à confirmer). **Les humanoïdes non humains
  le peuvent** (gobelins, hommes-lézards…). À porter comme un drapeau « capturable » par espèce.
- Monstres mis de côté : on les réactive tous dès que leur sprite existe.
- **Débuffs de défense (2026-10-02)** : une attaque PHYSIQUE à courte recharge réduit l'ARMURE seule
  (ex. Coup de tête −10 % armure 4 s) ; une attaque MAGIQUE à courte recharge réduit la RÉSISTANCE
  MAGIQUE seule ; les deux à la fois seulement sur une compétence d'identité / élite à longue
  recharge (ex. Brise-Garde). Chaque monstre « prépare » ainsi un type de dégâts.
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

## Lot 3 — humanoïdes (62) : VALIDÉ le 2026-10-02

- Kits et archétypes du CSV validés. Boss (Edric, Inquisiteur, gobelins, bandits, cultiste) : gérés
  par le propriétaire, kits du CSV à titre de proposition.
- Renommer **Exécuteur Bandit → Homme de main** (c'est un tank).
- Fanatique de la Tour : son portrait (hache + bouclier) contredit sa fiche de lanceur → le passer
  en défensif (gardien proposé), à confirmer.
- Doublons (Voleur / Coupe-Bourse, Pillard / Bandit, archers) : conservés si leurs sprites diffèrent.
- Les 33 monstres mis de côté (tous `art_pending`, aucun portrait) seront réactivés quand leur sprite
  existera, après le niveau 60 pour les créatures corrompues.

## Lot 4 — le sud (74) : VALIDÉ le 2026-10-02

- Kits et archétypes du CSV validés.
- Toutes les créatures du lot passent après le niveau 60 (après la Tour d'Asher), y compris celles
  placées aujourd'hui entre 15 et 60 (golems, squelettes, Loup de Cristal, Chien de Braise, Cheval
  Cauchemar, Faille / Vide / Abyssaux 40-60…).
- Élémentaires séparés en deux espèces : cristal (Loup de Cristal, glace) et braise (Chien de Braise, feu).
- Doublons (Horreur / Traqueur d'Effroi, Pillard d'Os / Guerrier Maudit, les 3 colosses, Spectre du
  Vide / Moissonneur, Porteur de Silence / Briseur d'Hymne) : à trancher en créant les sprites ;
  fusionner réduit le travail PixelLab.
- Boss (Gardien de la Forêt, Champion Maudit, Gueule de l'Abîme, Souverain, Avatar, Héraut, Première
  Fissure) : au retour, avec le lore à jour.

## Revue terminée : les 4 lots (200 monstres) sont validés.
