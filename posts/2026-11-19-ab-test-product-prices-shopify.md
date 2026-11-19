---
title: "How do I A/B test product prices on Shopify? What to measure, how much traffic you need and when to wait"
slug: ab-test-product-prices-shopify
description: "How to A/B test product prices on Shopify: how a price test works, why revenue per visitor beats conversion rate, how much traffic you need, and when to wait."
date: 2026-11-19
tags: [shopify, cro, pricing, ab-testing, premium-brands]
draft: false
---

Short answer: how do you A/B test product prices on Shopify? You use a price testing app that shows a share of visitors a different price and charges that same price in checkout. Test one price step at a time, often 10 to 20% up, and judge it on revenue per visitor and profit per visitor, not on conversion rate. Check that the store has the traffic for a clear read, keep tests out of sale weeks, and when a price wins, write it into the product data in Shopify so every channel shows it.

## Why test price at all?

Most premium brands set a price once, at launch, from cost, a target margin and a look at a few competitors. Then the product gets better, the brand gets known, reviews pile up, and the price stays where it was.

A price test is the cheapest way to find out whether the price still fits what the product is worth to the buyer. People who run these tests often report that a 10 to 20% increase barely moves conversion, and sometimes lifts it, because a higher price reads as a better product. Those reports are self-reported and won't hold for every brand. That is exactly why you test instead of guessing.

## How does a price test work on Shopify?

The app splits visitors into groups and keeps each visitor in the same group when they come back. Each group sees its own price everywhere: collection page, product page, quick add, cart and checkout.

Checkout is the part to check. If the product page shows the test price and checkout charges the old one, you don't have a test. You have a broken promise.

Before the test goes live, place a test order in each group and check:

- the price on the collection page, product page, cart drawer and checkout
- the order confirmation email and the order in the admin
- anything else that reacts to the price: bundles, a gift with purchase threshold, a free shipping threshold
- the price in each market and currency you sell in

## What the test doesn't reach

A price test runs on your storefront. Some places read the price from somewhere else:

- **Shopping feeds.** Google checks that the price on the landing page matches the price in the feed. If the app can keep traffic from shopping ads on the current price, use that. If it can't, talk to whoever runs the feed before you start.
- **AI assistants.** Shopping agents read the price from your Shopify product data, not from the theme or the test app. During the test they see the current price, and that traffic can't be part of the test.
- **Email and ads.** A campaign that names a price keeps naming the old one.

The same goes the other way after the test. A winning price that only lives in the test app is invisible to feeds and agents, so it has to go into the product itself.

## What should you measure?

Revenue per visitor is conversion rate times average order value. Profit per visitor adds the margin. Those are the two numbers that decide a price test.

An example with made-up round numbers. At €60 the product converts at 2.0%: €1.20 per visitor. At €69 it converts at 1.9%: about €1.31 per visitor. Conversion went down, revenue per visitor went up about 9%. With a product cost of €20, profit per visitor goes from €0.80 to about €0.93. Read only conversion rate and you would have kept the lower price.

Two more splits are worth reading:

- **New and returning visitors.** On a Dutch skincare store I work with, about three in four orders come from returning customers. They know the old price. A regular who sees a higher price on a product they reorder is a different test from a new visitor seeing it for the first time.
- **Traffic source.** A higher price can suit people who already know the brand and put off cold traffic from ads. After a rollout, watch paid ads for a few weeks: new customer acquisition cost and the share of new visitors.

## How much traffic do you need?

A common rule of thumb in CRO work is around 1,000 orders per variation before you trust a revenue result. Many premium stores don't sell that many of one product in a month.

That doesn't rule out price testing. It changes the plan. Test one price step across a group of products instead of one product, run it longer, and accept a wider margin of error. Compare the groups inside the test period, never the test against last month. This autumn Shopify started [filtering more bot traffic](/blog/conversion-rate-jump-bot-filtering/), and that moved conversion rates on its own.

And fix the page first. On the same skincare store we put testing on hold in October until the baseline fixes were done. A test on a page with known problems mostly measures the problems.

## When should you not run a price test?

### In sale weeks

Black Friday traffic, discounts and gift offers swamp a price result. Run the test after the sale, when traffic is back to normal. A price test on the hero cream of that skincare store is one of the tests I have lined up for after Black Friday, not during it.

### When a "was" price is involved

In the EU, a price reduction has to be shown against the lowest price of the previous 30 days. A test that moves the regular price and also shows a compare-at price can conflict with that. Keep price tests on the regular price, with no compare-at.

EU rules also require telling shoppers when a price is personalised by automated decision-making. Whether a random price test counts is not settled, so check with whoever advises you on consumer law before you run one in the EU.

### On an entry product

Some products are priced to bring people in. On the skincare store, about one in five buyers of a trial kit came back for a full-size product, mostly within about a week. That kit earns its keep on the second order, not the first. A test that only reads the first order would push its price up and miss the point.

## What to test besides the number

The price is one lever. The choice around it is another:

- **The options on the page.** CRO practitioners report that removing the cheapest size from a product page often raises revenue per visitor, in one report about half the time.
- **Value before price.** A bundle, a gift or a better explanation of what the product does can make a higher price feel fair. Test the value first, then test the price on top of it.

Both are easier to run than a price test, and they need the same measurement.

## Rolling out a winner

1. Roll out in steps, for example from 30% of traffic upward, and keep a small control for a while.
2. Write the price into the Shopify product, and into each Markets catalog for other currencies. Some testing apps can export the winning prices in Markets catalog format.
3. Update the shopping feed, email templates and any copy that names the price.
4. Write down why you think it won. That reason is the next test.

## A checklist before you start

1. Fix the known problems on the product page first.
2. Pick one price step and one product or group of products.
3. Check you can reach a useful number of orders per group in a few weeks.
4. Place a test order in each group and check every place the price shows.
5. Decide how shopping ad traffic and the feed are handled.
6. No compare-at prices during the test, and check the EU rules for your markets.
7. Measure revenue and profit per visitor, split by new and returning visitors.
8. Keep it out of sale weeks.

## Questions I get about this

### Can I test prices on Shopify without an app?

Not in a way I would trust. Duplicate products or discount codes can show different prices to different people, but not as a random split that holds from the product page through checkout, and duplicates split your reviews and search results.

### How long should a price test run?

At least two full weeks, so every weekday shows up twice, and until each group has the orders you planned for. Don't stop it the day it looks good.

### Will a higher price hurt a premium brand?

Sometimes the opposite. For a brand that sells on quality, a price that is too low can make buyers wonder what is wrong. The test tells you where that line is for your buyers.

### Should returning customers see the test price?

That is a choice to make before you start. Excluding them protects your regulars from a surprise. Including them tells you how the price lands with the people who buy most. If you include them, read them separately.

### What about subscriptions?

Test the one-time price first. A subscription price changes what customers pay for months, so a test there needs a longer read on cancellations, not only the first order.

If you're thinking about a price change and aren't sure your store can carry a test, I'm happy to look at the numbers with you.