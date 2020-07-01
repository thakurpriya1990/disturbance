<template lang="html">
    <div>

        Body annual rental fee

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
        },
        watch: {
            occupier_email: function(){
                this.emitContentsChangedEvent();
            },
        },
        data: function(){
            return {
                occupier_email: this.email,  // Copy props to the local variable
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
                    'occupier_name': this.occupier_name,
                    'occupier_phone': this.occupier_phone,
                    'occupier_mobile': this.occupier_mobile,
                    'occupier_email': this.occupier_email,
                });
            },
        },
    }
</script>

<style lang="css" scoped>
</style>
