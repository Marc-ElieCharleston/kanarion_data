# Retrait des auto-attaques — inventaire et migration de la vitesse d'attaque

**Décision (2026-07-30, Charleston) : le retrait des auto-attaques est définitif.**

Ce document conserve la trace de tout ce qui dépendait de la vitesse d'attaque, et de ce
par quoi chaque site a été remplacé. Il sert de référence si la décision est un jour révisée.

## Pourquoi la stat est morte

`attack_speed` (DB) est converti en `haste` (`combat_profile_builder.cpp:207`), et `haste`
n'est lu qu'à un seul endroit dans tout le backend :

```cpp
// room.cpp:291, 1245, 1270, 5355
TickNumber interval = aa.get_interval(stats.haste);   // intervalle d'auto-attaque
```

Le GCD, lui, vient d'une constante de config (`config_.gcd_duration_ticks`) et n'est pas
influencé par `haste`. Sans auto-attaques, la stat ne pilote donc plus rien.

**Les deux autres stats de tempo sont des fantômes, indépendamment des autos :**

| Stat | Plombée jusqu'à | Appliquée ? |
|------|-----------------|-------------|
| `haste` / `attack_speed` | `StatsComponent` | Oui, mais uniquement sur l'intervalle d'auto-attaque |
| `cooldown_reduction` | `StatsComponent`, cap 40% documenté | **Non.** `room.cpp:2797` n'applique que le multiplicateur de phase de boss |
| `cast_speed` | `StatsComponent`, cap 50% documenté | **Non.** `room.cpp:2814` : `complete_tick = current_tick_ + cast_time_ticks` |

Ticket **BE-6** : appliquer `cooldown_reduction` et `cast_speed`. Sans lui, le jeu n'a plus
aucun axe de tempo fonctionnel.

## Chiffrage de la perte

Simulation sur 120s (GCD 2.0s, autos au timer indépendant à 2.86s pour `attack_speed 0.7`,
cooldowns et coûts en Souffle réels, rotation gloutonne sur les skills de base) :

| Classe | Part des autos dans le DPS soutenu |
|--------|-----------------------------------|
| Healer | 74.5% |
| Archer | 68.4% |
| Artisan | 68.0% |
| Warrior | 67.5% |
| Rogue | 63.8% |
| Mage | 54.0% |

La cause n'est pas la puissance des autos mais le **temps mort** : entre cooldowns et Souffle,
27% à 66% des GCD étaient déjà vides, et les autos comblaient chaque trou gratuitement.

**Compensation retenue : un filler gratuit par classe** (clé `class_filler`, hors budget de
points, 100% de la stat primaire, coût 0, cooldown 0). Après ajout, les GCD vides retombent
à **0%** et le DPS revient à -2% / -8% de l'ancien niveau pour les classes physiques, -26%
pour le Mage (volontaire : il était le moins dépendant des autos, donc le plus avantagé par
leur retrait).

## Migration appliquée

Règle : conserver la puissance. `atk_speed_up`, `atk_up`, `damage_percent_up` et
`accuracy_up` partagent la même grille canonique (5% par charge, max 5 charges), donc un
échange 1:1 du nombre de charges laisse la force inchangée. Anti-collision : si le skill (ou
le pool) portait déjà l'effet cible, on prend le candidat suivant.

| Rôle | Avant | Après (par ordre de préférence) |
|------|-------|--------------------------------|
| Buff offensif | `atk_speed_up` | `damage_percent_up` > `atk_up` > `accuracy_up` |
| Malus offensif | `atk_speed_down` | `damage_percent_down` > `atk_down` > `accuracy_down` |
| Incantation | `cast_speed_down` | `damage_percent_down` > `accuracy_down` |

### Volumétrie

| Site | Nombre | État |
|------|--------|------|
| Effets dans `effects[]` | 47 | Remplacés |
| Références dans `buff_pool` / `debuff_pool` (Mage) | 6 | Remplacées |
| Descriptions FR/EN mentionnant la vitesse d'attaque | 74 | Réécrites |
| Passif inné Archer (`on_auto_attack`) | 1 | Recâblé sur `on_skill_cast` |
| Stat `attack_speed` dans les blocs de stats | 29 | **Laissée en place** (voir ci-dessous) |
| Mécaniques liées aux autos | 11 | **À trancher** (voir ci-dessous) |

Répartition des 47 effets : 28 `atk_speed_up` → `damage_percent_up`, 13 `atk_speed_down` →
`damage_percent_down`, 2 → `atk_up`, 2 → `accuracy_up`, 2 `cast_speed_down` →
`damage_percent_down`.

## Ce qui reste ouvert

**La stat `attack_speed` dans les blocs de stats (29 sites)** — `class_base_stats.json`,
`class_growth.json`, `panoplies.json`, `equipment*.json`, `summons.json`, `pet_balance.json`,
`game.json`. Elle est conservée pour l'instant : la retirer casserait les schémas de stats et
les panoplies. Elle est simplement inerte. À nettoyer si BE-6 ne rebranche pas `haste` sur
autre chose.

**Les mécaniques liées aux autos (11 sites)** — `autos_generate_momentum`,
`buff_magic_on_autos`, `bonus_double_hit_per_charge`, `buff_attack_speed`,
`double_attack_chance`, `mark_refresh_on_hit`. Elles ne se déclencheront plus jamais.
Concentrées sur le Mage (6) et l'Archer (3).

**Les noms de skills bâtis sur la vitesse** — la plupart décrivent le geste et restent
valides (« Tir Rapide », « Entaille Rapide »). Trois désignent littéralement la stat et
mériteraient un renommage : `skill_healer_cantor_hymn_of_haste` (Hymne de Hâte),
`skill_mob_support_haste` (Hâte), `skill_artisan_musician_tempo_shift` (Changement de Tempo).

**`each_hit_can_crit` (25 sites) survit** : ce champ est lié au `hit_count` des skills
multi-coups, pas aux auto-attaques. Ne pas le retirer par erreur.

## Tickets backend liés

1. **BE-1** — `percent_per_level` jamais appliqué (`room.cpp:3327`, pas d'`effective_scaling()`).
2. **BE-6** — `cooldown_reduction` et `cast_speed` jamais appliqués.
3. **BE-7** — charger la clé `class_filler` (copie du bloc `signature_movement`, `content_loader.cpp:320`).
4. **BE-8** — check `same_target_skill_cast`, pour rendre son identité exacte à l'inné Archer.
