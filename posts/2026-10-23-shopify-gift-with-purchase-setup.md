---
title: "How do I set up a gift with purchase on Shopify?"
slug: shopify-gift-with-purchase-setup
description: "The Buy X get Y discount makes the gift free on every plan, but it never adds the gift to the cart. The four ways to close that gap, from no code to Shopify Functions, with the settings and the test cases."
date: 2026-10-23
tags: [shopify, conversion, apps, shopify-plus]
faq_schema: true
draft: false
---

Short answer: a gift with purchase is two jobs, and Shopify only does one of them for you. Making the gift free is a Buy X get Y automatic discount, built in the admin on any plan in ten minutes. Getting the gift into the cart is not: Shopify's discounts price what is in the cart, they never add to it, and neither does any Shopify Function. So the second job goes to the theme, to an app, or on Shopify Plus to a checkout UI extension, and the rule it uses has to match the discount exactly. Everything else in this post follows from that split.

I'll go through what the admin gives you, why the gift doesn't add itself, the four ways to close that gap, and the test cases that catch the problems I see most often.

## What does Shopify give you out of the box?

The Buy X get Y discount, in Discounts, Create discount. Set the method to Automatic discount so nobody has to type a code. Under Customer buys, choose either a minimum quantity or a minimum purchase amount from the products or collections you pick. Under Customer gets, set the quantity, pick the gift product or a collection of gifts, and set the value to Free. Give it a start and end date and save.

Things worth knowing about it, straight from Shopify's own documentation:

- The free item is never added to the cart automatically. The buyer has to put both the qualifying items and the gift in the cart; then the discount applies on its own.
- A store can have at most 25 active automatic discounts, and discounts created by apps count towards that number.
- If the gift's inventory reaches zero, it shows as sold out and the discount can't be used. Track inventory on the gift and watch it.
- If the same product is in Customer buys and Customer gets, the lower-priced item is the one that gets discounted.
- Automatic discounts don't apply on the post-purchase page.
- The start and end times follow your store's time zone.

For a gift the buyer chooses themselves, that is the whole setup. Add a line to the product page and the cart saying "Add your free gift", link it to the gift product, and you are done. No app, no code, no risk.

## Why doesn't the gift add itself?

Because of where discounts sit in Shopify's model. A discount, whether from the admin or from a Shopify Function, reads the cart and changes prices. It doesn't change the cart's contents. The Cart Transform Function can expand a line into a bundle, merge lines or update a line's price and presentation, and that is all; there is no operation to add a line.

So the "add the gift" job always runs in the storefront: theme code, an app's theme embed, or on Plus a checkout UI extension. Which one is right depends on the plan and on how much the gift matters to the campaign.

## Route 1: the discount alone, no code

Right for: a gift that is one of several the buyer can pick, a small campaign, a store that would rather promote the gift than automate it.

Create the discount as above. Then make the gift easy to reach: a block on the product page and in the cart drawer with the gift's image and an Add button, visible only while the campaign runs. Both are theme settings in most themes, or a small section with a date range. Hide the gift from search and collections with the `seo.hidden` metafield and by leaving it out of your collections, but keep it published to the Online Store channel, otherwise nothing can add it.

What you give up: some buyers who qualify never add the gift, and the campaign's lift is smaller than the plan said.

## Route 2: the theme adds the gift, small code

Right for: a single gift at a threshold, a team that wants it to just appear, no appetite for another app.

The discount still does the pricing. The theme watches the cart and keeps the gift in sync with the same rule. In outline:

