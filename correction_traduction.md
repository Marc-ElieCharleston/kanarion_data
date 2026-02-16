# Plan de Correction des Traductions FR/EN — Kanarion Online

**Date :** 2026-02-16
**Auteur :** Marc-Elie Charleston
**Statut :** Valide par CTO (9/10) — pret pour execution
**Scope :** `kanarion_database/` (source de verite) + `kanarion_web/` (site/wiki)

---

## Constat

Les descriptions actuelles souffrent de 5 problemes majeurs :

1. **Melange code/texte** — `row_3`, `rect_2x3` visibles par le joueur
2. **Franglais** — `shield`, `atk speed`, `stack`, `Detonate` dans du texte FR
3. **Ton robotique** — "Augmente X de Y% par niveau" sans aucune identite
4. **Accents manquants** — ~536 champs avec caracteres non-accentes
5. **Traductions absurdes** — "ressusciter les tombes", "incontr0lable"

**Resultat :** Le joueur ne comprend pas ce que fait le sort. Le jeu fait prototype technique au lieu de MMO abouti.

---

## Principes directeurs

### 1. FR = langue source

> On ecrit d'abord en francais, puis on traduit en anglais.
> L'approche inverse a produit le franglais actuel.

### 2. Clarte > Poesie

Un joueur **scanne**, il ne lit pas un roman. Chaque description doit etre :
- **Immediatement comprehensible**
- **Lisible en 2 secondes**
- **Structuree de maniere previsible**

### 3. Structure standardisee pour tous les skills

```
Ligne 1 : Action claire
  → Inflige 24 (+45% ATK) degats a 3 cibles en ligne.

Ligne 2 : Effet secondaire (si applicable)
  → Applique Saignement pendant 3s.

Ligne 3 : Mecanique speciale (si applicable)
  → Les degats augmentent si la cible est immobilisee.
```

**Pas** de phrase longue. **Pas** de metaphore obscure. **Pas** de jargon dev.

### 4. Separation Flavor / Mecanique

Si on veut du ton fantasy, c'est **une phrase courte separee**, jamais melangee aux chiffres :

```
Une pluie de fleches s'abat sur vos ennemis.
Inflige 24 (+45% ATK) degats a 3 cibles en ligne.
Applique Saignement pendant 3s.
```

### 5. Le ton reflete la classe

Toutes les classes ne parlent pas pareil :

| Classe | Ton | Exemple |
|--------|-----|---------|
| Guerrier | Brut, direct | "Frappe devastatrice sur la premiere ligne." |
| Voleur | Precis, furtif | "Frappe chirurgicale dans le dos de la cible." |
| Mage | Mystique, arcanique | "Canalise les forces primordiales en un torrent." |
| Artisan | Technique, ingenieux | "Melange des reactifs volatils dans une fiole." |
| Soigneur | Noble, protecteur | "Enveloppe un allie d'une lumiere apaisante." |
| Archer | Tactique, calcule | "Vise le point faible avec une precision mortelle." |

---

## Glossaire standardise

Ce glossaire est la **reference unique**. Toute deviation est un bug.

### Stats et mecaniques

| Concept | FR (in-game) | EN (in-game) | Abrev. |
|---------|-------------|-------------|--------|
| Points de vie | Points de vie | Health Points | PV / HP |
| Points de mana | Points de mana | Mana Points | PM / MP |
| Attaque | Attaque | Attack | ATK |
| Magie | Magie | Magic | MAG |
| Armure | Armure | Armor | ARM |
| Resistance magique | Resistance magique | Magic Resist | RM / MR |
| Vitesse d'attaque | Vitesse d'attaque | Attack Speed | VdA / AS |
| Vitesse d'incantation | Vitesse d'incantation | Cast Speed | - |
| Chance critique | Chance critique | Critical Chance | Crit |
| Degats critiques | Degats critiques | Critical Damage | - |
| Penetration d'armure | Penetration d'armure | Armor Penetration | Pen. |
| Vol de vie | Vol de vie | Lifesteal | - |
| Reduction de degats | Reduction de degats | Damage Reduction | RD / DR |
| Precision | Precision | Accuracy | - |
| Esquive | Esquive | Evasion | - |
| Parade | Parade | Parry | - |
| Blocage | Blocage | Block | - |
| Puissance de soin | Puissance de soin | Heal Power | - |
| Temps de recharge | Temps de recharge | Cooldown | CD |
| Chance de double frappe | Chance de double frappe | Double Hit Chance | - |
| Chance d'effet | Chance d'effet | Effect Chance | - |
| Resistance aux effets | Resistance aux effets | Effect Resist | - |

