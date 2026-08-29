# SPEC — `recommended_players` sur les contrats

**Statut :** proposition, 2026-08-29. À implémenter par l'agent contrats.
**Origine :** demande de Charleston, après la mesure de rentabilité des 60 contrats.
**Dépend de :** le passage `= K★` → `≥ K★` proposé par l'agent back. Les deux se posent bien
ensemble, mais celui-ci ne l'attend pas.

---

## Le problème

Un contrat « nettoyer 3 packs 5★ » et un contrat « abattre 25 monstres » paient la même chose et
s'affichent côte à côte. Le premier demande dix joueurs, le second se fait seul. Rien ne le dit
au joueur avant qu'il l'accepte.

Le panneau doit annoncer le groupe recommandé. Il n'a aujourd'hui aucune donnée pour le faire.

---

## Où vit la valeur

**Une table, pas soixante valeurs.**

Le nombre de joueurs recommandé pour un contrat est une fonction du palier d'étoiles qu'il
demande. Écrire la valeur sur chacun des 60 contrats, c'est soixante occasions de diverger, et la
divergence ne se verrait qu'en jeu, sur un contrat, un jour.

La table vit dans **`entities/monster_variants.json`**, section `star_system`, à côté de
`packs` — c'est déjà là que vit *ce que la rencontre EST* (nombre de mobs, multiplicateurs de
stats, composition en élites). Le nombre de joueurs qu'elle demande est de la même nature.

Ce n'est **pas** `config/rewards.json` : ce fichier est propriétaire de *ce que la rencontre
RAPPORTE*. Une recommandation de groupe ne rapporte rien, elle décrit une difficulté.

```json
"star_system": {
  "roll_weights": [15.0, 32.0, 28.0, 15.0, 7.0, 3.0],
  "packs": { "...": "inchangé" },

  "recommended_players": {
    "_comment": "Groupe recommandé pour affronter un pack de ce palier. Dérivé de la charge du pack (mobs x hp_mult x atk_mult) rapportée au pack 0 étoile, avec l'hypothèse qu'un joueur encaisse jusqu'à deux fois un pack 0 étoile. Plafonné à game.json game_constants.max_party_size. Affiché au joueur, jamais appliqué : le serveur n'interdit pas d'y aller seul.",
    "_derivation": "ceil(charge_relative / 2), borné à [1, max_party_size]",
    "0": 1,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 6,
    "5": 10
  }
}
```

### D'où sortent ces six nombres

| ★ | mobs | hp_mult | atk_mult | charge | ÷ pack 0★ | joueurs |
|---|------|---------|----------|--------|-----------|---------|
| 0 | 1,5  | 1,00    | 1,00     | 1,5    | ×1,0      | 1 |
| 1 | 2,0  | 1,10    | 1,05     | 2,3    | ×1,5      | 1 |
| 2 | 3,0  | 1,25    | 1,10     | 4,1    | ×2,8      | 2 |
| 3 | 4,5  | 1,50    | 1,20     | 8,1    | ×5,4      | 3 |
| 4 | 6,5  | 1,90    | 1,30     | 16,1   | ×10,7     | 6 |
| 5 | 9,0  | 2,50    | 1,40     | 31,5   | ×21,0     | 10 |

Tout vient de `monster_variants.json`, **sauf le seuil de 2,0** — l'hypothèse qu'un joueur
encaisse jusqu'à deux fois un pack 0★. C'est le seul chiffre à valider en jeu.

Deux signaux qu'il est à peu près juste : l'échelle atterrit sur **10 joueurs pour un 5★**, soit
exactement `game.json` `game_constants.max_party_size` ; et le 3★, premier palier à porter un
élite, tombe sur 3 joueurs, ce qui correspond à la formulation du garde-fou déjà en data
(« un groupe 5 étoiles ne se prend pas seul »).

Si le playtest dit que le seuil est 1,5 ou 3,0, **on change ce seul nombre et on régénère la
colonne**. C'est pour ça qu'il est écrit dans `_derivation` plutôt que perdu dans un tableur.

---

## Comment un contrat obtient sa valeur

**Par résolution, pas par recopie.**

```
recommended_players(contrat) =
    contrat.recommended_players                     si le champ est présent (dérogation)
    sinon table[objectif.stars]                     si l'objectif porte `stars`
    sinon 1                                         (kill_mobs, win_combats : solo)
```

Un contrat n'écrit `recommended_players` **que pour déroger** — par exemple un contrat scénarisé
qu'on veut annoncer en groupe alors que son objectif ne porte pas d'étoiles. Toute dérogation
doit porter un `_note` disant pourquoi, sinon on ne sait plus, six mois plus tard, si c'est une
intention ou un oubli.

**Aujourd'hui, sur les 60 contrats : aucune dérogation.** Les 15 contrats `clear_star_packs`
héritent de la table, les 45 autres valent 1.

