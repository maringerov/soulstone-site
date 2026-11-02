---
title: "Your Shopify conversion rate jumped this autumn and nothing changed: it is the bot filter"
slug: conversion-rate-jump-bot-filtering
description: "Shopify changed how it counts sessions on 21 to 23 September 2026 and now filters bots by default. Why conversion rate moved, and what to compare for Black Friday."
date: 2026-11-02
tags: [shopify, analytics, conversion-rate, black-friday, premium-brands]
draft: false
---

Short answer: if your Shopify conversion rate went up in late September and your orders didn't, nothing happened to your store. Shopify changed how it measures sessions between 21 and 23 September 2026, and identified bot sessions are now left out of session reports by default. Fewer sessions with the same orders gives a higher conversion rate. For Black Friday targets and year on year reports, compare orders, net sales and customers. Treat conversion rate from before the change as a different ruler.

## What did Shopify change in September?

Shopify's help page on the update lists three changes to session measurement:

- Sessions follow continued customer activity instead of ending at midnight UTC. A session still ends after 30 minutes of inactivity.
- Some sessions without a pageview now count, for example a customer who goes straight to checkout from a cart link.
- Identified bot sessions are filtered out of session reports by default.

The first and third make your session count smaller. The second makes it larger. If bots were a real share of your traffic, the net result is fewer sessions.

Shopify is clear that "your orders, sales, and customer counts aren't affected by this update." Only the session side of the sum moved.

## Why does conversion rate go up when bots are filtered?

Conversion rate is orders divided by sessions. Bot sessions buy far less often than people do, so they sit in the bottom of that sum and pull the rate down. Take them out and the rate rises, even though the same people bought the same things.

Shopify's own example on its bot filtering page: 1,000 sessions and 35 completed checkouts read as 3.5%. Split out the 250 bot sessions and the human rate is 4%. Nobody changed the product page. The ruler changed.

Some operators on X posted large jumps on their stores in the weeks after the rollout. I'd treat those as single cases. Yours depends on how much bot traffic you had, and that varies a lot between stores.

## Which numbers are affected?

Shopify lists the metrics that can change. The ones that show up in most client reports:

- Sessions and online store visitors
- Conversion rate, add to cart rate, reached checkout rate and checkout conversion rate
- Bounce rate, pageviews per session and average session duration

It also lists the reports that use them: the Analytics overview, Live View, acquisition, behavior and marketing reports, search and product recommendation reports, and any custom report built on sessions. If an app reads session data from Shopify Analytics, its numbers can move too.

This is a change to Shopify Analytics. GA4 and your ad platforms count sessions their own way and are not part of it. So if your Shopify conversion rate and your GA4 conversion rate disagreed before, expect them to disagree differently now.

## Can I still compare with last year's Black Friday?

For orders, net sales, average order value and customers, yes. Those are counted from orders and didn't change.

For conversion rate and anything else built on sessions, not directly. Two details from Shopify's page matter here:

1. Bot classification only exists for sessions from 7 October 2025 onwards. Black Friday 2025 falls after that date, so the bot filter can be applied to it.
2. Even with the same filter setting, Shopify says sessions measured before the update are not directly comparable with sessions measured after it. The midnight rule and the no-pageview sessions changed too.

So last November's conversion rate is a number from a different method. If a Black Friday target was written as "beat last year's conversion rate", it will look beaten before the first email goes out.

## How I'd set targets for this peak season

What I recommend for November:

1. Write the targets in orders, net sales, average order value and new versus returning customers. Last year's figures for those still hold.
2. Note the rollout dates, 21 to 23 September 2026, in the report itself. Whoever reads it in January should not have to work out why the conversion rate line steps up in the middle.
3. Use October 2026 as the new session baseline. If you want a conversion rate target, base it on the weeks after the update, not on last year.
4. In reports that have the Human or bot session filter, keep the same setting for every period you compare. The Home page and Live View always hide bots and can't be switched.
5. Read any before and after test with care. A test that ran its two versions side by side is fine, because both arms were measured the same way. A "we changed the PDP in September and conversion went up" story needs checking against orders first.

## A five minute check in your admin

1. Go to Analytics > Reports and open Sessions by landing page or Sessions by device.
2. Set a period after the update and compare it with another period after the update.
3. If the report shows the Human or bot session filter, confirm both periods use the same value. Add Human or bot session as a dimension once, to see how much of your traffic was bots.
4. Open the Analytics overview for the same dates and look at orders, sales and customers.
5. If sessions moved and orders didn't, the update explains it. Write that down next to the chart.

If you run a headless storefront, Shopify notes that filters and session behaviour can differ depending on how storefront analytics are set up. Have your developer check it before you trust the new numbers.

## Questions I get about this

### Did my store get better at converting?

Not because of this. If orders, net sales and customer counts are flat while conversion rate is up, the change is in how sessions are counted.

### Can I turn the bot filter off?

In reports that support the Human or bot session filter, you can include bot sessions again. The Home page, Live View, and the search and product recommendation reports filter bots automatically and can't be changed.

### Does this mean bots are now blocked from my store?

No. The filter changes your reports. Bots can still visit; they are just counted separately. Shopify also notes some automated traffic isn't classified straight away, so the split improves over time.

### Should I change my CRO plans?

Not the plans, the baseline. Conversion rate is still useful for comparing periods measured the same way. Just don't let a measurement change claim credit for work that hasn't shipped yet.

If you want a second pair of eyes on your Black Friday numbers before the targets go to the board, I'm happy to look.
