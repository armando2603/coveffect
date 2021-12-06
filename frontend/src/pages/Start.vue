<template>
  <q-page class="row items-strech">
    <div class="column col-12 no-wrap">
      <div class="q-pa-md row justify-end no-wrap">
        <q-card class='row' style="width: 100%">
          <div class="q-pa-md col-8">
            <q-input v-model="doi" stack-label label="Insert a DOI" />
          </div>
          <div class="column justify-center q-pa-sm">
            <q-btn class='' rounded icon='add' color='primary' @click='getAbstract'/>
          </div>
          <div class="column justify-center q-pa-sm">
            <q-btn class='' rounded v-if='rows.length > 0 && selected.length > 0' icon='remove' color='negative' @click='removeSelection'/>
          </div>
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
          <q-btn class='' to='/AL' rounded icon='arrow_forward' color='positive' @click='saveList'/>
        </div>
      </div>
      <div class="q-pa-md column" style="flex-grow: 1">
        <q-table
        class="my-sticky-virtscroll-table"
        style="overflow: auto; flex-grow: 1"
        table-header-style="text-align: left"
        table-header-class="align-left"
        title="Papers List"
        wrap-cells
        virtual-scroll
        dense
        my-sticky-virtscroll-table
        :rows-per-page-options="[0]"
        separator="cell"
        :virtual-scroll-sticky-size-start="48"
        :rows="rows"
        :columns="columns"
        row-key="doi"
        selection="multiple"
        v-model:selected="selected"
        >
          <template v-slot:body-cell-keep="props">
            <q-td key='keep' :props="props">
              <q-checkbox v-model="props.row.keep" />
            </q-td>
          </template>
        </q-table>
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
  { name: 'index', label: '#', field: 'index',required: true, align: 'left' },
  { name: 'doi', label: 'Doi', field: 'doi', required: true, align: 'left' },
  { name: 'title', label: 'Title', field: 'title', sortable: true, align: 'left' },
  { name: 'authors', label: 'Authors', field: 'authors', sortable: true, align: 'left' },
  { name: 'abstract', label: 'Abstract', field: 'abstract', align: 'left' },
  // { name: 'year', label: 'Year', field: 'year', sortable: true, align: 'left' },
  { name: 'keep', label: 'Keep', field: 'keep', sortable: false, align: 'center' }
]

export default defineComponent({
  name: "PageIndex",
  setup () {
    return {
      doi : ref(''),
      alert : ref(false),
      columns,
      rows : ref([]),
      selected: ref([])
    }
  },
  methods : {
    getAbstract () {
      for (const element of this.rows) {
        if (element.doi === this.doi) {
          return
        }
      }
      api.post('/papers', {
        doi: this.doi
      }).then((response) => {
        if (response.data['found'] == true) {
          this.rows.push(response.data['metadata'])
          this.rows.slice(-1)[0].keep = true
          this.generateIndex()
        }
        else{
          this.alert = true
        }
      }).catch(error => (error.message))
    },
    getSeeds () {},
    generateIndex () {
      this.rows.forEach((row, index) => {
        row.index = index
      })
    },
    removeSelection () {
      for (const element of this.selected){
        this.rows.splice(element.index, 1)
        this.generateIndex()
        this.selected = []
      }
    },
    saveList () {
      api.post(
        '/paperlist',
        { paper_list: this.rows },
      ).catch(error => (error.message))
    }
  },
  created () {
    api.get(
      '/paperlist'
    ).then((response) => {
      this.rows = response.data.paper_list
    }).catch(error => (error.message))
  }
});
</script>
