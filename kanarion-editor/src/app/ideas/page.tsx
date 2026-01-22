'use client';

import { useEffect, useState } from 'react';

interface Idea {
  id: string;
  title: string;
  status: 'idea' | 'draft' | 'ready' | 'integrated';
  category: string;
  priority: 'low' | 'medium' | 'high';
  inspiration?: string;
  description: string;
  details?: Record<string, any>;
  added_date: string;
}

interface IdeasData {
  _meta: {
    version: string;
    description: string;
    status_legend: Record<string, string>;
    categories: string[];
  };
  ideas: Idea[];
}

const STATUS_CONFIG: Record<string, { color: string; icon: string }> = {
  idea: { color: 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30', icon: '💡' },
  draft: { color: 'bg-amber-500/20 text-amber-400 border-amber-500/30', icon: '📝' },
  ready: { color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30', icon: '✅' },
  integrated: { color: 'bg-blue-500/20 text-blue-400 border-blue-500/30', icon: '🔗' },
};

const PRIORITY_CONFIG: Record<string, { color: string; label: string }> = {
  low: { color: 'text-zinc-500', label: 'Low' },
  medium: { color: 'text-amber-400', label: 'Med' },
  high: { color: 'text-red-400', label: 'High' },
};

const CATEGORY_CONFIG: Record<string, { icon: string; color: string }> = {
  items: { icon: '🎒', color: 'text-amber-400' },
  combat: { icon: '⚔️', color: 'text-red-400' },
  classes: { icon: '🗡️', color: 'text-violet-400' },
  progression: { icon: '📈', color: 'text-emerald-400' },
  social: { icon: '👥', color: 'text-blue-400' },
  world: { icon: '🗺️', color: 'text-green-400' },
  pvp: { icon: '🏆', color: 'text-orange-400' },
  pve: { icon: '🐉', color: 'text-purple-400' },
  economy: { icon: '💰', color: 'text-yellow-400' },
  meta: { icon: '📋', color: 'text-zinc-400' },
};

export default function IdeasPage() {
  const [data, setData] = useState<IdeasData | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [expandedIdea, setExpandedIdea] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/ideas')
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="text-zinc-400">Loading...</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-8">
        <div className="text-red-400">Failed to load ideas</div>
      </div>
    );
  }

  const filteredIdeas = data.ideas.filter(idea => {
    if (filterCategory !== 'all' && idea.category !== filterCategory) return false;
    if (filterStatus !== 'all' && idea.status !== filterStatus) return false;
    return true;
  });

  // Group by category
  const groupedIdeas: Record<string, Idea[]> = {};
  filteredIdeas.forEach(idea => {
    if (!groupedIdeas[idea.category]) {
      groupedIdeas[idea.category] = [];
    }
    groupedIdeas[idea.category].push(idea);
  });

  // Stats
  const stats = {
    total: data.ideas.length,
    byStatus: {
      idea: data.ideas.filter(i => i.status === 'idea').length,
      draft: data.ideas.filter(i => i.status === 'draft').length,
      ready: data.ideas.filter(i => i.status === 'ready').length,
      integrated: data.ideas.filter(i => i.status === 'integrated').length,
    },
    byPriority: {
      high: data.ideas.filter(i => i.priority === 'high').length,
      medium: data.ideas.filter(i => i.priority === 'medium').length,
      low: data.ideas.filter(i => i.priority === 'low').length,
    }
  };

  return (
    <div className="p-4 md:p-6 lg:p-8">
      {/* Header */}
      <div className="mb-4 md:mb-6">
        <h1 className="text-2xl md:text-3xl font-bold mb-2">Ideas to Integrate</h1>
        <p className="text-zinc-500 text-sm">
          {stats.total} ideas • {stats.byStatus.idea} idea, {stats.byStatus.draft} draft, {stats.byStatus.ready} ready, {stats.byStatus.integrated} integrated
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {Object.entries(STATUS_CONFIG).map(([status, config]) => (
          <div
            key={status}
            onClick={() => setFilterStatus(filterStatus === status ? 'all' : status)}
            className={`p-3 rounded-lg border cursor-pointer transition-all ${
              filterStatus === status ? config.color + ' ring-2 ring-offset-2 ring-offset-zinc-900' : 'bg-zinc-900 border-zinc-800 hover:border-zinc-700'
            }`}
          >
            <div className="text-2xl mb-1">{config.icon}</div>
            <div className="font-medium capitalize">{status}</div>
            <div className="text-zinc-500 text-xs">{stats.byStatus[status as keyof typeof stats.byStatus]} ideas</div>
          </div>
        ))}
      </div>

      {/* Category Filter */}
      <div className="mb-6 flex flex-wrap gap-2">
        <button
          onClick={() => setFilterCategory('all')}
          className={`px-3 py-1.5 rounded-lg text-sm ${
            filterCategory === 'all' ? 'bg-zinc-700 text-white' : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800'
          }`}
        >
          All Categories
        </button>
        {data._meta.categories.map(cat => {
          const config = CATEGORY_CONFIG[cat] || { icon: '📦', color: 'text-zinc-400' };
          const count = data.ideas.filter(i => i.category === cat).length;
          return (
            <button
              key={cat}
              onClick={() => setFilterCategory(filterCategory === cat ? 'all' : cat)}
              className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-1 ${
                filterCategory === cat ? 'bg-zinc-700 text-white' : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800'
              }`}
            >
              <span>{config.icon}</span>
              <span className="capitalize">{cat}</span>
              <span className="text-zinc-600">({count})</span>
            </button>
          );
        })}
      </div>

      {/* Ideas List */}
      <div className="space-y-6">
        {Object.entries(groupedIdeas).map(([category, ideas]) => {
          const catConfig = CATEGORY_CONFIG[category] || { icon: '📦', color: 'text-zinc-400' };
          return (
            <div key={category}>
              <h2 className={`text-lg font-semibold mb-3 flex items-center gap-2 ${catConfig.color}`}>
                <span>{catConfig.icon}</span>
                <span className="capitalize">{category}</span>
                <span className="text-zinc-600 text-sm font-normal">({ideas.length})</span>
              </h2>

              <div className="space-y-2">
                {ideas.map(idea => {
                  const statusConfig = STATUS_CONFIG[idea.status];
                  const priorityConfig = PRIORITY_CONFIG[idea.priority];
                  const isExpanded = expandedIdea === idea.id;

                  return (
                    <div
                      key={idea.id}
                      className="bg-zinc-900 rounded-lg border border-zinc-800 overflow-hidden"
                    >
                      <div
                        className="p-4 cursor-pointer hover:bg-zinc-800/50 transition-colors"
                        onClick={() => setExpandedIdea(isExpanded ? null : idea.id)}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className={`text-xs px-2 py-0.5 rounded border ${statusConfig.color}`}>
                                {statusConfig.icon} {idea.status}
                              </span>
                              <span className={`text-xs ${priorityConfig.color}`}>
                                [{priorityConfig.label}]
                              </span>
                              {idea.inspiration && (
                                <span className="text-xs text-zinc-600">
                                  via {idea.inspiration}
                                </span>
                              )}
                            </div>
                            <h3 className="font-medium text-white">{idea.title}</h3>
                            <p className="text-sm text-zinc-400 mt-1">{idea.description}</p>
                          </div>
                          <div className="text-zinc-600 text-xl">
                            {isExpanded ? '−' : '+'}
                          </div>
                        </div>
                      </div>

                      {isExpanded && idea.details && (
                        <div className="px-4 pb-4 border-t border-zinc-800 pt-3">
                          <pre className="text-xs text-zinc-400 bg-zinc-950 p-3 rounded overflow-x-auto">
                            {JSON.stringify(idea.details, null, 2)}
                          </pre>
                          <div className="mt-2 text-xs text-zinc-600">
                            Added: {idea.added_date}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {filteredIdeas.length === 0 && (
        <div className="text-center py-12 text-zinc-500">
          No ideas match the current filters
        </div>
      )}
    </div>
  );
}
