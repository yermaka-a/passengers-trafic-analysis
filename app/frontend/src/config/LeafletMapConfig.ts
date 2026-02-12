export default class LeafletMapConfig {
  static get startedZoom(): number {
    return 14;
  }
  static get startedCoords(): [number, number] {
    return [52.544358, 103.888249];
  }

  static get OSMAttr(): string {
    return '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>';
  }
}
