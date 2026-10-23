---
title: "How do I customize Shopify checkout with checkout extensibility?"
slug: customize-shopify-checkout-extensibility
description: "Branding in the checkout and accounts editor, blocks from checkout UI extensions, rules in Shopify Functions, tracking in Customer events. What each layer does, what needs Plus, and the order I build in."
date: 2026-10-23
tags: [shopify, shopify-plus, checkout-extensibility, ui-extensions]
faq_schema: true
draft: false
---

Short answer: Shopify checkout is customized in four layers, and each one has a fixed place. Branding (logo, colours, fonts, section styles) lives in the checkout and accounts editor in the admin. Anything the buyer sees or fills in that Shopify doesn't ship comes from a checkout UI extension, placed in the same editor as a block. Anything that changes what the buyer can buy, pay or choose for delivery is a Shopify Function. Tracking is an app pixel or a custom pixel in Customer events. Theme code, custom JavaScript and CSS have no place in checkout, and that is the point of the model.

If you came here because a checkout.liquid or Additional scripts customization stopped working, start with [the migration check](/blog/checkout-extensibility-migration-tracking/). This post is for the next question: now that the old way is gone, how do you get the checkout you want?

## What are the four layers of checkout extensibility?

| Layer | What it changes | Where you work | Who can use it |
|---|---|---|---|
| Checkout and accounts editor | Logo, colours, fonts, section styles, which blocks sit where | Settings, Checkout, then Edit on a configuration | All plans from Basic up |
| Checkout UI extensions | Banners, fields, notes, upsells, surveys, anything visible | A block from an app, placed in the editor | Information, shipping and payment steps: Shopify Plus. Thank you and Order status pages: all plans except Starter |
| Shopify Functions | Discounts, delivery options, payment options, validation, bundles | Code in an app, configured from the admin | Public App Store apps: all plans except Starter. Custom apps with Functions: Shopify Plus |
| Customer events | Analytics and ad tracking | Settings, Customer events, as an app pixel or custom pixel | All plans except Starter |

There is a fifth, smaller layer for Plus stores: the GraphQL Admin API. As of API version 2026-04 the Checkout and Accounts Configuration API replaced the older Checkout Branding API, and it gives you branding settings the editor doesn't expose, including per-market branding. On most stores I never touch it, because the editor covers what a brand needs.

The reason the layers are strict is security. Each UI extension runs in a sandbox, separate from the checkout page and from other extensions, with no access to the page's HTML or to payment data. Functions run on Shopify's side with a hard time budget. That is what makes every customization upgrade-safe: Shopify can change checkout under you and your extensions keep working.

## What can I change without a developer?

More than most teams think. Before I write a line of code I check these three places.

**The editor.** Settings, Checkout, Edit on the live configuration. Logo and its position, a colour palette, heading and body fonts, corner radius, the background of the header, the main area and the order summary. Since May 2026 those settings also apply to customer accounts and the sign-in page, so the brand holds together from cart to account. Duplicate the configuration before a big change and work in the draft, then publish.

**Checkout settings.** The same Settings, Checkout page controls the contact method (email or phone), which address fields are optional or required, tipping, the marketing opt-in checkboxes and what happens after checkout. A surprising number of "we need a custom field" requests end here.

**Apps with blocks.** Any App Store app built for checkout extensibility shows up in the editor as a block you drag into place. Delivery date pickers, gift messages, trust badges, upsells and surveys all exist as apps. On Plus, Shopify's own Checkout Blocks app covers a lot of content and conditional display without code.

Pick one app that does several of these, not five that do one each. Every checkout app is another vendor in the path of a purchase. I wrote about where that leads in [the hidden cost of app sprawl](/blog/hidden-cost-shopify-plus-app-sprawl/).

## When do I need a checkout UI extension?

When the buyer needs to see or enter something that no setting and no app covers. On the stores I work on the common cases are:

- A note under a line item that reads product data: refill instructions, a delivery lead time, a warning about a hazardous item.
- A field the business needs on the order: a PO number for B2B, a preferred delivery slot, a gift message that goes to the warehouse.
- A banner that depends on the cart: free shipping almost reached, a returns window for a sale item, a message for a market.
- A thank you page block: a survey, a referral code, a link to a care guide.

An extension is a small piece of code in a custom app, built with the Shopify CLI. It targets a place in checkout. Block targets like `purchase.checkout.block.render` let the merchant position the block in the editor. Static targets like `purchase.checkout.cart-line-item.render-after` always render in one spot. The UI is built from Shopify's own components (`s-banner`, `s-text`, `s-text-field` and so on), so it inherits the branding from the editor and you can't make it look wrong.

A banner with one merchant setting is this small. The TOML declares the target and a text setting:

```toml
api_version = "2026-10"

[[extensions]]
name = "Checkout notice"
handle = "checkout-notice"
type = "ui_extension"

  [[extensions.targeting]]
  module = "./src/Notice.jsx"
  target = "purchase.checkout.block.render"

  [extensions.settings]
    [[extensions.settings.fields]]
    key = "notice"
    type = "single_line_text_field"
    name = "Notice text"
```

And the component reads the setting the merchant typed in the editor:

```jsx
import '@shopify/ui-extensions/preact';
import {render} from 'preact';

export default function extension() {
  render(<Notice />, document.body);
}

function Notice() {
  const text = shopify.settings.value.notice;
  if (!text) return null;
  return <s-banner tone="info">{text}</s-banner>;
}
```

The merchant places the block in the editor, types the text, and can change it on a Tuesday without a deploy. That is the pattern I aim for in every extension: the code decides how, the settings decide what.

