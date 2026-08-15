# Treatment construction

The core audit uses a 2 x 2 matched design. Each base profile creates four resumes. Only the two lines below change.

| Treatment | Control text | Treatment text |
|---|---|---|
| Education pathway | `Education: Traditional pathway; completed [same credential] through full-time study` | `Education: Non-traditional pathway; completed [same credential] through part-time study` |
| Career continuity | `Employment continuity: Continuous work history; no career break was recorded` | `Employment continuity: Twelve-month career break; return to work was completed` |

Everything else stays fixed within a matched set:

- candidate name;
- target role;
- years of experience;
- credential level and field;
- skills and skills count;
- employer history;
- experience summary;
- quantified achievement;
- formatting and field order.

## Automated checks

`scripts/audit_resume_balance.py` generates all 128 core resumes and checks:

- word count;
- sentence count;
- skills count;
- years of experience;
- quantified-achievement count;
- Flesch reading ease;
- a SHA-256 hash of all non-treatment text.

The build fails if word count, sentence count, skills, experience, quantified achievements, or non-treatment text vary within a matched set. Readability is reported but not forced to be identical because the intended treatment words themselves can change syllable counts.

Run:

```bash
python scripts/audit_resume_balance.py
```

Committed outputs are in `results/design/`.
