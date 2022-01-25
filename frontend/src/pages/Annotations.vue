<template>
  <q-page padding class="row items-strech">
    <div class="column col-12 no-wrap">
      <!-- <div class="q-pa-md column" style="flex-grow: 1;overflow: auto"> -->
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
          v-model:pagination='pagination'
          >
          <template v-slot:top>
            <div class="row justify-start" style="width: 100%">
              <q-btn icon="arrow_back" rounded color="red-4" to="/AL" />
              <div class="text-h5 text-primary q-pl-md q-pr-md">
                Annotated Papers List
              </div>
            </div>
          </template>
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
              <q-btn unelevated dense size="sm" color="primary" label='Extracted Values' @click="showExtractedValues = true; currentPaper = props.row.index"/>
            </q-td>
          </template>
        </q-table>
        <q-dialog v-model="showExtractedValues">
          <q-card style="width: 40%;height: 100%">
            <q-card-section class="row justify-evenly">
              <div class="col-11 text-h5 text-bold text-primary row justify-evenly">Extracted Values</div>
              <div class="col-1 justify-end row">
                <q-btn class='' color="primary" icon="close" flat round dense v-close-popup />
              </div>
            </q-card-section>
            <q-card-section>
              <div class="q-pt-md" v-for="(predictions_instance, instance_index) in fixedPapers[currentPaper].extracted_values" :key="predictions_instance">
                <q-card class="">
                <div class="q-pl-md">
                <div class="text-primary text-h6">{{'Instance: ' + instance_index}}</div>
                <div class='row no-wrap' v-for="attribute in output_attributes"  :key="attribute">
                  <!-- {{predictions_instance[attribute]}} -->
                  <q-field style="width: 300px" stack-label borderless label-color="primary" :label='attribute'>
                    <template v-slot:control>
                      <div v-if="fixedPapers.length !== 0" class="self-center full-width no-outline" tabindex="0">{{predictions_instance[attribute].value}}</div>
                    </template>
                  </q-field>
                  <div class="q-pl-xl column justify-evenly">
                  <q-badge v-if='predictions_instance[attribute].fullPaperValue' color="orange-8" label="Not in abstract" style='white-space: pre-line;height: 20px'/>
                  </div>
                </div>
                </div>
                </q-card>
              </div>
            </q-card-section>
          </q-card>
        </q-dialog>
    </div>
    <!-- content -->
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
import { api } from 'boot/axios'

export default {
  // name: 'PageName',
  setup () {
    return {
      showExtractedValues: ref(false),
      fixedPapers: ref([]),
      currentPaper: ref(0),
      output_attributes: ref([
        'mutation_type',
        'mutation_name',
        'effect',
        'level'
      ]),
      columns: [
        // { name: 'index', label: '#', field: 'index',required: true, align: 'left' },
        { name: 'doi', label: 'Doi', field: 'doi', required: true, align: 'left' },
        { name: 'title', label: 'Title', field: 'title', sortable: true, align: 'left' },
        { name: 'authors', label: 'Authors', field: 'authors', sortable: true, align: 'left' },
        { name: 'abstract', label: 'Abstract', field: 'abstract', align: 'left' },
        // { name: 'year', label: 'Year', field: 'year', sortable: true, align: 'left' },
        { name: 'journal', label: 'Source', field: 'journal', sortable: true, align: 'left' },
        { name: 'citations', label: 'Citations', field: 'numCitedBy', align: 'center' },
        // { name: 'warns', label: 'Warns', field: 'warns', sortable: true, align: 'center' },
        { name: 'extractions', label: 'Extracted Values', sortable: false, align: 'center' }
      ],
      pagination: ref({
        rowsPerPage: 200,
        sortBy: 'index',
        descending: true
      }),
    }
  },
  methods : {},
  created () {
    this.currentPaper = 0
    api.get(
      '/fixedPapers'
    ).then( (response) => {
      this.fixedPapers = response.data
      // console.log(this.fixedPapers[this.currentPaper])
    }).catch( (error) => error.message)
  }
}
</script>
