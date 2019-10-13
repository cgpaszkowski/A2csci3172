import queue
import requests
from bs4 import BeautifulSoup

########## METHODS ##########

def make_soup(url):
    page = requests.get(url)
    data = page.text
    soup = BeautifulSoup(data, features="html.parser")
    return soup



def find_categories(soup):
    qu1 = queue.Queue(0)
    
    menu = soup.find('ul', {'class':'categoryList_16LAC'})
    for links in menu.find_all('li'):
        link = links.find('a')
        extension = link.get('href')
        url = "https://www.bestbuy.ca"
        url += extension
        qu1.put(url)
    return qu1



def find_sub_category(qu_subcat, qu_products):
    qu_subcat1 = queue.Queue(0)
    
    while not qu_subcat.empty():
        url = qu_subcat.get()
        page = make_soup(url)
        
        cats = page.find('div', {'class':'container_1-PFH row_1Rbqw'})
        if cats is None:
            #print(url)
            qu_products.put(url)    #if the page has no sub-categories, must be product page
        else:
            ####### Modified to prevent timeout issue #######
            #for subcats in cats.find_all('a'):
            #    extension = subcats.get('href')
            #    url = "https://www.bestbuy.ca"
            #    url += extension
            #    qu_subcat1.put(url)
            #################################################
            subcats = cats.find('a')
            extension = subcats.get('href')
            url = "https://www.bestbuy.ca"
            url += extension
            qu_subcat1.put(url)
            #################################################

            
    return qu_subcat1, qu_products


def product_list(qu_products):
    qu_one_product = queue.Queue(0)
    while not qu_products.empty():
        url = qu_products.get()
        soup = make_soup(url)

        for product_list in soup.find_all('div', {'class':'productsRow_DcaXn row_1Rbqw'}):
            for product in product_list.find_all('a'):
                product_link = "https://www.bestbuy.ca"
                product_link += product.get('href')
                qu_one_product.put(product_link)
    product_page(qu_one_product)





def product_page(qu_products):
    while not qu_products.empty():
        url = qu_products.get()
        print(url)
        soup = make_soup(url)
        body_tag = soup.body
        page_title = soup.title.string
        print("Page Title: " + page_title + "\n")
        count = 0

        for codes in body_tag.find_all('ol', {'class': 'breadcrumbList_16xQ3 x-breadcrumbs'}):
            for codes1 in codes.find_all('li'):
                for codes2 in codes1.find_all('a'):
                    crumbs = codes2.find('span').string
                    if count < 1:
                        category = ""
                    elif count == 1:
                        category = "\tCategory: "
                    else:
                        category = "\t"*count + "Sub-category: "
                    print(category + crumbs)
                    count += 1

        product_name = body_tag.find('h1', {'class': 'productName_19xJx'})
        try:
            print("\t"*count + "Product Name: " + product_name.string)
        except:
            pass


        for details in body_tag.find_all('div', {'class': 'modelDetailSection_2o3XX'}):
            model_num = details.find('span', {'itemprop': 'model'})
            web_code = details.find('span', {'itemprop': 'sku'})
            try:
                print("\t"*count + "\tCode: " + web_code.string)
            except:
                pass
            try:
                print("\t"*count + "\tModel: " + model_num.string)
            except:
                pass
            

        price = body_tag.find('meta', {'itemprop': 'price'})
        try:
            print("\t"*count + "\tPrice: $" + price.get('content'))
        except:
            pass



########## MAIN ##########
        
url = "https://www.bestbuy.ca"
qu_cat = queue.Queue(0)
qu_subcat = queue.Queue(0)
qu_products = queue.Queue(0)

soup = make_soup(url)
qu_cat = find_categories(soup)
qu_subcat, qu_products = find_sub_category(qu_cat, qu_products)


while not qu_subcat.empty():
    qu_subcat, qu_products = find_sub_category(qu_subcat, qu_products)
    
product_list(qu_products)
