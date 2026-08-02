# Patch note — data `4cd7b57` → `09ffa25`

**Version** 4.11.0 → **4.30.0** · 33 commits · +2500 environ

> Le lot contient trois changements d'équilibre réels : les temps d'incantation du Mage,
> l'activation du scaling de durée (BE-16), et le nettoyage des passifs.
> Le reste est de la réparation et de la cohérence.

---

## FEAT

### Combat — ciblage et formes
- **Passes de ciblage sur les 6 classes.** Le vocabulaire passe à **29 formes distinctes**. Règle posée : *la forme suit le nom du sort*.
- **Plafond de 25 cases** sur les zones, fin des `all` offensifs — pour que portée et ligne de vue continuent de décider quelque chose.
- **Doctrine de ciblage** dans `combat/targeting.json` et **grille de balance** dans le nouveau `config/balance_model.json` (puissance, cast, cooldowns, portées, dosage des charges).

### Combat — Mage
- **Temps d'incantation indexés sur la puissance** (44 sorts). Avant, le cast ne corrélait rien.
- **Charges Arcaniques visibles** dans 22 tooltips qui les déplaçaient en silence.

### Combat — outils tactiques
- **Anti-soin et anti-crit** sur 9 sous-classes dont c'était l'identité. Le Mage et le Rogue n'en avaient aucun.
- **`cast_speed_down` activé** (3 sorts) — deux le promettaient déjà dans leur texte.
- **Portées dérogatoires** sur 6 sorts du Rogue (la ligne Corsair/Gunslasher est un tireur greffé sur une classe à portée 2).

### Passifs
- **Communs et classes de base nettoyés** : `balanced_power` n'est plus dominé, `precision` et `tenacity` redeviennent des spécialistes distincts.
- **`attack_speed` retiré de 6 passifs** après confirmation du back (auto-attaques coupées).

### Infrastructure
- **Grille 10x6 déclarée par défaut** — le client bootait sur `4x5`, une grille morte.
- **Scaling de durée activé** (BE-16) : 168 effets, avec les contrôles bornés avant activation.

---

## FIX

### Mécaniques qui ne faisaient rien
Toutes vérifiées code à l'appui.

