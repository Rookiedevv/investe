"""Walk-forward (no look-ahead) prediction of WIG20 dips.

For each refit date the models are trained only on rows whose targets are fully known
before that date, then used unchanged for the next REFIT sessions. Outputs one row per
session with the probabilities that would have been available that evening.
"""
from __future__ import annotations

import json
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import features as F  # noqa: E402

warnings.filterwarnings("ignore")

REFIT = 63            # refit every quarter of sessions
MIN_TRAIN = 750       # ~3 years before the first out-of-sample prediction (proxy history starts 2019)
HORIZONS = {"h1": ("t_oc1", 1), "h3": ("t_oc3", 3), "h5": ("t_oc5", 5)}


def models():
    return {
        "lr": lambda: make_pipeline(SimpleImputer(), StandardScaler(),
                                    LogisticRegression(C=0.05, max_iter=2000)),
        "gb": lambda: HistGradientBoostingClassifier(max_depth=3, learning_rate=0.04, max_iter=250,
                                                     l2_regularization=1.0, min_samples_leaf=40,
                                                     random_state=0),
    }


def walk(df: pd.DataFrame, feats: list[str], tag: str) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    n = len(df)
    X = df[feats].values.astype(float)
    starts = list(range(MIN_TRAIN, n, REFIT))
    for hname, (tcol, k) in HORIZONS.items():
        y = (df[tcol].values < 0).astype(int)
        known = ~np.isnan(df[tcol].values)
        for mname, mk in models().items():
            col = f"{tag}_{mname}_{hname}"
            out[col] = np.nan
            for s in starts:
                # targets of rows < s-k are known at decision time of row s (k-day look-ahead)
                tr = np.arange(0, max(0, s - k))
                tr = tr[known[tr]]
                m = mk()
                m.fit(X[tr], y[tr])
                te = np.arange(s, min(n, s + REFIT))
                out.iloc[te, out.columns.get_loc(col)] = m.predict_proba(X[te])[:, 1]
        # unconditional base rate from the training window (naive baseline)
        col = f"{tag}_base_{hname}"
        out[col] = np.nan
        for s in starts:
            tr = np.arange(0, max(0, s - k))
            tr = tr[known[tr]]
            te = np.arange(s, min(n, s + REFIT))
            out.iloc[te, out.columns.get_loc(col)] = y[tr].mean()
    return out


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "ETFBW20TR"
    f = F.build(base)
    f = f.dropna(subset=["r60", "dd250", "ma200"]).copy()  # warm-up
    have_foreign = all(c in f.columns for c in ("spx_r1", "vix"))
    feats_wig = F.FEATURES_WIG
    feats_all = feats_wig + ([c for c in F.FEATURES_FOREIGN if c in f.columns] if have_foreign else [])
    print(f"rows {len(f)}, {f.index.min().date()} .. {f.index.max().date()}, foreign={have_foreign}")

    res = walk(f, feats_wig, "wig")
    if have_foreign:
        res = res.join(walk(f, feats_all, "all"))
    # ensemble of the two learners on the full feature set
    tag = "all" if have_foreign else "wig"
    for h in HORIZONS:
        res[f"ens_{h}"] = res[[f"{tag}_lr_{h}", f"{tag}_gb_{h}"]].mean(axis=1)

    keep = ["close", "next_open", "next_close", "t_oc1", "t_cc1", "t_oc2", "t_oc3", "t_oc5", "t_minlow3",
            "vol20", "dd20", "spx_r1", "vix"]
    keep = [c for c in keep if c in f.columns]
    pred = f[keep].join(res)
    pred = pred[pred.filter(like="_h1").notna().any(axis=1)]
    pred.to_csv("research/wig20_model/predictions.csv", float_format="%.6f")

    # Scores, out of sample
    rows = []
    for h, (tcol, k) in HORIZONS.items():
        y = (pred[tcol] < 0).astype(int)
        ok = pred[tcol].notna()
        for col in [c for c in pred.columns if c.endswith(f"_{h}")]:
            p = pred[col]
            m = ok & p.notna()
            if m.sum() < 100:
                continue
            auc = roc_auc_score(y[m], p[m]) if p[m].nunique() > 1 else 0.5
            rows.append(dict(model=col, horizon=h, n=int(m.sum()), auc=round(auc, 4),
                             brier=round(brier_score_loss(y[m], p[m]), 4),
                             acc=round(((p[m] > 0.5) == y[m]).mean(), 4),
                             base_down=round(y[m].mean(), 4)))
    scores = pd.DataFrame(rows).sort_values(["horizon", "auc"], ascending=[True, False])
    print(scores.to_string(index=False))
    scores.to_csv("research/wig20_model/scores.csv", index=False)


if __name__ == "__main__":
    main()
