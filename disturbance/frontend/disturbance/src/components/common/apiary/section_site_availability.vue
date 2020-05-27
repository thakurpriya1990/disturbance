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
            proposal_apiary_id:{
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
            proposal_apiary_id: async function() {
                await this.loadApiarySiteLocation(this.proposal_apiary_id);
                this.constructOnSiteInformationTable();
            }
        },
        methods:{
            loadApiarySiteLocation: async function(id){
                let temp = await Vue.http.get('/api/proposal_apiary/' + id)
                this.proposal_apiary = temp.body;
            },
            constructOnSiteInformationTable: function(){
                if (this.proposal_apiary){

                    // Clear table
                    this.$refs.site_availability_table.vmDataTable.clear().draw();

                    // Construct table
                    if (this.proposal_apiary.apiary_sites.length > 0){
                        for(let i=0; i<this.proposal_apiary.apiary_sites.length; i++){
                            this.addApiarySiteToTable(this.proposal_apiary.apiary_sites[i]);
                        }
                    }
                }
            },
            addApiarySiteToTable: function(apiary_site) {
                this.$refs.site_availability_table.vmDataTable.row.add(apiary_site).draw();
            },
            addEventListeners: function() {
                $("#site-availability-table").on("click", ".toggle_availability", this.toggleAvailability);
            },
            toggleAvailability: function(e) {
                let vm = this;
                let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                let current_availability = e.target.getAttribute("data-apiary-site-available");
                let requested_availability = current_availability === 'true' ? false : true

                vm.$http.patch('/api/apiary_site/' + apiary_site_id + '/', { 'available': requested_availability }).then(
                    async function(accept){
                        await vm.loadApiarySiteLocation(vm.proposal_apiary_id);
                        vm.constructOnSiteInformationTable();
                    },
                    reject=>{
                        swal(
                            'Submit Error',
                            helpers.apiVueResourceError(err),
                            'error'
                        )
                    }
                );
            }
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
