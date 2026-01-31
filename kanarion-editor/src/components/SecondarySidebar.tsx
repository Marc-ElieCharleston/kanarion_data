'use client';

import { ReactNode, useState } from 'react';
import { useLocale } from '@/i18n/provider';
import { SearchBar } from '@/components/SearchBar';
import { ButtonGroup } from '@/components/ButtonGroup';

interface NavItem {
  id: string;
  icon?: string;
  label: string;
  count?: number;
  isActive: boolean;
  onClick: () => void;
  className?: string;
  activeClassName?: string;
}

interface NavGroup {
  id: string;
  label?: string;
  items: NavItem[];
}

interface FilterConfig {
  id: string;
  label: string;
  options: Array<{ value: string; label: string; count?: number }>;
  value: string;
  onChange: (value: string) => void;
}

interface SecondarySidebarProps {
  // Header
  title: string;
  subtitle?: string;

  // Search
  showSearch?: boolean;
  searchValue?: string;
  onSearchChange?: (value: string) => void;
  searchPlaceholder?: string;

  // Filters (ButtonGroup style)
  filters?: FilterConfig[];

  // Navigation - can be flat items or grouped
  navGroups?: NavGroup[];
  navItems?: NavItem[];

  // Custom content above/below navigation
  headerContent?: ReactNode;
  footerContent?: ReactNode;

  // Children for complete flexibility (replaces nav if provided alone)
  children?: ReactNode;
}

export function SecondarySidebar({
  title,
  subtitle,
  showSearch = false,
  searchValue = '',
  onSearchChange,
  searchPlaceholder,
  filters,
  navGroups,
  navItems,
  headerContent,
  footerContent,
  children,
}: SecondarySidebarProps) {
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const { locale } = useLocale();

  const defaultSearchPlaceholder = locale === 'fr' ? 'Rechercher...' : 'Search...';

  const handleItemClick = (onClick: () => void) => {
    onClick();
    setIsMobileOpen(false);
  };

  const renderNavItem = (item: NavItem) => {
    const baseClasses = 'w-full flex items-center justify-between gap-2 px-3 py-2.5 rounded-lg transition-colors text-left';
    const activeClasses = item.activeClassName || 'bg-violet-500/20 text-violet-300 border border-violet-500/30';
    const inactiveClasses = 'text-zinc-400 hover:bg-zinc-800/50 hover:text-white';

    return (
      <button
        key={item.id}
        onClick={() => handleItemClick(item.onClick)}
        className={`${baseClasses} ${item.isActive ? activeClasses : inactiveClasses} ${item.className || ''}`}
      >
        <span className="flex items-center gap-2">
          {item.icon && <span>{item.icon}</span>}
          <span>{item.label}</span>
        </span>
        {item.count !== undefined && (
          <span className="text-xs text-zinc-500">({item.count})</span>
        )}
      </button>
    );
  };

  const sidebarContent = (
    <>
      {/* Header */}
      <div className="p-4 border-b border-zinc-800">
        <h2 className="text-lg font-semibold">{title}</h2>
        {subtitle && <p className="text-xs text-zinc-500 mt-1">{subtitle}</p>}
      </div>

      {/* Custom header content */}
      {headerContent}

      {/* Search */}
      {showSearch && onSearchChange && (
        <div className="p-4 border-b border-zinc-800">
          <SearchBar
            value={searchValue}
            onChange={onSearchChange}
            placeholder={searchPlaceholder || defaultSearchPlaceholder}
          />
        </div>
      )}

      {/* Filters */}
      {filters && filters.map((filter) => (
        <div key={filter.id} className="p-4 border-b border-zinc-800">
          <label className="text-xs text-zinc-500 uppercase tracking-wider mb-2 block">
            {filter.label}
          </label>
          <ButtonGroup
            options={filter.options}
            value={filter.value}
            onChange={filter.onChange}
          />
        </div>
      ))}

      {/* Navigation */}
      {(navGroups || navItems) && (
        <nav className="p-2 flex-1">
          {/* Flat navigation items */}
          {navItems && navItems.map(renderNavItem)}

          {/* Grouped navigation */}
          {navGroups && navGroups.map((group) => (
            <div key={group.id} className="mb-2">
              {group.label && (
                <div className="text-xs text-zinc-500 uppercase tracking-wider px-2 py-1 mb-1">
                  {group.label}
                </div>
              )}
              {group.items.map(renderNavItem)}
            </div>
          ))}
        </nav>
      )}

      {/* Children (custom content) */}
      {children}

      {/* Footer content */}
      {footerContent}
    </>
  );

  return (
    <>
      {/* Mobile hamburger button */}
      <button
        onClick={() => setIsMobileOpen(!isMobileOpen)}
        className="lg:hidden fixed top-20 left-4 z-50 p-2 bg-zinc-800 rounded-lg border border-zinc-700 hover:bg-zinc-700 transition-colors"
        aria-label="Toggle filters"
      >
        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          {isMobileOpen ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          )}
        </svg>
      </button>

      {/* Mobile overlay */}
      {isMobileOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/50 z-40"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          w-64 bg-zinc-900/50 border-r border-zinc-800 overflow-y-auto flex flex-col
          lg:relative lg:translate-x-0
          ${isMobileOpen ? 'fixed inset-y-0 left-0 z-40 translate-x-0' : 'hidden lg:flex'}
        `}
      >
        {sidebarContent}
      </aside>
    </>
  );
}
