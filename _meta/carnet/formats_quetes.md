# Formats de quêtes (ce qu'on peut coder une fois, puis écrire en texte)

Statut : proposition (2026-10-03). Le jeu aura une centaine de quêtes, et plus : il faut un petit
nombre de **types d'objectifs codés une fois**, le reste n'est que du texte et de la data.

## Ce que le serveur gère déjà

`kanarion_back/services/quest/src/db/objective_templates.hpp` (`SUPPORTED_TEMPLATES`, ~40) :

| Famille | Types |
|---|---|
| Parler, aller | `talk_to_npc`, `enter_zone` |
| Combat | `kill_mobs`, `kill_mobs_in_zone`, `win_combats`, `win_combats_in_zone`, `defeat_boss`, `defeat_elite`, `clear_star_packs`, `complete_dungeon`, `win_arena`, `tutorial_combat_complete` |
| Objets | `loot_item`, `buy_item`, `sell_item`, `use_item`, `craft_item`, `equip_item`, `enhance_item` |
| Familiers | `capture_familiar`, `deposit_familiar_trace`, `familiar_learn_skill`, `activate_familiar`, `choose_familiar`, `claim_hatched_familiar`, `claim_familiar_gift` |
| Système | `reach_level`, `join_guild`, `recruit_mercenary`, `recruit_party_members`, `spend_skill_point`, `spend_stat_points`, `upgrade_passive`, `assign_quickslot`, `open_ui_screen`, `receive_blessing`, `manual` |

Déjà en data : `prerequisites` (liste), `chain_next`, `min_level`, `rewards` (xp, or, objets,
objet au choix), `moral_choice` / `moral_choices`.

## Ce qui manque pour les histoires (à coder une fois)

1. **Le choix** : un dialogue à 2 ou 3 réponses qui **pose un drapeau** (ex. `dorn_warned`) et fait
   bouger **compassion / rancune**. **Les `moral_choice` existent dans `world/quests.json`, mais le
   service de quêtes ne les lit pas** (aucune occurrence côté serveur) : aujourd'hui ces choix n'ont
   aucun effet.
2. **Des conditions sur les drapeaux** : `requires_flags` / `forbids_flags` sur une quête, et **des
   PNJ visibles ou non selon les drapeaux** (phasing par joueur : Matthis absent, Harlan assis).
3. **`deliver_item`** : remettre un objet à un PNJ (un `talk_to_npc` qui consomme un objet) : la
   lettre de Bastien, le repas pour Ezra.
4. **`complete_scenario`** : une petite **instance de combat scénarisée** (escorte de Corbin, antre de
   la Grande Ourse, défense du hameau, combat d'Harlan) plutôt qu'une escorte dans le monde. Même
   principe que le tutoriel d'arène existant.
5. **`take_part_in_event`** : participer à un événement (événements de Fissure).

Bonus pour les boss d'histoire : des **dialogues à des seuils de PV** (Harlan, tous les 20 %).

## Les 5 formats

| Format | Recette | Exemple |
|---|---|---|
| **Messager** | parler à A → parler à B (→ remettre un objet) | Gaspard et Hector |
| **Chasse** | tuer X / loot X sur un monstre | quêtes de zone |
| **Commerce** | acheter / fabriquer / remettre | une potion pour Aelina |
| **Exploration** | aller à un lieu / participer à un événement | trouver le hameau |
| **Choix** | dialogue à branches → drapeau (+ compteur) | prévenir les frères ou non |

Une **histoire** = une chaîne de quêtes de ces formats, reliées par des drapeaux. Écrire une quête =
choisir un format + écrire le texte.

## Fiche type pour écrire une quête

- id, type (principale / histoire / répétable), niveau minimum ;
- conditions : quêtes prérequises, drapeaux requis / interdits ;
- étapes : format + cible (PNJ, monstre, objet, zone) + quantité ;
- textes : donner, en cours, terminer (FR + EN) ;
- choix éventuel : réponses → drapeau posé → compteur ;
- récompenses ; PNJ qui apparaissent / disparaissent après.
