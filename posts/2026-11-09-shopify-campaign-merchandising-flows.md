---
title: "Shopify merchandising for complex campaigns: how to run launches, gifts and members-only drops without breaking the store"
slug: shopify-campaign-merchandising-flows
description: "How to set up Shopify merchandising for campaigns and promotions: give each product state one switch, keep cart and checkout rules in sync, and test the whole flow before launch."
date: 2026-11-09
updated: 2026-11-13
tags: [shopify, merchandising, promotions, campaigns, shopify-plus, premium-brands]
draft: false
---

Shopify merchandising for complex campaigns, launches, gifts and members-only drops works when every product state has one switch, one owner and one place where it is set. Write those switches down as a short merchandising guide, keep anything that lives in two places (theme and checkout) in sync on purpose, and test each campaign in a real cart before it goes live. Most campaign bugs I see are not code bugs. They are two tools that both think they own the same product.

## Why do campaigns get messy on Shopify?

A normal product is simple. It is published, it has a price, it shows in collections and search, and anyone can add it to the cart.

Campaigns add exceptions. A launch is visible but locked for everyone except members. A gift is in stock but must never show in a collection. A sample is added for free, but only when a certain product is in the cart. A limited edition hides from search but should still appear in one curated edit.

Each exception is easy on its own. The trouble starts when they stack. On a multi-market home and body care brand I work with, the store ran five of these special cases side by side. Each used a different part of the admin: product tags, theme templates, theme settings, a loyalty app, a cart app and a custom checkout app. When the team mixed them up, products disappeared, the wrong button showed on the product page, or a gift showed up free in the cart and full price at checkout.

## What are the product states a campaign needs?

Before you build anything, list the states. On that store, this was the full set:

- Members only: visible to everyone, buyable only by logged-in members. Everyone else sees a join button instead of Add to cart.
- Preorder: a normal product page with a Pre-order button, selling while stock is on its way.
- Spend-based gift: hidden from browse and search, added to the cart for free once the cart passes a spend tier.
- Product-based sample: added for free when a qualifying product is in the cart, run by a different rules engine than the spend gift.
- Hidden except in one collection: out of search and most listings, but shown in one launch edit.

Your list will differ. The point is to name each state, so the team talks about "a members-only product" and not "the one with the tag".

## How do you give each state one switch?

Pick one control per state and use nothing else for it. On that store it looked like this:

- Members only: one product tag. The theme reads the tag and the customer's loyalty tag, and decides which button to show.
- Preorder: one product template with a preorder suffix, plus "continue selling when out of stock" on the variant.
- Spend-based gift: one gift template that hides the product everywhere, plus the tier settings.
- Hidden in one collection: one hidden tag plus one product metafield that holds the target collection handle.

Then write down how the switches interact, because they will. A product can be both members only and preorder. Members then see Pre-order and everyone else still sees the join button. A store-exclusive tag beats the members-only tag. Decide those rules once, and put them in the guide.

## Why does a gift need to match in two places?

On Shopify, the cart and the checkout are run by different code. A spend-based gift is usually added by the theme or a cart app, and made free by a discount or a checkout function. If the theme says the first tier unlocks at one amount and the checkout rule says another, the shopper sees a free gift in the cart and pays for it at checkout. Or the gift appears and then vanishes.

That store's guide starts with one line: you always update two screens. Same gifts, same order, same spend amounts. Theme settings first, then the checkout app, then save both. It sounds basic. It is also the step that gets skipped at 17:00 on the day before a campaign starts.

If you can, have one of the two read from the other so there is only one number to change. If you can't, put the match check in the go-live list.

## Which tool should run which offer?

Use one rules engine per type of offer, and write the decision down:

- A gift for spending over a threshold goes in the spend tiers.
- A free sample when a specific product is in the cart goes in the cart app's rules.

Putting a sample into the spend tiers, or a spend gift into the sample widget, does not fail loudly. It just creates two engines that both add lines to the same cart. Also keep the spend total honest: free gift lines and free samples should not count toward the threshold for the next tier.

## How do you make campaign content editable without a developer?

Seasonal campaigns repeat every year, so build them as content, not code. For a December calendar campaign we built one section driven by metaobjects: one entry per day, with a title, image, call to action, an optional reward badge and an optional start and end time. The doors unlock on the store's own timezone. The team fills in the entries in the admin and adds the section in the theme editor. Next year they change the year and the content, and no one touches the theme code.

The same idea works for launch edits, campaign banners and gift messaging. If the merchandising team has to open a ticket to change a date, the flow is too tightly tied to the code. That also means keeping one live theme, not a copy per campaign. I wrote up [single theme vs multi-theme releases](/blog/shopify-single-theme-vs-multi-theme-releases/).

## What should you test before a campaign goes live?

Run the campaign in a real cart on a preview theme, on phone and desktop. The list we use:

1. Gifts and discounts are switched on, and every active tier has a product and a spend amount.
2. Thresholds are checked for each market, including any country overrides.
3. Below the threshold there is no gift. At the threshold the gift adds itself. Change the quantity and check that the gift moves up or down a tier.
4. The gift line is free at checkout, not only in the cart.
5. Hidden products are out of search and listings, and present in the one collection they belong to.
6. Members only products show the right button for a guest, a logged-in non-member and a member.
7. Any testing switches used during QA are turned off before publish.

Write down what you saw. A short note with the date and the result is enough.

## Questions I get about this

### Do I need Shopify Plus for complex campaign merchandising?

Not for most of it. Tags, templates, metafields and theme settings work on every plan. Plus matters when you want checkout logic of your own, such as a custom gift rule enforced in checkout.

### Should I use an app for gift with purchase or build it in the theme?

It depends on how many offer types you run. One simple gift is fine in an app. Several tiers, markets and members-only rules usually work better in the theme plus one checkout rule, with a clear guide. I wrote about the setup options in [How to add gift with purchase in Shopify](/blog/shopify-gift-with-purchase-setup/).

### Why did a product disappear from the store?

Usually two switches are fighting. The most common cases: the product is hidden but was never added to its target collection, the collection metafield holds the title instead of the handle, or a hidden template was left on after the campaign ended.

### How many tools are too many for one campaign?

When nobody on the team can say which tool owns a product's current state. More tools also means more app weight on the storefront, which I covered in [the hidden cost of Shopify Plus app sprawl](/blog/hidden-cost-shopify-plus-app-sprawl/).

If your next launch stacks a few of these and you want a second pair of eyes on the setup, I'm happy to look.
