import Box from '@mui/material/Box';
import { useEffect, useRef } from 'react';
import 'leaflet/dist/leaflet.css';
import '../../../jslibs/leaflet.groupedlayercontrol.css';
import { css } from '@emotion/react';
import L from 'leaflet';
import 'leaflet.fullscreen';
import 'leaflet.fullscreen/Control.FullScreen.css';
import '../../../jslibs/leaflet.groupedlayercontrol.js';
import type { MapTaskDetails } from '../../../client/types.gen';
import axios from 'axios';

interface MapTabProps {
  mapTask: MapTaskDetails;
}
interface MapTabInnerProps {
  mapTask: MapTaskDetails;
}

const TITILER_URL: string = import.meta.env.VITE_TITILER_URL;

// Inline CSS for the legend, mimicking map.html
const legendStyle = css`
  background: white;
  padding: 8px;
  font-size: 12px;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  text-align: center;
  width: 45px;
  .legend-scale {
    display: flex;
    flex-direction: column;
    align-items: center;
    font-size: 11px;
  }
  .legend-scale span {
    margin: 2px 0;
  }
  img {
    display: block;
    margin: 5px auto;
    width: 20px;
    height: 150px;
    transform: rotate(180deg);
  }
`;

// Helper: create a tile layer
function createTileLayer(url: string, options: L.TileLayerOptions = {}) {
  return L.tileLayer(url, options);
}

function file_type_2_color_map (file_type: string): string {
  switch (file_type) {
    case 'final':
      return 'greens';
    case 'slope':
      return 'greens';// "terrain",
    case 'restricted':
      return 'reds_r';
    case 'weighted':
      return 'greens';
    default:
      return 'greens';
  }
};

// Helper: create a legend control
function createLegendControl(): L.Control {
  const legend = new L.Control({ position: 'bottomleft' });
  legend.onAdd = function () {
    const div = L.DomUtil.create('div', 'legend');
    div.id = 'legend-content';
    div.innerHTML = `<div>No legend</div>`;
    return div;
  };
  return legend;
}

// Helper: update legend content
function updateLegend(min: number, max: number, imgUrl: string) {
  const div = document.getElementById('legend-content');
  if (!div) return;
  if(!imgUrl){
    div.innerHTML=`<div>No legend</div>`;
  }else{
  div.innerHTML = `
    <div><strong>Score</strong></div>
    <div class="legend-scale">
      <span>${max}</span>
      <img src="${imgUrl}" alt="legend"/>
      <span>${min}</span>
    </div>
  `;}
}

// Helper: fetch bounds from TiTiler using plain axios
async function fetchBounds(url: string): Promise<L.LatLngBoundsExpression | null> {
  try {
    const resp = await axios.get(`${TITILER_URL}/titiler/bounds`, {
      params: { url },
    });
    // Expecting: { bounds: [minX, minY, maxX, maxY] }
    const data = resp.data as { bounds?: [number, number, number, number] };
    if (data && data.bounds) {
      const b = data.bounds;
      return [ [b[1], b[0]], [b[3], b[2]] ];
    }
  } catch (e) {
    console.error('Error fetching bounds:', e);
  }
  return null;
}

