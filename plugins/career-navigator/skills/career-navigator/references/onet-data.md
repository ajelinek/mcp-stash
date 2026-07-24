# The bundled O*NET dataset

## Source and license

`src/mcp_stash_career_navigator/data/onet_occupations.json` is a trimmed,
pre-processed extract of the **O*NET 30.3 Database**
(https://www.onetcenter.org/database.html), sponsored by the U.S. Department
of Labor's Employment and Training Administration (USDOL/ETA). O*NET 30.3 is
licensed **CC BY 4.0** — free to use commercially or non-commercially, with
attribution.

Required attribution (include it wherever this data is presented at any
distance from this repo, e.g. in a report generated for a client):

> This product includes information from O\*NET OnLine by the U.S.
> Department of Labor, Employment and Training Administration (USDOL/ETA).
> Used under the CC BY 4.0 license. O\*NET® is a trademark of USDOL/ETA.

## Why a bundled snapshot, not a runtime download

O*NET's own flat files are ~50-100MB and change on USDOL/ETA's own release
schedule (quarterly, major update yearly). This repo's plugin pattern has no
mechanism for a first-run network download (see the root `CLAUDE.md`'s
`uv`-missing hook section: this repo deliberately never auto-fetches
anything unattended onto a client's machine), and a fully offline plugin is
simpler to reason about and test. So the dataset is committed as a single
~700KB JSON file, pre-joined and pre-trimmed to only what the matching logic
in `matching.py` actually uses. It won't reflect O*NET releases after 30.3 —
regenerate it (see below) to pick up a newer release.

## Build process

Joined the following O*NET 30.3 CSV tables
(`https://www.onetcenter.org/dl_files/database/db_30_3_csv/<name>.csv`) on
`O*NET-SOC Code`:

| Table | Used for |
|---|---|
| `occupation_data.csv` | `title`, `description` |
| `career_interest_types.csv` | RIASEC scores — O*NET's "Occupational Interests" scale (`OI`, range 1-7) per Realistic/Investigative/Artistic/Social/Enterprising/Conventional element |
| `job_zones.csv` + `job_zone_reference.csv` | `job_zone` (1-5) + its human-readable label |
| `education.csv` + `education_categories.csv` | `typical_education` — the modal (highest Data Value) "Required Level of Education" category, resolved to its label |
| `essential_skills.csv` | `top_skills` — top 5 skill elements by Importance (`IM`) score |
| `knowledge.csv` | `top_knowledge` — top 5 knowledge elements by Importance (`IM`) score |

Only the **923** occupations (of 1,016 total in `occupation_data.csv`) that
have all six RIASEC elements present in `career_interest_types.csv` were
kept — the rest have no RIASEC data in this O*NET release and can't be
matched on that axis. RIASEC scores are rounded to 2 decimals; `top_codes` is
the 3 highest-scoring letters, descending.

This was a one-time build, not something this repo automates — there's no
script in this plugin that re-runs it. To regenerate against a newer O*NET
release, re-fetch the tables above for the new version number and re-run the
same join/trim logic, then replace
`src/mcp_stash_career_navigator/data/onet_occupations.json` and bump the
plugin's version per the root `CLAUDE.md`'s release steps.

## Field schema (`onet_occupations.json`)

Each entry:

```json
{
  "soc_code": "15-1252.00",
  "title": "Software Developers",
  "description": "...",
  "riasec": {"R": 1.24, "I": 5.41, "A": 1.93, "S": 1.85, "E": 4.42, "C": 5.79},
  "top_codes": ["C", "I", "E"],
  "job_zone": 4,
  "job_zone_label": "Job Zone Four: Considerable Preparation Needed",
  "typical_education": "Bachelor's Degree",
  "top_skills": ["Reading Comprehension", "Active Listening", "..."],
  "top_knowledge": ["Computers and Electronics", "Mathematics", "..."]
}
```

`riasec` values are on O*NET's own 1-7 scale — **not** the same 0-100 scale
`career_update_profile` uses for the *student's* self-reported-by-Claude
scores. The two are never compared numerically; matching uses `top_codes`
rank-order overlap only (see `matching.py`), which sidesteps needing to
reconcile the two scales.
