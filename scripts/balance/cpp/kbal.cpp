// kbal: level-20 2v2 tournament allocation solver (C++ port of scripts/balance).
//
// Loads the tables exported by export_tables.py (level-20 stats and rotation plans
// solved with HiGHS MILPs), evaluates matchups with the combat.json pipeline, finds
// each team's play-to-win build by best response, solves the zero-sum game over the
// visited builds with HiGHS, and locks all four allocations so the fight is a coin flip.
//
// Build: make -C cpp        Run: cpp/kbal out/tables.bin --threads 16
#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <map>
#include <mutex>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#ifndef KBAL_NO_HIGHS
#include "Highs.h"
#endif

namespace {

constexpr double GCD = 2.0, HIT = 0.95, EPS = 1e-9, REDIRECT_CAP = 0.85;
constexpr int STAT_POINTS = 57;

enum { S_ATK, S_MAG, S_MAXHP, S_DEF, S_ARMOR, S_MAXMP, S_SHIELD, NSCAL };
enum { B_ATK_UP, B_MAG_UP, B_DMG_UP, B_CRIT_UP, B_CRITDMG_UP, B_ARMOR_UP, B_MR_UP, B_DR_UP, B_DEF_UP, B_EVA_UP,
       B_LS, B_HEALPOW_UP, B_ATK_DOWN, B_MAG_DOWN, B_DEF_DOWN, B_DMG_DOWN, NB_ };
enum { D_ARMOR_DOWN, D_MR_DOWN, D_DEF_DOWN, D_TAKEN, D_ATK_DOWN, D_MAG_DOWN, D_DMG_DOWN, D_HEALRED, D_DR_DOWN,
       D_CRIT_DOWN, D_CRITDMG_DOWN, ND_ };
// plan component offsets (see export_tables.py)
enum { C_DMG = 0, C_HITS = 14, C_PEN = 16, C_DOT = 18, C_POISON = 32, C_HEALFLAT = 33, C_HEALCOEF = 36, C_HOT = 57,
       C_SHFLAT = 60, C_SHCOEF = 63, C_SELF = 84, C_ALLY = 100, C_DEBUFF = 116, C_CC = 127, C_BLIND = 128, C_TAUNT = 129,
       C_CONF = 130, C_DISARM = 131, C_SLOW = 132, C_REDIR = 133, C_LS = 134, C_MPUSED = 148, C_TIME = 149, NCOMP_ = 150 };
// exported stat vector
enum { K_HP, K_MP, K_ATK, K_MAG, K_DEF, K_ARMOR, K_MR, K_CRIT, K_CRITDMG, K_APEN, K_MPEN, K_DMGPCT, K_DR, K_LS, K_SV,
       K_HEALRECV, K_TEN, P_ATK, P_MAG, P_HP, P_MP, P_ARMOR, P_MR, P_DEF, P_HEALPOW, P_SHPOW,
       I_ATKPCT, I_MAGPCT, I_TAKEN, I_DMGPCT, I_APEN, I_HEALPCT, I_SHPCT, NSTAT_ };

struct Tables {
    int nSub = 0, nT = 0, nW = 0, nMP = 0, nSkill = 0, nStat = 0, ncomp = 0;
    std::vector<double> T, W;
    std::vector<std::string> ids, base;
    std::vector<int> mainStat;                 // 0 = atk, 1 = mag
    std::vector<std::vector<std::string>> skills;
    std::vector<double> stats, plans, casts;
    std::map<std::string, int> index;

