<template id="revision_history">
    <div class="row">
        <div class="panel-body panel-collapse">
            <div style="white-space: nowrap;">
                <div style="float: left; width: 80%;">
                    <table class="table small-table">
                        <tr>
                            <th>Lodgement</th>
                            <th style="padding-left: 10px;">Date</th>
                            <th style="padding-left: 10px;">Action</th>
                        </tr>
                        <tr v-for="prop in this.lodgement_revisions_actions" :key="prop.id">
                            <td>{{ prop.id }}</td>
                            <td style="padding-left: 10px;">{{ prop.date | formatDateNoTime }}</td>
                            <td style="padding-left: 10px;" v-on:click="getCompareProposal(prop['index'])">
                                <span v-bind:id=prop.id v-html=prop.action></span>
                            </td>
                        </tr>
                    </table>
                </div>
                <div style="float: right; width: 20%;">
                    <table class="table small-table">
                        <tr>
                            <th style="visibility: hidden;">Version</th>
                        </tr>
                        <tr v-for="prop in this.lodgement_revisions_view_actions" :key="prop.id">
                            <td  style="padding-left: 15px;" v-on:click="getViewProposal(prop['index'])">
                                <span v-bind:id=prop.view_id v-html=prop.view_action></span>
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
            <a tabindex="2" ref="showActionBtn" class="actionBtn">Show All</a>
        </div>
    </div>
