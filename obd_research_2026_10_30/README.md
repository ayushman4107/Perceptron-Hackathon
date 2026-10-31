# PoliSee: Research and Evidence

This package supersedes the earlier abstract proposal. Start with the [revised abstract](ABSTRACT.md) and [illustrated PDF](output/pdf/Abstract_with_Evidence.pdf). The PDF contains two abstract pages (including a result plot) a one-page approach/evidence supplement, and the approved architecture on a landscape fourth page. The official brief suggests 600-900 words plus an optional approach page; the abstract text is within that word range. No claim is made that the organizers impose a strict three-page allowance; use the plain text if the submission form controls layout.

## What changed

We tested the previous likelihood extension on full Open Bandit campaign files and developed an exact policy-ratio grouping specialization. The grouping reduces an 80-item top-k comparison to two reward means while allowing item heterogeneity. A predictive-mixture likelihood variant improves on the original item-level method, but a simpler grouped exact-binomial bound wins the principal comparisons. The recommended implementation follows that result.

This is a concrete application extension and empirical contribution. It is not a validated claim to have invented likelihood inference, action grouping, safe policy improvement, or a globally superior OPE algorithm. [Technical derivation and closest prior work](TECHNICAL_DERIVATION.md) explain the distinction.

## Read in this order

1. [Abstract](ABSTRACT.md) / [plain text](ABSTRACT_plain.txt) / [PDF with graphs](output/pdf/Abstract_with_Evidence.pdf).
2. [Measured results and all comparisons](RESULTS_REPORT.md).
3. [Technical derivation, assumptions, and novelty boundary](TECHNICAL_DERIVATION.md).
4. [Frozen primary protocol](PROTOCOL.md) and [exploratory stability protocol](STABILITY_PROTOCOL.md).
5. [Machine-readable claim ledger](results/claim_ledger.json), [real intervals](results/real_intervals.csv), and [synthetic summaries](results/synthetic_summary.csv).

## Main findings

- 6,769,588 real rows processed across four full campaign files; first-position analysis avoids pooling the three slate positions as independent impressions.
- Primary Random/all pilot/certification/reference sizes: 91,674 / 183,450 / 182,881.
- Grouped exact intervals: median width reduction of 82.6% versus the earlier item likelihood, 79.0% versus item KL. Predictive likelihood was not the strongest grouped method.
- Selected top-20 candidate: gain interval [0.0528, 0.2515] CTR percentage points; independent empirical reference 0.2184 points. Do not confuse percentage points with relative percent improvement.
- 8,000 independent synthetic logs, eleven methods, 88,000 method-trial records; sixteen implementation tests passed. Exact methods are conservative; asymmetric Wald failures are not synonymous with false-improvement decisions.
- An additional 100 random splits per campaign are exploratory stability diagnostics, not independent real-world replications. Chronological tests expose limitations; they are not IID coverage tests.

## Small-storage data access

The 160 GB notice on [ZOZO's page](https://research.zozo.com/data.html) concerns SHIFT15M, a different dataset. The OBD ZIP is 412,931,917 bytes (~394 MiB) compressed. Our byte-range downloader fetches only three Random campaign members and BTS/men, totaling ~94 MiB. Streaming conversion creates ~35 MiB of compact arrays without extracting multi-gigabyte CSVs. Dataset binaries, wheels and dependencies are excluded from GitHub.

Data source: Saito, Aihara, Matsutani and Narita, [Open Bandit Dataset and Pipeline](https://arxiv.org/abs/2008.07146), NeurIPS 2021 Datasets and Benchmarks; supplied by ZOZO. The paper describes the release as CC BY 4.0; cite the authors and respect the release terms. Checksums, archive offsets and source metadata are in [data_manifest.json](data/data_manifest.json) and [archive_index.json](data/archive_index.json).

## Reproduce

Use Python 3.12 and an isolated environment. Install `requirements.txt`. The local `.deps` fallback in scripts is optional; normal environment installations work when that directory is absent.

```sh
python -m pip install -r requirements.txt
python download_data.py
python -m unittest test_methods -v
python real_experiment.py
python synthetic_experiment.py
python stability_experiment.py
python reversal_demo.py
python analyze_results.py
python build_submission.py
python validate.py
```

Run commands from this directory. Runners overwrite their saved results. Synthetic execution uses four CPU workers, fixed seeds, and no GPU. Data downloading requires network access; all evaluation after download is local. The evidence package keeps full raw synthetic trial records and source/protocol hashes. Historical provenance manifests are expected to change if you intentionally edit or rerun an experiment.

## What is implemented and what remains

Implemented: dataset conversion and integrity checks, IPS/SNIPS/tabular cross-fitted DR, exact-ratio algebra, confidence constructions, numerical endpoint witnesses, synthetic truth-based testing, real-data held-out comparisons, chronological and block-bootstrap diagnostics, saved graphs, and submission materials.

Planned: an integrated Streamlit interface, general personalized policies, a specified hidden-confounding sensitivity module, and deployment integrations. The certificate assumes identification, stationary independent observations and an appropriate position-wise response model. It is not a user-level causal guarantee or a whole-slate evaluation.

Regenerate the architecture with `python build_architecture.py` before running `python build_submission.py`. Editable SVG, PNG and vector PDF versions are in `figures/06_polisee_architecture.*`.
