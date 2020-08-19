<template lang="html">
    <div>

        <div class="row col-sm-12">
            <div class="form-group">
                <label class="inline">Title:</label>
                <input
                    type="text"
                    class="form-control"
                    v-model="proposal.proposal_apiary.title"
                    :readonly="readonly"
                    style="width: 100%;"
                />
            </div>
        </div>

        <div class="row col-sm-12">
            Mark the location of the new proposed site either by entering the latitude and longitude or by clicking the location in the map.
        </div>

        <div class="row">
            <div class="col-sm-4">
                <div class="form-group">
                    <label class="inline">Latitude:</label>
                    <input
                        type="number"
                        min="-90"
                        max="90"
                        class="form-control"
                        v-model.number="proposal.proposal_apiary.latitude"
                        :readonly="readonly"
                    />
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-sm-4">
                <div class="form-group">
                    <label class="inline">Longitude:</label>
                    <input
                        type="number"
                        min="-180"
                        max="180"
                        class="form-control"
                        v-model.number="proposal.proposal_apiary.longitude"
                        :readonly="readonly"
                    />
                    <template v-if="!readonly">
                        <input type="button" @click="tryCreateNewSiteFromForm" value="Add proposed site" class="btn btn-primary" style="margin: 1em 0 0 0;">
                    </template>
                </div>
            </div>
        </div>

        <template v-if="proposal && proposal.proposal_apiary">
            <div class="row debug-info">
                <div class="col-sm-12">
                    <div>
                        Category:
                        <select v-model="current_category" class="form-group">
                            <option value="south_west">South West</option>
                            <option value="remote">Remote</option>
                        </select>
                    </div>

                    Remainders:
                    <div v-for="remainder in proposal.proposal_apiary.site_remainders" class="debug-remainders">
                        <div>
                            {{ remainder.category_name }}: {{ remainder.remainders }} left (${{ remainder.fee }}/site)
                        </div>
                    </div>
                </div>
            </div>
        </template>

        <div class="row col-sm-12">
            <datatable ref="site_locations_table" id="site-locations-table" :dtOptions="dtOptions" :dtHeaders="dtHeaders" />
            <span class="view_all_button action_link" @click="displayAllFeatures">View All Proposed Sites On Map</span>
        </div>

        <div id="map" class="map"></div>

        <div :id="popup_id" class="ol-popup">
            <!--
            <a href="#" :id="popup_closer_id" class="ol-popup-closer"></a>
            -->
            <div :id="popup_content_id" class="text-center"></div>
        </div>


        <div class="row col-sm-12">
            <label>
                Click <a @click="existingSiteAvailableClicked">here</a> if you are interested in existing sites that are available by the site licence holder.
            </label>
        </div>

    </div>
</template>

