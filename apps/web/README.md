# Web client

The web client is a React 19/Vite application with TypeScript, Manrope, and Noto Sans Bengali. It talks to the FastAPI server through the `/api` proxy configured in `vite.config.ts`.

```bash
pnpm install --frozen-lockfile
pnpm dev
pnpm build
```

The client never receives Gemini or Hugging Face credentials. User-visible behavior, responsive layout, citation inspection, and accessibility requirements are specified in [UIUX.md](../../docs/UIUX.md).
