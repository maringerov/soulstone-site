# Blog generator

Static site, deployed from `main` by GitHub Pages. This repository is the
source of truth: all page copy lives in the committed HTML and in the compiled
bundles under `_ploy_static/_astro/*.js`. The generator turns Markdown posts
into pages that match the existing design and rebuilds everything that depends
on the list of posts.

Editing a static page (`/`, `/faq`, `/results`, `/shopify-plus-architecture`):
change the text in both the page HTML and the matching bundle, or the copy
reverts when the React island hydrates. `generator/lint.py` catches dashes in
both places but not text drift between them.

## Writing a post

1. Add `posts/YYYY-MM-DD-short-name.md`:

   ```markdown
   ---
   title: "Post title"
   slug: url-slug
   description: "One or two sentences for the card, meta description and RSS."
   date: 2026-10-19
   tags: [shopify, product-data]
   draft: false
   ---

   Body in Markdown. Tables and fenced code blocks work.
   ```

   `slug` and `updated` are optional. `draft: true` hides the post unless the
   build runs with `--include-drafts`.

2. Run the build and commit everything it touched:

   ```sh
   pip install -r generator/requirements.txt
   python3 generator/build.py
   ```

3. The build fails if any Markdown post, template, `site.json` or legacy post
   contains an em dash or an en dash. Use a comma, colon or full stop.
   `generator/lint.py` applies the same rule to every shipped `.html`, `.js`,
   `.css`, `.md`, `.txt`, `.xml`, `.json`, `.yml` and `.py` file.

## What the build writes

| Output | Source |
|---|---|
| `blog/<slug>/index.html` | `posts/*.md` and `generator/templates/post.html` |
| `blog/index.html`, `tag/<tag>/index.html` | all posts (Markdown and legacy HTML) |
| `sitemap-0.xml`, `sitemap-index.xml`, `rss.xml` | all posts plus `static_pages` in `site.json` |
| the shared head block on every page | `generator/site.json` (og:image, twitter card, RSS link, ProfessionalService and Person JSON-LD) |
| the author box on every post | `author` and `profiles` in `site.json` |

The five posts that predate the generator have no Markdown source. They are
read for their metadata and kept as they are, apart from the author box and
the shared head block. Edit their body copy directly in `blog/<slug>/index.html`.

Tag pages with fewer than `min_tag_posts_in_sitemap` posts stay online but
are left out of the sitemap and marked `noindex, follow`.

## Checks

```sh
python3 generator/build.py --check   # committed output matches a fresh build
python3 generator/lint.py            # dashes in all shipped HTML/JS/text, titles, meta, JSON-LD, sitemap, RSS
```

Both run in `.github/workflows/build.yml` on every push and pull request.

## Placeholders

`profiles.shopify_partner` and `profiles.booking` in `site.json` are marked
`PLACEHOLDER` until the real URLs exist. They appear verbatim in the JSON-LD
and the lint prints a warning for them. The landing page
`/shopify-plus-developer-amsterdam` carries a visible pricing placeholder for
the same reason.

## Ploy sync (retired)

`scripts/sync_from_ploy.py` is a no-op that exits with a message. The Ploy
preview is no longer synced; the repository is the source of truth.
