import scrapy

class Test7(scrapy.Spider):
    name = 'test7'
    start_urls = ['https://www.brainyquote.com/authors']
    
    def parse(self, response):
        #Get full URL list of authors:
        #Outcomes: /authors/a, /authors/b, /authors/c, /authors/d, etc.
        #self.logger.info(response.headers)
        author_list = response.css('.r_mb a[href="/authors/g"]::attr(href)').get() #THIS IS TO SELECT ONLY /authors/g
        self.logger.info(f'The resulted URL is: {author_list}')
        
        #Iterate through the list and follow each link:
        if author_list:
            self.logger.info(f'Now following this link: {author_list}')
            yield response.follow(author_list, callback = self.parse_author_page, dont_filter=True)
            
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
            yield response.follow(check_next_page, callback=self.parse_author_page, dont_filter=True)
        else:
            self.logger.info(f'Last page has been reached: {check_next_page}') 
            
        for each_author in author_by_letter:
            self.logger.info(f'Which each author: {each_author}')
            yield response.follow(each_author, callback=self.parse_each_author, dont_filter=True)
            
    #Define a new method to parse each author:
    def parse_each_author(self, response):
        #Get birth year and death year:
        years = response.xpath('normalize-space(//span[@class="sepLine"]/following-sibling::text())').re(r'\d+\s*[A-Za-z]*|\d+')
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
        elif years is None:
            yield {
                'Birth Year': None,
                'Death Year': None
                }
