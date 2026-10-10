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
  - [ ] `vac_familiar-species` — CONTIENT `vac_apply-monster-v2` (branche data la plus complète). Familiers
        par espèce + passifs d'espèce, `scripts/apply_familiar_species.py` (commit généré `53ad968` à jeter
        et relancer au retour, APRÈS `apply_monster_v2.py`).
  - [ ] `vac_apply-monster-v2` — contient `vac_balance-tools` + `vac_archetype-profiles` + le script
        `scripts/apply_monster_v2.py` + son résultat (commit `a0cab4b`, GÉNÉRÉ). Au retour : fusionner
        le travail du bureau (Tanière des loups…), ajouter les nouveaux monstres à `kits_tous.csv`
        (espèce, stade, archétype, kit), JETER le commit généré et relancer
        `python scripts/apply_monster_v2.py` puis `--check`. Monter `database_version` (règle CI).
  - [ ] `vac_archetype-profiles` — les 11 profils d'archétypes V2 (`config/monster_scaling_model.json`) ;
        lancer `ctest` (tests `test_monster_scaling_model.cpp` / `test_monster_balance_rules.cpp`)
- [ ] À chaque fusion data : conflit attendu sur `_meta/version.json` → `git add .` puis
      `python scripts/hash_content.py` puis `git add _meta/version.json` (voir CLAUDE.md).
- [x] **Back compilé et testé dans WSL le 2026-10-03** (toutes les branches `vac_*` fusionnées ensemble,
      data `vac_familiar-species` + `vac_koro` + `vac_familiar-ultimate-cd` + `vac_star-curve`) :
      familiers 48/48, présence 100/100, combat **2 118 / 2 126** (2 ignorés).
      - 3 tests mis à jour pour les nouvelles règles : `e3844780` et `09e5cd4e` (sur `vac_v2-monster-model`),
        `011c1801` (nouvelle branche `vac_koro-catalog-test`) ; nouveau test `FamiliarPassiveStats.*` vert.
      - **6 échecs DÉJÀ PRÉSENTS SUR `main`** (vérifié sans aucune branche vac_, data master ET data épinglée) :
        `MageMatrixTest.ShieldRatiosAndRemainingBreathCondition` — **CORRIGÉ** sur la nouvelle branche back
        `vac_spell-guard-fix` (`07976d70`) : depuis `74606ec2` (keystones) les sorts instantanés paient avant
        leurs effets, mais `caster_above_mp` retirait encore le coût (compté deux fois) ; testé dans WSL, 48/48
        tests mage / conditionnels verts. Et `ArcherMatrixTest.HeadshotCriticalResistanceAndKillReset`
        (critique malgré 100 de résistance aux critiques), 3 rangs : **décidé : critique absolu** (2026-10-03).
        Description corrigée (data `vac_collections`), test aligné sur la branche back `vac_headshot-absolute-crit`.
- [ ] Back : relire chaque branche `vac_*` avant fusion (compilées et testées ensemble, voir au-dessus) :
  - [ ] `vac_familiar-xp-90` — ctest combat + familiar
  - [ ] `vac_poison-cap` — `combat-tests --gtest_filter="*Poison*"`
  - [ ] `vac_koro-shield-rank` — `combat-tests --gtest_filter="*Koro*"`
  - [ ] `vac_familiar-species-passive` — suite unitaire du service familier (`LoadoutRollerTest.*`)
  - [ ] `vac_v2-monster-model` (contient `vac_v2-monster-mag`) — `ctest` complet : MAG séparée, espèces + stades,
        croissance des taux, ténacité / perce-bouclier, IA de téléportation, invocations temporaires,
        `shield_shatter`. Puis activer `MONSTER_SCALING_MODEL=1` sur un serveur de test avec la data V2.
  - [ ] `vac_defense-curve-test` — `ctest -R MonsterScaling` avec la data `vac_archetype-profiles`
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

