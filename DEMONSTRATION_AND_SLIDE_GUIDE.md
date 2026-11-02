# Part 3–4: presentation and experiment guide

## What was actually run
The program `code/epd_batch.cpp` was derived from the user-uploaded `main(1).cpp`. It keeps the original five strategy rules, payoffs, pair counting, `MATCHUP_TRIALS = 100`, MT19937 random generator, `executeGeneration()` and `scalePopulation()` rules, including largest-remainder integer assignment. The plotting code and interactive input are replaced with command-line arguments and per-generation CSV output. The original interactive code is **not** overwritten; a copy is bundled in `code/original_main.cpp`.

We ran **466 headless C++ simulations** in two sweeps: 250 exploratory runs across 25 configurations using 10 seeds, and 216 calibrated runs across 27 configurations using 8 seeds. Primary graphs and summary results use only the **216 calibrated runs**; do not mix their means with the exploratory batch. All 216 calibrated runs used 250 generations, 100 matchup trials per pairing per generation, and 600 individuals. Rounds = 30 unless the round-count experiment varies it. The baseline starts with 120 each of TFT, GT, AC, AD, and Random.

The model is a weak Prisoner's Dilemma, with (CC, CD, DC, DD) payoffs (3,3), (0,5), (5,0), (0,0); it is NOT a classical strict PD. Results are model-specific.

## How to run the headless C++ program
On Linux or another system with a C++17 compiler:

```bash
g++ -std=c++17 -O3 -o epd_batch code/epd_batch.cpp
./epd_batch 101 30 250 0.50 0.00 0.00 120 120 120 120 120 baseline_seed101.csv
```

Arguments, in order: `seed rounds generations alpha error forgiveness TFT GT AC AD Random output.csv`.

On your normal Windows UCRT64 environment, compile the same source using `g++ -std=c++17 -O3 -o epd_batch.exe code/epd_batch.cpp` then use `./epd_batch.exe` with the same parameters. This batch runner has no Matplot++ or GNUplot requirement. `run_experiments.py` automates the parameter sweeps and writes results; edit the executable path or compile it for the host platform first. `make_plots.py` requires pandas and matplotlib if you want to regenerate PNG plots. The user-facing interactive version continues to use Matplot++ and its own prompts.

## Slide 24 — Architecture
Stay on the slide only to explain the pipeline. In VS Code, point to `main()`, `executeGeneration()`, `scalePopulation()` and `plotit()` in the ORIGINAL source. Explain that `plotit()` is only a view, not part of the evolutionary logic.

## Slide 25 — One match
Switch to VS Code. Locate `chooseMove()` and explain each of the five branches. Then show `playGame()`: both strategy states start cooperative; intended moves are selected; errors may flip them; payoffs are added; executed moves update memory; defection triggers Grim Trigger. Mention that forgiveness for TFT is a probabilistic override after observing defection, while for GT it can reset the trigger. Show `payoff()` last.

## Slide 26 — One generation
Stay briefly on the two equations then open `executeGeneration()` and `scalePopulation()`. Point out `N_i × N_j` versus `N_i(N_i−1)/2`, repeated matchup sampling (100 trials), how total fitness is turned into average per-strategy payoff, and the selection factor `(1-alpha) + alpha*(averageFitness/meanFitness)`. Emphasise: weighted counts are integers, assigned by the largest-remainder method; there is no mutation; total N remains exactly constant.

## Slide 27 — Data collection
Show the ORIGINAL `plotit()` in VS Code. Then open `code/epd_batch.cpp` or a real CSV in VS Code. Explain that the batch version only removes Matplot++ and interactive prompts; every generation becomes a CSV row. `% share = strategy count / 600 × 100`.

## Slides 28–30 — Methodology
Explain controlled comparisons. 100 matchup trials are Monte Carlo samples PER matchup, PER generation; eight **whole-simulation seeds** are separate replications. Do not call 100 matchup trials 100 independent population experiments. Highlight the rounding issue: at alpha 0.03 or 0.05, the 600-person counts can remain frozen even while underlying payoffs differ. This is a discretisation artefact that must not be mislabelled an evolutionary equilibrium. The calibrated comparisons use alpha=0.50, and separately sweep alpha.

## Slide 31 — Live demo: clean baseline
Using ORIGINAL interactive executable, enter values in this order:

```
seed: 101
rounds: 30
generations: 250
Tit for Tat: 120
Grim Trigger: 120
Always Cooperate: 120
Always Defect: 120
Random: 120
alpha: 0.50
error: 0.00
forgiveness: 0.00
```

