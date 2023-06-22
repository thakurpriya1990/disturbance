<template lang="html">
        <span>
            <template v-if="!assessorMode">
                <template>
                    <label  for="refresh_time_value" class="inline" > {{ refresh_time_val }}</label>
                    <input type="hidden" class="form-control" :name="refresh_timestamp_name" :value="refresh_time" />
                </template>
                <template>
                    <a href="" @click.prevent="refresh">Refresh&nbsp;</i></a>
                </template>
            </template>
        </span>     
</template>
<script>
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
    name:"Refresh",
    props:["parent_name","parent_label","assessorMode","layer_data", "proposal_id", "refresh_time_value"],

components: {  },
data: function() {
  return{
    showingHelpText: false,
    pBody: 'pBody',
    refresh_timestamp_name : this.parent_name+'-refresh-timestamp',
    refresh_time:this.refresh_time_value,
    }
  },
 computed:{
        refresh_time_val: function(){
            return this.refresh_time ? moment(this.refresh_time).format('DD/MM/YYYY') + moment(this.refresh_time).format(' h:mm:ss a') : '';
        },
 },

 methods:{
         refresh: async function(){
            let vm=this;
            var found=[]
            var checkboxes=document.getElementsByClassName(vm.parent_name)
            //console.log('checkboxes', checkboxes)

            const mlq_data={label: '',
                            name: ''};
            mlq_data.label=vm.parent_label;
            mlq_data.name=vm.parent_name;
            let url = '/refresh'
            var found=null;
            await this.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,this.proposal_id + url),JSON.stringify(mlq_data),{
                    emulateJSON:true,
            }).then((response)=>{
                //self.isModalOpen = true;
                console.log(response);
                var values=response.body.value;
                if(values && typeof(values)=='object'){
                    for (const val of values){
                        for (const op of checkboxes){
                            console.log('options', op.name, 'value', val)
                            if(op.labels && op.labels[0] && op.labels[0].innerText== val){
                                console.log('found op', op.name)
                                op.checked=true;
                            }
                        }
                    }
                }
                vm.refresh_time= response.body.sqs_timestamp
                
            },(error)=>{
                swal(
                    'Error',
                    helpers.apiVueResourceError(error),
                    //error.body,
                    'error'
                )
            });
            //add api call here to get the refresh value and refresh time stamp
            //var values=['Section11-0-1', 'Section11-0-3']
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
            //console.log(found)
            // if(values){
            //     // if(found.length >1){
            //     //     var e = document.createEvent('HTMLEvents');
            //     //     e.initEvent('change', true, true);
            //     //     for (const ele of found){
            //     //         ele.dispatchEvent(e);
            //     //     }
                    
            //     // }
            //     var sqs_timestamp="2023-05-24 11:52:37";
            //     vm.refresh_time_value= sqs_timestamp;
            // }
        },
   }
}
</script>

<style lang="css">
</style>