| Sort / passif | Ce qui était cassé |
|---|---|
| `shadowstep` | **rendait l'ENNEMI invisible** au lieu du voleur |
| `warrior_charge` | **ne provoquait pas**, alors que son texte annonce « Provocation 2 s » |
| `guardian_swap` | l'allié ne recevait **aucun bouclier** |
| 3 soins de familier | **ne soignaient rien** (`heal_power` n'est lu nulle part) |
| `makeshift_shell` | bouclier inexistant |
| 6 `class_filler` | attaque gratuite illimitée, lue par personne |
| `grapple` | `debuff: slow` mort et jamais annoncé — retiré |

### Équilibre
- **13 durées de contrôle** hors politique, corrigées **avant** que BE-16 ne les active. La pire : un étourdissement de familier qui serait passé de 1,5 s à 2,4 s.
- **10 violations** du contrat Option A converties en charges.
- **Cooldowns recalibrés** : 62 sorts sortaient du modèle — c'étaient mes bornes qui étaient fausses, pas les sorts.

### Cohérence
- **0 sort dupliqué sur 498** (4 vrais doublons différenciés, jamais fusionnés).
- **13 collisions de noms** levées.
- **101 effets de statut, tous en `impl: done`**.
- **`boss_mechanics`** : 9 références inventées remplacées.

### Outillage CI
- **Couverture des sorts : 47% → 100%.** Le validateur ne descendait ni dans `tier3` ni dans `signature_movement` — **246 sorts jamais validés** depuis la création du script. C'est ce trou qui a laissé passer la régression du lifesteal.
- **Nouveau `validate_passives.py`** : les 126 passifs n'avaient **aucun** contrôle. Dès son premier passage il a trouvé 5 passifs branchés sur une stat morte.
- **3 nouvelles règles** : `utility` sans `value` = inerte, cohérence type de dégâts / stat, whitelist des champs de déplacement.

---

## SIGNALÉ EN JEU, PAS ENCORE RÉPARABLE CÔTÉ DATA

Ces mécaniques sont **conçues mais jamais implémentées** côté moteur. Je les ai laissées en data — les retirer supprimerait le design. Elles attendent le back.

### Le Cardmaster est très largement non fonctionnel

Aucune des mécaniques de tirage aléatoire n'est lue, ni par le loader ni par `room.cpp` : `random_buffs_*`, `random_debuffs_*`, `buff_pool`, `debuff_pool`, `marked_bonus_percent`.

**11 sorts du Mage touchés**, dont **2 entièrement inertes** :
- `card_lucky_draw` (Tirage Chanceux) — aucun dégât, aucun effet réel : **le sort ne fait rien**
- `fate_gambler_double_or_nothing` (Quitte ou Double) — idem

Les 9 autres conservent leurs dégâts mais perdent leur signature : `card_bad_luck`, `card_fate_flip`, les 3 `marked_bonus_percent` de l'Arcane Dealer (25 / 50 / **100%**), et 4 sorts du Fate Gambler.

Deux sorts d'Archer aussi (`precise_shot`, `falcon_striker_falcon_mark`).

**Et « monter Tirage Chanceux » n'apporte quasiment rien** même une fois réparé : le seul effet du niveau est `random_buffs_min_at_level_5` (le minimum passe de 1 à 2 buffs au niveau 5). Les niveaux 2, 3, 4 et 6 à 10 n'ajoutent **rien** — sauf du coût en Souffle. À revoir en design une fois la mécanique vivante.

### Autres mécaniques mortes

- **6 conditionnelles jamais parsées**, dont deux doublements de dégâts : `stealth_bonus_damage=100` sur le backstab du Rogue (l'attaque furtive ne profite pas de la furtivité) et `double_damage_if_armor_broken` sur la signature du Blacksmith.
- **`double_attack_chance` / `double_hit_chance`** ne se déclenchent que sur `basic_attack`, donc jamais depuis la coupure des auto-attaques. C'est pourquoi **Lancer de Carte n'a jamais frappé deux fois**.
- **`cooldown_reduction`** est sommée mais jamais appliquée. Elle est pourtant dans les stats de base des 6 classes, leurs courbes de croissance, 5 panoplies, l'équipement et 3 passifs.

---

## À VÉRIFIER / DÉCIDER

**`vampirism` (passif commun).** J'ai tracé toute la chaîne : le passif écrit `lifesteal`, le builder le mappe sur `lifesteal_percent`, et `damage_calculator.cpp:252` l'applique à **tous** les dégâts (pas seulement physiques) à pleine puissance sur les sorts. **Il devrait fonctionner.** Deux hypothèses : soit la valeur est simplement discrète (+4,5% au niveau 10, soit 13 PV sur un coup à 300), soit les niveaux alloués n'atteignent pas le combat — ce que la data ne permet pas de vérifier. À tester côté runtime.

`spell_vamp` est bien **différent** : lui est réservé aux dégâts **magiques** uniquement.

**`arcane_blade` (passif Mage, slot Spellblade) donne de l'ATQ — c'est une incohérence.** Le Spellblade est un bruiser de mêlée **magique**, ses sorts scalent sur `mag`. Le passif est même contradictoire avec lui-même : `atk %` d'un côté, `spell_vamp` de l'autre — or `spell_vamp` ne se déclenche que sur des dégâts magiques. Il devrait donner `mag`. **Correction en attente de ton feu vert**, c'est un changement d'équilibre sur une sous-classe.

**Descriptions dans l'interface.** Signalé comme peu lisible, et c'est fondé : la passe de réécriture n'a couvert que les **240 sorts tier3**. Les sorts de base et de sous-classe n'ont jamais été repris. À planifier.

---

## Dette connue, non bloquante

11 sorts étiquetés `basic` avec 20 à 36 s de recharge — ce sont les *tiers* qui sont faux, pas les cooldowns. `tier` n'est pas lu par le moteur de combat, l'impact est cosmétique mais trompeur en interface.

5 champs de sort ne sont lus par personne (`unlock_at_level`, `boss_bonus_percent`, `thorn_reflect_duration`, `self_heal_percent`, `counter_chance_per_level`) — whitelistés pour ne pas bloquer la CI, marqués comme dette dans le script.

`attack_speed` traîne encore dans 22 fichiers (panoplies, stats de base, croissance, uniques). Nettoyage à faire dans une passe dédiée.

---

## Brouillon d'entrées joueur pour `_meta/changelog.json`

À ajouter **au moment du déploiement seulement** — les joueurs ne doivent pas lire
une nouveauté qu'ils n'ont pas encore. Format identique aux patches existants.

```json
{
  "version": "0.8.7.0",
  "date": "A_REMPLIR_AU_DEPLOY",
  "title_fr": "Sorts plus lisibles, passifs qui fonctionnent vraiment",
  "title_en": "Clearer spells, passives that actually work",
  "entries": [
    { "type": "balance",
      "text_fr": "Les sorts du Mage ont desormais un temps d incantation a la hauteur de leur puissance : les plus devastateurs demandent de tenir la position.",
      "text_en": "Mage spells now have a cast time worth their power: the most devastating ones ask you to hold your ground." },
    { "type": "balance",
      "text_fr": "Monter un sort allonge enfin la duree de ses effets. Les etourdissements et controles restent volontairement peu affectes.",
      "text_en": "Levelling a spell finally extends its effect durations. Stuns and control effects stay deliberately close to their base." },
    { "type": "feat",
      "text_fr": "Nouveaux outils contre les soigneurs et les builds critiques, repartis sur les sous-classes dont c est le metier.",
      "text_en": "New tools against healers and crit builds, spread across the subclasses that specialise in them." },
    { "type": "fix",
      "text_fr": "Le Pas de l Ombre du voleur rendait l ENNEMI invisible au lieu du voleur.",
      "text_en": "The Rogue's Shadowstep was turning the ENEMY invisible instead of the Rogue." },
    { "type": "fix",
      "text_fr": "La Charge du guerrier ne provoquait pas, et la Garde du soigneur n accordait aucun bouclier, contrairement a ce qu annoncaient leurs descriptions.",
      "text_en": "The Warrior's Charge did not taunt, and the Healer's Guardian Swap granted no shield, despite what their descriptions promised." },
    { "type": "fix",
      "text_fr": "Trois soins de familier ne soignaient rien du tout.",
      "text_en": "Three familiar heals were healing nothing at all." },
    { "type": "fix",
      "text_fr": "Plusieurs passifs reposaient sur la vitesse d attaque, devenue sans effet depuis le retrait des auto-attaques. Ils donnent maintenant des bonus reels, et les points deja depenses sont conserves.",
      "text_en": "Several passives relied on attack speed, which no longer does anything since auto-attacks were removed. They now grant real bonuses, and points already spent are kept." }
  ]
}
```

Ne PAS annoncer aux joueurs ce qui n'est pas encore repare : le Cardmaster, les
6 conditionnelles mortes et `cooldown_reduction` attendent le back.
