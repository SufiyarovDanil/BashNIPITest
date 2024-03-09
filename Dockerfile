FROM python:3.12

RUN mkdir /bnipi_test

WORKDIR /bnipi_test

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

WORKDIR /bnipi_test/src

CMD gunicorn main:app --workers 5 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8070
