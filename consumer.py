import pika
from selenium import webdriver
import logging
import time


logging.basicConfig(level=logging.INFO)


def connect_to_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters("rabbitmq")
            )
            channel = connection.channel()
            return channel
        except pika.exceptions.AMQPConnectionError as e:
            logging.error(
                f"Ошибка подключения к RabbitMQ: {e}. Повтор через 5 секунд."
            )
            time.sleep(5)


channel = connect_to_rabbitmq()


options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Remote(
    command_executor="http://selenium-hub:4444/wd/hub",
    options=options,
)


def callback(ch, method, properties, body):
    url = body.decode("utf-8")
    logging.info(f"Получен URL: {url}")
    try:
        driver.get(url)
        html_content = driver.page_source
        logging.info(f"HTML страницы {url}:\n{html_content}")
    except Exception as e:
        logging.error(f"Ошибка при загрузке {url}: {e}")


channel.basic_consume(
    queue="url_queue", on_message_callback=callback, auto_ack=True)


try:
    logging.info("Запуск consumer...")
    channel.start_consuming()
except KeyboardInterrupt:
    logging.info("Остановка consumer...")
finally:
    driver.quit()
    channel.close()
