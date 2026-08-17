# Claude cross-provider replication protocol

The preregistered primary result belongs to one exact Gemini model snapshot. Claude is the planned cross-provider replication and is analyzed separately from the Gemini primary estimate.

## Sequence

1. Complete the externally preregistered Gemini primary run.
2. Preserve the raw Gemini output, manifests, analysis inputs, and figures without overwriting them.
3. Register the exact Claude model ID, date, and any unavoidable provider-specific API setting before the first Claude request.
4. Reuse the same 128 resumes, treatment assignments, primary prompt, response schema, five repetitions, randomization method, stopping rule, and analysis code.
5. Use the same temperature when supported by the selected Claude model. If the selected model requires a different sampling interface, document that constraint before the first request.
6. Save the Claude replication to a separate directory and report it beside, not pooled into, the Gemini primary estimate.

## Comparison

Report treatment estimates, 95% confidence intervals, standardized effects, recommendation probability changes, refusal and failure rates, and repeated-call variance for both providers.

A difference in statistical significance is not itself evidence that effects differ. Where estimable, report a direct model-by-treatment interaction or an equivalent contrast of treatment effects across providers.

## Interpretation

The replication tests whether the observed pattern transfers from Gemini to Claude under the same experimental structure. Agreement would strengthen evidence that the result is not unique to one provider. Disagreement would identify model-specific behavior that warrants further study.

Neither result establishes employer behavior, unlawful discrimination, model intent, or effects on real applicants.
