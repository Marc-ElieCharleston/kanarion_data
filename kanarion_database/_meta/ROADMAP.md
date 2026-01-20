# Kanarion Online - Roadmap & Ideas

## MVP Current (v0.1)
- [x] Combat system 2x5 grid
- [x] 6 classes with subclasses
- [x] Skills with cooldowns
- [x] Status effects (DoT, buffs, debuffs)
- [x] Party system (1 leader + 9 members = 10 slots)
- [x] Monster danger levels (1-5 stars)
- [x] Basic loot system
- [x] Database v3.0 (new_database/)
- [x] Dual targeting system (ally + enemy)
- [x] Dual target frames in combat (ally HP/buffs + enemy HP/debuffs)
- [x] GCD 2.0s pour combat strategique
- [x] Filler skills par classe
- [x] Counter debuffs (heal_reduction, shield_block)
- [x] Nerf Rogue skills (stab CD 4.5s, ambush power/ratio)
- [x] Rework Virtuoso → Cantor (resurrection skill)
- [x] Zoom in/out mobile (exploration + combat)

## Balance Tasks (IN PROGRESS)
- [ ] **Passifs incomplets** - 38/52 a completer
  - [ ] Nerf Rogue passifs (Cunning +5% crit_dmg → +3%, Shadow Mastery +10% → +5%)
  - [ ] Completer effects manquants toutes classes
  - [ ] Renommer passifs Cantor (Sacred Chant, Last Rites)
  - [ ] Fixer doublons (Inspiring Presence, Rhythm Master)
- [ ] Keystones system
- [ ] Equipment stats balancing

---

## Roadmap

### Phase 1: Core Multiplayer
- [ ] Server deployment (first test version)
- [ ] Real-time player sync
- [ ] Party system online validation
- [ ] Chat system (global, whisper, party)

### Phase 2: Group Finder System
- [ ] **Group Finder UI** - Search/create groups
  - Categories: `Normal`, `Dungeon`, `Raid`
  - Role tags: `DPS`, `Tank`, `Healer`, `Support`, `Debuffer`
  - Level range filter
- [ ] **Remote accept** - Join from anywhere
  - Option A: Teleport to leader
  - Option B: Arrow guide to leader location
- [ ] **Queue system** - Auto-match by role balance

### Phase 3: Raids (20v1+)
- [ ] **Raid groups** - MAX_RAID_SIZE = 20 players
- [ ] **Raid arenas** - Larger combat area with zoom out
- [ ] **World bosses** - Massive HP pools, multiple phases
- [ ] **Raid mechanics** - Positional requirements, role-specific duties

### Phase 4: Collectibles & Collections
- [ ] **Collection system** - Album/codex of found items
  - **Sources**:
    - Random spawns on maps (exploration reward)
    - 0.01% combat loot drops (ultra-rare)
    - Zone completion rewards
    - Event exclusives
  - **Ranks**: Common, Rare, Epic, Legendary, Mythic
  - **Set bonuses** - Complete a set for minor stat boosts
    - Example: "Forest Critters Set (5/5): +2% HP"
  - **Trading** - Sellable on AH (gold sink + lucky player income)
- [ ] **Titles** - Unlocked by collection milestones
- [ ] **Display cases** - Show off rare collectibles in player housing

### Phase 5: PvP Arena

#### 5.1 Modes
| Mode | Format | Description |
|------|--------|-------------|
| Duel | 1v1 | Pure skill, no carry |
| Tag Team | 2v2 | Synergies duo |
| Skirmish | 4v4 | Team composition |
| Battle | 8v8 | Large scale chaos |

