<template lang="html">
    <div>
        <div :id="elem_id" class="map"></div>
        
        <div :id="popup_id" class="ol-popup">
            <a href="#" :id="popup_closer_id" class="ol-popup-closer"></a>
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
    import { getFillColour, getStrokeColour, existingSiteRadius } from '@/components/common/apiary/site_colours.js'

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
        },
        watch: {

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
            forceToRefreshMap: function() {
                let vm = this
                setTimeout(function(){
                    console.log('updateResize()')
                    vm.map.updateSize();
                }, 50)
            },
            getStyle: function(status, checked){
                let fillObj = getFillColour(status)
                let strokeObj = getStrokeColour(status, checked)
                return new Style({
                            image: new CircleStyle({
                                radius: existingSiteRadius,
                                fill: fillObj,
                                stroke: strokeObj,
                            })
                        })
            },
            initMap: function() {
                let vm = this;

                vm.map = new Map({
                    layers: [
                        new TileLayer({
                            source: new OSM(),
                            opacity:0.5
                        })
                    ],
                    //target: 'map',
                    target: vm.elem_id,
                    view: new View({
                        center: [115.95, -31.95],
                        zoom: 7,
                        projection: 'EPSG:4326'
                    })
                });
                vm.apiarySitesQuerySource = new VectorSource({

                });
                vm.apiarySitesQueryLayer = new VectorLayer({
                    source: vm.apiarySitesQuerySource,
                    //style: this.drawStyle
                    style: function(feature, resolution){
                        return vm.getStyle(feature.get('status'), feature.get('checked'))
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
                let content_element = document.getElementById(vm.popup_content_id)
                let closer = document.getElementById(vm.popup_closer_id)

                closer.onclick = function() {
                    overlay.setPosition(undefined)
                    closer.blur()
                    return false
                }

                let overlay = new Overlay({
                    element: container,
                    autoPan: false,
                    offest: [0, -10]
                })
                vm.map.addOverlay(overlay)

                vm.map.on('click', function(evt){
                    let feature = vm.map.forEachFeatureAtPixel(evt.pixel, function(feature, layer) {
                        return feature;
                    });
                    if (feature){
                        console.log(feature)
                        let geometry = feature.getGeometry();
                        let coord = geometry.getCoordinates();
                        console.log(coord)
                        let content = '<div>site: ' + feature.id_ + '</div>';
                        content_element.innerHTML = content;
                        overlay.setPosition(coord);
                    }
                })
                vm.map.on('pointermove', function(e) {
                    if (e.dragging) return;
                    let pixel = vm.map.getEventPixel(e.originalEvent);
                    let hit = vm.map.hasFeatureAtPixel(pixel);
                    vm.map.getTargetElement().style.cursor = hit ? 'pointer' : '';
                });
            },
            getDegrees: function(coords){
                return coords[0].toFixed(6) + ', ' + coords[1].toFixed(6);
            },
            addApiarySite: function(apiary_site_geojson) {
                let feature = (new GeoJSON()).readFeature(apiary_site_geojson)
                this.apiarySitesQuerySource.addFeature(feature)
            },
            removeApiarySiteById: function(apiary_site_id){
                let feature = this.apiarySitesQuerySource.getFeatureById(apiary_site_id)
                console.log(feature)
                this.apiarySitesQuerySource.removeFeature(feature)
            },
            zoomToApiarySiteById: function(apiary_site_id){
                let feature = this.apiarySitesQuerySource.getFeatureById(apiary_site_id)
                        let geometry = feature.getGeometry();
                        let coord = geometry.getCoordinates();
                        console.log(coord)
                let view = this.map.getView()
                this.map.getView().animate({zoom: 16, center: feature['values_']['geometry']['flatCoordinates']})
            },
            setApiarySiteSelectedStatus: function(apiary_site_id, selected) {
                console.log('setApiarySiteSelectedStatus')
                let feature = this.apiarySitesQuerySource.getFeatureById(apiary_site_id)
                let style_applied = this.getStyle(feature.get('status'), selected)
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
        min-width: 80px;
        background-color: white;
        -webkit-filter: drop-shadow(0 1px 4px rgba(0,0,0,0.2));
        filter: drop-shadow(0 1px 4px rgba(0,0,0,0.2));
        padding: 2px;
        border-radius: 10px;
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
        content: "✖";
    }
</style>
