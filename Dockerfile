FROM python:3.9-slim

WORKDIR /app

RUN pip install --upgrade pip

COPY ./requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./ ./

EXPOSE 8000

CMD ["unvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]