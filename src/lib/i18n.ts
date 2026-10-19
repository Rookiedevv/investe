export type Lang = "pl" | "en";

const pl = {
  appName: "Inwestycje",
  login: {
    tagline: "Sygnały z przetestowanych reguł, zdarzenia rynkowe i dziennik transakcji testowych.",
    google: "Zaloguj się przez Google",
    failed: "Logowanie się nie udało. Spróbuj ponownie.",
    privateNote: "Aplikacja prywatna: wejdą tylko adresy z listy.",
  },
  notAllowed: {
    title: "Tego konta nie ma na liście",
    body: "Zaloguj się adresem, który dodano do aplikacji, albo poproś administratora o dodanie.",
    tryAnother: "Spróbuj innego konta",
  },
  nav: { home: "Sygnały", events: "Zdarzenia", findings: "Wnioski", journal: "Dziennik", settings: "Ustawienia" },
  data: {
    asOf: "Dane z sesji {date}",
    updated: "aktualizacja {time}",
    none: "Dane jeszcze nie zostały wczytane. Pierwsza aktualizacja trwa kilka minut po konfiguracji.",
    warning: "Uwaga: {msg}",
  },
  signals: {
    intro: "Reguły, które przetrwały testy na danych 2018–2026. Sprawdzane automatycznie po każdej sesji. To sygnały do transakcji testowych, nie porady inwestycyjne.",
    state: { idle: "Nic do zrobienia", watch: "Obserwuj", active: "Sygnał", blocked: "Blokada" },
    history: "Historia: {n} transakcji, średnio {avg} po kosztach, {win} zyskownych, najgorsza {worst}",
    showHistory: "Zobacz wszystkie transakcje",
    toJournal: "Zapisz w dzienniku",
    exitRule: "Sprzedaj, gdy w ciągu jednej sesji spadnie o więcej niż {drop} (maks. {days} sesji).",
    openSince: "Pozycja od {date}: {ret} po kosztach.",
    carparts: {
      title: "Części samochodowe: przyspieszenie sprzedaży",
      about: "Gdy miesięczna sprzedaż Inter Cars lub Auto Partner rośnie wyraźnie szybciej niż średnio w 3 poprzednich miesiącach (o ponad 5 pkt proc.), kurs zwykle rośnie aż do następnego raportu. Najlepszy wynik badań.",
      line: "{name}, {period}: {yoy} r/r, przyspieszenie {accel} (próg +5 pkt)",
      idle: "Brak sygnału. Kolejne dane ok. {date}.",
      buy: "Kup {name} na otwarciu {date}. Sprzedaj na otwarciu po kolejnym raporcie sprzedaży (ok. {next}).",
      buySoon: "Kup {name} na otwarciu drugiej sesji po raporcie. Sprzedaj po kolejnym raporcie (ok. {next}).",
      holding: "{name}: kupione {date} po {price} zł, teraz {ret} po kosztach. Sprzedaj na otwarciu po raporcie ok. {next}.",
    },
    readthrough: {
      title: "Banki: pierwszy raport w sezonie wyników",
      about: "Pierwszy bank publikujący wyniki zdradza nastrój całego sektora. Gdy rynek przyjmie go dobrze (o ≥1,5 pkt proc. lepiej niż pozostałe banki), banki zwykle rosną przez kolejne tygodnie. Gdy źle, lepiej przeczekać.",
      watch: "Sezon {period}: pierwsze raporty {date} ({tickers}). Wieczorem po raporcie sprawdzę reakcję rynku.",
      schedule: "Kalendarz raportów",
      buyNext: "Dobra reakcja na raport {tickers} ({reaction}). Kup koszyk banków na zamknięciu najbliższej sesji.",
      lastSeason: "Ostatni sezon {period}: {tickers} {reaction} vs reszta, ocena: {verdict}.",
      verdict: { good: "dobra", bad: "zła", neutral: "neutralna", pending: "czeka" },
      idle: "Następny sezon jeszcze nie w kalendarzu.",
      basket: "Koszyk = po równo 9 banków (PKO, Pekao, Erste, mBank, ING, Millennium, Alior, Handlowy, BNP).",
    },
    regime: {
      title: "Banki: przerwa po złych wiadomościach",
      about: "Po złej wiadomości dla banków (ustawa, wyrok, słaby pierwszy raport, spadek sektora o 6% w 2 dni) przez 20 sesji nie kupujemy banków. Po dobrej wiadomości kupujemy koszyk, gdy rośnie 3 sesje z rzędu.",
      blocked: "Nie kupuj banków jeszcze przez {n} sesji. Powód ({date}): {what}",
      idle: "Brak blokady. Ostatnia zła wiadomość {date}: {what}",
      lastGood: "Ostatnia dobra wiadomość {date}: {what}",
    },
    rotation: {
      title: "Energetyka po uderzeniu w banki",
      about: "Gdy rząd lub sąd uderza w banki, pieniądze bywają przenoszone do PGE, Tauronu i Enei. Niepotwierdzone: wynik w historii zależy głównie od jednej transakcji z 2020 r. Traktuj jako obserwację.",
      idle: "Brak sygnału. Ostatni: {date}, {ret}.",
      lead: "niepotwierdzone",
    },
    historyTitle: "Historia reguły",
    entry: "Wejście",
    exit: "Wyjście",
    open: "otwarta",
    noTrades: "Brak transakcji.",
    back: "Wróć do sygnałów",
    basketNote: "Ceny koszyków to indeks (start = 100), nie cena akcji.",
    how: "Na czym to polega?",
  },
  home: {
    watchlist: "Obserwowane",
    lastClose: "Ost. zamknięcie",
    day: "Sesja",
    noPrices: "brak danych",
    openTrades: "Twoje otwarte pozycje",
  },
  events: {
    title: "Zdarzenia",
    intro: "Zdarzenia z badań i kolejne, dopisywane przeze mnie. Opisy pochodzą ze źródeł (po angielsku).",
    all: "Wszystkie",
    upcoming: "Nadchodzące",
    past: "Ostatnie",
    more: "Pokaż więcej",
    empty: "Brak zdarzeń.",
    source: "Źródło",
    positive: "dobre",
    negative: "złe",
    neutral: "neutralne",
    scheduled: "planowane",
  },
  sectors: { banks: "Banki", utilities: "Energetyka", carparts: "Części aut", politics: "Polityka", developers: "Deweloperzy", index: "Indeks", other: "Inne" },
  findings: {
    title: "Wnioski z badań",
    intro: "Co zostało sprawdzone na danych z lat 2018–2026 i jaki był wynik. Koszty: ok. 1% za kupno i sprzedaż.",
    verdict: { works: "Działa", promising: "Obiecujące", lead: "Do sprawdzenia", rejected: "Nie działa" },
    groups: { general: "Ogólnie", banks: "Banki", utilities: "Energetyka", developers: "Deweloperzy", carparts: "Części samochodowe", rotation: "Rotacja sektorów" },
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
  },
  error: "Coś poszło nie tak. Sprawdź dane i spróbuj ponownie.",
};