- [x] Modèle V2 des monstres : espèces + stades (`vac_v2-monster-model`, à compiler).
- [ ] 11 archétypes dans `monster_scaling_model` (gardien, berserker, soigneur, invocateur,
      enchanteur + archer/mage séparés).
- [x] `tenacity` et `shield_pierce` lus dans les `base_stats` (`vac_v2-monster-model`).
- [x] Croissance des stats d'identité par archétype tous les 10 niveaux (`vac_v2-monster-model`).
- [x] Familiers : stats héritées de l'identité d'espèce (data `vac_familiar-species`) ; passif d'espèce
      aux niveaux 1 / 20 / 50 / 100 (data + serveur `vac_familiar-species-passive`).
- [ ] **À décider** : le rat de départ (Colette) hérite de l'identité frêle du rat (PV x0,6, ATK x0,8) :
      garder, ou exempter les familiers de départ ?
- [ ] Les passifs d'espèce ne touchent que PV / Souffle / ATK / MAG / armure / RM (seules stats
      appliquées aux familiers en combat) : pour esquive, blocage, ténacité… il faudra du code combat.
- [ ] Familiers : 21 des 31 passifs sans effet en combat ; compétences sans montée par niveau.
- [ ] Keystones `ks_support_harmony_*` : boucliers / soins de groupe sans plafond (recharge 0).
- [ ] Test `test_player_reference_curve.cpp` : n'applique jamais les passifs communs (clé `passives`
      au lieu de `common_passives`).
- [ ] Érosion (optionnel) : mécanique anti-soin qui réduit les PV max pendant le combat.
- [x] IA : téléportation hostile (TELEPORT_ADJACENT) autorisée (`vac_v2-monster-model` 4f2ba397) ; Saut de
      l'Ombre est une vraie téléportation, INSTANTANÉE (le chemin « incantation puis déplacement »
      n'est pas testé côté serveur : à vérifier avant de donner un temps d'incantation à un déplacement).
- [ ] (ancien) IA des monstres : elle ignorait toute compétence de déplacement (`kit_behavior.cpp:435`), donc
      ni la téléportation de l'assassin (Saut de l'Ombre) ni `skill_mob_assassin_shadow_strike` ne
      sont jamais lancées. À brancher.
- [x] Invocations temporaires (`lifetime`, `placement: near_caster`, `vac_v2-monster-model` 87ddfdef) ;
      Appel du Néant : 15 s à côté de l'invocateur. Une expiration ne rapporte ni XP ni butin.
- [ ] (ancien) Invocations : ajouter une durée de vie et une option « apparaît près de l'invocateur »
      (aujourd'hui permanentes, près de la ligne arrière des joueurs, un seul type par compétence).
- [x] Effet `shield_shatter` qui détruit tous les boucliers (`vac_v2-monster-model` 62ed0472), utilisé par Brise-Garde.
- [ ] Vérifier en jeu que l'IA lance bien Brise-Garde sur une cible protégée (le scoreur ne valorise pas
      encore explicitement la destruction de bouclier).
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

- [x] Script d'application écrit et lancé (`vac_apply-monster-v2`) : archétypes, rôles d'IA, espèces,
      stades, kits, MAG des archétypes magiques, 24 nouvelles compétences, Coup de tête sans
      étourdissement, araignées et Scarabée de Poussière mis de côté, Homme de main renommé,
      nouveau fichier `entities/monster_species.json`.
- [ ] Vérifier en jeu que l'IA du rôle `tank` (utilisée par les gardiens) lance bien les compétences
      d'alliés (Égide, Bastion) ; sinon un rôle d'IA dédié.
