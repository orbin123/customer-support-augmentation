# Support dashboard

React and TypeScript operator interface for Harbor & Pine support.

See the [project README](../README.md) for architecture, credentials, database setup, and the recorded demo.

```bash
npm ci
npm run dev
npm run build
npm run lint
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`. Sign in using the backend’s configured dashboard credentials. The interface provides Events, Tickets, and an editable Knowledge base.
