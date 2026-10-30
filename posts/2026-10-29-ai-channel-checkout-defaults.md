---
title: "What Shopify's AI channel checkout defaults are and how to change them"
slug: ai-channel-checkout-defaults
description: "By default Shopify shares products with AI channels and runs direct checkout in Google, Meta and Copilot. Open Sales channels > Agentic, turn off Allow Shopify to manage for me, then set each channel."
date: 2026-10-29
updated: 2026-10-30
tags: [shopify, agentic-commerce, checkout, ai-channels, premium-brands]
draft: false
---

What Shopify's AI channel checkout defaults are and how to change them: open Sales channels > Agentic in your Shopify admin. By default your products are shared with AI channels, direct checkout runs inside Google AI Mode and Gemini, Microsoft Copilot and Meta where they support it, and "Allow Shopify to manage for me" enrols your store in every new AI channel that comes along. Turn that setting off first. Until you do, the per-channel switches are not there to change. That default may be fine for you. It should still be a choice you made, not one you found in December.

## What is on by default?

Shopify's help page puts it plainly: "By default, all available channels have access to your products through Shopify Catalog." It goes on: "Direct checkout in AI channels is active where supported."

The setting that holds it all together is "Allow Shopify to manage for me". With it on, three things are true:

- AI channels can read your products through Shopify Catalog.
- Direct checkout is switched on for the channels that offer it.
- You are enrolled in new agentic storefronts automatically.

Direct checkout means the customer pays inside the chat. They never load your store. Shopify lists Google AI Mode and Gemini, Microsoft Copilot and Meta surfaces such as Muse as the channels that offer it. ChatGPT works differently today: it sends the buyer to your own checkout in an in-app browser or a new tab.

## Does this apply to a European brand?

Partly. Direct checkout is limited by where the buyer is. For Google AI Mode and Gemini it is rolling out to customers in the United States, Canada and Australia. For Meta it shows only to customers in the United States, Canada, Mexico, Brazil, Japan and Singapore.

So if you sell only inside the EU, buyers won't see direct checkout yet. Catalog access and automatic enrolment still apply to you. If you ship to the US or Canada, which many premium brands from here do, all of it applies now.

## What doesn't carry over into a direct checkout?

This is the part a design-led brand should read twice. According to Shopify's pages for Google and Meta, these don't work in their direct checkouts:

- Product bundles, customizable products and products sold only as subscriptions. A product with both options can still be bought once, without the subscription.
- Google Analytics and custom pixels. Only server-to-server checkout events fire, so your client-side tags never see the order.
- Local delivery, pickup in store and pickup points.
- Requiring customers to sign in before checkout.
- Most checkout blocks. Meta supports none. Google loads only the blocks that are essential to complete the purchase, and names upsells, loyalty, trust badges and consent collection among those that may not show.

What does run: Shopify Functions for shipping, discounts and validation, plus your automatic discounts and discount codes. The order lands in your admin attributed to the channel, and you stay the merchant of record for fulfilment, returns and service.

For a brand where the gift set, the engraving field, the loyalty points or the newsletter opt-in at checkout carry part of the sale, that list matters more than the headline.

## How to choose per channel

Turn off "Allow Shopify to manage for me" first. Until you do, the per-channel switches are not there to change. Then work through each one.

I'd keep direct checkout on for a channel if:

- Your best sellers are simple, single products that a buyer can choose from a photo and a price.
- You ship to the countries where that channel offers it, and you can read the orders in Shopify's own reports.

I'd switch direct checkout off, so buyers finish on your store, if:

- Your best sellers are bundles, sets, subscriptions or personalised products.
- Your checkout carries something you depend on: a gift note, a delivery date, a loyalty step or a marketing opt-in.
- Your reporting relies on GA4 or ad platform pixels and you need a clean read through Black Friday on 27 November.

Switching direct checkout off doesn't hide you. Shopify's pages say customers can still discover your products in that channel and are sent to your store to buy.

Two more settings are worth a decision:

1. Auto enroll new storefronts. I'd turn this off for most premium brands. New channels will keep arriving, and you can still join each one by hand once you've seen how it presents your products.
2. Shopify Catalog access. Only switch it off if you don't want to be in AI channels at all. Shopify notes it can take up to 7 days to stop sharing, that it also turns off direct checkout, and that your products can still be found through ordinary web crawling.

One trap: if you turn "Allow Shopify to manage for me" back on later, it switches every setting on again, direct checkout included.

## How to check it worked

A 10-minute check once you've saved:

1. Open Sales channels > Agentic and confirm "Allow Shopify to manage for me" is off and each channel shows the checkout setting you chose.
2. Check that the staff who should have access do. Shopify requires the store owner or a staff member with the Agentic permission.
3. Look at the performance view on the same page. It shows sales, orders and online store sessions per AI channel, so you can see whether any of this already moves money for you.
4. Write down what you chose and why, so whoever runs the store in November knows it was on purpose.

If tracking is still patchy after the checkout changes this summer, start with [the checkout extensibility tracking check](/blog/checkout-extensibility-migration-tracking/). Orders from a direct checkout won't show up in client-side tags at all, so it helps to know which numbers you trust before you add a channel your pixels can't see.

## Questions I get about this

### Is my store on this already?

If your store is eligible and you never changed anything, yes. "Allow Shopify to manage for me" is the default, and it means all channels are active.

### Will turning off direct checkout remove me from ChatGPT or Gemini?

No. Direct checkout only decides where the purchase happens. Your products can still appear, and the buyer is sent to your store to finish.

### Who owns the customer on these orders?

You do. Shopify says orders from AI channels show in your admin with channel attribution, and you keep the customer relationship and the post-purchase experience. What you may lose is the marketing opt-in, because consent blocks may not display in those checkouts.

### Is the Shop app part of this?

Shop is listed with the other channels, but you can't switch off its Catalog access from the Agentic page. Its checkout behaviour lives in the Shop sales channel settings.

If you sell to the US or run bundles and subscriptions, this is a short review before peak season. I'm happy to look through the settings with you.
