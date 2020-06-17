<template lang="html">
    <div>

            <span class="row col-sm-12">
                <input
                    type="text"
                    v-model="proposal.proposal_apiary.title"
                    :readonly="is_internal || !proposal.can_user_edit"
                />
            </span>

            <span class="row col-sm-12">
                Mark the location of the new proposed site either by entering the latitude and longitude or by clicking the location in the map.
            </span>

            <div class="row col-sm-12">
                <div class="col-sm-4 form-group">
                    <label class="inline">Latitude:</label>
                    <div v-if="true">
                        <input
                            type="number"
                            min="-90"
                            max="90"
                            class="form-control"
                            v-model.number="proposal.proposal_apiary.latitude"
                            :readonly="is_internal || !proposal.can_user_edit"
                        />
                    </div>
                </div>
            </div>

            <div class="row col-sm-12">
                <div class="col-sm-4 form-group">
                    <label class="inline">Longitude:</label>
                    <div v-if="true">
                        <input
                            type="number"
                            min="-180"
                            max="180"
                            class="form-control"
                            v-model.number="proposal.proposal_apiary.longitude"
                            :readonly="is_internal || !proposal.can_user_edit"
                        />
                        <input type="button" @click="tryCreateNewSiteFromForm" value="Add proposed site" class="btn btn-primary">
                    </div>
                </div>
            </div>

            <template v-if="proposal && proposal.proposal_apiary">
                <div class="row col-sm-12 debug-info">
                    How to set a site 'SouthWest'/'Remote':
                    <div class="debug-message">
                        <div>when latitude is more than or equal to 0, then the proposed site is regarded as 'SouthWest'</div>
                        <div>when latitude is less than 0, then the proposed site is regarded as 'Remote'</div>
                    </div>
                    Remainders:
                    <div v-for="remainder in proposal.proposal_apiary.site_remainders" class="debug-remainders">
                        <div>
                            {{ remainder.category_name }}: {{ remainder.remainders }} left (${{ remainder.fee }}/site)
                        </div>
                    </div>
                </div>
            </template>

            <div class="row col-sm-12">
                <datatable ref="site_locations_table" id="site-locations-table" :dtOptions="dtOptions" :dtHeaders="dtHeaders" />
            </div>

            <div id="map" class="map"></div>

            <!--
            <div class="row col-sm-12">
                <label>
                    Click <a @click="enlargeMapClicked">here</a> to enlarge map
                </label>
            </div>
            <div class="row col-sm-12">
                <label>
                    Click <a @click="existingSiteAvailableClicked">here</a> if you are interested in existing sites that are available by the site licence holder.
                </label>
            </div>
            -->

        <SiteLocationsModal ref="site_locations_modal" />

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

    import geo_data from "../../../assets/apiary_data.json"

    import TextField from '@/components/forms/text.vue'
    //import FileField from '@/components/forms/filefield.vue'
    import datatable from '@vue-utils/datatable.vue'
    import uuid from 'uuid';
    import SiteLocationsModal from './site_locations_modal';

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
                q: null,
                values:null,
                pBody: 'pBody'+vm._uid,
                showingHelpText: false,
                help_text: 'My Help text ...',
                marker_lng: null,
                marker_lat: null,
                site_locations: [],
                deed_poll_url: '',
                
                // variables for the GIS
                map: null,
                apiarySitesQuerySource: null,
                apiarySitesQueryLayer: null,
                bufferedSites: null,
                drawingLayerSource: null,
                drawingLayer: null,
                bufferLayerSource: null,
                bufferLayer: null,
                //

                dtHeaders: [
                    'id',
                    'guid',
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
                //    "id": '',
                //    "latitude": this.getDegrees(feature.getGeometry().getCoordinates()),
                //    "longitude": this.getDegrees(feature.getGeometry().getCoordinates()),
                //    "site_guid": feature.getId()
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
                                if (full.getId()) {
                                    //return full.site_guid;
                                    return full.getId();
                                } else {
                                    return '';
                                }
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                //return full.latitude;
                                return vm.getDegrees(full.getGeometry().getCoordinates())
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                //return full.longitude;
                                return vm.getDegrees(full.getGeometry().getCoordinates())
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                let ret_str = '<span class="delete_button" style="color:#347ab7; cursor: pointer;" data-site-location-guid="' + full.getId() + '">Delete</span>';
                                return ret_str;
                            }
                        },
                    ],
                },
            }
        },
        components: {
            TextField,
            //FileField,
            datatable,
            SiteLocationsModal,
        },
        computed:{
            readonly: function() {
                return false;
            },
        },
        watch:{

        },
        methods:{
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
                let candidates = [Number.POSITIVE_INFINITY];

                let nearestDrawnSite = this.drawingLayerSource.getClosestFeatureToCoordinate(coords, filter);
                if (nearestDrawnSite != null) {
                    candidates.push(getDistance(coords, nearestDrawnSite.getGeometry().getCoordinates()));
                }

                let nearestQuerySite = this.apiarySitesQuerySource.getClosestFeatureToCoordinate(coords, filter);
                if (nearestQuerySite != null) {
                    candidates.push(getDistance(coords, nearestQuerySite.getGeometry().getCoordinates()[0]));
                }

                let min = candidates[0];
                for (let i = 1; i < candidates.length; i++) {
                    min = Math.min(min, candidates[i]);
                }
                return min;
            },
            isNewPositionValid: function(coords){
                let distance = this.metersToNearest(coords, null);
                console.log(distance);
                if (distance < 3000) {
                    return false;
                }
                return true;
            },
            createBufferForSite: function(site){
                let id = site.getId() + "_buffer";
                let coords = site.getGeometry().getCoordinates();

                // apiary from json had 2d coords packed in an inner array.
                if (coords.length == 1){
                    coords = coords[0];
                }

                let buffer = new Feature(circular(coords, 3000, 16));
                this.bufferLayerSource.addFeature(buffer);
            },
            removeBufferForSite: function(site){
                let buffer = this.bufferLayerSource.getFeatureById(site.getId() + "_buffer");
                this.bufferLayerSource.removeFeature(buffer);
            },


            enlargeMapClicked: function() {
                console.log('enlargeMapClicked');
                this.$nextTick(() => {
                    this.$refs.site_locations_modal.isModalOpen = true;
                });
            },
            existingSiteAvailableClicked: function() {
                console.log('existingSiteAvailableClicked');
                alert("TODO: open screen 45: External - Contact Holder of Available Site in a different tab page.");
            },
            constructSiteLocationsTable: function(){
                // Clear table
                this.$refs.site_locations_table.vmDataTable.clear().draw();

                // Construct table
                if (this.site_locations.length > 0){
                    for(let i=0; i<this.site_locations.length; i++){
                        this.addSiteLocationToTable(this.site_locations[i]);
                    }
                }
            },
            addSiteLocationToTable: function(feature){
                console.log('*** addSiteLocationToTable ***');
                console.log(feature);
                this.$refs.site_locations_table.vmDataTable.row.add(feature).draw();
            },
           // addProposedSite: function(){
           //     console.log('in addProposedSite');
           //     this.site_locations.push({
           //         "id": '',
           //         "latitude": this.proposal.proposal_apiary.latitude,
           //         "longitude": this.proposal.proposal_apiary.longitude,
           //         "site_guid": uuid()
           //     });
           //     this.constructSiteLocationsTable();

           //     ///// test /////
           //     this.proposal.proposal_apiary.apiary_sites.push({
           //         "id": '',
           //         "latitude": this.proposal.proposal_apiary.latitude,
           //         "longitude": this.proposal.proposal_apiary.longitude,
           //         "site_guid": uuid()
           //     })
           //     ///// test /////
           // },
            addEventListeners: function(){
                $("#site-locations-table").on("click", ".delete_button", this.removeSiteLocation);
            },
            removeSiteLocation: function(e){
                let site_location_guid = e.target.getAttribute("data-site-location-guid");
                console.log('guid to delete');
                console.log(site_location_guid);

                let myFeature = this.drawingLayerSource.getFeatureById(site_location_guid)
                console.log('myFeature')
                console.log(myFeature)

                this.drawingLayerSource.removeFeature(myFeature);

                for (let i=0; i<this.site_locations.length; i++){
                    if (this.site_locations[i] == myFeature){
                        this.site_locations.splice(i, 1);
                    }
                }

                ///// test /////
                for (let i=0; i<this.proposal.proposal_apiary.apiary_sites.length; i++){
                    if (this.proposal.proposal_apiary.apiary_sites[i].site_guid == site_location_guid){
                        this.proposal.proposal_apiary.apiary_sites.splice(i, 1);
                    }
                }
                ///// test /////

                this.constructSiteLocationsTable();
            },
            initMap: function() {
                console.log('aho')
                console.log(geo_data)

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
                vm.apiarySitesQuerySource = new VectorSource({
                    features: (new GeoJSON()).readFeatures(geo_data)
                });
                console.log(vm.apiarySitesQuerySource);
                vm.apiarySitesQueryLayer = new VectorLayer({
                    source: vm.apiarySitesQuerySource,
                });
                console.log(vm.apiarySitesQueryLayer);
                vm.map.addLayer(vm.apiarySitesQueryLayer);

                vm.bufferedSites = [];
                vm.map.on("moveend", function(attributes){
                    let zoom = vm.map.getView().getZoom();
                    console.log(zoom);
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

                    console.log("zoom: " + zoom + ", fresh: " + fresh + ", cached: " + cached);
                });

                // In memory vector layer for digitization
                vm.drawingLayerSource = new VectorSource();
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
                            radius: 7,
                            fill: new Fill({
                                color: '#ffcc33'
                            })
                        })
                    })
                });
                vm.map.addLayer(vm.drawingLayer);

                // In memory vector layer for buffer

                vm.bufferLayerSource = new VectorSource();
                vm.bufferLayer = new VectorLayer({
                    source: vm.bufferLayerSource,
                    minZoom: 11,

                });
                vm.map.addLayer(vm.bufferLayer);

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
                }));

                // Draw and modify tools
                let modifyInProgressList = [];
                let drawTool = new Draw({
                    source: vm.drawingLayerSource,
                    type: "Point"
                });
                drawTool.on("drawstart", function(attributes){
                    if (!vm.isNewPositionValid(attributes.feature.getGeometry().getCoordinates())) {
                        drawTool.abortDrawing();
                    }
                });
                drawTool.on('drawend', function(attributes){
                    let feature = attributes.feature;
                    feature.setId(vm.uuidv4());
                    feature.set("source", "draw");
                    feature.getGeometry().on("change", function() {
                        console.log("Start Modify feature: " + feature.getId());
                        if (modifyInProgressList.indexOf(feature) < 0) {
                            modifyInProgressList.push(feature);
                        }
                    });
                    console.log("New Feature: " + feature.getId());
                    // update for individual feature, it is not in the layer collection yet. 
                    vm.updateVueFeature(feature);
                    vm.createBufferForSite(feature);
                });
                vm.map.addInteraction(drawTool);

                let modifyTool = new Modify({
                    source: vm.drawingLayerSource,
                });
                modifyTool.on("modifyend", function(attributes){
                    // this will list all features in layer, not so useful without cross referencing
                    attributes.features.forEach(function(feature){
                        let index = modifyInProgressList.indexOf(feature);
                        if (index > -1) {
                            console.log("End Modify Feature: " + index + "/" + modifyInProgressList.length + " " + feature.getId());
                            modifyInProgressList.splice(index, 1);
                            vm.updateVueFeature(feature);
                            vm.removeBufferForSite(feature);
                            vm.createBufferForSite(feature);
                        }
                    });
                });
                vm.map.addInteraction(modifyTool);



            },  // End: initMap()

            updateVueFeature: function(feature) {
                //app.$set(app.sites.items, feature.getId(), [feature.getId(), getDegrees(feature.getGeometry().getCoordinates()), feature.get("source")]);
                console.log('in updateVueFeature')
                console.log(feature)

                this.site_locations.push(feature);
                //this.site_locations.push({
                //    "id": '',
                //    "latitude": this.getDegrees(feature.getGeometry().getCoordinates()),
                //    "longitude": this.getDegrees(feature.getGeometry().getCoordinates()),
                //    "site_guid": feature.getId()
                //});
                this.constructSiteLocationsTable()
            },
            //deleteVueFeature: function(feature) {
            //    //app.$delete(app.sites.items, feature.getId());
            //    console.log('in deleteVueFeature')
            //    console.log(feature)
            //},
            tryCreateNewSiteFromForm: function()
            {
                console.log('in tryCreateNewSiteFromForm')
                let lat = this.proposal.proposal_apiary.latitude
                let lon = this.proposal.proposal_apiary.longitude
                // rough bounding box for preliminary check
                if (isNaN(lon) || lon < 112 || lon > 130 ||
                    isNaN(lat) || lat < -35 || lat > -11) {
                    return false;
                }
                if(!this.isNewPositionValid([lon,lat]))
                {
                    return false;
                }
                var feature = new Feature(new Point([lon,lat]));
                feature.setId(this.uuidv4());
                feature.set("source", "form");
                this.drawingLayerSource.addFeature(feature);
                this.createBufferForSite(feature);
                this.updateVueFeature(feature);
                return true;
            },
        },
        mounted: function() {
            let vm = this;

            vm.initMap();
            this.$nextTick(() => {
                vm.addEventListeners();
            });
            for(let i=0; i<this.proposal.proposal_apiary.apiary_sites.length; i++){
                let a_site = this.proposal.proposal_apiary.apiary_sites[i];
                a_site.longitude = 'retrieve from GIS server'
                a_site.latitude = 'retrieve from GIS server'
                this.site_locations.push(a_site);
            }
            this.constructSiteLocationsTable();
        }
    }
</script>

<style lang="css" scoped>
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
        padding: 1em;
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
    .ol-mouse-position {
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
</style>
