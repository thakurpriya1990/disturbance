<template lang="html">
        <span>
            <template v-if="layer_data && !assessorMode">
            <!-- <template v-if="!assessorMode"> -->
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
            var ele=$('[name='+vm.parent_name+']')[0]
            //add api call here to get the refresh value and refresh time stamp
            const mlq_data={label: '',
                            name: ''};
            mlq_data.label=vm.parent_label;
            mlq_data.name=vm.parent_name;
            let url = '/refresh'
            console.log('mlq_data', mlq_data)
            await this.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,this.proposal_id + url),JSON.stringify(mlq_data),{
                    emulateJSON:true,
            }).then((response)=>{
                //self.isModalOpen = true;
                console.log(response);
                var val=response.body.value;
                if(val && typeof(val)=='string')
                {
                    ele.value=val;
                }
                else if(val && typeof(val)=='object'){
                    for (const op of ele.options){
                        if(op.value == val){
                            op.selected=true;
                            found=op;                    
                        }
                    }
                }
                if(val){
                    if(ele){
                        var e = document.createEvent('HTMLEvents');
                        e.initEvent('change', true, true);
                        ele.dispatchEvent(e);
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

            var val=['Pingelly', 'SHIRE-OF-DUNDAS']
            // if(val && typeof(val)=='string')
            // {
            //     ele.value=val;
            // }
            // else if(val && typeof(val)=='object'){
            //     for (const op of ele.options){
            //         if(op.value == val){
            //             op.selected=true;
            //             found=op;                    
            //         }
            //     }
            // }
            // if(val){
            //     if(ele){
            //         var e = document.createEvent('HTMLEvents');
            //         e.initEvent('change', true, true);
            //         ele.dispatchEvent(e);
            //     }
            //     var sqs_timestamp="2023-05-24 11:52:37";
            //     vm.refresh_time_value= sqs_timestamp;
            // }
        },
   }
}
</script>

<style lang="css">
</style>


