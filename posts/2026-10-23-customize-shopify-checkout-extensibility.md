---
title: "How do I customize Shopify checkout with extensibility?"
slug: customize-shopify-checkout-extensibility
description: "Visible changes go in checkout UI extensions, logic goes in Shopify Functions, looks go in the branding API. What each can do, and what needs Plus."
date: 2026-10-23
tags: [shopify, shopify-plus, checkout-extensibility, ui-extensions]
faq_schema: true
draft: false
---

Short answer: every change you used to make in checkout.liquid now maps to one of four tools. Checkout UI extensions cover anything shoppers see, from a trust badge to a custom field. Shopify Functions cover logic: discounts, payment and delivery options, validation. Branding covers look and feel, in the checkout and accounts editor and, on Plus, through the branding API. Web pixels cover tracking. Shopify Plus stores can customize the Information, Shipping and Payment steps; the Thank you and Order status pages are open to every plan from Basic up.

That split is the whole model. Once you know which tool a request belongs to, the work is usually small. Most of this post is a sorting guide, with the plan limits and the things the model refuses to do.

## What replaced checkout.liquid?

Checkout.liquid let Plus stores edit the checkout template directly: any markup, any script, any style. It also broke at every Shopify update and made checkout hard to secure, so Shopify closed it. Plus stores moved to checkout extensibility in 2024 and 2025. For everyone else, the Additional scripts box and script tags on the Order status page stopped running on 26 August 2026. If something of yours went quiet then, start with [the migration check](/blog/checkout-extensibility-migration-tracking/).

What replaced it is a set of extension points rather than a template:

- **Checkout UI extensions** render inside checkout as blocks. Each one runs in a sandbox, separate from the page and from other extensions, with no access to the page's HTML or to payment details. Merchants place them in the checkout and accounts editor.
- **Shopify Functions** run on Shopify's side, in the discount, delivery, payment and validation steps of a purchase. They return a list of operations, never UI.
- **Branding** lives in the checkout and accounts editor: logo, colours, fonts, corner radius, section styles. Plus stores get the rest through the GraphQL Admin API. As of API version 2026-04 that is the Checkout and Accounts Configuration API, which replaced the Checkout Branding API and applies one set of brand settings across checkout, customer accounts and sign-in.
- **Web pixels** in Settings, Customer events, as app pixels or custom pixels, replace every tracking snippet.

Nothing from your theme runs in checkout. App embeds and `theme.liquid` stop at the cart, by design, so Shopify can update checkout without breaking stores.

## Which tool do I use for which change?

This is the table I keep open when a backlog of checkout requests lands on my desk.

| Change | Tool | Plan |
|---|---|---|
| A custom field (delivery slot, PO number, VAT ID) | Checkout UI extension, saved as a cart attribute or metafield | Plus on the checkout steps; all plans on Thank you and Order status |
| A trust badge or returns note | Checkout UI extension, block target | Plus on the checkout steps; all plans after purchase |
| A gift message | Checkout UI extension with a text field, saved as a line or cart attribute | Plus |
| Hide a payment method above or below an amount | Shopify Function, payment customization | Public app on any plan; custom app on Plus |
| Block a PO box address | Shopify Function, delivery customization or validation | Public app on any plan; custom app on Plus |
| A free-shipping progress bar | Checkout UI extension, reads cart cost | Plus |
| Fonts and colours | Checkout and accounts editor; branding API for the rest | Editor on all plans; API on Plus |
| Purchase tracking for an ad platform | Web pixel in Customer events | All plans except Starter |

Two notes on the table. Blocking a PO box through delivery customization only works for rates from carrier services and third-party shipping apps; with Shopify's built-in rates the function may not get the address detail it needs, and a validation function on the address field is the safer route. And the payment customization can hide wallets like Shop Pay and Apple Pay, but can't rename them.

## What can I change without Plus?

More than most teams expect:

