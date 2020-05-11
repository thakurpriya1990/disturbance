<template lang="html">
    <div>
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="modalTitle" large force>
            <div class="container-fluid">
                <div class="row col-sm-12">

                    <div class="form-group"><div class="row">
                        <label class="col-sm-3">Period From</label>
                        <div class="col-sm-4">
                            <div class="input-group date" ref="periodFromDatePicker">
                                <!-- input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="on_site_information.period_from" / -->
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" />
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                    </div></div>

                    <div class="form-group"><div class="row">
                        <label class="col-sm-3">Period To</label>
                        <div class="col-sm-4">
                            <div class="input-group date" ref="periodToDatePicker">
                                <!-- input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="on_site_information.period_to" / -->
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" />
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                    </div></div>

                    <div class="form-group"><div class="row">
                        <label class="col-sm-3">Site</label>
                        <div class="col-sm-3">
                            <select class="form-control" v-model="on_site_information.apiary_site">
                                <option value=""></option>
                                <option v-for="site in apiary_site_location.apiary_sites" :value="site" :key="site.id">
                                    <span>
                                        {{ site }}
                                    </span>
                                </option>
                            </select>
                        </div>
                    </div></div>

                    <div class="form-group"><div class="row">
                        <label class="col-sm-3">Comments</label>
                        <div class="col-sm-3">
                            <textarea class="form-control" v-model="on_site_information.comments"/>
                        </div>
                    </div></div>

                </div>
            </div>
            <div slot="footer">
                <div v-if="errorResponse" class="form-group">
                    <div class="row">
                        <div class="col-sm-12">
                            <strong>
                                <span style="white-space: pre;" v-html="errorResponse"></span>
                            </strong>
                        </div>
                    </div>
                </div>
                <button type="button" v-if="processingDetails" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i> Adding</button>
                <button type="button" v-else class="btn btn-default" @click="ok">Ok</button>
                <button type="button" class="btn btn-default" @click="cancel">Cancel</button>
            </div>
        </modal>
    </div>
</template>

<script>
import Vue from "vue";
import modal from '@vue-utils/bootstrap-modal.vue';
import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";

export default {
    name: "OnSiteInformationAdd",
    data: function() {
        return {
            processingDetails: false,
            isModalOpen: false,
            errorResponse: '',
            on_site_information: {
                apiary_site: null,
                comments: '',
                period_from: null,
                period_to: null,
            },
        }
    },
    components: {
      modal,
    },
    props:{
        apiary_site_location: {
            type: Object,
        },
    },
    watch:{
        isModalOpen: function() {
            console.log('in isModalOpen');
            console.log(this.isModalOpen);
        }
    },
    computed: {
        modalTitle: function() {
            return 'Add on site info'
        },
    },
    mounted: function () {
        this.$nextTick(() => {
            this.addEventListeners();
        });
    },
    methods: {
        openMe: function () {
            this.isModalOpen = true;
        },
        addEventListeners: function () {
            console.log('in addEventListeners');

            let vm = this;
            let el_fr = $(vm.$refs.periodFromDatePicker);
            let el_to = $(vm.$refs.periodToDatePicker);
            let options = { 
                format: "DD/MM/YYYY", 
                showClear: true ,
                useCurrent: false,
            };

            el_fr.datetimepicker(options);
            el_to.datetimepicker(options);

            el_fr.on("dp.change", function(e) {
                console.log('from changed');
                console.log(e);

                let selected_date = null;
                if (e.date){
                    // Date selected
                    selected_date = e.date.format('DD/MM/YYYY')  // e.date is moment object
                    vm.on_site_information.period_from = selected_date;
                    el_to.data('DateTimePicker').minDate(selected_date);  
                } else {
                    // Date not selected
                    vm.on_site_information.period_from = selected_date;
                    el_to.data('DateTimePicker').minDate(false);  
                }
                console.log('selected_date');
                console.log(selected_date);


               // if (el_fr.data("DateTimePicker").date()) {
               //     console.log('fr-if')
               //     vm.on_site_information.period_from = selected_date;
               //     el_to.data('DateTimePicker').minDate(selected_date);  
               // } else if (el_fr.data("date") === "") {
               //     console.log('fr-else')
               //     // Date has been cleared
               //     vm.on_site_information.period_from = '';
               //     el_to.data('DateTimePicker').minDate(false);
               // }
            });

            el_to.on("dp.change", function(e) {
                console.log('to changed');
                console.log(e);

                let selected_date = null;
                if (e.date){
                    selected_date = e.date.format('DD/MM/YYYY');
                    vm.on_site_information.period_to = selected_date;
                    el_fr.data('DateTimePicker').maxDate(selected_date);
                } else {
                    vm.on_site_information.period_to = '';
                    el_fr.data('DateTimePicker').maxDate(false);
                }
                console.log('selected_date');
                console.log(selected_date);

               // if (el_to.data("DateTimePicker").date()) {
               //     console.log('to-if')
               //     vm.on_site_information.period_to = selected_date;
               //     el_fr.data('DateTimePicker').maxDate(selected_date);
               // } else if (el_to.data("date") === "") {
               //     console.log('to-else')
               //     // Date has been cleared
               //     vm.on_site_information.period_to = '';
               //     el_fr.data('DateTimePicker').maxDate(false);
               // }
            });
        },
        ok: async function () {
            try {
                this.processingDetails = true;
                const response = await this.sendData();
                this.$emit('on_site_information_added');
                this.close();
            } catch (err){
                console.log(err);
                console.log('err');
                this.processError(err);
            } finally {
                this.processingDetails = false;
            }
        },
        processError: async function(err) {
            console.log('in processError');
            console.log(err);
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
                        errorText += field_name + ': ';
                        for (let j=0; j<err.body[field_name].length; j++){
                            errorText += err.body[field_name][j] + '<br />';
                        }
                    }
                }
            }
            this.errorResponse = errorText;
        },
        cancel: async function() {
            this.isModalOpen = false;
            this.close();
        },
        close: function () {
            let vm = this;
            this.isModalOpen = false;
        },
        sendData: async function () {
            let post_url = '/api/on_site_information/'
            let payload = {}
            Object.assign(payload, this.on_site_information);

            // Django only needs apiary_site.id
            try {
                payload.apiary_site_id = payload.apiary_site.id;
            } catch(err) {
                payload.apiary_site_id = 0
            }

            console.log('payload');
            console.log(payload);

            let res = await Vue.http.post(post_url, payload);
            return res
        },
    },
}
</script>

<style>

</style>
