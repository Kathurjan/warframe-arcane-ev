# Warframe Arcane EV

Calculates whether buying cheap Arcanes, dissolving them into Vosfor and opening Loid Arcane packs makes a profit, using live prices from warframe.market. It finds the cheapest Vosfor sources in the current order book and the expected value of each pack at today's prices.

## How it works

- `fetch.py` downloads the Arcane data table from the Warframe wiki (Vosfor value, max rank, rarity) and current orders plus trade statistics for every Arcane from the warframe.market API.
- `common.py` loads the data and works out a realistic sell price per Arcane: the recent trade median, capped by the cheapest in-game seller and raised to the best buy order unless that order looks like bait.
- `depth.py` walks the sell order book to find what 200 Vosfor actually costs at a given budget.
- `packs.py` holds the pack drop tables and calculates expected value, the exact value distribution of a 3-slot pack, chance of profit and the break-even Vosfor price.
- `liquidity.py` adds the weekly trade limit and market volume, which turns out to be the real cap on profit.
- `fodder.py` lists the best Arcanes to buy as Vosfor fodder.
- `report.py` prints everything as Markdown tables.

Only the Python standard library is used.

## Usage

Requires Python 3.9 or newer.

```
python fetch.py      # takes a few minutes, warframe.market allows about 3 requests per second
python report.py > report.txt
python liquidity.py
```

`fetch.py` must be run first. Run it again whenever you want fresh prices.

## Example output

```
| Pack | Best packs/week | Sales/week | Trades/week | Revenue | Vosfor cost | Profit/week |
| Cavia | 0 | - | - | - | - | 0 (never profitable after trade/min-sale filter) |
| Duviri | 332 | 166 | 210 | 1284p | 919p | +365p |
```

## Notes

- Pack drop chances are taken from the wiki and hardcoded in `packs.py`. Update them if the game changes.
- Prices change constantly, so results are only valid for the time the data was fetched.
