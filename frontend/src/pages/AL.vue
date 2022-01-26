<template>
  <q-page padding class="row items-strech">
    <div class="col-12 column no-wrap">
      <q-dialog v-model='showFixedList'>
        <q-card class="column no-wrap" style="min-width: 100%; height: 95%">
          <q-card-section class="row justify-between">
            <div class="text-h5">Annotated Papers List</div>
            <div class="col-1 justify-end row">
              <q-btn class='' icon="close" flat round dense v-close-popup />
            </div>
          </q-card-section>
          <q-card-section class="column" style="height: 100%">
            <div class="q-pa-md column" style="flex-grow: 1;overflow: auto">
              <q-table
              style="flex-grow: 1;overflow: auto"
              class="my-sticky-virtscroll-table"
              :columns="columns"
              :rows="fixedPapers"
              virtual-scroll
              wrap-cells
              separator="cell"
              row-key="doi"
              :rows-per-page-options="[0]"
              :virtual-scroll-sticky-size-start="48"
              my-sticky-virtscroll-table
              :visible-columns="annotated_visible_columns"
              >
              <template v-slot:body-cell-doi="props">
                <q-td
                key='doi'
                :props="props"
                >
                  <!-- <q-checkbox v-model="props.row.keep" /> -->
                  <a :href="'https://dx.doi.org/' + props.row.doi" target="_blank">{{props.row.doi}}</a>
                </q-td>
              </template>
              <template v-slot:body-cell-extractions="props">
                <q-td
                key='extractions'
                :props="props"
                >
                  <q-btn unelevated dense size="sm" color="primary" label='Extracted Values'/>
                </q-td>
              </template>
              </q-table>
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>
      <q-dialog v-model='showList'>
        <q-card class="column no-wrap" style="min-width: 100%; height: 95%">
          <q-card-section class="row justify-between">
            <div class="text-h5">Paper List</div>
            <div class="col-1 justify-end row">
              <q-btn class='' icon="close" flat round dense v-close-popup />
            </div>
          </q-card-section>
          <q-card-section class="column" style="height: 100%">
            <div class="q-pa-md column" style="flex-grow: 1;overflow: auto">
              <q-table
              style="flex-grow: 1;overflow: auto"
              class="my-sticky-virtscroll-table"
              :columns="columns"
              :rows="paperList"
              virtual-scroll
              wrap-cells
              separator="cell"
              row-key="doi"
              :rows-per-page-options="[0]"
              :virtual-scroll-sticky-size-start="48"
              my-sticky-virtscroll-table
              v-model:selected="selected"
              v-model:pagination='pagination'
              @row-click='loadSelection'
              :visible-columns="visible_columns"
              >
              <template v-slot:body-cell-doi="props">
                <q-td
                key='doi'
                :class="props.row.annotated ? 'bg-green-1' : ''"
                :props="props"
                >
                  <!-- <q-checkbox v-model="props.row.keep" /> -->
                  <a :href="'https://dx.doi.org/' + props.row.doi" target="_blank">{{props.row.doi}}</a>
                </q-td>
              </template>
              <template v-slot:body-cell="props">
                <q-td
                  :props="props"
                  :class="props.row.annotated ? 'bg-green-1' : ''"
                >
                  {{props.value}}
                </q-td>
              </template>
              </q-table>
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>
      <div class="row justify-end">
        <div class="column justify-evenly">
            <div class="row justify-end">
              <q-btn
                dense
                label="annotated papers"
                style="width:150px"
                to="/annotations"
                color="primary"
              />
            </div>
        </div>
        <div class="q-pl-md column justify-evenly">
            <div class="row justify-end">
              <q-btn
                dense
                icon='menu'
                style="width:50px"
                @click="showList = true"
                color="primary"
              />
            </div>
        </div>
      </div>
      <div class="col-4 q-pt-md">
        <q-card style="height: 100%" class="column no-wrap">
          <q-card-section class="row justify-evenly">
            <div class="text-h5">Abstract</div>
          </q-card-section>
          <q-card-section class="column" style="overflow: auto; flex-grow: 1">
            <div v-if='loadGpt2' class='row q-mt-md q-mb-md justify-evenly'>
              <q-spinner color="primary" size="5em" />
            </div>
            <div v-if='!loadGpt2' class="scroll overflow-auto">
              <!-- {{paperList.length === 0 ? '' : paperList[currentPaper].abstract}} -->
                <mark v-for="element in highlighted_abstract" :key="element" :class="element.color">
                  {{ element.text }}
                </mark>
            </div>
          </q-card-section>
        </q-card>
      </div>
      <div class="row col-7 justify-between q-pt-xl">
        <q-card class="col-3 column no-wrap" style="height: 100%">
          <div class="column col-12 no-wrap">
            <q-card-section class="row justify-evenly">
              <div class="text-h5">Paper Info</div>
            </q-card-section>
            <div class="column justify-evenly" style="overflow: auto; flex-grow: 1;">
              <q-card-section style="overflow: auto; flex-grow: 1;">
                <q-field stack-label borderless label-color="primary" label='DOI:'>
                  <template v-slot:control>
                    <div v-if="paperList.length !== 0" class="self-center full-width no-outline" tabindex="0"><a :href="'https://dx.doi.org/' + paperList[currentPaper].doi" target="_blank">{{paperList[currentPaper].doi}}</a></div>
                  </template>
                </q-field>
                <q-field stack-label borderless label-color="primary" label='Title:'>
                  <template v-slot:control>
                    <div class="self-center full-width no-outline" tabindex="0">{{paperList.length === 0 ? '' : paperList[currentPaper].title}}</div>
                  </template>
                </q-field>
                <q-field stack-label borderless label-color="primary" label='Authors:'>
                  <template v-slot:control>
                    <div class="self-center full-width no-outline" tabindex="0">{{paperList.length === 0 ? '' : paperList[currentPaper].authors}}</div>
                  </template>
                </q-field>
                <!-- <q-field stack-label borderless label-color="primary" label='Year:'>
                  <template v-slot:control>
                    <div class="self-center full-width no-outline" tabindex="0">{{paperList.length === 0 ? '' : paperList[currentPaper].year}}</div>
                  </template>
                </q-field> -->
                <q-field stack-label borderless label-color="primary" label='Source:'>
                  <template v-slot:control>
                    <div class="self-center full-width no-outline" tabindex="0">{{paperList.length === 0 ? '' : paperList[currentPaper].journal}}</div>
                  </template>
                </q-field>
                <q-field stack-label borderless label-color="primary" label='Citations:'>
                  <template v-slot:control>
                    <div class="self-center full-width no-outline" tabindex="0">{{paperList.length === 0 ? '' : paperList[currentPaper].numCitedBy}}</div>
                  </template>
                </q-field>
              </q-card-section>
            </div>
          </div>
        </q-card>
        <q-card class="col-5 column no-wrap" style="height: 100%">
          <div class="column col-12 no-wrap">
            <div class="column justify-between no-wrap" style="overflow: auto;flex-grow: 1">
              <q-card-section class="row justify-evenly">
                <div class="text-h5">Extracted Values</div>
              </q-card-section>
              <q-card-section style="overflow: auto; flex-grow: 1;">
                <div v-if='loadGpt2' class='row q-mt-md q-mb-md justify-evenly'>
                  <q-spinner color="primary" size="6em" />
                </div>
                <div v-if='!loadGpt2' class='my-outputs scroll overflow-auto' style="overflow: auto">
                  <div class="column" v-for="(predictions_instance, instance_index) in editable_predictions" :key="predictions_instance">
                    <div class="row">
                      <div class="column justify-evenly">{{instance_index + ": "}}</div>
                      <div style="width: 150px;height: auto" ref="editables" class='' v-for="(prediction, prediction_index) in predictions_instance" @click="visualize(instance_index, prediction_index)"  :key="prediction">
                        <div class='q-pa-sm'>
                        <q-field
                        ref="editable"
                        :class="predictionIndex === prediction_index && instanceIndex === instance_index ? 'output-field q-field--highlighted': 'output-field'"
                        label-color="grey-10"
                        color='indigo-8'
                        stack-label
                        outlined
                        dense
                        :bg-color='getOutputColor(prediction)'
                        :label="attributeLabels[prediction.attribute] + ' [' + Math.round(prediction.confidence * 100) + '%]'" >
                          <template v-slot:control>
                            <div class="self-center full-width no-outline q-pb-sm q-pt-md text-h13" style="overflow: hidden; min-height: 40px" tabindex="0">
                              {{prediction.value}}
                            </div>
                          </template>
                          <!-- <template class='' v-slot:label>
                            <div class="q-pt-sm row items-start" style='white-space: normal'>
                              <span>
                                {{output.field + ' [' + (correctionTable? correctionTable[index].confidence: output.confidence) * 100 + '%]'}}
                              </span>
                            </div>
                          </template> -->
                        </q-field>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="q-pa-sm row justify-evenly">
                    <q-btn rounded class="q-pa-sm" icon="add" color="primary" @click="addInstance"/>
                  </div>
                  <!-- <q-dialog v-model="showAddInstance">
                    <q-card class="" style="min-width: 50%; height: 30%">
                      <q-section class="row justify-between q-pa-sm">
                        <div class="col-11 text-h5 text-primary row justify-evenly">Add a New Tuple</div>
                        <div class="col-1 justify-end row">
                          <q-btn class='' color="primary" icon="close" flat round dense v-close-popup />
                        </div>
                      </q-section>
                      <q-section>
                        <q-form
                          @submit="onSubmit"
                          @reset="onReset"
                          class="q-gutter-md"
                        >
                          <q-input
                            filled
                            v-model="name"
                            label="Your name *"
                            hint="Name and surname"
                            lazy-rules
                            :rules="[ val => val && val.length > 0 || 'Please type something']"
                          />

                          <q-input
                            filled
                            type="number"
                            v-model="age"
                            label="Your age *"
                            lazy-rules
                            :rules="[
                              val => val !== null && val !== '' || 'Please type your age',
                              val => val > 0 && val < 100 || 'Please type a real age'
                            ]"
                          />

                          <q-toggle v-model="accept" label="I accept the license and terms" />

                          <div>
                            <q-btn label="Submit" type="submit" color="primary"/>
                            <q-btn label="Reset" type="reset" color="primary" flat class="q-ml-sm" />
                          </div>
                        </q-form>
                      </q-section>
                    </q-card>
                  </q-dialog> -->
                </div>    
              </q-card-section>
              <q-card-section class="row q-pb-md justify-evenly">
                <q-btn unelevate color='primary' label='save' @click="checkSaveAndTrain"/>
              </q-card-section>
            </div>
          </div>
        </q-card>
        <q-dialog v-model="confirmSaveAndTrain" persistent>
          <q-card style="width: 350px">
            <q-card-section>
              <div class='justify-evenly row'>
                <div v-if="!noGpuMode" class="text-h6 text-primary q-pb-sm q-pl-md">Save and Retrain</div>
                <div v-if="noGpuMode" class="text-h6 text-primary q-pb-sm q-pl-md">Save</div>
              </div>
            </q-card-section>
            <q-card-section class="row justify-evenly" v-if='loadingRetraining'>
              <q-spinner color="primary" size="3em" />
            </q-card-section>
            <q-card-section class="row justify-evenly" v-if='loadingRegenerating'>
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
            <q-card-section class="row justify-evenly">
              <span v-if='!loadingRegenerating && !loadingRetraining' class="q-ml-sm">You want to submit your corrections??</span>
              <span v-if='loadingRegenerating' class="q-ml-sm">Updating the table...</span>
              <span v-if='loadingRetraining' class="q-ml-sm">Training the model...</span>
              <!-- <span v-if='missingEdit' class="q-ml-sm">Please edit or confirm all red and yellow values</span> -->
              <!-- <span v-if='zeroWarns' class="q-ml-sm" style='text-align: center'>There are no more critical samples, now you can inspect the remaining samples and save all the remaining samples  with the 'Save All' button. Once all samples are saved you can download them with the 'Export' button  </span> -->
            </q-card-section>

            <q-card-actions v-if='!loadingRegenerating && !loadingRetraining' class="row justify-evenly">
              <q-btn class="q-pb-sm" flat label="No" color="primary" @click='missingEdit=false;confirmSaveAndTrain=false'/>
              <q-btn class="q-pb-sm" flat label="Yes" @click='saveAndTrain()' color="primary"/>
            </q-card-actions>
          </q-card>
        </q-dialog>
        <q-card class="col-3">
          <div style="height: 100%" class="column justify-between">
            <q-card-section class="row justify-evenly">
              <div class="text-h5">Editor</div>
            </q-card-section>
            <q-card-section>
              <q-field borderless label="Selected Attribute:" label-color='primary' stack-label>
                <template v-slot:control>
                  <div class="self-center full-width no-outline" tabindex="0">
                    {{ predictionIndex === 'no_index' ? 'Select a field' : editable_predictions[instanceIndex][predictionIndex].attribute }}
                  </div>
                </template>
              </q-field>
              <q-field borderless label="Confidence:" label-color='primary' stack-label>
                <template v-slot:control>
                  <div class="self-center full-width no-outline" tabindex="0">
                    {{ predictionIndex === 'no_index' ? 'Select a field' : Math.round(editable_predictions[instanceIndex][predictionIndex].confidence) * 100 + '%'}}
                  </div>
                  <!-- Math.round(prediction.confidence * 100 -->
                </template>
              </q-field>
              <q-checkbox v-model="fullPaperValue" left-label class="text-primary" label="Abstract doesn't contain this information" />
            </q-card-section>
            <q-card-section>
              <q-select
                outlined
                dense
                bg-color='grey-3'
                v-model="insertedValue"
                use-input
                fill-input
                hide-selected
                @input-value="onInputValue"
                input-debounce="0"
                :options="filterOptions"
                new-value-mode="add-unique"
                @filter="filterFn"
                @click.capture="onClick"
                @popup-hide="onPopupHide"
                @popup-show="onPopupShow"
              />
            </q-card-section>
            <div class="q-pt-md row justify-evenly">
              <div class="q-pb-md">
                <q-btn label="edit" @click="editValue" rounded color="primary" />
              </div>
            </div>
          </div>
        </q-card>
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
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import { api, apiGPU } from 'boot/axios'

const visible_columns = [
  // "cord_uid",
  // "index",
  "doi",
  "title",
  "authors",
  "abstract",
  "journal",
  "citations",
  "warns"
]

const annotated_visible_columns = [
  // "cord_uid",
  "doi",
  "title",
  "authors",
  "abstract",
  "journal",
  "citations",
  "extractions"
]

export default {
  name: 'AL',
  setup () {
    // how use notify
    // const $q = useQuasar()
    // $q.notify({
    //         color: 'red-5',
    //         textColor: 'white',
    //         icon: 'warning',
    //         message: 'You need to accept the license and terms first'
    //       })
    const $q = useQuasar()
    return {
      showNotif (message) {
        $q.notify({
          color: 'red-5',
          textColor: 'white',
          icon: 'warning',
          position: 'top',
          message: message
        })
      },
      lastPredictionIndex: ref(0),
      fullPaperValue: ref(false),
      noGpuMode: ref(false),
      showAddInstance: ref(false),
      annotated_visible_columns,
      visible_columns,
      showFixedList: ref(false),
      paperList: ref([]),
      currentPaper: ref(0),
      showList: ref(false),
      attributeLabels: ref({
        mutation_type: 'Mutation Type',
        mutation_name: 'Mutation Name',
        effect: 'Effect',
        level: 'Level'
      }),
      editable_predictions: ref([
        [
          { attribute: 'mutation_type', value: "Insert Value", confidence: 1, fixed: false },
          { attribute: 'mutation_name', value: "Insert Value", confidence: 1, fixed: false },
          { attribute: 'effect', value: "Insert Value", confidence: 1, fixed: false },
          { attribute: 'level', value: "Insert Value", confidence: 1, fixed: false }
        ],
        // [
        //   { attribute: 'Mutation Type', value: "single", confidence: 1 },
        //   { attribute: 'Name', value: "spike_A222V", confidence: 0.7 },
        //   { attribute: 'Effect', value: "trasmissibility", confidence: 0.7 },
        //   { attribute: 'Level', value: "low", confidence: 0.4 }
        // ],
      ]),
      predictionIndex: ref(0),
      instanceIndex: ref(0),
      greenThreshold: ref(0.8),
      redThreshold: ref(0.6),
      insertedValue: ref(''),
      filterOptions: ref([]),
      stringOptions: ref({
        mutation_type: ['single', 'group', 'variant'],
        mutation_name: [],
        effect: ['risk_of_reinfection', 'viral_load',
       'effectiveness_of_available_antiviral_drugs', 'binding_to_Abs',
       'binding_to_host_receptor', 'protein_stability',
       'sensitivity_to_convalescent_sera', 'viral_transmission',
       'sensitivity_to_neutralizing_mAbs', 'protein_flexibility',
       'infectivity', 'intraviral_protein_protein_interaction'],
        level: ['higher', 'lower', 'unknown']
      }),
      selected: ref([]),
      highlighted_abstract: ref([{ text: '', color: 'bg-white' }]),
      feedback_list: ref([]),
      saliency_maps: ref([]),
      output_attributes: ref([
        'mutation_type',
        'mutation_name',
        'effect',
        'level'
      ]),
      pagination: ref({
        rowsPerPage: 200,
        sortBy: 'index',
        descending: true
      }),
      columns: [
        { name: 'index', label: '#', field: 'index',required: false, align: 'left' },
        { name: 'doi', label: 'Doi', field: 'doi', required: true, align: 'left' },
        { name: 'title', label: 'Title', field: 'title', sortable: true, align: 'left' },
        { name: 'authors', label: 'Authors', field: 'authors', sortable: true, align: 'left' },
        { name: 'abstract', label: 'Abstract', field: 'abstract', align: 'left' },
        // { name: 'year', label: 'Year', field: 'year', sortable: true, align: 'left' },
        { name: 'journal', label: 'Source', field: 'journal', sortable: true, align: 'left' },
        { name: 'citations', label: 'Citations', field: 'numCitedBy', align: 'center' },
        { name: 'warns', label: 'Warns', field: 'warns', sortable: true, align: 'center' },
        { name: 'extractions', label: 'Extracted Values', sortable: false, align: 'center' }
      ],
      // fixedColumns: [
      //   // { name: 'index', label: '#', field: 'index',required: true, align: 'left' },
      //   { name: 'doi', label: 'Doi', field: 'doi', required: true, align: 'left' },
      //   { name: 'title', label: 'Title', field: 'title', sortable: true, align: 'left' },
      //   { name: 'authors', label: 'Authors', field: 'authors', sortable: true, align: 'left' },
      //   { name: 'abstract', label: 'Abstract', field: 'abstract', align: 'left' },
      //   // { name: 'year', label: 'Year', field: 'year', sortable: true, align: 'left' },
      //   { name: 'journal', label: 'Source', field: 'journal', sortable: true, align: 'left' },
      //   { name: 'citations', label: 'Citations', field: 'numCitedBy', align: 'center' },
      //   // { name: 'mutation', label: 'Mutation', field: (row) => row.extracted_values.mutation.value, sortable: true, align: 'left' },
      //   // { name: 'effect', label: 'Effect', field: (row) => row.extracted_values.effect.value, sortable: true, align: 'left' },
      //   // { name: 'level', label: 'Level', field: (row) => row.extracted_values.level.value, sortable: true, align: 'left' }
      //   // { name: 'keep', label: 'Keep', field: 'keep', sortable: false, align: 'center' }
      // ],
      confirmSaveAndTrain: ref(false),
      loadingRetraining: ref(false),
      loadingRegenerating: ref(false),
      loadStatus: ref(0),
      edited_Papers: ref([]),
      fixedPapers: ref([]),
      loadGpt2: ref(false)
    }
  },
  methods : {
    extraction (index) {
      this.loadGpt2 = true
      apiGPU.post('/extract_attributes',
      {
        input: this.paperList[index].abstract,
        output_attributes: this.output_attributes
      },
      {
        timeout: 6000
      }).then( (response) => {
        this.editable_predictions =  JSON.parse(JSON.stringify(response.data.outputs))
        // this.predictions.unshift({ attribute: 'mutation type', value: "missing", confidence: 0 })
        // this.predictions.push({ attribute: 'effect', value: "missing", confidence: 0 })
        // this.predictions.push({ attribute: 'level', value: "missing", confidence: 0 })
        this.saliency_maps = response.data.saliency_map
        this.loadGpt2 = false
        this.visualize(0)
      }).catch((error) => {
        error.message
        this.activateNoGpuMode()
      })
    },
    visualize (instanceIndex, predictionIndex) {
      if (this.predictionIndex !== predictionIndex) {
        this.$nextTick(() => {
          this.$refs.editable.$el.focus()
        })
      }
      this.fullPaperValue = false
      this.instanceIndex = instanceIndex
      this.predictionIndex = predictionIndex
      this.insertedValue = this.editable_predictions[instanceIndex][predictionIndex].value
      if (this.saliency_maps.length > 0) this.highlighted_abstract = this.saliency_maps[instanceIndex][predictionIndex][0]

    },
    generateTable () {
      let abstract_list = []
      for ( const paper of this.paperList) {
        abstract_list.push(paper.abstract)
      }
      // this.showNotif('The GPU server is not available, users can only annotate papers')
      apiGPU.post(
        '/generateTable',
        { output_attributes: this.output_attributes, inputs: abstract_list },
        { timeout: 6000 }
      ).then( (response) => {
        const extracted_values_list = response.data
        for ( const [index, extracted_values] of extracted_values_list.entries()) {
          this.paperList[index]['extracted_values'] = extracted_values
          this.paperList[index]['warns'] = this.count_warns(this.paperList[index])
        }
        this.resetPage()
      }).catch( (error) => {
        error.message
        const maxStatus = this.getSampleWithMaxWarns()
        if (maxStatus.index !== null) {
          this.selected = [ this.paperList[maxStatus.index] ]
        }
        this.currentPaper = maxStatus.index
        this.activateNoGpuMode()
      })
    },
    activateNoGpuMode () {
      this.loadGpt2 = false
      this.noGpuMode = true
      this.highlighted_abstract = [{ text: this.paperList[this.currentPaper].abstract, color: 'bg-white' }]
      this.showNotif('The prediction model is not available, users can only annotate papers')
    },
    count_warns (row) {
      if (!Object.keys(row).includes('extracted_values')) return row.index
      var nWarn = 0
      for (const prediction_instance of row.extracted_values) {
        for (var attribute of this.output_attributes) {
          if (prediction_instance[attribute].confidence < this.redThreshold) {
            nWarn += 1
          }
        }
      }
      return nWarn
    },
    getOutputColor (prediction) {
      if (prediction.fixed) {return 'info'}
      if (prediction.value === "Insert Value") {return 'grey-3'}
      if (prediction.confidence > this.greenThreshold) return 'green-3'
      else {
        if (prediction.confidence < this.redThreshold) return 'red-3'
        else return 'orange-3'
      }
    },
    filterFn (val, update) {
      // console.log(this.output_fields[2][[0]])
      update(() => {
        const index = this.predictionIndex === 'no_index' ? 0 : this.predictionIndex
        if (val === '') {
          this.filterOptions = this.stringOptions[this.output_attributes[index]].filter(
            v => v.length < 40
          )
        } else {
          const needle = val.toLowerCase()
          this.filterOptions = this.stringOptions[this.output_attributes[index]].filter(
            v => v.toLowerCase().indexOf(needle) > -1 && v.length < 40
          )
        }
      })
    },
    createValue (val, done) {
      if (val.length > 0) {
        if (!this.stringOptions.includes(val)) {
          this.stringOptions.push(val)
        }
        done(val, 'toogle')
      }
    },
    onInputValue (val) {
      this.insertedValue = val
    },
    onPopupShow (val) {
      this.popupOpen = true
    },
    onPopupHide (val) {
      this.popupOpen = false
    },
    onClick (event) {
      if (
        this.popupOpen === true
        // && event.target.nodeName.toLowerCase() === 'input' // only on click in input
      ) {
        event.stopImmediatePropagation()
      }
      // forces popup to show again. Can't avoid flickering
      // this.$refs.input.showPopup()
    },
    editValue () {
      if (this.insertedValue === '' || this.insertedValue === 'Insert Value') {
        this.showNotif('Insert a Value')
        return
      }
      this.editable_predictions[this.instanceIndex][this.predictionIndex].value = this.insertedValue
      this.editable_predictions[this.instanceIndex][this.predictionIndex].confidence = 1
      this.editable_predictions[this.instanceIndex][this.predictionIndex].fixed = true
      this.editable_predictions[this.instanceIndex][this.predictionIndex].fullPaperValue = this.fullPaperValue

      // console.log(Date())
      this.feedback_list.push(
        {
          timestamp: Date(),
          value: this.insertedValue,
          attribute: this.editable_predictions[this.instanceIndex][this.predictionIndex].attribute,
          doi: this.selected[0].doi,
          cord_uid: this.selected[0].cord_uid,
          abstract: this.selected[0].abstract
        }
      )
    },
    loadSelection (evt, row, index) {
      this.showList = false
      // console.log(row)
      this.currentPaper = row.index
      this.selected = [row]
      this.extraction(this.currentPaper)
      // console.log(this.selected[0])
    },
    resetPage () {
      // this.selected = [this.paperList[0]]
      this.insertedValue = ''
      this.highlighted_abstract = [{ text: this.paperList[this.selected[0].index].abstract, color: 'bg-white' }]
      this.editable_predictions = []
      this.feedback_list = []
      const maxStatus = this.getSampleWithMaxWarns()
      if (maxStatus.index !== null) {
        this.selected = [ this.paperList[maxStatus.index] ]
      }
      this.currentPaper = maxStatus.index
      this.extraction(this.currentPaper)
    },
    getSampleWithMaxWarns () {
      let max = -1
      let maxId = null
      for (const [index, row] of this.paperList.entries()) {
        if (this.count_warns(row) > max) {
          max = this.count_warns(row)
          maxId = index
        }
      }
      return { index: maxId, max: max }
    },
    saveAndTrain () {
      api.post(
        '/saveFeedbacks',
        { feedback_list: this.feedback_list }
      ).catch( (error) => (error.message))
      if (this.noGpuMode === true) {
        let extracted_values = []
        for (const instance of this.editable_predictions) {
          let output_instance = {}
          for (const [index, attribute] of this.output_attributes.entries()) {
            output_instance[attribute] = instance[index]
          }
          extracted_values.push(output_instance)
        }
        // console.log(extracted_values)
        this.paperList[this.currentPaper].extracted_values = extracted_values
        this.paperList[this.currentPaper].annotated = true
        this.paperList[this.currentPaper].warns = this.count_warns(this.paperList[this.currentPaper])
        api.post(
          '/paperlist',
          { paper_list: this.paperList }
        ).catch( (error) => error.message)
        const correctedRow = JSON.parse(JSON.stringify(this.paperList[this.currentPaper]))
        correctedRow.index = this.fixedPapers.length
        // console.log(correctedRow)
        this.fixedPapers.push(correctedRow)
        // console.log(this.fixedPapers)
        this.storeFixedPapers()
        this.confirmSaveAndTrain = false
        return
      }
      this.loadingRetraining = true
      const outputs = []
      // for (const output of this.editable_predictions) {
      //   if (output.fixed === true) outputs.push({ attribute: output.attribute, value: output.value })
      // }
      for (const output of this.editable_predictions) {
        outputs.push({ attribute: output.attribute, value: output.value })
      }
      apiGPU.post(
        '/saveAndTrain',
        {
          input_text: this.paperList[this.predictionIndex].abstract,
          outputs: outputs
        }
      ).then((response) => {
        const inputList = []
        for (const row of this.paperList) {
          inputList.push(row.abstract)
        }
        // TODO: aggiungi il sample modificato alla lista dei sample modificati

        this.loadingRetraining = false
        this.loadingRegenerating = true
        apiGPU.post(
          '/generateTable',
          { output_attributes: this.output_attributes, inputs: inputList }
        ).then((response) => {
          // this.dataset_json[this.datasetType] = response.data
          // for (const [index, row] of this.paperList.entries()) {
          //   for (const attribute of this.output_attributes) {
          //     if (this.paperList[index].extracted_values[attribute].fixed) {
          //       // console.log('uno fixato')
          //       // console.log(row.fields[field].value)
          //       newTable[index].fields[field].value = row.fields[field].value
          //       newTable[index].fields[field].confidence = row.fields[field].confidence
          //       newTable[index].fields[field].fixed = true
          //     }
          //   }
          //   this.loadingRegenerating = false
          // }
          const correctedRow = JSON.parse(JSON.stringify(this.paperList[this.currentPaper]))
          correctedRow.index = this.fixedPapers.length
          this.fixedPapers.push(correctedRow)
          const extracted_values_list = response.data
          for ( const [index, extracted_values] of extracted_values_list.entries()) {
            this.paperList[index]['extracted_values'] = extracted_values
            this.paperList[index]['warns'] = this.count_warns(this.paperList[index])
          }
          this.paperList.splice(this.currentPaper, 1)
          for (const [newIndex, row] of this.paperList.entries()) {
            this.paperList[newIndex].index = newIndex
          }
          this.storeFixedPapers()
          this.resetPage()
          this.confirmSaveAndTrain = false
        }).catch(error => {
          console.log(error.message)
          this.confirmSaveAndTrain = false
        })
        this.loadStatus = 0
        this.getLoadStatus()
      }).catch(error => {
        console.log(error.message)
        this.loadingRetraining = false
      })
      // seleziono paper subito dopo
      // this.selected = [this.paperList[this.selected[0].index + 1]]
      // this.loadSelection()
    },
    getLoadStatus () {
      apiGPU.get('/getGenerateStatus')
        .then(responde => {
          this.loadStatus = Math.round(responde.data)
          console.log(this.loadStatus)
          if (this.loadStatus < 100) this.getLoadStatus()
        }).catch(error => console.log(error))
    },
    storeFixedPapers () {
      api.post(
        '/fixedPapers',
        { fixed_papers: this.fixedPapers }
      ).catch( (error) => (error.message))
    },
    addInstance () {
      this.editable_predictions.push(
        [
          { attribute: 'mutation_type', value: "Insert Value", confidence: 1, fixed: false },
          { attribute: 'mutation_name', value: "Insert Value", confidence: 1, fixed: false },
          { attribute: 'effect', value: "Insert Value", confidence: 1, fixed: false },
          { attribute: 'level', value: "Insert Value", confidence: 1, fixed: false }
        ]
      )
    },
    checkSaveAndTrain () {
      for (const prediction_instance of this.editable_predictions) {
        for (const prediction of prediction_instance) {
          if (prediction.value === '' || prediction.value === 'Insert Value') {
            this.showNotif('One or more values are missing')
            return
          }
        }
      }
      this.confirmSaveAndTrain = true
    }
  },
  created () {
    this.loadGpt2 = true
    api.get(
      '/mutationValues'
    ).then( (response) => {
      this.stringOptions.mutation_name = response.data
      // console.log(response.data)
    }).catch( (error) => {error.message})
    api.get(
      '/paperlist'
    ).then((response) => {
      api.get(
        '/fixedPapers'
      ).then( (response) => {
        this.fixedPapers = response.data
      })
      this.paperList = response.data.paper_list
      this.generateTable()
    }).catch((error) => (error.message))
  }
}
</script>
