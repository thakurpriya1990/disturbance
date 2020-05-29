<template lang="html">
    <div>

        <div class="panel-body collapse in" id="deedPoll">
            <div class="row">
                <div class="col-sm-12">
                    <label>Print <a :href="deed_poll_url" target="_blank">the deed poll</a>, sign it, have it witnessed and attach it to this application.</label>
                </div>
            </div>
             <div class="row">
                <div class="col-sm-12">
                    <FileField :proposal_id="proposal.id" :isRepeatable="false" name="deed_poll" :id="'proposal'+proposal.id" :readonly="proposal.readonly" ref="deed_poll_doc"></FileField>
                </div>
             </div>
         </div>

    </div>
</template>

<script>

    import FileField from '@/components/forms/filefield.vue'

    export default {

        watch: {
            occupier_name: function(){
                this.emitContentsChangedEvent();
            },
            occupier_phone: function(){
                this.emitContentsChangedEvent();
            },
            occupier_mobile: function(){
                this.emitContentsChangedEvent();
            },
            occupier_email: function(){
                this.emitContentsChangedEvent();
            },
        },
        data: function(){
            return{
                occupier_name: '',
                occupier_phone: '',
                occupier_mobile: '',
                occupier_email: '',
            }
        },
        created: function(){
            this.occupier_name = this.name;
            this.occupier_phone = this.phone;
            this.occupier_mobile = this.mobile;
            this.occupier_email = this.email;
        },
        mounted: function(){
            let vm = this;
            this.$nextTick(() => {
                vm.addEventListeners();
            });
        },
        components: {
          FileField,
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
