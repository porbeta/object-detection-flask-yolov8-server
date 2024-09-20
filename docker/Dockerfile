FROM registry.access.redhat.com/ubi9/python-312:1-20.1722518948

# By default, listen on port 8081
EXPOSE 8081/tcp

# Set the working directory in the container
WORKDIR /projects

# Copy the content of the local src directory to the working directory
COPY . .

USER root

RUN yum update -y && yum install mesa-libGL  -y

USER default

# Install any dependencies
RUN \
  if [ -f requirements.txt ]; \
    then pip install -r requirements.txt; \
  elif [ `ls -1q *.txt | wc -l` == 1 ]; \
    then pip install -r *.txt; \
  fi

# Specify the command to run on container start
CMD [ "gunicorn", "wsgi", "--bind=0.0.0.0:8081", "--access-logfile=-", "-w=1", "--threads=100" ]