# Audit de scalabilité : familiers et monstres

**Date** : 2026-10-13. **Type** : audit en lecture seule, rien n'a été modifié dans les dépôts.

**Versions lues**
- back : `kanarion_back`, branche `vac_integration-all`, commit `96e51de5`
- data : `kanarion_database`, branche `vac_monstres-nouveaux`. Cette branche contient 227 monstres, 210 archétypes de familier, 103 familles, 51 espèces de monstre et 1030 empreintes.
- client : `kanarion_client`, `HEAD` = `37bc1c82`. Lu fichier par fichier avec `git show` (clone partiel).

**Objectif du propriétaire** : ajouter 40 monstres ou familiers doit se faire avec de la DATA seulement (JSON et sprites), sans toucher au code.

**Verdict** : on n'y est pas encore, mais on en est proche. Le gros du chemin de jeu lit déjà la data :
- IA par kit ;
- stats par espèce × archétype ;
- empreintes portant `family`, `role` et `rarity` ;
- loadouts validés au démarrage.

Ce qui bloque, c'est une douzaine de points précis :
- des tables recopiées dans le code ou dans les scripts Python ;
- des replis silencieux, le plus souvent vers le rat ;
- des listes d'identifiants VFX côté client ;
- l'absence de validateur qui relie monstres, familles, empreintes, assets et tables de butin.

Deux bugs **réels aujourd'hui** sont des conséquences directes de ces défauts :
- La rareté « uncommon » ne tombe jamais : 206 empreintes sur 1030 sont inatteignables.
- 59 familles de familier sur 103 n'ont pas de portrait. Elles s'affichent avec la tête du rat, sans aucun avertissement.

---

## 0. Ce qui est déjà sain (à garder comme modèle)

| Endroit | Pourquoi c'est bon |
|---|---|
| back `server-combat/src/ai/behaviors/behavior_factory.cpp` | Une seule `KitBehavior` : le rôle se déduit du kit. Il n'y a plus de table d'ids ni de repli « brute ». |
| back `combat_host.cpp:400-480` | La vérification croisée des loadouts et des `ai_profile` est **fatale** : le serveur ne démarre pas si elle échoue. |
| back `services/economy/.../economy_service.cpp:2144-2175` et `item_template.hpp:264-272` | `family`, `role` et `trace_rarity` sont lus depuis le template de l'objet. L'id n'est jamais découpé. |
| back `loot_roller.cpp:371-389` | La table « default » a été supprimée : un monstre sans table ne reçoit plus un butin inventé. |
| data `scripts/gen_familiar_traces.py` | Il ne garde aucune liste de familles en dur : il les lit dans `monsters.json`. Il a un mode `--check` et ne supprime rien sans `--prune`. |
| client `scripts/data/sprite_resolver.gd` et `sprite_tables.gd` | Les alias sont en data (`_meta/sprite_resolution.json`). Aucun repli ne change de genre (un animal ne devient jamais un humain), et chaque repli est signalé par un avertissement. |
| client `scripts/vfx/vfx_registry.gd` | Le rendu des statuts est piloté par `vfx_registry.json`. |

Ces patterns sont la cible : on les étend, on ne les réinvente pas.

---

## 1. Inventaire

**Catégories** :
- **LH** : liste en dur
- **NM** : nombre magique
- **RS** : repli silencieux
- **CC** : chaîne conditionnelle sur des ids, espèces ou rôles
- **TD** : table dupliquée
- **CN** : supposition de convention de nommage

**Gravité** :
- **BLOQUE** : bloque l'extension, ou produit un mauvais résultat dès aujourd'hui
- **RISQUÉ** : marche aujourd'hui, mais cassera sans bruit à l'extension
- **COSMÉTIQUE** : affichage ou dette sans effet de jeu

### 1.1 Back (`kanarion_back@vac_integration-all`)

