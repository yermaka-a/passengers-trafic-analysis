# MapLibre + Deck.gl Integration Skill

## Overview

This skill provides comprehensive guidance for integrating MapLibre GL JS with Deck.gl for geospatial data visualization in Vue 3 applications. It covers common pitfalls, reactive patterns, and best practices discovered through real-world implementation.

## When to Use

Use this skill when:
- Integrating Deck.gl layers with MapLibre GL JS
- Experiencing issues with layer rendering or reactivity
- Need to update layer styles dynamically (colors, dash patterns, opacity)
- Working with GeoJSON data visualization on maps
- Building interactive map applications with Vue 3 + Pinia

## Core Concepts

### 1. MapboxOverlay Integration

```typescript
import { MapboxOverlay } from "@deck.gl/mapbox";
import maplibregl from "maplibre-gl";

// Create MapLibre map
const map = new maplibregl.Map({
  container: "map",
  style: { /* style config */ },
});

// Create Deck.gl overlay with interleaved: true
const deckOverlay = new MapboxOverlay({
  layers: createDeckLayers(),
  interleaved: true, // Critical for proper MapLibre integration
});

// Add as control
map.addControl(deckOverlay);
```

**Key Points:**
- `interleaved: true` is REQUIRED for Deck.gl to render properly with MapLibre
- Add overlay as a control, not as a separate layer
- Deck.gl canvas will be automatically positioned over MapLibre

### 2. Reactive Layer Updates with Vue 3

**Problem:** Vue's reactivity doesn't work with Map/Set objects by default.

**Solution:** Convert Map to Array in watch:

```typescript
// ❌ WRONG - Won't detect mutations inside Map
watch(() => Objects.value, () => {
  updateLayers();
});

// ✅ CORRECT - Convert to Array for reactivity
watch(
  () => Array.from(Objects.value?.values() ?? []),
  (newObjects) => {
    if (deckOverlay && deckOverlay._deck) {
      deckOverlay._deck.setProps({
        layers: createDeckLayers(),
        _animate: true,
      });
      setTimeout(() => deckOverlay._deck.redraw(), 50);
    }
  },
  { deep: true }
);
```

### 3. Deck.gl Style Updates with updateTriggers

**Problem:** Deck.gl caches accessor function results (`getColor`, `getDashArray`, etc.). They only run once when layer is created.

**Solution:** Use `updateTriggers` to tell Deck.gl when to re-run accessors:

```typescript
new PathLayer({
  id: "polygon-stroke",
  data: lineObjects,
  getColor: (obj) => obj.style.color,
  getWidth: (obj) => obj.style.strokeWidth,
  getDashArray: (obj) => obj.style.strokeDasharray || [0, 0],
  
  // Critical: Tell Deck.gl when to re-run accessors
  updateTriggers: {
    getColor: lineObjects.map(o => ({ 
      id: o.id, 
      color: o.style.color 
    })),
    getWidth: lineObjects.map(o => ({ 
      id: o.id, 
      strokeWidth: o.style.strokeWidth 
    })),
    getDashArray: lineObjects.map(o => ({ 
      id: o.id, 
      strokeDasharray: o.style.strokeDasharray 
    })),
  },
})
```

**How it works:**
1. `updateTriggers` creates a dependency map
2. When trigger values change, Deck.gl re-runs the accessor
3. Layer updates with new styles

### 4. Immutable Object Updates in Pinia Store

**Problem:** Direct mutation doesn't trigger Vue reactivity:

```typescript
// ❌ WRONG - Mutates existing object
obj.style.color = newColor;
this.Objects.set(id, obj);

// ✅ CORRECT - Create new object
const updatedObj = {
  ...obj,
  style: { ...obj.style, color: newColor },
};
this.Objects.set(id, updatedObj);
```

**Store Pattern:**

```typescript
updateObjectStyle(id: string, style: Partial<DeckGLStyle>) {
  const obj = this.Objects.get(id);
  if (obj) {
    // Create NEW object for Vue reactivity
    const updatedObj: DeckGLObject = {
      ...obj,
      style: { ...obj.style, ...style },
    };
    this.Objects.set(id, updatedObj);
  }
}
```

### 5. PathStyleExtension for Dash Patterns

**Required for dashed lines:**

```typescript
import { PathStyleExtension } from "@deck.gl/extensions";

const pathStyleExtension = new PathStyleExtension({
  dash: true,      // Enable dash support
  highPrecision: false,
});

new PathLayer({
  // ... layer config
  getDashArray: (obj) => obj.style.strokeDasharray || [0, 0],
  extensions: [pathStyleExtension], // Don't forget this!
})
```

**Without extension, `getDashArray` is ignored!**

## Common Issues & Solutions

### Issue 1: Colors Don't Update on Map

**Symptoms:** Color picker works in UI, but map doesn't update.

**Cause:** Missing `updateTriggers` for `getColor`.

**Fix:**
```typescript
updateTriggers: {
  getColor: objects.map(o => ({ id: o.id, color: o.style.color })),
}
```

