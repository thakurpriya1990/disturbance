<template lang="html">
        <span>
            <template v-if="layer_data && !assessorMode">
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
    props:["parent_name","parent_label", "assessorMode","layer_data", "proposal_id", "refresh_time_value"],

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
            var ele=document.querySelectorAll('[name='+vm.parent_name+']')
            const mlq_data={label: '',
                            name: ''};
            mlq_data.label=vm.parent_label;
            mlq_data.name=vm.parent_name;
            let url = '/refresh'
            console.log('mlq_data', mlq_data)
            var found=null;
            await this.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,this.proposal_id + url),JSON.stringify(mlq_data),{
                    emulateJSON:true,
            }).then((response)=>{
                //self.isModalOpen = true;
                console.log(response);
                var val=response.body.value;
                if(val){
                    for (const el of ele){
                        // if(el.value == val){
                        //     el.checked=true;
                        //     found=el;                    
                        // }
                        if(el.labels && el.labels[0] && el.labels[0].innerText== val){
                            el.checked=true;
                            found=el;                    
                        }
                    }
                    if(found){
                        var e = document.createEvent('HTMLEvents');
                        e.initEvent('change', true, true);
                        found.dispatchEvent(e);
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
            // var val='no'
            // console.log(ele)
            // var found=null;
            // if(val){
            //     for (const el of ele){
            //         if(el.value == val){
            //             el.checked=true;
            //             found=el;                    
            //         }
            //     }
            //     if(found){
            //         var e = document.createEvent('HTMLEvents');
            //         e.initEvent('change', true, true);
            //         found.dispatchEvent(e);
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


