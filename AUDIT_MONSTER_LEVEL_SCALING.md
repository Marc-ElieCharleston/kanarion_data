# AUDIT — Scaling des monstres par niveau & format "chemin"

> Rédigé par l'agent DATA (2026-07-29) à passer au backend.
> Objectif produit : `desert_playtest` = LA map de test, un **chemin** où les monstres
> deviennent de plus en plus forts par niveau (lv1 → lv100 à terme, lv1-60 aujourd'hui).
> Diversité voulue : un même mob peut apparaître sur une **tranche de niveau** (ex: rat lv1-5).

---

## 1. État vérifié du moteur (code lu le 2026-07-29)

### 1.1 Spawn overworld — le `level_range` est IGNORÉ
`services/presence/src/presence_service.cpp` :
- L.3612 : `tmpl.level = base_level` (le template prend le `base_level` du mob).
- L.3638 : `out.level = override_level > 0 ? override_level : tmpl.level`.
- L.3786-3811 (parsing des bandes `spawn_areas[]`) : lit `mobs`, `bounds`, `count`,
  `max_stars`, `elite_pool`, `boss`. **NE LIT JAMAIS `level_range`.**

➡️ Conséquence : chaque mob spawn à son `base_level` **fixe**. Le `level_range` d'une bande
dans `zones.json` est purement décoratif. Un `mob_rat` (base_level 1) est **toujours lv1**,
quelle que soit la bande.

### 1.2 Combat — le monstre ne scale PAS par niveau
`server-combat/src/combat/room_manager.cpp` L.400-452 :
```cpp
StatsComponent stats = monster_template.stats;   // = base_stats FLAT
stats.attack_power *= spawn.atk_multiplier;        // × mult étoiles/monde
stats.defense      *= spawn.def_multiplier;
health.max          = spawn.hp_override>0 ? hp_override : base_hp;  // × mult étoiles
room->spawn_monster(..., monster_template.level, ...);  // level = AFFICHAGE seul
```
`room.cpp:5439` : `monster_identity.level = level` → stocké pour l'affichage + XP, **jamais**
utilisé pour recalculer les stats.

➡️ Il n'existe **AUCUN** `base + growth×(level-1)` pour les monstres (contrairement aux joueurs,
`combat_host.cpp:1650-1654`). Les stats d'un monstre = ses `base_stats` (fixées par la data à
son niveau voulu) × les multiplicateurs d'étoiles/danger.

### 1.3 Ce à quoi sert `level` aujourd'hui
- **Affichage** client (nameplate niveau, via `MONSTER_ZONE_STATE`, `monster_world.cpp:97`).
- **XP** : `loot_roller.cpp:38` `base_xp_for_level(level)` = `xp_to_next(level+1)/divisor`.
  Donc un mob de plus haut niveau donne **déjà** plus d'XP automatiquement.

---

## 2. Le problème

Le "chemin de mobs de plus en plus forts" fonctionne **uniquement** en plaçant des mobs
**distincts** de `base_level` croissant dans des bandes successives. Deux limites :

1. **Pas de tranche de niveau par mob.** On ne peut pas faire "rat lv1-5" : le rat est lv1 point.
   Pour couvrir lv1-5 il faut aujourd'hui 4-5 mobs distincts (rat_jeune, rat, rat_alpha…).
2. **Un "lv5 rat" serait un mensonge visuel.** Même si presence tirait un niveau dans la tranche,
   le combat afficherait "lv5" mais avec des stats de lv1 (aucun scaling). Juste un label + un
   peu plus d'XP.

➡️ Le level-range monstre **n'a de sens que si on ajoute le scaling par niveau côté moteur.**

---

## 3. Feature demandée — "Chemin" : level-roll + growth monstre

Deux mécanismes à câbler. **Le (B) est le cœur** ; le (A) est trivial une fois (B) en place.

### (A) Presence : bande `level_range` → tire un niveau au spawn
`presence_service.cpp`, boucle de spawn des bandes :
- Lire `spawn_area.level_range = [min, max]` (nouveau champ à consommer).
- Au spawn de chaque mob, tirer `instance_level = rng_uniform(min, max)`
  (ou pondéré vers le bas pour que le haut de bande reste rare — au choix).
- Poser ce niveau sur l'instance (le `MonsterDef.level` existe déjà, il suffit de le remplir
  par instance au lieu de laisser `base_level`).
- `MONSTER_ZONE_STATE` sérialise déjà `level` → le client affiche le bon niveau. Rien à changer client.

### (B) Combat : scaling des stats du monstre par niveau
`room_manager.cpp`, avant `spawn_monster`, appliquer un growth :
```
stat(L) = base_stat × (1 + GROWTH_PER_LEVEL × (L − base_level))
```
- `base_stats` = définies par la data au `base_level` du mob (inchangées, déjà tunées).
- `L` = niveau d'instance reçu (venu de presence, propagé jusqu'au combat).
- `GROWTH_PER_LEVEL` : ~0.08-0.10 (voir §5, je fournis la valeur / la table).
- Clamp : `L` reste dans `[base_level − k, base_level + k]` en pratique (la bande borne le roll
  près des base_levels de ses mobs → scaling modéré, pas de rat lv50).
