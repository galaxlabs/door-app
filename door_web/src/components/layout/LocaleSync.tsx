"use client";

import { useEffect } from "react";
import { LOCALE_STORAGE_KEY, LOCALE_UPDATED_EVENT, localeDirection, normalizeLocale } from "@/lib/locale";

function applyLocale(localeValue: unknown) {
  if (typeof document === "undefined") return;
  const locale = normalizeLocale(localeValue);
  const html = document.documentElement;
  html.lang = locale;
  html.dir = localeDirection(locale);
  html.dataset.locale = locale;
}

export default function LocaleSync() {
  useEffect(() => {
    applyLocale(window.localStorage.getItem(LOCALE_STORAGE_KEY));

    function onLocaleUpdated(event: Event) {
      const customEvent = event as CustomEvent<{ locale?: string }>;
      applyLocale(customEvent.detail?.locale);
    }

    function onStorage(event: StorageEvent) {
      if (event.key === LOCALE_STORAGE_KEY) {
        applyLocale(event.newValue);
      }
    }

    window.addEventListener(LOCALE_UPDATED_EVENT, onLocaleUpdated as EventListener);
    window.addEventListener("storage", onStorage);
    return () => {
      window.removeEventListener(LOCALE_UPDATED_EVENT, onLocaleUpdated as EventListener);
      window.removeEventListener("storage", onStorage);
    };
  }, []);

  return null;
}
