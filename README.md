# NEURO//LAB

A mobile-first personal development and curiosity lab, built as a Progressive Web App (PWA). The experience is organised around two connected spaces: **Inner Cosmos** for reflection and human meaning, and **Outer Cosmos** for astronomy and live space-weather observations.

## Current experiences

- **Inner Cosmos**
  - Birth chart reflection, with birth details entered by the user.
  - Cycle & Wellbeing tracking, with clear caveats about estimates and non-medical use.
  - Wisdom Library for exploring philosophical and spiritual traditions.
  - Mind Training with guided reflection, skill development, practice missions, saved reflections and progress insights.
  - Tarot readings with randomised card draws, multiple spreads, interpretations and a locally saved reading archive.
- **Outer Cosmos**
  - NASA Solar Dynamics Observatory imagery across several solar observation channels.
  - Space-weather observations and aurora-related information from public scientific data sources when available.
  - Clear unavailable-data messaging rather than invented live readings.
- **Personal data**
  - Browser-local progress and settings.
  - JSON backup and restore controls.
  - Installable PWA shell with a service worker and mobile-friendly interface.

## Try it on an iPhone

1. Open the deployed GitHub Pages site (the URL is shown under **Settings → Pages** in this repository).
2. Open it in Safari.
3. Tap **Share → Add to Home Screen** to install the app-like shortcut.
4. Explore both worlds and test the back navigation, Mind Training, Tarot draw/save, and backup/restore.

## Development and deployment

- The app is currently a lightweight, mostly single-page web app. The main interface is in `index.html`.
- `service-worker.js` manages the cached app shell.
- `.github/workflows/pages.yml` deploys `main` to GitHub Pages.
- `.github/workflows/neurolab-smoke-test.yml` runs regression checks for key interface elements, navigation, backup controls, Tarot structure, PWA assets and inline JavaScript syntax.
- Run the smoke tests locally with Python and Node.js installed:

  ```bash
  python -m unittest discover -s tests -v
  ```

## Privacy and limitations

- Personal data is stored in the browser on the current device. It is **not** synchronised to an account or between devices.
- Clearing browser/site data can erase saved progress. Export a backup before clearing data or changing devices.
- Live NASA/space-weather feeds require an internet connection and may be temporarily unavailable.
- Astrology, tarot, wellbeing and reflection content is for exploration and self-reflection. It is not medical, mental-health, diagnostic or guaranteed predictive advice.

## Product direction

The next priority is to make the experience feel coherent and genuinely useful on a phone: verify real-device navigation, strengthen functional tests, improve onboarding and accessibility, and sharpen the core reason to return. New features should build on a stable baseline rather than risk another broad redesign.
