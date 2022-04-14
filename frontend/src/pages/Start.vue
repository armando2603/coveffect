<template>
  <q-page class="row items-strech">
    <div class="column col-12 no-wrap">
      <q-dialog v-model="alert">
        <q-card >
          <q-card-section class="row justify-evenly">
            <!-- <div class="text-h6 text-red-5">No Abstract Found</div> -->
            <div class="text-h6 text-red-4">{{alertContent.title}}</div>
          </q-card-section>

          <q-card-section class="q-pt-none row justify-evenly">
            <!-- <div class="text-grey-7">The paper cannot be added</div> -->
            <div class="text-grey-7">{{alertContent.body}}</div>
          </q-card-section>

          <q-card-actions align="center">
            <q-btn flat label="OK" color="primary" v-close-popup />
          </q-card-actions>
        </q-card>
      </q-dialog>
      <!-- <div class="q-pa-md row justify-end no-wrap">
        <q-card class='row' style="width: 100%">
          <div class="q-pa-md col-8">
            <q-input v-model="doi" stack-label label="Insert a DOI" />
          </div>
          <div class="column justify-center q-pa-sm">
            <q-btn class='' rounded icon='add' color='primary' @click='getPaper'/>
          </div>
        </q-card>
        <div class="column justify-center q-pl-md q-pr-md">
          <q-btn class='' rounded icon='arrow_forward' color='positive' @click='saveList'/>
        </div>
      </div> -->
      <div class="q-pl-sm q-pr-sm q-mr-sm q-mt-sm row justify-between">
        <div class="q-pl-sm">
          <q-btn class='' rounded icon='arrow_back' color='primary' to="/" />
        </div>
        <div class="text-primary q-pt-sm text-h6 column justify-evenly">Select relevant papers among the results to continue</div>
        <q-btn class='' rounded icon='arrow_forward' color='positive' @click='saveList'/>
      </div>
      <div class="q-pl-md q-pr-md q-pb-sm q-pt-sm column" style="flex-grow: 1">
        <q-table
        class="my-sticky-virtscroll-table"
        style="overflow: auto; flex-grow: 1"
        table-header-style="text-align: left"
        table-header-class="align-left"
        wrap-cells
        virtual-scroll
        :rows-per-page-options="[0]"
        separator="cell"
        :virtual-scroll-item-size="48"
        :virtual-scroll-sticky-size-start="48"
        :rows="rows"
        :columns="columns"
        row-key="index"
        selection='multiple'
        v-model:selected='selection'
        v-model:pagination='pagination'
        :visible-columns="visible_columns"
        >
          <template v-slot:top>
            <div class="row justify-between" style="width: 100%">
              <div class="text-h5 text-primary q-pl-md q-pr-md">{{'Results for : "' + $route.params.keyword + '"'}}</div>
              <div class="col-4 row justify-end">
                <q-btn class='' rounded icon='add' color='primary' @click='showAddPaper=true'/>
                <!-- <div class='q-pl-sm'>
                  <q-btn rounded v-if='rows.length > 0' icon='remove' color='red-8' @click='removeSelection'/>
                </div> -->
                <div class="q-pl-sm">
                  <q-btn class='' label="Export TSV" rounded no-caps color='primary' @click='exportTSV'/>
                </div>
              </div>
            </div>
          </template>
          <template v-slot:body-cell-keep="props">
            <q-td
            key='keep'
            :props="props"
            :class="props.row.added ? 'bg-green-1' : ((props.row.similar_to !== '')?'bg-cyan-1':'bg-white')"
            >
              <q-checkbox v-model="props.row.keep" />
            </q-td>
          </template>
           <!-- <template v-slot:body-cell-journal="props">
            <q-td
            key='journal'
            :props="props"
            :class="props.row.added ? 'bg-green-1' : ((props.row.similar_to !== '')?'bg-cyan-1':'bg-white')"
            >
              {{props.value === "" ? 'preprint' : props.value}}
            </q-td>
          </template> -->
          <template v-slot:body-cell-doi="props">
            <q-td
            key='doi'
            :props="props"
            :class="props.row.added ? 'bg-green-1' : ((props.row.similar_to !== '')?'bg-cyan-1':'bg-white')"
            >
              <!-- <q-checkbox v-model="props.row.keep" /> -->
              <a :href="'https://dx.doi.org/' + props.row.doi" target="_blank">{{props.row.doi}}</a>
            </q-td>
          </template>
          <template v-slot:body-cell-similarto="props">
            <q-td
            key='similarto'
            :props="props"
            :class="props.row.added ? 'bg-green-1' : ((props.row.similar_to !== '')?'bg-cyan-1':'bg-white')"
            >
              <!-- <q-checkbox v-model="props.row.keep" /> -->
              <a :href="'https://dx.doi.org/' + props.row.similar_to" target="_blank">{{props.row.similar_to}}</a>
            </q-td>
          </template>
          <template v-slot:body-cell-similar="props">
            <q-td
            key='similar'
            :props="props"
            :class="props.row.added ? 'bg-green-1' : ((props.row.similar_to !== '')?'bg-cyan-1':'bg-white')"
            >
              <q-btn :disable="props.row.keep===false" unelevated dense size="sm" color="primary" label='find similar papers' @click="findSimilar(props.row)" />
            </q-td>
          </template>
          <template v-slot:body-cell="props">
            <q-td
              :props="props"
              :class="props.row.added ? 'bg-green-1' : ((props.row.similar_to !== '')?'bg-cyan-1':'bg-white')"
            >
              {{props.value}}
            </q-td>
          </template>
        </q-table>
        <q-dialog v-model="showAddPaper">
          <q-card style="width: 600px">
            <q-card-section class="row justify-between">
              <div class="text-h5 text-primary">Add Paper</div>
              <div class="col-1 justify-end row">
                <q-btn class='' icon="close" flat round dense v-close-popup />
              </div>
            </q-card-section>
            <q-card-section>
              <div class="q-pb-md row justify-evenly text-grey-9">Insert DOI of the paper you want to add</div>
              <q-input v-model="doi" hint="example: 10.1101/2020.10.25.20219063" square outlined stack-label label="DOI" />
            </q-card-section>
            <q-card-actions align="center">
              <div class="q-pb-sm">
                  <q-btn rounded label="ADD"  @click="getPaper" color="primary" v-close-popup />
              </div>
            </q-card-actions>
          </q-card>
        </q-dialog>
        <q-dialog v-model='showSimilars'>
          <q-card class="column no-wrap" style="min-width: 100%; height: 95%">
            <q-card-section class="row justify-between q-pb-sm">
              <div class="text-h5 text-primary text-bold q-pl-md">Similar paper to {{similarRow.doi}}</div>
              <div class="col-1 justify-end row">
                <q-btn class='' icon="close" flat round dense v-close-popup />
              </div>
            </q-card-section>
            <q-card-section class="column no-wrap" style="height: 100%">
              <div class="q-pb-md text-h6 text-primary row justify-evenly">Select relevant paper among the results</div>
              <div class="q-pa-md column" style="flex-grow: 1;overflow: auto">
                <q-table
                style="flex-grow: 1;overflow: auto"
                class="my-sticky-virtscroll-table"
                :columns="columns"
                :rows="similarPapers"
                virtual-scroll
                wrap-cells
                separator="cell"
                row-key="index"
                :rows-per-page-options="[0]"
                :virtual-scroll-sticky-size-start="48"
                my-sticky-virtscroll-table
                :visible-columns="similarVisibleColumns"
                selection='multiple'
                v-model:selected='similarSelection'
                v-model:pagination='pagination'
                >
                  <template v-slot:body-cell-keep="props">
                    <q-td key='keep' :props="props">
                      <q-checkbox v-model="props.row.keep" />
                    </q-td>
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
                </q-table>
              </div>
            </q-card-section>
            <div class="q-pb-md row justify-evenly">
              <q-btn unelevate color="primary" label="add selection" @click="addSimilarSelection"/>
            </div>
          </q-card>
        </q-dialog>
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
import { defineComponent } from "vue";
import { api } from 'boot/axios';
import { ref } from 'vue';
import { exportFile, useQuasar } from 'quasar'