### Effets de statut

| EN | FR |
|----|-----|
| Bleed | Saignement |
| Burn | Brulure |
| Poison | Poison |
| Stun | Etourdissement |
| Freeze | Gel |
| Silence | Silence |
| Blind | Aveuglement |
| Root | Immobilisation |
| Taunt | Provocation |
| Fear | Terreur |
| Sleep | Sommeil |
| Disarm | Desarmement |
| Shield | Bouclier |
| Buff | Buff (accepte en FR gaming) |
| Debuff | Debuff (accepte en FR gaming) |
| HoT | Soin continu |
| DoT | Degats continus |
| Cleanse | Purification |
| Stealth | Furtivite |
| Reflect | Renvoi |

### Termes internes a ne JAMAIS montrer au joueur

| Code interne | FR (description joueur) | EN |
|-------------|------------------------|-----|
| `row_2` | 2 cibles en ligne | 2 targets in a row |
| `row_3` | 3 cibles en ligne | 3 targets in a row |
| `row_4` | 4 cibles en ligne | 4 targets in a row |
| `rect_2x3` | zone 2x3 | 2x3 area |
| `cross` | en croix | cross pattern |
| `around_radius_1` | autour de la cible | around the target |
| `column` | en colonne | in a column |
| `atk speed` | vitesse d'attaque | attack speed |
| `Flat DR` | reduction de degats | damage reduction |
| `stacks` / `stack` | charges | stacks |
| `Toxin` | Toxine | Toxin |
| `Detonate` | fait exploser | detonates |
| `dmg` | degats | damage |
| `Heal self` | se soigne | heals self |
| `CC` | controle | crowd control |

---

## Phase 1 : Securite (typos + accents + nettoyage code)

**Effort estime : 3-4h**
**Impact : Rend le texte lisible et professionnel**

### 1A. Fix typos critiques

| Fichier | Champ | Actuel | Corrige |
|---------|-------|--------|---------|
| `_classes_index.json` | Berserker tagline | `"incontr0lable"` (zero) | `"incontrôlable"` |
| `_classes_index.json` | Healer wiki_intro | `"les tombes"` (= sepultures) | `"les allies tombes au combat"` |

### 1B. Ajout des accents — ~536 champs

Passe systematique sur tous les champs FR dans :

| Fichier | Champs | Nombre |
|---------|--------|--------|
| `classes/_classes_index.json` | tagline, description, lore, wiki_intro, playstyle_tips | ~96 |
| `classes/*/skills.json` (x6) | name_fr, description_fr | ~156 |
| `classes/*/passives.json` (x6) + common | name_fr, description_fr | ~70 |
| `entities/monsters.json` | name_fr | 26 |
| `world/zones.json` | name_fr, description_fr, name_override_fr | ~30 |
| `stats/status_effects.json` | name_fr, description_fr | ~70 |
| `items/consumables.json` | name_fr, description_fr | ~14 |
| `items/materials.json` | name_fr | ~74 |
| **Total** | | **~536** |

### 1C. Nettoyage du code interne dans les descriptions

Remplacement de tous les `row_3`, `rect_2x3`, `atk speed`, `Flat DR`, `stacks`, `shield`, `Heal self`, `CC`, etc. par les termes FR du glossaire.