</template>
<script>
import {
    api_endpoints,
    helpers
} from '@/utils/hooks'
import Vue from 'vue'
export default {
    name: 'RevisionHistorySection',
    props: {
        proposal: {
            type: Object,
            required: true
        },
    },
    data() {
        return {
            revisionsTable: null,
            dateFormat: 'DD/MM/YYYY HH:mm:ss',
            lodgement_revisions_actions: [],
            lodgement_revisions_view_actions: [],
            allRevisionsTableRows: '',
            popoversInitialised: false,
            actionsDtOptions: {
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                deferRender: true, 
                autowidth: true,
                dom:
                    "<'row'<'col-sm-5'l><'col-sm-6'f>>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'row'<'col-sm-5'i><'col-sm-7'p>>",
                processing: true,
                data: this.lodgement_revisions_actions,
                data: this.lodgement_revisions_view_actions,
                columns: [
                    { data: 'id' },
                    { data: 'date' },
                    { data: 'action' },
                    { data: 'view_action' },
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
            /* This creates a table of versions for the current Proposal. Each entry has the Proposal ID along with the revision
                number and date of submission. An action is provided for each entry to allow comparison between versions. 
                &#x1f441; is eyeball. Viewing doesn't fit very well. */
            let index = 0
            for (let prop in this.proposal.reversion_history) {
                let action_label = '<a style="cursor:pointer;">Compare</a>'
                let view_action_label = '<a style="cursor:pointer;">View</a>'
                if (index === 0) { 
                    view_action_label = '<div style="pointer-events: none;">&#x1f441;</div>'
                    action_label = '<div style="visibility: hidden; pointer-events: none;">View</div>'
                }
                this.lodgement_revisions_actions.push({"index": index,
                                                       "id": prop,
                                                       "action": action_label,
                                                       "date": this.proposal.reversion_history[prop]["date"],})
                this.lodgement_revisions_view_actions.push({"index": index,
                                                            "view_id": "v_"+prop,
                                                            "view_action": view_action_label})
                index += 1
            }
        },
    },
    methods:{
        getCompareProposal: async function (revision) {
            /* This handles the user clicks. Change the labels of entries and add all selected 
               revision differences to the DOM. */

                // Always Compare against the most recent version. 
               this.getViewProposal(0)

            let clicked_revision = this.lodgement_revisions_actions[revision]

            for (let index = 0; index < this.lodgement_revisions_actions.length; index++) {
                this.lodgement_revisions_actions[index].action = '<a style="cursor:pointer;">Compare</a>'
                clicked_revision.action = '<div>Comparing</div>'        // should be non-clickable now
                this.lodgement_revisions_actions[0].action = '<div style="visibility: hidden;">&#x1f441;</div>'
                this.lodgement_revisions_view_actions[0].view_action = '<div style="">&#x1f441;</div>'
                this.lodgement_revisions_view_actions[index].view_action = '<a style="cursor:pointer;">View</a>'
            }

            // Now post to the API to get the differences between latest version and this one.
            const revisions_length = Object.keys(this.proposal.reversion_history).length
            let revision_index = this.lodgement_revisions_actions.length - revision
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
                        const replacement_html = "<input disabled class='revision_note' style='width: 100%; margin-top: 3px; color: red; border: 1px solid red;' value='" + 
                                                 revision_text + 
                                                 "'><br class='revision_note'>"
                        replacement.after(replacement_html)
                    }
                    else if (replacement.attr('type') == "radio") {
                        const replacement_html = "<input disabled class='revision_note' type='radio' id='radio' checked>" + 
                                                 "<label class='revision_note' for='radio'" +
                                                 "style='margin-top: -200px; text-transform: capitalize; color: red; padding-left: 10px; padding-bottom: 20px;'>" + 
                                                 revision_text +
                                                 "</label><br class='revision_note'>"
                        $("#id_" + k ).parent().after(replacement_html)
                    }
                    else {
                        const replacement_html = "<input disabled class='revision_note' style='width: 100%; margin-top: 3px; padding-top: 0px; color: red; border: 1px solid red;' value='" + 
                                                 revision_text + 
                                                 "'>"

                        $("#id_" + k ).parent().append(replacement_html)
                    }
                }
            }
        },
        getViewProposal: async function (revision) {
            /* Handle the user clicks. Change the labels of entries and ask the page to be redrawn with 
               the selected revision. */
            
            let clicked_revision = this.lodgement_revisions_view_actions[revision]
            // Set initial values for the View table.
            for (let index = 0; index < this.lodgement_revisions_view_actions.length; index++) {
                this.lodgement_revisions_view_actions[index].view_action = '<a style="visibility: visible; cursor:pointer;">View</a>'
                clicked_revision.view_action = '<div style="">&#x1f441;</div>'
                this.lodgement_revisions_actions[0].action = '<div style="visibility: hidden;">&#x1f441;</div>'
                this.lodgement_revisions_actions[index].action = '<a style="cursor:pointer;">Compare</a>'
            }
            // Update the Proposal Page title to show the revision.
            if (clicked_revision.view_id.split('-')[1] == this.lodgement_revisions_view_actions.length) {                
                $( "#proposal_title" ).text("Proposal: " + clicked_revision.view_id.split('-')[0].replace('v_', ''))
            }
            else {
                $( "#proposal_title" ).text("Proposal: " + clicked_revision.view_id.replace('v_', ''))
            }

            await this.$emit("reversion_proposal", revision)
        },
        initialiseRevisionHistoryPopover: function(vm_uid, ref, datatable_options, actions, view_actions){
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
                                <th>View</th>
                            </tr>
                        </thead>
                        <tbody>
                        </tbody>
                    </table>`
                },
                html: true,
                title: 'Revision Log',
                container: 'body',
                placement: 'right',
                trigger: "click",
                template: `<div class="popover ${popover_name}" role="tooltip">
                                <div class="arrow"></div>
                                    <h3 class="popover-title"></h3>
                                        <div class="popover-content">
                                </div>
                          </div>`,
            }).on('inserted.bs.popover', function () {
                let data_for_table = []
                // Get the required combination of values from action and view action arrays.
                for (let row_count in actions) {
                    const formatted_date = moment(actions[row_count]['date']).format('DD/MM/YY HH:mm:ss');
                    data_for_table.push({"index": row_count,
                                         "id": actions[row_count]['id'],
                                         "action": actions[row_count]['action'],
                                         "view_action": view_actions[row_count]['view_action'],
                                         "date": formatted_date,})
                }
                datatable_options.data = data_for_table
                let table = $('#'+actionLogId).DataTable(datatable_options);
            }).on('shown.bs.popover', function () {
                var el = ref;
                var popoverheight = parseInt($('.'+popover_name).height());

                var popover_bounding_top = parseInt($('.'+popover_name)[0].getBoundingClientRect().top);
                var popover_bounding_bottom = parseInt($('.'+popover_name)[0].getBoundingClientRect().bottom);

                var el_bounding_top = parseInt($(el)[0].getBoundingClientRect().top);
                var el_bounding_bottom = parseInt($(el)[0].getBoundingClientRect().top);
                
                var diff = el_bounding_top - popover_bounding_top;

                var position = parseInt($('.'+popover_name).position().top);
                var pos2 = parseInt($(el).position().top) - 5;

                var x = diff + 5;
                $('.'+popover_name).children('.arrow').css('top', x + 'px');
            });
        },
        initialisePopovers: function(){ 
            if (!this.popoversInitialised){
                this.initialiseRevisionHistoryPopover(this._uid, 
                                                      this.$refs.showActionBtn, 
                                                      this.actionsDtOptions, 
                                                      this.lodgement_revisions_actions,
                                                      this.lodgement_revisions_view_actions);
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
