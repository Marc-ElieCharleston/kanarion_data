# Collections : contenu horizontal

Document de CONCEPTION (2026-10-03, vacances). Rien n'est implémenté. Inventaire fait par un agent
sur la copie du PC de la maison, **probablement en retard** : `kanarion_lore` date du 2026-04-26, et
le client cite `kanarion_lore/progression_et_acte1.md`, absent ici. À recouper avec le lore du PC du
bureau avant toute écriture de pages.

## 0. Décisions du propriétaire

- Contenu horizontal : des choses à collectionner et à découvrir. Récompenses : titres, cosmétiques,
  emotes, éventuellement un petit bonus de compte. Pas de puissance brute.
- Base : **une dizaine de livres de plusieurs pages qui racontent l'histoire du monde, avec le VRAI
  lore**. Jamais de pages vides.
- Les autres collections proposées plaisent (à discuter) : bestiaire, album des familiers, carnet
  des murmures, cartographie, reliques de la Faille, trophées de chasse, herbier, codex Koro.
- **Où tombent les pages** (2026-10-03) :
  - combats des événements de fissure ;
  - coffres ;
  - faible taux dans les groupes 5 étoiles ;
  - certaines récompenses de quête.
- **Les pages s'échangent** : hôtel des ventes et échange direct.
- Rappel : les futures quêtes liées au lore auront des choix pour le joueur.

L'idée était déjà écrite par le propriétaire : `_meta/ideas_to_integrate.json` l.232-262
(`collectible_system`, recommandation « cosmétiques + petit bonus de collection ») et
`_meta/suggestions/04_progression_systems.txt` l.264-362 (reliques historiques qui débloquent une
entrée de lore, paliers 10 / 50 / 200 / 500, onglet « Collections »).

## 1. Les livres d'histoire

### 1.1 Le texte existe déjà

