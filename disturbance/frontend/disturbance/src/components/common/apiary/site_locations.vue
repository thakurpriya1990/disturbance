<template lang="html">

    <div class="row" style="padding-bottom: 50px;">
      <div>
        <div v-if="is_external">
            <h3>Application: {{ proposal.lodgement_number }}</h3>
            <h4>Application Type: {{proposal.proposal_type }}</h4>

            <h4>Status: {{proposal.customer_status }}</h4>
        </div>

        <div class="col-md-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Site Locations<small></small>
                        <a class="panelClicker" :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pBody">
                    <span class="col-sm-12">
                        <TextField type="text" :value="proposal.apiary_site_location.title" name="site_location_title" isRequired="true" help_text="help text ..." id="id_title" label="Title" :readonly="is_internal || !proposal.can_user_edit"></TextField>
                    </span>
                    <span class="col-sm-6">
                        <TextField type="text" :value="proposal.apiary_site_location.latitude" name="site_location_latitude" isRequired="true" id="id_latitude" label="Latitude" :readonly="is_internal || !proposal.can_user_edit"></TextField>
                    </span>
                    <span class="col-sm-6">
                        <TextField type="text" :value="proposal.apiary_site_location.longitude" name="site_location_longitude" isRequired="true" id="id_longitude" label="Longitude" :readonly="is_internal || !proposal.can_user_edit"></TextField>
                    </span>

                    <!-- The below commented out block is equivalent to the <TextField> above for 'title'
                    <span>
                        <label :id="id" for="label" class="inline" >Title</label>
                        <a href="" @click.prevent="toggleHelpText"><i class="fa fa-question-circle" style="color:blue">&nbsp;</i></a>
                        <div v-show="showingHelpText">
                            <p class="col-sm-12" v-html="help_text"></p>
                        </div>
                    </span>
                    <input type="text" class="form-control" v-model="proposal.apiary_site_location.title" name="title" :disabled="proposal.readonly">
                    -->
                </div>
                <div>
                    <IFrame width="1000" height="800" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" title="Apiary Sites Beekeeper's Map (WBV)" :src="webmap_src"></IFrame>
                </div>
            </div>

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
                                    <FileField :proposal_id="proposal.id" isRepeatable="false" name="deed_poll" :id="'proposal'+proposal.id" :readonly="proposal.readonly" ref="deed_poll_doc"></FileField>
                                </div>
                            </div>
                </div>
            </div>

            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Checklist<small></small>
                    <a class="panelClicker" href="#checkList" data-toggle="collapse"  data-parent="#userInfo" expanded="true" aria-controls="checkList">
                    <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                    </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" id="checkList">
                            <div class="row">
                                <div class="col-sm-12">
                                    <label>Checklist items go here (pulled from Django Admin) ...</label>
                                </div>
                            </div>
                </div>
            </div>
        </div>

      </div>

    </div>

</template>

<script>

    import TextField from '@/components/forms/text.vue'
    import IFrame from '@/components/forms/iframe.vue'
    import FileField from '@/components/forms/filefield.vue'

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
                webmap_src: 'https://dpaw.maps.arcgis.com/apps/Embed/index.html?webmap=1d956bc5513e40568a4f01950906b64b&extent=95.5777,-38.2527,149.5425,-12.3581&home=true&zoom=true&scale=true&search=true&searchextent=true&details=true&disable_scroll=true&theme=light',
                //title: proposal.apiary_site_location.title,
                //latitude: proposal.apiary_site_location.location ? proposal.apiary_site_location.location.coordinates[0] : 2yy'',
                //longitude: proposal.apiary_site_location ? proposal.apiary_site_location.location.coordinates[1] : '',
                //latitude: -100,
                //longitude: 100,
                showingHelpText: false,
                help_text: 'My Help text ...',
            }
        },
        components: {
            TextField,
            IFrame,
            FileField,
        },
        computed:{
//            readonly: function(){
//                return !this.hasReferralMode && !this.hasAssessorMode ? true : false;
//            },

        },
        watch:{
        },

        methods:{
        },
        mounted: function() {
            let vm = this;
            //vm.form = document.forms.new_proposal;
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

