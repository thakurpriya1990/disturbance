<template lang="html">
    <div>

        <SiteLocation :proposal="proposal" id="site_locations" ref="apiary_site_location" :is_external="is_external" :is_internal="is_internal"></SiteLocation>

    </div>
</template>

<script>

    import SiteLocation from '@/components/common/apiary/site_locations.vue'

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
              SiteLocation,
        },
        computed:{
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