type Dict = typeof pl;

const en: Dict = {
  appName: "Investing",
  login: {
    tagline: "Signals from tested rules, market events and a paper-trading journal.",
    google: "Sign in with Google",
    failed: "Sign-in failed. Please try again.",
    privateNote: "Private app: only listed addresses can get in.",
  },
  notAllowed: {
    title: "This account isn't on the list",
    body: "Sign in with an address that was added to the app, or ask the admin to add you.",
    tryAnother: "Try another account",
  },
  nav: { home: "Signals", events: "Events", findings: "Findings", journal: "Journal", settings: "Settings" },
  data: {
    asOf: "Data from the {date} session",
    updated: "updated {time}",
    none: "Data hasn't been loaded yet. The first update takes a few minutes after setup.",
    warning: "Note: {msg}",
  },
  signals: {
    intro: "Rules that survived testing on 2018–2026 data, checked automatically after every session. Signals for paper trades, not investment advice.",
    state: { idle: "Nothing to do", watch: "Watch", active: "Signal", blocked: "Blocked" },
    history: "History: {n} trades, average {avg} after costs, {win} winners, worst {worst}",
    showHistory: "See all trades",
    toJournal: "Record in journal",
    exitRule: "Sell when it falls more than {drop} in a single session (max {days} sessions).",
    openSince: "Position since {date}: {ret} after costs.",
    carparts: {
      title: "Car parts: sales acceleration",
      about: "When Inter Cars' or Auto Partner's monthly sales grow clearly faster than the average of the previous 3 months (by more than 5 points), the share price usually keeps rising until the next report. The best research result.",
      line: "{name}, {period}: {yoy} y/y, acceleration {accel} (threshold +5 pts)",
      idle: "No signal. Next figures around {date}.",
      buy: "Buy {name} at the open on {date}. Sell at the open after the next sales report (around {next}).",
      buySoon: "Buy {name} at the open of the second session after the report. Sell after the next report (around {next}).",
      holding: "{name}: bought {date} at {price} zł, now {ret} after costs. Sell at the open after the report around {next}.",
    },
    readthrough: {
      title: "Banks: first report of the results season",
      about: "The first bank to report reveals the mood of the whole sector. If the market likes it (≥1.5 points better than the other banks), banks usually rise for the following weeks. If not, it's better to wait.",
      watch: "Season {period}: first reports on {date} ({tickers}). I'll check the market reaction that evening.",
      schedule: "Report calendar",
      buyNext: "Good reaction to {tickers} ({reaction}). Buy the bank basket at the close of the next session.",
      lastSeason: "Last season {period}: {tickers} {reaction} vs the rest, verdict: {verdict}.",
      verdict: { good: "good", bad: "bad", neutral: "neutral", pending: "pending" },
      idle: "Next season not in the calendar yet.",
      basket: "Basket = 9 banks in equal parts (PKO, Pekao, Erste, mBank, ING, Millennium, Alior, Handlowy, BNP).",
    },
    regime: {
      title: "Banks: pause after bad news",
      about: "After bad news for banks (a law, a ruling, a weak first report, a 6% sector fall in 2 days) we don't buy banks for 20 sessions. After good news we buy the basket once it rises 3 sessions in a row.",
      blocked: "Don't buy banks for another {n} sessions. Reason ({date}): {what}",
      idle: "No block. Last bad news {date}: {what}",
      lastGood: "Last good news {date}: {what}",
    },
    rotation: {
      title: "Utilities after a hit on banks",
      about: "When the government or a court hits banks, money sometimes moves to PGE, Tauron and Enea. Unproven: the history depends mostly on one 2020 trade. Treat it as an observation.",
      idle: "No signal. Last one: {date}, {ret}.",
      lead: "unproven",
    },
    historyTitle: "Rule history",
    entry: "Entry",
    exit: "Exit",
    open: "open",
    noTrades: "No trades.",
    back: "Back to signals",
    basketNote: "Basket prices are an index (start = 100), not a share price.",
    how: "How does it work?",
  },
  home: {
    watchlist: "Watchlist",
    lastClose: "Last close",
    day: "Session",
    noPrices: "no data",
    openTrades: "Your open positions",
  },
  events: {
    title: "Events",
    intro: "Events from the research plus new ones I add. Descriptions come from the sources (in English).",
    all: "All",
    upcoming: "Upcoming",
    past: "Recent",
    more: "Show more",
    empty: "No events.",
    source: "Source",
    positive: "good",
    negative: "bad",
    neutral: "neutral",
    scheduled: "scheduled",
  },
  sectors: { banks: "Banks", utilities: "Utilities", carparts: "Car parts", politics: "Politics", developers: "Developers", index: "Index", other: "Other" },
  findings: {
    title: "Research findings",
    intro: "What we tested on 2018–2026 data and what came out of it. Costs: about 1% per buy-and-sell.",
    verdict: { works: "Works", promising: "Promising", lead: "To check", rejected: "Doesn't work" },
    groups: { general: "General", banks: "Banks", utilities: "Utilities", developers: "Developers", carparts: "Car parts", rotation: "Sector rotation" },
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
  },
  error: "Something went wrong. Check the values and try again.",
};

