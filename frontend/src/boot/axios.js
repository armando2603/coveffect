import { boot } from 'quasar/wrappers'
import axios from 'axios'

const api = axios.create({ baseURL: 'http://geco.deib.polimi.it/muteffstage_api/' })
const apiGPU = axios.create({ baseURL: 'http://3.21.170.212:61114' })
// to work in local use instead this ip
// const api = axios.create({ baseURL: 'http://localhost:61113/' })
// const apiGPU = axios.create({ baseURL: 'http://094c-35-236-137-214.ngrok.io' })

export default boot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API
  app.config.globalProperties.$apiGPU = apiGPU
})

export { axios, api, apiGPU }