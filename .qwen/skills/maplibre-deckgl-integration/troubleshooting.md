# Troubleshooting Guide

## Issue: Colors Don't Update on Map

### Symptoms
- Color picker works in UI
- Store shows updated color
- Map display doesn't change

### Diagnosis Steps

1. **Check if watch fires:**
   ```typescript
   watch(
     () => Array.from(Objects.value.values()),
     () => console.log('Watch fired!')
   );
   ```

2. **Check accessor logging:**
   ```typescript
   getColor: (obj) => {
     console.log('getColor called:', obj.style.color);
     return obj.style.color;
   }
   ```

3. **Check updateTriggers:**
   ```typescript
   console.log('updateTriggers:', 
     objects.map(o => ({ id: o.id, color: o.style.color }))
   );
   ```

### Common Causes

1. **Missing updateTriggers:**
   ```typescript
   // ❌ WRONG
   new PathLayer({
     getColor: (obj) => obj.style.color,
   });
   
   // ✅ CORRECT
   new PathLayer({
     getColor: (obj) => obj.style.color,
     updateTriggers: {
       getColor: objects.map(o => ({ id: o.id, color: o.style.color })),
     },
   });
   ```

2. **Store mutation instead of replacement:**
   ```typescript
   // ❌ WRONG
   obj.style.color = newColor;
   
   // ✅ CORRECT
   const updatedObj = {
     ...obj,
     style: { ...obj.style, color: newColor },
   };
   ```

3. **Watch on Map instead of Array:**
   ```typescript
   // ❌ WRONG
   watch(() => Objects.value, updateLayers);
   
   // ✅ CORRECT
   watch(() => Array.from(Objects.value.values()), updateLayers);
   ```

---

## Issue: Dash Pattern Not Working

### Symptoms
- Slider changes value in UI
- `strokeDasharray` updates in store
- Line remains solid on map

### Diagnosis

1. **Check if PathStyleExtension is used:**
   ```typescript
   // ❌ WRONG - No extension
   new PathLayer({
     getDashArray: (obj) => obj.style.strokeDasharray,
   });
   
   // ✅ CORRECT - With extension
   const extension = new PathStyleExtension({ dash: true });
   new PathLayer({
     getDashArray: (obj) => obj.style.strokeDasharray,
     extensions: [extension],
   });
   ```

2. **Check getDashArray return value:**
   ```typescript
   // ❌ WRONG - Returns undefined for solid lines
   getDashArray: (obj) => obj.style.strokeDasharray,
   
   // ✅ CORRECT - Returns [0, 0] for solid
   getDashArray: (obj) => {
     const dash = obj.style.strokeDasharray;
     return dash && dash[0] > 0 ? dash : [0, 0];
   },
   ```

3. **Check dash array format:**
   ```typescript
   // Must be [dashLength, gapLength]
   // Example: [10, 5] = 10px dash, 5px gap
   
   // From slider value:
   const dashValue = value[0] === 0 
     ? [0, 0] 
     : [value[0], value[0] / 2]; // Gap is half of dash
   ```

---

## Issue: Fill Opacity Not Working

### Symptoms
- Opacity slider changes
- Store updates
- No visual change

### Solution

```typescript
// ❌ WRONG - Uses color alpha directly
getFillColor: (obj) => obj.style.color,

// ✅ CORRECT - Applies fillOpacity to alpha channel
getFillColor: (obj) => {
  const color = obj.style.color;
  return [
    color[0],
    color[1],
    color[2],
    Math.round(color[3] * (obj.style.fillOpacity ?? 0.5))
  ];
}
```

**Don't forget updateTriggers:**
```typescript
updateTriggers: {
  getFillColor: polygons.map(o => ({
    id: o.id,
    color: o.style.color,
    fillOpacity: o.style.fillOpacity,
  })),
}
```

---

## Issue: Cursors Not Displaying

### Symptoms
- Custom cursor SVGs exist
- CSS applied
- Default cursor still shows

