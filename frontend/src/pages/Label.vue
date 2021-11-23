<template>
  <q-page padding class="row items-strech">
    <div class="col-12 column q-pt-md">
      <div class="row no-wrap q-pa-sm justify-between">
        <q-card class="col-3">
          <q-card-section class="row justify-evenly">
            <div class="text-h5">Sample Info</div>
          </q-card-section>
          <q-card-section class="column justify-between">
            <q-field stack-label borderless label='#'>
              <template v-slot:control>
                <div class="self-center full-width no-outline" tabindex="0">{{currentPaper + 1}}/{{paperList.length}}</div>
              </template>
            </q-field>
            <q-field stack-label borderless label='DOI'>
              <template v-slot:control>
                <div class="self-center full-width no-outline" tabindex="0">{{paperList.length === 0 ? '' : paperList[currentPaper].doi}}</div>
              </template>
            </q-field>
            <q-field stack-label borderless label='Title'>
              <template v-slot:control>
                <div class="self-center full-width no-outline" tabindex="0">{{paperList.length === 0 ? '' : paperList[currentPaper].title}}</div>
              </template>
            </q-field>
            <q-field stack-label borderless label='Authors'>
              <template v-slot:control>
                <div class="self-center full-width no-outline" tabindex="0">{{paperList.length === 0 ? '' : paperList[currentPaper].authors}}</div>
              </template>
            </q-field>
            <q-field stack-label borderless label='Year'>
              <template v-slot:control>
                <div class="self-center full-width no-outline" tabindex="0">{{paperList.length === 0 ? '' : paperList[currentPaper].year}}</div>
              </template>
            </q-field>
          </q-card-section>
        </q-card>
        <q-card class="col-5">
          <q-card-section class="row justify-evenly">
            <div class="text-h5">Abstract</div>
          </q-card-section>
          <q-card-section>
            {{paperList.length === 0 ? '' : paperList[currentPaper].abstract}}
          </q-card-section>
        </q-card>
        <q-card class="col-3">
          <q-card-section class="q-pb-none q-mb-none row justify-evenly">
            <div class="text-h5">Editor</div>
          </q-card-section>
          <q-card-section class="column q-pb-none q-mb-none justify-start">
            <div class="q-pb-md row justify-center"><q-btn dense rounded color="primary" icon="add" /></div>
            <div v-for="(input, index) in inputs" :key="input">
              <div class="q-pb-md column justify-start">
                <div class="text-grey-8">
                  {{input.name}}:
                </div>
                <q-input v-if="index > 0" outlined dense v-model="input.value"/>
                <q-select v-if="index === 0" outlined :options="mutationList" dense v-model='mutationType' />
              </div>
            </div>
          </q-card-section>
          <q-card-actions class="row justify-evenly ">
            <div class="q-pb-md">
            <q-btn label="save" rounded color="primary" @click="saveSample" />
            </div>
          </q-card-actions>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script>
import { ref } from 'vue'
import { api } from 'boot/axios';

export default {
  name: 'Label',
  setup () {
    return {
      paperList: ref([]),
      currentPaper: ref(0),
      inputs: ref([
        { name: 'Mutation Type', value: [

        ]},
        { name: 'Name', value: 'Insert value' },
        { name: 'Effect', value: 'Insert value'},
        { name: 'Level', value: 'Insert value' },
        { name: 'Method', value: 'Insert value'}
      ]),
      mutationType: ref('Select an option'),
      mutationList: ref([
        "single mutation", "mutation group", "variant"
      ]),
      labelsList: ref([])
    }
  },
  methods : {
    saveSample () {
      this.labelsList.push({
        paper: this.paperList[this.currentPaper],
        labels: this.inputs
      })
      this.currentPaper += 1
    }
  },
  created () {
    api.get(
      '/paperlist'
    ).then((response) => {
      this.paperList = response.data.paper_list
    }).catch(error => (error.message))
  }
}
</script>
