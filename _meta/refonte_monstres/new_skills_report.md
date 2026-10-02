# Nouvelles compétences de monstres : rapport

24 compétences (`new_skills.json`). Script de vérification : effets connus, charges canoniques (content_loader.cpp:640-676), patterns, aucune collision d'ID. **À intégrer dans `basic_skills` / `role_basic_skills.<rôle>` / `archetype_skills.<arch>.pool`** : load_monster_skills ne lit que ces blocs (content_loader.cpp:274-311).

## Identité
| Compétence | Mécanique | Preuve |
|---|---|---|
| gardien_egide | `shield_max_hp` pct 8, `allies` + ring_1_center | room.cpp:5506-5516, 8423-8509 ; IA kit_behavior.cpp:98-117 |
| gardien_bastion | `damage_reduction_up` ×3, `allies` + `all` (recentré sur le lanceur) | room.cpp:8384-8390 |
| brute_brise_garde | `shield_break` + `armor_down` ×3 + `shield_block` 4 s | content_loader.cpp:899, damage_calculator.cpp:223-226, status_manager.cpp:1833-1840 |
| assassin_saut_ombre | frappe portée 12, hors ligne de vue + `exposed` ×2 | content_loader.cpp:877-887 |
| controleur_malediction | rect_2x2 : `heal_reduction` ×2 + `silence` 1,5 s | silence soumis au verrou anti-chaîne room.cpp:2171 |
| invocateur_appel | bloc `summon` (mob_void_spawn, 1, -3) | content_loader.cpp:851-859, room.cpp:4129, kit_behavior.cpp:440-452 |
| enchanteur_hymne | `target: all` : `atk_up` ×3 → `allies`, `purge` 1 → `enemies` | room.cpp:5595-5601, 5956-5966, 8929 (précédent : litany_of_light) |

## Rôle de base
coup_bouclier : RD sur soi via `target: self` (room.cpp:5596). Renfort recoupe `skill_mob_support_bolster` : il faut en garder un seul.

## Espèces
`blind` porte `value: 30`, sinon -75 % (status_manager.cpp:1464). `mana_drain` et `curse_dot` ne sont pas canoniques : pas de `stacks_to_apply` (sinon FATAL). La peur de dread_howl est soumise au verrou anti-chaîne.

## Limites et alternatives
- **Téléportation** : `teleport_adjacent` est validé par la salle (room.cpp:3297), mais l'IA des monstres ignore toute compétence de déplacement (kit_behavior.cpp:435). Alternative livrée : frappe à portée 12 qui ignore la ligne de vue, sans déplacement.
- **Invocation** : elle n'est pas temporaire (aucune durée de vie dans room_summon.cpp). L'invoqué apparaît près de la ligne arrière ennemie, pas près du lanceur, et un seul `monster_id` est possible par compétence. D'où count 1 et une recharge de 30 s.
- **Briser un bouclier** : aucun effet ne détruit un bouclier. `purge` retire le premier effet positif, quel qu'il soit (status_manager.cpp:2494-2510). Brise-Garde traverse donc le bouclier et bloque les nouveaux.

## Code serveur nécessaire
1. Brancher `teleport_adjacent` dans KitBehavior (la cible est une entité, pas une case).
2. Durée de vie des invocations et placement « près du lanceur ».
3. Un effet qui retire spécifiquement les boucliers.

## Bugs existants repérés
- `skill_mob_assassin_shadow_strike` : jamais lancée par un monstre (kit_behavior.cpp:435). Son `target_rule: self` n'est pas lu (le chargeur lit `target`, content_loader.cpp:728), donc l'invisibilité irait sur l'ennemi.
- `skill_mob_support_shield_barrier` : `scaling: mag` est ignoré sans charges (room.cpp:5490), d'où un bouclier fixe de 100 à tout niveau. Il faut `shield_mag` + `pct`.