    const double* stat(int s) const { return &stats[(size_t)s * nStat]; }
    const double* plan(int s, int ti, int wi, int mp) const {
        return &plans[((((size_t)s * nT + ti) * nW + wi) * nMP + mp) * ncomp];
    }
    const double* cast(int s, int ti, int wi, int mp) const {
        return &casts[((((size_t)s * nT + ti) * nW + wi) * nMP + mp) * nSkill];
    }
};

bool load_tables(const std::string& path, Tables& t) {
    std::ifstream f(path, std::ios::binary);
    if (!f) { std::cerr << "cannot open " << path << "\n"; return false; }
    std::string line;
    std::getline(f, line);
    if (line != "KBAL1") { std::cerr << "bad magic\n"; return false; }
    std::getline(f, line);
    { std::istringstream ss(line); int nb, nd, ns; ss >> t.nSub >> t.nT >> t.nW >> t.nMP >> nb >> nd >> ns >> t.nSkill >> t.nStat >> t.ncomp;
      if (nb != NB_ || nd != ND_ || ns != NSCAL || t.nStat != NSTAT_ || t.ncomp != NCOMP_) { std::cerr << "layout mismatch\n"; return false; } }
    std::getline(f, line); { std::istringstream ss(line); double v; while (ss >> v) t.T.push_back(v); }
    std::getline(f, line); { std::istringstream ss(line); double v; while (ss >> v) t.W.push_back(v); }
    for (int i = 0; i < t.nSub; ++i) {
        std::getline(f, line); std::istringstream ss(line);
        std::string id, bc, names; int m, n; ss >> id >> bc >> m >> n >> names;
        t.ids.push_back(id); t.base.push_back(bc); t.mainStat.push_back(m); t.index[id] = i;
        std::vector<std::string> sk; std::stringstream ns(names); std::string tok;
        while (std::getline(ns, tok, ',')) sk.push_back(tok);
        t.skills.push_back(sk);
    }
    std::getline(f, line);
    if (line != "BIN") { std::cerr << "missing BIN marker\n"; return false; }
    auto rd = [&](std::vector<double>& v, size_t n) { v.resize(n); f.read(reinterpret_cast<char*>(v.data()), n * sizeof(double)); return (size_t)f.gcount() == n * sizeof(double); };
    if (!rd(t.stats, (size_t)t.nSub * t.nStat)) return false;
    if (!rd(t.plans, (size_t)t.nSub * t.nT * t.nW * t.nMP * t.ncomp)) return false;
    if (!rd(t.casts, (size_t)t.nSub * t.nT * t.nW * t.nMP * t.nSkill)) return false;
    return true;
}

struct Alloc { int hp = 0, mp = 0, off = 0, def = 0; };   // field order matters for pattern_search
inline bool operator==(const Alloc& a, const Alloc& b) { return a.hp == b.hp && a.mp == b.mp && a.off == b.off && a.def == b.def; }
inline int dist(const Alloc& a, const Alloc& b) { return (std::abs(a.hp - b.hp) + std::abs(a.mp - b.mp) + std::abs(a.off - b.off) + std::abs(a.def - b.def)) / 2; }

struct Stats {
    double hp, mp, atk, mag, def, armor, mr, crit, crit_dmg, apen, mpen, dmgpct, dr, ls, sv, heal_pct, shield_pct, heal_recv, innate_taken;
    double S[NSCAL];
};

Stats derive(const Tables& t, int sub, const Alloc& a) {
    const double* b = t.stat(sub);
    auto m = [&](int p) { return 1.0 + b[p] / 100.0; };
    Stats s{};
    int xatk = t.mainStat[sub] == 0 ? a.off : 0, xmag = t.mainStat[sub] == 1 ? a.off : 0;
    s.atk = (b[K_ATK] + xatk) * m(P_ATK) * (1.0 + b[I_ATKPCT] / 100.0);
    s.mag = (b[K_MAG] + xmag) * m(P_MAG) * (1.0 + b[I_MAGPCT] / 100.0);
    s.hp = (b[K_HP] + 5.0 * a.hp) * m(P_HP);
    s.mp = (b[K_MP] + 5.0 * a.mp) * m(P_MP);
    s.armor = (b[K_ARMOR] + a.def) * m(P_ARMOR);
    s.mr = b[K_MR] * m(P_MR) + 0.2 * s.mag;
    s.def = b[K_DEF] * m(P_DEF);
    s.crit = b[K_CRIT]; s.crit_dmg = b[K_CRITDMG];
    s.apen = b[K_APEN] + b[I_APEN]; s.mpen = b[K_MPEN];
    s.dmgpct = b[K_DMGPCT] + b[I_DMGPCT]; s.dr = b[K_DR]; s.ls = b[K_LS]; s.sv = b[K_SV];
    s.heal_pct = b[P_HEALPOW] + b[I_HEALPCT]; s.shield_pct = b[P_SHPOW] + b[I_SHPCT];
    s.heal_recv = b[K_HEALRECV]; s.innate_taken = b[I_TAKEN];
    s.S[S_ATK] = s.atk; s.S[S_MAG] = s.mag; s.S[S_MAXHP] = s.hp; s.S[S_DEF] = s.def; s.S[S_ARMOR] = s.armor; s.S[S_MAXMP] = s.mp; s.S[S_SHIELD] = 0.15 * s.hp;
    return s;
}

struct Member {
    int sub = 0; Alloc a; int wi = 1; Stats st{};
};
Member make_member(const Tables& t, int sub, Alloc a, int wi) { Member m; m.sub = sub; m.a = a; m.wi = wi; m.st = derive(t, sub, a); return m; }
Member default_build(const Tables& t, int sub) {
    int mp = (int)std::lround(0.15 * STAT_POINTS), off = (int)std::lround(0.45 * STAT_POINTS);
    return make_member(t, sub, Alloc{STAT_POINTS - mp - off, mp, off, 0}, 1);
}

inline double mitig(double x) { return 100.0 / (100.0 + std::max(x, 0.0)); }

struct SideCtx {
    const Member* m[2];
    const double* P[2];
    double buff[2][NB_];
    double cc, blind, taunt, confusion, disarm, slow, redirect;
    double debuff[ND_];
};

void side_context(const Tables& t, const Member* A, int ti, SideCtx& c) {
    for (int k = 0; k < 2; ++k) { c.m[k] = &A[k]; c.P[k] = t.plan(A[k].sub, ti, A[k].wi, A[k].a.mp); }
    for (int k = 0; k < 2; ++k)
        for (int b = 0; b < NB_; ++b) c.buff[k][b] = c.P[k][C_SELF + b] + c.P[1 - k][C_ALLY + b];
    c.cc = c.P[0][C_CC] + c.P[1][C_CC]; c.blind = c.P[0][C_BLIND] + c.P[1][C_BLIND]; c.taunt = c.P[0][C_TAUNT] + c.P[1][C_TAUNT];
    c.confusion = c.P[0][C_CONF] + c.P[1][C_CONF]; c.disarm = c.P[0][C_DISARM] + c.P[1][C_DISARM];
    c.slow = c.P[0][C_SLOW] + c.P[1][C_SLOW]; c.redirect = c.P[0][C_REDIR] + c.P[1][C_REDIR];
    for (int d = 0; d < ND_; ++d) c.debuff[d] = c.P[0][C_DEBUFF + d] + c.P[1][C_DEBUFF + d];
}

double support_on(int tgt, const SideCtx& c, double T, double heal_red) {
    const Stats& ts = c.m[tgt]->st;
    double total = 0.0;
    for (int k = 0; k < 2; ++k) {
        const Stats& ms = c.m[k]->st; const double* P = c.P[k];
        int t0 = (k == tgt) ? 0 : 1;
        double heal = 0.0, shield = 0.0;
        for (int tt = t0; tt < 3; ++tt) {
            double h = P[C_HEALFLAT + tt], sh = P[C_SHFLAT + tt];
            for (int s = 0; s < NSCAL; ++s) { h += P[C_HEALCOEF + tt * NSCAL + s] * ms.S[s]; sh += P[C_SHCOEF + tt * NSCAL + s] * ms.S[s]; }
            h += P[C_HOT + tt] / 100.0 * ts.hp;
            heal += h; shield += sh;
        }
        heal *= (1.0 + ms.heal_pct / 100.0) * (1.0 + ts.heal_recv / 100.0) * (1.0 - heal_red / 100.0) * std::max(0.0, T - GCD) / T;
        shield *= (1.0 + ms.shield_pct / 100.0);
        total += heal + shield;
    }
    return total;
}

double damage_on(const SideCtx& att, const SideCtx& tgtc, int tgt, double T, int carry) {
    const Stats& ts = tgtc.m[tgt]->st; const double* tb = tgtc.buff[tgt]; const double* deb = att.debuff;
    double armor_t = ts.armor * (1.0 + (tb[B_ARMOR_UP] - deb[D_ARMOR_DOWN]) / 100.0);
    double mr_t = ts.mr * (1.0 + (tb[B_MR_UP] - deb[D_MR_DOWN]) / 100.0);
    double def_t = ts.def + tb[B_DEF_UP] - tb[B_DEF_DOWN] - deb[D_DEF_DOWN];
    double dr_t = std::min(75.0, ts.dr + tb[B_DR_UP] - deb[D_DR_DOWN]);
    double taken_t = 1.0 + deb[D_TAKEN] / 100.0;
    double evade_t = tb[B_EVA_UP] / 100.0;
    double total = 0.0;
    static const double zeros[ND_] = {0};
    for (int k = 0; k < 2; ++k) {
        const Stats& ms = att.m[k]->st; const double* P = att.P[k]; const double* buff = att.buff[k];
        const double* dme = (k == carry) ? tgtc.debuff : zeros;
        double atk_mult = 1.0 + (buff[B_ATK_UP] - buff[B_ATK_DOWN] - dme[D_ATK_DOWN]) / 100.0;
        double mag_mult = 1.0 + (buff[B_MAG_UP] - buff[B_MAG_DOWN] - dme[D_MAG_DOWN]) / 100.0;
        double Se[NSCAL]; for (int s = 0; s < NSCAL; ++s) Se[s] = ms.S[s];
        Se[S_ATK] *= atk_mult; Se[S_MAG] *= mag_mult;
        double amp = 1.0 + (ms.dmgpct + buff[B_DMG_UP] - buff[B_DMG_DOWN] - dme[D_DMG_DOWN]) / 100.0;
        double crit = std::min(100.0, ms.crit + buff[B_CRIT_UP] - dme[D_CRIT_DOWN]);
        double cdmg = ms.crit_dmg + buff[B_CRITDMG_UP] - dme[D_CRITDMG_DOWN];
        double ecrit = 1.0 + crit / 100.0 * (cdmg - 100.0) / 100.0;
        double act = 1.0, hit = HIT;
        if (k == carry) {
            act = std::min(1.0, std::max(0.1, 1.0 - tgtc.cc / T - tgtc.slow / (T * (GCD + 0.3)) - tgtc.disarm / T * 0.5));
            hit = HIT * (1.0 - std::min(1.0, tgtc.blind / T) * (1.0 - 0.25 / HIT));
        }
        hit *= (1.0 - evade_t);
        double taken = taken_t * (1.0 + ms.innate_taken / 100.0);
        double direct[2], dots[2], dsum[2];
        for (int d = 0; d < 2; ++d) {
            double di = 0, dt = 0, ds = 0;
            for (int s = 0; s < NSCAL; ++s) { di += P[C_DMG + d * NSCAL + s] * Se[s]; dt += P[C_DOT + d * NSCAL + s] * Se[s]; ds += P[C_DMG + d * NSCAL + s]; }
            direct[d] = di * amp * ecrit * hit * act; dots[d] = dt * amp * hit * act; dsum[d] = ds;
        }
        double hits0 = P[C_HITS + 0] * hit * act;
        double pen0 = dsum[0] > 0 ? P[C_PEN + 0] / std::max(dsum[0], EPS) : 0.0;
        double pen1 = dsum[1] > 0 ? P[C_PEN + 1] / std::max(dsum[1], EPS) : 0.0;
        double apen = std::min(70.0, ms.apen + pen0), mpen = std::min(70.0, ms.mpen + pen1);
        double flat = 0.5 * def_t * hits0;
        double phys = std::max(0.1 * direct[0], direct[0] - flat) * mitig(armor_t * (1.0 - apen / 100.0))
                      + dots[0] * mitig(armor_t) + P[C_POISON] * ts.hp * mitig(armor_t) * hit * act;
        double magd = direct[1] * mitig(mr_t * (1.0 - mpen / 100.0)) + dots[1] * mitig(mr_t);
        total += (phys + magd) * (1.0 - dr_t / 100.0) * taken;
    }
    return total;
}

struct Detail { double ttfk[2], dmg[2], ehp[2], prot[2]; int focus; };

void evaluate_bucket(const Tables& t, const Member* A, const Member* B, int ti, double& tX, double& tY, Detail* det = nullptr) {
    double T = t.T[ti];
    SideCtx cx, cy; side_context(t, A, ti, cx); side_context(t, B, ti, cy);
    double out[2];
    for (int side = 0; side < 2; ++side) {
        const SideCtx& att = side == 0 ? cx : cy; const SideCtx& tg = side == 0 ? cy : cx;
        double raw[2];
        for (int k = 0; k < 2; ++k) { raw[k] = 0; for (int d = 0; d < 2; ++d) for (int s = 0; s < NSCAL; ++s) raw[k] += (att.P[k][C_DMG + d * NSCAL + s] + att.P[k][C_DOT + d * NSCAL + s]) * att.m[k]->st.S[s]; }
        int carry = raw[1] > raw[0] ? 1 : 0;
        double best = 1e300;
        for (int tgt = 0; tgt < 2; ++tgt) {
            double dmg = damage_on(att, tg, tgt, T, carry);
            const double* prot = tg.P[1 - tgt];
            double u = std::min(1.0, prot[C_TAUNT] / T) + 0.5 * std::min(1.0, prot[C_CONF] / T) + prot[C_REDIR];
            u = std::min(REDIRECT_CAP, u);
            dmg *= (1.0 - u);
            double ehp = tg.m[tgt]->st.hp + support_on(tgt, tg, T, att.debuff[D_HEALRED]);
            double ttfk = T * ehp / std::max(dmg, EPS);
            if (det) { det[side].ttfk[tgt] = ttfk; det[side].dmg[tgt] = dmg; det[side].ehp[tgt] = ehp; det[side].prot[tgt] = u; }
            best = std::min(best, ttfk);
        }
        if (det) det[side].focus = det[side].ttfk[1] < det[side].ttfk[0] ? 1 : 0;
        out[side] = best;
    }
    tX = out[0]; tY = out[1];
}

struct Res { double margin, margin_d, tX, tY, kX, kY; int ti; };

Res evaluate(const Tables& t, const Member* A, const Member* B) {
    int best_ti = 0; double best_gap = 1e300, btX = 0, btY = 0;
    for (int ti = 0; ti < t.nT; ++ti) {
        double tX, tY; evaluate_bucket(t, A, B, ti, tX, tY);
        double fight = std::min(tX, tY);
        double gap = std::fabs(std::log(std::max(fight, 1.0)) - std::log(t.T[ti]));
        if (gap < best_gap) { best_gap = gap; best_ti = ti; btX = tX; btY = tY; }
    }
    Res r; r.ti = best_ti; r.tX = btX; r.tY = btY; r.margin = btY - btX;
    r.kX = GCD * std::ceil(btX / GCD) - GCD; r.kY = GCD * std::ceil(btY / GCD) - GCD; r.margin_d = r.kY - r.kX;
    return r;
}

inline double objective(const Res& r) { return r.margin / std::max(std::min(r.tX, r.tY), 2.0); }

// ---- allocation grids -------------------------------------------------------
std::vector<Alloc> coarse_grid(int step) {
    std::vector<Alloc> g;
    for (int mp = 0; mp <= STAT_POINTS; mp += step)
        for (int off = 0; off <= STAT_POINTS; off += step)
            for (int de = 0; de <= STAT_POINTS; de += step) {
                int hp = STAT_POINTS - mp - off - de;
                if (hp >= 0) g.push_back(Alloc{hp, mp, off, de});
            }
    std::sort(g.begin(), g.end(), [](const Alloc& a, const Alloc& b) { return std::tie(a.hp, a.mp, a.off, a.def) < std::tie(b.hp, b.mp, b.off, b.def); });
    return g;
}
std::vector<Alloc> local_grid(const Alloc& c, int radius) {
    std::vector<Alloc> g;
    auto lo = [&](int v) { return std::max(0, v - radius); }; auto hi = [&](int v) { return std::min(STAT_POINTS, v + radius); };
    for (int mp = lo(c.mp); mp <= hi(c.mp); ++mp)
        for (int off = lo(c.off); off <= hi(c.off); ++off)
            for (int de = lo(c.def); de <= hi(c.def); ++de) {
                int hp = STAT_POINTS - mp - off - de;
                if (hp >= 0) g.push_back(Alloc{hp, mp, off, de});
            }
    std::sort(g.begin(), g.end(), [](const Alloc& a, const Alloc& b) { return std::tie(a.hp, a.mp, a.off, a.def) < std::tie(b.hp, b.mp, b.off, b.def); });
    return g;
}

// ---- pattern search ---------------------------------------------------------------------
// Steepest-descent moves of `s` points from one stat to another (12 neighbours), s = 4, 2, 1.
bool g_exhaustive = false;
constexpr int COARSE_FAST = 6;
constexpr int FAST_STARTS = 3;      // pattern search from the best FAST_STARTS coarse points (multimodal landscape)

// keep the K best (value, alloc) pairs seen in a coarse sweep (minimizing)
struct TopK {
    double v[FAST_STARTS]; Alloc a[FAST_STARTS]; int n = 0;
    void push(double val, const Alloc& al) {
        if (n < FAST_STARTS) { v[n] = val; a[n] = al; n++; }
        else { int w = 0; for (int i = 1; i < n; ++i) if (v[i] > v[w]) w = i; if (val < v[w]) { v[w] = val; a[w] = al; } }
    }
};

template <class F>
Alloc pattern_search(Alloc a, F f, double& best) {
    best = f(a);
    static const int steps[3] = {4, 2, 1};
    for (int si = 0; si < 3; ++si) {
        int s = steps[si];
        for (;;) {
            Alloc bestc = a; double bestv = best;
            int* pa = &a.hp;
            for (int i = 0; i < 4; ++i) {
                if (pa[i] < s) continue;
                for (int j = 0; j < 4; ++j) {
                    if (j == i) continue;
                    Alloc c = a; int* pc = &c.hp; pc[i] -= s; pc[j] += s;
                    double v = f(c);
                    if (v < bestv - 1e-12) { bestv = v; bestc = c; }
                }
            }
            if (bestv < best - 1e-12) { best = bestv; a = bestc; } else break;
        }
    }
    return a;
}

// ---- play-to-win best response -------------------------------------------------
// subs: the two subclasses of team X; Y: the fixed enemy; cur: starting builds (updated in place).
double best_response(const Tables& t, Member* cur, const Member* Y, int rounds, int step, int refine, const int* w_fixed) {
    static thread_local std::vector<Alloc> coarse3 = coarse_grid(3);
    static thread_local std::vector<Alloc> coarse6 = coarse_grid(COARSE_FAST);
    const std::vector<Alloc>& coarse = g_exhaustive ? ((step == 3) ? coarse3 : coarse_grid(step)) : coarse6;
    double best_score = -1e300;
    for (int r = 0; r < rounds; ++r) {
        bool improved = false;
        for (int k = 0; k < 2; ++k) {
            Member team[2] = {cur[0], cur[1]};
            double ref_best = -1e300; Alloc ref_pt; int ref_w = cur[k].wi;
            int w0 = w_fixed ? w_fixed[k] : 0, w1 = w_fixed ? w_fixed[k] : t.nW - 1;
            for (int wi = w0; wi <= w1; ++wi) {
                double loc_best = -1e300; Alloc loc_pt;
                for (const Alloc& a : coarse) {
                    team[k] = make_member(t, cur[k].sub, a, wi);
                    double sc = objective(evaluate(t, team, Y));
                    if (sc > loc_best) { loc_best = sc; loc_pt = a; }
                }
                Alloc pt; double val;
                if (g_exhaustive) {
                    std::vector<Alloc> loc = local_grid(loc_pt, refine);
                    val = -1e300; pt = loc_pt;
                    for (const Alloc& a : loc) {
                        team[k] = make_member(t, cur[k].sub, a, wi);
                        double sc = objective(evaluate(t, team, Y));
                        if (sc > val) { val = sc; pt = a; }
                    }
                } else {
                    auto f = [&](const Alloc& a) { team[k] = make_member(t, cur[k].sub, a, wi); return -objective(evaluate(t, team, Y)); };
                    TopK top;
                    for (const Alloc& a : coarse) top.push(f(a), a);
                    val = -1e300; pt = loc_pt;
                    for (int i = 0; i < top.n; ++i) { double neg; Alloc q = pattern_search(top.a[i], f, neg); if (-neg > val) { val = -neg; pt = q; } }
                }
                if (val > ref_best) { ref_best = val; ref_pt = pt; ref_w = wi; }
            }
            if (ref_best > best_score + 1e-9) { best_score = ref_best; improved = true; cur[k] = make_member(t, cur[k].sub, ref_pt, ref_w); }
        }
        if (!improved) break;
    }
    return best_score;
}

// ---- balancing --------------------------------------------------------------------
int pick(const std::vector<double>& margin, const std::vector<double>& dist, double tol) {
    int best = -1; double bv = 1e300; bool any = false;
    for (size_t i = 0; i < margin.size(); ++i) if (std::fabs(margin[i]) <= tol) { any = true; break; }
    for (size_t i = 0; i < margin.size(); ++i) {
        double v = any ? (std::fabs(margin[i]) <= tol ? dist[i] + 1e-3 * std::fabs(margin[i]) : 1e300) : std::fabs(margin[i]) + 1e-3 * dist[i];
        if (v < bv) { bv = v; best = (int)i; }
    }
    return best;
}

double handicap(const Tables& t, Member* cur /*4*/, const Alloc* refs /*4*/, double tol, int passes, int step, int refine) {
    static thread_local std::vector<Alloc> coarse3 = coarse_grid(3);
    double m = evaluate(t, cur, cur + 2).margin;
    for (int p = 0; p < passes; ++p) {
        if (std::fabs(m) <= tol) break;
        int order[4]; if (m > 0) { order[0] = 0; order[1] = 1; order[2] = 2; order[3] = 3; } else { order[0] = 2; order[1] = 3; order[2] = 0; order[3] = 1; }
        for (int oi = 0; oi < 4; ++oi) {
            int k = order[oi];
            double other_dist = 0; for (int j = 0; j < 4; ++j) if (j != k) other_dist += dist(cur[j].a, refs[j]);
            Member team[4] = {cur[0], cur[1], cur[2], cur[3]};
            // the handicap always uses the exhaustive step-3 grid + local refinement: it is ~10% of the
            // per-matchup cost and the nearest-in-band solution is not reliably found by pattern search
            for (int pass = 0; pass < 2; ++pass) {
                const std::vector<Alloc>& grid = pass == 0 ? coarse3 : local_grid(cur[k].a, refine);
                std::vector<double> mg(grid.size()), ds(grid.size());
                for (size_t i = 0; i < grid.size(); ++i) {
                    team[k] = make_member(t, cur[k].sub, grid[i], cur[k].wi);
                    mg[i] = evaluate(t, team, team + 2).margin;
                    ds[i] = dist(grid[i], refs[k]) + other_dist;
                }
                int i = pick(mg, ds, tol);
                cur[k] = make_member(t, cur[k].sub, grid[i], cur[k].wi);
                m = mg[i];
            }
            if (std::fabs(m) <= tol) break;
        }
    }
    return m;
}

struct BalanceOut { Member A[2], B[2]; Alloc refA[2], refB[2]; double margin0, margin; int movedA, movedB; };

BalanceOut balance_matchup(const Tables& t, const Member* A0, const Member* B0, double tol, int passes, int br_rounds) {
    BalanceOut o;
    Member A[2] = {A0[0], A0[1]}, B[2] = {B0[0], B0[1]};
    int wA[2] = {A[0].wi, A[1].wi}, wB[2] = {B[0].wi, B[1].wi};
    for (int r = 0; r < br_rounds; ++r) { best_response(t, A, B, 2, 3, 3, wA); best_response(t, B, A, 2, 3, 3, wB); }
    o.refA[0] = A[0].a; o.refA[1] = A[1].a; o.refB[0] = B[0].a; o.refB[1] = B[1].a;
    o.margin0 = evaluate(t, A, B).margin;
    Member cur[4] = {A[0], A[1], B[0], B[1]}; Alloc refs[4] = {A[0].a, A[1].a, B[0].a, B[1].a};
    o.margin = handicap(t, cur, refs, tol, passes, 3, 3);
    o.A[0] = cur[0]; o.A[1] = cur[1]; o.B[0] = cur[2]; o.B[1] = cur[3];
    o.movedA = dist(cur[0].a, refs[0]) + dist(cur[1].a, refs[1]); o.movedB = dist(cur[2].a, refs[2]) + dist(cur[3].a, refs[3]);
    return o;
}

// ---- zero-sum game (HiGHS) --------------------------------------------------------
inline double win_prob(double margin, double tau) { double z = std::max(-60.0, std::min(60.0, margin / tau)); return 1.0 / (1.0 + std::exp(-z)); }

struct GameOut { double value; std::vector<double> x, y; };

GameOut solve_fp(const std::vector<std::vector<double>>& P) {   // fictitious play (fallback / no-HiGHS build)
    int m = (int)P.size(), n = (int)P[0].size();
    std::vector<double> cx(m, 0), cy(n, 0), ux(m, 0), uy(n, 0);
    int i = 0, j = 0;
    for (int it = 0; it < 4000; ++it) {
        for (int a = 0; a < m; ++a) ux[a] += P[a][j];
        for (int b = 0; b < n; ++b) uy[b] += P[i][b];
        cx[i] += 1; cy[j] += 1;
        i = (int)(std::max_element(ux.begin(), ux.end()) - ux.begin());
        j = (int)(std::min_element(uy.begin(), uy.end()) - uy.begin());
    }
    GameOut g; g.x.resize(m); g.y.resize(n); double v = 0;
    for (int a = 0; a < m; ++a) g.x[a] = cx[a] / 4000.0;
    for (int b = 0; b < n; ++b) g.y[b] = cy[b] / 4000.0;
    for (int a = 0; a < m; ++a) for (int b = 0; b < n; ++b) v += g.x[a] * P[a][b] * g.y[b];
    g.value = v; return g;
}

#ifndef KBAL_NO_HIGHS
// max v s.t. sum_i P[i][j] x_i - v >= 0 (all j), sum_i x_i = 1, x >= 0
GameOut solve_zero_sum(const std::vector<std::vector<double>>& P) {
    int m = (int)P.size(), n = (int)P[0].size();
    auto solve = [&](bool row_player) {
        int nv = row_player ? m : n, nc = row_player ? n : m;
        HighsLp lp; lp.num_col_ = nv + 1; lp.num_row_ = nc + 1;
        lp.col_cost_.assign(nv + 1, 0.0); lp.col_cost_[nv] = row_player ? -1.0 : 1.0;
        lp.col_lower_.assign(nv + 1, 0.0); lp.col_upper_.assign(nv + 1, kHighsInf);
        lp.col_lower_[nv] = -kHighsInf;
        lp.row_lower_.assign(nc + 1, row_player ? 0.0 : -kHighsInf); lp.row_upper_.assign(nc + 1, row_player ? kHighsInf : 0.0);
        lp.row_lower_[nc] = 1.0; lp.row_upper_[nc] = 1.0;
        lp.a_matrix_.format_ = MatrixFormat::kColwise;
        lp.a_matrix_.num_col_ = nv + 1; lp.a_matrix_.num_row_ = nc + 1;
        lp.a_matrix_.start_.push_back(0);
        for (int v = 0; v < nv; ++v) {
            for (int c = 0; c < nc; ++c) { lp.a_matrix_.index_.push_back(c); lp.a_matrix_.value_.push_back(row_player ? P[v][c] : P[c][v]); }
            lp.a_matrix_.index_.push_back(nc); lp.a_matrix_.value_.push_back(1.0);
            lp.a_matrix_.start_.push_back((HighsInt)lp.a_matrix_.index_.size());
        }
        for (int c = 0; c < nc; ++c) { lp.a_matrix_.index_.push_back(c); lp.a_matrix_.value_.push_back(-1.0); }
        lp.a_matrix_.start_.push_back((HighsInt)lp.a_matrix_.index_.size());
        Highs h; h.setOptionValue("output_flag", false); h.setOptionValue("threads", 1);
        std::vector<double> sol;
        if (h.passModel(lp) == HighsStatus::kOk && h.run() != HighsStatus::kError && h.getModelStatus() == HighsModelStatus::kOptimal)
            sol = h.getSolution().col_value;
        return sol;
    };
    std::vector<double> xs = solve(true), ys = solve(false);
    if (xs.size() != (size_t)m + 1 || ys.size() != (size_t)n + 1) return solve_fp(P);
    GameOut g; g.x.assign(xs.begin(), xs.begin() + m); g.value = xs[m]; g.y.assign(ys.begin(), ys.begin() + n);
    if (!(g.value == g.value)) return solve_fp(P);
    return g;
}
#else
GameOut solve_zero_sum(const std::vector<std::vector<double>>& P) { return solve_fp(P); }
#endif

// ---- per-matchup pipeline ----------------------------------------------------------
struct Build { Alloc a[2]; int w[2]; };
inline bool same(const Build& p, const Build& q) { return p.a[0] == q.a[0] && p.a[1] == q.a[1] && p.w[0] == q.w[0] && p.w[1] == q.w[1]; }
void add_build(std::vector<Build>& pool, const Member* m) { Build b{{m[0].a, m[1].a}, {m[0].wi, m[1].wi}}; for (auto& p : pool) if (same(p, b)) return; pool.push_back(b); }
void team_from(const Tables& t, const int* subs, const Build& b, Member* out) { out[0] = make_member(t, subs[0], b.a[0], b.w[0]); out[1] = make_member(t, subs[1], b.a[1], b.w[1]); }

struct MatchRow {
    int A[2], B[2]; double p_free; Build bestA, bestB; BalanceOut bal; Res locked;
};

// ---- stage 1: candidate pool per composition (mirrors run_tournament.py) -------------------
const char* REF_OPP[6][2] = {{"guardian", "lifewarden"}, {"berserker", "ranger"}, {"elementalist", "occultist"},
                             {"shadowblade", "lightbringer"}, {"weaponmaster", "cantor"}, {"gunslinger", "alchemist"}};

struct Refs { int subs[6][2]; Member m[6][2]; int n = 0; };

Refs build_refs(const Tables& t) {
    Refs r;
    for (int i = 0; i < 6; ++i) {
        auto a = t.index.find(REF_OPP[i][0]), b = t.index.find(REF_OPP[i][1]);
        if (a == t.index.end() || b == t.index.end()) continue;
        r.subs[r.n][0] = a->second; r.subs[r.n][1] = b->second;
        r.m[r.n][0] = default_build(t, a->second); r.m[r.n][1] = default_build(t, b->second); r.n++;
    }
    // one self-play pass: each reference answers the first other reference (updated in order)
    for (int i = 0; i < r.n; ++i) {
        int other = (i == 0) ? 1 : 0;
        if (r.n < 2) break;
        best_response(t, r.m[i], r.m[other], 2, 3, 3, nullptr);
    }
    return r;
}

void generic_pool(const Tables& t, const int* subs, std::vector<Build>& pool) {
    Member m[2];
    m[0] = default_build(t, subs[0]); m[1] = default_build(t, subs[1]); add_build(pool, m);
    const Alloc gen[4] = {Alloc{57, 0, 0, 0}, Alloc{0, 0, 57, 0}, Alloc{19, 19, 19, 0}, Alloc{29, 0, 0, 28}};
    for (const Alloc& g : gen) { m[0] = make_member(t, subs[0], g, 1); m[1] = make_member(t, subs[1], g, 1); add_build(pool, m); }
}

std::vector<Build> stage1_pool(const Tables& t, const int* subs, const Refs& refs) {
    std::vector<Build> pool;
    generic_pool(t, subs, pool);
    for (int i = 0; i < refs.n; ++i) {
        Member cur[2] = {default_build(t, subs[0]), default_build(t, subs[1])};
        best_response(t, cur, refs.m[i], 3, 3, 3, nullptr);
        add_build(pool, cur);
    }
    return pool;
}

GameOut pool_game(const Tables& t, const int* A, const int* B, const std::vector<Build>& poolA, const std::vector<Build>& poolB, double tau) {
    std::vector<std::vector<double>> P(poolA.size(), std::vector<double>(poolB.size()));
    for (size_t i = 0; i < poolA.size(); ++i) for (size_t j = 0; j < poolB.size(); ++j) {
        Member a[2], b[2]; team_from(t, A, poolA[i], a); team_from(t, B, poolB[j], b);
        P[i][j] = win_prob(evaluate(t, a, b).margin_d, tau);
    }
    return solve_zero_sum(P);
}

// ---- stage 2: one matchup ------------------------------------------------------------------
MatchRow solve_matchup(const Tables& t, const int* A, const int* B, const std::vector<Build>& poolA0, const std::vector<Build>& poolB0,
                       double tol, double tau, int br_iters) {
    MatchRow row; row.A[0] = A[0]; row.A[1] = A[1]; row.B[0] = B[0]; row.B[1] = B[1];
    std::vector<Build> poolA = poolA0, poolB = poolB0;
    GameOut g = pool_game(t, A, B, poolA, poolB, tau);
    auto top = [&](const GameOut& g, std::vector<Build>& pa, std::vector<Build>& pb, Member* a, Member* b) {
        int bi = (int)(std::max_element(g.x.begin(), g.x.end()) - g.x.begin()), bj = (int)(std::max_element(g.y.begin(), g.y.end()) - g.y.begin());
        team_from(t, A, pa[bi], a); team_from(t, B, pb[bj], b);
        row.bestA = pa[bi]; row.bestB = pb[bj];
    };
    Member a[2], b[2]; top(g, poolA, poolB, a, b);
    // best responses against the exact opponent, starting from the pool equilibrium
    for (int r = 0; r < br_iters; ++r) {
        best_response(t, a, b, 2, 3, 3, nullptr); add_build(poolA, a);
        best_response(t, b, a, 2, 3, 3, nullptr); add_build(poolB, b);
    }
    if (br_iters > 0) { g = pool_game(t, A, B, poolA, poolB, tau); top(g, poolA, poolB, a, b); }
    row.p_free = std::min(1.0, std::max(0.0, g.value));
    row.bal = balance_matchup(t, a, b, tol, 3, 1);
    row.locked = evaluate(t, row.bal.A, row.bal.B);
    return row;
}

std::string alloc_str(const Tables& t, int sub, const Alloc& a, int wi) {
    char buf[96]; snprintf(buf, sizeof buf, "hp%d/mp%d/%s%d/def%d/w%g", a.hp, a.mp, t.mainStat[sub] == 0 ? "atk" : "mag", a.off, a.def, t.W[wi]);
    return buf;
}
std::string fmt_t(double v) { char b[32]; if (v < 99.0) snprintf(b, sizeof b, "%.1f", v); else snprintf(b, sizeof b, "none"); return b; }

}  // namespace

