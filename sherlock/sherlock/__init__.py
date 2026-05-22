"""Sherlock Holmes knowledge graph pipeline.

Dense typed extraction from "A Scandal in Bohemia" and other Holmes stories.
Follows the medlit pattern: domain_spec.py as single source of truth,
LLM-based extraction, dedup/merge, kgbundle output.
"""
