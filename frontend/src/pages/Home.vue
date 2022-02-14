<template>
  <q-page padding class="column justify-evenly">
    <div class="q-pa-md">
      <div class="row justify-evenly">
        <div class=" text-h4 text-grey-8" style="text-align: center; max-width: 70%">
          Search papers over the COVID-19 literature using keywords
        </div>
      </div>
      <div class="row justify-center q-pt-md" >
        <div class="" style='width: 70%'>
        <q-input outlined placeholder="Insert keywords"  bottom-slots v-model="keywordText" stack-label>
          <template v-slot:append>
            <q-icon v-if="keywordText !== ''" name="close" @click="keywordText = ''" class="cursor-pointer" />
            <!-- <q-icon name="search"/> -->
          </template>
        </q-input>
        </div>

        <div class="q-pl-md q-pt-sm">
        <q-btn icon="search" color='primary' :loading="loadKey" @click='searchByKeywords();loadKey=true'/>
        </div>
      </div>
      <div class="row justify-evenly text-h5 q-pt-xl">
        <div class="text-grey-8" style="text-align: center; max-width: 70%">
          or load a specific paper through its DOI
        </div>
      </div>
      <div class="row justify-center q-pt-md">
        <div class="" style='width: 70%'>
          <q-input placeholder="Insert a DOI in the form of 10.1101/2020.11.28.20237016" outlined  bottom-slots v-model="DOIText" stack-label>
            <template v-slot:append>
              <q-icon v-if="DOIText !== ''" name="close" @click="DOIText = ''" class="cursor-pointer" />
            </template>
          </q-input>
        </div>
        <div class="q-pl-md q-pt-sm">
          <q-btn icon="search" color='primary' :loading="loadDoi" @click='searchByDOI(); loadDoi=true'/>
        </div>
      </div>
    </div>
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
  </q-page>
</template>

<script>
import { ref } from 'vue';
import { api } from 'boot/axios';

const alertTopics = {
  paper_not_found: {
    title: 'Abstract Not Found',
    body: 'Check the entered DOI'
  }
}

export default {
  setup () {
    return {
      fixedPapers: ref([]),
      previousPaperList: ref([]),
      loadKey: ref(false),
      loadDoi: ref(false),
      alertTopics,
      alert: ref(false),
      alertContent: ref({ title: '', body: ''}),
      keywordText: ref(''),
      DOIText: ref(''),
      paperList: ref([]),
      attributes: ref([
        'doi',
        'authors',
        'title',
        'abstract',
        'journal',
        'cord_uid'
      ])
    }
  },
  methods : {
    searchByKeywords () {
      api.post(
        '/search',
        { query: this.keywordText}
      ).then((response) => {
        // console.log(response.data[0])
        for (const element of response.data) {
          if (element.doi !== "") {
            let row = {}
            for (const attribute of this.attributes) {
              row[attribute] = element[attribute]
            }
            row['keep'] = true
            this.paperList.push(row)
          }
        }
        this.generateIndex()
        this.$router.replace({name: 'paperList', params: {keyword: this.keywordText, paperList: JSON.stringify(this.paperList), fixedPapers: JSON.stringify(this.fixedPapers), previousPaperList: JSON.stringify(this.previousPaperList)}})
        // api.post(
        //   '/paperlist',
        //   { paper_list: this.paperList },
        // ).then(response => {
        //   this.$router.replace({name: 'paperList', params: {keyword: this.keywordText}})
        //   // this.$router.resolve({ name: 'paperList', params: { chapters: [] } }).href
        //   // this.$router.replace({path: '/start'})
        // }).catch(error => (error.message))

      }).catch(error => {
        error.message
        this.loadKey=false
      })
    },
    searchByDOI () {
      api.post(
        '/papers',
        { doi: this.DOIText }
      ).then( (response) => {
        if (response.data['found'] == true) {
          let row = response.data['metadata']
          row.keep = true
          row['similar_to'] = ''
          row['added'] = false
          row['index'] = 0
          this.paperList.push(row)
          this.$router.replace({name: 'paperList', params: {keyword: this.DOIText, paperList: JSON.stringify(this.paperList), fixedPapers: JSON.stringify(this.fixedPapers), previousPaperList: JSON.stringify(this.previousPaperList)}})
          // api.post(
          //   '/paperlist',
          //   { paper_list: this.paperList },
          // ).then(response => {
          //   this.$router.replace({name: 'paperList', params: {keyword: this.DOIText}})
          // }).catch(error => (error.message))
        }
        else{
          this.alert = true
          this.alertContent = this.alertTopics.paper_not_found
        }
      }).catch( (error) => {
        error.message
        this.loadDoi = false
      })
    },
    generateIndex () {
      this.paperList.forEach((row, index) => {
        row.index = index
      })
    }
  },
  created () {
    if (Object.keys(this.$route.params).includes('previousPaperList')) {
      this.previousPaperList = JSON.parse(this.$route.params.previousPaperList)
    }
    if (Object.keys(this.$route.params).includes('fixedPapers')) {
      this.fixedPapers = JSON.parse(this.$route.params.fixedPapers)
    }
  }
  // name: 'PageName',
}
</script>
