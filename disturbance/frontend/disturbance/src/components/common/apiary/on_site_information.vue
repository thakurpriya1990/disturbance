<template lang="html">
    <div>
        <div class="row">
            <button :disabled="!addButtonEnabled" class="btn btn-primary pull-right" @click="openOnSiteInformationAddModal">Add</button>
        </div>

        <div class="row col-sm-12">
            <datatable ref="on_site_information_table" id="on-site-information-table" :dtOptions="dtOptions" :dtHeaders="dtHeaders" />
        </div>

        <template v-if="apiary_site_location">
            <OnSiteInformationAddModal ref="on_site_information_add_modal" :apiary_site_location="apiary_site_location" :key="modalBindId" />
        </template>
    </div>
</template>

<script>
    import Vue from 'vue'
    import datatable from '@vue-utils/datatable.vue'
    import uuid from 'uuid'
    import { api_endpoints, helpers, } from '@/utils/hooks'
    import OnSiteInformationAddModal from './on_site_information_add_modal'
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
                    'from',
                    'to',
                    'site',
                    'comments',
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
                                if (full.period_from) {
                                    return full.period_from;
                                } else {
                                    return '';
                                }
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                if (full.period_to) {
                                    return full.period_to;
                                } else {
                                    return '';
                                }
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                if (full.apiary_site_id) {
                                    return full.apiary_site_id;
                                } else {
                                    return '';
                                }
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                if (full.comments) {
                                    return full.comments;
                                } else {
                                    return '';
                                }
                            }
                        },
                    ],
                },
            }
        },
        components: {
            OnSiteInformationAddModal,
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
            openOnSiteInformationAddModal: async function() {
                this.modalBindId = uuid()

                try {
                    this.$nextTick(() => {
                        if (this.$refs.on_site_information_add_modal){
                            this.$refs.on_site_information_add_modal.openMe();
                        }
                    });
                } catch (err) {
                    this.processError(err);
                }
            },
            loadApiarySiteLocation: async function(id){
                console.log('loadApiarySiteLocation');
                console.log(id);
                //http://localhost:8071/api/proposal_apiary_site_location/11/on_site_information_list/
                let temp = await Vue.http.get('/api/proposal_apiary_site_location/' + id + '/on_site_information_list/')
                this.apiary_site_location = temp.body;
            },
            constructOnSiteInformationTable: function(){
                console.log('constructOnSiteInformationTable');
                if (this.apiary_site_location && this.apiary_site_location.on_site_information_list){
                    console.log('constructOnSiteInformationTable');

                    // Clear table
                    this.$refs.on_site_information_table.vmDataTable.clear().draw();

                    // Construct table
                    if (this.apiary_site_location.on_site_information_list.length > 0){
                        for(let i=0; i<this.apiary_site_location.on_site_information_list.length; i++){
                            this.addOnSiteInformationToTable(this.apiary_site_location.on_site_information_list[i]);
                        }
                    }
                }
            },
            addOnSiteInformationToTable: function(on_site_information) {
                this.$refs.on_site_information_table.vmDataTable.row.add(on_site_information).draw();
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
