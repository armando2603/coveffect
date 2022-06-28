<template>
  <q-page padding>
    <div class="q-pr-xl">
      <div class="row justify-between">
        <div class="q-pl-sm">
          <q-btn class='' rounded icon='arrow_back' color='primary' @click="this.$router.replace({name: 'home', params: {paperList: JSON.stringify(this.paperList), fixedPapers: JSON.stringify(this.fixedPapers), previousPaperList: JSON.stringify(this.previousPaperList), sessionName: this.sessionName}})" />
        </div>
        <div class="text-primary q-pt-sm text-h6 column justify-evenly">Evaluate a Model</div>
        <div class="q-pl-sm invisible" >
          <q-btn class='' rounded icon='arrow_back' color='primary' @click="this.$router.replace({name: 'home', params: {paperList: JSON.stringify(this.paperList), fixedPapers: JSON.stringify(this.fixedPapers), previousPaperList: JSON.stringify(this.previousPaperList), sessionName: this.sessionName}})" />
        </div>
      </div>
      <div class="q-pa-sm q-mt-md column">
        <div class="q-gutter-sm row justify-evenly">
          <div>
            <q-radio v-model="checkpointOptions" :val="new_checkpoints_list" label="New" @update:model-value="(value, evt) => {checkpointName=null}"/>
            <q-radio v-model="checkpointOptions" :val="history_checkpoints_list" label="History" @update:model-value="(value, evt) => {checkpointName=null}"/>
          </div>
        </div>
        <div class="q-pa-md row justify-evenly" >
          Choose a checkpoint:
        </div>
        <div class="row justify-evenly">
          <div style="width: 400px">
            <q-select dense filled v-model="checkpointName" :options="checkpointOptions" label="select" />
          </div>
        </div>
      </div>
      <div class="row justify-evenly q-pt-md">
        <q-btn class='' rounded label="evaluate" color='primary' @click="evaluate" />
      </div>
      <div class="row justify-evenly">
        <div style="width: 700px">
          <div class="text-primary text-h6 row justify-evenly q-pt-xl">{{loadedCheckpointName}}</div>
          <div class="text-primary text-h6 row justify-evenly q-pt-xl">Scores:</div>
          <div class="q-pa-md">
            <q-table
              title="Entity"
              title-class="text-primary"
              table-header-style="text-align: left"
              table-header-class="align-left text-primary text-bold"
              wrap-cells
              hide-bottom
              dense
              separator="cell"
              :rows="entity_scores"
            />
          </div>
          <div class="row justify-evenly" v-if="scores_dicts!==null">
            <q-btn
              label="Show Errors"
              rounded
              color='primary'
              @click="showErrors=true;error_table=scores_dicts['entity_scores_dict']['df_general_scores']"
            />
          </div>
          <div class="q-pa-md">
            <q-table
              title="Effect"
              title-class="text-primary"
              table-header-style="text-align: left"
              table-header-class="align-left text-primary text-bold"
              wrap-cells
              hide-bottom
              dense
              separator="cell"
              :rows="effect_scores"
            />
          </div>
          <div class="row justify-evenly" v-if="scores_dicts!==null">
            <q-btn
              label="Show Errors"
              rounded
              color='primary'
              @click="showErrors=true;error_table=scores_dicts['effect_scores_dict']['df_general_scores']"
            />
          </div>
          <div class="q-pa-md">
            <q-table
              title="Level"
              title-class="text-primary"
              table-header-style="text-align: left"
              table-header-class="align-left text-primary text-bold"
              wrap-cells
              hide-bottom
              dense
              separator="cell"
              :rows="level_scores"
            />
          </div>
          <div class="row justify-evenly" v-if="scores_dicts!==null">
            <q-btn
              label="Show Errors"
              rounded
              color='primary'
              @click="showErrors=true;error_table=scores_dicts['level_scores_dict']['df_general_scores']"
            />
          </div>
          <q-dialog v-model="showErrors">
            <q-card class="column no-wrap" style="min-width: 100%; height: 95%">
              <q-card-section class="row justify-between">
                <div class="text-h5 text-primary">Error</div>
                <div class="col-1 justify-end row">
                  <q-btn class='' icon="close" flat round dense v-close-popup />
                </div>
              </q-card-section>
              <q-card-section style="height: 100%">
                <div class="q-pa-md column" style="flex-grow: 1;overflow: auto">
                  <q-table
                    class="my-sticky-virtscroll-table"
                    style="flex-grow: 1;overflow: auto"
                    :rows-per-page-options="[0]"
                    table-header-style="text-align: left"
                    table-header-class="align-left text-primary text-bold"
                    wrap-cells
                    dense
                    separator="cell"
                    virtual-scroll
                    :virtual-scroll-item-size="48"
                    :virtual-scroll-sticky-size-start="48"
                    v-model:pagination='pagination'
                    :rows="error_table"
                    :columns="columns"
                  />
                </div>
              </q-card-section>
            </q-card>
          </q-dialog>
          <q-dialog v-model="showTestLoad" persistent>
            <q-card style="width: 350px">
              <q-card-section>
                <div class='justify-evenly row'>
                  <div class="text-h6 text-primary q-pb-sm q-pl-md">Testing The Model</div>
                </div>
              </q-card-section>
              <q-card-section class="row justify-evenly">
                <q-circular-progress
                  show-value
                  class=""
                  :value="loadStatus"
                  size="5em"
                  font-size="16px"
                  color="primary"
                >
                {{ loadStatus }}%
                </q-circular-progress>
              </q-card-section>
            </q-card>
          </q-dialog>
        </div>
      </div>
        
    </div>
  </q-page>
</template>

