#!/usr/bin/env python3
"""Inject a book's nav section into the main mkdocs.yml.

Usage: inject_book_nav.py <bundle-mkdocs.yml> <site-mkdocs.yml> <section-title> <path-prefix>

Reads the nav from the book bundle's mkdocs.yml, prefixes every page path with
<path-prefix>/, and inserts the result as a top-level nav section named
<section-title> immediately before the 'Books' entry in the site's mkdocs.yml.
Rewrites the site mkdocs.yml in place.
"""

import sys
import yaml


def prefix_paths(nav, prefix):
    result = []
    for item in nav:
        new_item = {}
        for k, v in item.items():
            if isinstance(v, str):
                new_item[k] = prefix + v
            elif isinstance(v, list):
                new_item[k] = prefix_paths(v, prefix)
        result.append(new_item)
    return result


def main():
    if len(sys.argv) != 5:
        print(f"Usage: {sys.argv[0]} <bundle-mkdocs.yml> <site-mkdocs.yml> <section-title> <path-prefix>", file=sys.stderr)
        sys.exit(1)

    bundle_yml, site_yml, section_title, path_prefix = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

    with open(bundle_yml) as f:
        bundle_config = yaml.safe_load(f)
    bundle_nav = bundle_config.get("nav")
    if not bundle_nav:
        print(f"Error: no 'nav' section found in {bundle_yml}", file=sys.stderr)
        sys.exit(1)
    prefixed_nav = prefix_paths(bundle_nav, path_prefix + "/")

    with open(site_yml) as f:
        config = yaml.safe_load(f)
    nav = config.get("nav", [])
    books_idx = next(
        (i for i, e in enumerate(nav) if isinstance(e, dict) and "Books" in e),
        len(nav),
    )
    nav.insert(books_idx, {section_title: prefixed_nav})
    config["nav"] = nav
    with open(site_yml, "w") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


if __name__ == "__main__":
    main()
