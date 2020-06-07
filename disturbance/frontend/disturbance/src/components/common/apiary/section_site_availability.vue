<template lang="html">
    <div>
        <div class="row col-sm-12">
            <datatable
                ref="site_availability_table"
                id="site-availability-table"
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
    //import uuid from 'uuid'

    export default {
        props:{
           // initial_apiary_sites: {
           //     type: Array,
           //     required: true,
           //     default: function() {
           //         return [];
           //     }
           // },
            approval_id: {
                type: Number,
                required: true,
                default: 0,
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
                proposal_apiary: null,
                modalBindId: null,
                apiary_sites: [],
                dtHeaders: [
                    'id',
                    'site',
                    'action',
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
                                return '(site name)'
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                let action_list = ['View on map (TODO)',]
                                let display_text = ''
                                if (full.available){
                                    display_text = 'Mark as unavailable';
                                } else {
                                    display_text = 'Mark as available';
                                }
                                let ret = '<a><span class="toggle_availability" data-apiary-site-id="' + full.id + '" data-apiary-site-available="' + full.available + '"/>' + display_text + '</span></a>';
                                action_list.push(ret);
                                return action_list.join('<br />');
                            }
                        },
                    ],
                },
            }
        },
        components: {
            datatable,
        },
        computed:{
            addButtonEnabled: function() {
                let enabled = false;
                try {
                    if(this.proposal_apiary.apiary_sites.length > 0){
                        enabled = true
                    }
                } catch(err) { }
                return enabled;
            }
        },
        watch:{
           // initial_apiary_sites: {
           //     deep: true,
           //     handler(){
           //         console.log('in watch: initial_apiary_site');
           //         this.apiary_sites = this.initial_apiary_sites;
           //         this.constructSitesTable();
           //     },
           // },
        },
        methods:{
            loadApiarySites: async function(){
                console.log('loadApiarySites');

                await this.$http.get('/api/approvals/' + this.approval_id + '/apiary_site/').then(
                    (accept)=>{
                        console.log('accept')
                        console.log(accept.body)
                        this.apiary_sites = accept.body
                        this.constructSitesTable()
                    },
                    (reject)=>{
                        console.log('reject')
                    },
                )
            },
            constructSitesTable: function(){
                console.log('constructSitesTable');
                // Clear table
                this.$refs.site_availability_table.vmDataTable.clear().draw();

                // Construct table
                if (this.apiary_sites.length > 0){
                    for(let i=0; i<this.apiary_sites.length; i++){
                        this.addApiarySiteToTable(this.apiary_sites[i]);
                    }
                }
            },
            addApiarySiteToTable: function(apiary_site) {
                this.$refs.site_availability_table.vmDataTable.row.add(apiary_site).draw();
            },
            addEventListeners: function() {
                $("#site-availability-table").on("click", ".toggle_availability", this.toggleAvailability);
            },
            updateApiarySite: function(site_updated) {
                // Update internal apiary_site data
                for (let i=0; i<this.apiary_sites.length; i++){
                    if (this.apiary_sites[i].id == site_updated.id){
                        this.apiary_sites[i].available = site_updated.available
                    }
                }
            },
            toggleAvailability: function(e) {
                let vm = this;
                let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                let current_availability = e.target.getAttribute("data-apiary-site-available");
                let requested_availability = current_availability === 'true' ? false : true

                vm.$http.patch('/api/apiary_site/' + apiary_site_id + '/', { 'available': requested_availability }).then(
                    async function(accept){
                        // Update the site in the table
                        let site_updated = accept.body
                        this.updateApiarySite(site_updated)
                        vm.constructSitesTable();
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
        },
        created: function() {
            console.log('in created')
            console.log('approval_id: ' + this.approval_id)
            this.loadApiarySites()
        },
        mounted: function() {
            let vm = this;
            this.$nextTick(() => {
                vm.addEventListeners();
                this.constructSitesTable();
            });
        }
    }
</script>

<style lang="css" scoped>

</style>
