#!/usr/bin/env python3
"""Retired. This repository is the source of truth for soulstone.co.

The Ploy preview is no longer synced. All page copy lives in the committed
HTML and in the compiled bundles under _ploy_static/_astro/*.js, and the blog,
tag pages, sitemap and RSS feed are produced by generator/build.py.

Edit the HTML and bundles directly, then run:

    python3 generator/build.py
    python3 generator/lint.py
"""
import sys

sys.exit(
    "sync_from_ploy.py is retired: the repository is the source of truth. "
    "Edit the committed HTML and _ploy_static bundles directly, then run "
    "generator/build.py and generator/lint.py. See generator/README.md."
)
