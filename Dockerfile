FROM python:2.7.15
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
RUN wget http://skylar.speech.cs.cmu.edu/~kyusonglee/model.tar 
RUN tar -xvf model.tar
COPY . .
EXPOSE 6000
CMD [ "gunicorn", "-b", "0.0.0.0:6000", "-w", "4", "wsgi:application"]
