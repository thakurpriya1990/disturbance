<template lang="html">
    <div>

        <div class="form-group"><div class="row">
            <label class="col-sm-2">Period From</label>
            <div class="col-sm-4">
                <div class="input-group date" ref="periodFromDatePicker">
                    <input type="text" class="form-control" placeholder="DD/MM/YYYY" id="period_from_input_element" :disabled="!period_from_enabled" />
                    <span class="input-group-addon">
                        <span class="glyphicon glyphicon-calendar"></span>
                    </span>
                </div>
            </div>
        </div></div>

        <div class="form-group"><div class="row">
            <label class="col-sm-2">Period To</label>
            <div class="col-sm-4">
                <div class="input-group date" ref="periodToDatePicker">
                    <input type="text" class="form-control" placeholder="DD/MM/YYYY" id="period_to_input_element" :disabled="!period_to_enabled" />
                    <span class="input-group-addon">
                        <span class="glyphicon glyphicon-calendar"></span>
                    </span>
                </div>
            </div>
        </div></div>

        <div class="row col-sm-12">
            <datatable
                ref="apiary_sites_table"
                id="apiary-sites-table"
                :dtOptions="dtOptions"
                :dtHeaders="dtHeaders"
            />
        </div>

    </div>
</template>

<script>
    import Vue from 'vue'
    import datatable from '@vue-utils/datatable.vue'
    import uuid from 'uuid'
    import { api_endpoints, helpers, } from '@/utils/hooks'

    export default {
        props:{
            from_date: {
                type: Object, // Expect moment obj
                default: null,
            }, 
            to_date: {
                type: Object, // Expect moment obj
                default: null,
            }, 
            apiary_sites_array: {
                type: Array,
                default: function(){
                    return [];
                }
            },
            from_date_enabled: {
                type: Boolean,
                default: false,
            },
            to_date_enabled: {
                type: Boolean,
                default: false,
            },
            is_external:{
              type: Boolean,
              default: false
            },
            is_internal:{
              type: Boolean,
              default: false
            },
        },
        data:function () {
            let vm=this;
            return{
                dtHeaders: [
                    'id',
                    '',
                    'Site',
                    'Action',
                ],
                dtOptions: {
                    serverSide: false,
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
                            visible: false,
                            mRender: function (data, type, full) {
                                return full.id;
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                let checked_str = ''
                                let disabled_str = ''
                                if (full.used){
                                    checked_str = "checked";
                                }
                                if (!full.editable){
                                    disabled_str = ' disabled="disabled" ';
                                }
                                return '<input type="checkbox" class="site_checkbox" data-apiary-site-id="' + full.id + '" ' + checked_str + disabled_str + '/>'
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                return 'site:' + full.id
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                let ret = '<a><span class="view_on_map" data-apiary-site-id="' + full.id + '"/>View on Map (TODO)</span></a>';
                                return ret;
                            }
                        },
                    ],
                },
                period_from: '',
                period_to: '',
                period_from_enabled: false,
                period_to_enabled: false,
                apiary_sites: [],
            }
        },
        created: function() {
            // Copy the values from props (it is not allowd to change props' value)
            if (this.from_date){
                if (this.from_date instanceof moment) {
                    this.period_from = this.from_date.format('DD/MM/YYYY');
                } else {
                    // Wrong type of object, clear it
                    console.warn('The value passed to from_date is wrong type');
                    this.period_from = null;
                }
            }
            if (this.to_date){
                if (this.to_date instanceof moment) {
                    this.period_to = this.to_date.format('DD/MM/YYYY');
                } else {
                    // Wrong type of object, clear it
                    console.warn('The value passed to to_date is wrong type');
                    this.period_to = null;
                }
            }
            if (this.apiary_sites_array.length > 0){
                this.apiary_sites = this.apiary_sites_array;
            }
            this.period_from_enabled = this.from_date_enabled;
            this.period_to_enabled = this.to_date_enabled;
        },
        components: {
            datatable,
        },
        computed:{

        },
        methods:{
            viewSiteOnMap: function(e){
                let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                console.log('view site-id: ' + apiary_site_id + ' on the map');
            },
            siteCheckboxClicked: function(e){
                let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                this.$emit('site_checkbox_clicked', apiary_site_id, e.target.checked);
            },
            constructApiarySitesTable: function(){
                // Clear table
                this.$refs.apiary_sites_table.vmDataTable.clear().draw();

                // Construct table
                if (this.apiary_sites.length > 0){
                    for(let i=0; i<this.apiary_sites.length; i++){
                        this.addApiarySiteToTable(this.apiary_sites[i]);
                    }
                }
            },
            addApiarySiteToTable: function(apiary_site) {
                this.$refs.apiary_sites_table.vmDataTable.row.add(apiary_site).draw();
            },
            addEventListeners: function () {
                $("#apiary-sites-table").on("click", ".view_on_map", this.viewSiteOnMap);
                $("#apiary-sites-table").on("click", ".site_checkbox", this.siteCheckboxClicked);

                let vm = this;
                let el_fr = $(vm.$refs.periodFromDatePicker);
                let el_to = $(vm.$refs.periodToDatePicker);
                let options = {
                    format: "DD/MM/YYYY",
                    showClear: true ,
                    useCurrent: false,
                };

                el_fr.datetimepicker(options);
                el_to.datetimepicker(options);

                el_fr.on("dp.change", function(e) {
                    let selected_date = null;
                    if (e.date){
                        // Date selected
                        selected_date = e.date.format('DD/MM/YYYY')  // e.date is moment object
                        vm.period_from = selected_date;
                        el_to.data('DateTimePicker').minDate(selected_date);
                    } else {
                        // Date not selected
                        vm.period_from = selected_date;
                        el_to.data('DateTimePicker').minDate(false);
                    }
                    vm.$emit('from_date_changed', vm.period_from)
                });

                el_to.on("dp.change", function(e) {
                    let selected_date = null;
                    if (e.date){
                        selected_date = e.date.format('DD/MM/YYYY');
                        vm.period_to = selected_date;
                        el_fr.data('DateTimePicker').maxDate(selected_date);
                    } else {
                        vm.period_to = '';
                        el_fr.data('DateTimePicker').maxDate(false);
                    }
                    vm.$emit('to_date_changed', vm.period_to)
                });

                //***
                // Set dates in case they are passed from the parent component
                //***
                let searchPattern = /^[0-9]{4}/

                let period_from_passed = vm.period_from;
                if (period_from_passed) {
                    // If date passed
                    if (searchPattern.test(period_from_passed)) {
                        // Convert YYYY-MM-DD to DD/MM/YYYY
                        period_from_passed = moment(period_from_passed, 'YYYY-MM-DD').format('DD/MM/YYYY');
                    }
                    $('#period_from_input_element').val(period_from_passed);
                    el_to.data('DateTimePicker').minDate(period_from_passed);
                }

                let period_to_passed = vm.period_to;
                if (period_to_passed) {
                    // If date passed
                    if (searchPattern.test(period_to_passed)) {
                        // Convert YYYY-MM-DD to DD/MM/YYYY
                        period_to_passed = moment(period_to_passed, 'YYYY-MM-DD').format('DD/MM/YYYY');
                    }
                    $('#period_to_input_element').val(period_to_passed);
                    el_fr.data('DateTimePicker').maxDate(period_to_passed);
                }
            },
        },
        mounted: function() {
            let vm = this;
            this.$nextTick(() => {
                vm.addEventListeners();
                this.constructApiarySitesTable();
            });
        }
    }
</script>

<style lang="css" scoped>

</style>
