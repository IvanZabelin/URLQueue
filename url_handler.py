from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import pika
import logging
import time


app = FastAPI()
logging.basicConfig(level=logging.INFO)


class BrowseRequest(BaseModel):
    """Модель данных для URL."""
    url: HttpUrl


def connect_to_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters("rabbitmq")
                )
            channel = connection.channel()
            channel.queue_declare(queue="url_queue")
            return channel
        except pika.exceptions.AMQPConnectionError as e:
            logging.error(
                f"Ошибка подключения к RabbitMQ: {e}. Повтор через 5 секунд."
                )
            time.sleep(5)


channel = connect_to_rabbitmq()


@app.post("/browse")
async def browse(request: BrowseRequest):
    try:
        url_str = str(request.url)
        channel.basic_publish(
            exchange="",
            routing_key="url_queue",
            body=url_str,
        )
        return {"message": "URL добавлен в очередь"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Не удалось добавить URL в очередь: {e}"
        )
