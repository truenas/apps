# MetaTana

[MetaTana](https://metatana.com) is an AI-powered media manager. It scans your
media files, identifies content with AI and metadata providers, enriches
artwork, subtitles, trailers, and people data, and organizes your library —
drop a folder and let it work.

## Configuration

- **Media Storage** — Set this to **Host Path** and point it at the dataset that
  holds your library so MetaTana can scan and organize it.
- **App Data Storage** — Keep on a persistent dataset. It holds the SQLite
  database, runtime state, and thumbnails.
- **User / Group** — MetaTana runs as the configured `run_as` user/group and
  needs read/write access to your media to organize files. Make sure the chosen
  user/group can access the media dataset.
- **Provider keys** — All optional. Add metadata/AI/integration keys (for
  example `TMDB_API_KEY`, `ANTHROPIC_API_KEY`, `TRAKT_CLIENT_ID`) under
  *Additional Environment Variables*, or configure providers later in the UI.

## Signing in

Open the WebUI and link a hosted MetaTana account from inside the app (Link
Device). No bootstrap token or environment secret is required for normal sign-in.

## Notes

- The image is multi-architecture (`linux/amd64`, `linux/arm64`).
- MetaTana is metadata-only: it works with any media library and is
  downloader-agnostic.
