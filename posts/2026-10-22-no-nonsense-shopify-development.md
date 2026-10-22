---
title: "No-nonsense Shopify development: take complexity out before you add more"
slug: no-nonsense-shopify-development
description: "Most overblown Shopify stacks don't need another app or a rebuild. Find who writes what, use what Shopify already runs, and ship small. Four rules I work by, with two real cases."
date: 2026-10-22
tags: [shopify, development, architecture, apps, shopify-plus]
draft: false
---

Short answer: most heavy Shopify stacks get lighter by removing things, not by adding a better tool. Before I build anything, I find out which system writes each field, I check what Shopify can already do on its own, and I ship the change in the smallest step that can be undone. Most of the time that's enough.

I wrote about [the hidden cost of app sprawl](/blog/hidden-cost-shopify-plus-app-sprawl/) earlier this year. That post is the why. This one is how I work day to day so a store doesn't end up there again.

## What does an overblown stack look like?

From the outside it's a slow store with many apps. From the inside it usually looks like this:

- Two or three systems write the same field, for example a price, a stock level or a tag, and nobody knows which one wins.
- Logic lives in three places: an app, a script in the theme and a rule in the ERP.
- A small change, like a promo end date, needs a developer and a deploy.
- Tracking tags sit in the theme and in an app at the same time, so some numbers count twice.
- A custom app has its own server, but most of what it does could run inside Shopify.

None of this comes from one bad decision. Each piece was added to fix something real. The problem is that nothing ever gets taken out.

## Rule 1: find the writer before you write code

When something on a store keeps changing back, the first question is not "what is wrong with the theme?" It is "who else writes this field?"

On an Amsterdam home and body care brand, a sale price kept coming back overnight after the team fixed it by hand. The theme was fine. The ERP sync owned the sale flag and wrote it back on its next run. The fix was a setting on the ERP side, and the ticket closed without a line of code. I wrote that one up in full: [the price keeps reverting, the theme is not the problem](/blog/price-keeps-reverting-theme-not-the-problem/).

Since then I keep a short writer map for every store I work on: for each important field, which system writes it and how often. It takes an hour to make, and it has saved many more.

## Rule 2: use what Shopify already runs

Before an app or a server, I check three things Shopify gives you for free:

- **Metafields and metaobjects** for data the team needs to edit.
- **Shopify Flow** for simple "when this happens, set that" rules.
- **Shopify Functions** for discount, validation and checkout logic. They run inside Shopify, so there is no server of yours in the path of a purchase.

The same body care brand wanted products to show as sold out a little before the warehouse actually ran out. The obvious routes were a stock app or holding back inventory in Shopify. Both would have failed, because the warehouse sync overwrites stock levels in Shopify within the hour.

So we didn't touch inventory at all. Flow sets a small flag on the variant when stock drops below a threshold, and the theme reads that flag and shows the product as sold out. The threshold is a setting the team can change per product. The second stage is a validation function that blocks the flagged variant at checkout too, including express checkout. It reads the same flag, runs on Shopify and needs no hosting. The whole thing adds no app and no new server, and it leaves the warehouse sync alone.

## Rule 3: put the knobs in settings, not in code

If the team will want to change it, it belongs in theme settings, a metafield or a metaobject, not in Liquid or JavaScript. Promo dates, thresholds, gift products, banner copy and which collection a section pulls from are all settings.

Hardcoded values are how a store ends up needing a developer for a Tuesday campaign. They are also how old promos quietly come back, because a date in the code never expires by itself.

My test is simple: if the marketing team can't change it in the theme editor or the admin, I ask why not.

## Rule 4: ship small and know what it touches

On a live store I change one thing at a time. I pull the live theme first, change the files I need, push only those, then pull again to check that nothing else moved. Before the push I write one line on what the change can affect: which templates, which apps, which markets.

It's slower on paper. In practice it's faster, because nothing breaks that needs a second fix, and anything that does go wrong points straight to one change.

The same goes for tracking. In a recent checkout audit for a Dutch skincare brand, the theme still had an ad tag that an app already sent. Removing it was one line, and the reports got more accurate because nothing was added.

## Where do I start on my own store?

A half day is enough for a first pass:

1. List every app, every script in `theme.liquid` and every pixel in Settings, Customer events. Give each one an owner and a reason.
2. For your five most important fields (price, compare-at price, stock, tags, product status), write down which system writes each one.
3. Mark anything two systems write. That's where your strange bugs come from.
4. Find the values your team asks a developer to change. Move them into settings.
5. For each app, ask whether a metafield, Flow or a Function could do the same job. Don't remove it yet, just write the answer down.

## Questions I get about this

### Is this a reason to replatform or go headless?

Usually not. A heavy stack moves to the new platform with you unless you take it apart first. I covered that in [replatforming is usually the wrong answer](/blog/replatforming-usually-wrong-answer/).

### Should we build a custom app instead of paying for three?

Sometimes. But check Functions, Flow and metafields first. A lot of what a custom app does can run inside Shopify, and then there's no server to host, patch and pay for.

### Won't removing things break the store?

It can, if you remove five things at once. Remove one, check, then the next. Keep a short list of what you removed and why, so it's easy to put back.

### Who should own this?

One person who can say no. Stacks grow because adding is easy and nobody's job is taking things out.

If your store feels heavier every quarter and nobody can say why, that's usually a writer map and a half day of looking. I'm happy to take a look.
