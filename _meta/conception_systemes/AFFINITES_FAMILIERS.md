# Familiers : affinités (couche 2) : conception serveur

Date : 2026-10-13. Lecture seule, rien n'a été modifié dans les dépôts.
Sources lues :
- spec décidée : `kanarion_database` `vac_collections:_meta/carnet/familiers_affinites.md` ;
- données : `vac_monstres-nouveaux:entities/{familiars,monster_species}.json`, `classes/familiar/passives.json`, `config/familiar_balance.json`, `stats/status_effects.json`, `vac_collections:_meta/carnet/runes.md` ;
- serveur : `kanarion_back` `vac_integration-all` (790d6281). Les numéros de ligne ci-dessous viennent de cette branche. Le `FamiliarPassiveProcessor` existe aussi sur `main` et sur `vac_familiar-passives-combat`, à ~10 lignes près.

Rappel de la spec : chaque familier a une affinité qui dépend de la famille de son espèce. Elle se déclenche à **chaque compétence lancée** par le familier. Chance selon la rareté tirée à la capture : commun 2 %, uncommon 4 %, rare 6 %, epic 8 %, légendaire 10 %.

---

## 1. Correspondance espèces → affinités

### 1.1 Les 51 `monster_species` (entities/monster_species.json)

| Affinité | monster_species | Remarque |
|---|---|---|
| **Sauvage** (Saignement) | rat, chien, corbeau, renard, sanglier, loup, hyene, ovin_caprin, bovin, cervide, cheval, sanglier_loup, batracien, loutre, cochon, lievre, blaireau, ours, chat_sauvage, belette, ragondin, loup_garou | catégorie par défaut des bêtes |
| Sauvage *(à trancher)* | serpent, araignee, scorpion, tatou, herisson | voir les signalements |
| **Pierre** (bouclier sur soi) | scarabee, tortue, golem | |
| **Givre** (Froid, Gel en légendaire) | cristal | |
| **Braise** (Brûlure) | braise | |
| **Faille** (Exposé) | faille | |
| **Ombre** (anti-soin) | spectre, effroi | |
| **Vide** (vol de Souffle) | vide | |
| **Mort** (petit soin sur soi) | squelette | il n'existe pas d'espèce « nécromancien » : `squelette_necromancien` est une famille de `squelette` |
| **Abysse** (dégâts supplémentaires) | abyssal, demon | |
| Abysse *(proposé)* | archonte_dechu | capturable mais aucun familier aujourd'hui |
| — (aucune) | bandit, hors_la_loi, converti, zelote, edric, chevalier_dechu, culte_obscur | non capturables (`capturable: false`) |
| — *(à décider)* | tribal (`capturable: null`), gobelin, homme_lezard, esprit_sylvestre | capturables mais sans familier dans familiars.json |

### 1.2 Les familles de familier (103 familles = 210 archétypes)

Dans `familiars.json`, chaque famille porte un champ `species` (par exemple `loup_cristal`) et un champ `monster_species` (par exemple `cristal`). Le tableau applique la correspondance du §1.1, avec deux surcharges proposées : `chacal_faille` et `ours_fissure` vont en Faille, au nom de la règle « variantes Fissurées » de la spec.

| Affinité | Familles | Archétypes | Familles concernées |
|---|---|---|---|
| Sauvage | **59** | 118 | belette, belier, biche, biche_fletrie, blaireau, blaireau_fletri, bouc, brebis, cerf, cerf_fletri, cerf_obscur, chat_sauvage, chat_sauvage_roux, cheval_sauvage, chevre, chien_sauvage, cochon, corbeau, crapaud_cracheur, grande_ourse, grenouille, grenouille_cornue, grenouille_soigneuse, herisson, hybride_sanglier_loup, hyene, hyene_alpha, laie, lievre, loup, loup_blanc, loup_enrage, loup_garou, loup_meneur, loup_noir, loutre, marcassin, ours_brun, ours_cavernes, ours_noir, ourse, ourson, ragondin, rat (4 archétypes), rat_alpha, rat_jeune, rat_soigneur, rat_sorcier, renard, renard_brumeux, sanglier, sanglier_enrage, scorpion (3), serpent, tatou, taureau, vache, vieux_loup, vieux_solitaire |
| Abysse | 9 | 18 | archonte_abyssal, chargeur_abyssal, demon_mineur, devoreur_ames, ecumeur_abyssal, juggernaut_abyssal, larve_abysse, seraphin_abyssal, sorcier_abyssal |
| Pierre | 8 | 16 | gardien_cloche, golem, golem_runique, scarabee (3), scarabee_geant, scarabee_larve, scarabee_sables, tortue_pierre |
| Faille | 6 | 12 | cerf_cauchemar, cheval_cauchemar, gueule_faille, traqueur_faille, **chacal_faille***, **ours_fissure*** |
| Ombre | 6 | 12 | horreur_effroi, loup_spectral, matrone_effroi, moissonneur_ames, revenant_vide, traqueur_effroi |
| Vide | 5 | 10 | chien_vide, invocateur_neant, pretre_vide, rejeton_vide, titan_vide |
| Mort | 4 | 8 | colosse_os, guerrier_squelette, squelette, squelette_necromancien |
| Givre | 3 | 6 | cerf_givre, loup_cristal, ours_givre |
| Braise | 3 | 6 | chien_braise, sanglier_braise, taureau_braise |

