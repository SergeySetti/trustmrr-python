<h1 align="center">trustmrr 🐍💸</h1>

<p align="center">
  <i>A Python client for the <a href="https://trustmrr.com">TrustMRR</a> API,<br/>
  for people who like their startup data the way they like their coffee:<br/>
  <b>strong, typed, and delivered in cents.</b></i>
</p>

<p align="center">
  <a href="https://pypi.org/project/trustmrr/"><img alt="PyPI" src="https://img.shields.io/pypi/v/trustmrr.svg"></a>
  <a href="https://pypi.org/project/trustmrr/"><img alt="Python" src="https://img.shields.io/pypi/pyversions/trustmrr.svg"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-Apache%202.0-blue.svg"></a>
</p>

---

## What is this? 🤔

You want to know which startups are on sale. You want to know their MRR, their multiples, their vibes. You want it in Python. You do **not** want to write `requests.get(...)` for the seventeenth time this week.

This library does that. You're welcome.

## Install 📦

```bash
pip install trustmrr
```

That's it. No build step. No native deps. No "first install Rust." It's 2026 and we're not animals.

## 60-second quickstart ⏱️

```python
from trustmrr import TrustMRRClient

client = TrustMRRClient(api_key="tmrr_your_api_key")  # don't commit this. don't.

deals = client.list_startups(sort="best-deal", on_sale=True, limit=5)

for s in deals["data"]:
    print(f"{s['slug']:20} MRR ${s['revenue']['mrr']/100:>10,.2f}  multiple {s['multiple']}x")
```

Output (your numbers will vary, theirs always do):

```
acmehq               MRR $  35,000.00  multiple 3.2x
widgetco             MRR $  18,420.00  multiple 2.7x
...
```

## Pagination, the lazy way 😴

You could write a `while True:` with a page counter and a `hasMore` check. Or you could not.

```python
for startup in client.iter_startups(category="SaaS", min_mrr=100_000):
    print(startup["slug"])
```

`iter_startups` yields rows forever until the API politely says "I have no more startups for you." It will then stop. Generators: still good.

## All the knobs 🎛️

Every parameter is keyword-only and optional. Set what you need, ignore the rest.

| Knob | Type | What it does |
|------|------|--------------|
| `page` | `int` | Page number (≥ 1). For when you're feeling sequential. |
| `limit` | `int` | 1–50. The API draws the line at 50. We agree with the API. |
| `sort` | `str` | One of: `revenue-desc`, `revenue-asc`, `price-desc`, `price-asc`, `multiple-asc`, `multiple-desc`, `growth-desc`, `growth-asc`, `listed-desc`, `listed-asc`, `best-deal`. |
| `on_sale` | `bool` | `True` for "show me the bargain bin." |
| `category` | `str` | `"SaaS"`, `"AI"`, `"fintech"`, and 20 friends. |
| `x_handle` | `str` | Founder's X/Twitter handle. Skip the `@`, we'll know. |
| `min_revenue` / `max_revenue` | `number` | Last-30-day revenue, in **cents**. |
| `min_mrr` / `max_mrr` | `number` | MRR, in **cents**. |
| `min_growth` / `max_growth` | `number` | Decimal. `0.1` = 10%. `1.0` = "are you sure?" |
| `min_price` / `max_price` | `number` | Asking price, in **cents**. |

> 💡 **Everything monetary is in cents.** `42500` means `$425.00`. Yes, we checked. Twice. Divide by 100 before showing it to humans.

## When things go sideways 💥

Non-2xx responses raise `TrustMRRError`. It has a `.status_code` and a `.payload`, both of which are nicer than a generic `requests.HTTPError`.

```python
from trustmrr import TrustMRRError

try:
    client.list_startups()
except TrustMRRError as e:
    if e.status_code == 401:
        print("Your key is wrong, or expired, or imaginary.")
    else:
        print(f"API said {e.status_code}: {e.payload}")
```

## Wait, where do I get an API key? 🔑

[trustmrr.com](https://trustmrr.com). Then read the [API docs](https://trustmrr.com/docs/api/list-startups) for the source of truth on parameters and response shape. (This README is the friendly tour; the docs are the legal text.)

## Development 🛠️

```bash
git clone https://github.com/SergeySetti/trustmrr-python.git
cd trustmrr-python
pip install -e ".[test]"
pytest
```

All tests are offline — HTTP is mocked, your wallet is safe.

Want to help? See [CONTRIBUTING.md](CONTRIBUTING.md). PRs welcome, opinions free.

## License 📜

[Apache 2.0](LICENSE). Use it, fork it, ship it, sell it. Just don't sue us.

---

<p align="center"><sub>Made with 🐍, ☕, and a healthy distrust of un-typed JSON.</sub></p>
