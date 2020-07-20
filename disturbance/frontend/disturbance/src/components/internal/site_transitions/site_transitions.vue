<template>
    <div class="container"> 
        <ComponentSiteSelection

        />
    </div>
</template>

<script>
import ComponentSiteSelection from '@/components/common/apiary/component_site_selection.vue'

export default {
    name: 'SiteTransitions',
    data: function(){
        return {

        }
    },
    components: {
        ComponentSiteSelection
    },
    props: {

    },
    watch: {

    },
    computed: {

    },
    methods: {

    },
    mounted: function() {

    },
    created: function() {
        let vm = this
        console.log('created')
    },
}
</script>

<style>

</style>
