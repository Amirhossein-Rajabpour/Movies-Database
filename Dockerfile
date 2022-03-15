FROM python:latest

WORKDIR /project

COPY . .

RUN pip install -r requierments.txt
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate

EXPOSE 8000

CMD ["python3", "manage.py", "runserver"]