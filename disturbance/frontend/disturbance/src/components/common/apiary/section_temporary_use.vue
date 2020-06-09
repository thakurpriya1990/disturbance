<template lang="html">
    <div>
        <div class="row col-sm-12">
            <button v-if="!creatingProposal" class="btn btn-primary pull-right" @click="openNewTemporaryUse">New Temporary Use</button>
        </div>

        <div class="row col-sm-12">
            <datatable
                ref="temporary_use_table"
                id="temporary-use-table"
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
   // import Swal from 'sweetalert2'
    //import Swal from 'sweetalert2/dist/sweetalert2.js'

    export default {
        props:{
            proposal_apiary_id:{
                type: Number,
                required: true,
                default: 0,
            },
            approval_id: {
                type: Number,
                required: true,
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
                creatingProposal: false,
                dtHeaders: [
                    'id',
                    'From',
                    'To',
                    'Site(s)',
                    'Temporary Occupier',
                    'Deed Poll',
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
                                return full.from_date;
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                return full.to_date;
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                return 'site:' + full.id
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                return full.temporary_occupier_name;
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                return 'deed pole (TODO)';
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

        },
        watch:{

        },
        methods:{
            openNewTemporaryUse: function() {
                let vm = this

                swal({
                    title: "Create Temporary Use Application",
                    text: "Are you sure you want to create temporary use application?",
                    type: "question",
                    showCancelButton: true,
                    confirmButtonText: 'Create'
                }).then(
                    () => {
                        vm.createProposal();
                    },
                    (error) => {

                    }
                );
            },
            _get_basic_data: function(){
                let data = {
                    'category': '',
                    'profile': '', // TODO how to determine this?
                    'district': '',
                    'application': '3',  // TODO Retrieve the id of the 'Temporary Use' type or handle it at the server side 
                                         //      like if there is apiary_temporary_use attribute, it must be a temporary use application, or so.
                    'sub_activity2': '',
                    'region': '',
                    'approval_level': '',
                    'behalf_of': '',  // TODO how to determine this?
                    'activity': '',
                    'sub_activity1': '',
                    'application_type_str': 'temporary_use',
                    'approval_id': this.approval_id,
                }
                return data
            },
            createProposal:function () {
                console.log('createProposal');

                let vm = this;
                vm.creatingProposal = true;
                let data = vm._get_basic_data();

                vm.$http.post('/api/proposal.json', data).then(res => {
                    vm.proposal = res.body;

                    console.log('returned: ')
                    console.log(vm.proposal)

                    vm.$router.push({ name:"draft_proposal", params:{ proposal_id: vm.proposal.id }});
                    vm.creatingProposal = false;
                },
                err => {
                    console.log(err);
                });
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
            });
        }
    }
</script>

<style lang="css" scoped>

</style>
