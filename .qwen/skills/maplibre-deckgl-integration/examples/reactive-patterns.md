# Reactive Patterns for Deck.gl + Vue 3

## Problem

Vue 3's reactivity system doesn't automatically detect changes in Map/Set objects. Deck.gl caches accessor function results. This creates two layers of reactivity challenges.

## Pattern 1: Watch Map Objects

```typescript
// ❌ WRONG - Won't work
watch(() => store.Objects.value, () => {
  updateLayers();
});

// ✅ CORRECT - Convert to Array
watch(
  () => Array.from(store.Objects.value?.values() ?? []),
  (newObjects) => {
    console.log('Objects changed:', newObjects.length);
    updateLayers();
  },
  { deep: true }
);
```

## Pattern 2: Immutable Store Updates

```typescript
// ❌ WRONG - Direct mutation
updateObjectStyle(id: string, style: Partial<DeckGLStyle>) {
  const obj = this.Objects.get(id);
  if (obj) {
    obj.style.color = style.color; // Mutation!
    this.Objects.set(id, obj); // Same reference
  }
}

// ✅ CORRECT - Create new object
updateObjectStyle(id: string, style: Partial<DeckGLStyle>) {
  const obj = this.Objects.get(id);
  if (obj) {
    const updatedObj: DeckGLObject = {
      ...obj,
      style: { ...obj.style, ...style },
    };
    this.Objects.set(id, updatedObj); // New reference
  }
}
```

## Pattern 3: Deck.gl updateTriggers

```typescript
// ❌ WRONG - Accessors cached, never re-run
new PathLayer({
  data: objects,
  getColor: (obj) => obj.style.color,
  // Deck.gl runs this ONCE and caches result
});

// ✅ CORRECT - Tell Deck.gl when to re-run
new PathLayer({
  data: objects,
  getColor: (obj) => obj.style.color,
  updateTriggers: {
    getColor: objects.map(o => ({ 
      id: o.id, 
      color: o.style.color // Change triggers re-run
    })),
  },
});
```

## Pattern 4: Forced Deck.gl Redraw

```typescript
watch(
  () => Array.from(Objects.value.values()),
  () => {
    if (deckOverlay && deckOverlay._deck) {
      // Force Deck.gl to re-evaluate accessors
      deckOverlay._deck.setProps({
        layers: createDeckLayers(),
        _animate: true,
      });
      
      // Force immediate redraw
      setTimeout(() => {
        deckOverlay._deck.redraw();
      }, 50);
    }
  }
);
```

## Complete Example

```typescript
// store/useMapObjectStore.ts
export const useMapObjectStore = defineStore("mapobjects", {
  state: () => ({
    Objects: new Map<string, DeckGLObject>(),
  }),
  
  actions: {
    updateObjectStyle(id: string, style: Partial<DeckGLStyle>) {
      const obj = this.Objects.get(id);
      if (!obj) return;
      
      // Create NEW object for Vue reactivity
      const updatedObj = {
        ...obj,
        style: { ...obj.style, ...style },
      };
      
      this.Objects.set(id, updatedObj);
    },
  },
});

// components/Map/Map.vue
const { Objects } = storeToRefs(mapObjectStore);

const createDeckLayers = () => {
  const objectsArray = Array.from(Objects.value?.values() ?? []);
  
  return [
    new PathLayer({
      id: "stroke",
      data: objectsArray,
      getColor: (obj) => obj.style.color,
      updateTriggers: {
        getColor: objectsArray.map(o => ({ 
          id: o.id, 
          color: o.style.color 
        })),
      },
    }),
  ];
};

onMounted(() => {
  // Initialize map and deckOverlay
  deckOverlay = new MapboxOverlay({
    layers: createDeckLayers(),
    interleaved: true,
  });
  map.addControl(deckOverlay);
  
  // Watch for changes
  watch(
    () => Array.from(Objects.value.values()),
    () => {
      if (deckOverlay?._deck) {
        deckOverlay._deck.setProps({
          layers: createDeckLayers(),
          _animate: true,
        });
        setTimeout(() => deckOverlay._deck.redraw(), 50);
      }
    },
    { deep: true }
  );
});
```

## Debugging Tips

1. **Add logging to accessors:**
   ```typescript
   getColor: (obj) => {
     console.log('getColor called for', obj.id, ':', obj.style.color);
     return obj.style.color;
   }
   ```

2. **Log updateTriggers values:**
   ```typescript
   const triggers = objects.map(o => ({ id: o.id, color: o.style.color }));
   console.log('updateTriggers:', triggers);
   ```

3. **Check if watch fires:**
   ```typescript
   watch(
     () => Array.from(Objects.value.values()),
     (newVal, oldVal) => {
       console.log('Watch fired!', { 
         old: oldVal?.length, 
         new: newVal?.length 
       });
     }
   );
   ```

4. **Verify store updates:**
   ```typescript
   updateObjectStyle(id, style) {
     console.log('Before:', this.Objects.get(id)?.style);
     // ... update logic
     console.log('After:', this.Objects.get(id)?.style);
   }
   ```
