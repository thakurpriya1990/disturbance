<template lang="html">
  <div id="schema-question">

    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Spatial Query Metrics
                        <a :href="'#'+pQuestionBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pQuestionBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pQuestionBody">
                    <div class="row"><br/></div> 
                    <div class="row">
                        <div class="col-md-12">
                            <div class="form-group">

                                <datatable ref="spatial_query_metrics_table"
                                    :id="spatial_query_metrics_id" 
                                    :dtOptions="dtOptionsSchemaQuestion"
                                    :dtHeaders="dtHeadersSchemaQuestion" 
                                />

                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <modal class="my-modal" transition="modal fade" @ok="ok()" title="Metrics" xlarge>
        <div class="container-fluid">
            <div id="error" v-if="missing_fields.length > 0" style="margin: 10px; padding: 5px; color: red; border:1px solid red;">
                <b>Please answer the following mandatory question(s):</b>
                <ul>
                    <li v-for="error in missing_fields">
                        {{ error.label }}
                    </li>
                </ul>
            </div>
             
        </div>

	<div class="row">
	    <div class="col-md-12">
		<div class="form-group">
		    <datatable ref="spatial_query_metrics_details_table"
			:id="spatial_query_metrics_details_id" 
			:dtOptions="dtOptionsSchemaMetrics"
			:dtHeaders="dtHeadersSchemaMetrics"
		    />
		</div>
	    </div>
	</div>

    </modal>

  </div>
</template>

<script>
import MetricsDetails from '@/components/internal/main/spatial_query_metrics.vue'
import datatable from '@/utils/vue/datatable.vue'
import modal from '@vue-utils/bootstrap-modal.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'

export default {
    name:'schema-question',
    components: {
        modal,
        datatable,
        MetricsDetails,
    },
    props:{
    },
    data:function () {
        let vm = this;
        vm.spatial_query_metrics_url = helpers.add_endpoint_join(api_endpoints.spatial_query_metrics_paginated, 'spatial_query_metrics_datatable_list/?format=datatables');
        console.log(vm.spatial_query_metrics_url)

        return {
            spatial_query_metrics_id: 'spatial_query_metrics-datatable-'+vm._uid,
            spatial_query_metrics_details_id: 'spatial_query_metrics_details-datatable-'+vm._uid,
            pOptionsBody: 'pOptionsBody' + vm._uid,
            pQuestionBody: 'pQuestionBody' + vm._uid,
            isModalOpen: false,
            isNewEntry: false,
            missing_fields: [],
            spatial_query_metrics: [],
            modal_id: 0,

            metricsData: {}, //{"data": []},
//            metricsData: {
//                "recordsTotal": 2,
//                "recordsFiltered": 2,
//                //"data": []
//		"data": [{"question":"100  initialised"}]
//            },

            dtHeadersSchemaQuestion: ["ID", "Lodgement Number", "When", "Query Time", "API Time", "Request Type", "Action"],
            dtOptionsSchemaQuestion:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                serverSide: true,
                autowidth: false,
                processing: true,
                searchDelay: 1000,
                ajax: {
                    "url": vm.spatial_query_metrics_url,
                    "dataSrc": 'data',
                    //"data": function (d) {
                    //    d.proposal_type_id = vm.filterTableProposalType;
                    //    d.section_id = vm.filterTableSection;
                    //    d.group_id = vm.filterTableGroup;
                    //}
                },
                //columnDefs: [
                //    { visible: false, targets: [ 0, 1, 2, ] } 
                //],
                columnDefs: [
                    { visible: true } 
                ],
                columns: [
                    { 
                        data: "id",
                        searchable: true,
                    },
                    { 
                        data: "lodgement_number",
                        searchable: true,
                    },
                    { 
                        data: "when",
                        mRender:function (data,type,full) {
                            return data.replace('T',' ').replace('Z','');
                        },
                        searchable: false,
                    },
                    { 
                        data: "total_query_time",
                        searchable: false,
                        orderable: true,
                    },
                    { 
                        data: "total_api_time",
                        searchable: false,
                    },
                    { 
                        data: "request_type",
                        searchable: true,
                    },
                    { 
                        data: "id",
                        searchable: false,
                        mRender:function (data,type,full) {
                            //var column = `<a class="view-row" data-metrics=data.metrics data-rowid=\"__ROWID__\">View</a><br/>`;
                            //return column.replace(/__ROWID__/g, full.id);
                            let links = '';
                            links +=  `<a href='#' class="updatedMetricsDetails" data-id="${full.id}">View</a><br/>`;
                            console.log(data)
                            return links;
                        }
                    },
                ],
                rowId: function(_data) {
                    return _data.id
                },
            },

            dtHeadersSchemaMetrics: ["Question", "Answer", "Layer Name", "Layer Cached", "Condition", "Error", "Retrive Layer Time", "Query Time"],
            //dtHeadersSchemaMetrics: ["Question", "Answer", "Layer Name"],
            //dtHeadersSchemaMetrics: ["Question"],
            dtOptionsSchemaMetrics:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                //serverSide: false,
                //autowidth: true,
                //processing: true,
//                "ajax": function (data, callback, settings) {
//		    callback(
//                        //vm.metricsData
//			{
//			    "recordsTotal": 0,
//			    "recordsFiltered": 0,
//			    //"data": [{"question":"1.2  ddd"}, {"question":"2.2  eee", }]
//			    "data": []
//			}
//
//		    );
//		  },

                columnDefs: [
                    { visible: true } 
                ],
                columns: [
                    {
                        data: "question",
                        searchable: true,
			'render': function (value) {
	  		    return helpers.dtPopover(value, 50);
			},
                        'createdCell': helpers.dtPopoverCellFn,
                    },
                    {
                        data: "answer_mlq",
                        searchable: true,
			'render': function (value) {
	  		    return helpers.dtPopover(value, 50);
			},
                        'createdCell': helpers.dtPopoverCellFn,
                    },
                    {
                        data: "layer_name",
                        searchable: true,
                    },
                    {
	 	        data: "layer_cached",
	                searchable: false,
		    },
		    {
			data: "condition",
			searchable: false,
		    },
		    {
			data: "error",
			searchable: false,
		    },
		    {
			data: "time_retrieve_layer",
			searchable: false,
                        visible: false,
		    },
		    {
			data: "time",
			searchable: false,
		    },

                ],
            },
        }

    },
    watch:{
    },
    computed: {    
    },
    methods: {
        updatedMetricsDetails(rowid){
            let self = this;
            self.$refs.spatial_query_metrics_table.row_of_data = self.$refs.spatial_query_metrics_table.vmDataTable.row('#'+rowid);
            let spatial_query_metrics = self.$refs.spatial_query_metrics_table.row_of_data.data().metrics; 
            console.log(spatial_query_metrics)

            this.$refs.spatial_query_metrics_details_table.vmDataTable.clear().rows.add( spatial_query_metrics ).draw()
            this.isModalOpen = true;
        },
        close: function() {
            const self = this;
            self.isModalOpen = false;
        },
        initEventListeners: function(){
            let self = this;

            self.$refs.spatial_query_metrics_table.vmDataTable.on('click', '.updatedMetricsDetails', function(e) {
                e.preventDefault();
                var rowid = $(this).attr('data-id');
                //console.log(rowid)
                self.updatedMetricsDetails(rowid);
            });
        },
    },
    mounted: function() {
        this.form = document.forms.spatial_query_metrics;
        this.$nextTick(() => {
            this.initEventListeners();
        });
    }
}
</script>

<style lang="css">


</style>
