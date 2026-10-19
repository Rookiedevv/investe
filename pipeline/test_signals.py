"""Small checks of the rule mechanics on made-up data. Run: python -m pytest pipeline -q"""
import pandas as pd

import signals as S


def sessions(n=10, start="2026-01-05"):
    return pd.bdate_range(start, periods=n)


def test_reaction_day_before_and_after_session():
    s = sessions()
    assert S.reaction_day(s, "2026-01-06", "08:00", "before") == 1
    assert S.reaction_day(s, "2026-01-06", "17:30", "after") == 2
    assert S.reaction_day(s, "2026-01-06", "18:10", None) == 2  # time alone decides
    # Saturday release -> Monday session
    assert S.reaction_day(s, "2026-01-10", None, "non_trading_day") == 5


def test_noise_exit_sells_on_big_drop():
    s = pd.Series([100, 101, 100.5, 101, 95, 96], dtype=float)
    nz = pd.Series([0.01] * 6)
    assert S.noise_exit(s, nz, 0, 2.0, 60) == (4, False)  # -5.9% < -2%


def test_noise_exit_stays_open_without_drop():
    s = pd.Series([100, 101, 102, 103], dtype=float)
    nz = pd.Series([0.01] * 4)
    assert S.noise_exit(s, nz, 0, 2.0, 60) == (3, True)


def test_bank_event_sign():
    assert S.bank_event_sign("Sejm passes law; negative for banks") == -1
    assert S.bank_event_sign("CJEU judgment; positive for banks: ...") == 1
    assert S.bank_event_sign("Rate 3.75% -> 3.75%; hold") == 0


def test_carparts_acceleration():
    rows = []
    for m, yoy in zip(range(1, 6), [10, 10, 10, 20, 9]):
        rows.append(dict(date=f"2026-0{m}-08", time="17:10", session_timing="after", ticker="CAR",
                         period=f"2026-0{m}", sales_pln_m="100", sales_prev_year_pln_m="", yoy_pct=str(yoy)))
    rel = S.carparts_releases(pd.DataFrame(rows))
    assert list(rel["accel"].round(2))[3:] == [10.0, -4.33]