Describe the curves; the aggregate final mean across eight calibrated seeds was TFT 32.8%, GT 38.6%, AC 28.0%, AD 0.2%, Random 0.5%. Do not claim one strategy universally wins.

## Slide 32 — Live demo: introduce an error
Run twice with seed 101, rounds 30, generations 250, population 120 each, alpha .50, forgiveness 0. Change ONLY error: 0.00, then 0.10. Discuss why accidental defections can reshape trajectories. The eight-seed means at error 0.10 were GT 84.3% and AC 14.7%. If time permits, show error 0.20: TFT returns to a substantial share in this model; effects are not monotonic.

## Slide 33 — Live demo: forgiveness
Run three times with seed 101, rounds 30, generations 250, population 120 each, alpha .50, error .08. Change forgiveness ONLY: 0.00, then 0.25, then 0.50. At forgiveness .25 the eight-seed mean for TFT was 52.0%; at forgiveness .50 AD was 99.3%. Discuss the tradeoff between recovery from mistakes and exploitability. This is a particularly strong demo.

### Live demo logistics
For each run, write the parameter combination in a text file beforehand so you can enter it accurately. Capture a screenshot of the graph before closing the original Matplot++ window, and allow the graph window to appear before continuing your narration. If the plotting backend fails, display the matching precomputed PNG and explain that the C++ batch runner saved identical-model histories, not that the GUI succeeded.

## Slides 34–38 — Plots to insert
Each slide intentionally contains a large blank rectangular plot area. Insert the named PNG and crop it to fit INSIDE the rectangle, preserving plot titles and axes. These source images are included in `plots/`.

| Slide | Insert this exact file | Intended interpretation |
| --- | --- | --- |
| 34 | `34_baseline_seed101.png` | Single representative seed, not an average trajectory; α=.50, error=0, forgiveness=0. |
| 35 | `35_error_sweep.png` | Eight-seed means for final shares; error 0, .01, .02, .05, .10, .20; α=.50, forgiveness=0. |
| 36 | `36_forgiveness_sweep.png` | Eight-seed means; error=.08, α=.50; forgiveness 0 to .75; observe non-monotonic shifts. |
| 37 | `37_selection_sweep.png` | Eight-seed means; error=.04, forgiveness=.05; note frozen states at low α due to rounding. |
| 38 | `38_initial_conditions.png` | Eight-seed means; α=.50, error=.04, forgiveness=.05; equal vs three skewed starting mixes. |

**On speaking about error bands:** shading is one sample standard deviation across the eight random seeds, not a 95% confidence interval. For the baseline plot, the single seed is a worked example and has no error bands.

## Principal calibrated findings, final generation (mean ± SD, percentage points, 8 seeds)

- Baseline (α=.50, error=0, forgiveness=0): TFT **32.8±0.1**, GT **38.6±0.1**, AC **28.0±0.1**, AD **0.2±0.1**, Random **0.5±0.1**.
- Error 0.10 (α=.50, forgiveness=0): GT **84.3±0.6**, AC **14.7±0.6**.
- Error 0.20 (α=.50, forgiveness=0): TFT **42.4±1.1**, GT **6.3±1.2**, AC **28.6±3.8**, Random **21.2±4.4**.
- Forgiveness 0.25 (error=.08, α=.50): TFT **52.0±4.5**, AC **22.0±0.6**, Random **15.3±2.0**, AD **2.4±0.9**.
- Forgiveness 0.50 (error=.08, α=.50): AD **99.3±0.0**.
- Selection α=.03 or α=.05 (error=.04, forgiveness=.05): all five stayed at **20.0%**, indicating rounding lock-in, NOT equivalent strategy payoffs.
- With increasing rounds from 20 to 50 (α=.50, error=.04, forgiveness=.05), the final mean AD share increased from **41.8%** to **83.5%** in this specific model.

## Important methodological qualifications
1. The program estimates the expected payoff for each strategy pairing from 100 representative repeated games and scales by the number of such pairings. It does not simulate every one of the approximately 180,000 individual pairs independently.
2. Strategy state resets for each repeated game, not across generations. Grim Trigger memory is only within the current match.
3. If any strategy reaches exactly zero individuals, it cannot reappear: there is no mutation or immigration.
4. Fixed total population + largest remainder creates finite-size rounding thresholds.
5. The random seed controls pseudorandom draws; results are reproducible within this compiled implementation, but exact pseudorandom distribution sequences may differ by C++ standard library implementation.
6. Sampling variability and batch computation should not be sold as a mathematical proof or a universal prescription for human behaviour.
7. The baseline and outcomes above were recorded from actual C++ executions. They were not invented to fill the presentation.
