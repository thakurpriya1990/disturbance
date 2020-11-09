<template lang="html">
    <div>
        <FormSection :formCollapse="false" :label="section_title" Index="checklist">
            <ul class="list-unstyled col-sm-12" v-for="q in checklist">
                <div class="row">
                    <div class="col-sm-12">
                        <li class="col-sm-6">
                            <label class="control-label">{{q.question.text}}</label>
                        </li>
                        <div v-if="q.question.answer_type === 'yes_no'">
                            <ul  class="list-inline col-sm-6">
                                <li class="list-inline-item">
                                    <input  class="form-check-input" v-model="q.answer" type="radio" :name="'option'+q.id" :id="'answer_one'+q.id" :value="true" data-parsley-required :disabled="readonly"/> Yes
                                </li>
                                <li class="list-inline-item">
                                    <input  class="form-check-input" v-model="q.answer" type="radio" :name="'option'+q.id" :id="'answer_two'+q.id" :value="false" data-parsley-required :disabled="readonly"/> No
                                </li>
                            </ul>
                        </div>
                        <div v-else-if="q.question.answer_type === 'free_text'">
                            <li class="list-inline-item">
                                <!--input class="form-check-input form-control" v-model="q.text_answer" type="text" :name="'option'+q.id" :id="'text_answer'+q.id" data-parsley-required :disabled="readonly"/-->
                                <textarea class="form-check-input form-control" v-model="q.text_answer" :name="'option'+q.id" :id="'text_answer'+q.id" data-parsley-required :disabled="readonly"/>
                            </li>
                        </div>
                    </div>
                </div>
            </ul>
        </FormSection>

    </div>
</template>

<script>
    import FileField from '@/components/forms/filefield_immediate.vue'
    import FormSection from "@/components/forms/section_toggle.vue"

    export default {
        name: 'SectionChecklist',
        props:{
            checklist: {
                type: Array,
            },
            section_title: {
                type: String,
                default: 'Checklist',
            },
            readonly: {
                type: Boolean,
                default: true,
            },
        },
        watch: {

        },
        data: function(){
            return{

            }
        },
        created: function(){

        },
        mounted: function(){
            let vm = this;
            this.$nextTick(() => {
                //vm.addEventListeners();
            });
        },
        components: {
            FileField,
            FormSection,
        },
        computed: {
        },
        methods: {
            /*
            addEventListeners: function () {

            },
            */
        },
    }
</script>

<style lang="css" scoped>

</style>
