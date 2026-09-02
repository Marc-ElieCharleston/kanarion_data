# Plan — Un déplacement signature par sous-classe

**Statut : DESIGN SEUL. Ne rien écrire en JSON tant que BE-S9 n'est pas livré.**
Le moteur ne sait charger qu'**un** `signature_movement` par classe de base
(`content_loader.cpp:338`, map `base class_id -> move` dans `skill_registry.hpp:66`), et le grant
résout explicitement la sous-classe vers sa base avant le lookup (`room.cpp:6196-6199`).
Vingt-quatre sorts écrits aujourd'hui seraient vingt-quatre sorts que personne ne recevrait.

Rédigé le 2026-09-02. À relire et arbitrer avant mise en JSON.

---

## Le problème qu'on résout

Le déplacement est aujourd'hui porté par la **classe de base**, donc les quatre sous-classes
héritent du même. Une Charge sur un Guardian est son métier : il colle le front et il tient.
La même Charge sur un Berserker le pose au rang 2, d'où sa portée de 2 couvre les rangs 0 et 1,
c'est-à-dire toute l'arrière-garde ennemie. Le contournement de la ligne de front, que
`combat/targeting.json` interdit pourtant noir sur blanc aux classes de contact, passe par le
déplacement.

Un déplacement par sous-classe règle ça à la source : c'est l'identité de la sous-classe qui
décide de ce que son déplacement a le droit de faire.

## Ce que le moteur sait déjà faire

Six types, `content_loader.cpp:755-760` : `teleport_adjacent`, `dash_line`, `self_move`, `pull`,
`pull_to_center`, `swap`. Modes : `free`, `flee`, `adjacent_enemy`.

**Deux inconnues à lever côté moteur avant d'écrire le JSON :**

1. **La poussée n'existe pas.** Il n'y a que `pull`. La « flèche qui fait reculer » demande soit un
   `push`, soit un `pull_distance` négatif, dont je n'ai pas vérifié s'il est clampé. Deux sorts
   ci-dessous en dépendent (Ballmaster, Gunslinger) et portent la mention **[POUSSÉE]**.
2. **`swap` accepte-t-il une cible ennemie ?** Il n'est utilisé aujourd'hui que sur un allié
   (`skill_healer_guardian_swap`). Deux sorts en dépendent, mention **[SWAP ENNEMI]**.

## Conventions retenues

- Tier `signature`, `mana_cost: 0`, cooldown 20 à 30s, comme les six déplacements actuels.
- Portée de déplacement **2 ou 3** par défaut. Seul le Rogue garde une portée longue : décision
  produit du 2026-09-02, sans elle une portée de base de 2 le laisse mourir dans les dégâts
  collatéraux sans jamais placer son burst.
- **Aucun déplacement de classe de contact ne fait atterrir au-delà du front ennemi** (rang 4),
  sauf Rogue. C'est ce qui règle le cas Berserker.
- IDs : `skill_<classe>_<sousclasse>_<nom>`.
- FR source, EN traduction, pas de tirets cadratins, « Souffle » jamais « Mana ».

---

## WARRIOR — base : Charge, `dash_line` 3

| sous-classe | sort | type | portée | effet à l'arrivée |
|---|---|---|---|---|
| guardian | **Rempart / Bulwark** | `dash_line` | 3 | `taunt` sur les ennemis adjacents |
| berserker | **Ruée Sanglante / Blood Rush** | `dash_line` | **2**, ne dépasse pas le front | `atk_up` 2 charges |
| weaponmaster | **Pas de Maître / Master's Step** | `self_move` | 2 | `crit_chance_up` 2 charges |
| warlord | **Ordre de Repli / Fall Back** | `swap` allié | 4 | l'allié échangé gagne `damage_reduction_up` 2 charges |

Le Guardian garde une charge pleine : il va au contact et il tient, c'est son métier. Le Berserker
perd exactement ce qu'il ne devait pas avoir, et récupère de la puissance à la place. Le Warlord
extrait un allié du danger et prend sa place, ce qui est littéralement son rôle d'aura protectrice.

## MAGE — base : Clignotement, `self_move` 2

| sous-classe | sort | type | portée | effet à l'arrivée |
|---|---|---|---|---|
| elementalist | **Pas de Givre / Frost Step** | `self_move` | 3 | `chill` 2 charges sur les ennemis adjacents |
| occultist | **Faille Courte / Short Rift** | `self_move` | 3 | `corruption` 2 charges sur la case de départ |
| cardmaster | **Battage / Shuffle** | `self_move` | 3 | tire 1 amélioration au hasard dans son pool |
| spellblade | **Lame Fendue / Split Blade** | `dash_line` | 3 | dégâts magiques sur la cible percutée |

Le « tp qui gèle » que tu décrivais. L'Occultiste laisse une trace là où il était, ce qui colle à sa
ligne de dégâts qui s'installent. Le Cardmaster réutilise le schéma de tirage aléatoire déjà gelé.

## HEALER — base : Échange Gardien, `swap` 5 (à retirer)

Le swap est remplacé, tu avais raison qu'il n'a pas beaucoup de sens.

