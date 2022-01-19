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
                        
                    />
                </div>
                <div>  
                     <File :name="map_doc_name" label="Upload Shapefile" :id="map_doc_name"  :isRepeatable="false" :readonly="proposal.readonly"   :proposal_id="proposal.id" :isRequired="true"></File>
                </div>
                <!-- <div>
                    <div class="row">
                        <div class="col-sm-2 pull-right">
                            <input
                                :disabled="valid_button_disabled"
                                @click="validate_map_docs"
                                type="button"
                                value="Validate"
                                class="btn btn-primary w-100"
                            />
                        </div>
                    </div>
                </div> -->
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
                
            }
        },
        components: {
            FileField,
            FormSection,
            ComponentMap,
            File,
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
            valid_button_disabled: function(){
                return false;
            }
        },
        methods:{
            validate_map_docs: function(){
                console.log('here');
            }
            
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

