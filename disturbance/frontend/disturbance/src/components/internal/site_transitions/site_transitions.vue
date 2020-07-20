<template>
    <div class="container"> 
        <ComponentSiteSelection
            :apiary_sites="apiary_sites"
            :is_internal="true"
            :is_external="false"
            :show_col_checkbox="false"
            :show_action_available_unavailable="false"
            :show_col_status="true"
            :show_col_previous_site_holder="true"
            :key="component_site_selection_key"
            @apiary_sites_updated="apiarySitesUpdated"
        />
    </div>
</template>

<script>
    import ComponentSiteSelection from '@/components/common/apiary/component_site_selection.vue'
    import uuid from 'uuid'
    import Vue from 'vue'

    export default {
        name: 'SiteTransitions',
        data: function(){
            return {
                component_site_selection_key: uuid(),
                apiary_sites: [],
            }
        },
        components: {
            ComponentSiteSelection,
        },
        props: {

        },
        watch: {

        },
        computed: {

        },
        methods: {
            apiarySitesUpdated: function(apiary_sites){
                console.log(apiary_sites)
            },
            loadSites: async function() {
                let vm = this

                Vue.http.get('/api/apiary_site/transitable_sites/').then(re => {
                    console.log(re.body)

                    vm.apiary_sites = re.body
                    this.component_site_selection_key = uuid()

                    ////let temp_use = re.body.apiary_temporary_use
                    //vm.apiary_temporary_use = re.body.apiary_temporary_use
                    //if (vm.apiary_temporary_use.from_date){
                    //    console.log(vm.apiary_temporary_use.from_date);
                    //    vm.apiary_temporary_use.from_date = moment(vm.apiary_temporary_use.from_date, 'YYYY-MM-DD');
                    //    console.log(vm.apiary_temporary_use.from_date);
                    //}
                    //if (vm.apiary_temporary_use.to_date){
                    //    console.log(vm.apiary_temporary_use.to_date);
                    //    vm.apiary_temporary_use.to_date = moment(vm.apiary_temporary_use.to_date, 'YYYY-MM-DD');
                    //    console.log(vm.apiary_temporary_use.to_date);
                    //}

                    //// Update PeriodAndSites component
                    //vm.period_and_sites_key = uuid();
                    //// Update TemporaryOccupier component
                    //vm.temporary_occupier_key = uuid();
                });
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
