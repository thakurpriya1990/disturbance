<template lang="html">
    <div>

        <div v-if="is_external" class="col-md-3">
            <div>
                <h3>Application: {{ proposal.lodgement_number }}</h3>
                <h4>Application Type: {{proposal.application_type }}</h4>
                <h4>Status: {{proposal.customer_status }}</h4>
            </div>
        </div>

        <div :class="apiary_sections_classname">
            <FormSection :formCollapse="false" label="Site Locations" Index="site_locations">

                <div v-if="draftApiaryApplication">

                    <SiteLocations
                        :proposal="proposal"
                        id="site_locations"
                        ref="apiary_site_locations"
                        :is_external="is_external"
                        :is_internal="is_internal"
                        @button_text="button_text"
                        @total_fee_south_west="total_fee_south_west"
                        @total_fee_remote="total_fee_remote"
                        @total_fee_south_west_renewal="total_fee_south_west_renewal"
                        @total_fee_remote_renewal="total_fee_remote_renewal"
                        @num_of_sites_remain_south_west="num_of_sites_remain_south_west"
                        @num_of_sites_remain_remote="num_of_sites_remain_remote"
                        @num_of_sites_remain_south_west_renewal="num_of_sites_remain_south_west_renewal"
                        @num_of_sites_remain_remote_renewal="num_of_sites_remain_remote_renewal"
                        @num_of_sites_south_west_to_add_as_remainder="num_of_sites_south_west_to_add_as_remainder"
                        @num_of_sites_remote_to_add_as_remainder="num_of_sites_remote_to_add_as_remainder"
                        @num_of_sites_south_west_renewal_to_add_as_remainder="num_of_sites_south_west_renewal_to_add_as_remainder"
                        @num_of_sites_remote_renewal_to_add_as_remainder="num_of_sites_remote_renewal_to_add_as_remainder"
                    />

                </div>
                <div v-else>
                    <ComponentSiteSelection
                        :apiary_sites="apiary_sites"
                        :is_internal="is_internal"
                        :is_external="is_external"
                        :show_col_checkbox="false"
                        :show_action_available_unavailable="showActionAvailableUnavailable"
                        :show_col_status="showColStatus"
                        :key="component_site_selection_key"
                      />
                </div>

            </FormSection>

            <FormSection :formCollapse="false" label="Deed Poll" Index="deed_poll">
                <div class="row">
                    <div class="col-sm-12">
                        <label>Print <a :href="deedPollUrl" target="_blank">the deed poll</a>, sign it, have it witnessed and attach it to this application.</label>
                    </div>
                </div>
                <div class="row">
                    <div class="col-sm-12">
                        <FileField
                            ref="deed_poll_documents"
                            name="deed-poll-documents"
                            :isRepeatable="false"
                            :documentActionUrl="deedPollDocumentUrl"
                            :readonly="readonly"
                        />
                    </div>
                </div>
            </FormSection>
            <ApiaryChecklist 
                :checklist="applicantChecklistAnswers"
                section_title="Applicant Checklist"
                :readonly="readonly"
                ref="applicant_checklist"
            />
            <div v-if="assessorChecklistVisibility">
                <ApiaryChecklist 
                :checklist="assessorChecklistAnswers"
                section_title="Assessor Checklist"
                :readonly="assessorChecklistReadonly"
                ref="assessor_checklist"
                />
            </div>
            <div v-for="r in referrerChecklistAnswers">
                <!--div v-if="(referral && r.referral_id === referral.id) || (assessorChecklistVisibility && proposal.processing_status === 'With Assessor')"-->
                <div v-if="(referral && r.referral_id === referral.id) || (assessorChecklistVisibility)">
                <!--div v-if="r.id = referral.id"-->
                    <ApiaryChecklist 
                    :checklist="r.referral_data"
                    :section_title="'Referral Checklist: ' + r.referrer_group_name"
                    :readonly="referrerChecklistReadonly"
                    ref="referrer_checklist"
                    />
                </div>
            </div>

            <!--FormSection :formCollapse="false" label="Checklist" Index="checklist">
                <ul class="list-unstyled col-sm-12" v-for="q in proposal.proposal_apiary.applicant_checklist_answers">
                    <div class="row">
                        <div class="col-sm-12">
                            <li class="col-sm-6">
                                <label class="control-label">{{q.question.text}}</label>
                            </li>

                            <ul  class="list-inline col-sm-6">
                                <li class="list-inline-item">
                                    <input  class="form-check-input" v-model="q.answer" ref="Checkbox" type="radio" :name="'option'+q.id" :id="'answer_one'+q.id":value="true" data-parsley-required :disabled="readonly"/> Yes
                                </li>
                                <li class="list-inline-item">
                                    <input  class="form-check-input" v-model="q.answer" ref="Checkbox" type="radio" :name="'option'+q.id" :id="'answer_two'+q.id" :value="false" data-parsley-required :disabled="readonly"/> No
                                </li>
                            </ul>
                        </div>
                    </div>
                </ul>
            </FormSection-->
        </div>

    </div>
