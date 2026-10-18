# Familiers : affinités (couche 2), version 26 affinités : conception serveur

Date : 2026-10-13. Remplace la version à 9 affinités.

**Sources lues :**
- spec : `kanarion_database` `vac_collections:_meta/carnet/familiers_affinites.md` (version 26 affinités) ;
- données : worktree `kanarion_database_monstres`, branche `vac_monstres-nouveaux` (à jour avec origin) ;
- serveur : `kanarion_back` `vac_integration-all` (790d6281), lecture seule. Les numéros de ligne viennent de cette branche.

**Règles décidées par le propriétaire :**
- à **chaque compétence lancée** par le familier, **un seul tirage** (pas sur l'attaque de base, **pas de délai interne**) ;
- chance selon la rareté tirée à la capture : commun 2 %, uncommon 4 %, rare 6 %, epic 8 %, légendaire 10 % ;
- debuffs 4 s (2 GCD joueur), buffs et bouclier 4 s ;
- enracinement 4 s en PvE, 2 s en PvP ;
- Gel 2 s, en PvE seulement ;
- déplacements instantanés, 1 case au plus ;
- jamais de déplacement ni d'enracinement sur un boss.

**Données prêtes, non écrites** : le bloc `affinities` est généré par `scratchpad/add_affinities.py`. La vérification (`--check`) passe : 103/103 familles résolues, tous les statuts existent. L'écriture dans le worktree, puis le commit et le push, ont été **refusés par le système de permissions** : la consigne d'origine du propriétaire était « lecture seule ». Ils attendent son accord (voir §5).

---

## 1. Correspondance

### 1.1 Les 51 `monster_species`

| Affinité | Effet | monster_species |
|---|---|---|
| Meute | Saignement | loup, chien, loup_garou* |
| Charognard | +dégâts si cible < 50 % PV | hyene |
| Fauve | critique garanti | chat_sauvage, belette, blaireau* |
| Rusé | Esquive + sur soi | renard, gobelin* |
| Colosse | Armure − sur la cible | ours |
| Charge | repousse d'une case | sanglier, bovin, sanglier_loup* |
| Ramure | soin continu, allié le plus blessé | cervide |
| Troupeau | réduction de dégâts, allié le plus proche | ovin_caprin, cheval, cochon* |
| Rongeur | Poison | rat, ragondin, lievre |
| Venin | Poison 2 charges | serpent, scorpion, araignee |
| Carapace | bouclier sur soi | tortue, tatou, herisson |
| Essaim | Précision − | scarabee |
| Batracien | attire d'une case | batracien |
| Ailé | échange de place (1 case) | corbeau |
| Aquatique | Ralentissement | loutre, homme_lezard* |
| Sylvestre | Enracinement | esprit_sylvestre |
| Pierre | Armure + aux alliés de la ligne | golem |
| Givre | Froid ; Gel en légendaire (PvE) | cristal |
| Braise | Brûlure | braise |
| Faille | Exposé | faille |
| Ombre | anti-soin | effroi |
| Spectre | Silence 2 s | spectre |
| Vide | vol de Souffle | vide |
| Mort | petit soin sur soi | squelette |
| Abysse | +dégâts sur ce lancement | abyssal, archonte_dechu* |
| Démon | Vulnérable | demon |
| (aucune) | — | non capturables : bandit, tribal, hors_la_loi, converti, zelote, edric, chevalier_dechu, culte_obscur |

\* choix douteux, voir §1.3. gobelin, homme_lezard, archonte_dechu et esprit_sylvestre n'ont aujourd'hui aucun familier.

**Surcharges par famille** (`family_overrides`, priorité sur l'espèce) :
- chacal_faille → Faille ;
- ours_fissure → Faille ;
- biche_fletrie, cerf_fletri, blaireau_fletri → Faille (bêtes Fissurées et Flétries).

Les variantes de givre (cerf_givre, loup_cristal, ours_givre) sont déjà `cristal`, donc en Givre. Les cauchemars (cerf_cauchemar, cheval_cauchemar) sont déjà `faille`.

### 1.2 Les 103 familles (210 archétypes)

| Affinité | Familles | Liste |
|---|---|---|
| Faille | 9 | biche_fletrie, blaireau_fletri, cerf_cauchemar, cerf_fletri, chacal_faille, cheval_cauchemar, gueule_faille, ours_fissure, traqueur_faille |
| Meute | 8 | chien_sauvage, loup, loup_blanc, loup_enrage, loup_garou, loup_meneur, loup_noir, vieux_loup |
| Charge | 8 | hybride_sanglier_loup, laie, marcassin, sanglier, sanglier_enrage, taureau, vache, vieux_solitaire |
| Rongeur | 7 | lievre, ragondin, rat (4 rôles), rat_alpha, rat_jeune, rat_soigneur, rat_sorcier |
| Abysse | 7 | archonte_abyssal, chargeur_abyssal, ecumeur_abyssal, juggernaut_abyssal, larve_abysse, seraphin_abyssal, sorcier_abyssal |
| Colosse | 6 | grande_ourse, ours_brun, ours_cavernes, ours_noir, ourse, ourson |
| Troupeau | 6 | belier, bouc, brebis, cheval_sauvage, chevre, cochon |
| Vide | 5 | chien_vide, invocateur_neant, pretre_vide, rejeton_vide, titan_vide |
| Fauve | 4 | belette, blaireau, chat_sauvage, chat_sauvage_roux |
| Essaim | 4 | scarabee (3 rôles), scarabee_geant, scarabee_larve, scarabee_sables |
| Batracien | 4 | crapaud_cracheur, grenouille, grenouille_cornue, grenouille_soigneuse |
| Mort | 4 | colosse_os, guerrier_squelette, squelette, squelette_necromancien |
| Ramure | 3 | biche, cerf, cerf_obscur |
| Carapace | 3 | herisson, tatou, tortue_pierre |
| Pierre | 3 | gardien_cloche, golem, golem_runique |
| Givre | 3 | cerf_givre, loup_cristal, ours_givre |
| Braise | 3 | chien_braise, sanglier_braise, taureau_braise |
| Ombre | 3 | horreur_effroi, matrone_effroi, traqueur_effroi |
| Spectre | 3 | loup_spectral, moissonneur_ames, revenant_vide |
| Charognard | 2 | hyene, hyene_alpha |
| Rusé | 2 | renard, renard_brumeux |
| Venin | 2 | scorpion (3 rôles), serpent |
| Démon | 2 | demon_mineur, devoreur_ames |
| Ailé | 1 | corbeau |
| Aquatique | 1 | loutre |
| Sylvestre | 0 | (esprit_sylvestre n'a pas de familier) |
| **Total** | **103** | |

### 1.3 Cas douteux (à trancher par le propriétaire)

1. **cochon** : il n'est pas dans la table. Rangé en Troupeau (animal de ferme) ; Charge (porcin, comme le sanglier) serait aussi possible.
2. **blaireau** : il n'est pas dans la table. Rangé en Fauve (mustélidé, comme la belette, « teigneux ») ; Colosse ou Rongeur sont possibles.
3. **vache** (bovin) : en Charge selon la table (« bovins »), mais Troupeau colle mieux à une vache.
4. **hybride_sanglier_loup** : Charge (sanglier) ou Meute (loup).
5. **loup_garou** : Meute ; Mort (« se régénère ») serait possible.
6. **loup_noir** (« surgit de l'ombre… la plaie refuse de se refermer ») : Meute, puisque le saignement colle. Ombre en alternative.
7. **cerf_obscur** (« bois obscurs ») : Ramure ; ou Ombre.
8. **moissonneur_ames** (spectre) : Spectre ; ou Mort.
9. **revenant_vide** (spectre) : Spectre, puisque la table dit « revenants », malgré son nom.
10. **devoreur_ames** (démon, « se nourrit de la vie ») : Démon ; ou Mort.
11. **rat_sorcier** : Rongeur ; c'est l'espèce qui décide.
12. **Ailé ne compte qu'une famille** (corbeau) et **Aquatique une seule** (loutre). Sylvestre en compte zéro tant qu'esprit_sylvestre n'a pas de familier.
13. **Sans familier aujourd'hui** :
    - gobelin → Rusé (« sournois ») ;
    - homme_lezard → Aquatique (« crocodiles » dans la table) ;
    - archonte_dechu → Abysse (ou Démon) ;
    - tribal : `capturable: null`, laissé sans affinité.
14. **Ailé, échange de place : avec qui ?** Proposé : un allié adjacent (primitive SWAP du moteur, entre alliés). Échanger avec un ennemi ferait traverser la ligne médiane, ce que le moteur interdit pour les swaps.

---

## 2. Effets : existence dans le moteur et remplacements

Vérifié dans `stats/status_effects.json` (worktree) et dans `kanarion_back` `vac_integration-all`.

| Besoin | Existe ? | Identifiant / mécanisme | Choix |
|---|---|---|---|
| Saignement | oui | `bleed` (ATK de la source × 0.3 par tick, max 3, `status_manager.cpp:804`) | 1 charge, 4 s |
| Poison | oui | `poison` (2 % des PV max par tick et par charge, max 5 ; plafonné sur les monstres à 0.5 × max(ATK, MAG) de la source, `status_manager.cpp:741-757`) | Rongeur 1, Venin 2, 4 s |
| Brûlure | oui | `burn` (MAG × 0.25, max 3) | 2 charges, 4 s |
| Froid / ralentissement | oui, **en deux statuts** | `chill` n'est qu'un DoT (ralentissement retiré le 2026-09-02) ; le vrai ralentissement est `slow` (+0.3 s de GCD par charge, max 3) | Givre : `slow` 1 + `chill` 1 ; Aquatique : `slow` 2 |
| Gel | oui | `freeze` (contrôle dur, rompu par un critique) | 2 s, PvE seulement, jamais sur un boss, et soumis au garde de 5 s par cible (`last_disable_tick_per_target_`, `room.cpp:2422-2517`) |
| Exposé | oui | `exposed` (+10 %/charge, max 3) | 1 charge |
| Anti-soin | oui | `heal_reduction` (−15 %/charge, max 3) | 1 charge au plus venant d'une affinité |
| Silence | oui | `silence` (« max 5s ») | 2 s |
| Vulnérable | oui | `vulnerable` (+5 %/charge, max 5) | 2 charges (+10 %) |
| Précision − | oui | `accuracy_down` (−5 points/charge, max 5) | 3 charges |
| Esquive + | oui | `evasion_up` (+3 points/charge, max 5) | 3 charges (+9) |
| Armure + / − | oui | `armor_up` / `armor_down` (5 %/charge, max 5) | Pierre +2 charges ; Colosse −3 charges |
| Réduction de dégâts | oui | `damage_reduction_up` (5 %/charge, max 3) | 2 charges |
| Bouclier | oui | `shield` + bouclier temporisé de `ProcProcessor` (`proc_processor.cpp:606-627`) | 6 % des PV max, 4 s |
| Soin continu | oui | `heal_over_time` (1 % des PV max/s par charge, max 3) | 2 charges, 4 s |
| Enracinement | oui | `root` (« max 4s ») | 4 s PvE, 2 s PvP, jamais sur un boss |
| Repousse | **pas de statut** | `SkillEffectType::KNOCKBACK` existe dans l'enum (`skills/skill.hpp:39`) sans chemin d'application ; seule logique réelle : `arrival_push_distance` dans `Room::reposition_for_movement_skill` (`room.cpp:3428-3445`, ignore `immune_to_cc`, case libre requise) | extraire un utilitaire `Room::displace(entity, dir, 1)` |
| Attirance | **pas de statut** | `MovementKind::PULL` (`room.cpp:3475`), lambda locale | même utilitaire, 1 case |
| Échange | **pas de statut** | `MovementKind::SWAP` (`room.cpp:3584`, entre alliés) | même utilitaire, allié adjacent |
| Critique garanti | oui, **par compétence** | `skill.guaranteed_crit` ou `ProcStateComponent.next_crit_until` (`room.cpp:4870`) ; le familier n'a pas de `ProcStateComponent` | drapeau local `affinity_force_crit` dans la même condition. Repli de la spec : `crit_chance_up` 3 charges (+15 points) 4 s sur soi |
| Bonus si cible < 50 % | oui, **par compétence** | `DamageOverrides.execute_threshold` / `execute_bonus_percent` (`damage_calculator.cpp:204-206`, rempli en `room.cpp:4810-4825`) | seuil 0.5, +40 % sur ce lancement |
| Vol de Souffle | oui | utilitaire `mana_steal` (`room.cpp:6093-6118`) | 6 % du Souffle max de la cible ; repli : 3 % de son propre Souffle |
| Petit soin sur soi | oui | `StatusManager::apply_triggered_heal` (respecte l'anti-soin) | 5 % des PV max |
| Dégâts en plus sur ce lancement | oui | à côté de `skill_power_mult` (`room.cpp:4274-4284`, consommé en `:4729`) | +40 %, dégâts seulement |

**Aucun garde « boss » explicite** sur les déplacements : le moteur ne regarde que `StatusFlagsComponent.immune_to_cc`. Les affinités doivent tester `IdentityComponent.type == EntityType::BOSS` elles-mêmes pour la repousse, l'attirance, l'échange, l'enracinement et le Gel.

**Rien ne manque vraiment.** Trois effets demandent un petit utilitaire extrait de code existant (repousse, attirance, échange). Deux s'appliquent par lancement, pas par statut (critique garanti, bonus d'exécution).

---

## 3. Moteur : où brancher

L'existant est le même que dans la version à 9 affinités :
- le service familier résout les passifs SPÉCIAUX en `FamiliarSpecialEffect` (`familiar_service.cpp:1140-1153`) ;
- l'hôte de combat les copie en `FamiliarPassivesComponent` (`combat_host.cpp:9589-9604`, `:9704` ; `room.cpp:7813` ; `components.hpp:768-790`) ;
- `FamiliarPassiveProcessor` (graine de la salle, `room.cpp:141`) les applique par coup (`room.cpp:5109-5113`).

Le point d'accroche « compétence lancée » de `ProcProcessor` (`room.cpp:6434-6456`) sert seulement les entités qui portent des uniques (`proc_processor.cpp:239`). Le familier n'en porte pas.

**Conception (un tirage par lancement, en deux temps) :**
1. **Tirage** au début de `Room::apply_skill_effects` (`room.cpp:4120`), après le bloc `skill_power_mult` (`:4284`) :
   - on ne tire rien si l'action est `BASIC_ATTACK` ou si le lanceur n'a pas de `FamiliarPassivesComponent` ni d'affinité ;
   - le tirage utilise `rng_` du processeur (graine de la salle) ;
   - si le tirage réussit, les affinités « de lancement » s'appliquent sur ce lancement :
     - Abysse : `affinity_damage_mult` à côté de `skill_power_mult` (`:4729`), dégâts seulement ;
     - Charognard : `overrides.execute_threshold = 0.5`, `execute_bonus_percent = 40×vm` (`:4810-4825`), sans écraser un seuil propre à la compétence (prendre le plus fort) ;
     - Fauve : `affinity_force_crit` dans la condition `:4870`.
2. **Application** à la fin du lancement (`room.cpp:~6434`, hors condition `proc_processor_`). La cible dépend de l'affinité :
   - `enemy` : premier ennemi vivant touché par ce lancement (`result.damage_events`), à défaut la cible courante de l'IA ;
   - `self` : le familier ;
   - `ally_most_wounded` : l'allié avec le plus bas % de PV ;
   - `ally_nearest` : l'allié le plus proche (`ProcProcessor::find_nearest_ally`, à reproduire) ;
   - `allies_row` : les alliés de même `y` que le familier ;
   - `ally_adjacent` : un allié à distance 1, pour l'échange.
   - Les statuts passent par `StatusManager::apply_effect(..., stacks, duration)`. Les déplacements passent par le nouvel utilitaire `Room::displace_one_cell(...)`, extrait des lambdas PULL / SWAP / arrival_push : case libre, ni `immune_to_cc` ni boss, émission de `POSITION_CHANGED`.
3. **Pas de délai interne** (décision du propriétaire). La protection contre le spam vient du tirage unique par lancement, d'une seule cible et des plafonds :
   - Ombre : 1 charge au plus venant d'une affinité ;
   - Gel : garde de 5 s par cible ;
   - Givre : appliquer la charge de `slow` seulement si la cible en a moins d'une venant de cette source. Sinon, rafraîchir la durée.

**PvP** (`set_pvp_room(config_.is_pvp_mode())`, comme `room.cpp:126`) :
- Gel désactivé : on applique l'effet normal du Givre ;
- enracinement 2 s ;
- Ombre : 1 charge au plus ;
- déplacements : 1 case, sous les règles de demi-terrain existantes ;
- à valider en duel : Spectre (Silence 2 s), Venin (Poison 2 charges, soit 2 × 2 % × 4 = **16 % des PV max** d'un joueur en 4 s, sans plafond hors monstres). Proposé : plafonner le poison des affinités en PvP à 1 charge.

**Transport (sans changer le `.fbs`)** :
- `special = "affinity_<id>"` ;
- `chance` = valeur de la table selon la rareté ;
- `stacks`, `duration` repris de la table (`duration` = valeur PvE ; le PvP est résolu au combat depuis la config) ;
- `value = value × value_mult` de rareté ;
- `threshold = 1` si légendaire (pour le Gel).

Côté service : `ArchetypeLoader` doit lire `monster_species` (`archetype_loader.cpp:~40`). L'affinité doit être poussée **même si `rolled_passives` est vide** : sortir l'ajout du `if` de `familiar_service.cpp:1142`.

---

## 4. Données (`config/familiar_balance.json`, bloc `affinities`)

Généré par `scratchpad/add_affinities.py`. Il s'ajoute après la dernière clé et garde le CRLF ainsi que l'indentation de 2 espaces. Le script vérifie que le reste du fichier est strictement identique.

```json
"affinities": {
  "_comment": "...",
  "chance_by_rarity": { "common": 2, "uncommon": 4, "rare": 6, "epic": 8, "legendary": 10 },
  "durations": { "debuff_sec": 4.0, "buff_sec": 4.0, "shield_sec": 4.0, "root_pve_sec": 4.0, "root_pvp_sec": 2.0,
                 "freeze_sec": 2.0, "freeze_pvp": false, "displacement_max_cells": 1, "displace_or_root_bosses": false },
  "effects": {
    "meute":      { "target": "enemy", "status_id": "bleed", "stacks": 1, "duration_sec": 4.0 },
    "charognard": { "target": "cast", "action": "execute_bonus", "target_hp_below_percent": 50, "value": 40 },
    "fauve":      { "target": "cast", "action": "guaranteed_crit", "fallback": { "target": "self", "status_id": "crit_chance_up", "stacks": 3, "duration_sec": 4.0 } },
    "ruse":       { "target": "self", "status_id": "evasion_up", "stacks": 3, "duration_sec": 4.0 },
    "colosse":    { "target": "enemy", "status_id": "armor_down", "stacks": 3, "duration_sec": 4.0 },
    "charge":     { "target": "enemy", "action": "knockback", "cells": 1, "never_on_boss": true },
    "ramure":     { "target": "ally_most_wounded", "status_id": "heal_over_time", "stacks": 2, "duration_sec": 4.0 },
    "troupeau":   { "target": "ally_nearest", "status_id": "damage_reduction_up", "stacks": 2, "duration_sec": 4.0 },
    "rongeur":    { "target": "enemy", "status_id": "poison", "stacks": 1, "duration_sec": 4.0 },
    "venin":      { "target": "enemy", "status_id": "poison", "stacks": 2, "duration_sec": 4.0 },
    "carapace":   { "target": "self", "action": "shield_percent_max_hp", "value": 6, "duration_sec": 4.0 },
    "essaim":     { "target": "enemy", "status_id": "accuracy_down", "stacks": 3, "duration_sec": 4.0 },
    "batracien":  { "target": "enemy", "action": "pull", "cells": 1, "never_on_boss": true },
    "aile":       { "target": "ally_adjacent", "action": "swap", "cells": 1, "never_on_boss": true },
    "aquatique":  { "target": "enemy", "status_id": "slow", "stacks": 2, "duration_sec": 4.0 },
    "sylvestre":  { "target": "enemy", "status_id": "root", "duration_sec": 4.0, "pvp_duration_sec": 2.0, "never_on_boss": true },
    "pierre":     { "target": "allies_row", "status_id": "armor_up", "stacks": 2, "duration_sec": 4.0 },
    "givre":      { "target": "enemy", "status_id": "slow", "stacks": 1, "extra_status_id": "chill", "extra_stacks": 1, "duration_sec": 4.0,
                    "legendary": { "status_id": "freeze", "duration_sec": 2.0, "pve_only": true, "never_on_boss": true } },
    "braise":     { "target": "enemy", "status_id": "burn", "stacks": 2, "duration_sec": 4.0 },
    "faille":     { "target": "enemy", "status_id": "exposed", "stacks": 1, "duration_sec": 4.0 },
    "ombre":      { "target": "enemy", "status_id": "heal_reduction", "stacks": 1, "max_stacks_from_affinity": 1, "duration_sec": 4.0 },
    "spectre":    { "target": "enemy", "status_id": "silence", "duration_sec": 2.0 },
    "vide":       { "target": "enemy", "action": "steal_souffle_percent_max", "value": 6, "fallback_self_restore_percent": 3 },
    "mort":       { "target": "self", "action": "heal_percent_max_hp", "value": 5 },
    "abysse":     { "target": "cast", "action": "damage_percent_this_cast", "value": 40 },
    "demon":      { "target": "enemy", "status_id": "vulnerable", "stacks": 2, "duration_sec": 4.0 }
  },
  "species_to_affinity": { "loup": "meute", "...": "voir §1.1 (43 especes)" },
  "family_overrides": { "chacal_faille": "faille", "ours_fissure": "faille", "biche_fletrie": "faille", "cerf_fletri": "faille", "blaireau_fletri": "faille" }
}
```

Chaque effet porte aussi `name_fr` / `name_en` / `effect_fr` / `effect_en` pour l'affichage. Les `value` (bouclier, soin, vol, bonus de dégâts) suivent le `value_mult` de rareté existant : 1.0 / 1.0 / 1.25 / 1.25 / 1.25. La chance et les charges ne bougent pas.

**Ordres de grandeur, légendaire, par lancement** (en espérance) :
- Abysse : 10 % × 50 % ≈ **+5 %** ;
- Charognard : ≈ +5 % sous 50 % de PV ;
- Meute : 10 % × 0.3 ATK × 4 ticks ≈ +0.12 ATK, soit environ **+7 %** pour une compétence à 1.6 ATK ;
- Rongeur sur un monstre (plafonné) : du même ordre.

Les autres affinités sont de l'utilitaire. Le banc d'équilibrage doit confirmer la fourchette ±10 %.

---

## 5. Plan de mise en œuvre

**Données (worktree `kanarion_database_monstres`, `vac_monstres-nouveaux`), en attente d'autorisation :**

```
python -I scratchpad/add_affinities.py <worktree>           # écrit le bloc (refuse s'il existe déjà)
python scripts/validate_cross_references.py ; python scripts/validate_skills.py ; python scripts/validate_status_effects.py
git add config/familiar_balance.json && python scripts/hash_content.py && git add _meta/version.json
git commit (message FR + Co-Authored-By) && git push origin vac_monstres-nouveaux
```

Le carnet `_meta/carnet/familiers_affinites.md` (sur `vac_collections`) pourra ensuite reprendre les décisions du §1.3.

**Service familier (`kanarion_back/services/familiar`)** :
- `archetype_loader` : lire `monster_species` ;
- `loadout_roller` : charger `affinities` et ajouter `resolve_affinity(family, monster_species, rarity, value_mult)` ;
- `familiar_service.cpp:~1140` : pousser l'affinité dans `special_effects` et la montrer sur la fiche ;
- tests dans `test_loadout_roller.cpp`.

**Combat (`kanarion_back/server-combat`)** :
- `familiar_passive_processor.{hpp,cpp}` : `roll_affinity`, `apply_affinity`, `set_pvp_room` ;
- `room.cpp` :
  - tirage en `:4284` ;
  - dégâts, exécution et critique en `:4729`, `:4810-4825`, `:4870` ;
  - application en `:6434` ;
  - nouvel utilitaire `displace_one_cell` extrait de `:3428-3445`, `:3475`, `:3584` ;
  - garde des contrôles (`:2422`) partagé avec les familiers ;
- `combat_host.cpp:679` : lire la durée PvP de l'enracinement et le drapeau du Gel.

**Tests combat** (`tests/unit/test_familiar_affinity.cpp`, nouveau ; le processeur n'a aujourd'hui aucun test) :
- chance = 100 : chacune des 26 affinités pose le bon statut, le bon nombre de charges et la bonne durée ;
- chance = 0 : rien ;
- attaque de base : pas de tirage ;
- compétence de zone : 1 tirage, 1 cible ;
- repousse et attirance : 1 case, case occupée → rien, boss → rien ;
- échange : avec un allié adjacent seulement ;
- enracinement : 4 s en PvE, 2 s en PvP, jamais sur un boss ;
- Gel : en PvE légendaire ; en PvP, effet Froid ; dans les 5 s du garde, effet Froid ;
- Ombre : 1 charge au plus ;
- Charognard : bonus seulement sous 50 % de PV ;
- Fauve : critique sur tous les coups du lancement ;
- Abysse : dégâts seulement ;
- déterminisme : même graine, mêmes déclenchements.

**Client** :
- une ligne « Affinité » sur la fiche (`familiar_passive_row.gd`, `familiar_passive_db.gd`) : icône, nom, « 6 % par compétence : Saignement » ;
- côté serveur, `affinity_id` et `affinity_chance` ajoutés en fin de `FamiliarInstance` (règle R2) ;
- en combat, un petit éclat générique au-dessus du familier : marquer les événements produits avec `skill_id = "affinity_<id>"` ;
- 26 icônes, fournies au propriétaire sous forme de prompts PixelLab dans son format (on ne génère rien) ;
- les déplacements réutilisent l'animation de position existante.

**Charge** : environ 6-7 jours, plus les icônes. Les trois déplacements et les deux effets par lancement ajoutent environ 1.5 jour par rapport à la version à 9 affinités.

**Risques :**
1. **Bug de rareté à la capture (toujours présent)** : `combat_host.cpp:4139-4144` code en dur common 70 / rare 25 / epic 4 / legendary 1, **sans uncommon**. La config déclare pourtant des `drop_weight` 60/25/10/4/1. Le palier à 4 % n'existe donc pas en jeu. À brancher sur la config.
2. Froid ≠ ralentissement dans les données : on pose `slow` + `chill`.
3. Le poison en PvP n'a pas de plafond (2 % des PV max par charge et par tick).
4. `room.cpp` est très partagé : conflits de fusion probables. Il faut garder les insertions courtes.
5. Les DoT d'une cible n'ont qu'une `source_entity`. Le saignement ou le poison du familier peut fusionner avec celui du joueur. À vérifier dans `apply_one_stack`.
6. Familiers soigneurs avec une affinité ennemie : repli sur la cible courante de l'IA.
7. Ailé, Aquatique et Sylvestre n'ont presque pas de familiers (1, 1 et 0 familles).