const columns = [
  { name: 'index', label: '#', field: 'index',required: true, align: 'left'},
  { name: 'cord_uid', label: 'Cord UID', field: 'cord_uid', align: 'center' },
  { name: 'doi', label: 'Doi', field: 'doi', required: true, align: 'left' },

  { name: 'title', label: 'Title', field: 'title', sortable: true, align: 'left' },
   { name: 'year', label: 'Year', field: 'year', sortable: true, align: 'left' },
  { name: 'authors', label: 'Authors', field: 'authors', sortable: true, align: 'left' },
  { name: 'abstract', label: 'Abstract', field: 'abstract', align: 'left' },
  { name: 'journal', label: 'Source', field: 'journal', sortable: true, align: 'left' },
  { name: 'keep', label: 'Keep', field: 'keep', sortable: false, align: 'center' },
  { name: 'numCitedBy', label: 'Citations', field: 'numCitedBy', align: 'center' },
  { name: 'similar', label: '', align: 'center' },
   { name: 'similar_to', label: 'Similar To', field: 'similar_to', align: 'center' }
]

const visible_columns = [
  // "cord_uid",
  "index",
  "doi",
  "title",
  "authors",
  "year",
  "abstract",
  "journal",
  "numCitedBy",
  "similar",
  "similar_to",
]

