FROM python:3.11-alpine

WORKDIR /python-room-booking
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install psycopg2-binary

COPY . .

ENV FLASK_APP=main:app
ENV FLASK_ENV=development
ENV DATABASE_URL=postgresql://sinqx:663857@db:5432/postgres

CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]