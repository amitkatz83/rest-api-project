FROM python:3.10
#EXPOSE 5000
WORKDIR /app 
COPY ./requirements.txt requirements.txt
#RUN pip install flask 
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt 
COPY . .
#CMD ["flask","run","--host","0.0.0.0"]
#to run on gunicorn
#CMD ["gunicorn", "--bind","0.0.0.0:80","app:create_app()"] 
CMD ["/bin/bash", "docker-entrypoint.sh"] 