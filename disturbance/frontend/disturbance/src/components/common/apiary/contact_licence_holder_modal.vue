<template lang="html">
    <div>
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="modalTitle" large force>
            Enter information that will be emailed to the site licence holder. Please ensure your contact details are included if you want to be contacted by the site licence holder.
            <div>
                <textarea />
            </div>
        </modal>
    </div>
</template>

<script>
    import Vue from "vue";
    import modal from '@vue-utils/bootstrap-modal.vue';
    import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";

    export default {
        name: "ContactLicenceHolderModal",
        data: function() {
            return {
                processingDetails: false,
                isModalOpen: false,  // This is accessed by the 'modal' component directly by this.$parent.close();
                errorResponse: '',
                apiary_site_id: null,
            }
        },
        components: {
          modal,
        },
        watch:{
            isModalOpen: function() {
                console.log('in isModalOpen');
                console.log(this.isModalOpen);
            }
        },
        computed: {
            modalTitle: function() {
                return 'Contact Licence Holder'
            },
        },
        mounted: function () {
            this.$nextTick(() => {
                this.addEventListeners();
            });
        },
        created: function() {
            console.log('in created')
        },
        methods: {
            openMe: function () {
                console.log('in openMe')
                this.isModalOpen = true
            },
            addEventListeners: function () {

            },
            ok: async function () {
                console.log('ok')
            },
            processError: async function(err) {

            },
            cancel: async function() {
                console.log('cancel')
                this.isModalOpen = false;
                this.close();
            },
            // This function is directly accessed by the child component 'modal' 
            close: function () {
                let vm = this;
                this.isModalOpen = false;
            },
            sendData: async function () {

            },
        },
    }
</script>

<style>

</style>
