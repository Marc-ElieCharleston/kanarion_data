# Kits bêtes B : décisions et points à remonter

26 monstres : 22 actifs (tous sous le niveau 40, donc 2 compétences ; la Vache, élite, en a 3) et 4 shelved sans espèce (niveaux 51 à 59). Tous les identifiants sont existants ou réservés.

## Archétypes corrigés
- **Taureau : tank → brute** (Coup de tête + Ruée Brutale). Il charge ; c'est la Vache qui protège.
- **Vache : tank → gardien** (signature « Rempart du troupeau ») ; **Cerf : tank → gardien** (Bois protecteurs = réduction de dégâts sur la ligne).
- **Chasseur du Vide : archer → assassin** (bête, tags melee).

## Choix notables
- Effet ovin et bovin = étourdissement : il passe par **Coup de tête** (Bélier, Bouc, Brebis, Taureau). La Chèvre garde **Coup de corne**, qui fait saigner : soit on change horn_jab, soit on admet l'exception.
- Bêlement du troupeau = compétence de rôle enchanteur de la Brebis. Léchage = compétence d'espèce de la Biche (elle n'a pas de bois).
- On propose l'espèce **faille** pour la Meute, le Behemoth et la Matriarche, et l'espèce **vide** pour le Chasseur. La Matriarche ferait une bonne **invocatrice** de la Meute de la Faille : c'est au propriétaire de trancher.

## Problèmes à remonter
1. **Pas de stat `mag`** sur les soigneurs, l'enchanteur et le mage (Biche, Brebis, Grenouille Soigneuse, Cerf Gardien, Crapaud) : le serveur prend MAG = ATK/2, leurs soins et sorts sont à moitié de leur puissance.
2. **Gabarit copié** : Tatou, Grenouille Cornue et Tortue ont les mêmes stats (1496/26/65). L'armure 65 ne va pas à un batracien.
3. **Vache élite** (920 PV) a moins de PV que le Bouc tough (1050).
4. **Ultimes et avancées à bas niveau** : Forteresse sur le Bélier (niv. 7), le Taureau et le Tatou ; téléportation du Cerf Obscur au niv. 25.
5. **Attaques absurdes** : Encornade sur le cheval et le tatou, Coup de Queue sur la grenouille, Dard sur le crapaud, Morsure sur un cerf.
6. **Doublons et monstres non placés** : Tortue, Tatou, Cheval, Cerf Obscur, Cerf Gardien. Le Cerf Gardien double la Biche, et son nom se confond avec l'archétype gardien. Chasseur du Vide est proche du Void Hound.
7. **Tortue** : catégorie `elemental` alors qu'elle est rangée dans l'espèce tortue.

## Compétences manquantes
- **Crachat** batracien à distance (Crapaud, Grenouille Soigneuse).
- **Ruade** pour le cheval (facultatif).
