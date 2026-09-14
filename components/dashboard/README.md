# ANSIMON Social-Worker Dashboard

A build-free static dashboard for heatwave prevention and older-adult care operations.

## Screens

| File | Screen | Backend integration |
| --- | --- | --- |
| `index.html` | Operations dashboard | Risk forecasts, older-adult list, and care-run execution |
| `elderly.html` | Older-adult records | Create, read, update, and delete through live APIs |
| `elderly-detail.html` | Profile and contact detail | Profile updates, care runs, and call-observation corrections |

`assets/theme.css` provides the shared visual system. `assets/api.js` provides shared fetch, API-base, and toast helpers.

## Run

Use a local static server; opening the files with `file://` may block API requests because of browser security rules.

```bash
python -m http.server 5500
```

Open `http://localhost:5500/index.html`. The default backend is `http://localhost:8080`. Override it with either a query parameter or a deployed global value:

```text
http://localhost:5500/index.html?api=http://localhost:8099
```

```javascript
window.ANSIMON_API_BASE = "https://api.example.com";
```

## API Surface

| Feature | Endpoint |
| --- | --- |
| List older adults | `GET /api/v1/elderly?page&size&sort&regionCode&consentStatus` |
| Create older adult | `POST /api/v1/elderly` |
| Read older adult | `GET /api/v1/elderly/{id}` |
| Update older adult | `PATCH /api/v1/elderly/{id}` |
| Delete older adult | `DELETE /api/v1/elderly/{id}` |
| Forecast risk | `POST /internal/v1/risk/forecast` |
| Run preventive care flow | `POST /internal/v1/guidance/care-runs/{elderlyId}` |
| Correct call observation | `PATCH /api/v1/contact/observations/{id}` |
| Delete call observation | `DELETE /api/v1/contact/observations/{id}` |

## Care-Run Behavior

A care run synchronously generates a plan, places the preventive call, and stores the summary. A real call can take tens of seconds. The UI locks the active row, shows elapsed time, and gives the request up to 130 seconds. Batch calling is deliberately sequential, and a second click stops the remaining queue. The UI blocks calls for people who have not consented.

The interface surfaces structured failures such as `CONSENT_REQUIRED`, `GUIDANCE_GENERATION_BLOCKED`, `RESOURCE_NOT_FOUND`, and upstream `502`/`504` failures.

## Prototype-Backed Areas

Some panels still use mock data because the original backend did not expose matching dashboard, weather, shelter, or call-history APIs. Manually edited action notes are stored in browser `localStorage` unless the backend supplies a saved plan. The banner at the top of the dashboard identifies live and mock-backed features.

For original project notes, see [README.ko.md](README.ko.md).
