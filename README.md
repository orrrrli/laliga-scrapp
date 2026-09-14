# La Liga Match Predictor

An end-to-end data pipeline that scrapes seven seasons of Spanish La Liga team
statistics, merges them into a single match-level dataset, and trains a neural
network to predict whether the home team wins.

Built as a research project for *Tópicos Selectos de la Investigación* (UABC).

---

## Pipeline

```
fbref.com
    │
    ├─ Selenium ──────────► JS-rendered stat tables (click "per 90" toggle, wait for re-render)
    └─ requests + BS4 ────► static tables (wages)
    │
    ▼
Raw per-season CSVs        9 stat families × 7 seasons
    │
    ▼
UnificadorDataSets.py      18 merges (9 datasets × home/away) on (Equipo, Temporada)
    │
    ▼
merged_all_statistics.txt  2,660 matches × 226 columns
    │
    ▼
train_test_split (stratified, 20% held out)
    │
    ▼
SMOTE (train only) ──► SimpleImputer(mean) ──► StandardScaler
    │
    ▼
Keras Tuner RandomSearch   Dense + Dropout + L2, EarlyStopping
    │
    ▼
soccer_model.h5  +  scaler.pkl  +  imputer.pkl
```

---

## Stack

| Stage | Tools |
|---|---|
| **Dynamic scraping** | Selenium (`WebDriverWait`, `expected_conditions`, JS-injected clicks) |
| **Static scraping** | requests · BeautifulSoup 4 |
| **Text normalization** | `unicodedata` NFKD · Unidecode · regex |
| **Data wrangling** | pandas (suffixed multi-key merges) · NumPy |
| **Class balancing** | SMOTE (imbalanced-learn) |
| **Preprocessing** | scikit-learn `SimpleImputer` · `StandardScaler`, persisted with joblib |
| **Model** | TensorFlow / Keras `Sequential` — Dense + Dropout + L2 regularization, sigmoid output |
| **Hyperparameter search** | Keras Tuner `RandomSearch` · `EarlyStopping(patience=10, restore_best_weights=True)` |
| **Baseline** | scikit-learn `RandomForestClassifier` |
| **Evaluation** | `classification_report` · `confusion_matrix` · `roc_auc_score` · ROC curves |
| **Visualization** | matplotlib · seaborn |

---

## The data

Scraped from [fbref.com](https://fbref.com), normalized to **per-90** figures where
the source offers that toggle.

| | |
|---|---|
| **Matches** | 2,660 |
| **Seasons** | 7 complete (2017-18 → 2023-24), 380 matches each |
| **Features** | 226 columns |
| **Target** | `golesLocal > golesVisitante` — binary home win |
| **Class balance** | 44.8% home wins |

### Stat families collected

Each is scraped per season, for home and away side:

`defensivas` · `gca` (goal & shot creation) · `pases` · `tipos_pases` ·
`porteria` · `porteria_avanzada` · `posesion` · `tiros` · `sueldos` (wages)

The `sueldos` scraper parses currency strings with regex and strips accents via
NFKD normalization so team names join cleanly across sources.

### Feature assembly

`data_sets/UnificadorDataSets.py` performs 18 left joins — every stat family twice,
once suffixed `_local` and once `_visitante` — keyed on `(Equipo, Temporada)`. Season
labels are normalized first (`2017-18` → `2017-2018`) so the keys actually match.

`scrapping_current_season/DataSetVersus.py` does the same for a single upcoming
fixture, producing one row in the exact shape the model expects.

---

## Modeling

Order matters here: the test split is carved out **before** SMOTE, so no synthetic
samples leak into held-out data.

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

X_train_balanced, y_train_balanced = SMOTE(random_state=42).fit_resample(X_train, y_train)
```

The search space covers layer widths, dropout rates, L2 strength, activations and
optimizer, across five tuning campaigns of increasing depth.

### Tuning search results

Best `val_accuracy` observed per campaign, recovered from the Keras Tuner trial records:

| Campaign | Trials | Best | Median | Architecture |
|---|---|---|---|---|
| `v1` | 10 | 0.697 | 0.685 | 2 layers, no L2 |
| `v2` | 20 | 0.815 | 0.802 | 2 layers + L2 |
| `v3` | 50 | 0.815 | 0.802 | 2 layers + L2 |
| `v4` | 50 | 0.742 | 0.729 | 2 layers + L2, wider search |
| `v5` | 100 | 0.731 | 0.715 | 3 layers + tunable activations |

> **Read these as search scores, not accuracy claims.** The tuner's validation split
> is taken from the SMOTE-balanced training set, so synthetic neighbours can land on
> both sides of the split and inflate the number. The honest metric is
> `model.evaluate(X_test, y_test)` on the untouched 20% hold-out — that cell exists in
> the notebook but its output was not committed. Treat the table as a record of which
> search configuration converged best, nothing more.

Adding L2 regularization (`v1` → `v2`) was the single biggest jump. Going deeper
(`v5`) did not help.

---

## Repo structure

```
scrapping_data/              # Historical scrapers, 2017–2024 (9 stat families + wages)
scrapping_current_season/    # Same families for the live 2024-25 season
data_sets/                   # Historical raw CSVs + UnificadorDataSets.py
current_season_data/         # 2024-25 raw CSVs, plus per-matchday fixtures (j1, j23, j24, j35)
training_model/
└── neuronal_networks/
    ├── first_approach.ipynb # Split → SMOTE → impute → scale → tune → evaluate
    ├── check_columns.ipynb  # Column alignment checks
    ├── soccer_model.h5      # Trained model
    ├── scaler.pkl           # Fitted StandardScaler
    └── imputer.pkl          # Fitted SimpleImputer
data_presentation.ipynb      # Exploratory analysis and plots
merged_all_statistics.txt    # The assembled dataset — 2,660 × 226
```

---

## Running it

```bash
pip install -r requirements.txt
```

Selenium needs a matching ChromeDriver on your `PATH`.

```bash
# Scrape one stat family (historical)
python scrapping_data/ScrappingDatosTiros.py

# Rebuild the merged dataset
cd data_sets && python UnificadorDataSets.py

# Train / evaluate
jupyter notebook training_model/neuronal_networks/first_approach.ipynb
```

---

## Known limitations

These are real and worth stating rather than hiding:

- **Hardcoded absolute paths.** `DataSetVersus.py` and `first_approach.ipynb` read from
  `C:/UABC/...`. They need editing before they run anywhere else.
- **`ScrapBDFutbol.py` imports a missing `Const` module**, so that scraper does not run
  as committed.
- **No held-out metric is committed.** See the tuning caveat above.
- **Team-season aggregates, not match-time state.** Features describe how a team
  performed across a whole season, so a match late in the season is partly described by
  statistics that already include it. A strictly honest setup would use only data
  available before kickoff.
