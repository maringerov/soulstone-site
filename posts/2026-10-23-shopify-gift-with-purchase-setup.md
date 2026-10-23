---
title: "How do I add a gift with purchase on Shopify?"
slug: shopify-gift-with-purchase-setup
description: "Native Buy X Get Y works, but Shopify never adds the gift to the cart for you. When that is fine, when you need a Function or an app, and the checkout edge cases."
date: 2026-10-23
tags: [shopify, conversion, apps, shopify-plus]
faq_schema: true
draft: false
---

Short answer: use an automatic Buy X Get Y discount with the gift at 100% off. That works on every plan, needs no app and takes ten minutes. What Shopify does not do is put the gift in the cart: the discount makes the gift free once the shopper adds it, and that is all. Auto-adding needs cart logic in the theme or an app, and on Shopify Plus a Function keeps the rules tight so the gift is never free on an order that didn't qualify. Whatever you pick, test it in accelerated checkout too, because Shop Pay and the express buttons skip the cart.

The rest of this post is the setup, a comparison of the four ways to do it, what breaks in checkout, and the checklist I run before a campaign goes live.

## Quickest way to give a free gift?

The native discount. It is the right answer more often than the app market would have you believe.

### Setting up Buy X Get Y

In the admin, go to Discounts, Create discount, Buy X get Y, and set the method to Automatic discount so nobody has to type a code. Under Customer buys, choose a minimum quantity or a minimum purchase amount, from the products or collections that qualify. Under Customer gets, set the quantity to one, pick the gift product (or a collection of gifts if the shopper may choose), and set the value to Free. Add start and end dates and save.

Points from Shopify's help centre that matter for a gift:

- A store can have at most 25 active automatic discounts, and app discounts count towards that total.
- If the gift's inventory reaches zero, it shows as sold out and the discount can't be used. Track inventory on the gift and watch it.
- When the same product is in Customer buys and Customer gets, the lower-priced item is the one that is discounted. Keep the gift out of the qualifying set.
- Automatic discounts don't apply on the post-purchase page.
- Start and end times follow the store's time zone.

### Why the gift doesn't appear in the cart

Because of what a discount is in Shopify's model. A discount reads the cart and changes prices; it never changes the cart's contents. Shopify's own documentation says it plainly: the free or discounted item is never automatically added to the cart, and the customer has to add both the qualifying items and the gift. The same is true of Shopify Functions. The Cart Transform Function can expand a line into a bundle, merge lines or update a line's price and presentation, and that is the full list; there is no operation that adds a line.

So "add the gift" is always a storefront or checkout job: theme code, an app's theme embed, or on Plus a checkout UI extension. The discount stays responsible for the price.

## Which method should I use?

| Method | Auto-adds the gift | Plus needed | Cost | Risk |
|---|---|---|---|---|
| Native Buy X Get Y, shopper adds the gift | No | No | None beyond the gift itself | Shoppers who qualify never add it, so the campaign under-delivers |
| Native discount plus theme cart logic | Yes, in the online store cart | No | A few hours of theme work, then upkeep when the theme changes | The theme and the discount drift apart; express checkout from the product page skips it |
| Gift with purchase app | Yes, with a popup or a progress bar | No | Monthly fee and one more app embed on every page | Another writer to the cart, another vendor in the path of a purchase |
| Discount Function plus a checkout UI extension | Yes, inside checkout, including Shop Pay when enabled | Yes | Development time and the Plus plan | Apple Pay and Google Pay sessions don't allow cart changes, so those shoppers still get no gift |

My rule of thumb: native alone for a gift the shopper picks or a small campaign; theme logic for one gift at one threshold on a store that already has a developer touching the theme; an app when the campaigns change weekly and need a popup; the Function route on Plus when the gift is a core part of the offer and the rules are too specific for the admin.

The one thing I push back on is adding a gift app to a store that already runs a discount or promotion app. Check whether the app you have does gifts first. [The hidden cost of app sprawl](/blog/hidden-cost-shopify-plus-app-sprawl/) is mostly a list of stores that didn't.

