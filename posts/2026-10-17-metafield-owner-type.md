---
title: "owner_type in checkout extension metafields: add it now, before 2027-01 blocks your deploy"
slug: checkout-extension-metafields-owner-type
description: "From API 2026-10, checkout and customer account UI extensions can set owner_type on metafields. From 2027-01 it is required. The change and a repo check."
date: 2026-10-17
tags: [shopify, changelog, checkout-extensibility, metafields, ui-extensions]
draft: false
---

Short answer: if you have a Checkout or Customer Account UI extension that declares metafields in `shopify.extension.toml`, add `owner_type` to every declaration now. It is optional on API version 2026-10. On 2027-01 and later, Shopify blocks the deploy if any declaration is missing it. It is a two-minute change per extension, and below is a small script that finds the ones you missed.

Shopify announced this on 8 October 2026 in the developer changelog. This post shows the before and after, and how I check a repo for it.

## What changed?

Metafield declarations in `[[extensions.metafields]]` and `[[extensions.targeting.metafields]]` now accept an `owner_type` property. It names the resource that owns the metafield, such as `PRODUCT` or `CUSTOMER`. Shopify uses it to load only the metafields from the resource types your extension needs, which makes the extension faster.

The dates:

- API 2026-10: `owner_type` is optional.
- API 2027-01: `owner_type` is required on every declaration. Deploys without it fail validation.

Extensions that don't declare metafields in the TOML are not affected. Theme code is not affected either.

## Which owner types can I use?

For checkout, the supported values are:

| owner_type | What it loads |
|---|---|
| `CART` | The cart of the current checkout |
| `PRODUCT` | Products the buyer is buying |
| `PRODUCTVARIANT` | Variants the buyer is buying |
| `CUSTOMER` | The signed-in customer |
| `COMPANY` | The B2B company |
| `COMPANY_LOCATION` | The B2B company location |
| `SHOP` | The shop |

`CUSTOMER`, `COMPANY` and `COMPANY_LOCATION` data needs protected customer data access, the same as before.

## Who is affected in practice?

Any app with a Checkout or Customer Account UI extension that reads metafields from the TOML. On the stores I work with, that is usually one of these:

- A loyalty or account page extension that reads a customer metafield (a loyalty tier or a points balance).
- A checkout note or banner that reads a product or variant metafield (refill information, a gift note, a delivery warning).
- A B2B checkout block that reads company or location data.

Third-party apps handle their own extensions and API versions. If a store only uses apps from the App Store, the app developer has to make this change, not you. For custom apps, it is on whoever maintains the repo. I ran the script below on a custom app for a body care brand this week. It found over a dozen declarations without `owner_type` across several extensions (most on customer account pages, a few in checkout), and none of them were on 2026-10 yet.

## Does this apply to Customer Account UI extensions too?

Yes. The rule is the same for both extension types: `owner_type` on every metafield declaration, required from 2027-01. The customer account docs list the owner types for that surface, so check them there if your extension runs on account pages.

## What does the change look like?

Here is a typical extension on a store I work with: a note under each line item in checkout that reads a product metafield (refill information for a refillable product), plus a gift note that the team sets per variant.

Before, on 2026-07:

```toml
api_version = "2026-07"

[[extensions]]
name = "Checkout notes"
handle = "checkout-notes"
type = "ui_extension"

  [[extensions.metafields]]
  namespace = "custom"
  key = "refill_info"

  [[extensions.targeting]]
  module = "./src/LineNote.jsx"
  target = "purchase.checkout.cart-line-item.render-after"

    [[extensions.targeting.metafields]]
    namespace = "custom"
    key = "gift_note"
```

After, on 2026-10:

```toml
api_version = "2026-10"

[[extensions]]
name = "Checkout notes"
handle = "checkout-notes"
type = "ui_extension"

  [[extensions.metafields]]
  namespace = "custom"
  key = "refill_info"
  owner_type = "PRODUCT"

  [[extensions.targeting]]
  module = "./src/LineNote.jsx"
  target = "purchase.checkout.cart-line-item.render-after"

    [[extensions.targeting.metafields]]
    namespace = "custom"
    key = "gift_note"
    owner_type = "PRODUCTVARIANT"
```