**Ce n'est pas une reecriture.** On remplace juste les termes anglais/code par leurs equivalents FR. La structure de la phrase reste la meme.

### 1D. Harmonisation terminologique

Appliquer le glossaire : meme terme = meme traduction partout.
Exemple : "lifesteal" -> "vol de vie" dans les 6 fichiers skills, pas "drain de vie" dans l'un et "vol de vie" dans l'autre.

**Methode :** Branche `fix/i18n-phase1`, commit par fichier, verification JSON valide a chaque etape.

---

## Phase 2 : Reecriture structuree des skills

**Effort estime : 8-10h**
**Impact : Les sorts deviennent comprehensibles**

### Objectif

Reecrire les descriptions pour qu'elles soient **claires, structurees et coherentes**. Pas une refonte narrative — un nettoyage professionnel.

### Format standard

```
[Phrase flavor courte — optionnelle, 1 ligne max]
[Action + degats + cibles]
[Effet secondaire]
[Mecanique speciale]
```

### Exemple complet : Artisan Alchemist

**Avant :**
```
name_fr: "Catalyse"
description_fr: "SIGNATURE - Catalyse zone 2x3. Detonate tous les Toxin:
(15 + 30% MAG) par stack. Consomme les stacks."
```

**Apres :**
```
name_fr: "Catalyse"
description_fr: "Declenche une reaction chimique en zone 2x3.
Fait exploser toutes les charges de Toxine : 15 (+30% MAG) degats par charge.
Consomme toutes les charges."
description_en: "Triggers a chemical reaction in a 2x3 area.
Detonates all Toxin stacks: 15 (+30% MAG) damage per stack.
Consumes all stacks."
```

### Exemple passif

**Avant :**
```
name_fr: "Soif de Sang"
description_fr: "Augmente le vol de vie de 0.5% par niveau."
```

**Apres :**
```
name_fr: "Soif de Sang"
description_fr: "Chaque coup nourrit le guerrier.
+0.5% de vol de vie par rang."
description_en: "Every strike feeds the warrior.
+0.5% lifesteal per rank."
```

Flavor et mecanique toujours **separes**. Le joueur peut ignorer la premiere ligne et scanner les chiffres.

### Priorite par classe

| Priorite | Classe | Raison | Nb skills |
|----------|--------|--------|-----------|
| 1 | Artisan | Incomprehensible, melange code/FR/EN | 26 |
| 2 | Warrior | Anglais + accents manquants | 26 |
| 3 | Healer | `shield`, `Heal self`, `row_3`, commentaires dev | 26 |
| 4 | Archer | `row_3`, `bleed`, `atk speed` | 26 |
| 5 | Rogue | Globalement OK, anglicismes mineurs | 26 |
| 6 | Mage | Le meilleur, corrections mineures | 26 |

**Methode :** Branche `fix/i18n-phase2`, commit par classe (6 commits), test build wiki apres chaque classe.

---

## Phase 3 : Passifs + renommages

**Effort estime : 3-4h**
**Impact : Les passifs ont une identite**

### Reecriture des 70 passifs

Meme format que Phase 2 : flavor court + mecanique claire.

### Renommages proposes

> **Note :** Le playtest n'a pas encore eu lieu. Aucun joueur n'a memorise ces noms. Le renommage est sans risque a ce stade.

| Actuel | Propose | Raison |
|--------|---------|--------|
| Focus Elementaire | Focalisation Elementaire | "Focus" est anglais |
| Conduit Magique | Canal Magique | "Conduit" = tuyau en FR |
| Efficacite Mana | Maitrise du Mana | Nom et effet incoherents |
| Patience du Sniper | Patience de l'Embusque | "Sniper" casse l'immersion fantasy |
| Pieds Agiles | Jeu de Jambes | Le nom dit esquive, l'effet est parade |
| Mains Stables | Mains Fermes | Plus idiomatique en FR |
| Travailleur Efficace | Gestes Precis | Trop "RH", pas fantasy |
| Exploitation des Vulnerabilites | Instinct du Predateur | Trop clinique |
| Exploitation des Faiblesses | Oeil du Chasseur | Doublon conceptuel avec le rogue |
| Entrainement a l'Evasion | Art de la Derobade | Plus thematique rogue |