### Solution

```css
/* Apply to map container */
:deep(#map) {
  cursor: url("./plus-cursor.svg") 16 16, auto !important;
}

/* Apply to MapLibre canvas */
:deep(.maplibregl-canvas) {
  cursor: inherit !important;
}

/* Grab cursor when dragging */
:deep(.maplibregl-canvas:active) {
  cursor: url("./grab-cursor.svg") 16 16, auto !important;
}
```

**Key points:**
- Use `!important` to override MapLibre defaults
- Set hot spot coordinates (16 16 for center)
- Use `cursor: inherit` on canvas

---

## Issue: Memory Leak on Unmount

### Symptoms
- App slows down over time
- Multiple map instances in memory
- Console shows duplicate logs

### Solution

```typescript
onUnmounted(() => {
  console.log("[Map] Cleaning up...");
  
  // 1. Finalize Deck.gl overlay
  if (deckOverlay) {
    deckOverlay.finalize();
    deckOverlay = null;
  }
  
  // 2. Remove MapLibre map
  if (mapInstance.value) {
    mapInstance.value.remove();
    mapInstance.value = null;
  }
  
  console.log("[Map] Cleanup complete");
});
```

---

## Issue: Layers Not Rendering

### Symptoms
- Map shows
- No Deck.gl layers visible
- No errors in console

### Checklist

1. **Check interleaved setting:**
   ```typescript
   // ❌ WRONG - May not render
   new MapboxOverlay({
     layers: layers,
   });
   
   // ✅ CORRECT
   new MapboxOverlay({
     layers: layers,
     interleaved: true,
   });
   ```

2. **Check z-index:**
   ```css
   :deep(.deckgl-overlay) {
     position: absolute !important;
     z-index: 10 !important;
   }
   ```

3. **Check coordinate format:**
   ```typescript
   // Deck.gl uses [lng, lat] NOT [lat, lng]!
   const coords = [[30, 50], [31, 51]]; // ✅ Correct
   // const coords = [[50, 30], [51, 31]]; // ❌ Wrong
   ```

4. **Check color format:**
   ```typescript
   // Deck.gl uses RGBA array [0-255]
   const color = [255, 0, 0, 255]; // ✅ Red
   // const color = "#ff0000"; // ❌ String not supported
   ```

---

## Debugging Checklist

When something doesn't work, check in this order:

1. **Store Level:**
   - [ ] Is value updated in store?
   - [ ] Is object created immutably (new reference)?
   - [ ] Does `getObjectById(id)` return updated value?

2. **Reactivity Level:**
   - [ ] Does watch fire when value changes?
   - [ ] Is Map converted to Array in watch?
   - [ ] Is `{ deep: true }` set?

3. **Deck.gl Level:**
   - [ ] Are updateTriggers defined?
   - [ ] Do trigger values actually change?
   - [ ] Are accessor functions being called?
   - [ ] Is extension added (for dash)?

4. **Rendering Level:**
   - [ ] Is `deckOverlay._deck.redraw()` called?
   - [ ] Are colors in RGBA format?
   - [ ] Are coordinates in [lng, lat] format?
   - [ ] Is layer visible in DevTools?

---

## Performance Tips

1. **Limit update frequency:**
   ```typescript
   // Debounce rapid updates
   const debouncedUpdate = debounce(() => {
     deckOverlay._deck.setProps({ layers: createDeckLayers() });
   }, 100);
   ```

2. **Use pickable: false for non-interactive layers:**
   ```typescript
   new PolygonLayer({
     pickable: false, // Improves performance
   });
   ```

3. **Separate fill and stroke layers:**
   ```typescript
   // Better performance than single layer with both
   new PolygonLayer({ id: "fill", ... });
   new PathLayer({ id: "stroke", ... });
   ```

4. **Limit object count:**
   - 50+ objects: May notice slowdown
   - 100+ objects: Consider clustering
   - 500+ objects: Use aggregation layers
