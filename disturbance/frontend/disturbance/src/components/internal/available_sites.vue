<template>
    <div class="container">
        <FormSection :formCollapse="false" label="Available Sites" Index="available_sites">
            <div class="map-wrapper">
                <div v-show="!fullscreen" id="filter_search_row_wrapper">
                    <div class="filter_search_wrapper" style="margin-bottom: 5px;" id="filter_search_row">
                        <template v-show="select2Applied">
                            <div class="row">
                                <div class="col-sm-1">
                                    <label class="control-label">Status</label>
                                </div>
                                <div class="col-sm-3">
                                    <select class="form-control" ref="filterStatus" ></select>
                                </div>
                                <div class="col-sm-1">
                                    <label class="control-label">Availability</label>
                                </div>
                                <div class="col-sm-3">
                                    <select class="form-control" ref="filterAvailability" ></select>
                                </div>
                                <div class="col-sm-1">
                                    <label :for="search_text" class="control-label">Search</label>
                                </div>
                                <div class="col-sm-3">
                                    <input v-model="search_text" id="search_text" class="form-control" />
                                </div>
                            </div>
                        </template>
                    </div>
                </div>
                <div :id="elem_id" class="map" style="position: relative;">
                    <div v-show="fullscreen" id="filter_search_on_map">

                        <!-- filters on map here -->

                    </div>
                    <div class="basemap-button">
                        <img id="basemap_sat" src="../../assets/satellite_icon.jpg" @click="setBaseLayer('sat')" />
                        <img id="basemap_osm" src="../../assets/map_icon.png" @click="setBaseLayer('osm')" />
                    </div>
                    <div class="optional-layers-wrapper">
                        <div class="optional-layers-button">
                            <template v-if="mode === 'layer'">
                                <img src="../../assets/info-bubble.svg" @click="set_mode('measure')" />
                            </template>
                            <template v-else>
                                <img src="../../assets/ruler.svg" @click="set_mode('layer')" />
                            </template>
                        </div>
                        <div style="position:relative">
                            <transition v-if="optionalLayers.length">
                                <div class="optional-layers-button" @mouseover="hover=true">
                                    <img src="../../assets/layers.svg" />
                                </div>
                            </transition>
                            <transition v-if="optionalLayers.length">
                                <div div class="layer_options" v-show="hover" @mouseleave="hover=false" >
                                    <div v-for="layer in optionalLayers">
                                        <input
                                            type="checkbox"
                                            :id="layer.ol_uid"
                                            :checked="layer.values_.visible"
                                            @change="changeLayerVisibility(layer)"
                                            class="layer_option"
                                        />
                                        <label :for="layer.ol_uid" class="layer_option">{{ layer.get('title') }}</label>
                                    </div>
                                </div>
                            </transition>
                        </div>
                    </div>
                </div>
                <Datatable
                    class="table_apiary_site"
                    ref="table_apiary_site"
                    :id="table_id"
                    :dtOptions="dtOptions"
                    :dtHeaders="dtHeaders"
                />
                <div class="button_row">
                    <span class="view_all_button" @click="displayAllFeatures">View All On Map</span>
                </div>
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

        <ContactLicenceHolderModal
            ref="contact_licence_holder_modal"
            :key="modalBindId"
            @contact_licence_holder="contactLicenceHolderOK"
        />
    </div>
</template>