- [x] Profils des 11 archétypes écrits (branche `vac_archetype-profiles`).
- [x] **BLOQUANT avant d'activer les profils V2** (fait sur `vac_v2-monster-mag`, à compiler) : le serveur doit lire `mag` pour `magic_power`
      (`room_manager.cpp` met aujourd'hui `magic_power = atk`). Les archétypes magiques ont ATK 2 :
      sans ce changement ils lanceraient à 2 de puissance.
- [ ] Serveur : lire aussi `parry_chance`,
      `lifesteal`, `reflect`, et `rate_growth_per_10_levels` du modèle.
- [ ] Retirer l'alias `support` quand plus aucun monstre ne pointe dessus (et adapter
      `test_monster_balance_rules.cpp` qui le cite).
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
- [ ] **Replacer les monstres selon la progression décidée** (voir `DECISIONS.md`) : animaux 1-40,
      humains touchés par les failles 45-55, fanatiques ~55-60 près de la Tour, Tour d'Asher 60,
      créatures après 60 (golems, squelettes, spectres, élémentaires, Faille, Vide, Abîme, Effroi,
      démons, archontes, hybrides).
- [ ] Séparer l'espèce `elementaire` en `cristal` (Loup de Cristal) et `braise` (Chien de Braise).
- [ ] Placements à comparer avec la NOUVELLE carte du bureau : Renard Brumeux (niv. 33) en
      expédition 1-10 et étage 1 du Repaire, Petite Araignée (niv. 10) en zone 25-30, Charognard
      (niv. 27) en zone 9-20, boss Gueule de l'Abîme aussi monstre de zone 60-70 / 85-100.
- [x] Familiers : table espèce de familier (65) → espèce de monstre (`FAMILIAR_TO_MONSTER` dans
      `scripts/apply_familiar_species.py`, champ `monster_species` dans familiars.json).
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

- [ ] **Afficher ces informations EN JEU**, sinon les joueurs ne les découvriront jamais : stats de
      base et identité de l'espèce (PV / ATK / armure / RM), passif d'espèce et ses paliers 1 / 20 / 50 /
      100, effet de la rareté, archétype du monstre (bestiaire, fiche de capture, panneau Colette).
- [x] **Rareté des familiers** (VALIDÉ et appliqué 2026-10-02, `config/familiar_balance.json`) : multiplicateurs actuels commun 1.0 /
      peu commun 1.06 / rare 1.12 / épique 1.2 / légendaire 1.3 → proposé 1.0 / 1.07 / 1.15 / 1.3 / 1.5.
      Avec 1.5, un rat légendaire tank ≈ 70 % des PV et 80 % de l'armure d'un golem commun : l'espèce
      compte plus que la rareté pour le rôle, la rareté récompense la chasse (drop légendaire 0,2 % : pas de capture, une fois l'empreinte droppée le familier est obtenu).
- [ ] **Passifs SPÉCIAUX de familier à préparer** (déclencheurs, ce qui rendra certains familiers ultra
      recherchés) : ex. « quand il est soigné, pose un soin sur la durée sur un allié proche », « quand
      il bloque, renvoie… », « à la mort d'un ennemi… ». Aujourd'hui le serveur n'implémente que 3
      passifs spéciaux (poison, saignement, silence, `familiar_passive_processor.cpp`) et 21 des 31
      passifs sont sans effet : concevoir les déclencheurs (on_healed, on_hit, on_block, on_kill,
      on_low_hp…) puis les coder.

- [ ] **Alpha / playtests** : aucun joueur niveau 100 et aucune stat de dégâts réelle aujourd'hui ;
      monter niveau 100 est long → prévoir une alpha (et des sessions de playtest payées) pour
      calibrer. Règle : mieux vaut trop dur que trop facile.
- [ ] Avec la défense raide (x25 au niv. 100), donner de la valeur à la PÉNÉTRATION : l'équipement
      ne donne que 1 à 5 % aujourd'hui → revoir les valeurs de pénétration (substats d'arme, passifs,
      keystones, Koro).
- [ ] Compétences de SUPPORT OFFENSIF : buffs de pénétration pour le groupe, débuffs de défense ;
      valoriser les supports offensifs et les débuffeurs.
- [ ] Consommables de buff (pénétration, dégâts…) dans l'économie / les métiers.

