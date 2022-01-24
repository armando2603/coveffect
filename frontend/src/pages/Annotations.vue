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
        <div class="q-pt-md">
        <q-card style="flex-grow: 1;overflow: auto">
          <q-card-section class="row justify-evenly">
            <div class="text-h5">Annotated Papers List</div>
          </q-card-section>
          <q-card-section>
            <div>
              <div>
                <!-- <q-field stack-label borderless label-color="primary" label='DOI:'>
                  <template v-slot:control>
                    <div v-if="paperList.length !== 0" class="self-center full-width no-outline" tabindex="0"><a :href="'https://dx.doi.org/' + paperList[currentPaper].doi" target="_blank">{{paperList[currentPaper].doi}}</a></div>
                  </template>
                </q-field> -->
              </div>
            </div>
          </q-card-section>
        </q-card>
        </div>
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
      fixedPapers: ref([]),
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
    api.get(
      '/fixedPapers'
    ).then( (response) => {
      this.fixedPapers = response.data
    }).catch( (error) => error.message)
  }
}
</script>
