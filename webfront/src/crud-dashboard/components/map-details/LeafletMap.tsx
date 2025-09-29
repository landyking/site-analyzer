import Box from '@mui/material/Box';
import { useEffect, useRef } from 'react';
import 'leaflet/dist/leaflet.css';
import { css } from '@emotion/react';
import L from 'leaflet';
import 'leaflet.fullscreen';
import 'leaflet.fullscreen/Control.FullScreen.css';
import axios from 'axios';

interface LeafletMapProps {
  fileUrl: string;
  fileTag: string;
  mapHeight: number;
}

const TITILER_URL: string = import.meta.env.VITE_TITILER_URL;

// Inline CSS for the legend, mimicking map.html
const legendStyle = css`
  background: white;
  padding: 0px;
  font-size: 12px;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  text-align: center;
  width: 20px;
  .legend-scale {
    display: flex;
    flex-direction: column;
    align-items: center;
    font-size: 11px;
  }
  .legend-scale span {
    margin: 1px 0;
  }
  img {
    display: block;
    margin: 1px auto;
    width: 8px;
    height: 150px;
    transform: rotate(180deg);
  }
`;

// Helper: create a tile layer
function createTileLayer(url: string, options: L.TileLayerOptions = {}) {
  return L.tileLayer(url, options);
}

function file_type_2_color_map(file_type: string): string {
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
function createLegendControl(fileTag: string): L.Control {
  const legend = new L.Control({ position: 'bottomleft' });
  legend.onAdd = function () {
    const div = L.DomUtil.create('div', 'legend');
    div.id = fileTag+'-legend-content';
    div.innerHTML = `<div>No legend</div>`;
    return div;
  };
  return legend;
}

// Helper: update legend content
function updateLegend(fileTag: string, min: number, max: number, imgUrl: string) {
  const div = document.getElementById(fileTag+'-legend-content');
  if (!div) return;
  if (!imgUrl) {
    div.innerHTML = `<div></div>`;
  } else {
    div.innerHTML = `
    <div class="legend-scale">
      <span>${max}</span>
      <img src="${imgUrl}" alt="legend"/>
      <span>${min}</span>
    </div>
  `;
  }
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
      return [[b[1], b[0]], [b[3], b[2]]];
    }
  } catch (e) {
    console.error('Error fetching bounds:', e);
  }
  return null;
}

// Helper: fetch raster stats and add overlay using plain axios
async function addRasterOverlay(params: {
  tag: string
  colorMap: string;
  map: L.Map;
  layerControl: L.Control.Layers;
  bounds: L.LatLngBoundsExpression;
  colorMapMapping: Record<string, [string, number, number]>;
  url: string;
}) {
  const { colorMap, map, tag, layerControl, bounds, colorMapMapping, url } = params;
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

      layerControl.addOverlay(raster, tag);
      colorMapMapping[tag] = [colorMap, min, max];
      raster.addTo(map);
    }
  } catch (e) {
    console.error('Error fetching raster stats:', e);
  }
}
const LeafletMap: React.FC<LeafletMapProps> = ({ fileUrl, fileTag, mapHeight }) => {

  const mapRef = useRef<HTMLDivElement>(null);
  const leafletMapRef = useRef<L.Map | null>(null);

  useEffect(() => {
    let isMounted = true;
    if (!mapRef.current) return;
    if (leafletMapRef.current) return;

    // Example: mimic the map.html logic
    (async () => {

      // 1. Fetch bounds
      const bounds = await fetchBounds(fileUrl);
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
      const map = L.map(mapRef.current, { layers: [cartoLight] }).setView([0, 0], 2);
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

      const layerControl: L.Control.Layers = L.control.layers(baseMaps).addTo(map);

      // 5. Add legend
      const legend = createLegendControl(fileTag);
      legend.addTo(map);

      // 6. Color map mapping for overlays
      const colorMapMapping: Record<string, [string, number, number]> = {};
      map.on('overlayadd', () => {
        const mapping = colorMapMapping[fileTag];
        if (mapping) {
          const [cm, min, max] = mapping;
          const url = `${TITILER_URL}/titiler/colorMaps/${cm}?orientation=vertical&f=png&format=png&min=${min}&max=${max}&width=20&height=150`;
          updateLegend(fileTag, min, max, url);
        } else {
          updateLegend(fileTag, 0, 0, '');
        }
      });
      map.on('overlayremove', () => {
        updateLegend(fileTag, 0, 0, '');
      });

      // 7. Add raster overlays
      await addRasterOverlay({
        colorMap: file_type_2_color_map(fileTag),
        map, layerControl, bounds: bounds!,
        colorMapMapping, tag: fileTag,
        url: fileUrl
      })
    })();

    return () => {
      isMounted = false;
      if (leafletMapRef.current) {
        leafletMapRef.current.remove();
        leafletMapRef.current = null;
      }
    };
  }, [fileTag, fileUrl]);

  return (
    <Box sx={{ p: 2 }}>
      <div
        ref={mapRef}
        style={{ height: mapHeight, width: '100%', borderRadius: 8, marginBottom: 16 }}
      />
      {/* Inline legend style for SSR/CSR consistency */}
      <style>{`.legend {${legendStyle.styles}}`}</style>
    </Box>
  );
};

export default LeafletMap;