<script>
    import 'ol/ol.css';
    //import 'index.css';  // copy-and-pasted the contents of this file at the <style> section below in this file
    import Map from 'ol/Map';
    import View from 'ol/View';
    import WMTSCapabilities from 'ol/format/WMTSCapabilities';
    import TileLayer from 'ol/layer/Tile';
    import OSM from 'ol/source/OSM';
    import WMTS, {optionsFromCapabilities} from 'ol/source/WMTS';
    import Collection from 'ol/Collection';
    import {Draw, Modify, Snap, Select} from 'ol/interaction';
    import {pointerMove} from 'ol/events/condition';
    import VectorLayer from 'ol/layer/Vector';
    import VectorSource from 'ol/source/Vector'; 
    import {Circle as CircleStyle, Fill, Stroke, Style, Icon} from 'ol/style';
    import {FullScreen as FullScreenControl, MousePosition as MousePositionControl} from 'ol/control';
    import Vue from 'vue/dist/vue';
    import { Feature } from 'ol';
    import { Point } from 'ol/geom';
    import { getDistance } from 'ol/sphere';
    import { circular} from 'ol/geom/Polygon';
    import GeoJSON from 'ol/format/GeoJSON';
    import TextField from '@/components/forms/text.vue'
    import datatable from '@vue-utils/datatable.vue'
    import uuid from 'uuid';
    import { getApiaryFeatureStyle, drawingSiteRadius } from '@/components/common/apiary/site_colours.js'
    import Overlay from 'ol/Overlay';

    export default {
        props:{
            proposal:{
                type: Object,
                required:true
            },
            canEditActivities:{
              type: Boolean,
              default: true
            },
            is_external:{
              type: Boolean,
              default: false
            },
            is_internal:{
              type: Boolean,
              default: false
            },
            is_referral:{
              type: Boolean,
              default: false
            },
            hasReferralMode:{
                type:Boolean,
                default: false
            },
            hasAssessorMode:{
                type:Boolean,
                default: false
            },
            referral:{
                type: Object,
                required:false
            },
            proposal_parks:{
                type:Object,
                default:null
            },
        },
        data:function () {
            let vm=this;
            return{
                current_category: 'south_west',
                q: null,
                values:null,
                showingHelpText: false,
                help_text: 'My Help text ...',
                marker_lng: null,
                marker_lat: null,
                deed_poll_url: '',
                buffer_radius: 3000, // [m]

                // Popup
                popup_id: uuid(),
                //popup_closer_id: uuid(),
                popup_content_id: uuid(),
                content_element: null,
                overlay: null,

                // variables for the GIS
                map: null,
                apiarySitesQuerySource: new VectorSource(),
                apiarySitesQueryLayer: null,
                bufferedSites: null,
                drawingLayerSource:  new VectorSource(),
                drawingLayer: null,
                bufferLayerSource: new VectorSource(),
                bufferLayer: null,
                existing_sites_feature_collection: null,
                apiary_site_being_selected: null,
                swZoneSource: null,
                //
                dtHeaders: [
                    'Id',
                    'Latitude',
                    'Longitude',
                    'Action',
                ],
                dtOptions: {
                    serverSide: false,
                    searchDelay: 1000,
                    lengthMenu: [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
                    order: [
                        [0, 'desc']
                    ],
                    language: {
                        processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                    },
                    responsive: true,
                    processing: true,
                    columns: [
                        {
                            visible: false,
                            mRender: function (data, type, full) {
                                if (full.id) {
                                    return full.id;
                                } else {
                                    return '';
                                }
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                let coords = full.getGeometry().getCoordinates()
                                return Number.parseFloat(coords[1]).toFixed(6)
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                let coords = full.getGeometry().getCoordinates()
                                return Number.parseFloat(coords[0]).toFixed(6)
                            }
                        },
                        {
                            mRender: function (data, type, feature) {
                                let action_list = []
                                let ret_str_delete = '<span class="delete_button action_link" data-site-location-guid="' + feature.getId() + '">Delete</span>'
                                let ret_str_view = '<span class="view_on_map action_link" data-apiary-site-id="' + feature.getId() + '"/>View on map</span>';

                                let status = feature.get('status')
                                console.log(status)

                                action_list.push(ret_str_view)
                                if (!vm.readonly){
                                    action_list.push(ret_str_delete)
                                }
                                return action_list.join('<br />');
                            }
                        },
                    ],
                },
            }
        },
        components: {
            TextField,
            datatable,
        },
        computed:{
            readonly: function() {
                let readonlyStatus = true;
                if (this.proposal.customer_status === 'Draft' && !this.is_internal) {
                    readonlyStatus = false;
                }
                return readonlyStatus;
            },
        },
        watch:{
            apiary_site_being_selected: function() {
                console.log(this.apiary_site_being_selected);
                if (this.apiary_site_being_selected){
                    this.showPopup(this.apiary_site_being_selected)
                } else {
                    this.closePopup()
                }
            }
        },
        methods:{
            showPopup: function(feature){
                console.log('** showPopup **')
                let geometry = feature.getGeometry();
                let coord = geometry.getCoordinates();
                console.log(coord)
                //let svg_hexa = "<svg xmlns='http://www.w3.org/2000/svg' version='1.1' height='20' width='15'>" + 
                //'<g transform="translate(0, 4) scale(0.9)"><path d="M 14.3395,12.64426 7.5609998,16.557828 0.78249996,12.64426 0.7825,4.8171222 7.5609999,0.90355349 14.3395,4.8171223 Z" id="path837" style="fill:none;stroke:#ffffff;stroke-width:1.565;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1" /></g></svg>'
                let content = 'vacant'
                this.content_element.innerHTML = content;
                this.overlay.setPosition(coord);
            },
            closePopup: function(){
                this.overlay.setPosition(undefined)
                //closer.blur()
                return false
            },
            displayAllFeatures: function() {
                if (this.map){
                    if (this.drawingLayerSource.getFeatures().length>0){
                        let view = this.map.getView()

                        let ext = this.drawingLayerSource.getExtent()
                        let centre = [(ext[0] + ext[2])/2.0, (ext[1] + ext[3])/2.0]
                        let resolution = view.getResolutionForExtent(ext);
                        let z = view.getZoomForResolution(resolution) - 1
                        view.animate({zoom: z, center: centre})
                    }
                }
            },
            zoomToApiarySiteById: function(apiary_site_id){
                console.log(apiary_site_id)
                let feature = this.drawingLayerSource.getFeatureById(apiary_site_id)
                let geometry = feature.getGeometry()
                let coord = geometry.getCoordinates()
                let view = this.map.getView()
                this.map.getView().animate({zoom: 16, center: feature['values_']['geometry']['flatCoordinates']})
                //this.showPopup(feature)
            },
            uuidv4: function () {
                return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, 
                    function(c) {
                        return (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16);
                    }
                );
            },
            getDegrees: function(coords){
                return coords[0].toFixed(6) + ', ' + coords[1].toFixed(6);
            },
            metersToNearest: function(coords, filter) {
                // Infinity is the distance to the nearest apiary_site as default
                // Which means we it is fine to put apiary_site at the coords
                let candidates = [Number.POSITIVE_INFINITY];

                // Retrieve the nearest apiary site from the drawingLayerSource
                let nearestDrawnSite = this.drawingLayerSource.getClosestFeatureToCoordinate(coords, filter);
                if (nearestDrawnSite != null) {
                    candidates.push(getDistance(coords, nearestDrawnSite.getGeometry().getCoordinates()));
                }

                // Retrieve the nearest apiary site from the existing apiary_sites
                let nearestQuerySite = this.apiarySitesQuerySource.getClosestFeatureToCoordinate(coords, filter);
                if (nearestQuerySite != null) {
                    candidates.push(getDistance(coords, nearestQuerySite.getGeometry().getCoordinates()));
                }

                let min = candidates[0];
                for (let i = 1; i < candidates.length; i++) {
                    // Ignore NaN
                    if (!isNaN(candidates[i])){
                        min = Math.min(min, candidates[i]);
                    }
                }
                return min;
            },
            isNewPositionValid: function(coords, filter=null){
                let distance = this.metersToNearest(coords, filter);
                if (distance < this.buffer_radius) {
                    return false;
                }
                return true;
            },
            zoneForCoordinates: function(coords){
                let zone = "remote";
                this.swZoneSource.getFeaturesAtCoordinate(coords).forEach(function(feat) {
                    zone = "south_west";
                });
                return zone;
            },
            createBufferForSite: function(site){
                let id = site.getId() + "_buffer";
                let coords = site.getGeometry().getCoordinates();

                // apiary from json had 2d coords packed in an inner array.
                if (coords.length == 1){
                    coords = coords[0];
                }

                let buffer = new Feature(circular(coords, this.buffer_radius, 16));
                buffer.setId(id)
                this.bufferLayerSource.addFeature(buffer);
            },
            removeBufferForSite: function(site){
                let buffer = this.bufferLayerSource.getFeatureById(site.getId() + "_buffer");
                this.bufferLayerSource.removeFeature(buffer);
            },
            apiaryStyleFunction: function(feature) {
                var status = feature.get("status");
                return getApiaryFeatureStyle(status);
            },
            existingSiteAvailableClicked: function() {
                alert("TODO: open screen 45: External - Contact Holder of Available Site in a different tab page.");
            },
            calculateRemainders: function(features){
                let remainders = null;
                if (this.proposal.application_type === 'Apiary' && this.proposal.proposal_type === 'renewal') {
                    remainders = this.proposal.proposal_apiary.renewal_site_remainders;
                } else {
                    remainders = this.proposal.proposal_apiary.site_remainders;
                }
                let num_remain_south_west = 0
                let num_remain_remote = 0

                for (let i=0; i<remainders.length; i++){
                    if (remainders[i].category_name == 'South West'){
                        num_remain_south_west = remainders[i].remainders
                    } else if (remainders[i].category_name == 'Remote'){
                        num_remain_remote = remainders[i].remainders
                    } else {
                        console.log('should not reach here')
                    }
                }

                for (let i=0; i<features.length; i++){
                    console.log(features[i].get('site_category'))
                    if (features[i].get('site_category') == 'south_west'){
                        num_remain_south_west = num_remain_south_west - 1
                    } else if (features[i].get('site_category') == 'remote'){
                        num_remain_remote = num_remain_remote - 1
                    }
                }
                console.log(num_remain_south_west)
                console.log(num_remain_remote)

                let button_text = 'Pay and submit'
                // TODO: improve this logic
                if (num_remain_south_west >= 0 && num_remain_remote >=0 && !this.proposal.proposal_type === 'renewal'){
                    button_text = 'Submit'
                }

                this.$emit('button_text', button_text)
            },
            constructSiteLocationsTable: function(){

                if (this.drawingLayerSource){
                    // Clear table
                    this.$refs.site_locations_table.vmDataTable.clear().draw();

                    // Get all the features drawn
                    let features = this.drawingLayerSource.getFeatures()

                    // Insert data into the table
                    for(let i=0; i<features.length; i++){
                        this.$refs.site_locations_table.vmDataTable.row.add(features[i]).draw();
                    }

                    this.calculateRemainders(features)
                }
                // Update proposal obj, which is sent to the server when save/submit.
                //this.proposal.proposal_apiary.apiary_sites = features
                //this.updateApiarySitesData()
            },
            getFeatures: function() {
                let allFeatures = this.drawingLayerSource.getFeatures()
                return allFeatures
            },
            addEventListeners: function(){
                $("#site-locations-table").on("click", ".delete_button", this.removeSiteLocation);
                $("#site-locations-table").on("click", ".view_on_map", this.zoomOnApiarySite)
            },
            zoomOnApiarySite: function(e) {
                let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                this.zoomToApiarySiteById(apiary_site_id)
            },
            removeSiteLocation: function(e){
                let site_location_guid = e.target.getAttribute("data-site-location-guid");
                let myFeature = this.drawingLayerSource.getFeatureById(site_location_guid)

                let myFeatureStatus = myFeature.get('status')
                if (myFeatureStatus && myFeatureStatus != 'draft'){
                    this.drawingLayerSource.removeFeature(myFeature);
                } else {
                    // Remove buffer
                    this.removeBufferForSite(myFeature)
                    this.drawingLayerSource.removeFeature(myFeature);
                }

                // Remove the row from the table
                $(e.target).closest('tr').fadeOut('slow', function(){ })
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
                    target: 'map',
                    view: new View({
                        center: [115.95, -31.95],
                        zoom: 7,
                        projection: 'EPSG:4326'
                    })
                });
                vm.apiarySitesQueryLayer = new VectorLayer({
                    source: vm.apiarySitesQuerySource,
                    style: vm.apiaryStyleFunction,
                });
                vm.map.addLayer(vm.apiarySitesQueryLayer);

                vm.bufferedSites = [];
                vm.map.on("moveend", function(attributes){
                    let zoom = vm.map.getView().getZoom();
                    if (zoom < 11) {
                        return;
                    }

                    let fresh = 0;
                    let cached = 0;

                    vm.apiarySitesQuerySource.forEachFeatureInExtent(vm.map.getView().calculateExtent(), function(feature) {
                        let id = feature.getId();
                        if (vm.bufferedSites.indexOf(id) == -1) {
                            vm.createBufferForSite(feature);
                            vm.bufferedSites.push(id);
                            fresh++;
                        }
                        else {
                            cached++;
                        }
                    });
                });

                // In memory vector layer for digitization
                //vm.drawingLayerSource = new VectorSource();
                vm.drawingLayerSource.on('addfeature', function(e){
                    //vm.proposal.proposal_apiary.apiary_sites.push(e.feature)
                    vm.constructSiteLocationsTable()
                });
                vm.drawingLayer = new VectorLayer({
                    source: vm.drawingLayerSource,
                    style: new Style({
                        fill: new Fill({
                            color: 'rgba(255, 255, 255, 0.2)'
                        }),
                        stroke: new Stroke({
                            color: '#ffcc33',
                            width: 2
                        }),
                        image: new CircleStyle({
                            radius: drawingSiteRadius,
                            fill: new Fill({
                                color: '#ffcc33'
                            })
                        })
                    })
                });
                vm.map.addLayer(vm.drawingLayer);

                let container = document.getElementById(vm.popup_id)
                vm.content_element = document.getElementById(vm.popup_content_id)
                //let closer = document.getElementById(vm.popup_closer_id)
                vm.overlay = new Overlay({
                    element: container,
                    autoPan: false,
                    offest: [0, -10]
                })
                //closer.onclick = function() {
                //    vm.overlay.setPosition(undefined)
                //    closer.blur()
                //    return false
                //}
                vm.map.addOverlay(vm.overlay)

                //vm.bufferLayerSource = new VectorSource();
                vm.bufferLayer = new VectorLayer({
                    source: vm.bufferLayerSource,
                    minZoom: 11,

                });
                vm.map.addLayer(vm.bufferLayer);

                vm.swZoneSource = new VectorSource({
                    url: "/static/disturbance/gis/sw_apiary_zone.geojson",
                    format: new GeoJSON(),
                });
                // a visible layer is required to trigger loading the data, the empty style will mean that the features are not drawn
                let swZoneLayer = new VectorLayer({
                    source: vm.swZoneSource,
                    style: new Style(),
                    visible: true,
                });
                vm.map.addLayer(swZoneLayer);

                // Full screen toggle
                vm.map.addControl(new FullScreenControl());

                // Show mouse coordinates
                vm.map.addControl(new MousePositionControl({
                    coordinateFormat: function(coords){
                        let message = vm.getDegrees(coords) + "\n";
                        let distance = vm.metersToNearest(coords, null);
                        if (distance < Number.POSITIVE_INFINITY) {
                            message += "<br>Nearest: "  + (distance / 1000).toFixed(2) + " km";
                        }
                        return  message;
                    },
                    target: document.getElementById('mouse-position'),
                    className: 'custom-mouse-position',
                }));

                // Draw and modify tools
                if (!vm.readonly){
                    let modifyInProgressList = [];
                    let drawTool = new Draw({
                        source: vm.drawingLayerSource,
                        type: "Point"
                    });
                    drawTool.on("drawstart", function(attributes){
                        if (vm.apiary_site_being_selected){
                            // Abort drawing, instead 'vacant' site is to be added
                            drawTool.abortDrawing();
                            // Copy the 'id_' attribute, which should have the apiary_site.id in the database, to the 'id' attribute
                            // This 'id' attribute is used to determine if it exists already in the database once posted.
                            //vm.apiary_site_being_selected.id = vm.apiary_site_being_selected.id_
                            vm.drawingLayerSource.addFeature(vm.apiary_site_being_selected);
                            vm.apiary_site_being_selected.getGeometry().on("change", function() {
                                if (modifyInProgressList.indexOf(vm.apiary_site_being_selected.getId()) == -1) {
                                    modifyInProgressList.push(vm.apiary_site_being_selected.getId());
                                }
                            });
                        } else {
                            if (!vm.isNewPositionValid(attributes.feature.getGeometry().getCoordinates())) {
                                drawTool.abortDrawing();
                            }
                        }
                    });
                    drawTool.on('drawend', function(attributes){
                        if (!this.readoly){
                            let feature = attributes.feature;
                            let draw_id = vm.uuidv4();
                            let draw_coords = feature.getGeometry().getCoordinates();
                            feature.setId(draw_id);
                            feature.set("source", "draw");
                            feature.set("stable_coords", draw_coords);
                            feature.set('site_category', vm.zoneForCoordinates(draw_coords));
                            feature.getGeometry().on("change", function() {
                                if (modifyInProgressList.indexOf(draw_id) == -1) {
                                    modifyInProgressList.push(draw_id);
                                }
                            });
                            vm.createBufferForSite(feature);
                            // Vue table is updated by the event 'addfeature' issued from the Source
                        }
                    });
                    vm.map.addInteraction(drawTool);

                    let modifyTool = new Modify({
                        source: vm.drawingLayerSource,
                        condition: function(e){
                            return true
                        }
                    });
                    modifyTool.on("modifystart", function(attributes){
                        attributes.features.forEach(function(feature){
                        })
                    });
                    modifyTool.on("modifyend", function(attributes){
                        // this will list all features in layer, not so useful without cross referencing
                        attributes.features.forEach(function(feature){
                            let id = feature.getId();
                            let index = modifyInProgressList.indexOf(id);
                            if (index != -1) {
                                modifyInProgressList.splice(index, 1);
                                let coords = feature.getGeometry().getCoordinates();
                                let filter = vm.excludeFeature(feature);
                                let valid = vm.isNewPositionValid(coords, filter);
                                if (!valid || feature.get('status')==='vacant') {
                                    // rollback proposed modification
                                    let c = feature.get("stable_coords");
                                    feature.getGeometry().setCoordinates(c);
                                    // setting coords will add the id to the modification list again, we don't need that so clear it now
                                    index = modifyInProgressList.indexOf(id);
                                    modifyInProgressList.splice(index, 1);
                                }
                                else {
                                    // confirm proposed modification
                                    feature.set("stable_coords", coords);
                                    vm.removeBufferForSite(feature);
                                    vm.createBufferForSite(feature);
                                    feature.set('site_category', vm.zoneForCoordinates(coords));
                                    vm.constructSiteLocationsTable();
                                }
                            }
                        });
                    });
                    vm.map.addInteraction(modifyTool);
                }

                /////////////////////
                // Test
                ////////////////////
                let hoverInteraction = new Select({
                    condition: pointerMove,
                    //condition: function(e){
                    //    return true
                    //},
                    layers: [vm.apiarySitesQueryLayer]
                });
                vm.map.addInteraction(hoverInteraction);
                hoverInteraction.on('select', function(evt){
                    if(evt.selected.length > 0){
                        if(evt.selected[0].get('status') === 'vacant'){
                            // When mouse hover on the 'vacant' apiary site, temporarily store it 
                            // so that it can be added to the new apiary site application when user clicking.
                            vm.apiary_site_being_selected = evt.selected[0]

                            let style_applied = getApiaryFeatureStyle(vm.apiary_site_being_selected.get('status'), true, 4)
                            vm.apiary_site_being_selected.setStyle(style_applied)
                        }
                    } else {
                        if (vm.apiary_site_being_selected){
                            let style_applied = getApiaryFeatureStyle(vm.apiary_site_being_selected.get('status'), false)
                            vm.apiary_site_being_selected.setStyle(style_applied)
                        }

                        vm.apiary_site_being_selected = null
                    }
                });
                //if(false){
                //    let snapInteraction = new Snap({
                //        source: vm.apiarySitesQuerySource
                //    })
                //    vm.map.addInteraction(snapInteraction);
                //}

                //let selected = null
                //vm.map.on('pointermove', function (e) {
                //    let pixel = vm.map.getEventPixel(e.originalEvent);
                //    //let hit = vm.map.hasFeatureAtPixel(pixel);
                //    let hit = vm.map.hasFeatureAtPixel(e.pixel, {
                //        layerFilter: function(layer) {
                //            if (layer === vm.apiarySitesQueryLayer){
                //                return true
                //            }
                //            return false
                //            //return layer.get('layer_name') === 'jls';
                //        }
                //    });

                //    if(hit){
                //        //console.log('hit')
                //    }


                //    if (selected !== null) {
                //        selected.setStyle(undefined);
                //        selected = null;
                //    }

                //    vm.map.forEachFeatureAtPixel(e.pixel, function (f, layer) {
                //        console.log(f.id)
                //        if (f.id){
                //            selected = f;
                //        }
                //        //f.setStyle(highlightStyle);
                //        return true;
                //    });

                //    if (selected) {
                //        console.log(selected)
                //    }
                //});

                //vm.map.on('click', function(evt){
                //    console.log('click')
                //    let feature = vm.map.forEachFeatureAtPixel(evt.pixel, function(feature, layer) {
                //        return feature;
                //    });
                //    if (feature){
                //        console.log(feature)
                //    }
                //})
                ////////////////////////
                // END TEST
                ////////////////////////

            },  // End: initMap()
            excludeFeature: function(excludedFeature) {
                return function(f) {
                    return excludedFeature.getId() != f.getId();
                };
            },
            tryCreateNewSiteFromForm: function(){
                let lat = this.proposal.proposal_apiary.latitude
                let lon = this.proposal.proposal_apiary.longitude
                let coords = [lon, lat];
                // rough bounding box for preliminary check
                if (isNaN(lon) || lon < 112 || lon > 130 ||
                    isNaN(lat) || lat < -35 || lat > -11) {
                    return false;
                }
                if(!this.isNewPositionValid(coords))
                {
                    return false;
                }
                
                let feature = new Feature(new Point(coords));
                feature.setId(this.uuidv4());
                feature.set("source", "form");
                feature.set('site_category', this.zoneForCoordinates(coords));
                this.drawingLayerSource.addFeature(feature);

                this.createBufferForSite(feature);
                return true;
            },
        },
        created: function() {
            let vm = this
            this.$http.get('/api/apiary_site/list_existing/?proposal_id=' + this.proposal.id)
            .then(
                res => {
                    vm.existing_sites_feature_collection = res.body
                    vm.apiarySitesQuerySource.addFeatures((new GeoJSON()).readFeatures(vm.existing_sites_feature_collection))
                },
                err => {

                }
            )
        },
        mounted: function() {
            let vm = this;

            this.$nextTick(() => {
                vm.initMap();
                vm.addEventListeners();
            });

            // Create feature and add it to the map, then reconstruct table
            // Don't forget add 'id' field to the feature which is used to determine if it is new feature or not

            for (let i=0; i<vm.proposal.proposal_apiary.apiary_sites.length; i++){
                 let apiary_site = vm.proposal.proposal_apiary.apiary_sites[i]

                 //let feature = new Feature(new Point([apiary_site.coordinates.lng, apiary_site.coordinates.lat]));
                 //feature.setId(apiary_site.site_guid);
                 //feature.id = apiary_site.id
                 //feature.set("source", "form");
                 //feature.set("site_category", apiary_site.site_category)
                 //this.drawingLayerSource.addFeature(feature);

                 let feature = (new GeoJSON).readFeature(apiary_site.as_geojson)
                 this.drawingLayerSource.addFeature(feature)

                 this.createBufferForSite(feature);
            }

            this.constructSiteLocationsTable();
        }
    }
</script>

<style lang="css">
    .delete_button {
        color: #337ab7 !important;
    }
    .section{
        text-transform: capitalize;
    }
    .list-group{
        margin-bottom: 0;
    }
    .fixed-top{
        position: fixed;
        top:56px;
    }
    .debug-info {
        background: #CCC;
        margin: 1em;
    }
    .debug-message {
        margin: 0 0 1em 0;
        padding: 0 0 0 1em
    }
    .debug-remainders {
        padding: 0 0 0 1em
    }
    .map {
        display: inline-block;
        width: 100%;
        height: 500px;
    }
    .custom-mouse-position {
        position: absolute;
        bottom: 16px;
        left: 16px;
        top: auto;
        right: auto;
        text-align: left;
        font-size: 0.8rem;
        border: 0;
        padding: 8px;
        color: white;
        background-color: rgba(37, 45, 51, 0.7);
    }
    .action_link {
        color: #347ab7; 
        cursor: pointer;
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
    /*
    .ol-popup-closer {
        text-decoration: none;
        position: absolute;
        top: 2px;
        right: 8px;
    }
    .ol-popup-closer:after {
        content: "✖";
    }
    */
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
</style>
