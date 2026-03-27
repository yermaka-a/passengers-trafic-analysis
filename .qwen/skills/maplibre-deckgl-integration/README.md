# MapLibre + Deck.gl Integration Skill

## 📚 Skill Contents

This skill provides comprehensive guidance for integrating MapLibre GL JS with Deck.gl in Vue 3 applications.

### Files

1. **SKILL.md** - Main skill documentation with:
   - Core concepts and patterns
   - Common issues and solutions
   - Layer type references
   - Testing checklist

2. **examples/reactive-patterns.md** - Vue 3 reactivity patterns:
   - Watching Map objects
   - Immutable store updates
   - Deck.gl updateTriggers
   - Complete working example

3. **examples/layer-configurations.md** - Layer configuration examples:
   - PolygonLayer with fill/stroke
   - PathLayer with dash patterns
   - ScatterplotLayer for markers
   - Color and coordinate utilities

4. **troubleshooting.md** - Debugging guide:
   - Step-by-step diagnosis
   - Common pitfalls
   - Performance tips
   - Debugging checklist

## 🎯 Quick Start

When facing MapLibre + Deck.gl issues, check:

1. **Colors not updating?** → See `troubleshooting.md` → "Colors Don't Update"
2. **Dash not working?** → See `examples/layer-configurations.md` → "Polyline with Dash Pattern"
3. **Reactivity broken?** → See `examples/reactive-patterns.md` → "Pattern 1: Watch Map Objects"
4. **Layers not rendering?** → See `troubleshooting.md` → "Layers Not Rendering"

## 🔑 Key Concepts

### 1. Reactive Updates
```typescript
watch(
  () => Array.from(Objects.value.values()),
  () => deckOverlay._deck.redraw()
);
```

### 2. Immutable Store Updates
```typescript
const updatedObj = { ...obj, style: { ...obj.style, color: newColor }};
```

### 3. Deck.gl updateTriggers
```typescript
updateTriggers: {
  getColor: objects.map(o => ({ id: o.id, color: o.style.color }))
}
```

### 4. PathStyleExtension for Dash
```typescript
extensions: [new PathStyleExtension({ dash: true })]
```

## 📖 When to Use

Use this skill when working with:
- MapLibre GL JS + Deck.gl integration
- Dynamic style updates (colors, dash, opacity)
- Vue 3 + Pinia reactive map applications
- GeoJSON visualization on maps

## 🚀 Related Skills

- `vue-reactivity-system` - Vue 3 reactivity fundamentals
- `pinia-state-management` - Pinia store patterns
- `frontend-design` - UI/UX best practices
