<template>
    <div class="container" id="internalProposalsMap">
    <div class="row">
        <div class="col-sm-12">
            <FormSection :formCollapse="false" label="Proposals Map (Geoserver)" Index="proposals_map_geoserver">
                <div class="map-wrapper">
                    <!-- <div v-show="!fullscreen" id="filter_search_row_wrapper">
                        <div class="filter_search_wrapper" style="margin-bottom: 5px;" id="filter_search_row">
                            <div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <button type="button" class="btn btn-primary btn-margin" @click="shapefileButtonClicked(false)" :disabled="download_shapefile_btn_disabled">
                                            <i v-if="download_shapefile_btn_disabled" class="fa fa-download fa-spinner fa-spin"></i>
                                            <i v-else class="fa fa-download"></i>
                                            Download Shapefile
                                        </button>
                                        <a class="btn btn-primary" href="/filelist" target="_blank">View Download Files</a>
                                    </div>
                                </div>
                                <div class="row mb-2"></div>
                            </div>
                        </div>
                    </div> -->
                    

                    <div :id="elem_id" class="map" style="position: relative;">
                        
                        <div v-show="fullscreen" id="filter_search_on_map">
                            <!-- filters on map here -->
                            <!-- end filter here -->
                        </div>     
                        <div v-if="loading_proposals" class="spinner_on_map">
                            <i class='fa fa-4x fa-spinner fa-spin'></i>
                        </div>
                        <div class="basemap-button">
                            <img id="basemap_sat" :src="satelliteIconUrl" @click="setBaseLayer('sat')" />
                            <img id="basemap_osm" :src="mapIconUrl" @click="setBaseLayer('osm')" />
                        </div>
                        <div class="optional-layers-wrapper">
                            <div style="position:relative">
                                <transition>
                                    <div v-if="optionalLayers.length" class="optional-layers-button" @mouseover="hover=true">
                                        <img src="@/assets/layers.svg" />
                                    </div>
                                </transition>
                                <transition v-if="optionalLayers.length">
                                    <div class="layer_options" v-show="hover" @mouseover="showOptions"  @mouseleave="hideOptions">
                                        <div v-for="layer in optionalLayers" :key="layer.ol_uid">
                                            <input
                                                type="checkbox"
                                                :id="layer.ol_uid"
                                                :checked="layer.values_.visible"
                                                @change="changeLayerVisibility(layer)"
                                                class="layer_option form-check-input"
                                            />
                                            <label :for="layer.ol_uid" class="layer_option">{{ layer.get('title') }}</label>
                                        </div>
                                    </div>
                                </transition>
                            </div>
                        </div>
                        <div id="mouse-position" class="custom-mouse-position"></div>
                    </div>
                    <!--- <div class="button_row">
                        <span class="view_all_button" @click="displayAllFeatures">View All On Map</span>
                    </div> -->
                </div>
                <div :id="popup_id" class="ol-popup">
                    <a href="#" :id="popup_closer_id" class="ol-popup-closer">
                        <svg xmlns='http://www.w3.org/2000/svg' version='1.1' height='20' width='20' class="close-icon">
                            <g transform='scale(3)'>
                                <path d     ="M 5.2916667,2.6458333 A 2.6458333,2.6458333 0 0 1 2.6458335,5.2916667 2.6458333,2.6458333 0 0 1 0,2.6458333 2.6458333,2.6458333 0 0 1 2.6458335,0 2.6458333,2.6458333 0 0 1 5.2916667,2.6458333 Z" style="fill:#ffffff;fill-opacity:1;stroke-width:0.182031" id="path846" />
                                <path d     ="M 1.5581546,0.94474048 2.6457566,2.0324189 3.7334348,0.94474048 4.3469265,1.5581547 3.2592475,2.6458334 4.3469265,3.7334353 3.7334348,4.3469261 2.6457566,3.2593243 1.5581546,4.3469261 0.9447402,3.7334353 2.0323422,2.6458334 0.9447402,1.5581547 Z" style="fill:#f46464;fill-opacity:1;stroke:none;stroke-width:0.0512157" id="path2740-3" />
                            </g>
                        </svg>
                    </a>
                    <div :id="popup_content_id"></div>
                </div>
            </FormSection>
        </div>
    </div>
    </div>
</template>