| sous-classe | sort | type | portée | effet à l'arrivée |
|---|---|---|---|---|
| lifewarden | **Veille Rapprochée / Close Watch** | `teleport_adjacent` allié | 4 | `heal_over_time` 3 charges sur l'allié rejoint |
| lightbringer | **Course de Lumière / Light Dash** | `teleport_adjacent` allié | 4 | dissipe un debuff sur l'allié rejoint |
| cantor | **Refrain Mobile / Walking Refrain** | `self_move` | 3 | `heal_power_up` 2 charges aux alliés adjacents |
| martyr | **Interposition / Interpose** | `teleport_adjacent` allié | 4 | prend une part des dégâts de l'allié pendant 6s |

Les trois premiers sont exactement ta demande : se déplacer à côté d'un allié et le soigner.
Le Martyr pousse l'idée jusqu'à son thème, se mettre à la place de celui qu'on protège.

## ARCHER — base : Pas de Retrait, `self_move` 2

| sous-classe | sort | type | portée | effet à l'arrivée |
|---|---|---|---|---|
| ranger | **Retraite Souple / Loose Retreat** | `self_move` mode `flee` | 3 | `evasion_up` 2 charges |
| falconer | **Emport / Carried Off** | `self_move` | 3 | `marked` 2 charges sur l'ennemi le plus proche de l'arrivée |
| ballmaster | **Traction / Haul** | `pull` ennemi | 5 | tire un ennemi de 2 cases vers soi |
| gunslinger | **Recul / Recoil** **[POUSSÉE]** | poussée de soi | 2 | `crit_chance_up` 2 charges |

Ta « flèche qui fait reculer » existe en deux moitiés. Le Ballmaster **tire l'ennemi à lui**, ce qui
est faisable aujourd'hui avec `pull`. Le Gunslinger **se repousse lui-même** avec le recul de son
arme, ce qui demande la poussée et reste donc bloqué.

## ROGUE — base : Pas de l'Ombre, `self_move` 20 (conservé)

| sous-classe | sort | type | portée | effet à l'arrivée |
|---|---|---|---|---|
| shadowblade | **Pas de l'Ombre / Shadowstep** | `self_move` | long | inchangé, c'est son identité |
| trickster | **Substitution / Switcheroo** **[SWAP ENNEMI]** | `swap` ennemi | 5 | échange sa place avec un ennemi |
| corsair | **À l'Abordage / Boarding** | `self_move` | 3 | `lifesteal` 2 charges |
| duelist | **En Mesure / Closing In** | `teleport_adjacent` ennemi | 4 | `parry_chance` renforcée pendant 6s |

Le Trickster est le seul cas où je propose de garder l'accès à l'arrière-garde, mais **en payant** :
il ne s'y téléporte pas, il **échange sa place** avec un ennemi. Il tire un lanceur au front et se
met lui-même en danger. C'est un vrai choix, pas un contournement gratuit.

## ARTISAN — base : Treuil, `pull_to_center` 7

Le Treuil n'est pas un déplacement de soi, c'est une zone qui aspire. Il reste en tant que tel.

| sous-classe | sort | type | portée | effet à l'arrivée |
|---|---|---|---|---|
| alchemist | **Repli Fumigène / Smoke Retreat** | `self_move` mode `flee` | 3 | `blind` sur les ennemis de la case de départ |
| blacksmith | **Coup d'Épaule / Shoulder Charge** | `dash_line` | 2, ne dépasse pas le front | `armor_down` 3 charges sur la cible percutée |
| chef | **Tournée / Rounds** | `teleport_adjacent` allié | 4 | petit soin sur l'allié rejoint |
| musician | **Marche d'Ouverture / Opening March** | `self_move` | 3 | `atk_up` 2 charges aux alliés adjacents |

Le Blacksmith est un tank de mêlée à portée 2 : il reçoit la même borne d'atterrissage que le
Berserker. Les trois autres sont des soutiens d'arrière-garde, leur déplacement sert à se replacer
ou à rejoindre quelqu'un, jamais à percer.

---

## Ce qu'il reste à trancher avant le JSON

1. **BE-S9 livré ?** Sans lui, rien de tout ceci n'est chargeable.
2. **La poussée** existe-t-elle, ou faut-il l'ajouter ? Bloque Gunslinger.
3. **`swap` sur un ennemi** est-il accepté ? Bloque Trickster.
4. **Coût en Souffle** : les six déplacements actuels sont à 0. Vu que le chantier Souffle vise à
   rendre la ressource contraignante, faut-il que ces vingt-quatre restent gratuits ? Mon avis :
   oui, ils sont déjà bornés par un cooldown de 20 à 30s, et un déplacement qu'on ne peut pas
   payer quand on en a besoin est une frustration, pas une décision.
5. **Le déplacement de base disparaît-il** quand la sous-classe en a un, ou les deux coexistent ?
   Mon avis : il disparaît. Deux déplacements sur un même kit, c'est deux fois trop de mobilité.
   Le fallback de BE-S9 s'en charge tout seul.
