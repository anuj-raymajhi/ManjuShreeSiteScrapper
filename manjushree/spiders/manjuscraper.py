import scrapy

class ManjuscraperSpider(scrapy.Spider):
    name = "manjuscraper"
    allowed_domains = ["manjushreefinance.com.np"]
    start_urls = ["https://manjushreefinance.com.np"]
    linkSet = set()
    detailLinkSet = set()
    reportLinks = set()
    branchLink = set()
    visitedLinks = set()

    def parse(self, response):
        pageLinks = response.css('a::attr(href)')
        for link in pageLinks:
            link_url = link.get()
            if self.start_urls[0] in link_url and 'uploads' not in link_url:
                self.linkSet.add(link_url)
                if 'detail' in link_url:
                    self.detailLinkSet.add(link_url)
                if 'reports' in link_url:
                    self.reportLinks.add(link_url)
                if 'branch' in link_url:
                    self.branchLink.add(link_url)

        ## working for details category site
        for link in self.detailLinkSet:
            self.visitedLinks.add(link)
            yield response.follow(link, callback=self.parse_detail)
        
        ## for branch : working
        for link in self.branchLink:
            self.visitedLinks.add(link)
            yield response.follow(link, callback=self.parse_branch)
        
        ## for reports category : working
        for link in self.reportLinks:
            self.visitedLinks.add(link)
            yield response.follow(link, callback=self.parse_report)

    def extract_text_recursive(self, selector):
        # Extract text from the element and its children
        text_parts = selector.xpath('.//text()').getall()
        combined_text = ''.join(text_parts).strip()
        return combined_text


    def parse_detail(self, response):
        # paragraphs = response.xpath('//div[@class="editor-box"]//p/text()').getall()
        # list_items = response.xpath('//div[@class="editor-box"]//ul/li/text()').getall()
        # tables = response.xpath('//div[@class="editor-box"]//table').getall()

        # yield {
        #     'paragraphs': paragraphs,
        #     'list_items': list_items,
        #     'tables': ''.join(tables)
        # }
        
        ## lemme set some heirarchy in data
        ## detail pages got 1 apply link, description, and sometimes tables as well

        #apply link
        applyLink = response.xpath('//a[@title="Apply Now"]').xpath('@href').get()
        #get all text content within, bad frontend practice, dude different structures cha lol
        contentContainer = response.xpath('//div[@class="editor-box"]/*')
        pageContent = f'\nApply Link : {applyLink}\n{self.extract_text_recursive(contentContainer)}\n'

        yield {
            'Page Source' : response.url,
            'Content': pageContent
        }
    
    def parse_branch(self, response):
        cards = response.xpath('//*[@id="accordionExample"]/div')
        branches = []
        for card in cards:
            branch_title = card.xpath('.//div[@class="card-header"]//button/text()').get()
            branchContent = card.xpath('.//div[contains(@class, "collapse")]/div/div/div')
            lines = []
            for valuesContainer in branchContent:
                title = valuesContainer.css('.branch-title::text').getall()
                description = valuesContainer.css('.description p::text').getall()
                # print(type(title), title)
                line = ' '.join(''.join(title).strip().split()) + '\n' + '\n'.join(description)
                lines.append(line)
            branchLocation = card.xpath('//div[contains(@class, "collapse")]/div/div/span/a')
            branchLocation = branchLocation.css('::attr(href)').get()
            branches.append(branch_title+'\n'+'\n'.join(lines)+f'Location : {branchLocation}')
        
        yield {
            'Page Source' : response.url,
            'Content' : '\n'.join(branches)
        }

    def parse_report(self, response):
        ## accordion -> report date -> view link, download link
        #get accordian container which contains card classes
        accordionContainer = response.xpath('//*[@id="accordion"]/div')
        
        #iterate through each card and extract: date, redirection link, download link
        reports = []
        for card in accordionContainer:
            date = card.xpath('.//div[@class="card-header"]//button/text()').get()
            linkContainer = card.xpath('.//div[contains(@class, "collapse")]/div/div/div/div') # contains report links in one date value
            linkContent = []
            for container in linkContainer:
                report_name = container.xpath('.//span[@class="main-title"]/text()').get()
                report_view_link = container.xpath('.//div[@class="item-box"]/a').xpath('@href').get()
                download_link = container.xpath('.//a[contains(@class, "download-btn")]').xpath('@href').get()
                linkContent.append(f'{report_name}:\nview link : {report_view_link}\ndownload link : {download_link}')
            linkContent = '\n\n'.join(linkContent)
            reports.append(f'{date}\n{linkContent}\n')
        
        yield {
            'Page Source' : response.url,
            'Content' : '\n'.join(reports)
        }