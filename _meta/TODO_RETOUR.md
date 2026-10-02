# TODO au retour de vacances

Liste de TOUT ce qu'il reste à faire après le travail fait depuis la maison (octobre 2026).
Tenue à jour à chaque ajout. Le détail des décisions et des branches est dans
`_meta/VACANCES_2026-10.md`. Cocher au fur et à mesure.

Dernière mise à jour : 2026-10-02.

## 1. Intégration (dans cet ordre)

- [ ] Pousser le travail du PC du bureau (quêtes, leveling, histoire, carte, Tanière des loups, lore).
- [ ] Fusionner les branches `vac_*` de la data une par une, après relecture :
  - [ ] `vac_koro` — Koro tier 3 au niveau 60 + compétences de familier retirées des Koro
  - [ ] `vac_familiar-ultimate-cd` — ultimes de familier 30 s + incantation 2 s
  - [ ] `vac_star-curve` — courbe des étoiles lissée
  - [ ] `vac_balance-tools` — scripts d'analyse, tables, ces notes
- [ ] À chaque fusion data : conflit attendu sur `_meta/version.json` → `git add .` puis
      `python scripts/hash_content.py` puis `git add _meta/version.json` (voir CLAUDE.md).
- [ ] Back : compiler et tester chaque branche `vac_*` (jamais compilées, pas de compilateur à la maison) :
  - [ ] `vac_familiar-xp-90` — ctest combat + familiar
  - [ ] `vac_poison-cap` — `combat-tests --gtest_filter="*Poison*"`
  - [ ] `vac_koro-shield-rank` — `combat-tests --gtest_filter="*Koro*"`
- [ ] Mettre à jour le pin de la data (`kanarion-meta`) dans le back et le client après fusion.

## 2. Tanière des loups (5 nouveaux loups, non poussés)

- [ ] Les intégrer au modèle V2 : pour chacun, espèce (`loup` ou nouvelle), stade (préfixe),
      archétype parmi les 11, et kit selon la règle (voir `VACANCES_2026-10.md`).
- [ ] Les ajouter à `SPECIES` dans `scripts/balance/species_table.py` et relancer les scripts
      `monster_review.py` puis `species_table.py`.
- [ ] Vérifier que Crocmarque (`boss_fangmark_den`) et le Loup Alpha restent cohérents avec eux.

## 3. Décisions à confirmer

- [ ] **Tribaux : humains (non capturables) ou non ?** À trancher en regardant les sprites. Vu dans le
      dépôt client : Brute Tribale = créature massive et velue à massue (ogre / troll ?) ; Seigneur de
      guerre tribal = coiffe de plumes + bouclier (humain ou orc ?). Pas de portrait dans le dépôt pour
      Sorcière Tribale, Chasseur Tribal, Chef de Guerre Tribal.
- [ ] Fanatique de la Tour (portrait hache + bouclier, fiche de lanceur) : gardien proposé.

- [ ] L'interrupteur `MONSTER_SCALING_MODEL` est-il activé en production ? (absent des dépôts)
- [ ] Joueurs qui possèdent déjà une carte Koro de familier : rembourser, convertir, ou laisser ?
- [ ] XP des familiers 90 % : valider en jeu sur un personnage neuf.
- [ ] Étoiles : relancer le harness de taux de victoire du 2026-09-29 (solo / groupe de 3 / groupe
      de 6) — 5 étoiles doit demander un groupe optimisé du même niveau.
- [ ] Invocateur : nombre de monstres temporaires, durée, compte ou non dans la limite de 10.
- [ ] Alternative horizontale au Paragon (le Paragon est vertical).

## 4. Serveur (back) — travail à faire

- [ ] Modèle V2 des monstres : lire les stats d'ESPÈCE (base niv. 1) au lieu du seul archétype.
- [ ] 11 archétypes dans `monster_scaling_model` (gardien, berserker, soigneur, invocateur,
      enchanteur + archer/mage séparés).
- [ ] Lire `tenacity` et `shield_pierce` dans les `base_stats` des monstres (aujourd'hui seulement via l'archétype).
- [ ] Croissance des stats d'identité par archétype tous les 10 niveaux (plafonnées).
- [ ] Familiers : stats héritées de l'identité de l'espèce ; passif d'espèce qui monte en puissance
      (par ex. aux niveaux 20 / 50 / 100).
- [ ] Familiers : 21 des 31 passifs sans effet en combat ; compétences sans montée par niveau.
- [ ] Keystones `ks_support_harmony_*` : boucliers / soins de groupe sans plafond (recharge 0).
- [ ] Test `test_player_reference_curve.cpp` : n'applique jamais les passifs communs (clé `passives`
      au lieu de `common_passives`).
