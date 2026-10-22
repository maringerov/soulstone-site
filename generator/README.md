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

   `date` is the day the post goes live, never later. A post dated after the
   build date (today in Europe/Amsterdam) is skipped with a warning: no page,
   and nothing in the blog index, tag pages, sitemap, RSS or `llms.txt`. Every
   sitemap `lastmod` is capped at the build date. `generator/lint.py` fails on
   any built page whose `datePublished`, or any sitemap `lastmod`, is in the
   future.

2. Run the build and commit everything it touched:

   ```sh
   pip install -r generator/requirements.txt
   python3 generator/build.py
   ```

3. The build fails if any Markdown post, template, `site.json` or legacy post
   contains an em dash or an en dash. Use a comma, colon or full stop.
   `generator/lint.py` applies the same rule to every shipped `.html`, `.js`,
   `.css`, `.md`, `.txt`, `.xml`, `.json`, `.yml`, `.py`, `.svg` and
   `.webmanifest` file.

4. The build also fails on banned words (`BANNED_WORDS` in `build.py`,
   case-insensitive, hyphenated spellings included). The site describes Marin
   as an independent developer and never uses the usual label for a
   self-employed contractor; write "independent Shopify Plus developer", "I
   work directly with brands", or leave the label out. `generator/lint.py`
   scans the same files as the dash check for the same words.

## What the build writes

| Output | Source |
|---|---|
| `blog/<slug>/index.html` | `posts/*.md` and `generator/templates/post.html`, plus one in-article Win Chat promo card (`ARTICLE_PROMO` in `build.py`) placed by `promo_position()`; legacy posts get the same card in place |
| `<path>/index.html` (for example `privacy/index.html`) | `pages/*.md` and `generator/templates/page.html` |
| `blog/index.html`, `tag/<tag>/index.html` | all posts (Markdown and legacy HTML) |
| `sitemap-0.xml`, `sitemap-index.xml`, `rss.xml` | all posts plus `static_pages` in `site.json` and every `pages/*.md` |
| `llms.txt` | `generator/templates/llms.txt` with the Journal list rendered from all posts |
| `site.webmanifest` | `site_name`, `business.description` and `icons` in `site.json` plus `MANIFEST_ICONS` in `build.py` |
| the shared head block on every page | `generator/site.json` (og:image, twitter card, RSS link, favicon and app icon links, manifest, theme-color, ProfessionalService and Person JSON-LD) plus the mobile menu styles and script (`NAV_CSS`, `NAV_NOSCRIPT_CSS`, `NAV_JS` in `build.py`) |
| the analytics block on every page | `analytics.ga4_measurement_id` in `site.json` plus the consent bar styles and script (`CONSENT_CSS`, `CONSENT_JS` in `build.py`) |
| the author box on every post | `author` and `profiles` in `site.json` |

## Static pages in Markdown

`pages/<name>.md` renders to `<path>/index.html` through
`generator/templates/page.html`. Front matter needs `title`, `description`,
`path` (for example `/privacy`) and `lastmod` (used in the sitemap); `eyebrow`
is optional. The body is Markdown and may contain inline HTML. The only page so
far is `pages/privacy.md`.

## Analytics and cookie consent

The build writes a second shared block, `<!-- soulstone-analytics:start -->` to
`<!-- soulstone-analytics:end -->`, right after the viewport meta on every page.
It holds the GA4 tag (`G-9HHW5MMJCP`, from `analytics.ga4_measurement_id` in
`site.json`) with a Consent Mode default that denies analytics storage, ad
storage, ad user data and ad personalisation, followed by the consent bar styles
and script. Only `analytics_storage` is ever granted; the ad signals stay denied.

The choice lives in `localStorage` under `ss_consent` (`granted` or `denied`).
On load the GA snippet grants analytics storage if the value is `granted`. The
consent script creates the bar (`#ss-consent`, `role="region"`, two buttons,
a link to `/privacy`) only when no choice is stored, sets
`--ss-consent-h` and `html.ss-consent-open` so the body gets bottom padding and
the mobile menu panel stays clear of the bar, and removes it once a button is
pressed. Any element with `data-ss-consent-reset` (the "Change cookie choice"
link on `/privacy`) clears the stored value, sets analytics storage back to
denied and shows the bar again. With JavaScript off there is no bar and the tag
never loads.

## Favicon and app icons

The mark is an S monogram drawn as vector paths (no font reference) in the
site's accent green `#59EC85` (`--ploy-accent-primary`) on a rounded square in
the page background `#080F0C` (`--ploy-background-primary`), so it reads on
light and dark browser tabs. The files live at the repository root and are
plain assets, not build output:

| File | Use |
|---|---|
| `favicon.svg` | modern browsers, `rel="icon"` with `type="image/svg+xml"` |
| `favicon.ico` | 16, 32 and 48 px fallback |
| `apple-touch-icon.png` | 180 px, full-bleed background (iOS applies its own mask) |
| `icon-192.png`, `icon-512.png` | manifest icons, rounded square with transparent corners |
| `icon-192-maskable.png`, `icon-512-maskable.png` | manifest `purpose: maskable`, mark kept inside the safe zone |

The build writes the link tags, `theme-color` and `site.webmanifest`, and
strips the Ploy starter `<link rel="icon" type="image/x-icon">` from every
page. `theme_color`, `background_color`, `short_name` and `logo` (the
ProfessionalService `logo` in the JSON-LD, `/icon-512.png`) come from `icons`
in `site.json`. The lint fails if a page lacks the icon links or a referenced
icon file is missing.

To regenerate the icon files after changing the mark, colours or sizes:

