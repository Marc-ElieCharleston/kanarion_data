# Audit Player Skills — Corrections 2026-03-13

## Résumé

Audit de cohérence description/data sur les 6 classes (90+ skills). Corrections appliquées directement.

---

## Corrections effectuées

### Warrior (2 fixes)

| Skill | Problème | Fix |
|-------|----------|-----|
| `skill_warrior_heavy_strike` | Bleed décrit mais pas dans effects[] | Ajouté `effects[]` avec bleed (value:1, duration:4s) |
| `skill_warrior_berserker_frenzy` | -15% DEF dans effects[] mais pas décrit | Description mise à jour pour mentionner le malus DEF |

### Mage (0 fixes)

Tout était déjà cohérent (cast_time, durations, effects[] tous présents et corrects).

### Healer (6 fixes)

| Skill | Problème | Fix |
|-------|----------|-----|
| `skill_healer_martyr_redemptive_wave` | **CRITIQUE** : description dit 50% mais scaling_percent=60 | `scaling_percent: 60` → `50` (description = design intent) |
| `skill_healer_lifewarden_nature_heal` | power_per_level:3 pas mentionné | Description: "+3/niv" ajouté |
| `skill_healer_lifewarden_natures_blessing` | power_per_level:7 pas mentionné | Description: "+7/niv" ajouté |
| `skill_healer_lightbringer_radiant_heal` | power_per_level:5 pas mentionné | Description: "+5/niv" ajouté |
| `skill_healer_lightbringer_cleanse_wave` | power_per_level:4 pas mentionné | Description: "+4/niv" ajouté |
| `skill_healer_lightbringer_absolution` | power_per_level:7 pas mentionné | Description: "+7/niv" ajouté |

### Archer (7 fixes)

| Skill | Problème | Fix |
|-------|----------|-----|
| `skill_archer_volley` | Bleed dans applies_bleed_stacks mais pas effects[] | Ajouté bleed (1 stack, 5s) dans effects[] |
| `skill_archer_falconer_falcon_strike` | Bleed décrit, pas d'effects[] | Créé effects[] avec bleed (1, 5s) |
| `skill_archer_falconer_talon_rend` | Bleed×2 dans custom, pas effects[] | Ajouté bleed (2, 6s) dans effects[] |
| `skill_archer_falconer_falcon_fury` | Bleed×3 dans custom, pas effects[] | Ajouté bleed (3, 6s) dans effects[] |
| `skill_archer_ballmaster_bounce_shot` | Bleed dans custom, pas d'effects[] | Créé effects[] avec bleed (1, 5s) |
| `skill_archer_gunslinger_double_tap` | Bleed dans custom, pas d'effects[] | Créé effects[] avec bleed (1, 5s) |
| `skill_archer_gunslinger_quickshot` | Description dit "CD 2s" mais cooldown=3.0 | Description corrigée: "CD 3s" |

### Rogue (8 fixes)

| Skill | Problème | Fix |
|-------|----------|-----|
| `skill_rogue_throw_dagger` | Bleed décrit mais pas d'effects[] | Créé effects[] avec bleed (1, 5s) |
| `skill_rogue_trickster_confuse` | duration_per_level:0.2 pas dans effects[] | Ajouté dans effect confusion |
| `skill_rogue_trickster_mislead` | duration_per_level:0.25 pas dans effects[] | Ajouté dans effect blind |
| `skill_rogue_trickster_disarm` | duration_per_level:0.2 pas dans effects[] | Ajouté dans effect disarm |
| `skill_rogue_duelist_en_garde` | buff_duration_per_level:0.3 pas dans effects[] | Ajouté dans effect en_garde_stance |
| `skill_rogue_duelist_riposte` | buff_duration_per_level:0.2 pas dans effects[] | Ajouté dans effect riposte_active |
| `skill_rogue_duelist_expose_weakness` | DEF reduction pas dans effects[] | Ajouté value:25, value_per_level:1, duration_per_level:0.4 |
| `skill_rogue_corsair_raid` | Blind value:75 non mentionné en description | Description corrigée: "-75% précision pendant 2s" |

### Artisan (non corrigé — issues mineures)

Issues identifiées mais non corrigées car nécessitent des décisions de design :
- 4 skills Musician avec `duration_scaling` non documenté en description
- `pb_sickening_mist` : effects[] manquant pour slow + atk_down
- `skill_artisan_expose_flaw` : team_damage_amp vs vulnerable dans effects[]
- Alchemist Catalyze : ambiguïté flat vs % scaling

---

## Issues restantes (nécessitent décision de design)

| Classe | Skill | Issue | Décision requise |
|--------|-------|-------|-----------------|
| Warrior | `guardian_protect_ally` | Shield 10% HP : via effect `damage_transfer` ou `shield` ? | Clarifier la mécanique |
| Warrior | `warlord_rally` | "alliés proches" vs pattern `row_3` | Clarifier le wording |
| Healer | `lifewarden_regrowth` | Description dit "-15% par rebond" mais pas de champ | Ajouter `bounce_damage_reduction: 15` ou retirer du texte |
| Rogue | `shadowblade_vanish` | "Prochain Backstab ×2" pas de data | Ajouter buff conditionnel ou retirer du texte |
| Artisan | 4 skills Musician | `duration_scaling` présent mais pas en description | Documenter ou retirer le scaling |
| Artisan | `sickening_mist` | Slow + ATK down décrits, pas d'effects[] | Créer effects[] |
| Artisan | `alchemist_catalyze` | "+30 par charge" = flat ou %MAG ? | Clarifier |

---

## Statistiques

| Métrique | Valeur |
|----------|--------|
| Skills audités | ~180 (6 classes) |
| Corrections appliquées | **23** |
| Critiques corrigées | 1 (healer redemptive_wave) |
| Issues restantes (design) | 7 |
