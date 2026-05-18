# GitHub Copilot Instructions — React Project

## Project Overview

This is a React project. All code suggestions, UI designs, and debugging assistance must follow the guidelines below to ensure consistency, quality, and maintainability.

---

## 🎨 UI Design Standards

### Component Structure
- Use **functional components** with hooks only — no class components.
- Every component must have a **single, clearly defined responsibility**.
- Extract repeated JSX into reusable components. If JSX repeats more than twice, it must be a component.
- Group related components in feature folders: `src/features/<feature-name>/`.

### Styling Rules
- Use **CSS Modules** (`Component.module.css`) or **Tailwind CSS** utility classes — never inline styles except for truly dynamic values.
- Define all design tokens (colors, spacing, font sizes, radii, shadows) as **CSS custom properties** in `:root` inside `src/styles/globals.css`.
- Example token structure:
  ```css
  :root {
    --color-primary: #2563eb;
    --color-surface: #f8fafc;
    --color-text: #0f172a;
    --radius-md: 8px;
    --shadow-card: 0 4px 16px rgba(0, 0, 0, 0.08);
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 32px;
  }
  ```
- **Never hardcode hex values or pixel values** outside of the token file.

### Typography
- Use a **distinctive font pairing** — one display/heading font and one readable body font.
- Define fonts in globals.css and apply via token variables.
- Maintain a clear type scale: `text-xs`, `text-sm`, `text-base`, `text-lg`, `text-xl`, `text-2xl`, `text-3xl`.
- Line height must be at least `1.5` for body text.

### Layout & Spacing
- Use **CSS Grid** for page-level layouts and **Flexbox** for component-level alignment.
- All spacing must use token variables — never magic numbers.
- Maintain a minimum tap target size of **44×44px** for all interactive elements.
- Respect a consistent **8px spacing grid**.

### Motion & Interaction
- Add subtle transitions (`transition: all 0.2s ease`) on hover/focus states for buttons and interactive elements.
- Use `@media (prefers-reduced-motion: reduce)` to disable animations for accessibility.
- Loading states must always show a **skeleton or spinner** — never a blank area.

### Accessibility (A11y)
- Every image must have a descriptive `alt` attribute.
- All interactive elements must be keyboard-navigable and have visible `:focus-visible` styles.
- Use semantic HTML: `<button>` for actions, `<a>` for navigation, `<main>`, `<nav>`, `<section>`, `<header>`, `<footer>`.
- Color contrast must meet **WCAG AA** (4.5:1 for text, 3:1 for UI components).
- Use `aria-label` or `aria-describedby` for icon-only buttons and complex widgets.

---

## 🐛 Debugging Guidelines

### Error Identification
When reviewing or generating code, Copilot must:

1. **Identify and flag** the following error categories:
   - **Runtime errors**: undefined variables, null/undefined access, type mismatches.
   - **React-specific errors**: missing `key` props in lists, stale closures in hooks, direct state mutations, calling hooks conditionally.
   - **Async errors**: unhandled promise rejections, missing `await`, race conditions.
   - **Performance issues**: unnecessary re-renders, missing `useMemo`/`useCallback`, large bundle imports.
   - **Accessibility errors**: missing alt text, improper ARIA roles, non-semantic HTML used as buttons.

2. **Annotate errors inline** using comments before the problematic line:
   ```js
   // ❌ BUG: Direct state mutation — use setState or spread operator instead
   state.items.push(newItem);
   ```

3. **Always provide a corrected version** immediately after the flagged code.

### Fix Strategy
- Fix **root causes**, not symptoms. If a value is unexpectedly `undefined`, trace where it originates — don't just add a `?.` guard everywhere.
- When fixing a bug, explain **why** it was a bug in a short comment.
- Prefer **explicit error boundaries** (`<ErrorBoundary>`) around feature sections.
- Use `try/catch` with meaningful error messages for all async operations.

### React-Specific Rules
- **State**: Never mutate state directly. Always use the setter from `useState` or `useReducer`.
- **Effects**: Every `useEffect` must have an explicit dependency array. Side effects that run once go in `[]`. Cleanup functions are required when subscribing to events or timers.
- **Keys**: List `.map()` renders must always use a stable, unique `key` — never array index unless the list is static and never reordered.
- **Props**: Destructure props at the top of the component. Use PropTypes or TypeScript interfaces for all props.
- **Refs**: Use `useRef` only for DOM access or storing mutable values that don't trigger re-renders.

### Code Quality
- No `console.log` in committed code — use a logger utility or remove before committing.
- No commented-out code blocks — delete dead code or use version control.
- Functions must do one thing. If a function exceeds 30 lines, consider splitting it.
- All async functions must handle the error case (`.catch()` or `try/catch`).

---


## ✅ Code Review Checklist (Copilot must validate before suggesting)

Before finalising any suggestion, verify:

- [ ] Component is functional and uses hooks correctly
- [ ] No direct state mutations
- [ ] All `useEffect` hooks have proper dependency arrays and cleanup
- [ ] All list renders include stable `key` props
- [ ] All images have `alt` attributes
- [ ] All buttons and interactive elements are keyboard accessible
- [ ] CSS uses token variables — no hardcoded values
- [ ] No `console.log` statements
- [ ] Async functions have error handling
- [ ] Component does one thing and is under ~100 lines (excluding styles)

---

## 🚫 Patterns to Avoid

| ❌ Avoid | ✅ Prefer |
|---|---|
| `class` components | Functional components + hooks |
| Inline styles | CSS Modules / Tailwind |
| Hardcoded colors/spacing | CSS token variables |
| `array.push()` on state | `setState([...arr, newItem])` |
| Index as list `key` | Stable unique ID as `key` |
| `useEffect` without deps | Explicit dependency array |
| Unhandled promises | `try/catch` or `.catch()` |
| `any` type in TypeScript | Explicit types/interfaces |
| Prop drilling > 2 levels | Context, Zustand, or Redux |
| `document.getElementById` | `useRef` |

---

## 💬 Copilot Response Format

When suggesting code changes or fixes, always use this structure:

```
### 🔍 Issue Found
[Brief description of what the problem is and why it's a problem]

### ✅ Fix
[Corrected code block]

### 📝 Explanation
[1–3 sentences explaining the fix]
```

When generating new UI components, always include:
1. The JSX component
2. The CSS Module (or Tailwind classes inline)
3. A brief usage example