Extensions can also read cart lines, the buyer's identity and metafields on products, variants, the customer and the shop. If you declare metafields in the TOML, add `owner_type` to each one now; [it becomes required on API 2027-01](/blog/checkout-extension-metafields-owner-type/). To write data, an extension sets cart attributes, line item attributes or metafields, which land on the order where your warehouse and your ERP can read them.

## When do I need a Shopify Function?

When the rule changes the outcome of the checkout rather than what it looks like:

- A discount Shopify's admin can't express: a tiered gift, a discount that depends on a customer metafield, a bundle price.
- Hiding, renaming or reordering payment methods: no cash on delivery above an amount, invoice payment for approved B2B customers only.
- The same for delivery options: hide express shipping for bulky items, rename a rate per market.
- Validation that blocks checkout: an order maximum, a product that can't ship to a country, a variant flagged as sold out before the warehouse count reaches zero.
- Cart transforms: expand a bundle into its components or merge lines into one.

Functions run on Shopify's infrastructure, so there is no server of yours in the path of a purchase, nothing to host and nothing to keep awake. That is why I reach for them before a custom app with its own backend. [No-nonsense Shopify development](/blog/no-nonsense-shopify-development/) has a worked example: a validation function that blocks a flagged variant at checkout, reading the same flag the theme uses to show it as sold out.

Two limits to know up front. Custom apps that contain Functions need Shopify Plus; on other plans you get Functions through public apps only. And a Function can change the price and presentation of lines in the cart, but it can't add a line. If you need a free gift to appear by itself, that is storefront or extension work, which I cover in [setting up a gift with purchase](/blog/shopify-gift-with-purchase-setup/).

## What can't checkout extensibility do?

Knowing this saves a week of trying:

- No custom JavaScript or CSS on the checkout page, and no access to its DOM. If a request starts with "can we inject", the answer is no.
- No removing or reordering Shopify's own fields and steps. You can make some fields optional or required in settings, and that is it.
- No blocks on the information, shipping and payment steps without Plus. Non-Plus stores customize the Thank you and Order status pages only.
- No adding a cart line from a Function. Cart Transform expands, merges and updates lines.
- No changing the order from a Thank you page extension. The order doesn't exist yet at that moment; you have the order ID and can read it later.
- Not every target renders in every express checkout. Test Shop Pay, Apple Pay and Google Pay separately and read the compatibility notes for the APIs you use.
- Nothing from your theme. Theme app embeds and anything in `theme.liquid` stop at the cart.

## In what order should I build?

The order matters because each step removes work from the next one.

1. Editor and settings first. Match the brand, set the fields, duplicate the configuration before you change anything else.
2. Then one app with blocks, if an app already does what you need and you are willing to have it in checkout.
3. Then a custom UI extension for the one thing that is left. Keep every value the team might change in a setting or a metafield.
4. Then Functions for the rules.
5. Tracking as pixels, from the start. Every tool that should know about a purchase gets an app pixel or a custom pixel in Customer events, nothing in the theme.

When I audit a checkout that was built in the other order, I usually find a custom extension doing something the editor could do, and a Function app installed for one discount the admin already supports.

## How do I test a checkout customization?

Work in a draft configuration and preview it in the editor. Then, on a development store or with the payment provider in test mode, place real test orders and check these:

- A cart just under and just over every threshold you use.
- The information, shipping and payment steps on a phone, not only in the desktop preview.
- Express checkout from a product page, which skips the cart. Blocks and Functions that depend on a cart state behave differently there.
- A guest buyer and a signed-in customer, because protected customer data only shows for the second one.
- Each market and language the store sells in, if your extension or Function reads them.
- The Thank you page and, after a refresh, the Order status page. They are different targets.
- The order in the admin: the attributes, metafields and discounts you expected are there, with the names your warehouse integration reads.
- Every tool in Customer events received the purchase. Check the vendor's own event log, not only the pixel's status in Shopify.

Then publish the configuration and keep the previous one as a draft for a week, so you can roll back in one click.

## FAQ

### Can I customize Shopify checkout without Shopify Plus?

Yes, within limits. On every plan from Basic up you get the checkout and accounts editor for logo, colours, fonts and layout settings, apps that add blocks to the Thank you and Order status pages, Functions through public App Store apps, and pixels in Customer events. Blocks on the information, shipping and payment steps, custom apps with Functions and the Admin API for branding need Shopify Plus.

### Do I need a custom app, or will an App Store app do?

Start with an App Store app if one does the job and you accept another vendor in checkout. Build a custom extension when the requirement is specific to your products or your operations, when you want the data to land in your own fields, or when the only app that fits brings ten features you don't need. A single custom extension is often less maintenance than an app.

### Can I add a custom field to checkout?

Yes. A checkout UI extension renders the field and saves the value as a cart attribute, a line item attribute or a metafield, so it appears on the order. On Plus the field can sit on any checkout step. On other plans it can only sit on the Thank you or Order status page, which works for surveys but not for information you need before payment.

### Will customizations slow my checkout down?

Not if they are built the usual way. Extensions are loaded by Shopify in a sandbox, and Functions have a strict budget for how long they may run, so one that overruns fails instead of holding up the page. The thing to avoid is an extension that waits on a network call before it renders. Render first, fetch after, and show nothing rather than a spinner if the call fails.

### Is checkout.liquid still an option anywhere?

No. Plus stores moved off checkout.liquid, and the Additional scripts box and script tags on the Order status page stopped running for everyone else on 26 August 2026. Everything they did now lives in the four layers above.

### Who maintains an extension once it is live?

Whoever maintains the custom app, which means someone has to bump the API version about once a year and read the changelog for the targets you use. That is a few hours a year, and it is far less than what checkout.liquid used to cost at every Shopify update.

If your checkout still carries a workaround from the old model, or a request has been sitting in the backlog because nobody is sure which layer it belongs to, send it over. Sorting it into the right layer is usually a short conversation.
