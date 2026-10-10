# Runes : premier catalogue (40)

Statut : proposition (2026-10-10), à relire. Règles générales : voir [runes.md](runes.md) (horizontal,
budget fixe par emplacement, pas de cumul de la même rune, délai interne, rareté ≠ puissance).

Légende faisabilité : ✅ moteur actuel (ProcProcessor, statuts, stats existantes) ; ⚠️ petit ajout ;
❌ ajout plus gros (une fois pour toutes).

## Comptage

- Aujourd'hui : **0 rune** dans le jeu.
- Possible avec le moteur : ~25 déclencheurs × ~30 effets → des centaines de combinaisons.
- Proposé pour démarrer : **40** = 24 runes de **déclenchement** (rangs I à V calés sur les bandes,
  chiffres qui suivent le niveau) + 16 runes de **style** (sans rang, une contrepartie chacune).
- Faisabilité : **28 ✅, 11 ⚠️, 1 ❌**.

## Runes de déclenchement (24, rangs I à V)

Chance fixe ; la **valeur** suit le rang ; **délai interne** indiqué (une rune ne se redéclenche pas
avant).

### Offensives (8)

| Rune | Déclencheur | Effet | Délai | Faisable |
|---|---|---|---|---|
| Braise | sur coup, 8 % | 1 charge de Brûlure | 6 s | ✅ |
| Lame sanglante | sur critique, 15 % | 1 charge de Saignement | 6 s | ✅ |
| Venin | sur coup, 8 % | 1 charge de Poison | 6 s | ✅ |
| Élan | sur élimination | prochain coup +X % de dégâts | 10 s | ✅ |
| Précision | tous les 5 sorts | prochain sort critique garanti | — | ✅ |
| Achèvement | cible sous 30 % PV | +X % d'attaque 4 s | 12 s | ✅ |
| Double frappe | sur critique, 10 % | double attaque sur le prochain coup | 8 s | ⚠️ (la stat `double_attack_chance` existe ; à brancher en bonus court) |
| Boule de feu | sur critique, 5 % | lance une boule de feu (sort existant) | 12 s | ❌ effet « lancer un sort » (auto-cast) |

### Défensives (8)

| Rune | Déclencheur | Effet | Délai | Faisable |
|---|---|---|---|---|
| Écorce | dégâts reçus, 5 % | bouclier X | 10 s | ✅ |
| Dernier rempart | sous 30 % PV | bouclier X % des PV max | 1 fois par combat | ✅ |
| Riposte | blocage ou parade | prochain coup +X % | 8 s | ✅ |
| Pas léger | esquive | +X % d'esquive 3 s | 10 s | ✅ |
| Rémission | **critique reçu**, 5 % | soin sur la durée sur soi | 10 s | ⚠️ déclencheur « critique reçu » (quelques lignes) |
| Volonté | contrôle reçu | purification | 20 s | ✅ |
| Peau de pierre | malus reçu | +X % d'armure 4 s | 12 s | ✅ |
| Second souffle | gros dégâts d'un coup | soin instantané X | 15 s | ✅ |

### Soutien (4)

| Rune | Déclencheur | Effet | Délai | Faisable |
|---|---|---|---|---|
| Main secourable | allié sous 30 % PV | bouclier sur cet allié | 15 s | ✅ |
| Écho de soin | soin lancé, 10 % | soin sur l'allié le plus blessé | 8 s | ✅ |
| Partage | buff reçu | propage le buff à un allié proche | 12 s | ✅ |
| Grand souffle | ultime lancé | rend X Souffle | 1 par ultime | ✅ |

### Souffle et rythme (4)

| Rune | Déclencheur | Effet | Délai | Faisable |
|---|---|---|---|---|
| Source | Souffle sous 20 % | rend X Souffle | 20 s | ✅ |
| Siphon | sur coup, 10 % | vole X Souffle | 8 s | ✅ |
| Hâte | début du combat | −X % de recharge 6 s | 1 par combat | ✅ |
| Ouverture | premier sort du combat | +X % de dégâts | 1 par combat | ✅ |

## Runes de style (16, sans rang, contrepartie obligatoire)

Une rune de style change la façon de jouer ; elle vaut autant au niveau 20 qu'au niveau 100.

| Famille | Rune | Bonus | Contrepartie | Faisable |
|---|---|---|---|---|
| Offense | Longue-vue | +1 portée des sorts mono-cible | −10 % de dégâts | ⚠️ modificateur de portée |
| Offense | Brutale | +15 % de dégâts | −10 % d'armure et RM | ✅ |
| Offense | Œil acéré | +8 de chance de critique | −15 dégâts critiques | ✅ |
| Offense | Patience | +20 % de dégâts des sorts à incantation | +10 % de temps d'incantation | ⚠️ |
| Défense | Rempart | +15 % d'armure et RM | −10 % de dégâts | ✅ |
| Défense | Vif | +10 d'esquive | −10 % de PV max | ✅ |
| Défense | Tenace | +20 de ténacité | −10 % de soins reçus | ✅ |
| Défense | Bouclier vivant | +20 % de boucliers reçus | −10 % de soins reçus | ⚠️ stat « boucliers reçus » |
| Déplacement | Bond | +1 portée des déplacements | +15 % de recharge des déplacements | ⚠️ |
| Déplacement | Agile | −20 % de recharge des déplacements | −1 portée des déplacements | ⚠️ |
| Déplacement | Ancre | immunité aux déplacements forcés (attirer / repousser) | −1 portée des déplacements | ⚠️ |
| Déplacement | Fuyant | après un déplacement, +20 d'esquive 2 s | −10 % de dégâts | ⚠️ |
| Soutien | Généreux | +15 % de soins donnés | −15 % de soins reçus | ✅ |
| Soutien | Martyr | +20 % de soins donnés | chaque soin coûte 3 % des PV | ⚠️ |
| Soutien | Économe | −15 % de coût en Souffle | −10 % de puissance | ⚠️ |
| Soutien | Concentré | +15 % de durée des buffs | −15 % de vitesse d'incantation | ✅ |

## Ce qu'il faut ajouter au serveur (une fois)

1. **Emplacements de runes** sur l'équipement (0 / 1 / 2 selon la rareté) + insertion à la forge + retrait
   contre de l'or.
2. **Effet « lancer un sort »** (auto-cast) — ❌, sert à toutes les runes de ce type.
3. **Déclencheur « critique reçu »** — quelques lignes.
4. **Modificateurs par catégorie de sort** (portée et recharge des déplacements, des sorts mono-cible, des
   sorts à incantation) — sert aux runes de style.
5. **Délai interne par rune** et **interdiction de cumuler la même rune** (le ProcProcessor a déjà des
   recharges d'effet).

## Visuels

Un **seul effet générique** de déclenchement (petit éclat d'icône, couleur de la famille) ; une rune qui
lance un sort réutilise l'animation du sort. Lisibilité en 10 contre 10.

## Questions

- [ ] Garder ces 40 ? En retirer, en ajouter ?
- [ ] Drop : chaque rune liée à des **espèces** de monstres (ex. Venin → araignées, scorpions ; Braise →
      élémentaires de feu ; Bond → loups) ?
- [ ] Chances et valeurs de départ : à mesurer au banc (`item_power_combat_probe`, ±10 %).
