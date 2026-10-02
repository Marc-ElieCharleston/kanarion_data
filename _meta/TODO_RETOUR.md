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
- [ ] Mécaniques des nouvelles compétences qui demanderaient du code : voir
      `new_skills_report.md` du concepteur (téléportation d'un monstre, invocation temporaire…).
      *(à compléter quand le rapport sera intégré)*

## 5. Data — travail à faire

- [ ] Appliquer la refonte des monstres à `entities/monsters.json` : archétype, espèce, stade, kit
      (tableaux dans `scripts/balance/out/`), après relecture.
- [ ] Écrire les profils des 4 nouveaux archétypes dans `config/monster_scaling_model.json`.
- [ ] Ajouter les nouvelles compétences de monstres dans `skills/monster_skills.json` (bloc séparé).
      *(liste à compléter quand le concepteur aura rendu son travail)*
- [ ] Nettoyer les fiches : clés `mr` et `spd` (une fois chacune), `magic_resist` manquant (1 monstre),
      stats aberrantes du Chien sauvage et du Culte obscur.
- [ ] 59 monstres actifs ne sont placés nulle part (zones, donjons, tour) : vérifier s'ils viennent
      de quêtes / événements, sinon les passer en `shelved` ou les placer.
- [ ] Familiers : table espèce de familier (65) → espèce de monstre (45).
- [ ] Descriptions : cartes Koro (le bouclier suit le rang), poison (plafonné sur les monstres),
      boucliers `shield_def` (décrits en % PV max, calculés sur la DEF).
- [ ] `entities/boss_mechanics.json` n'est lu par aucun serveur : supprimer ou brancher.
- [ ] Pré-existant : `validate_skills.py` (129 erreurs de liste blanche), `gen_pet_books.py --check`
      (descriptions périmées).

## 6. Assets (PixelLab, icônes)

- [ ] Seuls 158 portraits de monstres sont dans le dépôt client (le reste est synchronisé sur le
      serveur) : vérifier qu'aucun monstre actif n'en manque.
- [ ] Portraits non trouvés pour la revue : `mob_zealot_acolyte`, `mob_goblin_witch`,
      `mob_abyssal_scholar`, `mob_edric_chosen_guard`, `mob_nether_caller`, `mob_hollow_sentinel`,
      `mob_golem_sentinel`, `mob_rift_warden`, `mob_throne_sentinel`, `mob_grieving_sentinel`,
      `boss_forest_guardian`, `mob_abyssal_juggernaut`, `mob_edric_chosen_ritualist`.
- [ ] Monstres temporaires de l'invocateur : sprites à créer.
- [ ] Icônes des nouvelles compétences de monstres (identité d'archétype, rôle, attaques d'espèce).
      *(liste exacte à compléter quand le concepteur aura rendu son travail)*
- [ ] Nouveaux monstres pour les archétypes peu fournis (1 seul invocateur aujourd'hui).

## 7. Discussions ouvertes (design)

- [ ] Idées de contenu PvE à proposer (déjà en jeu : coffres, failles, tour infinie ; idée : pages
      de livre à collectionner qui racontent des histoires).
- [ ] Le lore du dépôt `kanarion_lore` sur GitHub date d'avril : pousser la version du bureau.
