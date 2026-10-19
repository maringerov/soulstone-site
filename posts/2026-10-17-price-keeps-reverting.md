---
title: "The price keeps reverting. The theme is not the problem."
slug: price-keeps-reverting-theme-not-the-problem
description: "A sale price came back overnight after a manual fix. How I traced the real writer in Shopify, and why I map every writer before touching code."
date: 2026-10-17
tags: [shopify, diagnostics, product-data, erp, compare-at]
draft: false
---

The ticket said: "We fixed the price on a couple of products last night. This morning they are back on sale, at most of the price off."

This was a home and body care brand with an ERP connected to Shopify and a handful of apps. The team assumed a theme bug or a Shopify glitch. It was neither, and the ticket closed without a single line of code. This post is the order I checked things in, because the same pattern shows up on almost every store that has more than one system writing product data.

## A price in Shopify is the last value someone wrote

Shopify does not know which system "owns" a price. A variant has a price and a compare-at price, and whatever wrote last wins. On a simple store that is the merchant in the admin. On a store with an ERP, a PIM, a sale app, Shopify Flow and the occasional CSV import, it is a shared field with several writers. Most of them run on a schedule, and none of them tell you when they run.

So my first question on any "the price changed by itself" ticket is: who else writes to this field?

## 1. Read the data, not the page

Before I open the theme, I open `/products/<handle>.js` on the storefront. It returns the product JSON the theme renders from, including `price` and `compare_at_price` per variant. If the JSON is wrong, the theme is showing the truth about bad data, and a theme fix would only hide it.

Here the JSON showed something extra. The affected variants had a compare-at price equal to the price. The manual fix had set compare-at to the regular price instead of clearing it. Most themes only show a sale badge when compare-at is higher than the price, so the page looked fine for a few hours. It was still wrong data, and I'll come back to why that matters.

## 2. Rule out Markets and B2B pricing

Next I checked the price lists. The store sells in several countries and has a B2B catalog. A fixed price on a market or a catalog overrides the base price for that audience, and it is easy to forget it exists.

All of them were relative adjustments at zero, with no fixed prices on these variants. So they mirrored the base price and could not cause a revert. A few minutes, and one suspect gone.

## 3. Compare tags and metafields across the affected products

Systems that write to Shopify usually leave fingerprints: tags, metafield namespaces, a field they update in the same second as every write.

All the affected products carried the ERP's sale tag. One of them also had a tag and an empty metafield from an older discount app, last written a long time ago. That made the discount app look guilty. But another affected product had been created recently and had no trace of that app. A cause has to explain every affected product, and the only thing they had in common was the ERP sale flag.

Across the store, a large group of products with that flag sat at the same fixed fraction of their compare-at price. The prices in the ticket fit that same pattern.

## 4. Look at when things changed

Shopify keeps an `updatedAt` timestamp per variant. I pulled it for every active variant and sorted by time. People edit a few products during office hours. Syncs leave a different shape.

Here the writes clustered a few minutes past every hour, plus a couple of large batches in the middle of the night. In the evening window the team mentioned, only a handful of variants changed, and one of them was a sibling product in the same range. Nobody on the team edits that many variants in the small hours.

One limit to know: `updatedAt` only keeps the latest write. The team's second fix had already overwritten the timestamp of the revert. You see the pattern across many variants, not the history of one.

## 5. Accept that the event log won't name the writer

Shopify's product events show things like "app X changed product status from draft to active". They do not log price changes. So no record anywhere says "the ERP set this price late in the evening". You get there by elimination and pattern, and you write down that it is an inference.

## What it was

The ERP still had the affected products flagged as on sale. On its next run, the sync pushed the ERP sale price back over the manual Shopify edit. A manual edit in Shopify can't hold while the source system says "sale".

The ERP vendor had said their sync doesn't touch prices. The pattern said otherwise. I asked for the sync log for those SKUs, which is the only place that can confirm it.

## The fix was in the admin, not the code

There was nothing to change in the theme. What I sent the team was a short list of exact steps:

- Remove the sale flag for those SKUs in the ERP, and confirm with the vendor that the next run respects it.
- After that run, clear compare-at in Shopify (empty, not equal to the price).
- Check the variants again after the next hourly run and after the nightly batch.

That is less satisfying than a commit, and it is the right answer. If I had "fixed" it in Liquid by hiding the sale badge for those products, the data would still be wrong and the sync would keep winning.

## Why the compare-at detail matters now

Compare-at equal to price looks harmless on the page. But the theme is no longer the only reader. Shopify's catalog for AI shopping agents reads product data, and it now takes a list price from compare-at. Agents and feeds don't see your theme logic. They see the fields. A compare-at that is "technically not a sale" in your theme can still read as a list price somewhere else.

My rule for product data now: price, compare-at, stock and shipping in Shopify have to be true on their own, without the theme interpreting them.

## What I changed in my own process

Every theme ticket that touches prices, sale badges or compare-at display now starts with a short writer map. Before any push I write down:

| Writer | What it touches | When it runs |
|---|---|---|
| ERP or PIM sync | price, compare-at, tags, status | hourly and nightly |
| Sale or discount app | price, compare-at, tags | on campaign start and end |
| Shopify Flow | tags, metafields | on product or inventory update |
| Markets price lists, B2B catalogs | price per audience | always |
| CSV imports, bulk editor | anything | when someone runs one |
| Staff in the admin | anything | office hours |

Then one line: the fact that makes this change safe, and how I checked it. If I can't fill that in, I'm not ready to touch the code.

On most stores I work on, this table has more rows than the team expects, and the team knows about roughly half of them.

If your store has prices that "change by themselves", write this table for your own setup before you open a ticket with your developer. It turns a long investigation into a short one, and it often shows that the fix belongs with whoever owns the source system.
