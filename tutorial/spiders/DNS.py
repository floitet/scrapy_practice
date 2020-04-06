import scrapy


class QuotesSpider(scrapy.Spider):
    name = "dns"
    start_urls = ['https://www.dns-shop.ru/catalog/17a8a01d16404e77/smartfony/']

    def parse(self, response):
        """
        In this method we get title, short description and image link
        + we create dict type item that we will be passing along through all methods
        until we yield ready item in the last method in the chain

        :return: request with meta that includes our formed item
        """
        for item in response.css('.n-catalog-product__main'):
            parsed_url = item.css(".ui-link").xpath("@href").get()
            next_url = 'https://www.dns-shop.ru' + parsed_url
            title = item.css('.product-info__title-link a.ui-link::text').get()
            title_desc = item.css('.product-info__title-description::text').get()
            images = item.css("img").xpath("@data-src").get()
            item_scraped = (dict(title=title, title_desc=title_desc, images=images))
            yield scrapy.Request(callback=self.parse_price_full_desc, meta={'item': item_scraped}, url=next_url)

    def parse_price_full_desc(self, response):
        """
        Here we add to our item from previous parsing method two new keys:
        price and full description along with their parsed values
        :return: request with meta that includes our updated item
        """
        next_url = response.url + 'characteristics/'
        item_scraped = response.meta['item']
        item_scraped['price'] = response.css(".current-price-value").xpath("@data-price-value").get()
        item_scraped['full description'] = response.css('.price-item-description p::text').get()
        yield scrapy.Request(callback=self.parse_full_params, meta={'item': item_scraped, 'item_url': response.url},
                             url=next_url)

    def parse_full_params(self, response):

        """
        In this method we parse all the item characteristics
        :param response: contains meta with our item as it is formed in previous parsing method
        :return: fully shaped item with dictionary "params" added
        """
        item_url = response.meta['item_url']
        next_url = item_url + 'opinion/'
        item_scraped = response.meta['item']
        params = {}

        # we need to get all the info from the characteristics table and shape it into dict
        # first we are going to get all the field's names such as "color", "size", etc.

        labels = response.css(".table-params .dots span::text").getall()

        # then let's clean them from spaces

        labels_no_spaces = list(filter(lambda x: x != ' ', labels))

        # now let's get all the parameters that fall into this fields
        # in html structure they don't have defined class name and stored in unmarked tds
        # the way around it could be get all the text from tds and clean it from what we don't need
        # !! first we are going to get all the text from tds and clean from spaces

        defined_params = response.css(".table-params tr td::text").getall()
        defined_params_no_spaces = list(filter(lambda x: x != ' ', defined_params))

        # what we need to exclude is general field names that got included in our selection
        # fortunately, they have class defined so let's grab them

        names_in_params = response.css(".table-part::text").getall()

        # and exclude them from our list of characteristics

        total_clean_defined_params = [item for item in defined_params_no_spaces if item not in names_in_params]

        # now we're ready to create a dict with all the labels and related characteristics
        # from two lists of the same length labels_no_spaces and total_clean_defined_params
        # where all the elements with same index related with each other

        for i in labels_no_spaces:
            params[i] = total_clean_defined_params[labels_no_spaces.index(i)]

        item_scraped['params'] = params

        yield scrapy.Request(callback=self.parse_reviews, meta={'item': item_scraped}, url=next_url)

    def parse_reviews(self, response):

        item_scraped = response.meta['item']

        overall_rating = {
            'Общий рейтинг': response.css('.circle-rating__number::text').get(),
            'Количество отзывов': response.css('.circle-rating__content a::text').get()
        }

        concrete_rating = response.css('.ow-user-ratings__text span::text').getall()

        for i in concrete_rating:
            if concrete_rating.index(i) % 2 == 0:
                overall_rating[i] = concrete_rating[concrete_rating.index(i) + 1]

        item_scraped['Average rating'] = overall_rating

        reviews = {}
        count = 1
        review_blocks = response.css('.ow-opinions__item')
        for item in review_blocks:
            if review_blocks.index(item) != 0:

                review = {
                    'Имя пользователя': item.css('.ow-user-info__name::text').getall()
                }

                user_rated = item.css('.ow-user-rating__text span::text').getall()

                if user_rated:
                    review['Рейтинг от юзера'] = {}
                    for i in user_rated:
                        if user_rated.index(i) % 2 == 0:
                            review['Рейтинг от юзера'][i] = user_rated[user_rated.index(i) + 1]

                adv_disadv_com = item.css('.ow-opinion__text ::text').getall()
                adv_disadv_com_no_spc = list(filter(lambda x: x != ' ', adv_disadv_com))

                review['Отзывы юзера'] = adv_disadv_com_no_spc
                next_user = 'Ревью пользователя {}'.format(count)
                reviews[next_user] = review
                count += 1

            item_scraped['Отзывы пользователей'] = reviews

        yield item_scraped