**Methode :** Branche `fix/i18n-phase3`, commit unique, verification que les IDs internes ne changent pas (seuls `name_fr` et `name_en` changent).

---

## Phase 4 : Noms FR pour l'equipement

**Effort estime : 2-3h**
**Impact : Les items ne sont plus en anglais**

### Probleme

**Aucun** des ~45 items n'a de `name_fr`. Tout est en anglais : "Rusty Sword", "Iron Helm", "Leather Tunic".

### Convention de nommage

| Type | Format | Exemple |
|------|--------|---------|
| Armes | [Type] de [Qualificatif] | Epee de Fer, Dague de l'Ombre |
| Armures | [Type] en [Materiau] | Cuirasse de Fer, Cotte de Mailles |
| Casques | [Type] de [Materiau] | Heaume de Fer, Capuche de Cuir |
| Accessoires | [Type] de [Attribut] | Anneau de Chance, Amulette de Force |

### Exemples

| EN (existant) | FR (propose) |
|---------------|-------------|
| Rusty Sword | Epee Rouillee |
| Iron Sword | Epee de Fer |
| Steel Sword | Epee d'Acier |
| Knight Sword | Lame du Chevalier |
| Shadow Dagger | Dague de l'Ombre |
| Night Fang | Croc Nocturne |
| Apprentice Staff | Baton d'Apprenti |
| Arcane Staff | Baton Arcanique |
| Simple Bow | Arc Simple |
| Hunter Bow | Arc de Chasseur |
| Eagle Bow | Arc de l'Aigle |
| Work Hammer | Marteau de Forge |
| Cloth Cap | Coiffe de Tissu |
| Iron Helm | Heaume de Fer |
| Leather Tunic | Tunique de Cuir |
| Chainmail | Cotte de Mailles |
| Iron Plate | Cuirasse de Fer |

**Methode :** Branche `fix/i18n-phase4`, commit unique.

---

## Phase 5 : Status effects + Monstres + Zones

**Effort estime : 2-3h**
**Impact : Coherence wiki complete**

### 5A. Status effects

- Traduire les 4 effets en anglais : "Crit Chance +/-" -> "Chance Critique +/-", "Crit Damage +/-" -> "Degats Critiques +/-"
- Nettoyer les descriptions FR contenant de l'anglais (`skills` -> "competences", `auto-attack` -> "auto-attaque", `Counter casters` -> "efficace contre les lanceurs de sorts")
- Supprimer les commentaires dev ("Spam damage car l'auto-attack du healer est faible")
- Corriger "Reflet" -> "Renvoi" (reflect = renvoi de degats, pas reflet dans un miroir)

### 5B. Monstres

- "Shaman Gobelin" -> "Gobelin Chaman" (ordre FR + mot FR)
- "Archer Squelette" -> "Squelette Archer" (ordre FR)
- Verifier coherence noms monstres entre `monsters.json` et les references dans `zones.json`

### 5C. Zones

