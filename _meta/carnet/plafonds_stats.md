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
| Ténacité | **50** : la durée est **divisée au plus par 2** | joueurs et monstres ; **DoT compris** (symétrie avec la durée des débuffs, qui les allonge) ; plancher 0,5 s ; stat rare (objets tank / support, jets faibles) |
| Résistance aux effets | application toujours entre **15 et 85 %** | jamais d'immunité totale aux contrôles, jamais de contrôle garanti |
| GCD | joueurs **2 s**, familiers **3 s**, monstres **3 s** | l'IA lit le vrai GCD ; les grosses attaques de boss passent par leurs propres recharges |

Résistance = chance de ne pas subir (contrée par la chance d'effet) ; ténacité = durée réduite de ce qu'on
subit (contrée par la durée des débuffs). Les deux valent pour les CC et les débuffs.

Aussi : blocage (75), parade (30) et vol de vie (50) sont maintenant plafonnés **au moment du jet**, buffs compris.

Inchangés, simplement déplacés dans la data : pénétration 70, CDR 40, incantation 50, réduction de dégâts
75, double / triple frappe 50 / 30, vol de sort et vol de vie 50, niveau max 100.

## Plus tard

- [ ] **Parade avec riposte** : réduit les dégâts et en renvoie une partie, plafond 50 (nouvelle mécanique,
      lot à part).
- [ ] **Renvoi de dégâts (reflect)** : la data annonçait 30, le serveur n'a jamais plafonné (100) ; un unique donne
      jusqu'à 52 au rang SS. Plafond à décider (gardé à 100 en attendant).
- [ ] **Bastion** (familier tank) : immunité aux contrôles 5 s (+0,15 s / niveau) pour une recharge de **8 s**,
      presque permanente même sans bonus ; le validateur le refuse. Recharge à revoir (proposé : 20 s).