- [ ] Érosion (optionnel) : mécanique anti-soin qui réduit les PV max pendant le combat.
- [ ] IA des monstres : elle ignore toute compétence de déplacement (`kit_behavior.cpp:435`), donc
      ni la téléportation de l'assassin (Saut de l'Ombre) ni `skill_mob_assassin_shadow_strike` ne
      sont jamais lancées. À brancher.
- [ ] Invocations : ajouter une durée de vie et une option « apparaît près de l'invocateur »
      (aujourd'hui permanentes, près de la ligne arrière des joueurs, un seul type par compétence).
- [ ] Un effet qui RETIRE les boucliers (la dissipation retire le premier buff trouvé).
- [ ] MAG absente d'une fiche monstre → le chargeur prend ATK/2 : soins et sorts de nombreux
      lanceurs/soigneurs à moitié de puissance. Corriger côté data (voir section 5) ; décider si
      le repli serveur doit rester.
- [ ] `target_rule` n'est pas lu (le serveur lit `target`, `content_loader.cpp:728`) :
      `skill_mob_assassin_shadow_strike` mettrait l'invisibilité sur l'ennemi.
- [ ] `base_monster` (fiches de boss) n'est lu nulle part dans le back.

## 5. Data — travail à faire

- [ ] Appliquer les décisions de la revue lot par lot : `_meta/refonte_monstres/DECISIONS.md`.
- [ ] Supprimer les araignées (`mob_spider_small`, `mob_spider_queen`, `boss_spider_queen`) et leurs
      placements ; retirer le Scarabée de Poussière (doublon) ; Larve et Géant = stades du scarabée.
- [ ] Remplacer dans `skills/monster_skills.json` les compétences de `new_skills.json` →
      `modified_existing` (Coup de tête : étourdissement → armure −10 %).
- [ ] Renommer `mob_bandit_enforcer` « Exécuteur Bandit » → « Homme de main » (FR + EN).
- [ ] Drapeau « capturable en familier » par espèce : NON pour les humains (bandits, hors-la-loi,
      convertis, zélotes, Edric, chevaliers déchus, culte obscur ; tribaux ?), OUI pour les humanoïdes
      non humains (gobelins, hommes-lézards…) et les bêtes.
- [ ] Réactiver chaque monstre mis de côté dès que son sprite existe ; Meute de la Faille, Chasseur du Vide,
      Béhémoth de la Faille, Matriarche Corrompue.
- [ ] Vérifier toutes les autres compétences à recharge courte des monstres : aucun contrôle dur.
- [ ] Déplacer après le niveau 60 (zones corrompues) les créatures non normales : Corbeau Charognard,
      Hybride Sanglier-Loup, Traqueur de Poussière, Molosse Corrompu, Chacal de la Faille (+ Loup-Garou ?).

- [ ] Appliquer la refonte des monstres à `entities/monsters.json` : archétype, espèce, stade, kit
      (tableaux dans `scripts/balance/out/`), après relecture.
- [ ] Écrire les profils des 4 nouveaux archétypes dans `config/monster_scaling_model.json`.
- [ ] Relire les kits des 200 monstres : `_meta/refonte_monstres/kits_tous.csv` (archétype final,
      kit, raisons, anomalies de stats et de compétences) + les 4 rapports `kits_*.md`.
- [ ] Ajouter les 24 nouvelles compétences (`_meta/refonte_monstres/new_skills.json`, rapport
      `new_skills_report.md`) dans les VRAIS blocs lus par le serveur : `basic_skills`,
      `role_basic_skills.<rôle>`, `archetype_skills.<arch>.pool` (`content_loader.cpp:274-311`).
- [ ] Doublon : `skill_mob_enchanteur_renfort` ≈ `skill_mob_support_bolster`, n'en garder qu'un.
- [ ] `skill_mob_support_shield_barrier` : bouclier fixe de 100 (le `scaling: mag` est ignoré,
      `room.cpp:5490`) → passer en `shield_mag` avec un pourcentage.
- [ ] Compétences encore à concevoir (demandées par les relecteurs) :
  - [ ] identités d'archétype à ≥ 20 s pour berserker, soigneur (purification de groupe), archer ;
        plus de variété pour les mages (10 partagent Nova de Givre ; Boule de Feu est à 18 s)
  - [ ] mécaniques de phase des boss de niveau ≥ 40 (5 boss du sud + Seigneur Cultiste niv. 48) ;
        le Héraut et la Première Fissure ont aujourd'hui le même kit
  - [ ] araignée : identité « Toile » (enracinement en zone) et ultime « Cocon »
  - [ ] attaque d'espèce avec étourdissement court pour sanglier / bovin / ovin (`headbutt` en attendant)
  - [ ] « Crachat » à distance pour les batraciens, « Fiole pestilente » (Docteur Pestilent),
        « Ruade » (cheval, facultatif), « Pinces » (scorpion, cosmétique)
  - [ ] variantes À DISTANCE des attaques d'espèce pour les archers et lanceurs (portée 2 aujourd'hui)
  - [ ] effet d'espèce pour archonte_dechu, elementaire, esprit_sylvestre