<script>
    import {v4 as uuidv4 } from 'uuid';
    import FormSection from '@/components/forms/section_toggle.vue';
    import 'ol/ol.css';
    import 'ol-layerswitcher/dist/ol-layerswitcher.css'
    import Map from 'ol/Map';
    import View from 'ol/View';
    import formatWKT  from 'ol/format/WKT';
    import TileLayer from 'ol/layer/Tile';
    import TileWMS from 'ol/source/TileWMS';
    import WMTS from 'ol/source/WMTS';
    import WMTSTilegrid from 'ol/tilegrid/WMTS';
    import { Modify } from 'ol/interaction';
    import VectorLayer from 'ol/layer/Vector';
    import VectorSource from 'ol/source/Vector';
    import { Circle as CircleStyle, Fill, Stroke, Style, Text } from 'ol/style';
    import { FullScreen as FullScreenControl, MousePosition as MousePositionControl } from 'ol/control';
    import { Point } from 'ol/geom';
    import GeoJSON from 'ol/format/GeoJSON';
    import Overlay from 'ol/Overlay';
    import { zoomToCoordinates } from '@/components/common/apiary/site_colours.js'
    import Cluster from 'ol/source/Cluster';
    import { api_endpoints, helpers } from '@/utils/hooks'
    import {getCenter} from 'ol/extent'
    import {get as getProjection} from 'ol/proj';
    import {getTopLeft, getWidth} from 'ol/extent'
    import { toRaw } from 'vue';
    export default {
        name: 'ProposalMapGeoserver',
        data: function(){

            return {
                satelliteIconUrl: new URL('../../../assets/satellite_icon.jpg', import.meta.url).href,
                mapIconUrl: new URL('../../../assets/map_icon.png', import.meta.url).href,
                newVectorLayer: null,
                newVectorLayerCluster: null,
                newQuerySource: null,
                debug: true,
                show_spinner: false,
                download_shapefile_btn_disabled: false,
                modalBindId: uuidv4(),
                map: null,
                proposals: null,
                proposalQuerySource: null,
                proposalClusterLayer: null,
                elem_id: uuidv4(),
                popup_id: uuidv4(),
                popup_closer_id: uuidv4(),
                popup_content_id: uuidv4(),
                overlay: null,
                content_element: null,
                modifyInProgressList: [],
                tileLayerOsm: null,
                tileLayerSat: null,
                optionalLayers: [],
                hover: false,
                mode: 'normal',
                fullscreen: false,
                proposal_status: [],

                is_external: false,
                is_internal: true,
                can_modify: false,
                level: 'internal',
            }
        },
        components: {
            FormSection,
        },
        watch: {
            
        },
        computed: {
            loading_proposals: function(){
                return false
            },
            csrf_token: function() { 
              return helpers.getCookie('csrftoken') 
            },

        },
        methods: {
            shapefileButtonClicked: function (geojson) {
                let vm = this
                vm.show_spinner = true;
                vm.download_shapefile_btn_disabled = true;
                let url = '/api/proposal/create_shapefile/'

                fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        geojson: geojson,
                    })
                })
                .then(response => response.json())
                .then(data => {
                    swal.fire({
                        title: 'Create shapefile',
                        html: data.message + "<br> Click <a href='/filelist' target='_blank'> here </a> to view downloaded file",
                        icon: 'success',
                        customClass: {confirmButton: 'btn btn-primary'},
                    });
                    vm.show_spinner = false;
                    vm.download_shapefile_btn_disabled = false;
                })
                .catch(error => {
                    swal.fire({
                        title: 'Create shapefile Error',
                        //text: helpers.apiVueResourceError(error),
                        text: error,
                        icon: 'error',
                        customClass: {confirmButton: 'btn btn-primary'},
                    });
                    vm.show_spinner = false;
                    vm.download_shapefile_btn_disabled = false;
                });

            },
            clearProposalsFromMap: function(){
                this.proposalQuerySource.clear()
            },
            loadFeatures: function (proposals) {
                let vm = this;
                // Remove all features from the layer
                vm.proposalQuerySource.clear();
                proposals.forEach(function (proposal) {
                    let feature = (new GeoJSON()).readFeatures(proposal.shapefile_json);
                     // let f=feature[0]
                    // f.setProperties({
                    //     proposal: proposal,
                    // })
                    if(feature.length>0){
                        feature.forEach(function (f){
                            f.setProperties({
                            proposal: proposal,
                            })
                        });
                    }
                    vm.proposalQuerySource.addFeatures(feature);
                    // Zoom to loaded features
                    vm.displayAllFeatures(vm.proposalQuerySource);
                });
            },
            mouseEnter: function(e){
                let vm = this;
                if (!vm.not_close_popup_by_mouseleave){
                    let apiary_site_id = e.currentTarget.getAttribute("data-apiary-site-id");
                    if (apiary_site_id){
                        vm.showPopupById(apiary_site_id)
                    }
                }
            },
            mouseLeave: function(){
                let vm = this;
                if (!vm.not_close_popup_by_mouseleave){
                    vm.closePopup()
                }
            },
            setBaseLayer: function(selected_layer_name){
                let vm = this
                if (selected_layer_name == 'sat') {
                    vm.tileLayerOsm.setVisible(false)
                    vm.tileLayerSat.setVisible(true)
                    $('#basemap_sat').hide()
                    $('#basemap_osm').show()
                } else {
                    vm.tileLayerOsm.setVisible(true)
                    vm.tileLayerSat.setVisible(false)
                    $('#basemap_osm').hide()
                    $('#basemap_sat').show()
                }
            },
            set_mode: function(mode){
                this.mode = mode
            },
            changeLayerVisibility: function(targetLayer){
                targetLayer.setVisible(!targetLayer.getVisible())
            },
            addOptionalLayers: function(){
                let vm = this
                fetch('/api/das_map_layers/').then(
                    async response => {
                        if (!response.ok) {
                            return await response.json().then(err => { throw err });
                        }
                        let layers = await response.json();
                        for (var i = 0; i < layers.length; i++ ){
                            // check if the layer name is 'DISTURBANCE_WA' to set it as default visible layer
                            const layerName = (layers[i].layer_full_name || '').toUpperCase()
                            // boolean to determine if the layer should be visible by default
                            const isDefaultVisibleLayer = layerName.includes('DISTURBANCE_WA') || layerName === 'DISTURBANCE_WA'

                            let l = new TileWMS({
                                // url: env['kmi_server_url'] + '/geoserver/' + layers[i].layer_group_name + '/wms',
                                //url:'/kb-proxy/geoserver/' + layers[i].layer_group_name + '/wms',
                                url: layers[i].layer_group_name ? '/kb-proxy/geoserver/' + layers[i].layer_group_name + '/wms' : '/kb-proxy/geoserver/wms',
                                //url:'/kmi-proxy/geoserver/' + layers[i].layer_group_name + '/wms',
                                params: {
                                    'FORMAT': 'image/png',
                                    'VERSION': '1.1.1',
                                    tiled: true,
                                    STYLES: '',
                                    LAYERS: layers[i].layer_full_name
                                },
                                //crossOrigin: 'Anonymous',
                            });

                            let tileLayer= new TileLayer({
                                title: layers[i].display_name.trim(),
                                visible: isDefaultVisibleLayer,
                                source: l,
                            })

                            // Set additional attributes to the layer
                            tileLayer.set('columns', layers[i].columns)
                            tileLayer.set('display_all_columns', layers[i].display_all_columns)

                            vm.optionalLayers.push(tileLayer)
                            vm.map.addLayer(tileLayer)
                        }
                    }).catch((error) => {
                        console.log(error);
                    }
                )
            },
            closePopup: function(){
                this.content_element.innerHTML = null
                this.overlay.setPosition(undefined)
                this.not_close_popup_by_mouseleave = false
                //this.$emit('popupClosed')
            },
            forceToRefreshMap: function() {
                let vm = this
                setTimeout(function(){
                    vm.map.updateSize();
                }, 50)
            },
            
            initMap: function() {
                let vm = this;
                // var ol = {'proj': proj, 'extent': Extent,}
                var projection = getProjection("EPSG:3857");
                var projectionExtent = projection.getExtent();
                var s = getWidth(projectionExtent) / 256;
                var matrixSet = "mercator";
                var resolutions = new Array(21);
                var matrixIds = new Array(21);
                
                for (var c = 0; c < 21; ++c)
                    resolutions[c] = s / Math.pow(2, c),
                    matrixIds[c] = matrixSet + ":" + c;
                
                var m = new WMTSTilegrid({
                    origin: getTopLeft(projectionExtent),
                    resolutions: resolutions,
                    matrixIds: matrixIds
                });
                
                let satelliteTileWms = new TileWMS({
                    url: env['kb_server_url'] + '/geoserver/kaartdijin-boodja-public/wms',
                    params: {
                        'FORMAT': 'image/png',
                        'VERSION': '1.1.1',
                        tiled: true,
                        STYLES: '',
                        LAYERS: 'kaartdijin-boodja-public:mapbox-satellite-public',
                    },
                });
                vm.tileLayerOsmWorking= new TileLayer({
                    name: "street",
                    canDelete: "no",
                    visible: !0,
                    source: new WMTS({
                        url: "/kb-proxy/geoserver/gwc/service/wmts",
                        format: "image/png",
                        layer: "kaartdijin-boodja-public:mapbox-streets-public",
                        matrixSet: matrixSet,
                        projection: 'EPSG:3857',
                        tileGrid: m,
                        //crossOrigin: 'Anonymous'
                    })
                })
                
                let streetsTileWMS = new TileWMS({
                url: env['kb_server_url'] + '/geoserver/kaartdijin-boodja-public/wms',
                params: {
                    FORMAT: 'image/png',
                    VERSION: '1.1.1',
                    tiled: true,
                    STYLES: '',
                    LAYERS: "kaartdijin-boodja-public:mapbox-streets-public",
                },
                });
                
                vm.tileLayerOsm= new TileLayer({
                    name: "street",
                    canDelete: "no",
                    visible: !0,
                    type: 'base',
                    source: streetsTileWMS,
                    }),

                vm.tileLayerSat = new TileLayer({
                    title: 'Satellite',
                    type: 'base',
                    visible: true,
                    source: satelliteTileWms,
                })

                vm.map = new Map({
                    layers: [
                        toRaw(vm.tileLayerOsm), 
                        toRaw(vm.tileLayerSat),
                    ],
                    //target: 'map',
                    target: vm.elem_id,
                    view: new View({
                        center: [115.95, -31.95],
                        zoom: 7,
                        projection: 'EPSG:4326'
                    }),
                    pixelRatio: 1,  // We need this in order to make this map work correctly with the browser and/or display scaling factor(s) other than 100%
                                    // Ref: https://github.com/openlayers/openlayers/issues/11464
                });

                vm.proposalQuerySource = new VectorSource({ });                

                let clusterSource = new Cluster({
                    distance: 50,
                    source: vm.proposalQuerySource,
                    geometryFunction: (feature) => {
                        try {
                            const geometry = feature.getGeometry();
                            const proposal = feature.getProperties().proposal.id;
                            if (!geometry) {
                                console.warn('Feature with null geometry for Proposal:', proposal);
                                return null;
                            }
                            const type = geometry.getType();
                            switch (type) {
                                case 'Polygon':
                                    return geometry.getInteriorPoint();
                                case 'LineString':
                                    return new Point(geometry.getCoordinateAt(0.5));
                                case 'Point':
                                    return geometry;
                                case 'MultiPolygon':
                                    return new Point(getCenter(feature.getGeometry().getExtent()), 'XY');
                                default:
                                    console.warn('Unsupported geometry type:', type, feature);
                                    return null;
                            }
                        } catch (err) {
                            console.log('Error processing feature', feature, err);
                            return null;
                        }
                    },
                })

                let styleCache = {}
                let sameFeature=false;
                var zoomedInStyle = new Style({
                    stroke: new Stroke({
                        color: 'orange',
                        width: 3
                    }),
                    fill: new Fill({
                        color: 'rgba(255, 165, 0, 0.1)'
                    }),
                    geometry: function(feature){
                        var originalFeature = feature.get('features');
                        return originalFeature[0].getGeometry();
                    }
                    });
                    styleCache[1]=zoomedInStyle;
                vm.proposalClusterLayer = new VectorLayer({
                    title: 'Cluster Layer',
                    source: clusterSource,
                    
                    style: function (clusteredFeature){
                        let featuresInClusteredFeature = clusteredFeature.get('features')
                        let size = featuresInClusteredFeature.length
                        let style = styleCache[size]
                        if(size == 1 ){
                            // When size is 1, which means the cluster feature has only one site
                            // we want to display it as dedicated style
                            return zoomedInStyle;
                        }
                        let radius_in_pixel = 16
                        if(size < 10){
                            radius_in_pixel = 10
                        } else if (size < 100){
                            radius_in_pixel = 12
                        } else if (size < 1000){
                            radius_in_pixel = 14
                        }
                        if(!style){
                            style = new Style({
                                image: new CircleStyle({
                                    radius: radius_in_pixel,
                                    stroke: new Stroke({
                                        color: '#fff',
                                    }),
                                    fill: new Fill({
                                        color: '#3399cc'
                                    }),
                                }),
                                text: new Text({
                                    text: size.toString(),
                                    fill: new Fill({
                                        color: '#fff',
                                    })
                                }), 
                            })
                            styleCache[size] = style
                        }
                        return style
                    },
                });
                vm.map.addLayer(vm.proposalClusterLayer);
                vm.proposalClusterLayer.setZIndex(10)  


                // Full screen toggle
                let fullScreenControl = new FullScreenControl()
                fullScreenControl.on('enterfullscreen', function(){
                    vm.fullscreen = true
                })
                fullScreenControl.on('leavefullscreen', function(){
                    vm.fullscreen = false
                })
                vm.map.addControl(fullScreenControl)

                // Show mouse coordinates
                vm.map.addControl(new MousePositionControl({
                    coordinateFormat: function(coords){
                        let message = vm.getDegrees(coords) + "\n";
                        return  message;
                    },
                    target: document.getElementById('mouse-position'),
                    className: 'custom-mouse-position',
                }));

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

                vm.map.on('singleclick', function(evt){
                    if (vm.mode === 'layer'){
                        let feature = vm.map.forEachFeatureAtPixel(evt.pixel, function(feature) {
                            return feature;
                            
                        });
                        if (feature){
                            let features = feature.get('features')
                            if (features.length == 1){
                                if (!feature.id){
                                    // When the Modify object is used for the layer, 'feature' losts some of the attributes including 'id', 'status'...
                                    // Therefore try to get the correct feature by the coordinate
                                    let geometry = feature.getGeometry();
                                    let coord = geometry.getCoordinates();
                                    feature = vm.proposalQuerySource.getFeaturesAtCoordinate(coord)
                                }
                                // let proposal = features[0].getProperties().proposal;
                                vm.showPopup(features[0])
                            } else {
                                //if proposal id is different but geometry is exactly same
                                sameFeature = false;
                                for(var i=0; i<features.length; i++ ){
                                    let formatwkt = new formatWKT();
                                    let feature1 = formatwkt.writeGeometry(features[0].getGeometry());
                                    let feature2 = formatwkt.writeGeometry(features[i].getGeometry());
                                    if(feature1 === feature2){
                                        sameFeature=true;
                                        //break;
                                    }
                                    else{
                                        sameFeature=false;
                                        break;
                                    }       
                                }
                                console.log('samefeature', sameFeature) 
                                if(sameFeature){
                                        //vm.proposalClusterLayer.setStyle(zoomedInStyle);
                                    vm.showPopupforSameFeatures(features, evt.coordinate)
                                        //vm.showPopup(features[0])
                                }
                                else{
                                    //else keep zooming in
                                    let currentZoomLevel = vm.map.getView().getZoom()
                                    let maxZoom = vm.map.getView().getMaxZoom() || 20
                                    
                                    // If we've reached max zoom or zoom level 18, show all features instead of zooming
                                    if (currentZoomLevel >= Math.min(maxZoom, 18)) {
                                        vm.showPopupforSameFeatures(features, evt.coordinate)
                                    } else {
                                        let geometry = feature.getGeometry();
                                        let coordinates = geometry.getCoordinates();
                                        zoomToCoordinates(vm.map, coordinates, currentZoomLevel + 1)
                                    }
                                }
                                //end
                                // //else keep zooming in
                                // let geometry = feature.getGeometry();
                                // let coordinates = geometry.getCoordinates();
                                // let currentZoomLevel = vm.map.getView().getZoom()
                                // zoomToCoordinates(vm.map, coordinates, currentZoomLevel + 1)
                            }
                        } else {
                            vm.closePopup()
                            let view = vm.map.getView()
                            let viewResolution = view.getResolution()

                            // Retrieve active layers' sources
                            for (let i=0; i < vm.optionalLayers.length; i++){
                                let visibility = vm.optionalLayers[i].getVisible()
                                if (visibility){
                                    // Retrieve column names to be displayed
                                    let column_names = vm.optionalLayers[i].get('columns')
                                    column_names = column_names.map(function(col){
                                        // Convert array of dictionaries to simple array
                                        if (vm.is_internal && col.option_for_internal){
                                            return col.name
                                        }
                                        if (vm.is_external && col.option_for_external){
                                            return col.name
                                        }
                                    })
                                    // Retrieve the value of display_all_columns boolean flag
                                    let display_all_columns = vm.optionalLayers[i].get('display_all_columns')

                                    // Retrieve the URL to query the attributes
                                    let source = vm.optionalLayers[i].getSource()
                                    let url = source.getFeatureInfoUrl(
                                        evt.coordinate, viewResolution, view.getProjection(),
                                        //{'INFO_FORMAT': 'text/html'}
                                        {'INFO_FORMAT': 'application/json'}
                                    )

                                    // Query 
                                    let p = fetch(url, {
                                        credentials: 'include'
                                    })

                                    p.then(async (res) => await res.json()).then(function(data){
                                        vm.showPopupForLayersJson(data, evt.coordinate, column_names, display_all_columns, vm.optionalLayers[i])
                                    })
                                }
                            }
                        }
                    } 
                })
                vm.map.on('pointermove', function(e) {
                    if (e.dragging) return;
                    let pixel = vm.map.getEventPixel(e.originalEvent);
                    let hit = vm.map.hasFeatureAtPixel(pixel);
                    vm.map.getTargetElement().style.cursor = hit ? 'pointer' : '';
                });
                vm.map.on('moveend', function(){
                    let extent = vm.map.getView().calculateExtent(vm.map.getSize());
                    let features = vm.proposalQuerySource.getFeaturesInExtent(extent)
                    vm.$emit('featuresDisplayed', features)
                });
                if (vm.can_modify){
                    let modifyTool = new Modify({
                        source: vm.proposalQuerySource,
                    });
                    modifyTool.on("modifystart", function(attributes){
                            attributes.features.forEach(function(){
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
                // document.addEventListener('keydown', vm.keydown, false)
            },
            // keydown: function(evt){
            //     let vm = this

            //     let charCode = (evt.which) ? evt.which : evt.keyCode;
            //     if (charCode === 27 && vm.measuring === true){ //esc key
            //         //dispatch event
            //         this.drawForMeasure.set('escKey', Math.random());
            //     }
            // },
            showPopupById: function(apiary_site_id){
                let feature = this.proposalQuerySource.getFeatureById(apiary_site_id)
                this.showPopup(feature)
            },
            
            showPopup: function(feature){
                let unique_id = uuidv4()
                // let proposal = feature.getProperties().proposal;
                // console.log('selected proposal', proposal);

                if (feature){
                    let geometry = feature.getGeometry();
                    let coord = geometry.getCoordinates();
                    let proposal = feature.getProperties().proposal;
                    let type = feature.getGeometry().getType();
                    if (type === 'Polygon') {
                        coord= feature.getGeometry().getInteriorPoint();
                    } else if (type === 'LineString') {
                        coord= feature.getGeometry().getCoordinateAt(0.5);
                    } else if (type === 'Point') {
                        coord= feature.getGeometry();
                    } else if (type === 'MultiPolygon') {
                        coord= new Point(getCenter(feature.getGeometry().getExtent()), 'XY');
                    }
                    coord=coord.getCoordinates();
                    let processing_status_str = proposal.processing_status_display
                    let customer_status_str = proposal.customer_status_display
                    let region_str = proposal.region_name
                    
                    //let proposal_type_str= proposal.proposal_type
                    let proposal_type_str= proposal.application_type_name
                    let lodgement_date_str= proposal.lodgement_date ? moment(proposal.lodgement_date).format('DD/MM/YYYY') : ''
                    let submitter_str=proposal.submitter_full_name
                    let applicant_name=proposal.applicant_name
                    let approval_rows=''
                    if(proposal.approval_lodgement_number){
                        approval_rows= '<tr>' +
                                  '<th scope="row">Approval</th>' +
                                  '<td>' + 
                                        '<table class="table">' +
                                        '<tbody>' +
                                        '<tr>' +
                                        '<th scope="row">Status</th>' +
                                        '<td>' + proposal.approval_status + '</td>' +
                                        '</tr>' +
                                        '<tr>' +
                                        '<th scope="row">Start Date</th>' +
                                        '<td>' + moment(proposal.approval_start_date).format('DD/MM/YYYY') + '</td>' +
                                        '</tr>' +
                                        '<tr>' +
                                        '<th scope="row">Expiry date</th>' +
                                        '<td>' + moment(proposal.approval_expiry_date).format('DD/MM/YYYY') + '</td>' +
                                        '</tr>' +
                                        '</tbody>' +
                                        '</table>'
                                  '</td>' +
                                '</tr>' 
                        
                    }
                    let a_table = ''
                    if (this.is_internal){
                        a_table = '<table class="table">' +
                              '<tbody>' +
                                '<tr>' +
                                  '<th scope="row">Proponent</th>' +
                                  '<td><span id=' + unique_id + '></span>'+ applicant_name+ '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Region</th>' +
                                  '<td>' + region_str + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Proposal Type</th>' +
                                  '<td>' + proposal_type_str + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Lodgement Date</th>' +
                                  '<td>' + lodgement_date_str + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Status</th>' +
                                  '<td>' + processing_status_str + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Submitter</th>' +
                                  '<td>' + submitter_str + '</td>' +
                                '</tr>' + 
                                approval_rows +
                              '</tbody>' +
                            '</table>'
                    } else if (this.is_external){
                        a_table = '<table class="table">' +
                              '<tbody>' +
                                '<tr>' +
                                  '<th scope="row">Proponent</th>' +
                                  '<td><span id=' + unique_id + '></span>'+ applicant_name+ '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Region</th>' +
                                  '<td>' + region_str + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Proposal Type</th>' +
                                  '<td>' + proposal_type_str + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Lodgement Date</th>' +
                                  '<td>' + lodgement_date_str + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Status</th>' +
                                  '<td>' + customer_status_str + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Submitter</th>' +
                                  '<td>' + submitter_str + '</td>' +
                                '</tr>' + 
                                approval_rows +
                              '</tbody>' +
                            '</table>'
                    }

                    let content = '<div style="padding: 0.25em;">' +
                                      '<div style="background: darkgray; color: white; text-align: center; padding: 0.5em;" class="align-middle">' + ' Proposal: ' + proposal.lodgement_number + '</div>' +
                                      a_table +
                                  '</div>'

                    this.content_element.innerHTML = content;
                    this.overlay.setPosition(coord);
                }
            },
            showPopupforSameFeatures: function(features, popupCoord=null){
                // let unique_id = uuidv4()
                // let proposal = feature.getProperties().proposal;
                // console.log('selected proposal', proposal);
                let proposal_rows='';
                for (let feature of features){
                    if (feature){
                        // let geometry = feature.getGeometry();
                        // let coord = geometry.getCoordinates();
                        let proposal = feature.getProperties().proposal;
                        // let type = feature.getGeometry().getType();
                        // if (type === 'Polygon') {
                        //     coord= feature.getGeometry().getInteriorPoint();
                        // } else if (type === 'LineString') {
                        //     coord= feature.getGeometry().getCoordinateAt(0.5);
                        // } else if (type === 'Point') {
                        //     coord= feature.getGeometry();
                        // } else if (type === 'MultiPolygon') {
                        //     coord= new Point(getCenter(feature.getGeometry().getExtent()), 'XY');
                        // }
                        // coord=coord.getCoordinates();
                        let processing_status_str = proposal.processing_status_display
                        // let customer_status_str = proposal.customer_status_display
                        let region_str = proposal.region_name
                        
                        //let proposal_type_str= proposal.proposal_type
                        let proposal_type_str= proposal.application_type_name
                        // let lodgement_date_str= proposal.lodgement_date ? moment(proposal.lodgement_date).format('DD/MM/YYYY') : ''
                        let submitter_str=proposal.submitter_full_name
                        // let applicant_name=proposal.applicant_name
                        let url = this.is_internal ? '/internal/proposal/' + proposal.id : '/external/proposal/' + proposal.id  
                        let proposal_row='<tr>' +
                                  '<td>' +proposal.lodgement_number + '</td>' +
                                //   '<td><span id=' + unique_id + '></span>'+ applicant_name+ '</td>' +
                                  '<td>' + region_str + '</td>' +
                                  '<td>' + proposal_type_str + '</td>' +
                                  '<td>' + processing_status_str + '</td>' +
                                  '<td>' + submitter_str + '</td>' +
                                  '<td>'+ '<a href="' + url + '">View</a>'
                                '</tr>'
                        proposal_rows=proposal_rows + proposal_row; 
                        
                    }
                }
                let a_table = '';
                if(features){

               
                        a_table = '<table class="table">' +
                              '<tbody>' +
                                '<tr>' +
                                  '<th scope="row">Proposal</th>' +
                                //   '<th scope="row">Applicant</th>' +
                                  '<th scope="row">Region</th>' +
                                  '<th scope="row">Proposal Type</th>' +
                                  '<th scope="row">Status</th>' +
                                  '<th scope="row">Submitter</th>' +
                                  '<th scope="row">Link</th>' +
                                '</tr>' +
                                proposal_rows+
                              '</tbody>' +
                            '</table>'
                        let coord = popupCoord;
                        if (!coord) {
                            let geometry = features[0].getGeometry();
                            coord = geometry.getCoordinates();
                            let type = features[0].getGeometry().getType();
                            if (type === 'Polygon') {
                                coord = features[0].getGeometry().getInteriorPoint();
                            } else if (type === 'LineString') {
                                coord = features[0].getGeometry().getCoordinateAt(0.5);
                            } else if (type === 'Point') {
                                coord = features[0].getGeometry();
                            } else if (type === 'MultiPolygon') {
                                coord = new Point(getCenter(features[0].getGeometry().getExtent()), 'XY');
                            }
                            coord = coord.getCoordinates();
                        }
                        let content = '<div style="padding: 0.25em;">' +
                                        '<div style="background: darkgray; color: white; text-align: center; padding: 0.5em;" class="align-middle">' +' Proposal: '+ '</div>' +
                                        a_table +
                                    '</div>'

                        this.content_element.innerHTML = content;
                        this.overlay.setPosition(coord);
                 }
            },
            showPopupForLayersJson: function(geojson, coord, column_names, display_all_columns, target_layer){
                let wrapper = $('<div>')  // Add wrapper element because html() used at the end exports only the contents of the jquery object
                let caption = $('<div style="text-align:center; font-weight: bold;">').text(target_layer.get('title'))
                let table = $('<table style="margin-bottom: 1em;">') //.addClass('table')
                let tbody = $('<tbody>')
                wrapper.append(caption)
                wrapper.append(table.append(tbody))

                for (let feature of geojson.features){
                    for (let key in feature.properties){
                        if (display_all_columns || column_names.includes(key)){
                            let tr = $('<tr style="border-bottom:1px solid lightgray;">')
                            let th = $('<th style="padding:0 0.5em;">').text(key)
                            let td = $('<td>').addClass('text-nowrap').text(feature.properties[key])
                            tr.append(th)
                            tr.append(td)
                            tbody.append(tr)
                        }
                    }
                    this.content_element.innerHTML += wrapper.html()  // Export contents as HTML string
                    this.overlay.setPosition(coord);
                }
            },
            showPopupForLayersHTML: function(html_str, coord, column_names, display_all_columns){
                // Generate jquery object from html_str
                let html_obj = $('<div>').html(html_str)

                // Retrieve tables as jquery object
                let tables = html_obj.find("table")

                if (!display_all_columns){
                    // Hide all columns
                    tables.find('th,td').css('display', 'none')

                    // Make a certain column visible
                    for (let i=0; i<column_names.length; i++){
                        let index = tables.find('th').filter(function(){
                            // <th> element whoose text is exactly same as column_names[i]
                            return $(this).text() === column_names[i]
                        }).css('display', '').index()

                        let idx = index + 1

                        // Display <td> in the same column
                        let td = tables.find('td:nth-child(' + idx + ')')
                        td.css('display', '')
                    }
                }

                if (tables.length){
                    this.content_element.innerHTML += html_obj.html()
                    this.overlay.setPosition(coord);
                }
            },
            getDegrees: function(coords){
                return coords[0].toFixed(6) + ', ' + coords[1].toFixed(6);
            },
            displayAllFeatures: function() {
                if (this.proposalQuerySource.getFeatures().length>0){
                    let view = this.map.getView()

                    let ext = this.proposalQuerySource.getExtent()
                    let centre = [(ext[0] + ext[2])/2.0, (ext[1] + ext[3])/2.0]
                    //view.fit(ext)
                    let resolution = view.getResolutionForExtent(ext);
                    let z = view.getZoomForResolution(resolution) - 1
                    view.animate({zoom: z, center: centre})
                }
            },
            displayAllFeaturesNew: function(querySource) {
                if (querySource.getFeatures().length>0){
                    let view = this.map.getView()

                    let ext = querySource.getExtent()
                    let centre = [(ext[0] + ext[2])/2.0, (ext[1] + ext[3])/2.0]
                    //view.fit(ext)
                    let resolution = view.getResolutionForExtent(ext);
                    let z = view.getZoomForResolution(resolution) - 1
                    view.animate({zoom: z, center: centre})
                }
            },

            fetchProposals: async function(){
                let vm=this;
                // let _ajax_obj=null;
                var ajax_data={"proposal_status": 'All'}
                // Add region filter if not 'All'
                // if (vm.filterProposalRegion && vm.filterProposalRegion !== 'All') {
                //     ajax_data['region'] = vm.filterProposalRegion;
                // }
                let url = api_endpoints.das_map_proposal 
                $.ajax({
                            url: url,
                            
                            //type:'GET',
                            
                            data: ajax_data,
                            dataType: 'json',
                            success: function(re){
                                vm.proposals = re;
                                if(vm.proposals.length>0){
                                    vm.loadFeatures(vm.proposals);
                                }
                            },
                            error: function (jqXhr, textStatus, errorMessage) { // error callback
                                console.log(errorMessage);
                            }
                        })
            },//End fetch_ajax_data
            showOptions() {
                this.hover = true;
            },
            hideOptions() {
                this.hover = false;
            },
        },
        
        mounted: function() {
            let vm = this;
            vm.initMap()
            vm.fetchProposals()
            vm.setBaseLayer('osm')
            vm.set_mode('layer')
            vm.addOptionalLayers()
            vm.displayAllFeatures()
        },
    }
</script>

<style lang="css" scoped>
    @import '../apiary/map_address_search_scoped.css';

    .map-wrapper {
        position: relative;
        padding: 0;
        margin: 0;
    }
    #filter_search_on_map {
        position: absolute;
        top: 10px;
        left: 60px;
        z-index: 99999;
    }
    .basemap-button {
        position: absolute;
        bottom: 25px;
        right: 10px;
        z-index: 400;
        -moz-box-shadow: 3px 3px 3px #777;
        -webkit-box-shadow: 3px 3px 3px #777;
        box-shadow: 3px 3px 3px #777;
        -moz-filter: brightness(1.0);
        -webkit-filter: brightness(1.0);
        filter: brightness(1.0);
        border: 2px white solid;
    }
    .basemap-button:hover,.optional-layers-button:hover{
        cursor: pointer;
        -moz-filter: brightness(0.9);
        -webkit-filter: brightness(0.9);
        filter: brightness(0.9);
    }
    .basemap-button:active {
        bottom: 24px;
        right: 9px;
        -moz-box-shadow: 2px 2px 2px #555;
        -webkit-box-shadow: 2px 2px 2px #555;
        box-shadow: 2px 2px 2px #555;
        -moz-filter: brightness(0.8);
        -webkit-filter: brightness(0.8);
        filter: brightness(0.8);
    }
    .optional-layers-wrapper {
        position: absolute;
        top: 70px;
        left: 10px;
    }
    .optional-layers-button {
        position: relative;
        z-index: 400;
        background: white;
        border-radius: 2px;
        border: 3px solid rgba(5, 5, 5, .1);
        margin-bottom: 2px;
        cursor: pointer;
        display: block;
    }
    .layer_options {
        position: absolute;
        max-height: 400px;
        overflow-y: auto;
        top: 0;
        left: 0;
        z-index: 410;
        background: white;
        border-radius: 2px;
        cursor: auto;
        min-width: max-content;
        /*
        box-shadow: 3px 3px 3px #777;
        -moz-filter: brightness(1.0);
        -webkit-filter: brightness(1.0);
        */
        padding: 0.5em;
        border: 3px solid rgba(5, 5, 5, .1);
    }
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
    .ol-layer canvas {
        transform: none !important;
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
    .table_caption {
        color: green;
    }
    .layer_option:hover {
        cursor: pointer;
    }
    .filter_search_wrapper {
        position: relative;
        z-index: 1100;
    }
    .button_row {
        display: flex;
        justify-content: flex-end;
    }
    .view_all_button {
        color: #03a9f4;
        cursor: pointer;
    }
    .sub_option {
        margin-left: 1em;
    }
    .spinner_on_map {
        position: absolute;
        top: 10%;
        left: 50%;
        z-index: 100000;
    }
    .map {
        width: 100%;
        height: 500px;
    }
    .custom-mouse-position {
        position: absolute;
        left: 20px;
        bottom: 10px;
        z-index: 450;
        background: rgba(90, 90, 90, 0.9);
        color: #fff;
        padding: 4px 8px;
        border-radius: 3px;
        font-size: 12px;
        font-weight: 600;
        line-height: 1.2;
        pointer-events: none;
    }
</style>

<style>
</style>
