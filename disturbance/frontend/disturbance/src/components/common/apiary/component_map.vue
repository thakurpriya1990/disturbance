<template lang="html">
    <div>
        <div :id="elem_id" class="map"></div>

        <div :id="popup_id" class="ol-popup">
            <a href="#" :id="popup_closer_id" class="ol-popup-closer">
           <svg xmlns='http://www.w3.org/2000/svg' version='1.1' height='20' width='20' class="close-icon">

               <g transform='scale(3)'>
    <path d="M 5.2916667,2.6458333 A 2.6458333,2.6458333 0 0 1 2.6458335,5.2916667 2.6458333,2.6458333 0 0 1 0,2.6458333 2.6458333,2.6458333 0 0 1 2.6458335,0 2.6458333,2.6458333 0 0 1 5.2916667,2.6458333 Z" style="fill:#ffffff;fill-opacity:1;stroke-width:0.182031" id="path846" />
    <path d="M 1.5581546,0.94474048 2.6457566,2.0324189 3.7334348,0.94474048 4.3469265,1.5581547 3.2592475,2.6458334 4.3469265,3.7334353 3.7334348,4.3469261 2.6457566,3.2593243 1.5581546,4.3469261 0.9447402,3.7334353 2.0323422,2.6458334 0.9447402,1.5581547 Z" style="fill:#f46464;fill-opacity:1;stroke:none;stroke-width:0.0512157" id="path2740-3" />
  </g>
           </svg>

            </a>
            <div :id="popup_content_id"></div>
        </div>

    </div>
</template>

