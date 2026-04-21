export type LocaleCode = "en" | "ur" | "ar";

export const LOCALE_STORAGE_KEY = "door_locale_preference";
export const LOCALE_UPDATED_EVENT = "door:locale-updated";

export function normalizeLocale(value: unknown): LocaleCode {
  if (value === "ur" || value === "ar") return value;
  return "en";
}

export function localeDirection(locale: LocaleCode): "ltr" | "rtl" {
  return locale === "en" ? "ltr" : "rtl";
}

export function persistLocale(locale: LocaleCode) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(LOCALE_STORAGE_KEY, locale);
  window.dispatchEvent(new CustomEvent(LOCALE_UPDATED_EVENT, { detail: { locale } }));
}