// Helper: fetch raster stats and add overlay using plain axios
async function addRasterOverlay(params: {
  task: number;
  tag: string;
  colorMap: string;
  map: L.Map;
  layerControl: L.Control.Layers;
  bounds: L.LatLngBoundsExpression;
  colorMapMapping: Record<string, [string, number, number]>;
  def?: boolean;
  url: string;
}) {
  const { tag, colorMap, map, layerControl, bounds, colorMapMapping, def, url } = params;
  try {
    const resp = await axios.get(`${TITILER_URL}/titiler/statistics`, {
      params: { url },
    });
    // Expecting: { b1: { min: number, max: number, ... } }
    const data = resp.data as { b1?: { min: number; max: number } };
    if (data && data.b1) {
      const b = data.b1;
      const min = Math.floor(b.min);
      const max = Math.ceil(b.max);
      const rescale = `${min},${max}`;
      const titilerUrl = `${TITILER_URL}/titiler/tiles/WebMercatorQuad/{z}/{x}/{y}.png?colormap_name=${colorMap}&url=${encodeURIComponent(url)}&rescale=${rescale}`;
      const raster = createTileLayer(titilerUrl, {
        tileSize: 256,
        opacity: 0.8,
        bounds,
        noWrap: true,
      });
      (layerControl as L.Control.Layers & { addOverlay: (layer: L.Layer, name: string, group: string) => void }).addOverlay(raster, tag, 'Results');
      colorMapMapping[tag] = [colorMap, min, max];
      if (def) raster.addTo(map);
    }
  } catch (e) {
    console.error('Error fetching raster stats:', e);
  }
}
const MapInner:React.FC<MapTabInnerProps> = ({ mapTask }) => {
  
  const mapRef = useRef<HTMLDivElement>(null);
  const leafletMapRef = useRef<L.Map | null>(null);

  useEffect(() => {
    let isMounted = true;
    if (!mapRef.current) return;
    if (leafletMapRef.current) return;

    // Example: mimic the map.html logic
    (async () => {
      // Demo task/tag/colormap
      const task = mapTask.id;
      // filter mapTask files to find type is "final"
      const finalFile = mapTask.files?.find(file => file.file_type === 'final');
      const finalUrl = (finalFile?.file_path || ''); //encodeURIComponent(finalFile?.file_path || '');

      // 1. Fetch bounds
      const bounds = await fetchBounds(finalUrl);
      if (!isMounted || !mapRef.current) return;

      // 2. Create base layers
      const osmStandard = createTileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
      });
      const cartoLight = createTileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '© OpenStreetMap contributors © CARTO',
        subdomains: 'abcd',
        maxZoom: 20,
      });
      const cartoDark = createTileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '© OpenStreetMap contributors © CARTO',
        subdomains: 'abcd',
        maxZoom: 20,
      });
      const emptyLayer = createTileLayer('', { attribution: '' });

      // 3. Init map
      const map = L.map(mapRef.current, { layers: [cartoDark] }).setView([0, 0], 2);
      leafletMapRef.current = map;
      if (bounds) map.fitBounds(bounds);

      // Add fullscreen control if plugin is loaded
      if ((L as any).control?.fullscreen) {
        (L as any).control.fullscreen({ position: 'topleft' }).addTo(map);
      }

      // 4. Grouped layer control
      const baseMaps = {
        None: emptyLayer,
        'OSM Standard': osmStandard,
        'Carto Light': cartoLight,
        'Carto Dark': cartoDark,
      };
      const options = {
        exclusiveGroups: ['Results'],
      };
  
      const layerControl: L.Control.Layers & { addOverlay: (layer: L.Layer, name: string, group: string) => void } = L.control.groupedLayers(baseMaps, {}, options).addTo(map);

      // 5. Add legend
      const legend = createLegendControl();
      legend.addTo(map);

      // 6. Color map mapping for overlays
      const colorMapMapping: Record<string, [string, number, number]> = {};
      map.on('overlayadd', (e: L.LayersControlEvent) => {
        const mapping = colorMapMapping[e.name];
        if (mapping) {
          const [cm, min, max] = mapping;
          const url = `${TITILER_URL}/titiler/colorMaps/${cm}?orientation=vertical&f=png&format=png&min=${min}&max=${max}&width=20&height=150`;
          updateLegend(min, max, url);
        }else{
          updateLegend(0,0,'');
        }
      });

      // 7. Add raster overlays
      const emptyLayer2 = createTileLayer('', { attribution: '', opacity: 0 });
      (layerControl as L.Control.Layers & { addOverlay: (layer: L.Layer, name: string, group: string) => void }).addOverlay(emptyLayer2, 'none', 'Results');
      const overlays: Promise<void>[] = []
      mapTask?.files?.forEach(file => {
        overlays.push(addRasterOverlay({
          task, tag: file.file_type, colorMap: file_type_2_color_map(file.file_type), 
          map, layerControl, bounds: bounds!,
           colorMapMapping, def: file.file_type === 'final',
           url: file.file_path
        }));
      });
      await Promise.all(overlays);
    })();

    return () => {
      isMounted = false;
      if (leafletMapRef.current) {
        leafletMapRef.current.remove();
        leafletMapRef.current = null;
      }
    };
  }, [mapTask]);

  return (
    <Box sx={{ p: 2 }}>
      <div
        ref={mapRef}
        style={{ height: 500, width: '100%', borderRadius: 8, marginBottom: 16 }}
      />
      {/* Inline legend style for SSR/CSR consistency */}
      <style>{`.legend {${legendStyle.styles}}`}</style>
    </Box>
  );
};

const MapTab: React.FC<MapTabProps> = ({ mapTask }) => {
  return <MapInner mapTask={mapTask}/>;
};

export default MapTab;