- [ ] Décider : la compétence d'identité suit-elle le niveau d'APPARITION (≥ 40) ou le niveau de
      base ? (rats du nid corrompu 40-50, Molosse jusqu'à 100, Renard Brumeux jusqu'à 58…)
- [ ] Ajouter `mag` aux lanceurs et soigneurs qui n'en ont pas (Biche, Brebis, Grenouille
      Soigneuse, Cerf Gardien, Crapaud Cracheur, Rat Sorcier, rats/louve/hyène soigneurs, Chien de
      Braise, Golem Runique, Nécromancien, Ancien Converti, Shaman Lézard, Prêtre Obscur, Ritualiste
      Zélote…), et MAG > ATK pour les lanceurs.
- [ ] Doublons à trancher : `mob_edric_warlord` / `boss_edric_tower`, `mob_bandit_warlord` /
      `boss_bandit_warlord`, deux donjons « Tour d'Asher » (`dungeon_asher_tower` et
      `dungeon_tower_asher`), deux Reines Araignées (le boss n'a pas de donjon), Cerf Gardien / Biche,
      Voleur / Coupe-Bourse, Pillard / Bandit, Horreur / Traqueur d'Effroi, Faucheur / Moissonneur
      d'Âmes, Gueule de la Faille / Gueule de l'Abîme.
- [ ] Fiches incohérentes : Gardien de la Forêt (copie du loup corrompu : Morsure, tags de bête,
      butin `wolf_corrupted`), Archonte Courroucé (nom de berserker, kit de mage), Tatou et
      Grenouille Cornue (stats identiques, 65 d'armure pour une grenouille), Rat du tutoriel (stats
      ≠ sa `_note`), Loup Alpha (boss non placé, 395 PV), boss gobelins niveau 10-12 pour des troupes
      niveau 20-23, élites moins solides que des tough (Vache, Gardien de la Cloche, Démon Majeur,
      Le Défait, Gardien du Trône), boss finaux moins solides que la Gueule de l'Abîme (le modèle V2
      règle les PV par la courbe).
- [ ] Identifiants trompeurs : `mob_goblin_witch`, `mob_bandit_hunter`, `mob_bandit_warchief` sont des
      tribaux ; `mob_goblin_warior` (faute). Renommer = migration (bases de données, butin, quêtes).
- [ ] Catégories : Tortue de Pierre `elemental` (rangée en tortue), Reines Araignées `humanoid`.
- [ ] Nettoyer les fiches : clés `mr` et `spd` (une fois chacune), `magic_resist` manquant (1 monstre),
      stats aberrantes du Chien sauvage et du Culte obscur.
- [ ] 59 monstres actifs ne sont placés nulle part (zones, donjons, tour) : vérifier s'ils viennent
      de quêtes / événements, sinon les passer en `shelved` ou les placer. Confirmés non placés par
      les relecteurs : Tortue, Tatou, Cheval, Cerf Obscur, Cerf Gardien, Traqueur de Poussière,
      Chacal de la Faille, Loup Alpha, boss gobelins.
- [ ] Placements à comparer avec la NOUVELLE carte du bureau : Renard Brumeux (niv. 33) en
      expédition 1-10 et étage 1 du Repaire, Petite Araignée (niv. 10) en zone 25-30, Charognard
      (niv. 27) en zone 9-20, boss Gueule de l'Abîme aussi monstre de zone 60-70 / 85-100.
- [ ] Familiers : table espèce de familier (65) → espèce de monstre (45).
- [ ] Descriptions : cartes Koro (le bouclier suit le rang), poison (plafonné sur les monstres),
      boucliers `shield_def` (décrits en % PV max, calculés sur la DEF).
- [ ] `entities/boss_mechanics.json` n'est lu par aucun serveur : supprimer ou brancher.
- [ ] Pré-existant : `validate_skills.py` (129 erreurs de liste blanche), `gen_pet_books.py --check`
      (descriptions périmées).

## 6. Assets (PixelLab, icônes)

