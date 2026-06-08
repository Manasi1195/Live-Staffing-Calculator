# Live-Staffing-Calculator

An **Erlang-C based workforce planning tool** built in Python.  
Given call volume and service targets, it calculates how many agents you need hour by hour.

---

## What It Does

| Input | Output |
|---|---|
| Average Handle Time (AHT) | Peak headcount to roster |
| Service level target (e.g. 80% in 20s) | Per-hour agent breakdown |
| Daily call volume or custom hourly profile | Avg service level, ASA, utilisation |
| Shrinkage % (breaks, training, etc.) | Intraday chart + CSV export |

---

## How to Run

### 1. Clone the repo
```bash
git clone https://github.com/your-username/contact-center-staffing-calculator.git
cd contact-center-staffing-calculator
```

### 2. Install dependencies
```bash
pip install pandas matplotlib notebook
```

### 3. Open the notebook
```bash
jupyter notebook contact_center_staffing_calculator.ipynb
```

### 4. Change inputs and run all cells
All inputs are in **Section 2** and **Section 3** — edit the values there and hit **Run All**.

---

## Key Parameters

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

## The Maths (in brief)

The calculator uses **Erlang-C queuing theory** the industry standard for call center staffing.

| Formula | Purpose |
|---|---|
| `A = (calls/hr × AHT) / 3600` | Traffic intensity in Erlangs |
| `ErlangC(N, A)` | Probability a caller waits |
| `SL = 1 − P(wait) × e^(−(N−A) × T / AHT)` | Service level achieved |
| `ASA = P(wait) × AHT / (N − A)` | Average Speed of Answer |
| `Headcount = ceil(N / (1 − shrinkage))` | Agents to roster |

A full plain-English walkthrough is included in **Section 9** of the notebook.

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
- `math` - Erlang-C calculation (no external queuing library needed)

---

## Project Structure

```
contact-center-staffing-calculator/
├── contact_center_staffing_calculator.ipynb   # Main notebook
├── staffing_results.csv                       # Generated output (after running)
├── staffing_chart.png                         # Generated chart (after running)
└── README.md
```
