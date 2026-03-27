# Deck.gl Layer Configuration Examples

## PolygonLayer with Fill and Stroke

```typescript
import { PolygonLayer } from "@deck.gl/layers";

// Fill layer (separate from stroke for better control)
new PolygonLayer({
  id: "polygon-fill",
  data: polygonObjects,
  getPolygon: (obj) => obj.coordinates,
  
  // Fill color with opacity
  getFillColor: (obj) => {
    const color = obj.style.color;
    const opacity = obj.style.fillOpacity ?? 0.5;
    return [
      color[0],
      color[1],
      color[2],
      Math.round(color[3] * opacity)
    ];
  },
  
  // No outline from fill layer
  getLineColor: [0, 0, 0, 0],
  
  // Important settings
  pickable: false,  // Let clicks pass through to stroke layer
  stroked: false,
  filled: true,
  wireframe: false,
  
  // Trigger updates when color or opacity changes
  updateTriggers: {
    getFillColor: polygonObjects.map(o => ({
      id: o.id,
      color: o.style.color,
      fillOpacity: o.style.fillOpacity,
    })),
  },
});

// Stroke layer (separate for independent control)
new PathLayer({
  id: "polygon-stroke",
  data: polygonObjects,
  getPath: (obj) => obj.coordinates,
  getColor: (obj) => obj.style.color,
  getWidth: (obj) => obj.style.strokeWidth ?? 2,
  
  // Dash pattern support
  getDashArray: (obj) => {
    const dash = obj.style.strokeDasharray;
    return dash && dash[0] > 0 ? dash : [0, 0];
  },
  
  pickable: true,
  autoHighlight: true,
  
  // Required for dash support
  extensions: [new PathStyleExtension({ dash: true })],
  
  updateTriggers: {
    getColor: polygonObjects.map(o => ({ id: o.id, color: o.style.color })),
    getWidth: polygonObjects.map(o => ({ id: o.id, strokeWidth: o.style.strokeWidth })),
    getDashArray: polygonObjects.map(o => ({ id: o.id, strokeDasharray: o.style.strokeDasharray })),
  },
});
```

## Polyline with Dash Pattern

```typescript
import { PathLayer } from "@deck.gl/layers";
import { PathStyleExtension } from "@deck.gl/extensions";

const pathStyleExtension = new PathStyleExtension({
  dash: true,           // Enable dash
  highPrecision: false, // Use standard precision (faster)
});

new PathLayer({
  id: "polyline",
  data: lineObjects,
  getPath: (obj) => obj.coordinates,
  getColor: (obj) => obj.style.color,
  getWidth: (obj) => obj.style.strokeWidth ?? 5,
  
  // Dash pattern: [dashLength, gapLength]
  getDashArray: (obj) => {
    const dash = obj.style.strokeDasharray;
    // Return [0, 0] for solid lines (required!)
    return dash && dash[0] && dash[0] > 0 ? dash : [0, 0];
  },
  
  // Joint and cap styles
  getMiterLimit: (obj) => 4,
  getCapRounding: (obj) => true,
  getJointRounding: (obj) => true,
  
  pickable: true,
  autoHighlight: true,
  
  extensions: [pathStyleExtension],
  
  updateTriggers: {
    getColor: lineObjects.map(o => ({ id: o.id, color: o.style.color })),
    getWidth: lineObjects.map(o => ({ id: o.id, strokeWidth: o.style.strokeWidth })),
    getDashArray: lineObjects.map(o => ({ id: o.id, strokeDasharray: o.style.strokeDasharray })),
  },
});
```

## CircleMarker (ScatterplotLayer)

