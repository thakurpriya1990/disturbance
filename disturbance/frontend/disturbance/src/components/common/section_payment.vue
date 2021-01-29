<template lang="html">
    <div>
        <FormSection :formCollapse="false" label="Payment" Index="payment_item">
            <div class="form-group row">
                <label class="col-sm-2">Invoice number</label>
                <div class="col-sm-3">
                    <input type="text" class="form-control" placeholder="" id="invoice_number_element" v-model="invoice_number" />
                </div>
            </div>
            <div class="form-group row">
                <label class="col-sm-2">Invoice date</label>
                <div class="col-sm-3">
                    <div class="input-group date" ref="invoiceDatePicker">
                        <input type="text" class="form-control" placeholder="DD/MM/YYYY" id="invoice_date_element" />
                        <span class="input-group-addon">
                            <span class="glyphicon glyphicon-calendar"></span>
                        </span>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-sm-2 pull-right">
                    <input
                        :disabled="pay_button_disabled"
                        @click="pay_button_clicked"
                        type="button"
                        value="Pay"
                        class="btn btn-primary"
                    />
                </div>
            </div>
        </FormSection>
    </div>
</template>

<script>
import FormSection from "@/components/forms/section_toggle.vue"
export default {
    name: 'LedgerPay',
    props:{

    },
    data:function () {
        let vm = this;
        return{
            payment_item: '',
            invoice_number: '',
        }
    },
    components: {
        FormSection
    },
    computed: {
        pay_button_disabled: function(){
            if(this.invoice_number){
                return false
            }
            return true
        }
    },
    methods: {
        pay_button_clicked: function(){
            console.log('pay button clicked')
        },
        addEventListeners: function(){
            let vm = this;
            let el_fr = $(vm.$refs.invoiceDatePicker);
            let options = {
                format: "DD/MM/YYYY",
                showClear: true ,
                useCurrent: false,
            };

            el_fr.datetimepicker(options);

            el_fr.on("dp.change", function(e) {
                let selected_date = null;
                if (e.date){
                    // Date selected
                    selected_date = e.date.format('DD/MM/YYYY')  // e.date is moment object
                    vm.period_from = selected_date;
                } else {
                    // Date not selected
                    vm.period_from = selected_date;
                }
                vm.$emit('from_date_changed', vm.period_from)
                //vm.constructApiarySitesTable();
            });
        }
    },
    created: function(){

    },
    mounted: function(){
        let vm = this;
        this.$nextTick(() => {
            vm.addEventListeners();
        });
    }
}
</script>

<style>
</style>
