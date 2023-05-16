<template lang="html">
        <span>
            <template v-if="!assessorMode">
                <template>
                    <a href="" @click.prevent="refresh">Refresh&nbsp;</i></a>
                </template>
            </template>
        </span>     
</template>

 



<script>
export default {
    props:["parent_name","assessorMode","layer_data"],

components: {  },
data: function() {
  return{
    showingHelpText: false,
    pBody: 'pBody'
    }
  },

 methods:{
         refresh: function(){
            let vm=this;
            console.log("inside refresh,", vm.parent_name)
            var ele=$('[name='+vm.parent_name+']')[0]
           ele.value='123';

        },
   }
}
</script>

<style lang="css">
</style>


