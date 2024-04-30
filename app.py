from bs4 import BeautifulSoup
from flask import Flask, request
import mysql.connector
import requests
import decimal

app = Flask(__name__)

def get_connection():
    config = {
        "user": "desarrollo",
        "password": "5239424209",
        "host": "localhost",
        "port": "3306",
        "database": "maxi",
    }
    conn = mysql.connector.connect(**config)

    return conn

@app.route("/api", methods=["GET"])
def grab_datetimes():
    products = check_url()
    if request.method == "GET":
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        for product in products:
            clear_price = product['price'].replace("$", "").replace(",", "")
            price = decimal.Decimal(clear_price)
            values = (product['name'], price)
            query = "INSERT INTO products (name, price) VALUES (%s, %s)"
            cursor.execute(query, values)
            connection.commit()
        cursor.close()
        connection.close()
        return products, 200

def check_url() -> list:
    url = 'https://free-gifts-demo.mageplaza.com/men/tops-men.html?product_list_limit=36'
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        ol_element = soup.find('ol', class_='products list items product-items')
        if ol_element:
            list_items = ol_element.find_all('li', class_='item product product-item')
            products = []
            for item in list_items:
                product_name = item.find('a', class_='product-item-link').text.strip()
                product_price = item.find('span', class_='price').text.strip()

                product = {
                    'name':product_name,
                    'price':product_price
                }
                products.append(product)
            return products
    return {}

if __name__ == "__main__":
    app.run(host="0.0.0.0")