<script>
    import uuid from 'uuid';
    import 'ol/ol.css';
    //import 'index.css';  // copy-and-pasted the contents of this file at the <style> section below in this file

    import Map from 'ol/Map';
    import View from 'ol/View';
    import WMTSCapabilities from 'ol/format/WMTSCapabilities';
    import TileLayer from 'ol/layer/Tile';
    import OSM from 'ol/source/OSM';
    import TileWMS from 'ol/source/TileWMS';
    import WMTS, {optionsFromCapabilities} from 'ol/source/WMTS';
    import Collection from 'ol/Collection';
    import {Draw, Modify, Snap} from 'ol/interaction';
    import VectorLayer from 'ol/layer/Vector';
    import VectorSource from 'ol/source/Vector';
    import {Circle as CircleStyle, Fill, Stroke, Style} from 'ol/style';
    import {FullScreen as FullScreenControl, MousePosition as MousePositionControl} from 'ol/control';
    import Vue from 'vue/dist/vue';
    import { Feature } from 'ol';
    import { Point } from 'ol/geom';
    import { getDistance } from 'ol/sphere';
    import { circular} from 'ol/geom/Polygon';
    import GeoJSON from 'ol/format/GeoJSON';
    import Overlay from 'ol/Overlay';
    import { getDisplayNameFromStatus, getDisplayNameOfCategory, getStatusForColour, getApiaryFeatureStyle } from '@/components/common/apiary/site_colours.js'
    import LayerSwitcher from 'ol-layerswitcher';
    import { BaseLayerOptions, GroupLayerOptions } from 'ol-layerswitcher';

    export default {
        props:{
            is_external:{
                type: Boolean,
                default: false
            },
            is_internal:{
                type: Boolean,
                default: false
            },
            apiary_site_geojson_array: {
                type: Array,
                default: function(){
                    return []
                }
            },
            can_modify: {
                type: Boolean,
                default: false
            },
            display_at_time_of_submitted: {
                type: Boolean,
                default: false
            }
        },
        watch: {
            display_at_time_of_submitted: function(){
                console.log('ahoooooooooooo')
            }
        },
        data: function(){
            return{
                map: null,
                apiarySitesQuerySource: null,
                apiarySitesQueryLayer: null,
                elem_id: uuid(),
                popup_id: uuid(),
                popup_closer_id: uuid(),
                popup_content_id: uuid(),
                overlay: null,
                content_element: null,
                modifyInProgressList: []
            }
        },
        created: function(){

        },
        mounted: function(){
            let vm = this;
            this.$nextTick(() => {
                vm.addEventListeners()
            });
            this.initMap()
            this.displayAllFeatures()
        },
        components: {

        },
        computed: {

        },
        methods: {
            closePopup: function(){
                this.overlay.setPosition(undefined)
                this.$emit('popupClosed')
            },
            forceToRefreshMap: function() {
                let vm = this
                setTimeout(function(){
                    vm.map.updateSize();
                }, 50)
            },
            initMap: function() {
                let vm = this;

                let satelliteTileWms = new TileWMS({
                            url: 'https://kmi.dpaw.wa.gov.au/geoserver/public/wms',
                            params: {
                                'FORMAT': 'image/png',
                                'VERSION': '1.1.1',
                                tiled: true,
                                STYLES: '',
                                LAYERS: 'public:mapbox-satellite',
                            }
                        });

                const osm = new TileLayer({
                    title: 'OpenStreetMap',
                    type: 'base',
                    visible: true,
                    source: new OSM(),
                });

                const tileLayerSat = new TileLayer({
                    title: 'Satellite',
                    type: 'base',
                    visible: true,
                    source: satelliteTileWms,
                })

                vm.map = new Map({
                    layers: [
                        osm, 
                        tileLayerSat,
                    ],
                    //target: 'map',
                    target: vm.elem_id,
                    view: new View({
                        center: [115.95, -31.95],
                        zoom: 7,
                        projection: 'EPSG:4326'
                    })
                });
                let layerSwitcher = new LayerSwitcher({
                    reverse: true,
                    groupSelectStyle: 'group'
                })
                vm.map.addControl(layerSwitcher)

                vm.apiarySitesQuerySource = new VectorSource({

                });
                vm.apiarySitesQueryLayer = new VectorLayer({
                    source: vm.apiarySitesQuerySource,
                    //style: this.drawStyle
                    style: function(feature, resolution){
                        let status = getStatusForColour(feature, false, vm.display_at_time_of_submitted)
                        return getApiaryFeatureStyle(status, feature.get('checked'))
                    },
                });
                vm.map.addLayer(vm.apiarySitesQueryLayer);

                // Full screen toggle
                vm.map.addControl(new FullScreenControl());

                // Show mouse coordinates
                vm.map.addControl(new MousePositionControl({
                    coordinateFormat: function(coords){
                        let message = vm.getDegrees(coords) + "\n";
                        return  message;
                    },
                    target: document.getElementById('mouse-position'),
                    className: 'custom-mouse-position',
                }));

                // Add apiary_sites passed as a props
                for (let i=0; i<vm.apiary_site_geojson_array.length; i++){
                    this.addApiarySite(vm.apiary_site_geojson_array[i])
                }

                let container = document.getElementById(vm.popup_id)
                vm.content_element = document.getElementById(vm.popup_content_id)
                let closer = document.getElementById(vm.popup_closer_id)

                vm.overlay = new Overlay({
                    element: container,
                    autoPan: false,
                    offest: [0, -10]
                })

                closer.onclick = function() {
                    vm.closePopup()
                    closer.blur()
                    return false
                }

                vm.map.addOverlay(vm.overlay)

                vm.map.on('click', function(evt){
                    let feature = vm.map.forEachFeatureAtPixel(evt.pixel, function(feature, layer) {
                        return feature;
                    });
                    if (feature){
                        if (!feature.id){
                            // When the Modify object is used for the layer, 'feature' losts some of the attributes including 'id', 'status'...
                            // Therefore try to get the correct feature by the coordinate
                            let geometry = feature.getGeometry();
                            let coord = geometry.getCoordinates();
                            feature = vm.apiarySitesQuerySource.getFeaturesAtCoordinate(coord)
                        }
                        vm.showPopup(feature[0])
                    }
                })
                vm.map.on('pointermove', function(e) {
                    if (e.dragging) return;
                    let pixel = vm.map.getEventPixel(e.originalEvent);
                    let hit = vm.map.hasFeatureAtPixel(pixel);
                    vm.map.getTargetElement().style.cursor = hit ? 'pointer' : '';
                });
                vm.map.on('moveend', function(e){
                    let extent = vm.map.getView().calculateExtent(vm.map.getSize());
                    let features = vm.apiarySitesQuerySource.getFeaturesInExtent(extent)
                    vm.$emit('featuresDisplayed', features)
                });
                if (vm.can_modify){
                    let modifyTool = new Modify({
                        source: vm.apiarySitesQuerySource,
                    });
                    modifyTool.on("modifystart", function(attributes){
                        attributes.features.forEach(function(feature){
                        })
                    });
                    modifyTool.on("modifyend", function(attributes){
                        attributes.features.forEach(function(feature){
                            let id = feature.getId();
                            let index = vm.modifyInProgressList.indexOf(id);
                            if (index != -1) {
                                // feature has been modified
                                vm.modifyInProgressList.splice(index, 1);
                                let coords = feature.getGeometry().getCoordinates();
                                vm.$emit('featureGeometryUpdated', {'id': id, 'coordinates': {'lng': coords[0], 'lat': coords[1]}})
                            }
                        });
                    });
                    vm.map.addInteraction(modifyTool);
                }
            },
            showPopupById: function(apiary_site_id){
                let feature = this.apiarySitesQuerySource.getFeatureById(apiary_site_id)
                this.showPopup(feature)
            },
            showPopup: function(feature){
                if (feature){
                    let geometry = feature.getGeometry();
                    let coord = geometry.getCoordinates();
                    let svg_hexa = "<svg xmlns='http://www.w3.org/2000/svg' version='1.1' height='20' width='15'>" +
                    '<g transform="translate(0, 4) scale(0.9)"><path d="M 14.3395,12.64426 7.5609998,16.557828 0.78249996,12.64426 0.7825,4.8171222 7.5609999,0.90355349 14.3395,4.8171223 Z" id="path837" style="fill:none;stroke:#ffffff;stroke-width:1.565;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1" /></g></svg>'
                    //let status_str = feature.get('is_vacant') ? getDisplayNameFromStatus(feature.get('status')) + ' (vacant)' : getDisplayNameFromStatus(feature.get('status'))
                    let status_str = getDisplayNameFromStatus(getStatusForColour(feature, false, this.display_at_time_of_submitted))
                    let content = '<div style="padding: 0.25em;">' +
                    '<div style="background: darkgray; color: white; text-align: center;" class="align-middle">' + svg_hexa + ' site: ' + feature.id_ + '</div>' +
                                      '<div style="font-size: 0.8em;">' +
                                          '<div>' + status_str + '</div>' +
                                          '<div>' + getDisplayNameOfCategory(feature.get('site_category')) + '</div>' +
                                          '<div>' + feature['values_']['geometry']['flatCoordinates'] + '</div>' +
                                      '</div>' +
                                  '</div>'
                    this.content_element.innerHTML = content;
                    this.overlay.setPosition(coord);
                }
            },
            getDegrees: function(coords){
                return coords[0].toFixed(6) + ', ' + coords[1].toFixed(6);
            },
            addApiarySite: function(apiary_site_geojson) {
                
                let vm = this
                let feature = (new GeoJSON()).readFeature(apiary_site_geojson)

                feature.getGeometry().on("change", function() {
                    let feature_id = feature.getId()
                    if (vm.modifyInProgressList.indexOf(feature_id) == -1) {
                        vm.modifyInProgressList.push(feature_id);
                    }
                })

                this.apiarySitesQuerySource.addFeature(feature)
            },
            removeApiarySiteById: function(apiary_site_id){
                let feature = this.apiarySitesQuerySource.getFeatureById(apiary_site_id)
                this.apiarySitesQuerySource.removeFeature(feature)
            },
            zoomToApiarySiteById: function(apiary_site_id){
                let feature = this.apiarySitesQuerySource.getFeatureById(apiary_site_id)
                let geometry = feature.getGeometry()
                let coord = geometry.getCoordinates()
                let view = this.map.getView()
                this.map.getView().animate({zoom: 16, center: feature['values_']['geometry']['flatCoordinates']})
                this.showPopup(feature)
            },
            setApiarySiteSelectedStatus: function(apiary_site_id, selected) {
                let feature = this.apiarySitesQuerySource.getFeatureById(apiary_site_id)
                let style_applied = getApiaryFeatureStyle(getStatusForColour(feature, false, this.display_at_time_of_submitted), selected)
                feature.setStyle(style_applied)
            },
            addEventListeners: function () {

            },
            displayAllFeatures: function() {
                if (this.apiarySitesQuerySource.getFeatures().length>0){
                    let view = this.map.getView()

                    let ext = this.apiarySitesQuerySource.getExtent()
                    let centre = [(ext[0] + ext[2])/2.0, (ext[1] + ext[3])/2.0]
                    //view.fit(ext)
                    let resolution = view.getResolutionForExtent(ext);
                    let z = view.getZoomForResolution(resolution) - 1
                    view.animate({zoom: z, center: centre})
                }
            },
        },
    }