| # | Emplacement | Cat. | Ce que ça bloque ou casse | Gravité |
|---|---|---|---|---|
| B1 | `server-combat/src/combat/combat_host.cpp:4139-4144` | NM, LH | La rareté des empreintes est tirée en dur à 70/25/4/1 (common/rare/epic/legendary), **sans uncommon**. La data dit 60/25/10/4/1 (`config/familiar_balance.json` `rarity_multipliers.*.drop_weight`). Conséquences : les 206 empreintes `_uncommon` ne tombent jamais, et tout réglage de rareté demande de recompiler. | **BLOQUE** (bug actif) |
| B2 | `services/familiar/src/db/incubation_loader.cpp:34-38` et data `config/familiar_incubation.json` `rarity_drop_weights` | TD | C'est une troisième copie des poids : chargée, mais jamais lue. Seconde ligne : `duration_for` (`:52-58`) retombe sur `common`, puis sur 300 s. `familiar_service.cpp:2166` a aussi `: 300`. | RISQUÉ |
| B3 | `combat_host.cpp:4164-4176` | LH, CC | L'empreinte garantie du tutoriel est codée en dur : `encounter_id != "tutorial_rat_solo"` et `"empreinte_souffle_rat_attaque_common"`. Changer la créature du tutoriel demande du code. | RISQUÉ |
| B4 | `combat_host.cpp:7067`, `7088-7099`, `7121-7128` (et `shared/flatbuffers/combat.fbs:171`) | LH, RS | Liste blanche héritée `rat_solo`/`group_contaminated`. Deux replis aggravent le cas : tout monstre de tutoriel absent devient **`mob_rat`** sans erreur, et le chemin hérité impose `mob_rat_tutorial` et `mob_rat` ×3. | RISQUÉ |
| B5 | `combat_host.cpp:6906` (`overlay_scenario_key`) | CC | `sparring_trinity` est mappé en dur vers `group_contaminated`. | COSMÉTIQUE |
| B6 | `combat_host.cpp:9675-9690` | CN, RS | Le sprite du familier vient du découpage de l'`archetype_id` (`familiar_` + espèce + `_<role>`). Si le préfixe manque, le familier prend le **sprite de classe joueur** (`class_id` : archer/warrior), sans aucun message. | RISQUÉ |
| B7 | `services/familiar/src/familiar_stat_helpers.hpp:95-113`, `familiar_service.cpp:115,131` | CN, TD | `derive_familiar_species()` déduit l'espèce de l'id, alors que `familiars.json` porte déjà `species`. La même logique est recopiée dans le client (C2). | RISQUÉ |
| B8 | `familiar_service.cpp:37-46` (`resolve_archetype`) et `:1055-1070` (`combat_get`) | RS | Un archétype inconnu retombe sur **`familiar_rat_<role>`**. Le commentaire « only the 4 rat archetypes ship as data » est obsolète : 210 archétypes sont livrés. Ce repli masque toute faute de data (un familier se bat avec les stats du rat sans que personne le voie). | **BLOQUE** (empêche de détecter les erreurs) |
| B9 | `services/familiar/src/gift_rules.hpp:18-41`, `db/pg_store.hpp:98-99`, `familiar_service.cpp:747` | LH, CN | Le rat d'Aldric repose sur `kTutorialRatArchetypePrefix = "familiar_rat_"` et l'offre `"aldric_rat"` en dur. Le serveur n'accepte qu'un `familiar_rat_*`. Le mécanisme `gift_offers` en data existe déjà, mais Aldric ne l'utilise pas. | RISQUÉ |
| B10 | `services/familiar/src/db/archetype_loader.cpp:40` | RS | `species = item.value("species", "rat")` : un archétype sans espèce devient un rat. | **BLOQUE** (silencieux) |
| B11 | `archetype_loader.cpp:81-85`, `familiar_service.cpp:1805-1807`, `db/loadout_roller.cpp:28-33` (`role_to_flavor`), migrations `050_familiars.sql:37` et `082_…:14` | LH, CC | Le vocabulaire des 4 rôles est recopié au moins 5 fois dans le back, plus 7 fois dans le client (C5 à C7). C'est un vocabulaire fermé : il ne bloque pas l'ajout de monstres, mais un 5ᵉ rôle demanderait plus de 12 modifications. | RISQUÉ |
| B12 | data `entities/familiars.json` : `class_id` et `ai_profile` dans chacun des 210 archétypes | TD | Ces deux champs sont des fonctions du rôle : attaque → archer/brute (75/75), tank → warrior/tank, heal → healer/healer, utilitaire → artisan/support. Chaque nouveau familier doit les recopier. | RISQUÉ |
| B13 | `server-combat/src/content/content_loader.cpp:1301-1440` (`parse_monster`) | RS | Valeurs par défaut silencieuses : `ai_role` "brute", `base_level` 1, `hp` 100, `mp` 50, `atk` 10, `def` 5, `threat_tier` "standard", `rarity` "normal", `species` "", capture désactivée. Une faute de frappe dans un champ donne un monstre plausible mais faux. Le contrôle des rôles (`combat_host.cpp:466-471`) **ne couvre pas `monsters.json`**. | **BLOQUE** (une erreur d'ajout passe en silence) |
| B14 | `shared/gameplay/monster_scaling_model.cpp:151-193` et `212-221` | RS | Une espèce ou un stade inconnu vaut ×1.0 sans rien dire. Un fichier d'espèces absent ou illisible donne un simple warn, et toutes les espèces passent à ×1.0. | **BLOQUE** (silencieux) |
| B15 | `server-combat/src/combat/room.cpp:7420-7425`, `loot_roller.cpp:376-383` | CN | Le visuel client vient de l'id auquel on retire `mob_`, mais pas `boss_`. Le butin, lui, retire `mob_` **et** `boss_`. Deux conventions différentes pour la même question, et aucun champ `sprite_id` ni `loot_table_id` obligatoire. | RISQUÉ |
| B16 | `loot_roller.cpp:384-389` et data `.github/workflows/validate.yml:118-127` | RS | Un monstre sans table de butin ne donne aucune ressource propre. Le commentaire affirme que « le validateur l'exige », mais **la CI ne vérifie que les références contenues dans les tables, pas la couverture des monstres**. Sur `vac_monstres-nouveaux`, **37 monstres** n'ont pas de table (`mob_rat_soigneur`, `mob_chat_sauvage`, `mob_ours_*`, …). | **BLOQUE** (bug actif) |
| B17 | `server-combat/src/ai/monster_ai.cpp:185-193` | RS | Un rôle IA inconnu devient « brute ». | RISQUÉ |
| B18 | `monster_ai.cpp:836-880` (`is_healer`/`is_tank`), `ai/behaviors/skill_util.cpp:257-262`, `kit_behavior.cpp:340-344`, `combat_host.cpp:6200` (`is_frontline`) | CC, CN | Plusieurs tests en dur : `ai_role == "healer" \|\| "support"`, `class_name == "priest"/"cleric"/"paladin"`, sous-chaînes `"heal"` et `"taunt"` dans l'id du skill, et `is_frontline = tank \|\| berserker`. | RISQUÉ |
| B19 | `combat_host.cpp:678-691` | RS | `off_role_skill_multiplier` : fichier ou clé absent → 1.0, puis bridé entre 0.1 et 1.0, sans erreur. | COSMÉTIQUE |
| B20 | `services/familiar/src/db/pg_store.cpp:60-64`, `familiar_stat_helpers.hpp:63` | RS | Une rareté inconnue vaut ×1.0 sans rien dire. Un multiplicateur hors de ]0, 5] est remis à 1.0. | RISQUÉ |
| B21 | `familiar_service.cpp:94,172,1874` | CN | L'id de la signature est composé : `"skill_familiar_sig_" + signature_template`. Aucun contrôle au démarrage ne vérifie que le skill composé existe (`check_loadouts` ne couvre que `skill_loadout`). | RISQUÉ |
| B22 | `combat/familiar_passive_processor.cpp:27-47` | CC | Chaîne `if/else` sur `p.special`. C'est un vocabulaire de **mécaniques** (légitime dans le code), mais un `special` inconnu en data est ignoré sans bruit. | RISQUÉ |

### 1.2 Data (`kanarion_database@vac_monstres-nouveaux`)