- [ ] Créer les monstres finaux du jeu à partir du lore À JOUR (pousser le lore du bureau d'abord) ;
      boss du sud : Gardien de la Forêt, Champion Maudit, Gueule de l'Abîme, Souverain, Avatar, Héraut,
      Première Fissure.

- [ ] **Familiers : livres de passif et de déplacement, passifs liés au maître** — document de conception
      `_meta/conception_familiers/LIVRES_DEPLACEMENTS_PASSIFS.md` (branche data `vac_familiar-books`),
      5 questions sur 6 tranchées (reste : légendaires qui ont déjà 2 passifs). Koro passe aussi à 80-150 %. Décidé : passifs = mêmes règles que les
      compétences (rangs C → SS, livre, hors rôle ×0,67) ; déplacements par archétype / par rôle.
- [ ] Back `vac_familiar-passives-combat` (`4d6a4a46`) : lot 1 des passifs de familier en combat (8 passifs
      de stats). Compiler et lancer `combat-tests --gtest_filter="FamiliarPassiveStats.*"`. Lots 2 et 3 à faire.
- [ ] **Boutique / financement** : à discuter (tous les visuels sont des assets IA temporaires ; il faut
      des revenus pour payer un artiste pour les skins de joueur et de familier). Éviter de vendre de la
      puissance brute.
- [ ] **Contenu horizontal : les COLLECTIONS** (à discuter cette semaine, 2026-10-02). Base : ~10 livres
      de X pages qui racontent l'histoire du monde, avec le VRAI texte du lore (le propriétaire pense l'avoir
      déjà, au bureau) — jamais de pages vides. Autres idées proposées et appréciées :
      - bestiaire (fiche par espèce = aussi l'affichage des infos en jeu) ;
      - album des familiers (chaque espèce x chaque rareté) ;
      - recueil des murmures (`world/whispers.json`) ;
      - cartographie (lieux remarquables par région) ;
      - reliques de la Faille (objets uniques des failles refermées, vitrine) ;
      - trophées de chasse (boss, monstres « champion », groupes 5 étoiles) ;
      - herbier / atlas des métiers (chaque ressource récoltée ou fabriquée) ;
      - album des Koro.
      Récompenses horizontales : titres, cosmétiques, emotes, éventuellement petit bonus de compte (+1 % de drop).
      Pages des livres (décidé 2026-10-03) : combats des événements de fissure, coffres, faible taux dans
      les groupes 5 étoiles, certaines récompenses de quête ; échangeables (HDV et échange direct).
- [ ] Collections : document de conception `_meta/conception_collections/COLLECTIONS.md` (branche data
      `vac_collections`) : 10 livres / ~70 pages tirés du VRAI lore, 6 contradictions de lore à trancher
      avec le lore du bureau, autres collections classées par effort, 5 questions ouvertes.
- [ ] Quêtes : prévoir des quêtes liées au lore AVEC DES CHOIX pour le joueur (rappel du propriétaire).
- [ ] **Histoires et Accusateur** : proposition `_meta/conception_histoires/HISTOIRES_ET_ACCUSATEUR.md`
      (branche data `vac_collections`) — Fissures = portes ouvertes par les œuvres de la chair, plan du Malin =
      l'Accusateur (VALIDÉ), structure quête principale + suites secondaires, X à chaque moment clé, paires
      d'histoires en miroir par niveau, 5 fiches (Dorn, Harlan, chasseuse et soigneuse, Lisa, Bastien). À FUSIONNER
      avec le lore et les quêtes du bureau. Carte décidée : Havreden 1-20, route du sud 20-50, Rochebourg 50+,
      Tour d'Asher 60+ (le lore d'avril la faisait tomber au niveau 20 : à recaler), ville en guerre tout en bas.
      Compteurs cachés : compassion / rancune.
- [ ] **Technique quêtes** : PNJ visibles ou non selon l'avancement de chaque joueur (phasing par joueur),
      nécessaire pour les histoires à choix (ex. un des frères Dorn disparaît). Vérifier client + serveur.
