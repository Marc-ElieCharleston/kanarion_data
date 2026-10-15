# Pass Kanarion (abonnement mensuel) : conception technique

> **Mise à jour 2026-10-15 (codé, branches `vac_premium-pass`).** Écarts avec ce document :
> plusieurs pass possibles (`systems/premium_pass.json` `passes[]`, au lieu de `systems/premium.json` à un seul pass) ;
> état `account_passes (account_id, pass_id, active_until)` au lieu de la colonne `accounts.premium_until` ;
> seul écrivain la fonction SQL `premium_grant()` (migration **114**, la 113 est prise) ; messages **0x047F-0x0482**
> (état, clé de la semaine) ; pas encore d'achat aux diamants ni de magasins ; pas de `use_pass_key` (la vraie clé
> d'abord, la Clé de passage en secours) ; bonus des préinscrits dans `preregistration_bonus`. Le reste (régénération
> ×2 personnage et familier, téléportation gratuite, −10 % PNJ arrondi au supérieur, Clé de passage liée et exclue de
> la Tour, reset lundi 05:00 Paris, plafond de 4) est codé comme décrit. Bilan : back `docs/premium-pass-2026-10-15.md`.

Date : 2026-10-13. Passe en LECTURE SEULE (rien d'édité, commité, buildé ni poussé).
Spec de référence : `kanarion_database` `vac_collections:_meta/carnet/pass_premium.md` (décisions du 2026-10-13).
Références de code : back `main` sauf mention contraire (`vac_integration-all` décale les numéros de ligne
d'`economy_service.cpp` mais ne touche à aucun des points d'accroche ci-dessous). Client : `HEAD` du clone partiel.

Rappel de la règle : **un seul pass**, ~5-6 €/mois, jeu ouvert et illimité pour tous, **zéro puissance en combat**.
Contenu : régénération hors combat ×2 (PV et Souffle), téléportation gratuite, −10 % chez les marchands PNJ,
1 clé de donjon par semaine. Cosmétiques plus tard. Le `battle_pass` de `boutique.json` disparaît.

---

## 1. L'existant

### 1.1 Monétisation, compte, portefeuille

| Sujet | Où | Constat |
|---|---|---|
| Table `accounts` | `tools/db-migrate/init.sql:10` + ALTER 002, 007, 029, 030, 045, 076, 077, 078, 087, 101 | Aucune notion d'abonnement, de VIP ni de date d'expiration premium. Colonnes monétisation : `diamonds` (077), `bonus_character_slots` (076), `rename_tokens` (078), `shop_test_bonus_granted_at` (087), `arena_tokens` (101), `is_guest`. |
| Diamants (monnaie premium, au niveau du compte) | migr `077_diamonds_wallet_and_emote_ownership.sql` ; data `items/currencies.json` id `diamonds` (`enabled: false`, 100 diamants = 1 €) | Débit : `services/economy/src/db/queries.hpp:380-402` (`GET/DEBIT/CREDIT_ACCOUNT_DIAMONDS`). Achats atomiques et idempotents via `audit_log.idempotency_key`, sur le modèle de `emotes/emote_shop_manager.cpp:20-161` et `cosmetics/cosmetic_shop_manager.cpp:51-296` (cosmétique, jeton de renommage, place de personnage). |
| Ancienne monnaie premium au niveau du perso | `character_currencies.premium_currency`, `currency/currency_manager.cpp:31,69,544-569`, `combat_host.cpp:5616` | Héritage. À ne PAS utiliser (piège l'argent réel sur un seul personnage, déjà dit dans la migr 077). |
| Crédit en argent réel | `services/marketing/app.py:470-545` `POST /webhook/stripe` (FastAPI + asyncpg) | Seul `checkout.session.completed` est traité ; il crédite des diamants selon `PACKS` (`app.py:376-386`, 5/10/20 €). Idempotent sur `event.id`. Rien sur les abonnements, les remboursements ni les litiges. `POST /shop/token` (`app.py:553-582`) : JWT du jeu vérifié, **les invités sont refusés** (`guest_account`). |
| Drapeau boutique | migr `096_shop_enabled_flag.sql`, lu dans `services/character/src/character_service.cpp:373-412`, champ 10 de `CharacterListResponse` (`shared/flatbuffers/character.fbs:112`) | Fermé par défaut. Le client ajoute un **second verrou Android** (`scripts/ui/popups/cosmetic_shop_window.gd:300-340`, `onglets_pour(serveur_ouvre, est_android)`) : Stripe n'est jamais proposé sur Android (Google Play impose son système de paiement). |
| Fondateurs | `services/auth/src/auth/account_manager.cpp:540-566` | +1000 diamants pour une préinscription confirmée (+500 de test, migr 087). |
| Admin | `services/admin/src/db/admin_queries.cpp:247-255` | `give_currency diamonds` crédite le compte. Modèle à reprendre pour `premium grant`. |
| Boutique client | `scripts/ui/popups/cosmetic_shop_window.gd`, `scripts/network/gameplay/diamond_shop_service.gd` (GET `/shop/packs`, POST `/shop/token`, ouvre le lien Stripe), `scripts/network/cosmetic_shop_protocol.gd` | Aucun plugin de facturation mobile dans le client (seul addon Android : `addons/godot_google_signin`). Ni Google Play Billing ni StoreKit. |
| Opcodes boutique | `shared/protocol/messages.hpp` : 0x0433-0x043B (emotes, cosmétiques, jeton de renommage) ; état `CosmeticShopStateResponse` (`economy.fbs:1299-1310`) | Dernier opcode économie utilisé sur `vac_integration-all` : `0x047E` (EQUIPMENT_UPGRADE_RESPONSE). |
| `systems/boutique.json` (data, master) | bloc `battle_pass` (45 jours, 50 niveaux, piste premium 980 gemmes, `exclusive_elixirs: true`) | **Aucun code ne le lit** (ni back ni client : `git grep battle_pass` ne renvoie rien). Le supprimer est une modification de data uniquement. La boutique utilise encore le nom `gems` (et `qol_shop.currency: "gems"`) alors que la monnaie s'appelle `diamonds` dans `currencies.json` : à aligner au passage. |

**Il n'existe donc aucun code d'abonnement, de droit d'accès (entitlement) ni de reçu IAP.** Tout est à créer, mais
le socle est bon : portefeuille au niveau du compte, `audit_log` idempotent, webhook Stripe en Python,
`GatewayMessage.account_id` canonique déjà passé aux handlers de boutique (`economy_service.cpp:853-873`).

### 1.2 Régénération hors combat (PV et Souffle)

- Minuterie 1 Hz : `EconomyService::schedule_regen` / `do_regen_tick` (`services/economy/src/economy_service.cpp:7954-7971`,
  lancée à la ligne 448).
- Calcul : `HealthCoordinator::apply_regen_tick` (`services/economy/src/health/health_coordinator.cpp:753-833`).
  **Un seul UPDATE SQL** (ligne 780-797) :
  `hp_current = LEAST(hp_current + (stats_profile_snapshot->'stats'->>'hp_regen')::int, hp_max)`, idem `mp_current`
  avec `mp_regen` (le Souffle est la colonne `mp_*`). Filtres : vivant, en ligne (`OnlineRoster`), pas gelé par la
  Tour (`vitals_frozen_until`). Puis une notification 0x091A par perso.
- En combat, les PV et le Souffle appartiennent à l'ECS de `server-combat` (`combat_profile_builder.cpp:222-331`) ; le
  tick DB est écrasé par `post_combat_persist`. **On ne touche pas au combat.**
- **Point d'accroche** : l'UPDATE de `apply_regen_tick`, ligne 782-783. Multiplier le gain par 2 quand le compte du
  personnage a `premium_until > NOW()`. Ne JAMAIS modifier `stats_profile_snapshot.hp_regen` (il sert l'affichage
  et alimente le profil de combat).
- **Familier (ajout du propriétaire, 2026-10-14)** : ses PV et son Souffle remontent eux aussi ×2 hors combat. Autre
  service, autre minuterie : `FamiliarService::schedule_regen` / `do_regen_tick` (`services/familiar/src/familiar_service.cpp`,
  tick de 5 s, taux par classe lus dans `class_regen_loader`), écriture `PgStore::apply_regen(instance_id, hp_delta,
  mp_delta)`. Le familier est lié au COMPTE : le droit se lit sur le compte du propriétaire de la ligne de loadout.

### 1.3 Téléportation

- Serveur : `EconomyService::handle_teleport` (`economy_service.cpp:5870-5930`, opcode `TELEPORT = 0x044D`,
  `economy.fbs:1005-1016`). Liste de zones codée en dur (ligne 5887-5892), **coût fixe `const int64_t cost = 50;`
  (ligne 5902)**, débit d'or idempotent, réponse `gold_deducted`.
- Data : `systems/economy.json` `gold_sinks.teleportation` (`base_cost 50`, formule à la distance) : **non lue**.
  PNJ `npc_teleporter_elle` (service `fast_travel`, `entities/npcs.json:951`).
- Client : `scripts/ui/popups/teleport_window.gd:113` affiche « 50 » en dur, contrôle d'or local (lignes 283-288),
  envoie `TELEPORT` (ligne 293-294) ; réponse dans `scripts/network/gameplay/economy_response_handler.gd:299-309`.
  Le déplacement lui-même est fait ensuite par le client (le serveur ne vérifie ni zone découverte ni position).
- **Point d'accroche** : la ligne 5902. `cost = premium ? 0 : 50`, et ne pas appeler `currency_->modify` quand le
  coût est nul.

### 1.4 Prix d'achat chez les marchands PNJ

- `EconomyService::handle_buy_item` (`economy_service.cpp:4832-4971`, opcode `BUY_ITEM = 0x0449`) : registre
  `NpcShopRegistry` (quel PNJ vend quoi, niveau minimum), puis `unit_price = buy_price > 0 ? buy_price : sell_price*2`
  (ligne 4910-4912), refus si le prix est nul, **`total_cost = unit_price * quantity` (ligne 4921)**, débit,
  ajout à l'inventaire avec remboursement en cas d'échec.
- Client : `scripts/ui/popups/shop_window.gd:904-908` `_get_buy_price` recalcule le prix (même formule) pour
  l'affichage.
- Vérification d'arbitrage faite sur la data `items/*.json` (master) : 703 objets ont un `buy_price` ; **aucun**
  n'a un `sell_price` supérieur à 90 % du `buy_price`. Le −10 % n'ouvre donc pas de boucle achat-revente.
- **Point d'accroche** : la ligne 4921. `total_cost = ceil(unit_price * quantity * 90 / 100)` si abonné (arrondi
  au supérieur, sur le TOTAL, jamais en dessous de 1).

### 1.5 Clés de donjon

- Consommation déjà codée : `DungeonService` entrée (`services/dungeon/src/dungeon_service.cpp:166-183`) →
  `consume_key` (ligne 204-233) → `DungeonRunStore::find_inventory_key` (`services/dungeon/src/dungeon/run_store.cpp:94-103`,
  cherche un `item_template_id` exact) → `kanarion.economy.inventory.remove`. Erreur `DUNGEON_MISSING_KEY`.
  La clé requise vient de `dungeon_templates.key_required_item_id` (migr 053 / 095).
- Aujourd'hui : les Égouts `fissure_1` ne demandent aucune clé (migr 095) ; le Repaire des Bandits normal/hard/heroic
  en demande une (migr 053, donjon ancien). La Tour a son propre chemin (`tower_service.cpp:~508`, clés
  `key_tower_tier_N`).
- Branche `vac_dungeon-keys` (back `3c8ef79f`, `fd06cd56` ; data `334e634`) : drop par tranche de niveau du monstre
  (`server-combat/src/loot/loot_roller.cpp:~424`, `dungeon_key_drops.level_band_drops`, encore **vide** en data),
  et dans la Tour seule la clé du porteur monte de niveau, plus 2 % de chance de clé par étage.
- **Point d'accroche** : `DungeonService::consume_key`. Si la clé exacte manque (ou si le joueur le demande),
  accepter une « Clé de passage » du pass. Rien à faire dans le loot.
- **Attention** : tant qu'aucun donjon actuel ne demande de clé (paliers 2-3 des Égouts pas encore faits), la clé
  hebdomadaire du pass **ne sert à rien**. Il faut la sortir en même temps que les premières clés de palier, ou
  afficher le bonus comme « bientôt ».

---

## 2. Conception

### 2.1 Modèle de droit d'accès : `accounts.premium_until`, le serveur fait foi

- **Une seule colonne lue par le jeu** : `accounts.premium_until TIMESTAMPTZ NULL`. Le compte est abonné si
  `premium_until > now()`. Au niveau du compte (tous les persos en profitent), comme les diamants.
- **Un registre fait foi pour l'histoire** : `premium_grants` (une ligne par période achetée ou offerte) et
  `premium_subscriptions` (un abonnement de magasin et son état). `premium_until` est **recalculé** depuis le
  registre à chaque changement (achat, renouvellement, remboursement, cadeau d'admin), dans la même transaction.
  On ne fait jamais `premium_until = premium_until + 30 jours` à l'aveugle hors de cette fonction.
- Règle de recalcul (`recompute_premium_until(account_id)`) :
  1. périodes des abonnements de magasin (Google, Apple, Stripe) non révoquées : intervalles fixes donnés par le
     magasin (`expiry_time`) ;
  2. passes achetés aux diamants et cadeaux : des **durées** (30 jours), chaînées à la suite de la couverture
     existante au moment du recalcul ;
  3. `premium_until` = fin de la couverture continue qui contient `now()` (ou la plus récente si tout est passé).
  Conséquence voulue : si un abonnement est remboursé, les jours achetés en diamants « reculent » au lieu de
  laisser un trou gratuit, et un joueur qui cumule les deux ne perd pas de jours.
- Pour éviter la double facturation : refuser l'achat d'un pass aux diamants tant qu'un abonnement de magasin est
  actif et en renouvellement automatique (message « vous avez déjà un abonnement »), et plafonner les jours
  stockés aux diamants (365).
- Tout lecteur côté jeu fait **une requête par usage** (pas de cache client) :
  `SELECT a.premium_until > now() FROM characters c JOIN accounts a ON a.id = c.account_id WHERE c.id = $1`.
  Achats et téléportations sont rares, une requête indexée par clé primaire ne coûte rien. Le tick de régénération
  fait la jointure dans son UPDATE. Aucune valeur venant du client n'est crue.

### 2.2 Comment chaque bonus lit le droit

| Bonus | Service | Changement |
|---|---|---|
| Régénération ×2 hors combat | economy, `HealthCoordinator::apply_regen_tick` | `UPDATE characters c SET hp_current = LEAST(hp_current + regen * CASE WHEN a.premium_until > NOW() THEN $2 ELSE 1 END, hp_max) … FROM accounts a WHERE a.id = c.account_id AND …` ; `$2` = multiplicateur lu dans `systems/premium.json` (2). Même chose pour le Souffle. Rien dans `server-combat`. |
| Régénération ×2 hors combat du familier | familiar, `FamiliarService::do_regen_tick` | `hp_delta` et `mp_delta` multipliés par `familiar_out_of_combat_regen_multiplier` quand le compte du propriétaire a `premium_until > NOW()`. Lire les comptes abonnés en UNE requête par tick (`SELECT id FROM accounts WHERE premium_until > NOW() AND id = ANY($1)`), jamais une requête par familier. Ne pas toucher aux taux par classe (affichage, combat). |
| Téléportation gratuite | economy, `handle_teleport` | `cost = is_premium(character_id) ? 0 : 50` ; pas d'appel à `currency_->modify` si 0 ; `gold_deducted = 0` dans la réponse. Profiter du passage pour lire le coût de base dans la data au lieu du `50` en dur (et le client ne l'affiche plus en dur). |
| −10 % marchands PNJ | economy, `handle_buy_item` | `total_cost = premium ? max(1, ceil(unit_price*qty*(100-pct)/100)) : unit_price*qty`. Le −10 % ne touche QUE les PNJ (pas l'hôtel des ventes, ni la forge, ni le repos à la taverne, ni le comptoir de Milo en cristaux de Souffle). Pas de bonus à la revente (écarté par la spec : création d'or). |
| Clé hebdomadaire | economy (réclamation) + dungeon (consommation) | Voir 2.3. |

Impact économique (lien avec l'audit de l'or du 2026-10-11) : la téléportation gratuite et le −10 % retirent un peu
des puits d'or pour les abonnés. C'est modeste (50 or par voyage, −10 % sur les consommables) et ça ne crée pas
d'or. À surveiller dans les métriques une fois les puits renforcés.

### 2.3 Clé hebdomadaire

- **Objet** : `key_pass_weekly` « Clé de passage » dans `items/consumables.json`. **Liée au personnage, non
  échangeable, non vendable à l'HDV** (`tradeable: false`, `hdv_listable: false`, prix de revente 0). Sinon
  l'abonnement deviendrait une source d'or vendable (argent réel → or), ce que la spec refuse.
- **Usage** : remplace la clé de N'IMPORTE QUEL donjon à clé (`dungeon_templates.key_required_item_id` non nul),
  dans la limite du niveau requis du donjon. **Exclue de la Tour infinie** (les clés de palier sont une échelle
  élitiste ; une clé payante y fausserait le classement de saison).
- **Ordre de consommation** : par défaut la vraie clé d'abord (le joueur garde sa clé de passage, plus souple) ;
  nouveau champ `use_pass_key` dans `EnterZoneRequest` pour forcer la clé de passage. Si la vraie clé manque, la clé
  de passage est prise automatiquement, et `EnterZoneResponse.pass_key_used = true`.
- **Réinitialisation** : chaque **lundi à 05:00, heure de Paris** (heure creuse, changement d'heure géré). Identifiant
  de semaine calculé en SQL, jamais par le client :
  `date_trunc('week', (now() AT TIME ZONE 'Europe/Paris') - interval '5 hours')::date`.
- **Réclamation, pas de cumul** : une réclamation **par compte et par semaine** (table `premium_weekly_claims`,
  clé primaire `(account_id, week_start)`), faite depuis le panneau du Pass, pour le perso connecté. Une semaine non
  réclamée est perdue (pas de rattrapage). Plafond de détention : refus si le perso possède déjà 4 clés de passage
  (évite le stock de toute une année d'abonnement ; valeur dans la data).
- **Droit** : il faut être abonné **au moment de la réclamation**. Pas de prorata.

### 2.4 À l'expiration

- Immédiat et sans action : chaque bonus relit `premium_until` à chaque usage. La régénération repasse ×1 au tick
  suivant, la téléportation redevient payante, le −10 % disparaît.
- **Rien n'est retiré** : les clés de passage déjà réclamées restent utilisables, les achats faits restent. Seule la
  clé de la semaine en cours n'est plus réclamable.
- Le serveur pousse `PREMIUM_STATUS_PUSH` si le joueur est en ligne quand ça change (expiration détectée par le
  balayage `do_cleanup`, achat, remboursement), pour mettre l'interface à jour. Ce n'est qu'un confort d'affichage,
  pas une condition de justesse.
- Délai de grâce de magasin (paiement refusé) : on suit la date d'expiration renvoyée par Google ou Apple (ils
  prolongent eux-mêmes pendant la grâce). Pas de tolérance maison en plus.

### 2.5 Parcours d'achat

Principe commun : **le client ne fait que lancer l'achat et transmettre la preuve ; le serveur vérifie auprès du
magasin, puis écrit le registre**. Tout passe par `services/marketing/app.py` (Python), qui a déjà l'accès à la base,
la vérification du JWT du jeu et le webhook Stripe, et dispose des bibliothèques officielles (Google API client,
`app-store-server-library` d'Apple, `stripe`). Comptes invités refusés (comme `/shop/token`) : il faut lier un compte
d'abord, sinon l'abonnement serait perdu avec l'appareil.

**Android (Google Play Billing, obligatoire pour un bien numérique)**
1. Client : plugin officiel Godot Google Play Billing ; achat du produit d'abonnement `kanarion_pass_monthly` avec
   `obfuscatedAccountId = sha256(account_id)` (lie l'achat au compte).
2. Client → `POST /iap/google/verify {purchase_token, product_id}` (Bearer JWT du jeu).
3. Serveur : `purchases.subscriptionsv2.get` (compte de service), contrôle du nom de paquet, du produit, de l'état,
   de l'identifiant obfusqué = compte du JWT ; `purchase_token` UNIQUE en base (un jeton ne peut servir qu'à un
   compte) ; gestion de `linkedPurchaseToken` (réabonnement) ; **acknowledge sous 3 jours** sinon Google rembourse.
4. Notifications temps réel (RTDN, Pub/Sub en push) → `POST /webhook/google-rtdn` : renouvellement, annulation,
   grâce, suspension, expiration, révocation. Chaque notification relance `subscriptionsv2.get` (on ne croit pas
   le contenu de la notification), puis `recompute_premium_until`.
5. Remboursements : API `voidedpurchases` interrogée chaque jour en plus des notifications.

**iOS (StoreKit 2)**
1. Client : plugin StoreKit 2 ; `appAccountToken = account_id` (UUID) à l'achat.
2. Client → `POST /iap/apple/verify {signed_transaction}` (JWS).
3. Serveur : vérification de la chaîne de certificats Apple (`SignedDataVerifier`), bundle id, produit,
   `appAccountToken` = compte du JWT, `originalTransactionId` UNIQUE ; état via App Store Server API.
4. App Store Server Notifications V2 → `POST /webhook/apple` (JWS vérifié) : `SUBSCRIBED`, `DID_RENEW`,
   `DID_FAIL_TO_RENEW`, `EXPIRED`, `REFUND`, `REVOKE`, `DID_CHANGE_RENEWAL_STATUS`.
5. Obligatoire chez Apple : bouton « Restaurer les achats », lien de gestion de l'abonnement, texte légal (prix,
   durée, renouvellement automatique, résiliation).

**Web et PC (Stripe Billing)**
- `POST /shop/subscription/checkout` → Checkout Stripe en `mode=subscription`, `metadata.account_id`.
- Webhook existant étendu : `checkout.session.completed` (mode subscription), `invoice.paid` (période jusqu'à
  `current_period_end`), `customer.subscription.updated/deleted`, `charge.refunded`, `charge.dispute.created`
  (révocation). Sur Android, l'onglet Stripe reste fermé (verrou client existant). Sur iOS également.
- Règles des magasins : ne jamais montrer dans l'appli mobile un lien ou un prix vers le web (anti-orientation).
  Un abonnement pris sur le web reste valable sur mobile (« multiplateforme », autorisé).

**Aux diamants (passe de 30 jours, sans renouvellement)**
- Comme Dofus avec les Ogrines : `PREMIUM_BUY_WITH_DIAMONDS` dans le service economy, sur le modèle exact de
  `handle_buy_rename_token` (`economy_service.cpp:1266`) : débit atomique + ligne `premium_grants` + recalcul +
  `audit_log` idempotent, en une transaction.
- Prix proposé : **550 diamants** (≈ 5,50 €) pour 30 jours, dans `systems/premium.json`. Les fondateurs (1000 + 500)
  ont ainsi environ 2 mois offerts : c'est cohérent avec un geste de lancement.
- Plus tard (option, non décidé) : un échange diamants ↔ or entre joueurs, à la Dofus, qui permettrait aux non-payeurs
  de s'offrir le pass avec de l'or.

**Prix** : même prix partout (5,99 €/mois sur les magasins). Google prend 15 % sur les abonnements, Apple 15 %
(Small Business Program) ; Stripe environ 1,5 % + 0,25 €. Le prix et les identifiants de produits restent côté
serveur (config de `marketing`), jamais dans la data publique (même règle que `currencies.json` pour les diamants).

### 2.6 Suppression du `battle_pass` et migration

- `systems/boutique.json` : supprimer le bloc `battle_pass` (personne ne le lit, aucun joueur n'a rien acheté
  dessus → **aucune migration de données joueur**). Le remplacer par `"premium_pass": {"see": "systems/premium.json"}`.
- Les récompenses de la « piste gratuite » (or, tickets) ne reviennent pas sous forme de pass : si on veut une
  progression saisonnière gratuite, elle passe par les succès ou les événements, ouverte à tous.
- Aucun élixir n'est réservé aux payants : si des élixirs étaient prévus pour la piste premium, ils vont au loot, au
  craft ou aux marchands, pour tout le monde.
- Au passage : `currencies.gems` → `diamonds` et `qol_shop.currency: "gems"` → `"diamonds"` ; `currencies.json`
  `gold.uses` garde `teleport`.
- `pass_premium.md` du carnet : ajouter un lien vers ce document une fois validé.

---

## 3. Forme des données et protocole

### 3.1 `systems/premium.json` (nouveau, data publique)

```json
{
  "_meta": {
    "version": "1.0",
    "last_updated": "2026-10-13",
    "description": "Pass Kanarion : un seul abonnement mensuel, confort et gain de temps, jamais de puissance en combat. Lu par economy (bonus, achat aux diamants, clé hebdo) et dungeon (clé de passage). Prix en euros et identifiants de produits des magasins : BACKEND uniquement.",
    "rule": "aucune stat, aucun bonus en combat, aucun contenu fermé aux non-abonnés"
  },
  "pass": {
    "id": "kanarion_pass",
    "name_fr": "Pass Kanarion",
    "name_en": "Kanarion Pass",
    "period_days": 30
  },
  "benefits": {
    "out_of_combat_regen_multiplier": 2,
    "familiar_out_of_combat_regen_multiplier": 2,
    "teleport_free": true,
    "npc_buy_discount_percent": 10,
    "weekly_key": {
      "item_id": "key_pass_weekly",
      "per_week": 1,
      "reset": { "weekday": "monday", "hour": 5, "timezone": "Europe/Paris" },
      "max_held": 4,
      "claim_scope": "account",
      "excluded_content": ["tower"]
    }
  },
  "diamond_offer": {
    "enabled": true,
    "price_diamonds": 550,
    "grant_days": 30,
    "max_banked_days": 365,
    "blocked_while_store_subscription_active": true
  },
  "cosmetics": {
    "_comment": "Plus tard : auras, ailes, faites par un artiste. Rien d'exclusif en jeu.",
    "items": []
  }
}
```

Et dans `items/consumables.json` :

```json
{
  "id": "key_pass_weekly",
  "name_fr": "Clé de passage",
  "name_en": "Passage Key",
  "description_fr": "Ouvre n'importe quel donjon à clé de votre niveau, une fois. Ne s'échange pas.",
  "type": "key",
  "stack_max": 10,
  "tradeable": false,
  "hdv_listable": false,
  "sell_price": 0,
  "bind": "character"
}
```

### 3.2 Base de données (migration `113_premium_pass.sql`, numéro à confirmer au merge)

```sql
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS premium_until TIMESTAMPTZ;

CREATE TABLE IF NOT EXISTS premium_subscriptions (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id       UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    provider         VARCHAR(16) NOT NULL CHECK (provider IN ('google_play','app_store','stripe')),
    external_id      VARCHAR(255) NOT NULL,      -- purchaseToken / originalTransactionId / sub_xxx
    product_id       VARCHAR(128) NOT NULL,
    status           VARCHAR(24) NOT NULL,       -- active | grace | on_hold | canceled | expired | revoked
    auto_renew       BOOLEAN NOT NULL DEFAULT TRUE,
    expires_at       TIMESTAMPTZ,
    last_verified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    raw              JSONB,
    UNIQUE (provider, external_id)
);

CREATE TABLE IF NOT EXISTS premium_grants (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id      UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    source          VARCHAR(16) NOT NULL,        -- google_play | app_store | stripe | diamonds | admin | gift
    subscription_id UUID REFERENCES premium_subscriptions(id),
    period_start    TIMESTAMPTZ,                 -- fixe pour les magasins
    period_end      TIMESTAMPTZ,
    duration_days   INT,                         -- pour diamants / cadeaux (chaînés au recalcul)
    revoked_at      TIMESTAMPTZ,
    revoke_reason   VARCHAR(32),                 -- refund | chargeback | admin
    idempotency_key VARCHAR(255) NOT NULL UNIQUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_premium_grants_account ON premium_grants(account_id);

CREATE TABLE IF NOT EXISTS premium_weekly_claims (
    account_id   UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    week_start   DATE NOT NULL,
    character_id UUID NOT NULL,
    claimed_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (account_id, week_start)
);
```

Plus : `INSERT INTO server_flags ('premium_enabled', FALSE)` (même logique que `shop_enabled` : le client et le
serveur partent avant que les magasins soient configurés) et une ligne `key_pass_weekly` dans les items connus
du serveur.

### 3.3 Messages (FlatBuffers, service economy, opcodes à confirmer après `0x047E`)

| Opcode | Sens | Contenu |
|---|---|---|
| `PREMIUM_STATE_REQUEST` 0x047F | C→S | vide |
| `PREMIUM_STATE_RESPONSE` 0x0480 | S→C | `active:bool`, `premium_until_ms:int64`, `source:string`, `auto_renew:bool`, `provider:string`, `weekly_key_claimable:bool`, `weekly_key_reason:string` (clé de traduction : déjà réclamée, plafond, non abonné), `next_week_reset_ms:int64`, `regen_multiplier:int`, `npc_discount_percent:int`, `teleport_free:bool`, `diamond_price:int64`, `diamond_offer_available:bool`, `premium_enabled:bool` |
| `PREMIUM_CLAIM_WEEKLY_KEY_REQUEST` 0x0481 | C→S | `idempotency_key` |
| `PREMIUM_CLAIM_WEEKLY_KEY_RESPONSE` 0x0482 | S→C | `success`, `error`, `item_instance_id`, `next_week_reset_ms` |
| `PREMIUM_BUY_WITH_DIAMONDS_REQUEST` 0x0483 | C→S | `idempotency_key` (prix lu côté serveur) |
| `PREMIUM_BUY_WITH_DIAMONDS_RESPONSE` 0x0484 | S→C | `success`, `error`, `new_diamonds`, `premium_until_ms` |
| `PREMIUM_STATUS_PUSH` 0x0485 | S→C | même table que l'état |

Ajouts en fin de table (compatibles) :
- `CharacterListResponse` champ 11 `premium_until_ms:int64 = 0` (statut dès la connexion).
- `BuyItemResponse` champ 4 `discount_percent:int32 = 0` (le client affiche la remise réellement appliquée).
- `TeleportResponse` : rien (`gold_deducted = 0` suffit) ; champ 4 `free_by_pass:bool` pour le message.
- `EnterZoneRequest` champ 2 `use_pass_key:bool = false` ; `EnterZoneResponse` champ 10 `pass_key_used:bool`.

HTTP (`services/marketing/app.py`, Bearer JWT du jeu, invités refusés) :
`POST /iap/google/verify`, `POST /iap/apple/verify`, `POST /shop/subscription/checkout`,
`POST /webhook/google-rtdn`, `POST /webhook/apple`, `POST /webhook/stripe` (étendu), `GET /premium/products`
(prix affichable, pour le web seulement : sur mobile, c'est le magasin qui donne le prix localisé).

---

## 4. Plan de mise en œuvre

### 4.1 Lots, fichiers, effort

| # | Lot | Fichiers | Effort |
|---|---|---|---|
| 1 | Data | `systems/premium.json` (nouveau), `items/consumables.json` (`key_pass_weekly`), `systems/boutique.json` (retrait `battle_pass`, `gems` → `diamonds`), validateur dans `scripts/` | 0,5 j |
| 2 | Migration + registre | `tools/db-migrate/113_premium_pass.sql` ; module `services/economy/src/premium/premium_store.{hpp,cpp}` (`is_premium(character_id)`, `recompute_premium_until`, `grant`, `revoke`) ; même fonction de recalcul en SQL (fonction PL/pgSQL `recompute_premium_until(uuid)`) pour que Python et C++ partagent UNE règle | 1,5 j |
| 3 | Bonus en jeu | `health_coordinator.cpp:780-797` (UPDATE … FROM accounts), `economy_service.cpp:5902` (téléportation), `economy_service.cpp:4921` (remise), chargement de `premium.json` au démarrage d'economy ; `familiar_service.cpp` `do_regen_tick` (familier) + chargement de `premium.json` au démarrage de familiar | 1,5 j |
| 4 | Clé hebdomadaire | handler de réclamation dans economy (transaction : vérif abonné + insert `premium_weekly_claims` + `inventory_->add_item`) ; `dungeon_service.cpp:166-233` + `run_store.cpp:94` (repli sur `key_pass_weekly`, exclusion Tour) ; `dungeon.fbs` | 1 j |
| 5 | Protocole + état | `shared/protocol/messages.hpp`, `economy.fbs`, `character.fbs` (champ 11), dispatch `economy_service.cpp:~850`, `character_service.cpp:~373` ; push sur expiration dans `do_cleanup` ; commande admin `premium grant/revoke` (`admin_queries.cpp`) | 1 j |
| 6 | Achat aux diamants | handler sur le modèle de `handle_buy_rename_token` | 0,5 j |
| 7 | Stripe abonnement (web/PC) | `app.py` : checkout, webhook étendu, remboursements et litiges ; produits dans `config/marketing.json` ; Stripe Customer Portal pour la résiliation | 1,5 j |
| 8 | Google Play | `app.py` : verify + RTDN + acknowledge + voidedpurchases (job quotidien) ; compte de service ; Pub/Sub ; produit dans la Play Console | 2 j |
| 9 | Apple | `app.py` : verify JWS + notifications V2 ; clé App Store Server API ; produit dans App Store Connect | 2 j (si l'appli iOS existe ; sinon reporter) |
| 10 | Client | voir 4.4 | 3-4 j |
| 11 | Tests | voir 4.2 | 2 j |

Total : environ **15-17 jours** pour tout ; **~6 jours** pour un premier palier utile (lots 1-7 : bonus, clé, diamants,
Stripe web, client sans magasins mobiles), puis Google Play, puis Apple.

Ordre conseillé : lots 1-5 derrière `premium_enabled = FALSE` (testables avec `premium grant` admin), puis 6-7, puis
8, puis 9. La clé hebdomadaire n'a de sens qu'avec les premières clés de palier (`vac_dungeon-keys` + contenu des
Égouts) : la mettre en service en même temps.

### 4.2 Tests

- Unitaires C++ (gtest, comme `services/economy/tests/unit`) : remise (arrondi au supérieur sur le total, jamais 0,
  quantité 1 et 99) ; téléportation gratuite sans écriture d'or ; recalcul de `premium_until` (abonnement seul,
  diamants seuls, cumul, remboursement au milieu, jours chaînés qui reculent, plafond 365) ; calcul de la semaine
  (lundi 04:59 / 05:00 Paris, passage heure d'été et heure d'hiver, réveillon).
- Intégration (`tests/integration`, Python) : régénération ×2 pour un abonné et ×1 pour un autre dans le même tick, pour le personnage ET pour son familier ;
  réclamation deux fois dans la même semaine refusée ; plafond de 4 ; abonnement expiré entre ouverture du panneau
  et réclamation refusé ; entrée de donjon avec clé de passage, avec vraie clé, avec les deux et `use_pass_key` ;
  Tour refuse la clé de passage ; rejouer la même `idempotency_key` ne débite pas deux fois.
- Python (`services/marketing`, comme `test_shop_token.py`) : webhook Stripe rejoué (idempotent), `invoice.paid`
  prolonge, `charge.refunded` révoque ; Google : jeton déjà lié à un autre compte refusé, identifiant obfusqué
  différent refusé, acknowledge appelé ; Apple : JWS mal signé refusé, `appAccountToken` différent refusé.
- Data : test que tout objet vendu par un PNJ a `sell_price ≤ 0,9 × buy_price` (aujourd'hui vrai pour 703 objets),
  pour que la remise n'ouvre jamais d'arbitrage plus tard.
- Garde-fou de la règle : test qui échoue si `premium.json` contient une clé de stat de combat
  (`shared/domain/stat_keys.hpp`).

### 4.3 Risques

| Risque | Parade |
|---|---|
| Faux reçu, reçu rejoué sur un autre compte | Vérification serveur uniquement, auprès du magasin ; `UNIQUE (provider, external_id)` ; identifiant de compte intégré à l'achat (`obfuscatedAccountId`, `appAccountToken`, `metadata.account_id`) et comparé au compte du JWT. |
| Achat Google non acquitté → remboursé au bout de 3 jours | Acknowledge dans `/iap/google/verify`, plus un job qui rattrape les achats non acquittés. |
| Notifications perdues ou en retard | Toujours relire l'état auprès du magasin ; job quotidien de réconciliation (abonnements actifs dont `expires_at` est passé ou proche). |
| Remboursements et litiges | Révocation du grant + recalcul ; on ne reprend pas les clés de passage déjà réclamées (montant faible) ; journal `audit_log` ; liste des comptes à remboursements répétés pour l'admin. |
| Fuseau horaire, changement d'heure | `TIMESTAMPTZ` en UTC partout ; seule la semaine de la clé utilise `Europe/Paris`, calculée en SQL ; tests aux deux changements d'heure. |
| Horloge du client | Le client n'envoie jamais de date ; il affiche `premium_until_ms` et `next_week_reset_ms` donnés par le serveur. |
| Règles des magasins | Pas de Stripe ni de lien web dans les applis mobiles ; restaurer les achats et gérer l'abonnement sur iOS ; textes légaux ; droit de rétractation UE (case à cocher sur le web pour un service commencé tout de suite). |
| Comptes invités | Achat refusé tant que le compte n'est pas lié (règle déjà en place pour les diamants). |
| Clé hebdomadaire inutile aujourd'hui | Ne l'activer qu'avec les premières clés de palier ; sinon l'afficher « bientôt ». |
| Puits d'or affaiblis (audit du 2026-10-11) | Remise limitée aux PNJ, pas de bonus de revente, clé non échangeable ; suivre la part d'or dépensée en téléportation et chez les PNJ avant/après. |
| Double chemin de vérité (Python et C++) | Une seule fonction SQL `recompute_premium_until` appelée par les deux. |
| Conflits avec les autres sessions | Points touchés dans `economy_service.cpp` très localisés (deux lignes) ; numéros de migration et d'opcodes à reprendre au moment du merge (`vac_integration-all` est déjà à 112 et 0x047E). |

### 4.4 Interface client

- **Panneau « Pass »** : nouvel onglet de `cosmetic_shop_window.gd` (ou fenêtre dédiée ouverte depuis le HUD) :
  les 4 avantages en clair, statut (« Actif jusqu'au 12 novembre », « Se renouvelle » / « Ne se renouvelle pas »),
  bouton d'achat selon la plateforme (Google Play sur Android, StoreKit sur iOS, Stripe sur web/PC, toujours
  « 550 diamants »), bouton « Gérer mon abonnement » (lien du magasin ou portail Stripe), « Restaurer » sur iOS,
  bouton « Réclamer la clé de la semaine » avec le compte à rebours jusqu'à lundi 05:00.
- **Plugins** : Godot Google Play Billing (Android), plugin StoreKit 2 (iOS) ; nouveau `premium_service.gd` sur le
  modèle de `diamond_shop_service.gd` (lance l'achat, envoie la preuve au serveur, relit l'état).
- **Marchand** (`shop_window.gd:904`) : afficher le prix barré et le prix remisé si abonné (ou, plus simple et sans
  divergence possible, afficher le total après réponse grâce à `BuyItemResponse.discount_percent`).
- **Téléportation** (`teleport_window.gd:113, 283-288`) : coût « Gratuit (Pass) » si abonné ; retirer le « 50 » en dur.
- **Donjon** : dans la fenêtre « clé requise », proposer « Utiliser une Clé de passage » quand le joueur en a une.
- **Badge discret** à côté du nom ou de la barre de vie (pas de couleur de nom réservée : ce serait un cosmétique).
- **Textes** FR/EN dans les fichiers de traduction ; expliquer la règle « confort, jamais de puissance ».
- Respecter le drapeau `premium_enabled` (et le verrou Android existant pour l'onglet Stripe).
