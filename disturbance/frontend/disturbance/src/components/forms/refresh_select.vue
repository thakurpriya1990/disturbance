<template lang="html">
        <span>
            <template v-if="layer_data && !assessorMode">
            <!-- <template v-if="!assessorMode"> -->
                <template>
                    <label  for="refresh_time_value" class="inline" > {{ refresh_time_value }}</label>
                    <input type="hidden" class="form-control" :name="refresh_timestamp_name" :value="refresh_time_value" />
                </template>
                <template>
                    <a href="" @click.prevent="refresh">Refresh&nbsp;</i></a>
                </template>
            </template>
        </span>     
</template>
<script>
export default {
    name:"Refresh",
    props:["parent_name","assessorMode","layer_data"],

components: {  },
data: function() {
  return{
    showingHelpText: false,
    pBody: 'pBody',
    refresh_timestamp_name : this.parent_name+'-refresh-timestamp',
    refresh_time_value:'',
    }
  },

 methods:{
         refresh: function(){
            let vm=this;
            var ele=$('[name='+vm.parent_name+']')[0]
            //add api call here to get the refresh value and refresh time stamp
            var val=['Pingelly', 'SHIRE-OF-DUNDAS']
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
                var sqs_timestamp="2023-05-24 11:52:37";
                vm.refresh_time_value= sqs_timestamp;
            }
        },
   }
}
</script>

<style lang="css">
</style>