<script>
    import ComponentSiteSelection from '@/components/common/apiary/component_site_selection.vue'
    import FormSection from "@/components/forms/section_toggle.vue"
    import ContactLicenceHolderModal from "@/components/common/apiary/contact_licence_holder_modal.vue"
    import uuid from 'uuid'
    import Vue from 'vue'

    import 'ol/ol.css';
    import 'ol-layerswitcher/dist/ol-layerswitcher.css'
    import Map from 'ol/Map';
    import View from 'ol/View';
    import WMTSCapabilities from 'ol/format/WMTSCapabilities';
    import TileLayer from 'ol/layer/Tile';
    import OSM from 'ol/source/OSM';
    import TileWMS from 'ol/source/TileWMS';
    import WMTS, {optionsFromCapabilities} from 'ol/source/WMTS';
    import Collection from 'ol/Collection';
    import { Draw, Modify, Snap } from 'ol/interaction';
    import VectorLayer from 'ol/layer/Vector';
    import VectorSource from 'ol/source/Vector';
    import { Circle as CircleStyle, Fill, Stroke, Style, Text, RegularShape } from 'ol/style';
    import { FullScreen as FullScreenControl, MousePosition as MousePositionControl } from 'ol/control';
    import { Feature } from 'ol';
    import { LineString, Point } from 'ol/geom';
    import { getDistance } from 'ol/sphere';
    import { circular} from 'ol/geom/Polygon';
    import GeoJSON from 'ol/format/GeoJSON';
    import Overlay from 'ol/Overlay';
    import { getDisplayNameFromStatus, getDisplayNameOfCategory, getStatusForColour, getApiaryFeatureStyle, SiteColours } from '@/components/common/apiary/site_colours.js'
    import { getArea, getLength } from 'ol/sphere'
    import MeasureStyles, { formatLength } from '@/components/common/apiary/measure.js'
    import Datatable from '@vue-utils/datatable.vue'
    import Cluster from 'ol/source/Cluster';
    import 'select2/dist/css/select2.min.css'
    import 'select2-bootstrap-theme/dist/select2-bootstrap.min.css'

    export default {
        name: 'AvailableSites',
        data: function(){
            return {
                debug: true,
                modalBindId: uuid(),
                table_id: uuid(),

                show_col_id: false,
                show_col_site: true,
                show_col_status: true,
                show_col_vacant: true,
                show_col_previous_site_holder: true,
                show_action_available_unavailable: true,
                show_action_make_vacant: true,
                show_action_contact_licence_holder: true,

                map: null,
                apiarySitesQuerySource: null,
                //apiarySitesQueryLayer: null,
                apiarySitesClusterLayer: null,
                elem_id: uuid(),
                popup_id: uuid(),
                popup_closer_id: uuid(),
                popup_content_id: uuid(),
                overlay: null,
                content_element: null,
                modifyInProgressList: [],
                tileLayerOsm: null,
                tileLayerSat: null,
                optionalLayers: [],
                hover: false,
                mode: 'normal',
                drawForMeasure: null,
                style: MeasureStyles.defaultStyle,
                segmentStyle: MeasureStyles.segmentStyle,
                labelStyle: MeasureStyles.labelStyle,
                segmentStyles: null,

                filter_selected_names: 'select status',
                search_text: '',
                fullscreen: false,

                useSelect2: true,
                select2Applied: false,
                filterStatuses: [],
                select2Obj: null,
                show_hide_instructions: [ // This array is used as instructions when showing/hiding the apiary sites on the map
                    // ApiarySite
                    {
                        'id': 'vacant',
                        'text': 'Vacant',
                        'show': false,
                        'loaded': false,
                        'map_updated': false,
                        'api': 'list_apiary_sites_vacant',
                        'features_and_rows': [],
                    },
                    // ApiarySiteOnProposal
                    {
                        'id': 'pending',
                        'text': 'Pending',
                        'show': false,
                        'loaded': false,
                        'map_updated': false,
                        'api': 'list_apiary_sites_pending',
                        'features_and_rows': [],
                    },
                    {
                        'id': 'denied',
                        'text': 'Denied',
                        'show': false,
                        'loaded': false,
                        'map_updated': false,
                        'api': 'list_apiary_sites_denied',
                        'features_and_rows': [],
                    },
                    // ApiarySiteOnApproval
                    {
                        'id': 'current',
                        'text': 'Current',
                        'show': false,
                        'loaded': false,
                        'map_updated': false,
                        'api': 'list_apiary_sites_current',
                        'features_and_rows': [],
                        'options': [
                            {
                                'id': 'available',
                                'text': 'Available',
                                'show': false,
                                'loaded': false,
                                'map_updated': false,
                                'api': 'list_apiary_sites_current_available',
                                'features_and_rows': [],
                            },
                            {
                                'id': 'unavailable',
                                'text': 'Unavailable',
                                'show': false,
                                'loaded': false,
                                'map_updated': false,
                                'api': 'list_apiary_sites_current_unavailable',
                                'features_and_rows': [],
                            }
                        ]
                    },
                    {
                        'id': 'not_to_be_reissued',
                        'text': 'Not to be reissued',
                        'show': false,
                        'loaded': false,
                        'map_updated': false,
                        'api': 'list_apiary_sites_not_to_be_reissued',
                        'features_and_rows': [],
                    },
                    {
                        'id': 'suspended',
                        'text': 'Suspended',
                        'show': false,
                        'loaded': false,
                        'map_updated': false,
                        'api': 'list_apiary_sites_suspended',
                        'features_and_rows': [],
                    },
                ],
                filter_status_options: [
                    {
                        'id': 'vacant',
                        'text': 'Vacant',
                    },
                    {
                        'id': 'pending',
                        'text': 'Pending',
                    },
                    {
                        'id': 'denied',
                        'text': 'Denied',
                    },
                    {
                        'id': 'current',
                        'text': 'Current',
                    },
                    {
                        'id': 'not_to_be_reissued',
                        'text': 'Not to be reissued',
                    },
                    {
                        'id': 'suspended',
                        'text': 'Suspended',
                    },
                ],
                filter_availability_options: [
                    {
                        'id': 'available',
                        'text': 'Available',
                    },
                    {
                        'id': 'unavailable',
                        'text': 'Unavailable',
                    },
                ]
            }
        },
        components: {
            ComponentSiteSelection,
            FormSection,
            ContactLicenceHolderModal,
            Datatable
        },
        props: {
            is_external:{
                type: Boolean,
                default: false
            },
            is_internal:{
                type: Boolean,
                default: true
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
            search_text: function(){
                // Clear data storage in the filters
                let vm = this

                for (let site_status of vm.show_hide_instructions){
                    if (site_status.show){
                        for (let far of site_status.features_and_rows){
                            try {
                                // Remove the apiary_site from the map
                                vm.apiarySitesQuerySource.removeFeature(far.feature)
                                //vm.consoleLogRemovingFeature(apiary_site_geojson.feature)
                            } catch(err){
                                console.log(err)
                            }
                        }
                    }
                    site_status.features_and_rows = []
                    site_status.loaded = false
                    site_status.map_updated = false
                    if (site_status.options){
                        for (let option of site_status.options){
                            console.log('updating map_updated')
                            option.features_and_rows = []
                            option.loaded = false
                            option.map_updated = false
                        }
                    }
                }
                vm.showHideApiarySites()
            }
        },
        computed: {
            ruler_colour: function(){
                if (this.mode === 'normal'){
                    return '#aaa';
                } else {
                    return '#53c2cf';
                }
            },
            dtHeaders: function(){
                return [
                    'Id',
                    'Site',
                    'Status',
                    'Vacant<br>(current status)',  // current status of the 'is_vacant'
                    'Previous Site Holder<br>Applicant',
                    'Action',
                ]
            },
            dtOptions: function(){
                let vm = this
                return {
                    serverSide: false,
                    searching: false,
                    searchDelay: 1000,
                    lengthMenu: [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
                    order: [
                        [1, 'desc'], [0, 'desc'],
                    ],
                    language: {
                        processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                    },
                    responsive: true,
                    processing: true,
                    createdRow: function(row, data, index){
                        console.log('row in createdRow')
                        console.log(row)
                        // Cache datatable row obj
                        data.feature_and_row.row_jquery = $(row).attr('data-apiary-site-id', data.id)
                    },
                    columns: [
                        {
                            // Id (database id)
                            visible: vm.show_col_id,
                            mRender: function (data, type, apiary_site) {
                                return apiary_site.id;
                            }
                        },
                        {
                            // Site (current): general status. Marker
                            visible: vm.show_col_site,
                            mRender: function (data, type, apiary_site) {
                                let status_for_colour = getStatusForColour(apiary_site, false)
                                let fillColour = SiteColours[status_for_colour].fill
                                let strokeColour = SiteColours[status_for_colour].stroke
                                let sub_str = ''

                                if (status_for_colour === 'denied'){
                                    sub_str = '<svg height="20" width="20">' +
                                        '<line x1="4" y1="4" x2="16" y2="16" stroke="' + strokeColour + '" + stroke-width="2" />' +
                                        '<line x1="4" y1="16" x2="16" y2="4" stroke="' + strokeColour + '" + stroke-width="2" />' +
                                           '</svg> site: ' + apiary_site.id
                                } else {
                                    sub_str = '<svg height="20" width="20">' +
                                                '<circle cx="10" cy="10" r="6" stroke="' + strokeColour + '" stroke-width="2" fill="' + fillColour + '" />' +
                                           '</svg> site: ' + apiary_site.id
                                }
                                return '<div data-site="' + apiary_site.id + '">' + sub_str + '</div>'
                            }
                        },
                        {
                            // Status (current): general status.  Text
                            visible: vm.show_col_status,
                            mRender: function (data, type, apiary_site){
                                let dynamic_status = getStatusForColour(apiary_site, false)
                                let display_name = getDisplayNameFromStatus(dynamic_status)
                                return display_name
                            }
                        },
                        {
                            // Vacant (current): yes/no
                            visible: vm.show_col_vacant,
                            mRender: function (data, type, apiary_site) {
                                let status = apiary_site.properties.status
                                let is_vacant = apiary_site.properties.is_vacant
                                if(status === 'vacant' || is_vacant === true){
                                    return '<i class="fa fa-check" aria-hidden="true"></i>'
                                }
                                return ''
                            }
                        },
                        {
                            // Previous Site Holder/Applicant
                            visible: vm.show_col_previous_site_holder,
                            mRender: function (data, type, apiary_site){
                                if (apiary_site.properties.previous_site_holder_or_applicant){
                                    return apiary_site.properties.previous_site_holder_or_applicant
                                } else {
                                    return ''
                                }
                            }
                        },
                        {
                            // Action
                            mRender: function (data, type, apiary_site) {
                                let action_list = []

                                // View on map
                                let view_on_map_html = '<a href="#' + apiary_site.id + '" data-view-on-map="' + apiary_site.id + '">View on map</a>';
                                action_list.push(view_on_map_html);

                                if (vm.show_action_available_unavailable){
                                    // Mark as Available/Unavailable
                                    let display_text = ''
                                    if ((vm.debug || vm.is_external) && ['current',].includes(apiary_site.properties.status.toLowerCase())){
                                        if (apiary_site.properties.available){
                                            display_text = 'Mark as unavailable';
                                        } else {
                                            display_text = 'Mark as available';
                                        }
                                        let ret = '<a data-toggle-availability="' + apiary_site.id + '" data-apiary-site-available="' + apiary_site.properties.available + '">' + display_text + '</a>';
                                        action_list.push(ret);
                                    //} else if (vm.is_internal && ['Current', 'current'].includes(apiary_site.status.id)){
                                    } else if (vm.is_internal && ['current',].includes(apiary_site.properties.status.toLowerCase())){
                                        if (apiary_site.properties.available){
                                            display_text = 'Available';
                                        } else {
                                            display_text = 'Unavailable';
                                        }
                                        action_list.push(display_text);
                                    }
                                }
                                if (vm.show_action_make_vacant){
                                    let display_text = 'Make Vacant'
                                    let ret = '<a data-make-vacant="' + apiary_site.id + '">' + display_text + '</a>';
                                    action_list.push(ret);
                                }
                                if (vm.show_action_contact_licence_holder){
                                    let display_text = 'Contact licence holder'
                                    let ret = '<a data-contact-licence-holder="' + apiary_site.id + '">' + display_text + '</a>';
                                    action_list.push(ret);
                                }
                                return action_list.join('<br />');
                            }
                        },
                    ],
                }
            },
        },
        methods: {
            updateStatusShowHideInstructions: function(status_option_changed){
                console.log('updateStatusShowHideInstructions')

                // Sync select2 selections with statuses array
                let vm = this
                let item_to_be_changed = vm.show_hide_instructions.filter(x => { return x.id === status_option_changed.id })[0]
                item_to_be_changed.map_updated = false
                item_to_be_changed.show = status_option_changed.selected

                if (item_to_be_changed.id === 'current'){
                    let options_to_be_changed = item_to_be_changed.options.filter(x => { return x.show })
                    for (let x of options_to_be_changed){
                        x.map_updated = false
                        console.log(x)
                    }
                }
            },
            updateAvailabilityShowHideInstructions: function(availability_option_changed){
                console.log('in updateAvailabilityShowHideInstructions')

                // Sync select2 selections with availability array
                let vm = this
                let current_status_item = vm.show_hide_instructions.filter(x => { return x.id === 'current' })[0]  // We just interested in the 'current' status
                let item_to_be_changed = current_status_item.options.filter(x => { return x.id === availability_option_changed.id })[0]
                item_to_be_changed.map_updated = false
                item_to_be_changed.show = availability_option_changed.selected
            },
            toggleFilterSearchRow: function(action){
                // Attach/Detach filter-search elements to/from the map
                let vm = this
                let filter_search_elements = $('#filter_search_row')
                let filter_search_row_wrapper = $('#filter_search_row_wrapper')
                let wrapper_in_map = $('#filter_search_on_map')

                if (action === 'enter'){
                    filter_search_elements.prependTo(wrapper_in_map)
                } else if (action === 'leave'){
                    filter_search_elements.prependTo(filter_search_row_wrapper)
                }
            },
            applySelect2: function(){
                let vm = this

                if (!vm.select2Applied){
                    $(vm.$refs.filterStatus).select2({
                        "theme": "bootstrap",
                        allowClear: true,
                        placeholder:"Select Status",
                        multiple:true,
                        data: vm.filter_status_options,
                    }).
                    on('select2:select', function(e){
                        vm.updateStatusShowHideInstructions(e.params.data)
                        vm.showHideApiarySites()
                    }).
                    on('select2:unselect', function(e){
                        vm.updateStatusShowHideInstructions(e.params.data)
                        vm.showHideApiarySites()
                    })

                    $(vm.$refs.filterAvailability).select2({
                        "theme": "bootstrap",
                        allowClear: true,
                        placeholder:"Select Availabilities",
                        multiple:true,
                        data: vm.filter_availability_options,
                    }).
                    on("select2:select",function (e) {
                        vm.updateAvailabilityShowHideInstructions(e.params.data)
                        vm.showHideApiarySites()
                    }).
                    on("select2:unselect",function (e) {
                        vm.updateAvailabilityShowHideInstructions(e.params.data)
                        vm.showHideApiarySites()
                    })
                    vm.select2Applied = true
                }
            },
            consoleLogAddingFeature: function(feature){
                console.log('adding feature: ')
                console.log(feature)
            },
            consoleLogRemovingFeature: function(feature){
                console.log('removing feature: ')
                console.log(feature)
            },
            addApiarySiteToMap: function(apiary_site_geojson) {
                let vm = this
                let feature = (new GeoJSON()).readFeature(apiary_site_geojson)
                this.apiarySitesQuerySource.addFeature(feature)
                //this.consoleLogAddingFeature(feature)
                return feature
            },
            addApiarySiteAsJqueryObjToTable: function(row_geojson){
                console.log('addApiarySiteAsJqueryObjToTable')
                this.$refs.table_apiary_site.vmDataTable.row.add(row_geojson).draw()
            },
            addApiarySiteToTable: function(apiary_site_geojson, feature_and_row){
                console.log('addApiarySiteToTable')

                // Attach the feature_and_row obj in order to cache the table row obj at the 'createdRow' in the feature_and_row obj
                apiary_site_geojson.feature_and_row = feature_and_row
                this.$refs.table_apiary_site.vmDataTable.row.add(apiary_site_geojson).draw()
            },
            removeApiarySiteFromTable: function(row_jquery){
                this.$refs.table_apiary_site.vmDataTable.row(row_jquery).remove().draw()
            },
            addEventListeners: function () {
                $("#" + this.table_id).on("click", "a[data-view-on-map]", this.zoomOnApiarySite)
                $("#" + this.table_id).on("click", "a[data-toggle-availability]", this.toggleAvailability)
                $("#" + this.table_id).on('click', 'a[data-make-vacant]', this.makeVacantClicked)
                $("#" + this.table_id).on('click', 'a[data-contact-licence-holder]', this.contactLicenceHolder)
                $("#" + this.table_id).on('mouseenter', "tr", this.mouseEnter)
                $("#" + this.table_id).on('mouseleave', "tr", this.mouseLeave)
            },
            getApiarySiteAvailableFromEvent(e){
                let apiary_site_available = e.target.getAttribute("data-apiary-site-available");

                if (!(apiary_site_available)){
                    apiary_site_available = e.target.getElementsByTagName('span')[0].getAttribute('data-apiary-site-available')
                }

                return apiary_site_available
            },
            toggleAvailability: function(e){
                console.log('in toggleAvailability')
                let vm = this;
                let apiary_site_id = e.target.getAttribute("data-toggle-availability");
                let current_availability = this.getApiarySiteAvailableFromEvent(e)
                let requested_availability = current_availability === 'true' ? false : true
                e.stopPropagation()

                vm.$http.patch('/api/apiary_site/' + apiary_site_id + '/', { 'available': requested_availability }).then(
                    async function(accept){
                        // Update the site in the table
                        let site_updated = accept.body
                        vm.updateApiarySite(site_updated)
                        vm.constructApiarySitesTable(site_updated);
                    },
                    reject=>{
                        swal(
                            'Submit Error',
                            helpers.apiVueResourceError(err),
                            'error'
                        )
                    }
                );
            },
            updateApiarySite: function(site_updated){
                // TODO: Update internal apiary_site data ==> Update map...?
                console.log('in updateApiarySite')
                console.log(site_updated)
                console.log(this.show_hide_instructions)
            },
            constructApiarySitesTable: function(site_updated){
                // TODO: Update table
                console.log('in constructApiarySitesTable')
                //console.log(site_updated)
            },
            makeVacantClicked: function(e){
                let vm = this;
                //let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                let apiary_site_id = e.target.getAttribute("data-make-vacant");
                e.stopPropagation()

                console.log('in makeVacantClicked')
                console.log('apiary_site_id: ' + apiary_site_id)

                swal({
                    title: "Make Vacant",
                    text: "Are you sure you want to make this apiary site: " + apiary_site_id + " vacant?",
                    type: "question",
                    showCancelButton: true,
                    confirmButtonText: 'Yes, make vacant'
                }).then(
                    () => {
                        vm.$http.patch('/api/apiary_site/' + apiary_site_id + '/', { 'status': 'vacant' }).then(
                            async function(accept){
                                // Remove the row from the table
                                // TODO: Update table
                                $(e.target).closest('tr').fadeOut('slow', function(){
                                    // Remove the site table which the table is based on
                                    vm.removeApiarySiteById(apiary_site_id)
                                })

                                // TODO: Update map
                                // Remove the site from the map
                                this.$refs.component_map.removeApiarySiteById(apiary_site_id)
                            },
                            reject=>{
                                swal(
                                    'Submit Error',
                                    helpers.apiVueResourceError(err),
                                    'error'
                                )
                            }
                        );
                    },
                    err => {
                    }
                );
            },
            toggleStatusFilterDropdown: function(){
                $(".status_filter_dropdown").slideToggle("fast")
            },
            mouseEnter: function(e){
                let vm = this;
                if (!vm.not_close_popup_by_mouseleave){
                    let apiary_site_id = e.currentTarget.getAttribute("data-apiary-site-id");
                    if (apiary_site_id){
                        //vm.$refs.component_map.showPopupById(apiary_site_id)
                        vm.showPopupById(apiary_site_id)
                    }
                }
            },
            mouseLeave: function(e){
                let vm = this;
                if (!vm.not_close_popup_by_mouseleave){
                    //vm.$refs.component_map.closePopup()
                    vm.closePopup()
                }
            },
            zoomOnApiarySite: function(e) {
                this.not_close_popup_by_mouseleave = true

                let apiary_site_id = e.target.getAttribute("data-view-on-map");
                this.zoomToApiarySiteById(apiary_site_id)
                e.stopPropagation()
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
                if (this.mode === 'layer'){
                    this.clearMeasurementLayer()
                    this.drawForMeasure.setActive(false)
                } else if (this.mode === 'measure') {
                    this.drawForMeasure.setActive(true)
                }
            },
            addJoint: function(point, styles){
                let s = new Style({
                    image: new CircleStyle({
                        radius: 2,
                        fill: new Fill({
                            color: '#3399cc'
                        }),
                    }),
                })
                s.setGeometry(point)
                styles.push(s)

                return styles
            },
            styleFunctionForMeasurement: function (feature, resolution){
                let vm = this
                let for_layer = feature.get('for_layer', false)

                const styles = []
                styles.push(vm.style)  // This style is for the feature itself
                styles.push(vm.segmentStyle)

                ///////
                // From here, adding labels and tiny circles at the end points of the linestring
                ///////
                const geometry = feature.getGeometry();
                if (geometry.getType() === 'LineString'){
                    let segment_count = 0;
                    geometry.forEachSegment(function (a, b) {
                        const segment = new LineString([a, b]);
                        const label = formatLength(segment);
                        const segmentPoint = new Point(segment.getCoordinateAt(0.5));

                        // Add a style for this segment
                        let segment_style = vm.segmentStyle.clone() // Because there could be multilpe segments, we should copy the style per segment
                        segment_style.setGeometry(segmentPoint)
                        segment_style.getText().setText(label)
                        styles.push(segment_style)

                        if (segment_count == 0){
                            // Add a tiny circle to the very first coordinate of the linestring
                            let p = new Point(a)
                            vm.addJoint(p, styles)
                        }
                        // Add tiny circles to the end of the linestring
                        let p = new Point(b)
                        vm.addJoint(p, styles)

                        segment_count++;
                    });
                }

                if (!for_layer){
                    // We don't need the last label when draw on the layer.
                    let label_on_mouse = formatLength(geometry);  // Total length of the linestring
                    let point = new Point(geometry.getLastCoordinate());
                    vm.labelStyle.setGeometry(point);
                    vm.labelStyle.getText().setText(label_on_mouse);
                    styles.push(vm.labelStyle);
                }

                return styles
            },
            clearMeasurementLayer: function(){
                let vm = this
                let features = vm.measurementLayer.getSource().getFeatures()
                features.forEach((feature) => {
                    vm.measurementLayer.getSource().removeFeature(feature)
                })
            },
            changeLayerVisibility: function(targetLayer){
                targetLayer.setVisible(!targetLayer.getVisible())
            },
            addOptionalLayers: function(){
                let vm = this
                this.$http.get('/api/map_layers/').then(response => {
                    let layers = response.body
                    for (var i = 0; i < layers.length; i++){
                        let l = new TileWMS({
                            url: env['kmi_server_url'] + '/geoserver/' + layers[i].layer_group_name + '/wms',
                            params: {
                                'FORMAT': 'image/png',
                                'VERSION': '1.1.1',
                                tiled: true,
                                STYLES: '',
                                LAYERS: layers[i].layer_full_name
                            }
                        });

                        let tileLayer= new TileLayer({
                            title: layers[i].display_name.trim(),
                            visible: false,
                            source: l,
                        })

                        // Set additional attributes to the layer
                        tileLayer.set('columns', layers[i].columns)
                        tileLayer.set('display_all_columns', layers[i].display_all_columns)

                        vm.optionalLayers.push(tileLayer)
                        vm.map.addLayer(tileLayer)
                    }
                })
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

                let satelliteTileWms = new TileWMS({
                    url: env['kmi_server_url'] + '/geoserver/public/wms',
                    params: {
                        'FORMAT': 'image/png',
                        'VERSION': '1.1.1',
                        tiled: true,
                        STYLES: '',
                        LAYERS: 'public:mapbox-satellite',
                    }
                });

                vm.tileLayerOsm = new TileLayer({
                    title: 'OpenStreetMap',
                    type: 'base',
                    visible: true,
                    source: new OSM(),
                });

                vm.tileLayerSat = new TileLayer({
                    title: 'Satellite',
                    type: 'base',
                    visible: true,
                    source: satelliteTileWms,
                })

                vm.map = new Map({
                    layers: [
                        vm.tileLayerOsm, 
                        vm.tileLayerSat,
                    ],
                    //target: 'map',
                    target: vm.elem_id,
                    view: new View({
                        center: [115.95, -31.95],
                        zoom: 7,
                        projection: 'EPSG:4326'
                    })
                });

                vm.apiarySitesQuerySource = new VectorSource({ });
                //vm.apiarySitesQueryLayer = new VectorLayer({
                //    source: vm.apiarySitesQuerySource,
                //    style: function(feature, resolution){
                //        let status = getStatusForColour(feature, false, vm.display_at_time_of_submitted)
                //        return getApiaryFeatureStyle(status, feature.get('checked'))
                //    },
                //});
                //vm.map.addLayer(vm.apiarySitesQueryLayer);

                let clusterSource = new Cluster({
                    distance: 50,
                    source: vm.apiarySitesQuerySource,
                })

                let styleCache = {}
                vm.apiarySitesClusterLayer = new VectorLayer({
                    title: 'Cluster Layer',
                    source: clusterSource,
                    style: function (clusteredFeature){
                        let featuresInClusteredFeature = clusteredFeature.get('features')
                        let size = featuresInClusteredFeature.length
                        let style = styleCache[size]
                        if(size == 1){
                            // When size is 1, which means the cluster feature has only one site
                            // we want to display it as dedicated style
                            let status = getStatusForColour(featuresInClusteredFeature[0])
                            return getApiaryFeatureStyle(status);
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
                                })
                            })
                            styleCache[size] = style
                        }
                        return style
                    },
                });
                vm.map.addLayer(vm.apiarySitesClusterLayer);
                vm.apiarySitesClusterLayer.setZIndex(10)  

                // Set zIndex to some layers to be rendered over the other layers
                //vm.apiarySitesQueryLayer.setZIndex(10)  

                // Full screen toggle
                let fullScreenControl = new FullScreenControl()
                fullScreenControl.on('enterfullscreen', function(){
                    vm.fullscreen = true
                    vm.toggleFilterSearchRow('enter')
                })
                fullScreenControl.on('leavefullscreen', function(){
                    vm.fullscreen = false
                    vm.toggleFilterSearchRow('leave')
                })
                vm.map.addControl(fullScreenControl)

                // Measure tool
                let draw_source = new VectorSource({ wrapX: false })
                vm.drawForMeasure = new Draw({
                    source: draw_source,
                    type: 'LineString',
                    style: vm.styleFunctionForMeasurement,
                })
                // Set a custom listener to the Measure tool
                vm.drawForMeasure.set('escKey', '')
                vm.drawForMeasure.on('change:escKey', function(evt){
                    //vm.drawForMeasure.finishDrawing()
                })
                vm.drawForMeasure.on('drawstart', function(evt){
                    vm.measuring = true
                })
                vm.drawForMeasure.on('drawend', function(evt){
                    vm.measuring = false
                })

                // Create a layer to retain the measurement
                vm.measurementLayer = new VectorLayer({
                    title: 'Measurement Layer',
                    source: draw_source,
                    style: function(feature, resolution){
                        feature.set('for_layer', true)
                        return vm.styleFunctionForMeasurement(feature, resolution)
                    },
                });
                vm.map.addInteraction(vm.drawForMeasure)
                vm.map.addLayer(vm.measurementLayer)

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
                //for (let i=0; i<vm.apiary_site_geojson_array.length; i++){
                //    //this.addApiarySite(vm.apiary_site_geojson_array[i])
                //}

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

                                    //p.then(res => res.text()).then(function(data){
                                    p.then(res => res.json()).then(function(data){
                                        //vm.showPopupForLayersHTML(data, evt.coordinate, column_names, display_all_columns)
                                        vm.showPopupForLayersJson(data, evt.coordinate, column_names, display_all_columns, vm.optionalLayers[i])
                                    })
                                }
                            }
                        }
                    } else if (vm.mode === 'measure'){
                        // When in measure mode, the styleFunction() is responsible for the drawing
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
                document.addEventListener('keydown', vm.keydown, false)
            },
            keydown: function(evt){
                let vm = this

                let charCode = (evt.which) ? evt.which : evt.keyCode;
                if (charCode === 27 && vm.measuring === true){ //esc key
                    //dispatch event
                    this.drawForMeasure.set('escKey', Math.random());
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
                        } else {

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
            removeApiarySiteById: function(apiary_site_id){
                let feature = this.apiarySitesQuerySource.getFeatureById(apiary_site_id)
                this.apiarySitesQuerySource.removeFeature(feature)
                //this.consoleLogRemovingFeature(feature)
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

            // Existed methods before merging
            contactLicenceHolderClicked: function(apiary_site_id){
                this.openOnSiteInformationModal(apiary_site_id)
            },
            contactLicenceHolder: function(e){
                console.log('contactLicenceHolder')
                let vm = this;
                //let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                let apiary_site_id = e.target.getAttribute("data-contact-licence-holder");

                this.contactLicenceHolderClicked(apiary_site_id)
                e.stopPropagation()
            },
            contactLicenceHolderOK: function(obj){
                this.$http.post('/api/apiary_site/' + obj.apiary_site_id + '/contact_licence_holder/', obj).then(
                    res => {
                        this.$refs.contact_licence_holder_modal.close();
                    },
                    err => {

                    }
                )
            },
            openOnSiteInformationModal: async function(apiary_site_id) {
                this.modalBindId = uuid()

                try {
                    this.$nextTick(() => {
                        if (this.$refs.contact_licence_holder_modal){
                            this.$refs.contact_licence_holder_modal.apiary_site_id = apiary_site_id
                            this.$refs.contact_licence_holder_modal.openMe();
                        }
                    });
                } catch (err) {

                }
            },
            showHideApiarySites: async function() {
                /////
                // This function shows/hides the apiary sites according to the show_hide_instructions object.
                /////
                let vm = this

                // Clear table (this is not efficient)
                //this.$refs.table_apiary_site.vmDataTable.clear().draw();

                for (let site_status of vm.show_hide_instructions){
                    if (site_status.options){
                        // Options (sub categories) exist
                        for (let option of site_status.options){
                            if (option.map_updated)
                                continue  // All the apiary sites in this option have been already updated on the map.  Go to the next option
                            if (site_status.show && option.show){
                                // Show the apiary sites only when both 'current' and 'available'/'unavailable' are true
                                if (option.loaded){
                                    // Data have been already loaded
                                    for (let far of option.features_and_rows){
                                        // Add the features to the map from the data storage
                                        vm.apiarySitesQuerySource.addFeature(far.feature)
                                        //vm.consoleLogAddingFeature(apiary_site_geojson.feature)
                                        // Add the features to the table from the data storage
                                        //vm.addApiarySiteToTable(apiary_site_geojson)
                                    }
                                } else {
                                    Vue.http.get('/api/apiary_site/' + option.api + '/?search_text=' + vm.search_text).then(re => {
                                        for (let apiary_site_geojson of re.body.features){
                                            // Add the apiary_site to the map
                                            let feature = vm.addApiarySiteToMap(apiary_site_geojson)

                                            // Add this feature to the geojson data as a property
                                            //apiary_site_geojson.feature = feature

                                            // Add the apiary_site to the table
                                            let feature_and_row = { 'feature': feature }
                                            option.features_and_rows.push(feature_and_row)
                                            apiary_site_geojson.feature_and_row = feature_and_row
                                            vm.addApiarySiteToTable(apiary_site_geojson)

                                            // Cache it
                                            //option.apiary_sites.push(apiary_site_geojson)
                                        }
                                        option.loaded = true
                                    })
                                }
                            } else {
                                for (let feature_and_row of option.features_and_rows){
                                    // Remove the apiary_site from the map.  There are no functions to show/hide a feature unlike the layer.
                                    if (feature_and_row && vm.apiarySitesQuerySource.hasFeature(feature_and_row.feature)){
                                        try{
                                            vm.apiarySitesQuerySource.removeFeature(feature_and_row.feature)
                                            //vm.consoleLogRemovingFeature(apiary_site_geojson.feature)
                                        } catch (err){
                                            console.log(err)
                                        }
                                    }
                                }
                            }
                            option.map_updated = true
                        }
                    } else {
                        // No sub options
                        if (site_status.map_updated)
                            continue  // All the apiary sites in this site_status have been already updated on the map.  Go to the next status
                        if (site_status.show){
                            // Show the apiary sites of this site_status
                            if (site_status.loaded){
                                // Data have been already loaded
                                for (let feature_and_row of site_status.features_and_rows){
                                    //apiary_site_geojson.rows = site_status.rows
                                    // Add the features to the map from the data storage
                                    vm.apiarySitesQuerySource.addFeature(feature_and_row.feature)
                                    //vm.consoleLogAddingFeature(apiary_site_geojson.feature)
                                    // Add the features to the table from the data storage
                                    //vm.addApiarySiteToTable(apiary_site_geojson)
                                    vm.addApiarySiteAsJqueryObjToTable(feature_and_row.row_geojson)
                                }
                            } else {
                                // Data have not been loaded yet
                                // Fetch data from the server
                                // Add the features to the map
                                // Add the features to the table
                                // Store data in the data storage
                                Vue.http.get('/api/apiary_site/' + site_status.api + '/?search_text=' + vm.search_text).then(re => {
                                    for (let apiary_site_geojson of re.body.features){
                                        apiary_site_geojson.rows = site_status.rows
                                        // Add the apiary_site to the map
                                        let feature = vm.addApiarySiteToMap(apiary_site_geojson)

                                        // Cache the feature obj for the map
                                        let feature_and_row = { 'feature': feature }

                                        // Cache the row_geojson for adding this row
                                        feature_and_row.row_geojson = apiary_site_geojson

                                        // Add this feature_and_row obj to the main storage
                                        site_status.features_and_rows.push(feature_and_row)

                                        // Add the row to the table
                                        vm.addApiarySiteToTable(apiary_site_geojson, feature_and_row)
                                    }
                                    site_status.loaded = true
                                })
                            }
                        } else {
                            // Hide the apiary_sites of this site_status
                            for (let feature_and_row of site_status.features_and_rows){
                                // Remove the apiary_site from the map.  There are no functions to show/hide a feature unlike the layer.
                                if (feature_and_row && vm.apiarySitesQuerySource.hasFeature(feature_and_row.feature)){
                                    try{
                                        vm.apiarySitesQuerySource.removeFeature(feature_and_row.feature)
                                        //vm.consoleLogRemovingFeature(apiary_site_geojson.feature)
                                        vm.removeApiarySiteFromTable(feature_and_row.row_jquery)
                                    } catch (err){
                                        console.log(err)
                                    }
                                }
                            }
                        }
                        site_status.map_updated = true
                    }
                }
            }, // END: showHideApiarySites()
        },
        created: function() {

        },
        mounted: function() {
            let vm = this;
            this.$nextTick(() => {
                vm.addEventListeners()
            });
            vm.initMap()
            vm.setBaseLayer('osm')
            vm.set_mode('layer')
            vm.addOptionalLayers()
            //vm.map.addLayer(vm.apiarySitesQueryLayer);
            vm.displayAllFeatures()
            this.applySelect2()
            //vm.updateStatusShowHideInstructions()
            //vm.updateAvailabilityShowHideInstructions()
            vm.showHideApiarySites()
        },
    }
</script>

<style lang="css" scoped>
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
        z-index: 10;
    }
    .table_apiary_site {
        position: relative;
        z-index: 10;
    }
    .button_row {
        display: flex;
        justify-content: flex-end;
    }
    .view_all_button {
        color: #03a9f4;
        cursor: pointer;
    }
    .status_filter_dropdown_wrapper {
        position: relative;
    }
    .status_filter_dropdown_button {
        cursor: pointer;
        width: 100%;
        position: relative;
    }
    .status_filter_dropdown {
        position: absolute;
        background: white;
        display: none;
        border-radius: 2px;
        min-width: max-content;
        padding: 0.5em;
        border: 3px solid rgba(5, 5, 5, .1);
    }
    .sub_option {
        margin-left: 1em;
    }
    .dropdown_arrow::after {
        content: "";
        width: 7px;
        height: 7px;
        border: 0px;
        border-bottom: solid 2px #909090;
        border-right: solid 2px #909090;
        -ms-transform: rotate(45deg);
        -webkit-transform: rotate(45deg);
        transform: rotate(45deg);
        position: absolute;
        top: 50%;
        right: 21px;
        margin-top: -4px;
    }
    /*
    .status_filter_dropdown {
        position: absolute;
        display: none;
        background: white;
        padding: 1em;
    }
    */
    .select2-container {
        z-index: 100000;
    }
    .select2-options {
        z-index: 100000;
    }
</style>
