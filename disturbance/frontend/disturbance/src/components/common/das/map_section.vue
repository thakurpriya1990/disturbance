<template lang="html">
    <div class="">
        <div class="col-md-3">
        </div>
        <div :class="das_sections_classname">
            <FormSection :formCollapse="false" label="Map" Index="1">
                <div class="row col-sm-12">
                    <ComponentMap
                        ref="component_map"
                        :is_internal="is_internal"
                        :is_external="is_external"
                        :can_modify="true"
                        :display_at_time_of_submitted="true"
                        :shapefile_json="shapefile_json"
                        :key="componentMapKey"
                        
                    />
                </div>
                <div>  
                     <File :name="map_doc_name" label="Upload Shapefile" :id="map_doc_id"  :isRepeatable="true" :readonly="proposal.readonly"   :proposal_id="proposal.id" :isRequired="true"></File>
                </div>
                <alert :show.sync="showError" type="danger" style="color: red"><strong>{{errorString}}</strong></alert>
                <div>
                    <div class="row">
                        <div class="col-sm-2">
                            <input
                                :disabled="valid_button_disabled"
                                @click="validate_map_docs"
                                type="button"
                                value="Validate"
                                class="btn btn-primary w-100"
                            />
                        </div>
                        <div class="col-sm-2">
                            <input
                                :disabled="prefill_button_disabled"
                                @click="prefill_proposal"
                                type="button"
                                value="Prefill"
                                class="btn btn-primary w-100"
                            />
                        </div>
                    </div>
                </div>
            </FormSection>  
        </div>
    </div>
</template>

<script>
    import File from '@/components/forms/map_file.vue'
    import FileField from '@/components/forms/filefield_immediate.vue'
    import FormSection from "@/components/forms/section_toggle.vue"
    import ComponentMap from '@/components/common/das/das_component_map.vue'
    import uuid from 'uuid'
    import { api_endpoints, helpers }from '@/utils/hooks'
    import alert from '@vue-utils/alert.vue'
    export default {
        name: 'DASMapSection',
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
            let vm = this;
            return{
                values:null,
                pBody: 'pBody'+vm._uid,
                componentMapKey: 0,
                showError:false,
                errorString:'',
            }
        },
        components: {
            FileField,
            FormSection,
            ComponentMap,
            File,
            alert,
        },
        computed:{
            das_sections_classname: function() {
                // For external page, we need 'col-md-9' classname
                // but not for the internal.
                // This is a hacky way, though...
                if(this.is_internal){
                    return ''
                } else {
                    return 'col-md-9'
                }
            },
            map_doc_name: function(){
                if(this.proposal){
                    return "proposal_"+this.proposal.id+"_map_doc";
                }
                return "proposal_map_doc"
            },
            map_doc_id: function(){
                if(this.proposal){
                    return "proposal_"+this.proposal.id+"_map_doc_id";
                }
                return "proposal_map_doc"
            },
            valid_button_disabled: function(){
                if(this.is_external && this.proposal && !this.proposal.readonly){
                    return false;
                }
                return true;
            },
            shapefile_json: function(){
                return (this.proposal && this.proposal.shapefile_json) ? this.proposal.shapefile_json : {};
            },
            proposal_id: function(){
                return (this.proposal && this.proposal.id) ? this.proposal.id : null;
            },
            prefill_button_disabled: function(){
                if(this.is_external && this.proposal && !this.proposal.readonly && this.proposal.shapefile_json){
                    return false;
                }
                return true;
            },
        },
        methods:{
             incrementComponentMapKey: function() {
                this.componentMapKey++;
            },
            validate_map_docs: function(){
                let vm = this;
                vm.showError=false;
                vm.errorString='';
                
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal.id+'/validate_map_files')).then(res=>{
                    //vm.proposal = res.body;
                    //vm.refreshFromResponse(res);
                    vm.$emit('refreshFromResponse',res);
                    },err=>{
                    console.log(err);
                    vm.showError=true;
                    vm.errorString=helpers.apiVueResourceError(err);
                    });
                vm.$refs.component_map.updateShape();
            },
            prefill_proposal: function(){
                let vm = this;
                vm.showError=false;
                vm.errorString='';
                
                swal({
                    title: "Prefill Proposal",
                    text: "Are you sure you want to prefill this Proposal? Prefilling the proposal will clear all the existing data.",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonText: 'Prefill Proposal',
                    confirmButtonColor:'#d9534f'
                }).then(() => {

                    //vm.prefilling=true;
                    swal({
                            title: "Loading...",
                            //text: "Loading...",
                            allowOutsideClick: false,
                            allowEscapeKey:false,
                            onOpen: () =>{
                                swal.showLoading()
                            }
                    })
                    vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal.id+'/prefill_proposal')).then(res=>{
                    //vm.proposal = res.body;
                    //vm.refreshFromResponse(res);
                    swal.hideLoading();
                    swal.close();
                    vm.$emit('refreshFromResponse',res);
                    //vm.prefilling=false;
                    },err=>{
                    console.log(err);
                    //vm.prefilling=false;
                    vm.showError=true;
                    vm.errorString=helpers.apiVueResourceError(err);
                    });

                },(error) => {
                });
                
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal.id+'/prefill_proposal')).then(res=>{
                    //vm.proposal = res.body;
                    //vm.refreshFromResponse(res);
                    vm.$emit('refreshFromResponse',res);
                    },err=>{
                    console.log(err);
                    vm.showError=true;
                    vm.errorString=helpers.apiVueResourceError(err);
                    });
                //vm.$refs.component_map.updateShape();
            },
            refreshFromResponse:function(response){
                let vm = this;
                vm.original_proposal = helpers.copyObject(response.body);
                vm.proposal = helpers.copyObject(response.body);
                // vm.$refs.component_map.shapefile_json=helpers.copyObject(vm.proposal.shapefile_json);
                //vm.$refs.component_map.updateShape();
            },
            
        },
        created: function() {
        },
        mounted: function() {
            let vm = this;
            
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
    .insurance-items {
        padding-inline-start: 1em;
    }
    .my-container {
        display: flex;
        flex-direction: row;
        align-items: center;
    }
    .grow1 {
        flex-grow: 1;
    }
    .grow2 {
        flex-grow: 2;
    }
    .input-file-wrapper {
        margin: 1.5em 0 0 0;
    }
</style>

