<template>
    <div class="container" id="externalApproval">
        <div class="row">
            <div class="col-sm-12">
                <div class="row">

                    <FormSection :formCollapse="false" label="Period and Site(s)" Index="period_and_sites">
                        <template v-if="licence">
                            <PeriodAndSites 
                                :is_external=is_external 
                                :is_internal=is_internal 
                                :from_date="apiary_temporary_use.from_date"
                                :to_date="apiary_temporary_use.to_date"
                                :apiary_sites_available="apiary_sites_available"
                                :existing_temporary_uses="existing_temporary_uses"
                                :apiary_sites_being_edited="apiary_temporary_use.apiary_sites"
                                :from_date_enabled="from_date_enabled"
                                :to_date_enabled="to_date_enabled"
                                @from_date_changed="fromDateChanged"
                                @to_date_changed="toDateChanged"
                                @site_checkbox_clicked="siteChechboxClicked"
                                :key="period_and_sites_key"
                            />
                        </template>
                    </FormSection>

                    <FormSection :formCollapse="false" label="Temporary Occupier" Index="temporary_occupier">
                        <template v-if="licence">
                            <TemporaryOccupier 
                                :is_external=is_external 
                                :is_internal=is_internal 
                                :name=apiary_temporary_use.temporary_occupier_name
                                :phone=apiary_temporary_use.temporary_occupier_phone
                                :mobile=apiary_temporary_use.temporary_occupier_mobile
                                :email=apiary_temporary_use.temporary_occupier_email
                                @contents_changed="occupierDataChanged"
                                :key="temporary_occupier_key"
                            />
                        </template>
                    </FormSection>

                    <FormSection :formCollapse="false" label="Deed Poll" Index="deed_poll">
                        component here
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
                period_and_sites_key: '',
                temporary_occupier_key: '',
                pBody: 'pBody'+vm._uid,
                licence: null,
                from_date_enabled: true,
                to_date_enabled: true,
                isSubmitting: false,
                apiary_temporary_use: {
                    id: null,
                    from_date: null,
                    to_date: null,
                    temporary_occupier_name: '',
                    temporary_occupier_phone: '',
                    temporary_occupier_mobile: '',
                    temporary_occupier_email: '',
                    apiary_sites: [],
                },
                application: {},
                apiary_sites_available: [],
                existing_temporary_uses: [],
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
            save: function(){
                console.log('in save()');
                if (this.apiary_temporary_use && this.apiary_temporary_use.id){
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

                let vm = this;

                let data = {
                    'category': '',
                    'profile': '', // TODO how to determine this?
                    'district': '',
                    'application': '3',  // TODO Retrieve the id of the 'Temporary Use' type or handle it at the server side 
                                         //      like if there is apiary_temporary_use attribute, it must be a temporary use application, or so.
                    'sub_activity2': '',
                    'region': '',
                    'approval_level': '',
                    'behalf_of': '',  // TODO how to determine this?
                    'activity': '',
                    'sub_activity1': '',
                    'apiary_temporary_use': this.apiary_temporary_use,
                }
                // Add proposal_apiary_base_id
                data['apiary_temporary_use']['proposal_apiary_base_id'] = this.licence.current_proposal.id

                this.$http.post('/api/proposal/', data).then(res=>{
                    console.log(res);
                    let application_id = res.body.id;
                    swal({
                        title: 'Saved',
                        text: 'Your proposal has been created',
                        type: 'success',
                        allowOutsideClick: false,
                    }).then(
                        res=>{
                            // Redirect
                            console.log('Redirect');
                            vm.$router.push({name: 'external-temporary-use', params: {licence_id: vm.licence.id, application_id: application_id}});
                        }, 
                        err=>{
                            // Should not reach here because allowOutsideClick is set to false
                        }
                    );
                },err=>{
                    this.processError(err)
                });
            },
            proposal_update: function(){
                console.log('in proposal_update');
                this.$http.put('/api/proposal/' + this.apiary_temporary_use.id + '/', '{}').then(res=>{
                    swal(
                        'Saved',
                        'Your proposal has been updated',
                        'success'
                    );
                },err=>{

                });
            },
            occupierDataChanged: function(value){
                this.apiary_temporary_use.temporary_occupier_name = value.occupier_name
                this.apiary_temporary_use.temporary_occupier_phone = value.occupier_phone
                this.apiary_temporary_use.temporary_occupier_mobile = value.occupier_mobile
                this.apiary_temporary_use.temporary_occupier_email = value.occupier_email
            },
            siteChechboxClicked: function(value){
                console.log('siteChechboxClicked');
                console.log(value);
                for (let item of this.apiary_temporary_use.apiary_sites){
                    console.log(item);
                    if (item.id == value.apiary_site_id){
                        item.used = value.checked;
                    }
                }
            },
            fromDateChanged: function(value){
                this.apiary_temporary_use.from_date = moment(value, 'DD/MM/YYYY');
            },
            toDateChanged: function(value){
                this.apiary_temporary_use.to_date = moment(value, 'DD/MM/YYYY');
            },
            addEventListeners: function() {

            },
            processError: async function(err){
                console.log('in processError');
                let errorText = '';
                if (err.body.non_field_errors) {
                    // When non field errors raised
                    for (let i=0; i<err.body.non_field_errors.length; i++){
                        errorText += err.body.non_field_errors[i] + '<br />';
                    }
                } else if(Array.isArray(err.body)) {
                    // When general errors raised
                    for (let i=0; i<err.body.length; i++){
                        errorText += err.body[i] + '<br />';
                    }
                } else {
                    // When field errors raised
                    for (let field_name in err.body){
                        if (err.body.hasOwnProperty(field_name)){
                            errorText += field_name + ':<br />';
                            for (let j=0; j<err.body[field_name].length; j++){
                                errorText += err.body[field_name][j] + '<br />';
                            }
                        }
                    }
                }
                await swal("Error", errorText, "error");
            },
        },
        beforeRouteEnter: async function(to, from, next) {
            console.log('in beforeRouteEnter');
            console.log(to);
            console.log(from);

            // Licence
            console.log('licence id: ' + to.params.licence_id);

            let vm = this;
            await Vue.http.get(`/api/approvals/${to.params.licence_id}.json`).then(res => {
                next(vm => {
                        // ProposalApiaryTemporaryUse
                        if (to.params.application_id){
                            console.log('Editing an existing temporary use id: ' + to.params.application_id);
                            Vue.http.get(`/api/proposal/${to.params.application_id}.json`).then(re => {
                                // TODO 
                                console.log('application retrieved:');
                                console.log(re.body.apiary_temporary_use);

                                //vm.apiary_temporary_use = re.body.apiary_temporary_use
                                // User is goint to edit existing application
                                // TODO: load ProposalApiaryTemporaryUse object and set it to the apiary_temporary_use
                                let temp_use = re.body.apiary_temporary_use
                                if (temp_use.from_date){
                                    console.log(temp_use.from_date);
                                    vm.apiary_temporary_use.from_date = moment(temp_use.from_date, 'YYYY-MM-DD');
                                    console.log(vm.apiary_temporary_use.from_date);
                                }
                                if (temp_use.to_date){
                                    console.log(temp_use.to_date);
                                    vm.apiary_temporary_use.to_date = moment(temp_use.to_date, 'YYYY-MM-DD');
                                    console.log(vm.apiary_temporary_use.to_date);
                                }
                                //vm.apiary_temporary_use.to_date = moment('06/05/2020', 'DD/MM/YYYY');
                                vm.apiary_temporary_use.id = temp_use.id
                                vm.apiary_temporary_use.temporary_occupier_name = temp_use.temporary_occupier_name
                                vm.apiary_temporary_use.temporary_occupier_phone = temp_use.temporary_occupier_phone
                                vm.apiary_temporary_use.temporary_occupier_mobile = temp_use.temporary_occupier_mobile
                                vm.apiary_temporary_use.temporary_occupier_email = temp_use.temporary_occupier_email

                                // Update PeriodAndSites component
                                vm.period_and_sites_key = uuid();
                                // Update TemporaryOccupier component
                                vm.temporary_occupier_key = uuid();
                            });
                        } else {
                            console.log('Creating new temporary use');
                        }

                        vm.licence = res.body;
                        for (let i=0; i<vm.licence.current_proposal.proposal_apiary.apiary_sites.length; i++){
                            let site = vm.licence.current_proposal.proposal_apiary.apiary_sites[i];
                            vm.apiary_sites_available.push(site);
                        }
                        for (let j=0; j<vm.licence.current_proposal.apiary_temporary_use_set.length; j++){
                            let temporary_use = vm.licence.current_proposal.apiary_temporary_use_set[j]
                            vm.existing_temporary_uses.push(temporary_use);
                        }
                    });
                },
                err => {
                    console.log(err);
                }
            ).then(res => {
            });
        },
        created: function() {

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
