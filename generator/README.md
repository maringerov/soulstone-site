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

   `faq_schema: true` adds a `FAQPage` node to the post's JSON-LD, next to the
   `Article` and `BreadcrumbList`. The questions come from the last H2 whose
   text contains "FAQ" or "Questions": every H3 under it is a question and the
   text up to the next H3 (or the next H2) is the answer, flattened to plain
   text. The build fails if the flag is set and that section or its H3s are
   missing. Without the flag the FAQ section is plain copy, as before.

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
| `blog/<slug>/index.html` | `posts/*.md` and `generator/templates/post.html`, plus one in-article Win Chat promo card (`ARTICLE_PROMO` in `build.py`) placed by `promo_position()` and one teardown card (`TEARDOWN_CTA`) before the author box; legacy posts get both cards in place |
| `<path>/index.html` (for example `privacy/index.html`) | `pages/*.md` and `generator/templates/page.html` |
| `blog/index.html`, `tag/<tag>/index.html` | all posts (Markdown and legacy HTML) |
| the teardown request form between `<!-- teardown-form:start -->` / `:end -->` on `/` and `/teardown/` | `TEARDOWN_FORM` in `build.py`, see Teardown request form below |
| `sitemap-0.xml`, `sitemap-index.xml`, `rss.xml` | all posts plus `static_pages` in `site.json` and every `pages/*.md` |
| `llms.txt` | `generator/templates/llms.txt` with the Journal list rendered from all posts |
| `site.webmanifest` | `site_name`, `business.description` and `icons` in `site.json` plus `MANIFEST_ICONS` in `build.py` |
| the shared head block on every page | `generator/site.json` (og:image, see Open Graph card below, twitter card, RSS link, favicon and app icon links, manifest, theme-color, ProfessionalService and Person JSON-LD) plus the mobile menu styles and script (`NAV_CSS`, `NAV_NOSCRIPT_CSS`, `NAV_JS` in `build.py`) |
| the analytics block on every page | `analytics.ga4_measurement_id` in `site.json` plus the consent bar styles and script (`CONSENT_CSS`, `CONSENT_JS` in `build.py`) |
| the author box on every post | `author` and `profiles` in `site.json` |

## Static pages in Markdown

`pages/<name>.md` renders to `<path>/index.html` through
`generator/templates/page.html`. Front matter needs `title`, `description`,
`path` (for example `/privacy`) and `lastmod` (used in the sitemap); `eyebrow`
is optional. The body is Markdown and may contain inline HTML. The pages so far
are `pages/privacy.md` and `pages/teardown.md`.

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

## Open Graph card

`assets/og-default-v2.jpg` (1200 x 630) is the image behind `og:image` and
`twitter:image` on every page, the RSS channel image and the `image` of the
ProfessionalService and Article JSON-LD. It is a plain asset, written by
`generator/og_image.py`: the dial texture from
`assets/c6b425b1-moser-fume-dial-clean.png` scaled to cover the canvas and
pulled down to near black under a gradient, with the copy set in the site's
own web fonts from `_ploy_static/_astro` (Playfair Display for the name,
Manrope for the strapline, JetBrains Mono for the eyebrow and the URL). The
copy, colours and layout constants live at the top of the script.

Link previews are cached by URL, so a card with new artwork needs a new file
name. To change the card:

```sh
pip install -r generator/requirements-og.txt
# 1. edit the copy or layout in generator/og_image.py
# 2. bump "og_image" in generator/site.json (og-default-v3.jpg, ...)
python3 generator/og_image.py            # writes the file named in site.json
git rm assets/og-default-v2.jpg          # the previous card
python3 generator/build.py               # repoints every page, rss.xml and the JSON-LD
```

The head pass also repoints the Article `image` baked into the five legacy
posts whenever it names an earlier version of the default card
(`DEFAULT_CARD_PREFIX` in `build.py`). The lint fails if any page or
`rss.xml` references an `/assets/` file that does not exist. `og_image_alt`
in `site.json` is the matching alt text.

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

The `Book a teardown` button (desktop and mobile menu) goes to `/teardown/`.
It lives in the same places: the static pages and templates (the two `<a>`
tags and the `ctaHref` prop of the SiteHeader island), the `ctaHref` default
in the SiteHeader bundle and the `ctaHref:` props in the three `page.*.js`
bundles. `/win-chat/` has its own header button. The lint fails if any of
them points anywhere else.

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

## Teardown card and the teardown note

