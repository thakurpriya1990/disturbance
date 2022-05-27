<template lang="html">
    <div class="row">
        <div class="col-md-12">
            <div class="form-group">
                <div class="row">
                  <p class="col-md-6" style="color:red">Layer Name: <p  style="color:red"v-html="layer_name"></p></p>
                  <p class="col-md-6" style="color:red">Layer last updated: <p style="color:red" v-html="layer_date"></p></p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    props:["help_text"],
    computed:{
        
        layer_name:function () {
            let lay_name='';
            if(this.help_text.hasOwnProperty('layer_name')){
                lay_name= this.help_text.layer_name;
            }
            return lay_name;
        },
        layer_date:function () {
            let lay_date='';
            if(this.help_text.hasOwnProperty('layer_upated')){
                lay_date= this.help_text.layer_upated;
            }
            return lay_date;
        },
    },
}

</script>

<style lang="css" scoped>
.buffer {
    margin-top: 5px;
}
</style>