```sh
pip install -r generator/requirements-icons.txt
python3 generator/icons.py            # writes the icon files to the repository root
python3 generator/icons.py --previews /tmp/previews   # also favicon-512.png and favicon-sizes.png
```

The five posts that predate the generator have no Markdown source. They are
read for their metadata and kept as they are, apart from the author box and
the shared head block. Edit their body copy directly in `blog/<slug>/index.html`.

Tag pages with fewer than `min_tag_posts_in_sitemap` posts stay online but
are left out of the sitemap and marked `noindex, follow`.

## Site header and mobile menu

The header markup is not generated. It lives in every static page, in the
three page templates and in the React island
`_ploy_static/_astro/site-header.HZhl7zMm.js`, which renders the same tree on
hydration. Change all three together or the header reverts on load.

Below 64rem (Tailwind `lg`) the desktop links are hidden and a `Menu` button
(`.ss-nav-toggle`, `aria-expanded`, `aria-controls="site-menu"`) opens the
`#site-menu` panel. The build writes the styles, a `<noscript>` fallback that
shows the links inline, and a short vanilla script into the shared head block.
The script only toggles `data-state` on the panel and `aria-expanded` on the
button (click, Enter and Space via the native button, Escape closes and
returns focus, a tap on a link or outside the panel closes). React does not own
that state, so hydration and the scroll re-render leave it alone. The lint
fails if a page lacks the toggle, the panel or the script.

The `Win Chat` link (`/win-chat/`) is the last item in both menus. It carries
the same classes as its neighbours; the accent colour and the dot come from
`NAV_CSS`, keyed on the href, so the server markup and the hydrated tree stay
identical. It lives in the same three places as the rest of the header (static
pages, templates, the `$o` default links in the SiteHeader bundle and the
`links:` props in the three `page.*.js` bundles). The lint fails if a page
lacks it in either menu.

## In-article Win Chat promo

Every post carries one promo card (`ARTICLE_PROMO` in `build.py`, wrapped in
`<!-- win-chat-promo:start -->` / `:end -->` so a rebuild replaces it in
place). `promo_position()` puts it at the section break nearest the middle of
the body: directly before the top-level H2 whose start is closest to 50% of the
body length, never before the end of the second paragraph and never after the
last H2. Posts with fewer than two H2s get it after the top-level paragraph
nearest the midpoint under the same limits. Blocks inside lists, tables,
quotes and code are ignored. The card styles (`ARTICLE_PROMO_CSS`) ship in the
shared head block. The lint fails if a post has anything other than exactly one
card, or if the card turns up on a page that is not a post.

## Promo banner

The build writes the Win Chat promo banner styles and script (`PROMO_CSS`,
`PROMO_JS` in `build.py`) into the shared head block. The script skips
`/win-chat/` itself and anyone who has dismissed the banner (localStorage
`ss_promo_winchat`), otherwise it adds `.ss-promo-open` to the html element
before first paint (moving the fixed header down and padding the body) and
inserts the `#ss-promo` strip at the top of the body on `DOMContentLoaded`.
The link and the dismiss button are both at least 44px tall. The consent bar
sits at the bottom of the viewport, so the two never overlap. With JavaScript
off there is no banner. The lint fails if a page lacks the script.

## Site footer

The footer markup is not generated either. It lives in every static page, in
the page templates and in the React island
`_ploy_static/_astro/site-footer.DULiVXzC.js`. Change the HTML and the bundle
together (the `Privacy` link in the Studio column is an example) or hydration
replaces the footer with the bundle's version. The lint fails if a page has no
footer link to `/privacy`.

## Trailing slashes

GitHub Pages serves `<dir>/index.html` at `<dir>/` and 301-redirects the
slashless form, so the URL that answers 200 for every page ends in a slash
(`/faq/`, `/blog/<slug>/`, `/tag/<tag>/`; the homepage is `/`). `site.json`,
front matter and the `static_pages` list keep the short form (`/faq`,
`/shopify-plus-developer-amsterdam#services`); `Site.url()` and `page_path()`
in `build.py` add the slash and keep fragments after it. The shared head pass
sets every page's canonical and `og:url` to its own trailing-slash URL and
rewrites internal `href`s, the serialized header links in the astro-island
props and the `url`, `@id`, `item` and `mainEntityOfPage` fields in the
JSON-LD, so Markdown posts and static pages do not need to get it right by
hand. Files with an extension (`/rss.xml`, `/favicon.svg`) keep their name.
The Astro bundles under `_ploy_static/_astro/` are not rewritten; their
`href:` values are edited by hand and the lint checks them.

## Checks

```sh
python3 generator/build.py --check   # committed output matches a fresh build
python3 generator/lint.py            # dashes and banned words in all shipped HTML/JS/text, titles, meta, JSON-LD, sitemap, RSS, llms.txt, GA4 tag, consent script, privacy link, trailing slashes
```

The lint fails if any canonical, `og:url`, hreflang, JSON-LD URL, sitemap
`<loc>`, RSS `<link>` or `<guid>`, `llms.txt` link or internal `href` (pages,
templates and bundles) points at an HTML page without the trailing slash, or
if a page's canonical is not its own URL.

Both run in `.github/workflows/build.yml` on every push and pull request.

## Placeholders

`profiles.shopify_partner` and `profiles.booking` in `site.json` are marked
`PLACEHOLDER` until the real URLs exist. The build leaves them out of the
JSON-LD (no `sameAs` entry, no `ReserveAction`) and the lint prints a warning
for them. The landing page
`/shopify-plus-developer-amsterdam` carries a visible pricing placeholder for
the same reason.

## Ploy sync (retired)

`scripts/sync_from_ploy.py` is a no-op that exits with a message. The Ploy
preview is no longer synced; the repository is the source of truth.
