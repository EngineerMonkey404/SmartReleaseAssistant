FROM python:3.10.16

WORKDIR /llm_service

COPY requirements.txt .

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["fastapi", "run", "--port", "8001", "--host", "0.0.0.0"]