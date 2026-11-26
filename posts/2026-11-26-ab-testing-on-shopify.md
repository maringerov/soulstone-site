---
title: "How do I run A/B tests on Shopify? Tools, theme tests and how to design a test you can trust"
slug: ab-testing-on-shopify
description: "How to A/B test on Shopify: which tools split traffic, what you can test in the theme, cart and checkout, how much traffic you need, and how to design a test you can trust."
date: 2026-11-26
tags: [shopify, cro, ab-testing, premium-brands]
draft: false
---

Short answer: how do you run an A/B test on Shopify? You use a testing app that splits visitors into groups, keeps each visitor in the same group, and shows each group a different version of a page, a theme or an offer. Change one thing per test, run it for at least two full weeks, and judge it on revenue per visitor, not on conversion rate alone. Before any of that, check that your tracking is right and that the store has enough orders for a clear read. If it doesn't, test bigger changes or don't test yet.

## What can you test on Shopify?

More than most people think, and less than the apps suggest.

- **Theme and page changes.** A new product page layout, a different hero, reviews higher up, a shorter description. Most testing apps either swap a template or run a full duplicate theme for one group.
- **Offers.** A gift above a threshold, a bundle, a free shipping level. These often move more than any layout change.
- **Prices.** A separate kind of test with its own risks. I wrote about it in [how to A/B test product prices on Shopify](/blog/ab-test-product-prices-shopify/), so I won't repeat it here.
- **Cart and checkout.** On Shopify Plus you can test checkout UI extensions, for example a row of card icons under the express buttons. On other plans checkout is mostly closed, so the cart drawer is where you test the same idea.
- **Email and pop-ups.** Klaviyo and similar tools have their own split tests. Score them on placed orders, not opens.

## Which tools do you need?

A testing app that does the split and the measuring. Look for three things:

1. It keeps a visitor in the same group across visits and devices where it can.
2. It reports revenue per visitor and, ideally, profit per visitor, with new and returning visitors apart.
3. It doesn't slow the page down or make it flicker. A test that changes the page after it loads is partly testing the flicker.

Shopify's own assistant, Sidekick, can now run tests against AI-simulated shoppers (Shopify calls it SimGym). I see it as a quick first read on an idea before you spend real traffic on it. It doesn't replace real buyers with real money.

## How do I design a test I can trust?

Most tests I see go wrong before they start. A short list of what I check:

- **Tracking first.** Place a test order in each group and check it lands in the app, in Shopify and in your analytics. This autumn Shopify started [filtering more bot traffic](/blog/conversion-rate-jump-bot-filtering/), which moved conversion rates on its own, so compare the groups inside the test, never the test against last month.
- **An A/A test.** Run the same version in both groups for a week or two. If the app shows a winner anyway, you know how much noise to expect.
- **One change per test.** Two changes at once give you an answer you can't use.
- **A written reason.** "Reviews higher up, because buyers ask about results before price" is a test. "Let's see what happens" is not.
- **A stopping rule.** Decide the run time and the number of orders before you start. Early reads shrink and flip, so don't stop the day it looks good.

## How much traffic do you need?

A common rule of thumb in CRO work is around 1,000 orders per variation before you trust a small difference. Many premium stores don't get there in a month, especially on one product.

That doesn't mean you can't test. It means you test differently:

- Test bigger changes. A small lift needs a lot of orders to show up. A large one doesn't.
- Test on templates that carry many products, not one product page.
- Run longer, and accept a wider margin of error.
- Fix what you already know is broken. That isn't a test, it's work.

## What a "test" without a control teaches you

A real example. On one store I work with, we ran a new customer offer for two weeks in October: a free gift above a basket threshold. New customer orders nearly doubled compared with the weeks before.

It looked like a clear win. But in the same two weeks the store also launched new welcome codes, new ads, a redesigned product page and a lower free shipping threshold. So what did we learn? That the package worked. Not which part of it.

That was still a useful result, and the right call for the season. It just isn't an A/B test, and it shouldn't be read as one. If you want to know whether the gift itself did the work, you need a control group that gets everything except the gift.

## When should you not test?

### During a sale

Black Friday and similar weeks bring different visitors with a different reason to buy. A result from sale week often doesn't hold in January. Run the sale, then test.

### On a page with known problems

On the same store we put testing on hold until the baseline fixes were done. A test on a page with known problems mostly measures the problems.

### When you can't act on the result

If the winning version needs a developer you don't have, or a change the brand team won't sign off, fix that first. A winner nobody ships is a cost, not a result.

## What to test first

On premium stores, in this order:

1. **The offer.** What the buyer gets and why now.
2. **The order value.** Bundles, sizes, what sits next to the main product.
3. **The page.** Layout, proof, copy, images.

The page comes last because it usually moves the least. Two cheap tests I like: card icons under the express buttons in checkout or the cart drawer, and the wording of a promo badge, for example "20% off" against "€5 off" for the same discount. The margin stays the same and only the framing changes.

## Rolling out a winner

1. Roll out in steps, for example from 30% of traffic upward, and keep a small control for a few weeks.
2. Move the winning version into the live theme or the product data, not only into the testing app. AI shopping assistants and feeds read your Shopify data, not the test.
3. Watch paid ads for a few weeks after the rollout. A version that wins on site can still change who your ads reach.
4. Write down why you think it won. That reason is the next test.

If you release theme work in more than one theme, the same rules apply to tests. I wrote about that in [single theme vs multi-theme releases](/blog/shopify-single-theme-vs-multi-theme-releases/).

## A checklist before you start

1. Tracking checked with a test order in each group.
2. An A/A test, or at least a known noise level.
3. One change, one written reason.
4. Run time and order count decided up front, at least two full weeks.
5. Revenue per visitor as the main number, new and returning visitors read apart.
6. Not in sale weeks, not on a page with known problems.
7. A plan to ship the winner into the theme or the product data.

## Questions I get about this

### Can I A/B test on Shopify without an app?

Not in a way I would trust. Duplicate pages or alternate templates linked from different ads give you two pages, not a random split, and the visitors who reach each one are different people.

### Can I test checkout on Shopify?

On Shopify Plus, yes, through checkout UI extensions and an app that can split them. On other plans you can't change much of checkout, so test the cart and the cart drawer instead.

### How long should a test run?

At least two full weeks, so every weekday shows up twice, and until each group has the orders you planned for.

### Is a test that loses a waste?

No. It tells you the idea doesn't move buyers, which saves you from building it properly. Write down why it lost, too.

### Should I run tests in-house or with outside help?

It depends on how many tests you can run and who owns them. I wrote about that choice in [in-house or outside CRO help](/blog/shopify-cro-in-house-or-external/).

If you're thinking about testing and aren't sure your store has the traffic for it, I'm happy to look at the numbers with you.