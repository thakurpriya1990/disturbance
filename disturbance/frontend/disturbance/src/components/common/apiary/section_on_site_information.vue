<template lang="html">
    <div>
        <div class="row col-sm-12">
            <template v-if="is_external">
                <button :disabled="!onSiteInformationEnabled" class="btn btn-primary pull-right" @click="openOnSiteInformationModalToAdd">Add</button>
            </template>
        </div>

        <div class="row col-sm-12">
            <datatable
                ref="on_site_information_table"
                id="on-site-information-table"
                :dtOptions="dtOptions"
                :dtHeaders="dtHeaders"
            />
        </div>

        <template v-if="approval_id">
            <OnSiteInformationModal
                ref="on_site_information_modal"
                :on_site_information="on_site_information_to_edit"
                :approval_id="approval_id"
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
    import OnSiteInformationModal from './on_site_information_modal'

    export default {
        props:{
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
            user_can_interact: {
                type: Boolean,
                default: false
            }
        },
        data:function () {
            let vm=this;
            return{
                proposal_apiary: null,
                on_site_information_list: [],
                on_site_information_to_edit: {
                    id: null,
                    apiary_site: null,
                    comments: '',
                    period_from: null,
                    period_to: null,
                },
                modalBindId: null,
                dtHeaders: [
                    'Id',
                    'From',
                    'To',
                    'Site',
                    'Comments',
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
                        {
                            visible: true,
                            mRender: function (data, type, full) {
                                console.log('aho')
                                console.log(full)
                                if (vm.is_external && vm.onSiteInformationEnabled){
                                    if (full.action) {
                                        return full.action;
                                    } else {
                                        let ret = '<a><span class="delete_on_site_information" data-on-site-information-id="' + full.id + '"/>Delete</span></a>';
                                        ret += '<br />'
                                        ret += '<a><span class="edit_on_site_information" data-on-site-information-id="' + full.id + '"/>Edit</span></a>';
                                        return ret;
                                    }
                                } else {
                                    return ''
                                }
                            }
                        },
                    ],
                },
            }
        },
        components: {
            OnSiteInformationModal,
            datatable,
        },
        computed:{
            onSiteInformationEnabled: function() {
                let enabled = false;
                try {
                    if(this.approval_id && this.user_can_interact){
                        enabled = true
                    }
                } catch(err) { }
                return enabled;
            }
        },
        watch:{

        },
        methods:{
            onSiteInformationAdded: async function() {
                await this.loadOnSiteInformation(this.approval_id);
                this.constructOnSiteInformationTable();
            },
            openOnSiteInformationModalToAdd: async function(e){
                this.openOnSiteInformationModal({
                    id: null,
                    apiary_site: null,
                    comments: '',
                    period_from: null,
                    period_to: null,
                });
            },
            openOnSiteInformationModal: async function(obj_to_edit) {
                console.log('openOnSiteInformationModal')
                console.log('obj_to_edit: ')
                console.log(obj_to_edit)

                // Refresh the component key
                this.modalBindId = uuid()

                this.on_site_information_to_edit = obj_to_edit;

                try {
                    this.$nextTick(() => {
                        if (this.$refs.on_site_information_modal){
                            this.$refs.on_site_information_modal.openMe();
                        }
                    });
                } catch (err) {
                    helpers.processError(err)
                }
            },
            constructOnSiteInformationTable: function(){
                // Clear table
                this.$refs.on_site_information_table.vmDataTable.clear().draw();

                // Construct table
                if (this.on_site_information_list.length > 0){
                    for(let i=0; i<this.on_site_information_list.length; i++){
                        this.addOnSiteInformationToTable(this.on_site_information_list[i]);
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
                console.log('in editOnSiteInformation')

                let vm = this;
                let on_site_information_id = e.target.getAttribute("data-on-site-information-id");
                
                console.log('on_site_information_id: ' + on_site_information_id)

                let obj_to_edit = {
                    id: null,
                    apiary_site: null,
                    comments: '',
                    period_from: null,
                    period_to: null,
                }

                for(let i=0; i<this.on_site_information_list.length; i++){
                    if(this.on_site_information_list[i].id == on_site_information_id){
                        obj_to_edit = this.on_site_information_list[i];
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
                        vm.$http.delete('/api/on_site_information/' + on_site_information_id + '/').then(
                            async function(accept){
                                await vm.loadOnSiteInformation(this.approval_id);
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
            loadOnSiteInformation: async function(){
                await this.$http.get('/api/approvals/' + this.approval_id + '/on_site_information/').then(
                    (accept)=>{
                        this.on_site_information_list = accept.body
                        this.constructOnSiteInformationTable()
                    },
                    (reject)=>{
                    },
                )
            }
        },
        created: function() {
            this.loadOnSiteInformation()
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
