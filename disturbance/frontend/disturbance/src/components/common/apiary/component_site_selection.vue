<template lang="html">
    <div>

        <div class="row col-sm-12">
            <div class="col-sm-6">
                <datatable
                    ref="table_apiary_site"
                    id="table-apiary-site"
                    :dtOptions="dtOptions"
                    :dtHeaders="dtHeaders"
                />
            </div>
            <div class="col-sm-6">
                <ComponentMap 
                    ref="component_map"
                    :apiary_site_geojson_array="apiary_site_geojson_array"
                    :key="component_map_key"
                />
            </div>
        </div>

    </div>
</template>

<script>
    import datatable from '@vue-utils/datatable.vue'
    import uuid from 'uuid'
    import ComponentMap from '@/components/common/apiary/component_map.vue'

    export default {
        props:{
            apiary_sites_with_selection: {
                type: Array,
                default: function(){
                    return [];
                }
            },
        },
        watch: {

        },
        data: function(){
            return{
                component_map_key: '',
                apiary_site_geojson_array: [],
                dtHeaders: [
                    'Id',
                    '',
                    'Site',
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
                            visible: false,
                            mRender: function (data, type, full) {
                                return full.id;
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                if (full.selected){
                                    return '<input type="checkbox" class="site_checkbox" data-apiary-site-id="' + full.id + '" checked/>'
                                } else {
                                    return '<input type="checkbox" class="site_checkbox" data-apiary-site-id="' + full.id + '" />'
                                }
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                return 'site:' + full.id
                            }
                        },
                        {
                            mRender: function (data, type, full) {
                                let ret = '<a><span class="view_on_map" data-apiary-site-id="' + full.id + '"/>View on Map</span></a>';
                                return ret;
                            }
                        },
                    ],
                },
            }
        },
        created: function(){

        },
        mounted: function(){
            let vm = this;
            this.$nextTick(() => {
                vm.addEventListeners();
                this.constructApiarySitesTable();
                this.addApiarySitesToMap(this.apiary_sites_with_selection)
            });
        },
        components: {
            ComponentMap,
            datatable,
        },
        computed: {

        },
        methods: {
            addApiarySitesToMap: function(apiary_sites) {
                for (let i=0; i<apiary_sites.length; i++){
                    this.apiary_site_geojson_array.push(apiary_sites[i].as_geojson)
                }

                // Reload ComponentMap by assigning a new key value
                this.component_map_key = uuid()
            },
            constructApiarySitesTable: function() {
                // Clear table
                this.$refs.table_apiary_site.vmDataTable.clear().draw();

                // Construct table
                if (this.apiary_sites_with_selection.length > 0){
                    for(let i=0; i<this.apiary_sites_with_selection.length; i++){
                        this.addApiarySiteToTable(this.apiary_sites_with_selection[i]);
                    }
                }
            },
            addApiarySiteToTable: function(apiary_site_with_selection) {
                this.$refs.table_apiary_site.vmDataTable.row.add(apiary_site_with_selection).draw();
            },
            addEventListeners: function () {
                $("#table-apiary-site").on("click", ".view_on_map", this.zoomOnApiarySite);
            },
            emitContentsChangedEvent: function () {
                this.$emit('contents_changed', {

                });
            },
            zoomOnApiarySite: function(e) {
                let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                this.$refs.component_map.zoomToApiarySiteById(apiary_site_id)
            },
        },
    }
</script>

<style lang="css" scoped>
.component-site-selection {
    border: solid 2px #5BB;
}
</style>
