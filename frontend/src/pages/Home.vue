<template>
  <q-page padding class="column justify-evenly">
    <div class="q-pa-md">
      <div class="row justify-evenly">
        <div class=" text-h4 text-grey-8" style="text-align: center; max-width: 70%">
          Search COVID-19 to find some papers about a mutation and its effects
        </div>
      </div>
      <div class="row justify-center q-pt-md" >
        <q-input style='width: 70%' outlined placeholder="Insert keywords here"  bottom-slots v-model="keywordText" stack-label>
          <template v-slot:append>
            <q-icon v-if="keywordText !== ''" name="close" @click="keywordText = ''" class="cursor-pointer" />
            <q-icon name="search"/>
          </template>
        </q-input>
      </div>
      <div class="row justify-evenly">
        <q-btn label='search' color='primary' @click='search'/>
      </div>
      <!-- <div class="row justify-evenly text-h5 q-pt-xl">
        <div class="text-grey-8" style="text-align: center; max-width: 70%">
          Or search a specific paper through its DOI
        </div>
      </div>
      <div class="row justify-center q-pt-md">
        <q-input style='width: 70%' placeholder="Insert a DOI" outlined  bottom-slots v-model="DOIText" stack-label>
          <template v-slot:append>
            <q-icon v-if="DOIText !== ''" name="close" @click="DOIText = ''" class="cursor-pointer" />
            <q-icon name="search" />
          </template>
        </q-input>
      </div> -->
    </div>
  </q-page>
</template>

<script>
import { ref } from 'vue';
import { api } from 'boot/axios';

export default {
  setup () {
    return {
      keywordText: ref(''),
      DOIText: ref(''),
      paperList: ref([]),
      attributes: ref([
        'doi',
        'authors',
        'title',
        'abstract',
        'journal'
      ])
    }
  },
  methods : {
    search () {
      api.get('/search').then((response) => {
        // console.log(response.data[0])
        for (const element of response.data) {
          let row = {}
          for (const attribute of this.attributes) {
            row[attribute] = element[attribute]
          }
          row['keep'] = true
          this.paperList.push(row)
        console.log(response.data)
        }
        this.generateIndex()
        api.post(
          '/paperlist',
          { paper_list: this.paperList },
        ).then(response => {
          this.$router.push({path: '/start'})
        }).catch(error => (error.message))

      }).catch(error => (error.message))
    },
    generateIndex () {
      this.paperList.forEach((row, index) => {
        row.index = index
      })
    }
  }
  // name: 'PageName',
}
</script>
