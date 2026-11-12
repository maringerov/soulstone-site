---
title: "One live Shopify theme or a copy per campaign? How to release content and code without losing either"
slug: shopify-single-theme-vs-multi-theme-releases
description: "Should you duplicate your Shopify theme for every campaign or keep one live theme? Where content and code should live, and a release routine that loses neither."
date: 2026-11-12
tags: [shopify, themes, releases, theme-editor, premium-brands]
draft: false
---

Short answer: should a Shopify store release from one live theme, or duplicate the theme for every campaign and publish the copy? For most premium brands, keep one live theme as the only place where content is edited, and use unpublished copies for code and previews only. A duplicated theme is a fork. Every template, section setting and translation the team adds to one copy is missing from the other, and the next publish quietly removes it. If you do run a theme per campaign, freeze content on the old theme and compare the two before you publish.

## Why does content disappear when we publish a new theme?

Because in Shopify, a lot of what the team thinks of as content lives inside the theme. Homepage sections, product page templates, section settings, block text and theme translations are all stored in the theme's files. Products, collections, metafields and metaobjects are not. They live in the store and every theme reads them.

So the moment someone duplicates the live theme, there are two copies of the content. The campaign team works on the copy. Customer service fixes a typo on live. A developer adds a new landing page template on live because a launch could not wait. When the campaign copy is published, it has the campaign and none of the other changes.

Nothing breaks loudly. A page goes back to last month's text. A template is gone, so a product falls back to the default layout. A translated block shows English again.

## What I see in practice

On a multi-market home and body care store, the merchandising team duplicated the theme for each campaign. In one month there were several dated copies: a gift launch, a mid-month theme, a home sale. Each was a sensible copy at the time. The cost came later, as requests like "this landing page is on the other theme, bring it to live" and "please carry this into future themes". Each one meant finding the source theme, moving the exact files and then moving the matching translations key by key.

On a Dutch skincare store with a smaller team, there is one live theme. Content is edited in the live theme editor. New product page templates go live unassigned and are switched on per product when they are ready. Code changes are tested on an unpublished copy, then moved to live one file at a time. That copy is never where content is edited, so there is nothing to lose when it is thrown away.

Both stores work. The second one spends far less time on archaeology.

## Single theme or multi-theme: when does each make sense?

### One live theme

Best for most brands. Content has one home, the theme editor always shows the truth, and new work is added next to what is live instead of replacing it.

It needs two habits:

- New layouts ship as new, unassigned templates, then get assigned. Nobody sees them until you say so.
- Timed campaigns use dates and settings, not a theme swap. Put start and end dates, thresholds and banner content in theme settings or metaobjects, so a campaign is switched by the calendar, not by a publish.

### A theme per campaign

Reasonable when a campaign changes the whole look of the store for a fixed window and you want to prepare it fully out of sight. It works only if the team accepts the rules that come with a fork:

- Content freeze on the live theme from the day of the copy, or a written list of every change made after it.
- A comparison of the two themes before publishing: templates, sections, section settings and translations.
- One person who owns the publish.
- A plan for the day after, because the campaign theme now carries everything forward.

If nobody can promise the freeze, the campaign theme will lose something. In my experience it usually does.

## Where should development changes live?

Not in a duplicated theme. Code belongs in version control, with one branch per release and one unpublished preview theme to test it on. On the body care store, every ticket lands on one shared development branch and one preview theme, and the release merges into live as one change, with a fresh pull of the live theme before the push and another after it to confirm nothing else moved.

That gives you three separate things, each with one home:

1. Code: the repository. Reviewed, versioned, easy to roll back.
2. Content in the theme: the live theme editor. Edited by the team, every day.
3. Store data: products, metafields, metaobjects. Shared by every theme.

Most release pain comes from one of these living in two places.

## How do you release code without overwriting the team's content?

The risky files are the JSON ones: templates, section groups and `config/settings_data.json`. The theme editor writes to them. A developer's copy of those files is out of date the moment someone saves in the editor.

What works:

- Pull the live theme before every push and compare. If the editor changed a file since your branch started, merge that change in first.
- Push only the files the release touches, not the whole theme.
- Pull again after the push and check that live matches what you expected.
- If the store uses Shopify's GitHub integration, remember that editor saves are committed back to the connected branch. Merge them into your work before you open a release.

## A release routine for a premium brand

1. Decide which model you run: one live theme, or a campaign theme with a freeze. Write it down.
2. Keep content edits on live. Keep code on a branch and an unpublished preview.
3. Ship new layouts as unassigned templates, then assign.
4. Put campaign dates and offers in settings or metaobjects, and test the timing on a preview with the date moved forward.
5. Before any publish or push, compare against the current live theme.
6. After it, check the pages that matter on phone and desktop: home, a product page, a collection, cart.
7. Delete old campaign copies once they are no longer a rollback option, so nobody edits the wrong theme.

## Questions I get about this

### Do translations follow a duplicated theme?

Translations for the theme's own content belong to that theme. Anything translated on one copy after the duplicate was made is not on the other. Moving it later means matching key by key, which is slow and easy to get half right.

### Can I schedule a theme publish for a campaign?

On Shopify Plus, Launchpad can schedule a theme to publish at a set time. That solves the timing, not the fork. The scheduled theme still needs the content freeze and the comparison.

### Is it safe to edit the live theme directly?

For content, yes. That is what the theme editor is for, and it is the reason a single-theme setup works. For code, test on an unpublished preview first and move only the files you changed.

### How many themes should a store keep?

As few as you can explain. The live theme, one preview for development, and the last published theme as a short-term rollback is enough for most stores. Every extra copy is one more place someone can edit by mistake.

### We already have several campaign themes. Where do we start?

Pick the live theme as the source of truth. List what exists only on the other copies, move what is still needed, then archive or delete them. After that, new campaigns follow the single-theme habits above.

If your team spends more time moving content between themes than making it, I'm happy to look at how your releases are set up.
