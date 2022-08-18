<template lang="html">
    <div>
        <div class="row col-sm-12" style="margin-bottom: 0.5em;">
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
                // For Expandable row
                td_expand_class_name: 'expand-icon',
                td_collapse_class_name: 'collapse-icon',
                expandable_row_class_name: 'expandable_row_class_name',
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
                    rowCallback: function (row, obj){
                        console.log('in rowCallback')
                        let row_jq = $(row)
                        row_jq.children().first().addClass(vm.td_expand_class_name)
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
            number_of_columns: function() {
                let num =  this.$refs.on_site_information_table.vmDataTable.columns(':visible').nodes().length;
                return num
            },
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

                // Listener for thr row
                let vm = this
                vm.$refs.on_site_information_table.vmDataTable.on('click', 'td', function(e) {
                    let td_link = $(this)

                    if (!(td_link.hasClass(vm.td_expand_class_name) || td_link.hasClass(vm.td_collapse_class_name))){
                        // This row is not configured as expandable row (at the rowCallback)
                        return
                    }

                    // Get <tr> element as jQuery object
                    let tr = td_link.closest('tr')

                    // Get full data of this row
                    let $row = vm.$refs.on_site_information_table.vmDataTable.row(tr)
                    let full_data = $row.data()
                    console.log({full_data})

                    let first_td = tr.children().first()
                    if(first_td.hasClass(vm.td_expand_class_name)){
                        // Expand

                        // If we don't need to retrieve the data from the server, follow the code below
                        let hives_loc = '<div><strong>The proposed location of the hives</strong>: ' + full_data.hives_loc + '</div>'
                        let hives_num = '<div><strong>Number of hives proposed to be placed on the site</strong>: ' + full_data.hives_num + '</div>'
                        let people_names = '<div><strong>The names of the people who are expected to be entering the site for apiary purposes</strong>: ' + full_data.people_names + '</div>'
                        let flora = '<div><strong>Flora targeted</strong>: ' + full_data.flora + '</div>'

                        let contents = hives_loc + hives_num + people_names + flora

                        let details_elem = $('<tr class="' + vm.expandable_row_class_name +'"><td colspan="' + vm.number_of_columns + '">' + contents + '</td></tr>')
                        details_elem.hide()
                        details_elem.insertAfter(tr)
                        details_elem.fadeIn(1000)

                        // Change icon class name to vm.td_collapse_class_name
                        first_td.removeClass(vm.td_expand_class_name).addClass(vm.td_collapse_class_name)
                    } else {
                        let nextElem = tr.next()
                        // Collapse
                        if(nextElem.is('tr') & nextElem.hasClass(vm.expandable_row_class_name)){
                            // Sticker details row is already shown.  Remove it.
                            nextElem.fadeOut(500, function(){
                                nextElem.remove()
                            })
                        }
                        // Change icon class name to vm.td_expand_class_name
                        first_td.removeClass(vm.td_collapse_class_name).addClass(vm.td_expand_class_name)
                    }
                })
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

<style>
.collapse-icon {
    cursor: pointer;
}
.collapse-icon::before {
    top: 5px;
    left: 4px;
    height: 14px;
    width: 14px;
    border-radius: 14px;
    line-height: 14px;
    border: 2px solid white;
    line-height: 14px;
    content: '-';
    color: white;
    background-color: #d33333;
    display: inline-block;
    box-shadow: 0px 0px 3px #444;
    box-sizing: content-box;
    text-align: center;
    text-indent: 0 !important;
    font-family: 'Courier New', Courier monospace;
    margin: 5px;
}
.expand-icon {
    cursor: pointer;
}
.expand-icon::before {
    top: 5px;
    left: 4px;
    height: 14px;
    width: 14px;
    border-radius: 14px;
    line-height: 14px;
    border: 2px solid white;
    line-height: 14px;
    content: '+';
    color: white;
    background-color: #337ab7;
    display: inline-block;
    box-shadow: 0px 0px 3px #444;
    box-sizing: content-box;
    text-align: center;
    text-indent: 0 !important;
    font-family: 'Courier New', Courier monospace;
    margin: 5px;
}
</style>