Two lines added, plus the version bump.

## What if the same key lives on two resources?

This is the one case that needs thought. With `owner_type`, each declaration loads from one resource type. Shopify's migration note is clear: if you need the same namespace and key from more than one resource type, create a separate declaration for each. So if the gift note can sit on the product or on the variant, declare it twice:

```toml
    [[extensions.targeting.metafields]]
    namespace = "custom"
    key = "gift_note"
    owner_type = "PRODUCT"

    [[extensions.targeting.metafields]]
    namespace = "custom"
    key = "gift_note"
    owner_type = "PRODUCTVARIANT"
```

Then decide in code which one wins. I let the variant override the product.

## Does the extension code change?

Not for reading. Each entry from `useAppMetafields` (or `shopify.appMetafields`) already has a `target` with a `type` and an `id`, so you filter on it. On the line item target, `shopify.target.value.merchandise.id` is the variant ID:

```jsx
import '@shopify/ui-extensions/preact';
import {render} from 'preact';
import {useAppMetafields} from '@shopify/ui-extensions/checkout/preact';

export default function extension() {
  render(<LineNote />, document.body);
}

function LineNote() {
  const variantId = shopify.target.value.merchandise.id;

  const [variantNote] = useAppMetafields({
    namespace: 'custom',
    key: 'gift_note',
    type: 'variant',
  }).filter((entry) => entry.target.id === variantId);

  if (!variantNote) return null;

  return <s-text>{variantNote.metafield.value}</s-text>;
}
```

The filter type is lower case (`variant`, `product`), while `owner_type` in the TOML is upper case (`PRODUCTVARIANT`, `PRODUCT`). That mismatch is easy to get wrong.

## How do I find declarations that are missing it?

I don't trust myself to read every TOML by eye on an app with several extensions. This script (Python 3.11 or later, no dependencies) lists every metafield declaration without `owner_type` and exits with code 1 if it finds one:

```python
import sys, tomllib, pathlib

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
missing = 0
for path in root.glob("extensions/*/shopify.extension.toml"):
    data = tomllib.loads(path.read_text())
    for ext in data.get("extensions", []):
        decls = list(ext.get("metafields", []))
        for t in ext.get("targeting", []):
            decls += t.get("metafields", [])
        for m in decls:
            if "owner_type" not in m:
                missing += 1
                print(f"{path}: {m['namespace']}.{m['key']} has no owner_type"
                      f" (api_version {data.get('api_version')})")
sys.exit(1 if missing else 0)
```

Run it from the app root: `python3 check_owner_type.py .`

Output looks like this:

```
extensions/checkout-notes/shopify.extension.toml: custom.gift_note has no owner_type (api_version 2026-10)
extensions/account-tier/shopify.extension.toml: $app:loyalty.tier has no owner_type (api_version 2026-07)
```

Because it exits with 1, you can add it to CI next to your lint step. Then nobody bumps an extension to 2027-01 without the field.

## What should I capture to confirm it worked?

If you hand this to a client or a team lead, these screenshots are enough:

1. The terminal output of `shopify app deploy` on 2026-10 with no metafield validation errors.
2. The checker script with exit code 0.
3. Checkout in a dev store with a product that has the metafield set. The note sits under the line item.
4. The same checkout with a product where the metafield is empty. No empty box appears.

## When should I do this?

Now, while it is optional. The upgrade to 2027-01 will come with other changes, and you don't want a deploy blocked by a missing field while you are fixing something else. On the stores I work on, I add it as part of the 2026-10 bump, and I've added a rule to my own checklist: no new metafield declaration without `owner_type`.

Source: the Shopify developer changelog entry of 8 October 2026 and the "Using metafields for custom data in checkout" docs on shopify.dev.