export type { Dict };

export function getDict(lang: Lang): Dict {
  return lang === "en" ? en : pl;
}

export function langFromHeader(accept: string): Lang {
  return /^en/i.test(accept) ? "en" : "pl";
}

/** Fill {placeholders} in a text. */
export function fill(text: string, vars: Record<string, string | number>) {
  return text.replace(/\{(\w+)\}/g, (_, k) => (k in vars ? String(vars[k]) : `{${k}}`));
}

const LOCALE: Record<Lang, string> = { pl: "pl-PL", en: "en-GB" };

export function fmtMoney(n: number, lang: Lang) {
  return new Intl.NumberFormat(LOCALE[lang], { style: "currency", currency: "PLN" }).format(n);
}

export function fmtNum(n: number, lang: Lang, digits = 2) {
  return new Intl.NumberFormat(LOCALE[lang], { minimumFractionDigits: digits, maximumFractionDigits: digits }).format(n);
}

export function fmtPct(n: number, lang: Lang, digits = 2) {
  return new Intl.NumberFormat(LOCALE[lang], { style: "percent", minimumFractionDigits: digits, maximumFractionDigits: digits }).format(n);
}

/** Signed percentage, e.g. +5,2% / −3,1%. */
export function fmtSigned(n: number, lang: Lang, digits = 1) {
  return new Intl.NumberFormat(LOCALE[lang], { style: "percent", signDisplay: "exceptZero", minimumFractionDigits: digits, maximumFractionDigits: digits }).format(n);
}

/** Signed percentage points from a number already in percent, e.g. +1,4 pkt. */
export function fmtPts(n: number, lang: Lang) {
  const v = new Intl.NumberFormat(LOCALE[lang], { signDisplay: "exceptZero", minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(n);
  return lang === "pl" ? `${v} pkt` : `${v} pts`;
}

export function fmtDate(iso: string, lang: Lang) {
  return new Intl.DateTimeFormat(LOCALE[lang], { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" }).format(
    new Date(`${iso.slice(0, 10)}T00:00:00Z`),
  );
}

export function fmtDateTime(iso: string, lang: Lang) {
  return new Intl.DateTimeFormat(LOCALE[lang], { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit", timeZone: "Europe/Warsaw" }).format(new Date(iso));
}
