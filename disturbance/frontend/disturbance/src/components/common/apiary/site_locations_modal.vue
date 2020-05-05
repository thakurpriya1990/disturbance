<template lang="html">
    <div>
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="modalTitle" large force>
            <div class="container-fluid">
                <div class="col-sm-12 form-group"><div class="row">
                        <iframe width="100%" height="600" :src="webmap_src"></iframe>
                </div></div>
            </div>
            <div slot="footer">
                <div v-if="errorResponse" class="form-group">
                    <div class="row">
                        <div class="col-sm-12">
                            <strong><span style="white-space: pre;" v-html="errorResponse"></span></strong>
                        </div>
                    </div>
                </div>
            </div>
        </modal>
    </div>
</template>

<script>
    import Vue from "vue";
    import modal from "@vue-utils/bootstrap-modal.vue";
    import datatable from "@vue-utils/datatable.vue";
    //import filefield from "@/components/common/compliance_file.vue";
    //import { mapGetters, mapActions } from "vuex";
    //import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
    //import utils from "../utils";
    import $ from "jquery";
    //import "jquery-ui/ui/widgets/draggable.js";
    import "bootstrap/dist/css/bootstrap.css";
    //import "awesomplete/awesomplete.css";
    //import IFrame from '@/components/forms/iframe.vue'
    
    export default {
        name: "SiteLocationsModal",
        data: function() {
            return {
                temporary_document_collection_id: null,
                isModalOpen: false,
                processingDetails: false,
                errorResponse: "",
                webmap_src: 'https://dpaw.maps.arcgis.com/apps/Embed/index.html?webmap=1d956bc5513e40568a4f01950906b64b&extent=95.5777,-38.2527,149.5425,-12.3581&home=true&zoom=true&scale=true&search=true&searchextent=true&details=true&disable_scroll=true&theme=light',
            }
        },
        props: {
    
        },
        components: {
            modal,
            datatable,
            //IFrame,
        },
        watch: {
    
        },
        computed: {
            modalTitle: function() {
                return "Site Locations";
            },
        },
        methods: {
            ok: async function() {
                try{
                    console.log('ok');
                } catch(err) {
    
                }
            },
            processError: async function(err){
                console.log('processError');
            },
            cancel: async function() {
                console.log('close');
                this.close();
            },
            close: function() {
                this.isModalOpen = false;
            },
            addEventListeners: function() {
                console.log('addEventListenr');
            },
            sendData: async function() {
                console.log('sendData');
            },
        },
        created: async function() {
            console.log('created');
        },
        mounted: function() {
            this.$nextTick(() => {
                this.addEventListeners();
            });
        }
    };
</script>

<style lang="css" scoped>

</style>
