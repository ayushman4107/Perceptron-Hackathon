# Secondary stability analysis

Added after seeing the fixed primary OBD results. This is explicitly exploratory and does not replace the original split or primary comparison.

Repeat random timestamp-group 20/40/40 pilot/certification/reference splits 100 times in each Random campaign, seeds 791000 through 791099. Relearn the same predefined top-k family on each pilot. Use the unchanged inference code and alpha conventions. Summarize interval-width reductions, number of candidates certified, selected k, and selected independent-reference point estimates. These are repeated splits of the SAME finite dataset, not 300 independent real-world datasets; no binomial confidence interval or nominal real-data coverage claim will be attached to their frequency.

The independent reference is accessed only after fitting and policy choice. A selected reference estimate below zero is a noisy disagreement diagnostic, not an observed causal false-positive label. No tuning or new method selection is performed using these splits. The grouped exact procedure is already the recommended simple implementation based on the initial comparison; this study checks its stability.
