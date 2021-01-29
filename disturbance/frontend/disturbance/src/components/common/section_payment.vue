<template lang="html">
    <div>
        This is section_payment.vue file
        <FormSection :formCollapse="false" label="Payment" Index="payment_item">
            <div class="form-group row">
                <label class="col-sm-2">Invoice number</label>
                <div class="col-sm-5">
                    <input type="text" class="form-control" placeholder="" id="invoice_number_element" />
                </div>
            </div>
            <div class="form-group row">
                <label class="col-sm-2">Invoice date</label>
                <div class="col-sm-5">
                    <input type="text" class="form-control" placeholder="DD/MM/YYYY" id="invoice_date_element" />
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
        }
    },
    components: {
        FormSection
    },
    computed: {

    },
    methods: {

    },
    created: function(){

    },
    mounted: function(){

    }
}
</script>

<style>
</style>
