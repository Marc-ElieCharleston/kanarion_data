# Kits — bêtes A (38 monstres, tous actifs)

## Décisions notables
- Aucun monstre du lot n'atteint le niveau 40 de base : normaux à 2 compétences, Reine Araignée (élite) à 3, 4 boss à 4. Les kits actuels à 3 compétences ou plus et les signatures posées sur des normaux (ground_slam sur Jeune Rat, Chacal, Loup-Garou) sont retirés.
- Archétypes changés : Loup-Garou contrôleur → berserker (vol de vie d'espèce) ; Molosse Corrompu et Hybride Sanglier-Loup assassin → brute ; boss Reine Araignée mage → contrôleur (conforme à boss_mechanics.json : toiles, cocon, toxine).
- Les soigneurs bêtes (rat, louve, hyène) prennent Léchage (soin en % des PV max) : ils n'ont pas de MAG.
- Sanglier : étourdissement via skill_mob_headbutt (aucune variante réservée). Scarabée : Morsure sans effet, car un scarabée n'a pas de dard.
- Rat tutoriel : exception à 1 compétence (scénario du tuto).

## À remonter au propriétaire
1. **Niveau de spawn ≥ 40** : rats au Nid Corrompu (40-50), Renard Brumeux (≤ 58), Molosse (≤ 100), Loup Meneur (≤ 47). Faut-il ajouter la compétence d'identité selon le niveau de spawn ? Je l'ai proposée dans kit_reason.
2. **MAG absente** chez le Rat Sorcier et les 3 soigneurs : le moteur se replie sur atk/2.
3. **Placement incohérent** : Renard Brumeux (niv. 33) en Expédition 1-10, Petite Araignée (niv. 10) dans la zone 25-30, Charognard (niv. 27) dans la zone 9-20.
4. **Doublons et monstres sans usage** : 2 Reines Araignées (boss sans donjon, dungeon_spider_cave absent) ; Loup Alpha (boss placé nulle part, PV faibles) ; Scarabée de Poussière proche du Scarabée Géant ; Traqueur de Poussière (placé nulle part, sans portrait, nom flou) ; Chacal de la Faille (placé nulle part, stats de tank).
5. **Stats** : Chien Sauvage fodder plus fort qu'une Hyène standard ; Corbeau trop blindé ; Reine élite à peine au-dessus d'un standard ; Rat tutoriel non conforme à sa _note.
6. **Catégorie** : les deux Reines Araignées sont « humanoid ». Le portrait de la Hyène Alpha ressemble à un loup.
7. **Compétences à créer** : identités soigneur et berserker (≥ 20 s), Toile et Cocon pour l'araignée, variante d'étourdissement d'espèce pour sanglier/bovin/ovin.
