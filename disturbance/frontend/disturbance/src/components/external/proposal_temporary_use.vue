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
                            :from_date_enabled="from_date_enabled"
                            :to_date_enabled="to_date_enabled"
                            :apiary_sites_array="apiary_sites_array"
                            @from_date_changed="fromDateChanged"
                            @to_date_changed="toDateChanged"
                            @site_checkbox_clicked="siteChechboxClicked"
                        />
                    </FormSection>

                    <FormSection :formCollapse="false" label="Temporary Occupier" Index="temporary_occupier">
                        <TemporaryOccupier 
                            :is_external=is_external 
                            :is_internal=is_internal 
                            :name=name
                            :phone=phone
                            :mobile=mobile
                            :email=email
                            @contents_changed="occupierDataChanged"
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
                proposal: null,
                from_date: null,
                to_date: null,
                apiary_sites_array: [],
                from_date_enabled: true,
                to_date_enabled: true,
                name: '',
                phone: '',
                mobile: '',
                email: '',
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
            occupierDataChanged: function(value){
                console.log('occupierDataChanged');
                console.log(value);
            },
            siteChechboxClicked: function(value){
                console.log('siteChechboxClicked');
                console.log(value);
            },
            fromDateChanged: function(value){
                console.log('fromDateChanged');
                console.log(value);
            },
            toDateChanged: function(value){
                console.log('toDateChanged');
                console.log(value);
            },
            addEventListeners: function() {

            },
        },
        beforeRouteEnter: function(to, from, next) {
            console.log(to);
            console.log(from);
            console.log(next);

            let vm = this;
            Vue.http.get(`/api/proposal/${to.params.proposal_id}.json`).then(res => {
                next(vm => {
                    //vm.loading.push('fetching proposal')
                    vm.proposal = res.body;
                    //vm.loading.splice('fetching proposal', 1);
                    //vm.setdata(vm.proposal.readonly);

                });
            },
            err => {
                console.log(err);
            });
        },
        created: function() {
            //**********
            // Store test data
            //**********
            this.from_date = moment('05/05/2020', 'DD/MM/YYYY');
            this.to_date = moment('06/05/2020', 'DD/MM/YYYY');
            this.apiary_sites_array = [
                {
                    'id': 1,
                    'used': true,
                    'editable': true,
                },
                {
                    'id': 2,
                    'used': false,
                    'editable': false,
                },
                {
                    'id': 3,
                    'used': false,
                    'editable': false,
                },
            ];
            this.from_date_enabled = false;
            this.to_date_enabled = true;
            this.name = 'AHO'
            this.phone = '12345'
            this.mobile = '67890'
            this.email = 'mail@mail.com'
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
