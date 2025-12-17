# traffic-signal-optimization
# Traffic Signal Timing Optimization

This repository contains the code for a course project on traffic signal timing optimization at a four-leg urban intersection.

## Description
We study an isolated intersection with two compatible phases (North–South and East–West).  
We compare:
- a fixed-cycle analytical baseline inspired by Webster's delay formula,
- a linear programming (LP) approach for green time allocation.

Experiments are conducted on both synthetic scenarios and real traffic demand data from Kaggle.

## Files
- `baseline_webster.py`: analytical delay proxy (Webster-inspired)
- `model_lp.py`: linear programming model for green time optimization
- `experiments.py`: runs all experiments and generates results
- `Metro_Interstate_Traffic_Volume.csv`: Kaggle traffic volume dataset
- `results_summary.csv`: summary of experimental results
- `delay_comparison.png`: baseline vs LP comparison plot

## How to run
```bash
python experiments.py
