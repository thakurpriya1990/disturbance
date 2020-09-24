<template lang="html">
    <div>

        <template v-if="table_and_map_in_a_row">
            <div class="row col-sm-12">
                <div class="col-sm-6">
                    <datatable
                        ref="table_apiary_site"
                        :id="table_id"
                        :dtOptions="dtOptions"
                        :dtHeaders="dtHeaders"
                    />
                    <template v-if="show_view_all_features_button">
                        <div class="button_row">
                            <span class="view_all_button" @click="displayAllFeatures">View All On Map</span>
                        </div>
                    </template>
                </div>

                <div class="col-sm-6">
                    <ComponentMap
                        ref="component_map"
                        :apiary_site_geojson_array="apiary_site_geojson_array"
                        :key="component_map_key"
                        @featuresDisplayed="updateTableByFeatures"
                        :can_modify="can_modify"
                        @featureGeometryUpdated="featureGeometryUpdated"
                    />
                </div>
            </div>
        </template>

        <template v-else>
            <div class="row col-sm-12">
                <ComponentMap
                    ref="component_map"
                    :apiary_site_geojson_array="apiary_site_geojson_array"
                    :key="component_map_key"
                    @featuresDisplayed="updateTableByFeatures"
                    :can_modify="can_modify"
                />
            </div>
            <div class="row col-sm-12">
                <datatable
                    ref="table_apiary_site"
                    :id="table_id"
                    :dtOptions="dtOptions"
                    :dtHeaders="dtHeaders"
                />
                <template v-if="show_view_all_features_button">
                    <div class="button_row">
                        <span class="view_all_button" @click="displayAllFeatures">View All On Map</span>
                    </div>
                </template>
            </div>
        </template>

    </div>
</template>