| # | Emplacement | Cat. | Ce que ça bloque ou casse | Gravité |
|---|---|---|---|---|
| D1 | `scripts/apply_familiar_species.py:26-61` `FAMILIAR_TO_MONSTER` (~100 entrées) | TD | Copie du champ `familiars.json.monster_species`, que **le script écrit lui-même à partir de cette table**. Ajouter une famille demande d'éditer le Python, sinon le script échoue avec `espèce sans correspondance`. | **BLOQUE** |
| D2 | `apply_familiar_species.py:66-113` `SPECIES_PASSIVE`, `TIERS`, `STAT_FR`/`STAT_EN` | LH | Les passifs d'espèce (nom et poids) vivent dans le script au lieu de `monster_species.json`. Une nouvelle espèce de monstre capturable demande d'éditer le Python. | **BLOQUE** |
| D3 | `scripts/apply_monster_v2.py:57-82` (`REMOVED`, `RENAMES`, `SPECIES_FIX`, `EXTRA_SPECIES`, `HUMANS`, `UNDECIDED_CAPTURE`, `SKIP`) et `scripts/balance/species_table.py:28-155` (`SPECIES`, `SPECIES_IDENTITY`, `STAGE`) | TD | `monster_species.json` est **régénéré** à partir de ces tables : `species_file()` écrase le fichier. `EXTRA_SPECIES` dit lui-même « mêmes valeurs que entities/monster_species.json ». On a donc deux sources pour la même valeur : une édition du JSON est perdue au prochain `apply`, et un ajout dans le Python seul diverge. `HUMANS` duplique `capturable`. | **BLOQUE** |
| D4 | `apply_monster_v2.py:44-55` (`ARCHETYPE_ID`, `AI_ROLE`, `MAGICAL`) | TD | La correspondance `stat_archetype` → `ai_role` et la liste des archétypes magiques ne vivent que dans le script. Elles devraient être dans `config/monster_scaling_model.json`. | RISQUÉ |
| D5 | `scripts/gen_familiar_traces.py:50-73` (`RARITIES` avec libellés et prix, `ROLES` avec libellés, `SHOP_BUY_PRICES`) | TD, LH | 4ᵉ copie des raretés, n-ième copie des rôles. Les prix de la boutique de Colette sont en dur dans le générateur au lieu de `npcs.json`. | RISQUÉ |
| D6 | `monsters.json` `familiar_capture.{signature_template, signature_name_fr/en, allowed_roles, drop_chance}` | TD | La signature est une copie de `familiars.json` (0 divergence aujourd'hui). `allowed_roles` doit rester l'ensemble des archétypes existants de la famille. `drop_chance` est une copie de `capture_rate_by_rarity[growth_tier]` (la data dit « changer ici PUIS re-appliquer aux mobs »), avec **4 divergences** : `mob_rat_soigneur` 0.03, `mob_rat_mage` 0.03, `mob_marcassin` 0.05, `mob_ourson` 0.05. | RISQUÉ |
| D7 | `familiars.json` `icon` | RS (côté data) | 76 icônes ne suivent pas `ui/familiars/<family>_<role>.png`. Les nouvelles familles (chat_sauvage, herisson, belette, ragondin, …) **pointent vers `rat_*.png`** : le rat sert de bouche-trou dans la data elle-même. | RISQUÉ |
| D8 | `.github/workflows/validate.yml` | — (validation absente) | La CI ne lance pas `apply_familiar_species.py --check`, `gen_familiar_traces.py --check` ni `apply_monster_v2.py --check`. Elle ne contrôle pas non plus la cohérence capture ↔ famille ↔ empreinte ↔ espèce, la couverture des tables de butin, ni la présence des assets. | **BLOQUE** |
| D9 | `config/familiar_balance.json` `affinities.species_to_affinity` / `family_overrides` | TD | L'affinité est un attribut de l'espèce, mais elle est stockée dans une table séparée indexée par espèce. Le serveur ne la lit pas encore : c'est le bon moment pour la déplacer. | COSMÉTIQUE |
| D10 | `_meta/sprite_resolution.json` `familiar_species_sprite` / `familiar_species_scale` | TD légère | Les alias et l'échelle sont en data (c'est bien), mais dans une table à part de la définition de la famille. **38 familles** n'ont aucun sprite qui résout (faune des vacances `art_pending` surtout), et rien ne le signale à la CI. | RISQUÉ |
| D11 | Vocabulaire « species » | CN | `familiars.json.species` désigne la *famille* du familier (103 valeurs, ex. `belier`). `monster_species` désigne l'*identité de stats* (51 valeurs, ex. `ovin_caprin`). `monsters.json.species` est l'espèce de stats, et `familiar_capture.family` est la famille (différente de l'espèce pour 80 monstres capturables sur 101). Le même mot désigne deux concepts : c'est la source des confusions B6, B7 et C2. | RISQUÉ |

### 1.3 Client (`kanarion_client@HEAD`)

| # | Emplacement | Cat. | Ce que ça bloque ou casse | Gravité |
|---|---|---|---|---|
| C1 | `scripts/data/familiar_portrait.gd:22,41-49` `_RAT_FALLBACK` | RS | **59 familles sur 103 n'ont pas de portrait** (`portraits_v2/` ou dossier parent) et s'affichent avec la tête du rat, sans avertissement. | **BLOQUE** (bug actif) |
| C2 | `familiar_portrait.gd:20,28-36` (`_ROLES`, `species_from_archetype`) | CN, TD | Copie de B7 côté client. Pourtant le serveur envoie déjà `species` (`familiar.fbs:36`, `presence.fbs:393`). | RISQUÉ |
| C3 | `scripts/vfx/effects/mage_skill_vfx.gd` : `:5` `CREATURE_MELEE_IDS` (67 ids), `:6-~80` `RENDERS` (preloads), `:84` `SELF_IDS` (31 ids), `script_for()` qui parcourt les constantes. Plus les 41 `scripts/vfx/creatures/*.gd`, chacun avec `const SKILL_IDS` (71 ids au total) et des dictionnaires de pose par clé (ex. `familiar_mastery01.gd:4,43`). | LH, CC | Un nouveau skill de monstre ou de familier demande de modifier 2 à 3 fichiers de code. `SELF_IDS` est redondant : `skills.json` porte déjà `target: "self"`. Un skill absent de toutes les listes n'a pas de rendu dédié, et rien ne le dit. | **BLOQUE** (pour tout nouveau skill ; un nouveau monstre qui réutilise des skills existants n'est pas bloqué) |
| C4 | `scripts/ui/familiar_choose_popup.gd:71-84` `SKILL_DISPLAY` | TD | 12 noms de skills sont en dur, alors que `familiar_skill_db.gd` lit déjà `classes/familiar/skills.json`. | COSMÉTIQUE |
| C5 | `familiar_choose_popup.gd:107` `STORAGE_CAP_DISPLAY := 50` | NM | Le serveur envoie `max_collection` (commentaire en data `_max_collection_note`). | COSMÉTIQUE |
| C6 | `familiar_choose_popup.gd:44-65,649,1687`, `familiar_incubation_screen.gd:28-31`, `familiar_icons.gd:40-47` (`_ROLE_FILE`, `_RARITIES`), `scripts/actors/familiar_proxy.gd:174-183` (`match role` → `class_id`, avec `_: "warrior"`) | LH, CC, RS | Les rôles et raretés sont recopiés à 7 endroits. `familiar_proxy` retombe sur warrior sans rien dire. | RISQUÉ |
| C7 | `scripts/combat/combat_role_map.gd:20-60`, `scripts/combat/visuals/hp_bar.gd:188-200` | CC | Chaînes `match` de `ai_role`/`stat_archetype` vers le rôle affiché. Un nouveau rôle IA en data s'affiche vide. | RISQUÉ |
| C8 | `scripts/data/familiar_trace_db.gd:55-56,69` `make_id(family, rarity)` | CN, RS | Format hérité **sans rôle** : produit des ids qui n'existent pas, donc un nom vide sans erreur. | COSMÉTIQUE |
| C9 | `scripts/data/loaders/monster_database.gd:199-~340` `_use_hardcoded_types()` | LH, RS | Environ 30 monstres historiques avec leurs stats en dur, utilisés si DataDB est absent. | RISQUÉ |
| C10 | `monster_database.gd:13,65-90,158-162` et `scripts/data/models/monster_data.gd:6-37` | TD, CN | Il faut un `resources/monsters/<id sans mob_>_data.tres` par monstre, qui **recopie des stats de jeu** (hp, atk, def, ai_role, tags). Le repli par famille (`_load_visual_family`, découpage sur `_`) n'affiche qu'un `print` en debug. 109 des 189 monstres actifs ont une ressource exacte. | RISQUÉ |
| C11 | `scripts/data/sprite_resolver.gd:75-90` | CN | Repli par famille en découpant l'id sur `_` (signalé, c'est bien). Mesuré sur les 189 monstres actifs : 109 exacts, 36 par famille, **44 sans aucun sprite** (bosses `boss_*`, faune des vacances, humains). Aucune CI ne le voit. | RISQUÉ |
| C12 | `scripts/actors/companion_overworld.gd:355-380` | CN, RS | Convention d'animation `<action>_<dir>`, miroir ouest → est, puis `_s`, puis le préfixe seul, puis **`avail[0]`** (n'importe quelle animation, sans avertissement). | RISQUÉ |
| C13 | `scripts/data/loaders/monster_skill_loader.gd:47-48` | CN | Teste l'id avec et sans `mob_`. | COSMÉTIQUE |
| C14 | `scripts/data/sprite_tables.gd` `SCALE_DEFAUT := 0.5` | RS | Si le fichier est absent, échelle par défaut avec un simple warning. Acceptable en prod, mais ce devrait être une erreur en dev ou en CI. | COSMÉTIQUE |

