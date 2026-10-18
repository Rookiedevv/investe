export type Lang = "pl" | "en";

const pl = {
  appName: "Inwestycje",
  login: {
    tagline: "Zdarzenia, ceny i dziennik transakcji testowych w jednym miejscu.",
    google: "Zaloguj się przez Google",
    failed: "Logowanie się nie udało. Spróbuj ponownie.",
    privateNote: "Aplikacja prywatna: wejdą tylko adresy z listy.",
  },
  notAllowed: {
    title: "Tego konta nie ma na liście",
    body: "Zaloguj się adresem, który dodano do aplikacji, albo poproś administratora o dodanie.",
    tryAnother: "Spróbuj innego konta",
  },
  nav: { home: "Pulpit", events: "Zdarzenia", journal: "Dziennik", settings: "Ustawienia" },
  home: {
    upcoming: "Najbliższe 14 dni",
    noUpcoming: "Brak zaplanowanych zdarzeń. Dodaj je w zakładce Zdarzenia.",
    watchlist: "Obserwowane",
    lastClose: "Ost. zamknięcie",
    noPrices: "brak danych",
    openTrades: "Otwarte pozycje",
  },
  events: {
    title: "Zdarzenia",
    add: "Dodaj zdarzenie",
    all: "Wszystkie",
    date: "Data",
    time: "Godzina",
    session: "Względem sesji",
    ticker: "Spółka / grupa",
    category: "Kategoria",
    type: "Typ",
    severity: "Waga (1–5)",
    direction: "Kierunek",
    description: "Opis",
    source: "Źródło (link)",
    save: "Zapisz",
    empty: "Brak zdarzeń.",
    delete: "Usuń",
    positive: "pozytywne",
    negative: "negatywne",
    mixed: "mieszane",
    none: "—",
  },
  journal: {
    title: "Dziennik transakcji testowych",
    note: "Transakcje na papierze, z prowizją eMaklera (0,39%, min. 5 zł) w każdą stronę.",
    open: "Otwórz pozycję",
    ticker: "Spółka",
    date: "Data",
    shares: "Liczba akcji",
    price: "Cena",
    reason: "Dlaczego",
    save: "Zapisz",
    close: "Zamknij",
    closePrice: "Cena wyjścia",
    openList: "Otwarte",
    closedList: "Zamknięte",
    empty: "Brak transakcji.",
    breakEven: "Próg rentowności",
    fees: "Prowizje",
    net: "Wynik netto",
    yearTotal: "Wynik w tym roku",
    belka: "Podatek Belki (szac.)",
    delete: "Usuń",
  },
  settings: {
    title: "Ustawienia",
    language: "Język",
    allowList: "Lista dostępu",
    allowListNote: "Tylko te adresy Google mogą się zalogować.",
    addEmail: "Dodaj",
    admin: "admin",
    remove: "Usuń",
    signOut: "Wyloguj",
    saved: "Zapisano",
  },
  sectors: { banks: "Banki", utilities: "Energetyka", other: "Inne" },
  error: "Coś poszło nie tak. Sprawdź dane i spróbuj ponownie.",
};

type Dict = typeof pl;

const en: Dict = {
  appName: "Investing",
  login: {
    tagline: "Events, prices and a paper-trading journal in one place.",
    google: "Sign in with Google",
    failed: "Sign-in failed. Please try again.",
    privateNote: "Private app: only listed addresses can get in.",
  },
  notAllowed: {
    title: "This account isn't on the list",
    body: "Sign in with an address that was added to the app, or ask the admin to add you.",
    tryAnother: "Try another account",
  },
  nav: { home: "Home", events: "Events", journal: "Journal", settings: "Settings" },
  home: {
    upcoming: "Next 14 days",
    noUpcoming: "Nothing scheduled. Add events on the Events tab.",
    watchlist: "Watchlist",
    lastClose: "Last close",
    noPrices: "no data",
    openTrades: "Open positions",
  },
  events: {
    title: "Events",
    add: "Add event",
    all: "All",
    date: "Date",
    time: "Time",
    session: "Relative to session",
    ticker: "Company / group",
    category: "Category",
    type: "Type",
    severity: "Severity (1–5)",
    direction: "Direction",
    description: "Description",
    source: "Source (link)",
    save: "Save",
    empty: "No events.",
    delete: "Delete",
    positive: "positive",
    negative: "negative",
    mixed: "mixed",
    none: "—",
  },
  journal: {
    title: "Paper-trading journal",
    note: "Paper trades, with eMakler commission (0.39%, min 5 zł) each way.",
    open: "Open a position",
    ticker: "Company",
    date: "Date",
    shares: "Shares",
    price: "Price",
    reason: "Why",
    save: "Save",
    close: "Close",
    closePrice: "Exit price",
    openList: "Open",
    closedList: "Closed",
    empty: "No trades.",
    breakEven: "Break-even move",
    fees: "Fees",
    net: "Net result",
    yearTotal: "Result this year",
    belka: "Belka tax (est.)",
    delete: "Delete",
  },
  settings: {
    title: "Settings",
    language: "Language",
    allowList: "Allow-list",
    allowListNote: "Only these Google addresses can sign in.",
    addEmail: "Add",
    admin: "admin",
    remove: "Remove",
    signOut: "Sign out",
    saved: "Saved",
  },
  sectors: { banks: "Banks", utilities: "Utilities", other: "Other" },
  error: "Something went wrong. Check the values and try again.",
};

export function getDict(lang: Lang): Dict {
  return lang === "en" ? en : pl;
}

export function langFromHeader(accept: string): Lang {
  return /^en/i.test(accept) ? "en" : "pl";
}

const LOCALE: Record<Lang, string> = { pl: "pl-PL", en: "en-GB" };

export function fmtMoney(n: number, lang: Lang) {
  return new Intl.NumberFormat(LOCALE[lang], { style: "currency", currency: "PLN" }).format(n);
}

export function fmtNum(n: number, lang: Lang, digits = 2) {
  return new Intl.NumberFormat(LOCALE[lang], { minimumFractionDigits: digits, maximumFractionDigits: digits }).format(n);
}

export function fmtPct(n: number, lang: Lang) {
  return new Intl.NumberFormat(LOCALE[lang], { style: "percent", minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n);
}

export function fmtDate(iso: string, lang: Lang) {
  return new Intl.DateTimeFormat(LOCALE[lang], { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" }).format(
    new Date(`${iso}T00:00:00Z`),
  );
}
