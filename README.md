# Live Staffing Calculator

An **Erlang-C based workforce planning tool** built in Python.  
Interactive dashboard which takes inputs like call volume, AHT, SL%, and as output it calculates how many agents are needed every hour.

---

## What It Does
| Input | Output |
|---|---|
| Average Handle Time (AHT) | Peak headcount to roster |
| Service level target (e.g. 80% in 20s) | Per-hour agent breakdown |
| Daily call volume or custom hourly profile | Avg service level, ASA, utilisation |
| Shrinkage % (breaks, training, etc.) | Intraday chart + CSV export |

---

## Key Input Parameters
```python
AHT                  = 240    # Average Handle Time in seconds
SERVICE_LEVEL_TARGET = 80     # Target: answer 80% of calls...
TARGET_ANSWER_TIME   = 20     # ...within 20 seconds
OPERATING_HOURS      = 12     # Contact centre open 12 hours/day
SHRINKAGE            = 0.20   # 20% of agent time lost to breaks etc.

VOLUME_MODE          = 'auto' # 'auto' = bell curve, 'custom' = enter hourly volumes
DAILY_CALLS          = 1200   # Used when VOLUME_MODE = 'auto'
```
---

The calculator uses **Erlang-C queuing theory** the industry standard for call center staffing.

| Formula | Purpose |
|---|---|
| `A = (calls/hr × AHT) / 3600` | Traffic intensity in Erlangs |
| `ErlangC(N, A)` | Call Wait Time |
| `SL = 1 − P(wait) × e^(−(N−A) × T / AHT)` | Service level achieved |
| `ASA = P(wait) × AHT / (N − A)` | Average Speed of Answer |
| `Headcount = ceil(N / (1 − shrinkage))` | Agents to roster |

---

## Output Files
After running, the notebook generates:
- **`staffing_results.csv`**  full intraday table
- **`staffing_chart.png`**  headcount and service level charts

---

## Tech Stack
- Python 3.x
- `pandas` - tabular results
- `matplotlib` - charts
- `math` - Erlang-C formulas (no external queuing library needed)
```