```typescript
import { ScatterplotLayer } from "@deck.gl/layers";

new ScatterplotLayer({
  id: "circle-marker",
  data: pointObjects,
  
  // Position from first coordinate
  getPosition: (obj) => obj.coordinates[0] ?? [0, 0],
  
  // Color and size
  getColor: (obj) => obj.style.color,
  getRadius: (obj) => obj.style.radius ?? 10,
  
  // Minimum/maximum radius in pixels
  radiusMinPixels: 5,   // Never smaller than 5px
  radiusMaxPixels: 20,  // Never larger than 20px
  
  // Rendering quality
  antialiasing: true,
  stroked: false,
  filled: true,
  
  // Interaction
  pickable: true,
  autoHighlight: true,
  highlightColor: [255, 255, 0, 100],
  
  updateTriggers: {
    getColor: pointObjects.map(o => ({ id: o.id, color: o.style.color })),
    getRadius: pointObjects.map(o => ({ id: o.id, radius: o.style.radius })),
  },
});
```

## Draft Layer (Temporary Object Being Created)

```typescript
const createDraftLayer = (draft: DraftObject | null) => {
  if (!draft || draft.coordinates.length === 0) return [];
  
  const draftColor = [255, 255, 0, 255] as [number, number, number, number];
  const layers: any[] = [];
  
  // CircleMarker draft (even with 1 point)
  if (draft.type === "CircleMarker" && draft.coordinates.length > 0) {
    layers.push(
      new ScatterplotLayer({
        id: "draft-circle",
        data: [draft],
        getPosition: (d) => d.coordinates[0] ?? [0, 0],
        getColor: draftColor,
        getRadius: 15,
        radiusMinPixels: 10,
        pickable: false,
      })
    );
  }
  
  // Polygon/Polyline draft (needs 2+ points)
  else if (draft.coordinates.length >= 2) {
    // Line layer for outline
    layers.push(
      new PathLayer({
        id: "draft-line",
        data: [draft],
        getPath: (d) => d.coordinates,
        getColor: draftColor,
        getWidth: 3,
        pickable: false,
      })
    );
    
    // Polygon fill (needs 3+ points)
    if (draft.type === "Polygon" && draft.coordinates.length >= 3) {
      layers.push(
        new PolygonLayer({
          id: "draft-polygon-fill",
          data: [draft],
          getPolygon: (d) => d.coordinates,
          getFillColor: [255, 255, 0, 100], // Semi-transparent yellow
          getLineColor: [0, 0, 0, 0],
          pickable: false,
        })
      );
    }
  }
  
  return layers;
};
```

## Complete Layer Factory Function