## How do I make the gift add itself?

### Theme Cart AJAX and its limits

The theme watches the cart and keeps the gift in step with the same rule the discount uses. The core is a few calls to the Cart AJAX API:

```js
const GIFT_VARIANT_ID = 1234567890; // from theme settings, never hard-coded
const THRESHOLD = 7500;             // in cents, the same amount as the discount

async function syncGift() {
  const cart = await (await fetch('/cart.js')).json();
  const gift = cart.items.find((item) => item.variant_id === GIFT_VARIANT_ID);
  const rest = cart.original_total_price - (gift ? gift.original_line_price : 0);

  if (rest >= THRESHOLD && !gift) {
    await post('/cart/add.js', {id: GIFT_VARIANT_ID, quantity: 1, properties: {_gift: 'true'}});
  } else if (rest < THRESHOLD && gift) {
    await post('/cart/change.js', {id: gift.key, quantity: 0});
  }
}

function post(url, body) {
  return fetch(url, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(body),
  });
}
```

Call `syncGift()` after every cart change the theme makes, then refresh the cart drawer the way the theme does it. The underscore in `_gift` follows the convention most themes use to hide a line property from the shopper. Put the variant, the threshold, the dates and the copy in theme settings or a metaobject, so marketing can end the campaign on a Sunday without a developer.

The limits are real:

- It only runs where the theme runs. A shopper who taps Shop Pay, Apple Pay or Google Pay on the product page goes straight to checkout and never passes this code. Nothing breaks; the gift is simply missing from that order.
- The theme must count the same subtotal the discount counts, excluding the gift. Build a cart just under and just over the line and compare what the discount does with what the theme does before trusting either.
- The discount makes one gift free. A shopper who raises the quantity to three pays for two. Hide the quantity control on the gift line, which most themes support through a line property.
- Every theme update is a chance for the logic to stop firing. Keep it in one snippet with one owner.

### When an app is right

When the campaign needs a popup with a choice of gifts, several thresholds with a progress bar, or a new rule every week, an app earns its place. It does the same AJAX work as above, with a settings page and a widget, and good ones handle the quantity guard and the removal case for you.

Treat it like any other app in the critical path: one app, not two; check what it adds to every page load; and run the test list below against it. Apps get the subtotal rule and the express checkout gap wrong too.

On Shopify Plus there is a fourth option that closes most of the gaps: a discount Function that gives 100% off any line whose product carries a `free-gift` tag, paired with a checkout UI extension that adds and removes the gift inside checkout based on the cart total. Because it runs in checkout, it also covers the shopper who arrived through an express button on the product page, and it renders in Shop Pay once the merchant enables the extension for it. A validation Function on the same tag can block a checkout that has the gift without the qualifying items. Custom apps with Functions and blocks on the checkout steps both need Plus; [customizing checkout with extensibility](/blog/customize-shopify-checkout-extensibility/) explains where each piece sits. Shopify Scripts, the old way to do this on Plus, are gone.

## What breaks in checkout?

Four cases are behind most of the gift problems I see.

**Shop Pay and express skip the cart.** The dynamic checkout buttons on the product page go straight to checkout. Theme logic never runs, so route 2 and most apps give those shoppers no gift. In checkout itself, a UI extension on Plus can add the gift during a standard checkout and during Shop Pay if the merchant has enabled it, but cart line changes return an error in Apple Pay and Google Pay sessions. Decide before launch whether a missing gift on those orders is acceptable, and say so in the campaign terms if it isn't.

**Removing the qualifying item.** The shopper adds the gift, then removes the product that qualified them. The discount stops applying, which is correct, but now a full-price gift sits in the cart. Theme logic has to remove it on the next cart update; an app has to do the same; in checkout only a UI extension or a validation Function can react. Test this path explicitly, because the happy path hides it.

