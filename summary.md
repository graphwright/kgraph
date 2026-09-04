# Project Summary

## Contents

- [CLAUDE.md](#user-content-claudemd)
- [CONCURRENCY.md](#user-content-concurrencymd)
- [OPERATIONS.md](#user-content-operationsmd)
- [README.md](#user-content-readmemd)
- [TODO.md](#user-content-todomd)
- [bfsql.md](#user-content-bfsqlmd)
- [docs/adapting-to-your-domain.md](#user-content-docsadapting-to-your-domainmd)
- [docs/architecture.md](#user-content-docsarchitecturemd)
- [docs/books.md](#user-content-docsbooksmd)
- [docs/canonical-ids-and-entity-resolution.md](#user-content-docscanonical-ids-and-entity-resolutionmd)
- [docs/contributing.md](#user-content-docscontributingmd)
- [docs/deployment-and-operations.md](#user-content-docsdeployment-and-operationsmd)
- [docs/examples/medlit.md](#user-content-docsexamplesmedlitmd)
- [docs/examples/sherlock.md](#user-content-docsexamplessherlockmd)
- [docs/identity/canonical-ids.md](#user-content-docsidentitycanonical-idsmd)
- [docs/identity/deduplication.md](#user-content-docsidentitydeduplicationmd)
- [docs/index.md](#user-content-docsindexmd)
- [docs/ingestion/chunking.md](#user-content-docsingestionchunkingmd)
- [docs/ingestion/error-handling.md](#user-content-docsingestionerror-handlingmd)
- [docs/ingestion/pipeline.md](#user-content-docsingestionpipelinemd)
- [docs/llm-integration/embeddings.md](#user-content-docsllm-integrationembeddingsmd)
- [docs/llm-integration/extraction-prompts.md](#user-content-docsllm-integrationextraction-promptsmd)
- [docs/llm-integration/mcp-server.md](#user-content-docsllm-integrationmcp-servermd)
- [docs/llm-integration/mcp-troubleshooting.md](#user-content-docsllm-integrationmcp-troubleshootingmd)
- [docs/llm-integration/querying.md](#user-content-docsllm-integrationqueryingmd)
- [docs/manifesto.md](#user-content-docsmanifestomd)
- [docs/microservices-runtime.md](#user-content-docsmicroservices-runtimemd)
- [docs/overview.md](#user-content-docsoverviewmd)
- [docs/pipeline.md](#user-content-docspipelinemd)
- [docs/schema-design-guide.md](#user-content-docsschema-design-guidemd)
- [docs/schema/adapting-to-your-domain.md](#user-content-docsschemaadapting-to-your-domainmd)
- [docs/schema/schema-design-guide.md](#user-content-docsschemaschema-design-guidemd)
- [docs/storage-and-export.md](#user-content-docsstorage-and-exportmd)
- [docs/trust/conflicting-claims.md](#user-content-docstrustconflicting-claimsmd)
- [docs/trust/provenance.md](#user-content-docstrustprovenancemd)
- [identity-server/domain_stub/__init__.py](#user-content-identity-serverdomainstubinitpy)
- [identity-server/domain_stub/app.py](#user-content-identity-serverdomainstubapppy)
- [identity-server/identity_server/__init__.py](#user-content-identity-serveridentityserverinitpy)
- [identity-server/identity_server/app.py](#user-content-identity-serveridentityserverapppy)
- [identity-server/identity_server/cache.py](#user-content-identity-serveridentityservercachepy)
- [identity-server/identity_server/core.py](#user-content-identity-serveridentityservercorepy)
- [identity-server/identity_server/database.py](#user-content-identity-serveridentityserverdatabasepy)
- [identity-server/identity_server/db_models.py](#user-content-identity-serveridentityserverdbmodelspy)
- [identity-server/identity_server/domain_client.py](#user-content-identity-serveridentityserverdomainclientpy)
- [identity-server/identity_server/models.py](#user-content-identity-serveridentityservermodelspy)
- [identity-server/identity_server/routers/__init__.py](#user-content-identity-serveridentityserverroutersinitpy)
- [identity-server/identity_server/routers/dump.py](#user-content-identity-serveridentityserverroutersdumppy)
- [identity-server/identity_server/routers/identity.py](#user-content-identity-serveridentityserverroutersidentitypy)
- [identity-server/tests/__init__.py](#user-content-identity-servertestsinitpy)
- [identity-server/tests/conftest.py](#user-content-identity-servertestsconftestpy)
- [identity-server/tests/test_cache.py](#user-content-identity-serverteststestcachepy)
- [identity-server/tests/test_core.py](#user-content-identity-serverteststestcorepy)
- [identity-server/tests/test_domain_client.py](#user-content-identity-serverteststestdomainclientpy)
- [identity-server/tests/test_dump.py](#user-content-identity-serverteststestdumppy)
- [kgbundle/kgbundle/__init__.py](#user-content-kgbundlekgbundleinitpy)
- [kgbundle/kgbundle/models.py](#user-content-kgbundlekgbundlemodelspy)
- [kgbundle/tests/test_models.py](#user-content-kgbundleteststestmodelspy)
- [kgraph/__init__.py](#user-content-kgraphinitpy)
- [kgraph/builders.py](#user-content-kgraphbuilderspy)
- [kgraph/canonical_id/__init__.py](#user-content-kgraphcanonicalidinitpy)
- [kgraph/canonical_id/helpers.py](#user-content-kgraphcanonicalidhelperspy)
- [kgraph/canonical_id/json_cache.py](#user-content-kgraphcanonicalidjsoncachepy)
- [kgraph/canonical_id/lookup.py](#user-content-kgraphcanonicalidlookuppy)
- [kgraph/canonical_id/models.py](#user-content-kgraphcanonicalidmodelspy)
- [kgraph/clock.py](#user-content-kgraphclockpy)
- [kgraph/context.py](#user-content-kgraphcontextpy)
- [kgraph/export.py](#user-content-kgraphexportpy)
- [kgraph/ingest.py](#user-content-kgraphingestpy)
- [kgraph/pipeline/__init__.py](#user-content-kgraphpipelineinitpy)
- [kgraph/pipeline/caching.py](#user-content-kgraphpipelinecachingpy)
- [kgraph/pipeline/embedding.py](#user-content-kgraphpipelineembeddingpy)
- [kgraph/pipeline/interfaces.py](#user-content-kgraphpipelineinterfacespy)
- [kgraph/pipeline/llm_client.py](#user-content-kgraphpipelinellmclientpy)
- [kgraph/pipeline/ollama_embedding.py](#user-content-kgraphpipelineollamaembeddingpy)
- [kgraph/pipeline/pass1_llm.py](#user-content-kgraphpipelinepass1llmpy)
- [kgraph/pipeline/streaming.py](#user-content-kgraphpipelinestreamingpy)
- [kgraph/pipeline/synonym_cache.py](#user-content-kgraphpipelinesynonymcachepy)
- [kgraph/pprint_logging.py](#user-content-kgraphpprintloggingpy)
- [kgraph/progress.py](#user-content-kgraphprogresspy)
- [kgraph/promotion.py](#user-content-kgraphpromotionpy)
- [kgraph/provenance.py](#user-content-kgraphprovenancepy)
- [kgraph/query/__init__.py](#user-content-kgraphqueryinitpy)
- [kgraph/stage_models.py](#user-content-kgraphstagemodelspy)
- [kgraph/storage/__init__.py](#user-content-kgraphstorageinitpy)
- [kgraph/storage/memory.py](#user-content-kgraphstoragememorypy)
- [kgraph/templates/__init__.py](#user-content-kgraphtemplatesinitpy)
- [kgraph/templates/render.py](#user-content-kgraphtemplatesrenderpy)
- [kgschema/kgschema/__init__.py](#user-content-kgschemakgschemainitpy)
- [kgschema/kgschema/canonical_id.py](#user-content-kgschemakgschemacanonicalidpy)
- [kgschema/kgschema/document.py](#user-content-kgschemakgschemadocumentpy)
- [kgschema/kgschema/domain.py](#user-content-kgschemakgschemadomainpy)
- [kgschema/kgschema/entity.py](#user-content-kgschemakgschemaentitypy)
- [kgschema/kgschema/identity.py](#user-content-kgschemakgschemaidentitypy)
- [kgschema/kgschema/promotion.py](#user-content-kgschemakgschemapromotionpy)
- [kgschema/kgschema/relationship.py](#user-content-kgschemakgschemarelationshippy)
- [kgschema/kgschema/spec.py](#user-content-kgschemakgschemaspecpy)
- [kgschema/kgschema/storage.py](#user-content-kgschemakgschemastoragepy)
- [kgserver/domain_spec.py](#user-content-kgserverdomainspecpy)
- [kgserver/index.md](#user-content-kgserverindexmd)
- [kgserver/mcp_main.py](#user-content-kgservermcpmainpy)
- [kgserver/mcp_server/__init__.py](#user-content-kgservermcpserverinitpy)
- [kgserver/mcp_server/ingest_worker.py](#user-content-kgservermcpserveringestworkerpy)
- [kgserver/mcp_server/server.py](#user-content-kgservermcpserverserverpy)
- [kgserver/pipeline_interface.py](#user-content-kgserverpipelineinterfacepy)
- [kgserver/pipeline_loader.py](#user-content-kgserverpipelineloaderpy)
- [kgserver/query/__init__.py](#user-content-kgserverqueryinitpy)
- [kgserver/query/bundle_loader.py](#user-content-kgserverquerybundleloaderpy)
- [kgserver/query/graph_traversal.py](#user-content-kgserverquerygraphtraversalpy)
- [kgserver/query/graphql_examples.py](#user-content-kgserverquerygraphqlexamplespy)
- [kgserver/query/graphql_schema.py](#user-content-kgserverquerygraphqlschemapy)
- [kgserver/query/routers/graph_api.py](#user-content-kgserverqueryroutersgraphapipy)
- [kgserver/query/routers/graphiql_custom.py](#user-content-kgserverqueryroutersgraphiqlcustompy)
- [kgserver/query/routers/rest_api.py](#user-content-kgserverqueryroutersrestapipy)
- [kgserver/query/routers/subgraph_api.py](#user-content-kgserverqueryrouterssubgraphapipy)
- [kgserver/query/server.py](#user-content-kgserverqueryserverpy)
- [kgserver/query/storage_factory.py](#user-content-kgserverquerystoragefactorypy)
- [kgserver/query/subgraph.py](#user-content-kgserverquerysubgraphpy)
- [kgserver/storage/__init__.py](#user-content-kgserverstorageinitpy)
- [kgserver/storage/backends/__init__.py](#user-content-kgserverstoragebackendsinitpy)
- [kgserver/storage/backends/identity.py](#user-content-kgserverstoragebackendsidentitypy)
- [kgserver/storage/backends/postgres.py](#user-content-kgserverstoragebackendspostgrespy)
- [kgserver/storage/backends/sqlite.py](#user-content-kgserverstoragebackendssqlitepy)
- [kgserver/storage/interfaces.py](#user-content-kgserverstorageinterfacespy)
- [kgserver/storage/models/__init__.py](#user-content-kgserverstoragemodelsinitpy)
- [kgserver/storage/models/bundle.py](#user-content-kgserverstoragemodelsbundlepy)
- [kgserver/storage/models/bundle_evidence.py](#user-content-kgserverstoragemodelsbundleevidencepy)
- [kgserver/storage/models/entity.py](#user-content-kgserverstoragemodelsentitypy)
- [kgserver/storage/models/ingest_job.py](#user-content-kgserverstoragemodelsingestjobpy)
- [kgserver/storage/models/mention.py](#user-content-kgserverstoragemodelsmentionpy)
- [kgserver/storage/models/relationship.py](#user-content-kgserverstoragemodelsrelationshippy)
- [kgserver/tests/conftest.py](#user-content-kgservertestsconftestpy)
- [kgserver/tests/test_bfs_subgraph.py](#user-content-kgserverteststestbfssubgraphpy)
- [kgserver/tests/test_bundle_loader.py](#user-content-kgserverteststestbundleloaderpy)
- [kgserver/tests/test_graph_api.py](#user-content-kgserverteststestgraphapipy)
- [kgserver/tests/test_graph_viz_theme.py](#user-content-kgserverteststestgraphvizthemepy)
- [kgserver/tests/test_graphql_schema.py](#user-content-kgserverteststestgraphqlschemapy)
- [kgserver/tests/test_mcp_graphql_tool.py](#user-content-kgserverteststestmcpgraphqltoolpy)
- [kgserver/tests/test_rest_api.py](#user-content-kgserverteststestrestapipy)
- [kgserver/tests/test_storage_backends.py](#user-content-kgserverteststeststoragebackendspy)
- [kgserver/tests/test_storage_factory.py](#user-content-kgserverteststeststoragefactorypy)
- [kgserver/tests/test_storage_provenance.py](#user-content-kgserverteststeststorageprovenancepy)
- [kgserver/tests/test_subgraph_api.py](#user-content-kgserverteststestsubgraphapipy)
- [medlit/domain_service/app.py](#user-content-medlitdomainserviceapppy)
- [medlit/domain_service/authority.py](#user-content-medlitdomainserviceauthoritypy)
- [medlit/domain_service/models.py](#user-content-medlitdomainservicemodelspy)
- [medlit/domain_service/survivor.py](#user-content-medlitdomainservicesurvivorpy)
- [medlit/domain_service/synonym_criteria.py](#user-content-medlitdomainservicesynonymcriteriapy)
- [medlit/domain_service/tests/test_app.py](#user-content-medlitdomainserviceteststestapppy)
- [medlit/domain_service/tests/test_survivor.py](#user-content-medlitdomainserviceteststestsurvivorpy)
- [medlit/domain_service/tests/test_synonym_criteria.py](#user-content-medlitdomainserviceteststestsynonymcriteriapy)
- [medlit/medlit/__init__.py](#user-content-medlitmedlitinitpy)
- [medlit/medlit/bundle_models.py](#user-content-medlitmedlitbundlemodelspy)
- [medlit/medlit/documents.py](#user-content-medlitmedlitdocumentspy)
- [medlit/medlit/domain.py](#user-content-medlitmedlitdomainpy)
- [medlit/medlit/domain_spec.py](#user-content-medlitmedlitdomainspecpy)
- [medlit/medlit/entities.py](#user-content-medlitmedlitentitiespy)
- [medlit/medlit/pipeline/__init__.py](#user-content-medlitmedlitpipelineinitpy)
- [medlit/medlit/pipeline/authority_lookup.py](#user-content-medlitmedlitpipelineauthoritylookuppy)
- [medlit/medlit/pipeline/bundle_builder.py](#user-content-medlitmedlitpipelinebundlebuilderpy)
- [medlit/medlit/pipeline/canonical_urls.py](#user-content-medlitmedlitpipelinecanonicalurlspy)
- [medlit/medlit/pipeline/config.py](#user-content-medlitmedlitpipelineconfigpy)
- [medlit/medlit/pipeline/dedup.py](#user-content-medlitmedlitpipelinededuppy)
- [medlit/medlit/pipeline/mentions.py](#user-content-medlitmedlitpipelinementionspy)
- [medlit/medlit/pipeline/ner_extractor.py](#user-content-medlitmedlitpipelinenerextractorpy)
- [medlit/medlit/pipeline/parser.py](#user-content-medlitmedlitpipelineparserpy)
- [medlit/medlit/pipeline/pmc_chunker.py](#user-content-medlitmedlitpipelinepmcchunkerpy)
- [medlit/medlit/pipeline/pmc_streaming.py](#user-content-medlitmedlitpipelinepmcstreamingpy)
- [medlit/medlit/pipeline/provenance_expansion.py](#user-content-medlitmedlitpipelineprovenanceexpansionpy)
- [medlit/medlit/pipeline/relationships.py](#user-content-medlitmedlitpipelinerelationshipspy)
- [medlit/medlit/pipeline/resolve.py](#user-content-medlitmedlitpipelineresolvepy)
- [medlit/medlit/pipeline/utils.py](#user-content-medlitmedlitpipelineutilspy)
- [medlit/medlit/promotion.py](#user-content-medlitmedlitpromotionpy)
- [medlit/medlit/relationships.py](#user-content-medlitmedlitrelationshipspy)
- [medlit/medlit/scripts/__init__.py](#user-content-medlitmedlitscriptsinitpy)
- [medlit/medlit/scripts/build_bundle.py](#user-content-medlitmedlitscriptsbuildbundlepy)
- [medlit/medlit/scripts/extract.py](#user-content-medlitmedlitscriptsextractpy)
- [medlit/medlit/scripts/fetch_vocab.py](#user-content-medlitmedlitscriptsfetchvocabpy)
- [medlit/medlit/scripts/ingest.py](#user-content-medlitmedlitscriptsingestpy)
- [medlit/medlit/scripts/parse_pmc_xml.py](#user-content-medlitmedlitscriptsparsepmcxmlpy)
- [medlit/medlit/vocab.py](#user-content-medlitmedlitvocabpy)
- [medlit/medlit_schema/__init__.py](#user-content-medlitmedlitschemainitpy)
- [medlit/medlit_schema/base.py](#user-content-medlitmedlitschemabasepy)
- [medlit/medlit_schema/document.py](#user-content-medlitmedlitschemadocumentpy)
- [medlit/medlit_schema/domain.py](#user-content-medlitmedlitschemadomainpy)
- [medlit/medlit_schema/entity.py](#user-content-medlitmedlitschemaentitypy)
- [medlit/medlit_schema/relationship.py](#user-content-medlitmedlitschemarelationshippy)
- [medlit/pipeline.py](#user-content-medlitpipelinepy)
- [medlit/tests/__init__.py](#user-content-medlittestsinitpy)
- [medlit/tests/conftest.py](#user-content-medlittestsconftestpy)
- [medlit/tests/test_authority_lookup.py](#user-content-medlitteststestauthoritylookuppy)
- [medlit/tests/test_build_bundle.py](#user-content-medlitteststestbuildbundlepy)
- [medlit/tests/test_dedup.py](#user-content-medlitteststestdeduppy)
- [medlit/tests/test_entity_normalization.py](#user-content-medlitteststestentitynormalizationpy)
- [medlit/tests/test_extract.py](#user-content-medlitteststestextractpy)
- [medlit/tests/test_ner_extractor.py](#user-content-medlitteststestnerextractorpy)
- [medlit/tests/test_promotion_lookup.py](#user-content-medlitteststestpromotionlookuppy)
- [medlit/tests/test_provenance_expansion.py](#user-content-medlitteststestprovenanceexpansionpy)
- [medlit/tests/test_two_pass_ingestion.py](#user-content-medlitteststesttwopassingestionpy)
- [proc.py](#user-content-procpy)
- [scripts/build_code_reference.py](#user-content-scriptsbuildcodereferencepy)
- [sherlock/README.md](#user-content-sherlockreadmemd)
- [sherlock/sherlock/__init__.py](#user-content-sherlocksherlockinitpy)
- [sherlock/sherlock/bundle_models.py](#user-content-sherlocksherlockbundlemodelspy)
- [sherlock/sherlock/documents.py](#user-content-sherlocksherlockdocumentspy)
- [sherlock/sherlock/domain.py](#user-content-sherlocksherlockdomainpy)
- [sherlock/sherlock/domain_spec.py](#user-content-sherlocksherlockdomainspecpy)
- [sherlock/sherlock/entities.py](#user-content-sherlocksherlockentitiespy)
- [sherlock/sherlock/pipeline/__init__.py](#user-content-sherlocksherlockpipelineinitpy)
- [sherlock/sherlock/pipeline/bundle_builder.py](#user-content-sherlocksherlockpipelinebundlebuilderpy)
- [sherlock/sherlock/pipeline/dedup.py](#user-content-sherlocksherlockpipelinededuppy)
- [sherlock/sherlock/pipeline/extractor.py](#user-content-sherlocksherlockpipelineextractorpy)
- [sherlock/sherlock/pipeline/parser.py](#user-content-sherlocksherlockpipelineparserpy)
- [sherlock/sherlock/promotion.py](#user-content-sherlocksherlockpromotionpy)
- [sherlock/sherlock/relationships.py](#user-content-sherlocksherlockrelationshipspy)
- [sherlock/sherlock/scripts/__init__.py](#user-content-sherlocksherlockscriptsinitpy)
- [sherlock/sherlock/scripts/build_bundle.py](#user-content-sherlocksherlockscriptsbuildbundlepy)
- [sherlock/sherlock/scripts/extract.py](#user-content-sherlocksherlockscriptsextractpy)
- [sherlock/sherlock/scripts/ingest.py](#user-content-sherlocksherlockscriptsingestpy)
- [sherlock/tests/conftest.py](#user-content-sherlocktestsconftestpy)
- [sherlock/tests/test_bundle.py](#user-content-sherlockteststestbundlepy)
- [sherlock/tests/test_bundle_models.py](#user-content-sherlockteststestbundlemodelspy)
- [sherlock/tests/test_dedup.py](#user-content-sherlockteststestdeduppy)
- [sherlock/tests/test_domain_spec.py](#user-content-sherlockteststestdomainspecpy)
- [sherlock/tests/test_parser.py](#user-content-sherlockteststestparserpy)
- [sherlock_design.md](#user-content-sherlockdesignmd)
- [summarize_codebase.py](#user-content-summarizecodebasepy)
- [tests/__init__.py](#user-content-testsinitpy)
- [tests/conftest.py](#user-content-testsconftestpy)
- [tests/test_build_code_reference.py](#user-content-teststestbuildcodereferencepy)
- [tests/test_caching.py](#user-content-teststestcachingpy)
- [tests/test_canonical_id.py](#user-content-teststestcanonicalidpy)
- [tests/test_entities.py](#user-content-teststestentitiespy)
- [tests/test_export.py](#user-content-teststestexportpy)
- [tests/test_git_hash.py](#user-content-teststestgithashpy)
- [tests/test_ingestion.py](#user-content-teststestingestionpy)
- [tests/test_logging.py](#user-content-teststestloggingpy)
- [tests/test_pass1_llm.py](#user-content-teststestpass1llmpy)
- [tests/test_pipeline_integration.py](#user-content-teststestpipelineintegrationpy)
- [tests/test_progress_tracker.py](#user-content-teststestprogresstrackerpy)
- [tests/test_promotion_merge.py](#user-content-teststestpromotionmergepy)
- [tests/test_provenance.py](#user-content-teststestprovenancepy)
- [tests/test_relationships.py](#user-content-teststestrelationshipspy)
- [tests/test_streaming.py](#user-content-teststeststreamingpy)

---

<span id="user-content-claudemd"></span>

# CLAUDE.md

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Knowledge graph system for extracting entities and relationships from documents across multiple knowledge domains (medical literature, legal documents, academic CS papers, etc.). The architecture uses a two-pass ingestion process:

1. **Pass 1 (Entity Extraction)**: Extract entities from documents, assign canonical IDs where appropriate (UMLS for medical, DBPedia URIs cross-domain, etc.)
2. **Pass 2 (Relationship Extraction)**: Identify edges/relationships between entities, produce per-document JSON with edges and provisional entities

    ...

<span id="user-content-concurrencymd"></span>

# CONCURRENCY.md

# Concurrency Issues in `ingest_paper` at Scale

This document identifies concurrency hazards in the `ingest_paper` MCP tool and
proposes mitigations for each. The context is a future production system with
thousands of simultaneous users, each potentially triggering paper ingestion at
the same time.

## Background

The `ingest_paper` MCP tool (implemented in `kgserver/mcp_server/ingest_worker.py`)

    ...

<span id="user-content-operationsmd"></span>

# OPERATIONS.md

# Operations Guide

## Full redeploy on the droplet

Tears down the running stack, prunes old images, pulls latest code, rebuilds, and
starts fresh. Use this after any code or bundle change.

```bash
docker compose --profile api down -v && \
docker image prune -a && \

    ...

<span id="user-content-readmemd"></span>

# README.md

# kgraph

Domain-agnostic knowledge graph framework for extracting entities and
relationships from documents. Current work primarily focuses on the domain of
medical literature, working from a set of papers in oncology and endocrinology,
retrieved from PubMed Central.

See `docs/overview.md` and the rest of `docs/` for documentation. For codebase
structure and module overview, see `summary.md` in the repo root (generated;
keep this file).

    ...

<span id="user-content-todomd"></span>

# TODO.md

# Ingestion Pipeline — Remaining Work

Remaining work on the ingestion pipeline, plus known data-quality defects.

---

## Phase E: Chunking and per-chunk extraction (higher risk)

### E1: Add chunking module

    ...

<span id="user-content-bfsqlmd"></span>

# bfsql.md

# KGServer BFS Query Language

## Overview

The BFS query ([breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)) provides a single, general-purpose mechanism for retrieving subgraphs from the
knowledge graph. It is designed to be constructed easily by an LLM while minimizing unnecessary
context window consumption in the response.

The design separates two orthogonal concerns:

    ...

<span id="user-content-docsadapting-to-your-domainmd"></span>

# docs/adapting-to-your-domain.md

# Adapting to Your Domain

Step-by-step guide to add a new domain to the framework: define your schema, write extraction prompts, configure your pipeline, and validate output.

## 1. Define your schema

- **Entity types** — What gets a node? Subclass `BaseEntity` for each type; register in your `DomainSchema.entity_types`.
- **Relationship types** — Which predicates? Subclass `BaseRelationship`; register in `DomainSchema.relationship_types`.
- **Document type** — Subclass `BaseDocument` for your input format (e.g. JATS for articles, plain sections for stories).
- **Provenance** — Include source document, section, and confidence in your relationship and evidence models so the graph stays traceable.

    ...

<span id="user-content-docsarchitecturemd"></span>

# docs/architecture.md

# Architecture Overview

## Two-Pass Ingestion Pipeline

The framework processes documents in two passes:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│  Raw Docs   │────▶│   Parser    │────▶│  BaseDocument   │
└─────────────┘     └─────────────┘     └────────┬────────┘

    ...

<span id="user-content-docsbooksmd"></span>

# docs/books.md

# Graphwright Publications

Three books covering the full pipeline from raw text to a language model that can reason over what that text contained.

---

## [The Typed Graph: Naming, Knowing, and Trusting Machine Knowledge](../identity-book/index.html)

The trustworthiness book. How canonical identity, a typed schema, and structural provenance together make machine knowledge defensible. Covers the epistemic commons (MeSH, HGNC, RxNorm, UniProt), the identity server's domain-agnostic core and plugin contract, the entity lifecycle, and the typed graph's central argument: that a finite predicate ontology with declared domain and range makes certain classes of error inexpressible rather than merely discouraged.

    ...

<span id="user-content-docscanonical-ids-and-entity-resolutionmd"></span>

# docs/canonical-ids-and-entity-resolution.md

# Canonical IDs and Entity Resolution

Canonical IDs are stable identifiers from authoritative sources (UMLS, MeSH, HGNC, RxNorm, UniProt, DBPedia, etc.) that uniquely identify entities across knowledge bases. This doc covers how identity works, authority lookups, and the synonym cache.

## How identity works

- **Canonical entities** have a stable `entity_id` from an authority (e.g. `UMLS:C0006142`). The same entity is the same node across documents.
- **Provisional entities** have a temporary ID until they are promoted (usage/confidence thresholds) or linked by a later lookup.
- Resolution maps each **mention** (text span from extraction) to either an existing entity or a new canonical/provisional entity.

    ...

<span id="user-content-docscontributingmd"></span>

# docs/contributing.md

# Contributing

## Internals

- **summary.md** — Generated codebase overview at repo root (e.g. `git ls-files | uv run python summarize_codebase.py > summary.md`). Keep this file; it is the reference for architecture and module layout (see also root `CLAUDE.md`).
- **kgschema** — Data structures and ABCs only; no business logic. Changes here affect all domains; keep the surface small and stable.
- **kgraph** — Orchestration, promotion, export, canonical_id, storage, pipeline interfaces. New pipeline stages should implement the existing ABCs where possible.
- **kgbundle** — Bundle contract between producer and consumer. Changes to the bundle format require coordination with kgserver and any existing bundles.
- **kgserver** — Query layer and storage backends. New backends implement the same interfaces; avoid server-specific assumptions in the bundle format.

    ...

<span id="user-content-docsdeployment-and-operationsmd"></span>

# docs/deployment-and-operations.md

# Deployment and Operations

## kgserver

The **kgserver** is a FastAPI application that loads a knowledge graph bundle (read-only) and exposes:

- **Health** — `GET /health`
- **REST** — `GET /api/v1/entities`, `GET /api/v1/relationships` (with limit, filters)
- **GraphQL** — `POST /graphql`; GraphiQL UI at `/graphiql/`
- **API docs** — OpenAPI at `/docs`

    ...

<span id="user-content-docsexamplesmedlitmd"></span>

# docs/examples/medlit.md

# The medlit Example

Annotated walkthrough of the **medical literature** reference implementation. It ingests biomedical journal articles (e.g. PMC/JATS XML), extracts entities (diseases, genes, drugs, etc.) and relationships (treats, causes, associated_with, etc.), resolves to canonical IDs (UMLS, HGNC, RxNorm, UniProt), and produces a bundle for kgserver.

## Schema (medlit_schema)

Entity types, predicates, and prompt instructions are defined in **`domain_spec.py`** (single source of truth). The extraction prompt, validation, and dedup all consume it.

- **Documents**: `JournalArticle` (BaseDocument) with paper_id, metadata, extraction provenance.
- **Entities**: DiseaseEntity, GeneEntity, DrugEntity, ProteinEntity, and others; entity_id uses authority IDs (UMLS:C..., HGNC:..., RxNorm:..., UniProt:...).

    ...

<span id="user-content-docsexamplessherlockmd"></span>

# docs/examples/sherlock.md

# The Sherlock Example

A **simpler, literary contrast case** that shows the framework’s generality. It ingests Sherlock Holmes stories (e.g. from Project Gutenberg), extracts characters, locations, and stories, and builds relationships such as `appears_in` and `co_occurs_with`. No biomedical authorities — a good template for non-medical domains.

## Schema

- **Documents**: Plain text or structured story documents (BaseDocument).
- **Entities**: Character, location, story; entity_id can be domain-minted (e.g. `holmes:char:SherlockHolmes`).
- **Relationships**: `appears_in` (character → story), `co_occurs_with` (character ↔ character), etc.
- **Domain**: DomainSchema defines the types and predicates; promotion config can be minimal (e.g. single use → canonical).

    ...

<span id="user-content-docsidentitycanonical-idsmd"></span>

# docs/identity/canonical-ids.md

# Canonical IDs and Entity Resolution

> **Placeholder** — content to be migrated and expanded from
> [`../canonical-ids-and-entity-resolution.md`](../canonical-ids-and-entity-resolution.md).

## The importance of canonical IDs

Canonical IDs are stable identifiers drawn from accepted ontologies — UMLS, MeSH, HGNC,
RxNorm, UniProt, DBPedia, and others. They are the mechanism by which entities become
part of the edifice of human knowledge rather than isolated, document-local names.

    ...

<span id="user-content-docsidentitydeduplicationmd"></span>

# docs/identity/deduplication.md

# Deduplication

> **Placeholder** — this page needs to be written.

Deduplication handles the case where two entity records refer to the same real-world
thing but have not yet been linked by canonical ID — either because both are provisional,
or because authority lookup returned different IDs that are actually synonymous.

## When dedup runs

    ...

<span id="user-content-docsindexmd"></span>

# docs/index.md

# Knowledge Graph Framework -- Documentation

This is a framework for building knowledge graphs over complex professional or academic
literature: medical papers, legal documents, technical specifications. Every assertion
in the graph traces back to a source document and location. Provenance is not an
afterthought -- it is load-bearing.

For the conceptual foundation, see **[Manifesto](manifesto.md)**, **[Overview](overview.md)** and
**[Architecture](architecture.md)**. For book-length treatments of the full
pipeline, see **[Graphwright Publications](books.md)**.

    ...

<span id="user-content-docsingestionchunkingmd"></span>

# docs/ingestion/chunking.md

# Chunking Strategies

> **Placeholder** — this page needs to be written.

Before an LLM can extract entities and relationships, a document must be segmented into
chunks that fit within a context window and preserve enough surrounding context to make
extraction meaningful.

## Goals of chunking

    ...

<span id="user-content-docsingestionerror-handlingmd"></span>

# docs/ingestion/error-handling.md

# Error Handling

> **Placeholder** — this page needs to be written.

Ingestion pipelines fail in predictable ways: LLMs return malformed JSON, authority
lookups time out, documents are corrupt. This page covers how the framework handles
partial failures without losing work.

## Failure modes

    ...

<span id="user-content-docsingestionpipelinemd"></span>

# docs/ingestion/pipeline.md

# The Ingestion Pipeline

> **Placeholder** — content to be migrated and expanded from
> [`../pipeline.md`](../pipeline.md).

## Two-pass architecture

The pipeline uses a two-pass architecture:

1. **Pass 1 — Entity extraction**: parse documents, extract entity mentions, resolve

    ...

<span id="user-content-docsllm-integrationembeddingsmd"></span>

# docs/llm-integration/embeddings.md

# Embeddings

> **Placeholder** — this page needs to be written.

Embeddings enable semantic search over the knowledge graph — finding entities by
meaning rather than exact string match.

## Where embeddings are generated

Embeddings are generated at the end of the ingestion pipeline, after entities are

    ...

<span id="user-content-docsllm-integrationextraction-promptsmd"></span>

# docs/llm-integration/extraction-prompts.md

# Prompt Design for Extraction

> **Placeholder** — this page needs to be written. See also
> [`../schema/adapting-to-your-domain.md`](../schema/adapting-to-your-domain.md)
> for the step-by-step workflow.

Extraction quality depends heavily on prompt design. This page covers principles and
patterns for writing prompts that produce reliable, schema-conformant output.

## General principles

    ...

<span id="user-content-docsllm-integrationmcp-servermd"></span>

# docs/llm-integration/mcp-server.md

# MCP Server

> **Placeholder** — content to be expanded from
> [`../deployment-and-operations.md`](../deployment-and-operations.md).

You want to expose a Model Context Protocol (MCP) endpoint that allows LLMs and
agents to query the knowledge graph as a tool. When working in Python, the
FastMCP library is good for this.

## What MCP provides

    ...

<span id="user-content-docsllm-integrationmcp-troubleshootingmd"></span>

# docs/llm-integration/mcp-troubleshooting.md

# MCP Troubleshooting

> **Placeholder** — this page needs to be written.

Things that go wrong with MCP connections, and how to fix them.

## Connection issues

**The client says "server not found" or times out.**

    ...

<span id="user-content-docsllm-integrationqueryingmd"></span>

# docs/llm-integration/querying.md

# Querying the Graph with LLMs

> **Placeholder** — this page needs to be written.

This page covers how LLMs navigate and query the knowledge graph in practice — what
patterns work, what to avoid, and how to structure agent prompts for effective graph use.

## The basic interaction pattern

1. The LLM receives a user question.

    ...

<span id="user-content-docsmanifestomd"></span>

# docs/manifesto.md

# A Manifesto for Machine Knowledge

We are now in an age of machine reasoning, and some of this reasoning is done
in high-stakes domains: medicine, law, engineering, spaceflight. Lives and
livelihoods can be affected by incorrect conclusions or decisions. The cost of
error is real and significant. LLMs are here, they are staying, and there is no
turning back the clock.

As we all know, LLMs have weaknesses. Their mastery of language syntax is
astonishing, but they don't understand "this refers to that," or "these two

    ...

<span id="user-content-docsmicroservices-runtimemd"></span>

# docs/microservices-runtime.md

# Microservices: Runtime Architecture and Interactions

> This document is derived from the source code and deployment configuration.
> Where the existing Markdown docs disagree with the code, the code wins.

---

## 1. Deployed Services

### 1.1 Edge and Ingress

    ...

<span id="user-content-docsoverviewmd"></span>

# docs/overview.md

# Overview

This codebase is a **domain-agnostic knowledge graph framework** for extracting entities and relationships from unstructured text. It addresses the core problem: turning documents (papers, legal text, reports) into a queryable graph with canonical identities and provenance.

For the conceptual foundation — why knowledge graphs, why extraction from text, and why this approach — see the book **[*Knowledge Graphs from Unstructured Text*](https://github.com/wware/kg-book)** (kg-book). The technical docs here describe how the framework is built and how to use or extend it.

## What this repo does

- **Two-pass ingestion**: Pass 1 extracts entities and resolves them to canonical or provisional IDs; Pass 2 extracts relationships between those entities.
- **Pluggable domains**: Each domain (medical literature, legal, literary, etc.) defines its own schema (entity types, relationship types, documents) and pipeline components.

    ...

<span id="user-content-docspipelinemd"></span>

# docs/pipeline.md

# The Pipeline

Each stage in detail: **parsing** (and chunking), **extraction** (entity then relationship), **dedup**, **resolution** (to canonical or provisional), and **bundle building**. The framework exposes interfaces for each; domain pipelines (e.g. medlit) implement them.

## Two-pass architecture

The knowledge graph ingestion pipeline uses a **two-pass architecture** to transform raw documents into structured knowledge:

1. **Pass 1 (Entity Extraction)**: Parse documents, extract entity mentions, and resolve them to canonical or provisional entities.
2. **Pass 2 (Relationship Extraction)**: Identify relationships (edges) between resolved entities within each document.

    ...

<span id="user-content-docsschema-design-guidemd"></span>

# docs/schema-design-guide.md

# Schema Design Guide

This guide describes how to define your domain's entities, relationships, and documents using **kgschema**. The schema is the contract between your pipeline and the framework.

## Domain schema (ABC)

Implement `DomainSchema` from `kgschema.domain` to declare entity types, relationship types, and document types:

- **Entity types** — Map type names to `BaseEntity` subclasses (e.g. `"drug"` → `DrugEntity`).
- **Relationship types** — Map predicate names to `BaseRelationship` subclasses.

    ...

<span id="user-content-docsschemaadapting-to-your-domainmd"></span>

# docs/schema/adapting-to-your-domain.md

# Adapting to Your Domain

> **Placeholder** — content to be migrated and expanded from
> [`../adapting-to-your-domain.md`](../adapting-to-your-domain.md).

Step-by-step guide to implementing the framework for a new domain.

## Step 1: Define your schema

Implement `DomainSchema` with your entity types, relationship types, and document type.

    ...

<span id="user-content-docsschemaschema-design-guidemd"></span>

# docs/schema/schema-design-guide.md

# Schema Design Guide

> **Placeholder** — content to be migrated and expanded from
> [`../schema-design-guide.md`](../schema-design-guide.md).

This guide describes how to define your domain's entities, relationships, and documents
using **kgschema**.

## Domain schema

    ...

<span id="user-content-docsstorage-and-exportmd"></span>

# docs/storage-and-export.md

# Storage and Export

## In-memory storage

The framework provides in-memory implementations of the kgschema storage interfaces (`EntityStorageInterface`, `RelationshipStorageInterface`, etc.) in `kgraph/storage/memory.py`. Use them for tests and single-process pipelines. They support the full entity lifecycle: add, resolve, promote, merge, and relationship CRUD.

## Bundle format

The **bundle** is the exchange format between producer (kgraph/pipeline) and consumer (kgserver). It is defined by the **kgbundle** package (Pydantic models: `BundleManifestV1`, `EntityRow`, `RelationshipRow`, `DocAssetRow`).

    ...

<span id="user-content-docstrustconflicting-claimsmd"></span>

# docs/trust/conflicting-claims.md

# Conflicting Claims

> **Placeholder** — this page needs to be written.

Scientific and legal literature routinely contains contradictory claims. A graph that
silently resolves conflicts by picking a winner destroys information. This framework
represents disagreements explicitly.

## What counts as a conflict

    ...

<span id="user-content-docstrustprovenancemd"></span>

# docs/trust/provenance.md

# Trust and Provenance

> **Placeholder** — this page needs to be written. Content currently lives in
> fragments across the pipeline and storage docs.

Provenance is the philosophical core of this project. Every assertion in the graph
must be traceable to a source document, a location within that document, and the
extraction step that produced it. Transparency is not an afterthought — it is
load-bearing.

    ...

<span id="user-content-identity-serverdomainstubinitpy"></span>

# identity-server/domain_stub/__init__.py

Domain stub package — minimal FastAPI domain service for development and testing.


<span id="user-content-identity-serverdomainstubapppy"></span>

# identity-server/domain_stub/app.py

Stub domain service for development and testing.

Implements the domain service HTTP contract with neutral defaults:
  - ``POST /resolve-authority`` — always returns no canonical ID (entity stays provisional)
  - ``POST /select-survivor``   — returns the candidate with the highest usage_count
  - ``POST /synonym-criteria``  — returns similarity_threshold = 0.90
  - ``GET  /health``            — returns {"status": "ok"}

This stub lets the identity server run without a real domain service.

> Stub domain service for development and testing.

Implements the domain service HTTP contract with neutral defaults:
  - ``POST /resolve-authority`` — always returns no canonical ID (entity stays provisional)
  - ``POST /select-survivor``   — returns the candidate with the highest usage_count
  - ``POST /synonym-criteria``  — returns similarity_threshold = 0.90
  - ``GET  /health``            — returns {"status": "ok"}

This stub lets the identity server run without a real domain service.


### `async def health() -> HealthResponse`

Return service health status.

### `async def resolve_authority(request: DomainResolveAuthorityRequest) -> DomainResolveAuthorityResponse`

Always return no canonical ID — the entity will remain provisional.

### `async def select_survivor(request: DomainSelectSurvivorRequest) -> DomainSelectSurvivorResponse`

Return the candidate with the highest usage_count (first if tied).

### `async def synonym_criteria(request: DomainSynonymCriteriaRequest) -> DomainSynonymCriteriaResponse`

Return the default similarity threshold of 0.90.

### `async def synonym_criteria_config() -> dict`

Return startup-time synonym criteria config.

### `async def schema() -> dict`

Return a minimal schema document for compatibility.

### `async def authorities() -> dict`

Return empty authority metadata for the stub service.


<span id="user-content-identity-serveridentityserverinitpy"></span>

# identity-server/identity_server/__init__.py

Identity server package — domain-agnostic entity identity microservice.


<span id="user-content-identity-serveridentityserverapppy"></span>

# identity-server/identity_server/app.py

FastAPI application entry point for the identity server.

The identity server is a domain-agnostic microservice that handles entity
identity for knowledge graphs: resolving mentions to canonical IDs, detecting
synonyms, merging duplicate entities, and managing the
provisional → canonical → merged lifecycle.

API documentation is available at ``/docs`` (Swagger UI) and ``/redoc``.

> FastAPI application entry point for the identity server.

The identity server is a domain-agnostic microservice that handles entity
identity for knowledge graphs: resolving mentions to canonical IDs, detecting
synonyms, merging duplicate entities, and managing the
provisional → canonical → merged lifecycle.

API documentation is available at ``/docs`` (Swagger UI) and ``/redoc``.


### `async def lifespan(app: FastAPI)`

Create database tables on startup.

### `async def health() -> HealthResponse`

Return service health status.


<span id="user-content-identity-serveridentityservercachepy"></span>

# identity-server/identity_server/cache.py

Authority-lookup cache backed by Redis.

Copied verbatim from kgraph/kgserver/storage/backends/identity.py and made
self-contained (no kgschema dependency).

> Authority-lookup cache backed by Redis.

Copied verbatim from kgraph/kgserver/storage/backends/identity.py and made
self-contained (no kgschema dependency).


## `class AuthorityCache`

Redis cache for authority-lookup results in ``resolve``.

Keys have the form ``resolve:{authority_version}:{entity_type}:{mention}``
so that a UMLS/DBPedia release can be invalidated by bumping
``authority_version`` without touching unrelated entries.

Values are JSON-serialised ``CanonicalId`` dicts (positive hit) or
``_NEGATIVE_SENTINEL`` (confirmed miss).

Designed for graceful degradation: every public method catches Redis
errors and logs at DEBUG level so a Redis outage never breaks ingestion.

Parameters
----------
redis_client:
    A ``redis.Redis`` (sync) client.  Pass ``None`` to disable caching.
authority_version:
    Opaque version string for the authority source, e.g. ``"umls-2026AA"``.
    Bump this to invalidate all cached lookups for that source.
positive_ttl:
    Seconds before a positive cache entry expires.
negative_ttl:
    Seconds before a negative cache entry expires.

### `def AuthorityCache.get(self, entity_type: str, mention: str) -> Optional[Any]`

Return cached ``CanonicalId``-like dict, ``None`` (miss), or
``_NEGATIVE_SENTINEL`` (confirmed negative).

Returns ``None`` on any Redis error so the caller falls through to the
live authority lookup.

### `def AuthorityCache.put_positive(self, entity_type: str, mention: str, canonical_id: object) -> None`

Cache a positive authority result.  ``canonical_id`` must be
JSON-serialisable (plain dict or object with ``__dict__``).

### `def AuthorityCache.put_negative(self, entity_type: str, mention: str) -> None`

Cache a confirmed negative (no canonical ID found).

### `def AuthorityCache.from_env(cls, authority_version: str = 'v1') -> 'AuthorityCache'`

Build an ``AuthorityCache`` from the ``REDIS_URL`` environment variable.

Returns a no-op cache (``redis_client=None``) if ``REDIS_URL`` is unset
or if the ``redis`` package is not installed, so the server starts
cleanly in environments without Redis.


<span id="user-content-identity-serveridentityservercorepy"></span>

# identity-server/identity_server/core.py

Postgres-backed implementation of the identity server.

This module provides ``PostgresIdentityServer``, the reference implementation
of the identity server interface.  It uses SQLModel ``Session`` and the
``Entity`` ORM model in ``db_models``, and delegates all domain-specific
logic to a ``DomainClient`` HTTP client.

Locking strategy (mirrors CONCURRENCY.md):
  - resolve:  ``INSERT ... ON CONFLICT DO NOTHING`` — Postgres serialises
              concurrent inserts on the same entity_id naturally.
  - promote:  ``SELECT ... FOR UPDATE`` on the entity row, then conditional
              update inside the same transaction.
  - merge:    Postgres advisory lock keyed on the sorted frozenset of entity
              IDs prevents two workers merging the same pair in opposite orders.
  - on_entity_added: called synchronously inside the same session as the
              triggering entity write; synonym detection is read-only and fires
              only after the row is durable.

Synonym detection uses the ``embedding`` JSON column on the ``Entity`` table
via in-process cosine similarity for now.  Once pgvector is activated on the
column the ``find_synonyms`` implementation can be swapped to a native vector
query with no interface change.

Authority-lookup caching uses Redis when a client is provided.  If Redis is
unavailable the server degrades gracefully to uncached lookups.  See
``AuthorityCache`` in ``cache.py``.

> Postgres-backed implementation of the identity server.

This module provides ``PostgresIdentityServer``, the reference implementation
of the identity server interface.  It uses SQLModel ``Session`` and the
``Entity`` ORM model in ``db_models``, and delegates all domain-specific
logic to a ``DomainClient`` HTTP client.

Locking strategy (mirrors CONCURRENCY.md):
  - resolve:  ``INSERT ... ON CONFLICT DO NOTHING`` — Postgres serialises
              concurrent inserts on the same entity_id naturally.
  - promote:  ``SELECT ... FOR UPDATE`` on the entity row, then conditional
              update inside the same transaction.
  - merge:    Postgres advisory lock keyed on the sorted frozenset of entity
              IDs prevents two workers merging the same pair in opposite orders.
  - on_entity_added: called synchronously inside the same session as the
              triggering entity write; synonym detection is read-only and fires
              only after the row is durable.

Synonym detection uses the ``embedding`` JSON column on the ``Entity`` table
via in-process cosine similarity for now.  Once pgvector is activated on the
column the ``find_synonyms`` implementation can be swapped to a native vector
query with no interface change.

Authority-lookup caching uses Redis when a client is provided.  If Redis is
unavailable the server degrades gracefully to uncached lookups.  See
``AuthorityCache`` in ``cache.py``.


## `class EntityStatus(str, Enum)`

Lifecycle status of an entity in the knowledge graph.

Entities progress through a lifecycle from provisional (newly discovered)
to canonical (stable, authoritative). This status determines how the
entity is treated in queries, exports, and merge operations.

### `def _cosine_similarity(a: list[float], b: list[float]) -> float`

Compute cosine similarity between two equal-length vectors.

### `def _advisory_lock_key(entity_ids: list[str]) -> int`

Derive a stable 64-bit advisory lock key from a sorted set of entity IDs.

Sorting ensures two workers locking the same pair always produce the same
key regardless of argument order, preventing deadlocks.

## `class _CachedCanonicalId`

Minimal canonical-ID-like object reconstructed from a Redis-cached dict.

### `def _dict_to_canonical_id(data: dict) -> _CachedCanonicalId`

Reconstruct a minimal canonical-ID-like object from a cached dict.

### `def _row_to_candidate(row: Entity) -> DomainCandidateEntity`

Convert an ``Entity`` ORM row to a ``DomainCandidateEntity`` for domain calls.

## `class PostgresIdentityServer`

Postgres-backed identity server.

Parameters
----------
session:
    An open SQLModel ``Session`` bound to the Postgres engine.  The caller
    is responsible for the session lifecycle (commit / rollback / close).
domain_client:
    HTTP client used to call the pluggable domain service for authority
    lookup, survivor selection, and synonym thresholds.
authority_cache:
    Optional ``AuthorityCache`` instance backed by Redis.  If omitted,
    authority lookups are performed on every ``resolve`` call with no
    caching.  Construct one via ``AuthorityCache.from_env()`` or pass a
    pre-built instance.
embedding_dim:
    Expected embedding dimension.  Reserved for future validation use.

### `async def PostgresIdentityServer.resolve(self, mention: str, entity_type: str, document_id: str, embedding: Optional[list[float]] = None) -> str`

Resolve a mention to an entity ID, creating a provisional one if needed.

Performs domain authority lookup via the domain service and returns a
canonical ID if one is found.  Otherwise creates and returns a new
provisional ID.  The lookup result is cached (keyed on normalised
mention + authority source version) so that transient API failures
do not produce inconsistent IDs on retry.

Uses ``INSERT ... ON CONFLICT DO NOTHING`` so concurrent workers
resolving the same mention produce the same entity without races.

Parameters
----------
mention:
    Surface form of the entity mention.
entity_type:
    Domain-specific entity type hint.
document_id:
    Source document identifier for provenance.
embedding:
    Pre-computed embedding vector for the mention.

Returns
-------
str
    A canonical or provisional entity ID.

### `async def PostgresIdentityServer.promote(self, provisional_id: str) -> str`

Attempt to promote a provisional entity to canonical status.

Uses ``SELECT FOR UPDATE`` to lock the row, then checks and updates
inside the same implicit transaction.  Behaviour by status:
  - provisional: attempts canonical ID assignment via domain service;
    upgrades if a canonical ID is returned.
  - canonical: no-op; returns existing ID.
  - merged: logs warning; returns survivor ID.

This operation must be idempotent.

Parameters
----------
provisional_id:
    The ID of the entity to promote.  May be provisional, canonical,
    or merged.

Returns
-------
str
    The canonical ID (new or pre-existing), or the survivor ID if
    the entity was merged.

### `async def PostgresIdentityServer.find_synonyms(self, entity_id: str) -> list[str]`

Return IDs of entities with cosine similarity above the per-type threshold.

Synonym criteria are fetched from the domain service
(``GET /synonym-criteria``).  Falls back to 0.90 if the service is
unreachable.

Currently uses in-process comparison of the ``embedding`` JSON column.
This is correct but O(n) — a pgvector index query can be substituted
here with no interface change once the column type is migrated.

Parameters
----------
entity_id:
    The entity to find synonyms for.

Returns
-------
list[str]
    IDs of synonym candidates, not including ``entity_id`` itself.
    Returns an empty list if no synonyms are found.

### `async def PostgresIdentityServer.merge(self, entity_ids: list[str], survivor_id: str) -> str`

Merge entities into survivor, redirecting all relationship references.

Acquires a Postgres advisory lock keyed on the sorted set of IDs to
prevent concurrent merges of the same pair in opposite directions.

Status rules:
  - all provisional → survivor stays provisional
  - any canonical → survivor becomes canonical

This operation must be idempotent: merging already-merged entities
is a no-op that returns the survivor ID.

Parameters
----------
entity_ids:
    The full set of IDs to unify, including the survivor.
survivor_id:
    The ID that will remain after the merge.  Must be a member of
    ``entity_ids``.

Returns
-------
str
    The survivor ID.

### `async def PostgresIdentityServer.on_entity_added(self, entity_id: str, context: dict) -> None`

Trigger synonym detection and merge for a newly added entity.

Must be called inside the same session/transaction as the entity insert
so that the row is visible.  Synonym detection is read-only; ``merge``
acquires its own advisory lock.

Typical implementation:
1. Call ``find_synonyms`` to identify candidates.
2. If candidates are found, call the domain service ``select_survivor``
   to determine the survivor.
3. Call ``merge`` for the confirmed synonym group.

Parameters
----------
entity_id:
    The ID of the entity that was just added or updated.
context:
    Domain-defined context forwarded from the triggering operation.

### `def PostgresIdentityServer._update_relationship_refs(self, old_id: str, new_id: str) -> None`

Redirect all relationship subject/object references from old_id to new_id.

### `def PostgresIdentityServer._store_embedding(self, entity_id: str, embedding: list[float]) -> None`

Persist an embedding vector to the entity row (JSON column).


<span id="user-content-identity-serveridentityserverdatabasepy"></span>

# identity-server/identity_server/database.py

Database setup for the identity server using SQLModel.

### `def create_db_and_tables() -> None`

Create all database tables defined in SQLModel metadata.

### `def get_session()`

FastAPI dependency that yields an open SQLModel session.


<span id="user-content-identity-serveridentityserverdbmodelspy"></span>

# identity-server/identity_server/db_models.py

Generic Entity ORM model for the identity server.

Adapted from kgraph/kgserver/storage/models/entity.py.

> 
Generic Entity ORM model for the identity server.

Adapted from kgraph/kgserver/storage/models/entity.py.


## `class Entity(SQLModel)`

A generic entity in the knowledge graph.


<span id="user-content-identity-serveridentityserverdomainclientpy"></span>

# identity-server/identity_server/domain_client.py

HTTP client for the pluggable domain service.

The domain service is a separate microservice that implements domain-specific
logic: authority lookup (e.g. UMLS, DBPedia), survivor selection during merge,
and synonym similarity thresholds per entity type.

The identity server calls the domain service via HTTP so that domain logic can
change without redeploying the identity server. If the domain service is
unreachable, all methods degrade gracefully to sensible defaults:
  - ``resolve_authority`` → None (entity stays provisional)
  - ``select_survivor`` → candidate with highest usage_count (first if tied)
  - ``synonym_criteria`` → 0.90

> HTTP client for the pluggable domain service.

The domain service is a separate microservice that implements domain-specific
logic: authority lookup (e.g. UMLS, DBPedia), survivor selection during merge,
and synonym similarity thresholds per entity type.

The identity server calls the domain service via HTTP so that domain logic can
change without redeploying the identity server. If the domain service is
unreachable, all methods degrade gracefully to sensible defaults:
  - ``resolve_authority`` → None (entity stays provisional)
  - ``select_survivor`` → candidate with highest usage_count (first if tied)
  - ``synonym_criteria`` → 0.90


## `class DomainClient`

HTTP client that calls the domain service.

Parameters
----------
base_url:
    Base URL of the domain service.  Reads ``DOMAIN_SERVICE_URL`` from the
    environment; defaults to ``http://domain-stub:8080``.
timeout:
    HTTP request timeout in seconds.

### `async def DomainClient.resolve_authority(self, mention: str, entity_type: str, document_id: str) -> Optional[DomainCanonicalId]`

Ask the domain service whether this mention has a canonical ID.

Parameters
----------
mention:
    Surface form of the entity mention.
entity_type:
    Domain-specific entity type hint.
document_id:
    Source document identifier.

Returns
-------
Optional[DomainCanonicalId]
    The canonical ID from the authority source, or ``None`` if no match
    was found or the domain service is unreachable.

### `async def DomainClient.select_survivor(self, candidates: list[DomainCandidateEntity]) -> str`

Ask the domain service which candidate should survive a merge.

Parameters
----------
candidates:
    All entities being considered for merge.

Returns
-------
str
    The entity ID of the chosen survivor.  Falls back to the candidate
    with the highest ``usage_count`` (first if tied) if the domain
    service is unreachable.

### `async def DomainClient.synonym_criteria(self, entity_type: str) -> float`

Fetch the cosine similarity threshold for synonym detection.

Parameters
----------
entity_type:
    Domain-specific entity type.

Returns
-------
float
    Minimum cosine similarity threshold.  Defaults to 0.90 if the
    domain service is unreachable.


<span id="user-content-identity-serveridentityservermodelspy"></span>

# identity-server/identity_server/models.py

HTTP request/response schemas for the identity server and domain service contract.

This module defines two groups of Pydantic models:

1. **Identity server schemas** — what callers (kgserver, ingestion pipeline) send
   to and receive from the identity server endpoints.

2. **Domain service schemas** — what the identity server sends to and receives from
   the pluggable domain service (authority lookup, survivor selection, synonym criteria).

> HTTP request/response schemas for the identity server and domain service contract.

This module defines two groups of Pydantic models:

1. **Identity server schemas** — what callers (kgserver, ingestion pipeline) send
   to and receive from the identity server endpoints.

2. **Domain service schemas** — what the identity server sends to and receives from
   the pluggable domain service (authority lookup, survivor selection, synonym criteria).


## `class ResolveRequest(BaseModel)`

Request body for POST /resolve.
**Fields:**

```python
mention: str
entity_type: str
document_id: str
embedding: Optional[list[float]]
```

## `class ResolveResponse(BaseModel)`

Response body for POST /resolve.
**Fields:**

```python
entity_id: str
```

## `class PromoteRequest(BaseModel)`

Request body for POST /promote.
**Fields:**

```python
entity_id: str
```

## `class PromoteResponse(BaseModel)`

Response body for POST /promote.
**Fields:**

```python
entity_id: str
```

## `class FindSynonymsRequest(BaseModel)`

Request body for POST /find-synonyms.
**Fields:**

```python
entity_id: str
```

## `class FindSynonymsResponse(BaseModel)`

Response body for POST /find-synonyms.
**Fields:**

```python
synonym_ids: list[str]
```

## `class MergeRequest(BaseModel)`

Request body for POST /merge.
**Fields:**

```python
entity_ids: list[str]
survivor_id: str
```

## `class MergeResponse(BaseModel)`

Response body for POST /merge.
**Fields:**

```python
survivor_id: str
```

## `class OnEntityAddedRequest(BaseModel)`

Request body for POST /on-entity-added.
**Fields:**

```python
entity_id: str
context: dict
```

## `class HealthResponse(BaseModel)`

Response body for GET /health.
**Fields:**

```python
status: str
```

## `class DomainCanonicalId(BaseModel)`

Canonical ID as returned by the domain service resolve-authority endpoint.
**Fields:**

```python
id: str
url: Optional[str]
synonyms: list[str]
```

## `class DomainResolveAuthorityRequest(BaseModel)`

Request body sent by the identity server to POST /resolve-authority on the domain service.
**Fields:**

```python
mention: str
entity_type: str
document_id: str
```

## `class DomainResolveAuthorityResponse(BaseModel)`

Response body from POST /resolve-authority on the domain service.
**Fields:**

```python
canonical_id: Optional[DomainCanonicalId]
```

## `class DomainCandidateEntity(BaseModel)`

A candidate entity sent to the domain service for survivor selection.
**Fields:**

```python
entity_id: str
name: str
entity_type: str
status: str
usage_count: int
confidence: float
```

## `class DomainSelectSurvivorRequest(BaseModel)`

Request body sent by the identity server to POST /select-survivor on the domain service.
**Fields:**

```python
candidates: list[DomainCandidateEntity]
```

## `class DomainSelectSurvivorResponse(BaseModel)`

Response body from POST /select-survivor on the domain service.
**Fields:**

```python
survivor_id: str
```

## `class DomainSynonymCriteriaRequest(BaseModel)`

Request body sent by the identity server to POST /synonym-criteria on the domain service.
**Fields:**

```python
entity_type: str
```

## `class DomainSynonymCriteriaResponse(BaseModel)`

Response body from POST /synonym-criteria on the domain service.
**Fields:**

```python
similarity_threshold: float
```


<span id="user-content-identity-serveridentityserverroutersinitpy"></span>

# identity-server/identity_server/routers/__init__.py

Routers sub-package for the identity server.


<span id="user-content-identity-serveridentityserverroutersdumppy"></span>

# identity-server/identity_server/routers/dump.py

Export and import endpoints for identity server state serialization.

Provides a simple dump/load mechanism for development and deployment workflows,
equivalent to ``pg_dump``/``pg_restore`` but scoped to just the entity table
and expressed as line-delimited JSON (NDJSON) for portability and diffability.

Endpoints
---------
GET  /dump         Stream all entity rows as NDJSON.
POST /load         Load NDJSON entity rows, skipping rows that already exist.
DELETE /wipe       Delete all entity rows (dev only; requires confirmation header).

> Export and import endpoints for identity server state serialization.

Provides a simple dump/load mechanism for development and deployment workflows,
equivalent to ``pg_dump``/``pg_restore`` but scoped to just the entity table
and expressed as line-delimited JSON (NDJSON) for portability and diffability.

Endpoints
---------
GET  /dump         Stream all entity rows as NDJSON.
POST /load         Load NDJSON entity rows, skipping rows that already exist.
DELETE /wipe       Delete all entity rows (dev only; requires confirmation header).


### `def _entities_to_ndjson(session: Session) -> bytes`

Return all entity rows serialised as NDJSON bytes, ordered by entity_id.

### `def dump(session: Session = Depends(get_session)) -> StreamingResponse`

Export all entity rows as NDJSON.

### `async def load(request: Request, session: Session = Depends(get_session)) -> dict`

Load NDJSON entity rows, skipping existing entity_ids.

### `def wipe(session: Session = Depends(get_session), x_confirm_wipe: str = Header(default='')) -> dict`

Delete all entity rows. Requires X-Confirm-Wipe: yes header.


<span id="user-content-identity-serveridentityserverroutersidentitypy"></span>

# identity-server/identity_server/routers/identity.py

FastAPI router implementing the identity server HTTP endpoints.

Each endpoint creates a ``PostgresIdentityServer`` instance with the
injected session and domain client, calls the appropriate method, and
returns the result.

Endpoints
---------
POST /resolve          Resolve a mention to a canonical or provisional entity ID.
POST /promote          Attempt to promote a provisional entity to canonical status.
POST /find-synonyms    Detect entities synonymous with the given entity.
POST /merge            Merge a set of entities into a single survivor.
POST /on-entity-added  Event hook: trigger synonym detection after an entity insert.

> FastAPI router implementing the identity server HTTP endpoints.

Each endpoint creates a ``PostgresIdentityServer`` instance with the
injected session and domain client, calls the appropriate method, and
returns the result.

Endpoints
---------
POST /resolve          Resolve a mention to a canonical or provisional entity ID.
POST /promote          Attempt to promote a provisional entity to canonical status.
POST /find-synonyms    Detect entities synonymous with the given entity.
POST /merge            Merge a set of entities into a single survivor.
POST /on-entity-added  Event hook: trigger synonym detection after an entity insert.


### `def get_domain_client() -> DomainClient`

FastAPI dependency that provides a ``DomainClient`` instance.

### `def get_authority_cache() -> AuthorityCache`

FastAPI dependency that provides a Redis-backed ``AuthorityCache``.

### `def get_identity_server(session: Session = Depends(get_session), domain_client: DomainClient = Depends(get_domain_client), authority_cache: AuthorityCache = Depends(get_authority_cache)) -> PostgresIdentityServer`

FastAPI dependency that assembles a ``PostgresIdentityServer``.

### `async def resolve(request: ResolveRequest, identity_server: PostgresIdentityServer = Depends(get_identity_server)) -> ResolveResponse`

Resolve a mention string to a canonical or provisional entity ID.

Creates a new provisional entity if no existing entity or authority match
is found.  Idempotent: resolving the same mention twice returns the same ID.

### `async def promote(request: PromoteRequest, identity_server: PostgresIdentityServer = Depends(get_identity_server)) -> PromoteResponse`

Attempt to promote a provisional entity to canonical status.

Returns the canonical ID (new or pre-existing), or the survivor ID if
the entity was already merged.  Idempotent.

### `async def find_synonyms(request: FindSynonymsRequest, identity_server: PostgresIdentityServer = Depends(get_identity_server)) -> FindSynonymsResponse`

Return the IDs of entities considered synonymous with the given entity.

Read-only — reports candidates without merging.  Call ``/merge`` to act
on the results.

### `async def merge(request: MergeRequest, identity_server: PostgresIdentityServer = Depends(get_identity_server)) -> MergeResponse`

Merge a set of entities into a single survivor.

All references from absorbed entities are redirected to the survivor.
Absorbed entities are marked ``status=MERGED`` with ``merged_into`` set.
Idempotent: already-merged entities are skipped.

### `async def on_entity_added(request: OnEntityAddedRequest, identity_server: PostgresIdentityServer = Depends(get_identity_server)) -> dict`

Event hook called after an entity is inserted or updated.

Triggers synonym detection and, if synonyms are found, calls the domain
service to select a survivor and performs the merge automatically.


<span id="user-content-identity-servertestsinitpy"></span>

# identity-server/tests/__init__.py

Identity server test suite.


<span id="user-content-identity-servertestsconftestpy"></span>

# identity-server/tests/conftest.py

Shared pytest fixtures for the identity server test suite.

Fixtures provided
-----------------
engine
    SQLite in-memory engine with all tables created.
session
    Open SQLModel Session bound to the in-memory engine.  Rolled back after
    each test to keep tests independent.
mock_domain_client
    A ``DomainClient`` instance whose HTTP methods are replaced with
    ``unittest.mock.AsyncMock`` so tests can control domain service responses
    without a real network connection.

> Shared pytest fixtures for the identity server test suite.

Fixtures provided
-----------------
engine
    SQLite in-memory engine with all tables created.
session
    Open SQLModel Session bound to the in-memory engine.  Rolled back after
    each test to keep tests independent.
mock_domain_client
    A ``DomainClient`` instance whose HTTP methods are replaced with
    ``unittest.mock.AsyncMock`` so tests can control domain service responses
    without a real network connection.


### `def engine_fixture()`

SQLite in-memory engine with all identity server tables created.

StaticPool ensures all connections (including those made inside FastAPI's
thread-pool for sync endpoints) share the same in-memory database, so
tables created here are visible to every connection throughout the test.

### `def session_fixture(engine)`

Open SQLModel Session.  Each test gets a fresh, isolated session.

### `def mock_domain_client_fixture()`

DomainClient with all async methods replaced by AsyncMock.

Default behaviour (can be overridden per-test):
  - resolve_authority → None  (no canonical ID found)
  - select_survivor   → first candidate's entity_id
  - synonym_criteria  → 0.90


<span id="user-content-identity-serverteststestcachepy"></span>

# identity-server/tests/test_cache.py

Tests for AuthorityCache (identity_server/cache.py).

Uses a mock Redis client (unittest.mock.MagicMock) so no real Redis is needed.
Tests cover:
  - cache miss (key not in Redis)
  - positive hit (canonical ID dict returned)
  - negative hit (_NEGATIVE_SENTINEL returned)
  - put_positive stores correct JSON
  - put_negative stores sentinel value
  - Redis errors degrade gracefully (no exception raised)
  - no-op when redis_client is None

> Tests for AuthorityCache (identity_server/cache.py).

Uses a mock Redis client (unittest.mock.MagicMock) so no real Redis is needed.
Tests cover:
  - cache miss (key not in Redis)
  - positive hit (canonical ID dict returned)
  - negative hit (_NEGATIVE_SENTINEL returned)
  - put_positive stores correct JSON
  - put_negative stores sentinel value
  - Redis errors degrade gracefully (no exception raised)
  - no-op when redis_client is None


### `def mock_redis()`

Return a MagicMock simulating a redis.Redis sync client.

### `def cache(mock_redis)`

AuthorityCache wired to the mock Redis client.

### `def test_get_miss_returns_none(cache, mock_redis)`

When Redis has no entry for the key, get() must return None.

### `def test_get_positive_hit_returns_dict(cache, mock_redis)`

When Redis has a cached canonical ID, get() returns the parsed dict.

### `def test_get_negative_hit_returns_sentinel(cache, mock_redis)`

When Redis has the negative sentinel, get() returns _NEGATIVE_SENTINEL.

### `def test_put_positive_stores_json(cache, mock_redis)`

put_positive() serialises the canonical ID and calls Redis setex.

### `def test_put_positive_with_plain_dict(cache, mock_redis)`

put_positive() works when given a plain dict (no __dict__ attribute).

### `def test_put_negative_stores_sentinel(cache, mock_redis)`

put_negative() writes _NEGATIVE_SENTINEL to Redis.

### `def test_get_redis_error_returns_none(cache, mock_redis)`

If Redis raises an exception, get() returns None (no crash).

### `def test_put_positive_redis_error_silent(cache, mock_redis)`

If Redis raises during put_positive, no exception is propagated.

### `def test_put_negative_redis_error_silent(cache, mock_redis)`

If Redis raises during put_negative, no exception is propagated.

### `def test_noop_cache_get_returns_none()`

AuthorityCache with redis_client=None always returns None from get().

### `def test_noop_cache_put_does_not_raise()`

AuthorityCache with redis_client=None accepts put_positive and put_negative silently.


<span id="user-content-identity-serverteststestcorepy"></span>

# identity-server/tests/test_core.py

Tests for PostgresIdentityServer (identity_server/core.py).

Uses SQLite in-memory (via the session fixture from conftest.py) for
portability — SQLModel works with SQLite for all non-Postgres-specific
operations.  Advisory locks and ON CONFLICT are skipped/adapted in SQLite:
  - pg_advisory_xact_lock is not available; merge tests that need it are
    tested at the logic level with a pre-existing DB state.
  - ON CONFLICT DO NOTHING falls back gracefully in SQLite (different syntax;
    we test the resolve semantics instead).

Tests cover:
  - resolve creates a provisional entity when no authority match is found
  - resolve returns the existing entity_id for a repeated mention
  - resolve returns canonical entity_id when domain client finds a match
  - resolve redirects through merged entities
  - promote is a no-op on a canonical entity
  - promote handles merged entity (returns survivor)
  - merge marks absorbed entities as MERGED and sets merged_into
  - merge raises ValueError when survivor_id is not in entity_ids
  - find_synonyms returns empty list when entity has no embedding
  - find_synonyms returns matching entities above similarity threshold
  - on_entity_added triggers merge when synonyms are detected

> Tests for PostgresIdentityServer (identity_server/core.py).

Uses SQLite in-memory (via the session fixture from conftest.py) for
portability — SQLModel works with SQLite for all non-Postgres-specific
operations.  Advisory locks and ON CONFLICT are skipped/adapted in SQLite:
  - pg_advisory_xact_lock is not available; merge tests that need it are
    tested at the logic level with a pre-existing DB state.
  - ON CONFLICT DO NOTHING falls back gracefully in SQLite (different syntax;
    we test the resolve semantics instead).

Tests cover:
  - resolve creates a provisional entity when no authority match is found
  - resolve returns the existing entity_id for a repeated mention
  - resolve returns canonical entity_id when domain client finds a match
  - resolve redirects through merged entities
  - promote is a no-op on a canonical entity
  - promote handles merged entity (returns survivor)
  - merge marks absorbed entities as MERGED and sets merged_into
  - merge raises ValueError when survivor_id is not in entity_ids
  - find_synonyms returns empty list when entity has no embedding
  - find_synonyms returns matching entities above similarity threshold
  - on_entity_added triggers merge when synonyms are detected


### `def test_cosine_similarity_identical()`

Cosine similarity of a vector with itself is 1.0.

### `def test_cosine_similarity_orthogonal()`

Orthogonal vectors have cosine similarity of 0.0.

### `def test_cosine_similarity_zero_vector()`

Zero vector produces 0.0 (no division by zero).

### `async def test_resolve_creates_provisional_entity(session, mock_domain_client)`

Resolve creates a new provisional entity when no authority match is found.

### `async def test_resolve_returns_existing_entity(session, mock_domain_client)`

Resolving the same mention twice returns the same entity ID.

### `async def test_resolve_returns_canonical_when_authority_found(session, mock_domain_client)`

When the domain client returns a canonical ID, the entity is inserted as canonical.

### `async def test_resolve_redirects_merged_entity(session, mock_domain_client)`

When the existing row is merged, resolve returns the survivor ID.

### `async def test_promote_noop_on_canonical(session, mock_domain_client)`

Promoting a canonical entity is a no-op that returns the same ID.

### `async def test_promote_merged_entity_returns_survivor(session, mock_domain_client)`

Promoting a merged entity logs a warning and returns the survivor ID.

### `async def test_promote_provisional_no_authority_stays_provisional(session, mock_domain_client)`

Promoting a provisional entity stays provisional when no canonical ID is returned.

### `async def test_merge_marks_absorbed_entities(session, mock_domain_client)`

Merge marks the absorbed entity as MERGED with merged_into set to survivor.

### `async def test_merge_raises_when_survivor_not_in_entity_ids(session, mock_domain_client)`

merge() raises ValueError if survivor_id is not a member of entity_ids.

### `async def test_merge_single_entity_is_noop(session, mock_domain_client)`

Merging a single entity into itself returns survivor_id immediately.

### `async def test_find_synonyms_empty_without_embedding(session, mock_domain_client)`

find_synonyms returns an empty list when the entity has no embedding.

### `async def test_find_synonyms_returns_similar_entities(session, mock_domain_client)`

find_synonyms returns entities whose cosine similarity exceeds the threshold.

### `async def test_on_entity_added_merges_synonyms(session, mock_domain_client)`

on_entity_added triggers merge when synonym candidates are found.


<span id="user-content-identity-serverteststestdomainclientpy"></span>

# identity-server/tests/test_domain_client.py

Tests for DomainClient (identity_server/domain_client.py).

Uses httpx.MockTransport to intercept HTTP calls without a real server.
Tests cover:
  - successful resolve-authority with a canonical ID
  - resolve-authority returning null canonical_id
  - connection error degrades to None / default values
  - successful select-survivor
  - select-survivor connection error falls back to highest usage_count
  - successful synonym-criteria
  - synonym-criteria connection error falls back to 0.90

> Tests for DomainClient (identity_server/domain_client.py).

Uses httpx.MockTransport to intercept HTTP calls without a real server.
Tests cover:
  - successful resolve-authority with a canonical ID
  - resolve-authority returning null canonical_id
  - connection error degrades to None / default values
  - successful select-survivor
  - select-survivor connection error falls back to highest usage_count
  - successful synonym-criteria
  - synonym-criteria connection error falls back to 0.90


### `def _make_transport(routes: dict)`

Build an httpx.MockTransport from a dict of {url_suffix: response_body}.

### `def _error_transport()`

A transport that always raises a connection error.

### `def _client_with_transport(transport) -> DomainClient`

DomainClient pre-wired with a custom transport (bypasses real HTTP).

### `async def test_resolve_authority_returns_canonical_id()`

Successful resolve-authority response with a canonical ID is parsed correctly.

### `async def test_resolve_authority_null_canonical_id()`

When the domain service returns canonical_id=null, resolve_authority returns None.

### `async def test_resolve_authority_connection_error_returns_none()`

When the domain service is unreachable, resolve_authority degrades to None.

### `async def test_select_survivor_success()`

Successful select-survivor response is returned correctly.

### `async def test_select_survivor_connection_error_falls_back_to_highest_usage()`

When domain service is unreachable, select_survivor returns highest usage_count candidate.

### `async def test_synonym_criteria_success()`

Successful synonym-criteria response is parsed and returned.

### `async def test_synonym_criteria_connection_error_returns_default()`

When domain service is unreachable, synonym_criteria falls back to default threshold.


<span id="user-content-identity-serverteststestdumppy"></span>

# identity-server/tests/test_dump.py

Tests for the /admin/dump, /admin/load, and /admin/wipe endpoints.

### `def client(session: Session, engine)`

TestClient with the session dependency overridden and lifespan bypassed.

### `def test_dump_load_roundtrip(client, session)`

Dump → wipe → load should restore the same rows.


<span id="user-content-kgbundlekgbundleinitpy"></span>

# kgbundle/kgbundle/__init__.py

Knowledge Graph Bundle Models

Lightweight Pydantic models defining the contract between bundle producers
(kgraph ingestion framework) and consumers (kgserver query server).

This package has minimal dependencies (only pydantic) and is designed to be
importable by both sides without pulling in heavy ML or web frameworks.

Example:
    # In kgraph (producer) - export bundle
    from kgbundle import BundleManifestV1, EntityRow, RelationshipRow

    entity = EntityRow(
        entity_id="char:123",
        entity_type="character",
        name="Sherlock Holmes",
        status="canonical",
        usage_count=1,
        created_at="2024-01-15T10:30:00Z",
        source="sherlock:curated"
    )

    # In kgserver (consumer) - load bundle
    from kgbundle import BundleManifestV1

    with open("manifest.json") as f:
        manifest = BundleManifestV1.model_validate_json(f.read())

> 
Knowledge Graph Bundle Models

Lightweight Pydantic models defining the contract between bundle producers
(kgraph ingestion framework) and consumers (kgserver query server).

This package has minimal dependencies (only pydantic) and is designed to be
importable by both sides without pulling in heavy ML or web frameworks.

Example:
    # In kgraph (producer) - export bundle
    from kgbundle import BundleManifestV1, EntityRow, RelationshipRow

    entity = EntityRow(
        entity_id="char:123",
        entity_type="character",
        name="Sherlock Holmes",
        status="canonical",
        usage_count=1,
        created_at="2024-01-15T10:30:00Z",
        source="sherlock:curated"
    )

    # In kgserver (consumer) - load bundle
    from kgbundle import BundleManifestV1

    with open("manifest.json") as f:
        manifest = BundleManifestV1.model_validate_json(f.read())



<span id="user-content-kgbundlekgbundlemodelspy"></span>

# kgbundle/kgbundle/models.py

Knowledge Graph Bundle Models

Lightweight Pydantic models defining the contract between bundle producers (kgraph)
and consumers (kgserver).

This module has minimal dependencies (only pydantic) and is designed to be
importable by both sides without pulling in heavy ML or web frameworks.

> 
Knowledge Graph Bundle Models

Lightweight Pydantic models defining the contract between bundle producers (kgraph)
and consumers (kgserver).

This module has minimal dependencies (only pydantic) and is designed to be
importable by both sides without pulling in heavy ML or web frameworks.


## `class EntityRow(BaseModel)`

Entity row format for bundle JSONL files.

Matches the server bundle contract with proper field names and types.
**Fields:**

```python
entity_id: str
entity_type: str
name: Optional[str]
status: str
confidence: Optional[float]
usage_count: int
created_at: str
source: str
canonical_url: Optional[str]
properties: Dict[str, Any]
first_seen_document: Optional[str]
first_seen_section: Optional[str]
total_mentions: int
supporting_documents: List[str]
```

## `class RelationshipRow(BaseModel)`

Relationship row format for bundle JSONL files.

Matches the server bundle contract with proper field names and types.
**Fields:**

```python
subject_id: str
object_id: str
predicate: str
confidence: Optional[float]
source_documents: List[str]
created_at: str
properties: Dict[str, Any]
evidence_count: int
strongest_evidence_quote: Optional[str]
evidence_confidence_avg: Optional[float]
```

## `class MentionRow(BaseModel)`

One entity mention occurrence (one line in mentions.jsonl).
**Fields:**

```python
entity_id: str
document_id: str
section: Optional[str]
start_offset: int
end_offset: int
text_span: str
context: Optional[str]
confidence: float
extraction_method: str
created_at: str
```

## `class EvidenceRow(BaseModel)`

One evidence span supporting a relationship (one line in evidence.jsonl).
**Fields:**

```python
relationship_key: str
document_id: str
section: Optional[str]
start_offset: int
end_offset: int
text_span: str
confidence: float
supports: bool
```

## `class BundleFile(BaseModel)`

Reference to a file within the bundle.
**Fields:**

```python
path: str
format: str
```

## `class DocAssetRow(BaseModel)`

Documentation asset row format for bundle doc_assets.jsonl files.

Lists static assets (markdown files, images, etc.) that should be
copied from the bundle to provide documentation for the knowledge domain.

Note: This is for human-readable documentation, NOT source documents
(papers, articles) used for entity/relationship extraction.
**Fields:**

```python
path: str
content_type: str
```

## `class BundleManifestV1(BaseModel)`

Bundle manifest format matching the server contract.

Contains bundle identification, file references, and metadata.
**Fields:**

```python
bundle_version: str
bundle_id: str
domain: str
label: Optional[str]
created_at: str
entities: BundleFile
relationships: BundleFile
doc_assets: Optional[BundleFile]
mentions: Optional[BundleFile]
evidence: Optional[BundleFile]
metadata: Dict[str, Any]
```


<span id="user-content-kgbundleteststestmodelspy"></span>

# kgbundle/tests/test_models.py

Tests for kgbundle Pydantic models (bundle contract).

## `class TestEntityRow`

Test EntityRow serialization and validation.

## `class TestRelationshipRow`

Test RelationshipRow serialization.

## `class TestMentionRow`

Test MentionRow (mentions.jsonl).

## `class TestEvidenceRow`

Test EvidenceRow (evidence.jsonl).

## `class TestBundleManifestV1`

Test BundleManifestV1.


<span id="user-content-kgraphinitpy"></span>

# kgraph/__init__.py

Knowledge Graph Framework - Domain-Agnostic Entity and Relationship Extraction.

A flexible framework for building knowledge graphs across multiple domains
(medical, legal, CS papers, etc.) with a two-pass ingestion process.

> 
Knowledge Graph Framework - Domain-Agnostic Entity and Relationship Extraction.

A flexible framework for building knowledge graphs across multiple domains
(medical, legal, CS papers, etc.) with a two-pass ingestion process.



<span id="user-content-kgraphbuilderspy"></span>

# kgraph/builders.py

## `class EntityBuilder(BaseModel)`


**Fields:**

```python
domain: DomainSchema
clock: IngestionClock
document: BaseDocument
entity_storage: EntityStorageInterface | None
provisional_prefix: str
```

## `class RelationshipBuilder(BaseModel)`


**Fields:**

```python
domain: DomainSchema
clock: IngestionClock
document: BaseDocument
entity_storage: EntityStorageInterface | None
```

### `async def RelationshipBuilder.link(self) -> BaseRelationship`

Create a relationship with structured provenance tracking.

Args:
    predicate: Relationship type (e.g., "treats", "causes")
    subject_id: Entity ID of the relationship subject
    object_id: Entity ID of the relationship object
    confidence: Confidence score (0.0-1.0)
    source_documents: Document IDs supporting this relationship
    metadata: Domain-specific metadata (prefer using evidence field for provenance)
    evidence: Structured evidence with provenance (document, section, paragraph, offsets)

Returns:
    BaseRelationship instance validated by the domain schema


<span id="user-content-kgraphcanonicalidinitpy"></span>

# kgraph/canonical_id/__init__.py

Canonical ID system for knowledge graph ingestion.

This package provides abstractions for working with canonical IDs (stable
identifiers from authoritative sources) throughout the ingestion pipeline.

Note: The CanonicalId model has been moved to kgschema.canonical_id but is
re-exported here for backwards compatibility.

> Canonical ID system for knowledge graph ingestion.

This package provides abstractions for working with canonical IDs (stable
identifiers from authoritative sources) throughout the ingestion pipeline.

Note: The CanonicalId model has been moved to kgschema.canonical_id but is
re-exported here for backwards compatibility.



<span id="user-content-kgraphcanonicalidhelperspy"></span>

# kgraph/canonical_id/helpers.py

Helper functions for working with canonical IDs in promotion logic.

This module provides generic helper functions that can be used by promotion
policies to extract canonical IDs from entity data.

> Helper functions for working with canonical IDs in promotion logic.

This module provides generic helper functions that can be used by promotion
policies to extract canonical IDs from entity data.


### `def extract_canonical_id_from_entity(entity: BaseEntity, priority_sources: Optional[list[str]] = None) -> Optional[CanonicalId]`

Extract canonical ID from entity's canonical_ids dict.

Args:
    entity: The entity to extract canonical ID from
    priority_sources: Optional list of source keys to check in priority order.
                     If None, checks all sources in the dict.

Returns:
    CanonicalId if found, None otherwise

### `def check_entity_id_format(entity: BaseEntity, format_patterns: dict[str, tuple[str, ...]]) -> Optional[CanonicalId]`

Check if entity_id matches any known canonical ID format.

Args:
    entity: The entity to check
    format_patterns: Dict mapping entity types to tuples of format prefixes/patterns.
                    For example: {"gene": ("HGNC:",), "disease": ("C",)}

Returns:
    CanonicalId if entity_id matches a format, None otherwise


<span id="user-content-kgraphcanonicalidjsoncachepy"></span>

# kgraph/canonical_id/json_cache.py

JSON file-based implementation of CanonicalIdCacheInterface.

This implementation stores canonical ID lookups in a JSON file, with support for
backward compatibility with the old cache format (dict[str, str]).

> JSON file-based implementation of CanonicalIdCacheInterface.

This implementation stores canonical ID lookups in a JSON file, with support for
backward compatibility with the old cache format (dict[str, str]).


## `class JsonFileCanonicalIdCache(CanonicalIdCacheInterface)`

JSON file-based implementation of CanonicalIdCacheInterface.

Stores canonical ID lookups in a JSON file. The cache format is:
{
    "cache_key": {
        "id": "UMLS:C12345",
        "url": "https://...",
        "synonyms": ["term1", "term2"]
    },
    ...
}

Known bad entries are stored with `"id": null` to distinguish them from
successful lookups.

Attributes:
    cache_file: Path to the JSON cache file
    _cache: In-memory cache dictionary mapping cache keys to CanonicalId objects
    _known_bad: Set of cache keys marked as "known bad"
    _cache_dirty: Whether the cache has been modified since last save
    _hits: Number of cache hits
    _misses: Number of cache misses

### `def JsonFileCanonicalIdCache.__init__(self, cache_file: Optional[Path] = None)`

Initialize the JSON file-based cache.

Args:
    cache_file: Path to the JSON cache file. If None, defaults to
               "canonical_id_cache.json" in the current directory.

### `def JsonFileCanonicalIdCache.load(self, tag: str) -> None`

Load cache from JSON file.

Args:
    tag: Path to the cache file (overrides self.cache_file if provided).
         If tag is a relative path, it's used as-is.
         If tag is an absolute path, it overrides self.cache_file.

### `def JsonFileCanonicalIdCache._migrate_old_format(self, old_data: dict[str, str]) -> None`

Migrate old cache format (dict[str, str]) to new format.

Args:
    old_data: Old cache data where values are either canonical ID strings or "NULL"

### `def JsonFileCanonicalIdCache.save(self, tag: str) -> None`

Save cache to JSON file.

Args:
    tag: Path to the cache file (overrides self.cache_file if provided).
         If tag is a path, it's used as-is.

### `def JsonFileCanonicalIdCache.store(self, term: str, entity_type: str, canonical_id: CanonicalId) -> None`

Store a canonical ID in the cache.

Args:
    term: The entity name/mention text
    entity_type: Type of entity (e.g., "disease", "gene", "drug")
    canonical_id: The CanonicalId object to store

### `def JsonFileCanonicalIdCache.fetch(self, term: str, entity_type: str) -> Optional[CanonicalId]`

Fetch a canonical ID from the cache.

Args:
    term: The entity name/mention text
    entity_type: Type of entity (e.g., "disease", "gene", "drug")

Returns:
    CanonicalId if found in cache, None if not found or marked as "known bad"

### `def JsonFileCanonicalIdCache.mark_known_bad(self, term: str, entity_type: str) -> None`

Mark a term as "known bad" (failed lookup, don't retry).

Args:
    term: The entity name/mention text
    entity_type: Type of entity (e.g., "disease", "gene", "drug")

### `def JsonFileCanonicalIdCache.is_known_bad(self, term: str, entity_type: str) -> bool`

Check if a term is marked as "known bad".

Args:
    term: The entity name/mention text
    entity_type: Type of entity (e.g., "disease", "gene", "drug")

Returns:
    True if the term is marked as "known bad", False otherwise

### `def JsonFileCanonicalIdCache.get_metrics(self) -> dict[str, int]`

Get cache performance metrics.

Returns:
    Dictionary with metrics:
    - "hits": Number of cache hits
    - "misses": Number of cache misses
    - "known_bad": Number of known bad entries
    - "total_entries": Total number of successful entries in cache


<span id="user-content-kgraphcanonicalidlookuppy"></span>

# kgraph/canonical_id/lookup.py

Canonical ID lookup interface for promotion policies.

This module provides an abstract interface for looking up canonical IDs,
which promotion policies can use to assign canonical IDs to entities.

> Canonical ID lookup interface for promotion policies.

This module provides an abstract interface for looking up canonical IDs,
which promotion policies can use to assign canonical IDs to entities.


## `class CanonicalIdLookupInterface(ABC)`

Abstract interface for looking up canonical IDs.

This interface is used by promotion policies to look up canonical IDs
for entities. It abstracts away the details of how lookups are performed
(API calls, cache, etc.) so promotion policies can work with any lookup
implementation.

### `async def CanonicalIdLookupInterface.lookup(self, term: str, entity_type: str) -> Optional[CanonicalId]`

Look up a canonical ID for a term.

Args:
    term: The entity name/mention text
    entity_type: Type of entity (e.g., "disease", "gene", "drug")

Returns:
    CanonicalId if found, None otherwise

### `def CanonicalIdLookupInterface.lookup_sync(self, term: str, entity_type: str) -> Optional[CanonicalId]`

Synchronous version of lookup (for use in sync contexts).

Args:
    term: The entity name/mention text
    entity_type: Type of entity (e.g., "disease", "gene", "drug")

Returns:
    CanonicalId if found, None otherwise


<span id="user-content-kgraphcanonicalidmodelspy"></span>

# kgraph/canonical_id/models.py

Canonical ID cache interface for knowledge graph ingestion.

This module provides the CanonicalIdCacheInterface for caching canonical ID
lookups across different knowledge domains.

> Canonical ID cache interface for knowledge graph ingestion.

This module provides the CanonicalIdCacheInterface for caching canonical ID
lookups across different knowledge domains.


## `class CanonicalIdCacheInterface(ABC)`

Abstract interface for caching canonical ID lookups.

This interface allows different storage backends (JSON file, database, etc.)
to be used for caching canonical ID lookups. The cache stores mappings from
(term, entity_type) pairs to CanonicalId objects.

The cache supports:
- Loading and saving with a tag/identifier (for multi-domain support)
- Storing and fetching CanonicalId objects
- Marking terms as "known bad" (failed lookups that shouldn't be retried)
- Cache metrics (hits, misses, etc.)

Implementations should be performant since the cache's purpose is to avoid
expensive external API calls.

### `def CanonicalIdCacheInterface.load(self, tag: str) -> None`

Load cache from storage.

Args:
    tag: Identifier for the cache (e.g., "medlit", "sherlock", or a file path).
         For file-based caches, this might be a file path.
         For database caches, this might be a domain identifier.

### `def CanonicalIdCacheInterface.save(self, tag: str) -> None`

Save cache to storage.

Args:
    tag: Identifier for the cache (same as used in load()).

### `def CanonicalIdCacheInterface.store(self, term: str, entity_type: str, canonical_id: CanonicalId) -> None`

Store a canonical ID in the cache.

Args:
    term: The entity name/mention text (will be normalized internally)
    entity_type: Type of entity (e.g., "disease", "gene", "drug")
    canonical_id: The CanonicalId object to store

### `def CanonicalIdCacheInterface.fetch(self, term: str, entity_type: str) -> Optional[CanonicalId]`

Fetch a canonical ID from the cache.

Args:
    term: The entity name/mention text (will be normalized internally)
    entity_type: Type of entity (e.g., "disease", "gene", "drug")

Returns:
    CanonicalId if found in cache, None if not found or marked as "known bad"

### `def CanonicalIdCacheInterface.mark_known_bad(self, term: str, entity_type: str) -> None`

Mark a term as "known bad" (failed lookup, don't retry).

This allows the cache to remember that a lookup was attempted and failed,
so we don't waste time retrying it.

Args:
    term: The entity name/mention text (will be normalized internally)
    entity_type: Type of entity (e.g., "disease", "gene", "drug")

### `def CanonicalIdCacheInterface.is_known_bad(self, term: str, entity_type: str) -> bool`

Check if a term is marked as "known bad".

Args:
    term: The entity name/mention text (will be normalized internally)
    entity_type: Type of entity (e.g., "disease", "gene", "drug")

Returns:
    True if the term is marked as "known bad", False otherwise

### `def CanonicalIdCacheInterface.get_metrics(self) -> dict[str, int]`

Get cache performance metrics.

Returns:
    Dictionary with metrics such as:
    - "hits": Number of cache hits
    - "misses": Number of cache misses
    - "known_bad": Number of known bad entries
    - "total_entries": Total number of entries in cache

### `def CanonicalIdCacheInterface._normalize_key(self, term: str, entity_type: str) -> str`

Normalize cache key for consistent lookups.

Args:
    term: The entity name/mention text
    entity_type: Type of entity

Returns:
    Normalized cache key string (e.g., "disease:breast cancer")


<span id="user-content-kgraphclockpy"></span>

# kgraph/clock.py

## `class IngestionClock(BaseModel)`


**Fields:**

```python
now: datetime
```


<span id="user-content-kgraphcontextpy"></span>

# kgraph/context.py

## `class IngestionContext(BaseModel)`


**Fields:**

```python
domain: DomainSchema
clock: IngestionClock
document: BaseDocument
entities: EntityBuilder
relationships: RelationshipBuilder
```


<span id="user-content-kgraphexportpy"></span>

# kgraph/export.py

### `def get_git_hash() -> Optional[str]`

Gets the current git commit hash in short format.

This is used to version-stamp exported bundles, providing a precise
reference to the codebase state at the time of export.

Returns:
    The short git commit hash (e.g., "6b50d25") as a string, or `None`
    if the git command fails (e.g., not in a git repository).

### `def _collect_doc_assets(docs_source: Path, bundle_path: Path) -> List[DocAssetRow]`

Copies documentation assets from a source directory into the bundle.

This function recursively walks the `docs_source` directory, copies each
file to a `docs/` subdirectory within the `bundle_path`, and generates
a `DocAssetRow` for each copied file to be included in the bundle's
`doc_assets.jsonl`.

Note: These are human-readable documentation files (markdown, images, etc.),
NOT source documents (papers, articles) used for entity extraction.

Args:
    docs_source: The source directory containing the documentation assets
                 (e.g., Markdown files).
    bundle_path: The root directory of the bundle being created.

Returns:
    A list of `DocAssetRow` objects, one for each file copied.

### `def _entity_provenance_summary(accumulator: ProvenanceAccumulator) -> Dict[str, Dict[str, Any]]`

Build per-entity provenance summary from accumulator mentions (first_seen, total_mentions, supporting_documents).

### `def _relationship_evidence_summary(accumulator: ProvenanceAccumulator) -> Dict[str, Dict[str, Any]]`

Build per-relationship evidence summary from accumulator evidence.

### `async def JsonlGraphBundleExporter.export_graph_bundle(self, entity_storage: EntityStorageInterface, relationship_storage: RelationshipStorageInterface, bundle_path: Path, domain: str, label: Optional[str] = None, docs: Optional[Path] = None, description: Optional[str] = None, provenance_accumulator: Optional[ProvenanceAccumulator] = None) -> None`

Exports the graph content into a standardized JSONL bundle format.

This method orchestrates the entire bundle creation process. It reads
all entities and relationships from the provided storage interfaces,
serializes them into JSONL files (`entities.jsonl`, `relationships.jsonl`),
copies any associated document assets, and generates a `manifest.json`
file that describes the bundle's contents.

Args:
    entity_storage: The storage backend containing the entities.
    relationship_storage: The storage backend containing the relationships.
    bundle_path: The root directory where the bundle will be written.
    domain: The knowledge domain of the graph (e.g., "medlit").
    label: An optional human-readable label for the bundle.
    docs: An optional path to a directory of document assets to include.
    description: An optional description to include in the manifest.

### `async def write_bundle(entity_storage: EntityStorageInterface, relationship_storage: RelationshipStorageInterface, bundle_path: Path, domain: str, label: Optional[str] = None, docs: Optional[Path] = None, description: Optional[str] = None, provenance_accumulator: Optional[ProvenanceAccumulator] = None) -> None`

Writes a knowledge graph bundle to disk using the default exporter.

This function is a convenient wrapper around the `JsonlGraphBundleExporter`
that serializes entities and relationships into JSONL files and creates a
bundle manifest.

Args:
    entity_storage: The storage backend for retrieving entities.
    relationship_storage: The storage backend for retrieving relationships.
    bundle_path: The root directory where the bundle will be created.
    domain: The knowledge domain identifier for the graph (e.g., "medlit").
    label: An optional human-readable label for the bundle.
    docs: An optional path to a directory of document assets to copy
          into the bundle.
    description: An optional description to be included in the bundle's
                 manifest metadata.


<span id="user-content-kgraphingestpy"></span>

# kgraph/ingest.py

Two-pass ingestion orchestrator for the knowledge graph framework.

This module provides the `IngestionOrchestrator` class, which coordinates the
complete document ingestion pipeline. The orchestrator manages the two-pass
process that transforms raw documents into structured knowledge:

**Pass 1 - Entity Extraction:**
    1. Parse raw document bytes into structured `BaseDocument`
    2. Extract entity mentions using the configured `EntityExtractorInterface`
    3. Resolve mentions to canonical or provisional entities
    4. Generate embeddings for new entities
    5. Store entities, updating usage counts for existing ones

**Pass 2 - Relationship Extraction:**
    1. Extract relationships between resolved entities
    2. Validate relationships against the domain schema
    3. Store relationships with source document references

The orchestrator also provides methods for:
    - Batch ingestion of multiple documents
    - Entity promotion (provisional → canonical)
    - Duplicate detection via embedding similarity
    - Entity merging
    - JSON export of entities and relationships

Example usage:
    ```python
    orchestrator = IngestionOrchestrator(
        domain=my_domain_schema,
        parser=my_parser,
        entity_extractor=my_extractor,
        entity_resolver=my_resolver,
        relationship_extractor=my_rel_extractor,
        embedding_generator=my_embedder,
        entity_storage=entity_store,
        relationship_storage=rel_store,
        document_storage=doc_store,
    )

    result = await orchestrator.ingest_document(
        raw_content=document_bytes,
        content_type="text/plain",
    )
    print(f"Extracted {result.entities_extracted} entities")
    ```

> Two-pass ingestion orchestrator for the knowledge graph framework.

This module provides the `IngestionOrchestrator` class, which coordinates the
complete document ingestion pipeline. The orchestrator manages the two-pass
process that transforms raw documents into structured knowledge:

**Pass 1 - Entity Extraction:**
    1. Parse raw document bytes into structured `BaseDocument`
    2. Extract entity mentions using the configured `EntityExtractorInterface`
    3. Resolve mentions to canonical or provisional entities
    4. Generate embeddings for new entities
    5. Store entities, updating usage counts for existing ones

**Pass 2 - Relationship Extraction:**
    1. Extract relationships between resolved entities
    2. Validate relationships against the domain schema
    3. Store relationships with source document references

The orchestrator also provides methods for:
    - Batch ingestion of multiple documents
    - Entity promotion (provisional → canonical)
    - Duplicate detection via embedding similarity
    - Entity merging
    - JSON export of entities and relationships

Example usage:
    ```python
    orchestrator = IngestionOrchestrator(
        domain=my_domain_schema,
        parser=my_parser,
        entity_extractor=my_extractor,
        entity_resolver=my_resolver,
        relationship_extractor=my_rel_extractor,
        embedding_generator=my_embedder,
        entity_storage=entity_store,
        relationship_storage=rel_store,
        document_storage=doc_store,
    )

    result = await orchestrator.ingest_document(
        raw_content=document_bytes,
        content_type="text/plain",
    )
    print(f"Extracted {result.entities_extracted} entities")
    ```


### `def _record_relationship_evidence(accumulator: Optional[ProvenanceAccumulator], rel: BaseRelationship) -> None`

If accumulator and rel.evidence are set, record evidence rows.

## `class DocumentResult(BaseModel)`

Result of processing a single document through the ingestion pipeline.

Contains statistics about the extraction process and any errors encountered.
Immutable (frozen) to ensure results can be safely shared and stored.

Attributes:
    document_id: Unique identifier assigned to the parsed document.
    entities_extracted: Total number of entity mentions found in the document.
    entities_new: Number of mentions that created new provisional entities.
    entities_existing: Number of mentions that matched existing entities.
    relationships_extracted: Number of relationships stored from this document.
    errors: Tuple of error messages encountered during processing.
**Fields:**

```python
document_id: str
entities_extracted: int
entities_new: int
entities_existing: int
relationships_extracted: int
errors: tuple[str, ...]
```

## `class IngestionResult(BaseModel)`

Result of batch document ingestion.

Aggregates statistics across multiple documents and provides per-document
breakdown via the `document_results` field.

Attributes:
    documents_processed: Total number of documents in the batch.
    documents_failed: Number of documents that had errors during processing.
    total_entities_extracted: Sum of entity mentions across all documents.
    total_relationships_extracted: Sum of relationships across all documents.
    document_results: Per-document results for detailed inspection.
    errors: Top-level errors that prevented document processing.
**Fields:**

```python
documents_processed: int
documents_failed: int
total_entities_extracted: int
total_relationships_extracted: int
document_results: tuple[DocumentResult, ...]
errors: tuple[str, ...]
```

### `def _determine_canonical_id_source(canonical_id: str) -> str`

Determine the canonical_ids dict key from canonical_id format.

Args:
    canonical_id: The canonical ID string (e.g., "HGNC:1100", "MeSH:D001943", "C0006142")

Returns:
    Source key for canonical_ids dict (e.g., "hgnc", "mesh", "umls", "dbpedia")

## `class IngestionOrchestrator(BaseModel)`

Orchestrates two-pass document ingestion for knowledge graph construction.

The orchestrator is the main entry point for document processing. It
coordinates all pipeline components (parser, extractors, resolver,
embedding generator) and storage backends to transform raw documents
into structured knowledge graph data.

**Two-Pass Architecture:**

- **Pass 1 (Entity Extraction)**: Extracts entity mentions from documents,
  resolves them to canonical or provisional entities, generates embeddings,
  and updates storage with new entities or incremented usage counts.

- **Pass 2 (Relationship Extraction)**: Identifies relationships between
  the resolved entities and stores them with source document references.

**Additional Operations:**

- `run_promotion()`: Promotes provisional entities to canonical status
  based on usage frequency and confidence thresholds.
- `find_merge_candidates()`: Detects potential duplicate entities using
  embedding similarity.
- `merge_entities()`: Combines duplicate entities and updates references.
- `export_*()`: Exports entities and relationships to JSON files.

Attributes:
    domain: Schema defining entity types, relationship types, and validation.
    parser: Converts raw bytes to structured documents.
    entity_extractor: Extracts entity mentions from documents.
    entity_resolver: Maps mentions to canonical or provisional entities.
    relationship_extractor: Extracts relationships between entities.
    embedding_generator: Creates semantic vectors for similarity operations.
    entity_storage: Persistence backend for entities.
    relationship_storage: Persistence backend for relationships.
    document_storage: Persistence backend for source documents.
**Fields:**

```python
domain: DomainSchema
parser: DocumentParserInterface
entity_extractor: EntityExtractorInterface
entity_resolver: EntityResolverInterface
relationship_extractor: RelationshipExtractorInterface
embedding_generator: EmbeddingGeneratorInterface
entity_storage: EntityStorageInterface
relationship_storage: RelationshipStorageInterface
document_storage: DocumentStorageInterface
document_chunker: DocumentChunkerInterface | None
streaming_entity_extractor: StreamingEntityExtractorInterface | None
streaming_relationship_extractor: StreamingRelationshipExtractorInterface | None
provenance_accumulator: Optional[ProvenanceAccumulator]
```

### `async def IngestionOrchestrator.extract_entities_from_document(self, raw_content: bytes, content_type: str, source_uri: str | None = None) -> DocumentResult`

Runs the first pass of the ingestion pipeline on a single document.

This pass focuses on identifying, resolving, and storing entities. The
process includes:
1.  Parsing the raw content into a structured document.
2.  Extracting potential entity mentions from the document text.
3.  Resolving each mention to either an existing or a new entity.
4.  Generating a vector embedding for new entities.
5.  Storing new entities or updating the usage count of existing ones.

Args:
    raw_content: The raw byte content of the document to process.
    content_type: The MIME type of the document (e.g., "application/json").
    source_uri: An optional URI identifying the document's origin.

Returns:
    A `DocumentResult` object containing statistics about the entity
    extraction pass, including counts of new and existing entities,
    and any errors encountered.

### `async def IngestionOrchestrator.extract_relationships_from_document(self, raw_content: bytes, content_type: str, source_uri: str | None = None, document_id: str | None = None) -> DocumentResult`

Runs the second pass of the ingestion pipeline on a single document.

This pass focuses on identifying and storing relationships between
entities that have already been extracted and stored. The process includes:
1.  Retrieving the parsed document from storage or parsing it if needed.
2.  Fetching the set of entities previously extracted from this document.
3.  Extracting potential relationships between those entities.
4.  Validating and storing the extracted relationships.

Args:
    raw_content: The raw byte content of the document.
    content_type: The MIME type of the document.
    source_uri: An optional URI for finding the pre-existing document.
    document_id: The specific ID of the document to process. If provided,
                 it is used to fetch the exact document and its associated
                 entities, bypassing lookup by `source_uri`.

Returns:
    A `DocumentResult` object containing statistics about the relationship
    extraction pass and any errors encountered.

### `async def IngestionOrchestrator.ingest_document(self, raw_content: bytes, content_type: str, source_uri: str | None = None) -> DocumentResult`

Ingests a single document through the complete two-pass pipeline.

This convenience method orchestrates both the entity extraction pass and
the relationship extraction pass in sequence for a single document.
For more granular control over the ingestion process, such as running
promotion between passes, call `extract_entities_from_document` and
`extract_relationships_from_document` separately.

Args:
    raw_content: The raw byte content of the document to process.
    content_type: The MIME type of the document (e.g., "application/json").
    source_uri: An optional URI identifying the document's origin.

Returns:
    A `DocumentResult` object containing the combined statistics from
    both the entity and relationship extraction passes.

### `async def IngestionOrchestrator.ingest_batch(self, documents: Sequence[tuple[bytes, str, str | None]]) -> IngestionResult`

Ingests a batch of documents using the two-pass pipeline.

This method iterates through a sequence of documents and calls
`ingest_document` for each one, collecting the results.

Args:
    documents: A sequence of tuples, where each tuple contains the
               raw content, content type, and optional source URI
               for a single document.

Returns:
    An `IngestionResult` object containing aggregated statistics for the
    entire batch, as well as a list of individual `DocumentResult`
    objects.

### `async def IngestionOrchestrator._lookup_canonical_ids_batch(self, policy: PromotionPolicy, candidates: list[BaseEntity], logger: Any) -> dict[str, CanonicalId | None]`

Look up canonical IDs for all candidate entities in batches.

Args:
    policy: The promotion policy to use for lookups
    candidates: List of candidate entities
    logger: Logger instance

Returns:
    Dictionary mapping entity_id to CanonicalId or None

### `async def IngestionOrchestrator._promote_single_entity(self, entity: BaseEntity, entity_canonical_id_map: dict[str, CanonicalId | None], policy: PromotionPolicy, logger: Any) -> BaseEntity | None | bool`

Promote a single entity to canonical status.

Args:
    entity: The entity to promote
    entity_canonical_id_map: Map of entity_id to CanonicalId
    policy: The promotion policy
    logger: Logger instance

Returns:
    BaseEntity if successfully promoted, None if no canonical ID found,
    False if storage promotion failed

### `async def IngestionOrchestrator.run_promotion(self, lookup = None) -> list[BaseEntity]`

Promotes eligible provisional entities to canonical status.

This method orchestrates the promotion process, which is a critical
step between the entity and relationship extraction passes. It uses the
domain's configured `PromotionPolicy` to evaluate provisional entities
and upgrade them to canonical status if they meet the criteria.

The process involves:
1.  Identifying provisional entities that meet usage and confidence thresholds.
2.  Using the promotion policy (and optional lookup service) to assign
    a canonical ID to each candidate.
3.  Updating the entity's status and ID in storage.
4.  Updating all relationship references from the old provisional ID to
    the new canonical ID.

Args:
    lookup: An optional canonical ID lookup service (e.g., an API client)
            to be used by the promotion policy.

Returns:
    A list of the `BaseEntity` objects that were successfully promoted
    to canonical status during this run.

### `async def IngestionOrchestrator.find_merge_candidates(self, similarity_threshold: float = 0.95) -> list[tuple[BaseEntity, BaseEntity, float]]`

Finds potential duplicate entities based on embedding similarity.

This method scans all canonical entities that have an embedding, computes
the pairwise cosine similarity between them, and identifies pairs that
exceed a given threshold. This is useful for data cleaning and
maintaining graph quality.

Note:
    This performs an O(n²) comparison and can be computationally
    expensive for a large number of entities. For larger-scale
    applications, consider approximate nearest neighbor (ANN) search
    methods.

Args:
    similarity_threshold: The minimum cosine similarity score (between 0.0
        and 1.0) required to consider two entities a potential match.

Returns:
    A list of tuples, where each tuple contains two entity objects and
    their similarity score. `[(entity1, entity2, score), ...]`.

Example:
    ```python
    candidates = await orchestrator.find_merge_candidates(threshold=0.98)
    for e1, e2, sim in candidates:
        print(f"{e1.name} ↔ {e2.name}: {sim:.3f}")
    ```

### `async def IngestionOrchestrator.merge_entities(self, source_ids: Sequence[str], target_id: str) -> bool`

Merges one or more source entities into a single target entity.

This operation is crucial for deduplication and graph cleaning. It
combines data from the source entities into the target, updates all
relationship references to point to the target, and then deletes the
source entities.

The merge logic includes:
1.  Re-mapping all relationships from source entities to the target entity.
2.  Combining synonyms and summing usage counts.
3.  Delegating the core entity data merge and deletion to the storage backend.

Args:
    source_ids: A sequence of entity IDs to merge and then delete.
    target_id: The ID of the entity that will absorb the source entities.

Returns:
    `True` if the merge was successful, `False` otherwise (e.g., if
    the target entity does not exist).

Example:
    ```python
    # After finding merge candidates
    candidates = await orchestrator.find_merge_candidates()
    for e1, e2, sim in candidates:
        # Keep the entity with more usage, merge the other into it
        if e1.usage_count >= e2.usage_count:
            await orchestrator.merge_entities([e2.entity_id], e1.entity_id)
        else:
            await orchestrator.merge_entities([e1.entity_id], e2.entity_id)
    ```

### `def IngestionOrchestrator._serialize_entity(self, entity: BaseEntity) -> dict[str, Any]`

Serialize an entity to a JSON-compatible dictionary.

### `def IngestionOrchestrator._serialize_relationship(self, rel: BaseRelationship) -> dict[str, Any]`

Serialize a relationship to a JSON-compatible dictionary.

### `async def IngestionOrchestrator.export_entities(self, output_path: str | Path, include_provisional: bool = False) -> int`

Exports entities from storage to a JSON file.

Serializes entities into a JSON format, by default including only
canonical entities.

Args:
    output_path: The path where the JSON file will be saved.
    include_provisional: If `True`, includes both canonical and
                         provisional entities in the export. Defaults
                         to `False`.

Returns:
    The total number of entities exported.

### `async def IngestionOrchestrator.export_document(self, document_id: str, output_path: str | Path) -> dict[str, int]`

Exports data related to a single document to a JSON file.

This function gathers all relationships and provisional entities that
originated from a specific document and writes them to a file.

Args:
    document_id: The ID of the document to export data for.
    output_path: The path where the JSON file will be saved.

Returns:
    A dictionary containing the counts of exported relationships and
    provisional entities.

### `async def IngestionOrchestrator.export_all(self, output_dir: str | Path) -> dict[str, Any]`

Exports the entire graph into a directory of JSON files.

This method orchestrates a full export, creating a file for all
canonical entities and separate files for each document's specific
data (relationships and provisional entities).

The output directory will contain:
- `entities.json`: All canonical entities.
- `paper_{document_id}.json`: One file for each processed document.

Args:
    output_dir: The path to the directory where files will be saved.

Returns:
    A summary dictionary containing statistics about the export,
    including the number of entities and documents exported.


<span id="user-content-kgraphpipelineinitpy"></span>

# kgraph/pipeline/__init__.py

Public exports for extraction pipeline building blocks.

This package-level module re-exports the core interfaces and commonly used
implementations needed to assemble ingestion/extraction flows:

- Base parser/extractor/resolver interfaces from ``kgraph.pipeline.interfaces``
- Embedding interfaces and cache adapters used by resolution/promotions
- Streaming chunking/extraction utilities for large-document processing

Import from ``kgraph.pipeline`` when composing pipelines so downstream code can
depend on a stable, centralized surface area instead of deep module paths.

> Public exports for extraction pipeline building blocks.

This package-level module re-exports the core interfaces and commonly used
implementations needed to assemble ingestion/extraction flows:

- Base parser/extractor/resolver interfaces from ``kgraph.pipeline.interfaces``
- Embedding interfaces and cache adapters used by resolution/promotions
- Streaming chunking/extraction utilities for large-document processing

Import from ``kgraph.pipeline`` when composing pipelines so downstream code can
depend on a stable, centralized surface area instead of deep module paths.



<span id="user-content-kgraphpipelinecachingpy"></span>

# kgraph/pipeline/caching.py

Caching primitives for extraction-time embedding reuse.

Uses asyncio.Lock in concrete caches so that concurrent get/put/save/load
do not corrupt in-memory state. Lock is held only around critical sections
to avoid deadlock (e.g. get_batch calling get, put calling save).

This module provides abstractions for caching expensive computations, especially
embedding vectors generated during entity extraction and resolution. Caching is
critical for:

- **Cost reduction**: Avoiding repeated API calls to embedding providers
- **Performance**: Eliminating redundant computation for frequently-seen entities
- **Consistency**: Ensuring the same text always produces the same embedding
- **Offline operation**: Working with pre-computed embeddings without API access

Key abstractions:
    - EmbeddingsCacheInterface: Generic cache for text→embedding mappings
    - InMemoryEmbeddingsCache: Fast in-memory LRU cache
    - FileBasedEmbeddingsCache: Persistent JSON-based cache

Typical usage:
    ```python
    # Create cache with persistence
    cache = FileBasedEmbeddingsCache(cache_file="embeddings.json")
    await cache.load()

    # Wrap embedding generator with caching
    generator = CachedEmbeddingGenerator(
        base_generator=ollama_embedder,
        cache=cache
    )

    # Subsequent calls with same text use cached embeddings
    emb1 = await generator.generate("aspirin")  # API call
    emb2 = await generator.generate("aspirin")  # Cached, no API call
    ```

> Caching primitives for extraction-time embedding reuse.

Uses asyncio.Lock in concrete caches so that concurrent get/put/save/load
do not corrupt in-memory state. Lock is held only around critical sections
to avoid deadlock (e.g. get_batch calling get, put calling save).

This module provides abstractions for caching expensive computations, especially
embedding vectors generated during entity extraction and resolution. Caching is
critical for:

- **Cost reduction**: Avoiding repeated API calls to embedding providers
- **Performance**: Eliminating redundant computation for frequently-seen entities
- **Consistency**: Ensuring the same text always produces the same embedding
- **Offline operation**: Working with pre-computed embeddings without API access

Key abstractions:
    - EmbeddingsCacheInterface: Generic cache for text→embedding mappings
    - InMemoryEmbeddingsCache: Fast in-memory LRU cache
    - FileBasedEmbeddingsCache: Persistent JSON-based cache

Typical usage:
    ```python
    # Create cache with persistence
    cache = FileBasedEmbeddingsCache(cache_file="embeddings.json")
    await cache.load()

    # Wrap embedding generator with caching
    generator = CachedEmbeddingGenerator(
        base_generator=ollama_embedder,
        cache=cache
    )

    # Subsequent calls with same text use cached embeddings
    emb1 = await generator.generate("aspirin")  # API call
    emb2 = await generator.generate("aspirin")  # Cached, no API call
    ```


## `class EmbeddingCacheConfig(BaseModel)`

Configuration for embedding caching strategies.

Attributes:
    max_cache_size: Maximum number of embeddings to store in memory (for LRU eviction)
    cache_file: Path to persistent cache file (for file-based caches)
    auto_save_interval: Number of cache updates before auto-saving (0 = manual save only)
    normalize_keys: Whether to normalize cache keys (lowercase, strip whitespace)
    normalize_collapse_whitespace: When True, collapse internal whitespace to one space (optional).
**Fields:**

```python
max_cache_size: int
cache_file: Path | None
auto_save_interval: int
normalize_keys: bool
normalize_collapse_whitespace: bool
```

## `class EmbeddingsCacheInterface(ABC)`

Abstract interface for caching text embeddings.

Implementations provide different storage backends (memory, disk, database)
with consistent semantics. All implementations should:
    - Be thread-safe for concurrent access
    - Support batch operations for efficiency
    - Provide cache statistics (hits, misses, size)
    - Handle cache invalidation gracefully

Cache keys are text strings; values are embedding vectors (tuples of floats).

### `async def EmbeddingsCacheInterface.get(self, text: str) -> Optional[tuple[float, ...]]`

Retrieve a cached embedding for the given text.

Args:
    text: The text to look up

Returns:
    Embedding vector if found in cache, None otherwise

### `async def EmbeddingsCacheInterface.get_batch(self, texts: Sequence[str]) -> list[Optional[tuple[float, ...]]]`

Retrieve multiple cached embeddings.

Args:
    texts: Sequence of texts to look up

Returns:
    List of embeddings (or None for cache misses) in same order as texts

### `async def EmbeddingsCacheInterface.put(self, text: str, embedding: tuple[float, ...]) -> None`

Store an embedding in the cache.

Args:
    text: The text this embedding represents
    embedding: The embedding vector to store

### `async def EmbeddingsCacheInterface.put_batch(self, texts: Sequence[str], embeddings: Sequence[tuple[float, ...]]) -> None`

Store multiple embeddings efficiently.

Args:
    texts: Sequence of texts
    embeddings: Sequence of embedding vectors (same order as texts)

### `async def EmbeddingsCacheInterface.clear(self) -> None`

Clear all cached embeddings and reset statistics.

Implementations should reset hit/miss counters in addition to clearing
the cache contents to provide a clean slate for fresh cache usage tracking.

### `def EmbeddingsCacheInterface.get_stats(self) -> dict[str, int]`

Get cache statistics.

Returns:
    Dictionary with metrics like:
        - "hits": Number of successful cache lookups
        - "misses": Number of cache misses
        - "size": Current number of cached embeddings
        - "evictions": Number of items evicted (for LRU caches)

### `async def EmbeddingsCacheInterface.save(self) -> None`

Persist cache to storage (for persistent implementations).

No-op for in-memory-only caches.

### `async def EmbeddingsCacheInterface.load(self) -> None`

Load cache from storage (for persistent implementations).

No-op for in-memory-only caches.

### `def EmbeddingsCacheInterface._normalize_key(self, text: str) -> str`

Normalize cache key for consistent lookups.

Args:
    text: The text to normalize

Returns:
    Normalized text (lowercase, stripped whitespace)

## `class InMemoryEmbeddingsCache(EmbeddingsCacheInterface)`

In-memory LRU cache for embeddings.

Uses an OrderedDict to maintain LRU semantics with O(1) lookups and updates.
When the cache exceeds max_cache_size, the least recently used items are evicted.

This implementation is fast but non-persistent. Suitable for:
    - Short-lived processes
    - Testing
    - Hot cache layer in front of persistent storage

Example:
    ```python
    cache = InMemoryEmbeddingsCache(
        config=EmbeddingCacheConfig(max_cache_size=5000)
    )

    await cache.put("aspirin", embedding_vector)
    result = await cache.get("aspirin")  # Fast O(1) lookup
    ```

### `def InMemoryEmbeddingsCache.__init__(self, config: EmbeddingCacheConfig | None = None)`

Initialize the in-memory cache.

Args:
    config: Cache configuration. If None, uses default config.

### `def InMemoryEmbeddingsCache._normalize_key(self, text: str) -> str`

Normalize cache key; optionally collapse internal whitespace.

### `async def InMemoryEmbeddingsCache.get(self, text: str) -> Optional[tuple[float, ...]]`

Retrieve embedding from memory cache.

Args:
    text: The text to look up

Returns:
    Embedding vector if found, None otherwise

### `async def InMemoryEmbeddingsCache.get_batch(self, texts: Sequence[str]) -> list[Optional[tuple[float, ...]]]`

Retrieve multiple embeddings from cache.

Args:
    texts: Sequence of texts to look up

Returns:
    List of embeddings (or None for misses) in same order

### `async def InMemoryEmbeddingsCache.put(self, text: str, embedding: tuple[float, ...]) -> None`

Store embedding in memory cache.

Args:
    text: The text this embedding represents
    embedding: The embedding vector to store

### `async def InMemoryEmbeddingsCache.put_batch(self, texts: Sequence[str], embeddings: Sequence[tuple[float, ...]]) -> None`

Store multiple embeddings efficiently.

Args:
    texts: Sequence of texts
    embeddings: Sequence of embedding vectors (same order)

### `async def InMemoryEmbeddingsCache.clear(self) -> None`

Clear all cached embeddings and reset statistics.

Note: This method resets hit/miss/eviction counters in addition to
clearing the cache contents. Use get_stats() before calling clear()
if you need to preserve statistics.

### `def InMemoryEmbeddingsCache.get_stats(self) -> dict[str, int]`

Get cache statistics.

Returns:
    Dictionary with hits, misses, size, and evictions

### `async def InMemoryEmbeddingsCache.save(self) -> None`

No-op for in-memory cache (non-persistent).

### `async def InMemoryEmbeddingsCache.load(self) -> None`

No-op for in-memory cache (non-persistent).

## `class FileBasedEmbeddingsCache(EmbeddingsCacheInterface)`

Persistent file-based embeddings cache using JSON.

Stores embeddings in a JSON file with optional in-memory LRU cache for
hot data. The file format is:
    ```json
    {
        "aspirin": [0.1, 0.2, ..., 0.9],
        "ibuprofen": [0.3, 0.4, ..., 0.8],
        ...
    }
    ```

Features:
    - Persistent storage survives process restarts
    - Optional auto-save on every N updates
    - In-memory LRU cache for hot data
    - Atomic writes to prevent corruption

Example:
    ```python
    cache = FileBasedEmbeddingsCache(
        config=EmbeddingCacheConfig(
            cache_file=Path("embeddings.json"),
            max_cache_size=5000,
            auto_save_interval=100
        )
    )

    await cache.load()  # Load existing cache
    await cache.put("aspirin", embedding)
    # Auto-saves every 100 updates
    ```

### `def FileBasedEmbeddingsCache.__init__(self, config: EmbeddingCacheConfig)`

Initialize the file-based cache.

Args:
    config: Cache configuration including cache_file path

Raises:
    ValueError: If config.cache_file is None

### `def FileBasedEmbeddingsCache._normalize_key(self, text: str) -> str`

Normalize cache key; optionally collapse internal whitespace.

### `async def FileBasedEmbeddingsCache.get(self, text: str) -> Optional[tuple[float, ...]]`

Retrieve embedding from cache.

Args:
    text: The text to look up

Returns:
    Embedding vector if found, None otherwise

### `async def FileBasedEmbeddingsCache.get_batch(self, texts: Sequence[str]) -> list[Optional[tuple[float, ...]]]`

Retrieve multiple embeddings from cache.

Args:
    texts: Sequence of texts to look up

Returns:
    List of embeddings (or None for misses) in same order

### `async def FileBasedEmbeddingsCache.put(self, text: str, embedding: tuple[float, ...]) -> None`

Store embedding in cache.

Args:
    text: The text this embedding represents
    embedding: The embedding vector to store

### `async def FileBasedEmbeddingsCache.put_batch(self, texts: Sequence[str], embeddings: Sequence[tuple[float, ...]]) -> None`

Store multiple embeddings efficiently.

Args:
    texts: Sequence of texts
    embeddings: Sequence of embedding vectors (same order)

### `async def FileBasedEmbeddingsCache.clear(self) -> None`

Clear all cached embeddings and reset statistics.

Note: This method resets hit/miss/eviction counters in addition to
clearing the cache contents. Use get_stats() before calling clear()
if you need to preserve statistics.

### `def FileBasedEmbeddingsCache.get_stats(self) -> dict[str, int]`

Get cache statistics.

Returns:
    Dictionary with hits, misses, size, and evictions

### `async def FileBasedEmbeddingsCache.save(self) -> None`

Persist cache to JSON file.

Uses atomic write (write to temp file, then rename) to prevent corruption.

### `async def FileBasedEmbeddingsCache.load(self) -> None`

Load cache from JSON file.

If file doesn't exist, starts with empty cache.
Keys are normalized on load when normalize_keys is True so lookups match.

## `class CachedEmbeddingGenerator(EmbeddingGeneratorInterface)`

Wraps an embedding generator with transparent caching.

This adapter provides a cache layer in front of any EmbeddingGeneratorInterface
implementation. Cache hits avoid API calls entirely, providing:
    - Significant cost savings for frequently-seen texts
    - Faster response times
    - Consistent embeddings (no variation from API)
    - Offline operation for cached texts

The cache is transparent to callers - the interface is identical to the
underlying generator.

Example:
    ```python
    # Wrap any embedding generator with caching
    cache = FileBasedEmbeddingsCache(
        config=EmbeddingCacheConfig(cache_file=Path("cache.json"))
    )
    await cache.load()

    cached_gen = CachedEmbeddingGenerator(
        base_generator=ollama_embedder,
        cache=cache
    )

    # First call hits API and caches result
    emb1 = await cached_gen.generate("aspirin")

    # Second call uses cached result
    emb2 = await cached_gen.generate("aspirin")  # No API call!
    ```

### `def CachedEmbeddingGenerator.__init__(self, base_generator: EmbeddingGeneratorInterface, cache: EmbeddingsCacheInterface)`

Initialize the cached generator.

Args:
    base_generator: The underlying embedding generator
    cache: The cache to use for storing/retrieving embeddings

### `def CachedEmbeddingGenerator.dimension(self) -> int`

Return embedding dimension from base generator.

Returns:
    Embedding dimension (e.g., 1536, 1024)

### `async def CachedEmbeddingGenerator.generate(self, text: str) -> tuple[float, ...]`

Generate embedding with caching.

Checks cache first. If miss, generates embedding and caches it.

Args:
    text: Text to embed

Returns:
    Embedding vector

### `async def CachedEmbeddingGenerator.generate_batch(self, texts: Sequence[str]) -> list[tuple[float, ...]]`

Generate embeddings in batch with caching.

Checks cache for all texts first, then only generates embeddings
for cache misses. This minimizes API calls.

Args:
    texts: Sequence of texts to embed

Returns:
    List of embedding vectors in same order as texts

### `async def CachedEmbeddingGenerator.save_cache(self) -> None`

Persist cache to storage.

Convenience method for explicit cache persistence.

### `def CachedEmbeddingGenerator.get_cache_stats(self) -> dict[str, int]`

Get cache statistics.

Returns:
    Dictionary with cache metrics


<span id="user-content-kgraphpipelineembeddingpy"></span>

# kgraph/pipeline/embedding.py

Embedding generation contracts used by extraction and entity resolution.

This module defines the interface for generating semantic vector embeddings,
which are dense numerical representations of text that capture meaning.
Embeddings enable several key knowledge graph operations:

- **Entity resolution**: Match entity mentions to existing entities with
  similar meanings but different surface forms (e.g., "heart attack" vs
  "myocardial infarction").

- **Duplicate detection**: Identify canonical entities that should be merged
  by finding pairs with high embedding similarity.

- **Semantic search**: Query the knowledge graph by meaning rather than
  exact text matching.

Implementations typically wrap embedding APIs such as:
    - OpenAI text-embedding-3-small/large
    - Cohere embed-english-v3.0
    - Sentence Transformers (local models)
    - Domain-specific embeddings (BioBERT, LegalBERT, etc.)

> Embedding generation contracts used by extraction and entity resolution.

This module defines the interface for generating semantic vector embeddings,
which are dense numerical representations of text that capture meaning.
Embeddings enable several key knowledge graph operations:

- **Entity resolution**: Match entity mentions to existing entities with
  similar meanings but different surface forms (e.g., "heart attack" vs
  "myocardial infarction").

- **Duplicate detection**: Identify canonical entities that should be merged
  by finding pairs with high embedding similarity.

- **Semantic search**: Query the knowledge graph by meaning rather than
  exact text matching.

Implementations typically wrap embedding APIs such as:
    - OpenAI text-embedding-3-small/large
    - Cohere embed-english-v3.0
    - Sentence Transformers (local models)
    - Domain-specific embeddings (BioBERT, LegalBERT, etc.)


## `class EmbeddingGeneratorInterface(ABC)`

Generate semantic vector embeddings for text.

This interface abstracts embedding generation, allowing the knowledge
graph framework to work with any embedding provider. Implementations
should be stateless and thread-safe.

The embedding vectors are stored as immutable tuples of floats to ensure
they can be safely shared and used as dictionary keys or set members.

Typical usage:
    ```python
    embedder = OpenAIEmbedding(client, model="text-embedding-3-small")
    embedding = await embedder.generate("aspirin")
    similar_entities = await storage.find_by_embedding(embedding, threshold=0.85)
    ```

When implementing:
    - Handle empty strings gracefully (return zero vector or raise)
    - Consider rate limiting and retries for API-based implementations
    - Normalize vectors if the similarity search requires it

### `def EmbeddingGeneratorInterface.dimension(self) -> int`

Return the dimensionality of generated embeddings.

This property is essential for:
    - Storage backends that need to configure vector columns/indices
    - Validation that embeddings match expected dimensions
    - Memory estimation for batch operations

The dimension depends on the underlying model:
    - OpenAI text-embedding-3-small: 1536
    - OpenAI text-embedding-3-large: 3072
    - Sentence Transformers all-MiniLM-L6-v2: 384

Returns:
    Integer dimension of embedding vectors (e.g., 1536, 3072).

### `async def EmbeddingGeneratorInterface.generate(self, text: str) -> tuple[float, ...]`

Generate an embedding vector for a single text string.

Transforms the input text into a dense vector representation that
captures its semantic meaning. Similar texts produce vectors with
high cosine similarity.

Args:
    text: Input text to embed. May be a single word, phrase, sentence,
        or paragraph. Very long texts may be truncated by the underlying
        model.

Returns:
    Embedding vector as an immutable tuple of floats with length
    equal to self.dimension. Values are typically in the range [-1, 1]
    for normalized embeddings.

Raises:
    ValueError: If text is empty (implementation-dependent).
    RuntimeError: If the embedding API call fails.

### `async def EmbeddingGeneratorInterface.generate_batch(self, texts: Sequence[str]) -> list[tuple[float, ...]]`

Generate embeddings for multiple texts efficiently.

Batch generation is significantly more efficient than calling
generate() repeatedly, especially for API-based implementations
that support batch requests.

Use batch generation when:
    - Processing multiple entity mentions from a document
    - Computing embeddings for entity promotion candidates
    - Initializing embeddings for imported entities

Args:
    texts: Sequence of input texts to embed. Order is preserved
        in the output.

Returns:
    List of embedding vectors in the same order as input texts.
    Each vector is a tuple of floats with length self.dimension.

Raises:
    ValueError: If texts is empty or contains empty strings
        (implementation-dependent).
    RuntimeError: If the embedding API call fails.


<span id="user-content-kgraphpipelineinterfacespy"></span>

# kgraph/pipeline/interfaces.py

Core interfaces for the two-pass extraction pipeline.

This module defines the abstract interfaces for the two-pass ingestion pipeline:

- **Pass 1 (Entity Extraction)**: Parse documents, extract entity mentions,
  and resolve them to canonical or provisional entities.
- **Pass 2 (Relationship Extraction)**: Identify relationships/edges between
  the resolved entities within each document.

The pipeline components are designed to be pluggable, allowing different
implementations for different domains (medical literature, legal documents,
academic papers, etc.) or different underlying technologies (LLMs, NER models,
rule-based extractors).

Typical flow:
    1. DocumentParserInterface converts raw bytes to BaseDocument
    2. EntityExtractorInterface identifies EntityMention instances
    3. EntityResolverInterface maps mentions to BaseEntity instances
    4. RelationshipExtractorInterface finds relationships between entities

> Core interfaces for the two-pass extraction pipeline.

This module defines the abstract interfaces for the two-pass ingestion pipeline:

- **Pass 1 (Entity Extraction)**: Parse documents, extract entity mentions,
  and resolve them to canonical or provisional entities.
- **Pass 2 (Relationship Extraction)**: Identify relationships/edges between
  the resolved entities within each document.

The pipeline components are designed to be pluggable, allowing different
implementations for different domains (medical literature, legal documents,
academic papers, etc.) or different underlying technologies (LLMs, NER models,
rule-based extractors).

Typical flow:
    1. DocumentParserInterface converts raw bytes to BaseDocument
    2. EntityExtractorInterface identifies EntityMention instances
    3. EntityResolverInterface maps mentions to BaseEntity instances
    4. RelationshipExtractorInterface finds relationships between entities


## `class DocumentParserInterface(ABC)`

Parse raw documents into structured BaseDocument instances.

Implementations handle format-specific parsing (PDF, HTML, plain text, etc.)
and extract document metadata such as title, author, publication date, and
structural elements like sections and paragraphs.

This is the entry point for the ingestion pipeline. The parsed document
provides the content that subsequent extractors process.

Example implementations might use:
    - PDF parsing libraries (PyMuPDF, pdfplumber)
    - HTML parsing (BeautifulSoup, lxml)
    - LLMs for structure extraction from unstructured text

### `async def DocumentParserInterface.parse(self, raw_content: bytes, content_type: str, source_uri: str | None = None) -> BaseDocument`

Parse raw content into a structured document.

Args:
    raw_content: Raw document bytes (may be UTF-8 text, PDF binary, etc.)
    content_type: MIME type or format indicator (e.g., 'text/plain',
        'application/pdf', 'text/html') used to select parsing strategy
    source_uri: Optional URI identifying the document's origin, useful
        for deduplication and provenance tracking

Returns:
    A BaseDocument instance with extracted content and metadata,
    ready for entity and relationship extraction.

Raises:
    ValueError: If content_type is unsupported or content is malformed.

## `class EntityExtractorInterface(ABC)`

Extract entity mentions from documents (Pass 1 of ingestion).

This interface handles the first pass of document processing: identifying
spans of text that refer to entities of interest. The output is a list of
EntityMention objects representing raw extractions that have not yet been
resolved to canonical or provisional entities.

Entity mentions capture:
    - The exact text span and its position in the document
    - The inferred entity type (domain-specific, e.g., 'drug', 'gene', 'person')
    - Extraction confidence score
    - Surrounding context for disambiguation

Implementations may use:
    - Named Entity Recognition (NER) models (spaCy, Hugging Face transformers)
    - Large Language Models with structured extraction prompts
    - Rule-based pattern matching for domain-specific entities
    - Hybrid approaches combining multiple techniques

### `async def EntityExtractorInterface.extract(self, document: BaseDocument) -> list[EntityMention]`

Extract entity mentions from a document.

Scans the document content to identify text spans that refer to
entities of interest. Does not perform resolution—that is handled
separately by EntityResolverInterface.

Args:
    document: The parsed document to extract entities from.

Returns:
    List of EntityMention objects, each representing a detected
    entity reference with its text, position, type, and confidence.
    Returns an empty list if no entities are found.

## `class EntityResolverInterface(ABC)`

Resolve entity mentions to canonical or provisional entities.

After extraction, entity mentions must be resolved to determine whether
they refer to existing known entities or represent new discoveries. This
interface handles the resolution process through multiple strategies:

1. **Name/synonym matching**: Check if the mention text matches known
   entity names or synonyms in storage.
2. **Embedding similarity**: Use semantic vector similarity to find
   entities with similar meaning but different surface forms.
3. **External authority lookup**: Query authoritative sources (UMLS for
   medical terms, DBPedia for general knowledge, etc.) to obtain
   canonical identifiers.
4. **Provisional creation**: If no match is found, create a provisional
   entity that may later be promoted to canonical status based on
   usage frequency and confidence scores.

The confidence score returned with each resolution indicates the certainty
of the match, enabling downstream filtering and quality control.

### `async def EntityResolverInterface.resolve(self, mention: EntityMention, existing_storage: EntityStorageInterface) -> tuple[BaseEntity, float]`

Resolve a single entity mention to an entity.

Attempts to match the mention to existing canonical entities using
name matching, embedding similarity, or external authority lookup.
If no suitable match is found, creates a new provisional entity.

Args:
    mention: The extracted entity mention to resolve.
    existing_storage: Storage interface to query for existing entities.
        Used for name lookups and embedding similarity searches.

Returns:
    A tuple of (resolved_entity, confidence_score) where:
        - resolved_entity: Either an existing entity from storage,
          a newly created canonical entity from an authority lookup,
          or a newly created provisional entity.
        - confidence_score: Float between 0 and 1 indicating the
          certainty of the resolution. Higher scores indicate stronger
          matches; provisional entities typically have lower scores.

### `async def EntityResolverInterface.resolve_batch(self, mentions: Sequence[EntityMention], existing_storage: EntityStorageInterface) -> list[tuple[BaseEntity, float]]`

Resolve multiple entity mentions efficiently.

Batch resolution enables optimizations such as:
    - Batched embedding generation (single API call for all mentions)
    - Batched similarity searches against vector storage
    - Parallel authority lookups
    - Deduplication within the batch

Args:
    mentions: Sequence of entity mentions to resolve.
    existing_storage: Storage interface to query for existing entities.

Returns:
    List of (entity, confidence) tuples in the same order as input
    mentions. Each tuple follows the same semantics as resolve().

## `class RelationshipExtractorInterface(ABC)`

Extract relationships between entities from documents (Pass 2 of ingestion).

After entities have been extracted and resolved, this interface identifies
the relationships (edges) between them within the document context. This
is the second pass of the ingestion pipeline.

Relationships are typically expressed as (subject, predicate, object) triples
with additional metadata such as:
    - Source document reference for provenance
    - Confidence score for the extraction
    - Supporting evidence (text spans, context)

The predicate vocabulary is typically domain-specific:
    - Medical: 'treats', 'causes', 'interacts_with', 'inhibits'
    - Legal: 'cites', 'overrules', 'amends', 'references'
    - Academic: 'authored_by', 'cites', 'builds_upon', 'contradicts'

Implementations may use:
    - LLMs with structured prompts listing entities and requesting triples
    - Dependency parsing to identify syntactic relationships
    - Pattern-based extraction using domain-specific templates
    - Pre-trained relation extraction models

### `async def RelationshipExtractorInterface.extract(self, document: BaseDocument, entities: Sequence[BaseEntity]) -> list[BaseRelationship]`

Extract relationships between entities in a document.

Analyzes the document content in the context of the provided entities
to identify relationships. Only considers relationships between the
given entities (not arbitrary text spans).

Args:
    document: The source document providing context for extraction.
    entities: The resolved entities from this document. Relationships
        will only be extracted between entities in this sequence.

Returns:
    List of BaseRelationship objects representing the extracted
    relationships. Each relationship includes subject/object entity
    references, predicate type, confidence score, and source document
    reference. Returns an empty list if no relationships are found.


<span id="user-content-kgraphpipelinellmclientpy"></span>

# kgraph/pipeline/llm_client.py

LLM client interfaces and Ollama implementation for extraction passes.

This module defines the shared async contract used by extraction components that
need model completions (plain text, structured JSON, or tool-calling flows), and
ships the default Ollama-backed implementation used in local/offline pipelines.

Rate limiting: OllamaLLMClient enforces a minimum interval between the start of any
two contiguous requests (default 3s, configurable via LLM_MIN_REQUEST_INTERVAL_SECONDS
or the min_request_interval_seconds constructor arg). The throttle is process-global
(shared across all threads and all OllamaLLMClient instances) so the server-side rate
limit is respected regardless of which code path or worker issues the request.

> LLM client interfaces and Ollama implementation for extraction passes.

This module defines the shared async contract used by extraction components that
need model completions (plain text, structured JSON, or tool-calling flows), and
ships the default Ollama-backed implementation used in local/offline pipelines.

Rate limiting: OllamaLLMClient enforces a minimum interval between the start of any
two contiguous requests (default 3s, configurable via LLM_MIN_REQUEST_INTERVAL_SECONDS
or the min_request_interval_seconds constructor arg). The throttle is process-global
(shared across all threads and all OllamaLLMClient instances) so the server-side rate
limit is respected regardless of which code path or worker issues the request.


### `def _ensure_global_interval_sync(interval_seconds: float) -> None`

Ensure at least interval_seconds since the last request start (process-wide); sleep if needed.

## `class LLMTimeoutError(TimeoutError)`

Raised when an LLM request (e.g. Ollama) exceeds the configured timeout.

Ingestion should treat this as a hard failure: abort the run, do not save
bundle or caches, and exit loudly.

## `class LLMClientInterface(ABC)`

Abstract interface for LLM clients.

### `async def LLMClientInterface.generate(self, prompt: str, temperature: float = 0.1, max_tokens: Optional[int] = None) -> str`

Generate text completion from a prompt.

### `async def LLMClientInterface.generate_json(self, prompt: str, temperature: float = 0.1) -> dict[str, Any] | list[Any]`

Generate structured JSON response from a prompt.

### `async def LLMClientInterface.generate_json_with_raw(self, prompt: str, temperature: float = 0.1) -> tuple[dict[str, Any] | list[Any], str]`

Generate structured JSON response AND return the raw model text.

### `async def LLMClientInterface.generate_json_with_tools(self, prompt: str, tools: list[Callable], temperature: float = 0.1) -> dict[str, Any] | list[Any]`

Generate JSON with tool calling support. Default: fall back to generate_json.

### `def _default_min_request_interval() -> float`

Minimum seconds between the start of any two contiguous LLM requests (for rate limiting).

## `class OllamaLLMClient(LLMClientInterface)`

Ollama LLM client implementation.

### `def OllamaLLMClient.__init__(self, model: str = 'llama3.1:8b', host: str = 'http://localhost:11434', timeout: float = 300.0, min_request_interval_seconds: Optional[float] = None, json_system_prompt: Optional[str] = None, tool_system_prompt: Optional[str] = None)`

Initialize Ollama client.

Args:
    model: Ollama model name.
    host: Ollama server URL.
    timeout: Request timeout in seconds (default: 300).
    min_request_interval_seconds: Rate limiting interval. Default from env.
    json_system_prompt: System prompt for generate_json. Default: generic extraction expert.
    tool_system_prompt: System prompt for generate_json_with_tools. Default: generic.

### `def OllamaLLMClient._ensure_interval_sync(self) -> None`

Ensure at least min_request_interval seconds since the last request start (process-global).

### `def OllamaLLMClient._parse_json_from_text(self, response_text: str) -> dict[str, Any] | list[Any]`

Extract and parse JSON from response text.

### `async def OllamaLLMClient.generate(self, prompt: str, temperature: float = 0.1, max_tokens: Optional[int] = None) -> str`

Generate text using Ollama.

### `async def OllamaLLMClient._call_llm_for_json(self, prompt: str, temperature: float = 0.1) -> str`

Call LLM and return raw response text (internal helper).

### `async def OllamaLLMClient.generate_json(self, prompt: str, temperature: float = 0.1) -> dict[str, Any] | list[Any]`

Generate structured JSON response from a prompt.

### `async def OllamaLLMClient.generate_json_with_raw(self, prompt: str, temperature: float = 0.1) -> tuple[dict[str, Any] | list[Any], str]`

Generate structured JSON response AND return the raw model text.

### `async def OllamaLLMClient.generate_json_with_tools(self, prompt: str, tools: list[Callable], temperature: float = 0.1, max_tool_iterations: int = 10) -> dict[str, Any] | list[Any]`

Generate JSON with Ollama tool calling support.


<span id="user-content-kgraphpipelineollamaembeddingpy"></span>

# kgraph/pipeline/ollama_embedding.py

Ollama-backed embedding generator for extraction pipeline components.

This module provides a concrete ``EmbeddingGeneratorInterface`` implementation
that calls Ollama's ``/api/embed`` endpoint for both single-item and batched
embedding generation, enabling local vectorization for entity resolution and
similarity-driven graph operations.

> Ollama-backed embedding generator for extraction pipeline components.

This module provides a concrete ``EmbeddingGeneratorInterface`` implementation
that calls Ollama's ``/api/embed`` endpoint for both single-item and batched
embedding generation, enabling local vectorization for entity resolution and
similarity-driven graph operations.


## `class OllamaEmbeddingGenerator(EmbeddingGeneratorInterface)`

Embedding generator using Ollama.

Uses Ollama's /api/embed API. Supports single text or batch of texts
in one request. Default model is nomic-embed-text; mxbai-embed-large
also works well.

### `def OllamaEmbeddingGenerator.dimension(self) -> int`

Return embedding dimension for the model.

Common dimensions:
- nomic-embed-text: 768
- mxbai-embed-large: 1024
- bge-large: 1024

### `async def OllamaEmbeddingGenerator.generate(self, text: str) -> tuple[float, ...]`

Generate embedding for a single text using Ollama /api/embed.

### `async def OllamaEmbeddingGenerator._request_batch(self, texts: list[str]) -> list[tuple[float, ...]]`

One HTTP request for one or more texts. Response order matches input order.

### `async def OllamaEmbeddingGenerator.generate_batch(self, texts: Sequence[str]) -> list[tuple[float, ...]]`

Generate embeddings for multiple texts in one request when possible.


<span id="user-content-kgraphpipelinepass1llmpy"></span>

# kgraph/pipeline/pass1_llm.py

Pass 1 LLM adapters and backend factory for extraction runs.

Pass 1 uses an LLM to produce structured JSON from paper text (entities,
relationships, and metadata). This module centralizes backend-specific adapter
logic (Anthropic/OpenAI/Ollama), response parsing, and runtime backend selection
via CLI/env configuration.

Set backend via ``--llm-backend`` or ``LLM_BACKEND``; provide API keys via
environment (``ANTHROPIC_API_KEY``, ``OPENAI_API_KEY``) or ``.env``.

> Pass 1 LLM adapters and backend factory for extraction runs.

Pass 1 uses an LLM to produce structured JSON from paper text (entities,
relationships, and metadata). This module centralizes backend-specific adapter
logic (Anthropic/OpenAI/Ollama), response parsing, and runtime backend selection
via CLI/env configuration.

Set backend via ``--llm-backend`` or ``LLM_BACKEND``; provide API keys via
environment (``ANTHROPIC_API_KEY``, ``OPENAI_API_KEY``) or ``.env``.


## `class Pass1LLMInterface(ABC)`

Interface for Pass 1 LLM: generate JSON from system + user message.

### `async def Pass1LLMInterface.generate_json(self, system_prompt: str, user_message: str, temperature: float = 0.1, max_tokens: int = 16384) -> dict[str, Any]`

Return a single JSON object (e.g. per-paper bundle).

### `def _parse_json_from_text(response_text: str) -> dict[str, Any]`

Extract and parse a JSON object from response text.

Brace counting skips { and } inside JSON string literals so that text spans
containing braces (e.g. "The {gene} increases risk") do not break parsing.
Falls back to json-repair if the strict parse fails.

## `class AnthropicPass1LLM(Pass1LLMInterface)`

Pass 1 LLM using Anthropic (Claude) API.

## `class OpenAIPass1LLM(Pass1LLMInterface)`

Pass 1 LLM using OpenAI API or OpenAI-compatible endpoint (e.g. Lambda Labs).

## `class OllamaPass1LLM(Pass1LLMInterface)`

Pass 1 LLM using existing Ollama client (generate_json).

### `def OllamaPass1LLM.__init__(self, ollama_client: Any)`

ollama_client must have async generate_json(prompt, temperature) -> dict|list.

### `def get_pass1_llm(backend: str) -> Pass1LLMInterface`

Return a Pass 1 LLM for the given backend.

backend: "anthropic" | "openai" | "ollama"
model: Override default model.
base_url: For OpenAI-compatible endpoints (e.g. Lambda Labs).
ollama_client: For backend "ollama", an OllamaLLMClient instance.


<span id="user-content-kgraphpipelinestreamingpy"></span>

# kgraph/pipeline/streaming.py

Streaming extraction interfaces for large-document processing.

This module provides abstractions for processing documents in a streaming fashion,
breaking them into manageable chunks (windows) that can be processed incrementally.
This is essential for:

- **Large documents**: Processing documents that exceed LLM context windows
- **Memory efficiency**: Avoiding loading entire documents into memory
- **Incremental processing**: Starting extraction before full document is parsed
- **Context preservation**: Using overlapping windows to maintain entity/relationship
  context across chunk boundaries

The design follows the patterns established in the plod branch for PMC XML streaming,
providing generic abstractions that work across different document formats.

Key abstractions:
    - DocumentChunker: Splits documents into overlapping chunks/windows
    - StreamingEntityExtractor: Extracts entities from document chunks with deduplication
    - StreamingRelationshipExtractor: Extracts relationships within windows

Typical usage:
    ```python
    chunker = WindowedDocumentChunker(chunk_size=2000, overlap=200)
    chunks = await chunker.chunk(document)

    extractor = BatchingEntityExtractor(base_extractor, batch_size=10)
    all_mentions = []
    async for chunk_mentions in extractor.extract_streaming(chunks):
        all_mentions.extend(chunk_mentions)
    ```

Based on the streaming extraction patterns from:
    - medlit/medlit/pipeline/pmc_streaming.py (plod branch)
    - medlit/medlit/pipeline/mentions.py (windowed entity extraction)

> Streaming extraction interfaces for large-document processing.

This module provides abstractions for processing documents in a streaming fashion,
breaking them into manageable chunks (windows) that can be processed incrementally.
This is essential for:

- **Large documents**: Processing documents that exceed LLM context windows
- **Memory efficiency**: Avoiding loading entire documents into memory
- **Incremental processing**: Starting extraction before full document is parsed
- **Context preservation**: Using overlapping windows to maintain entity/relationship
  context across chunk boundaries

The design follows the patterns established in the plod branch for PMC XML streaming,
providing generic abstractions that work across different document formats.

Key abstractions:
    - DocumentChunker: Splits documents into overlapping chunks/windows
    - StreamingEntityExtractor: Extracts entities from document chunks with deduplication
    - StreamingRelationshipExtractor: Extracts relationships within windows

Typical usage:
    ```python
    chunker = WindowedDocumentChunker(chunk_size=2000, overlap=200)
    chunks = await chunker.chunk(document)

    extractor = BatchingEntityExtractor(base_extractor, batch_size=10)
    all_mentions = []
    async for chunk_mentions in extractor.extract_streaming(chunks):
        all_mentions.extend(chunk_mentions)
    ```

Based on the streaming extraction patterns from:
    - medlit/medlit/pipeline/pmc_streaming.py (plod branch)
    - medlit/medlit/pipeline/mentions.py (windowed entity extraction)


## `class DocumentChunk(BaseModel)`

Represents a chunk/window of a document.

Chunks may overlap to preserve context across boundaries. For example,
a document split with 2000-character chunks and 200-character overlap
ensures entities mentioned near chunk boundaries aren't missed.

Attributes:
    content: The text content of this chunk
    start_offset: Character offset where this chunk starts in the original document
    end_offset: Character offset where this chunk ends in the original document
    chunk_index: Sequential index of this chunk (0-based)
    document_id: ID of the parent document
    metadata: Optional chunk-specific metadata (section name, page number, etc.)
**Fields:**

```python
content: str
start_offset: int
end_offset: int
chunk_index: int
document_id: str
metadata: dict[str, str]
```

## `class ChunkingConfig(BaseModel)`

Configuration for document chunking strategies.

Attributes:
    chunk_size: Target size of each chunk in characters
    overlap: Number of characters to overlap between consecutive chunks
    respect_boundaries: Whether to respect sentence/paragraph boundaries
    min_chunk_size: Minimum size for a chunk (to avoid tiny trailing chunks)
**Fields:**

```python
chunk_size: int
overlap: int
respect_boundaries: bool
min_chunk_size: int
```

## `class DocumentChunkerInterface(ABC)`

Interface for splitting documents into processable chunks.

Implementations handle different chunking strategies:
    - Fixed-size chunks with overlap
    - Semantic chunking (paragraph/section boundaries)
    - Token-based chunking (for LLM token limits)
    - Hybrid approaches

The chunker preserves document structure and maintains metadata for
reconstructing entity positions in the original document.

Optional: implement chunk_from_raw() for memory-efficient chunking from
raw bytes (e.g. PMC XML via iterparse) without loading the full document.

### `async def DocumentChunkerInterface.chunk(self, document: BaseDocument) -> list[DocumentChunk]`

Split a document into chunks.

Args:
    document: The document to split into chunks

Returns:
    List of DocumentChunk objects in document order

### `async def DocumentChunkerInterface.chunk_from_raw(self, raw_content: bytes, content_type: str, document_id: str, source_uri: str | None = None) -> list[DocumentChunk]`

Chunk from raw bytes without parsing the full document (optional).

Override this to support memory-efficient chunking (e.g. PMC XML
via iterparse). Default implementation raises NotImplementedError.

Args:
    raw_content: Raw byte content of the document.
    content_type: MIME type (e.g. "application/xml").
    document_id: Document ID to assign to produced chunks.
    source_uri: Optional source URI (e.g. file path).

Returns:
    List of DocumentChunk objects in order.

Raises:
    NotImplementedError: If this chunker does not support raw chunking.

## `class WindowedDocumentChunker(DocumentChunkerInterface)`

Chunks documents into overlapping fixed-size windows.

This implementation uses a simple sliding window approach with configurable
overlap. Optionally respects sentence boundaries to avoid breaking entities
mid-sentence.

Example:
    ```python
    chunker = WindowedDocumentChunker(
        config=ChunkingConfig(chunk_size=2000, overlap=200)
    )
    chunks = await chunker.chunk(document)
    ```

### `def WindowedDocumentChunker.__init__(self, config: ChunkingConfig | None = None)`

Initialize the windowed chunker.

Args:
    config: Chunking configuration. If None, uses default config.

### `async def WindowedDocumentChunker.chunk(self, document: BaseDocument) -> list[DocumentChunk]`

Split document into overlapping fixed-size chunks.

Args:
    document: The document to chunk

Returns:
    List of DocumentChunk objects with overlapping windows

## `class StreamingEntityExtractorInterface(ABC)`

Interface for extracting entities from document chunks in streaming fashion.

Extends EntityExtractorInterface with streaming capabilities for processing
large documents chunk by chunk. Implementations should:
    - Deduplicate entities found in overlapping chunks (by normalized key)
    - Adjust entity offsets to match the original document
    - Batch API calls for efficiency
    - Merge mentions with highest confidence when duplicates found

This follows the pattern from plod branch's windowed entity extraction which
deduplicates by (normalized_name, entity_type) and keeps the highest confidence
mention when duplicates are found across windows.

### `def StreamingEntityExtractorInterface.extract_streaming(self, chunks: Sequence[DocumentChunk]) -> AsyncIterator[list[EntityMention]]`

Extract entities from document chunks, yielding results as they're processed.

Note: This method is not async - it returns an AsyncIterator that can be
iterated with `async for`. This is the correct pattern for async generators.

Args:
    chunks: Sequence of document chunks to process

Yields:
    Lists of EntityMention objects for each processed chunk

### `def normalize_mention_key(name: str, entity_type: str) -> tuple[str, str]`

Normalize mention key for deduplication across windows.

Removes non-alphanumeric characters, collapses whitespace, and lowercases
for consistent matching. This ensures "Breast Cancer", "breast cancer",
and "BREAST  CANCER" are all treated as the same entity.

Based on _normalize_mention_key from plod branch medlit/pipeline/mentions.py.

Args:
    name: Entity name/mention text
    entity_type: Entity type (e.g., "disease", "gene", "drug")

Returns:
    Tuple of (normalized_name, entity_type) for use as dictionary key

## `class BatchingEntityExtractor(StreamingEntityExtractorInterface)`

Wraps an EntityExtractorInterface to provide streaming extraction with batching.

This adapter enables any EntityExtractorInterface implementation to work with
document chunks. It handles:
    - Converting chunks back to temporary BaseDocument objects
    - Batching extraction calls for efficiency
    - Adjusting entity mention offsets to match original document positions
    - Deduplicating mentions across overlapping windows (keeping highest confidence)

The deduplication approach follows the plod branch pattern: normalize entity names
to alphanumeric lowercase, then keep the highest confidence mention when duplicates
are found across windows.

Example:
    ```python
    base_extractor = MyEntityExtractor()
    streaming_extractor = BatchingEntityExtractor(
        base_extractor=base_extractor,
        batch_size=10,
        deduplicate=True
    )

    async for mentions in streaming_extractor.extract_streaming(chunks):
        # Process mentions as they arrive
        await process_mentions(mentions)
    ```

### `def BatchingEntityExtractor.__init__(self, base_extractor: EntityExtractorInterface, batch_size: int = 5, deduplicate: bool = True)`

Initialize the batching extractor.

Args:
    base_extractor: The underlying extractor to use for each chunk
    batch_size: Number of chunks to process in parallel (not yet implemented)
    deduplicate: Whether to deduplicate mentions across windows

### `async def BatchingEntityExtractor.extract_streaming(self, chunks: Sequence[DocumentChunk]) -> AsyncIterator[list[EntityMention]]`

Extract entities from chunks, yielding results incrementally.

When deduplicate=True, tracks mentions across windows and yields only
unique mentions (by normalized name+type), keeping the highest confidence
version of each entity.

Note: This is an async generator method. Pylint incorrectly flags async
generators that override methods returning AsyncIterator. The pattern is
correct: ABCs declare non-async methods returning AsyncIterator, while
implementations use async def to create the async generator.

Args:
    chunks: Sequence of document chunks to process

Yields:
    Lists of EntityMention objects for each chunk (deduplicated if enabled)

### `def BatchingEntityExtractor.get_unique_mentions(self) -> list[EntityMention]`

Get all unique mentions after deduplication.

Only meaningful when deduplicate=True. Returns the highest confidence
version of each unique entity across all processed windows.

Returns:
    List of unique EntityMention objects

## `class StreamingRelationshipExtractorInterface(ABC)`

Interface for extracting relationships from document chunks in streaming fashion.

Extends RelationshipExtractorInterface with windowed processing. This is useful for:
    - Large documents that exceed LLM context windows
    - Processing relationships as entities are discovered
    - Limiting relationship extraction to relevant windows (entities nearby)

Implementations should consider:
    - Only extracting relationships between entities within the same window
    - Using overlapping windows to catch cross-boundary relationships
    - Deduplicating relationships found in multiple overlapping windows

### `def StreamingRelationshipExtractorInterface.extract_windowed(self, chunks: Sequence[DocumentChunk], entities: Sequence[BaseEntity], window_size: int = 2000) -> AsyncIterator[list[BaseRelationship]]`

Extract relationships from windowed chunks.

Note: This method is not async - it returns an AsyncIterator that can be
iterated with `async for`. This is the correct pattern for async generators.

Args:
    chunks: Document chunks to process
    entities: All entities found in the document (with position info)
    window_size: Size of context window for relationship extraction

Yields:
    Lists of BaseRelationship objects found in each window

## `class WindowedRelationshipExtractor(StreamingRelationshipExtractorInterface)`

Extracts relationships using sliding windows over document chunks.

This implementation wraps a standard RelationshipExtractorInterface and applies
it to overlapping windows of the document. Only entities that appear within
the same window are considered for relationship extraction.

This approach is particularly useful for:
    - LLM-based extractors with limited context windows
    - Reducing false positives by focusing on nearby entities
    - Improving performance by limiting entity combinations

Example:
    ```python
    base_extractor = MyRelationshipExtractor()
    windowed_extractor = WindowedRelationshipExtractor(
        base_extractor=base_extractor,
        window_size=2000
    )

    async for relationships in windowed_extractor.extract_windowed(
        chunks, entities, window_size=2000
    ):
        await store_relationships(relationships)
    ```

### `def WindowedRelationshipExtractor.__init__(self, base_extractor: RelationshipExtractorInterface)`

Initialize the windowed relationship extractor.

Args:
    base_extractor: The underlying relationship extractor

### `async def WindowedRelationshipExtractor.extract_windowed(self, chunks: Sequence[DocumentChunk], entities: Sequence[BaseEntity], window_size: int = 2000) -> AsyncIterator[list[BaseRelationship]]`

Extract relationships within overlapping windows.

Note: This is an async generator method. Pylint incorrectly flags async
generators that override methods returning AsyncIterator. See extract_streaming
comment for details on this pattern.

Args:
    chunks: Document chunks to process
    entities: All entities found in the document
    window_size: Size of context window for relationship extraction

Yields:
    Lists of BaseRelationship objects found in each window


<span id="user-content-kgraphpipelinesynonymcachepy"></span>

# kgraph/pipeline/synonym_cache.py

Persistent SAME_AS cache used during Pass 2 identity reconciliation.

The cache stores previously observed synonym/identity decisions so repeated runs
can reuse known ``(name, class) -> canonical_id`` matches and preserve ambiguity
records for review. Loading at startup and saving at shutdown makes Pass 2 more
stable, faster, and closer to idempotent across incremental ingestions.

> Persistent SAME_AS cache used during Pass 2 identity reconciliation.

The cache stores previously observed synonym/identity decisions so repeated runs
can reuse known ``(name, class) -> canonical_id`` matches and preserve ambiguity
records for review. Loading at startup and saving at shutdown makes Pass 2 more
stable, faster, and closer to idempotent across incremental ingestions.


### `def load_synonym_cache(path: Path) -> dict[str, list[dict[str, Any]]]`

Load synonym cache from JSON file. Returns dict keyed by normalized name.

### `def save_synonym_cache(path: Path, data: dict[str, list[dict[str, Any]]]) -> None`

Save synonym cache to JSON file.

### `def lookup_entity(cache: dict[str, list[dict[str, Any]]], name: str, entity_class: str) -> tuple[Optional[str], Optional[list[dict[str, Any]]]]`

Look up canonical_id or ambiguities for (name, class).

Returns:
    (canonical_id, ambiguities). canonical_id is set if a high-confidence resolved
    link exists for this (name, class). ambiguities is the list of SAME_AS entries
    for the normalized name (for review or merging).

### `def add_same_as_to_cache(cache: dict[str, list[dict[str, Any]]], entity_a: dict[str, Any], entity_b: dict[str, Any], confidence: float, asserted_by: str, resolution: Optional[str], source_papers: list[str]) -> None`

Append a SAME_AS link to the in-memory cache (indexed by normalized names).


<span id="user-content-kgraphpprintloggingpy"></span>

# kgraph/pprint_logging.py

## `class PprintLogger`

A logger wrapper that adds pprint support to standard logging methods.

### `def PprintLogger._format_message(self, msg: Any, pprint: bool = True) -> str`

Format a message, optionally using pprint.

If the message is a Pydantic model and pprint=True, uses model_dump_json()
to show the model's internals. Otherwise uses pformat for complex objects
or str() for simple conversion.

### `def PprintLogger.debug(self, msg: Any, *args, **kwargs) -> None`

Log a debug message with optional pprint formatting.

### `def PprintLogger.info(self, msg: Any, *args, **kwargs) -> None`

Log an info message with optional pprint formatting.

### `def PprintLogger.warning(self, msg: Any, *args, **kwargs) -> None`

Log a warning message with optional pprint formatting.

### `def PprintLogger.error(self, msg: Any, *args, **kwargs) -> None`

Log an error message with optional pprint formatting.

### `def PprintLogger.critical(self, msg: Any, *args, **kwargs) -> None`

Log a critical message with optional pprint formatting.

### `def PprintLogger.exception(self, msg: Any, *args, **kwargs) -> None`

Log an exception message with optional pprint formatting.

### `def PprintLogger.__getattr__(self, name: str) -> Any`

Delegate any other attributes to the underlying logger.

### `def setup_logging(level: int = logging.INFO) -> PprintLogger`

Set up logging and return a PprintLogger instance.


<span id="user-content-kgraphprogresspy"></span>

# kgraph/progress.py

Progress tracking for long-running pipeline operations.

## `class ProgressTracker(BaseModel)`

Track and report progress during long-running operations.
**Fields:**

```python
total: int
completed: int
report_interval: float
start_time: float
last_report_time: float
```

### `def ProgressTracker.increment(self) -> None`

Increment completed count and report if interval elapsed.

### `def ProgressTracker.report(self) -> None`

Print progress report to stderr.


<span id="user-content-kgraphpromotionpy"></span>

# kgraph/promotion.py

Legacy promotion utilities.

This module is kept for backwards compatibility. The PromotionPolicy ABC
has been moved to kgschema.promotion.

> Legacy promotion utilities.

This module is kept for backwards compatibility. The PromotionPolicy ABC
has been moved to kgschema.promotion.


## `class TodoPromotionPolicy(PromotionPolicy)`

Placeholder promotion policy that raises NotImplementedError.


<span id="user-content-kgraphprovenancepy"></span>

# kgraph/provenance.py

Provenance accumulation for bundle export.

Collects entity mentions and relationship evidence during ingestion so the
exporter can write mentions.jsonl and evidence.jsonl and fill EntityRow/
RelationshipRow provenance summary fields.

> Provenance accumulation for bundle export.

Collects entity mentions and relationship evidence during ingestion so the
exporter can write mentions.jsonl and evidence.jsonl and fill EntityRow/
RelationshipRow provenance summary fields.


## `class ProvenanceAccumulator`

In-memory collector for entity mentions and relationship evidence.

The orchestrator calls add_mention when storing/updating entities and
add_evidence when storing relationships that have evidence. The exporter
reads the accumulated lists to write mentions.jsonl and evidence.jsonl
and to compute per-entity and per-relationship summary fields.

### `def ProvenanceAccumulator.add_mention(self) -> None`

Record one entity mention (one row in mentions.jsonl).

### `def ProvenanceAccumulator.add_evidence(self) -> None`

Record one evidence span (one row in evidence.jsonl).


<span id="user-content-kgraphqueryinitpy"></span>

# kgraph/query/__init__.py

Query interface for knowledge graph bundles.

This subpackage previously contained bundle models, which have been moved
to the standalone kgbundle package. Import from kgbundle directly.

Example:
    from kgbundle import BundleManifestV1, EntityRow, RelationshipRow

> Query interface for knowledge graph bundles.

This subpackage previously contained bundle models, which have been moved
to the standalone kgbundle package. Import from kgbundle directly.

Example:
    from kgbundle import BundleManifestV1, EntityRow, RelationshipRow



<span id="user-content-kgraphstagemodelspy"></span>

# kgraph/stage_models.py

Pydantic models for ingestion pipeline stage outputs.

These models capture the state of the pipeline at each stage, enabling:
1. Validation of intermediate results
2. JSON serialization for debugging and testing
3. Stopping the pipeline at any stage and dumping state to stdout

Stage Flow:
    Stage 1 (entities): Per-paper entity extraction
    Stage 2 (promotion): Batch de-duplication and promotion across all papers
    Stage 3 (relationships): Per-paper relationship extraction

Each stage produces a model that can be serialized to JSON for inspection.

> Pydantic models for ingestion pipeline stage outputs.

These models capture the state of the pipeline at each stage, enabling:
1. Validation of intermediate results
2. JSON serialization for debugging and testing
3. Stopping the pipeline at any stage and dumping state to stdout

Stage Flow:
    Stage 1 (entities): Per-paper entity extraction
    Stage 2 (promotion): Batch de-duplication and promotion across all papers
    Stage 3 (relationships): Per-paper relationship extraction

Each stage produces a model that can be serialized to JSON for inspection.


## `class IngestionStage(str, Enum)`

Pipeline stages where ingestion can be stopped.

## `class ExtractedEntityRecord(BaseModel)`

Record of a single extracted entity.
**Fields:**

```python
entity_id: str
name: str
entity_type: str
status: str
confidence: float
source: str
canonical_ids: dict[str, str]
synonyms: tuple[str, ...]
metadata: dict[str, Any]
```

## `class PaperEntityExtractionResult(BaseModel)`

Result of entity extraction from a single paper.
**Fields:**

```python
document_id: str
source_uri: str | None
extracted_at: datetime
entities_extracted: int
entities_new: int
entities_existing: int
entities: tuple[ExtractedEntityRecord, ...]
errors: tuple[str, ...]
```

## `class EntityExtractionStageResult(BaseModel)`

Complete result of Stage 1: Entity Extraction across all papers.

This model captures the state after all papers have been processed
for entity extraction, but before promotion.
**Fields:**

```python
stage: str
completed_at: datetime
papers_processed: int
papers_failed: int
total_entities_extracted: int
total_entities_new: int
total_entities_existing: int
paper_results: tuple[PaperEntityExtractionResult, ...]
entity_type_counts: dict[str, int]
provisional_count: int
canonical_count: int
```

## `class PromotedEntityRecord(BaseModel)`

Record of an entity that was promoted to canonical status.
**Fields:**

```python
old_entity_id: str
new_entity_id: str
name: str
entity_type: str
canonical_source: str
canonical_url: str | None
```

## `class PromotionStageResult(BaseModel)`

Complete result of Stage 2: Entity Promotion.

This model captures the state after provisional entities have been
de-duplicated and promoted to canonical status.
**Fields:**

```python
stage: str
completed_at: datetime
candidates_evaluated: int
entities_promoted: int
entities_skipped_no_canonical_id: int
entities_skipped_policy: int
entities_skipped_storage_failure: int
promoted_entities: tuple[PromotedEntityRecord, ...]
total_canonical_entities: int
total_provisional_entities: int
```

## `class ExtractedRelationshipRecord(BaseModel)`

Record of a single extracted relationship.
**Fields:**

```python
subject_id: str
subject_name: str
subject_type: str
predicate: str
object_id: str
object_name: str
object_type: str
confidence: float
source_document: str
evidence_quote: str | None
metadata: dict[str, Any]
```

## `class PaperRelationshipExtractionResult(BaseModel)`

Result of relationship extraction from a single paper.
**Fields:**

```python
document_id: str
source_uri: str | None
extracted_at: datetime
relationships_extracted: int
relationships: tuple[ExtractedRelationshipRecord, ...]
errors: tuple[str, ...]
```

## `class RelationshipExtractionStageResult(BaseModel)`

Complete result of Stage 3: Relationship Extraction.

This model captures the final state after relationship extraction.
**Fields:**

```python
stage: str
completed_at: datetime
papers_processed: int
papers_with_relationships: int
total_relationships_extracted: int
paper_results: tuple[PaperRelationshipExtractionResult, ...]
predicate_counts: dict[str, int]
```

## `class IngestionPipelineResult(BaseModel)`

Complete result of the full ingestion pipeline.

Combines results from all three stages for final output.
**Fields:**

```python
pipeline_version: str
started_at: datetime
completed_at: datetime
stopped_at_stage: str | None
entity_extraction: EntityExtractionStageResult | None
promotion: PromotionStageResult | None
relationship_extraction: RelationshipExtractionStageResult | None
total_documents: int
total_entities: int
total_relationships: int
```


<span id="user-content-kgraphstorageinitpy"></span>

# kgraph/storage/__init__.py

Storage interfaces and implementations for the knowledge graph.


<span id="user-content-kgraphstoragememorypy"></span>

# kgraph/storage/memory.py

In-memory storage implementations for testing and development.

This module provides dictionary-based implementations of the storage interfaces
that keep all data in memory. These implementations are suitable for:

- **Unit testing**: Fast, isolated tests without external dependencies
- **Development**: Quick iteration without database setup
- **Prototyping**: Experimenting with the framework before choosing a backend
- **Small datasets**: Demos and examples with limited data

**Not recommended for production** due to:
- No persistence (data is lost when the process exits)
- No concurrency control (not safe for multi-process access)
- Memory constraints (all data must fit in RAM)
- O(n) search operations (no indexing)

For production use, implement the storage interfaces with a proper database
backend (PostgreSQL with pgvector, Neo4j, etc.).

> In-memory storage implementations for testing and development.

This module provides dictionary-based implementations of the storage interfaces
that keep all data in memory. These implementations are suitable for:

- **Unit testing**: Fast, isolated tests without external dependencies
- **Development**: Quick iteration without database setup
- **Prototyping**: Experimenting with the framework before choosing a backend
- **Small datasets**: Demos and examples with limited data

**Not recommended for production** due to:
- No persistence (data is lost when the process exits)
- No concurrency control (not safe for multi-process access)
- Memory constraints (all data must fit in RAM)
- O(n) search operations (no indexing)

For production use, implement the storage interfaces with a proper database
backend (PostgreSQL with pgvector, Neo4j, etc.).


### `def _cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float`

Compute cosine similarity between two embedding vectors.

Cosine similarity measures the cosine of the angle between two vectors,
producing a value between -1 (opposite) and 1 (identical direction).
For normalized embeddings, this is equivalent to the dot product.

Args:
    a: First embedding vector.
    b: Second embedding vector (must have same dimension as a).

Returns:
    Cosine similarity score between -1 and 1. Returns 0.0 if vectors
    have different lengths, are empty, or have zero magnitude.

## `class InMemoryEntityStorage(EntityStorageInterface)`

In-memory entity storage using a dictionary keyed by entity_id.

Stores entities in a simple `dict[str, BaseEntity]` structure. All
operations are O(1) for direct lookups and O(n) for searches.

Thread safety: Not thread-safe. For concurrent access, use external
synchronization or a production database backend.

Example:
    ```python
    storage = InMemoryEntityStorage()
    await storage.add(my_entity)
    entity = await storage.get(my_entity.entity_id)
    ```

### `def InMemoryEntityStorage.__init__(self) -> None`

Initialize an empty entity storage.

### `async def InMemoryEntityStorage.add(self, entity: BaseEntity) -> str`

Adds a new entity to the storage.

If an entity with the same ID already exists, it will be overwritten.

Note: This operation is not thread-safe.

Args:
    entity: The `BaseEntity` object to add.

Returns:
    The ID of the added entity.

### `async def InMemoryEntityStorage.get(self, entity_id: str) -> BaseEntity | None`

Retrieves an entity by its ID.

Note: This operation is not thread-safe.

Args:
    entity_id: The ID of the entity to retrieve.

Returns:
    The `BaseEntity` object if found, otherwise `None`.

### `async def InMemoryEntityStorage.get_batch(self, entity_ids: Sequence[str]) -> list[BaseEntity | None]`

Retrieves a batch of entities by their IDs.

Note: This operation is not thread-safe.

Args:
    entity_ids: A sequence of entity IDs to retrieve.

Returns:
    A list of `BaseEntity` objects or `None` for each ID, in the
    same order as the input.

### `async def InMemoryEntityStorage.find_by_embedding(self, embedding: Sequence[float], threshold: float = 0.8, limit: int = 10) -> list[tuple[BaseEntity, float]]`

Finds entities with embeddings similar to a given vector.

This performs a brute-force, O(n) search over all entities.

Note: This operation is not thread-safe.

Args:
    embedding: The embedding vector to compare against.
    threshold: The minimum cosine similarity to be considered a match.
    limit: The maximum number of similar entities to return.

Returns:
    A list of tuples, each containing a matching `BaseEntity` and its
    similarity score, sorted by score in descending order.

### `async def InMemoryEntityStorage.find_by_name(self, name: str, entity_type: str | None = None, limit: int = 10) -> list[BaseEntity]`

Finds entities by a case-insensitive name or synonym match.

This performs an O(n) search over all entities.

Note: This operation is not thread-safe.

Args:
    name: The name to search for.
    entity_type: An optional entity type to narrow the search.
    limit: The maximum number of matching entities to return.

Returns:
    A list of matching `BaseEntity` objects.

### `async def InMemoryEntityStorage.find_provisional_for_promotion(self, min_usage: int, min_confidence: float) -> list[BaseEntity]`

Finds provisional entities that meet promotion criteria.

This performs an O(n) scan of all entities.

Note: This operation is not thread-safe.

Args:
    min_usage: The minimum `usage_count` required for promotion.
    min_confidence: The minimum `confidence` score required.

Returns:
    A list of provisional `BaseEntity` objects that are eligible
    for promotion.

### `async def InMemoryEntityStorage.update(self, entity: BaseEntity) -> bool`

Updates an existing entity in the storage.

If the entity ID does not exist, the operation fails.

Note: This operation is not thread-safe.

Args:
    entity: The entity object with updated data.

Returns:
    `True` if the update was successful, `False` if the entity ID
    was not found.

### `async def InMemoryEntityStorage.promote(self, entity_id: str, new_entity_id: str, canonical_ids: dict[str, str]) -> BaseEntity | None`

Promotes a provisional entity to a canonical one.

This involves changing the entity's ID, updating its status, and
assigning canonical IDs. The old entity record is removed.

Note: This operation is not thread-safe.

Args:
    entity_id: The current ID of the provisional entity.
    new_entity_id: The new, canonical ID for the entity.
    canonical_ids: A dictionary of canonical IDs to assign.

Returns:
    The updated, canonical `BaseEntity` object if the original entity
    was found, otherwise `None`.

### `async def InMemoryEntityStorage.merge(self, source_ids: Sequence[str], target_id: str) -> bool`

Merges multiple source entities into a single target entity.

This operation combines synonyms and usage counts from source entities
into the target entity and then deletes the source entities.

Note: This operation is not thread-safe.

Args:
    source_ids: A sequence of entity IDs to merge and then delete.
    target_id: The ID of the entity that will absorb the sources.

Returns:
    `True` if the merge was successful, `False` if the target or any
    source entity was not found.

### `async def InMemoryEntityStorage.delete(self, entity_id: str) -> bool`

Deletes an entity from storage by its ID.

Note: This operation is not thread-safe.

Args:
    entity_id: The ID of the entity to delete.

Returns:
    `True` if the entity was found and deleted, `False` otherwise.

### `async def InMemoryEntityStorage.count(self) -> int`

Returns the total number of entities in storage.

Note: This operation is not thread-safe if other operations are
modifying the storage concurrently.

Returns:
    The total count of entities.

### `async def InMemoryEntityStorage.list_all(self, status: str | None = None, limit: int = 1000, offset: int = 0) -> list[BaseEntity]`

Lists entities from storage, with optional filtering and pagination.

This performs an O(n) scan if filtering by status.

Note: This operation is not thread-safe.

Args:
    status: An optional status (`"canonical"` or `"provisional"`) to
            filter by.
    limit: The maximum number of entities to return.
    offset: The starting offset for pagination.

Returns:
    A list of `BaseEntity` objects.

## `class InMemoryRelationshipStorage(RelationshipStorageInterface)`

In-memory relationship storage using triple keys.

Stores relationships in a dictionary keyed by (subject_id, predicate, object_id)
tuples. This ensures uniqueness of triples and provides O(1) lookup for
specific relationships.

Traversal queries (get_by_subject, get_by_object) are O(n) as they scan
all relationships. For large graphs, use a database with proper indices.

Thread safety: Not thread-safe. For concurrent access, use external
synchronization or a production database backend.

Example:
    ```python
    storage = InMemoryRelationshipStorage()
    await storage.add(my_relationship)
    outgoing = await storage.get_by_subject(entity_id)
    ```

### `def InMemoryRelationshipStorage.__init__(self) -> None`

Initialize an empty relationship storage.

### `def InMemoryRelationshipStorage._make_key(self, rel: BaseRelationship) -> tuple[str, str, str]`

Create a dictionary key from a relationship's triple.

### `async def InMemoryRelationshipStorage.add(self, relationship: BaseRelationship) -> str`

Adds a new relationship to the storage.

If a relationship with the same triple (subject, predicate, object)
already exists, it will be overwritten.

Note: This operation is not thread-safe.

Args:
    relationship: The `BaseRelationship` object to add.

Returns:
    A string representation of the relationship's key.

### `async def InMemoryRelationshipStorage.get_by_subject(self, subject_id: str, predicate: str | None = None) -> list[BaseRelationship]`

Retrieves all relationships originating from a given subject.

This performs an O(n) scan of all relationships.

Note: This operation is not thread-safe.

Args:
    subject_id: The ID of the subject entity.
    predicate: An optional predicate to filter the relationships.

Returns:
    A list of matching `BaseRelationship` objects.

### `async def InMemoryRelationshipStorage.get_by_object(self, object_id: str, predicate: str | None = None) -> list[BaseRelationship]`

Retrieves all relationships pointing to a given object.

This performs an O(n) scan of all relationships.

Note: This operation is not thread-safe.

Args:
    object_id: The ID of the object entity.
    predicate: An optional predicate to filter the relationships.

Returns:
    A list of matching `BaseRelationship` objects.

### `async def InMemoryRelationshipStorage.find_by_triple(self, subject_id: str, predicate: str, object_id: str) -> BaseRelationship | None`

Finds a specific relationship by its full triple.

This is an O(1) lookup.

Note: This operation is not thread-safe.

Args:
    subject_id: The ID of the subject entity.
    predicate: The predicate of the relationship.
    object_id: The ID of the object entity.

Returns:
    The `BaseRelationship` object if found, otherwise `None`.

### `async def InMemoryRelationshipStorage.update_entity_references(self, old_entity_id: str, new_entity_id: str) -> int`

Updates all relationships that reference an old entity ID.

This is used during entity promotion or merging to retarget
relationships from an old ID to a new one.

Note: This operation is not thread-safe.

Args:
    old_entity_id: The entity ID to be replaced.
    new_entity_id: The new entity ID to use.

Returns:
    The number of relationships that were updated.

### `async def InMemoryRelationshipStorage.get_by_document(self, document_id: str) -> list[BaseRelationship]`

Retrieves all relationships sourced from a specific document.

This performs an O(n) scan of all relationships.

Note: This operation is not thread-safe.

Args:
    document_id: The ID of the source document.

Returns:
    A list of matching `BaseRelationship` objects.

### `async def InMemoryRelationshipStorage.delete(self, subject_id: str, predicate: str, object_id: str) -> bool`

Deletes a relationship from storage by its triple.

Note: This operation is not thread-safe.

Args:
    subject_id: The ID of the subject entity.
    predicate: The predicate of the relationship.
    object_id: The ID of the object entity.

Returns:
    `True` if the relationship was found and deleted, `False` otherwise.

### `async def InMemoryRelationshipStorage.count(self) -> int`

Returns the total number of relationships in storage.

Note: This operation is not thread-safe if other operations are
modifying the storage concurrently.

Returns:
    The total count of relationships.

### `async def InMemoryRelationshipStorage.list_all(self, limit: int = 1000, offset: int = 0) -> list[BaseRelationship]`

Lists all relationships from storage, with optional pagination.

Note: This operation is not thread-safe.

Args:
    limit: The maximum number of relationships to return.
    offset: The starting offset for pagination.

Returns:
    A list of `BaseRelationship` objects.

## `class InMemoryDocumentStorage(DocumentStorageInterface)`

In-memory document storage using a dictionary keyed by document_id.

Stores documents in a simple `dict[str, BaseDocument]` structure.
Document lookups by ID are O(1); lookups by source URI are O(n).

Thread safety: Not thread-safe. For concurrent access, use external
synchronization or a production database backend.

Example:
    ```python
    storage = InMemoryDocumentStorage()
    await storage.add(my_document)
    doc = await storage.get(my_document.document_id)
    ```

### `def InMemoryDocumentStorage.__init__(self) -> None`

Initialize an empty document storage.

### `async def InMemoryDocumentStorage.add(self, document: BaseDocument) -> str`

Adds a new document to the storage.

If a document with the same ID already exists, it will be
overwritten.

Note: This operation is not thread-safe.

Args:
    document: The `BaseDocument` object to add.

Returns:
    The ID of the added document.

### `async def InMemoryDocumentStorage.get(self, document_id: str) -> BaseDocument | None`

Retrieves a document by its ID.

Note: This operation is not thread-safe.

Args:
    document_id: The ID of the document to retrieve.

Returns:
    The `BaseDocument` object if found, otherwise `None`.

### `async def InMemoryDocumentStorage.find_by_source(self, source_uri: str) -> BaseDocument | None`

Finds a document by its source URI.

This performs an O(n) scan of all documents.

Note: This operation is not thread-safe.

Args:
    source_uri: The source URI to search for.

Returns:
    The `BaseDocument` object if found, otherwise `None`.

### `async def InMemoryDocumentStorage.list_ids(self, limit: int = 100, offset: int = 0) -> list[str]`

Lists document IDs from storage, with optional pagination.

Note: This operation is not thread-safe.

Args:
    limit: The maximum number of document IDs to return.
    offset: The starting offset for pagination.

Returns:
    A list of document ID strings.

### `async def InMemoryDocumentStorage.delete(self, document_id: str) -> bool`

Deletes a document from storage by its ID.

Note: This operation is not thread-safe.

Args:
    document_id: The ID of the document to delete.

Returns:
    `True` if the document was found and deleted, `False` otherwise.

### `async def InMemoryDocumentStorage.count(self) -> int`

Returns the total number of documents in storage.

Note: This operation is not thread-safe if other operations are
modifying the storage concurrently.

Returns:
    The total count of documents.


<span id="user-content-kgraphtemplatesinitpy"></span>

# kgraph/templates/__init__.py

Jinja2 templates for extraction prompts. Config-driven, domain-agnostic structure.


<span id="user-content-kgraphtemplatesrenderpy"></span>

# kgraph/templates/render.py

Render extraction prompts from config and Jinja2 templates.

### `def _format_from_domain_spec(domain_spec: Any) -> tuple[str, str, str]`

Build entity_types_str, predicates_str, domain_instructions from domain_spec module.

### `def _load_config(config_dir: Path) -> tuple[dict[str, Any], dict[str, Any], str]`

Load entity_types, predicates, domain_instructions from config_dir.

### `def _format_entity_types_for_prompt(entity_types: dict[str, Any]) -> str`

Pre-format entity_types into comma-separated bundle_class list for prompt.

### `def _format_predicates_for_prompt(predicates: dict[str, Any]) -> str`

Pre-format predicates into comma-separated list for prompt.

### `def _format_vocab_section(vocab_entries: list[dict[str, Any]]) -> str`

Format vocab entries for prompt appendix.

### `def render_extraction_prompt(config_dir: Optional[Path] = None, vocab_entries: Optional[list[dict[str, Any]]] = None, domain_spec: Optional[Any] = None) -> str`

Render entity/relationship extraction prompt from config and optional vocab.

When domain_spec is provided, uses it as single source of truth (ENTITY_CLASSES,
PREDICATES, PROMPT_INSTRUCTIONS). Otherwise loads from config_dir.

Args:
    config_dir: Directory containing entity_types.yaml, predicates.yaml,
        domain_instructions.md. Ignored when domain_spec is provided.
    vocab_entries: Optional list of {"name", "type", ...} for corpus vocab.
    domain_spec: Optional module with ENTITY_CLASSES, PREDICATES, PROMPT_INSTRUCTIONS.

Returns:
    Full prompt string for LLM.


<span id="user-content-kgschemakgschemainitpy"></span>

# kgschema/kgschema/__init__.py

Knowledge Graph Schema - Base Models and Interfaces

This package contains only Pydantic models and ABC interfaces with no
functional code. It defines:

- Entity, relationship, and document base classes
- Domain schema interface
- Storage interfaces
- Canonical ID model
- Promotion policy interface

These are used by both kgraph (ingestion) and can be referenced by
domain implementations.

> 
Knowledge Graph Schema - Base Models and Interfaces

This package contains only Pydantic models and ABC interfaces with no
functional code. It defines:

- Entity, relationship, and document base classes
- Domain schema interface
- Storage interfaces
- Canonical ID model
- Promotion policy interface

These are used by both kgraph (ingestion) and can be referenced by
domain implementations.



<span id="user-content-kgschemakgschemacanonicalidpy"></span>

# kgschema/kgschema/canonical_id.py

Canonical ID model for knowledge graph entities.

This module provides the CanonicalId model representing stable identifiers
from authoritative sources (UMLS, MeSH, HGNC, etc.).

> Canonical ID model for knowledge graph entities.

This module provides the CanonicalId model representing stable identifiers
from authoritative sources (UMLS, MeSH, HGNC, etc.).


## `class CanonicalId(BaseModel)`

Represents a canonical identifier from an authoritative source.

A canonical ID uniquely identifies an entity in an authoritative ontology
(e.g., UMLS, MeSH, HGNC, RxNorm, UniProt, DBPedia). This model stores
the ID, its URL (if available), and synonyms that map to this ID.

Attributes:
    id: The canonical ID string (e.g., "UMLS:C12345", "MeSH:D000570", "HGNC:1100")
    url: Optional URL to the authoritative source page for this ID
    synonyms: List of alternative names/terms that map to this canonical ID
**Fields:**

```python
id: str
url: Optional[str]
synonyms: tuple[str, ...]
```

### `def CanonicalId.__str__(self) -> str`

String representation of the canonical ID.


<span id="user-content-kgschemakgschemadocumentpy"></span>

# kgschema/kgschema/document.py

Document representation for the knowledge graph framework.

This module defines `BaseDocument`, the abstract base class for all documents
processed by the knowledge graph ingestion pipeline. Documents represent the
source material from which entities and relationships are extracted.

A document contains:
    - **Content**: The full text of the document
    - **Metadata**: Title, source URI, content type, creation timestamp
    - **Structure**: Domain-specific sections via `get_sections()`

Domain implementations subclass `BaseDocument` to add domain-specific fields
and structure. For example:
    - `JournalArticle` might add fields for authors, abstract, and citations
    - `LegalDocument` might add fields for court, case number, and parties
    - `ConferencePaper` might add fields for venue, year, and keywords

Documents are immutable (frozen Pydantic models) to ensure consistency
throughout the extraction pipeline.

> Document representation for the knowledge graph framework.

This module defines `BaseDocument`, the abstract base class for all documents
processed by the knowledge graph ingestion pipeline. Documents represent the
source material from which entities and relationships are extracted.

A document contains:
    - **Content**: The full text of the document
    - **Metadata**: Title, source URI, content type, creation timestamp
    - **Structure**: Domain-specific sections via `get_sections()`

Domain implementations subclass `BaseDocument` to add domain-specific fields
and structure. For example:
    - `JournalArticle` might add fields for authors, abstract, and citations
    - `LegalDocument` might add fields for court, case number, and parties
    - `ConferencePaper` might add fields for venue, year, and keywords

Documents are immutable (frozen Pydantic models) to ensure consistency
throughout the extraction pipeline.


## `class BaseDocument(ABC, BaseModel)`

Abstract base class for documents in the knowledge graph.

Represents a parsed document ready for entity and relationship extraction.
All documents share common fields (ID, content, metadata) while subclasses
add domain-specific structure and fields.

Documents are frozen (immutable) Pydantic models, ensuring they cannot be
modified after creation. This immutability guarantees consistency when
documents are referenced by multiple entities and relationships.

Subclasses must implement:
    - `get_document_type()`: Return the domain-specific document type
    - `get_sections()`: Return document structure as (name, content) tuples

Example:
    ```python
    class JournalArticle(BaseDocument):
        authors: tuple[str, ...] = Field(default=())
        abstract: str | None = None

        def get_document_type(self) -> str:
            return "journal_article"

        def get_sections(self) -> list[tuple[str, str]]:
            sections = []
            if self.abstract:
                sections.append(("abstract", self.abstract))
            sections.append(("body", self.content))
            return sections
    ```
**Fields:**

```python
document_id: str
title: str | None
content: str
content_type: str
source_uri: str | None
created_at: datetime
metadata: dict
```

### `def BaseDocument.get_document_type(self) -> str`

Return domain-specific document type.

Examples: 'journal_article', 'clinical_trial' for medical;
'case_opinion', 'statute' for legal; 'conference_paper' for CS.

### `def BaseDocument.get_sections(self) -> list[tuple[str, str]]`

Return document sections as (section_name, content) tuples.

Allows domain-specific document structure. For unstructured documents,
return a single section like [('body', self.content)].


<span id="user-content-kgschemakgschemadomainpy"></span>

# kgschema/kgschema/domain.py

Domain schema definition for the knowledge graph framework.

A domain schema defines the vocabulary and rules for a specific knowledge
domain (medical literature, legal documents, academic CS papers, etc.).
Each domain specifies:

- **Entity types**: The kinds of entities that can exist (drugs, diseases,
  legal cases, algorithms, etc.) and their concrete class implementations.

- **Relationship types**: Valid predicates between entities (treats, cites,
  implements, etc.) and their class implementations.

- **Document types**: Source document formats the domain processes (journal
  articles, court filings, conference papers, etc.).

- **Validation rules**: Domain-specific constraints on entities and
  relationships beyond basic type checking.

- **Promotion configuration**: Thresholds for promoting provisional entities
  to canonical status, which may vary by domain based on data quality and
  external authority availability.

The domain schema serves as the central configuration point for domain-specific
behavior, allowing the core knowledge graph framework to remain domain-agnostic
while supporting specialized use cases.

Example usage:
    ```python
    class MedicalDomainSchema(DomainSchema):
        @property
        def name(self) -> str:
            return "medical"

        @property
        def entity_types(self) -> dict[str, type[BaseEntity]]:
            return {"drug": DrugEntity, "disease": DiseaseEntity, "gene": GeneEntity}

        @property
        def relationship_types(self) -> dict[str, type[BaseRelationship]]:
            return {"treats": TreatsRelationship, "causes": CausesRelationship}
        # ... etc
    ```

> Domain schema definition for the knowledge graph framework.

A domain schema defines the vocabulary and rules for a specific knowledge
domain (medical literature, legal documents, academic CS papers, etc.).
Each domain specifies:

- **Entity types**: The kinds of entities that can exist (drugs, diseases,
  legal cases, algorithms, etc.) and their concrete class implementations.

- **Relationship types**: Valid predicates between entities (treats, cites,
  implements, etc.) and their class implementations.

- **Document types**: Source document formats the domain processes (journal
  articles, court filings, conference papers, etc.).

- **Validation rules**: Domain-specific constraints on entities and
  relationships beyond basic type checking.

- **Promotion configuration**: Thresholds for promoting provisional entities
  to canonical status, which may vary by domain based on data quality and
  external authority availability.

The domain schema serves as the central configuration point for domain-specific
behavior, allowing the core knowledge graph framework to remain domain-agnostic
while supporting specialized use cases.

Example usage:
    ```python
    class MedicalDomainSchema(DomainSchema):
        @property
        def name(self) -> str:
            return "medical"

        @property
        def entity_types(self) -> dict[str, type[BaseEntity]]:
            return {"drug": DrugEntity, "disease": DiseaseEntity, "gene": GeneEntity}

        @property
        def relationship_types(self) -> dict[str, type[BaseRelationship]]:
            return {"treats": TreatsRelationship, "causes": CausesRelationship}
        # ... etc
    ```


## `class ValidationIssue(BaseModel)`

A structured validation error with location and diagnostic information.

Provides detailed information about why validation failed, enabling
better error messages and programmatic handling of validation failures.

Attributes:
    field: The field that failed validation (e.g., "entity_type", "confidence")
    message: Human-readable description of the issue
    value: The invalid value (optional, for debugging)
    code: Machine-readable error code (optional, for programmatic handling)
**Fields:**

```python
field: str
message: str
value: str | None
code: str | None
```

## `class PredicateConstraint(BaseModel)`

Defines the valid subject and object entity types for a predicate.
**Fields:**

```python
subject_types: set[str]
object_types: set[str]
```

## `class Provenance(BaseModel)`

Tracks the precise location of extracted information within a document.

Used to record where entities, relationships, and other extracted data
originated, enabling traceability back to source text.

Fields:
    document_id: Unique identifier of the source document
    source_uri: Optional URI/path to the original document
    section: Name of the document section (e.g., "abstract", "methods", "results")
    paragraph: Paragraph number/index within the section (0-based)
    start_offset: Character offset where the relevant text begins
    end_offset: Character offset where the relevant text ends
**Fields:**

```python
document_id: str
source_uri: str | None
section: str | None
paragraph: int | None
start_offset: int | None
end_offset: int | None
```

## `class Evidence(BaseModel)`


**Fields:**

```python
kind: str
source_documents: tuple[str, ...]
primary: Provenance | None
mentions: tuple[Provenance, ...]
notes: dict[str, object]
```

## `class DomainSchema(ABC)`

Abstract schema definition for a knowledge domain.

Each domain (medical, legal, CS papers, etc.) implements this interface
to define its vocabulary of types and validation rules. The schema is
used throughout the ingestion pipeline to:

- Validate extracted entities and relationships before storage
- Configure entity promotion thresholds
- Determine valid predicates between entity type pairs
- Deserialize domain-specific entity/relationship subclasses

Implementations should be stateless and thread-safe, as the same schema
instance may be used across multiple concurrent ingestion operations.

Required methods to implement:
    - name: Unique domain identifier
    - entity_types: Registry of entity type names to classes
    - relationship_types: Registry of predicate names to classes
    - document_types: Registry of document format names to classes
    - validate_entity: Domain-specific entity validation
    - validate_relationship: Domain-specific relationship validation

Optional methods to override:
    - promotion_config: Customize promotion thresholds
    - get_valid_predicates: Restrict predicates by entity type pair

### `def DomainSchema.name(self) -> str`

Return the unique identifier for this domain.

The domain name is used for:
    - Namespacing entities in multi-domain deployments
    - Selecting the correct deserializer for stored data
    - Logging and debugging

Returns:
    A short, lowercase identifier (e.g., 'medical', 'legal', 'cs_papers').
    Should contain only alphanumeric characters and underscores.

### `def DomainSchema.entity_types(self) -> dict[str, type[BaseEntity]]`

Return the registry of entity types for this domain.

Maps type name strings to concrete BaseEntity subclasses. The type
names are used in entity extraction and must match the values
returned by each entity's `get_entity_type()` method.

Returns:
    Dictionary mapping entity type names to their implementing classes.

Example:
    ```python
    return {
        'drug': DrugEntity,
        'disease': DiseaseEntity,
        'gene': GeneEntity,
    }
    ```

### `def DomainSchema.relationship_types(self) -> dict[str, type[BaseRelationship]]`

Return the registry of relationship types for this domain.

Maps predicate name strings to concrete BaseRelationship subclasses.
The predicate names define the vocabulary of edges in the knowledge
graph and must match the values used in relationship extraction.

Returns:
    Dictionary mapping predicate names to their implementing classes.

Example:
    ```python
    return {
        'treats': TreatsRelationship,
        'causes': CausesRelationship,
        'interacts_with': InteractionRelationship,
    }
    ```

### `def DomainSchema.predicate_constraints(self) -> dict[str, PredicateConstraint]`

Return a dictionary of predicate constraints for this domain.

This maps predicate names to a PredicateConstraint object, which
defines the valid subject and object entity types for that predicate.
These constraints are used to validate relationships during ingestion
and to filter valid predicates for a given subject-object pair.

Returns:
    Dictionary mapping predicate names (e.g., "treats") to
    PredicateConstraint instances.

Example:
    ```python
    return {
        "treats": PredicateConstraint(
            subject_types={"drug", "procedure"},
            object_types={"disease", "symptom"},
        ),
        "causes": PredicateConstraint(
            subject_types={"gene", "exposure"},
            object_types={"disease"},
        ),
    }
    ```

### `def DomainSchema.document_types(self) -> dict[str, type[BaseDocument]]`

Return the registry of document types for this domain.

Maps document format names to concrete BaseDocument subclasses.
Different document types may have different structures and metadata
fields relevant to the domain.

Returns:
    Dictionary mapping document type names to their implementing classes.

Example:
    ```python
    return {
        'journal_article': JournalArticle,
        'clinical_trial': ClinicalTrialDocument,
        'drug_label': DrugLabelDocument,
    }
    ```

### `def DomainSchema.promotion_config(self) -> PromotionConfig`

Return the configuration for promoting provisional entities.

Promotion configuration controls when provisional entities (newly
discovered mentions without canonical IDs) are promoted to canonical
status. The thresholds should be tuned based on:

- Data quality: Noisy extraction requires higher thresholds
- External authority availability: Domains with good authorities
  (UMLS, DBPedia) can use higher confidence requirements
- Entity importance: Critical domains may require more evidence

Override this property to customize thresholds for your domain.
The default configuration uses framework defaults.

Returns:
    PromotionConfig with min_usage_count, min_confidence, and
    require_embedding settings appropriate for this domain.

### `def DomainSchema.validate_entity(self, entity: BaseEntity) -> list[ValidationIssue]`

Validate an entity against domain-specific rules.

Called by the ingestion pipeline before storing an entity. Use this
to enforce constraints beyond basic type checking, such as:

- Required fields for specific entity types
- Value constraints (e.g., confidence thresholds)
- Cross-field validation (e.g., canonical entities must have IDs)

Args:
    entity: The entity to validate.

Returns:
    Empty list if the entity is valid, otherwise a list of ValidationIssue
    objects describing each validation failure. Multiple issues can be
    returned to help users fix all problems at once.

Example:
    ```python
    def validate_entity(self, entity: BaseEntity) -> list[ValidationIssue]:
        issues = []
        if entity.get_entity_type() not in self.entity_types:
            issues.append(ValidationIssue(
                field="entity_type",
                message=f"Unknown entity type: {entity.get_entity_type()}",
                value=entity.get_entity_type(),
                code="UNKNOWN_TYPE",
            ))
        return issues
    ```

Note:
    At minimum, implementations should verify that the entity's type
    (from `get_entity_type()`) is registered in `entity_types`.

### `async def DomainSchema.validate_relationship(self, relationship: BaseRelationship, entity_storage: EntityStorageInterface | None = None) -> bool`

Validate a relationship against domain-specific rules.

This method first performs predicate constraint validation using the
`predicate_constraints` defined by the domain. If the relationship's
subject or object types do not conform to the constraints for its
predicate, a warning is logged, and the relationship is considered invalid.

If an `entity_storage` is provided, it will be used to look up the
subject and object entities to determine their types. Otherwise,
it will attempt to infer types directly from the relationship object
(e.g., for testing or when entities are not yet stored).

Subclasses can override this method to add further domain-specific
validation logic. It is recommended to call `super().validate_relationship()`
to ensure base predicate constraints are checked.

Args:
    relationship: The relationship to validate.
    entity_storage: Optional entity storage to look up subject/object types.

Returns:
    True if the relationship is valid for this domain, False otherwise.

### `def DomainSchema.get_valid_predicates(self, subject_type: str, object_type: str) -> list[str]`

Return predicates valid between two entity types.

Override this method to enforce type-specific relationship constraints.
For example, in a medical domain, "treats" might only be valid from
Drug to Disease, not from Disease to Drug.

The default implementation allows any predicate registered in
`relationship_types` between any entity type pair.

Args:
    subject_type: The entity type of the relationship subject.
    object_type: The entity type of the relationship object.

Returns:
    List of predicate names that are valid for this entity type pair.
    Returns an empty list if no predicates are valid.

Example:
    ```python
    def get_valid_predicates(self, subject_type: str, object_type: str) -> list[str]:
        if subject_type == "drug" and object_type == "disease":
            return ["treats", "prevents", "exacerbates"]
        if subject_type == "gene" and object_type == "disease":
            return ["associated_with", "causes"]
        return []  # No other combinations allowed
    ```

### `def DomainSchema.normalize_mention(self, mention: str) -> str`

Normalize a mention string before identity resolution.

Called by the identity server before ``resolve()`` to apply
domain-specific string normalization (e.g. spelling variants,
case folding, abbreviation expansion).

The default implementation returns the mention unchanged.
Override in domain subclasses to apply domain-specific rules.

Parameters
----------
mention:
    Raw surface form of the entity mention.

Returns
-------
str
    Normalized mention string.

### `def DomainSchema.get_promotion_policy(self, lookup = None) -> PromotionPolicy`

Return the promotion policy for this domain.

Override this method to provide domain-specific promotion logic.
Default implementation raises NotImplementedError.

Args:
    lookup: Optional canonical ID lookup service. Domains that support
           external lookups can use this to pass the service to the policy.

### `def DomainSchema.preferred_entity(self, candidates: list[BaseEntity]) -> BaseEntity`

Return the preferred survivor when merging a set of synonym candidates.

Called by the identity server's ``on_entity_added`` hook after
``find_synonyms`` returns candidates. The domain implements its own
preference rules, for example:

- Prefer canonical over provisional (a canonical entity already has a
  stable external ID and should not be displaced by a provisional one)
- Among entities of equal status, prefer the one with the highest
  ``usage_count`` (more evidence)
- Prefer the entity with an authoritative ``canonical_ids`` entry
  (e.g. a UMLS CUI or MeSH term) over one without

The returned entity must be a member of ``candidates``. The caller
passes its ``entity_id`` as ``survivor_id`` to ``IdentityServer.merge``.

Parameters
----------
candidates:
    Non-empty list of entities identified as synonyms. Guaranteed to
    contain at least two elements when called from ``on_entity_added``.

Returns
-------
BaseEntity
    The entity that should survive the merge.

### `def DomainSchema.evidence_model(self) -> type[Evidence]`

Return the domain's version of Evidence

The domain can add stuff to the evidence:
    - A predicate might be supported (or counter-argued) by lab data or test results
    - Or by whether some paper from the past was retracted or not

Returns:
    A type that is, or is a subclass of, the Evidence type

### `def DomainSchema.provenance_model(self) -> type[Provenance]`

Return the domain's version of Provenance

The domain can add stuff to the provenance, much like Evidence

Returns:
    A type that is, or is a subclass of, the Provenance type


<span id="user-content-kgschemakgschemaentitypy"></span>

# kgschema/kgschema/entity.py

Entity system for the knowledge graph framework.

This module defines the core entity types for the knowledge graph:

- **BaseEntity**: Abstract base class for all domain entities (nodes in the graph)
- **EntityMention**: Raw entity extraction from a document (before resolution)
- **EntityStatus**: Enum distinguishing canonical vs provisional entities
- **PromotionConfig**: Configuration for promoting provisional → canonical

**Entity Lifecycle:**

1. **Extraction**: The entity extractor finds mentions in document text,
   producing `EntityMention` objects with text spans and confidence scores.

2. **Resolution**: The entity resolver maps mentions to `BaseEntity` instances,
   either matching existing entities or creating new provisional ones.

3. **Promotion**: Provisional entities that accumulate sufficient usage and
   confidence are promoted to canonical status with stable identifiers.

4. **Merging**: Duplicate canonical entities detected via embedding similarity
   can be merged to maintain a clean entity vocabulary.

Entities are immutable (frozen Pydantic models) to ensure consistency when
referenced by relationships and stored in multiple indices.

> Entity system for the knowledge graph framework.

This module defines the core entity types for the knowledge graph:

- **BaseEntity**: Abstract base class for all domain entities (nodes in the graph)
- **EntityMention**: Raw entity extraction from a document (before resolution)
- **EntityStatus**: Enum distinguishing canonical vs provisional entities
- **PromotionConfig**: Configuration for promoting provisional → canonical

**Entity Lifecycle:**

1. **Extraction**: The entity extractor finds mentions in document text,
   producing `EntityMention` objects with text spans and confidence scores.

2. **Resolution**: The entity resolver maps mentions to `BaseEntity` instances,
   either matching existing entities or creating new provisional ones.

3. **Promotion**: Provisional entities that accumulate sufficient usage and
   confidence are promoted to canonical status with stable identifiers.

4. **Merging**: Duplicate canonical entities detected via embedding similarity
   can be merged to maintain a clean entity vocabulary.

Entities are immutable (frozen Pydantic models) to ensure consistency when
referenced by relationships and stored in multiple indices.


## `class EntityStatus(str, Enum)`

Lifecycle status of an entity in the knowledge graph.

Entities progress through a lifecycle from provisional (newly discovered)
to canonical (stable, authoritative). This status determines how the
entity is treated in queries, exports, and merge operations.

## `class PromotionConfig(BaseModel)`

Configuration for promoting provisional entities to canonical status.

Controls the thresholds that determine when a provisional entity has
accumulated enough evidence to be promoted. Different domains may
require different thresholds based on data quality and the availability
of external authority sources.

Attributes:
    min_usage_count: Minimum times the entity must appear across documents.
    min_confidence: Minimum confidence score from entity resolution.
    require_embedding: Whether an embedding vector is required for promotion.
**Fields:**

```python
min_usage_count: int
min_confidence: float
require_embedding: bool
```

## `class BaseEntity(ABC, BaseModel)`

Abstract base class for all domain entities (knowledge graph nodes).

Entities represent the nodes in the knowledge graph—the "things" that
relationships connect. Each entity has a unique identifier, a primary
name, optional synonyms, and domain-specific attributes.

Entities are frozen (immutable) Pydantic models. To modify an entity,
use `entity.model_copy(update={...})` to create a new instance with
updated fields.

Subclasses must implement:
    - `get_entity_type()`: Return the domain-specific type identifier

Key fields:
    - `entity_id`: Unique identifier (canonical ID or provisional UUID)
    - `status`: CANONICAL or PROVISIONAL lifecycle state
    - `name`: Primary display name
    - `synonyms`: Alternative names for matching
    - `embedding`: Semantic vector for similarity operations
    - `usage_count`: Number of document references (for promotion)
    - `confidence`: Resolution confidence score

Example:
    ```python
    class DrugEntity(BaseEntity):
        drug_class: str | None = None
        mechanism: str | None = None

        def get_entity_type(self) -> str:
            return "drug"
    ```
**Fields:**

```python
promotable: bool
entity_id: str
status: EntityStatus
name: str
synonyms: tuple[str, ...]
embedding: tuple[float, ...] | None
canonical_ids: dict[str, str]
confidence: float
usage_count: int
created_at: datetime
source: str
merged_into: str | None
metadata: dict
```

### `def BaseEntity.get_entity_type(self) -> str`

Return domain-specific entity type identifier.
Examples: 'drug', 'disease', 'gene' for medical domain;
'case', 'statute', 'court' for legal domain.

## `class EntityMention(BaseModel)`

A raw entity mention extracted from document text.

Represents the output of entity extraction (Pass 1) before resolution
to a canonical or provisional entity. Captures the exact text span,
its position in the document, and extraction confidence.

Entity mentions are intermediate objects that flow from the extractor
to the resolver. The resolver then maps each mention to an existing
entity or creates a new provisional entity.

Frozen (immutable) to ensure mentions can be safely passed through
the pipeline without modification.

Attributes:
    text: The exact text span that was identified as an entity.
    entity_type: Domain-specific type classification (e.g., "drug", "gene").
    start_offset: Character position where the mention begins.
    end_offset: Character position where the mention ends.
    confidence: Extraction confidence score (0.0 to 1.0).
    context: Optional surrounding text for disambiguation.
    metadata: Domain-specific extraction metadata.

Example:
    ```python
    mention = EntityMention(
        text="aspirin",
        entity_type="drug",
        start_offset=42,
        end_offset=49,
        confidence=0.95,
        context="...patients taking aspirin showed improved...",
    )
    ```
**Fields:**

```python
text: str
entity_type: str
start_offset: int
end_offset: int
confidence: float
context: str | None
metadata: dict
```


<span id="user-content-kgschemakgschemaidentitypy"></span>

# kgschema/kgschema/identity.py

Identity server interface for the knowledge graph framework.

The identity server is the authoritative component for entity identity across
the knowledge graph. It handles the full entity identity lifecycle:

- **resolve**: Map a mention string to a canonical or provisional entity ID,
  creating a new provisional entity if no match is found.
- **promote**: Elevate a provisional entity to canonical status when
  domain-defined thresholds are met.
- **find_synonyms**: Detect entities that refer to the same real-world concept
  (read-only; does not perform merges).
- **merge**: Collapse duplicate entities into a single survivor, redirecting
  all references from absorbed entities to the survivor.
- **on_entity_added**: Event hook called after each entity insert, triggering
  synonym detection and merge for newly added entities.

Implementations must be correct under concurrent access from multiple worker
processes and multiple server replicas. All mutating operations must be
idempotent so that workers can safely retry after transient failures.

See CONCURRENCY.md (Identity Server Specification section) for the full
design rationale, locking strategy, and merge × promotion status rules.

> Identity server interface for the knowledge graph framework.

The identity server is the authoritative component for entity identity across
the knowledge graph. It handles the full entity identity lifecycle:

- **resolve**: Map a mention string to a canonical or provisional entity ID,
  creating a new provisional entity if no match is found.
- **promote**: Elevate a provisional entity to canonical status when
  domain-defined thresholds are met.
- **find_synonyms**: Detect entities that refer to the same real-world concept
  (read-only; does not perform merges).
- **merge**: Collapse duplicate entities into a single survivor, redirecting
  all references from absorbed entities to the survivor.
- **on_entity_added**: Event hook called after each entity insert, triggering
  synonym detection and merge for newly added entities.

Implementations must be correct under concurrent access from multiple worker
processes and multiple server replicas. All mutating operations must be
idempotent so that workers can safely retry after transient failures.

See CONCURRENCY.md (Identity Server Specification section) for the full
design rationale, locking strategy, and merge × promotion status rules.


## `class IdentityServer(ABC)`

Abstract interface for entity identity management.

Implementations are responsible for resolving mentions to entity IDs,
promoting provisional entities, detecting synonyms, and merging
duplicates — all with correct behaviour under concurrent access.

The recommended implementation is Postgres-backed, using:
- ``INSERT ... ON CONFLICT DO NOTHING`` for idempotent creation
- ``SELECT FOR UPDATE`` for atomic promotion
- Postgres advisory locks (keyed on sorted entity ID pairs) for merge
- pgvector cosine similarity for synonym detection
- Redis for authority-lookup caching (shared across replicas)

Domain-pluggable behaviour (authority lookup, synonym thresholds,
survivor selection, promotion thresholds) is supplied by the domain
schema and its ``PromotionPolicy``.

### `async def IdentityServer.resolve(self, mention: str, context: dict) -> str`

Resolve a mention string to an entity ID.

Performs domain authority lookup (e.g. UMLS, DBPedia) and returns a
canonical ID if one is found. Otherwise creates and returns a new
provisional ID. The lookup result is cached (keyed on normalised
mention + authority source version) so that transient API failures
do not produce inconsistent IDs on retry.

This operation must be idempotent: resolving the same mention twice
returns the same ID.

Parameters
----------
mention:
    The surface form of the entity mention.
context:
    Domain-defined context (e.g. document ID, domain name, entity
    type hint, extraction metadata) used by authority lookup and
    synonym detection.

Returns
-------
str
    A canonical or provisional entity ID.

### `async def IdentityServer.promote(self, provisional_id: str) -> str`

Attempt to promote a provisional entity to canonical status.

The domain ``PromotionPolicy`` determines whether promotion is
warranted. Behaviour by current entity status:

- **provisional**: checks policy; upgrades if thresholds are met.
- **canonical**: no-op; returns the existing canonical ID.
  Promotion is a one-time transition.
- **merged**: the entity has been absorbed. Logs a warning with the
  stale ID and returns the survivor's ID; does not raise an error.

This operation must be idempotent.

Parameters
----------
provisional_id:
    The ID of the entity to promote. May be provisional, canonical,
    or merged.

Returns
-------
str
    The canonical ID (new or pre-existing), or the survivor ID if
    the entity was merged.

### `async def IdentityServer.find_synonyms(self, entity_id: str) -> list[str]`

Return the IDs of entities considered synonymous with the given entity.

Synonym criteria are domain-defined and may include:
- Cosine similarity above a threshold (via pgvector)
- Shared external identifier (same UMLS CUI, same MeSH term)
- String normalisation match

This method is read-only; it reports candidates without merging.
Call ``merge`` to act on the results.

Parameters
----------
entity_id:
    The entity to find synonyms for.

Returns
-------
list[str]
    IDs of synonym candidates, not including ``entity_id`` itself.
    Returns an empty list if no synonyms are found.

### `async def IdentityServer.merge(self, entity_ids: list[str], survivor_id: str) -> str`

Merge a set of entities into a single survivor.

All references (relationships, mentions, bundle edges) pointing to
any absorbed entity are redirected to the survivor. Absorbed entities
are marked ``status=MERGED`` with ``merged_into=survivor_id`` so
that stale external references remain resolvable via a single lookup.

Status rules for the survivor:
- provisional + provisional → survivor remains **provisional**
  (promotable via normal policy)
- canonical + anything → survivor remains **canonical**

Locking: implementations should acquire an advisory lock keyed on
the sorted set of entity IDs before the transaction to prevent
two workers from merging the same pair in opposite orders.

This operation must be idempotent: merging already-merged entities
is a no-op that returns the survivor ID.

Parameters
----------
entity_ids:
    The full set of IDs to unify, including the survivor.
survivor_id:
    The ID that will remain after the merge. Must be a member of
    ``entity_ids``. Determined by the caller via
    ``DomainSchema.preferred_entity``.

Returns
-------
str
    The survivor ID.

### `async def IdentityServer.on_entity_added(self, entity_id: str, context: dict) -> None`

Event hook called after an entity is inserted or updated.

Must be called inside the same transaction as the entity insert so
that synonym detection fires only after the row is durably committed
and visible. This prevents the race where two concurrent workers
each see the other as a merge candidate before either insert
completes.

Typical implementation:
1. Embed the entity (if not already embedded).
2. Call ``find_synonyms`` to identify candidates.
3. If candidates are found, call ``DomainSchema.preferred_entity``
   to select the survivor.
4. Call ``merge`` for each confirmed synonym pair.

This event-driven model subsumes batch synonym sweeps: a batch sweep
is equivalent to replaying ``on_entity_added`` for every entity in
the store.

Parameters
----------
entity_id:
    The ID of the entity that was just added or updated.
context:
    Domain-defined context forwarded from the triggering operation.


<span id="user-content-kgschemakgschemapromotionpy"></span>

# kgschema/kgschema/promotion.py

Promotion policy interface for entity canonical ID assignment.

This module provides the PromotionPolicy ABC that defines how domains
assign canonical IDs to entities during promotion from provisional to
canonical status.

> Promotion policy interface for entity canonical ID assignment.

This module provides the PromotionPolicy ABC that defines how domains
assign canonical IDs to entities during promotion from provisional to
canonical status.


## `class PromotionPolicy(ABC)`

Abstract base for domain-specific entity promotion policies.

### `def PromotionPolicy.should_promote(self, entity: BaseEntity) -> bool`

Check if entity meets promotion thresholds.

### `async def PromotionPolicy.assign_canonical_id(self, entity: BaseEntity) -> Optional[CanonicalId]`

Return canonical ID for this entity, or None if not found.

This method is async to support external API lookups.
Returns a CanonicalId object which includes the ID, URL, and synonyms.


<span id="user-content-kgschemakgschemarelationshippy"></span>

# kgschema/kgschema/relationship.py

Relationship system for the knowledge graph framework.

This module defines `BaseRelationship`, the abstract base class for all
relationships (edges) in the knowledge graph. Relationships connect entities
via typed predicates, forming the graph structure.

Each relationship is a triple: (subject_entity, predicate, object_entity)

- **Subject**: The entity performing or originating the action
- **Predicate**: The relationship type (domain-specific vocabulary)
- **Object**: The entity receiving or being affected by the action

For example:
    - ("Aspirin", "treats", "Headache")
    - ("Paper A", "cites", "Paper B")
    - ("Court Case X", "overrules", "Court Case Y")

Relationships also track:
    - **Confidence**: How certain we are about this relationship
    - **Source documents**: Which documents support this relationship
    - **Metadata**: Domain-specific evidence and provenance

Relationships are immutable (frozen Pydantic models) and are typically
extracted during Pass 2 of the ingestion pipeline, after entities have
been resolved.

> Relationship system for the knowledge graph framework.

This module defines `BaseRelationship`, the abstract base class for all
relationships (edges) in the knowledge graph. Relationships connect entities
via typed predicates, forming the graph structure.

Each relationship is a triple: (subject_entity, predicate, object_entity)

- **Subject**: The entity performing or originating the action
- **Predicate**: The relationship type (domain-specific vocabulary)
- **Object**: The entity receiving or being affected by the action

For example:
    - ("Aspirin", "treats", "Headache")
    - ("Paper A", "cites", "Paper B")
    - ("Court Case X", "overrules", "Court Case Y")

Relationships also track:
    - **Confidence**: How certain we are about this relationship
    - **Source documents**: Which documents support this relationship
    - **Metadata**: Domain-specific evidence and provenance

Relationships are immutable (frozen Pydantic models) and are typically
extracted during Pass 2 of the ingestion pipeline, after entities have
been resolved.


## `class BaseRelationship(ABC, BaseModel)`

Abstract base class for relationships (edges) in the knowledge graph.

Relationships connect two entities via a typed predicate, representing
facts extracted from source documents. The relationship model supports
aggregating evidence from multiple documents that assert the same fact.

Relationships are frozen (immutable) Pydantic models. To update a
relationship (e.g., to add a new source document), use
`rel.model_copy(update={...})` to create a new instance.

Subclasses must implement:
    - `get_edge_type()`: Return the domain-specific edge type category

Key fields:
    - `subject_id`: Entity ID of the relationship source (the "doer")
    - `predicate`: Relationship type from the domain vocabulary
    - `object_id`: Entity ID of the relationship target (the "receiver")
    - `confidence`: How certain we are about this relationship
    - `source_documents`: Documents that support this relationship

Example:
    ```python
    class TreatsRelationship(BaseRelationship):
        mechanism: str | None = None  # How the treatment works
        evidence_level: str = "observational"

        def get_edge_type(self) -> str:
            return "treats"
    ```
**Fields:**

```python
subject_id: str
predicate: str
object_id: str
confidence: float
source_documents: tuple[str, ...]
evidence: Any
created_at: datetime
last_updated: datetime | None
metadata: dict
```

### `def BaseRelationship.get_edge_type(self) -> str`

Return domain-specific edge type category.

Examples: 'treats', 'causes', 'interacts_with' for medical domain;
'cites', 'overrules', 'interprets' for legal domain.


<span id="user-content-kgschemakgschemaspecpy"></span>

# kgschema/kgschema/spec.py

Domain spec models for entity types, predicates, evidence, and mentions.

Used by domain_spec.py modules to define schema in Python as single source of truth.

> Domain spec models for entity types, predicates, evidence, and mentions.

Used by domain_spec.py modules to define schema in Python as single source of truth.


## `class EntitySpec(BaseModel)`

Display and prompt metadata for an entity type.
**Fields:**

```python
description: str
prompt_guidance: str
color: str
label: str
metadata_only: bool
```

## `class PredicateSpec(BaseModel)`

Validity and dedup metadata for a predicate.

subject_types/object_types: when None, means any entity type.
specificity: for dedup; higher = prefer when (s,o) has multiple predicates.
symmetric: if True, store with canonical (min,max) ordering; query layer treats as undirected.
is_merge_signal: if True, drives entity canonicalization (e.g. SAME_AS). Distinct from plain symmetric.
**Fields:**

```python
description: str
subject_types: Optional[list[type]]
object_types: Optional[list[type]]
specificity: int
symmetric: bool
is_merge_signal: bool
```

## `class EvidenceSpec(BaseModel)`

Evidence ID format and extraction methods.
**Fields:**

```python
id_format: str
methods: list[str]
section_names: list[str]
```

## `class MentionsSpec(BaseModel)`

Rules for entity mention extraction.
**Fields:**

```python
mentionable_types: list[type]
skip_name_equals_type: bool
```


<span id="user-content-kgschemakgschemastoragepy"></span>

# kgschema/kgschema/storage.py

Storage interface definitions for the knowledge graph framework.

This module defines abstract interfaces for persisting knowledge graph data:
entities, relationships, and documents. These interfaces decouple the core
framework from specific storage backends, enabling:

- **In-memory storage** for testing and development
- **Relational databases** (PostgreSQL, MySQL) for ACID guarantees
- **Vector databases** (Pinecone, Weaviate, Qdrant) for embedding search
- **Graph databases** (Neo4j, ArangoDB) for relationship traversal

All interfaces are async-first to support non-blocking I/O with database
drivers like asyncpg, motor, or aioredis.

The storage layer supports key knowledge graph operations:
    - Entity lifecycle: create, read, update, delete, promote, merge
    - Relationship management: add, query by subject/object, update references
    - Document tracking: store source documents for provenance
    - Similarity search: find entities by embedding vectors

> Storage interface definitions for the knowledge graph framework.

This module defines abstract interfaces for persisting knowledge graph data:
entities, relationships, and documents. These interfaces decouple the core
framework from specific storage backends, enabling:

- **In-memory storage** for testing and development
- **Relational databases** (PostgreSQL, MySQL) for ACID guarantees
- **Vector databases** (Pinecone, Weaviate, Qdrant) for embedding search
- **Graph databases** (Neo4j, ArangoDB) for relationship traversal

All interfaces are async-first to support non-blocking I/O with database
drivers like asyncpg, motor, or aioredis.

The storage layer supports key knowledge graph operations:
    - Entity lifecycle: create, read, update, delete, promote, merge
    - Relationship management: add, query by subject/object, update references
    - Document tracking: store source documents for provenance
    - Similarity search: find entities by embedding vectors


## `class EntityStorageInterface(ABC)`

Abstract interface for entity storage operations.

Entity storage is the primary persistence layer for knowledge graph nodes.
It must support both basic CRUD operations and specialized queries for
the entity lifecycle:

- **Canonical entities**: Stable entities linked to authoritative sources
  (UMLS CUIs, DBPedia URIs, etc.)
- **Provisional entities**: Newly discovered mentions awaiting promotion
  based on usage frequency and confidence thresholds

Implementations must handle:
    - Efficient lookup by ID and name/synonyms
    - Embedding-based similarity search for resolution and merge detection
    - Atomic promotion (provisional → canonical) and merge operations
    - Pagination for listing large entity collections

Thread safety: Implementations should be safe for concurrent access from
multiple async tasks.

### `async def EntityStorageInterface.add(self, entity: BaseEntity) -> str`

Store an entity and return its ID.

This is the primary method for persisting new entities. The entity's
`entity_id` field determines its storage key.

Args:
    entity: The entity to store. Must have a valid entity_id.

Returns:
    The entity_id of the stored entity.

Raises:
    ValueError: If entity_id is missing or invalid.

Note:
    If an entity with the same ID already exists, implementations
    may either update it (upsert behavior) or raise an error,
    depending on the backend's policy.

### `async def EntityStorageInterface.get(self, entity_id: str) -> BaseEntity | None`

Retrieve an entity by its unique identifier.

Args:
    entity_id: The unique identifier of the entity to retrieve.

Returns:
    The entity if found, or None if no entity exists with that ID.

### `async def EntityStorageInterface.get_batch(self, entity_ids: Sequence[str]) -> list[BaseEntity | None]`

Retrieve multiple entities by ID in a single operation.

Batch retrieval is more efficient than multiple get() calls,
especially for network-based storage backends.

Args:
    entity_ids: Sequence of entity IDs to retrieve.

Returns:
    List of entities in the same order as input IDs. Missing
    entities are represented as None in the corresponding position.

### `async def EntityStorageInterface.find_by_embedding(self, embedding: Sequence[float], threshold: float = 0.8, limit: int = 10) -> list[tuple[BaseEntity, float]]`

Find entities semantically similar to the given embedding vector.

This is the core operation for entity resolution and duplicate
detection. Uses cosine similarity (or similar metric) to compare
the query embedding against stored entity embeddings.

Args:
    embedding: Query embedding vector. Must have the same dimension
        as stored entity embeddings.
    threshold: Minimum similarity score (0.0 to 1.0) for inclusion
        in results. Higher thresholds return fewer, more similar results.
    limit: Maximum number of results to return.

Returns:
    List of (entity, similarity_score) tuples, sorted by descending
    similarity. Only includes entities with similarity >= threshold.
    Returns empty list if no entities meet the threshold.

Note:
    Performance depends heavily on the storage backend. Consider
    using specialized vector indices (pgvector, FAISS, HNSW) for
    large entity collections.

### `async def EntityStorageInterface.find_by_name(self, name: str, entity_type: str | None = None, limit: int = 10) -> list[BaseEntity]`

Find entities matching the given name or synonym.

Searches the entity's primary name and any registered synonyms.
Matching may be exact or fuzzy depending on the implementation.

Args:
    name: The name or synonym to search for.
    entity_type: Optional filter to restrict results to a specific
        entity type (e.g., 'drug', 'gene', 'person').
    limit: Maximum number of results to return.

Returns:
    List of matching entities, ordered by relevance (implementation-
    dependent). Returns empty list if no matches found.

### `async def EntityStorageInterface.find_provisional_for_promotion(self, min_usage: int, min_confidence: float) -> list[BaseEntity]`

Find provisional entities eligible for promotion to canonical status.

Promotion eligibility is based on:
    - Entity status is PROVISIONAL
    - Usage count >= min_usage (evidence of repeated mentions)
    - Confidence score >= min_confidence

Args:
    min_usage: Minimum number of times the entity must have been
        referenced across documents.
    min_confidence: Minimum confidence score from entity resolution.

Returns:
    List of provisional entities meeting the promotion criteria.
    These entities are candidates for canonical ID assignment.

### `async def EntityStorageInterface.update(self, entity: BaseEntity) -> bool`

Update an existing entity's data.

Replaces the stored entity with the provided entity. The entity_id
must match an existing entity.

Args:
    entity: The updated entity. The entity_id field identifies
        which entity to update.

Returns:
    True if the entity was found and updated, False if no entity
    exists with the given ID.

### `async def EntityStorageInterface.promote(self, entity_id: str, new_entity_id: str, canonical_ids: dict[str, str]) -> BaseEntity | None`

Promote a provisional entity to canonical status.

Promotion involves:
    1. Changing the entity's status from PROVISIONAL to CANONICAL
    2. Assigning the new canonical entity_id
    3. Recording canonical IDs from external authorities

Args:
    entity_id: Current ID of the provisional entity to promote.
    new_entity_id: New canonical ID for the entity (typically
        derived from an authority like UMLS or DBPedia).
    canonical_ids: Mapping of authority names to their IDs for this
        entity (e.g., {'umls': 'C0004057', 'mesh': 'D001241'}).

Returns:
    The updated entity with canonical status, or None if no entity
    was found with the given entity_id.

Note:
    Implementations should also update any relationships referencing
    the old entity_id, or provide a separate method for this.

### `async def EntityStorageInterface.merge(self, source_ids: Sequence[str], target_id: str) -> bool`

Merge multiple entities into a single target entity.

Used when duplicate detection identifies entities that represent
the same real-world concept. The merge operation:
    - Combines usage counts from all source entities into target
    - Merges synonyms from source entities into target
    - Removes source entities from storage
    - (Optionally) Updates relationship references

Args:
    source_ids: IDs of entities to merge into the target. These
        entities will be deleted after merging.
    target_id: ID of the entity that will absorb the source entities.
        Must exist in storage.

Returns:
    True if the merge succeeded, False if target_id was not found
    or if any source entity could not be processed.

### `async def EntityStorageInterface.delete(self, entity_id: str) -> bool`

Delete an entity from storage.

Args:
    entity_id: ID of the entity to delete.

Returns:
    True if the entity was found and deleted, False if no entity
    exists with the given ID.

Warning:
    Deleting entities may leave orphaned relationship references.
    Consider using merge() instead to preserve data integrity.

### `async def EntityStorageInterface.count(self) -> int`

Return the total number of entities in storage.

Returns:
    Integer count of all entities (both canonical and provisional).

### `async def EntityStorageInterface.list_all(self, status: str | None = None, limit: int = 1000, offset: int = 0) -> list[BaseEntity]`

List entities with pagination and optional filtering.

Args:
    status: Optional filter by entity status. Valid values:
        - 'canonical': Only canonical entities
        - 'provisional': Only provisional entities
        - None: All entities regardless of status
    limit: Maximum number of entities to return (default 1000).
    offset: Number of entities to skip for pagination (default 0).

Returns:
    List of entities matching the filter criteria. Order is
    implementation-dependent but should be consistent across
    paginated calls.

## `class RelationshipStorageInterface(ABC)`

Abstract interface for relationship (edge) storage operations.

Relationships represent the edges in the knowledge graph, connecting
entity nodes via typed predicates. Each relationship is a triple:
(subject_entity, predicate, object_entity) with additional metadata.

Key operations:
    - **Graph traversal**: Query outgoing edges (by subject) or
      incoming edges (by object) for graph navigation
    - **Triple lookup**: Check if a specific relationship exists
    - **Reference updates**: Maintain referential integrity when
      entities are promoted or merged
    - **Provenance tracking**: Query relationships by source document

Relationships may be extracted from multiple documents, so implementations
should support aggregating evidence (confidence scores, source documents)
when the same triple is extracted repeatedly.

### `async def RelationshipStorageInterface.add(self, relationship: BaseRelationship) -> str`

Store a relationship and return an identifier.

Args:
    relationship: The relationship to store, containing subject_id,
        predicate, object_id, and metadata (confidence, sources).

Returns:
    An identifier for the stored relationship. This may be a
    composite key derived from the triple or a generated ID.

Note:
    If a relationship with the same (subject, predicate, object)
    triple already exists, implementations may:
        - Merge metadata (combine source documents, update confidence)
        - Replace the existing relationship
        - Raise an error
    The exact behavior is implementation-dependent.

### `async def RelationshipStorageInterface.get_by_subject(self, subject_id: str, predicate: str | None = None) -> list[BaseRelationship]`

Get all relationships where the given entity is the subject.

This retrieves outgoing edges from an entity—relationships where
the entity is the "doer" or source of the action.

Args:
    subject_id: ID of the entity whose outgoing relationships to find.
    predicate: Optional filter to restrict results to a specific
        relationship type (e.g., 'treats', 'cites', 'authored_by').

Returns:
    List of relationships with the given subject. Returns empty
    list if no matching relationships exist.

Example:
    # Get all things that aspirin treats
    relationships = await storage.get_by_subject(aspirin_id, 'treats')

### `async def RelationshipStorageInterface.get_by_object(self, object_id: str, predicate: str | None = None) -> list[BaseRelationship]`

Get all relationships where the given entity is the object.

This retrieves incoming edges to an entity—relationships where
the entity is the "receiver" or target of the action.

Args:
    object_id: ID of the entity whose incoming relationships to find.
    predicate: Optional filter to restrict results to a specific
        relationship type.

Returns:
    List of relationships with the given object. Returns empty
    list if no matching relationships exist.

Example:
    # Get all drugs that treat headache
    relationships = await storage.get_by_object(headache_id, 'treats')

### `async def RelationshipStorageInterface.find_by_triple(self, subject_id: str, predicate: str, object_id: str) -> BaseRelationship | None`

Find a specific relationship by its complete triple.

Args:
    subject_id: ID of the subject entity.
    predicate: The relationship type/predicate.
    object_id: ID of the object entity.

Returns:
    The relationship if it exists, or None if no such triple
    has been stored.

Example:
    # Check if aspirin treats headache
    rel = await storage.find_by_triple(aspirin_id, 'treats', headache_id)
    if rel:
        print(f"Confidence: {rel.confidence}")

### `async def RelationshipStorageInterface.update_entity_references(self, old_entity_id: str, new_entity_id: str) -> int`

Update all relationships referencing an entity to use a new ID.

This is critical for maintaining referential integrity when:
    - Promoting a provisional entity (ID changes)
    - Merging duplicate entities (source IDs point to target)

Args:
    old_entity_id: The entity ID being replaced.
    new_entity_id: The entity ID to use in its place.

Returns:
    The number of relationship references that were updated.
    A relationship with both subject and object matching old_entity_id
    counts as two updates.

### `async def RelationshipStorageInterface.get_by_document(self, document_id: str) -> list[BaseRelationship]`

Get all relationships extracted from a specific document.

Useful for:
    - Viewing all knowledge extracted from a document
    - Re-processing a document (delete old relationships first)
    - Audit and provenance tracking

Args:
    document_id: ID of the source document.

Returns:
    List of relationships where document_id appears in the
    source_documents metadata. Returns empty list if no
    relationships reference that document.

### `async def RelationshipStorageInterface.delete(self, subject_id: str, predicate: str, object_id: str) -> bool`

Delete a specific relationship by its triple.

Args:
    subject_id: ID of the subject entity.
    predicate: The relationship type/predicate.
    object_id: ID of the object entity.

Returns:
    True if the relationship was found and deleted, False if
    no such relationship exists.

### `async def RelationshipStorageInterface.count(self) -> int`

Return the total number of relationships in storage.

Returns:
    Integer count of all stored relationships.

### `async def RelationshipStorageInterface.list_all(self, limit: int = 1000, offset: int = 0) -> list[BaseRelationship]`

List all relationships with pagination.

Args:
    limit: Maximum number of relationships to return (default 1000).
    offset: Number of relationships to skip for pagination (default 0).

Returns:
    List of relationships. Order is implementation-dependent but
    should be consistent across paginated calls.

## `class DocumentStorageInterface(ABC)`

Abstract interface for document storage operations.

Document storage provides persistence for source documents that have been
ingested into the knowledge graph. Documents are retained for:

- **Provenance**: Track where entities and relationships originated
- **Deduplication**: Detect if a document has already been processed
- **Re-processing**: Enable re-extraction when pipeline components improve
- **Debugging**: Examine source content when validating extractions

Documents may store full content or just metadata, depending on storage
constraints and use case requirements.

### `async def DocumentStorageInterface.add(self, document: BaseDocument) -> str`

Store a document and return its ID.

Args:
    document: The document to store, including content and metadata.

Returns:
    The document_id of the stored document.

Note:
    If a document with the same ID already exists, implementations
    may update it or raise an error.

### `async def DocumentStorageInterface.get(self, document_id: str) -> BaseDocument | None`

Retrieve a document by its unique identifier.

Args:
    document_id: The unique identifier of the document.

Returns:
    The document if found, or None if no document exists with that ID.

### `async def DocumentStorageInterface.find_by_source(self, source_uri: str) -> BaseDocument | None`

Find a document by its source URI.

Used for deduplication—check if a document from a given source
has already been ingested.

Args:
    source_uri: The URI from which the document was obtained
        (e.g., URL, file path, DOI).

Returns:
    The document if found, or None if no document has that source_uri.

### `async def DocumentStorageInterface.list_ids(self, limit: int = 100, offset: int = 0) -> list[str]`

List document IDs with pagination.

Useful for batch operations that need to iterate over all documents
without loading full document content.

Args:
    limit: Maximum number of IDs to return (default 100).
    offset: Number of IDs to skip for pagination (default 0).

Returns:
    List of document IDs. Order is implementation-dependent but
    should be consistent across paginated calls.

### `async def DocumentStorageInterface.delete(self, document_id: str) -> bool`

Delete a document from storage.

Args:
    document_id: ID of the document to delete.

Returns:
    True if the document was found and deleted, False if no
    document exists with the given ID.

Warning:
    Deleting a document does not automatically delete entities
    or relationships extracted from it. Consider whether to
    preserve or clean up related data.

### `async def DocumentStorageInterface.count(self) -> int`

Return the total number of documents in storage.

Returns:
    Integer count of all stored documents.


<span id="user-content-kgserverdomainspecpy"></span>

# kgserver/domain_spec.py

Domain spec for medical literature extraction.

Single source of truth for entity types, predicates, evidence, and mentions.
Consumers import from this module instead of loading YAML config.

> Domain spec for medical literature extraction.

Single source of truth for entity types, predicates, evidence, and mentions.
Consumers import from this module instead of loading YAML config.


## `class DiseaseEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class GeneEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class DrugEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class ProteinEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class HormoneEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class EnzymeEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class BiomarkerEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class SymptomEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class ProcedureEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class MutationEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class PathwayEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class BiologicalProcessEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class AnatomicalStructureEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class AuthorEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class InstitutionEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class PaperEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class HypothesisEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class EvidenceEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class LocationEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class EthnicityEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```


<span id="user-content-kgserverindexmd"></span>

# kgserver/index.md

# KGserver

A **read-only server** for a loaded knowledge graph. It does not ingest raw documents; domain pipelines build a bundle (entities + relationships), and the server loads that bundle at startup.

**Quick links:**

- [Medical literature chat](/chat/)
- [OpenAPI spec](/docs/)
- [Graph visualization](/graph-viz/) — currently focused on medical literature
- [GraphQL GUI](/graphiql/)

    ...

<span id="user-content-kgservermcpmainpy"></span>

# kgserver/mcp_main.py

Standalone MCP server entrypoint (SSE on port 8001).

Run with: uvicorn mcp_main:app --host 0.0.0.0 --port 8001

SSE endpoint: http://localhost:8001/sse (mount at root so path stays /sse).

> 
Standalone MCP server entrypoint (SSE on port 8001).

Run with: uvicorn mcp_main:app --host 0.0.0.0 --port 8001

SSE endpoint: http://localhost:8001/sse (mount at root so path stays /sse).


### `async def lifespan(app: FastAPI)`

Create all kgserver tables (entity, relationship, bundle, ingest_jobs, etc.)
before the bfsql lifespan runs, so the entity table always exists at startup.

### `async def health()`

Health check for container/orchestration.


<span id="user-content-kgservermcpserverinitpy"></span>

# kgserver/mcp_server/__init__.py

MCP (Model Context Protocol) server for Knowledge Graph.

Uses bfsql (BFS-QL) as the core graph query engine, exposing four standard
tools (describe_schema, search_entities, bfs_query, describe_entity) plus
kgserver-specific tools for ingestion and bundle inspection.

> 
MCP (Model Context Protocol) server for Knowledge Graph.

Uses bfsql (BFS-QL) as the core graph query engine, exposing four standard
tools (describe_schema, search_entities, bfs_query, describe_entity) plus
kgserver-specific tools for ingestion and bundle inspection.



<span id="user-content-kgservermcpserveringestworkerpy"></span>

# kgserver/mcp_server/ingest_worker.py

Background worker for paper ingestion jobs.

Processes jobs from a queue: fetch URL, run fetch_vocab/extract/ingest/build_bundle pipeline, load bundle incrementally.

> 
Background worker for paper ingestion jobs.

Processes jobs from a queue: fetch URL, run fetch_vocab/extract/ingest/build_bundle pipeline, load bundle incrementally.


### `def _storage_for_worker() -> tuple[StorageInterface, Callable[[], None]]`

Return (storage, close_fn) for use in the worker. Caller must call close_fn when done.

### `def _workspace_root() -> Path`

Persistent workspace root from env, defaulting to ./ingest_workspace.

### `def _ensure_workspace_dirs(root: Path) -> tuple[Path, Path, Path, Path]`

Create and return (bundles_dir, merged_dir, output_dir, vocab_dir). These persist across jobs.

Note: output_dir (bundle/) is always fully rebuilt by build_bundle.
The true incremental state is bundles_dir + merged_dir + vocab_dir (especially synonym_cache.json).

### `def _workspace_lock(workspace_root: Path)`

File lock serializing ingest → build_bundle → load_bundle_incremental across workers.

### `def _run_pass2_pass3_load(workspace_root: Path, bundles_dir: Path, merged_dir: Path, output_dir: Path) -> None`

Run ingest, build_bundle, and load_bundle_incremental under workspace lock. Raises on failure.

### `async def start_worker(max_workers: int = 1) -> None`

Start background worker tasks that process the ingest job queue.

### `async def stop_worker() -> None`

Cancel worker tasks and stop processing new jobs.

### `async def enqueue_job(job_id: str) -> None`

Add a job id to the queue. Non-blocking.

### `async def _worker_loop() -> None`

Pull job IDs from the queue and run ingestion.

### `async def _run_ingest_job(job_id: str) -> None`

Fetch job, run pipeline (Pass 1 → 2 → 3), load bundle incrementally, update job.

### `async def _run_ingest_job_impl(job_id: str, storage: StorageInterface, job) -> None`

Core implementation: fetch URL, run pipeline, load bundle.


<span id="user-content-kgservermcpserverserverpy"></span>

# kgserver/mcp_server/server.py

MCP Server implementation using bfsql (BFS-QL) as the core graph query engine.

Provides the five standard BFS-QL tools (describe_schema, search_entities,
bfs_query, intersect_subgraphs, describe_entity) via PostgresBackend, plus kgserver-specific tools
for ingestion, bundle inspection, and paper source retrieval.

> 
MCP Server implementation using bfsql (BFS-QL) as the core graph query engine.

Provides the five standard BFS-QL tools (describe_schema, search_entities,
bfs_query, intersect_subgraphs, describe_entity) via PostgresBackend, plus kgserver-specific tools
for ingestion, bundle inspection, and paper source retrieval.


### `def _get_storage()`

Context manager yielding a storage instance. Extracted for testability.

### `def _get_bundle_path() -> Path`

Resolve BUNDLE_PATH; raise ValueError if unset or invalid.

### `def _read_from_bundle(relative_path: str) -> str`

Read file from bundle (directory or ZIP). Returns file contents as string.

### `async def ingest_paper(url: str) -> dict`

Ingest a medical paper from a URL into the knowledge graph.

Kicks off a background job. Returns immediately with a job_id.
Poll check_ingest_status(job_id) to track progress.
Supports PMC full-text URLs and direct XML/JSON URLs.

Returns:
    Dict with job_id, status, url, message.

### `def check_ingest_status(job_id: str) -> dict`

Check the status of a paper ingestion job.

Returns:
    Dict with job_id, status, url, paper_title, pmcid, entities_added,
    relationships_added, error, created_at, started_at, completed_at.
Status values: queued | running | complete | failed | not_found

### `def get_paper_source(paper_id: str, max_chars: Optional[int] = None) -> str`

Retrieve the raw JATS-XML source of a paper for mention-inspection diagnostics.

Reads from bundle sources/ directory (or inside a ZIP bundle). Use with
get_mentions to verify that extracted mentions match the source text.

Args:
    paper_id: Paper identifier (e.g. PMC12345). Accepts with or without .xml suffix.
    max_chars: If set, truncate the returned string to this length.

Returns:
    Raw XML string. Raises ValueError if BUNDLE_PATH unset or paper not found.

### `def get_mentions(paper_id: Optional[str] = None) -> list[dict]`

Retrieve entity mentions from the bundle for mention-inspection diagnostics.

Reads mentions.jsonl (MentionRow schema). Filter by document_id when paper_id
is provided. Use with get_paper_source to verify extracted mentions against
the source text.

Args:
    paper_id: If provided, filter to mentions where document_id matches.
        For medlit, values are like PMC12345. If None, return all mentions.

Returns:
    List of mention dicts (entity_id, document_id, text_span, etc.).
    Empty list if mentions.jsonl missing or no matches.

### `def get_bundle_info() -> dict | None`

Get bundle metadata for debugging and provenance.

Returns information about the currently loaded knowledge graph bundle,
including bundle ID, domain, creation timestamp, and metadata.

Returns:
    Bundle dictionary with fields: bundleId, domain, createdAt, metadata.
    Returns None if no bundle is loaded.

### `def graphql_query(query: str, variables: Optional[dict[str, Any]] = None) -> dict`

Run an arbitrary GraphQL query against the knowledge graph.

Uses the same schema as the HTTP /graphql endpoint. Use this for custom
query shapes, multiple roots in one request, or when the discrete tools
are not enough. The schema supports: entity(id), entities(limit, offset,
filter), relationship(subjectId, predicate, objectId), relationships(limit,
offset, filter), bundle.

Args:
    query: GraphQL query string (e.g. "{ entity(id: "MeSH:D001943") { name } }").
    variables: Optional map of variable names to values for parameterized queries.

Returns:
    Dictionary with "data" (result payload, or None if errors) and "errors"
    (list of error dicts, or None if successful).


<span id="user-content-kgserverpipelineinterfacepy"></span>

# kgserver/pipeline_interface.py

Abstract base class for domain-specific ingest pipelines.

kgserver is domain-agnostic: it does not import any domain package directly.
Instead, a concrete implementation of IngestPipeline is loaded at startup from
the class path specified in the INGEST_PIPELINE_CLASS environment variable.

Domain packages (e.g. medlit_bundle) implement this interface and register
themselves via that env var.

Example::

    INGEST_PIPELINE_CLASS=medlit.pipeline.MedlitPipeline

> 
Abstract base class for domain-specific ingest pipelines.

kgserver is domain-agnostic: it does not import any domain package directly.
Instead, a concrete implementation of IngestPipeline is loaded at startup from
the class path specified in the INGEST_PIPELINE_CLASS environment variable.

Domain packages (e.g. medlit_bundle) implement this interface and register
themselves via that env var.

Example::

    INGEST_PIPELINE_CLASS=medlit.pipeline.MedlitPipeline


## `class IngestPipeline(ABC)`

Domain-specific ingest pipeline contract.

Implementations provide the four pipeline stages used by ingest_worker,
plus entity-type metadata for graph visualization.

All Path arguments are absolute paths to existing directories.
Implementations may assume the directories already exist.

### `async def IngestPipeline.fetch_vocab(self, input_dir: Path, vocab_dir: Path, llm_backend: str, papers: object, limit: int) -> None`

Pass 0: build/merge vocabulary from documents in input_dir into vocab_dir.

Parameters
----------
input_dir:
    Directory containing raw input documents (e.g. PubMed XML files).
vocab_dir:
    Persistent workspace directory for accumulated vocabulary files.
llm_backend:
    LLM backend identifier (e.g. "anthropic", "openai").
papers:
    Optional paper filter; pass None to process all documents in input_dir.
limit:
    Maximum number of documents to process in this call.

### `async def IngestPipeline.extract(self, input_dir: Path, bundles_dir: Path, llm_backend: str, limit: int, vocab_file: Path) -> None`

Pass 1 + 2: extract entities and relationships from documents, writing
per-document bundle JSON files into bundles_dir.

Parameters
----------
input_dir:
    Directory containing raw input documents.
bundles_dir:
    Output directory for per-document bundle JSON files (paper_*.json).
llm_backend:
    LLM backend identifier.
limit:
    Maximum number of documents to process.
vocab_file:
    Path to the accumulated vocabulary file produced by fetch_vocab.

### `def IngestPipeline.run_ingest(self, bundle_dir: Path, output_dir: Path, synonym_cache_path: Path, canonical_id_cache_path: object) -> None`

Pass 2 post-processing: merge bundle files, resolve synonyms and canonical IDs.

Parameters
----------
bundle_dir:
    Directory containing per-document bundle JSON files.
output_dir:
    Directory for merged output (synonym_cache.json, etc.).
synonym_cache_path:
    Path to the seeded or accumulated synonym cache file.
canonical_id_cache_path:
    Optional path to a canonical ID cache file; pass None to skip.

### `def IngestPipeline.build_bundle(self, merged_dir: Path, bundles_dir: Path, output_dir: Path) -> None`

Pass 3: assemble the final loadable bundle (manifest.json + NDJSON files).

Parameters
----------
merged_dir:
    Directory containing merged/deduped data from run_ingest.
bundles_dir:
    Directory containing per-document bundle JSON files.
output_dir:
    Output directory; must contain manifest.json on success.

### `def IngestPipeline.get_entity_type_specs(self) -> dict[str, dict[str, str]]`

Return entity-type metadata for graph visualization.

Returns a mapping of entity_type string to a dict with keys:
    - ``"color"``: hex color string (e.g. ``"#e57373"``)
    - ``"label"``: human-readable display label

A ``"default"`` key must be included as a fallback for unknown types.

The base implementation returns only the default entry.  Override in
domain subclasses to add domain-specific entity types.


<span id="user-content-kgserverpipelineloaderpy"></span>

# kgserver/pipeline_loader.py

Runtime loader for the domain-specific IngestPipeline implementation.

The pipeline class is specified via the INGEST_PIPELINE_CLASS environment
variable as a dotted import path, e.g.::

    INGEST_PIPELINE_CLASS=medlit.pipeline.MedlitPipeline

The class must be a concrete subclass of
:class:`kgserver.pipeline_interface.IngestPipeline`.

If the variable is unset or the import fails, callers receive a clear
error at the point of use rather than at server startup.

> 
Runtime loader for the domain-specific IngestPipeline implementation.

The pipeline class is specified via the INGEST_PIPELINE_CLASS environment
variable as a dotted import path, e.g.::

    INGEST_PIPELINE_CLASS=medlit.pipeline.MedlitPipeline

The class must be a concrete subclass of
:class:`kgserver.pipeline_interface.IngestPipeline`.

If the variable is unset or the import fails, callers receive a clear
error at the point of use rather than at server startup.


### `def get_pipeline() -> IngestPipeline`

Return the singleton IngestPipeline instance.

The implementation class is loaded from the INGEST_PIPELINE_CLASS
environment variable on first call and cached for subsequent calls.

Raises
------
RuntimeError
    If INGEST_PIPELINE_CLASS is not set or the class cannot be loaded.
TypeError
    If the loaded class is not a subclass of IngestPipeline.

### `def reset_pipeline() -> None`

Clear the cached pipeline instance.

Intended for use in tests that need to swap implementations between cases.


<span id="user-content-kgserverqueryinitpy"></span>

# kgserver/query/__init__.py

Query module for knowledge graph server.


<span id="user-content-kgserverquerybundleloaderpy"></span>

# kgserver/query/bundle_loader.py

Bundle loading utilities for the KG server.
Handles loading bundles from directories or ZIP files at startup.

> 
Bundle loading utilities for the KG server.
Handles loading bundles from directories or ZIP files at startup.


### `def load_bundle_at_startup(engine, db_url: str) -> None`

Load a bundle at server startup if BUNDLE_PATH is set.

Environment variables:
    BUNDLE_PATH: Path to a bundle directory or ZIP file

### `def _load_from_zip(engine, db_url: str, zip_path: Path) -> None`

Extract and load a bundle from a ZIP file.

### `def _load_from_directory(engine, db_url: str, bundle_dir: Path) -> None`

Load a bundle from a directory.

### `def _find_manifest(search_dir: Path) -> Path | None`

Find manifest.json in a directory (possibly in a subdirectory).

### `def _get_docs_destination_path(asset_path: str, app_docs: Path) -> Path | None`

Determine the destination path for a documentation asset.

### `def _process_single_doc_asset(line: str, bundle_dir: Path, app_docs: Path) -> bool`

Process a single documentation asset entry.

### `def _load_doc_assets(bundle_dir: Path, manifest: BundleManifestV1) -> None`

Load documentation assets from doc_assets.jsonl into docs directory.

Reads the doc_assets.jsonl file (if present) and copies all listed assets
to the docs directory, preserving directory structure. Special handling for
mkdocs.yml which is moved to the app root.

The docs directory defaults to /app/docs (for Docker) but can be overridden
via the KGSERVER_DOCS_DIR environment variable for local development.

Note: These are human-readable documentation files (markdown, images, etc.),
NOT source documents (papers, articles) used for entity extraction.

### `def _build_mkdocs_if_present()`

Build MkDocs documentation if mkdocs.yml exists and site is not already prebuilt.

### `def _initialize_storage(session: Session, db_url: str) -> StorageInterface`

Initialize and return the appropriate StorageInterface.

### `def _handle_force_reload(session: Session, bundle_id: str, storage: StorageInterface) -> bool`

Handle force reload logic, returning True if bundle should be skipped.

### `def _do_load(engine, db_url: str, bundle_dir: Path, manifest_path: Path) -> None`

Actually load the bundle into storage.


<span id="user-content-kgserverquerygraphtraversalpy"></span>

# kgserver/query/graph_traversal.py

Graph traversal logic for subgraph extraction.

Provides BFS-based traversal to extract subgraphs centered on a given entity,
returning D3.js-compatible node and edge data structures.

Symmetric predicates (PredicateSpec.symmetric=True): Storage uses canonical
(min,max) ordering for subject/object. Traversal MUST treat such edges as
undirected: we follow both subject_id and object_id (see BFS below), so
queries like "everyone X has collaborated with" work regardless of storage
direction.

> 
Graph traversal logic for subgraph extraction.

Provides BFS-based traversal to extract subgraphs centered on a given entity,
returning D3.js-compatible node and edge data structures.

Symmetric predicates (PredicateSpec.symmetric=True): Storage uses canonical
(min,max) ordering for subject/object. Traversal MUST treat such edges as
undirected: we follow both subject_id and object_id (see BFS below), so
queries like "everyone X has collaborated with" work regardless of storage
direction.


## `class GraphNode(BaseModel)`

D3-compatible node representation.
**Fields:**

```python
id: str
label: str
entity_type: str
properties: dict[str, Any]
```

## `class GraphEdge(BaseModel)`

D3-compatible edge representation.
**Fields:**

```python
source: str
target: str
label: str
predicate: str
properties: dict[str, Any]
```

## `class SubgraphResponse(BaseModel)`

Response format for graph visualization.
**Fields:**

```python
nodes: list[GraphNode]
edges: list[GraphEdge]
center_id: Optional[str]
hops: int
truncated: bool
total_entities: int
total_relationships: int
```

### `def _entity_to_node(entity) -> GraphNode`

Convert a storage Entity to a GraphNode.

### `def _sanitize_source_documents(docs: list[str]) -> list[str]`

Filter out placeholder values from source_documents.

### `def _entity_to_full_node(entity) -> dict[str, Any]`

Convert storage Entity to full node dict for BFS subgraph response.

### `def _entity_to_stub_node(entity) -> dict[str, Any]`

Convert storage Entity to stub node dict (identity only).

### `def _relationship_to_full_edge(rel) -> dict[str, Any]`

Convert storage Relationship to full edge dict for BFS subgraph response.

### `def _relationship_to_stub_edge(rel) -> dict[str, Any]`

Convert storage Relationship to stub edge dict (topology only).

### `def _relationship_to_edge(rel) -> GraphEdge`

Convert a storage Relationship to a GraphEdge.

### `def extract_subgraph(storage: StorageInterface, center_id: str, hops: int = 2, max_nodes: int = DEFAULT_MAX_NODES) -> SubgraphResponse`

Extract a subgraph centered on a given entity using BFS.

Args:
    storage: Storage interface for querying entities and relationships.
    center_id: The entity ID to center the subgraph on.
    hops: Number of hops (depth) to traverse from center (1-5).
    max_nodes: Maximum number of nodes to include.

Returns:
    SubgraphResponse with nodes, edges, and metadata.

### `def _extract_subgraph_multi_seed(storage: StorageInterface, seed_ids: list[str], hops: int = 2, max_nodes: int = DEFAULT_MAX_NODES, min_confidence: Optional[float] = None, predicate_set: Optional[frozenset[str]] = None) -> tuple[list, list, bool]`

Multi-seed BFS returning raw Entity and Relationship objects.

Returns (entities, relationships, truncated).
Used by REST subgraph API.

### `def extract_subgraph_bfs(storage: StorageInterface, seed_ids: list[str], hops: int = 2, max_nodes: int = DEFAULT_MAX_NODES, min_confidence: Optional[float] = None, node_filter: Optional[dict[str, Any]] = None, edge_filter: Optional[dict[str, Any]] = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]], bool]`

Multi-seed BFS returning serialized nodes and edges with optional full/stub presentation.

Topology: BFS with min_confidence filter only (no predicate-based topology filtering).
Presentation: node_filter.entity_types and edge_filter.predicates control full vs stub.

Returns (nodes, edges, truncated).

### `def extract_full_graph(storage: StorageInterface, max_nodes: int = DEFAULT_MAX_NODES) -> SubgraphResponse`

Extract the entire graph (up to max_nodes).

Args:
    storage: Storage interface for querying entities and relationships.
    max_nodes: Maximum number of nodes to include.

Returns:
    SubgraphResponse with all nodes and edges (up to limits).


<span id="user-content-kgserverquerygraphqlexamplespy"></span>

# kgserver/query/graphql_examples.py

Example GraphQL queries for the Knowledge Graph API.

These queries are displayed in the GraphiQL interface to help users get started.
When a bundle provides its own ``graphql_examples.yml``, that file replaces
the built-in examples at startup.

> 
Example GraphQL queries for the Knowledge Graph API.

These queries are displayed in the GraphiQL interface to help users get started.
When a bundle provides its own ``graphql_examples.yml``, that file replaces
the built-in examples at startup.


### `def load_examples(path: Path | None = None) -> None`

Load (or reload) example queries from a YAML file.

Args:
    path: Path to a ``graphql_examples.yml`` file.
          When *None*, the built-in default is used.

### `def get_examples() -> dict[str, str]`

Return the current example queries dict.

### `def get_default_query() -> str`

Return the current default query string.


<span id="user-content-kgserverquerygraphqlschemapy"></span>

# kgserver/query/graphql_schema.py

GraphQL schema for the Knowledge Graph API.

This schema uses proper Strawberry types for type safety and better GraphQL introspection.

> 
GraphQL schema for the Knowledge Graph API.

This schema uses proper Strawberry types for type safety and better GraphQL introspection.


## `class Entity`

Generic entity GraphQL type.

## `class Relationship`

Generic relationship GraphQL type.

## `class EntityPage`

Paginated result for entities.

## `class RelationshipPage`

Paginated result for relationships.

## `class EntityFilter`

Filter criteria for entity queries.

## `class RelationshipFilter`

Filter criteria for relationship queries.

## `class BundleInfo`

Bundle metadata for debugging and provenance.

### `def Query.entity(self, info: Info, id: str) -> Optional[Entity]`

Retrieve a single entity by its ID.

### `def Query.entities(self, info: Info, limit: int = 100, offset: int = 0, filter: Optional[EntityFilter] = None) -> EntityPage`

List entities with pagination and optional filtering.

### `def Query.relationship(self, info: Info, subject_id: strawberry.ID, predicate: str, object_id: strawberry.ID) -> Optional[Relationship]`

Retrieve a single relationship by its triple.

### `def Query.relationships(self, info: Info, limit: int = 100, offset: int = 0, filter: Optional[RelationshipFilter] = None) -> RelationshipPage`

Find relationships with pagination and optional filtering.

### `def Query.bundle(self, info: Info) -> Optional[BundleInfo]`

Get bundle metadata for debugging and provenance.


<span id="user-content-kgserverqueryroutersgraphapipy"></span>

# kgserver/query/routers/graph_api.py

Graph visualization API router for the Knowledge Graph Server.

Provides endpoints for extracting subgraphs suitable for D3.js force-directed
graph visualization.

> 
Graph visualization API router for the Knowledge Graph Server.

Provides endpoints for extracting subgraphs suitable for D3.js force-directed
graph visualization.


## `class SearchResult(BaseModel)`

A single entity search result.
**Fields:**

```python
entity_id: str
name: str
entity_type: str
```

## `class SearchResponse(BaseModel)`

Response from entity search.
**Fields:**

```python
results: list[SearchResult]
total: int
query: str
```

### `def _get_entity_types_from_domain_spec() -> dict[str, dict[str, str]]`

Load entity type metadata (color, label) from domain_spec.
Returns {entity_type: {color, label}}. Includes 'default' for unknown types.

## `class EntityTypeSpec(BaseModel)`

Color and label for an entity type.
**Fields:**

```python
color: str
label: str
```

## `class EntityTypesResponse(BaseModel)`

Entity type metadata for graph visualization.
**Fields:**

```python
entity_types: dict[str, EntityTypeSpec]
```

### `async def get_entity_types() -> EntityTypesResponse`

Get entity type colors and labels from domain_spec.

### `async def search_entities(q: str = Query(..., min_length=1, description='Search query (searches entity names, case-insensitive)'), limit: int = Query(default=20, ge=1, le=100, description='Maximum number of results to return'), entity_type: Optional[str] = Query(default=None, description="Filter by entity type (e.g., 'disease', 'drug', 'gene')"), storage: StorageInterface = Depends(get_storage)) -> SearchResponse`

Search for entities by name.

Returns entities whose names contain the query string (case-insensitive).
Results are returned with exact matches prioritized.

### `async def get_subgraph(center_id: Optional[str] = Query(default=None, description='Entity ID to center the subgraph on (required unless include_all=true)'), hops: int = Query(default=2, ge=1, le=MAX_HOPS, description=f'Number of hops from center entity (1-{MAX_HOPS})'), max_nodes: int = Query(default=DEFAULT_MAX_NODES, ge=1, le=MAX_NODES_LIMIT, description=f'Maximum number of nodes to return (1-{MAX_NODES_LIMIT})'), include_all: bool = Query(default=False, description='If true, return entire graph instead of subgraph around center_id'), storage: StorageInterface = Depends(get_storage)) -> SubgraphResponse`

Retrieve a subgraph for visualization.

If include_all is True, returns the entire graph (up to max_nodes).
Otherwise, performs BFS from center_id for the specified number of hops.

### `async def get_node_details(entity_id: str, storage: StorageInterface = Depends(get_storage)) -> GraphNode`

Get full details for a single node.

### `async def get_edge_details(subject_id: str = Query(..., description='Subject entity ID'), predicate: str = Query(..., description='Relationship predicate'), object_id: str = Query(..., description='Object entity ID'), storage: StorageInterface = Depends(get_storage)) -> GraphEdge`

Get full details for a single edge.

## `class MentionsResponse(BaseModel)`

Mentions (provenance) for an entity.
**Fields:**

```python
mentions: list[dict]
```

### `async def get_entity_mentions(entity_id: str, storage: StorageInterface = Depends(get_storage)) -> MentionsResponse`

Get mention provenance for an entity.

## `class EvidenceResponse(BaseModel)`

Evidence for a relationship.
**Fields:**

```python
evidence: list[dict]
```

### `async def get_edge_evidence(subject_id: str = Query(..., description='Subject entity ID'), predicate: str = Query(..., description='Relationship predicate'), object_id: str = Query(..., description='Object entity ID'), storage: StorageInterface = Depends(get_storage)) -> EvidenceResponse`

Get evidence for a relationship.


<span id="user-content-kgserverqueryroutersgraphiqlcustompy"></span>

# kgserver/query/routers/graphiql_custom.py

Custom GraphiQL interface with example queries.

Serves a custom GraphiQL HTML page with a dropdown menu of example queries.

> 
Custom GraphiQL interface with example queries.

Serves a custom GraphiQL HTML page with a dropdown menu of example queries.


### `def create_graphiql_html(graphql_endpoint: str = '/graphql') -> str`

Create custom GraphiQL HTML with example queries dropdown.

Attributes:

    graphql_endpoint: The GraphQL endpoint URL

Returns: HTML string for the GraphiQL interface

### `async def graphiql_interface()`

Serve custom GraphiQL interface with example queries dropdown.


<span id="user-content-kgserverqueryroutersrestapipy"></span>

# kgserver/query/routers/rest_api.py

REST API router for the Medical Literature Knowledge Graph.

> 
REST API router for the Medical Literature Knowledge Graph.


### `async def get_entity_by_id(entity_id: str, storage: StorageInterface = Depends(get_storage))`

Retrieve a single medical entity (e.g., Disease, Gene, Drug) by its
canonical identifier (e.g., UMLS ID, HGNC ID).

### `async def list_entities(limit: int = 100, offset: int = 0, storage: StorageInterface = Depends(get_storage))`

List all medical entities in the knowledge graph.

- **limit**: Maximum number of entities to return.
- **offset**: Number of entities to skip for pagination.

### `async def find_relationships(subject_id: Optional[str] = None, predicate: Optional[str] = None, object_id: Optional[str] = None, limit: int = 100, storage: StorageInterface = Depends(get_storage))`

Find relationships based on subject, predicate, or object.

- **subject_id**: Canonical ID of the subject entity.
- **predicate**: Type of the relationship (e.g., 'TREATS', 'CAUSES').
- **object_id**: Canonical ID of the object entity.
- **limit**: Maximum number of relationships to return.


<span id="user-content-kgserverqueryrouterssubgraphapipy"></span>

# kgserver/query/routers/subgraph_api.py

REST Subgraph API router.

Returns subgraphs as JSON (entities + relationships) with flexible entity
selection (ID, name glob) and filters (hops, min_confidence, predicates).
LLM-friendly alternative to GraphQL.

> 
REST Subgraph API router.

Returns subgraphs as JSON (entities + relationships) with flexible entity
selection (ID, name glob) and filters (hops, min_confidence, predicates).
LLM-friendly alternative to GraphQL.


## `class BfsSubgraphRequest(BaseModel)`

JSON body for BFS subgraph POST.
**Fields:**

```python
seeds: list[str]
max_hops: int
max_nodes: int
topology_filter: Optional[dict]
node_filter: Optional[dict]
edge_filter: Optional[dict]
```

## `class BfsSubgraphResponse(BaseModel)`

BFS subgraph response with nodes and edges (full or stub).
**Fields:**

```python
seeds: list[str]
max_hops: int
node_count: int
edge_count: int
truncated: bool
nodes: list[dict]
edges: list[dict]
```

## `class SubgraphQueryEcho(BaseModel)`

Echo of query params for LLM consumer.
**Fields:**

```python
seeds: list[str]
hops: int
filters: dict
truncated: bool
```

## `class SubgraphResponse(BaseModel)`

Subgraph as entities + relationships + query echo.
**Fields:**

```python
entities: list[Entity]
relationships: list[Relationship]
query: SubgraphQueryEcho
```

### `async def post_bfs_subgraph(body: BfsSubgraphRequest, storage: StorageInterface = Depends(get_storage)) -> BfsSubgraphResponse`

POST BFS subgraph with JSON body.

### `async def get_subgraph(entity: Optional[str] = Query(default=None, description='Entity ID(s) or glob pattern (comma-separated)'), name: Optional[str] = Query(default=None, description='Glob pattern on entity name (e.g. cushing*)'), hops: int = Query(default=2, ge=1, le=MAX_HOPS, description=f'Hops from seeds (1-{MAX_HOPS})'), min_confidence: Optional[float] = Query(default=None, ge=0.0, le=1.0, description='Filter relationships by confidence'), predicates: Optional[str] = Query(default=None, description='Comma-separated predicate filter (e.g. TREATS,CAUSES)'), max_nodes: int = Query(default=DEFAULT_MAX_NODES, ge=1, le=MAX_NODES_LIMIT, description=f'Max nodes (1-{MAX_NODES_LIMIT})'), storage: StorageInterface = Depends(get_storage)) -> SubgraphResponse`

Get subgraph from entity/name selection.


<span id="user-content-kgserverqueryserverpy"></span>

# kgserver/query/server.py

### `async def lifespan(app: FastAPI)`

Application lifespan manager.
Initializes storage on startup, loads bundle if configured, and closes on shutdown.

### `async def health_check()`

Health check endpoint to verify that the server is running.

### `async def _root_redirect()`

Serve docs index at /, redirect to marketing URL, or return JSON pointers.


<span id="user-content-kgserverquerystoragefactorypy"></span>

# kgserver/query/storage_factory.py

Storage factory for creating and managing storage backend instances.

> 
Storage factory for creating and managing storage backend instances.


### `def get_engine()`

Returns a singleton instance of the SQLAlchemy engine and db_url.

### `def get_storage() -> Generator[StorageInterface, None, None]`

FastAPI dependency that provides a storage instance with a request-scoped session.

### `def close_storage()`

Closes the engine connection.


<span id="user-content-kgserverquerysubgraphpy"></span>

# kgserver/query/subgraph.py

Subgraph extraction for REST API.

Resolves seed entities from entity/name params (with glob support) and runs
multi-seed BFS with optional filters (min_confidence, predicates).

> 
Subgraph extraction for REST API.

Resolves seed entities from entity/name params (with glob support) and runs
multi-seed BFS with optional filters (min_confidence, predicates).


### `def _glob_to_name_contains(pattern: str) -> str`

Convert glob pattern to substring for name_contains.

Deliberate simplification: `*` is ignored; the whole pattern minus `*`
becomes the substring. Multi-wildcard patterns (e.g. `cushing*disease`
→ `cushingdisease`) are mangled. Low risk for typical usage patterns.

### `def resolve_seeds(storage: StorageInterface, entity_param: Optional[str] = None, name_param: Optional[str] = None, limit: int = 100) -> list[str]`

Resolve entity/name params to a list of seed entity IDs.

- entity: comma-separated. Each token: exact id via get_entity, or glob via
  name_contains (strip * and use substring match).
- name: glob on name field, same as entity glob.
- Returns deduplicated list of entity_ids.

### `def extract_subgraph_rest(storage: StorageInterface, seed_ids: list[str], hops: int = 2, max_nodes: int = DEFAULT_MAX_NODES, min_confidence: Optional[float] = None, predicates: Optional[Sequence[str]] = None) -> tuple[list[Entity], list[Relationship], bool]`

Extract a merged subgraph from multiple seeds with optional filters.

Returns (entities, relationships, truncated).


<span id="user-content-kgserverstorageinitpy"></span>

# kgserver/storage/__init__.py

Storage layer for medical literature knowledge graph.

This package provides a clean abstraction for data persistence, separating
infrastructure concerns from domain logic.

Key Components:

- **interfaces**: Abstract base classes defining storage contracts
- **backends**: Concrete implementations (SQLite, PostgreSQL)
- **models**: SQLModel schemas for database persistence

Example:

    >>> from storage.interfaces import StorageInterface
    >>> from storage.backends.sqlite import SQLiteStorage
    >>>
    >>> # Create an in-memory SQLite storage
    >>> storage = SQLiteStorage(":memory:")
    >>>
    >>> # Add entities, papers, relationships
    >>> storage.entities.add_disease(disease)
    >>> storage.add_paper(paper)
    >>> storage.add_relationship(relationship)

For more information, see the README.md in this directory.

> 
Storage layer for medical literature knowledge graph.

This package provides a clean abstraction for data persistence, separating
infrastructure concerns from domain logic.

Key Components:

- **interfaces**: Abstract base classes defining storage contracts
- **backends**: Concrete implementations (SQLite, PostgreSQL)
- **models**: SQLModel schemas for database persistence

Example:

    >>> from storage.interfaces import StorageInterface
    >>> from storage.backends.sqlite import SQLiteStorage
    >>>
    >>> # Create an in-memory SQLite storage
    >>> storage = SQLiteStorage(":memory:")
    >>>
    >>> # Add entities, papers, relationships
    >>> storage.entities.add_disease(disease)
    >>> storage.add_paper(paper)
    >>> storage.add_relationship(relationship)

For more information, see the README.md in this directory.



<span id="user-content-kgserverstoragebackendsinitpy"></span>

# kgserver/storage/backends/__init__.py

Storage backend implementations.

This package contains concrete implementations of storage interfaces for
different database backends.

Available Backends:

- **sqlite**: SQLite implementation for testing and development
- **postgres**: PostgreSQL+pgvector implementation for production
- **sqlite_entity_collection**: SQLite-based entity collection

Example:

    >>> from storage.backends.sqlite import SQLiteStorage
    >>> storage = SQLiteStorage("my_database.db")

    >>> from storage.backends.postgres import PostgresStorage
    >>> storage = PostgresStorage("postgresql://user:pass@localhost/db")

For detailed backend comparison and usage, see backends/README.md.

> 
Storage backend implementations.

This package contains concrete implementations of storage interfaces for
different database backends.

Available Backends:

- **sqlite**: SQLite implementation for testing and development
- **postgres**: PostgreSQL+pgvector implementation for production
- **sqlite_entity_collection**: SQLite-based entity collection

Example:

    >>> from storage.backends.sqlite import SQLiteStorage
    >>> storage = SQLiteStorage("my_database.db")

    >>> from storage.backends.postgres import PostgresStorage
    >>> storage = PostgresStorage("postgresql://user:pass@localhost/db")

For detailed backend comparison and usage, see backends/README.md.



<span id="user-content-kgserverstoragebackendsidentitypy"></span>

# kgserver/storage/backends/identity.py

Postgres-backed implementation of the IdentityServer ABC.

This module provides ``PostgresIdentityServer``, the reference implementation
of ``kgschema.IdentityServer``.  It uses the existing SQLModel ``Session`` and
``Entity``/``Relationship`` models already in the kgserver stack.

Locking strategy (mirrors CONCURRENCY.md):
  - resolve:  ``INSERT ... ON CONFLICT DO NOTHING`` — Postgres serialises
              concurrent inserts on the same entity_id naturally.
  - promote:  ``SELECT ... WITH (UPDLOCK)`` equivalent via raw SQL
              ``SELECT ... FOR UPDATE`` on the entity row, then conditional
              update inside the same transaction.
  - merge:    Postgres advisory lock keyed on the sorted frozenset of entity
              IDs prevents two workers merging the same pair in opposite orders.
  - on_entity_added: called synchronously inside the same session as the
              triggering entity write; synonym detection is read-only and fires
              only after the row is durable.

Synonym detection uses the ``embedding`` JSON column on the ``Entity`` table
via in-process cosine similarity for now.  Once pgvector is activated on the
column (``ALTER TABLE entity ADD COLUMN embedding vector(N)``), the
``find_synonyms`` implementation can be swapped to a native vector query with
no interface change.

Authority-lookup caching uses Redis when a client is provided.  If Redis is
unavailable the server degrades gracefully to uncached lookups.  See
``AuthorityCache`` below.

> Postgres-backed implementation of the IdentityServer ABC.

This module provides ``PostgresIdentityServer``, the reference implementation
of ``kgschema.IdentityServer``.  It uses the existing SQLModel ``Session`` and
``Entity``/``Relationship`` models already in the kgserver stack.

Locking strategy (mirrors CONCURRENCY.md):
  - resolve:  ``INSERT ... ON CONFLICT DO NOTHING`` — Postgres serialises
              concurrent inserts on the same entity_id naturally.
  - promote:  ``SELECT ... WITH (UPDLOCK)`` equivalent via raw SQL
              ``SELECT ... FOR UPDATE`` on the entity row, then conditional
              update inside the same transaction.
  - merge:    Postgres advisory lock keyed on the sorted frozenset of entity
              IDs prevents two workers merging the same pair in opposite orders.
  - on_entity_added: called synchronously inside the same session as the
              triggering entity write; synonym detection is read-only and fires
              only after the row is durable.

Synonym detection uses the ``embedding`` JSON column on the ``Entity`` table
via in-process cosine similarity for now.  Once pgvector is activated on the
column (``ALTER TABLE entity ADD COLUMN embedding vector(N)``), the
``find_synonyms`` implementation can be swapped to a native vector query with
no interface change.

Authority-lookup caching uses Redis when a client is provided.  If Redis is
unavailable the server degrades gracefully to uncached lookups.  See
``AuthorityCache`` below.


## `class AuthorityCache`

Redis cache for authority-lookup results in ``resolve``.

Keys have the form ``resolve:{authority_version}:{entity_type}:{mention}``
so that a UMLS/DBPedia release can be invalidated by bumping
``authority_version`` without touching unrelated entries.

Values are JSON-serialised ``CanonicalId`` dicts (positive hit) or
``_NEGATIVE_SENTINEL`` (confirmed miss).

Designed for graceful degradation: every public method catches Redis
errors and logs at DEBUG level so a Redis outage never breaks ingestion.

Parameters
----------
redis_client:
    A ``redis.Redis`` (sync) client.  Pass ``None`` to disable caching.
authority_version:
    Opaque version string for the authority source, e.g. ``"umls-2026AA"``.
    Bump this to invalidate all cached lookups for that source.
positive_ttl:
    Seconds before a positive cache entry expires.
negative_ttl:
    Seconds before a negative cache entry expires.

### `def AuthorityCache.get(self, entity_type: str, mention: str) -> Optional[Any]`

Return cached ``CanonicalId``-like dict, ``None`` (miss), or
``_NEGATIVE_SENTINEL`` (confirmed negative).

Returns ``None`` on any Redis error so the caller falls through to the
live authority lookup.

### `def AuthorityCache.put_positive(self, entity_type: str, mention: str, canonical_id: object) -> None`

Cache a positive authority result.  ``canonical_id`` must be
JSON-serialisable (plain dict or object with ``__dict__``).

### `def AuthorityCache.put_negative(self, entity_type: str, mention: str) -> None`

Cache a confirmed negative (no canonical ID found).

### `def AuthorityCache.from_env(cls, authority_version: str = 'v1') -> 'AuthorityCache'`

Build an ``AuthorityCache`` from the ``REDIS_URL`` environment variable.

Returns a no-op cache (``redis_client=None``) if ``REDIS_URL`` is unset
or if the ``redis`` package is not installed, so the server starts
cleanly in environments without Redis.

### `def _cosine_similarity(a: list[float], b: list[float]) -> float`

Compute cosine similarity between two equal-length vectors.

### `def _advisory_lock_key(entity_ids: list[str]) -> int`

Derive a stable 64-bit advisory lock key from a sorted set of entity IDs.

Sorting ensures two workers locking the same pair always produce the same
key regardless of argument order, preventing deadlocks.

## `class PostgresIdentityServer(IdentityServer)`

Postgres-backed identity server using the existing kgserver SQLModel session.

Parameters
----------
session:
    An open SQLModel ``Session`` bound to the Postgres engine.  The caller
    is responsible for the session lifecycle (commit / rollback / close).
domain:
    The active ``DomainSchema`` instance.  Used for ``preferred_entity``
    (survivor selection) and ``get_promotion_policy`` (canonical ID
    assignment during promotion).
similarity_threshold:
    Minimum cosine similarity for two entities to be considered synonyms.
    Default 0.90 — intentionally conservative.
embedding_dim:
    Expected embedding dimension.  Used for validation only.
authority_cache:
    Optional ``AuthorityCache`` instance backed by Redis.  If omitted,
    authority lookups are performed on every ``resolve`` call with no
    caching.  Construct one via ``AuthorityCache.from_env()`` or pass a
    pre-built instance.

### `async def PostgresIdentityServer.resolve(self, mention: str, context: dict) -> str`

Resolve a mention to an entity ID, creating a provisional one if needed.

Uses ``INSERT ... ON CONFLICT DO NOTHING`` so concurrent workers
resolving the same mention produce the same entity without races.

Authority lookup (UMLS etc.) is attempted first via the domain's
promotion policy.  If the authority returns a canonical ID, the entity
is inserted as canonical.  Otherwise a provisional UUID is created.

The ``context`` dict may contain:
  - ``entity_type`` (str): domain entity type hint
  - ``document_id`` (str): source document for provenance
  - ``embedding`` (list[float]): pre-computed embedding vector

### `async def PostgresIdentityServer.promote(self, provisional_id: str) -> str`

Attempt to promote a provisional entity to canonical status.

Uses ``SELECT FOR UPDATE`` to lock the row, then checks and updates
inside the same implicit transaction.  Behaviour by status:
  - provisional: attempts canonical ID assignment; upgrades if found.
  - canonical: no-op; returns existing ID.
  - merged: logs warning; returns survivor ID.

### `async def PostgresIdentityServer.find_synonyms(self, entity_id: str) -> list[str]`

Return IDs of entities with cosine similarity above the threshold.

Currently uses in-process comparison of the ``embedding`` JSON column.
This is correct but O(n) — a pgvector index query can be substituted
here with no interface change once the column type is migrated.

### `async def PostgresIdentityServer.merge(self, entity_ids: list[str], survivor_id: str) -> str`

Merge entities into survivor, redirecting all relationship references.

Acquires a Postgres advisory lock keyed on the sorted set of IDs to
prevent concurrent merges of the same pair in opposite directions.

Status rules:
  - all provisional → survivor stays provisional
  - any canonical → survivor becomes canonical

### `async def PostgresIdentityServer.on_entity_added(self, entity_id: str, context: dict) -> None`

Trigger synonym detection and merge for a newly added entity.

Must be called inside the same session/transaction as the entity insert
so that the row is visible.  Synonym detection is read-only; ``merge``
acquires its own advisory lock.

### `def PostgresIdentityServer._update_relationship_refs(self, old_id: str, new_id: str) -> None`

Redirect all relationship subject/object references from old_id to new_id.

### `def PostgresIdentityServer._store_embedding(self, entity_id: str, embedding: list[float]) -> None`

Persist an embedding vector to the entity row (JSON column).

## `class _StubEntity(BaseEntity)`

Minimal BaseEntity subclass used to call domain policies from kgserver.

Domain ``preferred_entity`` and ``PromotionPolicy`` methods require a
``BaseEntity`` instance.  We don't know the domain-specific subclass here,
so we use a generic concrete subclass and bypass pydantic validation with
``model_construct`` to avoid requiring all optional fields.

### `def _entity_row_to_stub(row: Entity) -> _StubEntity`

Convert a kgserver ``Entity`` ORM row to a ``_StubEntity`` for domain calls.

### `def _make_stub_entity(mention: str, entity_type: str, document_id: str, embedding: Optional[list[float]]) -> _StubEntity`

Build a minimal stub for authority lookup (no DB row exists yet).

## `class _CachedCanonicalId`

Minimal CanonicalId-like object reconstructed from a Redis-cached dict.

### `def _dict_to_canonical_id(data: dict) -> _CachedCanonicalId`

Reconstruct a minimal CanonicalId-like object from a cached dict.


<span id="user-content-kgserverstoragebackendspostgrespy"></span>

# kgserver/storage/backends/postgres.py

PostgreSQL implementation of the storage interface.

> 
PostgreSQL implementation of the storage interface.


## `class PostgresStorage(StorageInterface)`

PostgreSQL implementation of the storage interface.

### `def PostgresStorage.load_bundle(self, bundle_manifest: BundleManifestV1, bundle_path: str) -> None`

Load a data bundle into the storage.
This is an idempotent operation. If the bundle is already loaded, it will do nothing.

### `def PostgresStorage.load_bundle_incremental(self, bundle_manifest: BundleManifestV1, bundle_path: str) -> None`

Load a bundle into the graph without truncating; upsert entities (accumulate
usage_count) and relationships, append provenance.

### `def PostgresStorage._load_entities_incremental(self, entities_file: str) -> None`

Upsert entities from JSONL; on conflict add usage_count to existing row.

### `def PostgresStorage._load_relationships_incremental(self, relationships_file: str) -> None`

Upsert relationships from JSONL by (subject_id, predicate, object_id).

### `def PostgresStorage.create_ingest_job(self, url: str) -> IngestJob`

Create a new ingest job and return it.

### `def PostgresStorage.get_ingest_job(self, job_id: str) -> Optional[IngestJob]`

Get an ingest job by id, or None if not found.

### `def PostgresStorage.update_ingest_job(self, job_id: str, **fields) -> Optional[IngestJob]`

Update an ingest job by id; return updated model or None if not found.

### `def PostgresStorage._debug_print_sample_entities(self, entities_file: str) -> None`

Print first few entities for debugging.

### `def PostgresStorage._load_entities(self, entities_file: str) -> None`

Load entities from JSONL file.

### `def PostgresStorage._capture_entity_sample(self, entity_data: dict, entity_id: str, status: str) -> dict`

Capture a sample entity for debugging.

### `def PostgresStorage._check_canonical_url_in_props(self, entity_data: dict, entity_id: str, status: str) -> tuple[bool, dict]`

Check if canonical_url exists in properties and return it along with props.

### `def PostgresStorage._print_entity_loading_summary(self, canonical_url_count: int, canonical_entities: int, total_entities: int, sample_canonical_entity: Optional[dict], sample_entity_raw: Optional[dict], sample_with_url: Optional[dict], sample_without_url: Optional[dict]) -> None`

Print summary of entity loading with debug information.

### `def PostgresStorage._print_entity_sample(self, title: str, sample: dict) -> None`

Print a sample entity structure.

### `def PostgresStorage._load_relationships(self, relationships_file: str) -> None`

Load relationships from JSONL file.

### `def PostgresStorage._normalize_entity(self, data: dict) -> dict`

Normalize entity data, flattening metadata fields.

### `def PostgresStorage._normalize_relationship(self, data: dict) -> dict`

Normalize relationship data, mapping field names.

### `def PostgresStorage.is_bundle_loaded(self, bundle_id: str) -> bool`

Check if a bundle with the given ID is already loaded.

### `def PostgresStorage.record_bundle(self, bundle_manifest: BundleManifestV1) -> None`

Record that a bundle has been loaded.

### `def PostgresStorage.get_entity(self, entity_id: str) -> Optional[Entity]`

Get an entity by its ID.

### `def PostgresStorage.get_entities(self, limit: int = 100, offset: int = 0, entity_type: Optional[str] = None, name: Optional[str] = None, name_contains: Optional[str] = None, source: Optional[str] = None, status: Optional[str] = None) -> Sequence[Entity]`

List entities with optional filtering.

name_contains is a substring match, deliberately not a regex or glob: a wildcard
search like "cushing*" is expressed as name_contains="cushing". Synonym matching is
not applied here — only the entity name is searched.

### `def PostgresStorage.count_entities(self, entity_type: Optional[str] = None, name: Optional[str] = None, name_contains: Optional[str] = None, source: Optional[str] = None, status: Optional[str] = None) -> int`

Count entities matching filter criteria.

### `def PostgresStorage.find_relationships(self, subject_id: Optional[str] = None, predicate: Optional[str] = None, object_id: Optional[str] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> Sequence[Relationship]`

Find relationships matching criteria.

### `def PostgresStorage.count_relationships(self, subject_id: Optional[str] = None, predicate: Optional[str] = None, object_id: Optional[str] = None) -> int`

Count relationships matching filter criteria.

### `def PostgresStorage.get_relationship(self, subject_id: str, predicate: str, object_id: str) -> Optional[Relationship]`

Get a relationship by its canonical triple (subject_id, predicate, object_id).

### `def PostgresStorage.get_relationships(self, limit: int = 100, offset: int = 0) -> Sequence[Relationship]`

List all relationships.

### `def PostgresStorage.get_bundle_info(self)`

Get bundle metadata (latest bundle).
Returns None if no bundle is loaded.

### `def PostgresStorage.get_mentions_for_entity(self, entity_id: str) -> Sequence[MentionRow]`

Return all mention rows for the given entity (bundle provenance).

### `def PostgresStorage.get_evidence_for_relationship(self, subject_id: str, predicate: str, object_id: str) -> Sequence[EvidenceRow]`

Return all evidence rows for the given relationship triple (bundle provenance).

### `def PostgresStorage.close(self) -> None`

Close connections and clean up resources.


<span id="user-content-kgserverstoragebackendssqlitepy"></span>

# kgserver/storage/backends/sqlite.py

SQLite implementation of the storage interface.

> 
SQLite implementation of the storage interface.


## `class SQLiteStorage(StorageInterface)`

SQLite implementation of the storage interface.

### `def SQLiteStorage.add_entity(self, entity: Entity) -> None`

Add a single entity to the storage.

### `def SQLiteStorage.add_relationship(self, relationship: Relationship) -> None`

Add a single relationship to the storage.

### `def SQLiteStorage.load_bundle(self, bundle_manifest: BundleManifestV1, bundle_path: str) -> None`

Load a data bundle into the storage.
This is an idempotent operation. If the bundle is already loaded, it will do nothing.

### `def SQLiteStorage.load_bundle_incremental(self, bundle_manifest: BundleManifestV1, bundle_path: str) -> None`

Load a bundle without truncating; upsert entities (accumulate usage_count)
and relationships, append provenance.

### `def SQLiteStorage.create_ingest_job(self, url: str) -> IngestJob`

Create a new ingest job and return it.

### `def SQLiteStorage.get_ingest_job(self, job_id: str) -> Optional[IngestJob]`

Get an ingest job by id, or None if not found.

### `def SQLiteStorage.update_ingest_job(self, job_id: str, **fields) -> Optional[IngestJob]`

Update an ingest job by id; return updated model or None if not found.

### `def SQLiteStorage._normalize_entity(self, data: dict) -> dict`

Normalize entity data, flattening metadata fields.

### `def SQLiteStorage._normalize_relationship(self, data: dict) -> dict`

Normalize relationship data, mapping field names.

### `def SQLiteStorage.is_bundle_loaded(self, bundle_id: str) -> bool`

Check if a bundle with the given ID is already loaded.

### `def SQLiteStorage.record_bundle(self, bundle_manifest: BundleManifestV1) -> None`

Record that a bundle has been loaded.

### `def SQLiteStorage.get_entity(self, entity_id: str) -> Optional[Entity]`

Get an entity by its ID.

### `def SQLiteStorage.get_entities(self, limit: int = 100, offset: int = 0, entity_type: Optional[str] = None, name: Optional[str] = None, name_contains: Optional[str] = None, source: Optional[str] = None, status: Optional[str] = None) -> Sequence[Entity]`

List entities with optional filtering.

### `def SQLiteStorage.count_entities(self, entity_type: Optional[str] = None, name: Optional[str] = None, name_contains: Optional[str] = None, source: Optional[str] = None, status: Optional[str] = None) -> int`

Count entities matching filter criteria.

### `def SQLiteStorage.find_relationships(self, subject_id: Optional[str] = None, predicate: Optional[str] = None, object_id: Optional[str] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> Sequence[Relationship]`

Find relationships matching criteria.

### `def SQLiteStorage.count_relationships(self, subject_id: Optional[str] = None, predicate: Optional[str] = None, object_id: Optional[str] = None) -> int`

Count relationships matching filter criteria.

### `def SQLiteStorage.get_relationship(self, subject_id: str, predicate: str, object_id: str) -> Optional[Relationship]`

Get a relationship by its canonical triple (subject_id, predicate, object_id).

### `def SQLiteStorage.get_relationships(self, limit: int = 100, offset: int = 0) -> Sequence[Relationship]`

List all relationships.

### `def SQLiteStorage.get_bundle_info(self)`

Get bundle metadata (latest bundle).
Returns None if no bundle is loaded.

### `def SQLiteStorage.get_mentions_for_entity(self, entity_id: str) -> Sequence[MentionRow]`

Return all mention rows for the given entity (bundle provenance).

### `def SQLiteStorage.get_evidence_for_relationship(self, subject_id: str, predicate: str, object_id: str) -> Sequence[EvidenceRow]`

Return all evidence rows for the given relationship triple (bundle provenance).

### `def SQLiteStorage.close(self) -> None`

Close connections and clean up resources.


<span id="user-content-kgserverstorageinterfacespy"></span>

# kgserver/storage/interfaces.py

Storage interfaces for the Knowledge Graph Server.

> 
Storage interfaces for the Knowledge Graph Server.


## `class StorageInterface(ABC)`

Abstract interface for a knowledge graph storage backend.

### `def StorageInterface.load_bundle(self, bundle_manifest: BundleManifestV1, bundle_path: str) -> None`

Load a data bundle into the storage.
This should be an idempotent operation.

### `def StorageInterface.load_bundle_incremental(self, bundle_manifest: BundleManifestV1, bundle_path: str) -> None`

Load a bundle into the graph without truncating; add/merge entities and
relationships (e.g. upsert entities and accumulate usage_count).

### `def StorageInterface.is_bundle_loaded(self, bundle_id: str) -> bool`

Check if a bundle with the given ID is already loaded.

### `def StorageInterface.record_bundle(self, bundle_manifest: BundleManifestV1) -> None`

Record that a bundle has been loaded.

### `def StorageInterface.get_entity(self, entity_id: str) -> Optional[Entity]`

Get an entity by its ID.

### `def StorageInterface.get_entities(self, limit: int = 100, offset: int = 0, entity_type: Optional[str] = None, name: Optional[str] = None, name_contains: Optional[str] = None, source: Optional[str] = None, status: Optional[str] = None) -> Sequence[Entity]`

List entities with optional filtering.

### `def StorageInterface.count_entities(self, entity_type: Optional[str] = None, name: Optional[str] = None, name_contains: Optional[str] = None, source: Optional[str] = None, status: Optional[str] = None) -> int`

Count entities matching filter criteria.

### `def StorageInterface.find_relationships(self, subject_id: Optional[str] = None, predicate: Optional[str] = None, object_id: Optional[str] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> Sequence[Relationship]`

Find relationships matching criteria.

### `def StorageInterface.count_relationships(self, subject_id: Optional[str] = None, predicate: Optional[str] = None, object_id: Optional[str] = None) -> int`

Count relationships matching filter criteria.

### `def StorageInterface.get_relationship(self, subject_id: str, predicate: str, object_id: str) -> Optional[Relationship]`

Get a relationship by its canonical triple (subject_id, predicate, object_id).

### `def StorageInterface.get_relationships(self, limit: int = 100, offset: int = 0) -> Sequence[Relationship]`

List all relationships.

### `def StorageInterface.get_bundle_info(self)`

Get bundle metadata (latest bundle).
Returns None if no bundle is loaded.

### `def StorageInterface.create_ingest_job(self, url: str) -> 'IngestJob'`

Create a new ingest job and return it.

### `def StorageInterface.get_ingest_job(self, job_id: str) -> Optional['IngestJob']`

Get an ingest job by id, or None if not found.

### `def StorageInterface.update_ingest_job(self, job_id: str, **fields) -> Optional['IngestJob']`

Update an ingest job by id; return updated model or None if not found.

### `def StorageInterface.get_mentions_for_entity(self, entity_id: str) -> Sequence['MentionRow']`

Return all mention rows for the given entity (bundle provenance).
Returns empty list if no mentions or provenance not loaded.

### `def StorageInterface.get_evidence_for_relationship(self, subject_id: str, predicate: str, object_id: str) -> Sequence['EvidenceRow']`

Return all evidence rows for the given relationship triple (bundle provenance).
Returns empty list if no evidence or provenance not loaded.

### `def StorageInterface.close(self) -> None`

Close connections and clean up resources.


<span id="user-content-kgserverstoragemodelsinitpy"></span>

# kgserver/storage/models/__init__.py

SQLModel schemas for database persistence.

> 
SQLModel schemas for database persistence.



<span id="user-content-kgserverstoragemodelsbundlepy"></span>

# kgserver/storage/models/bundle.py

## `class Bundle(SQLModel)`

Represents a loaded data bundle's metadata for idempotent tracking.


<span id="user-content-kgserverstoragemodelsbundleevidencepy"></span>

# kgserver/storage/models/bundle_evidence.py

Bundle provenance: one row per relationship evidence span (evidence.jsonl).

> 
Bundle provenance: one row per relationship evidence span (evidence.jsonl).


## `class BundleEvidence(SQLModel)`

One evidence span for a relationship from a loaded bundle (evidence.jsonl).


<span id="user-content-kgserverstoragemodelsentitypy"></span>

# kgserver/storage/models/entity.py

Generic Entity model for the Knowledge Graph Server.

> 
Generic Entity model for the Knowledge Graph Server.


## `class Entity(SQLModel)`

A generic entity in the knowledge graph.


<span id="user-content-kgserverstoragemodelsingestjobpy"></span>

# kgserver/storage/models/ingest_job.py

Ingest job model for tracking paper ingestion background jobs.

> 
Ingest job model for tracking paper ingestion background jobs.


## `class IngestJob(SQLModel)`

A single paper ingestion job (queued, running, complete, or failed).


<span id="user-content-kgserverstoragemodelsmentionpy"></span>

# kgserver/storage/models/mention.py

Bundle provenance: one row per entity mention (mentions.jsonl).

> 
Bundle provenance: one row per entity mention (mentions.jsonl).


## `class Mention(SQLModel)`

One entity mention from a loaded bundle (mentions.jsonl).


<span id="user-content-kgserverstoragemodelsrelationshippy"></span>

# kgserver/storage/models/relationship.py

Generic Relationship model for the Knowledge Graph Server.

> 
Generic Relationship model for the Knowledge Graph Server.


## `class Relationship(SQLModel)`

A generic relationship in the knowledge graph.


<span id="user-content-kgservertestsconftestpy"></span>

# kgserver/tests/conftest.py

Pytest configuration and shared fixtures for GraphQL tests.

> 
Pytest configuration and shared fixtures for GraphQL tests.


### `def in_memory_storage()`

Create an in-memory SQLite storage for testing.

### `def sample_entities()`

Create sample entities for testing.

### `def sample_relationships()`

Create sample relationships for testing.

### `def populated_storage(in_memory_storage, sample_entities, sample_relationships)`

Create storage with sample data.

### `def graphql_context(populated_storage)`

Create GraphQL context with populated storage.

### `def graphql_schema()`

Create GraphQL schema for testing.

### `def sample_bundle()`

Create a sample bundle for testing.

### `def storage_with_bundle(populated_storage, sample_bundle)`

Create storage with bundle metadata.

### `def bundle_dir_with_provenance(tmp_path)`

Create a bundle directory with entities, relationships, mentions, and evidence (for provenance API tests).

### `def storage_with_provenance_bundle(tmp_path, bundle_dir_with_provenance)`

SQLite storage with a bundle loaded that includes mentions and evidence.


<span id="user-content-kgserverteststestbfssubgraphpy"></span>

# kgserver/tests/test_bfs_subgraph.py

Unit tests for extract_subgraph_bfs in graph_traversal.py.

Uses populated_storage fixture (entities 1,2,3 and relationships 1->2, 1->3, 2->3).

> 
Unit tests for extract_subgraph_bfs in graph_traversal.py.

Uses populated_storage fixture (entities 1,2,3 and relationships 1->2, 1->3, 2->3).


### `def test_extract_subgraph_bfs_no_filters(populated_storage)`

With no filters, all nodes and edges are full.

### `def test_extract_subgraph_bfs_node_filter(populated_storage)`

node_filter.entity_types: matching nodes full, others stub.

### `def test_extract_subgraph_bfs_edge_filter(populated_storage)`

edge_filter.predicates: matching edges full, others stub.

### `def test_extract_subgraph_bfs_topology_min_confidence(populated_storage)`

topology_filter.min_confidence: edges below threshold skipped.

### `def test_extract_subgraph_bfs_multi_seed(populated_storage)`

Multi-seed returns union of neighborhoods.

### `def test_extract_subgraph_bfs_truncation(populated_storage)`

When max_nodes hit, truncated is True.


<span id="user-content-kgserverteststestbundleloaderpy"></span>

# kgserver/tests/test_bundle_loader.py

Tests for query/bundle_loader.py bundle loading logic.

Tests cover:
- _find_manifest() function
- Bundle loading from directory
- Bundle loading from ZIP
- Bundle-specific graphql_examples.yml override
- Error handling

> 
Tests for query/bundle_loader.py bundle loading logic.

Tests cover:
- _find_manifest() function
- Bundle loading from directory
- Bundle loading from ZIP
- Bundle-specific graphql_examples.yml override
- Error handling


### `def sample_manifest_data()`

Create sample manifest data.

### `def bundle_directory(sample_manifest_data, tmp_path)`

Create a temporary bundle directory with manifest and data files.

### `def bundle_zip(bundle_directory, tmp_path)`

Create a ZIP file from bundle directory.

### `def test_engine()`

Create a test SQLAlchemy engine.

## `class TestLoadFromDirectory`

Test _load_from_directory() function.

### `def TestLoadFromDirectory.test_load_from_directory_success(self, bundle_directory, test_engine)`

Test successfully loading bundle from directory.

### `def TestLoadFromDirectory.test_load_from_directory_no_manifest(self, tmp_path, test_engine)`

Test loading from directory without manifest.

## `class TestLoadFromZip`

Test _load_from_zip() function.

### `def TestLoadFromZip.test_load_from_zip_success(self, bundle_zip, test_engine)`

Test successfully loading bundle from ZIP.

### `def TestLoadFromZip.test_load_from_zip_no_manifest(self, tmp_path, test_engine)`

Test loading ZIP without manifest.

## `class TestBundleGraphqlExamples`

Test that a bundle's graphql_examples.yml replaces the default examples.

### `def TestBundleGraphqlExamples.test_bundle_examples_override(self, bundle_directory, test_engine)`

When a bundle contains graphql_examples.yml, those examples
should replace the built-in defaults after loading.

### `def TestBundleGraphqlExamples.test_no_bundle_examples_keeps_defaults(self, bundle_directory, test_engine)`

When a bundle does NOT contain graphql_examples.yml, the built-in
defaults should remain unchanged.


<span id="user-content-kgserverteststestgraphapipy"></span>

# kgserver/tests/test_graph_api.py

Tests for graph visualization API and traversal logic.

> 
Tests for graph visualization API and traversal logic.


### `def app()`

Create FastAPI app with Graph API and Subgraph API routers.

## `class TestGraphTraversal`

Tests for BFS graph traversal logic.

### `def TestGraphTraversal.test_extract_subgraph_single_hop(self, populated_storage)`

Test extracting a subgraph with 1 hop from center.

### `def TestGraphTraversal.test_extract_subgraph_two_hops(self, populated_storage)`

Test extracting a subgraph with 2 hops.

### `def TestGraphTraversal.test_extract_subgraph_nonexistent_center(self, populated_storage)`

Test extracting subgraph with non-existent center returns empty.

### `def TestGraphTraversal.test_extract_subgraph_respects_max_nodes(self, populated_storage)`

Test that max_nodes limit is respected.

### `def TestGraphTraversal.test_extract_full_graph(self, populated_storage)`

Test extracting the full graph.

### `def TestGraphTraversal.test_graph_node_structure(self, populated_storage)`

Test that GraphNode has correct structure.

### `def TestGraphTraversal.test_graph_edge_structure(self, populated_storage)`

Test that GraphEdge has correct structure.

## `class TestGraphAPI`

Tests for graph visualization REST API.

### `def TestGraphAPI.file_storage(self, tmp_path, sample_entities, sample_relationships)`

Create SQLite storage for thread-safe testing.

### `def TestGraphAPI.client(self, app, file_storage)`

Create test client with storage dependency override.

### `def TestGraphAPI.test_get_subgraph_with_center(self, client)`

Test GET /api/v1/graph/subgraph with center_id.

### `def TestGraphAPI.test_get_subgraph_include_all(self, client)`

Test GET /api/v1/graph/subgraph with include_all=true.

### `def TestGraphAPI.test_get_subgraph_missing_center_id(self, client)`

Test that missing center_id returns 400 when include_all is false.

### `def TestGraphAPI.test_get_node_details(self, client)`

Test GET /api/v1/graph/node/{entity_id}.

### `def TestGraphAPI.test_get_node_details_not_found(self, client)`

Test GET /api/v1/graph/node with non-existent entity.

### `def TestGraphAPI.test_get_edge_details(self, client)`

Test GET /api/v1/graph/edge.

### `def TestGraphAPI.test_get_edge_details_not_found(self, client)`

Test GET /api/v1/graph/edge with non-existent relationship.

### `def TestGraphAPI.test_hops_parameter_validation(self, client)`

Test that hops parameter is validated.

### `def TestGraphAPI.test_max_nodes_parameter(self, client)`

Test max_nodes parameter.

### `def TestGraphAPI.test_search_entities(self, client)`

Test GET /api/v1/graph/search.

### `def TestGraphAPI.test_search_entities_no_results(self, client)`

Test search with no matching entities.

### `def TestGraphAPI.test_search_entities_with_type_filter(self, client)`

Test search with entity_type filter.

### `def TestGraphAPI.test_get_entity_types(self, client)`

Test GET /api/v1/graph/entity-types returns colors and labels from domain_spec.

### `def TestGraphAPI.test_get_entity_mentions_empty_without_provenance(self, client)`

GET /entity/{id}/mentions returns 200 and empty list when no mentions stored.

### `def TestGraphAPI.test_get_edge_evidence_empty_without_provenance(self, client)`

GET /edge/evidence returns 200 and empty list when no evidence stored.

## `class TestSubgraphAPI`

Tests for REST Subgraph API.

### `def TestSubgraphAPI.file_storage(self, tmp_path, sample_entities, sample_relationships)`

Create SQLite storage for thread-safe testing.

### `def TestSubgraphAPI.client(self, app, file_storage)`

Create test client with storage dependency override.

### `def TestSubgraphAPI.test_subgraph_requires_entity_or_name(self, client)`

GET /api/v1/subgraph with no params returns 400.

### `def TestSubgraphAPI.test_subgraph_by_entity_id(self, client)`

entity=test:entity:1&hops=1 returns 200, entities non-empty, query.seeds correct.

### `def TestSubgraphAPI.test_subgraph_by_name_glob(self, client)`

name=Test&hops=1 resolves seeds from name match.

### `def TestSubgraphAPI.test_subgraph_empty_seeds(self, client)`

entity=nonexistent123 returns 200 with empty entities and relationships.

### `def TestSubgraphAPI.test_subgraph_query_echo(self, client)`

Response includes query with seeds, hops, filters, truncated.

## `class TestGraphAPIProvenance`

Graph API includes provenance/evidence in node and edge payloads when present.

### `def TestGraphAPIProvenance.storage_with_provenance_properties(self, tmp_path)`

Storage with entities and relationships that have provenance in properties.

### `def TestGraphAPIProvenance.client_provenance(self, app, storage_with_provenance_properties)`

Test client with storage that has provenance in entity/relationship properties.

### `def TestGraphAPIProvenance.test_node_details_include_provenance(self, client_provenance)`

GET /node/{id} includes first_seen_document, total_mentions, supporting_documents in properties.

### `def TestGraphAPIProvenance.test_edge_details_include_evidence_summary(self, client_provenance)`

GET /edge includes evidence_count, strongest_evidence_quote, evidence_confidence_avg in properties.

### `def TestGraphAPIProvenance.test_subgraph_node_properties_include_provenance(self, client_provenance)`

Subgraph nodes include provenance fields in properties when present.

### `def TestGraphAPIProvenance.test_subgraph_edge_properties_include_evidence(self, client_provenance)`

Subgraph edges include evidence summary in properties when present.

## `class TestGraphAPIMentionsEvidenceEndpoints`

GET /entity/{id}/mentions and GET /edge/evidence return stored provenance.

### `def TestGraphAPIMentionsEvidenceEndpoints.client_with_mentions_evidence(self, app, storage_with_provenance_bundle)`

Test client with storage that has mentions and evidence from a loaded bundle.

### `def TestGraphAPIMentionsEvidenceEndpoints.test_get_entity_mentions_returns_mentions(self, client_with_mentions_evidence)`

GET /entity/{id}/mentions returns mention rows when bundle had mentions.jsonl.

### `def TestGraphAPIMentionsEvidenceEndpoints.test_get_edge_evidence_returns_evidence(self, client_with_mentions_evidence)`

GET /edge/evidence returns evidence rows when bundle had evidence.jsonl.


<span id="user-content-kgserverteststestgraphvizthemepy"></span>

# kgserver/tests/test_graph_viz_theme.py

E2E tests for graph-viz (theme, controls, validation).

Requires: pip install -e ".[e2e]" && playwright install chromium

Run with: uv run pytest kgserver/tests/test_graph_viz_theme.py -v -p no:playwright
Run with: uv run pytest -m playwright -v -p no:playwright  # run playwright tests only

Use -p no:playwright to disable the pytest-playwright plugin and avoid teardown hang.

> 
E2E tests for graph-viz (theme, controls, validation).

Requires: pip install -e ".[e2e]" && playwright install chromium

Run with: uv run pytest kgserver/tests/test_graph_viz_theme.py -v -p no:playwright
Run with: uv run pytest -m playwright -v -p no:playwright  # run playwright tests only

Use -p no:playwright to disable the pytest-playwright plugin and avoid teardown hang.


### `def _find_free_port() -> int`

Find an available port for the test server.

### `def graph_viz_server()`

Start a minimal static file server for graph-viz, yield base URL, then stop.

### `def _close_browser_with_timeout(context, browser, timeout_sec: int = 15) -> None`

Close context and browser with a timeout to avoid indefinite hang on teardown.
If close hangs, exit the process (known pytest-playwright + server fixture issue).

### `def graph_viz_page(graph_viz_server)`

Page navigated to graph-viz. Uses sync_playwright directly to avoid pytest-playwright
session-scoped browser teardown hang when used with custom server fixtures.

## `class TestGraphVizTheme`

Theme select and persistence tests (syncs with Chainlit via vite-ui-theme).

### `def TestGraphVizTheme.test_theme_toggle_via_js_directly(self, graph_viz_page: Page)`

Verify theme logic works when applied manually (proves CSS/DOM work).

### `def TestGraphVizTheme.test_initial_theme_is_dark_when_saved(self, graph_viz_page: Page)`

When vite-ui-theme is 'dark', theme should be dark.

### `def TestGraphVizTheme.test_select_light_shows_light_theme(self, graph_viz_page: Page)`

Selecting Light from dropdown should switch to light theme.

### `def TestGraphVizTheme.test_select_dark_shows_dark_theme(self, graph_viz_page: Page)`

Selecting Dark from dropdown should switch to dark theme.

### `def TestGraphVizTheme.test_theme_persists_in_local_storage(self, graph_viz_page: Page)`

Selecting light theme should persist across reload.

### `def TestGraphVizTheme.test_dark_theme_persists_in_local_storage(self, graph_viz_page: Page)`

Dark theme selection should persist across reload.

## `class TestGraphVizControls`

Controls visibility, validation, and include-all checkbox tests.

### `def TestGraphVizControls.test_controls_are_visible(self, graph_viz_page: Page)`

Search, center ID, sliders, checkboxes, and buttons are present and visible.

### `def TestGraphVizControls.test_load_graph_without_center_id_shows_error(self, graph_viz_page: Page)`

With 'Show entire graph' unchecked and no center ID, Load Graph shows error.

### `def TestGraphVizControls.test_include_all_disables_center_id_and_search(self, graph_viz_page: Page)`

When 'Show entire graph' is checked, center ID and search are disabled.

### `def TestGraphVizControls.test_include_all_unchecked_enables_center_id_and_search(self, graph_viz_page: Page)`

When 'Show entire graph' is unchecked, center ID and search are enabled.


<span id="user-content-kgserverteststestgraphqlschemapy"></span>

# kgserver/tests/test_graphql_schema.py

Tests for GraphQL schema queries and types.

Tests cover:
- Entity queries (by ID, list with pagination and filtering)
- Relationship queries (by triple, list with pagination and filtering)
- Bundle introspection query
- Pagination types and metadata
- Filter functionality
- Max limit enforcement

> 
Tests for GraphQL schema queries and types.

Tests cover:
- Entity queries (by ID, list with pagination and filtering)
- Relationship queries (by triple, list with pagination and filtering)
- Bundle introspection query
- Pagination types and metadata
- Filter functionality
- Max limit enforcement


### `def execute_query(schema, query: str, context: dict)`

Helper to execute a GraphQL query.

## `class TestEntityQueries`

Test entity-related GraphQL queries.

### `def TestEntityQueries.test_entity_by_id(self, graphql_schema, graphql_context)`

Test retrieving a single entity by ID.

### `def TestEntityQueries.test_entity_not_found(self, graphql_schema, graphql_context)`

Test querying for non-existent entity.

### `def TestEntityQueries.test_entities_pagination(self, graphql_schema, graphql_context)`

Test entities query with pagination.

### `def TestEntityQueries.test_entities_pagination_offset(self, graphql_schema, graphql_context)`

Test entities query with offset.

### `def TestEntityQueries.test_entities_filter_by_type(self, graphql_schema, graphql_context)`

Test filtering entities by entity type.

### `def TestEntityQueries.test_entities_filter_by_name(self, graphql_schema, graphql_context)`

Test filtering entities by exact name.

### `def TestEntityQueries.test_entities_filter_name_contains(self, graphql_schema, graphql_context)`

Test filtering entities by name containing string.

### `def TestEntityQueries.test_entities_filter_by_source(self, graphql_schema, graphql_context)`

Test filtering entities by source.

### `def TestEntityQueries.test_entities_filter_by_status(self, graphql_schema, graphql_context)`

Test filtering entities by status.

### `def TestEntityQueries.test_entities_filter_combined(self, graphql_schema, graphql_context)`

Test combining multiple filters.

### `def TestEntityQueries.test_entities_max_limit_enforcement(self, graphql_schema, graphql_context, monkeypatch)`

Test that max limit is enforced.

## `class TestRelationshipQueries`

Test relationship-related GraphQL queries.

### `def TestRelationshipQueries.test_relationship_by_triple(self, graphql_schema, graphql_context)`

Test retrieving a single relationship by triple.

### `def TestRelationshipQueries.test_relationship_not_found(self, graphql_schema, graphql_context)`

Test querying for non-existent relationship.

### `def TestRelationshipQueries.test_relationships_pagination(self, graphql_schema, graphql_context)`

Test relationships query with pagination.

### `def TestRelationshipQueries.test_relationships_filter_by_subject(self, graphql_schema, graphql_context)`

Test filtering relationships by subject ID.

### `def TestRelationshipQueries.test_relationships_filter_by_object(self, graphql_schema, graphql_context)`

Test filtering relationships by object ID.

### `def TestRelationshipQueries.test_relationships_filter_by_predicate(self, graphql_schema, graphql_context)`

Test filtering relationships by predicate.

### `def TestRelationshipQueries.test_relationships_filter_combined(self, graphql_schema, graphql_context)`

Test combining multiple relationship filters.

### `def TestRelationshipQueries.test_relationships_max_limit_enforcement(self, graphql_schema, graphql_context, monkeypatch)`

Test that max limit is enforced for relationships.

## `class TestBundleQuery`

Test bundle introspection query.

### `def TestBundleQuery.test_bundle_query(self, graphql_schema, storage_with_bundle)`

Test bundle introspection query.

### `def TestBundleQuery.test_bundle_query_no_bundle(self, graphql_schema, graphql_context)`

Test bundle query when no bundle is loaded.

## `class TestFieldNaming`

Test that GraphQL field names use camelCase.

### `def TestFieldNaming.test_entity_camelcase_fields(self, graphql_schema, graphql_context)`

Test that entity fields are camelCase in GraphQL.

### `def TestFieldNaming.test_relationship_camelcase_fields(self, graphql_schema, graphql_context)`

Test that relationship fields are camelCase in GraphQL.

### `def TestFieldNaming.test_relationship_id_field(self, graphql_schema, graphql_context)`

Test that relationship id field is exposed and is a string (UUID).

## `class TestPaginationMetadata`

Test pagination metadata correctness.

### `def TestPaginationMetadata.test_entities_pagination_metadata(self, graphql_schema, graphql_context)`

Test that pagination metadata is correct.

### `def TestPaginationMetadata.test_relationships_pagination_metadata(self, graphql_schema, graphql_context)`

Test that relationship pagination metadata is correct.


<span id="user-content-kgserverteststestmcpgraphqltoolpy"></span>

# kgserver/tests/test_mcp_graphql_tool.py

Tests for the MCP graphql_query tool.

Verifies that the tool executes GraphQL against the same schema and returns
the standard { data, errors } shape. Uses patched storage so we don't depend
on bundle/env.

> 
Tests for the MCP graphql_query tool.

Verifies that the tool executes GraphQL against the same schema and returns
the standard { data, errors } shape. Uses patched storage so we don't depend
on bundle/env.


### `def mock_storage(populated_storage)`

Provide populated storage to the MCP tool via _get_storage.

### `def _call_tool(query: str, variables = None)`

Call the underlying MCP tool function (FastMCP wraps it in FunctionTool).

### `def test_graphql_query_returns_data_and_errors_shape(mock_storage)`

graphql_query returns dict with 'data' and 'errors' keys.

### `def test_graphql_query_entity(mock_storage)`

graphql_query can fetch an entity by id.

### `def test_graphql_query_entities_paginated(mock_storage)`

graphql_query can list entities with pagination.

### `def test_graphql_query_returns_errors_on_invalid_query(mock_storage)`

graphql_query returns errors in standard shape for invalid GraphQL.


<span id="user-content-kgserverteststestrestapipy"></span>

# kgserver/tests/test_rest_api.py

Tests for query/routers/rest_api.py REST API endpoints.

Tests cover:
- GET /api/v1/entities/{entity_id}
- GET /api/v1/entities
- GET /api/v1/relationships

> 
Tests for query/routers/rest_api.py REST API endpoints.

Tests cover:
- GET /api/v1/entities/{entity_id}
- GET /api/v1/entities
- GET /api/v1/relationships


### `def app()`

Create FastAPI app with REST API router.

### `def file_storage(tmp_path, sample_entities, sample_relationships)`

Create SQLite storage for thread-safe testing with FastAPI TestClient.

Uses tmp_path which automatically cleans up files after tests.
Uses check_same_thread=False for TestClient threading compatibility.

### `def client(app, file_storage)`

Create test client with storage dependency override.

## `class TestGetEntityById`

Test GET /api/v1/entities/{entity_id} endpoint.

### `def TestGetEntityById.test_get_existing_entity(self, client)`

Test retrieving an existing entity.

### `def TestGetEntityById.test_get_nonexistent_entity(self, client)`

Test retrieving a non-existent entity returns 404.

## `class TestListEntities`

Test GET /api/v1/entities endpoint.

### `def TestListEntities.test_list_entities_default(self, client)`

Test listing entities with default parameters.

### `def TestListEntities.test_list_entities_with_limit(self, client)`

Test listing entities with limit.

### `def TestListEntities.test_list_entities_with_offset(self, client)`

Test listing entities with offset.

### `def TestListEntities.test_list_entities_empty_result(self, client)`

Test listing entities with offset beyond available.

## `class TestFindRelationships`

Test GET /api/v1/relationships endpoint.

### `def TestFindRelationships.test_find_all_relationships(self, client)`

Test finding all relationships.

### `def TestFindRelationships.test_find_relationships_by_subject(self, client)`

Test filtering relationships by subject_id.

### `def TestFindRelationships.test_find_relationships_by_object(self, client)`

Test filtering relationships by object_id.

### `def TestFindRelationships.test_find_relationships_by_predicate(self, client)`

Test filtering relationships by predicate.

### `def TestFindRelationships.test_find_relationships_combined_filters(self, client)`

Test filtering relationships with multiple filters.

### `def TestFindRelationships.test_find_relationships_with_limit(self, client)`

Test limiting relationship results.

### `def TestFindRelationships.test_find_relationships_no_matches(self, client)`

Test finding relationships with no matches.


<span id="user-content-kgserverteststeststoragebackendspy"></span>

# kgserver/tests/test_storage_backends.py

Direct tests for storage backend implementations.

Tests cover:
- SQLiteStorage direct operations
- PostgresStorage direct operations (when available)
- Filter combinations
- Edge cases

> 
Direct tests for storage backend implementations.

Tests cover:
- SQLiteStorage direct operations
- PostgresStorage direct operations (when available)
- Filter combinations
- Edge cases


## `class TestSQLiteStorage`

Direct tests for SQLiteStorage.

### `def TestSQLiteStorage.test_get_entity_existing(self, in_memory_storage, sample_entities)`

Test retrieving an existing entity.

### `def TestSQLiteStorage.test_get_entity_nonexistent(self, in_memory_storage)`

Test retrieving non-existent entity.

### `def TestSQLiteStorage.test_get_entities_with_filters(self, in_memory_storage, sample_entities)`

Test get_entities with various filters.

### `def TestSQLiteStorage.test_count_entities(self, in_memory_storage, sample_entities)`

Test count_entities.

### `def TestSQLiteStorage.test_find_relationships_with_filters(self, in_memory_storage, sample_entities, sample_relationships)`

Test find_relationships with filters.

### `def TestSQLiteStorage.test_count_relationships(self, in_memory_storage, sample_entities, sample_relationships)`

Test count_relationships.

### `def TestSQLiteStorage.test_get_bundle_info(self, in_memory_storage)`

Test get_bundle_info.

### `def TestSQLiteStorage.test_get_bundle_info_none(self, in_memory_storage)`

Test get_bundle_info when no bundle exists.

### `def TestSQLiteStorage.test_is_bundle_loaded(self, in_memory_storage)`

Test is_bundle_loaded.

## `class TestPostgresStorage`

Direct tests for PostgresStorage using mocked database.

### `def TestPostgresStorage.postgres_storage(self)`

Create PostgresStorage using in-memory SQLite (mocks PostgreSQL).

### `def TestPostgresStorage.test_postgres_storage_basic(self, postgres_storage, sample_entities)`

Test basic PostgresStorage operations.

### `def TestPostgresStorage.test_postgres_storage_filters(self, postgres_storage, sample_entities)`

Test PostgresStorage with filters.


<span id="user-content-kgserverteststeststoragefactorypy"></span>

# kgserver/tests/test_storage_factory.py

Tests for query/storage_factory.py storage factory logic.

Tests cover:
- get_engine() with different DATABASE_URL values
- get_storage() for PostgreSQL vs SQLite
- Error handling for unsupported schemes

> 
Tests for query/storage_factory.py storage factory logic.

Tests cover:
- get_engine() with different DATABASE_URL values
- get_storage() for PostgreSQL vs SQLite
- Error handling for unsupported schemes


## `class TestGetEngine`

Test get_engine() function.

### `def TestGetEngine.test_get_engine_with_sqlite_url(self, monkeypatch)`

Test get_engine with SQLite URL.

### `def TestGetEngine.test_get_engine_with_postgres_url(self, monkeypatch)`

Test get_engine with PostgreSQL URL.

### `def TestGetEngine.test_get_engine_defaults_to_sqlite(self, monkeypatch)`

Test that get_engine defaults to SQLite when DATABASE_URL not set.

### `def TestGetEngine.test_get_engine_singleton(self, monkeypatch)`

Test that get_engine returns the same engine instance.

## `class TestGetStorage`

Test get_storage() function.

### `def TestGetStorage.test_get_storage_sqlite(self, monkeypatch)`

Test get_storage with SQLite.

### `def TestGetStorage.test_get_storage_postgres(self, monkeypatch)`

Test get_storage with PostgreSQL.

### `def TestGetStorage.test_get_storage_unsupported_scheme(self, monkeypatch)`

Test get_storage with unsupported database scheme.

### `def TestGetStorage.test_get_storage_sqlite_file_path(self, monkeypatch)`

Test get_storage with SQLite file path.

## `class TestCloseStorage`

Test close_storage() function.

### `def TestCloseStorage.test_close_storage(self, monkeypatch)`

Test that close_storage disposes the engine.

### `def TestCloseStorage.test_close_storage_when_none(self)`

Test that close_storage handles None engine gracefully.


<span id="user-content-kgserverteststeststorageprovenancepy"></span>

# kgserver/tests/test_storage_provenance.py

Tests for bundle provenance in storage: load_bundle with mentions/evidence,
get_mentions_for_entity, get_evidence_for_relationship, and entity/relationship
properties containing provenance summary.

> 
Tests for bundle provenance in storage: load_bundle with mentions/evidence,
get_mentions_for_entity, get_evidence_for_relationship, and entity/relationship
properties containing provenance summary.


### `def bundle_dir_with_provenance(tmp_path)`

Create a bundle directory with entities, relationships, mentions, and evidence.

### `def storage_with_provenance_bundle(tmp_path, bundle_dir_with_provenance)`

SQLite storage with a bundle loaded that includes mentions and evidence.

## `class TestLoadBundleProvenance`

Loading a bundle with mentions and evidence populates provenance tables.

### `def TestLoadBundleProvenance.test_load_bundle_stores_mentions(self, storage_with_provenance_bundle)`

After load_bundle, get_mentions_for_entity returns mention rows.

### `def TestLoadBundleProvenance.test_load_bundle_stores_evidence(self, storage_with_provenance_bundle)`

After load_bundle, get_evidence_for_relationship returns evidence rows.

### `def TestLoadBundleProvenance.test_get_mentions_for_entity_nonexistent_returns_empty(self, storage_with_provenance_bundle)`

get_mentions_for_entity for unknown entity returns empty list.

### `def TestLoadBundleProvenance.test_get_evidence_for_relationship_nonexistent_returns_empty(self, storage_with_provenance_bundle)`

get_evidence_for_relationship for unknown triple returns empty list.

## `class TestEntityRelationshipProvenanceProperties`

Entity and relationship provenance summary is stored in properties after load.

### `def TestEntityRelationshipProvenanceProperties.test_entity_properties_contain_provenance(self, storage_with_provenance_bundle)`

Entity loaded from bundle has first_seen_document, total_mentions, etc. in properties.

### `def TestEntityRelationshipProvenanceProperties.test_entity_without_provenance_has_empty_or_no_provenance_keys(self, storage_with_provenance_bundle)`

Entity e2 was written without provenance fields; properties may not have them.

### `def TestEntityRelationshipProvenanceProperties.test_relationship_properties_contain_evidence_summary(self, storage_with_provenance_bundle)`

Relationship loaded from bundle has evidence_count, strongest_evidence_quote in properties.

## `class TestLoadBundleWithoutProvenanceFiles`

Bundles without mentions/evidence files load successfully.

### `def TestLoadBundleWithoutProvenanceFiles.test_load_bundle_missing_mentions_file_does_not_raise(self, tmp_path)`

Manifest has mentions but file is missing; load_bundle does not raise.


<span id="user-content-kgserverteststestsubgraphapipy"></span>

# kgserver/tests/test_subgraph_api.py

Tests for query/routers/subgraph_api.py REST API endpoints.

Covers GET (legacy) and POST (BFS JSON body) subgraph endpoints.

> 
Tests for query/routers/subgraph_api.py REST API endpoints.

Covers GET (legacy) and POST (BFS JSON body) subgraph endpoints.


### `def app()`

Create FastAPI app with subgraph router.

### `def file_storage(tmp_path, sample_entities, sample_relationships)`

Create SQLite storage for testing.

### `def client(app, file_storage)`

Create test client with storage dependency override.

## `class TestPostBfsSubgraph`

Test POST /api/v1/subgraph (BFS JSON body).

### `def TestPostBfsSubgraph.test_post_valid_returns_200(self, client)`

POST with valid JSON body returns 200 and BfsSubgraphResponse shape.

### `def TestPostBfsSubgraph.test_post_unknown_seed_returns_400(self, client)`

POST with unknown seed ID returns 400 with error identifying unknown ID(s).

## `class TestGetSubgraph`

Test GET /api/v1/subgraph (legacy query params).

### `def TestGetSubgraph.test_get_returns_legacy_format(self, client)`

GET without JSON returns legacy format (entities, relationships, query).


<span id="user-content-medlitdomainserviceapppy"></span>

# medlit/domain_service/app.py

Medlit domain service — FastAPI application.

### `async def health() -> HealthResponse`

Return service health status.

### `async def get_schema() -> DomainSchemaResponse`

Return immutable domain schema contract.

### `async def resolve_authority_endpoint(request: ResolveAuthorityRequest) -> ResolveAuthorityResponse`

Resolve a mention to a canonical ID from medical authorities.

### `async def select_survivor_endpoint(request: SelectSurvivorRequest) -> SelectSurvivorResponse`

Select the preferred merge survivor.

### `async def synonym_criteria_config_endpoint() -> SynonymCriteriaConfig`

Return aggregate synonym criteria for startup-time caching.

### `async def synonym_criteria_endpoint(request: SynonymCriteriaRequest) -> SynonymCriteriaResponse`

Backward-compatible per-entity-type synonym threshold endpoint.

### `async def authorities_endpoint() -> AuthoritiesResponse`

Return authority metadata for diagnostics.

### `async def compute_confidence_endpoint(request: ComputeConfidenceRequest) -> ComputeConfidenceResponse`

Aggregate confidence over provenance records with medlit domain weights.


<span id="user-content-medlitdomainserviceauthoritypy"></span>

# medlit/domain_service/authority.py

Authority lookup wrapper for the medlit domain service.

Wraps ``medlit.pipeline.authority_lookup.CanonicalIdLookup`` with:
- The ``_AUTHORITY_TYPE_OVERRIDES`` remapping from ``MedLitPromotionPolicy``
  (hormone→drug, enzyme→protein, biomarker→disease) so the right ontology
  is used for each entity type.
- The LOOKUP_BLOCKLIST check (generic/type-like terms never sent to APIs).
- Persistent on-disk JSON cache via ``JsonFileCanonicalIdCache``.

The lookup instance is a module-level singleton so the cache is shared across
all requests in a single process.

> Authority lookup wrapper for the medlit domain service.

Wraps ``medlit.pipeline.authority_lookup.CanonicalIdLookup`` with:
- The ``_AUTHORITY_TYPE_OVERRIDES`` remapping from ``MedLitPromotionPolicy``
  (hormone→drug, enzyme→protein, biomarker→disease) so the right ontology
  is used for each entity type.
- The LOOKUP_BLOCKLIST check (generic/type-like terms never sent to APIs).
- Persistent on-disk JSON cache via ``JsonFileCanonicalIdCache``.

The lookup instance is a module-level singleton so the cache is shared across
all requests in a single process.


### `def authority_for_entity_type(entity_type: str) -> str`

Return the likely backing authority for an entity type.

### `def get_authorities_info() -> tuple[AuthorityInfo, ...]`

Return static authority metadata for diagnostics/observability endpoints.

### `def get_lookup() -> CanonicalIdLookup`

Return the module-level CanonicalIdLookup singleton, creating it on first call.

### `async def resolve_authority(mention: str, entity_type: str) -> Optional[CanonicalIdResponse]`

Look up a canonical ID for a mention from medical ontology authorities.

Parameters
----------
mention:
    Surface form of the entity mention (already normalised by the identity server).
entity_type:
    Domain entity type (e.g. 'disease', 'gene', 'drug').

Returns
-------
Optional[CanonicalIdResponse]
    Canonical ID if found, ``None`` if the mention has no authority match.


<span id="user-content-medlitdomainservicemodelspy"></span>

# medlit/domain_service/models.py

Pydantic schemas for the medlit domain service API.

## `class FrozenModel(BaseModel)`

Shared frozen base model.

## `class ResolveAuthorityRequest(FrozenModel)`

Request body for POST /resolve-authority.

## `class CanonicalIdResponse(FrozenModel)`

Canonical ID payload for authority resolution.

## `class ResolveAuthorityResponse(FrozenModel)`

Response body for POST /resolve-authority.

## `class CandidateEntity(FrozenModel)`

A candidate entity sent by the identity server for survivor selection.

## `class SelectSurvivorRequest(FrozenModel)`

Request body for POST /select-survivor.

## `class SelectSurvivorResponse(FrozenModel)`

Response body for POST /select-survivor.

## `class SynonymCriteriaRequest(FrozenModel)`

Backward-compatible request body for POST /synonym-criteria.

## `class SynonymCriteriaResponse(FrozenModel)`

Backward-compatible response body for POST /synonym-criteria.

## `class PredicateContract(FrozenModel)`

Predicate schema declaration.

## `class DomainSchemaResponse(FrozenModel)`

Response body for GET /schema.

## `class SynonymCriteriaConfig(FrozenModel)`

Response body for GET /synonym-criteria.

## `class AuthorityInfo(FrozenModel)`

Authority metadata entry.

## `class AuthoritiesResponse(FrozenModel)`

Response body for GET /authorities.

## `class ProvenanceRecord(FrozenModel)`

Provenance input record used for confidence aggregation.

## `class ComputeConfidenceRequest(FrozenModel)`

Request body for POST /compute-confidence.

## `class ComputeConfidenceResponse(FrozenModel)`

Response body for POST /compute-confidence.

## `class HealthResponse(FrozenModel)`

Response body for GET /health.


<span id="user-content-medlitdomainservicesurvivorpy"></span>

# medlit/domain_service/survivor.py

Survivor selection logic for the medlit domain service.

Implements the ``preferred_entity`` preference order from ``MedLitDomainSchema``:

1. Canonical status over provisional
2. Presence of any canonical_ids (non-empty ``entity_id`` that isn't a provisional UUID)
3. Higher ``usage_count`` (more evidence)
4. Lower (earlier) creation order — approximated here by entity_id lexical order
   since we don't have ``created_at`` in the HTTP contract.

The identity server sends a flat list of ``CandidateEntity`` dicts; this module
selects and returns the survivor's ``entity_id``.

> Survivor selection logic for the medlit domain service.

Implements the ``preferred_entity`` preference order from ``MedLitDomainSchema``:

1. Canonical status over provisional
2. Presence of any canonical_ids (non-empty ``entity_id`` that isn't a provisional UUID)
3. Higher ``usage_count`` (more evidence)
4. Lower (earlier) creation order — approximated here by entity_id lexical order
   since we don't have ``created_at`` in the HTTP contract.

The identity server sends a flat list of ``CandidateEntity`` dicts; this module
selects and returns the survivor's ``entity_id``.


### `def _has_authority_id(entity_id: str) -> bool`

Return True if entity_id looks like an authoritative ID (not a provisional UUID).

### `def select_survivor(candidates: list[CandidateEntity]) -> str`

Return the entity_id of the preferred merge survivor.

Preference order (highest priority first):
1. Canonical status ('canonical' > 'provisional' > 'merged')
2. Has an authoritative ID (entity_id does not start with 'prov:')
3. Higher usage_count
4. Lexically smallest entity_id (stable tie-breaker)

Parameters
----------
candidates:
    All entities being considered for merge (must be non-empty).

Returns
-------
str
    The ``entity_id`` of the selected survivor.


<span id="user-content-medlitdomainservicesynonymcriteriapy"></span>

# medlit/domain_service/synonym_criteria.py

Per-entity-type similarity thresholds for synonym detection.

The identity server calls POST /synonym-criteria before running cosine similarity
to get the right threshold for each entity type. Tighter thresholds for entity
types where false positives are costly (gene, drug); looser for types where
surface-form variation is high (anatomicalstructure, biologicalprocess).

> Per-entity-type similarity thresholds for synonym detection.

The identity server calls POST /synonym-criteria before running cosine similarity
to get the right threshold for each entity type. Tighter thresholds for entity
types where false positives are costly (gene, drug); looser for types where
surface-form variation is high (anatomicalstructure, biologicalprocess).


### `def get_threshold(entity_type: str) -> float`

Return the cosine similarity threshold for synonym detection for this entity type.


<span id="user-content-medlitdomainserviceteststestapppy"></span>

# medlit/domain_service/tests/test_app.py

Integration tests for the domain service FastAPI endpoints.

### `def test_resolve_authority_no_match()`

When authority lookup returns None, response has canonical_id=null.

### `def test_resolve_authority_match()`

When authority lookup returns a canonical ID, it is included in the response.


<span id="user-content-medlitdomainserviceteststestsurvivorpy"></span>

# medlit/domain_service/tests/test_survivor.py

Tests for survivor selection logic.


<span id="user-content-medlitdomainserviceteststestsynonymcriteriapy"></span>

# medlit/domain_service/tests/test_synonym_criteria.py

Tests for per-entity-type synonym thresholds.


<span id="user-content-medlitmedlitinitpy"></span>

# medlit/medlit/__init__.py

Medical literature domain extension for kgraph.

This package provides domain-specific types and pipeline components for
extracting knowledge from biomedical journal articles.

> Medical literature domain extension for kgraph.

This package provides domain-specific types and pipeline components for
extracting knowledge from biomedical journal articles.



<span id="user-content-medlitmedlitbundlemodelspy"></span>

# medlit/medlit/bundle_models.py

Pydantic models for the per-paper bundle JSON (Pass 1 output / Pass 2 input).

Matches the structure in INGESTION_REFACTOR.md. Entity type is stored with
Field(alias="class") because "class" is a Python reserved word; use
model_dump(by_alias=True) for JSON and populate_by_name=True for parsing.

> Pydantic models for the per-paper bundle JSON (Pass 1 output / Pass 2 input).

Matches the structure in INGESTION_REFACTOR.md. Entity type is stored with
Field(alias="class") because "class" is a Python reserved word; use
model_dump(by_alias=True) for JSON and populate_by_name=True for parsing.


## `class StudyDesignMetadata(BaseModel)`

Study design trust signal extracted from Methods/abstract (second LLM call per paper).
**Fields:**

```python
study_type: Optional[str]
sample_size: Optional[int]
multicenter: bool
held_out_validation: bool
```

## `class AuthorInfo(BaseModel)`

Author with optional affiliations.
**Fields:**

```python
name: str
affiliations: list[str]
affiliation_rors: list[str]
```

## `class PaperInfo(BaseModel)`

Paper metadata in the per-paper bundle.
**Fields:**

```python
doi: Optional[str]
pmcid: Optional[str]
title: str
authors: list[str]
author_details: Optional[list[AuthorInfo]]
document_id: str
journal: Optional[str]
year: Optional[int]
study_type: Optional[str]
eco_type: Optional[str]
study_design: Optional[StudyDesignMetadata]
cited_pmc_ids: list[str]
```

## `class ExtractedEntityRow(BaseModel)`

Minimal entity record in the bundle. JSON key "class" via alias.
**Fields:**

```python
id: str
entity_class: str
name: str
synonyms: list[str]
symbol: Optional[str]
brand_names: list[str]
source: Literal['extracted', 'umls', 'hgnc', 'rxnorm', 'loinc', 'uniprot']
canonical_id: Optional[str]
umls_id: Optional[str]
hgnc_id: Optional[str]
rxnorm_id: Optional[str]
loinc_code: Optional[str]
uniprot_id: Optional[str]
```

## `class EvidenceEntityRow(BaseModel)`

Evidence entity in the bundle. id format: {paper_id}:{section}:{paragraph_idx}:{method}.
**Fields:**

```python
id: str
entity_class: Literal['Evidence']
entity_id: Optional[str]
paper_id: str
text_span_id: Optional[str]
text: Optional[str]
confidence: float
extraction_method: str
study_type: Optional[str]
eco_type: Optional[str]
source: Literal['extracted']
```

## `class ProvenanceEntry(BaseModel)`

One provenance record for a relationship (section, sentence, optional citation markers).
**Fields:**

```python
section: Optional[str]
sentence: Optional[str]
citation_markers: list[str]
```

## `class RelationshipRow(BaseModel)`

One relationship in the bundle. evidence_ids optional for SAME_AS.
**Fields:**

```python
subject: str
predicate: str
object_id: str
evidence_ids: list[str]
provenance: list[ProvenanceEntry]
source_papers: list[str]
confidence: float
linguistic_trust: Optional[LinguisticTrust]
properties: dict[str, Any]
section: Optional[str]
asserted_by: str
resolution: Optional[Literal['merged', 'distinct']]
note: Optional[str]
```

## `class PerPaperBundle(BaseModel)`

Per-paper bundle: Pass 1 output and Pass 2 input. Immutable after Pass 1.
**Fields:**

```python
paper: PaperInfo
extraction_provenance: Optional[ExtractionProvenance]
entities: list[ExtractedEntityRow]
evidence_entities: list[EvidenceEntityRow]
relationships: list[RelationshipRow]
notes: list[str]
```

### `def PerPaperBundle.to_bundle_dict(self) -> dict`

Serialize for JSON with alias 'class' used for entity type.

### `def PerPaperBundle.from_bundle_dict(cls, data: dict) -> 'PerPaperBundle'`

Load from dict/JSON (accepts key 'class' for entity type).


<span id="user-content-medlitmedlitdocumentspy"></span>

# medlit/medlit/documents.py

Journal article document representation for medical literature domain.

## `class JournalArticle(BaseDocument)`

A journal article (research paper) as a source document for extraction.

Maps from med-lit-schema's Paper model to kgraph's BaseDocument.
Papers are NOT the same as doc_assets.jsonl (which is for documentation assets).
Papers are the source of information for building the knowledge graph, taken
from sources like PubMed, PLOS ONE, or medical journals if available.

Key mappings:
- Paper.paper_id → BaseDocument.document_id (prefer doi:, else pmid:, else stable hash)
- Paper.title → BaseDocument.title
- Paper.abstract + (optional full text) → BaseDocument.content
- PaperMetadata → BaseDocument.metadata (study type, sample size, journal, etc.)
- Paper.extraction_provenance → BaseDocument.metadata["extraction"]

### `def JournalArticle.get_document_type(self) -> str`

Return domain-specific document type.

### `def JournalArticle.get_sections(self) -> list[tuple[str, str]]`

Return document sections as (section_name, content) tuples.

For journal articles, we typically have:
- title: The paper title
- abstract: The abstract text
- body: The full text content (if available)

### `def JournalArticle.study_type(self) -> str | None`

Convenience property for accessing study_type from metadata.

### `def JournalArticle.sample_size(self) -> int | None`

Convenience property for accessing sample_size from metadata.

### `def JournalArticle.mesh_terms(self) -> list[str]`

Convenience property for accessing mesh_terms from metadata.


<span id="user-content-medlitmedlitdomainpy"></span>

# medlit/medlit/domain.py

Domain schema for medical literature knowledge graph.

## `class MedLitDomainSchema(DomainSchema)`

Domain schema for medical literature extraction.

Defines the vocabulary and validation rules for extracting medical knowledge
from journal articles. Uses canonical IDs (UMLS, HGNC, RxNorm, UniProt) for
entity identification and supports rich relationship metadata with evidence
and provenance tracking.

### `def MedLitDomainSchema.promotion_config(self) -> PromotionConfig`

Medical domain promotion configuration.

Lowered thresholds to match LLM extraction characteristics:
- min_usage_count=1: Entities appear once per paper
- min_confidence=0.4: LLM typically returns ~0.47 confidence
- require_embedding=False: Don't block promotion if embeddings not ready

### `def MedLitDomainSchema.normalize_mention(self, mention: str) -> str`

Lowercase, strip, and apply British→American spelling normalization.

### `def MedLitDomainSchema.validate_entity(self, entity: BaseEntity) -> list[ValidationIssue]`

Validate an entity against medical domain rules.

Rules:
- Entity type must be registered
- Canonical entities should have canonical IDs in entity_id or canonical_ids
- Provisional entities are allowed (they'll be promoted later)

### `async def MedLitDomainSchema.validate_relationship(self, relationship: BaseRelationship, entity_storage: EntityStorageInterface | None = None) -> bool`

Validate a relationship against medical domain rules.

Rules:
- Predicate must be registered
- Subject and object entity types must be compatible with predicate
- Confidence must be in valid range (enforced by BaseRelationship)

### `def MedLitDomainSchema.get_valid_predicates(self, subject_type: str, object_type: str) -> list[str]`

Return predicates valid between two entity types.

Uses the vocabulary validation function to enforce domain-specific
constraints on which relationships are semantically valid.

### `def MedLitDomainSchema.preferred_entity(self, candidates: list[BaseEntity]) -> BaseEntity`

Select the merge survivor from a set of synonym candidates.

Preference order (highest wins):
1. Canonical status over provisional
2. Presence of an authoritative ``canonical_ids`` entry (UMLS, HGNC, etc.)
3. Higher ``usage_count`` (more evidence)
4. Earlier ``created_at`` (stable, long-lived entity)

### `def MedLitDomainSchema.get_promotion_policy(self, lookup: CanonicalIdLookup | None = None) -> PromotionPolicy`

Return the promotion policy for medical literature domain.

Uses MedLitPromotionPolicy which assigns canonical IDs based on
authoritative medical ontologies (UMLS, HGNC, RxNorm, UniProt).

Args:
    lookup: Optional canonical ID lookup service. If None, a new
            instance will be created (without UMLS API key unless
            set in environment).


<span id="user-content-medlitmedlitdomainspecpy"></span>

# medlit/medlit/domain_spec.py

Domain spec for medical literature extraction.

Single source of truth for entity types, predicates, evidence, and mentions.
Consumers import from this module instead of loading YAML config.

> Domain spec for medical literature extraction.

Single source of truth for entity types, predicates, evidence, and mentions.
Consumers import from this module instead of loading YAML config.


## `class DiseaseEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class GeneEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class DrugEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class ProteinEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class HormoneEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class EnzymeEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class BiomarkerEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class SymptomEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class ProcedureEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class MutationEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class PathwayEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class BiologicalProcessEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class AnatomicalStructureEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class AuthorEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class InstitutionEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class PaperEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class HypothesisEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class EvidenceEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class LocationEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class EthnicityEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```


<span id="user-content-medlitmedlitentitiespy"></span>

# medlit/medlit/entities.py

Medical entity types for the knowledge graph.

## `class DiseaseEntity(BaseEntity)`

Represents medical conditions, disorders, and syndromes.

Uses UMLS as the primary identifier system with additional mappings to
MeSH and ICD-10 for interoperability with clinical systems.

Mapping from med-lit-schema:
- Disease.entity_id (UMLS ID) → BaseEntity.entity_id
- Disease.umls_id → BaseEntity.canonical_ids["umls"]
- Disease.mesh_id → BaseEntity.canonical_ids["mesh"]
- Disease.icd10_codes → BaseEntity.metadata["icd10_codes"]
- Disease.category → BaseEntity.metadata["category"]

## `class GeneEntity(BaseEntity)`

Represents genes and their genomic information.

Uses HGNC (HUGO Gene Nomenclature Committee) as the primary identifier
with additional mappings to NCBI Entrez Gene.

Mapping from med-lit-schema:
- Gene.entity_id (HGNC ID) → BaseEntity.entity_id
- Gene.hgnc_id → BaseEntity.canonical_ids["hgnc"]
- Gene.entrez_id → BaseEntity.canonical_ids["entrez"]
- Gene.symbol → BaseEntity.metadata["symbol"]
- Gene.chromosome → BaseEntity.metadata["chromosome"]

## `class DrugEntity(BaseEntity)`

Represents medications and therapeutic substances.

Uses RxNorm as the primary identifier for standardized medication naming.

Mapping from med-lit-schema:
- Drug.entity_id (RxNorm ID) → BaseEntity.entity_id
- Drug.rxnorm_id → BaseEntity.canonical_ids["rxnorm"]
- Drug.brand_names → BaseEntity.metadata["brand_names"]
- Drug.drug_class → BaseEntity.metadata["drug_class"]
- Drug.mechanism → BaseEntity.metadata["mechanism"]

## `class ProteinEntity(BaseEntity)`

Represents proteins and their biological functions.

Uses UniProt as the primary identifier for protein sequences and annotations.

Mapping from med-lit-schema:
- Protein.entity_id (UniProt ID) → BaseEntity.entity_id
- Protein.uniprot_id → BaseEntity.canonical_ids["uniprot"]
- Protein.gene_id → BaseEntity.metadata["gene_id"]
- Protein.function → BaseEntity.metadata["function"]
- Protein.pathways → BaseEntity.metadata["pathways"]

## `class SymptomEntity(BaseEntity)`

Represents clinical signs and symptoms.

## `class ProcedureEntity(BaseEntity)`

Represents medical tests, diagnostics, treatments.

## `class BiomarkerEntity(BaseEntity)`

Represents measurable indicators.

## `class PathwayEntity(BaseEntity)`

Represents biological pathways.

## `class LocationEntity(BaseEntity)`

Represents geographic locations relevant to epidemiological analysis.

Used for tracking disease prevalence by region, endemic diseases, and
geographic health disparities. Uses provisional IDs initially; canonical
IDs could come from GeoNames or ISO country codes in the future.

## `class EthnicityEntity(BaseEntity)`

Represents ethnic or population groups for epidemiological analysis.

Used for tracking genetic predispositions, health disparities, and
population-specific disease risk factors. Uses provisional IDs initially;
canonical IDs could come from standardized ethnicity codes in the future.


<span id="user-content-medlitmedlitpipelineinitpy"></span>

# medlit/medlit/pipeline/__init__.py

Pipeline components for medical literature extraction.


<span id="user-content-medlitmedlitpipelineauthoritylookuppy"></span>

# medlit/medlit/pipeline/authority_lookup.py

Canonical ID lookup from medical ontology authorities.

Provides lookup functionality for canonical IDs from various medical ontology
sources: UMLS, HGNC, RxNorm, and UniProt.

Features persistent caching to avoid repeated API calls across runs.

> Canonical ID lookup from medical ontology authorities.

Provides lookup functionality for canonical IDs from various medical ontology
sources: UMLS, HGNC, RxNorm, and UniProt.

Features persistent caching to avoid repeated API calls across runs.


### `def validate_umls_type(umls_id: str, assigned_type: str, _cache: dict[tuple[str, str], tuple[bool, str | None]] | None = None, _semantic_types_override: dict[str, list[str]] | None = None) -> tuple[bool, str | None]`

Return (ok, correct_type_if_known).

Looks up the UMLS semantic type(s) for the CUI and checks whether assigned_type
is compatible. Returns (False, expected_type) when assigned_type is incompatible
and the mapping is unambiguous; (True, None) when compatible; (False, None) when
ambiguous (multiple allowed types). Uses in-memory cache keyed by (umls_id,
assigned_type) so each CUI is looked up at most once per run when cache is passed.
For tests, pass _semantic_types_override mapping CUI -> list of semantic type names
to avoid live API calls.

## `class CanonicalIdLookup(CanonicalIdLookupInterface)`

Look up canonical IDs from various medical ontology authorities.

Supports lookup from:
- UMLS (diseases, symptoms, procedures)
- HGNC (genes)
- RxNorm (drugs)
- UniProt (proteins)

Features persistent caching to disk to avoid repeated API calls across runs.

### `def CanonicalIdLookup.__init__(self, umls_api_key: Optional[str] = None, cache_file: Optional[Path] = None, embedding_generator: Any = None, similarity_threshold: float = 0.5)`

Initialize the canonical ID lookup service.

Args:
    umls_api_key: Optional UMLS API key. If not provided, will try to
                 read from UMLS_API_KEY environment variable.
    cache_file: Optional path to cache file. If not provided, defaults
               to "canonical_id_cache.json" in current directory.
    embedding_generator: Optional; if set, used to rerank multiple candidates
                        (UMLS/MeSH) by cosine similarity to the search term.
                        Must have async generate(text: str) -> tuple[float, ...].
    similarity_threshold: Min cosine similarity when using embedding rerank (0-1).

### `def CanonicalIdLookup._save_cache(self, force: bool = False) -> None`

Save cache to disk.

Args:
    force: If True, save even if cache is not marked dirty (for emergency saves).

### `async def CanonicalIdLookup.lookup(self, term: str, entity_type: str) -> Optional[CanonicalId]`

Look up canonical ID for a medical term (interface method).

Args:
    term: The entity name/mention text
    entity_type: Type of entity (disease, gene, drug, protein, etc.)

Returns:
    CanonicalId if found, None otherwise

### `async def CanonicalIdLookup.lookup_canonical_id(self, term: str, entity_type: str) -> Optional[str]`

Look up canonical ID for a medical term.

Args:
    term: The entity name/mention text
    entity_type: Type of entity (disease, gene, drug, protein, etc.)

Returns:
    Canonical ID string if found, None otherwise

### `async def CanonicalIdLookup._rerank_by_similarity(self, term: str, candidates: list[tuple[str, str]]) -> Optional[str]`

Pick the candidate whose label is most similar to the search term.

candidates: list of (id, label) e.g. (cui, name) or (mesh_id, label).
Returns the id of the best candidate above threshold, or None.

### `async def CanonicalIdLookup._lookup_umls(self, term: str) -> Optional[str]`

Look up UMLS CUI for a disease/symptom term.

Tries exact match first, then words match for broader candidates.
When multiple results and embedding_generator is set, reranks by cosine similarity.
Falls back to MeSH if UMLS API key is not available.

### `def CanonicalIdLookup._normalize_mesh_search_terms(self, term: str) -> list[str]`

Generate normalized search terms for MeSH lookup.

MeSH uses formal terminology, so we normalize common informal terms.
Returns a list of search terms to try, in order of preference.

Args:
    term: Original search term

Returns:
    List of normalized search terms (original first, then normalized variants)

### `async def CanonicalIdLookup._lookup_mesh(self, term: str) -> Optional[str]`

Look up MeSH descriptor ID for a disease/symptom term.

MeSH (Medical Subject Headings) is freely accessible without API key.
Returns MeSH descriptor IDs like "MeSH:D001943" (breast neoplasms).

Strategy:
1. Try descriptor lookup with original term and normalized variants
2. Collect all results and score them together
3. Return the best match across all search terms

### `def CanonicalIdLookup._extract_mesh_id_from_results(self, data: list, search_terms: str | list[str]) -> Optional[str]`

Extract MeSH descriptor ID from API results, preferring best matches.

Scores results based on how well they match any of the provided search terms.
This allows normalized terms (e.g., "breast neoplasms") to score well even
when the original search was "breast cancer".

Scoring strategy:
1. Exact match (case-insensitive) gets highest score
2. Exact word match (all words present) gets high score
3. Prefer shorter labels (more general terms) over longer ones (complications)
4. Prefer matches where term is at the start of the label
5. Penalize matches that are much longer than the search term (likely complications)
6. Prefer matches to earlier search terms (original > normalized)

Args:
    data: List of result dictionaries from MeSH API
    search_terms: Single search term (str) or list of search terms tried
                 (original first, then normalized variants). If a single string
                 is provided, it's treated as the only search term.

### `async def CanonicalIdLookup._try_mesh_descriptor_lookup_all(self, term: str) -> list[dict]`

Try to find MeSH descriptors for a term, returning all results.

Args:
    term: Search term

Returns:
    List of result dictionaries from MeSH API

### `async def CanonicalIdLookup._lookup_hgnc(self, term: str) -> Optional[str]`

Look up HGNC ID for a gene.

Tries official symbol first, then falls back to alias search.
This handles cases like "p53" which is an alias for "TP53".

### `async def CanonicalIdLookup._lookup_rxnorm(self, term: str) -> Optional[str]`

Look up RxNorm ID for a drug.

### `async def CanonicalIdLookup._lookup_mesh_by_id(self, mesh_id: str) -> Optional[str]`

Look up MeSH ID by known ID (no search needed).

Args:
    mesh_id: MeSH descriptor ID (e.g., "D001943" or "MeSH:D001943")

Returns:
    Formatted MeSH ID (e.g., "MeSH:D001943")

### `async def CanonicalIdLookup._lookup_umls_by_id(self, umls_id: str) -> Optional[str]`

Look up UMLS CUI by known ID (no search needed).

Args:
    umls_id: UMLS CUI (e.g., "C0006142")

Returns:
    UMLS CUI string (e.g., "C0006142")

### `async def CanonicalIdLookup._lookup_hgnc_by_id(self, hgnc_id: str) -> Optional[str]`

Look up HGNC ID by known ID (no search needed).

Args:
    hgnc_id: HGNC ID (e.g., "1100" or "HGNC:1100")

Returns:
    Formatted HGNC ID (e.g., "HGNC:1100")

### `async def CanonicalIdLookup._lookup_rxnorm_by_id(self, rxnorm_id: str) -> Optional[str]`

Look up RxNorm ID by known ID (no search needed).

Args:
    rxnorm_id: RxNorm ID (e.g., "1187832" or "RxNorm:1187832")

Returns:
    Formatted RxNorm ID (e.g., "RxNorm:1187832")

### `async def CanonicalIdLookup._lookup_uniprot_by_id(self, uniprot_id: str) -> Optional[str]`

Look up UniProt ID by known ID (no search needed).

Args:
    uniprot_id: UniProt accession (e.g., "P38398" or "UniProt:P38398")

Returns:
    Formatted UniProt ID (e.g., "UniProt:P38398")

### `async def CanonicalIdLookup._lookup_uniprot(self, term: str) -> Optional[str]`

Look up UniProt ID for a protein.

### `async def CanonicalIdLookup._lookup_ror(self, term: str) -> Optional[str]`

Look up ROR ID for a research institution using the affiliation endpoint.

Uses the ROR affiliation-matching endpoint which is designed for messy
affiliation strings (e.g. department names, abbreviations, addresses).
Returns a ROR ID (format "ROR:{id}") for confident matches only.
No authentication required.

### `async def CanonicalIdLookup._lookup_orcid(self, term: str) -> Optional[str]`

Look up ORCID iD for a researcher by name using the ORCID public API.

Uses the ORCID public search API (no authentication required for search).
Returns an ORCID iD (format "ORCID:0000-0001-2345-6789") when a single
unambiguous result is found for the name.

### `def CanonicalIdLookup._dbpedia_label_matches(self, term: str, label: str) -> bool`

Check if a DBPedia label is a good match for the search term.

### `async def CanonicalIdLookup._lookup_dbpedia(self, term: str) -> Optional[str]`

Look up DBPedia URI as fallback for any entity type.

DBPedia is a general knowledge base extracted from Wikipedia.
Used as a fallback when specialized medical ontologies don't find a match.

Only accepts results where the label closely matches the search term
to avoid garbage matches like "HER2-enriched" → "Insect".

### `async def CanonicalIdLookup._extract_authoritative_id_from_dbpedia(self, dbpedia_id: str, entity_type: str, original_term: str) -> Optional[str]`

Extract authoritative ID from DBPedia resource properties.

After finding a DBPedia match, query the resource to find authoritative IDs
(MeSH, UMLS, HGNC, RxNorm, UniProt) that may be embedded in DBPedia properties.
If found, perform a follow-up lookup with the authoritative source.

Args:
    dbpedia_id: DBPedia ID in format "DBPedia:ResourceName"
    entity_type: Type of entity (disease, gene, drug, protein, etc.)
    original_term: Original search term for caching

Returns:
    Authoritative canonical ID if found, None otherwise

### `def CanonicalIdLookup._extract_authoritative_id_from_dbpedia_sync(self, client: 'httpx.Client', dbpedia_id: str, entity_type: str, original_term: str) -> Optional[str]`

Synchronous version of authoritative ID extraction from DBPedia.

Args:
    client: Synchronous HTTP client
    dbpedia_id: DBPedia ID in format "DBPedia:ResourceName"
    entity_type: Type of entity (disease, gene, drug, protein, etc.)
    original_term: Original search term for caching

Returns:
    Authoritative canonical ID if found, None otherwise

### `def CanonicalIdLookup._lookup_mesh_by_id_sync(self, mesh_id: str) -> Optional[str]`

Sync version: Look up MeSH ID by known ID.

### `def CanonicalIdLookup._lookup_umls_by_id_sync(self, umls_id: str) -> Optional[str]`

Sync version: Look up UMLS CUI by known ID.

### `def CanonicalIdLookup._lookup_hgnc_by_id_sync(self, hgnc_id: str) -> Optional[str]`

Sync version: Look up HGNC ID by known ID.

### `def CanonicalIdLookup.lookup_hgnc_by_cui_sync(self, cui: str) -> Optional[str]`

Resolve UMLS CUI to HGNC ID for gene concepts.

Uses UMLS REST API to fetch preferred atom name, then HGNC lookup.
Results are cached under key 'cui:{cui}' with entity_type 'gene'.
Required for cross-paper gene dedup when one paper has UMLS-only, another has HGNC.

Args:
    cui: UMLS CUI (e.g., C0079419 for TP53)

Returns:
    HGNC ID string (e.g., HGNC:11998) or None if resolution fails

### `def CanonicalIdLookup._lookup_rxnorm_by_id_sync(self, rxnorm_id: str) -> Optional[str]`

Sync version: Look up RxNorm ID by known ID.

### `def CanonicalIdLookup._lookup_uniprot_by_id_sync(self, uniprot_id: str) -> Optional[str]`

Sync version: Look up UniProt ID by known ID.

### `def CanonicalIdLookup.lookup_sync(self, term: str, entity_type: str) -> Optional[CanonicalId]`

Synchronous lookup (interface method).

Args:
    term: The entity name/mention text
    entity_type: Type of entity (disease, gene, drug, protein, etc.)

Returns:
    CanonicalId if found, None otherwise

### `def CanonicalIdLookup.lookup_canonical_id_sync(self, term: str, entity_type: str) -> Optional[str]`

Synchronous wrapper for use as Ollama tool.

This is needed because Ollama tool functions must be synchronous.
Uses the cache first, then makes synchronous HTTP calls if needed.

Args:
    term: The entity name/mention text
    entity_type: Type of entity (disease, gene, drug, protein, etc.)

Returns:
    Canonical ID string if found, None otherwise

### `def CanonicalIdLookup._lookup_umls_sync(self, client: 'httpx.Client', term: str) -> Optional[str]`

Synchronous UMLS lookup with MeSH fallback.

### `def CanonicalIdLookup._lookup_mesh_sync(self, client: 'httpx.Client', term: str) -> Optional[str]`

Synchronous MeSH lookup with term normalization.

Uses the same multi-term approach as async version.

### `def CanonicalIdLookup._lookup_hgnc_sync(self, client: 'httpx.Client', term: str) -> Optional[str]`

Synchronous HGNC lookup with alias fallback.

### `def CanonicalIdLookup._lookup_rxnorm_sync(self, client: 'httpx.Client', term: str) -> Optional[str]`

Synchronous RxNorm lookup.

### `def CanonicalIdLookup._lookup_uniprot_sync(self, client: 'httpx.Client', term: str) -> Optional[str]`

Synchronous UniProt lookup.

### `def CanonicalIdLookup._lookup_dbpedia_sync(self, client: 'httpx.Client', term: str) -> Optional[str]`

Synchronous DBPedia lookup as fallback with validation.

### `async def CanonicalIdLookup.close(self) -> None`

Close the HTTP client and save cache.

### `async def CanonicalIdLookup.__aenter__(self)`

Async context manager entry.

### `async def CanonicalIdLookup.__aexit__(self, exc_type, exc_val, exc_tb)`

Async context manager exit - saves cache and closes client.


<span id="user-content-medlitmedlitpipelinebundlebuilderpy"></span>

# medlit/medlit/pipeline/bundle_builder.py

build_bundle: Build kgbundle from merged and extracted.

Reads merged output (entities.json, relationships.json, id_map.json, synonym_cache.json)
and extracted paper_*.json bundles; writes a kgbundle directory loadable by kgserver.

> 
build_bundle: Build kgbundle from merged and extracted.

Reads merged output (entities.json, relationships.json, id_map.json, synonym_cache.json)
and extracted paper_*.json bundles; writes a kgbundle directory loadable by kgserver.


### `def load_merged_output(merged_dir: Path) -> tuple[list[dict], list[dict], dict, dict]`

Load merged ingest output and id_map.

Returns (entities, relationships, id_map, synonym_cache).
Raises FileNotFoundError if id_map.json is missing.

### `def load_extracted_bundles(bundles_dir: Path) -> list[tuple[str, PerPaperBundle]]`

Load all paper_*.json bundles from bundles_dir. Returns list of (paper_id, bundle).

### `def _section_from_evidence_id(evidence_id: str) -> str | None`

Extract section from evidence_id. Format: {paper_id}:{section}:{paragraph_idx}:{method}.

### `def _entity_usage_from_bundles(bundles: list[tuple[str, PerPaperBundle]], id_map: dict[str, dict[str, str]]) -> dict[str, dict[str, Any]]`

Compute usage_count, total_mentions, supporting_documents, first_seen_* per merge_key.

Semantics:
- usage_count: number of unique papers in supporting_documents (each paper counted once per entity).
- total_mentions: sum of evidence_ids across all relationships where the entity appears (subject or object).
Large gaps (e.g. usage_count=7, total_mentions=65) are expected when an entity appears many times within a few papers.

### `def _credit_entity(merge_key: str | None, evidence_id: str | None) -> None`

Credit merge_key with one mention from paper_id.

### `def _merged_entity_to_entity_row(ent: dict, usage: dict[str, Any], created_at: str) -> EntityRow`

Convert merged entity dict to EntityRow.

### `def _relationship_evidence_stats(merged_rels: list[dict], bundles: list[tuple[str, PerPaperBundle]], id_map: dict[str, dict[str, str]]) -> dict[tuple[str, str, str], dict[str, Any]]`

For each (sub, pred, obj) merge key, compute evidence_count, strongest_evidence_quote, evidence_confidence_avg.

### `def _merged_rel_to_relationship_row(rel: dict, stats: dict[tuple[str, str, str], dict[str, Any]], created_at: str) -> RelationshipRow`

Convert merged relationship dict to RelationshipRow.

### `def _build_evidence_rows(bundles: list[tuple[str, PerPaperBundle]], id_map: dict[str, dict[str, str]], merged_relationships: list[dict]) -> list[EvidenceRow]`

Build EvidenceRow list from bundles; relationship_key uses merge keys. Offsets stubbed (0, len(text)).

### `def _build_mention_rows(bundles: list[tuple[str, PerPaperBundle]], id_map: dict[str, dict[str, str]], created_at: str) -> list[MentionRow]`

Build MentionRow list from bundles; entity_id is merge_key. Offsets stubbed (0, len(text_span)).

### `def _fetch_pmc_titles(pmc_ids: list[str], batch_size: int = 200) -> dict[str, str]`

Batch-fetch paper titles from NCBI esummary for a list of PMC IDs.

Returns a dict mapping PMC ID (e.g. 'PMC12345') -> title string.
IDs not found in the response are omitted. Rate-limited to NCBI guidelines
(max 3 req/s without API key; we use 0.34s delay between batches).

### `def run_build_bundle(merged_dir: Path, bundles_dir: Path, output_dir: Path, pmc_xmls_dir: Path | None = None) -> dict[str, Any]`

Build kgbundle from merged ingest output and extracted bundles. Writes all bundle files.

If pmc_xmls_dir is provided, copies JATS-XML source files for each paper into
output_dir/sources/ (for get_paper_source diagnostic tool).


<span id="user-content-medlitmedlitpipelinecanonicalurlspy"></span>

# medlit/medlit/pipeline/canonical_urls.py

Utility functions for constructing canonical URLs from entity canonical IDs.

### `def build_canonical_url(canonical_id: str, entity_type: Optional[str] = None) -> Optional[str]`

Build a canonical URL for an entity based on its canonical ID.

Supports:
- DBPedia: https://dbpedia.org/page/{entity_name}
- MeSH: https://meshb.nlm.nih.gov/record/ui?ui={ID}
- UniProt: https://www.uniprot.org/uniprotkb/{ID}
- HGNC: https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/{ID}
- UMLS: https://uts.nlm.nih.gov/uts/umls/concept/{ID}
- RxNorm: https://www.nlm.nih.gov/research/umls/rxnorm/overview.html (no direct link, returns None)

Args:
    canonical_id: The canonical ID (e.g., "MeSH:D000570", "UniProt:P38398", "HGNC:1100")
    entity_type: Optional entity type hint (e.g., "disease", "gene", "protein")

Returns:
    URL string if a link can be constructed, None otherwise.

### `def build_canonical_urls_from_dict(canonical_ids: dict[str, str], entity_type: Optional[str] = None) -> dict[str, str]`

Build canonical URLs for all canonical IDs in a dictionary.

Args:
    canonical_ids: Dictionary mapping source names to canonical IDs
        (e.g., {"umls": "C0006142", "mesh": "MeSH:D000570"})
    entity_type: Optional entity type hint

Returns:
    Dictionary mapping source names to URLs (e.g., {"umls": "https://...", "mesh": "https://..."})


<span id="user-content-medlitmedlitpipelineconfigpy"></span>

# medlit/medlit/pipeline/config.py

Load medlit pipeline config from TOML (e.g. medlit.toml).

Config file is looked up in order:
  1. Path in MEDLIT_CONFIG env var (if set)
  2. medlit.toml in the medlit package directory
  3. medlit.toml in the current working directory

If no file is found, built-in defaults are used (window_size=1536, overlap=400).

> Load medlit pipeline config from TOML (e.g. medlit.toml).

Config file is looked up in order:
  1. Path in MEDLIT_CONFIG env var (if set)
  2. medlit.toml in the medlit package directory
  3. medlit.toml in the current working directory

If no file is found, built-in defaults are used (window_size=1536, overlap=400).


### `def _default_config_paths() -> list[Path]`

Return paths to check for medlit.toml (first existing wins).

### `def load_medlit_config() -> dict[str, Any]`

Load medlit config from TOML file.

Returns:
    Config dict with at least "chunker" key containing window_size and overlap.
    Uses DEFAULT_WINDOW_SIZE and DEFAULT_OVERLAP if no file or [chunker] section.


<span id="user-content-medlitmedlitpipelinededuppy"></span>

# medlit/medlit/pipeline/dedup.py

ingest: Deduplication and promotion over per-paper bundles.

Reads all PerPaperBundle JSONs from a directory, builds name/type index (with
synonym cache), resolves high-confidence SAME_AS, assigns canonical IDs,
updates relationship refs, accumulates triples, and saves the synonym cache.
Original bundle files are never modified; output is written to a separate
directory (overlay or merged graph).

> ingest: Deduplication and promotion over per-paper bundles.

Reads all PerPaperBundle JSONs from a directory, builds name/type index (with
synonym cache), resolves high-confidence SAME_AS, assigns canonical IDs,
updates relationship refs, accumulates triples, and saves the synonym cache.
Original bundle files are never modified; output is written to a separate
directory (overlay or merged graph).


### `def _normalize_for_dedup(name: str) -> str`

Lowercase, strip, and apply British→American spelling map for dedup lookups.

### `def _is_authoritative_id(s: str) -> bool`

Return True if s looks like an authoritative ontology ID, not a synthetic slug.

### `def _format_hgnc_id(val: str) -> str`

Ensure HGNC ID has HGNC: prefix if numeric.

### `def _preferred_authoritative_id(e: ExtractedEntityRow, lookup: Any) -> Optional[str]`

Return the best authoritative ID for merge key, preferring HGNC for genes.

For Gene: if both umls_id and hgnc_id present, prefer hgnc_id. If only umls_id,
resolve via UMLS→HGNC cross-lookup when lookup is available.
For other classes: first match in canonical_id, umls_id, hgnc_id, rxnorm_id, uniprot_id.

### `def _entity_class_to_lookup_type(entity_class: str, entity_class_to_lookup: dict[str, str]) -> Optional[str]`

Map bundle entity_class to CanonicalIdLookup entity_type (lowercase).

Deprecated: will be removed when the resolution loop in run_ingest is
replaced by PostgresIdentityServer.resolve() in Piece 3.

### `def _build_entity_class_to_lookup_type() -> dict[str, str]`

Derive bundle_class -> lookup_type from domain_spec.NORMALIZED_TO_BUNDLE.

### `def _build_entity_class_to_predicate_type() -> dict[str, str]`

Bundle_class -> entity type for predicate constraint checks (no authority overrides).

Authority overrides (e.g. Hormone->drug) are for UMLS/RxNorm lookup, not for
predicate semantics. CAUSES(hormone, symptom) requires Hormone->hormone.

### `def _should_swap_relationship(predicate: str, subject_class: str, object_class: str, predicate_constraints: dict[str, Any], entity_class_to_lookup: dict[str, str], entity_class_to_predicate_type: dict[str, str]) -> bool`

Return True if subject and object should be swapped to satisfy predicate constraints.

Fixes backwards relationships from Pass 1 LLM (e.g. disease treats drug -> drug treats disease).
Uses entity_class_to_predicate_type (no authority overrides) for semantic type checks.

### `def _canonical_id_slug() -> str`

Generate a short synthetic merge key for entities without authoritative ID.

### `def run_ingest(bundle_dir: Path, output_dir: Path, synonym_cache_path: Optional[Path] = None, canonical_id_cache_path: Optional[Path] = None, embedding_generator: Any = None, similarity_threshold: float = 0.88, cross_type_threshold: float = 0.9) -> dict[str, Any]`

Run ingest: dedup and promotion. Reads bundles from bundle_dir, writes to output_dir.

Original bundle files in bundle_dir are never modified.
Returns summary dict (entities_count, relationships_count, etc.).

Args:
    embedding_generator: Optional; if set, used for embedding-based dedup of provisional
        entities and cross-type candidate detection. Must have generate(text) -> vector.
    similarity_threshold: Min cosine similarity for same-class provisional merge (default 0.88).
    cross_type_threshold: Min similarity for cross-type candidate flagging (default 0.90).

### `def _run_ingest_impl(bundle_dir: Path, output_dir: Path, synonym_cache_path: Path, cache: dict, lookup: Any, embedding_generator: Any = None, similarity_threshold: float = 0.88, cross_type_threshold: float = 0.9, entity_class_to_lookup: Optional[dict[str, str]] = None, entity_class_to_predicate_type: Optional[dict[str, str]] = None) -> dict[str, Any]`

Inner ingest implementation (lookup created and saved by caller).

### `def _populate_name_index(cid: str, n: str, ec: str) -> None`

Add (normalized_name, entity_class) -> cid for name, synonyms, and spelling-normalized forms.

### `def _resolve_by_name(name: str) -> Optional[str]`

Fuzzy fallback: resolve a free-form name string to a canonical ID.

When the LLM writes a relationship subject/object as a plain name (e.g.
"FOLFIRINOX") rather than the entity ID it assigned ("mfolfirinox"),
local_to_canonical misses. This searches name_type_to_canonical across
all entity classes using exact, normalized, and synonym matches.

### `async def run_ingest_with_identity_server(bundle_dir: Path, output_dir: Path, identity_server: Any) -> dict[str, Any]`

Run ingest using PostgresIdentityServer for entity resolution.

Replaces the hand-built name/type index, synonym cache, authority lookup
chain, SAME_AS resolution, and embedding-based dedup with calls to the
identity server's ``resolve()`` and ``on_entity_added()`` methods.

The identity server handles:
- Spelling normalization (via DomainSchema.normalize_mention)
- Authority lookup with type overrides (via MedLitPromotionPolicy)
- Concurrent-safe entity creation (INSERT ... ON CONFLICT)
- Synonym detection and auto-merge (via on_entity_added)
- Provisional→canonical promotion

The pipeline retains responsibility for:
- Relationship predicate swap correction (_should_swap_relationship)
- Evidence and provenance accumulation per triple
- Output file writing (id_map.json, entities.json, relationships.json)

Args:
    bundle_dir: Directory containing paper_*.json bundle files (Pass 1 output).
    output_dir: Directory to write merged output files.
    identity_server: A PostgresIdentityServer (or any IdentityServer) instance.

Returns:
    Summary dict with entities_count, relationships_count, etc.


<span id="user-content-medlitmedlitpipelinementionspy"></span>

# medlit/medlit/pipeline/mentions.py

Entity mention extraction from journal articles.

Extracts entity mentions from Paper JSON format (from med-lit-schema).
Since the papers already have extracted entities, we convert those to EntityMention objects.
Can also use Ollama LLM for NER extraction from text.

> Entity mention extraction from journal articles.

Extracts entity mentions from Paper JSON format (from med-lit-schema).
Since the papers already have extracted entities, we convert those to EntityMention objects.
Can also use Ollama LLM for NER extraction from text.


### `def _normalize_mention_key(name: str, entity_type: str) -> tuple[str, str]`

Normalized key for deduping mentions: (alphanumeric lower name, type).

### `def _is_type_masquerading_as_name(name: str, entity_type: str) -> bool`

Return True if the name is just the entity type (or a type label), not a real entity name.

When the LLM (or pre-extracted data) puts the type in the 'entity'/'name' field,
we get e.g. name='disease', type='disease'. Reject these so we never create
entities whose name is the type.

## `class MedLitEntityExtractor(EntityExtractorInterface)`

Extract entity mentions from journal articles.

This extractor works with Paper JSON format from med-lit-schema, which
already contains extracted entities. We convert those to EntityMention objects.

Can also use Ollama LLM to extract entities directly from text if llm_client is provided.
Note: Canonical ID lookup is handled during the promotion phase, not during extraction.

### `def MedLitEntityExtractor.__init__(self, llm_client: LLMClientInterface | None = None, domain: DomainSchema | None = None)`

Initialize entity extractor.

Args:
    llm_client: Optional LLM client for extracting entities from text.
                If None, only uses pre-extracted entities from Paper JSON.
    domain: Domain schema for entity type validation (needed for normalization).

### `def MedLitEntityExtractor._normalize_entity_type(self, entity_type_raw: str) -> str | None`

Normalize LLM entity types to schema types.

Handles:
- Multi-type format (drug|protein) → takes first valid type
- Common mistakes (test → procedure)
- Invalid types → returns None (skip entity)

Args:
    entity_type_raw: Raw entity type string from LLM

Returns:
    Normalized type string if valid, None if invalid/non-medical

### `async def MedLitEntityExtractor.extract(self, document: BaseDocument) -> list[EntityMention]`

Extract entity mentions from a journal article (single chunk).

If the document metadata contains pre-extracted entities (from med-lit-schema),
we convert those to EntityMention objects. Otherwise, if llm_client is provided,
extracts entities from document text using LLM (one prompt per document/chunk).

When used behind BatchingEntityExtractor, this is called once per chunk;
the orchestrator handles streaming and deduplication across chunks.

Args:
    document: The journal article document (or a chunk document).

Returns:
    List of EntityMention objects for this document/chunk.


<span id="user-content-medlitmedlitpipelinenerextractorpy"></span>

# medlit/medlit/pipeline/ner_extractor.py

NER-based entity extraction for medical literature (PLAN3).

Uses a HuggingFace token-classification (NER) model for fast, local entity
extraction instead of an LLM. Default model: tner/roberta-base-bc5cdr (BC5CDR
chemical and disease entities). Install with: pip install -e ".[ner]"

Label mapping (BC5CDR-style): Chemical -> drug, Disease -> disease.
Gene/protein entities are not covered by this model; use a second model or
hybrid with LLM for full coverage.

> 
NER-based entity extraction for medical literature (PLAN3).

Uses a HuggingFace token-classification (NER) model for fast, local entity
extraction instead of an LLM. Default model: tner/roberta-base-bc5cdr (BC5CDR
chemical and disease entities). Install with: pip install -e ".[ner]"

Label mapping (BC5CDR-style): Chemical -> drug, Disease -> disease.
Gene/protein entities are not covered by this model; use a second model or
hybrid with LLM for full coverage.


### `def _normalize_entity_group(label: str) -> str`

Normalize pipeline entity_group to lowercase, strip B-/I- prefix if present.

### `def _get_document_text(document: BaseDocument) -> str`

Get text to run NER on: content or abstract.

### `def _run_ner_sync(pipeline: Any, text: str) -> list[dict]`

Run NER pipeline on text; returns list of dicts with start, end, entity_group, score.

### `def _chunk_text(text: str, chunk_size: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP) -> list[tuple[int, str]]`

Split text into overlapping chunks; returns [(start_offset, chunk_text), ...].

### `def _merge_and_dedupe(chunk_results: list[tuple[int, list[dict]]]) -> list[dict]`

Merge NER results from chunks: adjust offsets and dedupe by span (keep higher score).

## `class MedLitNEREntityExtractor(EntityExtractorInterface)`

Extract entity mentions using a local NER model (e.g. BC5CDR).

Much faster than LLM-based extraction. Supports disease and chemical (drug)
out of the box with the default model; other types can be added via
label mapping or a different model.

### `def MedLitNEREntityExtractor.__init__(self, model_name_or_path: str = 'tner/roberta-base-bc5cdr', domain: DomainSchema | None = None, device: str | None = None, max_length: int = 512, label_to_type: dict[str, str] | None = None, pipeline: Any = None)`

Initialize the NER extractor.

Args:
    model_name_or_path: HuggingFace model id or local path.
    domain: Medlit domain for type filtering; if None, all mapped types kept.
    device: "cuda", "cpu", or None for auto.
    max_length: Tokenizer max length.
    label_to_type: Override label -> medlit type map; default LABEL_TO_MEDLIT_TYPE.
    pipeline: Optional pre-built NER pipeline (for testing); if set, model is not loaded.

Raises:
    ImportError: If transformers/torch are not installed (install with pip install -e ".[ner]").

### `async def MedLitNEREntityExtractor.extract(self, document: BaseDocument) -> list[EntityMention]`

Extract entity mentions from document text using the NER model.


<span id="user-content-medlitmedlitpipelineparserpy"></span>

# medlit/medlit/pipeline/parser.py

Document parser for journal articles.

Converts raw paper input (PMC XML, JSON, etc.) into JournalArticle documents.

> Document parser for journal articles.

Converts raw paper input (PMC XML, JSON, etc.) into JournalArticle documents.


## `class JournalArticleParser(DocumentParserInterface)`

Parse raw journal article content into JournalArticle documents.

This parser handles various input formats (PMC XML, JSON from med-lit-schema,
etc.) and converts them to kgraph's JournalArticle format.

For now, this is a minimal implementation. A full implementation would:
1. Parse PMC XML (using existing med-lit-schema parser logic)
2. Parse JSON from med-lit-schema's Paper format
3. Extract metadata and map to JournalArticle fields

### `async def JournalArticleParser.parse(self, raw_content: bytes, content_type: str, source_uri: str | None = None) -> JournalArticle`

Parses raw document content into a structured `JournalArticle`.

This method acts as a dispatcher, routing the raw content to the
appropriate parsing logic based on its `content_type`. It supports
JSON (conforming to `med-lit-schema`) and PMC XML formats.

Args:
    raw_content: The raw byte content of the document.
    content_type: The MIME type of the document, used to select the
                  correct parser (e.g., "application/json", "application/xml").
    source_uri: An optional URI for the document's origin, which can be
                used to infer a document ID.

Returns:
    A `JournalArticle` instance populated with the parsed data.

Raises:
    ValueError: If the `content_type` is not supported or if the
                content is malformed and cannot be parsed.

### `def JournalArticleParser._parse_xml_to_dict(self, root: Any, source_uri: str | None) -> dict[str, Any]`

Converts a PMC XML structure into a dictionary.

This method traverses the XML element tree of a PubMed Central article
and extracts key information, mapping it to a dictionary that loosely
conforms to the `med-lit-schema` Paper format. This intermediate
dictionary is then passed to `_parse_from_dict`.

Args:
    root: The root element of the parsed XML tree.
    source_uri: An optional source URI, used as a fallback to derive
                the paper's ID from its filename.

Returns:
    A dictionary containing the extracted title, abstract, authors,
    and other metadata.

### `def JournalArticleParser._parse_from_dict(self, data: dict[str, Any], source_uri: str | None) -> JournalArticle`

Constructs a `JournalArticle` from a dictionary.

This method takes a dictionary (conforming to `med-lit-schema`'s Paper
format or the output of `_parse_xml_to_dict`) and maps its fields to
the `JournalArticle` document model.

Key mapping logic:
-   `document_id` is chosen in order of preference: DOI, then PMID,
    then the original `paper_id`.
-   `content` is created by combining the abstract and full text.
-   Pre-existing `entities` and `relationships` from the input data
    are moved into the `metadata` dictionary, so that downstream
    extractors in the kgraph pipeline can find them.
-   Other fields like authors, publication date, and journal are
    mapped directly.

Args:
    data: A dictionary containing the paper's data.
    source_uri: The original source URI of the document.

Returns:
    A fully populated `JournalArticle` object.

Raises:
    ValueError: If no valid identifier (paper_id, doi, or pmid)
                can be found in the input data.


<span id="user-content-medlitmedlitpipelinepmcchunkerpy"></span>

# medlit/medlit/pipeline/pmc_chunker.py

PMC-specific document chunker using iter_pmc_windows for memory-efficient streaming.

Produces DocumentChunks from raw PMC/JATS XML bytes without loading the full
document into memory. Implements DocumentChunkerInterface with chunk_from_raw()
for the streaming path and chunk(document) as a fallback for parsed documents.

> PMC-specific document chunker using iter_pmc_windows for memory-efficient streaming.

Produces DocumentChunks from raw PMC/JATS XML bytes without loading the full
document into memory. Implements DocumentChunkerInterface with chunk_from_raw()
for the streaming path and chunk(document) as a fallback for parsed documents.


### `def _content_type_is_xml(content_type: str) -> bool`

Return True if content_type is XML (strip parameters like ; charset=utf-8).

## `class PMCStreamingChunker(DocumentChunkerInterface)`

Chunker for PMC/JATS XML that uses iter_pmc_windows for memory-efficient chunking.

When chunk_from_raw() is used with XML content type, yields overlapping
windows from raw bytes without parsing the full document. For chunk(document)
(e.g. already-parsed document or non-XML), delegates to a windowed chunker
over document.content.

### `def PMCStreamingChunker.__init__(self, window_size: int = DEFAULT_WINDOW_SIZE, overlap: int = DEFAULT_OVERLAP, include_abstract_separately: bool = True, document_chunk_config: ChunkingConfig | None = None)`

Initialize the PMC streaming chunker.

Args:
    window_size: Target characters per window (used for chunk_from_raw).
    overlap: Overlap between consecutive windows.
    include_abstract_separately: If True, first window is abstract alone.
    document_chunk_config: Config for chunk(document) fallback. If None,
        uses window_size and overlap for the windowed chunker.

### `async def PMCStreamingChunker.chunk(self, document: BaseDocument) -> list[DocumentChunk]`

Split a parsed document into chunks (fallback when no raw bytes).

Delegates to WindowedDocumentChunker over document.content.

### `async def PMCStreamingChunker.chunk_from_raw(self, raw_content: bytes, content_type: str, document_id: str, source_uri: str | None = None) -> list[DocumentChunk]`

Chunk from raw PMC XML bytes without loading the full document.

Uses iter_pmc_windows for memory-efficient streaming. If content_type
is not XML, returns a single chunk with decoded text (for non-PMC use).

### `def document_id_from_source_uri(source_uri: str | None) -> str`

Derive a document ID from source_uri (e.g. file stem). Used when parsing is deferred.


<span id="user-content-medlitmedlitpipelinepmcstreamingpy"></span>

# medlit/medlit/pipeline/pmc_streaming.py

Streaming PMC XML chunker for full-paper extraction.

Yields overlapping text windows from a PMC/JATS XML document without loading
the entire body into a single string. Uses iterparse so the parser does not
hold the full tree in memory; sections are yielded and then cleared.

Use for:
- Entity extraction: run NER on each window, then merge/dedupe mentions.
- Relationship extraction: run relationship extraction on each window with
  the full entity list, then merge relationships.

> Streaming PMC XML chunker for full-paper extraction.

Yields overlapping text windows from a PMC/JATS XML document without loading
the entire body into a single string. Uses iterparse so the parser does not
hold the full tree in memory; sections are yielded and then cleared.

Use for:
- Entity extraction: run NER on each window, then merge/dedupe mentions.
- Relationship extraction: run relationship extraction on each window with
  the full entity list, then merge relationships.


### `def _local_tag(tag: str) -> str`

Strip XML namespace from tag for comparison.

### `def iter_pmc_sections(raw_content: bytes) -> Iterator[tuple[str, str]]`

Yield (section_id, text) for abstract and each body section.

Uses iterparse so we do not build a full DOM for the body. After
yielding each element's text we clear it to free memory. Yields:
- ("abstract", abstract_text) first if present
- ("sec_<id>", section_text) for each <sec> (full text of that section,
  including nested secs and paragraphs)

Namespaces in JATS are stripped so we match "abstract", "body", "sec".

### `def iter_overlapping_windows(sections: Iterator[tuple[str, str]], window_size: int = DEFAULT_WINDOW_SIZE, overlap: int = DEFAULT_OVERLAP) -> Iterator[tuple[int, str]]`

Turn a stream of (section_id, text) into overlapping windows.

Concatenates section texts. When accumulated length reaches window_size,
yields (window_index, text). Then slides by (window_size - overlap) so
consecutive windows overlap by `overlap` characters. This helps the LLM
see context across boundaries and avoids splitting entities.

If include_abstract_separately is True, the first yielded window is
always the abstract alone (if any section has section_id == "abstract").
Subsequent windows are from body content only. Only one window-sized
buffer is kept in memory.

Args:
    sections: Iterator of (section_id, text).
    window_size: Target size of each window in characters.
    overlap: Number of characters to overlap between consecutive windows.
    include_abstract_separately: If True, yield abstract as window 0.

Yields:
    (window_index, text) for each window.

### `def iter_pmc_windows(raw_content: bytes, window_size: int = DEFAULT_WINDOW_SIZE, overlap: int = DEFAULT_OVERLAP, include_abstract_separately: bool = True) -> Iterator[tuple[int, str]]`

Yield overlapping text windows from PMC XML for full-paper extraction.

Convenience generator: iter_pmc_sections(raw_content) -> iter_overlapping_windows(...).
Use when you have raw PMC/XML bytes and want a sequence of prompts (e.g. for
entity or relationship extraction) without loading the whole paper into one string.

Args:
    raw_content: Raw bytes of the PMC/JATS XML document.
    window_size: Target characters per window.
    overlap: Overlap between consecutive windows.
    include_abstract_separately: If True, first window is the abstract alone.

Yields:
    (window_index, text) for each window.


<span id="user-content-medlitmedlitpipelineprovenanceexpansionpy"></span>

# medlit/medlit/pipeline/provenance_expansion.py

Provenance expansion: derive Author, Institution, Paper entities and relationships from metadata.

### `def normalize_author_id(name: str, paper_id: str) -> str`

Return Author:{normalized} where normalized = last word + first initial, lowercased, alphanumeric only.

### `def normalize_institution_id(affiliation: str) -> str`

Return Institution:{normalized} where normalized = first 50 chars, lowercased, non-alphanumeric -> underscore.

### `def expand_provenance(bundle: PerPaperBundle) -> tuple[list[ExtractedEntityRow], list[RelationshipRow]]`

Derive Author, Institution, Paper entities and AUTHORED, AFFILIATED_WITH, DESCRIBED from metadata.

DESCRIBED is limited to the top 2 domain entities by relationship count (central to the paper).
COAUTHORED_WITH is omitted; derive via AUTHORED hops (Author -> Paper <- Author).


<span id="user-content-medlitmedlitpipelinerelationshipspy"></span>

# medlit/medlit/pipeline/relationships.py

Relationship extraction from journal articles.

Extracts relationships from Paper JSON format (from med-lit-schema).
Since the papers already have extracted relationships, we convert those to BaseRelationship objects.
Can also use Ollama LLM for relationship extraction from text.

> Relationship extraction from journal articles.

Extracts relationships from Paper JSON format (from med-lit-schema).
Since the papers already have extracted relationships, we convert those to BaseRelationship objects.
Can also use Ollama LLM for relationship extraction from text.


### `def _deduplicate_relationships_by_predicate_specificity(relationships: list[BaseRelationship]) -> list[BaseRelationship]`

For each (subject_id, object_id), keep only the relationship with highest predicate specificity.

### `def _normalize_evidence_for_match(text: str) -> str`

Normalize evidence text for substring matching: lowercase, strip, collapse whitespace.

### `def _evidence_has_disease_context(evidence: str) -> bool`

Return True if evidence text suggests disease/marker context (IHC, tumor, etc.).

### `def _evidence_contains_both_entities(evidence: str, subject_name: str, object_name: str, subject_entity: BaseEntity | None, object_entity: BaseEntity | None) -> tuple[bool, str | None, dict[str, Any]]`

Check that both subject and object (or synonyms) appear in the evidence text.

Returns:
    (ok, drop_reason, detail): ok is True only if both entities appear;
    drop_reason is set when ok is False; detail has subject_in_evidence, object_in_evidence.

### `async def _evidence_contains_both_entities_semantic(evidence: str, subject_entity: BaseEntity, object_entity: BaseEntity, embedding_generator: Any, threshold: float, evidence_cache: dict[str, tuple[float, ...]], entity_name_cache: dict[str, tuple[float, ...]]) -> tuple[bool, str | None, dict[str, Any]]`

Check that evidence semantically contains both entities via embedding similarity.

Uses evidence_cache and entity_name_cache to avoid duplicate embedding API calls
within a document. Returns same shape as _evidence_contains_both_entities.

## `class MedLitRelationshipExtractor(RelationshipExtractorInterface)`

Extract relationships from journal articles.

This extractor works with Paper JSON format from med-lit-schema, which
already contains extracted relationships. We convert those to BaseRelationship objects.

Can also use Ollama LLM to extract relationships directly from text if llm_client is provided.

### `def MedLitRelationshipExtractor.__init__(self, llm_client: Optional[LLMClientInterface] = None, domain: Optional['MedLitDomainSchema'] = None, trace_dir: Optional[Path] = None, embedding_generator: Any = None, evidence_similarity_threshold: float = 0.5)`

Initialize relationship extractor.

Args:
    llm_client: Optional LLM client for extracting relationships from text.
                If None, only uses pre-extracted relationships from Paper JSON.
    domain: Optional domain schema for type validation and predicate constraints.
            If provided, will attempt to swap subject/object on type mismatches.
    trace_dir: Optional directory for writing trace files. If None, uses default.
    embedding_generator: Optional embedding generator for semantic evidence validation.
                        When set, failed string evidence check is retried with cosine similarity.
    evidence_similarity_threshold: Minimum cosine similarity (0-1) for semantic evidence pass. Default 0.5.

### `def MedLitRelationshipExtractor.trace_dir(self) -> Path`

Get the trace directory.

### `def MedLitRelationshipExtractor.trace_dir(self, value: Path) -> None`

Set the trace directory.

### `def MedLitRelationshipExtractor._should_swap_subject_object(self, predicate: str, subject_entity: BaseEntity, object_entity: BaseEntity) -> bool`

Check if subject and object should be swapped based on type constraints.

Args:
    predicate: The relationship predicate
    subject_entity: The subject entity
    object_entity: The object entity

Returns:
    True if swapping subject and object would satisfy type constraints, False otherwise.

### `def MedLitRelationshipExtractor._validate_predicate_semantics(self, predicate: str, evidence: str) -> bool`

Validate that predicate semantics match the evidence text.

Checks for semantic mismatches like:
- "increases_risk" with positive therapeutic language
- "treats" with negative/harmful language

Args:
    predicate: The relationship predicate (e.g., "treats", "increases_risk")
    evidence: The evidence text supporting the relationship

Returns:
    True if predicate matches evidence semantics, False if there's a mismatch.

### `async def MedLitRelationshipExtractor.extract(self, document: BaseDocument, entities: Sequence[BaseEntity]) -> list[BaseRelationship]`

Extract relationships from a journal article.

If the document metadata contains pre-extracted relationships (from med-lit-schema),
we convert those to BaseRelationship objects. Otherwise, if llm_client is provided,
extracts relationships from document text using LLM.

Args:
    document: The journal article document.
    entities: The resolved entities from this document.

Returns:
    List of BaseRelationship objects representing relationships in the paper.

### `def MedLitRelationshipExtractor._build_llm_prompt(self, text_sample: str, entity_list: str) -> str`

Build the prompt for the LLM.

Notes:
- This prompt is driven by the domain schema:
  - self._domain.relationship_types (vocabulary)
  - self._domain.predicate_constraints (allowed subject/object types)
- Predicates must be returned in *lowercase* (e.g. "treats"), because downstream
  code currently normalizes and stores predicates as lowercase. :contentReference[oaicite:3]{index=3}

### `async def MedLitRelationshipExtractor._extract_with_llm(self, document: BaseDocument, entities: Sequence[BaseEntity]) -> list[BaseRelationship]`

Extract relationships using LLM.

Also writes a trace file to /tmp/kgraph-relationship-traces/ for debugging.
The trace captures: prompt, raw LLM output, parsed JSON, and per-item decisions.

### `async def MedLitRelationshipExtractor._process_llm_item(self, item: Any, entity_index: dict[str, list[BaseEntity]], document: BaseDocument) -> tuple[BaseRelationship | None, dict[str, Any]]`

Process a single item from the LLM response.

### `def MedLitRelationshipExtractor.write_skip_trace(self, document_id: str, reason: str, entity_count: int) -> None`

Write a minimal trace file when a window is skipped (e.g. fewer than 2 entities).

Uses the same path convention as _write_trace so skip and full traces
appear in the same directory. Call from WindowedRelationshipExtractor
when a chunk is skipped so --trace-all still produces a trace per window.

### `def MedLitRelationshipExtractor._write_trace(self, document_id: str, trace: dict[str, Any]) -> None`

Write trace file for debugging relationship extraction.

When document_id is from a windowed run (e.g. PMC12770061_window_5),
the filename includes the window index so each window gets its own file
(e.g. PMC12770061.5.relationships.trace.json) and earlier windows are
not overwritten.


<span id="user-content-medlitmedlitpipelineresolvepy"></span>

# medlit/medlit/pipeline/resolve.py

Entity resolution for medical literature domain.

Resolves entity mentions to canonical entities using UMLS, HGNC, RxNorm, UniProt IDs.

> Entity resolution for medical literature domain.

Resolves entity mentions to canonical entities using UMLS, HGNC, RxNorm, UniProt IDs.


## `class MedLitEntityResolver(BaseModel, EntityResolverInterface)`

Resolve medical entity mentions to canonical or provisional entities.

Resolution strategy (hybrid approach):
1. If mention has canonical_id_hint (from pre-extracted entities), use that
2. Check if entity with that ID already exists in storage
3. If not, create new canonical entity (since we have authoritative IDs)
4. For mentions without canonical IDs:
   a. Try embedding-based semantic matching against existing entities (if embedding_generator provided)
   b. If no match found, create provisional entities

The embedding-based matching acts as a semantic cache, catching variations like:
- "BRCA-1" vs "BRCA1"
- "breast cancer 1 gene" vs "BRCA1"
- "TP53" vs "p53"
**Fields:**

```python
domain: DomainSchema
embedding_generator: EmbeddingGeneratorInterface | None
similarity_threshold: float
```

### `async def MedLitEntityResolver.resolve(self, mention: EntityMention, existing_storage: EntityStorageInterface) -> tuple[BaseEntity, float]`

Resolves a single entity mention to a canonical or provisional entity.

This method implements the core resolution logic, applying a hybrid
strategy. It prioritizes explicit canonical IDs, falls back to
embedding-based similarity matching, and finally creates a new
provisional entity if no match is found.

Args:
    mention: The `EntityMention` to resolve.
    existing_storage: The entity storage backend to query for existing
                      entities.

Returns:
    A tuple containing the resolved `BaseEntity` (which may be new or
    existing, canonical or provisional) and a confidence score for the
    resolution.

Raises:
    ValueError: If the mention's entity type is not defined in the
                domain schema.

### `async def MedLitEntityResolver.resolve_batch(self, mentions: Sequence[EntityMention], existing_storage: EntityStorageInterface) -> list[tuple[BaseEntity, float]]`

Resolves a sequence of entity mentions.

This method currently resolves mentions sequentially by calling `resolve`
for each one. It is designed to be a placeholder for a future, more
optimized implementation that could batch database lookups or API calls.

Args:
    mentions: A sequence of `EntityMention` objects to resolve.
    existing_storage: The entity storage backend, passed to `resolve`.

Returns:
    A list of (entity, confidence) tuples, with each tuple
    corresponding to an input mention in the same order.

### `def MedLitEntityResolver._parse_canonical_id(self, entity_id: str, entity_type: str) -> dict[str, str]`

Parses a canonical ID string into a structured dictionary.

This utility function takes a raw ID string (e.g., "HGNC:1100") and
converts it into a `canonical_ids` dictionary (e.g.,
`{"hgnc": "HGNC:1100"}`). It handles both prefixed IDs and attempts to
infer the authority for non-prefixed IDs based on the entity type.

Args:
    entity_id: The canonical ID string to parse.
    entity_type: The entity's type, used to infer the authority for
                 non-prefixed IDs.

Returns:
    A dictionary mapping the authority name (e.g., "hgnc") to the
    full canonical ID.


<span id="user-content-medlitmedlitpipelineutilspy"></span>

# medlit/medlit/pipeline/utils.py

Shared utilities for medlit pipeline.

### `def canonicalize_symmetric(subject_id: str, object_id: str) -> tuple[str, str]`

Return (min, max) of subject and object for deterministic symmetric edge storage.

Used by dedup so symmetric predicates (e.g. ASSOCIATED_WITH) produce
identical (subject, object_id) regardless of order.


<span id="user-content-medlitmedlitpromotionpy"></span>

# medlit/medlit/promotion.py

Promotion policy for medical literature domain.

Promotes provisional entities to canonical status when they have authoritative
identifiers (UMLS, HGNC, RxNorm, UniProt) or meet usage/confidence thresholds.

> Promotion policy for medical literature domain.

Promotes provisional entities to canonical status when they have authoritative
identifiers (UMLS, HGNC, RxNorm, UniProt) or meet usage/confidence thresholds.


## `class MedLitPromotionPolicy(PromotionPolicy)`

Promotion policy for medical literature domain.

Assigns canonical IDs based on authoritative medical ontologies:
- Diseases: UMLS IDs (e.g., "C0006142")
- Genes: HGNC IDs (e.g., "HGNC:1100")
- Drugs: RxNorm IDs (e.g., "RxNorm:1187832")
- Proteins: UniProt IDs (e.g., "UniProt:P38398")

Promotion strategy:
1. If entity already has canonical_id in canonical_ids dict, use that
2. If entity_id is already a canonical ID format, use it directly
3. Otherwise, look up canonical ID from authority APIs (UMLS, HGNC, RxNorm, UniProt)

Some entity types do not have their own authority but map naturally to one
that does.  ``_AUTHORITY_TYPE_OVERRIDES`` redirects those types so the
lookup uses the right ontology.

### `def MedLitPromotionPolicy.__init__(self, config, lookup: Optional[CanonicalIdLookupInterface] = None)`

Initialize promotion policy.

Args:
    config: Promotion configuration with thresholds.
    lookup: Optional canonical ID lookup service. If None, will create
            a new CanonicalIdLookup instance (without UMLS API key unless set in env).

### `def MedLitPromotionPolicy.should_promote(self, entity: BaseEntity) -> bool`

Check if entity meets promotion thresholds.

Force-promote rules (bypass standard thresholds):
- If confidence >= 0.7, ignore usage count requirement
- If canonical ID is found (checked in run_promotion), promote regardless

Standard thresholds:
- usage_count >= min_usage_count (default: 1)
- confidence >= min_confidence (default: 0.4)
- embedding required only if require_embedding=True (default: False)

### `async def MedLitPromotionPolicy.assign_canonical_id(self, entity: BaseEntity) -> Optional[CanonicalId]`

Assign canonical ID for a provisional entity.

Args:
    entity: The provisional entity to promote.

Returns:
    CanonicalId if available, None otherwise.


<span id="user-content-medlitmedlitrelationshipspy"></span>

# medlit/medlit/relationships.py

Medical relationship types for the knowledge graph.

Following Pattern A (simple, scalable): many predicates → one relationship class.
This allows fast implementation without class explosion, while the predicate
still stays in the `predicate` field for clear queries.

> Medical relationship types for the knowledge graph.

Following Pattern A (simple, scalable): many predicates → one relationship class.
This allows fast implementation without class explosion, while the predicate
still stays in the `predicate` field for clear queries.


## `class MedicalClaimRelationship(BaseRelationship)`

Base class for all medical claim relationships.

This single class handles all medical predicates (treats, causes,
increases_risk, etc.). The predicate field distinguishes the relationship
type, and domain-specific metadata can be stored in the metadata dict.

Mapping from med-lit-schema:
- AssertedRelationship.subject_id → BaseRelationship.subject_id
- AssertedRelationship.predicate → BaseRelationship.predicate
- AssertedRelationship.object_id → BaseRelationship.object_id
- AssertedRelationship.confidence → BaseRelationship.confidence
- AssertedRelationship.evidence → BaseRelationship.metadata["evidence"]
- AssertedRelationship.section → BaseRelationship.metadata["section"]
- AssertedRelationship.metadata → BaseRelationship.metadata (merged)

For multi-paper aggregation:
- source_documents includes all paper IDs that assert this relationship
- metadata["assertions"][paper_id] = {"evidence": "...", "section": "...", ...}

### `def MedicalClaimRelationship.get_edge_type(self) -> str`

Return edge type category.

For Pattern A, we return a generic "medical_claim" since all
predicates use the same class. If we later split into typed classes,
each would return its specific type.


<span id="user-content-medlitmedlitscriptsinitpy"></span>

# medlit/medlit/scripts/__init__.py

Scripts for medical literature ingestion.


<span id="user-content-medlitmedlitscriptsbuildbundlepy"></span>

# medlit/medlit/scripts/build_bundle.py

build_bundle: Build kgbundle from merged and extracted.

Reads merged_dir (entities.json, relationships.json, id_map.json, synonym_cache.json)
and bundles_dir (paper_*.json), writes output_dir in kgbundle format for kgserver.

> build_bundle: Build kgbundle from merged and extracted.

Reads merged_dir (entities.json, relationships.json, id_map.json, synonym_cache.json)
and bundles_dir (paper_*.json), writes output_dir in kgbundle format for kgserver.



<span id="user-content-medlitmedlitscriptsextractpy"></span>

# medlit/medlit/scripts/extract.py

extract: Extract entities and relationships from papers via LLM → per-paper bundle JSON.

Reads papers from --input-dir (JATS XML or JSON), calls the configured LLM once per paper,
and writes one JSON file per paper to --output-dir. These bundles are immutable;
ingest reads them and writes overlays or a merged graph elsewhere.

Requires an LLM backend: --llm-backend anthropic | openai | ollama.
Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or run Ollama locally. See LLM_SETUP.md.

Usage:
  python -m medlit.scripts.extract --input-dir pmc_xmls/ --output-dir bundles/ --llm-backend anthropic
  python -m medlit.scripts.extract --input-dir pmc_xmls/ --output-dir bundles/ --llm-backend ollama --limit 1
  python -m medlit.scripts.extract --input-dir pmc_xmls/ --output-dir bundles/ --papers "PMC127*.xml,PMC128*.json"

> extract: Extract entities and relationships from papers via LLM → per-paper bundle JSON.

Reads papers from --input-dir (JATS XML or JSON), calls the configured LLM once per paper,
and writes one JSON file per paper to --output-dir. These bundles are immutable;
ingest reads them and writes overlays or a merged graph elsewhere.

Requires an LLM backend: --llm-backend anthropic | openai | ollama.
Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or run Ollama locally. See LLM_SETUP.md.

Usage:
  python -m medlit.scripts.extract --input-dir pmc_xmls/ --output-dir bundles/ --llm-backend anthropic
  python -m medlit.scripts.extract --input-dir pmc_xmls/ --output-dir bundles/ --llm-backend ollama --limit 1
  python -m medlit.scripts.extract --input-dir pmc_xmls/ --output-dir bundles/ --papers "PMC127*.xml,PMC128*.json"


### `def _fix_evidence_paper_id(evidence_id: str, paper_id: str) -> str`

Replace placeholder or hallucinated paper_id in evidence ID with actual.

When processing paper X, the only valid paper_id in evidence is X. Replace:
- Placeholders (PMC_UNKNOWN, paper_id, PMC11000000, etc.)
- PMC IDs that are not the current paper (hallucinated citations)

### `def _replace_current_paper_in_bundle(obj: Any, paper_id: str) -> None`

Recursively replace ==CURRENT_PAPER== with paper_id in dict/list/str (mutates in place).

### `def _git_info() -> dict`

Return git_commit, git_commit_short, git_branch, git_dirty, repo_url.

### `def build_provenance(llm_name: str, llm_version: str, prompt_version: str = 'v1', prompt_template: str = 'medlit_extraction_v1', prompt_checksum: Optional[str] = None, duration_seconds: Optional[float] = None, schema_version: Optional[str] = None) -> ExtractionProvenance`

Build extraction_provenance for extract output.

### `def normalize_entity_type(raw_type: str, normalized_to_bundle: dict[str, str]) -> str`

Map raw LLM type string to bundle entity_class (PascalCase). Unknown types -> 'Other'.

### `def _default_system_prompt(vocab_entries: Optional[list[dict]] = None, domain_spec: Optional[Any] = None) -> str`

Build system prompt from domain_spec via Jinja2 template.

### `async def _paper_content_from_parser(raw_content: bytes, content_type: str, source_uri: str) -> tuple[str, Optional[PaperInfo]]`

Extract text and minimal PaperInfo from raw content using existing parser.

### `async def _extract_study_design(llm: Any, content: str) -> Optional[StudyDesignMetadata]`

Second LLM call: extract study design from Methods/abstract. Returns None on failure.

### `def _paper_content_fallback(raw_content: bytes, source_uri: str) -> tuple[str, PaperInfo]`

Fallback: use raw text and filename for paper id.

### `async def run_extract(input_dir: Path, output_dir: Path, llm_backend: str, limit: Optional[int] = None, papers: Optional[list[str]] = None, system_prompt: Optional[str] = None, vocab_file: Optional[Path] = None) -> None`

Run extract: for each paper in input_dir, call LLM and write bundle JSON to output_dir.


<span id="user-content-medlitmedlitscriptsfetchvocabpy"></span>

# medlit/medlit/scripts/fetch_vocab.py

fetch_vocab: Fast vocabulary extraction across papers → vocab.json + seeded synonym cache.

Runs a cheap LLM prompt per paper (entities only, no relationships), merges results
into a shared vocabulary, runs UMLS type validation on entities with umls_id, and
writes vocab.json plus an ingest-compatible seeded_synonym_cache.json. extract and
ingest consume these for consistent names/types and dedup seeding.

Usage:
  python -m medlit.scripts.fetch_vocab --input-dir pmc_xmls/ --output-dir vocab --llm-backend anthropic
  python -m medlit.scripts.fetch_vocab --input-dir pmc_xmls/ --output-dir vocab --llm-backend ollama --papers "PMC115*.xml"

> fetch_vocab: Fast vocabulary extraction across papers → vocab.json + seeded synonym cache.

Runs a cheap LLM prompt per paper (entities only, no relationships), merges results
into a shared vocabulary, runs UMLS type validation on entities with umls_id, and
writes vocab.json plus an ingest-compatible seeded_synonym_cache.json. extract and
ingest consume these for consistent names/types and dedup seeding.

Usage:
  python -m medlit.scripts.fetch_vocab --input-dir pmc_xmls/ --output-dir vocab --llm-backend anthropic
  python -m medlit.scripts.fetch_vocab --input-dir pmc_xmls/ --output-dir vocab --llm-backend ollama --papers "PMC115*.xml"


### `def _pass1a_system_prompt() -> str`

Build fetch_vocab system prompt from domain_spec.

### `def _vocab_key(entry: dict[str, Any]) -> tuple[str, str]`

Key for merging: (normalized name, type).

### `async def _paper_content(path: Path, input_dir: Path) -> tuple[str, str]`

Return (content_text, paper_id) for a paper file.

### `def _merge_vocab_into(existing: list[dict[str, Any]], new_entries: list[dict[str, Any]], source_paper: str) -> None`

Merge new_entries into existing in place; same (name, type) adds source_paper to source_papers.

### `def _run_umls_validation(vocab_entries: list[dict[str, Any]]) -> None`

Run UMLS type validation on entries with umls_id; update type and set umls_type_validated/umls_type_conflict.

### `def _vocab_to_seeded_cache(vocab_entries: list[dict[str, Any]], normalized_to_bundle: dict[str, str]) -> dict[str, list[dict[str, Any]]]`

Build ingest synonym cache format from vocab list so lookup_entity returns canonical_id.

### `def _atomic_write_json(path: Path, data: Any) -> None`

Write JSON to path via temp file then rename.

### `async def run_fetch_vocab(input_dir: Path, output_dir: Path, llm_backend: str, papers: Optional[list[str]] = None, limit: Optional[int] = None) -> None`

Run fetch_vocab: extract vocabulary from papers, merge, validate UMLS types, write vocab + seeded cache.


<span id="user-content-medlitmedlitscriptsingestpy"></span>

# medlit/medlit/scripts/ingest.py

ingest: Deduplication and promotion over per-paper bundles.

Reads all paper_*.json bundles from --bundle-dir (output of extract), builds
name/type index and synonym cache, resolves SAME_AS, assigns canonical IDs,
and writes merged entities and relationships to --output-dir. Original
bundle files are never modified.

Usage (legacy file-based pipeline):
  python -m medlit.scripts.ingest --bundle-dir extracted/ --output-dir merged/

Usage (identity server):
  python -m medlit.scripts.ingest --bundle-dir extracted/ --output-dir merged/ \
      --use-identity-server
  Requires DATABASE_URL env var pointing to a running Postgres instance with
  the kgserver schema already created.

> ingest: Deduplication and promotion over per-paper bundles.

Reads all paper_*.json bundles from --bundle-dir (output of extract), builds
name/type index and synonym cache, resolves SAME_AS, assigns canonical IDs,
and writes merged entities and relationships to --output-dir. Original
bundle files are never modified.

Usage (legacy file-based pipeline):
  python -m medlit.scripts.ingest --bundle-dir extracted/ --output-dir merged/

Usage (identity server):
  python -m medlit.scripts.ingest --bundle-dir extracted/ --output-dir merged/ \
      --use-identity-server
  Requires DATABASE_URL env var pointing to a running Postgres instance with
  the kgserver schema already created.



<span id="user-content-medlitmedlitscriptsparsepmcxmlpy"></span>

# medlit/medlit/scripts/parse_pmc_xml.py

Parse PMC JATS-XML files directly to Paper schema JSON format.

This script combines XML parsing and schema conversion into a single step,
converting JATS-XML files directly to the format expected by JournalArticleParser.

> Parse PMC JATS-XML files directly to Paper schema JSON format.

This script combines XML parsing and schema conversion into a single step,
converting JATS-XML files directly to the format expected by JournalArticleParser.


### `def parse_pmc_xml_to_paper_schema(xml_path: Path) -> dict`

Parse PMC XML file directly into Paper schema JSON format.

Args:
    xml_path: Path to the PMC XML file

Returns:
    Dictionary in Paper schema format with:
    - paper_id: PMC ID (from filename)
    - title: Article title
    - abstract: Dict with "text" key containing abstract
    - full_text: Full body text (if available)
    - authors: List of author names
    - metadata: Dict with keywords (if available)


<span id="user-content-medlitmedlitvocabpy"></span>

# medlit/medlit/vocab.py

Vocabulary and validation for medical literature domain.

Defines valid predicates and their constraints (which entity types
can participate in which relationships).

> Vocabulary and validation for medical literature domain.

Defines valid predicates and their constraints (which entity types
can participate in which relationships).


### `def get_valid_predicates(subject_type: str, object_type: str) -> list[str]`

Return predicates valid between two entity types.

This implements domain-specific constraints. For example:
- Drug → Disease: treats, prevents, contraindicated_for, side_effect
- Gene → Disease: increases_risk, decreases_risk, associated_with
- Gene → Protein: encodes
- Drug → Drug: interacts_with
- Disease → Symptom: causes
- Disease → Procedure: diagnosed_by

Args:
    subject_type: The entity type of the relationship subject.
    object_type: The entity type of the relationship object.

Returns:
    List of predicate names that are valid for this entity type pair.


<span id="user-content-medlitmedlitschemainitpy"></span>

# medlit/medlit_schema/__init__.py

Medical Literature Domain Schema for kgraph.

This package provides production-ready schema definitions for medical
literature knowledge graphs, with full provenance tracking, ontology
integration, and evidence-based relationships.

Schema version: 1.0.0
Compatible with: kgschema >=0.2.0
Ontologies: UMLS, HGNC, RxNorm, UniProt, ECO, OBI, STATO, SEPIO

> 
Medical Literature Domain Schema for kgraph.

This package provides production-ready schema definitions for medical
literature knowledge graphs, with full provenance tracking, ontology
integration, and evidence-based relationships.

Schema version: 1.0.0
Compatible with: kgschema >=0.2.0
Ontologies: UMLS, HGNC, RxNorm, UniProt, ECO, OBI, STATO, SEPIO



<span id="user-content-medlitmedlitschemabasepy"></span>

# medlit/medlit_schema/base.py

Base models for the medlit schema.

## `class ModelInfo(BaseModel)`

Information about the model used for extraction.
**Fields:**

```python
name: str
version: str
```

## `class ExtractionProvenance(BaseModel)`

Complete provenance metadata for an extraction.

This is the complete audit trail of how extraction was performed.
Enables:
- Reproducing exact extraction with same code/models/prompts
- Comparing outputs from different pipeline versions
- Debugging quality issues
- Tracking pipeline evolution over time
- Meeting reproducibility requirements for research

Example queries enabled by provenance:
- "Find all papers extracted with prompt v1 so I can re-extract with v2"
- "Which papers were extracted with uncommitted code changes?"
- "Compare entity extraction quality between llama3.1:70b and claude-4"

Attributes:
    extraction_pipeline: Pipeline version info
    models: Models used, keyed by role (e.g., 'llm', 'embeddings')
    prompt: Prompt version info
    execution: Execution environment info
    entity_resolution: Entity resolution details if applicable
**Fields:**

```python
extraction_pipeline: Optional['ExtractionPipelineInfo']
models: dict[str, ModelInfo]
prompt: Optional['PromptInfo']
execution: Optional['ExecutionInfo']
entity_resolution: Optional['EntityResolutionInfo']
model_info: Optional[ModelInfo]
```

## `class SectionType(str, Enum)`

Type of section in a paper.

## `class TextSpanRef(BaseModel)`

A structural locator for text within a parsed document.

This is a parser/segmentation address that uses structural coordinates
(section type, paragraph index, sentence index) to locate text. It is
distinct from TextSpan (entity.py), which is a graph entity anchor with
precise character offsets.

Use this for:
- Intermediate parsing stages before final offsets are computed
- Structural navigation within documents
- Creating TextSpan entities once offsets are finalized

Attributes:
    paper_id: The ID of the paper this span belongs to.
    section_type: The type of section (abstract, introduction, etc.).
    paragraph_idx: Zero-based paragraph index within the section.
    sentence_idx: Optional sentence index within the paragraph.
    text_span: Optional text snippet for reference.
    start_offset: Optional character offset (for when computed).
    end_offset: Optional character offset (for when computed).
**Fields:**

```python
paper_id: str
section_type: SectionType
paragraph_idx: int
sentence_idx: Optional[int]
text_span: Optional[str]
start_offset: Optional[int]
end_offset: Optional[int]
```

## `class ExtractionMethod(str, Enum)`

Method used for extraction.

## `class StudyType(str, Enum)`

Type of study.

## `class PredicateType(str, Enum)`

All possible predicates (relationship types) in the medical literature knowledge graph.

This enum provides type safety for relationship categorization and enables
validation of entity-relationship compatibility.

## `class EntityType(str, Enum)`

All possible entity types in the knowledge graph.

This enum provides type safety for entity categorization and enables
validation of entity-relationship compatibility.

## `class ClaimPredicate(BaseModel)`

Describes the nature of a claim made in a paper.

Examples:
    - "Olaparib significantly improved progression-free survival" (TREATS)
    - "BRCA1 mutations increase breast cancer risk by 5-fold" (INCREASES_RISK)
    - "Warfarin and aspirin interact synergistically" (INTERACTS_WITH)

Attributes:
    predicate_type: The type of relationship asserted in the claim
    description: A natural language description of the predicate as it appears in the text
**Fields:**

```python
predicate_type: PredicateType
description: str
```

## `class Provenance(BaseModel)`

Information about the origin of a piece of data.

Attributes:
    source_type: The type of source (e.g., 'paper', 'database', 'model_extraction')
    source_id: An identifier for the source (e.g., DOI, database record ID)
    source_version: The version of the source, if applicable
    notes: Additional notes about the provenance
**Fields:**

```python
source_type: str
source_id: str
source_version: Optional[str]
notes: Optional[str]
```

## `class EvidenceType(BaseModel)`

The type of evidence supporting a relationship, linked to evidence ontologies.

Examples:
    - RCT: ontology_id="ECO:0007673", ontology_label="randomized controlled trial evidence"
    - Observational: ontology_id="ECO:0000203", ontology_label="observational study evidence"
    - Case report: ontology_id="ECO:0006016", ontology_label="case study evidence"

Attributes:
    ontology_id: Identifier from an evidence ontology (ECO, SEPIO)
    ontology_label: Human-readable label for the ontology term
    description: A fuller description of the evidence type
**Fields:**

```python
ontology_id: str
ontology_label: str
description: Optional[str]
```

## `class EntityReference(BaseModel)`

Reference to an entity in the knowledge graph.

Lightweight pointer to a canonical entity (Disease, Drug, Gene, etc.)
with the name as it appeared in this specific paper.

Attributes:
    id: Canonical entity ID
    name: Entity name as mentioned in paper
    type: Entity type (drug, disease, gene, protein, etc.)
**Fields:**

```python
id: str
name: str
type: EntityType
```

## `class Polarity(str, Enum)`

Polarity of evidence relative to a claim.

## `class Edge(BaseModel)`

Base edge in the knowledge graph.
**Fields:**

```python
id: EdgeId
subject: EntityReference
object: EntityReference
provenance: Provenance
```

## `class ExtractionEdge(Edge)`

Edge from automated extraction.

## `class ClaimEdge(Edge)`

Edge representing a claim from a paper.

## `class EvidenceEdge(Edge)`

Edge representing evidence for a claim.

## `class ExtractionPipelineInfo(BaseModel)`

Information about the extraction pipeline version.

Tracks the exact code version that performed entity/relationship extraction.
Essential for reproducibility and debugging extraction quality issues.

Attributes:
    name: Pipeline name (e.g., 'ollama_langchain_ingest')
    version: Semantic version of the pipeline
    git_commit: Full git commit hash
    git_commit_short: Short git commit hash (7 chars)
    git_branch: Git branch name
    git_dirty: Whether working directory had uncommitted changes
    repo_url: Repository URL
**Fields:**

```python
name: str
version: str
git_commit: str
git_commit_short: str
git_branch: str
git_dirty: bool
repo_url: str
```

## `class PromptInfo(BaseModel)`

Information about the prompt used.

Tracks prompt evolution. Critical for understanding extraction behavior changes.

Attributes:
    version: Prompt version identifier
    template: Prompt template name
    checksum: SHA256 of actual prompt text for exact reproduction
    schema_version: 8-char hex hash of config (entity_types, predicates, domain_instructions)
**Fields:**

```python
version: str
template: str
checksum: Optional[str]
schema_version: Optional[str]
```

## `class ExecutionInfo(BaseModel)`

Information about when and where extraction was performed.

Useful for debugging issues related to specific machines or time periods.

Attributes:
    timestamp: ISO 8601 UTC timestamp
    hostname: Hostname of machine that ran extraction
    python_version: Python version
    duration_seconds: Extraction duration in seconds
**Fields:**

```python
timestamp: str
hostname: str
python_version: str
duration_seconds: Optional[float]
```

## `class EntityResolutionInfo(BaseModel)`

Information about entity resolution process.

Tracks how entities were matched to canonical IDs. Helps identify when
entity deduplication is working poorly.

Attributes:
    canonical_entities_matched: Number of entities matched to existing canonical IDs
    new_entities_created: Number of new canonical entities created
    similarity_threshold: Similarity threshold used for matching
    embedding_model: Embedding model used for similarity
**Fields:**

```python
canonical_entities_matched: int
new_entities_created: int
similarity_threshold: float
embedding_model: str
```

## `class Measurement(BaseModel)`

Quantitative measurements associated with relationships.

Stores numerical data with appropriate metadata for statistical
analysis and evidence quality assessment.

Attributes:
    value: The numerical value
    unit: Unit of measurement (if applicable)
    value_type: Type of measurement (effect_size, p_value, etc.)
    p_value: Statistical significance
    confidence_interval: 95% confidence interval
    study_population: Description of study population
    measurement_context: Additional context about the measurement

Example:
    >>> measurement = Measurement(
    ...     value=0.59,
    ...     value_type="response_rate",
    ...     p_value=0.001,
    ...     confidence_interval=(0.52, 0.66),
    ...     study_population="BRCA-mutated breast cancer patients"
    ... )
**Fields:**

```python
value: float
unit: Optional[str]
value_type: str
p_value: Optional[float]
confidence_interval: Optional[tuple[float, float]]
study_population: Optional[str]
measurement_context: Optional[str]
```


<span id="user-content-medlitmedlitschemadocumentpy"></span>

# medlit/medlit_schema/document.py

Medlit document definitions.


<span id="user-content-medlitmedlitschemadomainpy"></span>

# medlit/medlit_schema/domain.py

Domain schema for the Medical Literature domain.

## `class MedlitDomain(DomainSchema)`

Domain schema for medical literature.


<span id="user-content-medlitmedlitschemaentitypy"></span>

# medlit/medlit_schema/entity.py

Medlit entity definitions.

## `class BaseMedicalEntity(BaseEntity)`

Base for all medical entities.
**Fields:**

```python
name: str
synonyms: tuple[str, ...]
abbreviations: List[str]
embedding: Optional[tuple[float, ...]]
source: Literal['umls', 'mesh', 'rxnorm', 'hgnc', 'uniprot', 'extracted']
```

## `class Disease(BaseMedicalEntity)`

Represents medical conditions, disorders, and syndromes.

Uses UMLS as the primary identifier system with additional mappings to
MeSH and ICD-10 for interoperability with clinical systems.

Attributes:
    umls_id: UMLS Concept ID (e.g., "C0006142" for Breast Cancer)
    mesh_id: Medical Subject Heading ID for literature indexing
    icd10_codes: List of ICD-10 diagnostic codes
    category: Disease classification (genetic, infectious, autoimmune, etc.)

Example:
    >>> breast_cancer = Disease(
    ...     entity_id="C0006142",
    ...     name="Breast Cancer",
    ...     synonyms=("Breast Carcinoma", "Mammary Cancer"),
    ...     umls_id="C0006142",
    ...     mesh_id="D001943",
    ...     icd10_codes=["C50.9"],
    ...     category="genetic",
    ...     source="umls"
    ... )
**Fields:**

```python
umls_id: Optional[str]
mesh_id: Optional[str]
icd10_codes: List[str]
category: Optional[str]
```

## `class Gene(BaseMedicalEntity)`

Represents human genes.

Uses HGNC (HUGO Gene Nomenclature Committee) as the primary identifier
with additional mappings to Entrez Gene for cross-reference.

Attributes:
    symbol: Official gene symbol (e.g., "BRCA1")
    hgnc_id: HGNC identifier (e.g., "HGNC:1100")
    chromosome: Chromosomal location (e.g., "17q21.31")
    entrez_id: NCBI Entrez Gene ID

Example:
    >>> brca1 = Gene(
    ...     entity_id="HGNC:1100",
    ...     name="BRCA1",
    ...     symbol="BRCA1",
    ...     hgnc_id="HGNC:1100",
    ...     chromosome="17q21.31",
    ...     entrez_id="672",
    ...     source="hgnc"
    ... )
**Fields:**

```python
symbol: Optional[str]
hgnc_id: Optional[str]
chromosome: Optional[str]
entrez_id: Optional[str]
```

## `class Drug(BaseMedicalEntity)`

Represents pharmaceutical drugs and medications.

Uses RxNorm as the primary identifier system for standardized drug names.

Attributes:
    rxnorm_id: RxNorm concept identifier (e.g., "1187832" for Olaparib)
    brand_names: Commercial brand names (e.g., ["Lynparza"])
    drug_class: Pharmacological class (e.g., "PARP inhibitor")
    mechanism: Mechanism of action description

Example:
    >>> olaparib = Drug(
    ...     entity_id="RxNorm:1187832",
    ...     name="Olaparib",
    ...     rxnorm_id="1187832",
    ...     brand_names=["Lynparza"],
    ...     drug_class="PARP inhibitor",
    ...     mechanism="Inhibits PARP enzymes",
    ...     source="rxnorm"
    ... )
**Fields:**

```python
rxnorm_id: Optional[str]
brand_names: List[str]
drug_class: Optional[str]
mechanism: Optional[str]
```

## `class Protein(BaseMedicalEntity)`

Represents proteins and protein complexes.

Uses UniProt as the primary identifier system.

Attributes:
    uniprot_id: UniProt accession (e.g., "P38398" for BRCA1 protein)
    gene_id: Associated gene identifier
    function: Protein function description
    pathways: List of pathway IDs this protein participates in

Example:
    >>> brca1_protein = Protein(
    ...     entity_id="UniProt:P38398",
    ...     name="BRCA1",
    ...     uniprot_id="P38398",
    ...     gene_id="HGNC:1100",
    ...     function="DNA repair",
    ...     pathways=["R-HSA-5685942"],
    ...     source="uniprot"
    ... )
**Fields:**

```python
uniprot_id: Optional[str]
gene_id: Optional[str]
function: Optional[str]
pathways: List[str]
```

## `class Mutation(BaseMedicalEntity)`

Represents genetic mutations and variants.

Attributes:
    variant_notation: HGVS notation (e.g., "c.68_69delAG")
    consequence: Effect of mutation (e.g., "frameshift", "missense")
    clinical_significance: ClinVar significance (pathogenic, benign, etc.)

Example:
    >>> brca1_mutation = Mutation(
    ...     entity_id="BRCA1_c.68_69delAG",
    ...     name="BRCA1 c.68_69delAG",
    ...     variant_notation="c.68_69delAG",
    ...     consequence="frameshift",
    ...     clinical_significance="pathogenic",
    ...     source="extracted"
    ... )
**Fields:**

```python
variant_notation: Optional[str]
consequence: Optional[str]
clinical_significance: Optional[str]
```

## `class Symptom(BaseMedicalEntity)`

Represents clinical signs and symptoms.

Attributes:
    severity_scale: Measurement scale if applicable (e.g., "0-10", "mild/moderate/severe")
    onset_pattern: Typical onset (acute, chronic, intermittent)

Example:
    >>> pain = Symptom(
    ...     entity_id="C0030193",
    ...     name="Pain",
    ...     umls_id="C0030193",
    ...     severity_scale="0-10",
    ...     onset_pattern="varies",
    ...     source="umls"
    ... )
**Fields:**

```python
severity_scale: Optional[str]
onset_pattern: Optional[str]
```

## `class Biomarker(BaseMedicalEntity)`

Represents biological markers used for diagnosis or prognosis.

Attributes:
    loinc_code: LOINC code for lab tests
    measurement_type: Type of measurement (protein, metabolite, imaging, etc.)
    clinical_use: Primary clinical application

Example:
    >>> ca125 = Biomarker(
    ...     entity_id="LOINC:10334-1",
    ...     name="CA-125",
    ...     loinc_code="10334-1",
    ...     measurement_type="protein",
    ...     clinical_use="ovarian cancer screening",
    ...     source="extracted"
    ... )
**Fields:**

```python
loinc_code: Optional[str]
measurement_type: Optional[str]
clinical_use: Optional[str]
```

## `class Pathway(BaseMedicalEntity)`

Represents biological pathways.

Attributes:
    kegg_id: KEGG pathway identifier
    reactome_id: Reactome pathway identifier
    pathway_type: Type of pathway (signaling, metabolic, etc.)

Example:
    >>> dna_repair = Pathway(
    ...     entity_id="R-HSA-5685942",
    ...     name="HDR through Homologous Recombination",
    ...     reactome_id="R-HSA-5685942",
    ...     pathway_type="DNA repair",
    ...     source="extracted"
    ... )
**Fields:**

```python
kegg_id: Optional[str]
reactome_id: Optional[str]
pathway_type: Optional[str]
```

## `class Procedure(BaseMedicalEntity)`

Represents medical tests, diagnostics, treatments.

Attributes:
    type: Procedure category (diagnostic, therapeutic, preventive)
    invasiveness: Invasiveness level (non-invasive, minimally invasive, invasive)
**Fields:**

```python
type: Optional[str]
invasiveness: Optional[str]
```

## `class PaperMetadata(BaseModel)`

Extended metadata about the research paper.

Combines study characteristics (for evidence quality assessment) with
bibliographic information (for citations and filtering).

This is MORE than just storage - these fields enable critical queries:
- "Show me only RCT evidence for this drug-disease relationship"
- "What's the sample size distribution for studies on this topic?"
- "Find papers from high-impact journals on this mutation"

Attributes:
    study_type: Type of study (observational, rct, meta_analysis, case_report, review)
    sample_size: Study sample size - larger = more reliable
    study_population: Description of study population
    primary_outcome: Primary outcome measured
    clinical_phase: Clinical trial phase if applicable
    mesh_terms: Medical Subject Headings - NLM's controlled vocabulary for indexing

Example:
    >>> metadata = PaperMetadata(
    ...     study_type="rct",
    ...     sample_size=302,
    ...     study_population="Women with BRCA1/2-mutated metastatic breast cancer",
    ...     primary_outcome="Progression-free survival",
    ...     clinical_phase="III",
    ...     mesh_terms=["Breast Neoplasms", "BRCA1 Protein", "PARP Inhibitors"]
    ... )
**Fields:**

```python
study_type: Optional[str]
sample_size: Optional[int]
study_population: Optional[str]
primary_outcome: Optional[str]
clinical_phase: Optional[str]
mesh_terms: List[str]
```

## `class TextSpan(BaseEntity)`

Represents a specific span of text within a document, acting as an anchor for evidence.

This entity provides fine-grained provenance for assertions by linking them
to exact locations within a source paper. It serves as a first-class entity
that can be referenced by Evidence.

TextSpan is canonical-only (not promotable) because:
- Character offsets are stable only relative to a specific text representation
- The combination of paper_id + section + offsets provides a natural canonical ID
- There is no meaningful "provisional" state for a text location

Note: This is distinct from TextSpanRef (base.py), which is a structural locator
using paragraph/sentence indices for parsing stages before final offsets are computed.

Attributes:
    paper_id: The ID of the paper this text span belongs to.
    section: The section of the paper (e.g., "abstract", "introduction", "results").
    start_offset: The character offset where the span starts in the section content (required).
    end_offset: The character offset where the span ends in the section content (required).
    text_content: The actual text content of the span (optional, for convenience and caching).
**Fields:**

```python
promotable: bool
status: EntityStatus
paper_id: str
section: str
start_offset: int
end_offset: int
text_content: Optional[str]
```

### `def TextSpan.end_must_be_greater_than_start(cls, v, info)`

Validate that end_offset > start_offset.

## `class Paper(BaseEntity)`

A research paper with extracted entities, relationships, and full provenance.

This is the COMPLETE representation of a paper in the knowledge graph, combining:

1. Bibliographic metadata (authors, journal, identifiers)
2. Text content (title, abstract)
3. Study metadata (study type, sample size, etc.)
4. Extraction provenance (how extraction was performed)

Design philosophy:

- Top-level fields are FREQUENTLY QUERIED (paper_id, title, authors, publication_date)
- Nested objects group related data (paper_metadata for study info, extraction_provenance for pipeline info)

Why certain fields are top-level:

- paper_id: Primary key, referenced everywhere
- title, abstract: Core content, always displayed
- authors: Essential for citations, frequently filtered
- publication_date: Frequently used for filtering by recency
- journal: Frequently used for quality filtering

Why other fields are nested:

- paper_metadata: Study details, accessed together for evidence assessment
- extraction_provenance: Technical details, only for debugging/reproducibility

Attributes:
    paper_id: Unique identifier - PMC ID preferred, but can be DOI or PMID
    pmid: PubMed ID - different from PMC ID
    doi: Digital Object Identifier
    title: Full paper title
    abstract: Complete abstract text
    authors: List of author names in citation order
    publication_date: Publication date in ISO format (YYYY-MM-DD)
    journal: Journal name
    paper_metadata: Extended metadata including study type, sample size, MeSH terms
    extraction_provenance: Complete provenance of how extraction was performed

Example:
    >>> paper = Paper(
    ...     entity_id="PMC8437152",
    ...     paper_id="PMC8437152",
    ...     pmid="34567890",
    ...     doi="10.1234/nejm.2023.001",
    ...     title="Efficacy of Olaparib in BRCA-Mutated Breast Cancer",
    ...     abstract="Background: PARP inhibitors have shown promise...",
    ...     authors=["Smith J", "Johnson A", "Williams K"],
    ...     publication_date=datetime(2023, 6, 15),
    ...     journal="New England Journal of Medicine",
    ...     paper_metadata=PaperMetadata(
    ...         study_type="rct",
    ...         sample_size=302,
    ...         mesh_terms=["Breast Neoplasms", "PARP Inhibitors"]
    ...     )
    ... )
**Fields:**

```python
paper_id: str
pmid: Optional[str]
doi: Optional[str]
title: Optional[str]
abstract: Optional[str]
authors: List[str]
publication_date: Optional[datetime]
journal: Optional[str]
paper_metadata: PaperMetadata
extraction_provenance: Optional[ExtractionProvenance]
```

## `class Author(BaseEntity)`

Represents a researcher or author of scientific publications.

Attributes:
    orcid: ORCID identifier (unique researcher ID)
    affiliations: List of institutional affiliations
    h_index: Citation metric indicating research impact

Example:
    >>> author = Author(
    ...     entity_id="0000-0001-2345-6789",
    ...     name="Jane Smith",
    ...     orcid="0000-0001-2345-6789",
    ...     affiliations=["Harvard Medical School", "Massachusetts General Hospital"],
    ...     h_index=45,
    ...     source="orcid",
    ...     created_at=datetime.now()
    ... )
**Fields:**

```python
orcid: Optional[str]
affiliations: List[str]
h_index: Optional[int]
```

## `class ClinicalTrial(BaseEntity)`

Represents a clinical trial registered on ClinicalTrials.gov.

Attributes:
    nct_id: ClinicalTrials.gov identifier (e.g., "NCT01234567")
    title: Official trial title
    phase: Trial phase (I, II, III, IV)
    trial_status: Current status (recruiting, completed, terminated, etc.)
    intervention: Description of treatment being tested

Example:
    >>> trial = ClinicalTrial(
    ...     entity_id="NCT01234567",
    ...     name="Study of Drug X in Patients with Disease Y",
    ...     nct_id="NCT01234567",
    ...     title="Study of Drug X in Patients with Disease Y",
    ...     phase="III",
    ...     trial_status="completed",
    ...     intervention="Drug X 100mg daily",
    ...     source="clinicaltrials.gov",
    ...     created_at=datetime.now()
    ... )
**Fields:**

```python
nct_id: Optional[str]
title: Optional[str]
phase: Optional[str]
trial_status: Optional[str]
intervention: Optional[str]
```

## `class Institution(BaseEntity)`

Represents research institutions and affiliations.

Attributes:
    country: Country location
    department: Department or division

Example:
    >>> institution = Institution(
    ...     entity_id="INST:harvard_med",
    ...     name="Harvard Medical School",
    ...     country="USA",
    ...     department="Oncology",
    ...     source="extracted",
    ...     created_at=datetime.now()
    ... )
**Fields:**

```python
country: Optional[str]
department: Optional[str]
```

## `class Hypothesis(BaseEntity)`

Represents a scientific hypothesis tracked across the literature.

Uses IAO (Information Artifact Ontology) for standardized representation
of hypotheses as information content entities. Enables tracking of
hypothesis evolution: from proposal through testing to acceptance/refutation.

Attributes:
    iao_id: IAO identifier (typically IAO:0000018 for hypothesis)
    sepio_id: SEPIO identifier for assertions (SEPIO:0000001)
    proposed_by: Paper ID where hypothesis was first proposed
    proposed_date: Date when hypothesis was first proposed
    hypothesis_status: Current status (proposed, supported, controversial, refuted)
    description: Natural language description of the hypothesis
    predicts: List of entity IDs that this hypothesis predicts outcomes for

Example:
    >>> hypothesis = Hypothesis(
    ...     entity_id="HYPOTHESIS:amyloid_cascade_alzheimers",
    ...     name="Amyloid Cascade Hypothesis",
    ...     iao_id="IAO:0000018",
    ...     sepio_id="SEPIO:0000001",
    ...     proposed_by="PMC123456",
    ...     proposed_date="1992",
    ...     hypothesis_status="controversial",
    ...     description="Beta-amyloid accumulation drives Alzheimer's disease pathology",
    ...     predicts=["C0002395"],
    ...     source="extracted",
    ...     created_at=datetime.now()
    ... )
**Fields:**

```python
iao_id: Optional[str]
sepio_id: Optional[str]
proposed_by: Optional[str]
proposed_date: Optional[str]
hypothesis_status: Optional[str]
description: Optional[str]
predicts: List[str]
```

## `class StudyDesign(BaseEntity)`

Represents a study design or experimental protocol.

Uses OBI (Ontology for Biomedical Investigations) to standardize
study design classifications. Enables filtering by evidence quality
based on study design.

Attributes:
    obi_id: OBI identifier for study design type
    stato_id: STATO identifier for study design (if applicable)
    design_type: Human-readable design type
    description: Description of the study design
    evidence_level: Quality level (1-5, where 1 is highest quality)

Example:
    >>> rct = StudyDesign(
    ...     entity_id="OBI:0000008",
    ...     name="Randomized Controlled Trial",
    ...     obi_id="OBI:0000008",
    ...     stato_id="STATO:0000402",
    ...     design_type="interventional",
    ...     evidence_level=1,
    ...     source="obi",
    ...     created_at=datetime.now()
    ... )
**Fields:**

```python
obi_id: Optional[str]
stato_id: Optional[str]
design_type: Optional[str]
description: Optional[str]
evidence_level: Optional[int]
```

## `class StatisticalMethod(BaseEntity)`

Represents a statistical method or test used in analysis.

Uses STATO (Statistics Ontology) to standardize statistical method
classifications. Enables tracking of analytical approaches across studies.

Attributes:
    stato_id: STATO identifier for the statistical method
    method_type: Category of method (hypothesis_test, regression, etc.)
    description: Description of the method
    assumptions: Key assumptions of the method

Example:
    >>> ttest = StatisticalMethod(
    ...     entity_id="STATO:0000288",
    ...     name="Student's t-test",
    ...     stato_id="STATO:0000288",
    ...     method_type="hypothesis_test",
    ...     description="Parametric test comparing means of two groups",
    ...     source="stato",
    ...     created_at=datetime.now()
    ... )
**Fields:**

```python
stato_id: Optional[str]
method_type: Optional[str]
description: Optional[str]
assumptions: List[str]
```

## `class EvidenceLine(BaseEntity)`

Represents a line of evidence using SEPIO framework.

Uses SEPIO (Scientific Evidence and Provenance Information Ontology)
to represent structured evidence chains. Links evidence items to
assertions they support or refute.

Attributes:
    sepio_type: SEPIO evidence line type ID
    eco_type: ECO evidence type ID
    assertion_id: ID of the assertion this evidence supports
    supports_ids: List of hypothesis IDs this evidence supports
    refutes_ids: List of hypothesis IDs this evidence refutes
    evidence_items: List of paper IDs providing evidence
    strength: Evidence strength classification
    provenance_info: Provenance information

Example:
    >>> evidence = EvidenceLine(
    ...     entity_id="EVIDENCE_LINE:olaparib_brca_001",
    ...     name="Clinical evidence for Olaparib in BRCA-mutated breast cancer",
    ...     sepio_type="SEPIO:0000084",
    ...     eco_type="ECO:0007673",
    ...     assertion_id="ASSERTION:olaparib_brca",
    ...     supports_ids=["HYPOTHESIS:parp_inhibitor_synthetic_lethality"],
    ...     evidence_items=["PMC999888", "PMC888777"],
    ...     strength="strong",
    ...     source="extracted",
    ...     created_at=datetime.now()
    ... )
**Fields:**

```python
sepio_type: Optional[str]
eco_type: Optional[str]
assertion_id: Optional[str]
supports_ids: List[str]
refutes_ids: List[str]
evidence_items: List[str]
strength: Optional[str]
provenance_info: Optional[str]
```

## `class Evidence(BaseEntity)`

Evidence for a relationship, treated as a first-class entity.

Evidence entities have immediate canonical ID promotion using format:
{paper_id}:{section}:{paragraph}:{method}

Example canonical ID: "PMC8437152:results:5:llm"

This format enables:
- Immediate promotion (no provisional state needed)
- Efficient lookups by paper/section
- Deduplication across extraction runs
- Database indexing for queries like "all evidence from Section 2"

Attributes:
    entity_id: Canonical ID in format {paper_id}:{section}:{paragraph}:{method}
    paper_id: PMC ID of source paper
    text_span_id: Reference to TextSpan entity (for exact location)
    confidence: Confidence score 0.0-1.0
    extraction_method: Method used (scispacy_ner, llm, table_parser, pattern_match, manual)
    study_type: Type of study (observational, rct, meta_analysis, case_report, review)
    sample_size: Number of subjects in the study
    eco_type: ECO evidence type ID (e.g., "ECO:0007673" for RCT)
    obi_study_design: OBI study design ID (e.g., "OBI:0000008" for RCT)
    stato_methods: List of STATO statistical method IDs used

Schema Rules:
- entity_id MUST follow canonical ID format
- paper_id and text_span_id MUST be non-empty
- Evidence entities are immediately promotable (no usage threshold)

Example:
    >>> evidence = Evidence(
    ...     entity_id="PMC999888:results:3:llm",
    ...     name="Evidence from Olaparib RCT results",
    ...     paper_id="PMC999888",
    ...     text_span_id="PMC999888:results:3",
    ...     confidence=0.92,
    ...     extraction_method=ExtractionMethod.LLM,
    ...     study_type=StudyType.RCT,
    ...     sample_size=302,
    ...     eco_type="ECO:0007673",
    ...     obi_study_design="OBI:0000008",
    ...     stato_methods=["STATO:0000288"],
    ...     source="extracted",
    ...     created_at=datetime.now()
    ... )
**Fields:**

```python
promotable: bool
status: EntityStatus
paper_id: str
text_span_id: str
confidence: float
extraction_method: 'ExtractionMethod'
study_type: 'StudyType'
sample_size: Optional[int]
eco_type: Optional[str]
obi_study_design: Optional[str]
stato_methods: List[str]
```


<span id="user-content-medlitmedlitschemarelationshippy"></span>

# medlit/medlit_schema/relationship.py

Medlit relationship definitions.

## `class EvidenceItem(BaseModel)`

Lightweight evidence reference for relationships.

Attributes:
    paper_id: PMC ID of source paper
    study_type: Type of study (observational, rct, meta_analysis, case_report, review)
    sample_size: Number of subjects in the study
    confidence: Confidence score (0.0-1.0)
**Fields:**

```python
paper_id: str
study_type: str
sample_size: Optional[int]
confidence: float
```

## `class BaseMedicalRelationship(BaseRelationship)`

Base class for all medical relationships with comprehensive provenance tracking.

All medical relationships inherit from this class and include evidence-based
provenance fields to support confidence scoring, contradiction detection,
and temporal tracking of medical knowledge.

Combines lightweight tracking (just paper IDs) with optional rich provenance
(detailed Evidence objects) and quantitative measurements.

Schema Rules:
- Medical assertion relationships MUST have non-empty evidence_ids
- Bibliographic relationships (AuthoredBy, Cites) do NOT require evidence

Attributes:
    subject_id: Entity ID of the subject (source node)
    predicate: Relationship type
    object_id: Entity ID of the object (target node)
    evidence_ids: REQUIRED list of Evidence entity IDs (for medical assertions)
    confidence: Confidence score (0.0-1.0) based on evidence strength
    source_papers: List of PMC IDs supporting this relationship (lightweight)
    evidence_count: Number of papers providing supporting evidence
    contradicted_by: List of PMC IDs with contradicting findings
    first_reported: Date when this relationship was first observed
    last_updated: Date of most recent supporting evidence
    evidence: List of detailed EvidenceItem objects (optional, for rich provenance)
    measurements: List of quantitative measurements (optional)
    properties: Flexible dict for relationship-specific properties

Example (lightweight):
    >>> relationship = Treats(
    ...     subject_id="RxNorm:1187832",
    ...     predicate="TREATS",
    ...     object_id="C0006142",
    ...     evidence_ids=["PMC123:results:5:llm", "PMC456:abstract:2:llm"],
    ...     source_papers=["PMC123", "PMC456"],
    ...     confidence=0.85,
    ...     evidence_count=2,
    ...     response_rate=0.59
    ... )

Example (rich provenance):
    >>> relationship = Treats(
    ...     subject_id="RxNorm:1187832",
    ...     predicate="TREATS",
    ...     object_id="C0006142",
    ...     evidence_ids=["PMC123:results:5:rct"],
    ...     confidence=0.85,
    ...     evidence=[EvidenceItem(paper_id="PMC123", study_type="rct", sample_size=302)],
    ...     measurements=[Measurement(value=0.59, value_type="response_rate")],
    ...     response_rate=0.59
    ... )

### `def BaseMedicalRelationship.evidence_required_for_medical_assertions(cls, v)`

Medical assertion relationships must include evidence.

This validator is overridden in non-medical relationship classes
(like ResearchRelationship) that don't require evidence.

## `class Treats(BaseMedicalRelationship)`

Represents a therapeutic relationship between a drug and a disease.

Direction: Drug → Disease

Attributes:
    efficacy: Effectiveness measure or description
    response_rate: Percentage of patients responding (0.0-1.0)
    line_of_therapy: Treatment sequence (first-line, second-line, etc.)
    indication: Specific approved use or condition

Example:
    >>> treats = Treats(
    ...     subject_id="RxNorm:1187832",  # Olaparib
    ...     object_id="C0006142",  # Breast Cancer
    ...     predicate="TREATS",
    ...     evidence_ids=["PMC999:results:5:rct", "PMC888:abstract:2:rct"],
    ...     efficacy="significant improvement in PFS",
    ...     response_rate=0.59,
    ...     line_of_therapy="second-line",
    ...     indication="BRCA-mutated breast cancer",
    ...     source_papers=["PMC999", "PMC888"],
    ...     confidence=0.85
    ... )

## `class Causes(BaseMedicalRelationship)`

Represents a causal relationship between a disease and a symptom.

Direction: Disease → Symptom (or Gene/Mutation → Disease)

Attributes:
    frequency: How often the symptom occurs (always, often, sometimes, rarely)
    onset: When the symptom typically appears (early, late)
    severity: Typical severity of the symptom (mild, moderate, severe)

Example:
    >>> causes = Causes(
    ...     subject_id="C0006142",  # Breast Cancer
    ...     object_id="C0030193",  # Pain
    ...     predicate="CAUSES",
    ...     evidence_ids=["PMC123:results:3:llm"],
    ...     frequency="often",
    ...     onset="late",
    ...     severity="moderate",
    ...     source_papers=["PMC123"],
    ...     confidence=0.75
    ... )

## `class Prevents(BaseMedicalRelationship)`

Drug prevents disease relationship.

Direction: Drug → Disease

Attributes:
    efficacy: Effectiveness measure or description
    risk_reduction: Risk reduction percentage (0.0-1.0)

## `class IncreasesRisk(BaseMedicalRelationship)`

Represents genetic risk factors for diseases.

Direction: Gene/Mutation → Disease

Attributes:
    risk_ratio: Numeric risk increase (e.g., 2.5 means 2.5x higher risk)
    penetrance: Percentage who develop condition (0.0-1.0)
    age_of_onset: Typical age when disease manifests
    population: Studied population or ethnic group

Example:
    >>> risk = IncreasesRisk(
    ...     subject_id="HGNC:1100",  # BRCA1
    ...     object_id="C0006142",  # Breast Cancer
    ...     predicate="INCREASES_RISK",
    ...     evidence_ids=["PMC123:results:7:llm", "PMC456:discussion:2:llm"],
    ...     risk_ratio=5.0,
    ...     penetrance=0.72,
    ...     age_of_onset="40-50 years",
    ...     population="Ashkenazi Jewish",
    ...     source_papers=["PMC123", "PMC456"],
    ...     confidence=0.92
    ... )

## `class SideEffect(BaseMedicalRelationship)`

Represents adverse effects of medications.

Direction: Drug → Symptom

Attributes:
    frequency: How often it occurs (common, uncommon, rare)
    severity: Severity level (mild, moderate, severe)
    reversible: Whether the side effect resolves after stopping the drug

Example:
    >>> side_effect = SideEffect(
    ...     subject_id="RxNorm:1187832",  # Olaparib
    ...     object_id="C0027497",  # Nausea
    ...     predicate="SIDE_EFFECT",
    ...     evidence_ids=["PMC999:results:8:llm"],
    ...     frequency="common",
    ...     severity="mild",
    ...     reversible=True,
    ...     source_papers=["PMC999"],
    ...     confidence=0.75
    ... )

## `class AssociatedWith(BaseMedicalRelationship)`

Represents a general association between entities.

This is used for relationships where causality is not established but
statistical association exists.

Valid directions:
    - Disease → Disease (comorbidities)
    - Gene → Disease
    - Biomarker → Disease

Attributes:
    association_type: Nature of association (positive, negative, neutral)
    strength: Association strength (strong, moderate, weak)
    statistical_significance: p-value from statistical tests

Example:
    >>> assoc = AssociatedWith(
    ...     subject_id="C0011849",  # Diabetes
    ...     object_id="C0020538",  # Hypertension
    ...     predicate="ASSOCIATED_WITH",
    ...     evidence_ids=["PMC111:results:4:llm"],
    ...     association_type="positive",
    ...     strength="strong",
    ...     statistical_significance=0.001,
    ...     source_papers=["PMC111"],
    ...     confidence=0.80
    ... )

## `class InteractsWith(BaseMedicalRelationship)`

Represents drug-drug interactions.

Direction: Drug ↔ Drug (bidirectional)

Attributes:
    interaction_type: Nature of interaction (synergistic, antagonistic, additive)
    severity: Clinical severity (major, moderate, minor)
    mechanism: Pharmacological mechanism of interaction
    clinical_significance: Description of clinical implications

Example:
    >>> interaction = InteractsWith(
    ...     subject_id="RxNorm:123",  # Warfarin
    ...     object_id="RxNorm:456",  # Aspirin
    ...     predicate="INTERACTS_WITH",
    ...     evidence_ids=["PMC789:discussion:3:llm"],
    ...     interaction_type="synergistic",
    ...     severity="major",
    ...     mechanism="Additive anticoagulant effect",
    ...     clinical_significance="Increased bleeding risk",
    ...     source_papers=["PMC789"],
    ...     confidence=0.90
    ... )

## `class ContraindicatedFor(BaseMedicalRelationship)`

Drug -[CONTRAINDICATED_FOR]-> Disease/Condition

Attributes:
    severity: Contraindication severity (absolute, relative)
    reason: Why contraindicated

## `class DiagnosedBy(BaseMedicalRelationship)`

Represents diagnostic tests or biomarkers used to diagnose a disease.

Direction: Disease → Procedure/Biomarker

Attributes:
    sensitivity: True positive rate (0.0-1.0)
    specificity: True negative rate (0.0-1.0)
    standard_of_care: Whether this is standard clinical practice

Example:
    >>> diagnosis = DiagnosedBy(
    ...     subject_id="C0006142",  # Breast Cancer
    ...     object_id="LOINC:123",  # Mammography
    ...     predicate="DIAGNOSED_BY",
    ...     evidence_ids=["PMC555:methods:2:llm"],
    ...     sensitivity=0.87,
    ...     specificity=0.91,
    ...     standard_of_care=True,
    ...     source_papers=["PMC555"],
    ...     confidence=0.88
    ... )

## `class ParticipatesIn(BaseMedicalRelationship)`

Gene/Protein -[PARTICIPATES_IN]-> Pathway

Attributes:
    role: Function in pathway
    regulatory_effect: Type of regulation (activates, inhibits, modulates)

## `class SubtypeOf(BaseMedicalRelationship)`

When one disease is a subtype of another disease

## `class ResearchRelationship(BaseRelationship)`

Base class for research metadata relationships.

These relationships connect papers, authors, and clinical trials.
Unlike medical relationships, they don't require provenance tracking
since they represent bibliographic metadata rather than medical claims.

Attributes:
    subject_id: ID of the subject entity
    predicate: Relationship type
    object_id: ID of the object entity
    properties: Flexible dict for relationship-specific properties

## `class Cites(ResearchRelationship)`

Represents a citation from one paper to another.

Direction: Paper → Paper (citing → cited)

Attributes:
    context: Section where citation appears
    sentiment: How the citation is used (supports, contradicts, mentions)

## `class StudiedIn(ResearchRelationship)`

Links medical entities to papers that study them.

Direction: Any medical entity → Paper

Attributes:
    role: Importance in the paper (primary_focus, secondary_finding, mentioned)
    section: Where discussed (results, methods, discussion, introduction)

## `class AuthoredBy(ResearchRelationship)`

Paper -[AUTHORED_BY]-> Author

Attributes:
    position: Author position (first, last, corresponding, middle)

## `class PartOf(ResearchRelationship)`

Paper -[PART_OF]-> ClinicalTrial

Attributes:
    publication_type: Type of publication (protocol, results, analysis)

## `class SameAs(ResearchRelationship)`

Provisional identity link between two entities.

Not a BaseMedicalRelationship — no evidence_ids required.
Direction: conventionally lower bundle ID → higher bundle ID.

Attributes:
    confidence: Strength of identity claim (0.0-1.0)
    resolution: Outcome after review ("merged", "distinct", null = unreviewed)
    note: Free text explaining the ambiguity

## `class Indicates(BaseMedicalRelationship)`

Biomarker or test result indicates disease or condition.

Direction: Biomarker / Evidence → Disease

## `class Predicts(BaseMedicalRelationship)`

Represents a hypothesis predicting an observable outcome.

Direction: Hypothesis → Entity (Disease, Outcome, etc.)

Attributes:
    prediction_type: Nature of prediction (positive, negative, conditional)
    conditions: Conditions under which prediction holds
    testable: Whether the prediction is empirically testable

## `class Refutes(BaseMedicalRelationship)`

Represents evidence that refutes a hypothesis.

Direction: Evidence/Paper → Hypothesis

Attributes:
    refutation_strength: Strength of refutation (strong, moderate, weak)
    alternative_explanation: Alternative explanation for observations
    limitations: Limitations of the refuting evidence

## `class TestedBy(BaseMedicalRelationship)`

Represents a hypothesis being tested by a study or clinical trial.

Direction: Hypothesis → Paper/ClinicalTrial

Attributes:
    test_outcome: Result of the test (supported, refuted, inconclusive)
    methodology: Study methodology used
    study_design_id: OBI study design ID

## `class Supports(BaseMedicalRelationship)`

Evidence supports a hypothesis or claim.

Direction: Evidence → Hypothesis

Attributes:
    support_strength: Strength of support (strong, moderate, weak)

## `class Generates(BaseMedicalRelationship)`

Represents a study generating evidence for analysis.

Direction: ClinicalTrial/Paper → Evidence

Attributes:
    evidence_type: Type of evidence generated (experimental, observational, etc.)
    eco_type: ECO evidence type ID
    quality_score: Quality assessment score

### `def create_relationship(predicate: str, subject_id: str, object_id: str, **kwargs) -> BaseRelationship`

Factory function for creating typed relationship instances.

Provides type-safe relationship creation with predicate validation.
Returns the appropriate relationship subclass based on predicate.

Args:
    predicate: Relationship type (must match RELATIONSHIP_TYPE_MAP keys)
    subject_id: Entity ID of the subject
    object_id: Entity ID of the object
    **kwargs: Relationship-specific fields (evidence_ids, confidence, etc.)

Returns:
    Typed relationship instance (Treats, Causes, Cites, etc.)

Raises:
    ValueError: If predicate is not recognized

Example:
    >>> rel = create_relationship(
    ...     predicate="TREATS",
    ...     subject_id="RxNorm:1187832",
    ...     object_id="C0006142",
    ...     evidence_ids=["PMC123:results:5:rct"],
    ...     response_rate=0.59,
    ...     confidence=0.85
    ... )
    >>> isinstance(rel, Treats)
    True


<span id="user-content-medlitpipelinepy"></span>

# medlit/pipeline.py

MedlitPipeline: top-level IngestPipeline implementation for medlit.

Implements the IngestPipeline ABC (or ducks as one if the interface package
is not installed) by delegating to the medlit pipeline scripts.

> MedlitPipeline: top-level IngestPipeline implementation for medlit.

Implements the IngestPipeline ABC (or ducks as one if the interface package
is not installed) by delegating to the medlit pipeline scripts.


## `class MedlitPipeline(IngestPipeline)`

End-to-end medlit knowledge-graph ingestion pipeline.

Orchestrates fetch_vocab → extract → ingest → build_bundle stages
for medical-literature papers in JATS-XML or pre-parsed JSON format.

### `def MedlitPipeline.get_entity_type_specs(self) -> dict[str, Any]`

Return entity type specifications from the medlit domain spec.

### `def MedlitPipeline.fetch_vocab(self, input_dir: Path, output_dir: Path, llm_backend: str = 'anthropic', papers: Optional[list[str]] = None, limit: Optional[int] = None) -> None`

Extract vocabulary from papers and write vocab.json + seeded_synonym_cache.json.

Args:
    input_dir: Directory containing paper XML/JSON files.
    output_dir: Output directory for vocab.json and seeded_synonym_cache.json.
    llm_backend: LLM backend to use ("anthropic", "openai", or "ollama").
    papers: Optional list of glob patterns to filter input files.
    limit: Optional maximum number of papers to process.

### `def MedlitPipeline.extract(self, input_dir: Path, output_dir: Path, llm_backend: str = 'anthropic', papers: Optional[list[str]] = None, limit: Optional[int] = None, vocab_dir: Optional[Path] = None) -> None`

Run Pass 1 + Pass 2 extraction and write per-paper bundle JSON files.

Args:
    input_dir: Directory containing paper XML/JSON files.
    output_dir: Output directory for paper_*.json bundle files.
    llm_backend: LLM backend to use.
    papers: Optional list of glob patterns to filter input files.
    limit: Optional maximum number of papers to process.
    vocab_dir: Optional path to vocab.json / seeded_synonym_cache.json.

### `def MedlitPipeline.run_ingest(self, bundle_dir: Path, output_dir: Path, synonym_cache_path: Optional[Path] = None, canonical_id_cache_path: Optional[Path] = None, similarity_threshold: float = 0.88) -> dict[str, Any]`

Deduplicate and promote entities/relationships from per-paper bundles.

Args:
    bundle_dir: Directory containing paper_*.json bundle files.
    output_dir: Output directory for merged entities.json and relationships.json.
    synonym_cache_path: Optional path to synonym cache file.
    canonical_id_cache_path: Optional path to canonical ID lookup cache.
    similarity_threshold: Min cosine similarity for embedding-based merge.

Returns:
    Result dict with entities_count, relationships_count, and output paths.

### `def MedlitPipeline.build_bundle(self, merged_dir: Path, bundles_dir: Path, output_dir: Path, pmc_xmls_dir: Optional[Path] = None) -> dict[str, Any]`

Build kgbundle from merged ingest output and per-paper bundles.

Args:
    merged_dir: ingest output directory (entities.json, relationships.json, id_map.json).
    bundles_dir: Directory containing paper_*.json bundle files.
    output_dir: Output directory in kgbundle format.
    pmc_xmls_dir: Optional directory of JATS-XML sources to copy into output.

Returns:
    Summary dict with entity_count, relationship_count, evidence_count, manifest_path.


<span id="user-content-medlittestsinitpy"></span>

# medlit/tests/__init__.py

Tests for the medlit example application.


<span id="user-content-medlittestsconftestpy"></span>

# medlit/tests/conftest.py

Conftest for medlit tests — provides shared fixtures.

### `def entity_storage() -> InMemoryEntityStorage`

Provide a fresh in-memory entity storage instance.

### `def relationship_storage() -> InMemoryRelationshipStorage`

Provide a fresh in-memory relationship storage instance.

### `def document_storage() -> InMemoryDocumentStorage`

Provide a fresh in-memory document storage instance.


<span id="user-content-medlitteststestauthoritylookuppy"></span>

# medlit/tests/test_authority_lookup.py

Tests for canonical ID authority lookup.

Tests the matching logic for DBPedia and other ontology lookups,
and UMLS type validation (validate_umls_type).

> Tests for canonical ID authority lookup.

Tests the matching logic for DBPedia and other ontology lookups,
and UMLS type validation (validate_umls_type).


## `class TestDBPediaLabelMatching`

Test the DBPedia label matching logic.

### `def TestDBPediaLabelMatching.lookup(self)`

Create a CanonicalIdLookup instance for testing.

### `def TestDBPediaLabelMatching.test_exact_match(self, lookup)`

Exact match should succeed.

### `def TestDBPediaLabelMatching.test_term_contained_in_label(self, lookup)`

Term contained in label should succeed.

### `def TestDBPediaLabelMatching.test_label_contained_in_term(self, lookup)`

Label contained in term should succeed.

### `def TestDBPediaLabelMatching.test_label_starts_with_term(self, lookup)`

Label starting with term should succeed.

### `def TestDBPediaLabelMatching.test_common_prefix_singular_plural(self, lookup)`

Common 6-char prefix should succeed (handles singular/plural).

### `def TestDBPediaLabelMatching.test_html_tags_stripped(self, lookup)`

HTML bold tags should be stripped from labels.

### `def TestDBPediaLabelMatching.test_case_insensitive(self, lookup)`

Matching should be case-insensitive.

### `def TestDBPediaLabelMatching.test_garbage_match_insect(self, lookup)`

Garbage match 'HER2-enriched' → 'Insect' should fail.

### `def TestDBPediaLabelMatching.test_garbage_match_animal(self, lookup)`

Garbage match 'basal-like' → 'Animal' should fail.

### `def TestDBPediaLabelMatching.test_unrelated_terms(self, lookup)`

Completely unrelated terms should fail.

### `def TestDBPediaLabelMatching.test_substring_match_allowed(self, lookup)`

Substring matching is allowed (term in label).

### `def TestDBPediaLabelMatching.test_no_overlap_fails(self, lookup)`

Terms with no overlap should fail.

## `class TestMeSHTermNormalization`

Test MeSH term normalization (cancer → neoplasms).

### `def TestMeSHTermNormalization.lookup(self)`

Create a CanonicalIdLookup instance for testing.

### `def TestMeSHTermNormalization.test_mesh_id_extraction(self, lookup)`

Test extracting MeSH ID from API results.

### `def TestMeSHTermNormalization.test_mesh_id_extraction_word_order(self, lookup)`

Test MeSH extraction handles word order differences.

### `def TestMeSHTermNormalization.test_mesh_id_extraction_no_match(self, lookup)`

Test MeSH extraction returns None for no match.

### `def TestMeSHTermNormalization.test_mesh_id_extraction_empty_data(self, lookup)`

Test MeSH extraction handles empty data.

### `def TestMeSHTermNormalization.test_mesh_id_extraction_prefers_general_over_complication(self, lookup)`

Test that general terms are preferred over complications.

"breast cancer" should match "Breast Neoplasms" (D001943)
rather than "Breast Cancer Lymphedema" (D000072656).

### `def TestMeSHTermNormalization.test_mesh_id_extraction_exact_match_priority(self, lookup)`

Test that exact matches get highest priority.

## `class TestValidateUmlsType`

Test validate_umls_type with injected semantic type mapping (no live API).

### `def TestValidateUmlsType.test_cortisol_gene_misclassified_returns_correction(self)`

Cortisol (C0020268) as hormone/drug; assigned type 'gene' should return (False, correct_type).

### `def TestValidateUmlsType.test_pasireotide_drug_compatible_returns_ok(self)`

Pasireotide (or any CUI) mapped to Pharmacologic Substance with type drug returns (True, None).

### `def TestValidateUmlsType.test_unknown_cui_returns_ok_no_correction(self)`

Unknown CUI (not in override, or empty override) returns (True, None).

### `def TestValidateUmlsType.test_cache_reused(self)`

Results are cached when _cache dict is passed; second call does not recompute.

### `def TestValidateUmlsType.test_ambiguous_multiple_allowed_returns_false_none(self)`

When UMLS maps to multiple allowed types (e.g. drug or biomarker), return (False, None).


<span id="user-content-medlitteststestbuildbundlepy"></span>

# medlit/tests/test_build_bundle.py

Tests for build_bundle (merged + extracted -> kgbundle).

### `def minimal_merged_dir(tmp_path)`

Minimal merged dir: entities.json, relationships.json, id_map.json, synonym_cache.json.

### `def minimal_bundles_dir(tmp_path)`

Minimal bundles dir: one paper_*.json with one relationship and matching evidence_entity.

### `def test_run_build_bundle_produces_bundle_files(minimal_merged_dir, minimal_bundles_dir, tmp_path)`

run_build_bundle writes entities.jsonl, relationships.jsonl, evidence.jsonl, mentions.jsonl, manifest.json.

### `def test_entity_row_has_usage_and_status(minimal_merged_dir, minimal_bundles_dir, tmp_path)`

EntityRow in entities.jsonl has entity_id, status, usage_count/total_mentions from bundle scan.

### `def test_first_seen_section_populated_from_evidence_id(minimal_merged_dir, minimal_bundles_dir, tmp_path)`

first_seen_section is parsed from evidence_id (format paper_id:section:paragraph_idx:method).

### `def test_relationship_row_includes_provenance_in_properties(minimal_merged_dir, minimal_bundles_dir, tmp_path)`

When merged relationships have provenance, Pass 3 emits it in properties.

### `def test_evidence_row_relationship_key_uses_merge_keys(minimal_merged_dir, minimal_bundles_dir, tmp_path)`

EvidenceRow relationship_key uses merge keys (from id_map), not local ids.

### `def test_run_build_bundle_raises_when_id_map_missing(tmp_path, minimal_bundles_dir)`

If id_map.json is missing in merged_dir, run_build_bundle raises FileNotFoundError.

### `def test_load_merged_output_requires_id_map(tmp_path)`

load_merged_output raises FileNotFoundError when id_map.json is missing.

### `def test_load_extracted_bundles(minimal_bundles_dir)`

load_extracted_bundles returns list of (paper_id, PerPaperBundle).

### `def test_provenance_denylist_excludes_pmc_placeholder(tmp_path)`

Entities with only PMC_PLACEHOLDER in relationships get usage_count 0, first_seen_document None.

### `def test_provenance_denylist_excludes_pmc_id_not_provided(tmp_path)`

Entities with only PMC_ID_NOT_PROVIDED in relationships get usage_count 0, first_seen_document None.

### `def test_provenance_denylist_excludes_pmc_unknown(tmp_path)`

Entities with only PMC_UNKNOWN in supporting_documents get usage_count 0.

### `def test_zero_mention_orphan_dropped(tmp_path)`

Entity in relationship but with no evidence_ids gets usage_count 0 and is dropped.

### `def test_provenance_derived_entities_retained(tmp_path)`

Paper, Author, Institution from provenance_expansion (no evidence_ids) get usage_count and are retained.

### `def test_run_build_bundle_copies_sources_when_pmc_xmls_dir_provided(tmp_path)`

When --pmc-xmls-dir is provided, copy XML files into output_dir/sources/.


<span id="user-content-medlitteststestdeduppy"></span>

# medlit/tests/test_dedup.py

Tests for ingest dedup: synonym indexing, namespace normalization, reconciliation.

### `def test_synonym_indexing_merges_name_to_synonym(tmp_path)`

Entity A has synonym X; entity B has name X (same class) -> merge to one canonical.

### `def test_synonym_indexing_does_not_merge_different_classes(tmp_path)`

Same name/synonym but different entity_class -> do not merge.

### `def test_spelling_normalization_merges_hyperglycaemia_hyperglycemia(tmp_path)`

British/American spelling variants (hyperglycaemia/hyperglycemia) merge to one canonical.

### `def test_preferred_authoritative_id_prefers_hgnc_for_gene()`

When Gene has both umls_id and hgnc_id, prefer hgnc_id.

### `def test_preferred_authoritative_id_returns_umls_when_only_umls()`

When Gene has only umls_id, return umls_id (no lookup without lookup object).

### `def test_is_authoritative_id()`

_is_authoritative_id correctly identifies authoritative vs prov- slugs.

### `def test_canonical_id_slug_format()`

_canonical_id_slug produces prov- prefixed hex.


<span id="user-content-medlitteststestentitynormalizationpy"></span>

# medlit/tests/test_entity_normalization.py

Tests for entity type normalization in MedLitEntityExtractor.

Tests the _normalize_entity_type() method which handles:
- Pipe-separated types from LLM output
- Common LLM mistakes (test → procedure)
- Invalid type filtering

> Tests for entity type normalization in MedLitEntityExtractor.

Tests the _normalize_entity_type() method which handles:
- Pipe-separated types from LLM output
- Common LLM mistakes (test → procedure)
- Invalid type filtering


## `class TestTypeNormalizationWithDomain`

Test entity type normalization with domain schema validation.

### `def TestTypeNormalizationWithDomain.extractor(self)`

Create extractor with domain for full validation.

### `def TestTypeNormalizationWithDomain.test_valid_type_passes_through(self, extractor)`

Valid entity types should pass through unchanged.

### `def TestTypeNormalizationWithDomain.test_case_normalization(self, extractor)`

Types should be normalized to lowercase.

### `def TestTypeNormalizationWithDomain.test_whitespace_stripped(self, extractor)`

Whitespace should be stripped from types.

### `def TestTypeNormalizationWithDomain.test_pipe_separated_takes_first_valid(self, extractor)`

Pipe-separated types should return first valid type.

### `def TestTypeNormalizationWithDomain.test_pipe_separated_skips_invalid(self, extractor)`

Pipe-separated types should skip invalid types.

### `def TestTypeNormalizationWithDomain.test_pipe_separated_all_invalid_returns_none(self, extractor)`

Pipe-separated with all invalid types should return None.

### `def TestTypeNormalizationWithDomain.test_common_mistake_test_to_procedure(self, extractor)`

'test' should be normalized to 'procedure'.

### `def TestTypeNormalizationWithDomain.test_common_mistake_diagnostic_to_procedure(self, extractor)`

'diagnostic' should be normalized to 'procedure'.

### `def TestTypeNormalizationWithDomain.test_common_mistake_imaging_to_procedure(self, extractor)`

'imaging' should be normalized to 'procedure'.

### `def TestTypeNormalizationWithDomain.test_common_mistake_assay_to_biomarker(self, extractor)`

'assay' should be normalized to 'biomarker'.

### `def TestTypeNormalizationWithDomain.test_common_mistake_marker_to_biomarker(self, extractor)`

'marker' should be normalized to 'biomarker'.

### `def TestTypeNormalizationWithDomain.test_skip_system_type(self, extractor)`

'system' should be skipped (returns None).

### `def TestTypeNormalizationWithDomain.test_skip_organization_type(self, extractor)`

'organization' should be skipped (returns None).

### `def TestTypeNormalizationWithDomain.test_invalid_type_returns_none(self, extractor)`

Unknown types should return None.

## `class TestTypeNormalizationWithoutDomain`

Test entity type normalization without domain (basic mode).

### `def TestTypeNormalizationWithoutDomain.extractor(self)`

Create extractor without domain for basic normalization.

### `def TestTypeNormalizationWithoutDomain.test_basic_type_passes_through(self, extractor)`

Types pass through in basic mode (no validation).

### `def TestTypeNormalizationWithoutDomain.test_basic_pipe_takes_first(self, extractor)`

Pipe-separated takes first part in basic mode.

### `def TestTypeNormalizationWithoutDomain.test_basic_mapping_applied(self, extractor)`

TYPE_MAPPING is still applied in basic mode.

## `class TestTypeMappingConstants`

Test the TYPE_MAPPING constant has expected entries.

### `def TestTypeMappingConstants.test_procedure_mappings_exist(self)`

Procedure mappings should exist.

### `def TestTypeMappingConstants.test_biomarker_mappings_exist(self)`

Biomarker mappings should exist.

### `def TestTypeMappingConstants.test_skip_mappings_exist(self)`

Skip mappings (None values) should exist.

## `class TestTypeMasqueradingAsName`

Reject entity names that are actually type labels (e.g. LLM returns entity='disease', type='disease').

### `def TestTypeMasqueradingAsName.test_name_equals_type_rejected(self)`

When name equals type, treat as type masquerading as name.

### `def TestTypeMasqueradingAsName.test_known_type_labels_rejected_as_name(self)`

Known type labels must not be used as entity names.

### `def TestTypeMasqueradingAsName.test_real_entity_names_allowed(self)`

Real entity names should not be rejected.

### `def TestTypeMasqueradingAsName.test_empty_name_rejected(self)`

Empty or whitespace-only name is rejected.

### `async def TestTypeMasqueradingAsName.test_pre_extracted_type_as_name_dropped(self)`

Pre-extracted entities with name=type (e.g. name='disease', type='disease') produce no mention.


<span id="user-content-medlitteststestextractpy"></span>

# medlit/tests/test_extract.py

Unit tests for extract helpers: vocab-in-prompt and type normalization.

## `class TestNormalizeEntityType`

Test raw LLM type string -> bundle class (PascalCase).

### `def TestNormalizeEntityType.test_biological_process_to_biological_process(self)`

'biological process' (with space) normalizes to BiologicalProcess.

### `def TestNormalizeEntityType.test_gene_to_gene(self)`

'gene' -> Gene.

### `def TestNormalizeEntityType.test_disease_lowercase(self)`

'disease' -> Disease.

### `def TestNormalizeEntityType.test_hormone_and_enzyme(self)`

PLAN3: hormone -> Hormone, enzyme -> Enzyme.

### `def TestNormalizeEntityType.test_biological_process_underscore(self)`

'biological_process' -> BiologicalProcess.

### `def TestNormalizeEntityType.test_unknown_maps_to_other(self)`

Unknown type maps to Other.

### `def TestNormalizeEntityType.test_whitespace_stripped(self)`

Whitespace is stripped before mapping.

## `class TestBuildSystemPromptWithVocab`

Test that vocab section is appended when vocab_entries provided.

### `def TestBuildSystemPromptWithVocab.test_empty_vocab_returns_base(self)`

None or empty vocab returns base prompt without vocab section.

### `def TestBuildSystemPromptWithVocab.test_vocab_entries_included_in_prompt(self)`

Short vocab list is included in the prompt with names and types.

## `class TestFixEvidencePaperId`

Replace LLM placeholder paper IDs in evidence with actual paper_id.

### `def TestFixEvidencePaperId.test_pmc_unknown_replaced(self)`

PMC_UNKNOWN in evidence ID is replaced with actual paper_id.

### `def TestFixEvidencePaperId.test_paper_id_literal_replaced(self)`

'paper_id' literal is replaced.

### `def TestFixEvidencePaperId.test_real_paper_id_unchanged(self)`

Real paper IDs are left as-is.

### `def TestFixEvidencePaperId.test_no_colon_unchanged(self)`

Evidence IDs without colon are returned unchanged.

### `def TestFixEvidencePaperId.test_pmc11000000_replaced(self)`

PMC11000000 placeholder is replaced.

### `def TestFixEvidencePaperId.test_current_paper_replaced(self)`

==CURRENT_PAPER== placeholder is replaced.

### `def TestFixEvidencePaperId.test_hallucinated_pmc_replaced(self)`

PMC ID from citation/hallucination (not current paper) is replaced.

### `def TestFixEvidencePaperId.test_current_paper_unchanged(self)`

Evidence with correct current paper_id is left as-is.

## `class TestReplaceCurrentPaperInBundle`

Global replace of ==CURRENT_PAPER== in raw bundle before parsing.

### `def TestReplaceCurrentPaperInBundle.test_replaces_in_evidence_ids(self)`

==CURRENT_PAPER== in evidence_entities and relationships is replaced.

### `def TestReplaceCurrentPaperInBundle.test_leaves_other_strings_unchanged(self)`

Strings without ==CURRENT_PAPER== are unchanged.


<span id="user-content-medlitteststestnerextractorpy"></span>

# medlit/tests/test_ner_extractor.py

Tests for NER-based entity extraction (PLAN3).

## `class TestNormalizeEntityGroup`

Test label normalization for NER pipeline output.

## `class TestLabelMapping`

Test default label -> medlit type mapping.

## `class TestChunkText`

Test long-document chunking.

## `class TestGetDocumentText`

Test document text extraction.

## `class TestMedLitNEREntityExtractorWithMock`

Test NER extractor with a mock pipeline (no real model load).

### `def TestMedLitNEREntityExtractorWithMock.mock_pipeline(self)`

Pipeline that returns fixed entities for testing.

### `async def TestMedLitNEREntityExtractorWithMock.test_type_as_name_filtered_out(self, mock_pipeline)`

When mock returns entity with word 'disease' (type label), it should be filtered out.

## `class TestMedLitNEREntityExtractorImportError`

Test that NER extractor raises clear ImportError when transformers not installed.

### `def TestMedLitNEREntityExtractorImportError.test_instantiation_without_pipeline_raises_import_error_when_no_transformers(self)`

When transformers is not installed, constructing without pipeline= raises ImportError.


<span id="user-content-medlitteststestpromotionlookuppy"></span>

# medlit/tests/test_promotion_lookup.py

Tests for promotion with canonical ID lookup service integration.

Tests that verify the lookup parameter is correctly passed through the promotion chain:
- run_promotion(lookup=...) → get_promotion_policy(lookup=...) → MedLitPromotionPolicy(lookup=...)

> Tests for promotion with canonical ID lookup service integration.

Tests that verify the lookup parameter is correctly passed through the promotion chain:
- run_promotion(lookup=...) → get_promotion_policy(lookup=...) → MedLitPromotionPolicy(lookup=...)


### `async def medlit_orchestrator(entity_storage: InMemoryEntityStorage, relationship_storage: InMemoryRelationshipStorage, document_storage: InMemoryDocumentStorage)`

Create orchestrator with MedLit domain for promotion testing.

### `def mock_lookup()`

Create a mock CanonicalIdLookupInterface for testing.

## `class TestPromotionLookupIntegration`

Test that lookup service is passed through the promotion chain.

### `async def TestPromotionLookupIntegration.test_get_promotion_policy_accepts_lookup_parameter(self, medlit_orchestrator: IngestionOrchestrator, mock_lookup: MagicMock)`

get_promotion_policy accepts lookup parameter and passes it to policy.

### `async def TestPromotionLookupIntegration.test_get_promotion_policy_works_without_lookup(self, medlit_orchestrator: IngestionOrchestrator)`

get_promotion_policy works when lookup is None (creates new instance).

### `async def TestPromotionLookupIntegration.test_run_promotion_passes_lookup_to_policy(self, medlit_orchestrator: IngestionOrchestrator, entity_storage: InMemoryEntityStorage, mock_lookup: MagicMock)`

run_promotion passes lookup parameter through to get_promotion_policy.

### `async def TestPromotionLookupIntegration.test_promotion_uses_provided_lookup_service(self, medlit_orchestrator: IngestionOrchestrator, entity_storage: InMemoryEntityStorage, mock_lookup: MagicMock)`

Promotion uses the provided lookup service when assigning canonical IDs.


<span id="user-content-medlitteststestprovenanceexpansionpy"></span>

# medlit/tests/test_provenance_expansion.py

Tests for provenance expansion (Author, Institution, Paper, derived relationships).

### `def test_canonicalize_symmetric() -> None`

canonicalize_symmetric returns (min, max) for deterministic storage.

### `def test_expand_provenance_creates_author_institution_paper() -> None`

expand_provenance produces Author, Institution, Paper entities and derived relationships.

### `def test_expand_provenance_described_top_two_by_relationship_count() -> None`

DESCRIBED is limited to top 2 domain entities by relationship count.

### `def test_expand_provenance_skips_author_institution_evidence() -> None`

DESCRIBED excludes Author, Institution, Evidence; only domain entities considered.


<span id="user-content-medlitteststesttwopassingestionpy"></span>

# medlit/tests/test_two_pass_ingestion.py

Integration test for ingest (dedup) using pre-baked fixture bundles.

Uses fixture JSONs only; no live LLM calls. extract is tested separately
(manual run or --dry-run / mocked LLM).

> Integration test for ingest (dedup) using pre-baked fixture bundles.

Uses fixture JSONs only; no live LLM calls. extract is tested separately
(manual run or --dry-run / mocked LLM).


### `def fixture_bundle_dir(tmp_path)`

Copy fixture bundles to a temp dir so ingest can read them.

### `def test_pass2_merges_same_name_class(fixture_bundle_dir, tmp_path)`

Entities with same (name, class) across papers get the same canonical_id.

### `def test_pass2_writes_synonym_cache(fixture_bundle_dir, tmp_path)`

Pass 2 writes synonym_cache.json.

### `def test_pass2_does_not_modify_input_bundles(fixture_bundle_dir, tmp_path)`

Original bundle files are not modified (read-only).

### `def test_pass2_writes_id_map(fixture_bundle_dir, tmp_path)`

Pass 2 writes id_map.json so Pass 3 can resolve (paper_id, local_id) -> merge_key.

### `def test_pass2_accumulates_relationship_sources(fixture_bundle_dir, tmp_path)`

Merged relationships aggregate source_papers and evidence_ids.

### `def test_pass2_accumulates_provenance_from_evidence(fixture_bundle_dir, tmp_path)`

Merged relationships have provenance built from evidence_entities (section, sentence).

### `def test_fixture_bundles_load(fixture_bundle_dir)`

Fixture bundles are valid PerPaperBundle.

### `def test_is_authoritative_id()`

_is_authoritative_id returns True for ontology IDs, False for synthetic slugs.

### `def test_pass2_output_has_entity_id_and_canonical_id_null_when_synthetic(fixture_bundle_dir, tmp_path)`

Pass 2 output entities have entity_id (merge key) and canonical_id null when synthetic.

### `def test_pass2_swaps_backwards_treats_relationship(tmp_path)`

Backwards (disease, treats, drug) from Pass 1 LLM is corrected to (drug, treats, disease).

### `def test_pass2_authoritative_id_from_bundle_preserved(tmp_path)`

When a bundle entity has umls_id (or other authoritative ID), Pass 2 uses it as entity_id and canonical_id.


<span id="user-content-procpy"></span>

# proc.py

Poor man's literate programming preprocessor.

Processes a Python file in source order, emitting:
  - Top-level string literals verbatim as markdown
  - Markdown summaries (signature + docstring) for top-level functions and classes

Example usage:
$ docker run -it --rm -v "$(pwd):/work" python:3.13-bookworm     python3 /work/proc.py /work/example.py > example.md

> 
Poor man's literate programming preprocessor.

Processes a Python file in source order, emitting:
  - Top-level string literals verbatim as markdown
  - Markdown summaries (signature + docstring) for top-level functions and classes

Example usage:
$ docker run -it --rm -v "$(pwd):/work" python:3.13-bookworm     python3 /work/proc.py /work/example.py > example.md



<span id="user-content-scriptsbuildcodereferencepy"></span>

# scripts/build_code_reference.py

Build MkDocs-ready code-reference markdown from Python source files.


<span id="user-content-sherlockreadmemd"></span>

# sherlock/README.md

# Sherlock Holmes Knowledge Graph Pipeline

Dense typed knowledge graph extraction from "A Scandal in Bohemia" (Arthur Conan Doyle, 1891).

## Overview

This package builds a rich, entity-typed knowledge graph from the Sherlock Holmes story
"A Scandal in Bohemia" using LLM-driven extraction — the same approach that made the
`medlit` pipeline produce dense graphs (many entity types, semantically specific predicates)
rather than sparse co-occurrence graphs.

    ...

<span id="user-content-sherlocksherlockinitpy"></span>

# sherlock/sherlock/__init__.py

Sherlock Holmes knowledge graph pipeline.

Dense typed extraction from "A Scandal in Bohemia" and other Holmes stories.
Follows the medlit pattern: domain_spec.py as single source of truth,
LLM-based extraction, dedup/merge, kgbundle output.

> Sherlock Holmes knowledge graph pipeline.

Dense typed extraction from "A Scandal in Bohemia" and other Holmes stories.
Follows the medlit pattern: domain_spec.py as single source of truth,
LLM-based extraction, dedup/merge, kgbundle output.



<span id="user-content-sherlocksherlockbundlemodelspy"></span>

# sherlock/sherlock/bundle_models.py

Pydantic models for the per-story bundle JSON (Pass 1 output / Pass 2 input).

Mirrors medlit's bundle_models.py but adapted for fiction:
- StoryInfo instead of PaperInfo
- NarratorTrust and story_time fields on RelationshipRow (Sherlock-specific epistemic metadata)
- Evidence IDs use {story_id}:{section}:{paragraph_idx}:{method}

> Pydantic models for the per-story bundle JSON (Pass 1 output / Pass 2 input).

Mirrors medlit's bundle_models.py but adapted for fiction:
- StoryInfo instead of PaperInfo
- NarratorTrust and story_time fields on RelationshipRow (Sherlock-specific epistemic metadata)
- Evidence IDs use {story_id}:{section}:{paragraph_idx}:{method}


## `class StoryInfo(BaseModel)`

Metadata for a Sherlock Holmes story.
**Fields:**

```python
story_id: str
title: str
collection: Optional[str]
author: str
year: Optional[int]
source_uri: Optional[str]
document_id: str
```

## `class ExtractedEntityRow(BaseModel)`

Minimal entity record in the story bundle. JSON key 'class' via alias.
**Fields:**

```python
id: str
entity_class: str
name: str
synonyms: list[str]
canonical_id: Optional[str]
source: Literal['extracted', 'curated']
description: Optional[str]
```

## `class EvidenceEntityRow(BaseModel)`

Evidence entity in the story bundle.

id format: {story_id}:{section}:{paragraph_idx}:{method}
**Fields:**

```python
id: str
entity_class: Literal['Evidence']
entity_id: Optional[str]
story_id: str
section: Optional[str]
paragraph_idx: Optional[int]
text: Optional[str]
confidence: float
extraction_method: str
source: Literal['extracted']
```

## `class ProvenanceEntry(BaseModel)`

One provenance record for a relationship.
**Fields:**

```python
section: Optional[str]
sentence: Optional[str]
paragraph_idx: Optional[int]
```

## `class RelationshipRow(BaseModel)`

One relationship in the story bundle.
**Fields:**

```python
subject: str
predicate: str
object_id: str
evidence_ids: list[str]
provenance: list[ProvenanceEntry]
source_stories: list[str]
confidence: float
narrator_trust: Optional[NarratorTrustLiteral]
story_time: Optional[StoryTimeLiteral]
narrative_position: Optional[int]
known_by: Optional[list[str]]
properties: dict[str, Any]
section: Optional[str]
asserted_by: str
resolution: Optional[Literal['merged', 'distinct']]
note: Optional[str]
```

## `class PerStoryBundle(BaseModel)`

Per-story bundle: Pass 1 output and Pass 2 input.
**Fields:**

```python
story: StoryInfo
entities: list[ExtractedEntityRow]
evidence_entities: list[EvidenceEntityRow]
relationships: list[RelationshipRow]
notes: list[str]
```

### `def PerStoryBundle.to_bundle_dict(self) -> dict`

Serialize for JSON with alias 'class' used for entity type.

### `def PerStoryBundle.from_bundle_dict(cls, data: dict) -> 'PerStoryBundle'`

Load from dict/JSON (accepts key 'class' for entity type).


<span id="user-content-sherlocksherlockdocumentspy"></span>

# sherlock/sherlock/documents.py

Sherlock Holmes story document representation.

## `class SherlockStory(BaseDocument)`

A Sherlock Holmes short story or novel as a source document for extraction.

The story is split into paragraphs by the parser; each paragraph becomes
an evidence entity with a stable index.

Fields:
    collection: The collection title (e.g. 'Adventures of Sherlock Holmes').
    story_slug: Short identifier used in evidence IDs (e.g. 'scandal_in_bohemia').
    author: Typically 'Arthur Conan Doyle'.
    year: Publication year.

### `def SherlockStory.get_sections(self) -> list[tuple[str, str]]`

Return story as a single 'body' section.


<span id="user-content-sherlocksherlockdomainpy"></span>

# sherlock/sherlock/domain.py

Domain schema for Sherlock Holmes knowledge graph.

## `class SherlockDomainSchema(DomainSchema)`

Domain schema for Sherlock Holmes fiction extraction.

Defines entity types, predicates, and validation rules for extracting
a dense typed knowledge graph from Holmes stories.

Key design choices:
- No external authority APIs: canonical IDs from curated DBPedia map + synthetic scheme
- All entities promoted immediately (fiction = no provisional/canonical gap)
- Rich predicate vocabulary (28 predicates vs. 3 generic ones in old approach)
- NarratorTrust and story_time metadata on every relationship

### `def SherlockDomainSchema.normalize_mention(self, mention: str) -> str`

Normalize character mention for dedup (lowercase, strip, common alias expansion).

### `def SherlockDomainSchema.preferred_entity(self, candidates: list[BaseEntity]) -> BaseEntity`

Select merge survivor: prefer canonical, then curated, then higher usage.


<span id="user-content-sherlocksherlockdomainspecpy"></span>

# sherlock/sherlock/domain_spec.py

Domain spec for Sherlock Holmes knowledge graph extraction.

Single source of truth for entity types, predicates, evidence, and mentions.
Follows the medlit pattern: consumers import from this module.

Design goals:
- Rich typed schema (not just generic co_occurs_with) → dense graph
- Epistemic metadata: narrator trust, narrative position, story time
- Strong predicate constraints → semantically specific edges
- Alias/coreference handling via SAME_AS → merged canonical nodes

> Domain spec for Sherlock Holmes knowledge graph extraction.

Single source of truth for entity types, predicates, evidence, and mentions.
Follows the medlit pattern: consumers import from this module.

Design goals:
- Rich typed schema (not just generic co_occurs_with) → dense graph
- Epistemic metadata: narrator trust, narrative position, story time
- Strong predicate constraints → semantically specific edges
- Alias/coreference handling via SAME_AS → merged canonical nodes


## `class NarratorTrust(str, Enum)`

Epistemic source/reliability of an assertion in the narrative.

In fiction, all assertions have an epistemic source. Watson narrates
retrospectively, Holmes deduces, characters speak and act. This enum
captures *who* asserts a fact and *how reliably*, so the graph can be
filtered to e.g. only Holmes-inference edges for "solve the case" queries.

## `class CharacterEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class LocationEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class StoryEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class PhysicalObjectEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class EventEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class OccupationEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

## `class OrganizationEntity(BaseEntity)`


**Fields:**

```python
spec: ClassVar[EntitySpec]
```

### `def _entity_class_matches_type(cls: type, entity_type: str) -> bool`

Return True if an entity class's type string matches entity_type.

### `def get_valid_predicates(subject_type: str, object_type: str) -> list[str]`

Return predicates valid between two entity types.

Checks each predicate's subject_types/object_types constraints.
When a predicate has None constraints it accepts any type.

### `def make_canonical_id(entity_type: str, safe_name: str, story_slug: Optional[str] = None) -> str`

Build a stable canonical ID for a Sherlock entity.

Args:
    entity_type: One of the entity type strings from domain_spec.
    safe_name: Name with spaces/special chars removed (PascalCase recommended).
    story_slug: Short story identifier, e.g. 'scandal'. Required for per-story types.


<span id="user-content-sherlocksherlockentitiespy"></span>

# sherlock/sherlock/entities.py

Sherlock Holmes entity types.

All entity classes import their spec from domain_spec.py (single source of truth).
They are re-exported here for convenience.

> Sherlock Holmes entity types.

All entity classes import their spec from domain_spec.py (single source of truth).
They are re-exported here for convenience.



<span id="user-content-sherlocksherlockpipelineinitpy"></span>

# sherlock/sherlock/pipeline/__init__.py

Sherlock Holmes pipeline package.


<span id="user-content-sherlocksherlockpipelinebundlebuilderpy"></span>

# sherlock/sherlock/pipeline/bundle_builder.py

Bundle builder for Sherlock Holmes knowledge graph.

Reads a deduplicated PerStoryBundle JSON and produces a kgbundle directory
(entities.jsonl, relationships.jsonl, evidence.jsonl, manifest.json) that
kgserver can load directly.

Also adds story-level provenance: the Story entity is automatically connected
to all Character/Location/Object entities via DESCRIBED_IN relationships.

> Bundle builder for Sherlock Holmes knowledge graph.

Reads a deduplicated PerStoryBundle JSON and produces a kgbundle directory
(entities.jsonl, relationships.jsonl, evidence.jsonl, manifest.json) that
kgserver can load directly.

Also adds story-level provenance: the Story entity is automatically connected
to all Character/Location/Object entities via DESCRIBED_IN relationships.


### `def _build_entity_rows(bundle: PerStoryBundle) -> list[EntityRow]`

Convert extracted entity rows to kgbundle EntityRow objects.

### `def _build_canonical_id_map(bundle: PerStoryBundle) -> dict[str, str]`

Build local_id -> canonical_id map from entity rows.

### `def _build_relationship_rows(bundle: PerStoryBundle, cid_map: dict[str, str]) -> list[BundleRelationshipRow]`

Convert bundle RelationshipRows to kgbundle format.

### `def _build_evidence_rows(bundle: PerStoryBundle, cid_map: dict[str, str]) -> list[EvidenceRow]`

Build evidence rows from evidence_entities + relationships.

### `def _add_story_provenance_relationships(bundle: PerStoryBundle, entity_rows: list[EntityRow], rel_rows: list[BundleRelationshipRow], cid_map: dict[str, str]) -> None`

Add DESCRIBED_IN edges from all non-Story entities to the Story entity.

This provenance expansion is crucial for graph density: every entity
extracted from a story is explicitly connected to the story node.

### `def build_bundle(bundle: PerStoryBundle, output_dir: Path) -> Path`

Build kgbundle from a deduplicated PerStoryBundle.

Writes:
    {output_dir}/entities.jsonl
    {output_dir}/relationships.jsonl
    {output_dir}/evidence.jsonl
    {output_dir}/manifest.json

Returns output_dir.

### `def build_bundle_from_files(bundle_json_path: Path, output_dir: Path) -> dict[str, int]`

Load deduplicated bundle JSON, build kgbundle, return summary stats.


<span id="user-content-sherlocksherlockpipelinededuppy"></span>

# sherlock/sherlock/pipeline/dedup.py

Deduplication and alias resolution for Sherlock Holmes entities.

Reads PerStoryBundle JSON(s), resolves SAME_AS relationships (alias merges),
builds a canonical ID index, collapses entity fragments, and writes the
merged output as a unified bundle JSON.

Key differences vs medlit dedup:
- No external authority API lookup (fiction entities use synthetic IDs)
- Character alias handling is critical: "the King", "His Majesty",
  "Wilhelm Gottsreich Sigismond von Ormstein" → single canonical node
- SAME_AS edges extracted from LLM output drive merges
- Synonym-normalisation is also important: "Dr. Watson", "Watson",
  "Dr. John H. Watson", "the doctor" → Dr. Watson

> Deduplication and alias resolution for Sherlock Holmes entities.

Reads PerStoryBundle JSON(s), resolves SAME_AS relationships (alias merges),
builds a canonical ID index, collapses entity fragments, and writes the
merged output as a unified bundle JSON.

Key differences vs medlit dedup:
- No external authority API lookup (fiction entities use synthetic IDs)
- Character alias handling is critical: "the King", "His Majesty",
  "Wilhelm Gottsreich Sigismond von Ormstein" → single canonical node
- SAME_AS edges extracted from LLM output drive merges
- Synonym-normalisation is also important: "Dr. Watson", "Watson",
  "Dr. John H. Watson", "the doctor" → Dr. Watson


### `def _normalize_name(name: str) -> str`

Lowercase, strip, and apply alias normalisation.

### `def _slug() -> str`

Synthetic merge key for entities without authoritative ID.

### `def _build_name_type_index(bundle: PerStoryBundle) -> dict[tuple[str, str], str]`

Map (normalized_name, entity_class) -> canonical_id (first-pass index).

### `def _resolve_same_as(bundle: PerStoryBundle) -> dict[str, str]`

Build entity_id -> canonical_id map by following SAME_AS edges.

Also applies _ALIAS_NORMALIZATIONS to collapse well-known aliases.

### `def _collapse_entities(bundle: PerStoryBundle, merge_map: dict[str, str]) -> list[ExtractedEntityRow]`

Merge entity rows according to merge_map; accumulate synonyms and descriptions.

### `def _remap_relationships(bundle: PerStoryBundle, merge_map: dict[str, str]) -> list[RelationshipRow]`

Remap subject/object IDs in relationships through merge_map.

Drop SAME_AS edges (they've been consumed). Drop self-loops.
Deduplicate (subject, predicate, object) triples.

### `def run_dedup(bundle: PerStoryBundle) -> PerStoryBundle`

Run full dedup pipeline on a single PerStoryBundle.

Steps:
1. Resolve SAME_AS edges → merge_map
2. Apply alias normalizations to find additional merges
3. Collapse entity rows
4. Remap relationship IDs
5. Return clean merged bundle

Returns:
    New PerStoryBundle with deduplicated entities and remapped relationships.

### `def run_dedup_from_file(input_path: Path, output_path: Path) -> dict[str, int]`

Load a bundle JSON, run dedup, write to output_path. Returns summary stats.


<span id="user-content-sherlocksherlockpipelineextractorpy"></span>

# sherlock/sherlock/pipeline/extractor.py

LLM extraction pipeline for Sherlock Holmes stories.

For each story chunk (paragraph window), calls the LLM with the Sherlock domain
prompt and collects entities + relationships into a PerStoryBundle.

Follows the medlit pass1_llm pattern: generate_json() → normalize → validate → store.

> LLM extraction pipeline for Sherlock Holmes stories.

For each story chunk (paragraph window), calls the LLM with the Sherlock domain
prompt and collects entities + relationships into a PerStoryBundle.

Follows the medlit pass1_llm pattern: generate_json() → normalize → validate → store.


### `def _fix_evidence_story_id(evidence_id: str, story_id: str) -> str`

Replace placeholder story_id in evidence ID with actual.

### `def _replace_placeholder_in_obj(obj: Any, story_id: str) -> None`

Recursively replace ==CURRENT_STORY== with story_id (in place).

### `def normalize_entity_type(raw_type: str) -> str`

Map raw LLM entity type string to bundle entity_class (PascalCase).

### `def _build_extraction_prompt(chunk_text: str, section: str, paragraph_idx: int, story_id: str) -> str`

Build the user message for a single story chunk.

The system prompt is PROMPT_INSTRUCTIONS (domain spec). The user message
provides the text chunk with context metadata.

### `async def extract_chunk(llm: Any, chunk: dict, story_id: str) -> dict`

Call LLM on a single chunk, return raw JSON bundle dict.

### `def _parse_entities(raw_entities: list, story_id: str) -> list[ExtractedEntityRow]`

Parse and normalize entity rows from LLM output.

### `def _parse_evidence(raw_evidence: list, story_id: str) -> list[EvidenceEntityRow]`

Parse evidence entity rows.

### `def _parse_relationships(raw_rels: list, story_id: str) -> list[RelationshipRow]`

Parse relationship rows.

### `def merge_bundles(bundles: list[PerStoryBundle]) -> PerStoryBundle`

Merge multiple per-chunk bundles into one for the whole story.

Entities with the same (id, class) are deduplicated by keeping the first
occurrence and accumulating synonyms.

### `async def extract_story(story_info: StoryInfo, chunks: list[dict], llm: Any) -> PerStoryBundle`

Run extraction over all chunks of a story, return merged PerStoryBundle.

Args:
    story_info: Story metadata.
    chunks: List of chunk dicts (from parser.chunk_story_windowed).
    llm: LLM instance with generate_json(system_prompt, user_message, ...) method.
    temperature: LLM sampling temperature.
    max_tokens: Max tokens per LLM call.
    verbose: Print progress to stderr.


<span id="user-content-sherlocksherlockpipelineparserpy"></span>

# sherlock/sherlock/pipeline/parser.py

Story parser and paragraph chunker for Sherlock Holmes stories.

Fetches "A Scandal in Bohemia" from Project Gutenberg (or accepts a local file),
strips the Gutenberg header/footer, and produces a SherlockStory document with
paragraph-level chunking for extraction.

Evidence IDs use: {story_id}:{section}:{paragraph_idx}:llm

> Story parser and paragraph chunker for Sherlock Holmes stories.

Fetches "A Scandal in Bohemia" from Project Gutenberg (or accepts a local file),
strips the Gutenberg header/footer, and produces a SherlockStory document with
paragraph-level chunking for extraction.

Evidence IDs use: {story_id}:{section}:{paragraph_idx}:llm


### `def _fetch_gutenberg_text(url: str, timeout: int = 30) -> str`

Fetch plain text from an allowed domain (Project Gutenberg only).

Raises ValueError for disallowed hosts to prevent SSRF.

### `def _extract_story(full_text: str, start_marker: str, end_marker: str) -> str`

Extract a story section from a multi-story collection.

### `def _clean_text(text: str) -> str`

Remove Gutenberg header/footer boilerplate and normalize whitespace.

### `def get_story_text(local_path: Optional[Path] = None, story_url: str = SCANDAL_GUTENBERG_URL) -> str`

Fetch and return the clean text of 'A Scandal in Bohemia'.

Priority:
1. local_path (override for offline / test use)
2. Project Gutenberg fetch
3. Embedded excerpt fallback

### `def chunk_story(story_text: str, min_words: int = 40) -> list[dict]`

Split story text into paragraph chunks with stable indices.

Returns a list of dicts:
    {
        "section": str,          # "opening" | "body"
        "paragraph_idx": int,    # 0-based index across entire story
        "text": str,             # paragraph text
    }

### `def chunk_story_windowed(story_text: str, window_size: int = 3, min_words: int = 40) -> list[dict]`

Return overlapping windows of paragraphs for richer context in LLM extraction.

Each chunk contains `window_size` consecutive paragraphs. The `paragraph_idx`
is the index of the FIRST paragraph in the window.


<span id="user-content-sherlocksherlockpromotionpy"></span>

# sherlock/sherlock/promotion.py

Promotion policy for Sherlock Holmes domain.

Fiction entities don't have external authority APIs like UMLS or HGNC.
Instead we use a curated DBPedia URI map for well-known characters/locations,
and generate synthetic canonical IDs (holmes:<story_slug>:<type>:<SafeName>)
for all others.

Entities are promoted immediately (all fiction entities are inherently real
within the story universe) — there's no provisional/canonical distinction
for fictional entities. The main purpose of this policy is to assign
stable canonical IDs.

> Promotion policy for Sherlock Holmes domain.

Fiction entities don't have external authority APIs like UMLS or HGNC.
Instead we use a curated DBPedia URI map for well-known characters/locations,
and generate synthetic canonical IDs (holmes:<story_slug>:<type>:<SafeName>)
for all others.

Entities are promoted immediately (all fiction entities are inherently real
within the story universe) — there's no provisional/canonical distinction
for fictional entities. The main purpose of this policy is to assign
stable canonical IDs.


## `class SherlockPromotionPolicy(PromotionPolicy)`

Promotion policy for Sherlock Holmes fiction domain.

All fiction entities are promoted (there is no external validation step).
Canonical IDs are assigned from:
1. Curated DBPedia map (for well-known entities).
2. Synthetic holmes:<story_slug>:<type>:<SafeName> IDs for all others.

### `def SherlockPromotionPolicy.should_promote(self, entity: BaseEntity) -> bool`

All provisional fiction entities are promoted.

### `async def SherlockPromotionPolicy.assign_canonical_id(self, entity: BaseEntity) -> Optional[object]`

Assign a canonical ID for a Sherlock entity.

Priority:
1. Already has a canonical ID in canonical_ids → use it.
2. Curated DBPedia map lookup.
3. Synthetic holmes: URI from name + type.


<span id="user-content-sherlocksherlockrelationshipspy"></span>

# sherlock/sherlock/relationships.py

Sherlock Holmes relationship class.

Single relationship class with a `predicate` field, following the medlit pattern.
Sherlock-specific metadata (narrator_trust, narrative_position, story_time, known_by)
is stored in the `metadata` dict.

> Sherlock Holmes relationship class.

Single relationship class with a `predicate` field, following the medlit pattern.
Sherlock-specific metadata (narrator_trust, narrative_position, story_time, known_by)
is stored in the `metadata` dict.


## `class SherlockRelationship(BaseRelationship)`

A typed relationship in the Sherlock Holmes knowledge graph.

Uses Pattern A (single class, many predicates) for simplicity.
Sherlock-specific epistemic metadata is stored in metadata dict:
    narrator_trust: One of NarratorTrust enum values
    story_time: One of STORY_TIME_VALUES
    narrative_position: Optional int paragraph index
    known_by: Optional comma-separated character list (who knew this at story time)


<span id="user-content-sherlocksherlockscriptsinitpy"></span>

# sherlock/sherlock/scripts/__init__.py

Sherlock scripts package.


<span id="user-content-sherlocksherlockscriptsbuildbundlepy"></span>

# sherlock/sherlock/scripts/build_bundle.py

build_bundle: Assemble kgbundle from deduped Sherlock story bundle.

Reads the deduplicated story bundle JSON (from sherlock-ingest) and writes a
kgbundle directory (entities.jsonl, relationships.jsonl, evidence.jsonl, manifest.json)
that can be loaded directly by kgserver.

Usage:
  sherlock-build-bundle --input deduped/deduped_story_scandal_in_bohemia.json --output-dir bundle/
  sherlock-build-bundle --input sherlock_output/deduped/deduped_story_scandal_in_bohemia.json

> build_bundle: Assemble kgbundle from deduped Sherlock story bundle.

Reads the deduplicated story bundle JSON (from sherlock-ingest) and writes a
kgbundle directory (entities.jsonl, relationships.jsonl, evidence.jsonl, manifest.json)
that can be loaded directly by kgserver.

Usage:
  sherlock-build-bundle --input deduped/deduped_story_scandal_in_bohemia.json --output-dir bundle/
  sherlock-build-bundle --input sherlock_output/deduped/deduped_story_scandal_in_bohemia.json



<span id="user-content-sherlocksherlockscriptsextractpy"></span>

# sherlock/sherlock/scripts/extract.py

extract: LLM extraction from 'A Scandal in Bohemia' → per-story bundle JSON.

Fetches the story text (from Project Gutenberg or a local file), chunks it into
paragraph windows, calls the configured LLM once per window, and writes a single
bundle JSON file.

Usage:
  sherlock-extract --output-dir output/ --llm-backend anthropic
  sherlock-extract --output-dir output/ --llm-backend ollama
  sherlock-extract --output-dir output/ --story-file scandal.txt --llm-backend anthropic
  sherlock-extract --output-dir output/ --llm-backend anthropic --window-size 5 --limit-chunks 10

Set ANTHROPIC_API_KEY for Anthropic, or run Ollama locally.

> extract: LLM extraction from 'A Scandal in Bohemia' → per-story bundle JSON.

Fetches the story text (from Project Gutenberg or a local file), chunks it into
paragraph windows, calls the configured LLM once per window, and writes a single
bundle JSON file.

Usage:
  sherlock-extract --output-dir output/ --llm-backend anthropic
  sherlock-extract --output-dir output/ --llm-backend ollama
  sherlock-extract --output-dir output/ --story-file scandal.txt --llm-backend anthropic
  sherlock-extract --output-dir output/ --llm-backend anthropic --window-size 5 --limit-chunks 10

Set ANTHROPIC_API_KEY for Anthropic, or run Ollama locally.


### `async def run_extract(output_dir: Path, llm_backend: str, story_file: Optional[Path] = None, window_size: int = 3, limit_chunks: Optional[int] = None, skip_if_exists: bool = True) -> None`

Run full extraction pipeline for A Scandal in Bohemia.


<span id="user-content-sherlocksherlockscriptsingestpy"></span>

# sherlock/sherlock/scripts/ingest.py

ingest: Deduplication and alias resolution for Sherlock story bundle.

Reads a story bundle JSON (from sherlock-extract), runs the dedup pipeline
(SAME_AS resolution, alias normalisation, entity merging), and writes the
deduplicated bundle JSON.

Usage:
  sherlock-ingest --input story_scandal_in_bohemia.json --output deduped/
  sherlock-ingest --input sherlock_output/story_scandal_in_bohemia.json

> ingest: Deduplication and alias resolution for Sherlock story bundle.

Reads a story bundle JSON (from sherlock-extract), runs the dedup pipeline
(SAME_AS resolution, alias normalisation, entity merging), and writes the
deduplicated bundle JSON.

Usage:
  sherlock-ingest --input story_scandal_in_bohemia.json --output deduped/
  sherlock-ingest --input sherlock_output/story_scandal_in_bohemia.json



<span id="user-content-sherlocktestsconftestpy"></span>

# sherlock/tests/conftest.py

Test fixtures for Sherlock Holmes pipeline tests.

### `def minimal_bundle(story_info: StoryInfo) -> PerStoryBundle`

A minimal bundle for testing dedup and builder.


<span id="user-content-sherlockteststestbundlepy"></span>

# sherlock/tests/test_bundle.py

Tests for the bundle builder.

### `def test_build_bundle_creates_files(minimal_bundle: PerStoryBundle)`

build_bundle must create all expected output files.

### `def test_manifest_content(minimal_bundle: PerStoryBundle)`

manifest.json must have expected fields and correct domain.

### `def test_entities_jsonl_valid(minimal_bundle: PerStoryBundle)`

entities.jsonl must be valid JSONL with expected fields.

### `def test_relationships_jsonl_valid(minimal_bundle: PerStoryBundle)`

relationships.jsonl must be valid JSONL with expected fields.

### `def test_story_provenance_added(minimal_bundle: PerStoryBundle)`

DESCRIBED_IN edges must be added for all non-Story entities.

### `def test_no_self_loops_in_bundle(minimal_bundle: PerStoryBundle)`

Bundle relationships must not contain self-loops.

### `def test_narrator_trust_in_properties(minimal_bundle: PerStoryBundle)`

narrator_trust should appear in relationship properties.

### `def test_bundle_roundtrip(minimal_bundle: PerStoryBundle)`

Bundle serialization round-trip must be lossless.


<span id="user-content-sherlockteststestbundlemodelspy"></span>

# sherlock/tests/test_bundle_models.py

Tests for bundle_models — serialization, Pydantic validation, etc.

### `def test_extracted_entity_row_alias()`

entity_class must be serialized as 'class' via alias.

### `def test_extracted_entity_row_roundtrip()`

ExtractedEntityRow must survive serialization round-trip.

### `def test_relationship_row_alias()`

object_id must serialize as 'object' via alias.

### `def test_relationship_narrator_trust_valid()`

narrator_trust must accept valid enum values.

### `def test_relationship_story_time_valid()`

story_time must accept valid values.

### `def test_evidence_entity_row_class_literal()`

Evidence entity_class must be 'Evidence'.

### `def test_per_story_bundle_roundtrip(story_info: StoryInfo, minimal_bundle: PerStoryBundle)`

PerStoryBundle must survive to_bundle_dict/from_bundle_dict round-trip.

### `def test_per_story_bundle_empty()`

PerStoryBundle with no entities/rels must serialize without error.


<span id="user-content-sherlockteststestdeduppy"></span>

# sherlock/tests/test_dedup.py

Tests for the dedup pipeline.

### `def test_normalize_name_aliases()`

Key character aliases must normalize correctly.

### `def test_same_as_resolution(minimal_bundle: PerStoryBundle)`

SAME_AS edges must cause entity merges.

### `def test_same_as_edges_removed(minimal_bundle: PerStoryBundle)`

SAME_AS edges must not appear in deduped relationships.

### `def test_no_self_loops(minimal_bundle: PerStoryBundle)`

Dedup must not produce self-loop relationships.

### `def test_entity_synonyms_merged(minimal_bundle: PerStoryBundle)`

When two entity rows share a canonical ID (via SAME_AS), synonyms should be merged.

### `def test_run_dedup_reduces_duplicate_relationships(story_info: StoryInfo)`

Duplicate (subject, predicate, object) triples must be deduplicated.


<span id="user-content-sherlockteststestdomainspecpy"></span>

# sherlock/tests/test_domain_spec.py

Tests for domain_spec.py — entity types, predicates, and prompt instructions.

### `def test_entity_classes_registered()`

All entity classes must be in ENTITY_CLASSES.

### `def test_normalized_to_bundle()`

NORMALIZED_TO_BUNDLE must map lowercase class names to PascalCase.

### `def test_all_predicates_defined()`

ALL_PREDICATES must include core Sherlock predicates.

### `def test_predicate_specs_have_descriptions()`

All predicates must have non-empty descriptions.

### `def test_same_as_is_merge_signal()`

SAME_AS must be flagged as a merge signal.

### `def test_ally_of_is_symmetric()`

ALLY_OF should be symmetric.

### `def test_get_valid_predicates_character_location()`

get_valid_predicates(character, location) must include spatial predicates.

### `def test_get_valid_predicates_character_character()`

get_valid_predicates(character, character) must include social predicates.

### `def test_get_valid_predicates_character_story()`

get_valid_predicates(character, story) must include APPEARS_IN.

### `def test_narrator_trust_enum_values()`

NarratorTrust must have all 8 required values.

### `def test_prompt_instructions_non_empty()`

PROMPT_INSTRUCTIONS must be a non-trivial string.

### `def test_entity_spec_has_colors()`

All entity classes with specs must have hex color.

### `def test_entity_get_entity_type()`

Entity classes must return correct type strings.


<span id="user-content-sherlockteststestparserpy"></span>

# sherlock/tests/test_parser.py

Tests for story parser and chunker.

### `def test_get_story_text_embedded_fallback()`

get_story_text() must return content even if network is unavailable or URL is invalid.

### `def test_fetch_rejects_disallowed_host()`

_fetch_gutenberg_text must raise ValueError for non-Gutenberg URLs.

### `def test_clean_text_removes_pg_footer()`

_clean_text must strip Gutenberg boilerplate.

### `def test_extract_story_finds_section()`

_extract_story must find the story section by marker.

### `def test_chunk_story_returns_paragraphs()`

chunk_story must return a list of chunks with expected keys.

### `def test_chunk_story_unique_indices()`

Chunk paragraph_idx values must be unique.

### `def test_chunk_story_windowed_overlap()`

Windowed chunking must produce overlapping windows.

### `def test_sections_assigned()`

Early chunks get 'opening' section; later get 'body'.


<span id="user-content-sherlockdesignmd"></span>

# sherlock_design.md

# Sherlock Holmes Example: Design Notes

## Goal

Upgrade the Sherlock example from a thin demo (3 entity types, 5 generic predicates,
no LLM extraction) to a richly specified domain that:

1. Follows the `domain_spec.py` single-source-of-truth pattern from medlit
2. Captures the epistemic complexity of fiction, especially the unreliable narrator
3. Supports a compelling "solve the crime" demo using BFS graph traversal + LLM inference

    ...

<span id="user-content-summarizecodebasepy"></span>

# summarize_codebase.py

Extract documentation from Python source files into Markdown.

Walks the AST to find docstrings, standalone strings, and creates
formatted signatures for classes, methods, and functions.

Includes a portion of each *.md, *.yml, Dockerfile, and shell script
to add more context.

$ git ls-files | uv run python summarize_codebase.py > summary.md

> 
Extract documentation from Python source files into Markdown.

Walks the AST to find docstrings, standalone strings, and creates
formatted signatures for classes, methods, and functions.

Includes a portion of each *.md, *.yml, Dockerfile, and shell script
to add more context.

$ git ls-files | uv run python summarize_codebase.py > summary.md


### `def DocExtractor.visit_Module(self, node: ast.Module) -> None`

Extract module-level docstring and top-level standalone strings.


<span id="user-content-testsinitpy"></span>

# tests/__init__.py

Tests for the kgraph knowledge graph framework.


<span id="user-content-testsconftestpy"></span>

# tests/conftest.py

Test fixtures and minimal test domain implementation.

This module provides:
- Minimal concrete implementations of abstract base classes (SimpleEntity,
  SimpleDocument, SimpleRelationship, SimpleDomainSchema) for use in unit tests
- Mock implementations of pipeline interfaces (document parsing, entity
  extraction/resolution, relationship extraction, embedding generation)
- Pytest fixtures that instantiate in-memory storage and mock components
- Helper factory functions for creating test entities and relationships

The test domain uses a simple convention where entities are denoted by
square brackets in document text (e.g., "[aspirin]" becomes an entity).

> Test fixtures and minimal test domain implementation.

This module provides:
- Minimal concrete implementations of abstract base classes (SimpleEntity,
  SimpleDocument, SimpleRelationship, SimpleDomainSchema) for use in unit tests
- Mock implementations of pipeline interfaces (document parsing, entity
  extraction/resolution, relationship extraction, embedding generation)
- Pytest fixtures that instantiate in-memory storage and mock components
- Helper factory functions for creating test entities and relationships

The test domain uses a simple convention where entities are denoted by
square brackets in document text (e.g., "[aspirin]" becomes an entity).


## `class SimpleEntity(BaseEntity)`

Minimal concrete entity implementation for unit tests.

Provides a single entity type ("test_entity") with configurable type
via the entity_type field. Inherits all standard entity fields from
BaseEntity (entity_id, name, status, confidence, usage_count, etc.).
**Fields:**

```python
entity_type: str
```

### `def SimpleEntity.get_entity_type(self) -> str`

Return the entity's type identifier.

## `class SimpleRelationship(BaseRelationship)`

Minimal concrete relationship implementation for unit tests.

Uses the predicate field directly as the edge type. Supports any
predicate string, allowing flexible relationship testing without
schema constraints.

### `def SimpleRelationship.get_edge_type(self) -> str`

Return the relationship's edge type (same as predicate).

## `class SimpleDocument(BaseDocument)`

Minimal concrete document implementation for unit tests.

Represents documents as a single "body" section containing the full
content. The document type defaults to "test_document" but can be
customized for tests requiring multiple document types.

### `def SimpleDocument.get_document_type(self) -> str`

Return the document's type identifier.

### `def SimpleDocument.get_sections(self) -> list[tuple[str, str]]`

Return document sections as (section_name, content) tuples.

For SimpleDocument, returns a single "body" section with full content.

## `class SimpleDomainSchema(DomainSchema)`

Minimal domain schema defining types and validation for the test domain.

Configures:
- One entity type: "test_entity"
- Two relationship types: "related_to", "causes"
- One document type: "test_document"
- Lenient promotion config: 2 usages, 0.7 confidence, no embedding required

This schema is intentionally simple to allow straightforward testing
of domain-agnostic graph operations without real-world complexity.

### `def SimpleDomainSchema.name(self) -> str`

Return the domain name identifier.

### `def SimpleDomainSchema.entity_types(self) -> dict[str, type[BaseEntity]]`

Return mapping of entity type names to their classes.

### `def SimpleDomainSchema.relationship_types(self) -> dict[str, type[BaseRelationship]]`

Return mapping of relationship type names to their classes.

### `def SimpleDomainSchema.predicate_constraints(self) -> dict[str, PredicateConstraint]`

Define predicate constraints for the test domain.

For simplicity in testing, we'll allow all relationships to be valid
between 'test_entity' types by default, but this can be overridden
in specific tests if needed.

### `def SimpleDomainSchema.document_types(self) -> dict[str, type[BaseDocument]]`

Return mapping of document type names to their classes.

### `def SimpleDomainSchema.promotion_config(self) -> PromotionConfig`

Return configuration for promoting provisional entities to canonical.

Uses lenient thresholds suitable for testing: requires only 2 usages
and 0.7 confidence, with no embedding requirement.

### `def SimpleDomainSchema.validate_entity(self, entity: BaseEntity) -> list[ValidationIssue]`

Check if the entity's type is registered in this schema.

### `async def SimpleDomainSchema.validate_relationship(self, relationship: BaseRelationship, entity_storage: EntityStorageInterface | None = None) -> bool`

Check if the relationship's predicate is registered in this schema.

Also calls the superclass method to apply predicate constraints.

## `class MockEmbeddingGenerator(EmbeddingGeneratorInterface)`

Mock embedding generator producing deterministic hash-based embeddings.

Generates fixed-dimension vectors derived from the text's hash, ensuring
identical text always produces identical embeddings. Useful for testing
embedding-dependent logic (similarity search, merge detection) without
requiring a real embedding model.

Args:
    dim: Embedding vector dimension (default: 8).

### `def MockEmbeddingGenerator.dimension(self) -> int`

Return the embedding vector dimension.

### `async def MockEmbeddingGenerator.generate(self, text: str) -> tuple[float, ...]`

Generate a deterministic embedding from text using its hash.

### `async def MockEmbeddingGenerator.generate_batch(self, texts: Sequence[str]) -> list[tuple[float, ...]]`

Generate embeddings for multiple texts sequentially.

## `class MockDocumentParser(DocumentParserInterface)`

Mock document parser that wraps raw bytes in a SimpleDocument.

Decodes raw content as UTF-8 text and creates a SimpleDocument with
a randomly generated document_id. Does not perform any actual parsing
or structure extraction.

### `async def MockDocumentParser.parse(self, raw_content: bytes, content_type: str, source_uri: str | None = None) -> BaseDocument`

Parse raw bytes into a SimpleDocument.

Args:
    raw_content: Document bytes (decoded as UTF-8).
    content_type: MIME type of the content.
    source_uri: Optional URI identifying the document source.

Returns:
    SimpleDocument instance with generated ID and current timestamp.

## `class MockEntityExtractor(EntityExtractorInterface)`

Mock entity extractor using bracket notation for entity detection.

Extracts entities from document text by finding text enclosed in
square brackets. For example, the text "Patient took [aspirin] for
[headache]" yields two EntityMention objects for "aspirin" and
"headache", each with 0.9 confidence and "test_entity" type.

This simple convention allows tests to precisely control which
entities are extracted without needing NLP or ML components.

### `async def MockEntityExtractor.extract(self, document: BaseDocument) -> list[EntityMention]`

Extract entity mentions from bracketed text in the document.

Args:
    document: Document to extract entities from.

Returns:
    List of EntityMention objects for each bracketed term found.

## `class MockEntityResolver(EntityResolverInterface)`

Mock entity resolver that links mentions to entities via name matching.

Resolution strategy:
1. Search existing storage for an entity with matching name and type
2. If found, return existing entity with 0.95 confidence
3. If not found, create a new provisional SimpleEntity with the
   mention's confidence score

This simple name-based matching is sufficient for testing entity
resolution and promotion logic without external knowledge bases.

### `async def MockEntityResolver.resolve(self, mention: EntityMention, existing_storage: EntityStorageInterface) -> tuple[BaseEntity, float]`

Resolve an entity mention to an existing or new entity.

Args:
    mention: The entity mention to resolve.
    existing_storage: Storage to search for existing entities.

Returns:
    Tuple of (resolved entity, resolution confidence score).

### `async def MockEntityResolver.resolve_batch(self, mentions: Sequence[EntityMention], existing_storage: EntityStorageInterface) -> list[tuple[BaseEntity, float]]`

Resolve multiple mentions sequentially.

## `class MockRelationshipExtractor(RelationshipExtractorInterface)`

Mock relationship extractor that chains adjacent entities.

Creates "related_to" relationships between consecutively ordered
entities. For a document with entities [A, B, C], produces edges
A->B and B->C, each with 0.8 confidence.

This simple linear chaining allows tests to verify relationship
storage and traversal without complex extraction logic.

### `async def MockRelationshipExtractor.extract(self, document: BaseDocument, entities: Sequence[BaseEntity]) -> list[BaseRelationship]`

Extract relationships between consecutive entities.

Args:
    document: Source document for provenance tracking.
    entities: Ordered sequence of entities from the document.

Returns:
    List of "related_to" relationships linking adjacent entities.

### `def test_domain() -> SimpleDomainSchema`

Provide a SimpleDomainSchema instance for domain-aware tests.

The schema defines entity types, relationship types, and promotion
configuration suitable for unit testing graph operations.

### `def entity_storage() -> InMemoryEntityStorage`

Provide a fresh in-memory entity storage instance.

Each test receives an empty storage, ensuring test isolation.

### `def relationship_storage() -> InMemoryRelationshipStorage`

Provide a fresh in-memory relationship storage instance.

Each test receives an empty storage, ensuring test isolation.

### `def document_storage() -> InMemoryDocumentStorage`

Provide a fresh in-memory document storage instance.

Each test receives an empty storage, ensuring test isolation.

### `def embedding_generator() -> MockEmbeddingGenerator`

Provide a MockEmbeddingGenerator with default 8-dimensional vectors.

Generates deterministic embeddings based on text hash for reproducible
similarity comparisons in tests.

### `def document_parser() -> MockDocumentParser`

Provide a MockDocumentParser for converting raw bytes to SimpleDocument.

Decodes content as UTF-8 without performing actual parsing or
structure extraction.

### `def entity_extractor() -> MockEntityExtractor`

Provide a MockEntityExtractor using bracket notation.

Extracts entities from text enclosed in square brackets (e.g.,
"[aspirin]" becomes an entity mention).

### `def entity_resolver() -> MockEntityResolver`

Provide a MockEntityResolver for name-based entity matching.

Links mentions to existing entities by name or creates new
provisional entities when no match is found.

### `def relationship_extractor() -> MockRelationshipExtractor`

Provide a MockRelationshipExtractor for linear entity chaining.

Creates "related_to" relationships between consecutively ordered
entities in a document.

### `def make_test_entity(name: str, status: EntityStatus = EntityStatus.PROVISIONAL, entity_id: str | None = None, usage_count: int = 0, confidence: float = 1.0, embedding: tuple[float, ...] | None = None, canonical_ids: dict[str, str] | None = None) -> SimpleEntity`

Factory function to create SimpleEntity instances with sensible defaults.

Provides a concise way to create entities in tests without specifying
all required fields. Generates a random UUID if entity_id is not provided.

Args:
    name: Display name for the entity (required).
    status: Entity lifecycle status (default: PROVISIONAL).
    entity_id: Unique identifier (default: auto-generated UUID).
    usage_count: Number of document references (default: 0).
    confidence: Confidence score from extraction (default: 1.0).
    embedding: Optional semantic embedding vector.
    canonical_ids: Optional mapping of authority names to external IDs.

Returns:
    Configured SimpleEntity instance with current timestamp.

### `def make_test_relationship(subject_id: str, object_id: str, predicate: str = 'related_to', confidence: float = 1.0) -> SimpleRelationship`

Factory function to create SimpleRelationship instances with defaults.

Provides a concise way to create relationships in tests. Both subject
and object entity IDs are required; predicate and confidence have defaults.

Args:
    subject_id: Entity ID of the relationship source.
    object_id: Entity ID of the relationship target.
    predicate: Relationship type name (default: "related_to").
    confidence: Confidence score for the relationship (default: 1.0).

Returns:
    Configured SimpleRelationship instance with current timestamp.


<span id="user-content-teststestbuildcodereferencepy"></span>

# tests/test_build_code_reference.py

Tests for scripts/build_code_reference.py.

### `def test_build_code_reference_generates_expected_structure(tmp_path: Path) -> None`

Generator writes package/module pages and excludes tests/cache paths.

### `def test_build_code_reference_module_title_uses_package_name_for_init(tmp_path: Path) -> None`

`__init__.py` pages use package module names without __init__ suffix.


<span id="user-content-teststestcachingpy"></span>

# tests/test_caching.py

Tests for embedding caching components.

Tests in-memory and file-based caching, as well as the cached embedding generator.

> Tests for embedding caching components.

Tests in-memory and file-based caching, as well as the cached embedding generator.


## `class TestEmbeddingCacheConfig`

Test EmbeddingCacheConfig model.

### `def TestEmbeddingCacheConfig.test_default_config(self)`

Test default cache configuration.

### `def TestEmbeddingCacheConfig.test_custom_config(self)`

Test custom cache configuration.

### `def TestEmbeddingCacheConfig.test_config_immutability(self)`

Test that config is immutable (frozen=True).

## `class TestInMemoryEmbeddingsCache`

Test InMemoryEmbeddingsCache implementation.

### `async def TestInMemoryEmbeddingsCache.test_put_and_get(self)`

Test basic put and get operations.

### `async def TestInMemoryEmbeddingsCache.test_cache_miss(self)`

Test get with cache miss.

### `async def TestInMemoryEmbeddingsCache.test_cache_stats(self)`

Test cache statistics tracking.

### `async def TestInMemoryEmbeddingsCache.test_lru_eviction(self)`

Test LRU eviction when cache is full.

### `async def TestInMemoryEmbeddingsCache.test_lru_access_order(self)`

Test that accessing items updates LRU order.

### `async def TestInMemoryEmbeddingsCache.test_batch_get(self)`

Test batch get operation.

### `async def TestInMemoryEmbeddingsCache.test_batch_put(self)`

Test batch put operation.

### `async def TestInMemoryEmbeddingsCache.test_clear(self)`

Test clearing the cache.

### `async def TestInMemoryEmbeddingsCache.test_key_normalization(self)`

Test that keys are normalized when enabled.

### `async def TestInMemoryEmbeddingsCache.test_no_key_normalization(self)`

Test cache without key normalization.

## `class TestFileBasedEmbeddingsCache`

Test FileBasedEmbeddingsCache implementation.

### `async def TestFileBasedEmbeddingsCache.test_put_and_get(self)`

Test basic put and get operations.

### `async def TestFileBasedEmbeddingsCache.test_persistence(self)`

Test that cache persists across instances.

### `async def TestFileBasedEmbeddingsCache.test_auto_save(self)`

Test automatic saving at intervals.

### `async def TestFileBasedEmbeddingsCache.test_manual_save(self)`

Test manual save operation.

### `async def TestFileBasedEmbeddingsCache.test_load_nonexistent_file(self)`

Test loading from nonexistent file.

### `async def TestFileBasedEmbeddingsCache.test_normalize_keys_on_load(self)`

Keys loaded from file are normalized so get() with different casing hits.

### `async def TestFileBasedEmbeddingsCache.test_lru_eviction_with_persistence(self)`

Test LRU eviction works with persistent cache.

### `async def TestFileBasedEmbeddingsCache.test_batch_operations(self)`

Test batch put and get with persistence.

### `async def TestFileBasedEmbeddingsCache.test_concurrent_access(self)`

Concurrent get/put/save/load do not corrupt cache.

## `class TestCachedEmbeddingGenerator`

Test CachedEmbeddingGenerator wrapper.

### `async def TestCachedEmbeddingGenerator.test_cache_hit(self)`

Test that cached values are returned without calling base generator.

### `async def TestCachedEmbeddingGenerator.test_cache_miss(self)`

Test that cache misses call base generator.

### `async def TestCachedEmbeddingGenerator.test_dimension_property(self)`

Test that dimension is passed through from base generator.

### `async def TestCachedEmbeddingGenerator.test_batch_generation_with_cache(self)`

Test batch generation with partial cache hits.

### `async def TestCachedEmbeddingGenerator.test_save_cache_convenience_method(self)`

Test convenience method for saving cache.

### `async def TestCachedEmbeddingGenerator.test_get_cache_stats(self)`

Test getting cache statistics through wrapper.

### `async def TestCachedEmbeddingGenerator.test_cached_generator_calls_base_once_per_text(self)`

Repeated generate() with same text calls base generator only once.

### `async def TestCachedEmbeddingGenerator.test_cached_generator_batch_returns_correct_order(self)`

generate_batch with mixed hits/misses returns list in input order.

## `class TestCachingIntegration`

Integration tests for caching components.

### `async def TestCachingIntegration.test_end_to_end_caching_workflow(self)`

Test complete caching workflow with persistence.

### `async def TestCachingIntegration.test_cache_with_many_items(self)`

Test cache performance with many items.


<span id="user-content-teststestcanonicalidpy"></span>

# tests/test_canonical_id.py

Tests for canonical ID abstractions.

This module tests the core canonical ID abstractions:
- CanonicalId model
- CanonicalIdCacheInterface and JsonFileCanonicalIdCache
- CanonicalIdLookupInterface
- Helper functions in canonical_helpers

> Tests for canonical ID abstractions.

This module tests the core canonical ID abstractions:
- CanonicalId model
- CanonicalIdCacheInterface and JsonFileCanonicalIdCache
- CanonicalIdLookupInterface
- Helper functions in canonical_helpers


## `class TestCanonicalId`

Tests for the CanonicalId model.

### `def TestCanonicalId.test_canonical_id_creation(self)`

CanonicalId can be created with id, url, and synonyms.

### `def TestCanonicalId.test_canonical_id_minimal(self)`

CanonicalId can be created with just an id.

### `def TestCanonicalId.test_canonical_id_frozen(self)`

CanonicalId is frozen (immutable).

### `def TestCanonicalId.test_canonical_id_str_representation(self)`

CanonicalId string representation returns the id.

## `class TestJsonFileCanonicalIdCache`

Tests for JsonFileCanonicalIdCache implementation.

### `def TestJsonFileCanonicalIdCache.test_cache_creation(self)`

Cache can be created with a file path.

### `def TestJsonFileCanonicalIdCache.test_store_and_fetch(self)`

Can store and fetch CanonicalId objects.

### `def TestJsonFileCanonicalIdCache.test_fetch_miss_returns_none(self)`

Fetching non-existent entry returns None.

### `def TestJsonFileCanonicalIdCache.test_mark_known_bad(self)`

Can mark terms as known bad and check them.

### `def TestJsonFileCanonicalIdCache.test_cache_persistence(self)`

Cache persists to disk and can be reloaded.

### `def TestJsonFileCanonicalIdCache.test_cache_metrics(self)`

Cache tracks metrics correctly.

### `def TestJsonFileCanonicalIdCache.test_cache_migration_from_old_format(self)`

Cache can migrate from old format (dict[str, str]).

### `def TestJsonFileCanonicalIdCache.test_cache_normalizes_keys(self)`

Cache normalizes keys (case-insensitive, strips whitespace).

## `class TestCanonicalHelpers`

Tests for canonical ID helper functions.

### `def TestCanonicalHelpers.test_extract_canonical_id_from_entity_with_priority(self)`

extract_canonical_id_from_entity respects priority order.

### `def TestCanonicalHelpers.test_extract_canonical_id_from_entity_no_priority(self)`

extract_canonical_id_from_entity returns first available if no priority.

### `def TestCanonicalHelpers.test_extract_canonical_id_from_entity_no_canonical_ids(self)`

extract_canonical_id_from_entity returns None if no canonical_ids.

### `def TestCanonicalHelpers.test_check_entity_id_format_prefix_match(self)`

check_entity_id_format matches prefix patterns.

### `def TestCanonicalHelpers.test_check_entity_id_format_umls_pattern(self)`

check_entity_id_format matches UMLS pattern (C + digits).

### `def TestCanonicalHelpers.test_check_entity_id_format_numeric_pattern(self)`

check_entity_id_format handles numeric patterns (HGNC, RxNorm).

### `def TestCanonicalHelpers.test_check_entity_id_format_uniprot_pattern(self)`

check_entity_id_format matches UniProt pattern (P/Q + alphanumeric).

### `def TestCanonicalHelpers.test_check_entity_id_format_no_match(self)`

check_entity_id_format returns None if no pattern matches.

### `def TestCanonicalHelpers.test_check_entity_id_format_wrong_entity_type(self)`

check_entity_id_format returns None for wrong entity type.


<span id="user-content-teststestentitiespy"></span>

# tests/test_entities.py

Tests for entity creation, status management, and in-memory storage operations.

This module verifies:
- Entity instantiation with provisional vs canonical status
- Entity attributes: synonyms, embeddings, canonical IDs from authority sources
- Entity immutability (frozen Pydantic models)
- InMemoryEntityStorage CRUD operations (add, get, update, delete)
- Batch retrieval and counting
- Name-based lookups (case-insensitive, synonym-aware)
- Embedding-based similarity search with configurable thresholds

> Tests for entity creation, status management, and in-memory storage operations.

This module verifies:
- Entity instantiation with provisional vs canonical status
- Entity attributes: synonyms, embeddings, canonical IDs from authority sources
- Entity immutability (frozen Pydantic models)
- InMemoryEntityStorage CRUD operations (add, get, update, delete)
- Batch retrieval and counting
- Name-based lookups (case-insensitive, synonym-aware)
- Embedding-based similarity search with configurable thresholds


## `class TestEntityCreation`

Tests for creating entities with different statuses and attributes.

Verifies that entities can be created with provisional or canonical status,
store multiple canonical IDs from different authority sources (e.g., UMLS,
Wikidata), maintain synonyms for alternative names, hold semantic embeddings
for similarity comparisons, and enforce immutability via frozen Pydantic models.

### `def TestEntityCreation.test_create_provisional_entity(self) -> None`

Provisional entities are created with PROVISIONAL status and empty canonical IDs.

Provisional entities represent mentions that have been extracted from documents
but not yet validated against authoritative sources. They start with no
canonical IDs and can later be promoted to canonical status.

### `def TestEntityCreation.test_create_canonical_entity(self) -> None`

Canonical entities store validated identifiers from multiple authority sources.

Canonical entities have been validated and assigned stable IDs from
authoritative sources (e.g., test_authority, wikidata). Multiple canonical
IDs allow cross-referencing across different knowledge bases.

### `def TestEntityCreation.test_entity_with_synonyms(self) -> None`

Entities store alternative names as synonyms for improved matching.

Synonyms enable entity resolution to match different textual mentions
(e.g., "ASA" and "acetylsalicylic acid") to the same canonical entity.

### `def TestEntityCreation.test_entity_with_embedding(self) -> None`

Entities store semantic vector embeddings for similarity-based operations.

Embeddings enable semantic similarity comparisons between entities,
used for detecting potential duplicates during merge candidate detection
and for semantic search queries.

### `def TestEntityCreation.test_entity_immutability(self) -> None`

Entities are immutable (frozen Pydantic models) to ensure data integrity.

Immutability prevents accidental in-place modifications. To modify an
entity, use model_copy(update={...}) to create a new instance, then
persist the change through the storage layer.

## `class TestEntityStorage`

Tests for InMemoryEntityStorage CRUD operations and query capabilities.

Verifies add/get/update/delete operations, batch retrieval, name-based
lookups (case-insensitive with synonym support), embedding-based similarity
search with configurable thresholds, and entity counting.

### `async def TestEntityStorage.test_add_and_get(self, entity_storage: InMemoryEntityStorage) -> None`

Storage supports basic add and retrieve by entity ID.

### `async def TestEntityStorage.test_get_nonexistent(self, entity_storage: InMemoryEntityStorage) -> None`

Retrieving a nonexistent entity ID returns None rather than raising an error.

### `async def TestEntityStorage.test_get_batch(self, entity_storage: InMemoryEntityStorage) -> None`

Batch retrieval returns entities in order, with None for missing IDs.

### `async def TestEntityStorage.test_find_by_name(self, entity_storage: InMemoryEntityStorage) -> None`

Name-based search is case-insensitive for robust entity matching.

### `async def TestEntityStorage.test_find_by_name_with_synonyms(self, entity_storage: InMemoryEntityStorage) -> None`

Name-based search includes synonyms, matching alternative entity names.

### `async def TestEntityStorage.test_find_by_embedding(self, entity_storage: InMemoryEntityStorage) -> None`

Embedding search returns entities with cosine similarity above threshold.

### `async def TestEntityStorage.test_find_by_embedding_threshold(self, entity_storage: InMemoryEntityStorage) -> None`

Embedding search excludes results below the similarity threshold (orthogonal vectors).

### `async def TestEntityStorage.test_update_entity(self, entity_storage: InMemoryEntityStorage) -> None`

Update replaces an existing entity with a modified copy (e.g., incremented usage count).

### `async def TestEntityStorage.test_update_nonexistent(self, entity_storage: InMemoryEntityStorage) -> None`

Updating a nonexistent entity returns False rather than creating it.

### `async def TestEntityStorage.test_delete_entity(self, entity_storage: InMemoryEntityStorage) -> None`

Delete removes an entity from storage so subsequent get returns None.

### `async def TestEntityStorage.test_count(self, entity_storage: InMemoryEntityStorage) -> None`

Count returns the total number of entities in storage.


<span id="user-content-teststestexportpy"></span>

# tests/test_export.py

Tests for exporting entities and documents to JSON files.

This module verifies:
- Entity export: Writing canonical (and optionally provisional) entities to
  a global entities.json file with all fields properly serialized
- Document export: Writing per-document JSON files containing relationships
  and provisional entities extracted from that document
- Full export: Generating both the global entities.json and per-document files
- Storage list_all methods: Pagination, status filtering, and document-based queries

> Tests for exporting entities and documents to JSON files.

This module verifies:
- Entity export: Writing canonical (and optionally provisional) entities to
  a global entities.json file with all fields properly serialized
- Document export: Writing per-document JSON files containing relationships
  and provisional entities extracted from that document
- Full export: Generating both the global entities.json and per-document files
- Storage list_all methods: Pagination, status filtering, and document-based queries


### `def orchestrator(tmp_path: Path) -> IngestionOrchestrator`

Create an orchestrator for export tests.

## `class TestExportEntities`

Tests for exporting entities to a JSON file.

By default, only canonical entities are exported to the global entities.json.
Provisional entities can be included via the include_provisional flag.

### `async def TestExportEntities.test_export_canonical_entities(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None`

Default export includes only canonical entities, excluding provisionals.

### `async def TestExportEntities.test_export_includes_provisional_when_requested(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None`

Export with include_provisional=True includes both canonical and provisional entities.

### `async def TestExportEntities.test_export_entity_fields(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None`

All entity fields are correctly serialized: ID, name, synonyms, embedding, canonical_ids, etc.

### `async def TestExportEntities.test_export_creates_parent_directories(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None`

Export automatically creates missing parent directories for the output file.

## `class TestExportDocument`

Tests for exporting per-document JSON files (paper_{doc_id}.json).

Each document export includes relationships sourced from that document
and provisional entities that originated from it.

### `async def TestExportDocument.test_export_document_relationships(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None`

Document export includes relationships whose source_documents include the document ID.

### `async def TestExportDocument.test_export_document_provisional_entities(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None`

Document export includes provisional entities whose source matches the document ID.

### `async def TestExportDocument.test_export_document_includes_title(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None`

Document export includes the document title metadata when present.

### `async def TestExportDocument.test_export_nonexistent_document(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None`

Export for a nonexistent document ID creates a file with zero relationships/entities.

## `class TestExportAll`

Tests for full export: global entities.json plus per-document files.

The export_all method generates a complete export of the knowledge graph:
entities.json with all canonical entities, and paper_{doc_id}.json for each
ingested document.

### `async def TestExportAll.test_export_all_creates_files(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None`

Full export creates entities.json and paper_{doc_id}.json for each document.

### `async def TestExportAll.test_export_all_returns_statistics(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None`

Full export returns statistics: output_dir, canonical_entities, documents_exported, per-document stats.

## `class TestListAllMethods`

Tests for storage list_all methods used by export functionality.

These methods support pagination (limit/offset), status filtering for entities,
and document-based queries for relationships.

### `async def TestListAllMethods.test_entity_list_all(self, orchestrator: IngestionOrchestrator) -> None`

list_all() returns all entities regardless of status.

### `async def TestListAllMethods.test_entity_list_all_with_status_filter(self, orchestrator: IngestionOrchestrator) -> None`

list_all(status='canonical'/'provisional') filters entities by status.

### `async def TestListAllMethods.test_entity_list_all_pagination(self, orchestrator: IngestionOrchestrator) -> None`

list_all(limit, offset) supports pagination for large result sets.

### `async def TestListAllMethods.test_relationship_get_by_document(self, orchestrator: IngestionOrchestrator) -> None`

get_by_document() returns relationships whose source_documents include the given document ID.

### `async def TestListAllMethods.test_relationship_list_all(self, orchestrator: IngestionOrchestrator) -> None`

list_all() returns all relationships in storage.

## `class TestExportBundleProvenance`

Tests for bundle export with provenance (mentions.jsonl, evidence.jsonl, summary fields).

### `async def TestExportBundleProvenance.test_write_bundle_with_provenance_writes_mentions_and_evidence(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None`

With provenance_accumulator populated, write_bundle writes mentions.jsonl and evidence.jsonl and sets manifest.

### `async def TestExportBundleProvenance.test_write_bundle_entity_rows_get_provenance_summary(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None`

Entity rows in entities.jsonl include first_seen_document, total_mentions, supporting_documents.

### `async def TestExportBundleProvenance.test_write_bundle_relationship_rows_get_evidence_summary(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None`

Relationship rows in relationships.jsonl include evidence_count, strongest_evidence_quote, evidence_confidence_avg.

### `async def TestExportBundleProvenance.test_write_bundle_without_provenance_no_mentions_or_evidence_files(self, orchestrator: IngestionOrchestrator, tmp_path: Path) -> None`

Without provenance_accumulator, no mentions.jsonl or evidence.jsonl and manifest has no mentions/evidence.


<span id="user-content-teststestgithashpy"></span>

# tests/test_git_hash.py

Tests for git hash utility in export module.

Tests the get_git_hash() function for version tracking in bundles.

> Tests for git hash utility in export module.

Tests the get_git_hash() function for version tracking in bundles.


## `class TestGetGitHash`

Test the get_git_hash() function.

### `def TestGetGitHash.test_returns_string_in_git_repo(self)`

Should return a string when in a git repository.

### `def TestGetGitHash.test_returns_short_hash_format(self)`

Hash should be short format (7+ characters, alphanumeric).

### `def TestGetGitHash.test_returns_none_when_git_unavailable(self)`

Should return None when git command fails.

### `def TestGetGitHash.test_returns_none_when_not_in_repo(self)`

Should return None when not in a git repository.

### `def TestGetGitHash.test_returns_none_on_timeout(self)`

Should return None when git command times out.

### `def TestGetGitHash.test_strips_whitespace_from_output(self)`

Should strip whitespace from git output.

### `def TestGetGitHash.test_uses_correct_git_command(self)`

Should call git rev-parse --short HEAD.


<span id="user-content-teststestingestionpy"></span>

# tests/test_ingestion.py

Tests for the two-pass document ingestion pipeline.

This module verifies the IngestionOrchestrator's ability to:
- Pass 1: Parse documents, extract entities, assign embeddings, resolve to
  existing entities or create new provisionals
- Pass 2: Extract relationships between entities from document content
- Store parsed documents, entities, and relationships in their respective storages
- Handle batch ingestion of multiple documents
- Validate entities and relationships against domain-specific schemas
- Detect merge candidates among canonical entities via embedding similarity

> Tests for the two-pass document ingestion pipeline.

This module verifies the IngestionOrchestrator's ability to:
- Pass 1: Parse documents, extract entities, assign embeddings, resolve to
  existing entities or create new provisionals
- Pass 2: Extract relationships between entities from document content
- Store parsed documents, entities, and relationships in their respective storages
- Handle batch ingestion of multiple documents
- Validate entities and relationships against domain-specific schemas
- Detect merge candidates among canonical entities via embedding similarity


### `def orchestrator(test_domain: SimpleDomainSchema, entity_storage: InMemoryEntityStorage, relationship_storage: InMemoryRelationshipStorage, document_storage: InMemoryDocumentStorage, document_parser: MockDocumentParser, entity_extractor: MockEntityExtractor, entity_resolver: MockEntityResolver, relationship_extractor: MockRelationshipExtractor, embedding_generator: MockEmbeddingGenerator) -> IngestionOrchestrator`

Create an ingestion orchestrator with mock components.

## `class TestSingleDocumentIngestion`

Tests for ingesting a single document through the two-pass pipeline.

Verifies that ingestion extracts entities, creates relationships, stores
the parsed document, generates embeddings for new entities, and increments
usage counts when the same entity is mentioned across multiple documents.

### `async def TestSingleDocumentIngestion.test_ingest_extracts_entities(self, orchestrator: IngestionOrchestrator, entity_storage: InMemoryEntityStorage) -> None`

Pass 1 extracts bracketed entity mentions and stores them in entity storage.

### `async def TestSingleDocumentIngestion.test_ingest_creates_relationships(self, orchestrator: IngestionOrchestrator, relationship_storage: InMemoryRelationshipStorage) -> None`

Pass 2 extracts relationships (edges) between entities found in the document.

### `async def TestSingleDocumentIngestion.test_ingest_stores_document(self, orchestrator: IngestionOrchestrator, document_storage: InMemoryDocumentStorage) -> None`

Ingestion stores the parsed document with its content and metadata.

### `async def TestSingleDocumentIngestion.test_ingest_generates_embeddings(self, orchestrator: IngestionOrchestrator, entity_storage: InMemoryEntityStorage) -> None`

New entities receive semantic embeddings for similarity-based operations.

### `async def TestSingleDocumentIngestion.test_ingest_increments_usage_count(self, orchestrator: IngestionOrchestrator, entity_storage: InMemoryEntityStorage) -> None`

Repeated entity mentions across documents increment the usage count.

Usage count tracks how often an entity appears and is used as a criterion
for promoting provisional entities to canonical status.

### `async def TestSingleDocumentIngestion.test_ingest_no_entities(self, orchestrator: IngestionOrchestrator) -> None`

Ingestion handles documents without extractable entities gracefully (no errors).

## `class TestBatchIngestion`

Tests for ingesting multiple documents in a single batch operation.

Verifies that batch ingestion processes multiple documents, aggregates
statistics across all documents, and continues processing remaining
documents even if individual documents encounter errors.

### `async def TestBatchIngestion.test_batch_ingest_multiple_documents(self, orchestrator: IngestionOrchestrator) -> None`

Batch ingestion processes multiple documents and aggregates entity counts.

### `async def TestBatchIngestion.test_batch_reports_per_document_results(self, orchestrator: IngestionOrchestrator) -> None`

Batch result includes individual extraction stats for each document.

### `async def TestBatchIngestion.test_batch_continues_on_error(self, orchestrator: IngestionOrchestrator) -> None`

Batch ingestion is fault-tolerant: failures in one document don't halt the batch.

## `class TestDomainValidation`

Tests for validating entities and relationships against domain schemas.

Each knowledge domain defines valid entity types and relationship predicates.
These tests verify that the orchestrator validates extracted data against
the configured domain schema.

### `async def TestDomainValidation.test_validates_entities(self, orchestrator: IngestionOrchestrator, test_domain: SimpleDomainSchema) -> None`

Entities with valid types (per domain schema) are accepted without errors.

### `async def TestDomainValidation.test_validates_relationships(self, orchestrator: IngestionOrchestrator) -> None`

Relationships with valid predicates (per domain schema) are accepted.

## `class TestMergeCandidateDetection`

Tests for detecting potential duplicate entities via embedding similarity.

Merge candidate detection identifies canonical entities with high embedding
similarity (cosine) that may represent the same real-world concept and
should be merged. Only canonical entities with embeddings are considered.

### `async def TestMergeCandidateDetection.test_find_merge_candidates_with_similar_entities(self, orchestrator: IngestionOrchestrator, entity_storage: InMemoryEntityStorage) -> None`

Entities with high cosine similarity (e.g., 'USA' and 'United States') are flagged.

Only canonical entities with embeddings are compared. Provisional entities
and entities without embeddings are excluded from merge candidate detection.

### `async def TestMergeCandidateDetection.test_find_merge_candidates_returns_empty_list(self, orchestrator: IngestionOrchestrator, entity_storage: InMemoryEntityStorage) -> None`

No merge candidates are returned when all entities are below the similarity threshold.


<span id="user-content-teststestloggingpy"></span>

# tests/test_logging.py

Tests for the PprintLogger and setup_logging functionality.

This module verifies:
- PprintLogger wraps standard logging.Logger correctly
- pprint parameter defaults to True and formats complex objects
- pprint=False uses simple string conversion
- All log levels support pprint formatting
- Delegation to underlying logger methods works
- Simple strings work with both pprint options
- Pydantic models use model_dump_json() when pprint=True

> Tests for the PprintLogger and setup_logging functionality.

This module verifies:
- PprintLogger wraps standard logging.Logger correctly
- pprint parameter defaults to True and formats complex objects
- pprint=False uses simple string conversion
- All log levels support pprint formatting
- Delegation to underlying logger methods works
- Simple strings work with both pprint options
- Pydantic models use model_dump_json() when pprint=True


## `class TestPprintLogger`

Tests for PprintLogger formatting and delegation.

### `def TestPprintLogger.test_pprint_formats_dict(self) -> None`

Test that pprint=True formats dictionaries nicely.

### `def TestPprintLogger.test_pprint_false_uses_str(self) -> None`

Test that pprint=False uses simple string conversion.

### `def TestPprintLogger.test_pprint_defaults_to_true(self) -> None`

Test that pprint parameter defaults to True.

### `def TestPprintLogger.test_simple_string_with_pprint(self) -> None`

Test that simple strings work with pprint=True.

### `def TestPprintLogger.test_all_log_levels_support_pprint(self) -> None`

Test that all log levels (debug, info, warning, error, critical) support pprint.

### `def TestPprintLogger.test_exception_logging(self) -> None`

Test that exception logging works with pprint.

### `def TestPprintLogger.test_delegates_to_underlying_logger(self) -> None`

Test that PprintLogger delegates other methods to underlying logger.

### `def TestPprintLogger.test_nested_structures_formatted(self) -> None`

Test that deeply nested structures are formatted correctly.

### `def TestPprintLogger.test_list_formatting(self) -> None`

Test that lists are formatted nicely with pprint.

### `def TestPprintLogger.test_pydantic_model_uses_model_dump_json(self) -> None`

Test that Pydantic models use model_dump_json() when pprint=True.

## `class TestModel(BaseModel)`


**Fields:**

```python
name: str
age: int
nested: dict[str, str]
```

### `def TestPprintLogger.test_pydantic_model_with_pprint_false(self) -> None`

Test that Pydantic models use str() when pprint=False.

## `class TestModel(BaseModel)`


**Fields:**

```python
name: str
```

## `class TestSetupLogging`

Tests for setup_logging function.

### `def TestSetupLogging.test_setup_logging_returns_pprint_logger(self) -> None`

Test that setup_logging returns a PprintLogger instance.

### `def TestSetupLogging.test_setup_logging_configures_handler(self) -> None`

Test that setup_logging properly configures handlers and formatters.

### `def TestSetupLogging.test_setup_logging_uses_caller_name(self) -> None`

Test that setup_logging uses the calling function's name as logger name.

### `def TestSetupLogging.test_setup_logging_does_not_duplicate_handlers(self) -> None`

Test that setup_logging doesn't add duplicate handlers on multiple calls.


<span id="user-content-teststestpass1llmpy"></span>

# tests/test_pass1_llm.py

Tests for Pass 1 LLM JSON parsing.

## `class TestParseJsonFromText`

Test _parse_json_from_text handles braces inside strings.

### `def TestParseJsonFromText.test_simple_object(self)`

Basic JSON object parses.

### `def TestParseJsonFromText.test_braces_in_string_value(self)`

Braces inside string values are ignored by depth counter.

### `def TestParseJsonFromText.test_closing_brace_in_string(self)`

Closing brace inside string does not end the object.

### `def TestParseJsonFromText.test_escaped_quote_in_string(self)`

Escaped quotes inside string do not toggle string state.

### `def TestParseJsonFromText.test_strips_markdown_code_block(self)`

Markdown code block wrapper is stripped.

### `def TestParseJsonFromText.test_nested_object_with_string_braces(self)`

Nested objects with braces in inner strings parse correctly.


<span id="user-content-teststestpipelineintegrationpy"></span>

# tests/test_pipeline_integration.py

Integration test for the full kgraph ingestion pipeline.

This test verifies the complete end-to-end flow:
1. Batch document ingestion
2. Provisional entity creation
3. Entity promotion based on usage thresholds
4. Merge candidate detection via embedding similarity

> Integration test for the full kgraph ingestion pipeline.

This test verifies the complete end-to-end flow:
1. Batch document ingestion
2. Provisional entity creation
3. Entity promotion based on usage thresholds
4. Merge candidate detection via embedding similarity


### `def orchestrator(test_domain: SimpleDomainSchema, entity_storage: InMemoryEntityStorage, relationship_storage: InMemoryRelationshipStorage, document_storage: InMemoryDocumentStorage, document_parser: MockDocumentParser, entity_extractor: MockEntityExtractor, entity_resolver: MockEntityResolver, relationship_extractor: MockRelationshipExtractor, embedding_generator: MockEmbeddingGenerator) -> IngestionOrchestrator`

Create an ingestion orchestrator with mock components.

## `class TestFullPipelineIntegration`

End-to-end integration tests for the complete ingestion pipeline.

These tests verify that batch ingestion, promotion, and merge candidate
detection work together correctly in a realistic workflow.

### `async def TestFullPipelineIntegration.test_batch_ingestion_creates_provisional_entities(self, orchestrator: IngestionOrchestrator, entity_storage: InMemoryEntityStorage) -> None`

Batch ingestion creates provisional entities from document mentions.

The mock entity extractor finds entities in [brackets]. This test verifies
that multiple documents are processed and unique entities are stored.

### `async def TestFullPipelineIntegration.test_repeated_mentions_increase_usage_count(self, orchestrator: IngestionOrchestrator, entity_storage: InMemoryEntityStorage) -> None`

Entities mentioned in multiple documents have higher usage counts.

### `async def TestFullPipelineIntegration.test_promotion_converts_high_usage_provisionals_to_canonical(self, orchestrator: IngestionOrchestrator, entity_storage: InMemoryEntityStorage) -> None`

Entities meeting usage threshold are promoted to canonical status.

The test domain promotes entities with usage_count >= 2.

### `async def TestFullPipelineIntegration.test_merge_candidates_detected_by_embedding_similarity(self, orchestrator: IngestionOrchestrator, entity_storage: InMemoryEntityStorage) -> None`

Similar canonical entities are identified as merge candidates.

Entities with high cosine similarity in their embeddings are flagged
as potential duplicates that may need manual review or merging.

### `async def TestFullPipelineIntegration.test_full_pipeline_ingestion_promotion_merge_detection(self, orchestrator: IngestionOrchestrator, entity_storage: InMemoryEntityStorage) -> None`

Complete pipeline: ingest documents, promote entities, detect merge candidates.

This test exercises the full workflow a user would follow:
1. Ingest a batch of documents
2. Run promotion to elevate high-usage entities
3. Add similar canonical entities
4. Detect merge candidates among canonicals


<span id="user-content-teststestprogresstrackerpy"></span>

# tests/test_progress_tracker.py

Tests for ProgressTracker (kgraph.progress).

Tests progress tracking and reporting functionality.

> Tests for ProgressTracker (kgraph.progress).

Tests progress tracking and reporting functionality.


## `class TestProgressTrackerBasics`

Test basic ProgressTracker functionality.

### `def TestProgressTrackerBasics.test_initial_state(self)`

Tracker should start with zero completed.

### `def TestProgressTrackerBasics.test_increment_increases_completed(self)`

Increment should increase completed count.

### `def TestProgressTrackerBasics.test_percentage_calculation(self)`

Report should calculate correct percentage.

### `def TestProgressTrackerBasics.test_percentage_zero_total(self)`

Report should handle zero total gracefully.

### `def TestProgressTrackerBasics.test_report_shows_progress_count(self)`

Report should show completed/total count.

## `class TestProgressTrackerTiming`

Test ProgressTracker timing-related functionality.

### `def TestProgressTrackerTiming.test_rate_calculation(self)`

Report should calculate processing rate.

### `def TestProgressTrackerTiming.test_elapsed_time_shown(self)`

Report should show elapsed time.

### `def TestProgressTrackerTiming.test_estimated_remaining_shown(self)`

Report should show estimated remaining time when not complete.

## `class TestProgressTrackerAutoReport`

Test automatic reporting based on interval.

### `def TestProgressTrackerAutoReport.test_no_auto_report_before_interval(self)`

Should not auto-report before interval elapses.

### `def TestProgressTrackerAutoReport.test_auto_report_after_interval(self)`

Should auto-report when interval elapses.

## `class TestProgressTrackerEdgeCases`

Test edge cases for ProgressTracker.

### `def TestProgressTrackerEdgeCases.test_large_total(self)`

Should handle large totals.

### `def TestProgressTrackerEdgeCases.test_custom_report_interval(self)`

Should respect custom report interval.

### `def TestProgressTrackerEdgeCases.test_completed_equals_total(self)`

Should handle 100% completion.


<span id="user-content-teststestpromotionmergepy"></span>

# tests/test_promotion_merge.py

Tests for entity promotion (provisional to canonical) and merging duplicate entities.

This module verifies:
- Promotion: Changing provisional entities to canonical status when they meet
  usage count and confidence thresholds defined by the domain configuration
- Merge: Combining duplicate canonical entities, consolidating their synonyms,
  summing usage counts, and updating relationship references

> Tests for entity promotion (provisional to canonical) and merging duplicate entities.

This module verifies:
- Promotion: Changing provisional entities to canonical status when they meet
  usage count and confidence thresholds defined by the domain configuration
- Merge: Combining duplicate canonical entities, consolidating their synonyms,
  summing usage counts, and updating relationship references


### `def orchestrator(test_domain: SimpleDomainSchema, entity_storage: InMemoryEntityStorage, relationship_storage: InMemoryRelationshipStorage, document_storage: InMemoryDocumentStorage, document_parser: MockDocumentParser, entity_extractor: MockEntityExtractor, entity_resolver: MockEntityResolver, relationship_extractor: MockRelationshipExtractor, embedding_generator: MockEmbeddingGenerator) -> IngestionOrchestrator`

Create an ingestion orchestrator with mock components.

## `class TestEntityPromotion`

Tests for promoting provisional entities to canonical status.

Provisional entities become canonical when they meet domain-specific
thresholds for usage count and confidence. Promotion assigns a new
canonical ID and updates the storage reference.

### `async def TestEntityPromotion.test_promote_updates_status(self, entity_storage: InMemoryEntityStorage) -> None`

Promotion changes status from PROVISIONAL to CANONICAL and assigns a new entity ID.

### `async def TestEntityPromotion.test_promote_updates_storage_reference(self, entity_storage: InMemoryEntityStorage) -> None`

Promotion replaces the old provisional ID with the new canonical ID in storage.

### `async def TestEntityPromotion.test_promote_nonexistent_returns_none(self, entity_storage: InMemoryEntityStorage) -> None`

Attempting to promote a nonexistent entity ID returns None.

### `async def TestEntityPromotion.test_find_provisional_for_promotion(self, entity_storage: InMemoryEntityStorage) -> None`

Find provisionals meeting min_usage and min_confidence thresholds for promotion.

Only provisional entities that exceed both the usage count and confidence
thresholds are returned as promotion candidates. Already-canonical entities
and those below either threshold are excluded.

### `async def TestEntityPromotion.test_run_promotion(self, orchestrator: IngestionOrchestrator, entity_storage: InMemoryEntityStorage) -> None`

Orchestrator run_promotion() finds and promotes all eligible provisional entities.

## `class TestEntityMerging`

Tests for merging duplicate canonical entities into a single target entity.

Merging consolidates synonyms from source entities, sums usage counts,
removes source entities from storage, and updates all relationship
references from source IDs to the target ID.

### `async def TestEntityMerging.test_merge_combines_synonyms(self, entity_storage: InMemoryEntityStorage) -> None`

Merge adds the source entity's name and synonyms to the target's synonym list.

### `async def TestEntityMerging.test_merge_combines_usage_counts(self, entity_storage: InMemoryEntityStorage) -> None`

Merge sums the usage counts of all source entities into the target.

### `async def TestEntityMerging.test_merge_removes_source_entities(self, entity_storage: InMemoryEntityStorage) -> None`

Merge deletes source entities from storage after consolidation.

### `async def TestEntityMerging.test_merge_nonexistent_target_fails(self, entity_storage: InMemoryEntityStorage) -> None`

Merge fails (returns False) if the target entity ID does not exist.

### `async def TestEntityMerging.test_merge_updates_relationships(self, orchestrator: IngestionOrchestrator, entity_storage: InMemoryEntityStorage, relationship_storage: InMemoryRelationshipStorage) -> None`

Merge rewrites all relationship subject_id/object_id references from source to target.

Relationships that previously referenced a source entity (as subject or object)
are updated to reference the target entity, maintaining graph connectivity.


<span id="user-content-teststestprovenancepy"></span>

# tests/test_provenance.py

Tests for provenance accumulation during ingestion.

Covers ProvenanceAccumulator: add_mention, add_evidence, counts, and
that accumulated data is exposed for export.

> Tests for provenance accumulation during ingestion.

Covers ProvenanceAccumulator: add_mention, add_evidence, counts, and
that accumulated data is exposed for export.


## `class TestProvenanceAccumulator`

ProvenanceAccumulator records mentions and evidence for bundle export.

### `def TestProvenanceAccumulator.test_init_empty(self) -> None`

New accumulator has no mentions or evidence.

### `def TestProvenanceAccumulator.test_add_mention_appends_and_increments_count(self) -> None`

add_mention appends a MentionRow and mention_count increases.

### `def TestProvenanceAccumulator.test_add_evidence_appends_and_increments_count(self) -> None`

add_evidence appends an EvidenceRow and evidence_count increases.

### `def TestProvenanceAccumulator.test_mentions_and_evidence_independent(self) -> None`

Mention and evidence lists are independent; adding one does not affect the other.

### `def TestProvenanceAccumulator.test_mentions_exposed_for_export(self) -> None`

Accumulator exposes mentions list for exporter to iterate.


<span id="user-content-teststestrelationshipspy"></span>

# tests/test_relationships.py

Tests for relationship (edge) creation and in-memory storage operations.

This module verifies:
- Relationship instantiation with subject, predicate, and object
- Relationship attributes: metadata, source documents, immutability
- InMemoryRelationshipStorage CRUD operations (add, find, delete)
- Queries by subject, object, and triple (subject-predicate-object)
- Updating entity references when entities are merged

> Tests for relationship (edge) creation and in-memory storage operations.

This module verifies:
- Relationship instantiation with subject, predicate, and object
- Relationship attributes: metadata, source documents, immutability
- InMemoryRelationshipStorage CRUD operations (add, find, delete)
- Queries by subject, object, and triple (subject-predicate-object)
- Updating entity references when entities are merged


## `class TestRelationshipCreation`

Tests for creating relationship (edge) instances.

Relationships represent directed edges in the knowledge graph, connecting
a subject entity to an object entity via a predicate (edge type).

### `def TestRelationshipCreation.test_create_relationship(self) -> None`

Relationships have a subject_id, predicate, and object_id forming a directed edge.

### `def TestRelationshipCreation.test_relationship_with_metadata(self) -> None`

Relationships store domain-specific metadata (e.g., evidence_type, section).

### `def TestRelationshipCreation.test_relationship_with_source_documents(self) -> None`

Relationships track which documents they were extracted from via source_documents.

### `def TestRelationshipCreation.test_relationship_immutability(self) -> None`

Relationships are immutable (frozen Pydantic models) to ensure data integrity.

## `class TestRelationshipStorage`

Tests for InMemoryRelationshipStorage CRUD operations and queries.

Verifies add/find/delete operations, queries by subject or object entity,
optional predicate filtering, entity reference updates for merging, and counting.

### `async def TestRelationshipStorage.test_add_and_find(self, relationship_storage: InMemoryRelationshipStorage) -> None`

Storage supports add and find_by_triple (exact subject-predicate-object lookup).

### `async def TestRelationshipStorage.test_find_nonexistent_triple(self, relationship_storage: InMemoryRelationshipStorage) -> None`

find_by_triple returns None when no matching relationship exists.

### `async def TestRelationshipStorage.test_get_by_subject(self, relationship_storage: InMemoryRelationshipStorage) -> None`

get_by_subject returns all relationships where the given entity is the subject.

### `async def TestRelationshipStorage.test_get_by_subject_with_predicate(self, relationship_storage: InMemoryRelationshipStorage) -> None`

get_by_subject with predicate filter returns only matching edge types.

### `async def TestRelationshipStorage.test_get_by_object(self, relationship_storage: InMemoryRelationshipStorage) -> None`

get_by_object returns all relationships where the given entity is the object.

### `async def TestRelationshipStorage.test_update_entity_references(self, relationship_storage: InMemoryRelationshipStorage) -> None`

update_entity_references rewrites subject/object IDs when entities are merged.

This is called during entity merging to update all relationships that
reference the source entity to instead reference the target entity.

### `async def TestRelationshipStorage.test_delete_relationship(self, relationship_storage: InMemoryRelationshipStorage) -> None`

delete removes a relationship by its triple (subject, predicate, object).

### `async def TestRelationshipStorage.test_delete_nonexistent(self, relationship_storage: InMemoryRelationshipStorage) -> None`

delete returns False when the specified triple does not exist.

### `async def TestRelationshipStorage.test_count(self, relationship_storage: InMemoryRelationshipStorage) -> None`

count returns the total number of relationships in storage.


<span id="user-content-teststeststreamingpy"></span>

# tests/test_streaming.py

Tests for streaming pipeline components.

Tests document chunking, streaming entity extraction, and windowed relationship
extraction capabilities.

> Tests for streaming pipeline components.

Tests document chunking, streaming entity extraction, and windowed relationship
extraction capabilities.


### `def make_simple_document(document_id: str, content: str) -> SimpleDocument`

Helper to create SimpleDocument with required fields.

## `class TestDocumentChunk`

Test DocumentChunk model.

### `def TestDocumentChunk.test_chunk_creation(self)`

Test creating a document chunk.

### `def TestDocumentChunk.test_chunk_immutability(self)`

Test that chunks are immutable (frozen=True).

## `class TestChunkingConfig`

Test ChunkingConfig model.

### `def TestChunkingConfig.test_default_config(self)`

Test default chunking configuration.

### `def TestChunkingConfig.test_custom_config(self)`

Test custom chunking configuration.

### `def TestChunkingConfig.test_config_immutability(self)`

Test that config is immutable (frozen=True).

## `class TestWindowedDocumentChunker`

Test WindowedDocumentChunker implementation.

### `async def TestWindowedDocumentChunker.test_single_chunk_document(self)`

Test chunking a document that fits in a single chunk.

### `async def TestWindowedDocumentChunker.test_multiple_chunks_no_overlap(self)`

Test chunking a document into multiple non-overlapping chunks.

### `async def TestWindowedDocumentChunker.test_multiple_chunks_with_overlap(self)`

Test chunking with overlap between chunks.

### `async def TestWindowedDocumentChunker.test_respect_sentence_boundaries(self)`

Test chunking that respects sentence boundaries.

### `async def TestWindowedDocumentChunker.test_chunk_metadata_preserved(self)`

Test that document ID is preserved in chunks.

### `async def TestWindowedDocumentChunker.test_chunk_indices_sequential(self)`

Test that chunk indices are sequential.

## `class TestBatchingEntityExtractor`

Test BatchingEntityExtractor implementation.

### `async def TestBatchingEntityExtractor.test_extract_from_single_chunk(self)`

Test extracting entities from a single chunk.

### `async def TestBatchingEntityExtractor.test_extract_from_multiple_chunks(self)`

Test extracting entities from multiple chunks.

### `async def TestBatchingEntityExtractor.test_offset_adjustment(self)`

Test that entity offsets are adjusted for chunk position.

### `async def TestBatchingEntityExtractor.test_streaming_iteration(self)`

Test that results are yielded incrementally.

## `class TestWindowedRelationshipExtractor`

Test WindowedRelationshipExtractor implementation.

### `async def TestWindowedRelationshipExtractor.test_extract_from_single_window(self)`

Test extracting relationships from a single window.

### `async def TestWindowedRelationshipExtractor.test_deduplication_across_windows(self)`

Test that duplicate relationships are deduplicated across overlapping windows.

### `async def TestWindowedRelationshipExtractor.test_empty_window(self)`

Test handling windows with no entities.

### `async def TestWindowedRelationshipExtractor.test_single_entity_window(self)`

Test handling windows with only one entity.

## `class TestIntegrationStreamingPipeline`

Integration tests for streaming pipeline.

### `async def TestIntegrationStreamingPipeline.test_full_streaming_pipeline(self)`

Test complete streaming pipeline: chunk -> extract entities -> extract relationships.

### `async def TestIntegrationStreamingPipeline.test_large_document_chunking(self)`

Test handling very large documents with many chunks.