- Everything in the checkout and accounts editor: logo, palette, fonts, backgrounds for the header, main area and order summary, and corner radius. Since May 2026 the same settings carry through to customer accounts and sign-in.
- Checkout settings: contact method, which address fields are hidden, optional or required, tipping, the marketing opt-in checkboxes, and what happens after an order.
- Apps with blocks on the Thank you and Order status pages: surveys, referral codes, order tracking, upsells through order editing.
- Shopify Functions, as long as they come in a public App Store app. Many discount, shipping and payment apps are Functions underneath.
- Web pixels, for any tracking.

What stays behind the Plus line: blocks on the Information, Shipping and Payment steps, custom apps that contain Functions, and the branding API. If those are the things your business needs, the plan question is part of the architecture conversation, and I'd rather have it early. [Shopify Plus architecture](/shopify-plus-architecture/) covers how I approach that.

## How do I build a checkout UI extension?

An extension is a small amount of code in a custom app, generated and deployed with the Shopify CLI. It uses Preact and Shopify's own components (`s-banner`, `s-text`, `s-text-field` and friends), so it inherits the branding from the editor and can't look out of place. Three decisions shape every extension.

### Targets

A target is the place in checkout where the extension renders. Block targets such as `purchase.checkout.block.render` let the merchant drag the block anywhere in the editor. Static targets such as `purchase.checkout.cart-line-item.render-after` or `purchase.checkout.delivery-address.render-before` always render next to one core feature, and disappear when that feature isn't shown (no shipping methods for pickup, for example). Thank you and Order status pages have their own targets, `purchase.thank-you.block.render` and `customer-account.order-status.block.render`.

Pick a block target when the content stands on its own, a static target when it belongs to a line item, the address or the payment section.

### Merchant settings

Anything the team might want to change belongs in a setting, not in code. The extension declares its settings in `shopify.extension.toml` and reads them at runtime:

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

The merchant places the block, types the text in the editor, and changes it on a Tuesday without a deploy. The code decides how, the settings decide what.

### Reading and saving data

Extensions read the cart lines, the cost, the buyer's identity, the delivery and payment selection, and metafields on the shop, products, variants, the customer and the cart. Metafields are the right way to get data into checkout: your app writes them ahead of time, and checkout reads them with no network call. If you declare metafields in the TOML, add `owner_type` to each declaration now, because [it becomes required on API 2027-01](/blog/checkout-extension-metafields-owner-type/).

To save data, an extension writes cart attributes, line item attributes or metafields through `applyAttributeChange` and `applyMetafieldChange`. They land on the order, where the warehouse, the ERP and Flow can read them. Checkout UI extensions can also add, update and remove cart lines with `applyCartLinesChange`, which is how an upsell or an automatic gift works inside checkout. External network calls need the `network_access` capability and a request in the Partner Dashboard; use a metafield instead whenever you can.

## When do I need a Function?

When the change alters the outcome of the checkout rather than how it looks:

- A discount the admin can't express: a tiered gift, a price that depends on a customer metafield, a bundle.
- Hiding, reordering or renaming payment methods: no cash on delivery above an amount, invoice payment for approved B2B customers only.
- The same for delivery options: hide express for bulky items, rename a rate per market, hide options for PO boxes.
- Validation that stops the buyer: an order maximum, a product that can't ship to a country, a variant flagged as sold out before the warehouse count reaches zero.
- Cart transforms: expanding a bundle into its components or merging lines into one.

Functions run on Shopify's infrastructure, so there is no server of yours in the path of a purchase. They have a strict budget for how long they may run, and one that overruns fails instead of holding up checkout. That is why I reach for a Function before a custom app with its own backend.

Custom apps that contain Functions need Shopify Plus; on other plans you get Functions through public apps only. And a Function changes prices and presentation, never the contents of the cart: Cart Transform can expand, merge and update lines, but there is no operation to add one.

## What can't it do?

Knowing this up front saves a week:

