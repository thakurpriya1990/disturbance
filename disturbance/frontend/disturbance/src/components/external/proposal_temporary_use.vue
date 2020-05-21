<template>
    <div class="container" id="externalApproval">
        <div class="row">
            <div class="col-sm-12">
                <div class="row">
                    <FormSection :formCollapse="false" label="Period and Site(s)" Index="period_and_sites">
                        component here
                    </FormSection>
                    <FormSection :formCollapse="false" label="Temporary Occupier" Index="temporary_occupier">
                        component here
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
            }
        },
        components: {
            FormSection,
            datatable,
        },
        computed:{

        },
        watch:{

        },
        methods:{
            loadApiarySiteLocation: async function(id){
                //let temp = await Vue.http.get('/api/proposal_apiary_site_location/' + id + '/on_site_information_list/')
                //this.apiary_site_location = temp.body;
            },
            constructOnSiteInformationTable: function(){
               // console.log('constructOnSiteInformationTable');
               // if (this.apiary_site_location && this.apiary_site_location.on_site_information_list){
               //     console.log('constructOnSiteInformationTable');

               //     // Clear table
               //     this.$refs.on_site_information_table.vmDataTable.clear().draw();

               //     // Construct table
               //     if (this.apiary_site_location.on_site_information_list.length > 0){
               //         for(let i=0; i<this.apiary_site_location.on_site_information_list.length; i++){
               //             this.addOnSiteInformationToTable(this.apiary_site_location.on_site_information_list[i]);
               //         }
               //     }
               // }
            },
            addOnSiteInformationToTable: function(on_site_information) {
                //this.$refs.on_site_information_table.vmDataTable.row.add(on_site_information).draw();
            },
            addEventListeners: function() {
              //  $("#on-site-information-table").on("click", ".delete_on_site_information", this.deleteOnSiteInformation);
              //  $("#on-site-information-table").on("click", ".edit_on_site_information", this.editOnSiteInformation);
            },
        },
        created: function() {
        },
        mounted: function() {
            let vm = this;
            this.$nextTick(() => {
                vm.addEventListeners();
                this.constructOnSiteInformationTable();
            });
        }
    }
</script>

<style lang="css" scoped>

</style>