</script>

<style lang="css" scoped>
    .ol-popup {
        position: absolute;
        min-width: 95px;
        background-color: white;
        -webkit-filter: drop-shadow(0 1px 4px rgba(0,0,0,0.2));
        filter: drop-shadow(0 1px 4px rgba(0,0,0,0.2));
        padding: 2px;
        border-radius: 4px;
        border: 1px solid #ccc;
        bottom: 12px;
        left: -50px;
    }
    .ol-popup:after, .ol-popup:before {
        top: 100%;
        border: solid transparent;
        content: " ";
        height: 0;
        width: 0;
        position: absolute;
        pointer-events: none;
    }
    .ol-popup:after {
        border-top-color: white;
        border-width: 10px;
        left: 48px;
        margin-left: -10px;
    }
    .ol-popup:before {
        border-top-color: #cccccc;
        border-width: 11px;
        left: 48px;
        margin-left: -11px;
    }
    .ol-popup-closer {
        text-decoration: none;
        position: absolute;
        top: 2px;
        right: 8px;
    }
    .ol-popup-closer:after {
        /*
        content: "✖";
        */
    }
    .close-icon:hover {
        filter: brightness(80%);
    }
    .close-icon {
        position: absolute;
        left: 1px;
        top: -11px;
        filter: drop-shadow(0 1px 4px rgba(0,0,0,0.2));
    }
    .popup-wrapper {
        padding: 0.25em;
    }
    .popup-content-header {
        background: darkgray;
        color: white;
    }
    .popup-content {
        font-size: small;
    }
</style>
