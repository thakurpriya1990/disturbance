<template lang="html">
    <div>

        <div class="form-group row">
            <label class="col-sm-5">Do not charge annual rental fee until</label>
            <div class="col-sm-6">
                <div class="input-group date" ref="periodFromDatePicker">
                    <input type="text" class="form-control" placeholder="DD/MM/YYYY" id="no_charge_until" :readonly="is_readonly"/>
                    <span class="input-group-addon">
                        <span class="glyphicon glyphicon-calendar"></span>
                    </span>
                </div>
            </div>
        </div>

        <div class="form-group row">
            <label class="col-sm-5">Calendar year</label>
            <div class="col-sm-6">
                <select class="form-control" v-model="year_name_selected">
                    <template v-for="annual_rental_fee_period in annual_rental_fee_periods">
                        <option :value="annual_rental_fee_period.year_name" :key="annual_rental_fee_period.id">
                            {{ annual_rental_fee_period.year_name }}
                        </option>
                    </template>
                </select>
            </div>
        </div>

        <div class="form-group row">
            <label class="col-sm-5">Invoice</label>
            <div class="col-sm-6">
                <template v-for="annual_rental_fee_period in annual_rental_fee_periods">
                    <template v-if="annual_rental_fee_period.year_name == year_name_selected">
                        <template v-for="annual_rental_fee in annual_rental_fee_period.annual_rental_fees">
                            <a :href="'/payments/invoice-pdf/' + annual_rental_fee.invoice_reference + '.pdf'" target='_blank'><i style='color:red;' class='fa fa-file-pdf-o'></i> Invoice</a>
                        </template>
                    </template>
                </template>
            </div>
        </div>

    </div>
</template>

<script>
    export default {
        name: 'SectionAnnualRentalFee',
        props:{
            email: {
                type: String,
                default: '',
            },
            is_readonly: {
                type: Boolean,
                default: true,
            },
            no_annual_rental_fee_until: {
                type: String,  // Expect YYYY-MM-DD format
                default: '',
            },
            annual_rental_fee_periods: {
                type: Array,
                default: function(){
                    return []
                }
            }
        },
        watch: {
            occupier_email: function(){
                this.emitContentsChangedEvent();
            },
        },
        data: function(){
            return {
                occupier_email: this.email,  // Copy props to the local variable
                year_name_selected: null,
            }
        },
        created: function(){

        },
        mounted: function(){
            let vm = this;
            this.$nextTick(() => {
                vm.addEventListeners();
            });
        },
        components: {

        },
        computed: {

        },
        methods: {
            addEventListeners: function () {

            },
            emitContentsChangedEvent: function () {
                this.$emit('contents_changed', {
                    'occupier_email': this.occupier_email,
                });
            },
        },
    }
</script>

<style lang="css" scoped>
</style>
