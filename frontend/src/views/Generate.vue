<template>

<div class="main-container">
    <label>Ссылка на задачу</label>
    <input v-model="input" placeholder="введите ссылку на задачу" style="width: 400px"/>
    <button @click="handleSubmit">Оценить время</button>
    <div v-if="isSuccess" style="color: green">Успешно оценено</div>
    <div v-if="hasError" style="color:red">Произошла ошибка</div>
</div>
</template>

<script setup lang="ts">
import axios from "axios"
import { ref, watch } from "vue"


const input = ref('');
const hasError = ref(false);
const isSuccess = ref(false);


async function handleSubmit() {
    isSuccess.value = false
    hasError.value = false
    const page_id = input.value.split('pageId=')[1]
    console.log(page_id)
    try {
        const response = await axios.post('http://localhost:8001/estimate-time', {"page_id": page_id})
        isSuccess.value = true
        return response
    }
    catch(e) {
        hasError.value = true
        throw e;
    }
   
}

watch(input, () => {
    hasError.value = false;
    isSuccess.value = false;
})
</script>