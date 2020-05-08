<template lang="html">
    <div>
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="modalTitle" large force>
            <div class="container-fluid">
                <div class="row col-sm-12">

                    <div class="form-group"><div class="row">
                        <label class="col-sm-3">Period From</label>
                        <div class="col-sm-4">
                            <div class="input-group date" ref="periodFromDatePicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="on_site_information.period_from" />
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
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="on_site_information.period_to" />
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
//import "jquery-ui/ui/widgets/draggable.js";

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
       // due_date_max: {
       //     type: String,
       //     default: '',
       // },
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
            //this.makeModalsDraggable();
        });
    },
    methods: {
        openMe: function () {
            this.isModalOpen = true;
        },
      //  makeModalsDraggable: function(){
      //      this.elem_modal = $('.modal > .modal-dialog');
      //      for (let i=0; i<this.elem_modal.length; i++){
      //          $(this.elem_modal[i]).draggable();
      //      }
      //  },
        addEventListeners: function () {
            console.log('in addEventListeners');

            let vm = this;
            let el_fr = $(vm.$refs.periodFromDatePicker);
            let el_to = $(vm.$refs.periodToDatePicker);
            let options = { format: "DD/MM/YYYY", showClear: true };

          //  if (vm.due_date_max){
          //      options['maxDate'] = vm.extendMaxDate;
          //  }

           // if (vm.comingDueDate){
           //     // Copy comingDuDate object
           //     let coming_due_date = new Date(vm.comingDueDate.getTime());
           //     // Calculate next day and set it to the datepicker as a minDate
           //     coming_due_date.setDate(coming_due_date.getDate() + 1);
           //     options['minDate'] = coming_due_date;
           //     // Enter a default value to the input box
           //     vm.new_due_date = coming_due_date.getDate() + '/' + (coming_due_date.getMonth() + 1) + '/' + coming_due_date.getFullYear();
           // }

            el_fr.datetimepicker(options);
            el_to.datetimepicker(options);

            el_fr.on("dp.change", function(e) {
                console.log('from changed');
                console.log(e);

                if (el_fr.data("DateTimePicker").date()) {
                    console.log('from if');
                    vm.on_site_information.period_from = e.date.format("DD/MM/YYYY");
                    el_to.data('DateTimePicker').minDate(e.date);
                } else if (el_fr.data("date") === "") {
                    // Date has been cleared
                    vm.on_site_information.period_from = null;
                    el_to.data('DateTimePicker').minDate(false);
                }
            });

            el_to.on("dp.change", function(e) {
                console.log('to changed');
                console.log(e);

                if (el_to.data("DateTimePicker").date()) {
                    console.log('to if');
                    vm.on_site_information.period_to = e.date.format("DD/MM/YYYY");
                    el_fr.data('DateTimePicker').maxDate(e.date);
                } else if (el_to.data("date") === "") {
                    // Date has been cleared
                    vm.on_site_information.period_to = null;
                    el_fr.data('DateTimePicker').maxDate(false);
                }
            });
        },
        ok: async function () {
            try {
                this.processingDetails = true;
                const response = await this.sendData();
                this.close();
                //this.$parent.loadSanctionOutcome({ sanction_outcome_id: this.$parent.sanction_outcome.id });
            } catch (err){
                this.processError(err);
            } finally {
                this.processingDetails = false;
            }
        },
        processError: async function(err) {
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
            let payload = this.on_site_information

            payload.period_from = moment(payload.period_from).format('YYYY-MM-DD');
            payload.period_to = moment(payload.period_to).format('YYYY-MM-DD');
            payload.apiary_site_id = payload.apiary_site.id;

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
