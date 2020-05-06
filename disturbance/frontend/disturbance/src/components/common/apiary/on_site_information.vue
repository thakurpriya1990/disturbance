<template lang="html">
    <div>
        apiary site location id: {{ apiary_site_location_id }}
    </div>
</template>

<script>
    import datatable from '@vue-utils/datatable.vue'
    import uuid from 'uuid';

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
                dtHeaders: [
                    'id',
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
            apiary_site_location_id: async function() {
                console.log(this.apiary_site_location_id);
                console.log('load pasl');
                let temp = await this.loadOnSiteInformation(this.apiary_site_location_id);

                console.log(temp);
            }
        },
        methods:{
            loadOnSiteInformation: async function(id){


            },
            constructOnSiteInformationTable: function(){
                console.log('constructOnSiteInformationTable');

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
