<template lang="html">
    <div>
        <div class="row col-sm-12">
            <button class="btn btn-primary pull-right" @click="openNewTemporaryUse">New Temporary Use</button>
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
            licence_id: {
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
                console.log('in openNewTemporaryUse');
                //this.$router.push({name: 'draft_proposal', params: {proposal_id: '484'}});
                this.$router.push({name: 'external-new-temporary-use', params: {licence_id: this.licence_id}});
                //this.$router.push({name: 'external-proposals-dash'}); //Navigate to dashboard
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