**Stacking and combinations.** Each discount has combination settings. If the Buy X Get Y discount and a code are not both set to combine with each other's discount class, the shopper sees one or the other and the support inbox fills up. Shopify also caps codes at five product or order codes and one shipping code per order. Test the exact pair you plan to run, including a free shipping code.

**Gift stock running out.** With inventory tracked, the gift goes sold out, can't be added, and the discount has nothing to apply to. Shoppers who were promised it in a banner now see a product page that says sold out. Have the theme or app check availability before it shows the prompt, watch the gift's stock during the campaign, and keep a second gift ready.

## How do I test before launch?

On a development store, or on the live store with Shopify Payments in test mode, the day before the campaign starts:

1. A cart just under and just over the threshold. The gift appears and disappears at the same amount in the cart, in checkout and on the order.
2. Add the gift, then remove the qualifying item. The gift is removed, or at least no longer free.
3. Raise the gift quantity. Only one is free.
4. Set the gift's inventory to zero. The prompts stop and nothing errors in the cart.
5. A discount code on top, and a free shipping code on top of that. Check the result against the combination settings.
6. Shop Pay from the cart, then Apple Pay or Google Pay from the product page.
7. A guest and a signed-in customer, in each market and currency the store sells in; thresholds in a second currency are easy to get wrong.
8. The order in the admin and in reports: the gift line at full price with a discount allocation, inventory decremented, and the line visible to the warehouse integration with whatever property or tag tells them to pack it.
9. The morning after the end date: the gift is no longer free and every prompt is gone.

Numbers 1 and 6 are the ones that get skipped, and the ones that show up later in the margin report. If tracking on the Thank you page is part of how you measure the campaign, [check that it still runs](/blog/checkout-extensibility-migration-tracking/) before you count on the numbers.

## FAQ

### Does Shopify automatically add the free gift to the cart?

No. Shopify's own documentation states that the free or discounted item is never automatically added; the shopper has to add the qualifying items and the gift, and then the discount applies. Auto-adding is theme logic, an app, or on Plus a checkout UI extension.

### Can I do a gift with purchase without an app?

Yes. The Buy X Get Y automatic discount handles the pricing on every plan. If the shopper adding the gift themselves is acceptable, you are done. If the gift must appear by itself, a small piece of theme code using the Cart AJAX API does it in the online store cart, with the limits described above.

### Do I need Shopify Plus for a gift with purchase?

No. The native discount, the theme route and the app route all work on every plan. Plus is needed for a custom discount or validation Function and for a block on the checkout steps, which is what closes the express checkout gap and keeps the rules tight. If you are weighing Plus for reasons like this, [Shopify Plus architecture](/shopify-plus-architecture/) is where I'd start the conversation.

### Does the gift work with Shop Pay and express checkout?

Partly. The discount applies everywhere, so a gift that is already in the cart is free in every checkout. Adding the gift is the problem: express buttons on the product page skip the cart, so theme logic never runs. In checkout, a UI extension on Plus can add it in standard checkout and in Shop Pay when the merchant enables the extension for Shop Pay, but not in Apple Pay or Google Pay sessions.

### Can I combine the gift with a discount code?

Yes, if both discounts are set to combine with each other's class in their combination settings. A shopper can use at most five product or order discount codes plus one shipping code on an order. Test the exact combination you plan to run before launch.

### What happens when the gift is out of stock?

With inventory tracked, the gift shows as sold out, it can't be added, and the discount has nothing to apply to. Check availability before showing the prompt, watch the stock during the campaign, and have a replacement gift ready. The general questions about how I work are on the [FAQ page](/faq/).

If your last gift campaign cost more margin than it brought in, or the gift keeps appearing on orders that didn't qualify, the rule and the discount have drifted apart. [I work directly with brands on this kind of fix](/shopify-plus-developer-amsterdam/), and more notes on Plus-specific setups are under [the Shopify Plus tag](/tag/shopify-plus/).
