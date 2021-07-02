import requests
import json

# ключ доступа
KEY = ''

SITE_URL = ''

DATA_URLS = {
    'product': 'oc_product',  # информация о товаре  (price, product_id, uid все тут)
    'product_description': 'oc_product_description',  # информация о товаре
    'product_to_category': 'oc_product_to_category',  # информация о товаре и принадлежность к категории
    'product_to_store': 'oc_product_to_store',  # публикация в магазине
    'product_to_multistore': 'oc_product_to_multistore',  # принадлежность товара к складам
    'product_to_layout': 'oc_product_to_layout',  # публикация в магазине
    'product_special': 'oc_product_special', # акционная цена
    'multistore': 'oc_multistore' # система складов

}

#url = SITE_URL + DATA_URLS

headers_auth = {
        'Content-Type': 'application/json',
        'key': KEY
    }


def post_product():
    '''

    :return:
    '''
    data = {
        'product_id': 82303,  # генерируется автоматически
        'uid': 1,   # id идентификатора из 1с
        'price': 0,
        'status': 1,
        'stock_status_id': 5,  # в наличии
        'shipping': 1,
        'subtract': 1,
    }
    data_oc = json.dumps(data, ensure_ascii=False).encode('utf8')
    url_post = requests.post(SITE_URL + DATA_URLS['product'], headers=headers_auth, data=data_oc)

def get_product():
    '''
        В заголовке передаем, что работаем с JSON и ключ сгенерированный в админке
        (Обязательно в админке указать IP адресс с которого будет идти запрос)
        Использовать в запросе параметр transform=1 = тогда вид отображения данных будет
        {"product_id":"1"}

        Использование нужных колонок параметр columns:
        columns=product_id,price

        Filters param -
        cs: contain string (string contains value)
        sw: start with (string starts with value)
        ew: end with (string end with value)
        eq: equal (string or number matches exactly)
        lt: lower than (number is lower than value)
        le: lower or equal (number is lower than or equal to value)
        ge: greater or equal (number is higher than or equal to value)
        gt: greater than (number is higher than value)
        bt: between (number is between two comma separated values)
        in: in (number or string is in comma separated list of values)
        is: is null (field contains "NULL" value, does not need value specified)

        Использование единичного фильтра для этого использовать параметр-
        filter=product_name,eq,Internet

        Использование нескольких запросов -
        filter[]=id,ge,1&filter[]=id,le,3&satisfy=all

        Конечная ссылка с параметрами
        ?columns=product_id,price&filter[]=product_id,eq,1&filter[]=product_id,eq,3&satisfy=all&transform=1



    '''
    url_get = requests.get(SITE_URL + DATA_URLS['product'], headers=headers_auth)


def put_product(product_id):
    """

    :param product_id: id товара на сайте который нужно обновить
    :return:
    """
    data = {
        'quantity': 17,
    }
    data_oc = json.dumps(data, ensure_ascii=False).encode('utf8')
    url_put = requests.put(SITE_URL + DATA_URLS['product'] + f"/{product_id}", headers=headers_auth, data=data_oc)

print(put_product(159874))

