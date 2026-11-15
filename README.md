# Rainbow Weather for Home Assistant

Unofficial cloud-polling integration for Rainbow Weather's minute-by-minute precipitation nowcast. No general-purpose weather entity is provided.

## Install using HACS

1. In HACS, open **Custom repositories**.
2. Add `https://github.com/quivalen/rainbow-weather-ha` with category **Integration**.
3. Download Rainbow Weather and restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration → Rainbow Weather**.
5. Supply your own Rainbow API key and coordinates. Coordinates default to your Home Assistant home location.

Alternatively, copy `custom_components/rainbow_weather` into your HA `config/custom_components` directory and restart.

This repository is not included in the default HACS catalog. Requires Home Assistant 2025.1 or newer.

## Entities

- Precipitation rate (mm/h) and type for the current forecast minute.
- Next precipitation start (unknown when already precipitating or none is predicted).
- Current precipitation end (unknown when dry, or the episode extends beyond the forecast).
- Next precipitation end (end of the next episode, or the current episode when already precipitating; unknown if none is predicted or the end is beyond the forecast).
- Forecast precipitation total (mm) and peak rate (mm/h) over the remaining forecast.
- Forecast summary with a `forecast` attribute containing UTC time, rate and type for every remaining minute.
- Forecast fetched diagnostic timestamp (retrieval time, **not** model issue time).
- Precipitation expected binary sensor: any precipitation in the next 30 minutes.
- Refresh forecast button, including recovery after failed requests.

Missing or expired current-minute coverage makes forecast sensors unavailable; it is never treated as dry. Forecast totals integrate rates over the remaining time, including partial minutes. Summary is the provider's whole-window intensity classification. No API data is logged. Minute forecast attributes are excluded from Recorder history to reduce storage.

## Refresh and quotas

One shared API request per location every **5 minutes**, about **8,928 requests per 31-day month**, plus setup and manual requests. Local minute-by-minute updates do not call the API. Check your account's actual allowance; quotas and pricing may change. Multiple locations multiply usage.

Trigger an immediate shared refresh from an automation:

```yaml
action: button.press
target:
  entity_id: button.rainbow_weather_refresh_forecast
```

Use the actual entity ID from your installation. Concurrent refresh requests are coalesced by Home Assistant's coordinator. Rate-limit manual automation triggers to avoid exhausting your allowance. The refresh button is the supported immediate-poll hook.

## Privacy and configuration

Credentials and coordinates are supplied only through Home Assistant's UI and stored in its config entry. Coordinates and key are sent to Rainbow to retrieve forecasts. Do not publish your HA configuration or `.storage` directory. No keys or fixed GPS coordinates ship in this repository. To change credentials/location, remove and re-add the integration.

Rainbow's edge currently requires browser-like request headers. These are included, but Cloudflare policies may change; a 403 is reported as a connection failure.

## Development

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q custom_components
```

Pure forecast calculations have offline unit tests. GitHub Actions runs tests, Hassfest, and HACS validation through `.github/workflows/validate.yml`. A running Home Assistant instance is still required for end-to-end verification.

Data by [Rainbow Weather](https://rainbow.ai/). API documentation: https://doc.rainbow.ai/api-ref/nowcast/ . This project is not affiliated with Rainbow Weather.
