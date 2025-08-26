// Type definitions for leaflet.groupedlayercontrol.js (minimal, for TS compatibility)
import * as L from 'leaflet';

declare module 'leaflet' {
  namespace control {
    function groupedLayers(
      baseLayers: { [name: string]: L.Layer },
      groupedOverlays: { [group: string]: { [name: string]: L.Layer } },
      options?: any
    ): L.Control.Layers;
  }
}

declare module '*.js' {
  // Allow importing JS plugins with no types
  const value: any;
  export default value;
}