| Source | Contenu | Taille | Déjà découpé |
|---|---|---|---|
| `kanarion_lore/lore.json` : prologue, livre_premier → livre_quatrieme, epilogue | l'histoire complète | ~1 900 mots, 32 chapitres | **oui**, en livres et chapitres |
| `lore.json` : `arc_tour_asher`, `motivation_imitateur`, `le_marcheur`, `mecanisme_fissures`, `les_murmures` | thèmes | ~2 000 mots | en sous-clés |
| `archive/Kanarian Online Lore (1).txt` l.607-784 | « Chronique des Origines », version révisée | ~720 mots | 5 blocs |
| même fichier l.790-943 | **version fragmentée : 40 fragments en 10 groupes** (le X, « Fragment final », à ne donner qu'une fois) | ~570 mots | **oui** |
| même fichier l.1326-1553 | « Le Texte de la Faille » | ~970 mots | prose finie |
| `chronology.md`, `world_building.md` | calendrier, Souffle, corruption, factions | ~7 000 mots | par sections |

Aucun de ces textes n'est montré en jeu aujourd'hui.

### 1.2 Découpage proposé : 10 livres, ~70 pages

| # | Livre | Sources | Pages |
|---|---|---|---|
| 1 | La Parole (Création) | prologue + révisée l.608-626 + fragments I + chronology l.8-19 | 5 |
| 2 | L'Harmonie et le Premier Témoin | livre_premier ch. 1-5 + chronology l.21-37 + fragments II | 7 |
| 3 | La Chute et l'Alliance | livre_premier ch. 6-8 + révisée l.630-657 + fragments III-IV | 6 |
| 4 | Le Temps de X | livre_second ch. 1-4 + révisée l.661-704 + fragments V-VI + `le_marcheur` | 7 |
| 5 | Le Monde malade et le Souffle | livre_second ch. 5-6 + world_building (Souffle, corruption, éclats) | 8-10 |
| 6 | La Tour d'Asher | `arc_tour_asher` + chronology l.73-140 | 8-10 |
| 7 | Les Fissures | `mecanisme_fissures` + chronology l.143-172 + cinématique d'Ezra | 5 |
| 8 | Le Texte de la Faille | archive l.1326-1553 | 8 |
| 9 | L'Imitateur et les Murmures | `motivation_imitateur` + livre_troisieme + `les_murmures` | 7 |
| 10 | La Division et ce qui demeure | livre_quatrieme + épilogue + fragments VII-IX (X à part) | 6-7 |

Travail d'édition nécessaire : accents manquants dans les `.md`, transitions entre sources.

### 1.3 Règles proposées

- **Une page = un objet** échangeable (HDV, échange direct). Une fois **lue**, elle est ajoutée au
  livre du compte et l'objet est consommé ; on peut revendre les doublons.
- **Les livres qui dévoilent X et l'Imitateur (4, 9, 10) sont verrouillés par la progression** : leurs
  pages ne tombent qu'à partir d'un certain niveau ou d'une étape de l'histoire, car le lore veut
  « distiller lentement ». **[À DÉCIDER]** les seuils.
- **Le lieu de drop suit le thème** : les pages des Fissures tombent dans les combats de fissure, celles
  de la Tour près de la Tour, etc. Les livres 1-3 (les plus anciens) sont les plus faciles à trouver.
- Les 5 étoiles donnent une chance faible sur **n'importe quelle** page de leur tranche de niveau.
- Le « Fragment final » (X) : unique, non échangeable, récompense de quête. **[À DÉCIDER]**
- Livre complet → titre (et peut-être un cosmétique). Les 10 livres complets → titre rare.

### 1.4 Contradictions du lore à trancher AVANT d'écrire les pages

Probablement déjà réglées dans le lore du bureau : à vérifier là-bas.

1. **L'Imitateur** : présent dès l'origine (« Premier Témoin », `lore.json`, chronology l.13 et l.28)
   OU apparu pendant le temps de X (chronique révisée l.679-691) ?
2. **Arrivée du joueur** : avant la Chute (trame de l'archive l.139-200) OU bien après, en EP 1247
   (chronique révisée l.718, chronology l.105) ?
3. **Les Fissures** : elles existaient avant (intro en jeu, `config/game.json` écran 2) OU elles
   naissent de la Tour et du Souffle (chronology l.112-172) ?
4. **Noms** : acte 2 « Âge des Cendres » OU « Âge du Discernement » ; « Kanarian » OU « Kanarion » ;
   le village « Kanarion » renommé Havreden.
5. **Niveau du choix de faction** : 40-50, 40-60 ou 60 selon la source.
6. `AUDIT_COHERENCE.md` §5 et §8 : murmures et répliques de X à corriger.

## 2. Les autres collections

| Collection | Ce qui existe | Ce qui manque | Effort |
|---|---|---|---|
| **Carnet des murmures** | 118 murmures écrits (`world/whispers.json`), 26 utilisés en jeu | sauvegarder les murmures vus (aujourd'hui en mémoire de session seulement, côté client) ; ne pas dire QUI parle (ambiguïté voulue) | faible |
| **Album des familiers** | 65 espèces × 5 raretés = 325 cases, table `familiars` | garder l'historique (un familier relâché disparaît ; collection plafonnée à 50) | faible |
| **Codex Koro** | 553 sorts × 5 rangs = 2 765 cartes ; source de succès `koro_cards_owned` | interface | faible |
| **Galerie des cinématiques** | 1 cinématique + l'intro | rien de bloquant | faible |
| **Trophées de chasse** | 16 boss et 14 élites actifs, packs 5 étoiles (3 %) | compter les victoires par boss et par espèce (le serveur ne compte que le total) ; il n'existe PAS de rareté « champion » | moyen |
| **Bestiaire** | 166 monstres actifs ; `lore.json` `progression_des_ennemis` (~1 300 mots) | **aucune description de monstre** : à écrire ; suivi des espèces vues | moyen + texte |
| **Cartographie** | 21 aires nommées dans Havreden | **aucun suivi des zones découvertes** ; lieux remarquables à définir | moyen |
| **Reliques de la Faille** | `mat_relic_r1..r5` du Collectionneur (intermédiaire de fabrication) | les transformer en objets de lore | moyen + texte |
| **Herbier / atlas des métiers** | 237 matériaux, 15 métiers | la récolte n'est pas branchée | plus tard |

### 2.1 Le bestiaire (décidé 2026-10-03 : descriptions liées au lore)

Modèle : le Journal du Chasseur de Hollow Knight, le Pokédex. Version légère :
- **une fiche par ESPÈCE** (46), pas par monstre (166) ; une ligne par stade (jeune, adulte,
  corrompu, alpha…) ;
- **1 à 3 phrases** de lore par espèce, à partir de `lore.json` `progression_des_ennemis` ;
- **débloquée par paliers** :
  1. première rencontre : nom et image ;
  2. 10 victoires : stats de base, archétype, déplacement ;
  3. 50 victoires : drops et faiblesses ;
  4. 100 victoires : le texte de lore ;
- c'est aussi **l'endroit où afficher les infos en jeu** (stats de base, passif d'espèce) ; la même fiche
  sert à l'album des familiers ;
- priorité : après les livres (il faut écrire les 46 textes, et suivre les victoires par espèce).

## 3. Systèmes sur lesquels bâtir

- **Succès** (data + serveur + client, le plus complet) : `systems/achievements.json` (145 succès,
  18 donnent un titre), service quête `achievement_catalog.hpp`, table `achievement_unlocks` au
  compte ou au personnage, fenêtre client par catégorie. Une collection peut être une **catégorie de
  succès** avec de nouvelles sources (`lore_pages_read`, `whispers_heard`, `species_owned`…).
- **Titres et cosmétiques** : `ui/cosmetics.json` (26 titres), table `account_cosmetics`. Le titre en
  récompense marche déjà de bout en bout (sauf l'affichage sur la plaque de nom, pas branché).
- **Emotes** : `ui/emotes.json` (80, dont 72 premium) ; il faut un mode « obtenue en récompense ».
- **Coffres de zone** (`chest_world.hpp`) et **événements de fissure** (`world_event_rewards`) : là où
  greffer le drop des pages.
- **Métier de Collectionneur** (maître : Yuki) : porte naturelle pour les reliques ; le Scribe pourrait
  « relier » les pages en livre.

## 4. Ordre proposé

1. Trancher les contradictions du lore (avec le lore du bureau).
2. **Livres d'histoire** : générer les pages depuis le vrai texte, objet page, livre au compte,
   drops (fissures, coffres, 5 étoiles, quêtes), titres.
3. Collections « gratuites » sur des données existantes : carnet des murmures, album des familiers,
   codex Koro, galerie des cinématiques.
4. Trophées de chasse (suivi des victoires par boss).
5. Bestiaire et cartographie (texte et suivi à créer).
6. Onglet « Collections » côté client (un seul écran pour tout).

## 5. Questions ouvertes

- [ ] Seuils de déverrouillage des livres 4, 9 et 10 (X, l'Imitateur).
- [ ] Le « Fragment final » : récompense de quête unique et non échangeable ?
- [ ] Récompenses : titre par livre ? cosmétique ? petit bonus de compte (lequel) pour les 10 livres ?
- [ ] Taux de drop des pages (fissure, coffre, 5 étoiles).
- [ ] Quelles collections après les livres, et dans quel ordre ?
