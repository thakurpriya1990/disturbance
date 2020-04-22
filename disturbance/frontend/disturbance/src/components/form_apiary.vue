<template lang="html">

    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Site Locations<small></small>
                        <a class="panelClicker" :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pBody">
                    <input v-model="name" placeholder="Enter name">
                </div>
            </div>
        </div>
    </div>

<!--
    <div class="row">
      <div class="col-sm-12">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">Site Locations
                    <a :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                        <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                    </a>
                </h3>
            </div>
            <div class="panel-body collapse in" :id="pBody">
                <div class="col-sm-12">
                    <div class="form-group">
                        <div>
                            <input v-model="name" placeholder="Enter name">
                        </div>
                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>
-->
</template>

<script>

//    import Profile from '@/components/user/profile.vue'
//    import Organisation from '@/components/external/organisations/manage.vue'
//    import Applicant from '@/components/common/tclass/applicant.vue'
//    import Assessment from '@/components/common/tclass/assessment.vue'
//
//    import Activity from '@/components/common/filming/activity.vue'
//    import Access from '@/components/common/filming/access.vue'
//    import Equipment from '@/components/common/filming/equipment.vue'
//    import OtherDetails from '@/components/common/filming/other_details.vue'
//    import OnlineTraining from '@/components/common/filming/online_training.vue'
//    import Payment from '@/components/common/filming/payment.vue'
//    import Confirmation from '@/components/common/filming/confirmation.vue'

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
//            Applicant,
//            Activity,
//            Access,
//            Equipment,
//            OtherDetails,
//            Confirmation,
//            Profile,
//            Organisation,
//            Assessment
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

