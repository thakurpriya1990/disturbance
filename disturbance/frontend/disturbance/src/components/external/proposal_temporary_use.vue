<template>
    <div class="container" id="externalApproval">
        <div class="row">
            <div class="col-sm-12">
                <div class="row">

                    <FormSection :formCollapse="false" label="Period and Site(s)" Index="period_and_sites">
                        <PeriodAndSites 
                            :is_external=is_external 
                            :is_internal=is_internal 
                            :from_date="from_date"
                            :to_date="to_date"
                            :apiary_sites_array="apiary_sites_array"
                        />
                    </FormSection>

                    <FormSection :formCollapse="false" label="Temporary Occupier" Index="temporary_occupier">
                        <TemporaryOccupier 
                            :is_external=is_external 
                            :is_internal=is_internal 
                        />
                    </FormSection>

                    <FormSection :formCollapse="false" label="Deed Poll" Index="deed_poll">
                        component here
                    </FormSection>

                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import Vue from 'vue'
    import datatable from '@vue-utils/datatable.vue'
    import uuid from 'uuid'
    import { api_endpoints, helpers, } from '@/utils/hooks'
    import FormSection from "@/components/forms/section_toggle.vue"
    import PeriodAndSites from "@/components/common/apiary/period_and_sites.vue"
    import TemporaryOccupier from "@/components/common/apiary/temporary_occupier.vue"

    export default {
        props:{
            is_external:{
              type: Boolean,
              default: false
            },
            is_internal:{
              type: Boolean,
              default: false
            },
        },
        data:function () {
            let vm=this;

            return{
                pBody: 'pBody'+vm._uid,
                from_date: null,
                to_date: null,
            }
        },
        components: {
            FormSection,
            datatable,
            PeriodAndSites,
            TemporaryOccupier,
        },
        computed:{

        },
        watch:{

        },
        methods:{
            addEventListeners: function() {

            },
        },
        created: function() {
            this.from_date = moment('05/05/2020', 'DD/MM/YYYY');
            this.to_date = moment('06/05/2020', 'DD/MM/YYYY');
            this.apiary_sites_array = [];
        },
        mounted: function() {
            let vm = this;
            this.$nextTick(() => {
                vm.addEventListeners();
            });
        }
    }
</script>

<style lang="css" scoped>

</style>