- Descriptions courtes : garder le style concis actuel (c'est bien pour du jeu)
- Verifier coherence noms de boss avec `monsters.json`

**Methode :** Branche `fix/i18n-phase5`, commit par fichier.

---

## Phase 6 : Site web (fr.json)

**Effort estime : 30min-1h**
**Impact : Landing page pro**

| Actuel | Corrige | Raison |
|--------|---------|--------|
| "Playtest bientot" | "Phase de test bientot" | Anglicisme sur la landing |
| "preparation au lancement" | "preparation du lancement" | Grammaire |
| "DPS Distance" | "DPS a distance" | Grammaire |
| Roles classes | Verifier coherence avec `_classes_index.json` | Sync |

**Methode :** Directement sur `main`, correction mineure.

---

## Phase 7 : Synchronisation submodules

Apres chaque phase :

```bash
# 1. Depuis le repo source (kanarion_database/)
git add . && git commit -m "fix(i18n): phase N - [description]" && git push

# 2. Mise a jour des 3 submodules
cd kanarion_back/kanarion-meta && git pull origin master
cd kanarion_front/kanarion-meta && git pull origin master
cd kanarion_web/Kanarion_Online/kanarion_database && git pull origin master

# 3. Commit des refs dans les repos parents
cd kanarion_back && git add kanarion-meta && git commit -m "chore: sync submodule i18n phase N" && git push
cd kanarion_front && git add kanarion-meta && git commit -m "chore: sync submodule i18n phase N" && git push
cd kanarion_web/Kanarion_Online && git add kanarion_database && git commit -m "chore: sync submodule i18n phase N" && git push
```

**Test wiki :** `npm run build` apres chaque sync pour verifier que rien n'est casse.

---

## Exclusions

### Panoplies (noms en hebreu)

Les panoplies ont des noms en hebreu **intentionnellement** (lore de l'univers). On n'y touche pas.
Verifier simplement que c'est coherent dans tout le jeu et que le wiki/lore explique ce choix aux joueurs.

---

## Points de vigilance CTO

### 1. Ne pas uniformiser le ton

Le tableau "ton par classe" est un guide, pas un template rigide. Chaque classe doit garder sa personnalite. Eviter de tout transformer en "Inflige X degats a Y cibles" — c'est clair mais generique.

### 2. Noms d'equipement : rester court

Pas de "Lame du Chevalier des Ombres de l'Aube". Les noms courts sont plus lisibles en inventaire. 2-4 mots max.

### 3. Phase 2 = le coeur du projet

C'est la que le jeu change de perception. Ce n'est pas juste du wording, c'est l'experience utilisateur. A faire avec rigueur, pas en vitesse.

---

## Gestion des risques

| Risque | Mitigation |
|--------|-----------|
| JSON casse | Validation JSON a chaque commit |
| Cle manquante EN/FR | Verification que chaque `description_fr` a un `description_en` |
| Regression wiki | `npm run build` apres chaque phase |
| Sync submodule ratee | Hooks `pre-push` deja en place sur les 3 submodules |
| Perte de travail | Branche par phase, merge sur master seulement si OK |
| Ton trop uniforme | Relecture par classe, varier les formulations |
| Noms d'items trop longs | Limite stricte : 2-4 mots par nom |

---

## Resume chiffre

| Phase | Description | Fichiers | Champs | Effort |
|-------|------------|----------|--------|--------|
| 1 | Securite (accents, typos, nettoyage code, glossaire) | 20 JSON | ~536 | 3-4h |
| 2 | Skills (reecriture structuree FR+EN) | 6 JSON | 156 x2 | 8-10h |
| 3 | Passifs (flavor + mecanique + renommages) | 7 JSON | 70 x2 | 3-4h |
| 4 | Equipment (noms FR) | 1 JSON | ~45 | 2-3h |
| 5 | Effects + Monstres + Zones | 3 JSON | ~120 | 2-3h |
| 6 | Site web | 1 JSON | ~10 | 30min-1h |
| 7 | Sync submodules (par phase) | - | - | 15min/phase |
| **Total** | | **38 fichiers** | **~900+** | **~20-24h** |

---

## Validation CTO

- [x] Glossaire de terminologie valide
- [x] Ton valide : clarte > poesie, flavor separe de la mecanique
- [x] Principe confirme : FR = langue source, EN = traduction
- [x] Renommages de passifs valides (pre-playtest, aucun joueur impacte)
- [x] Convention de nommage equipement validee (noms courts, 2-4 mots)
- [x] Estimation 20-24h acceptee
- [x] Panoplies (hebreu) : ne pas toucher, c'est du lore intentionnel
- [x] Vigilance : ne pas uniformiser le ton, garder la personnalite par classe
- [x] Phase 2 identifiee comme coeur du projet — rigueur > vitesse
