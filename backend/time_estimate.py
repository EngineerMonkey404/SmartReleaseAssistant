import requests
from bs4 import BeautifulSoup
from yandex_cloud_ml_sdk import AsyncYCloudML
from enum import Enum
from dataclasses import dataclass

# Конфигурация Confluence

# CONFLUENCE_PAGE_ID = "1048587"

CONFLUENCE_URL = "http://localhost:8090"
CONFLUENCE_USERNAME = "admin"
CONFLUENCE_PASSWORD = "admin"


class ModelArch(str, Enum):
    YGPT = "yandexgpt"
    YGTP_LITE = "yandexgpt-lite"
    LLAMA8 = "llama-lite"
    LLAMA70 = "llama"


DEFAULT_TEMP = 0.2




def get_ml_sdk():
    sdk = AsyncYCloudML(
        folder_id="",
        auth="",
    )
    return sdk

sdk = get_ml_sdk()
model = sdk.models.completions(ModelArch.YGTP_LITE.value).configure(temperature=0.2)

async def generate(prompt):
    messages = [
        {
        "role": "system",
        "text": """
           Ты — тимлид команды фронтенда. Оцени время выполнения задачи в часах на основе её технического задания.
           Ответ должен быть только числом (например, "8"), без пояснений.
        """,
        },
        {
            "role": "user",
            "text": f"Задача: {prompt}",
        },
    ]

    operation = await model.run_deferred(messages)
    result = await operation.wait()
    print(result)
    res: str = result[0].text

    return res


async def estimate_task_time(task_description):
    prompt = f"""
    Ты — тимлид команды фронтенда. Оцени время выполнения задачи в часах на основе её технического задания.
    Задача: {task_description}
    Ответ должен быть только числом (например, "8"), без пояснений.
    """
    response = await generate(prompt=task_description)
    try:
        time_estimate = int(''.join(filter(str.isdigit, response)))
        return time_estimate
    except:
        return None


def get_confluence_page(page_id):
    url = f"{CONFLUENCE_URL}/rest/api/content/{page_id}?expand=body.view,version"
    try:
        response = requests.get(
            url,
            auth=(CONFLUENCE_USERNAME, CONFLUENCE_PASSWORD),
            headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении страницы: {e}")
        return None
    

def get_storage_confluence_page(page_id):
    url = f"{CONFLUENCE_URL}/rest/api/content/{page_id}?expand=body.storage,version"
    try:
        response = requests.get(
            url,
            auth=(CONFLUENCE_USERNAME, CONFLUENCE_PASSWORD),
            headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении страницы: {e}")
        return None

def get_page_content_by_id(page_id):
    url = f"{CONFLUENCE_URL}/rest/api/content/{page_id}?expand=body.storage"
    try:
        response = requests.get(
            url,
            auth=(CONFLUENCE_USERNAME, CONFLUENCE_PASSWORD),
            headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        data = response.json()
        return BeautifulSoup(data['body']['storage']['value'], 'html.parser').get_text()
    except Exception as e:
        print(f"Ошибка при получении содержимого страницы {page_id}: {e}")
        return None
    
def extract_task_page_ids(page_data):
    tasks = []
    soup = BeautifulSoup(page_data['body']['view']['value'], 'html.parser')
    table = soup.find('table')
    
    if not table:
        return tasks
    
    for row in table.find_all('tr')[1:]: 
        cells = row.find_all('td')
        if cells:
            link = cells[0].find('a', href=True)
            if link:
                href = link['href']
                if 'pageId=' in href:
                    page_id = href.split('pageId=')[1].split('&')[0]
                    tasks.append(page_id)
    
    return tasks

def update_confluence_table(page_id, estimates):
    page_data = get_storage_confluence_page(page_id)

    current_content = page_data['body']['storage']['value']
    
    soup = BeautifulSoup(current_content, 'html.parser')
    table = soup.find('table')
    
    rows = table.find_all('tr')[1:]
    for row, estimate in zip(rows, estimates):
        cells = row.find_all('td')
        if len(cells) >= 2:
            cells[1].string = str(estimate) if estimate else "Не удалось оценить"
    
    updated_content = str(soup)

    update_url = f"{CONFLUENCE_URL}/rest/api/content/{page_id}"
    payload = {
        "version": {
            "number": page_data['version']['number'] + 1, 
        },
        "title": page_data['title'],
        "type": "page",
        "body": {
            "storage": {
                "value": updated_content,
                "representation": "storage"
            }
        }
    }
    
    response = requests.put(
        update_url,
        json=payload,
        auth=(CONFLUENCE_USERNAME, CONFLUENCE_PASSWORD)
    )
    return response.json()


async def estimate_time(page_id):
    page_data = get_confluence_page(page_id)
    if not page_data:
        print("Не удалось загрузить страницу из Confluence")
        return
    
    task_page_ids = extract_task_page_ids(page_data)
    if not task_page_ids:
        print("Не найдено задач для оценки")
        return
    
    print("Найденные ID страниц с ТЗ:", task_page_ids)
    
    tasks_content = []
    for page_id in task_page_ids:
        content = get_page_content_by_id(page_id)
        if content:
            tasks_content.append(content)
        else:
            tasks_content.append(f"Не удалось получить ТЗ (страница {page_id})")
    
    estimates = [await estimate_task_time(task) for task in tasks_content]
    print("Полученные оценки:", estimates)
    
    result = update_confluence_table(page_id, estimates)
    if result:
        print("Оценки задач успешно обновлены в Confluence")
    else:
        print("Не удалось обновить оценки в Confluence")

