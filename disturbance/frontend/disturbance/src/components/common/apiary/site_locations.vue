<template lang="html">
    <div>

        <!-- div class="row col-sm-12">
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
        </div -->

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
                </div>
            </div>
            <template v-if="!readonly">
                <div class="col-sm-4">
                    <input type="button" @click="tryCreateNewSiteFromForm" value="Add proposed site" class="btn btn-primary" style="margin: 1em 0 0 0;">
                </div>
            </template>
        </div>

        <template v-if="display_debug_info && proposal && proposal.proposal_apiary">
            <div class="row debug-info">
                <div class="col-sm-12">
                    <div>
                        <div><strong>New</strong></div>
                        <div>
                            <div>Previously paid sites 'South West' region: {{ num_of_sites_remain_south_west }} (${{ fee_south_west }})</div>
                            <div>Total fee: {{ total_fee_south_west }}</div>
                        </div>
                        <div>
                            <div>Previously paid sites 'Remote' region: {{ num_of_sites_remain_remote }} (${{ fee_remote }})</div>
                            <div>Total fee: {{ total_fee_remote }}</div>
                        </div>
                        <div><strong>Renewal</strong></div>
                        <div>
                            <div>Previously paid sites 'South West' region: {{ num_of_sites_remain_south_west_renewal }} (${{ fee_south_west_renewal }})</div>
                            <div>Total fee: {{ total_fee_south_west_renewal }}</div>
                        </div>
                        <div>
                            <div>Previously paid sites 'Remote' region: {{ num_of_sites_remain_remote_renewal }} (${{ fee_remote_renewal }})</div>
                            <div>Total fee: {{ total_fee_remote_renewal }}</div>
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
                Click <a href="/external/available_sites/">here</a> if you are interested in existing sites that are available by the site licence holder.
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
    import { getStatusForColour, getApiaryFeatureStyle, drawingSiteRadius, existingSiteRadius, SiteColours } from '@/components/common/apiary/site_colours.js'
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
                min_num_of_sites_for_renewal: 5,
                min_num_of_sites_for_new: 5,
                existing_sites_loaded: false,
                style_for_vacant_selected: new Style({
                    image: new CircleStyle({
                        radius: existingSiteRadius,
                        fill: new Fill({
                            color: SiteColours.vacant.fill
                        }),
                        stroke: new Stroke({
                            color: SiteColours.vacant.stroke,
                            width: 4
                        })
                    })
                }),
                style_for_new_apiary_site: new Style({
                    image: new CircleStyle({
                        radius: existingSiteRadius,
                        fill: new Fill({
                            color: SiteColours.draft_external.fill
                        }),
                        stroke: new Stroke({
                            color: SiteColours.draft_external.stroke,
                            width: 2
                        })
                    })
                }),
                // Popup
                popup_id: uuid(),
                popup_content_id: uuid(),
                content_element: null,
                overlay: null,

                // Remainders base
                num_of_sites_remain_south_west_base: 0,
                num_of_sites_remain_south_west_renewal_base: 0,
                num_of_sites_remain_remote_base: 0,
                num_of_sites_remain_remote_renewal_base: 0,

                // Sites on the map
                num_of_sites_south_west_applied: 0,
                num_of_sites_south_west_renewal_applied: 0,
                num_of_sites_remote_applied: 0,
                num_of_sites_remote_renewal_applied: 0,

                // Fee
                fee_south_west: 0,
                fee_remote: 0,
                fee_south_west_renewal: 0,
                fee_remote_renewal: 0,

                // variables for the GIS
                map: null,
                apiarySitesQuerySource: new VectorSource(),
                apiarySitesQueryLayer: null,
                bufferedSites: null,
                drawingLayerSource:  new VectorSource(),
                drawingLayer: null,
                bufferLayerSource: new VectorSource(),
                bufferLayer: null,
                vacantLayerSource: new VectorSource(),
                vacantLayer: null,
                vacant_site_being_selected: null,
                swZoneSource: null,
                //
                dtHeaders: [
                    'Id',
                    'Latitude',
                    'Longitude',
                    'Category',
                    'Vacant',
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
                            // id
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
                            // Lat
                            mRender: function (data, type, full) {
                                let coords = full.getGeometry().getCoordinates()
                                return Number.parseFloat(coords[1]).toFixed(6)
                            }
                        },
                        {
                            // Lng
                            mRender: function (data, type, full) {
                                let coords = full.getGeometry().getCoordinates()
                                return Number.parseFloat(coords[0]).toFixed(6)
                            }
                        },
                        {
                            // Category
                            mRender: function (data, type, feature) {
                                let cat = feature.get('site_category')
                                if (cat){
                                    cat = cat.replace('_', ' ')
                                    return cat.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
                                } else {
                                    return '---'
                                }
                            }
                        },
                        {
                            // Vacant
                            mRender: function (data, type, feature) {
                                let my_status = feature.get('status')
                                let is_vacant = feature.get('is_vacant')
                                if(my_status === 'vacant' || is_vacant === true){
                                    // Once saved, 'vacant' site status gets 'draft' therefore we have to check another attribute 'is_vacant', too
                                    return '<i class="fa fa-check" aria-hidden="true"></i>'
                                }
                                return ''
                            }
                        },
                        {
                            // Action
                            mRender: function (data, type, feature) {
                                let action_list = []
                                let ret_str_delete = '<span class="delete_button action_link" data-site-location-guid="' + feature.getId() + '">Delete</span>'
                                let ret_str_view = '<span class="view_on_map action_link" data-apiary-site-id="' + feature.getId() + '"/>View on map</span>';

                                let status = feature.get('status')

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
            display_debug_info: function(){
                if (location.host === 'localhost:8071'){
                    return true
                }
                return false
            },
            is_proposal_type_new: function(){
                if (this.proposal_type_name === 'new'){
                    return true
                }
                return false
            },
            is_proposal_type_renewal: function(){
                if (this.proposal_type_name === 'renewal'){
                    return true
                }
                return false
            },
            proposal_type_name: function() {
                if (this.proposal.application_type === 'Apiary'){
                    if (this.proposal.proposal_type.toLowerCase() === 'renewal'){
                        return 'renewal'
                    } else {
                        return 'new'
                    }
                } else {
                    return '---'
                }
            },
            readonly: function() {
                let readonlyStatus = true;
                if (this.proposal.customer_status === 'Draft' && !this.is_internal) {
                    readonlyStatus = false;
                }
                return readonlyStatus;
            },

            // 1. South West
            // 1.1 New
            num_of_sites_remain_south_west: function(){
                // Number of sites paid left - number of sites to be applied
                let value = this.num_of_sites_remain_south_west_base - this.num_of_sites_south_west_applied
                value = value >= 0 ? value : 0
                return value
            },
            num_of_sites_south_west_after_deduction: function(){
                let value = this.num_of_sites_south_west_applied - this.num_of_sites_remain_south_west_base
                return value >= 0 ? value : 0
            },
            quotient_south_west: function(){
                return Math.floor(this.num_of_sites_south_west_after_deduction / this.min_num_of_sites_for_new)
            },
            remainder_south_west: function(){
                return this.num_of_sites_south_west_after_deduction % this.min_num_of_sites_for_new
            },
            num_of_sites_south_west_calculate: function(){
                let ret_value = this.quotient_south_west * this.min_num_of_sites_for_new
                if (this.remainder_south_west){
                    ret_value =  ret_value + this.min_num_of_sites_for_new
                }
                return ret_value
            },
            num_of_sites_south_west_to_add_as_remainder: function(){
                return this.num_of_sites_south_west_calculate - this.num_of_sites_south_west_after_deduction
            },
            total_fee_south_west: function() {
                let total_fee = this.num_of_sites_south_west_calculate * this.fee_south_west
                return total_fee
            },
            // 1.2 Renewal
            num_of_sites_remain_south_west_renewal: function(){
                // Number of sites paid left
                let value = this.num_of_sites_remain_south_west_renewal_base - this.num_of_sites_south_west_renewal_applied
                value = value >= 0 ? value : 0
                return value
            },
            num_of_sites_south_west_renewal_after_deduction: function(){
                let value = this.num_of_sites_south_west_renewal_applied - this.num_of_sites_remain_south_west_renewal_base
                return value >= 0 ? value : 0
            },
            quotient_south_west_renewal: function(){
                return Math.floor(this.num_of_sites_south_west_renewal_after_deduction / this.min_num_of_sites_for_renewal)
            },
            remainder_south_west_renewal: function(){
                return this.num_of_sites_south_west_renewal_after_deduction % this.min_num_of_sites_for_renewal
            },
            num_of_sites_south_west_renewal_calculate: function(){
                let ret_value = this.quotient_south_west_renewal * this.min_num_of_sites_for_renewal
                if (this.remainder_south_west_renewal){
                    ret_value =  ret_value + this.min_num_of_sites_for_renewal
                }
                return ret_value
            },
            num_of_sites_south_west_renewal_to_add_as_remainder: function(){
                return this.num_of_sites_south_west_renewal_calculate - this.num_of_sites_south_west_renewal_after_deduction
            },
            total_fee_south_west_renewal: function() {
                let total_fee = this.num_of_sites_south_west_renewal_calculate * this.fee_south_west_renewal
                return total_fee
            },

            // 2. Remote
            // 2.1 New
            num_of_sites_remain_remote: function(){
                let value = this.num_of_sites_remain_remote_base - this.num_of_sites_remote_applied
                value = value >= 0 ? value : 0
                return value
            },
            num_of_sites_remote_after_deduction: function(){
                let value = this.num_of_sites_remote_applied - this.num_of_sites_remain_remote_base
                return value >= 0 ? value : 0
            },
            quotient_remote: function(){
                return Math.floor(this.num_of_sites_remote_after_deduction / this.min_num_of_sites_for_new)
            },
            remainder_remote: function(){
                return this.num_of_sites_remote_after_deduction % this.min_num_of_sites_for_new
            },
            num_of_sites_remote_calculate: function(){
                let ret_value = this.quotient_remote * this.min_num_of_sites_for_new
                if (this.remainder_remote){
                    ret_value =  ret_value + this.min_num_of_sites_for_new
                }
                return ret_value
            },
            num_of_sites_remote_to_add_as_remainder: function(){
                return this.num_of_sites_remote_calculate - this.num_of_sites_remote_after_deduction
            },
            total_fee_remote: function() {
                let total_fee = this.num_of_sites_remote_calculate * this.fee_remote
                return total_fee
            },
            // 2.2 Renewal
            num_of_sites_remain_remote_renewal: function(){
                let value = this.num_of_sites_remain_remote_renewal_base - this.num_of_sites_remote_renewal_applied
                value = value >= 0 ? value : 0
                return value
            },
            num_of_sites_remote_renewal_after_deduction: function(){
                let value = this.num_of_sites_remote_renewal_applied - this.num_of_sites_remain_remote_renewal_base
                return value >= 0 ? value : 0
            },
            quotient_remote_renewal: function(){
                return Math.floor(this.num_of_sites_remote_renewal_after_deduction / this.min_num_of_sites_for_renewal)
            },
            remainder_remote_renewal: function(){
                return this.num_of_sites_remote_renewal_after_deduction % this.min_num_of_sites_for_renewal
            },
            num_of_sites_remote_renewal_calculate: function(){
                let ret_value = this.quotient_remote_renewal * this.min_num_of_sites_for_renewal
                if (this.remainder_remote_renewal){
                    ret_value =  ret_value + this.min_num_of_sites_for_renewal
                }
                return ret_value
            },
            num_of_sites_remote_renewal_to_add_as_remainder: function(){
                return this.num_of_sites_remote_renewal_calculate - this.num_of_sites_remote_renewal_after_deduction
            },
            total_fee_remote_renewal: function() {
                let total_fee = this.num_of_sites_remote_renewal_calculate * this.fee_remote_renewal
                return total_fee
            },
        },
        watch:{
            existing_sites_loaded: function() {
                if (this.existing_sites_loaded){
                    this.load_apiary_sites_in_this_proposal()
                    this.displayAllFeatures()
                }
            },
            num_of_sites_south_west_to_add_as_remainder: function(){
                this.$emit('num_of_sites_south_west_to_add_as_remainder', this.num_of_sites_south_west_to_add_as_remainder)
            },
            num_of_sites_remote_to_add_as_remainder: function(){
                this.$emit('num_of_sites_remote_to_add_as_remainder', this.num_of_sites_remote_to_add_as_remainder)
            },
            num_of_sites_south_west_renewal_to_add_as_remainder: function(){
                this.$emit('num_of_sites_south_west_renewal_to_add_as_remainder', this.num_of_sites_south_west_renewal_to_add_as_remainder)
            },
            num_of_sites_remote_renewal_to_add_as_remainder: function(){
                this.$emit('num_of_sites_remote_renewal_to_add_as_remainder', this.num_of_sites_remote_renewal_to_add_as_remainder)
            },
            num_of_sites_remain_south_west: function() {
                this.$emit('num_of_sites_remain_south_west', this.num_of_sites_remain_south_west)
            },
            num_of_sites_remain_remote: function() {
                this.$emit('num_of_sites_remain_remote', this.num_of_sites_remain_remote)
            },
            num_of_sites_remain_south_west_renewal: function() {
                this.$emit('num_of_sites_remain_south_west_renewal', this.num_of_sites_remain_south_west_renewal)
            },
            num_of_sites_remain_remote_renewal: function() {
                this.$emit('num_of_sites_remain_remote_renewal', this.num_of_sites_remain_remote_renewal)
            },
            total_fee_south_west: function(){
                this.$emit('total_fee_south_west', this.total_fee_south_west)
            },
            total_fee_south_west_renewal: function(){
                this.$emit('total_fee_south_west_renewal', this.total_fee_south_west_renewal)
            },
            total_fee_remote: function(){
                this.$emit('total_fee_remote', this.total_fee_remote)
            },
            total_fee_remote_renewal: function(){
                this.$emit('total_fee_remote_renewal', this.total_fee_remote_renewal)
            },
            vacant_site_being_selected: function() {
                if (this.vacant_site_being_selected){
                    this.showPopup(this.vacant_site_being_selected)
                } else {
                    this.closePopup()
                }
            }
        },
        methods:{
            load_apiary_sites_in_this_proposal: function(){
                // Load the apiary sites in this proposal on the map
                let vm = this
                for (let i=0; i<vm.proposal.proposal_apiary.apiary_sites.length; i++){
                     let apiary_site = vm.proposal.proposal_apiary.apiary_sites[i]

                    if (apiary_site.properties.status === 'vacant'){
                        // apiary_site is 'vacant' site
                        let feature = vm.apiarySitesQuerySource.getFeatureById(apiary_site.id)
                        // Set new attribute to apply a specific style for the 'vacant' selected site
                        feature.set('vacant_selected', true)

                        vm.drawingLayerSource.addFeature(feature);
                    } else {
                        let feature = (new GeoJSON).readFeature(apiary_site)
                        this.drawingLayerSource.addFeature(feature)
                        this.createBufferForSite(feature);
                    }
                }
                this.constructSiteLocationsTable();
            },
            is_feature_new_or_renewal: function(feature){
                if (feature.get('for_renewal')){
                    return 'renewal'
                } else {
                    return 'new'
                }
            },
            showPopup: function(feature){
                let geometry = feature.getGeometry();
                let coord = geometry.getCoordinates();
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
                let vm = this
                let distance = vm.metersToNearest(coords, filter);
                if (distance < vm.buffer_radius) {
                    return false
                }
                return true
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
                console.log('in removeBufferForSite')
                let buffer = this.bufferLayerSource.getFeatureById(site.getId() + "_buffer");
                if (buffer){
                    this.bufferLayerSource.removeFeature(buffer);
                }
            },
            apiaryStyleFunctionExisting: function(feature) {
                // This is used for the existing apiary sites
                //let status = this.get_status_for_colour(feature)
                let status = getStatusForColour(feature)
                return getApiaryFeatureStyle(status);
            },
            apiaryStyleFunctionProposed: function(feature){
                // This is used for the proposed apiary sites
                let vacant_selected = feature.get('vacant_selected')
                if (vacant_selected){
                    console.log('here1')
                    return this.style_for_vacant_selected
                } else {
                    return this.style_for_new_apiary_site
                }
            },
            existingSiteAvailableClicked: function() {
                alert("TODO: open screen 45: External - Contact Holder of Available Site in a different tab page.");
            },
            make_remainders_reactive: function(){
                let remainders = null;
                if (this.proposal.application_type === 'Apiary') {
                    remainders = this.proposal.proposal_apiary.site_remainders;
                }

                for (let i=0; i<remainders.length; i++){
                    if (remainders[i].category_name == 'South West'){
                        this.num_of_sites_remain_south_west_base = remainders[i].remainders
                        this.num_of_sites_remain_south_west_renewal_base = remainders[i].remainders_renewal
                        this.fee_south_west = remainders[i].fee
                        this.fee_south_west_renewal = remainders[i].fee_renewal
                    } else if (remainders[i].category_name == 'Remote'){
                        this.num_of_sites_remain_remote_base = remainders[i].remainders
                        this.num_of_sites_remain_remote_renewal_base = remainders[i].remainders_renewal
                        this.fee_remote = remainders[i].fee
                        this.fee_remote_renewal = remainders[i].fee_renewal
                    } else {
                        console.log('should not reach here')
                    }
                }
            },
            calculateRemainders: function(features){
                console.log('in calculateRemainders')
                let remainders = null;
                if (this.proposal.application_type === 'Apiary') {
                    remainders = this.proposal.proposal_apiary.site_remainders;
                }
                this.num_of_sites_south_west_applied = 0
                this.num_of_sites_remote_applied = 0
                this.num_of_sites_south_west_renewal_applied = 0
                this.num_of_sites_remote_renewal_applied = 0

                for (let i=0; i<features.length; i++){
                    console.log(features[i])
                    let new_or_renewal = this.is_feature_new_or_renewal(features[i])
                    let site_status = features[i].get('status')
                    let site_category = features[i].get('site_category')
                    let application_fee_paid = features[i].get('application_fee_paid')

                    if (application_fee_paid){
                        console.log('1')
                        // For this apiary site, application fee has been already paid
                        // We should ignore this site interms of the calculation for the remainders and fees
                    } else {
                        console.log('2')
                        if (site_status === 'vacant'){
                            if (site_category == 'south_west'){
                                console.log('vacant south_west')
                                this.num_of_sites_south_west_applied += 1
                            } else if (site_category == 'remote'){
                                console.log('vacant remote')
                                this.num_of_sites_remote_applied += 1
                            }
                        } else {
                            if (new_or_renewal === 'renewal'){
                                if (site_category == 'south_west'){
                                    console.log('renewal south_west')
                                    this.num_of_sites_south_west_renewal_applied += 1
                                } else if (site_category == 'remote'){
                                    console.log('renewal remote')
                                    this.num_of_sites_remote_renewal_applied += 1
                                }
                            }
                            if (new_or_renewal === 'new'){
                                if (site_category == 'south_west'){
                                    console.log('new south_west')
                                    this.num_of_sites_south_west_applied += 1
                                } else if (site_category == 'remote'){
                                    console.log('new remote')
                                    this.num_of_sites_remote_applied += 1
                                }
                            }
                        }
                    }
                }

                let button_text = 'Pay and Submit'
                // TODO: improve this logic
                if (this.num_of_sites_remain_south_west >= 0 && this.num_of_sites_remain_remote >=0 && !this.proposal.proposal_type === 'renewal'){
                    button_text = 'Submit'
                }

                this.$emit('button_text', button_text)
            },
            constructSiteLocationsTable: function(){
                console.log('in constructSiteLocationsTable')
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
            removeApiarySiteById: function(apiary_site_id){
                console.log('in removeApiarySiteById')
                let myFeature = this.drawingLayerSource.getFeatureById(apiary_site_id)
                this.deleteApiarySite(myFeature)
                this.constructSiteLocationsTable()
            },
            deleteApiarySite: function(myFeature){
                let site_category = myFeature.get('site_category')
                let application_fee_paid = myFeature.get('application_fee_paid')
                let new_or_renewal = this.is_feature_new_or_renewal(myFeature)

                if (application_fee_paid){
                    // For this apiary site, application fee has been already paid
                    // We should ignore this site interms of the calculation for the remainders and fees
                } else {
                    if (new_or_renewal === 'new'){
                        if (site_category === 'south_west'){
                            this.num_of_sites_south_west_applied -= 1
                        } else {
                            this.num_of_sites_remote_applied -= 1
                        }
                    }
                    if (new_or_renewal === 'renewal'){
                        if (site_category === 'south_west'){
                            this.num_of_sites_south_west_renewal_applied -= 1
                        } else {
                            this.num_of_sites_remote_renewal_applied -= 1
                        }
                    }
                }

                let myFeatureStatus = myFeature.get('status')
                if (myFeatureStatus && myFeatureStatus != 'draft'){
                    this.drawingLayerSource.removeFeature(myFeature);
                } else {
                    // Remove buffer
                    this.removeBufferForSite(myFeature)
                    this.drawingLayerSource.removeFeature(myFeature);
                }
                // Remove vacant_selected attribute from the feature
                myFeature.unset('vacant_selected')
                //let status = this.get_status_for_colour(myFeature)
                let status = getStatusForColour(myFeature)
                let style_applied = getApiaryFeatureStyle(status)
                myFeature.setStyle(style_applied)

                // Remove the row from the table
                //$(e.target).closest('tr').fadeOut('slow', function(){ })
            },
            removeSiteLocation: function(e){
                console.log('in removeSiteLocation')
                let site_location_guid = e.target.getAttribute("data-site-location-guid");
                let myFeature = this.drawingLayerSource.getFeatureById(site_location_guid)
                this.deleteApiarySite(myFeature)

                // Remove the row from the table
                $(e.target).closest('tr').fadeOut('slow', function(){ })
            },
            initMap: async function() {
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
                    style: vm.apiaryStyleFunctionExisting,
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
                vm.drawingLayerSource.on('addfeature', async function(e){
                    let coords = e.feature.getGeometry().getCoordinates()
                    let ret = await vm.$http.get('/gisdata/?layer=wa_coast_smoothed&lat=' + coords[1] + '&lng=' + coords[0])
                    if(!ret.body.hasOwnProperty('id')){
                        vm.removeBufferForSite(e.feature)
                        vm.drawingLayerSource.removeFeature(e.feature);
                    }
                    vm.constructSiteLocationsTable()
                });
                vm.drawingLayer = new VectorLayer({
                    source: vm.drawingLayerSource,
                    style: vm.apiaryStyleFunctionProposed,
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
                        type: "Point",
                    });
                    drawTool.on("drawstart", async function(attributes){
                        console.log('in drawstart')

                        let coords = attributes.feature.getGeometry().getCoordinates()

                        if (vm.vacant_site_being_selected){
                            console.log('vacant_site_being_selected')
                            console.log(vm.vacant_site_being_selected)
                            // Abort drawing, instead 'vacant' site is to be added
                            drawTool.abortDrawing();

                            vm.vacant_site_being_selected.set('vacant_selected', true)

                            vm.drawingLayerSource.addFeature(vm.vacant_site_being_selected);
                            vm.vacant_site_being_selected.getGeometry().on("change", function() {
                                if (modifyInProgressList.indexOf(vm.vacant_site_being_selected.getId()) == -1) {
                                    modifyInProgressList.push(vm.vacant_site_being_selected.getId());
                                }
                            });
                        } else {
                            let coords = attributes.feature.getGeometry().getCoordinates()
                            if (!vm.isNewPositionValid(coords)) {
                                drawTool.abortDrawing();
                            }
                        }
                    });
                    //drawTool.on('drawend', function(attributes){
                    drawTool.on('drawend', async function(attributes){
                        console.log('in drawend')
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

                    });
                    modifyTool.on("modifyend", function(attributes){
                        console.log('in modifyend')
                        // this will list all features in layer, not so useful without cross referencing
                        attributes.features.forEach(async function(feature){
                            console.log(feature)
                            let id = feature.getId();
                            let index = modifyInProgressList.indexOf(id);
                            if (index != -1) {
                                modifyInProgressList.splice(index, 1);
                                let coords = feature.getGeometry().getCoordinates();
                                let filter = vm.excludeFeature(feature);
                                let valid = vm.isNewPositionValid(coords, filter);

                                if (!valid || feature.get('is_vacant')===true) {
                                    console.log('in is_vacant==true')
                                    // rollback proposed modification
                                    let c = feature.get("stable_coords");
                                    feature.getGeometry().setCoordinates(c);
                                    // setting coords will add the id to the modification list again, we don't need that so clear it now
                                    index = modifyInProgressList.indexOf(id);
                                    modifyInProgressList.splice(index, 1);
                                }
                                else {
                                    let ret = await vm.$http.get('/gisdata/?layer=wa_coast_smoothed&lat=' + coords[1] + '&lng=' + coords[0])
                                    if(!ret.body.hasOwnProperty('id')){
                                        // rollback proposed modification
                                        let c = feature.get("stable_coords");
                                        feature.getGeometry().setCoordinates(c);
                                        // setting coords will add the id to the modification list again, we don't need that so clear it now
                                        index = modifyInProgressList.indexOf(id);
                                        modifyInProgressList.splice(index, 1);
                                    } else {
                                        // confirm proposed modification
                                        feature.set("stable_coords", coords);
                                        vm.removeBufferForSite(feature);
                                        vm.createBufferForSite(feature);
                                        feature.set('site_category', vm.zoneForCoordinates(coords));
                                        vm.constructSiteLocationsTable();
                                    }
                                }
                            }
                        });
                    });
                    vm.map.addInteraction(modifyTool);
                }

                let hoverInteraction = new Select({
                    condition: pointerMove,
                    layers: [vm.apiarySitesQueryLayer]
                });
                vm.map.addInteraction(hoverInteraction);
                hoverInteraction.on('select', function(evt){
                    if(evt.selected.length > 0){
                        // Mouse hover in
                        let is_vacant = evt.selected[0].get('is_vacant')
                        let making_payment = evt.selected[0].get('making_payment') || false
                        let status = evt.selected[0].get('status')

                        if(is_vacant && !making_payment && status != 'pending'){
                            // When mouse hover on the 'vacant' apiary site, temporarily store it
                            // so that it can be added to the new apiary site application when user clicking on it.
                            vm.vacant_site_being_selected = evt.selected[0]

                            // Thicken border when hover
                            let style_applied = getApiaryFeatureStyle(vm.vacant_site_being_selected.get('status'), true, 5)
                            vm.vacant_site_being_selected.setStyle(style_applied)
                        }
                        else {

                        }
                        if (vm.$route.query.debug === 'true'){
                            console.log(evt.selected[0])
                        }
                    } else {
                        // Mouse hover out
                        if (vm.vacant_site_being_selected){
                            //let status = vm.get_status_for_colour(vm.vacant_site_being_selected)
                            let status = getStatusForColour(vm.vacant_site_being_selected)
                            let style_applied = getApiaryFeatureStyle(status, false)

                            let vacant_selected = vm.vacant_site_being_selected.get('vacant_selected')
                            if (vacant_selected){
                                console.log('here2')
                                style_applied = vm.style_for_vacant_selected
                            }

                            vm.vacant_site_being_selected.setStyle(style_applied)
                        }

                        // Release feature
                        vm.vacant_site_being_selected = null
                    }
                });
            },  // End: initMap()
            //get_status_for_colour: function(feature){
            //    let status = feature.get("status");
            //    let is_vacant = feature.get('is_vacant')
            //    let making_payment = feature.get('making_payment')

            //    if (is_vacant){
            //        status = 'vacant'
            //    } else if (making_payment){
            //        status = 'making_payment'
            //    }
            //    return status
            //},
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
                    vm.apiarySitesQuerySource.addFeatures((new GeoJSON()).readFeatures(res.body))
                    vm.existing_sites_loaded = true
                },
                err => {

                }
            )
            this.make_remainders_reactive()
        },
        mounted: function() {
            let vm = this;
            this.$nextTick(() => {
                vm.initMap();
                vm.addEventListeners();
            });
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
