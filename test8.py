import scrapy

class Test8(scrapy.Spider):
    name = 'test8'
    start_urls = ['https://www.brainyquote.com/authors']
    
    def parse(self, response):
        author_list = response.css('.r_mb a[href="/authors/g"]::attr(href)').get() # Selecting only /authors/g
        self.logger.info(f'The resulted URL is: {author_list}')
        
        if author_list:
            self.logger.info(f'Now following this link: {author_list}')
            yield response.follow(author_list, callback=self.parse_author_page, dont_filter=True)
            
    def parse_author_page(self, response):
        author_links = response.css('td a::attr(href)').getall()
        author_names = response.css('td a::text').getall()
        
        self.logger.info(f'Retrieve author names: {author_names}')

        for author_name, author_link in zip(author_names, author_links):
            yield response.follow(author_link, callback=self.parse_each_author, dont_filter=True, meta={'author_name': author_name})

        # Check for the "Next" button
        check_next_page = response.xpath('//li[contains(@class, "page-item")]/*[text()="Next"]/@href').get()
        if check_next_page:
            self.logger.info(f'Following next page: {check_next_page}')
            yield response.follow(check_next_page, callback=self.parse_author_page, dont_filter=True)

    def parse_each_author(self, response):
        author_name = response.meta['author_name']  # Retrieve author name
        years = response.xpath('normalize-space(//span[@class="sepLine"]/following-sibling::text())').re(r'\d+\s*[A-Za-z]*|\d+')

        birth_year = years[0] if len(years) > 0 else None
        death_year = years[1] if len(years) > 1 else None

        yield {
            'Author': author_name,
            'Birth Year': birth_year,
            'Death Year': death_year
        }
