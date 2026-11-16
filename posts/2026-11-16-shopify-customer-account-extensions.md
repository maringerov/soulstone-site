---
title: "How do I show more data in Shopify customer accounts? A guide to customer account extensions"
slug: shopify-customer-account-extensions
description: "How to add loyalty points, membership and order data to Shopify customer accounts with extensions: which page to extend, where the data lives, and the limits."
date: 2026-11-16
tags: [shopify, customer-accounts, extensions, loyalty, premium-brands]
draft: false
---

Short answer: how do you show more data to customers in their Shopify account, like loyalty points, membership level or care notes for what they bought? You build a customer account UI extension in an app. Pick the page first (order list, order status, profile, or a page of your own), then decide where the data lives. If Shopify can hold it in a metafield, read it straight from the Customer Account API and skip a server. If it lives in another system, call your own app backend with a session token, never the other system directly. And handle a 429, because one rate limit is shared by every app the customer touches.

## What can a customer account extension add?

Customer account UI extensions only run on the new customer accounts, not the legacy ones. Legacy accounts are deprecated, so most stores are on the new version by now or will be soon.

There are four places to add something:

- Order list: the page customers land on after signing in. Good for a loyalty balance, an offer or a reorder prompt.
- Order status: one order, with blocks next to line items, fulfilment, payment and returns. Good for care instructions, tracking context or points earned on that order.
- Profile: name, addresses and, for B2B, the company. Good for membership level, preferences and customer fields.
- A full page of your own: a rewards page, a wishlist, an archive of past editions. There is also an order-specific full page, for things like a custom return flow.

Each of these is a target in the extension's `shopify.extension.toml`, such as `customer-account.profile.block.render` or `customer-account.page.render`. Block targets can be moved by the merchant in the checkout and accounts editor, and any extension can be limited to certain markets there.

## Where should the data come from?

This is the decision that shapes the whole build. There are three sources, and the simplest one that fits is the right one.

### Data Shopify already has

Orders, addresses and the customer profile come from the Customer Account API. An extension calls it with a plain `fetch` to `shopify://customer-account/api/{version}/graphql.json`. Shopify authenticates the request for you. No token, no server.

### Data you can store in Shopify

A loyalty tier, a preferred language, a membership number: if it can live in a metafield on the customer, the order, the company or the company location, the extension can query it through the same API.

```graphql
query {
  customer {
    metafield(namespace: "loyalty", key: "tier") {
      value
    }
  }
}
```

On order status targets, you can also declare the metafields in the TOML and Shopify delivers them with the extension, with no query at runtime. Product care notes on a past order are a good fit for that. Since API version 2026-10 each declaration takes an `owner_type`, and from 2027-01 it is required. I wrote about that change in [owner_type in checkout extension metafields](/blog/checkout-extension-metafields-owner-type/).

Writing back, for example saving a preference from the profile page, also goes through metafields. It needs the customer read and write scopes and approved access to protected customer data.

### Data that lives in another system

Loyalty platforms, ERPs and subscription tools keep their own records. The extension then needs `network_access` in its capabilities, approved for the app, and a backend you control. The extension asks Shopify for a session token, sends it to your backend as a bearer token, and the backend verifies it, reads the customer from the token and calls the other system with a key that never leaves the server.

If you can sync the few fields the page needs into metafields instead, do that. One fewer network call on every account visit, and the page still works when the other system is slow.

## What I see in practice

On a multi-market home and body care store, the custom app adds three account surfaces: a loyalty page of its own, a loyalty block on the order list, and marketing preferences on the profile page. The loyalty data lives in an outside loyalty platform, so this is the third case above, and the backend in the middle is what keeps it safe.

The mistake I look for first in a review is a vendor key placed in the extension settings so the extension can call the other platform directly. Extension code and its settings run in the shopper's browser. Anyone signed in can open devtools and read the key. If the vendor endpoint also accepts a customer ID from the request, that key can read other customers' data. The fix is the pattern above: the backend takes the customer from the verified session token, holds the key itself, returns only the fields the page shows, and the old key gets rotated.

## Why the account page is worth the effort

For a premium brand, most of the value is in the second and third order. The account page is one of the few places a returning customer looks on purpose, already signed in. That makes it a good home for the things that bring people back: their points, what they bought and how to look after it, the next tier, a refill. It does not need a pop-up or a discount to work.

Treat it like any other page you want to perform. Decide what the customer should do next on it, show one thing well, and measure whether account visitors reorder more often than they did before.

## How do I handle the Customer Account API rate limit?

Since 7 October 2026 the Customer Account API allows 3,000 requests per minute per customer on a store, shared across every app that calls it, on top of the existing cost limit. Normal traffic stays well under it. An extension that refetches on every render, or polls, can still hit it, and it then fails for every app on that customer's account, not only yours.

When the limit is hit, the API returns HTTP 429 with a `THROTTLED` error and a `Retry-After` header. A small wrapper covers it:

```js
async function accountQuery(query, variables = {}, version = '2026-10') {
  const url = `shopify://customer-account/api/${version}/graphql.json`;
  const body = JSON.stringify({query, variables});
  const opts = {method: 'POST', headers: {'Content-Type': 'application/json'}, body};

  let res = await fetch(url, opts);
  if (res.status === 429) {
    const wait = Number(res.headers.get('Retry-After')) || 1;
    await new Promise((r) => setTimeout(r, wait * 1000));
    res = await fetch(url, opts);
  }
  if (!res.ok) throw new Error(`Customer Account API ${res.status}`);
  return res.json();
}
```

Retry once, then show the page without that block rather than a spinner. Fetch once per page view, not once per component.

## A checklist before you build

1. Confirm the store is on the new customer accounts.
2. Pick one page and one job for the extension. Write down what the customer should see and do.
3. Choose the data source: Customer Account API, metafields, or your own backend. Prefer the first two.
4. Declare every metafield with its `owner_type`.
5. If you call a backend: `network_access`, session token, customer taken from the token, no keys in extension settings, CORS set on the backend.
6. Wrap Customer Account API calls with a 429 retry that reads `Retry-After`.
7. Test signed in, and on the order status page that order emails open before sign-in, on phone and desktop, in each market where the extension is on.

## Questions I get about this

### Do I need Shopify Plus for customer account extensions?

No. Shopify lists apps with UI extensions for all customer account pages as available on Basic and higher. The checkout targets on the information, shipping and payment steps are Plus only, which is where the confusion usually comes from.

### Can I add a loyalty page without a loyalty app?

You can build a full page extension in a custom app and read the balance from a metafield your own process keeps up to date. Whether that beats an app depends on how much of the programme logic you want to own. The extension is the easy part.

### Can the theme show this data instead?

The new customer accounts are not rendered by the theme, so Liquid in the theme does not reach the account pages. Extensions are the supported way to add content there.

### Is it safe to put an API key in extension settings?

No. Settings are sent to the browser with the extension. Keep keys on your backend and authenticate the extension with a session token.

### How many extensions should an account page have?

As few as the page needs. Each one that loads data is a request on every visit, and every app shares the same per-customer limit. One clear block usually beats four small ones.

If your account pages show less than your customers would expect, I'm happy to look at what yours could carry.