- [ ] **Monstres agressifs selon le niveau** : un monstre ≥ 10 niveaux au-dessus du joueur l'attaque de lui-même
      (même accompagné d'un joueur de haut niveau), pour qu'on ne se balade pas partout sans crainte. Vérifier ce que
      le monde ouvert (presence) fait aujourd'hui.
- [ ] **Boss à dialogues** : seuils de dialogue configurables (ex. tous les 20 % de PV) pour les boss
      d'histoire (Harlan). Aujourd'hui : phases fixes à 50 % et 20 %.
- [ ] **Panthéon** (idée du propriétaire) : les premiers du serveur (niveau 100, par classe, par métier,
      familier niveau 100, donjons, Tour, collections, histoire…), titres exclusifs. Voir `_meta/carnet/pantheon.md`.
- [ ] **Quêtes, briques** (`_meta/carnet/formats_quetes.md`) : (1) le CHOIX et (2) les drapeaux + conditions
      sont **codés côté serveur** (branche back `vac_quest-moral-choices`, migration 111 — la renuméroter si le
      bureau a déjà une 111) ; reste le CLIENT (boutons de choix, PNJ visibles selon les drapeaux, constructeurs
      GDScript du protocole : turn-in champ 3, état champs 7-9) et la réécriture des 6 choix existants
      (`severite` ≠ `rancune`) ; (3) `deliver_item` ; (4) `complete_scenario` (instance scénarisée) ;
      (5) `take_part_in_event`.
- [ ] **Équipement** (`_meta/carnet/equipement.md`) : 5 décisions validées, codées ET TESTÉES dans WSL sur `vac_equipment`
      (data + back) + `vac_craft-rolls` (back, artisanat : bibliothèque `kanarion-loot` partagée combat / économie)
      — loot 39/39, forge 17/17, artisanat 12/12. À relire, puis recaler `test_player_reference_curve.cpp` (base d'objet,
      affixes, forge, sets) et la calibration des monstres. Supprimer `upgrade_system` / `substat_upgrade_chance`
      de `equipment_stats.json` après avoir vérifié que le client ne les lit pas.
- [ ] Grille : passer au moins en 12×6 plus tard (tutoriel en 10×6) → grille par mode (`combat_grids.by_mode`),
      zoom caméra par grille côté client, fonds peints, portées archer/mage. Voir `_meta/carnet/deplacements_combat.md`.
- [ ] **Bug signalé par le propriétaire** : dans le donjon des rats, les Rats Sorciers touchent sans ligne de vue et à
      portée « infinie » (sorts `skill_mob_artillery_bolt` / `fire_bolt` : portée 7, sans ligne de vue). **CORRIGÉ** :
      cause = la DATA (les projectiles ignoraient la ligne de vue) ; data `c5d0230` (8 projectiles exigent la ligne de
      vue) + `b0e9a37` (entrave, silence, éclair : ligne de vue ; projectiles 7 → 5) ; back `vac_ai-los-range`
      (repère de ligne de vue de l'IA joueur, cibles valides seulement pour le coordinateur de groupe). Suite combat
      complète avec toutes les branches vac_ : 2 135 / 2 137, 2 ignorés, 0 échec.
- [ ] `scripts/validate_skills.py` échoue déjà sur master (129 erreurs) : champs de sorts de familier
      (`icon`, `off_role_exempt`…) absents de la liste blanche du validateur. À ajouter à la liste blanche.
- [ ] Bug IA (existant) : `server-combat/src/ai/player_ai.cpp:637-646`, la ligne de vue de l'IA joueur utilise
      l'ancien repère (« front = y==0 »), faux sur le plateau unifié.
- [ ] **Réapparition des monstres** (pas encore traitée) : rapide en zone de farm, lente pour les gros monstres,
      élites et boss ; ne pas laisser les joueurs avancés vider les zones des débutants. Voir `_meta/carnet/monstres.md`.
- [ ] **Rythme du loot** : régler le loot pour qu'on ne soit pas équipé trop vite, idem pour les ressources,
      surtout les ratios en donjon et en groupes 4 et 5 étoiles (contenu volontairement dur).
- [ ] Le lore du dépôt `kanarion_lore` sur GitHub date d'avril : pousser la version du bureau.