#### 5.2 Infrastructure
- [ ] Queue system (file d'attente par mode)
- [ ] Matchmaking par rang ELO
- [ ] Arena maps dedicees (differents terrains)
- [ ] Anti-cheat server-side validation
- [ ] Anti-grief (penalites AFK/leave: -50 ELO, temp ban)
- [ ] Spectator mode

#### 5.3 Ranking System (ELO)
```
Points de depart: 1000

Gains/Pertes:
┌─────────────────┬──────────┬─────────┐
│ vs Rang         │ Victoire │ Defaite │
├─────────────────┼──────────┼─────────┤
│ Rang inferieur  │ +10-15   │ -20-25  │
│ Rang egal       │ +15-20   │ -15-20  │
│ Rang superieur  │ +20-30   │ -10-15  │
└─────────────────┴──────────┴─────────┘

Rangs:
  Bronze I-III:    0-999
  Silver I-III:    1000-1499
  Gold I-III:      1500-1999
  Platinum I-III:  2000-2499
  Diamond I-III:   2500-2999
  Master:          3000+
  Grandmaster:     Top 100 server
```

#### 5.4 Leaderboard
- [ ] Classement global par mode (1v1, 2v2, 4v4, 8v8)
- [ ] Classement par classe/subclass
- [ ] Historique des matchs (10 derniers)
- [ ] Stats detaillees (win rate, KDA, avg damage)
- [ ] Profil public joueur avec badges

#### 5.5 Seasons & Rewards
```
Duree saison: 3 mois

Rewards fin de saison:
┌──────────────┬────────────────────────────────────────────┐
│ Rang         │ Rewards                                    │
├──────────────┼────────────────────────────────────────────┤
│ Bronze       │ Titre + Border bronze                      │
│ Silver       │ Titre + Border + 500 gold                  │
│ Gold         │ Titre + Border + 1000 gold + Pet           │
│ Platinum     │ Titre + Border + 2000 gold + Mount         │
│ Diamond      │ Titre + Border + 5000 gold + Exclusive skin│
│ Master       │ Tout + Aura exclusive                      │
│ Grandmaster  │ Tout + Hall of Fame + Statue in town       │
└──────────────┴────────────────────────────────────────────┘

Reset: Soft reset (Rang / 2 + 500)
  Ex: Diamond 2500 → 1750 (Gold)
```

#### 5.6 PvP Balance Adjustments
```
PvP-specific modifiers (vs PvE):
- All damage: -30% (longer fights)
- Healing: -20% (anti-heal meta)
- CC duration: -40% (less frustrating)
- CC diminishing returns: 50% → 25% → immune (10s reset)

Cooldown adjustments:
- Resurrection: DISABLED in arena
- Ultimate skills: +50% CD

Banned in ranked:
- Consumables (potions) in 1v1
- Allowed in 2v2+ (strategy element)
```

---

## Ideas (Brainstorm)

### Collections Detailed Design
```
Collection Categories:
- Creatures: Monster illustrations (kill X to unlock)
- Artifacts: Rare items found in world
- Lore Pages: Story fragments scattered in zones
- Landscapes: Visit hidden scenic spots
- Boss Trophies: Defeat dungeon/raid bosses

Stat Bonuses (examples):
- 5 items collected: +1% Gold Find
- 10 items: +5 HP
- 25 items: +1% XP
- 50 items: +1 ATK
- 100 items: Unique title + cosmetic
```

### Raid Combat Camera
```
Normal combat: Default zoom (current)
Raid combat (20 players):
- Zoom out ~30-40%
- Smaller character sprites
- More visible arena
- Boss health bar prominent at top
- Role icons on player frames
```

### Group Finder Flow
```
1. Player opens Group Finder
2. Select: [Normal] [Dungeon] [Raid]
3. Select role: [DPS] [Tank] [Healer] [Support]
4. Browse listings OR create own group
5. Apply to group / Accept applicants
6. When accepted:
   - Popup: "Group found! [Teleport] [Navigate]"
   - Teleport: Instant join (costs gold?)
   - Navigate: Arrow points to leader
```

### Economy Considerations
- Collectibles as gold sink (completionists buy from AH)
- Teleport to group cost (optional convenience fee)
- Raid entry fees? (consumables, keys)

### Shop System (Fair Monetization)
```
┌─────────────────────────────────────────────────────────────────────┐
│                      DUAL SHOP SYSTEM                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  TOWN SHOPS (Gold)              PREMIUM SHOP (Diamonds)             │
│  ─────────────────              ─────────────────────               │
│  Location: In towns only        Location: Accessible ANYWHERE       │
│  Currency: Gold                 Currency: Diamonds (premium)        │
│                                                                     │
│  Items:                         Items:                              │
│  ✓ HP Potions                   ✓ HP Potions (SAME items)           │
│  ✓ MP Potions                   ✓ MP Potions (SAME items)           │
│  ✓ Food (HP regen)              ✓ Food (SAME items)                 │
│  ✓ Crafting materials           ✗ NOT available                     │
│  ✓ Skill books                  ✗ NOT available                     │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  PHILOSOPHY: "Pay for CONVENIENCE, not POWER"                       │
│                                                                     │
│  - SAME items available to ALL players                              │
│  - Premium = skip travel time (open shop mid-dungeon)               │
│  - F2P players just need to PLAN AHEAD                              │
│  - NO pay-to-win advantage in combat                                │
│  - Rewards organization over wallet                                 │
└─────────────────────────────────────────────────────────────────────┘

Use Cases:
- F2P: Stock up on potions before dungeon run
- Premium: Forgot potions? Buy mid-dungeon (convenience tax)
- Raid wipe: Premium users can restock without leaving
- Exploration: Premium can buy anywhere while exploring

Price Ratio (example):
- Town: 100 gold per HP Potion
- Premium: 5 diamonds per HP Potion (~50 gold equivalent?)
  → Slight "convenience tax" makes town shopping better value
```

---

## Technical Notes

### Group Size Constants
```gdscript
# main.gd
const MAX_PARTY_SIZE: int = 9   # + 1 leader = 10 (current)
const MAX_RAID_SIZE: int = 19   # + 1 leader = 20 (future)

# combat_layout.gd
const MAX_SLOTS: int = 10       # Per team (party)
const MAX_RAID_SLOTS: int = 20  # Per team (raids)
```

### Collectible Drop Chances
```
Normal mob: 0.01% (1 in 10,000)
Elite mob: 0.05% (1 in 2,000)
Boss: 0.5% (1 in 200)
World spawn: 1-5 per zone, 30min respawn, random location
```

---

*Last updated: 2026-01-12*
