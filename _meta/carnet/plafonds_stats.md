# Plafonds des stats (décisions du 2026-10-14)

Morceau B du refactor « tout dans la data » ([architecture_data.md](architecture_data.md)) : les plafonds
sont lus dans `stats/definitions.json`, une colonne joueurs et une colonne monstres, plus aucune copie
dans le code.

## Décidé (propriétaire)

| Stat | Plafond | Note |
|---|---|---|
| Durée des buffs lancés | **100 %** sur buffs, soins sur la durée et **immunités** ; **50 %** sur les boucliers | prolonger une immunité fait partie du jeu ; garde-fou : le validateur refuse une immunité dont la durée × 2 atteint sa recharge (pas d'immunité permanente) |
| Durée des débuffs lancés | 50 % (inchangé) | |
| Parade | **30** | spé du Duelliste (passifs jusqu'à +14 %, Riposte) ; la parade **annule** le coup, elle ne renvoie rien |
| Ténacité (joueurs) | **90** | stat **rare** (peu d'objets tank / support, jets faibles) ; 3 s d'étourdissement → 0,5 s (plancher de durée) |
| Résistance aux effets | application toujours entre **15 et 85 %** | jamais d'immunité totale aux contrôles, jamais de contrôle garanti |
| GCD | joueurs **2 s**, familiers **3 s**, monstres **3 s** | l'IA lit le vrai GCD ; les grosses attaques de boss passent par leurs propres recharges |

Résistance = chance de ne pas subir (contrée par la chance d'effet) ; ténacité = durée réduite de ce qu'on
subit (contrée par la durée des débuffs). Les deux valent pour les CC et les débuffs.

Inchangés, simplement déplacés dans la data : pénétration 70, CDR 40, incantation 50, réduction de dégâts
75, double / triple frappe 50 / 30, vol de sort et vol de vie 50, niveau max 100.

## Plus tard

- [ ] **Parade avec riposte** : réduit les dégâts et en renvoie une partie, plafond 50 (nouvelle mécanique,
      lot à part).
- [ ] **Contre-stat de la ténacité** (pénétration de ténacité) si les tanks à 90 % deviennent intouchables.
