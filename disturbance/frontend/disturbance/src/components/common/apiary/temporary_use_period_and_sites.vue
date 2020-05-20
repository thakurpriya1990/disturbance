<template lang="html">
    <div>
        <div class="row col-sm-12">
            <datatable 
                ref="on_site_information_table" 
                id="on-site-information-table" 
                :dtOptions="dtOptions" 
                :dtHeaders="dtHeaders" 
            />
        </div>

        <template v-if="apiary_site_location">
            <OnSiteInformationAddModal 
                ref="on_site_information_add_modal" 
                :apiary_site_location="apiary_site_location" 
                :on_site_information="on_site_information_to_edit"
                :key="modalBindId" 
                @on_site_information_added="onSiteInformationAdded"
            />
        </template>
    </div>
</template>

<script>
    import Vue from 'vue'
    import datatable from '@vue-utils/datatable.vue'
    import uuid from 'uuid'
    import { api_endpoints, helpers, } from '@/utils/hooks'
    import OnSiteInformationAddModal from './on_site_information_add_modal'

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
                on_site_information_to_edit: {
                    id: null,
                    apiary_site: null,
                    comments: '',
                    period_from: null,
                    period_to: null,
                },
                modalBindId: null,
                dtHeaders: [
                    'id',
                    'from',
                    'to',
                    'site',
                    'comments',
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
                                if (full.apiary_site) {
                                    return full.apiary_site.id;
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
                        {
                            mRender: function (data, type, full) {
                                if (full.action) {
                                    return full.action;
                                } else {
                                    let ret = '<a><span class="delete_on_site_information" data-on-site-information-id="' + full.id + '"/>Delete</span></a>';
                                    ret += '<br />'
                                    ret += '<a><span class="edit_on_site_information" data-on-site-information-id="' + full.id + '"/>Edit</span></a>';
                                    return ret;
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
            onSiteInformationAdded: async function() {
                await this.loadApiarySiteLocation(this.apiary_site_location_id);
                this.constructOnSiteInformationTable();
            },
            openOnSiteInformationModalToAdd: async function(e){
                console.log('in openOnSiteInformationModalToAdd()');
                this.openOnSiteInformationModal({
                    id: null,
                    apiary_site: null,
                    comments: '',
                    period_from: null,
                    period_to: null,
                });
            },
            openOnSiteInformationModal: async function(obj_to_edit) {
                console.log('in openOnSiteInformationModal()');
                // Refresh the component key
                this.modalBindId = uuid()

                console.log('obj_to_edit');
                console.log(obj_to_edit);

                this.on_site_information_to_edit = obj_to_edit;

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
                $("#on-site-information-table").on("click", ".delete_on_site_information", this.deleteOnSiteInformation);
                $("#on-site-information-table").on("click", ".edit_on_site_information", this.editOnSiteInformation);
            },
            editOnSiteInformation: async function(e) {
                let vm = this;
                let on_site_information_id = e.target.getAttribute("data-on-site-information-id");
                let obj_to_edit = {
                    id: null,
                    apiary_site: null,
                    comments: '',
                    period_from: null,
                    period_to: null,
                }

                for(let i=0; i<this.apiary_site_location.on_site_information_list.length; i++){
                    if(this.apiary_site_location.on_site_information_list[i].id == on_site_information_id){
                        obj_to_edit = this.apiary_site_location.on_site_information_list[i];
                        break;
                    }
                }

                this.openOnSiteInformationModal(obj_to_edit);

            },
            deleteOnSiteInformation: async function(e) {
                let vm = this;
                let on_site_information_id = e.target.getAttribute("data-on-site-information-id");

                swal({
                      title: "Delete on site information",
                      text: "Are you sure you want to delete this?",
                      type: "warning",
                      showCancelButton: true,
                      confirmButtonClass: "btn-danger",
                      confirmButtonText: "Yes, delete it",
                }).then(
                    (accept) => {
                        vm.$http.delete('/api/on_site_information/' + on_site_information_id).then(
                            async function(accept){
                                await vm.loadApiarySiteLocation(this.apiary_site_location_id);
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
                    },
                    (reject)=>{

                    }
                )
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
