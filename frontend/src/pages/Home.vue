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
        <q-btn label='search' color='primary' to='/start' />
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
import { api } from 'boot/axios'

export default {
  setup () {
    return {
      keywordText: ref(''),
      DOIText: ref('')
    }
  }
  // name: 'PageName',
}
</script>