---

## Qui lit quoi

| Lecteur | Usage |
|---------|-------|
| Panneau de contrats (client) | Affiche « Groupe conseillé : N » sur chaque ligne |
| Infobulle / détail de quête | Idem, avec la raison si dérogation |
| Serveur (quest service) | **Rien.** Il n'applique pas la recommandation. |

Le serveur ne doit **pas** refuser un contrat parce que le joueur est seul. C'est une
recommandation, pas une condition d'acceptation — un joueur surniveau doit pouvoir tenter un
contrat étoilé en solo, et un contrat déjà accepté ne doit pas se bloquer parce qu'un
coéquipier se déconnecte.

Si un jour on veut une vraie condition, ce sera un **autre champ** (`required_players`), pas
celui-ci. Un champ qui est tantôt un conseil tantôt une règle finit par être appliqué au
mauvais moment.

---

## Validation CI

À ajouter dans `scripts/validate_cross_references.py` :

1. **La table couvre les six paliers.** `recommended_players` a les clés `"0"` à `"5"`, toutes
   entières et ≥ 1.
2. **Elle ne dépasse pas la taille de groupe.** Aucune valeur > `game.json`
   `game_constants.max_party_size`. Aujourd'hui 10 ; le jour où quelqu'un baisse cette
   constante, la table doit rougir plutôt que d'annoncer un groupe impossible.
3. **Elle est monotone.** `table[k] <= table[k+1]`. Un palier plus dur ne peut pas demander
   moins de monde. C'est le genre d'inversion qui passe inaperçue après une retouche manuelle.
4. **Toute dérogation porte sa raison.** Un contrat avec `recommended_players` et sans `_note`
   échoue.
5. **Tout `clear_star_packs` référence un palier existant.** `objectives[].stars` ∈ [0, 5].

---

## Anti-patterns

**Écrire la valeur sur les 60 contrats.** C'est la tentation immédiate — c'est explicite, ça se
lit dans le fichier. C'est aussi soixante valeurs à maintenir à la main le jour où le seuil
change, et la première qui diverge ne se verra pas.

**La recalculer côté client.** Le client n'a pas à dériver un nombre de joueurs depuis la charge
des packs : c'est la règle R2 du projet, et surtout le panneau, l'infobulle et le futur
matchmaking donneraient trois réponses différentes à la même question.

**La mettre dans `rewards.json`.** Ce fichier tune ce qu'une rencontre rapporte. Y ranger une
difficulté rouvre exactement le mélange que sa migration vient de fermer.

**En faire une condition d'entrée.** Voir plus haut : `required_players` serait un autre champ,
avec une autre discussion.

---

## Ce qui reste à trancher

**Le seuil de 2,0.** À valider en playtest : un joueur de niveau adapté encaisse-t-il vraiment
un pack 2★ (3 mobs, ×1,25 PV) seul, mais pas un 3★ ? C'est le seul chiffre inventé de cette
spec.

**`stars` veut dire « exactement » ou « au moins » ?** Le garde-fou en data dit que
`update_star_pack_progress(char_id, star_rating)` filtre sur le nombre d'étoiles, sans préciser
le sens. Si c'est « exactement », le contrat S est encore plus dur que mesuré : 3 % pile, sans
compensation possible. La spec suppose « au moins », comme le correctif ≥K★ proposé par le back.

**La recommandation vaut-elle pour un contrat, ou pour son objectif ?** Ici elle porte sur
l'objectif (le pack à nettoyer). Le jour où un contrat aura plusieurs objectifs de paliers
différents, il faudra décider : le max, ou une valeur par objectif. Aujourd'hui les 60 contrats
n'ont qu'un objectif chacun, la question ne se pose pas — mais elle se posera.

---

## Ce que cette spec ne corrige pas

La mesure qui l'a motivée a trouvé plus grave, et c'est ailleurs :

**Le contenu de groupe est perdant.** L'XP d'un pack est divisée par le nombre de joueurs, et le
bonus de groupe (`rewards.json` : `1 + (N-1) × 0,055`, plafond 1,5) ne compense pas. À dix
joueurs sur un pack 5★, chacun gagne **dix fois moins vite** qu'en solo sur un pack 0★. Annoncer
« groupe conseillé : 10 » sur un contrat rend le coût lisible — ça ne le rend pas acceptable.

**Et deux formules de groupe se contredisent en data.** `rewards.json` dit 0,055 par joueur
supplémentaire (plafond 1,5) ; `progression.json` `party_xp_scaling` dit 0,4 par membre (plafond
1,0). À deux joueurs : 53 % de l'XP solo par tête contre 70 %. Une des deux est morte. Il faut
savoir laquelle **avant** de toucher au tuning de groupe.

Les deux sont hors du périmètre de l'agent contrats : c'est du `rewards.json` et du back.