<style lang="sass">
.my-sticky-virtscroll-table
  /* height or max-height is important */
  height: 410px

  .q-table__top,
  .q-table__bottom,
  thead tr:first-child th /* bg color is important for th; just specify one */
    background-color: #fff

  thead tr th
    position: sticky
    z-index: 1
  /* this will be the loading indicator */
  thead tr:last-child th
    /* height of all previous header rows */
    top: 48px
  thead tr:first-child th
    top: 0
</style>

<script>
import { apiGPU } from 'src/boot/axios'
import { ref } from 'vue'

const columns = [
  { name: 'doi', label: 'DOI',field: 'doi', required: true, sortable: true, align: 'left'},
  { name: 'f1', label: 'f1', field: row => row['f1'].toFixed(3), required: true, sortable: true, align: 'left' },
  { name: 'targets', label: 'Targets', field: 'targets', required: true, align: 'left' },
  { name: 'predictions', label: 'predictions', field: 'predictions', required: true, align: 'left' },

]

export default {
  // name: 'PageName',
  setup () {
    return {
      loadedCheckpointName: ref('No Checkpoint Loaded'),
      showErrors: ref(false),
      previousPaperList: ref([]),
      fixedPapers: ref([]),
      paperList: ref([]),
      sessionName: ref(null),
      checkpointOptions: ref(['loading...']),
      checkpointName: ref(null),
      scores_dicts: ref(null),
      error_table: ref([]),
      entity_scores: ref([]),
      entity_scores_dict: ref({}),
      effect_scores: ref([]),
      effect_scores_dict: ref({}),
      level_scores: ref([]),
      level_scores_dict: ref({}),
      history_checkpoints_list: ref(['loading...']),
      new_checkpoints_list : ref(null),
      loadStatus: ref(0),
      showTestLoad: ref(false),
      columns,
      pagination: ref({
        sortBy: 'f1',
        descending: false
      })
    }
  },
  methods: {
    evaluate () {
      if ( this.checkpointOptions === this.new_checkpoints_list) {
        this.showTestLoad = true
        this.getLoadStatus()
      }
      apiGPU.post(
        '/evaluate',
        { checkpoint_name: this.checkpointName}
      ).then( (response) => {
        if ( this.checkpointOptions === this.new_checkpoints_list) {
          this.history_checkpoints_list = this.history_checkpoints_list.filter(function(value, index, arr){ 
              return value !== this.checkpointName;
          });
        }
        this.loadedCheckpointName = this.checkpointName
        this.checkpointName = null
        this.showTestLoad = false
        this.scores_dicts = response.data
        // console.log(this.scores_dicts)
        this.entity_scores_dict = this.scores_dicts['entity_scores_dict']
        this.effect_scores_dict = this.scores_dicts['effect_scores_dict']
        this.level_scores_dict = this.scores_dicts['level_scores_dict']
        let entity_scores = []
        for (const aggregate_type of Object.keys(this.scores_dicts['entity_scores_dict']['scores']) ) {
          let aggregate_row = {}
          aggregate_row['aggregate_type'] =  aggregate_type
          for (const metric of Object.keys(this.scores_dicts['entity_scores_dict']['scores'][aggregate_type]) ) {
            aggregate_row[metric] = this.scores_dicts['entity_scores_dict']['scores'][aggregate_type][metric].toFixed(3)
          }
          entity_scores.push(aggregate_row)
        }
        this.entity_scores = entity_scores

        let effect_scores = []
        for (const aggregate_type of Object.keys(this.scores_dicts['effect_scores_dict']['scores']) ) {
          let aggregate_row = {}
          aggregate_row['aggregate_type'] =  aggregate_type
          for (const metric of Object.keys(this.scores_dicts['effect_scores_dict']['scores'][aggregate_type]) ) {
            aggregate_row[metric] = this.scores_dicts['effect_scores_dict']['scores'][aggregate_type][metric].toFixed(3)
          }
          effect_scores.push(aggregate_row)
        }
        this.effect_scores = effect_scores

        let level_scores = []
        for (const aggregate_type of Object.keys(this.scores_dicts['level_scores_dict']['scores']) ) {
          let aggregate_row = {}
          aggregate_row['aggregate_type'] =  aggregate_type
          for (const metric of Object.keys(this.scores_dicts['level_scores_dict']['scores'][aggregate_type]) ) {
            aggregate_row[metric] = this.scores_dicts['level_scores_dict']['scores'][aggregate_type][metric].toFixed(3)
          }
          level_scores.push(aggregate_row)
        }
        this.level_scores = level_scores
        // this.effect_scores_dict = this.scores_dicts['effect_scores_dict']
        // this.level_scores_dict = this.scores_dicts['level_scores_dict']
      }).catch( (error) => {error.message})
    },
    getLoadStatus () {
      apiGPU.get('/getGenerateStatus')
        .then(responde => {
          this.loadStatus = Math.round(responde.data)
          console.log(this.loadStatus)
          if (this.loadStatus < 100) this.getLoadStatus()
          else this.showTestLoad = false
        }).catch(error => console.log(error))
    },
  },
  created () {
    this.previousPaperList = JSON.parse(this.$route.params.previousPaperList)
    this.fixedPapers = JSON.parse(this.$route.params.fixedPapers)
    this.paperList = JSON.parse(this.$route.params.paperList)
    this.sessionName = this.$route.params.sessionName
    this.checkpointOptions = this.history_checkpoints_list

    apiGPU.get(
      '/checkpoint_list'
    ).then( (response) => {
      this.history_checkpoints_list = response.data['history_checkpoints']
      this.new_checkpoints_list = response.data['new_checkpoints']
      this.checkpointOptions = response.data['history_checkpoints']
    }).catch( (error) => {error.message})
  }
}
</script>
