# ZX Infrastructure engineering interview assignment

This repo contains a minimal prototype app that fetches cryptocurrency prices and writes timestamped CSV snapshots to `./data`. There are two services: `app/web/fetch_prices.py`, which pulls crypto prices from several sources and `app/web/server.py`, which exposes read-only endpoints for the end user. However, no automation, CI/CD, or modern devops practices have been applied; instructions to start the application are outlined below.

Your goal is to build out the CI/CD platform to the greatest degree possible within a reasonable amount of time. 
Depending on your background, interest and available time, this may or may not involve:
- creating a reproducible execution environment using tools like Docker and/or Ansible
- automating environment builds and testing using Github Actions/Gitlab CI
- programmatic infrastructure provisioning with Terraform
- setting up basic observability using Grafana, etc.
- automate app deployment
- anything not listed that you feel is important in a production application

The deliverable is a link to a copy of this repo that includes
the implementation of components of the CI/CD pipeline. The README should be updated
to include updated documentation indicating how to run and deploy the
updated application. Complete 

We are looking for:
- general clean coding practices 
- systems-level design and thinking 
- modularity and clarity
- clear and thorough documentation

_There is no need to deploy the application to a cloud provider directly_ (please don't spend money!), so please use your favorite local development solution (like docker or VMs) for a "mock deployment" solution that we can reproduce locally. However, deployment should be implemented with a future cloud deployment and scale-up in mind: you should be able to quickly adapt the repo to AWS/Azure/GCP with minimal overhead and documentation.

We encourage you to ask any clarifying questions that would help you to come up
with a better solution. 

Finally, we obviously can't prevent you from using LLM-based tools while solving
this assignment. However, _we prefer a high-quality partial solution over a 
low-quality, but more complete solution._ As such, you will not be penalized for a 
partial solution: we will evaluate what has been completed on its own merit.

## App deployment 

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .

# fetch a snapshot
python app/fetch_prices.py --assets bitcoin,ethereum,solana --out data

# run tiny web server (read-only)
export DATA_DIR=data
python app/web/server.py  # exposes /health and /latest

# run fetcher service that writes snapshots every minute and exposes status endpoints
export DATA_DIR=data
python app/web/fetch_prices.py  # exposes /health, /status, POST /fetch
```

## Output schema
CSV headers written by `app/storage/writer.py`:

```
timestamp_utc,source,asset,price_usd,http_status,latency_ms,attempt
```

## Data sources
Primary and fallback providers (no auth keys required for these specific endpoints at time of writing):
- CoinGecko Simple Price: `GET /api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd`
- CoinCap Assets: `GET /v2/assets?ids=bitcoin,ethereum`
- Binance Ticker Price: `GET /api/v3/ticker/price?symbol=BTCUSDT`
- Coinbase Exchange Rates: `GET /v2/exchange-rates?currency=USD`

> Note: providers may enforce rate limits. The app includes basic retry/backoff and fails over to the next source if the primary fails. Providers are subject to change over time.

## Testing
```bash
pytest -q
```

## Assumptions & notes
- All prices are treated as **USD** (Binance quotes USDT, assumed ~ USD for simplicity).
- Snapshot files are partitioned by date: `data/YYYY/MM/DD/prices-HHMM.csv`.
- This repo is a **starting point**; feel free to extend/modify for your process.
