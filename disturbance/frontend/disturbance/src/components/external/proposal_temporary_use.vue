<template>
    <div class="container" id="externalApproval">
        <div class="row">
            <div class="col-sm-12">
                <div class="row">

                    <FormSection :formCollapse="false" label="Period and Site(s)" Index="period_and_sites">
                        <PeriodAndSites
                            :is_external=is_external
                            :is_internal=is_internal
                            :from_date="proposal_apiary_temporary_use.from_date"
                            :to_date="proposal_apiary_temporary_use.to_date"
                            :apiary_sites_array="proposal_apiary_temporary_use.apiary_sites"
                            :from_date_enabled="from_date_enabled"
                            :to_date_enabled="to_date_enabled"
                            @from_date_changed="fromDateChanged"
                            @to_date_changed="toDateChanged"
                            @site_checkbox_clicked="siteChechboxClicked"
                        />
                    </FormSection>

                    <FormSection :formCollapse="false" label="Temporary Occupier" Index="temporary_occupier">

                        <TemporaryOccupier
                            :is_external=is_external
                            :is_internal=is_internal
                            :name=proposal_apiary_temporary_use.temporary_occupier_name
                            :phone=proposal_apiary_temporary_use.temporary_occupier_phone
                            :mobile=proposal_apiary_temporary_use.temporary_occupier_mobile
                            :email=proposal_apiary_temporary_use.temporary_occupier_email
                            @contents_changed="occupierDataChanged"
                        />
                    </FormSection>

                    <FormSection :formCollapse="false" label="Deed Poll" Index="deed_poll">
                        <DeedPoll
                        :is_external=is_external
                            :is_internal=is_internal
                            @contents_changed="occupierDataChanged"
                        />
                    </FormSection>

                </div>
            </div>
        </div>

        <div>
            <div class="row" style="margin-bottom: 50px">
                <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                    <div class="navbar-inner">
                        <div class="container">
                            <p class="pull-right" style="margin-top:5px;">
                                <input type="button" @click.prevent="save_exit" class="btn btn-primary" value="Save and Exit"/>
                                <input type="button" @click.prevent="save" class="btn btn-primary" value="Save and Continue"/>
                                <input v-if="!isSubmitting" type="button" @click.prevent="submit" class="btn btn-primary" value="Submit"/>
                                <button v-else disabled class="btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Submitting</button>
                            </p>
                        </div>
                    </div>
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
    import PeriodAndSites from "@/components/common/apiary/section_period_and_sites.vue"
    import TemporaryOccupier from "@/components/common/apiary/section_temporary_occupier.vue"
    import DeedPoll from "@/components/common/apiary/section_deed_poll.vue"

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
                application: null,
                from_date_enabled: true,
                to_date_enabled: true,
                isSubmitting: false,
                proposal_apiary_temporary_use: {
                    from_date: null,
                    to_date: null,
                    temporary_occupier_name: '',
                    temporary_occupier_phone: '',
                    temporary_occupier_mobile: '',
                    temporary_occupier_email: '',
                    apiary_sites: [],
                }
            }
        },
        components: {
            FormSection,
            datatable,
            PeriodAndSites,
            TemporaryOccupier,
            DeedPoll,
        },
        computed:{

        },
        watch:{

        },
        methods:{
            set_data: function() {
                //**********
                // Store test data
                //**********
                this.proposal_apiary_temporary_use.from_date = moment('05/05/2020', 'DD/MM/YYYY');
                this.proposal_apiary_temporary_use.to_date = moment('06/05/2020', 'DD/MM/YYYY');
                this.proposal_apiary_temporary_use.apiary_sites = [
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
                this.proposal_apiary_temporary_use.temporary_occupier_name = 'AHO'
                this.proposal_apiary_temporary_use.temporary_occupier_phone = '12345'
                this.proposal_apiary_temporary_use.temporary_occupier_mobile = '67890'
                this.proposal_apiary_temporary_use.temporary_occupier_email = 'mail@mail.com'
                this.from_date_enabled = false;
                this.to_date_enabled = true;
            },
            save: function(){
                console.log('in save()');
                let proposal_id = 0;
                if (proposal_id){
                    this.proposal_update();
                } else {
                    this.proposal_create();
                }
            },
            save_exit: function() {
                console.log('in save_exit()');
                this.save();
                this.exit();
            },
            submit: function() {
                console.log('in submit');
            },
            exit: function() {
                console.log('in exit()');
            },
            proposal_create: function(){
                console.log('in proposal_create');

                let data = {
                    'category': '',
                    'profile': '', // TODO
                    'district': '',
                    'application': '3',  // TODO retrieve the id of the 'Temporary Use' type
                    'sub_activity2': '',
                    'region': '',
                    'approval_level': '',
                    'behalf_of': '',  // TODO
                    'activity': '',
                    'sub_activity1': '',
                    'proposal_apiary_temporary_use': this.proposal_apiary_temporary_use,
                }

                data.proposal_apiary_temporary_use.from_date = data.proposal_apiary_temporary_use.from_date.format('YYYY-MM-DD')
                data.proposal_apiary_temporary_use.to_date = data.proposal_apiary_temporary_use.to_date.format('YYYY-MM-DD')

                this.$http.post('/api/proposal/', data).then(res=>{
                    swal(
                        'Saved',
                        'Your proposal has been created',
                        'success'
                    );
                },err=>{

                });
            },
            proposal_update: function(){
                console.log('in proposal_update');
                vm.$http.put('/api/proposal/', '').then(res=>{
                    swal(
                        'Saved',
                        'Your proposal has been updated',
                        'success'
                    );
                },err=>{

                });
            },
            occupierDataChanged: function(value){
                this.proposal_apiary_temporary_use.temporary_occupier_name = value.occupier_name
                this.proposal_apiary_temporary_use.temporary_occupier_phone = value.occupier_phone
                this.proposal_apiary_temporary_use.temporary_occupier_mobile = value.occupier_mobile
                this.proposal_apiary_temporary_use.temporary_occupier_email = value.occupier_email
            },
            siteChechboxClicked: function(value){
                console.log('siteChechboxClicked');
                console.log(value);
                for (let item of this.proposal_apiary_temporary_use.apiary_sites){
                    console.log(item);
                    if (item.id == value.apiary_site_id){
                        item.used = value.checked;
                    }
                }
            },
            fromDateChanged: function(value){
                this.proposal_apiary_temporary_use.from_date = moment(value, 'DD/MM/YYYY');
            },
            toDateChanged: function(value){
                this.proposal_apiary_temporary_use.to_date = moment(value, 'DD/MM/YYYY');
            },
            addEventListeners: function() {

            },
        },
        beforeRouteEnter: function(to, from, next) {
            console.log(to);
            console.log(from);

            console.log('licence id: ');
            console.log(to.params.licence_id);

            console.log('application id: ');
            if (to.params.application_id){
                console.log(to.params.application_id);
            } else {
                console.log('not set');
            }

            let vm = this;
            Vue.http.get(`/api/approvals/${to.params.licence_id}.json`).then(res => {
                next(vm => {
                    console.log('res.body');
                    console.log(res.body);
                    vm.proposal = res.body;
                    });
                },
                err => {
                    console.log(err);
                }
            );
        },
        created: function() {
            this.set_data();
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
