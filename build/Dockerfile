FROM python:3

ADD src /app
ADD requirements.txt /app

WORKDIR /app
RUN pip install -r requirements.txt

CMD [ "python", "/app/main.py" ]