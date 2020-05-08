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
            apiary_site_location_id:{
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
                apiary_site_location: null,
                modalBindId: null,
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
                                return 'site name?'
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                return 'View on map<br />Mark as available<br />(Mark as unavailable)'
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
                    if(this.apiary_site_location.apiary_sites.length > 0){
                        enabled = true
                    }
                } catch(err) { }
                return enabled;
            }
        },
        watch:{
            apiary_site_location_id: async function() {
                await this.loadApiarySiteLocation(this.apiary_site_location_id);
                this.constructOnSiteInformationTable();
            }
        },
        methods:{
            loadApiarySiteLocation: async function(id){
                let temp = await Vue.http.get('/api/proposal_apiary_site_location/' + id)
                this.apiary_site_location = temp.body;
            },
            constructOnSiteInformationTable: function(){
                console.log('constructOnSiteInformationTable');
                if (this.apiary_site_location){
                    console.log('constructOnSiteInformationTable');

                    // Clear table
                    this.$refs.site_availability_table.vmDataTable.clear().draw();

                    // Construct table
                    if (this.apiary_site_location.apiary_sites.length > 0){
                        for(let i=0; i<this.apiary_site_location.apiary_sites.length; i++){
                            this.addApiarySiteToTable(this.apiary_site_location.apiary_sites[i]);
                        }
                    }
                }
            },
            addApiarySiteToTable: function(apiary_site) {
                this.$refs.site_availability_table.vmDataTable.row.add(apiary_site).draw();
            },
            addEventListeners: function() {

            },
        },
        created: function() {
        },
        mounted: function() {
            let vm = this;
            this.$nextTick(() => {
                vm.addEventListeners();
                this.constructOnSiteInformationTable();
            });
        }
    }
</script>

<style lang="css" scoped>

</style>
