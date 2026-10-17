# NEURO//LAB

A mobile-first personal development prototype, designed to deploy as a Progressive Web App (PWA).

## Features
- Three interactive starter missions: self-awareness, emotional regulation, and habit design.
- Personal objectives with completion tracking.
- Field notes.
- Browser-local persistence.
- PWA manifest, app icon, service worker and GitHub Pages deployment workflow.

## Deploy
1. In GitHub, open **Settings → Pages**.
2. Set the source to **GitHub Actions**.
3. The workflow in `.github/workflows/pages.yml` deploys the site when changes are pushed to `main`.
4. Once the workflow completes, open the Pages URL on your iPhone in Safari, tap Share, then **Add to Home Screen**.

## Important
This is an early prototype, not a medical or diagnostic tool. Data is stored in the browser on the device and is not synced between devices. Clearing browser/site data may erase it. The service worker provides basic app-shell caching after the first successful load; test offline behaviour on the deployed site.

## Planned next
1. Expand the learning path into structured skill trees and scenario simulations.
2. Add weekly reviews and more meaningful progress insights.
3. Improve accessibility and testing.
4. Consider export/backup before any cloud account system.