int main(int argc, char** argv) {
    if (argc < 2) { std::cerr << "usage: kbal tables.bin [--threads N] [--tol S] [--tau S] [--no-repeats] [--limit N] [--out DIR] [--br-iters N] [--exhaustive]\n"
                                 "       kbal tables.bin --matchup a b c d      (verbose single matchup)\n"
                                 "       kbal tables.bin --eval a b c d hp/mp/off/def/w x4   (evaluate given builds)\n"; return 1; }
    Tables t;
    if (!load_tables(argv[1], t)) return 1;
    int threads = (int)std::thread::hardware_concurrency(); double tol = 0.25, tau = 2.0; bool no_repeats = false; int limit = 0, br_iters = 2;
    std::string out = "out"; std::vector<std::string> pos;
    std::string mode;
    for (int i = 2; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--threads") threads = atoi(argv[++i]); else if (a == "--tol") tol = atof(argv[++i]); else if (a == "--tau") tau = atof(argv[++i]);
        else if (a == "--no-repeats") no_repeats = true; else if (a == "--limit") limit = atoi(argv[++i]); else if (a == "--out") out = argv[++i];
        else if (a == "--br-iters") br_iters = atoi(argv[++i]); else if (a == "--exhaustive") g_exhaustive = true; else if (a == "--matchup" || a == "--eval" || a == "--gametest") mode = a; else pos.push_back(a);
    }
    auto sub_id = [&](const std::string& s) { auto it = t.index.find(s); if (it == t.index.end()) { std::cerr << "unknown subclass " << s << "\n"; exit(1); } return it->second; };
    auto parse_alloc = [&](const std::string& s, Alloc& a, int& wi) {
        int hp, mp, off, de; double w; char st[8];
        if (sscanf(s.c_str(), "hp%d/mp%d/%3[a-z]%d/def%d/w%lf", &hp, &mp, st, &off, &de, &w) != 6) { std::cerr << "bad alloc " << s << "\n"; exit(1); }
        a = Alloc{hp, mp, off, de}; wi = 1; for (int i = 0; i < t.nW; ++i) if (std::fabs(t.W[i] - w) < 1e-9) wi = i;
    };
    if (mode == "--gametest") {
        std::vector<std::vector<double>> P = {{1.0, 0.0, 0.7}, {0.0, 1.0, 0.2}, {0.4, 0.6, 0.5}};
        GameOut g = solve_zero_sum(P), f = solve_fp(P);
        printf("HiGHS: value %.4f x %.3f %.3f %.3f y %.3f %.3f %.3f\n", g.value, g.x[0], g.x[1], g.x[2], g.y[0], g.y[1], g.y[2]);
        printf("FP   : value %.4f x %.3f %.3f %.3f y %.3f %.3f %.3f\n", f.value, f.x[0], f.x[1], f.x[2], f.y[0], f.y[1], f.y[2]);
        return 0;
    }
    if (mode == "--eval") {
        if (pos.size() < 8) { std::cerr << "need 4 subclasses and 4 allocations\n"; return 1; }
        Member A[2], B[2];
        for (int k = 0; k < 4; ++k) { Alloc a; int wi; parse_alloc(pos[4 + k], a, wi); Member m = make_member(t, sub_id(pos[k]), a, wi); (k < 2 ? A[k] : B[k - 2]) = m; }
        Res r = evaluate(t, A, B);
        printf("margin %.6f margin_d %.1f ttfk_X %.6f ttfk_Y %.6f ti %d T %.0f\n", r.margin, r.margin_d, r.tX, r.tY, r.ti, t.T[r.ti]);
        Detail det[2]; double tX, tY; evaluate_bucket(t, A, B, r.ti, tX, tY, det);
        for (int s = 0; s < 2; ++s) printf("  side %c: ttfk %.4f %.4f dmg %.4f %.4f ehp %.4f %.4f\n", 'A' + s, det[s].ttfk[0], det[s].ttfk[1], det[s].dmg[0], det[s].dmg[1], det[s].ehp[0], det[s].ehp[1]);
        return 0;
    }
    if (mode == "--matchup") {
        if (pos.size() < 4) { std::cerr << "need 4 subclasses\n"; return 1; }
        int A[2] = {sub_id(pos[0]), sub_id(pos[1])}, B[2] = {sub_id(pos[2]), sub_id(pos[3])};
        auto t0 = std::chrono::steady_clock::now();
        Refs refs = build_refs(t);
        std::vector<Build> pa = stage1_pool(t, A, refs), pb = stage1_pool(t, B, refs);
        MatchRow r = solve_matchup(t, A, B, pa, pb, tol, tau, br_iters);
        double secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
        printf("play to win: P(%s+%s wins) = %.3f\n", pos[0].c_str(), pos[1].c_str(), r.p_free);
        printf("  best A: %s | %s\n  best B: %s | %s\n", alloc_str(t, A[0], r.bestA.a[0], r.bestA.w[0]).c_str(), alloc_str(t, A[1], r.bestA.a[1], r.bestA.w[1]).c_str(),
               alloc_str(t, B[0], r.bestB.a[0], r.bestB.w[0]).c_str(), alloc_str(t, B[1], r.bestB.a[1], r.bestB.w[1]).c_str());
        printf("balanced: play-to-win margin %+.2f s -> locked margin %+.2f s (P = %.3f), moved A %d, B %d, horizon %.0f s, ttfk %.1f / %.1f\n",
               r.bal.margin0, r.bal.margin, win_prob(r.bal.margin, tau), r.bal.movedA, r.bal.movedB, t.T[r.locked.ti], r.locked.tX, r.locked.tY);
        for (int k = 0; k < 2; ++k) printf("  LOCK %-13s %s   (ref %s)\n", t.ids[A[k]].c_str(), alloc_str(t, A[k], r.bal.A[k].a, r.bal.A[k].wi).c_str(), alloc_str(t, A[k], r.bal.refA[k], r.bal.A[k].wi).c_str());
        for (int k = 0; k < 2; ++k) printf("  LOCK %-13s %s   (ref %s)\n", t.ids[B[k]].c_str(), alloc_str(t, B[k], r.bal.B[k].a, r.bal.B[k].wi).c_str(), alloc_str(t, B[k], r.bal.refB[k], r.bal.B[k].wi).c_str());
        const Member* all[4] = {&r.bal.A[0], &r.bal.A[1], &r.bal.B[0], &r.bal.B[1]};
        for (int k = 0; k < 4; ++k) {
            const Member& m = *all[k]; const double* c = t.cast(m.sub, r.locked.ti, m.wi, m.a.mp);
            printf("  %-13s casts:", t.ids[m.sub].c_str());
            for (size_t s = 0; s < t.skills[m.sub].size(); ++s) if (c[s] > 0) printf(" %s x%d,", t.skills[m.sub][s].c_str(), (int)c[s]);
            printf("\n");
        }
        printf("solved in %.2f s\n", secs);
        return 0;
    }
    // full table
    std::vector<std::pair<int, int>> comps;
    for (int i = 0; i < t.nSub; ++i) for (int j = i; j < t.nSub; ++j) if (!(no_repeats && i == j)) comps.push_back({i, j});
    if (limit > 0 && (int)comps.size() > limit) comps.resize(limit);
    std::vector<std::pair<int, int>> pairs;
    for (int i = 0; i < (int)comps.size(); ++i) for (int j = i; j < (int)comps.size(); ++j) pairs.push_back({i, j});
    printf("%zu compositions, %zu matchups, %d threads\n", comps.size(), pairs.size(), threads); fflush(stdout);
    auto t0 = std::chrono::steady_clock::now();
    Refs refs = build_refs(t);
    std::vector<std::vector<Build>> pools(comps.size());
    {
        std::atomic<size_t> nxt{0};
        auto w1 = [&]() { for (;;) { size_t i = nxt.fetch_add(1); if (i >= comps.size()) break; int S[2] = {comps[i].first, comps[i].second}; pools[i] = stage1_pool(t, S, refs); } };
        std::vector<std::thread> p1; for (int k = 0; k < threads; ++k) p1.emplace_back(w1); for (auto& th : p1) th.join();
    }
    printf("stage 1 (candidate pools) done in %.1f s\n", std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count()); fflush(stdout);
    std::vector<MatchRow> rows(pairs.size());
    std::atomic<size_t> next{0}, done{0};
    auto worker = [&]() {
        for (;;) {
            size_t i = next.fetch_add(1);
            if (i >= pairs.size()) break;
            int A[2] = {comps[pairs[i].first].first, comps[pairs[i].first].second};
            int B[2] = {comps[pairs[i].second].first, comps[pairs[i].second].second};
            rows[i] = solve_matchup(t, A, B, pools[pairs[i].first], pools[pairs[i].second], tol, tau, br_iters);
            done.fetch_add(1);
        }
    };
    std::vector<std::thread> pool;
    for (int k = 0; k < threads; ++k) pool.emplace_back(worker);
    while (done.load() < pairs.size()) {
        std::this_thread::sleep_for(std::chrono::seconds(5));
        double el = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
        size_t d = done.load();
        printf("  %zu/%zu matchups, %.0f s elapsed, ETA %.0f s\n", d, pairs.size(), el, d ? el * (pairs.size() - d) / d : 0.0); fflush(stdout);
    }
    for (auto& th : pool) th.join();
    double secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    // outputs
    std::string bpath = out + "/balanced_cpp.csv";
    FILE* f = fopen(bpath.c_str(), "w");
    if (!f) { std::cerr << "cannot write " << bpath << "\n"; return 1; }
    fprintf(f, "class1,class2,class3,class4,lock_class1,lock_class2,lock_class3,lock_class4,p_team12_wins_locked,margin_s_locked,ttfk_team12,ttfk_team34,horizon_s,favoured_before,points_moved,points_moved_12,points_moved_34,p_team12_wins_free,best_class1,best_class2,best_class3,best_class4\n");
    std::vector<double> comp_score(comps.size(), 0.0); std::vector<int> comp_n(comps.size(), 0);
    for (size_t i = 0; i < rows.size(); ++i) {
        const MatchRow& r = rows[i];
        fprintf(f, "%s,%s,%s,%s,%s,%s,%s,%s,%.3f,%+.2f,%s,%s,%.0f,%s,%d,%d,%d,%.3f,%s,%s,%s,%s\n",
                t.ids[r.A[0]].c_str(), t.ids[r.A[1]].c_str(), t.ids[r.B[0]].c_str(), t.ids[r.B[1]].c_str(),
                alloc_str(t, r.A[0], r.bal.A[0].a, r.bal.A[0].wi).c_str(), alloc_str(t, r.A[1], r.bal.A[1].a, r.bal.A[1].wi).c_str(),
                alloc_str(t, r.B[0], r.bal.B[0].a, r.bal.B[0].wi).c_str(), alloc_str(t, r.B[1], r.bal.B[1].a, r.bal.B[1].wi).c_str(),
                win_prob(r.bal.margin, tau), r.bal.margin, fmt_t(r.locked.tX).c_str(), fmt_t(r.locked.tY).c_str(), t.T[r.locked.ti],
                r.bal.margin0 > 0 ? "A" : (r.bal.margin0 < 0 ? "B" : "-"), r.bal.movedA + r.bal.movedB, r.bal.movedA, r.bal.movedB, r.p_free,
                alloc_str(t, r.A[0], r.bestA.a[0], r.bestA.w[0]).c_str(), alloc_str(t, r.A[1], r.bestA.a[1], r.bestA.w[1]).c_str(),
                alloc_str(t, r.B[0], r.bestB.a[0], r.bestB.w[0]).c_str(), alloc_str(t, r.B[1], r.bestB.a[1], r.bestB.w[1]).c_str());
        int ci = pairs[i].first, cj = pairs[i].second;
        comp_score[ci] += r.p_free; comp_n[ci]++;
        if (ci != cj) { comp_score[cj] += 1.0 - r.p_free; comp_n[cj]++; }
    }
    fclose(f);
    std::string cpath = out + "/compositions_cpp.csv";
    f = fopen(cpath.c_str(), "w");
    fprintf(f, "subclass_1,subclass_2,mean_win_prob_free\n");
    std::vector<int> order(comps.size()); for (size_t i = 0; i < order.size(); ++i) order[i] = (int)i;
    std::sort(order.begin(), order.end(), [&](int a, int b) { return comp_score[a] / comp_n[a] > comp_score[b] / comp_n[b]; });
    for (int i : order) fprintf(f, "%s,%s,%.3f\n", t.ids[comps[i].first].c_str(), t.ids[comps[i].second].c_str(), comp_score[i] / comp_n[i]);
    fclose(f);
    std::string spath = out + "/subclasses_cpp.csv";
    f = fopen(spath.c_str(), "w");
    fprintf(f, "subclass,base_class,mean_win_prob_free\n");
    std::vector<double> ss(t.nSub, 0.0); std::vector<int> sn(t.nSub, 0);
    for (size_t i = 0; i < comps.size(); ++i) { double v = comp_score[i] / comp_n[i]; ss[comps[i].first] += v; sn[comps[i].first]++; if (comps[i].second != comps[i].first) { ss[comps[i].second] += v; sn[comps[i].second]++; } }
    std::vector<int> so(t.nSub); for (int i = 0; i < t.nSub; ++i) so[i] = i;
    std::sort(so.begin(), so.end(), [&](int a, int b) { return ss[a] / std::max(1, sn[a]) > ss[b] / std::max(1, sn[b]); });
    for (int i : so) fprintf(f, "%s,%s,%.3f\n", t.ids[i].c_str(), t.base[i].c_str(), ss[i] / std::max(1, sn[i]));
    fclose(f);
    int within = 0; for (auto& r : rows) if (std::fabs(r.bal.margin) <= tol + 1e-9) within++;
    printf("done in %.0f s: %zu matchups, %.1f%% within tol, outputs %s, %s, %s\n", secs, rows.size(), 100.0 * within / rows.size(), bpath.c_str(), cpath.c_str(), spath.c_str());
    return 0;
}
