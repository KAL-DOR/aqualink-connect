import 'leaflet';

declare module 'leaflet' {
  interface MarkerClusterGroupOptions {
    chunkedLoading?: boolean;
    maxClusterRadius?: number;
    spiderfyOnMaxZoom?: boolean;
    showCoverageOnHover?: boolean;
    zoomToBoundsOnClick?: boolean;
    disableClusteringAtZoom?: number;
    iconCreateFunction?: (cluster: MarkerCluster) => L.DivIcon | L.Icon;
    spiderLegPolylineOptions?: L.PolylineOptions;
    singleMarkerMode?: boolean;
    removeOutsideVisibleBounds?: boolean;
    animate?: boolean;
    animateAddingMarkers?: boolean;
    spiderfyDistanceMultiplier?: number;
    polygonOptions?: L.PolylineOptions;
  }

  interface MarkerCluster extends L.Marker {
    getChildCount(): number;
    getAllChildMarkers(): L.Marker[];
    spiderfy(): void;
    unspiderfy(): void;
  }

  interface MarkerClusterGroup extends L.FeatureGroup {
    addLayer(layer: L.Layer): this;
    removeLayer(layer: L.Layer): this;
    clearLayers(): this;
    getVisibleParent(marker: L.Marker): L.Marker | MarkerCluster;
    refreshClusters(layers?: L.Layer | L.Layer[]): this;
    hasLayer(layer: L.Layer): boolean;
    zoomToShowLayer(layer: L.Marker, callback?: () => void): void;
  }

  function markerClusterGroup(options?: MarkerClusterGroupOptions): MarkerClusterGroup;
}