const similarVisibleColumns = [
  // "cord_uid",
  "title",
  "authors",
  "abstract",
  "year",
  "journal",
  "numCitedBy",
  // "keep",
]

const alertTopics = {
  paper_not_found: {
    title: 'Abstract Not Found',
    body: 'The paper cannot be added'
  },
  paper_already_exist: {
    title: 'Paper Already Exist',
    body: 'The paper cannot be added'
  }
}

export default defineComponent({
  name: "paperList",
  setup () {
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
      sessionName: ref(null),
      searchKeyword: ref(''),
      doi : ref(''),
      alert : ref(false),
      columns,
      alertTopics,
      rows : ref([]),
      visible_columns,
      showSimilars: ref(false),
      similarPapers: ref([]),
      similarVisibleColumns,
      similarRow: ref({}),
      selection: ref([]),
      similarSelection: ref([]),
      alertContent : ref({ title: '', body: ''}),
      showAddPaper: ref(false),
      pagination: ref({
        sortBy: 'index',
        descending: false
      }),
      fixedPapers: ref([]),
      previousPaperList: ref([])
    }
  },
  methods : {
    getPaper () {
      for (const element of this.rows) {
        if (element.doi === this.doi) {
          this.alert = true
          this.alertContent = this.alertTopics.paper_already_exist
          return
        }
      }
      api.post('/papers', {
        doi: this.doi
      }).then((response) => {
        if (response.data['found'] == true) {
          this.rows.unshift(response.data['metadata'])
          this.rows[0].keep = true
          this.rows[0]['similar_to'] = ''
          this.rows[0]['added'] = true
          this.rows[0]['journal'] = response.data['metadata']['journal'] === '' ? 'preprint' : response.data['metadata']['journal']
          this.generateIndex(this.rows)
        }
        else{
          this.alert = true
          this.alertContent = this.alertTopics.paper_not_found
        }
      }).catch(error => (error.message))
    },
    getSeeds () {},
    generateIndex (no_indexed_list) {
      no_indexed_list.forEach((row, index) => {
        row.index = index
      }) 
    },
    // removeSelection () {
    //   for (const element of this.selected){
    //     this.rows.splice(element.index, 1)
    //     this.generateIndex()
    //     this.selected = []
    //   }
    // },
    saveList () {
      if (this.selection.length === 0) {
        this.showNotif('Select at least one paper')
        return
      }
      // for (const element of this.rows) {
      //   if (element.keep === true) {
      //     saved_list.push(element)
      //   }
      // }
      let newPaperList = []
      newPaperList = this.selection.concat(this.previousPaperList)
      this.generateIndex(newPaperList)
      this.$router.replace({name: 'AL', params: {paperList : JSON.stringify(newPaperList), fixedPapers: JSON.stringify(this.fixedPapers), sessionName: this.sessionName}})
    },
    findSimilar (row) {
      this.similarSelection = []
      this.similarPapers = []
      this.similarRow = row
      let by = ""
      let id = ""
      if (row.cord_uid === '') {
        by = "doi"
        id = row.doi
      } else {
        by = "cord"
        id = row.cord_uid
      }
      api.post(
        '/similar',
        { by: by, id: id}
      ).then( (response) => {
        let similars = response.data
        // let current_index = 0
        this.similarPapers = []
        for (let similar of similars) {
          similar['keep'] = true
          // element['similar_to'] = id
          let AlreadyExist = false
          for (const row of this.rows)
            if (row.doi === similar.doi || similar.doi === ""){
              AlreadyExist = true
            }
          if (!AlreadyExist) {
            api.post('/papers', {
              doi: similar.doi
            }).then((response) => {
              if (response.data['found'] == true) {
                similar['numCitedBy'] = response.data['metadata']['numCitedBy']
                similar['annotated'] = false
                similar['journal'] = response.data['metadata']['journal'] === '' ? 'preprint' : response.data['metadata']['journal']
                this.similarPapers.push(similar)
                this.generateIndex(this.similarPapers)
              }
            }).catch(error => (error.message))
          }
        }
        this.showSimilars = true
        // this.generateIndex(this.similarPapers)
      }).catch(error => (error.message))
    },
    addSimilarSelection () {
      // console.log(similars)
      let current_index = this.similarRow.index
      // console.log(index)
      for (let element of this.similarSelection) {
        element['similar_to'] = this.similarRow.doi
        this.rows.splice(current_index + 1, 0, element)
        current_index += 1
      }
      this.generateIndex(this.rows)
      this.similarPapers = []
      this.showSimilars = false
    },
    // removeSelection () {
    //   for (const element of this.selection){
    //     for (const [index, row] of this.rows.entries()) {
    //       if (row.index === element.index) {
    //         this.rows.splice(index, 1)
    //         break
    //       }
    //     }
    //   }
    //   this.generateIndex(this.rows)
    //   this.selection = []
    // },
    exportTSV () {
      let columns = this.visible_columns.slice(0,-1)
      // write the 1st row that contains columns
      let content = ''
      for (const column of columns) {
        content += column + '\t'
      }
      content = content.slice(0, -1) + '\r\n'
    
      for (const row of this.rows) {
        for (const column of columns) {
          content += row[column] + '\t'
        }
        content = content.slice(0, -1) + '\r\n'
      }

      exportFile(
        'table-export.tsv',
        content,
        'text/tsv'
      )
    }
  },
  created () {
    // console.log('stampo previous papers senza parse')
    // console.log(this.$route.params.previousPaperList)
    // console.log('stampo previous papers con parse')
    // console.log(JSON.parse(this.$route.params.previousPaperList))
    // console.log('doppio parse')
    // console.log(JSON.parse(JSON.parse(this.$route.params.previousPaperList)))
    this.previousPaperList = JSON.parse(this.$route.params.previousPaperList)
    this.fixedPapers = JSON.parse(this.$route.params.fixedPapers)
    this.paperList = JSON.parse(this.$route.params.paperList)
    this.sessionName = this.$route.params.sessionName
    // console.log(this.$route.params.sessionName)
    // console.log(this.previousPaperList)
    // console.log(this.fixedPapers)
    // console.log(this.paperList)
    for (let row of this.paperList) {
      row['similar_to'] = ''
      row['journal'] = row.journal === '' ? 'preprint' : row.journal
      api.post('/papers', {
        doi: row.doi
      }).then((response) => {
        if (response.data['found'] == true) {
          row['numCitedBy'] = response.data['metadata']['numCitedBy']
          row['annotated'] = false
          row['year'] = response.data['metadata']['year']
          // row['journal'] = response.data['metadata']['journal']
          this.rows.push(row)
          this.generateIndex(this.rows)
        }
      }).catch(error => (error.message))
    }
    // api.get(
    //   '/paperlist'
    // ).then((response) => {
    //   // this.rows = response.data.paper_list
    //   for (let row of response.data.paper_list) {
    //     row['similar_to'] = ''
    //     row['journal'] = row.journal === '' ? 'preprint' : row.journal
    //     api.post('/papers', {
    //       doi: row.doi
    //     }).then((response) => {
    //       if (response.data['found'] == true) {
    //         row['numCitedBy'] = response.data['metadata']['numCitedBy']
    //         // row['journal'] = response.data['metadata']['journal']
    //         this.rows.push(row)
    //         this.generateIndex(this.rows)
    //       }
    //     }).catch(error => (error.message))
    //   }
    //   // console.log(this.rows[0])
    // }).catch(error => (error.message))
  }
});
</script>
