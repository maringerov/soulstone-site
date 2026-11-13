---
title: "Shopify Fall 26 Edition checkout: what is live before Black Friday"
slug: fall-26-checkout-bfcm
description: "Shopify Fall 26 Edition checkout: what is live before Black Friday. Payment tiles are rolling out; native custom fields and Apple Pay outside Safari are still coming soon."
date: 2026-11-05
updated: 2026-11-13
tags: [shopify, checkout, fall-edition, black-friday, premium-brands]
draft: false
---

Short answer: Shopify Fall 26 Edition checkout, what is live before Black Friday, is payment methods as side-by-side tiles already rolling out. Built-in custom checkout fields will not ship before or during Black Friday Cyber Monday, and Apple Pay outside Safari is still coming soon. Shopify's Fall '26 Edition ("Exponential") landed on 28 October 2026 with 150+ updates. For Black Friday on 27 November, treat checkout as a timing problem, not a feature list. Plan peak-season checkout work only around what shoppers can see today.

## What do the Edition status labels mean?

Edition items are not all live the day the marketing page goes up. Shopify and the surrounding write-ups use a few buckets:

- Live: available in a normal admin today.
- Rolling out / rolling out soon: shipping store by store. Your checkout may already show it, or it may still look like last month.
- Early access: some stores can try it; most cannot.
- Coming soon: announced, not released. No date you can put in a sprint plan.

If a slide deck says "Fall '26 checkout" without a status, ask which bucket it is in before anyone books a developer day against Black Friday.

## What is already moving in checkout?

### Payment methods as tiles

Shopify's changelog for 22 October 2026 describes a refreshed payment method design: a tiled layout instead of a radio list. The tiles show when your payment methods meet certain criteria, including offering four or fewer methods. Otherwise the standard list stays.

The Fall '26 Edition page lists the same change as "Simpler layout for payment methods in checkout" and marks it rolling out soon. So this is not a rumour. It is a gradual rollout. Place a test order on phone and desktop and see which view your shoppers get.

### Why that matters for CRO

If you ran payment-step tests earlier this year against a radio list, the page shape has changed for stores that already have tiles. The offer that sat next to a long list may sit differently next to a compact grid. Do not credit or blame a campaign for a layout Shopify moved under you. Note the payment layout in the baseline for November, the same way you note the September [session measurement update and bot filtering](/blog/conversion-rate-jump-bot-filtering/) when you read conversion rate.

## What must not be planned for Black Friday?

### Custom checkout fields: confirmed coming soon

Shopify's help page on custom checkout fields is unambiguous:

- Custom fields are not available yet.
- They will not be released before or during Black Friday Cyber Monday, so your checkout will not change for that reason during the event.
- There is no early access.
- When they do release, they are added to the checkout and accounts editor automatically. You do not request access.

What they will do, once live: collect order-level information (delivery instructions, gift message, membership number and similar), save the value to an order metafield, and work in online store checkout and in agentic storefronts that offer direct checkout.

Plan limits matter too. Shopify Plus gets the full set of field types (text, text area, choice list, date, checkbox). Other plans get Delivery instructions and Gift message only when the feature arrives.

So if a BFCM brief asks for a native gift note or delivery date field in Shopify's own editor, that work belongs after the season. Keep any app-based fields you already rely on for November. When native fields land, switch carefully so shoppers do not see the same ask twice.

### Apple Pay outside Safari: coming soon

Shopify's Apple Pay help page still says customers need Safari on a compatible device today, and states that Apple Pay support for non-Safari browsers is coming soon. Treat Chrome, Edge and Firefox Apple Pay (including any QR flow people talk about) as announced, not as something you can promise shoppers for 27 November.

## What I'd do with the three weeks left

1. Freeze new checkout experiments that depend on unreleased Edition items.
2. Place test orders and record whether payment methods show as tiles or as a list.
3. Keep gift notes, delivery dates and similar collection on whatever already works (checkout UI extension or a trusted app).
4. Write Black Friday targets in orders, net sales and average order value, not in a checkout conversion rate that still carries the September session change.
5. Park native custom fields and non-Safari Apple Pay for a December or January pass.

This is separate from the AI-channel checkout settings decision, from how agents read your product data, and from the agentic knowledge base in admin. Those are real topics. They are not this triage.

## A five minute check in your admin

1. Open the online store checkout as a customer would. Add a product, reach the payment step.
2. Count the payment methods shown and note tiles versus list. Try phone and desktop.
3. Confirm any gift message, delivery note or date picker you expect still appears, and where it comes from (extension or app).
4. Open Settings > Payments and confirm Apple Pay is on if you want it. Remember it still needs Safari for shoppers today.
5. Open Sales channels > Agentic only if you still owe yourself the per-channel checkout decision from late October. Do not mix that review into a custom-fields hope for BFCM.
6. Write one line in the peak-season notes: "native custom fields after BFCM; payment tiles may already be live."

## Questions I get about this

### Is every Fall '26 checkout change live?

No. The Edition announced a lot at once. Checkout alone mixes rolling payment tiles with coming-soon custom fields and coming-soon Apple Pay outside Safari. Read the status, not the headline.

### Can I get custom fields early for Black Friday?

Shopify says no. The help page states they will not release before or during BFCM, and early access is not available.

### Do I need Shopify Plus for any of this?

For native custom fields later: Plus gets all field types; other plans get Delivery instructions and Gift message. Payment tiles are a checkout layout change, not a Plus-only editor feature. Confirm what you see with a test order on your plan.

### Should I rebuild my payment-step tests?

If tiles are already live on your store, yes: refresh the baseline screenshot and any heatmaps for the payment step before you read November results. If you still see the list, note that too, because the tiles can arrive mid-season on a rolling schedule.

### What about the rest of the Edition?

Most of the 150+ updates sit outside checkout: Sidekick, Canvas, Catalog, Shop, admin chrome, developer tools. Useful later. For the next three weeks, the checkout question is narrow: what can a shopper already use, and what is only on a slide.

If you want a short read on whether your checkout is ready for the traffic you are buying, I'm happy to look.
