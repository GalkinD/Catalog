import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

data = {
    "Категория": [],
    "Артикул": [],
    "Бренд": [],
    "Наименование товара": [],
    "Цена": [],
    "Описание": [],
    "Ссылки на изображения": []
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
}


def get_category_links(main_url):
    response = requests.get(main_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    category_links = []
    category_blocks = soup.select('li.sect a')

    for category in category_blocks:
        full_link = "https://yacht-parts.ru" + category['href']
        category_links.append((category.text.strip(), full_link))

    return category_links


def get_product_links(category_url):
    response = requests.get(category_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    product_links = []
    product_blocks = soup.select(".list_item_wrapp .list_item")

    for product in product_blocks:
        product_link = "https://yacht-parts.ru" + product.select_one(".desc_name a")['href']
        product_links.append(product_link)

    return product_links


def parse_product(product_url, category_name):
    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    try:
        name_elem = soup.select_one("#pagetitle")
        name = name_elem.text.strip() if name_elem else "Наименование отсутствует"

        sku_elem = soup.select_one(".article .value")
        sku = sku_elem.text.strip() if sku_elem else "Не указан"

        brand_elem = soup.select_one(".item-title")
        brand = brand_elem.text.strip() if brand_elem else "Бренд не указан"

        description_elem = soup.select_one(".preview_text")
        description = description_elem.text.strip() if description_elem else "Описание отсутствует"

        price_elem = soup.select_one(".cost .price")
        price = price_elem.text.strip() if price_elem else "Цена не указана"

        images = []
        for img in soup.select("img[id^='bx_'][src]"):
            src = img['src']
            if not src.startswith("http"):
                src = "https://yacht-parts.ru" + src
            images.append(src)
        image_links = ", ".join(images)

        data["Категория"].append(category_name)
        data["Артикул"].append(sku)
        data["Бренд"].append(brand)
        data["Наименование товара"].append(name)
        data["Цена"].append(price)
        data["Описание"].append(description)
        data["Ссылки на изображения"].append(image_links)

        print(f"Товар добавлен: {name}, Артикул: {sku}, Категория: {category_name}")

    except Exception as e:
        print(f"Ошибка при парсинге товара {product_url}: {e}")


def main():
    main_url = "https://yacht-parts.ru/catalog/"

    print(f"Парсинг всех категорий из: {main_url}")

    category_links = get_category_links(main_url)

    start_time = time.time()

    for category_name, category_link in category_links:
        print(f"Парсинг категории: {category_link}")
        product_links = get_product_links(category_link)

        for product_link in product_links:
            if time.time() - start_time > 300:
                print("Время выполнения превышено. Завершение парсинга.")
                return

            parse_product(product_link, category_name)
            time.sleep(1)


main()


if any(data.values()):
    df = pd.DataFrame(data)
    df.to_excel("yacht_parts_catalog.xlsx", index=False)
    print("Данные успешно записаны в файл yacht_parts_catalog.xlsx")
else:
    print("Данные для записи отсутствуют")
