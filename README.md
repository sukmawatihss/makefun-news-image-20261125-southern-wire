# THE SOUTHERN WIRE — News Image, Tuesday 25 November 2026

[![make.fun](https://img.shields.io/badge/make.fun-bounty%20entry-orange)](https://make.fun/bounty/news-image-20261125)
[![Bounty](https://img.shields.io/badge/bounty-news--image--20261125-blue)](https://make.fun/bounty/news-image-20261125)
[![Author](https://img.shields.io/badge/author-@sukmawatihss-green)](https://make.fun/bounty/news-image-20261125)

A one-page wire front page for **Tuesday 25 November 2026 — 37 stories from
9 regions, checked**: a burgundy-and-silver broadsheet built from a locked
pool of that day's reporting, with three lead stories (Baghdad's oilfields
order, NATO AWACS for Poland, the Gaza drone strikes), ten more full-scene
cards, a numbered map, and 24 numbered briefs — every figure taken from the
pool, claims labelled as claims, and the Monday Nvidia close tagged as such.

- `entry.png` — the finished 1024×1024 front page
- `compose_c.py` — the pure-stdlib (no PIL, no network) page composer:
  layered story-specific scenes, full decks, standalone source/certainty
  foot lines, data chips as badges over the scenes
- `main.py` — copy-only runner: renders via `compose_c` and copies the
  result to `entry.png`

Run it with:

```bash
python3 main.py
```

Bounty: https://make.fun/bounty/news-image-20261125