---

## 2. Correctifs pilotés par la data, point par point

**Règle générale.** Chaque repli silencieux devient l'un de ces deux cas :
- **(a)** une erreur au chargement (le serveur ne démarre pas, ou la CI échoue) ;
- **(b)** un repli **déclaré en data**, par exemple `"art_pending": true` qui affiche une silhouette neutre, et que la CI liste.

Rien ne tombe plus « par défaut » sur le rat, le guerrier ou la brute.

### 2.1 Raretés (B1, B2, B20, D5, C6)

**Source unique** : `config/familiar_balance.json`. Le bloc `rarity_multipliers` devient `rarities`, une **liste ordonnée** :

```json
"rarities": [
  {"id": "common",   "stat_multiplier": 1.0,  "drop_weight": 60, "color_hex": "#9E9E9E",
   "incubation_seconds": 120, "affinity_chance_pct": 2,  "trace_sell_price": 40,
   "label_key": "RARITY_COMMON"},
  {"id": "uncommon", "stat_multiplier": 1.07, "drop_weight": 25, "...": "..."}
]
```

Ce bloc absorbe trois tables qui existent aujourd'hui à part :
- `familiar_incubation.json.durations_seconds` ;
- le miroir mort `rarity_drop_weights` (à supprimer) ;
- `affinities.chance_by_rarity`.

**Back**
- Créer un `shared/domain/familiar_rarity_registry.{hpp,cpp}` chargé une fois et utilisé par combat (tirage B1), le service familier (multiplicateurs, durées) et l'économie.
- `roll()` fait un tirage pondéré sur `drop_weight`.
- Une rareté inconnue est une **erreur** (log error et refus), plus jamais ×1.0.
- Au démarrage, l'ensemble des ids doit être égal à la liste du `CHECK` SQL (`058`/`059`). Sinon : fatal.

**Python** : `gen_familiar_traces.py` lit `rarities` (libellés via les clés i18n, prix de vente) au lieu de `RARITIES`.

**Client** : `familiar_icons.gd` lit l'ordre et les ids depuis la même liste.

### 2.2 Rôles de familier (B11, B12, C5, C6)

**Source unique** : `familiar_balance.json.roles`. Le bloc fusionne avec l'actuel `role_profiles` :

```json
"roles": {
  "attaque": {"class_id": "archer", "ai_profile": "brute", "passive_flavor": "dps",
              "label_key": "FAMILIAR_ROLE_ATTACK", "hint_key": "FAMILIAR_ROLE_ATTACK_HINT",
              "color_hex": "#D9594D", "art_token": "attack", "order": 1,
              "base_stats": {}, "growth": {}}
}
```

- `familiars.json` perd `class_id` et `ai_profile`. On autorise une surcharge explicite par archétype, mais rare.
- `loadout_roller::role_to_flavor` lit `passive_flavor`.
- `is_valid_familiar_role` interroge le registre.
- Côté client : `familiar_proxy`, `familiar_choose_popup`, `familiar_incubation_screen` et `familiar_icons` lisent ce registre. Plus de `match`.
- Le `CHECK` SQL reste comme garde-fou d'intégrité, avec un contrôle au démarrage : les rôles de la data doivent être inclus dans ceux du `CHECK`.

### 2.3 Familles de familier et espèces de monstre (B6, B7, B8, B10, D1, D2, D3, D7, D9, D10, D11, C1, C2)

**Vocabulaire à figer partout** :
- **monster_species** : identité de stats (51), dans `entities/monster_species.json` ;
- **family** : lignée de familier (103).

**Le champ `familiars.json.species` est renommé `family`.** On peut garder un alias en lecture le temps d'une version.

**`entities/monster_species.json` devient la seule source** de l'espèce. Il gagne les champs suivants :

```json
"rat": {"identity": {}, "rate_bonus": {}, "capturable": true,
        "familiar_passive": {"name_fr": "Grignoteur", "name_en": "Gnawer", "weights": {"atk": 1.0}},
        "affinity": "rongeur"}
```

Le palier des passifs (`TIERS`) va dans `familiar_balance.json.species_passive_tiers`.

**Nouveau bloc `families`**, en tête de `familiars.json` ou dans un `entities/familiar_families.json` dédié :

```json
"families": {
  "belier": {"name_fr": "Bélier", "name_en": "Ram", "monster_species": "ovin_caprin",
             "sprite_id": "ram", "portrait_id": "belier", "overworld_scale": 0.5,
             "affinity_override": null, "art_pending": false}
}
```

Ce bloc absorbe trois tables :
- `FAMILIAR_TO_MONSTER` ;
- `sprite_resolution.json.familiar_species_sprite` et `familiar_species_scale` ;
- `affinities.family_overrides`.

**Archétypes** : `familiar_<family>_<role>` reste une convention d'id **vérifiée par le validateur**, mais **plus aucun code ne découpe l'id**. Le back et le client lisent `archetype.family` dans le registre. Le serveur transporte `family`, `sprite_id` et `portrait_id` dans les FlatBuffers. Il transporte déjà `species` : on ajoute des champs en fin de table, ce qui reste compatible.

**Replis à transformer**