</template>

<script>

    import ComponentSiteSelection from '@/components/common/apiary/component_site_selection.vue'
    import FileField from '@/components/forms/filefield_immediate.vue'
    import FormSection from "@/components/forms/section_toggle.vue"
    import SiteLocations from '@/components/common/apiary/site_locations.vue'
    import ApiaryChecklist from '@/components/common/apiary/section_checklist.vue'
    import uuid from 'uuid'
    import {
        api_endpoints,
        helpers
    }from '@/utils/hooks'

    export default {
        name: 'ApiaryForm',
        props:{
            proposal:{
                type: Object,
                required:true
            },
            canEditActivities:{
              type: Boolean,
              default: true
            },
            is_external:{
              type: Boolean,
              default: false
            },
            is_internal:{
              type: Boolean,
              default: false
            },
            is_referral:{
              type: Boolean,
              default: false
            },
            hasReferralMode:{
                type:Boolean,
                default: false
            },
            hasAssessorMode:{
                type:Boolean,
                default: false
            },
            referral:{
                type: Object,
                required:false
            },
            proposal_parks:{
                type:Object,
                default:null
            },
        },
        data:function () {
            let vm=this;
            return{
                values:null,
                pBody: 'pBody'+vm._uid,
                //checklist_answers : [],
                component_site_selection_key: '',
            }
        },
        components: {
            SiteLocations,
            ComponentSiteSelection,
            FileField,
            FormSection,
            ApiaryChecklist,
        },
        computed:{
            showActionAvailableUnavailable: function() {
                let show = false
                if(this.is_external){
                    if(this.proposal && ['approved', 'Approved'].includes(this.proposal.customer_status)){
                        show = true
                    }
                }
                return show
            },
            showColStatus: function() {
                let show = false
                
                show = true

                return show
            },
            apiary_sections_classname: function() {
                // For external page, we need 'col-md-9' classname
                // but not for the internal.
                // This is a hacky way, though...
                if(this.is_internal){
                    return ''
                } else {
                    return 'col-md-9'
                }
            },
            deedPollDocumentUrl: function() {
                let url = '';
                if (this.proposal && this.proposal.proposal_apiary) {
                    url = helpers.add_endpoint_join(
                        //api_endpoints.proposal_apiary,
                        '/api/proposal_apiary/',
                        this.proposal.proposal_apiary.id + '/process_deed_poll_document/'
                        )
                }
                return url;
            },
            /*
            referralChecklistTitle: function() {
                let title = 'Referral Checklist ';
                if (this.referral &&
                */
            deedPollUrl: function() {
                return '';
            },
            readonly: function() {
                let readonlyStatus = true;
                if (this.proposal.customer_status === 'Draft' && !this.is_internal) {
                    readonlyStatus = false;
                }
                return readonlyStatus;
            },
            assessorChecklistReadonly: function() {
                let readonlyStatus = true;
                //if (this.proposal.processing_status === 'With Assessor' && this.is_internal) {
                if (this.is_internal && this.proposal && this.proposal.assessor_mode && this.proposal.assessor_mode.assessor_can_assess) {
                    readonlyStatus = false;
                }
                return readonlyStatus;
            },
            assessorChecklistVisibility: function() {
                let visibility = false;
                //if (this.proposal.processing_status === 'With Assessor' && this.is_internal) {
                if (this.is_internal && this.proposal && this.proposal.assessor_mode && this.proposal.assessor_mode.has_assessor_mode) {
                    visibility = true;
                }
                return visibility;
            },
            referrerChecklistReadonly: function() {
                let readonlyStatus = true;
                // referrer must have access
                if (this.is_internal && this.proposal.processing_status === 'With Referral' && 
                    this.referral && this.referral.processing_status === 'Awaiting' &&
                    this.referral.apiary_referral && this.referral.apiary_referral.can_process) {
                    readonlyStatus = false;
                }
                return readonlyStatus;
            },
            referrerChecklistVisibility: function() {
                let visibility = false;
                // must be relevant referral
                if ((!this.referrerChecklistReadonly && r.id === this.referral.id) || this.assessorChecklistVisibility) {
                    visibility = true;
                }
                return visibility;
            },
            getUnansweredChecklistQuestions: function() {
                let UnansweredChecklistQuestions = false;

                if(this.applicantChecklistAnswers){
                    let numOfAnswers = this.applicantChecklistAnswers.length;
                    for( let i=0; i< numOfAnswers ; i ++){
                        if(this.applicantChecklistAnswers[i].answer == null && !this.applicantChecklistAnswers[i].text_answer){
                            UnansweredChecklistQuestions = true;
                        }
                    }
                }
                return UnansweredChecklistQuestions;
            },
            apiary_sites: function() {
                if (this.proposal && this.proposal.proposal_apiary) {
                    return this.proposal.proposal_apiary.apiary_sites;
                }
            },
            draftApiaryApplication: function() {
                let draftStatus = false;
                if (this.is_external && this.proposal && this.proposal.application_type === 'Apiary' && this.proposal.customer_status === 'Draft') {
                    draftStatus = true;
                }
                return draftStatus;
            },
            applicantChecklistAnswers: function() {
                if (this.proposal && this.proposal.proposal_apiary && this.proposal.proposal_apiary.applicant_checklist_answers &&
                    this.proposal.proposal_apiary.applicant_checklist_answers.length > 0) {
                    return this.proposal.proposal_apiary.applicant_checklist_answers;
                }
            },
            assessorChecklistAnswers: function() {
                if (this.proposal && this.proposal.proposal_apiary && this.proposal.proposal_apiary.assessor_checklist_answers &&
                    this.proposal.proposal_apiary.assessor_checklist_answers.length > 0) {
                    return this.proposal.proposal_apiary.assessor_checklist_answers;
                }
            },
            referrerChecklistAnswers: function() {
                if (this.proposal && this.proposal.proposal_apiary && this.proposal.proposal_apiary.referrer_checklist_answers && 
                    this.proposal.proposal_apiary.referrer_checklist_answers.length > 0) {
                    return this.proposal.proposal_apiary.referrer_checklist_answers;
                }
            },

          //applicantType: function(){
          //  return this.proposal.applicant_type;
          //},
        },
        methods:{
            num_of_sites_south_west_to_add_as_remainder: function(value){
                this.$emit('num_of_sites_south_west_to_add_as_remainder', value)
            },
            num_of_sites_remote_to_add_as_remainder: function(value){
                this.$emit('num_of_sites_remote_to_add_as_remainder', value)
            },
            num_of_sites_south_west_renewal_to_add_as_remainder: function(value){
                this.$emit('num_of_sites_south_west_renewal_to_add_as_remainder', value)
            },
            num_of_sites_remote_renewal_to_add_as_remainder: function(value){
                this.$emit('num_of_sites_remote_renewal_to_add_as_remainder', value)
            },
            button_text: function(button_text) {
                this.$emit('button_text', button_text)
            },
            total_fee_south_west: function(total_fee){
                this.$emit('total_fee_south_west', total_fee)
            },
            total_fee_remote: function(total_fee){
                this.$emit('total_fee_remote', total_fee)
            },
            total_fee_south_west_renewal: function(total_fee){
                this.$emit('total_fee_south_west_renewal', total_fee)
            },
            total_fee_remote_renewal: function(total_fee){
                this.$emit('total_fee_remote_renewal', total_fee)
            },
            num_of_sites_remain_south_west: function(value){
                this.$emit('num_of_sites_remain_south_west', value)
            },
            num_of_sites_remain_remote: function(value){
                this.$emit('num_of_sites_remain_remote', value)
            },
            num_of_sites_remain_south_west_renewal: function(value){
                this.$emit('num_of_sites_remain_south_west_renewal', value)
            },
            num_of_sites_remain_remote_renewal: function(value){
                this.$emit('num_of_sites_remain_remote_renewal', value)
            },
            /*
            getChecklistAnswers: function() {
                let vm = this;
                this.checklist_answers.push({
                    'id' : 'this.proposal.proposal_apiary.checklist_answers.id',
                    'answer' : 'this.proposal.proposal_apiary.checklist_answers.answer'
                 })
             return checklist_answers;
            },
            */

        },
        mounted: function() {
            //let vm = this;
            this.component_site_selection_key = uuid()
            //vm.form = document.forms.new_proposal;
            //window.addEventListener('beforeunload', vm.leaving);
            //window.addEventListener('onblur', vm.leaving);
        }

    }
</script>

<style lang="css" scoped>
    .section{
        text-transform: capitalize;
    }
    .list-group{
        margin-bottom: 0;
    }
    .fixed-top{
        position: fixed;
        top:56px;
    }

</style>

