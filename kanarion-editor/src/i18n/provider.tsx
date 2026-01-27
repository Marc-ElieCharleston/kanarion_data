'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { NextIntlClientProvider } from 'next-intl';
import { Locale, defaultLocale } from './config';

type LocaleContextType = {
  locale: Locale;
  setLocale: (locale: Locale) => void;
};

const LocaleContext = createContext<LocaleContextType | null>(null);

export function useLocale() {
  const context = useContext(LocaleContext);
  if (!context) {
    throw new Error('useLocale must be used within a LocaleProvider');
  }
  return context;
}

async function loadMessages(locale: Locale) {
  return (await import(`../../messages/${locale}.json`)).default;
}

export function LocaleProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(defaultLocale);
  const [messages, setMessages] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    // Load saved locale from localStorage
    const savedLocale = localStorage.getItem('locale') as Locale | null;
    if (savedLocale && (savedLocale === 'fr' || savedLocale === 'en')) {
      setLocaleState(savedLocale);
    }
  }, []);

  useEffect(() => {
    // Load messages when locale changes
    loadMessages(locale).then(setMessages);
    localStorage.setItem('locale', locale);
  }, [locale]);

  const setLocale = (newLocale: Locale) => {
    setLocaleState(newLocale);
  };

  if (!messages) {
    return null; // Loading state
  }

  return (
    <LocaleContext.Provider value={{ locale, setLocale }}>
      <NextIntlClientProvider locale={locale} messages={messages}>
        {children}
      </NextIntlClientProvider>
    </LocaleContext.Provider>
  );
}