### Issue 2: Dash Pattern Not Working

**Symptoms:** `strokeDasharray` changes in store, but line remains solid.

**Causes:**
1. Missing `PathStyleExtension`
2. `getDashArray` returns `undefined` instead of `[0, 0]`

**Fix:**
```typescript
// 1. Add extension
const extension = new PathStyleExtension({ dash: true });
extensions: [extension]

// 2. Return [0, 0] for solid lines
getDashArray: (obj) => {
  const dash = obj.style.strokeDasharray;
  return dash && dash[0] > 0 ? dash : [0, 0];
}
```

### Issue 3: Watch Not Triggering on Map Changes

**Symptoms:** Store updates but `watch` doesn't fire.

**Cause:** Watching Map object directly instead of converting to Array.

**Fix:**
```typescript
watch(
  () => Array.from(Objects.value.values()),
  () => { /* now works */ }
)
```

### Issue 4: Cursors Not Applying to Canvas

**Symptoms:** Custom cursors work in CSS but not on map canvas.

**Solution:** Apply via CSS with `!important`:

```css
:deep(.maplibregl-map) {
  cursor: url("./plus-cursor.svg") 16 16, auto !important;
}

:deep(.maplibregl-canvas:active) {
  cursor: url("./grab-cursor.svg") 16 16, auto !important;
}
```

## Layer Types Reference

### PolygonLayer (Fill)

```typescript
new PolygonLayer({
  id: "polygon-fill",
  data: polygons,
  getPolygon: (obj) => obj.coordinates,
  getFillColor: (obj) => {
    const color = obj.style.color;
    return [
      color[0],
      color[1],
      color[2],
      Math.round(color[3] * (obj.style.fillOpacity ?? 0.5))
    ];
  },
  getLineColor: [0, 0, 0, 0], // No outline
  pickable: false, // Let click through to stroke layer
  stroked: false,
  filled: true,
  updateTriggers: {
    getFillColor: polygons.map(o => ({ 
      id: o.id, 
      color: o.style.color,
      fillOpacity: o.style.fillOpacity 
    })),
  },
})
```

### PathLayer (Stroke)

```typescript
new PathLayer({
  id: "polygon-stroke",
  data: lines,
  getPath: (obj) => obj.coordinates,
  getColor: (obj) => obj.style.color,
  getWidth: (obj) => obj.style.strokeWidth ?? 2,
  getDashArray: (obj) => {
    const dash = obj.style.strokeDasharray;
    return dash && dash[0] > 0 ? dash : [0, 0];
  },
  pickable: true,
  autoHighlight: true,
  extensions: [new PathStyleExtension({ dash: true })],
  updateTriggers: {
    getColor: lines.map(o => ({ id: o.id, color: o.style.color })),
    getWidth: lines.map(o => ({ id: o.id, strokeWidth: o.style.strokeWidth })),
    getDashArray: lines.map(o => ({ id: o.id, strokeDasharray: o.style.strokeDasharray })),
  },
})
```

### ScatterplotLayer (Circle Markers)

```typescript
new ScatterplotLayer({
  id: "circle-marker",
  data: points,
  getPosition: (obj) => obj.coordinates[0] ?? [0, 0],
  getColor: (obj) => obj.style.color,
  getRadius: (obj) => obj.style.radius ?? 10,
  radiusMinPixels: 5,
  radiusMaxPixels: 20,
  pickable: true,
  updateTriggers: {
    getColor: points.map(o => ({ id: o.id, color: o.style.color })),
    getRadius: points.map(o => ({ id: o.id, radius: o.style.radius })),
  },
})
```

## File Structure

```
app/frontend/src/
├── components/
│   └── Map/
│       └── Map.vue              # Main map component
├── store/
│   └── useMapObjectStore.ts     # Pinia store with reactive patterns
├── config/
│   ├── DeckGLMapConfig.ts       # Default styles
│   └── MaplibreMapConfig.ts     # Map configuration
└── utils/
    ├── coords.ts                # Coordinate conversion
    └── color.ts                 # Color conversion (hex ↔ RGBA)
```

## Testing Checklist

- [ ] Color changes reflect on map immediately
- [ ] Dash pattern updates when slider moves
- [ ] Fill opacity changes apply correctly
- [ ] Stroke width changes are visible
- [ ] Watch triggers fire on store updates
- [ ] No memory leaks on component unmount
- [ ] Cursors display correctly
- [ ] Map zoom/pan works smoothly with 50+ objects

## Related Skills

- `vue-reactivity-system` - Vue 3 reactivity patterns
- `pinia-state-management` - Pinia store best practices
- `frontend-design` - UI/UX for map applications

## Resources

- [Deck.gl Documentation](https://deck.gl/docs)
- [MapLibre GL JS](https://maplibre.org/maplibre-gl-js-docs/)
- [Deck.gl + Mapbox Integration](https://deck.gl/docs/api-reference/mapbox/overlay)
- [PathStyleExtension](https://deck.gl/docs/api-reference/extensions/path-style-extension)