- [ ] **Sprites des 33 monstres mis de côté** (tous `art_pending`, aucun portrait), à créer pour
      pouvoir les réactiver :
      - `mob_rift_pack` Meute de la Faille (niv. 51)
      - `mob_void_wraith` Spectre du Vide (niv. 51)
      - `mob_fallen_zealot` Zélote Déchu (niv. 52)
      - `mob_void_hunter` Chasseur du Vide (niv. 53)
      - `mob_abyssal_brute` Brute Abyssale (niv. 53)
      - `mob_riftstone_colossus` Colosse de Pierre-Faille (niv. 54)
      - `mob_corrupted_cleric` Clerc Corrompu (niv. 55)
      - `mob_nightmare_weaver` Tisseur de Cauchemars (niv. 55)
      - `mob_greater_demon` Démon Majeur (niv. 56)
      - `mob_soul_reaver` Faucheur d'Âmes (niv. 57)
      - `mob_imitator_echo` Écho de l'Imitateur (niv. 58)
      - `mob_rift_behemoth` Behemoth de la Faille (niv. 58)
      - `mob_corrupted_matriarch` Matriarche Corrompue (niv. 59)
      - `mob_avatar_of_the_rift` Avatar de la Faille (niv. 60)
      - `mob_broken_cherub` Chérubin Brisé (niv. 81)
      - `mob_fallen_watcher` Veilleur Déchu (niv. 81)
      - `mob_tarnished_guardian` Gardien Terni (niv. 82)
      - `mob_corrupted_seraph` Séraphin Corrompu (niv. 83)
      - `mob_hymn_breaker` Briseur d'Hymne (niv. 85)
      - `mob_fallen_valkyr` Valkyr Déchue (niv. 86)
      - `mob_light_eater` Mangeur de Lumière (niv. 87)
      - `mob_choir_of_ruin` Chœur de Ruine (niv. 88)
      - `mob_herald_of_the_fissure` Héraut de la Fissure (niv. 90)
      - `mob_shard_of_severance` Éclat de Rupture (niv. 91)
      - `mob_severance_priest` Prêtre de la Rupture (niv. 92)
      - `mob_first_fallen` Premier Déchu (niv. 93)
      - `mob_void_archangel` Archange du Vide (niv. 94)
      - `mob_silence_bringer` Porteur de Silence (niv. 95)
      - `mob_ruin_colossus` Colosse de Ruine (niv. 96)
      - `mob_the_unmade` Le Défait (niv. 97)
      - `mob_apostle_of_severance` Apôtre de la Rupture (niv. 98)
      - `mob_warden_of_the_throne` Gardien du Trône (niv. 99)
      - `mob_the_first_fissure` La Première Fissure (niv. 100)
- [ ] Famille des tortues (dans un lac) autour de la Tortue de Pierre.
- [ ] Nouvelle famille de monstres pour remplacer les araignées (supprimées : PixelLab ne gère
      pas bien les 8 pattes) — humanoïde ou quadrupède.

- [ ] Seuls 158 portraits de monstres sont dans le dépôt client (le reste est synchronisé sur le
      serveur) : vérifier qu'aucun monstre actif n'en manque.
- [ ] Portraits non trouvés pour la revue : `mob_zealot_acolyte`, `mob_goblin_witch`,
      `mob_abyssal_scholar`, `mob_edric_chosen_guard`, `mob_nether_caller`, `mob_hollow_sentinel`,
      `mob_golem_sentinel`, `mob_rift_warden`, `mob_throne_sentinel`, `mob_grieving_sentinel`,
      `boss_forest_guardian`, `mob_abyssal_juggernaut`, `mob_edric_chosen_ritualist`.
- [ ] Aucun portrait dans le dépôt client pour les monstres abyssaux, du Vide et d'Effroi (à vérifier
      sur le serveur).
- [ ] Portraits qui ne collent pas à la fiche : Fanatique de la Tour (guerrier hache + bouclier, fiche
      de lanceur), Hyène Alpha (ressemble à un loup).
- [ ] Monstres temporaires de l'invocateur : sprites à créer (aujourd'hui le Rejeton du Vide sert d'invocation).
- [ ] Icônes des 24 nouvelles compétences de monstres (`_meta/refonte_monstres/new_skills.json`) :
  - identité : Égide, Bastion, Brise-Garde, Saut de l'Ombre, Malédiction, Appel du Néant, Hymne de Guerre
  - rôle : Coup de bouclier (gardien), Trait (invocateur), Renfort (enchanteur, si gardé)
  - espèce : morsure infectieuse (rat), morsure venimeuse (serpent), dard et toile (araignée),
    déchirure (loup), mâchoire putride (hyène), écrasement (golem/tortue/tatou), coup de bec
    aveuglant (corbeau), taillade (squelette), toucher glacé (spectre), griffe ardente (démon),
    frappe du vide, frappe maudite (abyssal), hurlement d'effroi, déchirure de faille
- [ ] Icônes des compétences encore à concevoir (section 5).
- [ ] Nouveaux monstres pour les archétypes peu fournis (1 seul invocateur aujourd'hui).

## 7. Discussions ouvertes (design)

- [ ] Idées de contenu PvE à proposer (déjà en jeu : coffres, failles, tour infinie ; idée : pages
      de livre à collectionner qui racontent des histoires).
- [ ] Le lore du dépôt `kanarion_lore` sur GitHub date d'avril : pousser la version du bureau.