```js
const GIFT_VARIANT_ID = 1234567890; // from theme settings
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

Call `syncGift()` after every cart change your theme makes, then refresh the cart drawer the way the theme does it. The underscore in `_gift` follows the convention most themes use to hide a line property from the buyer. Hard-code nothing: the variant, the threshold and the dates belong in theme settings or a metaobject, so marketing can change the campaign without a deploy. That is rule three in [no-nonsense Shopify development](/blog/no-nonsense-shopify-development/), and gift campaigns are where it matters most, because the campaign ends on a Sunday.

Three things to get right:

- The threshold and what it counts. The theme must count the same subtotal the discount counts, excluding the gift itself. Build a cart just under and just over the line and compare what the discount does with what the theme does before you trust either.
- Express checkout buttons on the product page skip the cart. A buyer who taps Shop Pay or Apple Pay there never runs your theme code and gets no gift. Nothing breaks; the gift is simply missing for those orders. Decide whether that is acceptable for the campaign.
- Quantity. The discount makes one gift free; a buyer who raises the quantity to three pays for two. Most themes let you hide the quantity control for a line with a property, which is the simplest guard.

## Route 3: an app

Right for: a choice of gifts in a popup, several tiers, a progress bar, campaigns that change every week.

Gift with purchase apps do route 2 for you, with a popup and a settings page. The cost is the usual one: a theme app embed in the path of every page view, another automatic discount in your 25, and another system that writes to the cart. If you already run a discount or promotion app, check whether it has a gift feature before adding a second one. [The hidden cost of app sprawl](/blog/hidden-cost-shopify-plus-app-sprawl/) is mostly a list of stores that didn't.

Whichever app you pick, the test list at the end of this post applies to it as much as to your own code. Apps get the subtotal rule and the quantity guard wrong too.

## Route 4: Shopify Plus, Functions and a checkout block

Right for: Plus stores that used to do this with a Script, campaigns with rules the admin can't express, and stores where express checkout from the product page is a large share of orders.

Shopify Scripts are gone, and the replacement has two parts. A discount Function makes the gift free. It is deliberately simple: find lines whose product carries a `free-gift` tag and discount them in full. The input query asks for exactly that:

```graphql
query RunInput {
  cart {
    lines {
      id
      merchandise {
        __typename
        ... on ProductVariant {
          product {
            isGift: hasAnyTag(tags: ["free-gift"])
          }
        }
      }
    }
  }
}
```

And the function returns one operation:

```js
export function run(input) {
  const gifts = input.cart.lines.filter(
    (line) => line.merchandise.__typename === 'ProductVariant' && line.merchandise.product.isGift,
  );
  if (gifts.length === 0) return {operations: []};
  return {
    operations: [
      {
        addCartLinesDiscount: {
          candidates: [
            {
              targets: gifts.map((line) => ({cartLine: {id: line.id}})),
              value: {percentage: {value: '100'}},
              message: 'Free gift',
            },
          ],
          selectionStrategy: 'FIRST',
        },
      },
    ],
  };
}
```

Deploy it with the Shopify CLI and create an automatic app discount that points at it. The threshold logic lives in the second part: a checkout UI extension on the checkout steps that adds the gift line when the cart qualifies and removes it when it stops qualifying. Because it runs inside checkout, it also catches the buyer who came in through an express checkout button on the product page, which route 2 can't. Put the threshold and the gift variant in the extension's settings or a shop metafield so marketing owns them. For how extensions and Functions fit together, see [customizing checkout with checkout extensibility](/blog/customize-shopify-checkout-extensibility/).

If gift-only orders are a worry, a validation Function can block checkout when a tagged gift is in the cart without the qualifying items. The same tag drives all three pieces, so there is one place to change.

Two limits: custom apps that contain Functions need Shopify Plus, and blocks on the checkout steps need Plus too. On other plans, routes 1 to 3 are the options.

## What should be a setting rather than code?

Whatever route you take, these should never be hard-coded:

- The gift variant, or the collection of gifts.
- The threshold, in each currency you sell in. Check the discount's behaviour per market with a test cart.
- Start and end date and time.
- Whether the gift is one per order or one per qualifying item.
- The copy: the product page line, the cart drawer prompt, the message in checkout.

On Plus, the Function can read a metafield on the discount itself, which is the standard place for its configuration. In a theme, settings or a metaobject do the same job. The point is that the campaign after this one shouldn't need a developer.

## What should I test before the campaign goes live?

Run these on a development store or with payments in test mode, and again on the live store with a test order the day before launch:

1. A cart just under the threshold and just over it. The gift appears and disappears at the same amount in the cart, in checkout and on the order.
2. Add the gift, then remove the qualifying item. The gift goes too, or at least stops being free.
3. Raise the gift quantity. Only one is free.
4. The gift at zero inventory. The campaign messaging stops, and nothing errors in the cart.
5. A discount code on top of the gift. Check the combination settings on both discounts and the result in checkout.
6. Express checkout from the product page, and from the cart.
7. A guest and a signed-in customer, in each market.
8. The order in the admin and in your reports: the gift line at full price with a discount allocation, inventory decremented, and the line visible to your warehouse integration with whatever property or tag it needs to pack it.
9. Twenty-four hours after the end date, the gift is no longer free and the prompts are gone.

Numbers 1 and 6 are the ones that get skipped, and the ones that show up later in the margin report.

## FAQ

### Does the free gift count towards the spend threshold?

Keep the gift out of the products and collections you put under Customer buys, so it can't help unlock itself. In your own theme code, subtract the gift's line price from the subtotal before comparing it with the threshold, as the example above does. Then build a cart that sits just under the threshold and confirm that adding the gift does not qualify it.

### Can the buyer choose between several gifts?

Yes. Under Customer gets, pick a collection of gift products instead of one product and set the quantity to one. The buyer adds whichever they want and that one becomes free. Automating the add in that case needs a popup, which is where an app or a custom block earns its place.

### What happens when the gift runs out of stock?

With inventory tracked, the gift shows as sold out, it can't be added, and the discount has nothing to apply to. Keep an eye on the gift's stock during the campaign, and have the theme or app check availability before it shows the prompt, so buyers aren't promised something they can't get.

### Can I run the gift together with a discount code?

Yes, if the combination settings allow it. Both the automatic discount and the code need to be set to combine with each other's discount class, and a buyer can use at most five product or order discount codes and one shipping code on an order. Test the exact pair you plan to run.

### Can Shopify Flow add the gift to the cart?

No. Flow acts on orders, customers, products and inventory after the fact, not on a live cart. It is useful around the campaign, for example to tag orders that contained the gift for reporting, or to alert you when the gift's stock drops below a level.

### Do I need Shopify Plus for a gift with purchase?

No. The discount, the theme route and the app route work on every plan. Plus is needed for custom Functions and for blocks on the checkout steps, which is what you want when express checkout from the product page is a large share of your orders or the rules are too specific for the admin.

If your last gift campaign cost more margin than it brought in orders, or the gift keeps showing up on orders that didn't qualify, the rule and the discount have drifted apart. I'm happy to look at where.