```typescript
const createDeckLayers = () => {
  const layers: any[] = [];
  const objectsArray = Array.from(Objects.value?.values() ?? []);
  
  // 1. Polygon fill layer
  const polygonFillObjects = objectsArray.filter(
    (obj) => (obj.type === "Polygon" || obj.type === "Polyline") && obj.style.filled !== false
  );
  
  if (polygonFillObjects.length > 0) {
    layers.push(
      new PolygonLayer({
        id: "polygon-fill",
        data: polygonFillObjects,
        getPolygon: (obj) => obj.coordinates,
        getFillColor: (obj) => {
          const color = obj.style.color;
          return [
            color[0]!,
            color[1]!,
            color[2]!,
            Math.round(color[3]! * (obj.style.fillOpacity ?? 0.5))
          ];
        },
        getLineColor: [0, 0, 0, 0],
        pickable: false,
        stroked: false,
        filled: true,
        updateTriggers: {
          getFillColor: polygonFillObjects.map(o => ({
            id: o.id,
            color: o.style.color,
            fillOpacity: o.style.fillOpacity,
          })),
        },
      })
    );
  }
  
  // 2. Polygon/Polyline stroke layer
  const lineObjects = objectsArray.filter(
    (obj) => obj.type === "Polygon" || obj.type === "Polyline"
  );
  
  if (lineObjects.length > 0) {
    const pathStyleExtension = new PathStyleExtension({
      dash: true,
      highPrecision: false,
    });
    
    layers.push(
      new PathLayer({
        id: "polygon-stroke",
        data: lineObjects,
        getPath: (obj) => obj.coordinates,
        getColor: (obj) => obj.style.color,
        getWidth: (obj) => obj.style.strokeWidth ?? 2,
        getDashArray: (obj) => {
          const dash = obj.style.strokeDasharray;
          return dash && dash[0] > 0 ? dash : [0, 0];
        },
        pickable: true,
        autoHighlight: true,
        extensions: [pathStyleExtension],
        updateTriggers: {
          getColor: lineObjects.map(o => ({ id: o.id, color: o.style.color })),
          getWidth: lineObjects.map(o => ({ id: o.id, strokeWidth: o.style.strokeWidth })),
          getDashArray: lineObjects.map(o => ({ id: o.id, strokeDasharray: o.style.strokeDasharray })),
        },
      })
    );
  }
  
  // 3. CircleMarker layer
  const pointObjects = objectsArray.filter(
    (obj) => obj.type === "CircleMarker"
  );
  
  if (pointObjects.length > 0) {
    layers.push(
      new ScatterplotLayer({
        id: "circle-marker",
        data: pointObjects,
        getPosition: (obj) => obj.coordinates[0] ?? [0, 0],
        getColor: (obj) => obj.style.color,
        getRadius: (obj) => obj.style.radius ?? 10,
        radiusMinPixels: 5,
        radiusMaxPixels: 20,
        pickable: true,
        autoHighlight: true,
        updateTriggers: {
          getColor: pointObjects.map(o => ({ id: o.id, color: o.style.color })),
          getRadius: pointObjects.map(o => ({ id: o.id, radius: o.style.radius })),
        },
      })
    );
  }
  
  // 4. Draft layer (optional)
  if (DraftObject.value && DraftObject.value.coordinates.length > 0) {
    const draftLayers = createDraftLayer(DraftObject.value);
    layers.push(...draftLayers);
  }
  
  console.log("[Map] Total layers:", layers.length);
  return layers;
};
```

## Color Conversion Utilities

```typescript
// utils/color.ts

export type RGBAColor = [number, number, number, number];

/**
 * Convert hex color to RGBA array
 * @param hex - Hex color (#RRGGBB)
 * @param alpha - Alpha value (0-255), default 255
 */
export const hexToRGBA = (hex: string, alpha: number = 255): RGBAColor => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) return [0, 0, 0, alpha];
  
  return [
    parseInt(result[1]!, 16),
    parseInt(result[2]!, 16),
    parseInt(result[3]!, 16),
    alpha,
  ];
};

/**
 * Convert RGBA to hex color
 * @param rgba - RGBA array [r, g, b, a]
 */
export const rgbaToHex = ([r, g, b]: RGBAColor): string => {
  return `#${[r, g, b]
    .map((c) => Math.round(c).toString(16).padStart(2, "0"))
    .join("")}`;
};

// Usage in component:
const newColor = hexToRGBA('#ff0000'); // [255, 0, 0, 255]
const hexColor = rgbaToHex([0, 128, 255, 255]); // "#0080ff"
```

## Coordinate Conversion Utilities

```typescript
// utils/coords.ts

import type { LngLatTuple, BackendLatLng } from "@/types";

/**
 * Convert backend coordinates to Deck.gl format
 * Backend: [{lat, lng}, ...] → Deck.gl: [[lng, lat], ...]
 */
export const backendCoordsToDeckGL = (coords: BackendLatLng[]): LngLatTuple[] => {
  return coords.map(({ lat, lng }) => [lng, lat]);
};

/**
 * Convert Deck.gl coordinates to backend format
 * Deck.gl: [[lng, lat], ...] → Backend: [{lat, lng}, ...]
 */
export const deckGLToBackendCoords = (coords: LngLatTuple[]): BackendLatLng[] => {
  return coords.map(([lng, lat]) => ({ lat, lng }));
};

// Usage in component:
const deckCoords = backendCoordsToDeckGL([{ lat: 50, lng: 30 }]);
// Result: [[30, 50]]

const backendCoords = deckGLToBackendCoords([[30, 50]]);
// Result: [{ lat: 50, lng: 30 }]
```
