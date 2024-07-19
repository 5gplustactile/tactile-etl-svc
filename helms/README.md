Airflow Manual Process
-----------------------


```
k apply -f git-pvc.yaml
k apply -f git-pod.yaml
k appy -f airflow-cronjob.yaml

apt install git -y

# include ssh key access github if not exists
ssh-keygen –t rsa –b 4096

# import the id_rsa.pub to github

cd /dags-folder
git clone git@github.com:5gplustactile/tactile-etl-svc.git


helm upgrade --install  -n airflow airflow --create-namespace  apache-airflow/airflow -f values-airflow.yaml

# install the requirements in flower, scheduler, triggerer, webserver and worker pods
cat > r.txt << EOF
urllib3==1.26.3
pymongo==4.3.3
random-object-id==2.0.0
requests==2.27.1
PyGithub==2.1.1
termcolor==2.4.0
minio==7.2.4
statsmodels==0.14.2
python-dotenv==1.0.0
random-object-id==2.0.0
EOF

pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r r.txt
pip3 install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r r.txt

```