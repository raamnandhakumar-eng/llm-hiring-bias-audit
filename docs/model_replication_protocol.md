# Model-version replication protocol

The confirmatory result belongs to one exact model snapshot. A second model or later snapshot is a replication, not part of the primary analysis.

## Sequence

1. Complete the externally preregistered primary run.
2. Preserve the raw primary output and manifest without overwriting either file.
3. Register the replication model ID and date before its first request.
4. Reuse the same 128 resumes, primary prompt, temperature, five repetitions, response schema, randomization method, stopping rule, and analysis code.
5. Save the replication to a separate directory and report it beside, not pooled into, the primary estimate.

## Comparison

Report the treatment estimates, 95% confidence intervals, standardized effects, recommendation probability changes, refusal rates, and repeated-call variance for both model snapshots. A difference in significance is not itself evidence that effects differ. Report a direct model-by-treatment interaction when comparing snapshots.

## Interpretation

Replication can show whether the result transfers across model snapshots. It cannot establish that the same behavior appears across vendors, employers, prompts, or real hiring decisions.
