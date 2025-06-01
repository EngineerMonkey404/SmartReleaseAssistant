<template>
    <div class="estimate-container">
    <div class="task-label">Ссылка на задачу</div>
    <input
        v-model="input"
        type="text" 
        class="task-input" 
        placeholder="https://confluence/pages/viewpage.action?pageId=1048587"
    >
    <button class="estimate-button" @click="handleSubmit" :disabled="isLoading">
        Оценить время
    </button>
        <div v-if="isSuccess" style="color: green">Успешно оценено</div>
        <div v-if="hasError" style="color:red">Произошла ошибка</div>
        <div v-if="isLoading" style="color: orange">Идёт оценка</div>
    </div>
</template>

<script setup lang="ts">
import axios from "axios"
import { ref, watch } from "vue"


const input = ref('');
const hasError = ref(false);
const isSuccess = ref(false);
const isLoading = ref(false);


async function handleSubmit() {
    isSuccess.value = false
    hasError.value = false
    isLoading.value = true
    const page_id = input.value.split('pageId=')[1]
    try {
        const response = await axios.post('http://localhost:8001/estimate-time', {"page_id": page_id}, {
        headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json',
        },
    })
        isSuccess.value = true
        return response
    }
    catch(e) {
        hasError.value = true
        throw e;
    }
    finally {
        isLoading.value = false
    }
   
}

watch(input, () => {
    hasError.value = false;
    isSuccess.value = false;
})
</script>