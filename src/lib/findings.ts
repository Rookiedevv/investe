// Summary of the research log (claude/research_log.md in the project), Oct 2026.
// Update this file when a new hypothesis is tested.

export type Verdict = "works" | "promising" | "lead" | "rejected";
export type Group = "general" | "banks" | "utilities" | "developers" | "carparts" | "rotation";

export type Finding = {
  group: Group;
  verdict: Verdict;
  pl: { idea: string; result: string };
  en: { idea: string; result: string };
};

export const FINDINGS: Finding[] = [
  // ── General ──
  {
    group: "general",
    verdict: "rejected",
    pl: { idea: "Reguły oparte tylko na cenie: kupno po dużym spadku, na miesięcznym dołku, po odbiciu; stop-lossy i szybkie realizacje zysku", result: "Sprawdzone na bankach, energetyce, deweloperach i częściach aut: wszystkie tracą 0,4–2% na transakcji po kosztach, tyle co losowe wejścia. Bez prawdziwego powodu wejścia stopy i cele tylko przetasowują straty." },
    en: { idea: "Price-only rules: buy after a big drop, at a monthly low, after a rebound; stop-losses and quick profit-taking", result: "Tested on banks, utilities, developers and car parts: all lose 0.4–2% per trade after costs, the same as random entries. Without a real reason to enter, stops and targets only reshuffle losses." },
  },
  {
    group: "general",
    verdict: "lead",
    pl: { idea: "Godzina transakcji: noc vs sesja", result: "Kursy średnio rosną między zamknięciem a otwarciem, a w ciągu sesji lekko spadają. Nie da się na tym zarabiać (koszty), ale: kupuj raczej pod koniec sesji, sprzedawaj raczej rano." },
    en: { idea: "Time of day: overnight vs session", result: "Prices rise on average between close and open and dip slightly during the session. Not tradable (costs), but: buy late in the session, sell in the morning." },
  },
  {
    group: "general",
    verdict: "rejected",
    pl: { idea: "Złoto, ropa, gaz, CO2 jako zapowiedź ruchów na GPW", result: "Brak wyprzedzenia. Ropa i złoto pokazują nastrój rynku (strach), ale nie przewidują kolejnego tygodnia ani miesiąca." },
    en: { idea: "Gold, oil, gas, CO2 as an early warning for Warsaw stocks", result: "No lead. Oil and gold reflect market mood (fear) but don't predict the next week or month." },
  },
  // ── Banks ──
  {
    group: "banks",
    verdict: "promising",
    pl: { idea: "Pierwszy raport w sezonie wyników jako sygnał dla całego sektora", result: "6 sezonów z dobrą reakcją (2021–2026): koszyk banków średnio +6% po kosztach, 4 z 6 zyskowne. Po złej reakcji banki przez kolejne tygodnie słabną. Mało przypadków, więc w trakcie testu na papierze." },
    en: { idea: "First report of the results season as a signal for the whole sector", result: "6 seasons with a good reaction (2021–2026): bank basket +6% on average after costs, 4 of 6 winners. After a bad reaction banks weaken for weeks. Few cases, so being paper-tested." },
  },
  {
    group: "banks",
    verdict: "promising",
    pl: { idea: "Przerwa ok. miesiąca po złej wiadomości, kupno po dobrej", result: "Głównie ogranicza największe straty (najgorsza transakcja −9% zamiast −29%). Przewaga nad losowymi wejściami ok. 1,5–2,4 pkt proc., tylko 9–10 transakcji." },
    en: { idea: "About a month's pause after bad news, buying after good news", result: "Mainly cuts the worst losses (worst trade −9% instead of −29%). Edge over random entries about 1.5–2.4 points, only 9–10 trades." },
  },
  {
    group: "banks",
    verdict: "works",
    pl: { idea: "Wstrząsy polityczne i regulacyjne (wakacje kredytowe, podatki, CHF)", result: "Pierwsza zapowiedź: sektor −5% do −9% w 2 dni. Kolejne kroki prawne działają dużo słabiej. Dlatego są podstawą reguły „przerwy”." },
    en: { idea: "Political and regulatory shocks (mortgage holidays, taxes, CHF)", result: "First announcement: sector −5% to −9% in 2 days. Later legal steps move prices much less. That's why they drive the 'pause' rule." },
  },
  {
    group: "banks",
    verdict: "rejected",
    pl: { idea: "Stopy procentowe i decyzje NBP", result: "Ok. 0,1% ruchu na każde +10 pb. Zaskoczenia NBP bez istotnego wpływu na żaden bank." },
    en: { idea: "Interest rates and NBP decisions", result: "About 0.1% move per +10 bp. NBP surprises have no significant effect on any bank." },
  },
  {
    group: "banks",
    verdict: "rejected",
    pl: { idea: "Słabsze banki doganiają resztę po wstrząsie", result: "77–92% ruchu dużych banków to ruch całego sektora; kolejność losowa, maruderzy nie nadrabiają." },
    en: { idea: "Laggard banks catch up after a shock", result: "77–92% of large banks' moves is the whole sector; the order is random and laggards don't catch up." },
  },
  {
    group: "banks",
    verdict: "rejected",
    pl: { idea: "Kupno banków taniej po złym pierwszym raporcie", result: "Silnie odrzucone: zlecenia z limitem traciły 2,7–4%, bo realizują się właśnie wtedy, gdy kurs dalej spada. Zły raport = sygnał, żeby przeczekać." },
    en: { idea: "Buying banks cheaper after a bad first report", result: "Strongly rejected: limit orders lost 2.7–4%, because they fill exactly when the price keeps falling. A bad report means wait." },
  },
  {
    group: "banks",
    verdict: "lead",
    pl: { idea: "Millennium przy opiniach i wyrokach TSUE w sprawie CHF", result: "Millennium ok. +1 pkt proc. względem innych banków na zdarzenie CHF (t ≈ 3). Pozostałe banki: szum." },
    en: { idea: "Millennium on CJEU CHF opinions and rulings", result: "Millennium about +1 point vs other banks per CHF event (t ≈ 3). Other banks: noise." },
  },
  // ── Utilities ──
  {
    group: "utilities",
    verdict: "works",
    pl: { idea: "Co porusza PGE, Tauron i Eneę", result: "Najmocniej: wydzielenie węgla (NABE) ±8–10% w 2 dni, ETS/CO2 ±5–7%, dywidendy. Polenergia zachowuje się zupełnie inaczej i wymaga osobnej analizy." },
    en: { idea: "What moves PGE, Tauron and Enea", result: "Most of all: the coal spin-off (NABE) ±8–10% in 2 days, ETS/CO2 ±5–7%, dividends. Polenergia behaves completely differently and needs its own analysis." },
  },
  {
    group: "utilities",
    verdict: "rejected",
    pl: { idea: "Kontynuacja ruchu po wiadomościach (jak w bankach)", result: "Wiadomość jest wyceniona w 1–2 dni, potem brak trendu. Reguły bankowe na energetyce tracą." },
    en: { idea: "Follow-through after news (like banks)", result: "News is priced within 1–2 days, then no trend. Bank rules lose money on utilities." },
  },
  {
    group: "utilities",
    verdict: "lead",
    pl: { idea: "Kupno na otwarciu po wiadomości spoza sesji", result: "Od otwarcia do zamknięcia średnio +2% w kierunku wiadomości, ale tylko 13 przypadków. Wymagałoby powiadomień w czasie rzeczywistym." },
    en: { idea: "Buying at the open after news outside the session", result: "Open to close +2% on average in the news direction, but only 13 cases. Would need real-time alerts." },
  },
  {
    group: "utilities",
    verdict: "rejected",
    pl: { idea: "Polityka (wybory, rząd, UE) a spadki energetyki", result: "Polityka zwiększa wahania w obie strony, ale kierunku nie da się przewidzieć z rodzaju wydarzenia." },
    en: { idea: "Politics (elections, government, EU) and falls in utilities", result: "Politics increases swings both ways, but the direction can't be predicted from the type of event." },
  },
  // ── Developers ──
  {
    group: "developers",
    verdict: "lead",
    pl: { idea: "Trend 12-miesięczny względem WIG (Dom Development, koszyk)", result: "Lepszy od losowego wyczucia czasu, ale nie lepszy od zwykłego trzymania sektora, który urósł 6,7×. Przydatny głównie jako „wyjdź z tonącego sektora” (zadziałał raz, 2022)." },
    en: { idea: "12-month trend vs WIG (Dom Development, basket)", result: "Better than random timing, but not better than simply holding a sector that rose 6.7×. Useful mainly as 'get out of a sinking sector' (fired once, 2022)." },
  },
  {
    group: "developers",
    verdict: "rejected",
    pl: { idea: "Kwartalna sprzedaż mieszkań i pierwszy raportujący (Atal)", result: "Brak kontynuacji; po bardzo dobrej sprzedaży kurs raczej się cofa. Zysk z kupna po słabej sprzedaży pochodzi prawie tylko z mało płynnego Archicomu." },
    en: { idea: "Quarterly home sales and the first reporter (Atal)", result: "No follow-through; after very strong sales the price tends to fall back. Gains from buying after weak sales come almost only from illiquid Archicom." },
  },
  {
    group: "developers",
    verdict: "lead",
    pl: { idea: "Obniżki stóp NBP", result: "Deweloperzy po obniżce zostawali w tyle za WIG w 8 z 12 przypadków (średnio −3,9 pkt). Za mało, żeby na tym grać." },
    en: { idea: "NBP rate cuts", result: "Developers lagged WIG after a cut in 8 of 12 cases (−3.9 points on average). Too small to trade on." },
  },
  // ── Car parts ──
  {
    group: "carparts",
    verdict: "promising",
    pl: { idea: "Przyspieszenie miesięcznej sprzedaży Inter Cars i Auto Partner", result: "47 transakcji, średnio +6% po kosztach (ok. miesiąc), 68% zyskownych, dodatnio w obu okresach i dla obu spółek, 8 z 9 lat na plusie. Najlepszy wynik badań, teraz test na papierze." },
    en: { idea: "Monthly sales acceleration at Inter Cars and Auto Partner", result: "47 trades, +6% on average after costs (about a month), 68% winners, positive in both periods and for both companies, 8 of 9 years up. The best result so far, now paper-tested." },
  },
  {
    group: "carparts",
    verdict: "rejected",
    pl: { idea: "Auto Partner (raportuje pierwszy) jako zapowiedź dla Inter Cars", result: "Sprzedaż AP przewiduje sprzedaż IC (korelacja 0,78), ale nie reakcję kursu IC: rynek już to wycenia." },
    en: { idea: "Auto Partner (reports first) as a preview for Inter Cars", result: "AP's sales predict IC's sales (correlation 0.78), but not IC's share reaction: the market already prices it in." },
  },
  // ── Rotation ──
  {
    group: "rotation",
    verdict: "lead",
    pl: { idea: "Energetyka po uderzeniu rządu w banki", result: "Dodatnie, ale zależne głównie od jednej transakcji z 2020 r.; bez niej przewaga ok. 2 pkt proc. Za mało transakcji." },
    en: { idea: "Utilities after a government hit on banks", result: "Positive but driven mostly by one 2020 trade; without it the edge is about 2 points. Too few trades." },
  },
  {
    group: "rotation",
    verdict: "rejected",
    pl: { idea: "Co miesiąc najlepszy sektor z ostatniego miesiąca", result: "Wynik zależał od dnia miesiąca zmiany (koniec miesiąca +827%, 10. dzień +41%), czyli przypadek kalendarza, nie prawdziwa zależność." },
    en: { idea: "Each month, the best sector of the past month", result: "The result depended on the day of the month (month-end +827%, the 10th +41%): calendar luck, not a real effect." },
  },
];
