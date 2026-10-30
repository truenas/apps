# Cellarion

[Cellarion](https://cellarion.app) is a self-hosted wine cellar manager. Track your bottles, lay them out in racks, scan labels and get drink-window advice from a shared wine registry.

The app runs five containers: the web frontend (nginx), the backend API (Node.js), MongoDB, Meilisearch and a small label-photo background-removal service. The first account you register becomes an administrator by running `node src/scripts/make-admin.js <email>` in a shell on the backend container.
