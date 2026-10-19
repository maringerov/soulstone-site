---
title: "How do I migrate to checkout extensibility after checkout.liquid and Additional scripts?"
slug: checkout-extensibility-migration-tracking
description: "Tracking moves to Customer events, visible changes move to UI extensions, and theme code never runs in checkout. The 15-minute check and the fixes."
date: 2026-10-19
tags: [shopify, checkout-extensibility, tracking, customer-events, shopify-qa]
draft: false
---

Short answer: everything that used to live in checkout.liquid or in the Additional scripts box now has one of two homes. Tracking goes to Customer events, as an app pixel or a custom pixel. Anything the buyer sees goes to checkout and customer account UI extensions, as blocks you place in the checkout editor. Code in your theme never runs in checkout or on the thank you page, so a tag in `theme.liquid` is not a backup.

For stores on a non-Plus plan, the deadline to upgrade the Thank you and Order status pages was 26 August 2026. Since then, old scripts on those pages don't run. Purchases kept coming in. What stopped, on many stores, is some of the tools that report them.

Below is the check I run, then the questions I get most about it.

## What actually stopped on 26 August?

It depends on how the store was set up. These are the usual cases:

- Code in the Additional scripts box on the Order status page. The box has been view-only since 28 August 2025, and on the new pages its content doesn't run.
- Script tags that apps added to the Order status page. Shopify's script tag documentation lists 26 August 2026 as the date these stopped.
- Older app integrations that relied on either of those, from vendors that never moved to an app pixel.

Plus stores went through the same change earlier, with checkout.liquid on the checkout steps as well. The answer is the same for both.

What kept working: app pixels in Settings, Customer events. Shopify loads them in a sandbox on checkout and the thank you page, so they never depended on your scripts.

## How do I check my store in 15 minutes?

This is the checklist from a recent audit for a Dutch skincare brand on the Advanced plan. Nothing in it needs a developer.

1. Open Settings, Checkout. If you still see an upgrade notice in the Configurations section, you're on the old pages. Open the upgrade guide from that notice. It lists your customizations and which of your apps are compatible.
2. Open Settings, Customer events. Write down every app pixel and custom pixel, and next to each one the person or team who owns it. Any pixel you can't explain goes on a list to check.
3. List every tool that should know about a purchase: analytics, each ad platform, email, session recording, affiliates. Mark each one as "pixel in Customer events", "server-side only" or "nothing". The last group is what went quiet.
4. In your analytics tool, compare daily purchases with Shopify orders from the start of August. A drop on 26 August, or more purchases than orders, is the signal. A gap of a few percent from consent and ad blockers is normal.
5. Search `theme.liquid` and your theme snippets for tags that also exist as an app pixel. Loading the same ad account twice can count storefront events twice.

On the skincare store, purchase tracking was fine for analytics, the main ad platforms and email, because they all ran as app pixels. Session recording had been blind on checkout since 26 August, because it only ever lived in theme code, and the same was true for any ad tag outside Customer events. The theme also loaded one ad account a second time, next to its app pixel. And one app pixel was sending marketing data to an outside server that nobody on the team could place.

## What still runs on the thank you page?

Only what Shopify loads itself:

- App pixels and custom pixels from Customer events.
- Blocks from checkout and customer account UI extensions, placed in the checkout editor.
- Shopify's own features and settings.

Your theme, its app embeds and anything in `theme.liquid` stop at the cart. That is by design. Shopify keeps checkout closed to theme code so it stays secure and upgrade-safe for every store.

## How do I replace a tracking script that stopped?

First look for the vendor's official app with a pixel. Most large ad and analytics platforms have one, and it's the least work to keep running.

If there is none, add a custom pixel in Settings, Customer events, Add custom pixel. A custom pixel subscribes to standard events. The minimum for a purchase looks like this:

```js
analytics.subscribe("checkout_completed", (event) => {
  const checkout = event.data.checkout;
  const order = {
    id: checkout.order?.id,
    value: checkout.totalPrice?.amount,
    currency: checkout.currencyCode,
  };
  // send `order` to your vendor here
});
```

Set the pixel's customer privacy settings to match what the vendor does with the data, so it follows the buyer's consent choice. Then place a test order and check the vendor's own event log, not only the pixel's status in the admin.

For ad platforms, also turn on the server-side option if the app has one (enhanced conversions, a conversions API). Server events don't depend on the browser, so they keep counting when a pixel is blocked.

## How do I replace a visible customization?

Anything the buyer saw, such as a delivery note, a survey, an upsell or a loyalty message, becomes a block. Install an app that offers it as a checkout or customer account block, or build a small UI extension in a custom app. Then place it in the checkout editor.

Non-Plus stores can customize the Thank you and Order status pages this way. Blocks on the information, shipping and payment steps are Plus only.

## FAQ

### Did my purchase tracking stop on 26 August?

Not if it ran as an app pixel. Step 3 above tells you which tools did. A tool that only had a script in Additional scripts, or a script tag on the Order status page, has seen no purchases since then.

### Should I keep the Google Tag Manager snippet in my theme?

Keep it only if something still uses it on the storefront. GTM in the theme doesn't load in checkout. If you want GTM for checkout events, load it from a custom pixel. Before you delete it, check whether a tag inside it does something else, such as a site verification.

### What changes on 1 March 2027 for storefront script tags?

Script tags stop running on storefront pages too. Since 1 October 2026, apps can't create or update them. If an app still loads its code that way, ask the vendor for a theme app extension, or replace the app. Code you added to the theme yourself is not a script tag and is not affected.

### Is an unknown app pixel a problem?

It can be. A pixel sees page views and purchases, and some send data marked as sale of data. If nobody can say why it's there, find the app it belongs to and remove it if it isn't needed.

### Does this matter for AI shopping agents?

Yes, in one way. When an agent completes a checkout for a buyer, your storefront tags never see that visit. Server-side conversions and Shopify's own order data are what still count those sales.

If your ad platforms report fewer sales since late August and nobody knows why, this is the first place I look.
