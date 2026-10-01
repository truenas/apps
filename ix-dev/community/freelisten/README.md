# FreeListen

[FreeListen](https://github.com/Alextheguy1/FreeListen) searches the
[MusicBrainz](https://musicbrainz.org) database, or a public Spotify playlist,
and saves tagged audio files to a directory you choose.

Downloads carry title, artist, album, year, genre and track number, with cover
art embedded where the format supports it, and are filed as
`Artist/Album/NN - Title`. Music servers such as Navidrome or Jellyfin pick them
up with no further configuration. Point FreeListen's music storage at the same
directory your music server reads and new downloads appear there.

Output format is MP3, FLAC, Opus or AAC, with configurable encode quality for
the lossy ones. Downloads run through a queue you can watch while it works.

## Configuration

Spotify credentials, a ListenBrainz token, audio format and quality are set
from the app's own Settings page once it is running, and stored in the config
storage you configure here. None of them are required to search and download.

## Storage

- **Music storage**: where downloaded audio is saved.
- **Config storage**: the app's `settings.json`. It is small, but keep it on
  persistent storage so your settings survive updates.

## Note

FreeListen obtains audio from YouTube. That sits in a grey area under YouTube's
Terms of Service, and this app is intended for personal use.