Every post ends with one teardown card (`TEARDOWN_CTA` in `build.py`, wrapped
in `<!-- teardown-cta:start -->` / `:end -->`) placed directly before the
author box: an eyebrow, a heading, a button to `/teardown/` (the same target as
the header and footer buttons) and one line (`TEARDOWN_NOTE`) on what the 30
minutes cover and who they are for, built from the FAQ and landing page copy.
The card holds no `<div>`, because `article_body_span()` finds the end of the
post body by the last `</div>` before the author box. The lint fails if a post
has anything other than exactly one card, or if the card turns up on a page
that is not a post.

The homepage hero shows the same note under its teardown button. The Hero
component in `_ploy_static/_astro/closing-cta.B27vAxRK.js` takes an optional
`note` prop that the HomePage bundle (`page.Br0xdvU1.js`) passes; the other
pages pass nothing and render no note. Change the note in `build.py`, in
`index.html` and in `page.Br0xdvU1.js` together. The homepage contact section
carries the request form instead (next section), with the note under its
button.

## Teardown request form

`TEARDOWN_FORM` in `build.py` is the one copy of the form markup. The build
writes it between `<!-- teardown-form:start -->` / `:end -->` on any page that
carries the markers: the contact section of `index.html` and the body of
`pages/teardown.md` (so `/teardown/`). Pages with the form also get the form
styles and script (`TEARDOWN_FORM_CSS`, `TEARDOWN_FORM_JS`) in their shared
head block; other pages do not.

The form posts `application/x-www-form-urlencoded` to the Apps Script endpoint
(`TEARDOWN_ENDPOINT`) with the fields `name`, `email`, `store_url` (all
required), `revenue_band`, `country`, `main_problem`, `source_page` (hidden,
set to `location.pathname`) and `website` (a honeypot: visually hidden,
`aria-hidden`, `tabindex="-1"`, `autocomplete="off"`; a filled-in value is
treated as sent without posting). The field names are the endpoint's contract.
The script validates on the client (inline messages, `aria-invalid`, focus on
the first problem; a store URL without a scheme gets `https://`), disables the
button while sending, sends with `fetch` in `no-cors` mode (an opaque response
counts as sent), falls back to a hidden iframe when `fetch` is missing or
rejects, and when that fails too shows a message with a `mailto:` link that
carries the entered details. On success it shows "Thanks, I'll reply within
one working day." Under the button sit the teardown note, a privacy line
linking to `/privacy/` and the email address as the fallback. Without
JavaScript the browser posts the form to the endpoint itself.

The homepage is one React island (`HomePage` in `page.Br0xdvU1.js`), so the
contact section has to render the same form on hydration. `ClosingCta` in
`closing-cta.B27vAxRK.js` takes an optional `form` prop (an HTML string) and
renders it through `dangerouslySetInnerHTML` inside
`.ss-teardown-form-wrap` instead of the mailto button; React leaves the
server-rendered form, its values and the status line alone on hydration and on
later renders. The HomePage bundle passes `const T="..."`, a JSON-encoded copy
of `TEARDOWN_FORM`. After changing the form in `build.py`, rebuild and refresh
that constant:

```sh
python3 generator/build.py
python3 -c 'import json,sys; sys.path.insert(0,"generator"); import build; print(json.dumps(build.TEARDOWN_FORM, ensure_ascii=False))'
# paste the output as the value of const T= in _ploy_static/_astro/page.Br0xdvU1.js
```

The lint fails when the constant differs from the form in `index.html`, when a
page with the markers has anything other than exactly one form with the
expected fields, endpoint, honeypot, status line, privacy line and email
fallback, when a page has the form without its script or the script without
the form, and when any header or footer `Book a teardown` link (pages,
templates and bundles) points anywhere but `/teardown/`.

Below 40rem the hero copy (`.ss-hero-copy`) on the static pages is reordered
by `TEARDOWN_CSS` in the shared head block so the teardown button comes
straight after the heading and the intro paragraph (`.ss-hero-intro`) moves
below it; on a 390px wide screen the button is on the first screen. The
compiled Tailwind CSS has no responsive order utilities, so the two classes
live in the Hero component and in the hero markup of `/`, `/faq`, `/results`
and `/shopify-plus-architecture`.

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
replaces the footer with the bundle's version. The `Book a teardown` link in
the Studio column goes to `/teardown/`, like the header button and the post
card. The lint fails if a page has no footer link to `/privacy` or if the
footer teardown link points anywhere else.

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