- No custom JavaScript or CSS on the checkout page, and no access to its DOM. If a request starts with "can we inject", the answer is no.
- No removing or reordering Shopify's own fields and steps. Some fields can be hidden or made optional in settings; that is the extent of it.
- No changing Shopify's action buttons. Continue to payment and Pay now keep their labels and states.
- No blocks on the Information, Shipping and Payment steps without Plus.
- No adding a cart line from a Function, and no changing the order from a Thank you page extension, because the order doesn't exist yet at that moment.
- Not everything renders in accelerated checkout. In Shop Pay an extension only shows if the merchant turns on "Include app in Shop Pay" for it in the editor. In Apple Pay and Google Pay sessions, cart line changes and some other writes return errors.
- Nothing from the theme. The theme ends at the cart.

## How do I test safely?

Checkout is the one page where a mistake costs orders by the minute, so I test the same way every time:

1. Duplicate the live checkout configuration and work in the draft. Preview it in the editor and publish only when the list below is done.
2. On a development store, or with Shopify Payments in test mode, place real test orders: a guest and a signed-in customer, each market and language the store sells in, a cart just under and just over every threshold an extension or Function uses.
3. Walk the Information, Shipping and Payment steps on a phone, not only in the desktop preview. Then the Thank you page, and after a refresh the Order status page, which is a different target.
4. Test accelerated checkout separately: Shop Pay with the extension enabled in the editor, then Apple Pay or Google Pay from the product page, which skips the cart.
5. Check the order in the admin: the attributes, metafields and discounts you expected, with the names the warehouse integration reads.
6. Confirm every tool in Customer events received the purchase, in the vendor's own event log, not only the pixel status in Shopify.
7. Keep the previous configuration as a draft for a week after you publish, so rollback is one click.

If you want to see how this plays out on real stores, the posts under [checkout extensibility](/tag/checkout-extensibility/) go through specific cases.

## FAQ

### Can I still edit checkout.liquid?

No. Plus stores moved off checkout.liquid, and the Additional scripts box and script tags on the Order status page stopped running for other plans on 26 August 2026. Everything they did now belongs to a UI extension, a Function, a branding setting or a web pixel.

### Do I need Shopify Plus to customize checkout?

Not for branding, for Thank you and Order status page blocks, for Functions inside public apps, or for tracking. You do need Plus for blocks on the Information, Shipping and Payment steps, for custom apps with Functions, and for the branding API.

### Can I add a custom field to checkout?

Yes. A checkout UI extension renders the field and saves the value as a cart attribute, a line item attribute or a metafield, so it appears on the order. On Plus it can sit on any checkout step. On other plans it can only sit on the Thank you or Order status page, which works for a survey but not for information you need before payment.

### Can I hide or rename a payment or shipping method?

Yes, with a Shopify Function. Payment customizations hide, reorder and rename payment methods, with the exception that wallets such as Shop Pay, Apple Pay and Google Pay can be hidden but not renamed. Delivery customizations hide, reorder and rename shipping options. Hiding an option for PO box addresses only works with rates from carrier services and third-party shipping apps. On a non-Plus plan you get these through a public app; a custom one needs Plus.

### Do UI extensions slow down checkout?

Not when built the usual way. Shopify loads them in a sandbox alongside the page, and Functions have a hard run budget. The one thing to avoid is an extension that waits on an external network call before it renders. Read from metafields instead, and if a call is unavoidable, render first and fetch after.

### Should I use an app or a custom extension?

Start with an App Store app if one does the job and you accept another vendor in checkout. Build a custom extension when the requirement is specific to your products or operations, when you want the data in your own fields, or when the only app that fits brings ten features you don't need. One custom extension is often less to maintain than an app, and every app in checkout is a cost you keep paying; [the hidden cost of app sprawl](/blog/hidden-cost-shopify-plus-app-sprawl/) has the long version.

If your backlog has checkout requests nobody has sorted into a tool yet, or a workaround from the checkout.liquid days is still in place, [I work directly with brands on exactly this](/shopify-plus-developer-amsterdam/). Sorting the list is usually a short conversation.
