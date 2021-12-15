<template>
    <div class="container">
        <template v-for="status in filters">
            <div>
                <input type="checkbox" :id="status.id" :value="status.value" v-model="checkedNames">
                <label :for="status.id">{{ status.display }}</label>
            </div>
        </template>
        <input v-model="search_text">
        <FormSection :formCollapse="false" label="Available Sites" Index="available_sites">
            <ComponentSiteSelection
                ref="component_site_selection"
                :apiary_sites="apiary_sites"
                :is_internal="true"
                :is_external="false"
                :show_col_checkbox="false"
                :show_col_status="true"
                :show_col_previous_site_holder="true"
                :key="component_site_selection_key"
                :table_and_map_in_a_row="true"
                :show_action_contact_licence_holder="false"
                :show_action_make_vacant="true"
                @apiary_sites_updated="apiarySitesUpdated"
                @contact-licence-holder-clicked="contactLicenceHolderClicked"
            />
            <div @click="filterBy">Button</div>
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
                filters: {
                    // ApiarySite
                    'vacant': {
                        'id': 'vacant',
                        'value': 'vacant',
                        'display': 'Vacant',
                    },

                    // ApiarySiteOnProposal
                    'draft': {
                        'id': 'draft',
                        'value': 'draft',
                        'display': 'Draft',
                    },
                    'pending': {
                        'id': 'pending',
                        'value': 'pending',
                        'display': 'Pending',
                    },
                    'denied': {
                        'id': 'denied',
                        'value': 'denied',
                        'display': 'Denied',
                    },

                    // ApiarySiteOnApproval
                    'current': {
                        'id': 'current',
                        'value': 'current',
                        'display': 'Current',
                    },
                    'not_to_be_reissued': {
                        'id': 'not_to_be_reissued',
                        'value': 'not_to_be_reissued',
                        'display': 'Not to be reissued',
                    },
                    'suspended': {
                        'id': 'suspended',
                        'value': 'suspended',
                        'display': 'Suspended',
                    },
                    'discarded': {
                        'id': 'discarded',
                        'value': 'discarded',
                        'display': 'Discarded',
                    },
                },
                checkedNames: [],
                search_text: '',
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
            checkedNames: function(){
                console.log('changed')
                console.log(this.checkedNames)
            },
            search_text: function(){
                console.log('changed')
                console.log(this.search_text)
            }
        },
        computed: {

        },
        methods: {
            filterBy: function(statuses){
                this.component_site_selection_key = uuid()
                this.loadSites()
            },
            contactLicenceHolderClicked: function(apiary_site_id){
                this.openOnSiteInformationModal(apiary_site_id)
            },
            contactLicenceHolder: function(obj){
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

            },
            loadSites: async function() {
                let vm = this
                let apis = [
                    'list_existing_proposal_vacant_draft',
                    'list_existing_proposal_vacant_processed',
                    'list_existing_approval_vacant',
                    //'list_existing_proposal_draft',
                    //'list_existing_proposal_processed',  // 'denied' included
                    //'list_existing_approval',  // includes 'available_sites' and 'not_to_be_reissued'
                    //'available_sites',   // All the available_sites are retrieved by the query above: list_existing_approval, too
                                         // ApiarySiteOnApproval.site_status = 'current' 
                                         //   AND
                                         // ApiarySiteOnApproval.available = True

                    //'transitable_sites', // Some site may be already retrieved by the query above: list_existing_proposal_processed/fil
                                         // Not vacant and ApiarySiteOnApproval.site_status = 'not_to_be_reissued'
                                         //   OR 
                                         // Not vadant and ApiarySiteOnProposal.site_status = 'denied'
                ]

                for (let api of apis){
                    Vue.http.get('/api/apiary_site/' + api + '/').then(re => {
                        console.log('in ' + api)
                        console.log(re.body.features.length + ' sites')
                        vm.$refs.component_site_selection.addApiarySitesToMap(re.body.features)
                    })
                }
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
