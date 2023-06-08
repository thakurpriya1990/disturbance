<template lang="html">
  <div id="spatialQueryQuestion">

    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Spatial Query Questions
                        <a :href="'#'+pSpatialQueryQuestionBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pSpatialQueryQuestionBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pSpatialQueryQuestionBody">

                    <div class="row">
                        <div class="col-md-12">
                            <button class="btn btn-primary pull-right" @click.prevent="addTableEntry()" name="add-spatialquery">New Question</button>
                        </div>
                    </div>
                    <div class="row"><br/></div> 
                    <div class="row">
                        <div class="col-md-12">
                            <div class="form-group">
                                <!--{{profile}}-->

                                <datatable ref="spatial_query_question_table"
                                    :id="spatial_query_question_id" 
                                    :dtOptions="dtOptionsSpatialQueryQuestion"
                                    :dtHeaders="dtHeadersSpatialQueryQuestion" 
                                />

                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div v-if="showQuestionModal">
    <modal transition="modal fade" @ok="ok()" title="Spatial Query Question" large>
        <div class="container-fluid">
            <div id="error" v-if="missing_fields.length > 0" style="margin: 10px; padding: 5px; color: red; border:1px solid red;">
                <b>Please answer the following mandatory question(s):</b>
                <ul>
                    <li v-for="error in missing_fields">
                        {{ error.label }}
                    </li>
                </ul>
            </div>
            <div>
                <form class="form-horizontal" name="spatial_query_question">
                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Question</label>
                        </div>
                        <div class="col-md-9">
                            <input class="form-control" name="layer_name" v-model="spatialquery.question"></input>
                        </div>
                    </div>

                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Answer</label>
                        </div>
                        <div class="col-md-9">
                            <input class="form-control" name="layer_url" v-model="spatialquery.answer_mlq"></input>
                        </div>
                    </div>

                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Layer name</label>
                        </div>
                        <div class="col-md-9">
                            <input class="form-control" name="layer_name" v-model="spatialquery.layer_name"></input>
                        </div>
                    </div>

                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Layer url</label>
                        </div>
                        <div class="col-md-9">
                            <input class="form-control" name="layer_url" v-model="spatialquery.layer_url"></input>
                        </div>
                    </div>

                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >CDDP Group</label>
                        </div>
                        <div class="col-md-3">
                           {{spatialquery.group}}
                            <select class="form-control" ref="select_group" name="select-group" v-model="spatialquery.group.id">
                                <option v-for="group in spatialquery_selects.cddp_groups" :value="group.id" >{{group.name}}</option>
                                <!--<option v-for="(g, gid) in spatialquery_selects.cddp_groups" :value="g.id" v-bind:key="`purpose_${gid}`">{{g.name}}</option> -->
                            </select>     
                        </div>
                    </div>


                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Expiry</label>
                        </div>
                        <div class="col-md-3">
                            <input type="date" class="form-control" name="expiry" v-model="spatialquery.expiry"></input>
                        </div>
                        <div class="col-md-6"></div>
                    </div>

                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div>
                        <div class="row">
                            <div class="col-md-3"></div>
                            <div class="col-md-3">
                                <label class="control-label pull-left" >Visible to proponent</label>
                            </div>
                            <div class="col-md-3">
                                <label class="control-label pull-left" >Buffer (metres)</label>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-3"></div>
                            <div class="col-md-3">
                                <input type="radio" id="visible_to_proponent_yes" name="visible_to_proponent" value="true" v-model="spatialquery.visible_to_proponent">
                                <label for="visible_to_proponent_yes">Yes</label>&nbsp;&nbsp;&nbsp;
                                <input type="radio" id="visible_to_proponent_no" name="visible_to_proponent" value="false" v-model="spatialquery.visible_to_proponent">
                                <label for="visible_to_proponent_no">No</label>


                            </div>
                            <div class="col-md-3">
                                <input type="number" min="0" class="form-control" name="buffer" v-model="spatialquery.buffer"></input>
                            </div>
                        </div>
                    </div>


                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Intersection operator</label>
                        </div>
                        <div class="col-md-3">
                            <select class="form-control" ref="select_how" name="select-how" v-model="spatialquery.how">
                                <option v-for="operator in spatialquery_selects.how" :value="operator.value" >{{operator.label}}</option>
                            </select>     
                        </div>
                    </div>

                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div>
                        <div class="row">
                            <div class="col-md-3"></div>
                            <div class="col-md-3">
                                <label class="control-label pull-left" >Column name</label>
                            </div>
                            <div class="col-md-3">
                                <label class="control-label pull-left" >Operator</label>
                            </div>
                            <div class="col-md-3">
                                <label class="control-label pull-left" >Value</label>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-3"></div>
                            <div class="col-md-3">
                                <input type="text" class="form-control" name="column_name" v-model="spatialquery.column_name" style="width:100%;"></input>
                            </div>
                            <div class="col-md-3">
                                <select class="form-control" ref="select_operator" name="select-operator" v-model="spatialquery.operator">
                                    <option v-for="operator in spatialquery_selects.operators" :value="operator.value" >{{operator.label}}</option>
                                </select>     
                            </div>
                            <div class="col-md-3">
                                <input type="text" class="form-control" name="value" v-model="spatialquery.value" style="width:100%;"></input>
                            </div>
                        </div>
                    </div>

                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Prefix answer</label>
                        </div>
                        <div class="col-md-9">
                            <input type="text" class="form-control" name="prefix_answer" v-model="spatialquery.prefix_answer"></input>
                        </div>
                    </div>

                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" style="text-align: left;">Number of polygons to process (Proponent)</label>
                        </div>
                        <div class="col-md-3">
                            <input type="number" min="-1" class="form-control" name="no_polygons_proponent" v-model="spatialquery.no_polygons_proponent"></input>
                        </div>
                    </div>

                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Answer</label>
                        </div>
                        <div class="col-md-9">
                            <input type="text" class="form-control" name="answer" v-model="spatialquery.answer"></input>
                        </div>
                    </div>

                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Prefix info</label>
                        </div>
                        <div class="col-md-9">
                            <input type="text" class="form-control" name="prefix_info" v-model="spatialquery.prefix_info"></input>
                        </div>
                    </div>

                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" style="text-align: left;">Number of polygons to process (Assessor)</label>
                        </div>
                        <div class="col-md-3">
                            <input type="number" min="-1" class="form-control" name="no_polygons_assessor" v-model="spatialquery.no_polygons_assessor"></input>
                        </div>
                    </div>

                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Info for assessor</label>
                        </div>
                        <div class="col-md-9">
                            <input type="text" class="form-control" name="assessor_info" v-model="spatialquery.assessor_info"></input>
                        </div>
                    </div>

                </form>
            </div>
        </div>
        <div slot="footer">
            <button type="button" class="btn btn-primary" @click="saveSpatialquery()">Save</button>
        </div>
    </modal>
    </div>

    <div v-else-if="showTestModal">
    <modal id="test-id"  @ok.prevent="ok()" title="Spatial Query Question - Test" large>
        <div class="container-fluid">
            <div id="error" v-if="missing_fields.length > 0" style="margin: 10px; padding: 5px; color: red; border:1px solid red;">
                <b>Please answer the following mandatory question(s):</b>
                <ul>
                    <li v-for="error in missing_fields">
                        {{ error.label }}
                    </li>
                </ul>
            </div>
            <div>
                <form class="form-horizontal" name="proposal_id">
                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left">Proposal Lodgement No.</label>
                        </div>
                        <div class="col-md-2">
                            <input class="form-control" name="layer_name" placeholder="P000123" v-model="proposal.lodgement_number"></input>
                        </div>
                        <div class="col-md-2">
                            <label class="control-label pull-right">Grouped MLQ's</label>
                            <label class="control-label pull-right">All MLQ's</label>
                        </div>
                        <div class="col-md-1">
                            <input class="med" type="checkbox" id="group_mlqs" name="group_mlqs" title="Request non-expired Grouped MasterList Questions (grouped by Radiobutton, Checkbox, Select, Multiselect)" v-model="proposal.group_mlqs"><br>
                            <input class="med" type="checkbox" id="all_mlqs" name="all_mlqs" title="Request with all non-expired MasterList Questions" v-model="proposal.all_mlqs">
                        </div>
                        <div v-if="request_time" class="col-md-4">
                            <p><b>Request Time:   </b> {{request_time}}ms</p>
                            <p><b>No. Questions:  </b> {{num_questions}}</p>
                            <p><b>Layers Utilised:</b> {{num_layers_utilised}}</p>
                        </div>

                    </div>
                </form>
                <textarea id="output" cols="100" rows="35" v-model="sqs_response"></textarea>
            </div>
        </div>
        <div slot="footer">
            <!--
            <button type="button" style="bckground-color: red;" v-if="requesting" disabled class="btn btn-default" @click="test_spatialquery()"><i class="fa fa-spinner fa-spin"></i> Processing</button>
            <button type="button" v-else class="btn btn-primary" @click="test_spatialquery()">Test</button>
            -->
            <!--
            <button type="button" class="btn btn-primary" @click="test_spatialquery()">Test</button>
            -->
            <!--
            <button type="button" style="background-color: red;" v-if="requesting" class="btn btn-default" @click="test_spatialquery()"><i class="fa fa-spinner fa-spin"></i> Processing</button>
            -->
            <button type="button" v-if="requesting" class="btn btn-default" @click="test_spatialquery()"><i class="fa fa-spinner fa-spin"></i> Processing</button>
            <button type="button" v-else class="btn btn-primary" @click="test_spatialquery()">Test</button>
        </div>
    </modal>
    </div>

  </div>
