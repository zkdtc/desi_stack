FROM debian:latest
RUN apt-get update --quiet -y && apt-get install --quiet -y python-pip && apt-get --quiet -y install postgresql-client && apt-get --quiet -y install python-psycopg2
RUN pip install bokeh
RUN pip install Flask
RUN pip install mysql-connector
ENV FLASK_APP=app 
ENV FLASK_ENV=development
WORKDIR /app
ADD . /app/
ENTRYPOINT ["python"]
CMD ["app.py"]