| Repli actuel | Remplacement |
|---|---|
| B8 (`familiar_rat_<role>`) | Supprimé. Archétype inconnu → erreur `ARCHETYPE_UNKNOWN` et métrique. Le validateur garantit qu'aucune empreinte ne peut produire un archétype absent (0 cas aujourd'hui, ce qui prouve que ce repli est du code mort qui ne fait que masquer). |
| B10 (`species` "rat") | Champ obligatoire : le loader lève une exception. |
| B6 (sprite = classe joueur) | `sprite_id` obligatoire. Absent → pas de spawn visuel et une erreur, jamais un humain. |
| C1 (portrait rat) | `portrait_id` résolu. Absent ou `art_pending` → silhouette **neutre** `portrait_unknown.png` et `push_warning`. La CI liste les manquants. |
| D7 (`icon` → `rat_*.png`) | Champ `icon` supprimé de l'archétype : il se déduit de `portrait_id`. Pas de bouche-trou en data. |

**Scripts**
- `apply_familiar_species.py` lit `families[f].monster_species` et `monster_species[*].familiar_passive`. Il ne contient plus aucune table.
- `apply_monster_v2.py` est déplacé dans `scripts/migrations/2026-10-02_monster_v2.py`, comme migration figée qu'on ne relance plus.
- `species_table.py` **lit** `monster_species.json` au lieu de le définir.

### 2.4 Template de monstre (B13, B14, B15, B16, D4, D6, C9, C10, C11, C13)

**`monsters.json` : schéma strict.** Ces champs deviennent obligatoires :
- `id`, `name_fr`, `name_en` ;
- `stat_archetype` (∈ `monster_scaling_model.json`) ;
- `ai_role` (∈ `monster_ai.json`) ;
- `species` (∈ `monster_species.json`, ou `"none"` explicite pour le mannequin) ;
- `stage` (∈ `stages`, ou absent) ;
- `threat_tier`, `base_level`, `level_range`, `skills` ;
- `loot_table_id` (doit exister, une liste vide est permise) ;
- `visual`.

Les défauts « hp 100 / atk 10 / brute » disparaissent. Le loader C++ lève une erreur par champ manquant et refuse le démarrage, comme pour les loadouts. Le contrôle `check_roles` est étendu à `monsters.json.ai_role`.

**Nouveau bloc visuel** :

```json
"visual": {"sprite_id": "wolf", "scale": 1.0, "portrait_id": "wolf", "art_pending": false}
```

Le serveur envoie `sprite_id` (champ ajouté en fin de `monster.fbs`) au lieu de retirer `mob_` de l'id (B15). Le repli client par découpage de l'id (C10, C11) est supprimé : le choix est explicite en data (`"sprite_id": "rat"` pour `mob_rat_alpha`).

**Bloc de capture** :

```json
"familiar_capture": {"family": "rat", "growth_tier": "starter", "drop_chance": null}
```

