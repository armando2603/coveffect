<template>
  <q-page class="row items-strech">
    <div class="column col-12 no-wrap">
      <div class="q-pa-md row justify-end no-wrap">
        <q-card class='row' style="width: 100%">
          <div class="q-pa-md col-8">
            <q-input v-model="doi" stack-label label="Insert a DOI" />
          </div>
          <div class="column justify-center q-pa-sm">
            <q-btn class='' rounded icon='add' color='primary' @click='getPaper'/>
          </div>
          <!-- <div class="column justify-center q-pa-sm">
            <q-btn class='' rounded v-if='rows.length > 0 && selected.length > 0' icon='remove' color='negative' @click='removeSelection'/>
          </div> -->
          <!-- <div class="column justify-center q-pa-sm">
            <q-btn class='' label='add seeds' color='primary' @click='getSeeds'/>
          </div> -->
          <q-dialog v-model="alert">
            <q-card>
              <q-card-section>
                <div class="text-h6 text-red-5">No Abstract Found</div>
              </q-card-section>

              <q-card-section class="q-pt-none">
                <div class="text-grey-7">The paper cannot be added</div>
              </q-card-section>

              <q-card-actions align="right">
                <q-btn flat label="OK" color="primary" v-close-popup />
              </q-card-actions>
            </q-card>
          </q-dialog>
        </q-card>
        <div class="column justify-center q-pl-md q-pr-md">
          <q-btn class='' rounded icon='arrow_forward' color='positive' @click='saveList'/>
        </div>
      </div>
      <div class="q-pa-md column" style="flex-grow: 1">
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
        :visible-columns="visible_columns"
        >
          <template v-slot:body-cell-keep="props">
            <q-td
            key='keep'
            :props="props"
            :class="(props.row.similar_to !== '')?'bg-cyan-1 text-black':'bg-white text-black'"
            >
              <q-checkbox v-model="props.row.keep" />
            </q-td>
          </template>
          <template v-slot:body-cell-doi="props">
            <q-td
            key='doi'
            :props="props"
            :class="(props.row.similar_to !== '')?'bg-cyan-1 text-black':'bg-white text-black'"
            >
              <!-- <q-checkbox v-model="props.row.keep" /> -->
              <a :href="'https://dx.doi.org/' + props.row.doi" target="_blank">{{props.row.doi}}</a>
            </q-td>
          </template>
          <template v-slot:body-cell-similar="props">
            <q-td
            key='similar'
            :props="props"
            :class="(props.row.similar_to !== '')?'bg-cyan-1 text-black':'bg-white text-black'"
            >
              <q-btn :disable="props.row.keep===false" unelevated dense size="sm" color="primary" label='find similars' @click="findSimilar(props.row)" />
            </q-td>
          </template>
          <template v-slot:body-cell="props">
            <q-td
              :props="props"
              :class="(props.row.similar_to !== '')?'bg-cyan-1 text-black':'bg-white text-black'"
            >
              {{props.value}}
            </q-td>
          </template>
        </q-table>
        <q-dialog v-model='showSimilars'>
          <q-card class="column no-wrap" style="min-width: 100%; height: 95%">
            <q-card-section class="row justify-between">
              <div class="text-h5">Similar Papers</div>
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
                :rows="similarPapers"
                virtual-scroll
                wrap-cells
                separator="cell"
                row-key="index"
                :rows-per-page-options="[0]"
                :virtual-scroll-sticky-size-start="48"
                my-sticky-virtscroll-table
                :visible-columns="similarVisibleColumns"
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
              <q-btn unelevate color="primary" label="add" @click="addSimilarSelection"/>
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
import { ref } from 'vue'

const columns = [
  { name: 'index', label: '#', field: 'index',required: true, align: 'left'},
  { name: 'cord_uid', label: 'Cord UID', field: 'cord_uid', align: 'center' },
  { name: 'doi', label: 'Doi', field: 'doi', required: true, align: 'left' },
  { name: 'similarto', label: 'Similar To', field: 'similar_to', align: 'center' },
  { name: 'title', label: 'Title', field: 'title', sortable: true, align: 'left' },
  { name: 'authors', label: 'Authors', field: 'authors', sortable: true, align: 'left' },
  { name: 'abstract', label: 'Abstract', field: 'abstract', align: 'left' },
  // { name: 'year', label: 'Year', field: 'year', sortable: true, align: 'left' },
  { name: 'journal', label: 'Journal', field: 'journal', sortable: true, align: 'left' },
  { name: 'keep', label: 'Keep', field: 'keep', sortable: false, align: 'center' },
  { name: 'similar', label: '', align: 'center' }
]

const visible_columns = [
  // "cord_uid",
  "similarto",
  "title",
  "authors",
  "abstract",
  "journal",
  "keep",
  "similar"
]

const similarVisibleColumns = [
  // "cord_uid",
  "title",
  "authors",
  "abstract",
  "journal",
  "keep",
]

export default defineComponent({
  name: "PageIndex",
  setup () {
    return {
      doi : ref(''),
      alert : ref(false),
      columns,
      rows : ref([]),
      visible_columns,
      showSimilars: ref(false),
      similarPapers: ref([]),
      similarVisibleColumns,
      similarRow: ref({})
    }
  },
  methods : {
    getPaper () {
      for (const element of this.rows) {
        if (element.doi === this.doi) {
          return
        }
      }
      api.post('/papers', {
        doi: this.doi
      }).then((response) => {
        if (response.data['found'] == true) {
          this.rows.unshift(response.data['metadata'])
          this.rows[0].keep = true
          this.generateIndex(this.rows)
        }
        else{
          this.alert = true
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
      let saved_list = []
      for (const element of this.rows) {
        if (element.keep === true) {
          saved_list.push(element)
        }
      }
      this.generateIndex(saved_list)
      api.post(
        '/paperlist',
        { paper_list: saved_list },
      ).then( response => (this.$router.push({path: '/AL'}))
      ).catch(error => (error.message))
    },
    findSimilar (row) {
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
        let current_index = 0
        this.similarPapers = []
        for (let element of similars) {
          element['keep'] = true
          // element['similar_to'] = id
          if (element.doi !== "") {
            this.similarPapers.push(element)
          }
        }
        this.showSimilars = true
        this.generateIndex(this.similarPapers)
      }).catch(error => (error.message))
    },
    addSimilarSelection () {
      // console.log(similars)
      let current_index = this.similarRow.index
      // console.log(index)
      for (let element of this.similarPapers) {
        if (element.keep === true) {
          element['keep'] = true
          element['similar_to'] = this.similarRow.index
          this.rows.splice(current_index + 1, 0, element)
          current_index += 1
        }
      }
      this.generateIndex(this.rows)
      this.similarPapers = []
      this.showSimilars = false
    }
  },
  created () {
    api.get(
      '/paperlist'
    ).then((response) => {
      // this.rows = response.data.paper_list
      for (let row of response.data.paper_list) {
        row['similar_to'] = ''
        this.rows.push(row)
      }
      console.log(this.rows[0])
    }).catch(error => (error.message))
  }
});
</script>
