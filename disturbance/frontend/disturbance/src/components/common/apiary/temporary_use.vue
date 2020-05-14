<template id='temporary_use' >

  <div class = "row">
    <div class="col-sm-12">
      <div class ="panel panel-default">
        <div class = "panel-heading">
          <h3 class= "panel-title">Temporary Use
            <a :href="'#'+pBody" data-toggle="collapse" data-parent="#userInfo" expanded="true" :aria-controls="pBody">
              <span class="glyphicon glyphicon-chevron-up pull-right "></span>
            </a>
           </h3>
        </div>
        <div class="panel-body collapse in" :id="pBody">
          <div class ="row">
            <div class="col-md=3">
              <router-link style="margin-top:25px;" class="btn btn-primary pull-right" :to="#">New temporary use</router-link>
            </div>
          </div>

          <div class="row">
            <div class="col-md-3">
              <div class="form-group">
                <label for="">From:</label>
                <select style="width:100%" class="form-control input-sm" multiple ref="#">
                  <option>Test-1</option>
                  <option>Test-2</option>
                </select>
              </div>
            </div>
            <div class="col-md-3">
              <div class="form-group">
                <label for="">To:</label>
                <select style="width:100%" class="form-control input-sm" multiple ref="#">
                  <option>Test-1</option>
                  <option>Test-2</option>
                </select>
              </div>
            </div>
          </div>

          <div class="row">
            <div class="col-lg-12">
                <datatable v-if="level=='external'" ref="proposal_datatable" :id="datatable_id" :dtOptions="proposal_ex_options" :dtHeaders="proposal_ex_headers"/>
                <datatable v-else ref="proposal_datatable" :id="datatable_id" :dtOptions="proposal_options" :dtHeaders="proposal_headers"/>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

</template>

<script>

</script>