- L'ordre reste : **growth par niveau D'ABORD, puis multiplicateurs d'étoiles** (les étoiles
  ajoutent la variance de difficulté par-dessus une base déjà au bon niveau).

**Propagation du niveau presence → combat :** aujourd'hui le combat relit `monster_template.level`
(= base_level) depuis sa propre copie de `monsters.json`. Il faut que **le niveau d'instance
tiré par presence voyage jusqu'au combat** (via l'encounter / le spawn payload), pas que le
combat reprenne le base_level. C'est le vrai point d'intégration inter-service.

---

## 4. Interaction avec les systèmes existants (à ne PAS casser)

| Système | Effet du scaling par niveau | Règle |
|---|---|---|
| **Étoiles** (atk/def/hp mult) | inchangé | s'appliquent APRÈS le growth par niveau |
| **XP** (`base_xp_for_level`) | synergie gratuite | un niveau tiré plus haut donne déjà + d'XP, auto |
| **xp_multiplier** (palier) | inchangé | se cumule sur l'XP (fodder 0.6 … boss 4.0), **déjà aligné en data, poussé `c499ab5`+`7ad9183`** |
| **danger_level** | inchangé | pilote l'intelligence IA, indépendant du niveau |
| **B1 (XP par palier)** | RETIRÉ backend | fait 100% en data via `xp_multiplier`. Ne rien recâbler. |

---

## 5. Ce que la DATA fournit (moi)

1. **`GROWTH_PER_LEVEL`** : je peux livrer soit
   - une **constante globale** (~0.09/niveau, simple), soit
   - une **table par rôle** (tank/brute montent + en hp/def, caster/assassin + en atk/mag),
     dérivée des courbes que j'ai déjà (`curve_hp/atk/def` du générateur de roster).
   ➡️ Reco : **constante globale d'abord** (livrable en 5 min, safe), table par rôle en V2 si besoin.
2. **`level_range` par bande** : la réorganisation de `desert_playtest` (voir §6).
3. **base_stats inchangées** — tout mon tuning actuel reste valide (base au base_level).

---

## 6. Réorganisation `desert_playtest` — LIVRÉE (`b0c5575`)

Fini les 13 bandes horizontales (rats lv1-5 = une bande entière). Nouveau format **poches
carrées compactes en grille 3×2 au centre de la map** (map de test = accès rapide à tous les
paliers sans traverser). Chaque poche = `bounds` serrés + `level_range` + pool mixte riche.

```
              ▲ SPAWN (0,-1550)
   ┌──────────┬──────────┬──────────┐
   │ lv51-60  │  lv1-10  │ lv41-50  │   rangée haute (Faille "en haut", accès direct)
   ├──────────┼──────────┼──────────┤
   │ lv31-40  │ lv11-20  │ lv21-30  │   rangée basse
   └──────────┴──────────┴──────────┘
   X[-1900,1900] Y[-1400,650] — 6 poches, 0 overlap, 111 mobs placés
```

| Poche | level_range | bounds x / y | Thème |
|---|---|---|---|
| pocket_start | 1-10 | [-575,575] / [-1400,-500] | Lisière du village (sous le spawn) |
| pocket_bandits | 11-20 | [-575,575] / [-250,650] | Camps de bandits / zélotes |
| pocket_wilds | 21-30 | [750,1900] / [-250,650] | Terres sauvages (gobelins, lézards) |
| pocket_confins | 31-40 | [-1900,-750] / [-250,650] | Confins tribaux |
| pocket_faille_seuil | 41-50 | [750,1900] / [-1400,-500] | Faille — le Seuil |
| pocket_faille_coeur | 51-60 | [-1900,-750] / [-1400,-500] | Faille — le Cœur + boss Avatar |

- **Marche DÉJÀ sans backend** : les mobs spawnent à leur `base_level` dans chaque poche
  (diversité par variété). Le `level_range` est prêt à devenir live dès que presence le lira (feature A+B).
- Poids par palier (fodder 18 / standard 15 / tough 9 / elite 5 / boss 2) → commons fréquents, boss rares.
- Extensible lv61-100 : ajouter des poches quand les mobs existeront (bords de map encore libres).

---

## 7. Résumé exécutable pour le backend

1. **Presence** : lire `spawn_area.level_range` → tirer `instance_level` par mob → le porter sur l'instance.
2. **Inter-service** : propager `instance_level` presence → combat (ne pas retomber sur base_level).
3. **Combat** (`room_manager.cpp`) : `stat(L) = base_stat × (1 + GROWTH × (L − base_level))`, growth AVANT les mults d'étoiles.
4. **Rien à toucher** : client (affiche déjà `level`), XP (déjà level-derived), étoiles, xp_multiplier.
5. **Data fournit** : `GROWTH_PER_LEVEL` (constante ~0.09 d'abord) + réorg des bandes.

**Ordre de livraison conseillé** : réorg bandes (data, débloque le test tout de suite, marche sans backend)
→ growth constant + level-roll (backend) → table growth par rôle (V2 si nécessaire).