<script>
    import Vue from 'vue'
    import datatable from '@vue-utils/datatable.vue'
    import uuid from 'uuid'
    import ComponentMap from '@/components/common/apiary/component_map.vue'
    import SiteColours from '@/components/common/apiary/site_colours.js'

    export default {
        props:{
            apiary_sites: {
                type: Array,
                default: function(){
                    return [];
                }
            },
            is_external:{
                type: Boolean,
                default: false,
            },
            is_internal:{
                type: Boolean,
                default: false,
            },
            table_and_map_in_a_row: {
                type: Boolean,
                default: true,
            },
            show_col_id: {
                type: Boolean,
                default: false,
            },
            show_col_checkbox: {
                type: Boolean,
                default: true,
            },
            enable_col_checkbox: {
                type: Boolean,
                default: true,
            },
            show_col_site: {
                type: Boolean,
                default: true,
            },
            show_col_longitude: {
                type: Boolean,
                default: false,
            },
            show_col_latitude: {
                type: Boolean,
                default: false,
            },
            show_col_district: {
                type: Boolean,
                default: false,
            },
            show_col_status: {
                type: Boolean,
                default: false,
            },
            show_col_previous_site_holder: {
                type: Boolean,
                default: false,
            },
            show_col_action: {
                type: Boolean,
                default: true,
            },
            show_view_all_features_button: {
                type: Boolean,
                default: true,
            },
            show_action_available_unavailable: {
                type: Boolean,
                default: true,
            },
            show_action_make_vacant: {
                type: Boolean,
                default: false,
            },
            show_action_contact_licence_holder: {
                type: Boolean,
                default: false,
            },
            can_modify: {
                type: Boolean,
                default: false,
            }
        },
        watch: {

        },
        data: function(){
            let vm = this;
            return{
                apiary_sites_local: JSON.parse(JSON.stringify(this.apiary_sites)),  // Deep copy the array
                component_map_key: '',
                table_id: uuid(),
                apiary_site_geojson_array: [],  // This is passed to the ComponentMap as props
                default_checkbox_checked: false,  // If checked property isn't set as a apiary_site's property, this default value is used
                dtHeaders: [
                    'Id',
                    '',
                    'Site',
                    'Longitude',
                    'Latitude',
                    'District',
                    'Status',
                    'Previous Site Holder<br>Applicant',
                    'Action',
                ],
                dtOptions: {
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
                    columns: [
                        {
                            // Id (database id)
                            visible: vm.show_col_id,
                            mRender: function (data, type, apiary_site) {
                                return apiary_site.id;
                            }
                        },
                        {
                            // Checkbox
                            visible: vm.show_col_checkbox,
                            className: 'dt-body-center',
                            mRender: function (data, type, apiary_site) {
                                let disabled_str = ''
                                if (!vm.enable_col_checkbox){
                                    disabled_str = ' disabled '
                                }
                                if (apiary_site.checked){
                                    return '<input type="checkbox" class="site_checkbox" data-apiary-site-id="' + apiary_site.id + '"' + disabled_str + ' checked/>'
                                } else {
                                    return '<input type="checkbox" class="site_checkbox" data-apiary-site-id="' + apiary_site.id + '"' + disabled_str + '/>'
                                }
                            }
                        },
                        {
                            // Site
                            visible: vm.show_col_site,
                            mRender: function (data, type, apiary_site) {
                                let fillColour = SiteColours[apiary_site.properties.status].fill
                                let strokeColour = SiteColours[apiary_site.properties.status].stroke
                                return '<svg height="20" width="20">' +
                                            '<circle cx="10" cy="10" r="6" stroke="' + strokeColour + '" stroke-width="2" fill="' + fillColour + '" />' +
                                       '</svg> site: ' + apiary_site.id
                            }
                        },
                        {
                            // Longitude
                            visible: vm.show_col_longitude,
                            mRender: function (data, type, apiary_site){
                                return 'lng'
                            }
                        },
                        {
                            // Latitude
                            visible: vm.show_col_latitude,
                            mRender: function (data, type, apiary_site){
                                return 'lat'
                            }
                        },
                        {
                            // District
                            visible: vm.show_col_district,
                            mRender: function (data, type, apiary_site){
                                return 'dist'
                            }
                        },
                        {
                            // Status
                            visible: vm.show_col_status,
                            mRender: function (data, type, apiary_site){
                                return apiary_site.properties.status
                            }
                        },
                        {
                            // Previous Site Holder/Applicant
                            visible: vm.show_col_previous_site_holder,
                            mRender: function (data, type, apiary_site){
                                return apiary_site.properties.previous_site_holder_or_applicant
                            }
                        },
                        {
                            // Action
                            mRender: function (data, type, apiary_site) {
                                //let ret = '<a><span class="view_on_map" data-apiary-site-id="' + apiary_site.id + '"/>View on Map</span></a>';
                                //return ret;

                                let action_list = []

                                // View on map
                                let view_on_map_html = '<a><span class="view_on_map" data-apiary-site-id="' + apiary_site.id + '"/>View on map</span></a>';
                                action_list.push(view_on_map_html);

                                if (vm.show_action_available_unavailable){
                                    // Mark as Available/Unavailable
                                    let display_text = ''
                                    //if (vm.is_external && ['Current', 'current'].includes(apiary_site.status.id)){
                                    if (vm.is_external && ['Current', 'current'].includes(apiary_site.properties.status)){
                                        if (apiary_site.available){
                                            display_text = 'Mark as unavailable';
                                        } else {
                                            display_text = 'Mark as available';
                                        }
                                        let ret = '<a><span class="toggle_availability" data-apiary-site-id="' + apiary_site.id +
                                            '" data-apiary-site-available="' + apiary_site.available + '"/>' + display_text + '</span></a>';
                                        action_list.push(ret);
                                    //} else if (vm.is_internal && ['Current', 'current'].includes(apiary_site.status.id)){
                                    } else if (vm.is_internal && ['Current', 'current'].includes(apiary_site.properties.status)){
                                        if (apiary_site.available){
                                            display_text = 'Available';
                                        } else {
                                            display_text = 'Unavailable';
                                        }
                                        action_list.push(display_text);
                                    }
                                }
                                if (vm.show_action_make_vacant){
                                    let display_text = 'Make Vacant'
                                    let ret = '<a><span class="make_vacant" data-apiary-site-id="' + apiary_site.id + '"/>' + display_text + '</span></a>';
                                    action_list.push(ret);
                                }
                                if (vm.show_action_contact_licence_holder){
                                    let display_text = 'Contact licence holder'
                                    let ret = '<a><span class="contact_licence_holder" data-apiary-site-id="' + apiary_site.id + '"/>' + display_text + '</span></a>';
                                    action_list.push(ret);
                                }
                                return action_list.join('<br />');
                            }
                        },
                    ],
                },
            }
        },
        created: function(){

        },
        mounted: function(){
            let vm = this;
            this.$nextTick(() => {
                vm.addEventListeners();
                vm.constructApiarySitesTable(vm.apiary_sites);
                vm.addApiarySitesToMap(vm.apiary_sites)
                vm.ensureCheckedStatus();
            });
            this.$emit('apiary_sites_updated', this.apiary_sites_local)
        },
        components: {
            ComponentMap,
            datatable,
        },
        computed: {

        },
        methods: {
            testEvent: function(e){
                console.log('in testEvent')
                console.log(e)
                if (e.target.tagName === "A"){
                    let spans = e.target.getElementsByTagName('span')
                    if (spans.length == 1){
                        let className = spans[0].className
                        console.log(className)
                        switch(className){
                            case 'view_on_map':
                                this.zoomOnApiarySite(e)
                                break;
                            case 'toggle_availability':
                                this.toggleAvailability(e)
                                break;
                            case 'make_vacant':
                                this.makeVacantClicked(e)
                                break;
                            case 'contact_licence_holder':
                                this.contactLicenceHolder(e)
                                break;
                        }
                    } 
                }
            },
            featureGeometryUpdated: function(feature){
                this.$emit('featureGeometryUpdated', feature)
            },
            updateTableByFeatures: function(features) {
                console.log('in updateTableByFeatures')
                console.log(features)

                // Generate a list of the feature ids displayed on the map
                let ids = $.map(features, function(feature){
                    return feature.id_
                })

                // Generate a list of apiary_sites whose ids are in the list generated above
                let apiary_sites_filtered = this.apiary_sites_local.filter(function(apiary_site){
                    return ids.includes(apiary_site.id)
                })

                // Update the table
                this.constructApiarySitesTable(apiary_sites_filtered)
            },
            ensureCheckedStatus: function() {
                console.log('in ensureCheckedStatus')
                if (this.apiary_sites.length > 0){
                    for(let i=0; i<this.apiary_sites.length; i++){
                        if (!this.apiary_sites[i].hasOwnProperty('checked')){
                            this.apiary_sites[i].checked = this.default_checkbox_checked
                        }
                    }
                }
            },
            forceToRefreshMap: function() {
                console.log('forceToRefreshMap in component_site_selection.vue')
                if (this.$refs.component_map){
                    this.$refs.component_map.forceToRefreshMap()
                }
            },
            displayAllFeatures: function(){
                if (this.$refs.component_map){
                    this.$refs.component_map.displayAllFeatures()
                }
            },
            addApiarySitesToMap: function(apiary_sites) {
                console.log('in addApiarySitesToMap')
                for (let i=0; i<apiary_sites.length; i++){
                    console.log(apiary_sites[i])
                    if (apiary_sites[i].hasOwnProperty('checked')){
                        //apiary_sites[i].as_geojson['properties']['checked'] = apiary_sites[i].checked
                        //apiary_sites[i].as_geojson.properties.checked = apiary_sites[i].checked
                        apiary_sites[i].properties.checked = apiary_sites[i].checked
                    }
                    //this.apiary_site_geojson_array.push(apiary_sites[i].as_geojson)
                    this.apiary_site_geojson_array.push(apiary_sites[i])
                }

                // Reload ComponentMap by assigning a new key value
                this.component_map_key = uuid()
            },
            //constructApiarySitesTable: function() {
            //    if (this.$refs.table_apiary_site){
            //        // Clear table
            //        this.$refs.table_apiary_site.vmDataTable.clear().draw();

            //        // Construct table
            //        if (this.apiary_sites.length > 0){
            //            for(let i=0; i<this.apiary_sites.length; i++){
            //                this.addApiarySiteToTable(this.apiary_sites[i]);
            //            }
            //        }
            //    }
            //},
            constructApiarySitesTable: function(apiary_sites) {
                if (this.$refs.table_apiary_site){
                    // Clear table
                    this.$refs.table_apiary_site.vmDataTable.clear().draw();

                    // Construct table
                    if (apiary_sites.length > 0){
                        for(let i=0; i<apiary_sites.length; i++){
                            this.addApiarySiteToTable(apiary_sites[i]);
                        }
                    }
                }
            },
            addApiarySiteToTable: function(apiary_site) {
                this.$refs.table_apiary_site.vmDataTable.row.add(apiary_site).draw();
            },
            addEventListeners: function () {
                $("#" + this.table_id).on("click", ".view_on_map", this.zoomOnApiarySite)
                $("#" + this.table_id).on("click", ".toggle_availability", this.toggleAvailability)
                $("#" + this.table_id).on('click', 'input[type="checkbox"]', this.checkboxClicked)
                $("#" + this.table_id).on('click', '.make_vacant', this.makeVacantClicked)
                $("#" + this.table_id).on('click', '.contact_licence_holder', this.contactLicenceHolder)
                $("#" + this.table_id).on('click', this.testEvent)
            },
            updateApiarySite: function(site_updated) {
                // Update internal apiary_site data
                for (let i=0; i<this.apiary_sites.length; i++){
                    if (this.apiary_sites[i].id == site_updated.id){
                        this.apiary_sites[i].available = site_updated.available
                    }
                }
            },
            removeApiarySiteById: function(site_id){
                // Remove a site for the array which the table is created based on.
                let array_index_removed = null
                for (let i=0; i<this.apiary_sites.length; i++){
                    if (this.apiary_sites[i].id == site_id){
                        array_index_removed = i
                        break
                    }
                }
                if (array_index_removed >= 0){
                    this.apiary_sites.splice(array_index_removed, 1)
                }
            },
            checkboxClicked: function(e) {
                let vm = this;
                //let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                let apiary_site_id = this.getApiarySiteIdFromEvent(e)
                let checked_status = e.target.checked
                for (let i=0; i<this.apiary_sites_local.length; i++){
                    if (this.apiary_sites_local[i].id == apiary_site_id){
                        this.apiary_sites_local[i].checked = checked_status
                    }
                }
                this.$emit('apiary_sites_updated', this.apiary_sites_local)
                this.$refs.component_map.setApiarySiteSelectedStatus(apiary_site_id, checked_status)
                e.stopPropagation()
            },
            contactLicenceHolder: function(e){
                console.log('in contactLicenceHolder')
                let vm = this;
                //let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                let apiary_site_id = this.getApiarySiteIdFromEvent(e)

                this.$emit('contact-licence-holder-clicked', apiary_site_id)
                e.stopPropagation()
            },
            makeVacantClicked: function(e) {
                console.log('in makeVacantClicked')
                console.log(e)
                let vm = this;
                //let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                let apiary_site_id = this.getApiarySiteIdFromEvent(e)
                e.stopPropagation()

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
                                $(e.target).closest('tr').fadeOut('slow', function(){
                                    // Remove the site table which the table is based on
                                    vm.removeApiarySiteById(apiary_site_id)
                                })

                                // Remove the site from the map
                                this.$refs.component_map.removeApiarySiteById(apiary_site_id)
                                //vm.component_map_key = uuid()
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
                        console.log(err)
                    }
                );
            },
            toggleAvailability: function(e) {
                console.log('in toggleAvailability')
                let vm = this;
                //let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                let apiary_site_id = this.getApiarySiteIdFromEvent(e)
                //let current_availability = e.target.getAttribute("data-apiary-site-available");
                let current_availability = this.getApiarySiteAvailableFromEvent(e)
                let requested_availability = current_availability === 'true' ? false : true
                e.stopPropagation()

                vm.$http.patch('/api/apiary_site/' + apiary_site_id + '/', { 'available': requested_availability }).then(
                    async function(accept){
                        // Update the site in the table
                        let site_updated = accept.body
                        vm.updateApiarySite(site_updated)
                       // vm.constructApiarySitesTable();
                        vm.constructApiarySitesTable(vm.apiary_sites);
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
            zoomOnApiarySite: function(e) {
                console.log('in zoomOnApiarySite')
                //let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                let apiary_site_id = this.getApiarySiteIdFromEvent(e)
                this.$refs.component_map.zoomToApiarySiteById(apiary_site_id)
                e.stopPropagation()
            },
            getApiarySiteIdFromEvent(e){
                let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                if (!(apiary_site_id)){
                    apiary_site_id = e.target.getElementsByTagName('span')[0].getAttribute('data-apiary-site-id')
                }
                return apiary_site_id
            },
            getApiarySiteAvailableFromEvent(e){
                let apiary_site_available = e.target.getAttribute("data-apiary-site-available");
                if (!(apiary_site_available)){
                    apiary_site_available = e.target.getElementsByTagName('span')[0].getAttribute('data-apiary-site-available')
                }
                return apiary_site_available
            }
        },
    }
</script>

<style lang="css" scoped>
.component-site-selection {
    border: solid 2px #5BB;
}
.button_row {
    display: flex;
    justify-content: flex-end;
}
.view_all_button {
    color: #03a9f4;
    cursor: pointer;
}
.site_checkbox {
    text-align: center;
}
</style>
