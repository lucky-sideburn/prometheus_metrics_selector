FROM python:3.8-slim-buster

WORKDIR /app
RUN mkdir /app/conf
COPY requirements.txt requirements.txt
COPY metrics_selector.ini /app/conf/metrics_selector.ini

RUN pip3 install -r requirements.txt

EXPOSE 5000

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
