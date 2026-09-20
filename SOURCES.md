# Data sources

The corpus is **not** versioned in this repository.
`scripts/ingest_sgb5.py` fetches it reproducibly into `data/raw/`, which is
excluded via `.gitignore`.

## SGB V — German statutory health insurance

| | |
|---|---|
| Source | https://www.gesetze-im-internet.de/sgb_5/ |
| Bulk download | https://www.gesetze-im-internet.de/sgb_5/xml.zip (609 KB) |
| Publisher | Federal Ministry of Justice / Federal Office of Justice |
| Provenance | `builddate` in the XML, logged on every ingest |
| Size | 694 provisions, 591 with text → 3,002 chunks |

**Legal basis for use:** under section 5(1) UrhG, statutes carry no copyright
protection. The statutory text is therefore freely usable.

**Caveat:** the *consolidated* version and the XML preparation come from the
Federal Office of Justice together with juris GmbH. The archive is therefore
not redistributed but fetched at runtime. Derived text excerpts in the index
are unaffected.

**Non-official status:** gesetze-im-internet.de provides *non-official*
consolidated versions. Only the *Bundesgesetzblatt* is authoritative. The
agent therefore cites its source in every answer rather than implying
authority.

## Hand-written FAQ layer

`data/faq/faq.yaml` holds hand-written German question–answer pairs, each
referencing a provision. Entirely self-authored, covered by this repository's
MIT licence, and versioned with it.

The content stays German by design — this layer exists to match German user
queries. Only the YAML field names are English.

## Deliberately not used

- **Health insurer FAQs (TK, AOK, Barmer):** copyrighted.
- **gesund.bund.de:** ministry content, no `robots.txt` and no usage licence
  published — no dependable right of reuse.

## Non-goal

No patient data, no personal data, no individual medical advice. The corpus
consists exclusively of public statutory text on entitlements.
