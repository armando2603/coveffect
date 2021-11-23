<template>
  <q-page class="column">
    <div class="q-pa-md col-6 row justify-end">
      <q-card class='row' style="width: 100%">
        <div class="q-pa-md col-8">
          <q-input v-model="doi" stack-label label="Insert DOI" />
        </div>
        <div class="column justify-center">
          <q-btn class='' label='search' color='primary' @click='getAbstract'/>
        </div>
      </q-card>
    </div>
    <div class="q-pa-md row justify-between">
      <div class="col-6">
        <q-card class="" style='width: 100%'>
          <q-card-section class="flex flex-center">
            <div class="text-h6 text-grey-8">Selected Paper</div>
          </q-card-section>
          <q-card-section class="">
            <q-field class="q-pa-sm" q-field borderless readonly stack-label label='Abstract'>
              <template v-slot:control>
                <div class="self-center full-width no-outline" tabindex="0">{{abstract}}</div>
              </template>
            </q-field>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-5">
        <q-card class="">
          <q-card-section class="flex flex-center">
            <div class="text-h6 text-grey-8">Extracted Data</div>
          </q-card-section>
          <q-card-section class="">
            <div class="q-pa-md col-8">
              <q-input v-model="mutation" stack-label label="Insert Mutation Type"/>
            </div>
            <div class="q-pa-md col-8">
              <q-input v-model="effect" stack-label label="Insert Trasmition Effect"/>
            </div>
            <div class="q-pa-md col-8">
              <q-input v-model="level" stack-label label="Insert Advantage Level"/>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script>
import { defineComponent } from "vue";
import { api } from 'boot/axios';
import { ref } from 'vue'

export default defineComponent({
  name: "PageIndex",
  setup () {
    return {
      doi : ref(''),
      abstract : ref('No content loaded'),
      mutation: ref(''),
      effect : ref(''),
      level : ref('')
    }
  },
  methods : {
    getAbstract () {
      api.post('/papers', {
        doi: this.doi
      }).then((response) => {
        if (response.data['found'] == true) {
          this.abstract = response.data['abstract']

        }
        else{
          this.abstract = "abstract doesn't found"
        }
      }).catch(error => (error.message))
    }
  }
});
</script>
