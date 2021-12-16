<template>
    <div class="container">
        <FormSection :formCollapse="false" label="Available Sites" Index="available_sites">
            <div class="map-wrapper row col-sm-12">
                <div :id="elem_id" class="map">
                    <div class="basemap-button">
                        <img id="basemap_sat" src="../../assets/satellite_icon.jpg" @click="setBaseLayer('sat')" />
                        <img id="basemap_osm" src="../../assets/map_icon.png" @click="setBaseLayer('osm')" />
                    </div>
                    <div class="optional-layers-wrapper">
                        <div class="optional-layers-button">
                            <template v-if="mode === 'layer'">
                                <img src="../../assets/info-bubble.svg" @click="set_mode('measure')" />
                            </template>
                            <template v-else>
                                <img src="../../assets/ruler.svg" @click="set_mode('layer')" />
                            </template>
                        </div>
    <!--
                        <div style="position:relative">
                            <transition v-if="optionalLayers.length">
                                <div class="optional-layers-button" @mouseover="hover=true">
                                    <img src="../../../assets/layers.svg" />
                                </div>
                            </transition>
                            <transition v-if="optionalLayers.length">
                                <div div class="layer_options" v-show="hover" @mouseleave="hover=false" >
                                    <div v-for="layer in optionalLayers">
                                        <input
                                            type="checkbox"
                                            :id="layer.ol_uid"
                                            :checked="layer.values_.visible"
                                            @change="changeLayerVisibility(layer)"
                                            class="layer_option"
                                        />
                                        <label :for="layer.ol_uid" class="layer_option">{{ layer.get('title') }}</label>
                                    </div>
                                </div>
                            </transition>
                        </div>
    -->
                    </div>
                </div>
            </div>
            <!--
                <ComponentSiteSelection
                    :apiary_sites="apiary_sites"
                    :is_internal="true"
                    :is_external="false"
                    :show_col_checkbox="false"
                    :show_col_status="false"
                    :show_col_previous_site_holder="false"
                    :key="component_site_selection_key"
                    :table_and_map_in_a_row="true"
                    :show_action_contact_licence_holder="false"
                    @apiary_sites_updated="apiarySitesUpdated"
                    @contact-licence-holder-clicked="contactLicenceHolderClicked"
                />
            -->
        </FormSection>

        <ContactLicenceHolderModal
            ref="contact_licence_holder_modal"
            :key="modalBindId"
            @contact_licence_holder="contactLicenceHolder"
        />
    </div>
</template>

<script>
    import ComponentSiteSelection from '@/components/common/apiary/component_site_selection.vue'
    import FormSection from "@/components/forms/section_toggle.vue"
    import ContactLicenceHolderModal from "@/components/common/apiary/contact_licence_holder_modal.vue"
    import uuid from 'uuid'
    import Vue from 'vue'

    export default {
        name: 'AvailableSites',
        data: function(){
            return {
                component_site_selection_key: uuid(),
                apiary_sites: [],
                modalBindId: uuid(),

                map: null,
                apiarySitesQuerySource: null,
                apiarySitesQueryLayer: null,
                elem_id: uuid(),
                popup_id: uuid(),
                popup_closer_id: uuid(),
                popup_content_id: uuid(),
                overlay: null,
                content_element: null,
                modifyInProgressList: [],
                tileLayerOsm: null,
                tileLayerSat: null,
                optionalLayers: [],
                hover: false,
                mode: 'normal',
                drawForMeasure: null,
                style: MeasureStyles.defaultStyle,
                segmentStyle: MeasureStyles.segmentStyle,
                labelStyle: MeasureStyles.labelStyle,
                segmentStyles: null,
            }
        },
        components: {
            ComponentSiteSelection,
            FormSection,
            ContactLicenceHolderModal
        },
        props: {

        },
        watch: {

        },
        computed: {

        },
        methods: {
            setBaseLayer: function(selected_layer_name){
                let vm = this
                if (selected_layer_name == 'sat') {
                    vm.tileLayerOsm.setVisible(false)
                    vm.tileLayerSat.setVisible(true)
                    $('#basemap_sat').hide()
                    $('#basemap_osm').show()
                } else {
                    vm.tileLayerOsm.setVisible(true)
                    vm.tileLayerSat.setVisible(false)
                    $('#basemap_osm').hide()
                    $('#basemap_sat').show()
                }
            },
            set_mode: function(mode){
                this.mode = mode
                if (this.mode === 'layer'){
                    this.clearMeasurementLayer()
                    this.drawForMeasure.setActive(false)
                } else if (this.mode === 'measure') {
                    this.drawForMeasure.setActive(true)
                }
            },
            contactLicenceHolderClicked: function(apiary_site_id){
                console.log(apiary_site_id)
                this.openOnSiteInformationModal(apiary_site_id)
            },
            contactLicenceHolder: function(obj){
                console.log('contactLicenceHolder')
                this.$http.post('/api/apiary_site/' + obj.apiary_site_id + '/contact_licence_holder/', obj).then(
                    res => {
                        this.$refs.contact_licence_holder_modal.close();
                    },
                    err => {

                    }
                )
            },
            openOnSiteInformationModal: async function(apiary_site_id) {
                this.modalBindId = uuid()

                try {
                    this.$nextTick(() => {
                        if (this.$refs.contact_licence_holder_modal){
                            this.$refs.contact_licence_holder_modal.apiary_site_id = apiary_site_id
                            this.$refs.contact_licence_holder_modal.openMe();
                        }
                    });
                } catch (err) {

                }
            },
            apiarySitesUpdated: function(apiary_sites){
                console.log(apiary_sites)
            },
            loadSites: async function() {
                let vm = this

                Vue.http.get('/api/apiary_site/available_sites/').then(re => {
                    console.log(re.body)

                    vm.apiary_sites = re.body
                    this.component_site_selection_key = uuid()
                });
            },
        },
        created: function() {
            this.loadSites()
        },
        mounted: function() {

        },
    }
</script>

<style>
</style>
