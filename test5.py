import scrapy

class Test5(scrapy.Spider):
    name = 'test5'
    start_urls = ['https://www.brainyquote.com/authors/g']

    def parse_author_page(self, response):
        author_by_letter = response.css('td a::attr(href)').getall() #Get all author links of each page
        self.logger.info(f'Authors by letter are: {author_by_letter}')
        
        #Retrieve author names from each page:
        author_names = response.css('td a::text').getall()
        self.logger.info(f'Retrieve author names from each page: {author_names}')
        yield {'Author': author_names}
        
        #Check if there is a Next button:
        check_next_page = response.xpath('//li[contains(@class, "page-item")]/*[text()="Next"]/@href').get()
        self.logger.info(f'Next page is: {check_next_page}')
        #If the Next button exists, check whether it's disabled or not:
        #Check if Next button exists, and the button is enabled:
        if check_next_page is not None:
            self.logger.info(f'Which next page is being followed: {check_next_page}')
            yield response.follow(check_next_page, callback=self.parse_author_page)
        else:
            self.logger.info(f'Last page has been reached: {check_next_page}') 
            
        for each_author in author_by_letter:
            self.logger.info(f'Which each author: {each_author}')
            yield response.follow(each_author, callback=self.parse_each_author)
            
    #Define a new method to parse each author:
    def parse_each_author(self, response):
        if response.xpath('//span[@class="sepLine"]'):
            yield {'Extracted text for birth/death': response.xpath('//span[@class="sepLine"]/following-sibling::node()')}

        else:
            yield {'Extracted text for birth/death': None}
            