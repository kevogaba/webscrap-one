import csv
import requests
from bs4 import BeautifulSoup

home_url = 'https://www.bilbasen.dk'
base_url = "https://www.bilbasen.dk/brugt/bil?IncludeEngrosCVR=true&amp;PriceFrom=0&amp;includeLeasing=true"
headers = {'User-Agent': 'Chrome/96.0.4664.45'}

'''Create empty list'''
quotes  = []
Specs = []
Summary = []

'''Allow user to choose between dealer and private'''
print(f'Choose between 1 for dealer and 2 for private \n')
choice = 2
# choice = input('>')
print(f'\n Scrapping... \n')

'''The choice logic'''
if choice == 1:
    url = 'https://www.bilbasen.dk/brugt/bil?ZipCode=0&IncludeEngrosCVR=True&Seller=1'
elif choice == 2:
    url = 'https://www.bilbasen.dk/brugt/bil?ZipCode=0&IncludeEngrosCVR=True&Seller=2'
else:
    url = base_url


while True:
    """
        Iterate over the url i.e. through the 'main url' 
        and those generated during pagination
    """

    html = requests.get(url, headers=headers)
    soup = BeautifulSoup(html.content, 'html5lib')
    all_cars = soup.find('div', attrs={'class':'contentWrapper'})


    '''Scrap for all the listings and urls'''
    for car in all_cars.findAll('div', attrs={'class':'row listing listing-plus bb-listing-clickable'}):

        '''Scrap for individual car'''
        for each_car in car.findAll('div', attrs={'class':'col-xs-4'}):

            '''find the individual car url'''
            individual_car = each_car.div.a['href']
            individual_car_url = home_url+individual_car

            individual_car_result = requests.get(individual_car_url, headers=headers)
            individual_car_soup = BeautifulSoup(individual_car_result.content, 'lxml')
            individual_car_info = individual_car_soup.find('div', attrs={'class':'bbVipWrapper cf'})

            '''find the name, price and summary info of each car'''
            name2 = individual_car_info.header.h1['title']
            price = individual_car_info.find('span', attrs={'class':'value'}).text
            summary = individual_car_info.find('section', attrs={'id':'bbVipDescription'}).text.replace('\r\n','').strip()
            Summary.append(summary)

            '''A for loop for all the tabulated data about the car'''
            info = individual_car_info.find('table', attrs={'class':'type1'})        
            for details in info.findAll('td'):
                specs = details.text.replace(' ','').strip()
                Specs.append(specs)

            '''Save the information in the list as dictionaries'''
            quote = {}
            quote['Name'] = name2
            quote['Price'] = price
            quote['Vehicle Summary'] = Summary
            quote['Top Features & Specs'] = Specs
            quotes.append(quote)

            '''Write the list to a csv file'''
            filename = 'car_details.csv'
            with open(filename, 'w', newline='') as f:
            	w = csv.DictWriter(f,['Name','Price','Vehicle Summary','Top Features & Specs'])
            	w.writeheader()
            	for quote in quotes:
            		w.writerow(quote)
            

    '''Find the next page to scrap in pagination and break the while loop'''
    next_url = None
    cur_page = soup.find('li', attrs={'class':'active'})
    search_next = cur_page.find_next('a', attrs={'class':'next'})
    if search_next:
        next_url = cur_page.find_next('a', attrs={'class':'next'}).get('href')
        url = next_url
        print(f'Scrapping the next page... \n')
    else:
        break
