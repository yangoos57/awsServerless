FROM python:3.9.16-slim-bullseye

ENV DIR dodomoa

RUN apt-get update -y && apt-get install -y gcc

COPY requirements.txt ${DIR}/

COPY App ${DIR}/app

WORKDIR /${DIR}

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

WORKDIR /${DIR}/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]`

# CMD ["sleep","3600"]
