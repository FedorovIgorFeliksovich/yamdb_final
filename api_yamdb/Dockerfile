FROM python:3.7-slim 

WORKDIR /app/api_yamdb 

COPY requirements.txt ./ 

RUN pip3 install -r ./requirements.txt --no-cache-dir --no-input 

COPY ./ . 

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ]
