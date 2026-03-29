# AGENTS.md

**Generated:** 2026-03-29
**Area:** Frontend UI Components

## OVERVIEW

React components for DeerFlow chat interface. Components are split into purpose-specific directories. UI primitives and AI elements are auto-generated from registries.

## STRUCTURE

```
components/
├── ui/              # Shadcn UI primitives (AUTO-GENERATED - don't edit)
├── ai-elements/     # Vercel AI SDK elements (AUTO-GENERATED - don't edit)
├── workspace/       # Chat page components
│   ├── messages/    # Message display, artifacts, suggestions
│   ├── settings/    # Thread settings, model selection
│   └── composer/    # Input composer
└── landing/         # Landing page sections
```

## AUTO-GENERATED (DON'T EDIT)

- `components/ui/` - Shadcn UI registry
- `components/ai-elements/` - Vercel AI SDK registry

These are generated from upstream libraries. Edit source registries, not these directories.

## KEY COMPONENTS

**Workspace Components** (`components/workspace/`):
- `messages/` - MessageList, MessageItem, ArtifactViewer, SuggestionList
- `settings/` - SettingsPanel, ModelSelector, ThreadSettings
- `composer/` - Composer (busy-state wiring owned by `app/workspace/chats/[thread_id]/page.tsx`)

## CONVENTIONS

**Path Alias**: `@/*` maps to `src/*`

**State Management**:
- Server state: TanStack Query (`@tanstack/react-query`)
- Thread state: `src/core/threads/hooks.ts` (`useThreadStream`, `useSubmitThread`, `useThreads`)
- Local state: `localStorage` for user settings

**Thread Lifecycle Ownership**:
- `src/app/workspace/chats/[thread_id]/page.tsx` owns composer busy-state wiring
- `src/core/threads/hooks.ts` owns pre-submit upload state and thread submission
- `src/hooks/usePoseStream.ts` is passive store selector

**Imports**: Enforced ordering (builtin → external → internal → parent → sibling), alphabetized, newlines between groups. Use inline type imports: `import { type Foo }`.

**Class Names**: Use `cn()` from `@/lib/utils` for conditional Tailwind classes.

## STYLE

- **Tailwind CSS 4** with `@import` syntax and CSS variables for theming
- **Server Components by default**, `"use client"` only for interactive components

## DEPENDENCIES

- `@langchain/langgraph-sdk@1.5.3` - Agent orchestration
- `@langchain/core@1.1.15` - AI building blocks
- `@tanstack/react-query@5.90.17` - Server state
- Shadcn UI, MagicUI, React Bits, Vercel AI SDK

## NOTES

- `src/env.js` validates environment with `@t3-oss/env-nextjs` + Zod
- LangGraph client singleton via `getAPIClient()` in `src/core/api/`
- WebSocket lifecycle managed in `App.tsx`
