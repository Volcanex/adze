# Skeleton

Placeholder shapes shown while content loads.

## When to use which loading state

1. **Skeleton** — you know the shape of what's arriving. Best option.
2. **ProgressBar** — you know how far along you are.
3. **Spinner** — you know neither. Last resort.

## The one rule that matters

The skeleton must match the real content's dimensions. If the placeholder is
48px tall and the real row is 64px, the page jumps when data lands and it
feels worse than showing nothing. Match the real geometry or use a Spinner.

`SkeletonRows` is pre-matched to the content-admin list row — use it for list
views rather than composing your own.

## Usage

```jsx
// Content-admin list view
{loading ? <SkeletonRows count={4} /> : <ItemList items={items} />}

// A paragraph of unknown text
<Skeleton variant="text" lines={3} />

// An image slot — match the real aspect
<Skeleton variant="block" height="180px" />
```

## Rules

- `lines > 1` automatically shortens the last line. Don't override it — even
  ragged endings are what make it read as text rather than a barcode.
- Never animate a skeleton for longer than ~10s. Past that, the operation has
  failed; show an `EmptyState variant="error"` with a retry.
- Skeletons are `aria-hidden`; wrap the region in `role="status"` (SkeletonRows
  already does) so screen readers announce loading once rather than reading
  out empty boxes.
