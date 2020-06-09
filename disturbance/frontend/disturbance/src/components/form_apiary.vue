<template lang="html">
    <div>

        <SiteLocations 
            :proposal="proposal" 
            id="site_locations" 
            ref="apiary_site_locations" 
            :is_external="is_external" 
            :is_internal="is_internal">
        </SiteLocations>

        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">Deed Poll<small></small>
                <a class="panelClicker" href="#deedPoll" data-toggle="collapse"  data-parent="#userInfo" expanded="true" aria-controls="deedPoll">
                <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                </a>
                </h3>
            </div>
            <div class="panel-body collapse in" id="deedPoll">
                <div class="row">
                    <div class="col-sm-12">
                        <label>Print <a :href="deed_poll_url" target="_blank">the deed poll</a>, sign it, have it witnessed and attach it to this application.</label>
                    </div>
                </div>
                <div class="row">
                    <div class="col-sm-12">
                        <FileField
                        ref="deed_poll_documents" 
                        name="deed-poll-documents" 
                        :isRepeatable="true" 
                        :documentActionUrl="deedPollDocumentUrl" 
                        :readonly="is_internal"
                        />
                        <!--FileField 
                        :proposal_id="proposal.id" 
                        :isRepeatable="false" 
                        name="deed_poll" 
                        :id="'proposal'+proposal.id" 
                        :readonly="proposal.readonly" 
                        ref="deed_poll_doc"
                        /-->
                    </div>
                </div>
            </div>
        </div>

    </div>
</template>

<script>

    import SiteLocations from '@/components/common/apiary/site_locations.vue'
    import FileField from '@/components/forms/filefield_immediate.vue'
    import {
        api_endpoints,
        helpers
    }from '@/utils/hooks'

    export default {
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
            }
        },
        components: {
            SiteLocations,
            FileField
        },
        computed:{
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
          //applicantType: function(){
          //  return this.proposal.applicant_type;
          //},
        },
        methods:{
        },
        mounted: function() {
            let vm = this;
            //vm.form = document.forms.new_proposal;
            //window.addEventListener('beforeunload', vm.leaving);
            //indow.addEventListener('onblur', vm.leaving);
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

