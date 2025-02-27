import scrapy

class Test4(scrapy.Spider):
    name = 'test4'
    start_urls = ['https://www.brainyquote.com/authors']
    
    def parse(self, response):
        #Get full URL list of authors:
        #Outcomes: /authors/a, /authors/b, /authors/c, /authors/d, etc.
        author_list = response.css('div.r_mb a::attr(href)').get() #THIS IS TO SELECT ONLY /authors/a
        self.logger.info(f'The resulted URL is: {author_list}')
        
        #Iterate through the list and follow each link:
        if author_list:
            self.logger.info(f'Now following this link: {author_list}')
            yield response.follow(author_list, callback = self.parse_author_page)
            
    #Define a new method to parse every author page from the list     
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
        #Get birth year and death year by the last 4 digits:
        #Two cases to cover:
        #1) 551 BC - 479 BC (authors/confucius-quotes)
        #2) No birth year and no death year (authors/lao-tzu-quotes)

        years = response.xpath('//div[@class="subnav-below-p"]/a[contains(@href, "/birthdays")]/text()').re(r'\d{4}')
        if years:
            self.logger.info(f'Extracted years: {years}')
        else:
            self.logger.info('No birth or death year found')

        if len(years) > 1:
            yield {
                'Birth Year': years[0],
                'Death Year': years[1]
                }
        elif len(years) == 1:
            yield {
                'Birth Year': years[0],
                'Death Year': None
                }