FROM python:3.8-slim-buster
# working directory
WORKDIR /app
# create new directory under /app/conf
RUN mkdir /app/conf
# copy requirements using requirements.txt
COPY requirements.txt requirements.txt
# copy metrics_selector.ini in /app/conf
COPY src/resources/metrics_selector.ini /app/conf/metrics_selector.ini
# copy app.yml ni /app/conf
COPY src/resources/app.yml /app/conf/app.yml
# install requirements using requirements.txt
RUN pip3 install -r requirements.txt
# clean and update container packages
RUN apt-get clean && apt-get update -y && apt-get install curl -y
# exposing port 55000
EXPOSE 5000
# copy all project structure into container
COPY . .
# entrypoint
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