\* surcharge par famille (leur `monster_species` vaut `hyene` et `ours`).

### 1.3 Espèces et familles qui collent mal (à trancher par le propriétaire)

1. **Sauvage pèse 57 %** (59 familles sur 103). Ce n'est pas un problème en soi (ce sont des bêtes), mais un joueur verra « Saignement » sur plus d'un familier sur deux. Les reclassements ci-dessous le ramènent à environ 50 %.
2. **Carapaces → Pierre ?** `tatou` (« se roule en boule »), `herisson` (« piquants : armure ») et `scorpion` (« carapace et dard ») ont le même profil que le scarabée. Proposé : Pierre (+3 familles).
3. **Flétris → Faille ?** `blaireau_fletri` (« terre pourrie par la Fissure »), `biche_fletrie` et `cerf_fletri` sont touchés par la Fissure. La spec dit « faille, variantes Fissurées ». Proposé : Faille (+3).
4. **Venin** : `serpent` et `araignee` collent mal avec le Saignement, et il n'existe pas d'affinité Poison. On les laisse en Sauvage, ou on crée une 10e affinité « Venin → Poison » (le statut `poison` existe et `on_hit_poison` est déjà branché dans le processeur).
5. **Ombres « animales »** : `cerf_obscur` (« bois obscurs ») et `loup_noir` (« surgit de l'ombre… la plaie refuse de se refermer »). Le loup noir garde Sauvage, puisque sa description décrit un saignement. Le cerf obscur pourrait passer en Ombre.
6. **Noms trompeurs** : `revenant_vide` est un `spectre`, donc Ombre, alors que son nom évoque le Vide. `moissonneur_ames` (spectre) serait aussi crédible en Mort. `cerf_cauchemar` et `cheval_cauchemar` (faille) restent Faille.
7. **`loup_garou`** (« bête maudite, se régénère ») : Sauvage par défaut. Mort (soin sur soi) collerait à « se régénère ».
8. **`rat_sorcier`** est un lanceur de sorts mais reste Sauvage (espèce rat). C'est voulu par la règle « une espèce = son affinité ».
9. **`archonte_dechu`, `gobelin`, `homme_lezard`, `esprit_sylvestre`** sont capturables sans familier. Il faudra leur donner une affinité le jour où ils en auront un. `esprit_sylvestre` (« gardien ancien ») n'entre dans aucune case : Pierre au plus proche.

---

## 2. Moteur : l'existant et la meilleure façon de brancher

### 2.1 Ce que fait le serveur aujourd'hui

Correction de la note de la spec : les passifs de familier ne font plus « que des stats ». Il existe déjà un **processeur de passifs spéciaux de familier**, branché en combat.

| Étape | Où |
|---|---|
| Le service familier résout les passifs tirés en effets de stat, `value × value_mult` de rareté | `services/familiar/src/familiar_service.cpp:1110-1121` |
| Il ajoute le passif d'espèce, par palier de niveau | `familiar_service.cpp:1123-1136`, `loadout_roller.cpp:254-266` (clé : `arch.species` = famille) |
| Il résout les passifs SPÉCIAUX et les envoie dans `special_effects` | `familiar_service.cpp:1140-1153`, `loadout_roller.cpp:283-299` |
| Transport : `FamiliarSpecialEffect {special, stat, value, stacks, chance, threshold, duration, hp_percent}`, champ 18 de `FamiliarCombatGetResponse` | `shared/flatbuffers/familiar.fbs:278-287, 318` |
| L'hôte de combat applique les stats principales hp/mp/atk/mag/armor/magic_resist (add_percent / add_flat) | `server-combat/src/combat/combat_host.cpp:9560-9585` |
| L'hôte de combat met les stats secondaires dans `StatsComponent` avant le spawn | `combat_host.cpp:9639-9648` (`domain::apply_familiar_secondary_stat`) |
| L'hôte de combat lit `special_effects` dans `std::vector<FamiliarSpecialPassive>` | `combat_host.cpp:9589-9604` |
| Il les attache après le spawn | `combat_host.cpp:9704` → `Room::attach_familiar_passives` (`room.cpp:7813`) → `FamiliarPassivesComponent` (`entities/components.hpp:768-790`) |
| Le processeur est créé avec la graine de la salle (déterministe) | `room.cpp:141` |
| Point d'accroche « dégâts infligés » (par coup et par cible) | `room.cpp:5109-5113` → `FamiliarPassiveProcessor::on_damage_dealt` (`familiar_passive_processor.cpp:16-49`), qui gère `on_hit_poison`, `on_crit_bleed`, `on_hit_silence` |

L'hôte de combat ne connaît **ni la rareté en texte ni la `monster_species`**. Il reçoit seulement `rarity_stat_multiplier` (champ 16). Côté service, `ArchetypeLoader` lit `species` (`archetype_loader.cpp:40`) mais pas `monster_species`.

### 2.2 Existe-t-il un accroche « compétence lancée » ?

- **Oui, dans `ProcProcessor`** (le moteur des uniques, keystones et futures runes) : `Room::apply_skill_effects` (`room.cpp:4120`) se termine par le bloc « Proc hooks: on_skill_used » (`room.cpp:6434-6456`). Ce bloc est sauté sur `ActionType::BASIC_ATTACK`, s'exécute **une fois par lancement** et dispose de `result.damage_events` et `result.heal_events`. Il appelle `ProcProcessor::on_skill_used` (`proc_processor.cpp:234`).
- **Inutilisable tel quel pour un familier** : `on_skill_used` et `check_procs` sortent dès que l'entité n'a pas `EquippedUniquesComponent` + `ProcStateComponent` (`proc_processor.cpp:239`, `:345`), et un familier ne porte aucun unique. C'est d'ailleurs pour cela que le `FamiliarPassiveProcessor` a été séparé (commentaire du `.hpp`).
- Il n'y a pas d'accroche « on_cast » dans l'arbre de passifs : `tree_on_hit_resolved` fonctionne par coup (`room.cpp:5107`).
- Utilitaires réutilisables :
  - `StatusManager::apply_effect(entities, target, id, source, tick, buf, stacks, duration_sec, scalar, pct)` (`status_manager.hpp:115`) ;
  - `StatusManager::apply_triggered_heal` (`status_manager.hpp:92`). Il respecte `heal_blocked` et `heal_reduction` (`status_manager.cpp:1183-1187`) ;
  - le bouclier temporisé de `ProcProcessor` (`shield_percent_max_hp` avec durée : `register_effect` d'un id dédié de type SHIELD, puis `apply_effect(..., scalar=absorb)`, `proc_processor.cpp:606-627`), à reproduire ;
  - le vol de Souffle des compétences (`room.cpp:6093-6118`, `util.stat == "mana_steal"`), à reproduire en 5 lignes ;
  - le multiplicateur de puissance par lancement `skill_power_mult` (`room.cpp:4274-4284`, consommé sur les dégâts en `:4729-4733`), qui servira à Abysse ;
  - le garde anti-enchaînement de contrôles : `last_disable_tick_per_target_` + `config_.shared_disable_cooldown_ticks` = 50 ticks (5 s), dans `room.cpp:2422-2517` et `room.hpp:262, 1811`. Il ne protège aujourd'hui que des monstres ; à réutiliser pour le Gel.
- Pas de rendements décroissants des contrôles en PvP. Seule la ténacité réduit les durées (0-50 %, `status_manager.cpp:2058-2082`). Pas de multiplicateur de soin propre au PvP.

### 2.3 Recommandation : étendre `FamiliarPassiveProcessor`, sans passer par `ProcProcessor`

On ne réutilise pas le moteur des runes. Le brancher demanderait de donner aux familiers un faux `EquippedUniquesComponent` et un registre d'uniques synthétiques. On réutilise plutôt **son point d'accroche** et **ses utilitaires**, dans le processeur déjà dédié aux familiers.

**Un tirage par lancement, en deux temps :**

1. **Tirage au début de `apply_skill_effects`**, juste après le bloc `skill_power_mult` (`room.cpp:~4284`) :
   ```cpp
   // nouveau : familiar_passive_processor.hpp
   struct AffinityProc { const FamiliarSpecialPassive* aff = nullptr; };
   AffinityProc roll_affinity(entt::registry&, entt::entity caster, TickNumber tick);
   ```
   - On ne fait rien si `action.type == BASIC_ATTACK`, si le lanceur n'a pas de `FamiliarPassivesComponent`, si le familier n'a pas d'affinité ou si le délai interne court encore.
   - Le tirage utilise `rng_` du processeur (graine de la salle, jamais `rand()`).
   - En cas de réussite, le délai interne démarre tout de suite (`affinity_ready_tick = tick + icd`).
   - **Abysse** se consomme dans le même lancement : une variable locale `affinity_damage_mult` (1.0 sinon) multiplie `base_damage` et `scaling` à côté de `skill_power_mult` (`room.cpp:4729`). On ne touche **pas** au soin, d'où une variable séparée et non un repli dans `skill_power_mult`.
2. **Application à la fin de `apply_skill_effects`**, juste avant ou après le bloc `on_skill_used` (`room.cpp:~6434`), et **hors** de la condition `proc_processor_` :
   ```cpp
   void apply_affinity(entt::registry&, entt::entity caster, const AffinityProc&,
                       entt::entity primary_enemy, const AffinityContext& ctx,
                       TickNumber, EventBuffer&);
   // ctx : bool pvp ; std::function<bool(EntityId)> can_disable (le garde de la salle)
   ```
   - `primary_enemy` est le premier `result.damage_events[i].target_id` encore vivant et ennemi. À défaut, c'est la cible courante de l'IA du familier (cas des familiers soigneurs ou soutiens). À défaut encore, il n'y a pas d'effet sur un ennemi.
   - Les effets sur soi (Pierre, Mort, et le repli de Vide) n'ont pas besoin de cible.

Ce découpage règle de lui-même les compétences multi-coups et de zone : **un seul tirage par lancement**, appliqué à **une seule cible** (sauf Abysse, qui amplifie tout le lancement). Il n'y a pas de récursion, puisque les effets de l'affinité ne repassent ni par `on_damage_dealt` ni par `apply_skill_effects`.

**État à ajouter** dans `FamiliarPassivesComponent` (`components.hpp:782`) : `TickNumber affinity_ready_tick = 0;`.
**Signal PvP** : `set_pvp_room(bool)` sur le processeur, comme `proc_processor_->set_pvp_room(config_.is_pvp_mode())` (`room.cpp:126`).
**Délai interne** : lu dans `familiar_balance.json` par l'hôte de combat, au même endroit que `off_role_skill_multiplier` (`combat_host.cpp:679-690`), puis passé au processeur.

### 2.4 Effets exacts (identifiants de `stats/status_effects.json`)

Conventions :
- `stacks` = `stacks_to_apply` (contrat Option A : jamais de `value` sur un effet de la grille canonique) ;
- `durée` = `duration_override_sec` ;
- les valeurs de base sont multipliées par le `value_mult` de rareté **existant** (`classes/familiar/passives.json` `roll_rules.rarity_gating` : common 1.0, uncommon 1.0, rare 1.25, epic 1.25, legendary 1.25). C'est la même règle que les autres passifs, où « seule la magnitude suit la rareté ». La **chance** vient du tableau de l'affinité.

| Affinité | Cible | Statut / action | Charges | Durée | Valeur (base → ×1.25) | Notes |
|---|---|---|---|---|---|---|
| Sauvage | ennemi | `bleed` (Saignement, DoT physique, ATK de la **source** × 0.3 par tick et par charge, `status_manager.cpp:804`) | 1 | 3 s | — | durée par défaut des DoT : 6 s (`status_manager.cpp:532`), raccourcie à 3 s pour le budget |
| Givre | ennemi | `slow` (Ralentissement : +0.3 s de GCD par charge) **+** `chill` (Froid : DoT magique MAG × 0.1, aspect visuel du givre) | 1 + 1 | 3 s | — | ⚠ `chill` n'est **plus** un ralentissement (décision du 2026-09-02 : il ne reste qu'un DoT). Le vrai ralentissement, c'est `slow`. Le texte affiché reste « Froid : ralentit » |
| Givre légendaire | ennemi | `freeze` (Gel : contrôle dur, rompu par un critique) **au lieu** de `slow` | — | 1 s | — | seulement si `ctx.can_disable(target)` (garde de 5 s par cible) et si la cible n'est pas immunisée aux contrôles (filtré par `apply_effect`). Sinon : Froid normal. **En PvP : jamais de Gel**, toujours Froid |
| Braise | ennemi | `burn` (Brûlure, MAG de la source × 0.25 par tick et par charge, `status_manager.cpp:734`) | **2** | 3 s | — | 2 charges, car les familiers Braise sont attaque ou tank avec une MAG d'environ 0.5-0.7 × ATK. À 2 charges, la Brûlure vaut à peu près le Saignement |
| Faille | ennemi | `exposed` (Exposé : +10 % de dégâts subis par charge) | 1 | 4 s | — | défaut : 10 s (`stat_modifiers`), raccourci à 4 s. Effet de groupe : tout le monde en profite |
| Ombre | ennemi | `heal_reduction` (Anti-Soin : −15 % de soins reçus par charge) | 1, **jamais plus d'une charge venant d'une affinité** | 4 s (3 s en PvP) | — | appliqué seulement si la cible a 0 charge, sinon on rafraîchit la durée (sans ajouter de charge) |
| Pierre | soi | bouclier temporisé, id dédié `affinity_pierre_shield` (type SHIELD, `register_effect` comme dans `proc_processor.cpp:617-624`) | — | 4 s | **6 % des PV max du familier** → 7.5 % | `apply_shield` respecte `shield_blocked` |
| Vide | ennemi → soi | vol de Souffle (logique de `room.cpp:6093-6118`) : `steal = min(pct × Souffle max de la cible, Souffle actuel de la cible)` | — | instantané | **6 % du Souffle max de la cible** → 7.5 % | si la cible n'a pas de Souffle : le familier récupère **3 % de son propre Souffle max**. Émettre `MP_CHANGE` pour les deux entités |
| Mort | soi | `apply_triggered_heal(familier, amount)` | — | instantané | **5 % des PV max du familier** → 6.25 % | réduit par l'Anti-Soin et bloqué par `heal_blocked` (déjà géré) |
| Abysse | lancement | `affinity_damage_mult` sur les dégâts de **ce** lancement | — | ce lancement | **+40 %** → +50 % | ne touche ni le soin, ni les boucliers, ni les DoT déjà posés |

**Ordres de grandeur** (familier attaque légendaire, compétence d'environ 1.6 × ATK) :
- Saignement : 10 % × 0.3 ATK × 3 ticks ≈ +0.09 ATK par lancement, soit environ **+5-6 %** de dégâts ;
- Abysse : 10 % × 50 % ≈ **+5 %**, en pointes ;
- Brûlure à 2 charges : du même ordre ;
- Givre, Faille et Ombre sont de l'utilitaire ; Pierre et Mort, de la survie (≈ 0.6 % des PV max par lancement, en espérance).

L'écart entre commun (2 %) et légendaire (10 %) est voulu par le propriétaire.

### 2.5 Délai interne et anti-spam

- **Un tirage par lancement**, jamais par coup ni par cible (cf. §2.3).
- **Délai interne de 4 s par familier**, armé dès qu'un tirage réussit. Avec un GCD de 2 s, cela fait au plus un déclenchement tous les deux lancements, même en légendaire.
- Pas de tirage sur l'attaque de base, sur les ticks de DoT, ni sur les effets produits par une affinité (pas de récursion).
- **Plafonds par effet** :
  - Ombre : 1 charge au maximum venant d'une affinité ;
  - Givre : 1 charge de `slow` au maximum venant d'une affinité. Ne pas monter à 3 si la cible en a déjà, appliquer seulement si les charges sont < 1, sinon rafraîchir la durée ;
  - Gel : soumis au garde partagé de 5 s par cible.
- Règle anti-amplification de `status_effects.json` (`rules_anti_amplification_chain.rule_2`) : une même source ne pose pas d'anti-soin en même temps qu'un amplificateur de dégâts subis. C'est respecté, puisqu'un familier n'a qu'une affinité. Exposé (+10 %) peut se cumuler avec l'Exposé du Voleur jusqu'au plafond de 3 charges, comme toute autre source.

### 2.6 Garde-fous PvP (à valider en duel avant d'ouvrir, comme le demande la spec)

1. **Gel désactivé en PvP**. Un légendaire Givre y pose Froid (`slow` + `chill`). Un Gel de 1 s sur un joueur, même à 10 %, serait un contrôle dur aléatoire et non lisible.
2. **Froid** : 1 charge au plus venant des affinités, 3 s. Il passe déjà par la ténacité (−0 à 50 % de durée).
3. **Anti-soin (Ombre)** : 1 charge au plus (−15 %), 3 s en PvP. Il ne se cumule pas au-delà avec d'autres familiers Ombre, puisque le plafond est vérifié sur la cible. Option : nommer l'id `heal_reduction` avec un `source_tag`. Le plus simple reste de lire les charges actuelles avant d'appliquer.
4. **Vide** : le vol porte sur le Souffle **max** de la cible (7.5 % au plus), jamais en pourcentage du Souffle courant, pour éviter de vider un joueur à sec.
5. Dans le duel, on ajoute au banc PvP un test « deux familiers légendaires, même affinité » pour vérifier les plafonds.

---

## 3. Forme des données

### 3.1 Où ranger quoi

- **Table des affinités et chances par rareté** : dans `config/familiar_balance.json`, nouveau bloc `affinities`. Ce fichier est déjà lu par l'hôte de combat (`combat_host.cpp:679`) et par le service familier (`loadout_roller.cpp:155`).
- **Correspondance espèce → affinité** : dans le même bloc, `by_monster_species` plus `family_overrides` (clé = `species` de familiars.json, la famille). On garde ainsi une seule source, qui suit la règle de la spec (« familles tirées de `monster_species` ») tout en permettant les exceptions du §1.3.
  - Variante possible : un champ `affinity` dans chaque espèce de `entities/monster_species.json`. C'est plus naturel pour l'outillage d'équilibrage, mais ce fichier n'est pas encore lu par le serveur (« Pas encore lu par le serveur (travail V2) »). On l'écarte pour l'instant.
- **Le service** doit connaître la `monster_species` de l'archétype : ajouter `a.monster_species = item.value("monster_species", "")` dans `ArchetypeLoader` (`archetype_loader.cpp:~40`).

### 3.2 Exemple JSON (`config/familiar_balance.json`)

```json
"affinities": {
  "_comment": "Couche 2 des familiers (decision 2026-10-13, _meta/carnet/familiers_affinites.md). Un passif par famille d'espece, tire a CHAQUE competence lancee par le familier (pas l'attaque de base), un tirage par lancement, une cible. chance_by_rarity = rarete tiree a la capture. Les 'value' suivent le value_mult de rarete de classes/familiar/passives.json (comme les autres passifs). Resolu par le service familier, transporte en FamiliarSpecialEffect special='affinity_<id>', applique par FamiliarPassiveProcessor.",
  "chance_by_rarity": { "common": 2, "uncommon": 4, "rare": 6, "epic": 8, "legendary": 10 },
  "internal_cooldown_sec": 4.0,
  "effects": {
    "sauvage": { "name_fr": "Sauvage", "name_en": "Wild",   "icon": "ui/familiars/affinities/sauvage.png",
                 "target": "enemy", "status_id": "bleed", "stacks": 1, "duration_sec": 3.0,
                 "tooltip_fr": "{chance} % par competence : Saignement.", "tooltip_en": "{chance}% per skill: Bleed." },
    "givre":   { "name_fr": "Givre", "name_en": "Frost", "icon": "ui/familiars/affinities/givre.png",
                 "target": "enemy", "status_id": "slow", "extra_status_id": "chill", "stacks": 1, "duration_sec": 3.0,
                 "legendary_status_id": "freeze", "legendary_duration_sec": 1.0, "legendary_pvp": false,
                 "tooltip_fr": "{chance} % par competence : Froid (ralentit).", "tooltip_fr_legendary": "{chance} % par competence : Gel (1 s) ; Froid si la cible ne peut pas etre gelee." },
    "braise":  { "target": "enemy", "status_id": "burn", "stacks": 2, "duration_sec": 3.0, "...": "..." },
    "faille":  { "target": "enemy", "status_id": "exposed", "stacks": 1, "duration_sec": 4.0 },
    "ombre":   { "target": "enemy", "status_id": "heal_reduction", "stacks": 1, "max_stacks_from_affinity": 1,
                 "duration_sec": 4.0, "pvp_duration_sec": 3.0 },
    "pierre":  { "target": "self", "action": "shield_percent_max_hp", "value": 6, "duration_sec": 4.0 },
    "vide":    { "target": "enemy", "action": "steal_souffle_percent_max", "value": 6, "fallback_self_restore_percent": 3 },
    "mort":    { "target": "self", "action": "heal_percent_max_hp", "value": 5 },
    "abysse":  { "target": "cast", "action": "damage_percent_this_cast", "value": 40 }
  },
  "by_monster_species": {
    "rat": "sauvage", "chien": "sauvage", "corbeau": "sauvage", "renard": "sauvage", "sanglier": "sauvage",
    "loup": "sauvage", "hyene": "sauvage", "ovin_caprin": "sauvage", "bovin": "sauvage", "cervide": "sauvage",
    "cheval": "sauvage", "sanglier_loup": "sauvage", "batracien": "sauvage", "loutre": "sauvage", "cochon": "sauvage",
    "lievre": "sauvage", "blaireau": "sauvage", "ours": "sauvage", "chat_sauvage": "sauvage", "belette": "sauvage",
    "ragondin": "sauvage", "loup_garou": "sauvage", "serpent": "sauvage", "araignee": "sauvage",
    "scorpion": "sauvage", "tatou": "sauvage", "herisson": "sauvage",
    "scarabee": "pierre", "tortue": "pierre", "golem": "pierre",
    "cristal": "givre", "braise": "braise", "faille": "faille",
    "spectre": "ombre", "effroi": "ombre", "vide": "vide", "squelette": "mort",
    "abyssal": "abysse", "demon": "abysse", "archonte_dechu": "abysse"
  },
  "family_overrides": {
    "chacal_faille": "faille",
    "ours_fissure": "faille"
  }
}
```

### 3.3 Résolution côté service et transport (sans changer le `.fbs`)

- Nouvelle méthode `LoadoutRoller::resolve_affinity(const std::string& family, const std::string& monster_species, const std::string& rarity, float value_mult)`. Elle renvoie `std::optional<SpecialEffect>` avec :
  - `special = "affinity_<id>"` ;
  - `chance = chance_by_rarity[rarity]` ;
  - `stacks`, `duration` repris de la table ;
  - `value = value × value_mult` ;
  - `stat` = statut principal (`bleed`…) ;
  - `threshold` = 1 pour signaler « légendaire » (Gel).
- Elle est poussée dans `se_offsets` (`familiar_service.cpp:1140-1153`), **même si `rolled_passives` est vide**. Attention : la boucle actuelle est conditionnée à `!row->rolled_passives.empty()`, il faut sortir l'affinité de ce `if`.
- Le `FamiliarSpecialEffect` existant suffit. L'hôte de combat le copie déjà dans `FamiliarSpecialPassive` (`combat_host.cpp:9589-9604`). La seule chose à ajouter côté combat est la lecture de `internal_cooldown_sec`.
- Une espèce sans affinité (absente de la table) donne aucun effet, avec un `warn` au chargement.

---

## 4. Plan de mise en œuvre

### 4.1 Fichiers

**Données (`kanarion_database`)**
1. `config/familiar_balance.json` : bloc `affinities` (§3.2).
2. `scripts/validate_*` : chaque famille de `familiars.json` doit se résoudre en une affinité. Chaque `status_id` doit exister dans `stats/status_effects.json`. Les chances doivent couvrir les 5 raretés.
3. `_meta/carnet/familiers_affinites.md` : noter les décisions du §1.3 et la précision « Froid = `slow` + `chill` ».

**Service familier (`kanarion_back/services/familiar`)**
4. `src/db/archetype_loader.{hpp,cpp}` : lire `monster_species`.
5. `src/db/loadout_roller.{hpp,cpp}` : charger `affinities` (fail-soft, comme le reste) et ajouter `resolve_affinity(...)`.
6. `src/familiar_service.cpp:~1140` : pousser l'affinité dans `special_effects`, et l'exposer à la fiche (§4.3).

**Combat (`kanarion_back/server-combat`)**
7. `src/entities/components.hpp:782` : ajouter `affinity_ready_tick` à `FamiliarPassivesComponent`.
8. `src/combat/familiar_passive_processor.{hpp,cpp}` :
   - `roll_affinity`, `apply_affinity`, `set_pvp_room`, `set_affinity_icd_ticks` ;
   - aides internes : bouclier temporisé, vol de Souffle, plafonds de charges.
9. `src/combat/room.cpp` :
   - tirage après `:4284` ;
   - `affinity_damage_mult` en `:4729` ;
   - application près de `:6434` ;
   - `set_pvp_room` en `:141` ;
   - lambda `can_disable` sur `last_disable_tick_per_target_`, en mettant à jour cette table quand le Gel est posé.
10. `src/combat/combat_host.cpp:679-690` : lire `affinities.internal_cooldown_sec` et le transmettre à la salle et au processeur.

### 4.2 Tests

- `services/familiar/tests/unit/test_loadout_roller.cpp` (le fichier existe) :
  - chance par rareté (2/4/6/8/10) ;
  - `value × value_mult` ;
  - surcharge de famille prioritaire sur `monster_species` ;
  - espèce inconnue → aucun effet ;
  - un familier sans passif tiré reçoit quand même son affinité.
- `server-combat/tests/unit/test_familiar_affinity.cpp` (nouveau, à ajouter à `tests/CMakeLists.txt` à côté de `test_familiar_passive_stats.cpp:128`). Le `FamiliarPassiveProcessor` n'a aujourd'hui **aucun test** : on peut en profiter pour couvrir `on_hit_poison` et `on_crit_bleed`. Cas à couvrir :
  - avec chance = 100, chaque affinité pose le bon statut, le bon nombre de charges et la bonne durée ;
  - avec chance = 0, rien ne se passe ;
  - attaque de base : pas de tirage ;
  - compétence de zone sur 3 cibles : 1 tirage, 1 cible ;
  - délai interne : un 2e lancement dans les 4 s ne se déclenche pas, il se déclenche après 4 s ;
  - Ombre : 1 charge au maximum, même après 5 déclenchements ;
  - Givre légendaire en PvE : Gel ; dans les 5 s du garde : Froid ; en PvP : Froid ;
  - Mort sous Anti-Soin : soin réduit de 15 % ;
  - Vide : borné par le Souffle actuel, repli si la cible n'a pas de Souffle ;
  - Abysse : dégâts × 1.4, soin inchangé ;
  - déterminisme : même graine, mêmes déclenchements.
- Banc d'équilibrage : vérifier au `item_power_combat_probe` (ou au banc des familiers) que le légendaire attaque reste dans la fourchette ±10 % de la règle horizontale des runes.

### 4.3 Affichage client (`kanarion_client`)

- **Fiche du familier** : une ligne « Affinité » avec icône + nom + texte : « Sauvage — 6 % par compétence : Saignement ». Fichiers concernés : `scripts/ui/components/familiar_passive_row.gd` et `scripts/data/familiar_passive_db.gd`.
  - Règle R2 (le client ne dérive rien) : ajouter en fin de `FamiliarInstance` (`familiar.fbs`) `affinity_id:string` (29) et `affinity_chance:float` (30), remplis par le service. Le client prend nom, icône et texte dans les données.
  - Les écrans de capture et de choix (`familiar_choose_popup.gd`) affichent l'affinité de l'espèce avec la fourchette « 2-10 % selon la rareté ».
- **En combat** : pas de nouvelle animation (règle des runes : un petit éclat d'icône générique au-dessus de l'unité).
  - Le serveur marque les événements produits par une affinité avec `skill_id = "affinity_<id>"` (`STATUS_APPLIED`, `HEAL`, `MP_CHANGE`). Le client y réagit par l'éclat de l'icône d'affinité au-dessus du familier.
  - Les icônes de statut existantes (`bleed_drops`, `slow_chains`, `frost_aura`, `burn_flames`, `exposed_mark`, `anti_heal_aura`, `shield_aura`, `mana_drain_swirl`) s'affichent déjà sur la cible.
- **9 icônes d'affinité** à produire, `ui/familiars/affinities/<id>.png`. Rappel : on donne au propriétaire des prompts PixelLab dans son format, on ne génère rien via MCP.
- Tooltips FR/EN : dans la table `affinities.effects[*].tooltip_*`, avec `{chance}` remplacé par la valeur envoyée.

### 4.4 Charge estimée

| Lot | Charge |
|---|---|
| Données + validateur + décisions du §1.3 | 0.5 j |
| Service (chargeur, résolution, transport, champ de fiche) + tests | 1 j |
| Combat (processeur, 3 points d'accroche dans room.cpp, PvP, délai interne) | 1.5 j |
| Tests combat + banc d'équilibrage | 1 j |
| Client (ligne de fiche, éclat, tooltips) hors icônes | 1 j |
| **Total** | **≈ 5 j** (plus les icônes) |

### 4.5 Risques et points d'attention

1. **`uncommon` n'est jamais tiré à la capture** : `combat_host.cpp:4139-4144` code en dur common 70 / rare 25 / epic 4 / legendary 1, sans uncommon, alors que `familiar_balance.json` déclare des `drop_weight` 60/25/10/4/1 avec uncommon. Le palier à 4 % n'existera pas tant que ce tirage n'est pas branché sur la config. À corriger ensemble (petit lot séparé).
2. **Froid ≠ ralentissement dans les données** : depuis le 2026-09-02, `chill` n'est qu'un DoT ; le ralentissement réel est `slow`, sur le GCD. Il faut poser les deux, ou décider que « Froid » = `slow` seul.
3. **`room.cpp` est très fréquenté** (plus de 9 000 lignes, plusieurs sessions en parallèle) : conflits de fusion probables sur les zones `:4284`, `:4729` et `:6434`. Il faut garder les insertions courtes, la logique vivant dans le processeur.
4. **DoT partagés** : une cible n'a qu'une instance `bleed` / `burn` avec une seule `source_entity`, dont la stat (ATK/MAG) est lue à chaque tick (`status_manager.cpp:734-812`). Si le Guerrier du propriétaire saigne déjà la cible, le Saignement du familier peut ajouter des charges à cette instance et prendre (ou non) l'ATK de l'autre source. À vérifier dans `apply_one_stack` (quelle source est retenue au cumul).
5. **Familiers soigneurs ou soutiens avec une affinité offensive** (grenouille_soigneuse Sauvage, pretre_vide Vide…) : leurs compétences ne touchent pas d'ennemi. D'où le repli « cible courante de l'IA », sinon l'affinité serait presque morte pour ces rôles. À valider.
6. **Déséquilibre Sauvage** (57 %) : voir §1.3.
7. **Gel** : contrôle dur, même à 10 % et 1 s. Le garde partagé de 5 s ne visait que les monstres ; vérifier que l'ajouter aux familiers ne gêne pas les monstres (même table `last_disable_tick_per_target_`).
8. **Familiers déjà possédés** : l'affinité est calculée à chaque spawn depuis la config (rareté + espèce stockées). Aucune migration de base n'est nécessaire et tous les familiers existants la reçoivent.
