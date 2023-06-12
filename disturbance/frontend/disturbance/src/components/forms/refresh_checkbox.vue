<template lang="html">
        <span>
            <template v-if="!assessorMode">
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
            var found=[]
            var checkboxes=document.getElementsByClassName(vm.parent_name)
            //console.log('checkboxes', checkboxes)
            //add api call here to get the refresh value and refresh time stamp
            var values=['Section11-0-1', 'Section11-0-3']
            if(values && typeof(values)=='string')
            {
                checkboxes.value=val;
            }
            else if(values && typeof(values)=='object'){
                for (const val of values){
                    for (const op of checkboxes){
                        console.log('options', op.name, 'value', val)
                        if(op.name == val){
                            console.log('found op', op.name)
                            op.checked=true;
                            found.push(op);                    
                        }
                    }
                }
                
            }
            //console.log(found)
            if(values){
                // if(found.length >1){
                //     var e = document.createEvent('HTMLEvents');
                //     e.initEvent('change', true, true);
                //     for (const ele of found){
                //         ele.dispatchEvent(e);
                //     }
                    
                // }
                var sqs_timestamp="2023-05-24 11:52:37";
                vm.refresh_time_value= sqs_timestamp;
            }
        },
   }
}
</script>

<style lang="css">
</style>


