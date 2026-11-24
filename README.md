# The World in One Day — Tuesday 24 November 2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/Koceng144/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/Koceng144/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

Entry for the [news-image-20261124 bounty](https://make.fun/bounties/news-image-20261124):
**"Sum up 24 November's world news in one image."**

A cream magazine-cover front page — a huge burning-tanker hero in the
Strait of Hormuz with the headline overlaid on a dusk-orange sky, a
Sanofi lead image panel ($41bn Insmed deal), two smaller secondary
image panels with captions (the Nepal quake, Hormuz talks), an honest
markets %-bar strip, the day in ten as a numbered 3-column index with
region tags, a dotted world map with numbered pins (leads 1–10), 28 more
stories, and a DATE CHECK box holding over the big stories that were
*not* Tuesday's news. 38 stories total. Earlier variants (v2 broadsheet,
v3 cover) are kept in-repo as `entry.png` / `entry-v3.png` with their
builders; the submitted image is `entry-v4.png`.

Date rule: leads 1–10 all happened on Tuesday 24 November 2026.
Items 11–38 were reported on 24 Nov; some describe events of 22–23
Nov (Nvidia's chief returning, the warship sinking off Libya, the NATO
space warning) and are worded as reports in the tail list only, never
as leads and never as "happened today". See `facts-2026-11-24.md`
for the per-story verification and the DATE CHECK exclusions.

`main.py` (stdlib only) copies the pre-composed `entry-v4.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`). `build-v4.py`
composes the image offline with PIL; run `python3 build-v4.py` to
re-render it. No network, deterministic — two runs write identical
bytes.
