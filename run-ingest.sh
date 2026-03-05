#!/bin/bash -xe
# Three-pass medlit ingestion: Pass 1 (LLM extract) → Pass 2 (dedup) → Pass 3 (build kgbundle).
# To ADD more papers to an existing bundle: keep pass1_bundles/ and medlit_merged/ from the first run.
# Then run Pass 1 with --output-dir pass1_bundles and --papers "NEW_PAPER1.xml,NEW_PAPER2.xml" (skips existing),
# then re-run Pass 2 (same --output-dir medlit_merged, same --synonym-cache), then re-run Pass 3.
# See examples/medlit/INGESTION.md § "Adding more papers to an existing bundle".

# a nice short paper
# PAPER="PMC12771675.xml"

# a bit longer
# PAPER="PMC12756687.xml"

# five papers
# PAPER="PMC12757875.xml,PMC12784210.xml,PMC12784773.xml,PMC12788344.xml,PMC12780394.xml"

# ten papers
# PAPER="PMC12757875.xml,PMC12784210.xml,PMC12784773.xml,PMC12788344.xml,PMC12780394.xml,PMC12757429.xml,PMC12784249.xml,PMC12764803.xml,PMC12783088.xml,PMC12775561.xml"

# twenty papers
# PAPER="PMC12757875.xml,PMC12784210.xml,PMC12784773.xml,PMC12788344.xml,PMC12780394.xml,PMC12757429.xml,PMC12784249.xml,PMC12764803.xml,PMC12783088.xml,PMC12775561.xml,PMC12766194.xml,PMC12750049.xml,PMC12758042.xml,PMC12780067.xml,PMC12785246.xml,PMC12785631.xml,PMC12753587.xml,PMC12754092.xml,PMC12764813.xml,PMC5487382.xml"

# Endocrinology/Cushing's papers
# PAPER="PMC11560769.xml,PMC11779774.xml,PMC11548364.xml,PMC2386281.xml,PMC12187266.xml,PMC4374115.xml,PMC11128938.xml,PMC11685751.xml,PMC12035109.xml,PMC12055610.xml"

# For reference, here's what each one is:

# | PMC ID | Title / Topic | Year |
# |---|---|---|
# | PMC11560769 | Editorial: Insights in Cushing's Syndrome and Disease, Vol. II | 2024 |
# | PMC11779774 | Medical management pathways for Cushing's disease in pituitary tumor centers | 2025 |
# | PMC11548364 | New Trends in Treating Cushing's Disease (novel therapeutics review) | 2024 |
# | PMC2386281 | Diagnosis of Cushing's Syndrome — Endocrine Society Clinical Practice Guideline | 2008 |
# | PMC12187266 | Diagnosis of Cushing's syndrome with generalized linear model + mobile app | 2025 |
# | PMC4374115 | Comorbidities in Cushing's disease (cardiovascular, metabolic, QoL) | 2015 |
# | PMC11128938 | ACTH-dependent Cushing syndrome: desmopressin / petrosal sinus case report | 2024 |
# | PMC11685751 | Pheochromocytoma-induced pseudo-Cushing's syndrome (differential diagnosis) | 2024 |
# | PMC12035109 | Cognitive function and risk factors from prolonged cortisol exposure in CD | 2025 |
# | PMC12055610 | Osilodrostat for Cushing syndrome (new steroidogenesis inhibitor) | 2025 |
# PAPER="PMC11560769.xml,PMC11779774.xml,PMC11548364.xml,PMC2386281.xml,PMC12187266.xml,PMC4374115.xml,PMC11128938.xml,PMC11685751.xml,PMC12035109.xml,PMC12055610.xml"
# PAPER="PMC11560769.xml,PMC11779774.xml,PMC11548364.xml,PMC2386281.xml,PMC12187266.xml"

# Good topical spread — covers diagnosis, medical management, novel drugs, comorbidities, cognitive effects, edge cases (pregnancy, pseudo-Cushing's), and the classic guideline paper. All are open-access CC-licensed, so XML should be available via the PMC OA FTP or API.

# adrenal stuff
# PAPER="PMC10667925.xml,PMC4880116.xml,PMC11795198.xml"
# other stuff
# PAPER="PMC6727998.xml,PMC4192497.xml,PMC4480270.xml,PMC3607291.xml,PMC4398279.xml,PMC5579818.xml"

# smorgasbord, 40 papers across oncology and endocrinology
PAPER="PMC10667925.xml,PMC11128938.xml,PMC11548364.xml,PMC11560769.xml,PMC11685751.xml,PMC11779774.xml,PMC11795198.xml,PMC12035109.xml,PMC12055610.xml,PMC12187266.xml,PMC12750049.xml,PMC12753587.xml,PMC12754092.xml,PMC12757429.xml,PMC12757875.xml,PMC12758042.xml,PMC12764803.xml,PMC12764813.xml,PMC12766194.xml,PMC12775561.xml,PMC12780067.xml,PMC12780394.xml,PMC12783088.xml,PMC12784210.xml,PMC12784249.xml,PMC12784773.xml,PMC12785246.xml,PMC12785631.xml,PMC12788344.xml,PMC2386281.xml,PMC3607291.xml,PMC4192497.xml,PMC4374115.xml,PMC4398279.xml,PMC4480270.xml,PMC4880116.xml,PMC5487382.xml,PMC5579818.xml,PMC6727998.xml"

(
cd examples/medlit/pmc_xmls
for PMC in $(echo $PAPER | tr ',' '\n' | sed 's/\.xml//'); do
    [ -f "${PMC}.xml" ] && continue
    curl -o "${PMC}.xml" \
      "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=${PMC}&rettype=xml&retmode=xml"
    sleep 0.5
done
)

# DEBUG=
DEBUG="--debug"
TIMEOUT=1000

# Clean up first
git rm -rf medlit_bundle/* medlit_merged/* pass1_bundles/* pass1_vocab/*
git commit -m 'start fresh'

# Legacy ingest.py removed (PLAN10). Use four-pass pipeline: 1a (vocab) → 1b (extract) → 2 (dedup) → 3 (bundle).

# Pass 1a: fast vocabulary extraction across all papers
uv run python -m examples.medlit.scripts.pass1a_vocab \
  --input-dir examples/medlit/pmc_xmls \
  --output-dir pass1_vocab \
  --llm-backend anthropic \
  --papers $PAPER

# Pass 1b: full extraction with vocabulary context
uv run python -m examples.medlit.scripts.pass1_extract \
  --input-dir examples/medlit/pmc_xmls \
  --output-dir pass1_bundles \
  --llm-backend anthropic \
  --vocab-file pass1_vocab/vocab.json \
  --papers $PAPER

# Pass 2: dedup, seeded with pass1a synonym cache
uv run python -m examples.medlit.scripts.pass2_dedup \
  --bundle-dir pass1_bundles \
  --output-dir medlit_merged \
  --synonym-cache pass1_vocab/seeded_synonym_cache.json

uv run python -m examples.medlit.scripts.pass3_build_bundle \
  --merged-dir medlit_merged \
  --bundles-dir pass1_bundles \
  --output-dir medlit_bundle
