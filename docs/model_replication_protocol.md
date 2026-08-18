# Model-version replication protocol

The confirmatory result belongs to one exact model snapshot. A second Claude model or later Claude snapshot is a replication, not part of the primary analysis. The completed Gemini feasibility pilot is not treated as this replication because it was operational and quota-limited rather than an inferential matched-sample run.

## Sequence

1. Complete the prospectively code-locked `claude-sonnet-4-6` primary run.
2. Preserve the raw primary output, run manifest, and `claude_confirmatory_design_lock.json` without overwriting them.
3. Prospectively record and hash-lock the replication model ID and date before its first request.
4. Reuse the same 128 resumes, primary prompt, temperature, five repetitions, response schema, randomization method, stopping rule, and analysis code.
5. Save the replication to a separate directory and report it beside, not pooled into, the primary estimate.

## Comparison

Report the treatment estimates, 95% confidence intervals, standardized effects, recommendation probability changes, refusal rates, and repeated-call variance for both model snapshots. A difference in significance is not itself evidence that effects differ. Report a direct model-by-treatment interaction when comparing snapshots.

## Interpretation

Replication can show whether the result transfers across model snapshots. It cannot establish that the same behavior appears across vendors, employers, prompts, or real hiring decisions.