"""
 Тела запросов для DATA_URLS
 лучше соблюдать такой порядок действий при добавлении товара. Работа со складами идет последним так как там 
 динамический первичный ключ который обновляется если кто то в магазине отредактирует товар.
 
1) Отправляете данные в oc_product - информация о номере модели , цена и т.д (магазин формирует product_id который нам 
нужен в дальнейшем для использования)
2) Отправляете GET запрос на получение этого product_id, отправляете параметр filter=uid,eq,id_1c
где id_1c(id идентификатора в 1с) далее в ответе вы получите product_id его лучше сохранить в 1с чтобы в дальнейшем 
использовать
 
 oc_product = {
        'product_id': 82303,  # генерируется автоматически
        'uid': id_1c,   # id идентификатора товара из 1с
        'price': 0,
        'status': 1,
        'stock_status_id': 5,  # в наличии
        'shipping': 1,
        'subtract': 1,
 }
 
 Если вдруг надо обновить название товара -
 то использовать в PUT такой запрос f"/{product_id}-1" - где цифра 1 постоянна а product_id = product_id
 oc_product_description = {
    'product_id': 82303,
    'language_id': 1, - всегда 1 - означает что текст на русском языке
    'name': "тестовый товар"
 }
 
 oc_product_special = {
    'product_special_id': 213, - генерируется автоматически если отправлять POST запрос на добавление при PUT(обновлении)
    использовать product_special_id, получить данный product_special_id можно GET запросом с параметром фильтра product_id
    
    'product_id': 82303,
    'customer_group_id': 1, - всегда 1 для розничных клиентов
    'priority': 1,
    'price': 84, - акционная цена 
    'date_start': 2021-03-31, # по желанию дата старта акции в формате строки
    'date_end': 2021-04-31, # по желанию дата окончания акции в формате строки
 }
 
 oc_product_category = {
    'product_id': 82303,
    'category_id': 34, - id категории куда добавляется новый товар и в дальнейшем будут редактировать менеджеры
    'main_category': 0
 }
 
 oc_product_to_store = {
    'product_id': 82303,
    'store_id': 0 - всегда 0
 }
 
 oc_product_to_layout = {
    'product_id': 82303,
    'store_id': 0, - всегда 0
    'layout_id': 0, - всегда 0
 }
 
 
 Теперь работаем со складом.
 Внимание ! Так же нужно будет сумму товаров со всех складов передать в oc_product подробнее внизу.
 для получения id склада в интернет магазине обращаемся по запросу GET = 
 ?columns=multistore_id,cid&filter=cid,eq,UR97495&transform=1
 ответ получим {'multistore_id': 5', cid': UR97495 } - нужно в 1с будет сохранить значение multistore_id чтобы проще
 было к нему обращаться
 
 oc_multistore = {
    'multistore_id': 5,
    'cid': UR97495
 }
 
 Далее отправляем информацию о товаре если товар новый:
 Для того что передать массово все склады использовать вариант с массивом
 [{'multistore_id': 1, 'product_id': 82303, 'quantity': 0 }, {'multistore_id': 5, 'product_id': 82303, 'quantity': 9  },{'multistore_id': 4, 'product_id': 82303, 'quantity': 8 }]
 
 это если единично
 oc_product_to_multistore = {
    'product_id': 82303,
    'multistore_id': 5,
    'quantity': 9 - количество конкретно на складе UR97495 
 }
 
 Для обновления использовать PUT запрос где указывается "/{product_id}-{multistore_id}" 
 пример: /oc_product_to_multistore/82303-5 
 Он обновит product_id у склада номер 5 
 
 Для массового обновления склада можно использовать массив как в случае с POST запросом.
 Но при этом порядок в массиве должен соответвовать перечисленным id
 пример: /oc_product_to_multistore/82303-1,82303-5,82303-4
 [{'multistore_id': 1, 'product_id': 82303, 'quantity': 0 }, {'multistore_id': 5, 'product_id': 82303, 'quantity': 9  },{'multistore_id': 4, 'product_id': 82303, 'quantity': 8 }]
 
 Обязательно ! Обновить quantity в oc_product для этого вызвать PUT запрос который указан в примере 
 в поле quantity oc_product передавать сумму всех товаров складов 
 пример написан в функции put_product
 
 
"""

"""
Информация о заказе -  чтобы получить информацию о заказе, надо отправить запрос на адрес - 
oc_order = {
    order_id: 2333  - id заказа
    invoice_no /// не надо
    invoice_prefix /// не надо
    store_id: 0
    store_name: // не надо
    store_url: // не надо
    customer_id: 3448 - id клиента в базе сайта
    customer_group_id: 1 по умолчанию
    firstname: имя
    lastname: фамилия
    email: имейл
    telephone: телефон
    fax: /// не надо
    custom_field /// не надо
    payment_firstname /// не надо
    payment_lastname /// не надо
    payment_company /// не надо
    payment_address_1: адресс доставки клиента
    payment_address_2 /// не надо
    payment_city: Город
    payment_postcode: почтовое отделение
    payment_country: страна
    payment_country_id /// не надо
    payment_zone: регион
    payment_zone_id; /// не надо
    payment_address_format /// не надо
    payment_custom_field /// не надо
    payment_method: метод оплаты картой и т.д
    payment_code: /// не надо
    shipping_firstname /// не надо
    shipping_lastname /// не надо
    shipping_company /// не надо
    shipping_address_1 /// не надо
    shipping_address_2 /// не надо
    shipping_city /// не надо
    shipping_postcode /// не надо
    shipping_country /// не надо
    shipping_country_id /// не надо
    shipping_zone /// не надо
    shipping_zone_id /// не надо
    shipping_address_format /// не надо
    shipping_custom_field /// не надо
    shipping_method: метод доставки 
    shipping_code /// не надо
    comment: комментарии
    total: Итоговая сумма
    order_status_id: статус товара
    affiliate_id: /// не надо
    commission /// не надо
    marketing_id /// не надо
    tracking /// не надо
    language_id /// не надо
    currency_id /// не надо
    currency_code /// не надо
    currency_value /// не надо
    ip /// не надо
    forwarded_ip /// не надо
    user_agent /// не надо
    accept_language /// не надо
    date_added /// не надо
    date_modified /// не надо
    sent_to_1c: будет меняться с 1 на 0 где 1 это надо отправить заказ в 1с, после получения информации о заказе 1с меняет значение на 0
    sent_to_sms: 0 - тестовый смс модуль
}


получение информации о товарах:
    oc_order_product = {
        order_product_id  /// не надо
        order_id: указываем id заказа
        product_id: id товара в магазине
        name: /// не надо
        model: код товара из 1с
        quantity 2
        price: цена товара за 1 единицу
        total: итого конкретного товара
        tax /// не надо
        reward /// не надо
}

"""

