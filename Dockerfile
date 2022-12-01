
FROM tiangolo/uwsgi-nginx-flask:python3.11

RUN mkdir /code
RUN mkdir /code/data
WORKDIR /code
ADD requirements.txt /code/
RUN apt-get update && apt-get install -y python3-pip git
RUN pip install --upgrade pip
RUN pip install --upgrade flask
RUN pip install uwsgi
RUN pip install -r requirements.txt --no-cache-dir
RUN pip3 install --no-cache-dir "optime @ git+https://github.com/mtyt/optime"

# add all contents of src into /code/
ADD src /code/
COPY data/students_example.csv /code/data

# ssh
ENV SSH_PASSWD "root:Docker!"
RUN apt-get update \
        && apt-get install -y --no-install-recommends dialog \
        && apt-get update \
	&& apt-get install -y --no-install-recommends openssh-server \
	&& echo "$SSH_PASSWD" | chpasswd 

COPY sshd_config /etc/ssh/
COPY init.sh /usr/local/bin/
COPY uwsgi.ini /app/
	
RUN chmod u+x /usr/local/bin/init.sh
EXPOSE 8000 2222 9191
#CMD ["python", "/code/manage.py", "runserver", "0.0.0.0:8000"]
ENTRYPOINT ["init.sh"]
