<template id="revision_history">
    <div class="row">
        <div class="panel panel-default">
            <div class="panel-heading">
                Revision History
            </div>
            <div class="panel-body panel-collapse">
                <div style="white-space: nowrap;">
                    <div style="float: left; width: 80%;">
                            <table class="table small-table">
                                <tr>
                                    <th>Lodgement</th>
                                    <th>Date</th>
                                    <th>Action</th>
                                </tr>
                                <tr v-for="prop in this.lodgement_revisions" :key="prop.id">
                                    <td>{{ prop.id }}</td>
                                    <td>{{ prop.date | formatDateNoTime }}</td>
                                    <td style="padding: 0px;" v-on:click="getCompareProposal(prop['index'])">
                                        <span v-bind:id=prop.id v-html=prop.action></span>
                                    </td>
                                </tr>
                            </table>

                    </div>
                    <div style="float: right; width: 20%;">
                        <table class="table small-table">
                            <tr>
                                <th>Action</th>
                            </tr>
                            <tr v-for="prop in this.lodgement_revisions" :key="'v_'+prop.id">
                                <td style="padding: 0px;" v-on:click="getViewProposal(prop['index'])">
                                    <span :key="prop.id" v-bind:id=prop.id v-html=prop.action></span>
                                </td>
                            </tr>
                        </table>

                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import {
    api_endpoints,
    helpers
}from '@/utils/hooks'
import Vue from 'vue'
export default {
    name: 'RevisionHistorySection',
    props: {
        logs_url:{
            type: String,
            required: true
        },
        proposal: {
            type: Object,
            required: true
        },
    },
    data() {
        return {
            revisionsTable: null,
            dateFormat: 'DD/MM/YYYY HH:mm:ss',
            lodgement_revisions: [],
            allRevisionsTableRows: '',
            popoversInitialised: false,
            actionsDtOptions: {
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                deferRender: true, 
                autowidth: true,
                order: [[3, 'desc']], // order the non-formatted date as a hidden column
                dom:
                    "<'row'<'col-sm-5'l><'col-sm-6'f>>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'row'<'col-sm-5'i><'col-sm-7'p>>",
                processing: true,
                data: this.lodgement_revisions,
                columns: [
                    { data: 'id' },
                    { data: 'date' },
                    { data: 'action' },
                ],
                order: [],
            },
        }
    },
    components:{
    },
    filters: {
        formatDateNoTime: function(data){
            return data ? moment(data).format('DD/MM/YY'): '';
        },
    },
    watch:{
    },
    computed: {
        getRevisionDiffsUrl: function() {
            let url = ''
            url = helpers.add_endpoint_join('/api/proposal/',
                                            this.proposal.id +
                                            '/get_revision_diffs/')
            return url;
        },
        createLodgementRevisionTable: function() {
            /*
                This creates a table of versions for the current Proposal. Each entry has the Proposal ID along with the revision \
                number and date of submission. An action is provided for each entry to allow comparison between versions.
            */
            index += 1
            let index = 0
            for (let prop in this.proposal.reversion_history) {
                let action_label = '<a style="cursor:pointer;">Compare</a>'
                if (index === 0) { index += 1; continue; } // The first entry is the latest version
                if (index === 1) { action_label = 'Viewing'}
                this.lodgement_revisions.push({"index": index,
                                                "id": prop,
                                                "date": this.proposal.reversion_history[prop]["date"],
                                                "action": action_label})
                index += 1
            }
        },
    },
    methods:{
        getCompareProposal: async function (revision) {
            /* 
                Handle the user clicks. Change the labels of entries and add all selected 
                differences to the DOM.
            */
            let clicked_revision = this.lodgement_revisions[revision-1]
            for (let index = 0; index < this.lodgement_revisions.length; index++) {
                if (revision > 0) {
                    this.lodgement_revisions[index].action = '<a style="cursor:pointer;">Compare</a>'
                    clicked_revision.action = 'Comparing'        // should be non-clickable now

                    // If we are comparing, allow the original to be View(ed).
                    this.lodgement_revisions[0].action = '<a style="cursor:pointer;">View</a>'
                }
            }
            
            // If we click View, show that we are now viewing.
            if (revision == 1) {
                if (this.lodgement_revisions[0].action = 'View') {
                    clicked_revision.action = 'Viewing'
                }
            }

            // Now post to the API to get the differences between latest version and this one.
            const revisions_length = Object.keys(this.proposal.reversion_history).length
            let revision_index = this.lodgement_revisions.length - revision + 2
            const diffs = await Vue.http.post(this.getRevisionDiffsUrl, {"version_number": revision_index})

            // Remove any previous revisions
            $(".revision_note").remove()

            // Find each section that has a revision and append it to that section title.
            for (let entry in diffs.data) {
                for (let k in diffs.data[entry]) {
                    const revision_text = diffs.data[entry][k]
                    if (revision_text == '') {continue;}

                    const replacement = $("#id_" + k ).parent().find('input')

                    if (replacement.attr('type') == "text") {
                        const replacement_html = "<input class='revision_note' style='width: 100%; margin-top: 3px; color: red; border: 1px solid red;' value='" + 
                                                 revision_text + 
                                                 "'><br class='revision_note'>"
                        replacement.after(replacement_html)
                    }
                    else if (replacement.attr('type') == "radio") {
                        const replacement_html = "<input class='revision_note' type='radio' id='radio' checked>" + 
                                                 "<label class='revision_note' for='radio'" +
                                                 "style='margin-top: -200px; text-transform: capitalize; color: red; padding-left: 10px; padding-bottom: 20px;'>" + 
                                                 revision_text +
                                                 "</label><br class='revision_note'>"
                        $("#id_" + k ).parent().after(replacement_html)
                    }
                    else {
                        const replacement_html = "<input class='revision_note' style='width: 100%; margin-top: 3px; padding-top: 0px; color: red; border: 1px solid red;' value='" + 
                                                 revision_text + 
                                                 "'>"

                        $("#id_" + k ).parent().append(replacement_html)
                    }
                }
            }

            // Update the Proposal Page title to show the revision.
            $( "#proposal_title" ).text("Proposal: " + clicked_revision.id)
        },
        getViewProposal: async function (revision) {
            /* 
                Handle the user clicks. Change the labels of entries and add all selected 
                differences to the DOM.
            */
           console.log('--------------getViewProposal-----------------')
            let clicked_revision = this.lodgement_revisions[revision-1]
            for (let index = 0; index < this.lodgement_revisions.length; index++) {
                if (revision > 0) {
                    this.lodgement_revisions[index].action = '<a style="cursor:pointer;">View</a>'
                    clicked_revision.action = 'Viewing'        // should be non-clickable now

                    // // If we are comparing, allow the original to be View(ed).
                    // this.lodgement_revisions[0].action = '<a style="cursor:pointer;">View</a>'
                }
            }
            
            // If we click View, show that we are now viewing.
            if (revision == 1) {
                if (this.lodgement_revisions[0].action = 'View') {
                    clicked_revision.action = 'Viewing'
                }
            }
        },
        initialiseRevisionHistory: function(vm_uid, ref, datatable_options, table, data){
            let vm = this;
            let actionLogId = 'actions-log-table'+vm_uid;
            let popover_name = 'popover-'+ vm._uid+'-logs';
            $(ref).popover({
                content: function() {
                    return ` 
                    <table id="${actionLogId}" class="hover table table-striped table-bordered dt-responsive" cellspacing="0" width="100%">
                        <thead>
                            <tr>
                                <th>Lodgement</th>
                                <th>Date</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                        </tbody>
                    </table>`
                },
                html: true,
                title: 'Action Log',
                container: 'body',
                placement: 'right',
                trigger: "click",
                template: `<div class="popover ${popover_name}" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>`,
            }).on('inserted.bs.popover', function () {
                datatable_options.data = data
                table = $('#'+actionLogId).DataTable(datatable_options);
            });
            // }).on('shown.bs.popover', function () {
            //     var el = ref;
            //     var popoverheight = parseInt($('.'+popover_name).height());

            //     var popover_bounding_top = parseInt($('.'+popover_name)[0].getBoundingClientRect().top);
            //     var popover_bounding_bottom = parseInt($('.'+popover_name)[0].getBoundingClientRect().bottom);

            //     var el_bounding_top = parseInt($(el)[0].getBoundingClientRect().top);
            //     var el_bounding_bottom = parseInt($(el)[0].getBoundingClientRect().top);
                
            //     var diff = el_bounding_top - popover_bounding_top;

            //     var position = parseInt($('.'+popover_name).position().top);
            //     var pos2 = parseInt($(el).position().top) - 5;

            //     var x = diff + 5;
            //     $('.'+popover_name).children('.arrow').css('top', x + 'px');
            // });
        },
        initialisePopovers: function(){ 
            if (!this.popoversInitialised){
                this.initialiseRevisionHistory(this._uid, this.$refs.showActionBtn, this.actionsDtOptions, this.revisionsTable, this.lodgement_revisions);
                this.popoversInitialised = true;
            }
        },
    },
    created: function() {
        // Populate the revision table
        this.createLodgementRevisionTable

    },
    mounted: function(){
        let vm = this;
        this.$nextTick(() => {
            vm.initialisePopovers();
        });
    }
}
</script>
<style scoped>
.top-buffer-s {
    margin-top: 10px;
}
.actionBtn {
    cursor: pointer;
}
</style>