- `drop_chance` est `null`, ce qui veut dire `capture_rate_by_rarity[growth_tier]`. Une valeur n'est permise que comme **surcharge explicite**, accompagnée de `"_override_reason"`. Les 4 divergences actuelles deviennent des surcharges assumées, ou sont corrigées.
- `allowed_roles` est supprimé : il se déduit des archétypes existants de la famille. On le garde seulement s'il restreint, et le validateur vérifie alors qu'il est inclus dans les archétypes.
- `signature_*` est supprimé (il est porté par l'archétype).

**Archétypes et rôles IA** : la correspondance `stat_archetype` → `default_ai_role` et `is_magical` va dans `monster_scaling_model.json.archetypes_lv1_standard.<id>` (D4).

**Modèle de scaling** (B14) : espèce ou stade inconnu, ou fichier absent → **fatal** au chargement.

**Client**
- `_use_hardcoded_types()` est supprimé (C9) : sans DataDB, on a une erreur, pas un faux bestiaire.
- `monster_data.tres` ne garde que le visuel (frames, échelle, noms d'animations) ; il ne recopie plus les stats. Il devient même optionnel si `visual` suffit (C10).

### 2.5 IA (B17, B18, C7)

`config/monster_ai.json.ai_roles.<id>` gagne :

```json
{"threat_class": "healer|tank|dps|support", "frontline": true, "display_role": "tank"}
```

- `is_healer`/`is_tank` et `is_frontline` lisent ces drapeaux (et les classes joueur depuis leur propre fichier de classes). Les sous-chaînes `"heal"`/`"taunt"` dans les ids sont remplacées par les `tags` des skills (`"heal"`, `"taunt"`), qui existent déjà.
- Rôle inconnu → erreur au démarrage, déjà couvert par l'extension de `check_roles`. Le `default_role` brute de `monster_ai.cpp:185-193` devient un `assert` ou une erreur.
- Client : `combat_role_map.gd` et `hp_bar.gd` lisent `display_role` et l'icône depuis le même JSON.

### 2.6 Compétences, signatures et VFX (B21, B22, C3, C4)

**Signature** : le validateur Python et le contrôle C++ au démarrage vérifient que `skill_familiar_sig_<signature_template>` existe pour chaque archétype. Variante plus propre : un champ `signature_skill_id` explicite.

**Passifs** : le back exporte la liste des `special` qu'il sait traiter (une constante unique, plus un test qui vérifie que chaque valeur a une branche). `validate_passives.py` refuse tout `special` hors de cette liste. Un passif « pas encore implémenté » doit porter `"engine_status": "planned"`, qui est listé, pas ignoré.

**VFX** : chaque skill gagne un bloc dans `skills.json` (familier, monstre, classes) :

```json
"vfx": {"renderer": "familiar_mastery01", "motion": "melee", "pose": "riposte"}
```

- `motion` vaut `melee`, `self`, `ranged` ou `ground`. `self` se déduit de `target == "self"` s'il est absent.
- Un registre `assets/vfx/skill_renderers.json` associe chaque `renderer` à un chemin de script ou de scène.
- `mage_skill_vfx.gd` résout par ce registre. `CREATURE_MELEE_IDS`, `SELF_IDS` et les `SKILL_IDS` des 41 scripts deviennent inutiles. Les `assert(id in SKILL_IDS)` deviennent `assert(id in renderer_config)`.
- Repli **déclaré** : `"vfx": {"renderer": "generic", "by": "vfx_type"}`.
- La CI vérifie que tout skill référencé par un monstre ou un familier a un renderer qui existe, ou un `"vfx": null` explicite.
- Pour ne rien perdre, la migration est **générée** par un script ponctuel qui lit les constantes actuelles.

**Noms des skills** : `SKILL_DISPLAY` est supprimé et remplacé par `FamiliarSkillDB` (C4).

### 2.7 Tutoriel et Aldric (B3, B4, B5, B9)

`config/tutorial_encounters.json.scenarios.<id>` gagne :

```json
{"overlay_key": "group_contaminated",
 "guaranteed_rewards": [{"item_id": "empreinte_souffle_rat_attaque_common", "quantity": 1, "personal": true}]}
```

- `grant_tutorial_trace` lit ce champ, avec la clé `encounter_id == "tutorial_" + scenario_id` donnée par la data.
- `overlay_scenario_key` lit `overlay_key`, et retombe sur l'id lui-même.
- Le chemin hérité `rat_solo`/`group_contaminated` est supprimé, et `tutorial_encounters.json` devient **obligatoire** (fatal s'il est absent).
- `resolve_monster_id` ne remplace plus rien par `mob_rat` : un monstre absent donne `UNKNOWN_MOB`. Le validateur garantit que tout `monster_id` de scénario existe.

**Aldric** : dans `familiar_balance.json.gift_offers`, on ajoute `"aldric_rat": ["familiar_rat_attaque", "familiar_rat_tank", "familiar_rat_heal", "familiar_rat_utilitaire"]` et `"default_offer_id": "aldric_rat"`. Un `offer_id` vide vaut l'offre par défaut, ce qui supprime `kTutorialRatArchetypePrefix` et `kTutorialRatOfferId`.

**Point d'attention** : `familiar_gifts` contient déjà des lignes `'aldric_rat'`. On garde l'id tel quel pour que les rejeux restent idempotents.

---

## 3. Architecture cible

### 3.1 Une source par concept

| Concept | Source unique | Lecteurs |
|---|---|---|
| Espèce de monstre (stats, capturable, passif familier, affinité) | `entities/monster_species.json` | scaling C++, service familier (passif), scripts, client (bestiaire) |
| Stade | `monster_species.json.stages` | scaling C++ |
| Archétype de stats → rôle IA par défaut, magique | `config/monster_scaling_model.json` | scaling, scripts |
| Rôle IA (drapeaux, rôle affiché, icône) | `config/monster_ai.json.ai_roles` | IA C++, client nameplate/hp_bar |
| Template de monstre (kit, butin, capture, visuel) | `entities/monsters.json` (schéma strict) | combat, presence, loot, client |
| Famille de familier (espèce, sprite, portrait, échelle, affinité) | `familiars.json.families` (ou `familiar_families.json`) | service familier, combat, client |
| Archétype de familier (famille × rôle, signature, mp de base) | `familiars.json.familiars` | service familier, combat |
| Rôle de familier (classe, profil IA, saveur, profil de stats, libellés, couleur) | `familiar_balance.json.roles` | back ×3, scripts, client |
| Rareté (stat_mult, poids de drop, durée, chance d'affinité, prix, couleur) | `familiar_balance.json.rarities` | combat (tirage), familier, économie, scripts, client |
| Empreintes | `items/consumables.json.familiar_traces`, **générées** par `gen_familiar_traces.py --check` en CI | économie, client |
| Skills et VFX | `classes/familiar/skills.json`, `skills/monster_skills.json` (+ bloc `vfx`), `assets/vfx/skill_renderers.json` | combat, client |
| Assets | conventions de chemin **calculées depuis les ids explicites** (`sprite_id`, `portrait_id`) dans un seul module (`sprite_resolver.gd`, `familiar_portrait.gd`) | client |
| Tutoriel et dons | `tutorial_encounters.json`, `familiar_balance.json.gift_offers` | combat, familier |

### 3.2 Registres

- **Back** : `shared/domain/` reçoit `MonsterCatalog` (templates, espèces, stades) et `FamiliarCatalog` (familles, archétypes, rôles, raretés, offres), avec un seul parseur par fichier. Ils sont chargés au démarrage par server-combat, le service familier et l'économie, qui suppriment leurs parseurs locaux (`archetype_loader`, `balance_loader`, `incubation_loader`, `parse_monster`). Toute incohérence lève une exception, ce qui donne `content_valid_ = false`, comme les loadouts aujourd'hui.
- **Client** : `scripts/data/familiar_catalog.gd` et `monster_catalog.gd` (sans `class_name`, en preload, selon la convention existante) lisent les mêmes JSON dans le sous-module `kanarion-meta`. Les UI ne connaissent ni les rôles, ni les raretés, ni aucun id.

### 3.3 Validateurs qui échouent fort en CI

Nouveau script **`scripts/validate_bestiary.py`** dans le dépôt data, lancé par `validate.yml`. Il vérifie :
1. le schéma de `monsters.json` (champs obligatoires, vocabulaires fermés : `stat_archetype`, `ai_role`, `species`, `stage`, `threat_tier`) ;
2. que tout monstre actif a un `loot_table_id` qui existe ;
3. que tout `familiar_capture.family` existe dans `families` et que l'espèce est `capturable: true` ;
4. que tout couple (famille, rôle) des archétypes respecte `id == familiar_<family>_<role>`, qu'il existe ≥ 1 rôle par famille capturable, et que `skill_familiar_sig_<template>` existe ;
5. que les empreintes sont exactement {familles capturées × rôles × raretés}, en lançant `gen_familiar_traces.py --check` ;
6. `apply_familiar_species.py --check` (les stats dérivées sont à jour) ;
7. que `drop_chance` vaut `capture_rate_by_rarity[growth_tier]`, ou porte une surcharge justifiée ;
8. que les raretés sont égales à `CHECK` SQL et que les rôles sont inclus dans `CHECK` SQL (listes copiées dans un `scripts/db_vocab.json`, lui-même relu par un test back) ;
9. que tout `monster_id` de `tutorial_encounters.json` et tout archétype de `gift_offers` existent ;
10. que tout `special` de passif est connu du moteur, sauf `planned`.

Côté client, un **`tests/test_bestiary_assets.gd`** (GUT/headless, déjà en place pour `test_familiar_portraits.gd`) parcourt `monsters.json` et `families`. Pour chaque `sprite_id`, il vérifie que `assets/animations/monsters/<id>_frames.tres` existe et contient les animations obligatoires (`idle_s`, `walk_s`, `attack_s`, …, selon un contrat écrit dans `_meta/sprite_resolution.json.animation_contract`). Il fait de même pour chaque `portrait_id`. Les entrées `art_pending: true` sont **listées en avertissement**, les autres font **échouer** le test.

Côté back, des **tests de chargement des vraies données** (`test_content_real_data.cpp`) chargent le sous-module data réel et vérifient `content_valid_ == true`.

### 3.4 Checklist « ajouter 40 monstres ou familiers », sans toucher au code

1. **Espèce** : si elle est nouvelle, une entrée dans `monster_species.json` avec `identity`, `rate_bonus`, `capturable`, `familiar_passive` et `affinity`.
2. **Monstre** : une entrée dans `monsters.json` avec les champs obligatoires et `visual.sprite_id`, plus `familiar_capture {family, growth_tier}` s'il est capturable.
3. **Butin** : une entrée dans `items/loot_tables.json.monster_loot_tables` (une liste vide est permise).
4. **Skills** : réutiliser des skills existants, ou en ajouter dans `skills/monster_skills.json` avec un bloc `vfx` (renderer existant ou `generic`).
5. **Famille** (si capturable) : une entrée `families.<family>` avec `monster_species`, `sprite_id`, `portrait_id` et `overworld_scale`.
6. **Archétypes** : une ligne `familiar_<family>_<role>` par rôle autorisé, avec `signature_template` et `mp` de base. Puis `python scripts/apply_familiar_species.py` pour recalculer les stats.
7. **Empreintes** : `python scripts/gen_familiar_traces.py`.
8. **Sprites** : `assets/animations/monsters/<sprite_id>_frames.tres` selon le contrat d'animation, et `assets/ui/familiars/portraits_v2/<portrait_id>.png`. Sinon `art_pending: true`, qui affiche une silhouette neutre et apparaît dans la liste CI.
9. **Placement** : zones et spawns (déjà en data).
10. **Vérification** : `python scripts/validate_bestiary.py`, la CI data, puis le test d'assets du client. Le serveur refuse de démarrer si quelque chose manque.

---

## 4. Plan de refactor par lots

**Ordre** : on pose d'abord les garde-fous (validateur), puis on retire les replis (les erreurs deviennent visibles), puis on unifie les sources. Chaque lot peut être fusionné seul. Les changements de schéma data sont **additifs** d'abord (nouveaux champs, lecture avec ancien nom en secours), puis les anciens champs sont retirés dans un lot de nettoyage.

**Risque de fusion général** : `combat_host.cpp` fait environ 9700 lignes et a été touché par 4 fusions récentes (`vac_shared-loot`, `vac_monster-gold`, `vac_familiar-passives-combat`, `vac_v2-monster-model`). La règle : **extraire vers de nouveaux fichiers** et ne laisser dans `combat_host.cpp` qu'un appel d'une ligne, pour réduire les conflits. Faire chaque lot depuis le dernier `vac_integration-all`, et en séquence quand deux lots touchent les mêmes fichiers (lots 1, 3, 4, 8).

| Lot | Taille | Dépôts | Contenu | Tests à ajouter | Risque de fusion |
|---|---|---|---|---|---|
| **L0** | S | data | `scripts/validate_bestiary.py` (contrôles 1 à 10 du §3.3), ajout dans `validate.yml` des `--check` de `apply_familiar_species.py` et `gen_familiar_traces.py`. Mode **erreur** pour la logique, **avertissement** pour les assets. Corriger ou assumer en data les 37 tables de butin manquantes et les 4 `drop_chance` divergents. | Le script lui-même, plus des fixtures cassées dans `scripts/tests/` (un cas par contrôle). | Nul (nouveau fichier). Fusionner dans `vac_monstres-nouveaux` **avant** sa fusion vers master, puisqu'il porte les 37 manques. |
| **L1** | S | back, data | **Rareté pilotée par la data** : `shared/domain/familiar_rarity_registry` et un nouveau `server-combat/src/loot/capture_trace_roller.{hpp,cpp}`. `combat_host.cpp:4139-4144` est remplacé par un appel. Suppression de `rarity_drop_weights` (data et `incubation_loader`). `duration_for` et `rarity_multiplier_for` : une rareté inconnue donne une erreur. | `test_capture_trace_roller` : graine fixe, 100 000 tirages ; chaque rareté est à ±1 % de son poids, **uncommon > 0** ; poids vides ou négatifs → échec de chargement ; l'id composé existe dans les templates. `test_rarity_registry` : ids égaux au `CHECK` SQL. | Faible : zone 4110-4180, retouchée par `vac_shared-loot` (pot commun). L'appel `roll_capture_traces` est conservé, seul le corps change. |
| **L2** | S/M | back, data | **Fin des replis rat côté familier** : suppression de `resolve_archetype` (rat) et du repli de `combat_get` (B8) ; `species`/`family` obligatoire (B10) ; Aldric par `gift_offers.aldric_rat` + `default_offer_id` (B9). Data : ajout de l'offre. | `test_gift_rules` : offre par défaut lue depuis la data, archétype hors offre → `TUTORIAL_RAT_ONLY` (renommé `NOT_IN_OFFER`). `test_archetype_loader` : `species` absent → exception. Test du service : archétype inconnu → erreur, pas de stats de rat. | Moyen : `familiar_service.cpp` (dernier passage : `vac_familiar-species-passive`). Coordonner avec toute branche « familier » ouverte. |
| **L3** | M | back, data | **Tutoriel piloté par la data** : `overlay_key` et `guaranteed_rewards` dans `tutorial_encounters.json`, suppression du chemin hérité et du repli `mob_rat`, fichier obligatoire (B3, B4, B5). Extraire `tutorial_plan_resolver.{hpp,cpp}`. Mettre à jour le commentaire de `combat.fbs:171`. | `test_tutorial_plan_resolver` : scénario inconnu → `UNKNOWN_SCENARIO` ; monstre inconnu → `UNKNOWN_MOB` (aucune substitution) ; la récompense garantie vient de la data ; `overlay_key`. | Moyen : `combat_host.cpp:6890-7130`. À éviter pendant un chantier onboarding. |
| **L4** | M | data puis back | **Familles et sources uniques des scripts** (D1 à D5, D9, D10, D11) : bloc `families` (généré une fois depuis `FAMILIAR_TO_MONSTER` et `sprite_resolution.json`), `familiar_passive` et `affinity` dans `monster_species.json`, `apply_familiar_species.py` et `gen_familiar_traces.py` sans tables, `apply_monster_v2.py` archivé, `species_table.py` en lecture. Back : `family`, `sprite_id` et `portrait_id` dans `familiar.fbs` et `presence.fbs` (champs ajoutés **en fin** de table) ; combat utilise `sprite_id` (B6) ; `derive_familiar_species` supprimé (B7). | Les scripts `--check` sont idempotents (deux exécutions = zéro diff). Test FB : un ancien client sans les champs fonctionne encore. `test_familiar_stat_helpers` : suppression des tests `derive_*`, remplacés par une recherche dans le registre. | Data : moyen (fichiers générés). Lancer les scripts **après** rebase et ne jamais fusionner à la main les JSON générés. Back : faible (champs additifs). |
| **L5** | M | data puis back | **Monstre strict** : bloc `visual.sprite_id` et `loot_table_id` sur les 227 monstres (script ponctuel), `familiar_capture` allégé (D6), `default_ai_role`/`is_magical` dans `monster_scaling_model.json` (D4). Back : `parse_monster` sans défauts (B13), `check_roles` étendu aux monstres, scaling fatal sur espèce ou stade inconnu (B14), `sprite_id` envoyé au lieu de retirer `mob_` (B15), `loot_table_id` obligatoire (B16). | `test_content_loader` : une fixture par champ manquant → échec. `test_monster_scaling_model` : espèce inconnue → exception. Chargement des vraies données → `content_valid_`. | Moyen à élevé : `content_loader.cpp` (touché par `vac_loot-affinity` et `vac_monster-gold`) et `room.cpp`. Faire la partie data d'abord (champs additifs, ignorés par l'ancien serveur), puis la partie back. |
| **L6** | M | client | **Catalogue familier côté client** : `familiar_catalog.gd` (familles, rôles, raretés) ; portrait par `portrait_id` avec silhouette neutre au lieu du rat (C1) ; `species_from_archetype` supprimé (C2) ; `SKILL_DISPLAY` supprimé (C4) ; `max_collection` serveur (C5) ; rôles et raretés depuis la data (C6) ; `make_id` supprimé (C8) ; `combat_role_map` et `hp_bar` depuis `monster_ai.json` (C7). | Étendre `tests/test_familiar_portraits.gd` : famille sans art → silhouette, **jamais le rat**. Nouveau `tests/test_bestiary_assets.gd` en mode avertissement. | Faible : surtout des fichiers UI isolés. Vérifier qu'aucune branche client « familier » n'est ouverte. |
| **L7** | L | data, client | **VFX pilotés par la data** (C3) : bloc `vfx` dans les skills, `skill_renderers.json`, script de migration qui lit les `SKILL_IDS`, `CREATURE_MELEE_IDS` et `SELF_IDS` actuels pour écrire la data, `mage_skill_vfx.gd` renommé `skill_vfx_router.gd` (le commentaire du fichier le demande déjà), poses par clé déplacées dans les configs de renderer. | Test : pour chaque skill de `skills.json` qui avait un rendu, le routeur choisit **le même script** qu'avant (comparaison avant/après générée). La CI vérifie que tout skill de monstre ou de familier a un `vfx` ou `null`. Les tests d'accents VFX existants (`test_archer_vfx_accents.gd`, …) passent toujours. | Moyen : 41 scripts créatures et le routeur partagé avec mage, artisan et archer. À faire hors période de tournoi, comme le note le fichier lui-même. |
| **L8** | M | back, data | **IA par drapeaux** (B17, B18) : `threat_class`, `frontline` et `display_role` dans `monster_ai.json` ; `is_healer`/`is_tank`/`is_frontline` lisent les drapeaux et les tags de skills ; `default_role` brute supprimé. | `test_monster_ai` : un healer est détecté par drapeau et non par sous-chaîne ; un skill nommé `…heal…` sans tag n'est **pas** compté comme soin ; rôle inconnu → erreur au chargement. | Moyen : `monster_ai.cpp`, `skill_util.cpp`, `kit_behavior.cpp` (`vac_monster-gcd` est récent dans cette zone). |
| **L9** | S | client | `_use_hardcoded_types` supprimé (C9) ; `monster_data.tres` réduit au visuel (C10) ; repli par découpage d'id supprimé au profit de `sprite_id` (C11, C13) ; contrat d'animation et suppression du repli `avail[0]` (C12) ; `SCALE_DEFAUT` en erreur en debug (C14) ; `test_bestiary_assets.gd` passe en mode **erreur** pour les entrées sans `art_pending`. | `test_bestiary_assets.gd` en mode strict. | Faible. Dépend de L5 (`sprite_id` en data). |
| **L10** | S | back, data | Nettoyage : retrait des anciens champs (`species` des archétypes, `class_id`/`ai_profile` par familier, `allowed_roles`/`signature_*` dans `familiar_capture`, `familiar_species_sprite`), `special` des passifs validés (B22), signature validée au démarrage (B21), `off_role` obligatoire (B19). | Le test de chargement des vraies données reste vert ; `validate_passives.py` refuse un `special` inconnu. | Faible, à faire en dernier. |

### Ordre conseillé et dépendances

Séquence : L0 → L1 → L2 → L3 → L4 → L5 → (L6 ∥ L8) → L9 → L7 → L10.
- **L1 et L2** corrigent les deux bugs visibles (uncommon jamais tiré, replis rat) et tiennent en peu de lignes.
- **L4 et L5** sont le cœur de la scalabilité. Une fois faits, une extension n'a plus besoin que de data.
- **L7** est le plus gros lot. Il ne bloque que les **nouveaux** skills : un monstre qui réutilise des skills existants n'en dépend pas.

### Notes de fusion avec `vac_integration-all`

- Les branches `vac_*` ouvertes au moment de l'audit (`vac_poison-cap-pvp`, `vac_shared-loot`, `vac_dungeon-keys`, `vac_monster-gcd`, `vac_loot-affinity`, …) touchent `combat_host.cpp`, `content_loader.cpp` et l'IA. Créer chaque lot depuis le **dernier** `vac_integration-all` et limiter `combat_host.cpp` à des appels (extraction en nouveaux fichiers).
- Les JSON générés (`familiars.json`, `consumables.json`, `passives.json`, `monster_species.json`) ne se fusionnent **jamais à la main** : on rebase le dépôt data, puis on relance les générateurs, puis `--check`.
- Les schémas FlatBuffers ne reçoivent que des champs **ajoutés en fin de table**, ce qui reste compatible avec un client plus ancien.
- Ne pas renommer l'offre `aldric_rat` en base (`familiar_gifts`), sous peine de casser l'idempotence des rejeux.

---

## Annexe : mesures (scripts lancés sur les fichiers extraits par `git show`)

- Familiers : 210 archétypes, 103 familles ; `archetype_id == familiar_<species>_<role>` sur 210/210. Rôles : attaque 75, utilitaire 74, tank 48, heal 13. `class_id`/`ai_profile` sont une fonction stricte du rôle.
- Capture : 164 blocs, dont 101 actifs ; 0 couple (famille, rôle) sans archétype ; 0 signature divergente. 3 familles ne se capturent sur aucun monstre (`chien_sauvage`, `scarabee_sables`, `serpent`). `rat` tank et utilitaire ne s'obtiennent que par Aldric.
- Empreintes : 1030 = 206 couples × 5 raretés, 0 manquante, 30 orphelines (conservées par `gen_familiar_traces.py` sans `--prune`). **206 « uncommon » ne tombent jamais** (B1).
- Monstres : 227, dont 189 actifs ; 1 sans espèce (`mob_training_dummy`). Tous les `ai_role` sont connus de `monster_ai.json`. **37 sans table de butin.**
- Assets client : **59 familles sur 103 sans portrait** (→ rat) ; **38 familles sur 103 sans sprite** qui résout ; 44 monstres actifs sur 189 sans sprite qui résout (36 autres passent par le repli de famille).
- VFX client : 67 ids en `CREATURE_MELEE_IDS`, 31 en `SELF_IDS`, 71 dans les `SKILL_IDS` des 41 scripts créatures.