</template>

<script>
import Vue from 'vue'
import datatable from '@/utils/vue/datatable.vue'
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
import SchemaOption from './schema_add_option.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
    name:'spatialQueryQuestionModal',
    components: {
        modal,
        alert,
        datatable,
        SchemaOption,
    },
    props:{
    },
    data:function () {
        let vm = this;
        vm.spatial_query_question_url = helpers.add_endpoint_join(api_endpoints.spatial_query_paginated, 'spatial_query_question_datatable_list/?format=datatables');
//        vm.proposal = {
//            lodgement_number: '',
//            masterlist_question_id: '',
//            group_mlqs: true,
//            all_mlqs: false,
//        };
        //vm.proposal.group_mlqs=true;


        return {
            spatial_query_question_id: 'spatial-query-question-datatable-'+vm._uid,
            pSpatialQueryQuestionBody: 'pSpatialQueryQuestionBody' + vm._uid,
            pOptionBody: 'pOptionBody' + vm._uid,
            pHeaderBody: 'pHeaderBody' + vm._uid,
            pExpanderBody: 'pOptionBody' + vm._uid,
            filterOptions: '',
            isModalOpen:false,
            spatialquery_selects: [],
            missing_fields: [],
            question_id: Number,
            showQuestionModal: false,
            showTestModal: false,
            showTestJsonResponse: false,
            sqs_response: false,
            requesting: false,
            request_time: null,
            num_questions: null,
            num_layers_utilised: null,
            profile: {},

            dtHeadersSpatialQueryQuestion: ["ID", "Question", "Answer Option", "Visible to proponent", "Buffer (m)", "Layer name", "Group", "Overlapping/Outside", "Column", "Operator", "Value", "Layer URL", "Expiry", "Prefix Answer", "Number of polygons (Proponent)", "Answer", "Prefix Info", "Number of polygons (Assessor)", "Assessor Info", "Regions", "Action"],
            dtOptionsSpatialQueryQuestion:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                serverSide: true,
                autowidth: false,
                processing: true,
                ajax: {
                    "url": vm.spatial_query_question_url, 
                    data: function (data) {
                      // needed because the datatables url GET length was too long - browser returned an error - jm
                      // eg. http://localhost:8000/api/spatial_query_paginated/spatial_query_question_datatable_list/?format=datatables&draw=1&length=1
                      for (var i = 10, len = data.columns.length; i < len; i++) {
                        delete data.columns[i].search;
                        delete data.columns[i].searchable;
                        delete data.columns[i].orderable;
                        delete data.columns[i].name;
                      }
                      //delete data.search.regex;
                    }
                },
                columnDefs: [
                    //{ visible: false, targets: [ 3, 5, 6] } 
                    //{ visible: false, targets: [ 3, 6] } 
                    //{ orderable: false, targets: [ 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19] } 
                ],
                columns: [
                    { 
                        data: "id",
                        visible: false,
                    },
                    { 
                        data: "question",
                        width: "80%",
                        mRender:function (data,type,full) {
                            var ellipsis = '...',
                                truncated = _.truncate(data, {
                                    length: 100,
                                    omission: ellipsis,
                                    separator: ' '
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template('<a href="#" ' +
                                    'role="button" ' +
                                    'data-toggle="popover" ' +
                                    'data-trigger="click" ' +
                                    'data-placement="top auto"' +
                                    'data-html="true" ' +
                                    'data-content="<%= text %>" ' +
                                    '>more</a>');
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: data
                                });
                            }

                            return result
                        },
                        'createdCell': helpers.dtPopoverCellFn,
                    },
                    { 
                        data: "answer_mlq",
                    },
                                        { 
                        data: "visible_to_proponent",
                    },
                    { 
                        data: "buffer",
                    },

                    //{ 
                    //    data: "layer",
                    //},
                    { 
                        data: "layer_name",
                    },
                    { 
                        data: "group.name",
                    },
                    { 
                        data: "how",
                    },
                    { 
                        data: "column_name",
                    },
                    { 
                        data: "operator",
                    },
                    { 
                        data: "value",
                    },

                    { 
                        data: "layer_url",
                        visible: false,
                    },
                    { 
                        data: "expiry",
                        visible: false,
                    },
                    { 
                        data: "prefix_answer",
                        visible: false,
                    },
                    { 
                        data: "no_polygons_proponent",
                        visible: false,
                    },
                    { 
                        data: "answer",
                        visible: false,
                    },
                    { 
                        data: "prefix_info",
                        visible: false,
                    },
                    { 
                        data: "no_polygons_assessor",
                        visible: false,
                    },
                    { 
                        data: "assessor_info",
                        visible: false,
                    },
                    { 
                        data: "regions",
                        visible: false,
                    },

                    { 
                        data: "id",
                        width: "10%",
                        mRender:function (data,type,full) {
                            var column = `<a class="edit-row" data-rowid=\"__ROWID__\">Edit</a><br/>`;
                            column += `<a class="delete-row" data-rowid=\"__ROWID__\">Delete</a><br/>`;
                            column += `<a class="test-row" data-rowid=\"__ROWID__\">Test</a><br/>`;
                            return column.replace(/__ROWID__/g, full.id);
                        }
                    },
                ],
                rowId: function(_data) {
                    return _data.id
                },
                initComplete: function () {
                    var $searchInput = $('div.dataTables_filter input');
                    $searchInput.unbind('keyup search input');
                    $searchInput.bind('keypress', (vm.delay(function(e) {
                        if (e.which == 13) {
                            vm.$refs.spatial_query_question_table.vmDataTable.search( this.value ).draw();
                        }
                    }, 0)));
                }
            },
            spatialquery: {
                id: '',
                name: '',
                question: '',
                answer_type: '',
                options: null,
                headers: null,
                expanders: null,
                help_text: '',
                help_text_assessor:'',
                help_text_url: false,
                help_text_assessor_url: false,
            },
            proposal: {
                lodgement_number: '',
                masterlist_question_id: '',
                group_mlqs: true,
                all_mlqs: false,
            },

            answerTypes: [],
            addedHeaders: [],
            addedHeader: {
                label: '',
                value: ''
            },
            addedExpanders: [],
            addedExpander: {
                label: '',
                value: '',
            },
            showOptions: false,
            showTables: false,
            addedOptions: [],
            addedOption: {
                id: '',
                label: '',
                value: '',
            },
            isNewEntry: false,
        }

    },
    watch:{
    },
    computed: {
        isHelptextUrl: function () {
            return this.spatialquery? this.spatialquery.help_text_url: false;
        },
        isHelptextAssessorUrl: function () {
            return this.spatialquery? this.spatialquery.help_text_assessor_url : false;
        },
        csrf_token: function() {
            return helpers.getCookie('csrftoken')
        },
        group_mlqs: function() {
            return this.proposal.group_mlqs
        },
    },
    methods: {
        has_test_form_errors: function () {
            if (!this.proposal.lodgement_number) {
                this.missing_fields.push({'label':'Proposal lodgement number required (eg. P000123)'});
            }

            if (this.missing_fields.length>0) {
                return true;
            } 
            return false
        },

        pretty: function(value) {
            //return JSON.stringify(JSON.parse(value), null, 2);
            return JSON.stringify(JSON.parse(value), null, 2);
        },
        selected_question: function(selected_id) {
            return this.spatialquery_selects.all_masterlist.find( t => t.id === selected_id );
        },
        has_options: function(selected_id) {
            return this.selected_question(selected_id).option.length > 0;
        },
        delay(callback, ms) {
            var timer = 0;
            return function () {
                var context = this, args = arguments;
                clearTimeout(timer);
                timer = setTimeout(function () {
                    callback.apply(context, args);
                }, ms || 0);
            };
        },
        setShowAdditional: function(selected_id) {
            const table = ['expander_table']
            const option = ['radiobuttons', 'checkbox', 'select', 'multi-select']
            const q_type = this.answerTypes.find( t => t.value === selected_id && (table.includes(t.value) || option.includes(t.value)))

            this.showOptions = q_type && option.includes(q_type.value) ? true : false
            this.showTables = q_type && table.includes(q_type.value) ? true : false

            if (this.showOptions && this.isNewEntry) {
                this.addedOption.id = ''
                this.addedOption.label = ''
                this.addedOption.value = ''
                let newOption = Object.assign(this.addedOption)
                this.addedOptions.push(newOption);          
            }

            if (this.showTables && this.isNewEntry) {
                let newHeader = Object.assign(this.addedHeader)
                this.addedHeaders.push(newHeader);
                let newExpander = Object.assign(this.addedExpander)
                this.addedExpanders.push(newExpander);           
            }
        },
        addOption: function() {
            this.addedOptions.push(Object.assign(this.addedOption))
        },
        addHeader: function() {
            this.addedHeaders.push(Object.assign(this.addedHeader))
        },
        addExpander: function() {
            this.addedExpanders.push(Object.assign(this.addedExpander))
        },
        close: function() {
            const self = this;

            if (!self.errors) {
                $(this.$refs.select_answer_type).val(null).trigger('change');
                $('.has-error').removeClass('has-error');
                let header_name = 'header-answer-type-0'
                $(`[name='${header_name}]`).removeClass('header-answer-type-0')
                self.addedOptions = [];
                self.addedHeaders = [];
                self.addedExpanders = [];

                self.showOptions = false;
                self.showTables = false;
                self.isModalOpen = false;
                self.showQuestionModel = false;
                self.showTestModel = false;
                self.showTestJsonResponse = false;

                self.request_time = null;
                self.num_questions = null;
                self.num_layers_utilised = null;
            }
        },
        saveSpatialquery: async function() {
            const self = this;
            const data = self.spatialquery;
            this.missing_fields = [];
             
            if (self.has_form_errors()) {
                self.isModalOpen = true;
                return;
            }

            if (data.id === '') {
                console.log(data);

                await self.$http.post(api_endpoints.spatial_query, JSON.stringify(data),{
                    emulateJSON:true
                }).then((response) => {
                    self.$refs.spatial_query_question_table.vmDataTable.ajax.reload();
                    self.close();
                }, (error) => {
                    swal(
                        'Save Error',
                        helpers.apiVueResourceError(error),
                        'error'
                    )
                });

            } else {

                data.group = data.group.id;

                await self.$http.post(helpers.add_endpoint_json(api_endpoints.spatial_query,data.id+'/save_spatialquery'),JSON.stringify(data),{
                        emulateJSON:true,
                }).then((response)=>{
                    self.$refs.spatial_query_question_table.vmDataTable.ajax.reload();
                    self.close();
                },(error)=>{
                    console.log('Error: ' + JSON.stringify(error))
                    swal(
                        'Save Error',
                        helpers.apiVueResourceError(error),
                        'error'
                    )
                });

            }
            this.isNewEntry = false;
        },
        test_spatialquery: async function(e) {
            //e.preventDefault();
            const self = this;
            const data = self.proposal;
            data['csrfmiddlewaretoken'] = self.csrf_token
            this.missing_fields = [];
             
            if (self.has_test_form_errors()) {
                self.isModalOpen = true;
                return;
            }

            let url = self.proposal.all_mlqs ? '/sqs_data' : '/sqs_data_single'
            const start_time = new Date()
            self.requesting = true;
            self.request_time = null;
            self.num_questions = null;
            self.num_layers_utilised = null;
            const uniq = (items) => [...new Set(items)];

            console.log(helpers.add_endpoint_json(api_endpoints.proposals,self.proposal.lodgement_number + url));
            await self.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,self.proposal.lodgement_number + url),JSON.stringify(data),{
                    emulateJSON:true,
            }).then((response)=>{
                //self.isModalOpen = true;
                console.log('Response: ' + JSON.stringify(response));
                self.sqs_response = JSON.stringify(response.body, null, 4);
                //self.sqs_response = response;
                //self.showTestJsonResponse = true;
                //self.showTestModal = false;
                self.isModalOpen = true;
                //self.close();
                self.requesting = false;
                self.num_questions = response.body['layer_data'].length;
                self.num_layers_utilised = uniq(response.body['layer_data'].map((item) => item.layer_name)).length // unique layers used
            },(error)=>{
                console.log('Error: ' + JSON.stringify(error))
                swal(
                    'Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });

            self.request_time = new Date() - start_time
            this.isNewEntry = false;
        },

        has_form_errors: function () {
            console.log
            if (!this.spatialquery.question) { this.missing_fields.push({'label':'Question field is required'}); }
            if (!this.spatialquery.answer_mlq) { this.missing_fields.push({'label':'Answer field is required'}); }
            if (!this.spatialquery.layer_name) { this.missing_fields.push({'label':'Layer Name field is required'}); }
            if (!this.spatialquery.layer_url) { this.missing_fields.push({'label':'Layer URL field is required'}); }
            if (!this.spatialquery.group) { this.missing_fields.push({'label':'CDDP Group field is required'}); }
            if (!this.spatialquery.how) { this.missing_fields.push({'label':'Intersector operator field is required'}); }
            if (!this.spatialquery.column_name) { this.missing_fields.push({'label':'Column name field is required'}); }
            if (!this.spatialquery.operator) { this.missing_fields.push({'label':'Operator field is required'}); }

            //if (this.spatialquery.operator && (this.spatialquery.operator == 'Equals' || this.spatialquery.operator != 'GreaterThan' || this.spatialquery.operator != 'LessThan')) { 
            if(['Equals','GreaterThan','LessThan'].includes(this.spatialquery.operator)) {
                if (!this.spatialquery.value) { 
                    this.missing_fields.push({'label':'Value field is required (for Equals/GreaterThan/LessThan operators)'}); 
                }
            }

            if (this.missing_fields.length>0) {
                return true;
            } 
            return false
        },

        addTableEntry: function() {
            this.isNewEntry = true;
            this.spatialquery.answer_type = '';
            this.spatialquery.question = '';
            this.spatialquery.answer_mlq = '';
            this.spatialquery.layer_name = '';
            this.spatialquery.layer_url = '';
            this.spatialquery.group = '';
            this.spatialquery.expiry = '';
            this.spatialquery.visible_to_proponent = '';
            this.spatialquery.buffer = '';
            this.spatialquery.how = '';
            this.spatialquery.column_name = '';
            this.spatialquery.operator = '';
            this.spatialquery.value = '';
            this.spatialquery.prefix_answer = '';
            this.spatialquery.no_polygons_proponent = '-1';
            this.spatialquery.answer = '';
            this.spatialquery.prefix_info = '';
            this.spatialquery.no_polygons_assessor = '-1';
            this.spatialquery.assessor_info = '';
            this.spatialquery.regions = '';
            this.spatialquery.id = '';
            this.addedOptions = [];
            this.addedHeaders = [];
            this.addedExpanders = [];
            this.spatialquery.help_text='';
            this.spatialquery.help_text_assessor='';
            this.spatialquery.help_text_url=false;
            this.spatialquery.help_text_assessor_url=false;

            this.showOptions = false;
            this.proposal.lodgement_number = '';
            this.proposal.group_mlqs = true;
            this.proposal.all_mlqs = false;
            this.showQuestionModal = true;
            this.isModalOpen = true;
        },
        initEventListeners: function(){
            const self = this;

            self.$refs.spatial_query_question_table.vmDataTable.on('click','.edit-row', function(e) {
                e.preventDefault();
                self.isNewEntry = false;
                self.$refs.spatial_query_question_table.row_of_data = self.$refs.spatial_query_question_table.vmDataTable.row('#'+$(this).attr('data-rowid'));

                self.spatialquery.id = self.$refs.spatial_query_question_table.row_of_data.data().id;
                self.spatialquery.question = self.$refs.spatial_query_question_table.row_of_data.data().question;
                self.spatialquery.answer_mlq = self.$refs.spatial_query_question_table.row_of_data.data().answer_mlq;
                self.spatialquery.layer_name = self.$refs.spatial_query_question_table.row_of_data.data().layer_name;
                self.spatialquery.layer_url = self.$refs.spatial_query_question_table.row_of_data.data().layer_url;
                self.spatialquery.group = self.$refs.spatial_query_question_table.row_of_data.data().group;
                self.spatialquery.expiry = self.$refs.spatial_query_question_table.row_of_data.data().expiry;
                self.spatialquery.visible_to_proponent = self.$refs.spatial_query_question_table.row_of_data.data().visible_to_proponent;
                self.spatialquery.buffer = self.$refs.spatial_query_question_table.row_of_data.data().buffer;
                self.spatialquery.how = self.$refs.spatial_query_question_table.row_of_data.data().how;
                self.spatialquery.column_name = self.$refs.spatial_query_question_table.row_of_data.data().column_name;
                self.spatialquery.operator = self.$refs.spatial_query_question_table.row_of_data.data().operator;
                self.spatialquery.value = self.$refs.spatial_query_question_table.row_of_data.data().value;
                self.spatialquery.prefix_answer = self.$refs.spatial_query_question_table.row_of_data.data().prefix_answer;
                self.spatialquery.no_polygons_proponent = self.$refs.spatial_query_question_table.row_of_data.data().no_polygons_proponent;
                self.spatialquery.answer = self.$refs.spatial_query_question_table.row_of_data.data().answer;
                self.spatialquery.prefix_info = self.$refs.spatial_query_question_table.row_of_data.data().prefix_info;
                self.spatialquery.no_polygons_assessor = self.$refs.spatial_query_question_table.row_of_data.data().no_polygons_assessor;
                self.spatialquery.assessor_info = self.$refs.spatial_query_question_table.row_of_data.data().assessor_info;
                self.spatialquery.regions = self.$refs.spatial_query_question_table.row_of_data.data().regions;

                self.addedOptions = self.$refs.spatial_query_question_table.row_of_data.data().options;
                self.addedHeaders = self.$refs.spatial_query_question_table.row_of_data.data().headers;       
                self.addedExpanders = self.$refs.spatial_query_question_table.row_of_data.data().expanders;

                self.isModalOpen = true;
                self.showQuestionModal = true;
                self.showTestModal = false;
                self.showTestJsonResponse = false;
            });

            self.$refs.spatial_query_question_table.vmDataTable.on('click','.delete-row', function(e) {
                e.preventDefault();
                self.$refs.spatial_query_question_table.row_of_data = self.$refs.spatial_query_question_table.vmDataTable.row('#'+$(this).attr('data-rowid'));
                self.spatialquery.id = self.$refs.spatial_query_question_table.row_of_data.data().id;

                swal({
                    title: "Delete Spatialquery",
                    text: "Are you sure you want to delete?",
                    type: "question",
                    showCancelButton: true,
                    confirmButtonText: 'Accept'

                }).then(async (result) => {
                    if (result) {
                        await self.$http.delete(helpers.add_endpoint_json(api_endpoints.spatial_query,(self.spatialquery.id+'/delete_spatialquery')))
                        .then((response) => {
                            self.$refs.spatial_query_question_table.vmDataTable.ajax.reload();
                        }, (error) => {
                            swal(
                                'Delete Error',
                                helpers.apiVueResourceError(error),
                                'error'
                            )
                        });
                    }

                },(error) => {
                    //
                });                
            });

            self.$refs.spatial_query_question_table.vmDataTable.on('click','.test-row', function(e) {
                e.preventDefault();
                self.isNewEntry = false;
                self.proposal.group_mlqs = true;
                self.$refs.spatial_query_question_table.row_of_data = self.$refs.spatial_query_question_table.vmDataTable.row('#'+$(this).attr('data-rowid'));
                self.proposal.lodgement_number = self.$refs.spatial_query_question_table.row_of_data.data().lodgement_number;
                //self.proposal.group_mlqs = self.$refs.spatial_query_question_table.row_of_data.data().group_mlqs;
                self.proposal.all_mlqs = self.$refs.spatial_query_question_table.row_of_data.data().all_mlqs;
                self.proposal.masterlist_question_id = $(this).attr('data-rowid')
                self.isModalOpen = true;
                self.showTestModal = true;
                self.showQuestionModal = false;
                self.showTestJsonResponse = false;
                self.sqs_response = ''
            });
        },
        initAnswerTypeSelector: function () {
            const self = this;
            $(self.$refs.select_answer_type).select2({
                "theme": "bootstrap",
                placeholder:"Select Answer Type..."
            }).
            on("select2:selecting",function (e) {
                let selected = $(e.currentTarget);
            }).
            on("select2:select",function (e) {
                let selected = $(e.currentTarget);
                self.spatialquery.answer_type = selected.val()
                self.setShowAdditional(selected.val())
            }).
            on("select2:unselect",function (e) {
                let selected = $(e.currentTarget);
                self.spatialquery.answer_type = selected.val()
            });
        },
        initHeaderAnswerTypeSelector: function (index) {
            const self = this;
            let header_name = 'header-answer-type-' + index
            $(`[name='${header_name}]`).select2({
                "theme": "bootstrap",
                placeholder:"Select Answer Type..."
            }).
            on("select2:selecting",function (e) {
                let selected = $(e.currentTarget);
            }).
            on("select2:select",function (e) {
                let selected = $(e.currentTarget);
                // self.spatialquery.answer_type = selected.val()
                // self.setShowAdditional(selected.val())
            }).
            on("select2:unselect",function (e) {
                let selected = $(e.currentTarget);
                self.spatialquery.answer_type = selected.val()
            });
        },
        initSelects: async function() {

            //console.log(helpers.add_endpoint_json(api_endpoints.spatial_query,'get_spatialquery_selects'))
            await this.$http.get(helpers.add_endpoint_json(api_endpoints.spatial_query,'get_spatialquery_selects')).then(res=>{

                    this.spatialquery_selects = res.body

            },err=>{
                swal(
                    'Get Application Selects Error',
                    helpers.apiVueResourceError(err),
                    'error'
                )
            });
            this.initAnswerTypeSelector();
        },        

        fetchProfile: function(){
            let vm = this;
            Vue.http.get(api_endpoints.profile).then((response) => {
                vm.profile = response.body

            },(error) => {
                console.log(error);

            })
        },

    },
    mounted: function() {
        this.form = document.forms.spatial_query_question;
        this.fetchProfile();
        this.$nextTick(() => {
            this.initEventListeners();
            this.initSelects();
        });
    }
}
</script>

<style lang="css" scoped>
.control-label label > div {
    text-align: left;
}
.med {
    transform: scale(1.5);
}
</style>
