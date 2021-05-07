FROM python:3.6-stretch
COPY . /Fernbach
WORKDIR /Fernbach
ADD . /Fernbach
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["flask", "run"]