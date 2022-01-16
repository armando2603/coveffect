<template>
  <q-page padding class="row items-strech">
    <div class="col-12 column no-wrap">
      <q-dialog v-model='showFixedList'>
        <q-card class="column no-wrap" style="min-width: 100%; height: 95%">
          <q-card-section class="row justify-between">
            <div class="text-h5">Fixed Paper List</div>
            <div class="col-1 justify-end row">
              <q-btn class='' icon="close" flat round dense v-close-popup />
            </div>
          </q-card-section>
          <q-card-section class="column" style="height: 100%">
            <div class="q-pa-md column" style="flex-grow: 1;overflow: auto">
              <q-table
              style="flex-grow: 1;overflow: auto"
              class="my-sticky-virtscroll-table"
              :columns="fixedColumns"
              :rows="fixedPapers"
              virtual-scroll
              wrap-cells
              separator="cell"
              row-key="index"
              :rows-per-page-options="[0]"
              :virtual-scroll-sticky-size-start="48"
              my-sticky-virtscroll-table
              >
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
              row-key="index"
              :rows-per-page-options="[0]"
              :virtual-scroll-sticky-size-start="48"
              my-sticky-virtscroll-table
              v-model:selected="selected"
              v-model:pagination='pagination'
              selection="single"
              @update:selected='loadSelection'
              >
              </q-table>
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>
      <div class="row justify-end">
        <div class="col-1 column justify-evenly">
            <div class="row justify-end">
              <q-btn
                label="Saved Samples"
                style="width:150px"
                @click="showFixedList = true"
                color="primary"
              />
            </div>
        </div>
        <div class="col-1 column justify-evenly">
            <div class="row justify-end">
              <q-btn
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
              <q-spinner color="primary" size="2em" />
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
        <q-card class="col-3 column justify-evenly">
          <q-card-section class="row justify-evenly">
            <div class="text-h5">Paper Info</div>
          </q-card-section>
          <q-card-section class="column justify-evenly">
            <q-field stack-label borderless label-color="primary" label='DOI:'>
              <template v-slot:control>
                <div class="self-center full-width no-outline" tabindex="0">{{paperList.length === 0 ? '' : paperList[currentPaper].doi}}</div>
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
            <q-field stack-label borderless label-color="primary" label='Year:'>
              <template v-slot:control>
                <div class="self-center full-width no-outline" tabindex="0">{{paperList.length === 0 ? '' : paperList[currentPaper].year}}</div>
              </template>
            </q-field>
          </q-card-section>
        </q-card>
        <q-card class="col-5 column justify-between">
          <div>
          <q-card-section class="row justify-evenly">
            <div class="text-h5">Extracted Values</div>
          </q-card-section>
          <q-card-section>
            <div v-if='loadGpt2' class='row q-mt-md q-mb-md justify-evenly'>
              <q-spinner color="primary" size="4em" />
            </div>
            <div v-if='!loadGpt2' class='my-outputs row'>
              <div style="width: 133px;height: auto" class='' v-for="(prediction, index) in editable_predictions" @click="visualize(index)"  :key="prediction">
                <div class='q-pa-sm'>
                <q-field
                :class="index===lastIndex?'output-field':'output-field'"
                label-color="grey-10"
                color='indigo-8'
                stack-label
                outlined
                dense
                :bg-color='getOutputColor(prediction)'
                :label="prediction.attribute" >
                  <template v-slot:control>
                    <div class="self-center full-width no-outline q-pb-sm q-pt-md text-h13" style="overflow: hidden" tabindex="0">
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
          </q-card-section>
          </div>
          <q-card-section class="row justify-evenly">
            <q-btn unelevate color='primary' label='save' @click="confirmSaveAndTrain = true"/>
          </q-card-section>
        </q-card>
        <q-dialog v-model="confirmSaveAndTrain" persistent>
          <q-card style="width: 350px">
            <q-card-section>
              <div class='justify-evenly row'>
                <div class="text-h6 text-primary q-pb-sm q-pl-md">Save and Retrain</div>
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
        <q-card class="col-3 column justify-evenly">
          <q-card-section class="row justify-evenly">
            <div class="text-h5">Editor</div>
          </q-card-section>
          <q-card-section>
            <q-field borderless label="Selected Attribute:" label-color='primary' stack-label>
              <template v-slot:control>
                <div class="self-center full-width no-outline" tabindex="0">
                  {{ lastIndex === 'no_index' ? 'Select a field' : editable_predictions[lastIndex].attribute }}
                </div>
              </template>
            </q-field>
            <q-field borderless label="Confidence:" label-color='primary' stack-label>
              <template v-slot:control>
                <div class="self-center full-width no-outline" tabindex="0">
                  {{ lastIndex === 'no_index' ? 'Select a field' : editable_predictions[lastIndex].confidence }}
                </div>
              </template>
            </q-field>
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
            <div class="">
              <q-btn label="edit" @click="editValue" rounded color="primary" />
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
import { api, apiGPU } from 'boot/axios'
export default {
  name: 'AL',
  setup () {
    return {
      showFixedList: ref(false),
      paperList: ref([]),
      currentPaper: ref(0),
      showList: ref(false),
      editable_predictions: ref([]),
      lastIndex: ref('no_index'),
      greenThreshold: ref(0.8),
      redThreshold: ref(0.6),
      insertedValue: ref(''),
      filterOptions: ref([]),
      stringOptions: ref({
        mutation: [],
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
        'mutation',
        'effect',
        'level'
      ]),
      pagination: ref({
        rowsPerPage: 200,
        sortBy: 'warns',
        descending: true
      }),
      columns: [
        { name: 'index', label: '#', field: 'index',required: true, align: 'left' },
        { name: 'doi', label: 'Doi', field: 'doi', required: true, align: 'left' },
        { name: 'title', label: 'Title', field: 'title', sortable: true, align: 'left' },
        { name: 'authors', label: 'Authors', field: 'authors', sortable: true, align: 'left' },
        { name: 'abstract', label: 'Abstract', field: 'abstract', align: 'left' },
        // { name: 'year', label: 'Year', field: 'year', sortable: true, align: 'left' },
        { name: 'journal', label: 'Journal', field: 'journal', sortable: true, align: 'left' },
        { name: 'warns', label: 'Warns', field: 'warns', sortable: true, align: 'center' }
        // { name: 'keep', label: 'Keep', field: 'keep', sortable: false, align: 'center' }
      ],
      fixedColumns: [
        { name: 'index', label: '#', field: 'index',required: true, align: 'left' },
        { name: 'doi', label: 'Doi', field: 'doi', required: true, align: 'left' },
        { name: 'title', label: 'Title', field: 'title', sortable: true, align: 'left' },
        { name: 'authors', label: 'Authors', field: 'authors', sortable: true, align: 'left' },
        { name: 'abstract', label: 'Abstract', field: 'abstract', align: 'left' },
        // { name: 'year', label: 'Year', field: 'year', sortable: true, align: 'left' },
        { name: 'journal', label: 'Journal', field: 'journal', sortable: true, align: 'left' },
        { name: 'mutation', label: 'Mutation', field: (row) => row.extracted_values.mutation.value, sortable: true, align: 'left' },
        { name: 'effect', label: 'Effect', field: (row) => row.extracted_values.effect.value, sortable: true, align: 'left' },
        { name: 'level', label: 'Level', field: (row) => row.extracted_values.level.value, sortable: true, align: 'left' }
        // { name: 'keep', label: 'Keep', field: 'keep', sortable: false, align: 'center' }
      ],
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
      }).then( (response) => {
        this.editable_predictions =  JSON.parse(JSON.stringify(response.data.outputs))
        // this.predictions.unshift({ attribute: 'mutation type', value: "missing", confidence: 0 })
        // this.predictions.push({ attribute: 'effect', value: "missing", confidence: 0 })
        // this.predictions.push({ attribute: 'level', value: "missing", confidence: 0 })
        this.saliency_maps = response.data.saliency_map
        this.loadGpt2 = false
        this.visualize(0)
      }).catch((error) => (error.message))
    },
    visualize (index) {
      // if (this.lastIndex !== index) {
      //   this.$nextTick(() => {
      //     console.log(this.$refs.editables_2)
      //     this.$refs.editables_2.click()
      //   })
      // }

      this.lastIndex = index
      this.insertedValue = this.editable_predictions[index].value
      this.highlighted_abstract = this.saliency_maps[index][0]

    },
    generateTable () {
      let abstract_list = []
      for ( const paper of this.paperList) {
        abstract_list.push(paper.abstract)
      }
      apiGPU.post(
        '/generateTable',
        { output_attributes: this.output_attributes, inputs: abstract_list }
      ).then( (response) => {
        const extracted_values_list = response.data
        for ( const [index, extracted_values] of extracted_values_list.entries()) {
          this.paperList[index]['extracted_values'] = extracted_values
          this.paperList[index]['warns'] = this.count_warns(this.paperList[index])
        }
        this.resetPage()
      }).catch( (error) => error.message)
    },
    count_warns (row) {
      if (!Object.keys(row).includes('extracted_values')) return row.index
      var nWarn = 0
      for (var attribute of this.output_attributes) {
        if (row.extracted_values[attribute].confidence < this.redThreshold) {
          nWarn += 1
        }
      }
      return nWarn
    },
    getOutputColor (prediction) {
      if (prediction.fixed) {return 'info'}
      if (prediction.confidence > this.greenThreshold) return 'green-3'
      else {
        if (prediction.confidence < this.redThreshold) return 'red-3'
        else return 'orange-3'
      }
    },
    filterFn (val, update) {
      // console.log(this.output_fields[2][[0]])
      update(() => {
        const index = this.lastIndex === 'no_index' ? 0 : this.lastIndex
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
      this.editable_predictions[this.lastIndex].value = this.insertedValue
      this.editable_predictions[this.lastIndex].confidence = 1
      this.editable_predictions[this.lastIndex].fixed = true
      this.feedback_list.push(
        {
          value: this.insertedValue,
          attribute: this.editable_predictions[this.lastIndex].attribute,
          doi: this.selected[0].doi,
          cord_uid: this.selected[0].cord_uid,
          abstract: this.selected[0].abstract
        }
      )
    },
    loadSelection () {
      this.showList = false
      this.currentPaper = this.selected[0].index
      this.extraction(this.currentPaper)
      // console.log(this.selected[0])
    },
    resetPage () {
      this.selected = [this.paperList[0]]
      this.insertedValue = ''
      this.highlighted_abstract = [{ text: this.paperList[this.selected[0].index].abstract, color: 'bg-white' }]
      this.editable_predictions = []
      this.feedback_list = []
      const maxStatus = this.getSampleWithMaxWarns()
      if (maxStatus.index !== null) {
        this.selected = [{ index: maxStatus.index }]
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
          input_text: this.paperList[this.lastIndex].abstract,
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
    }
  },
  created () {
    this.loadGpt2 = false
    api.get(
      '/mutationValues'
    ).then( (response) => {
      this.stringOptions.mutation = response.data
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
