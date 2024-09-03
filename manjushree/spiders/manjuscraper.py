import scrapy

class ManjuscraperSpider(scrapy.Spider):
    name = "manjuscraper"
    allowed_domains = ["manjushreefinance.com.np"]
    start_urls = ["https://manjushreefinance.com.np"]
    linkSet = set()
    detailLinkSet = set()
    reportLinks = set()
    branchLink = set()
    teamLinks = set()
    rateLinks = set()
    pageLinks = set()
    downloadsLink = set()
    menuSites = ['/other-services','/products','/loan','/digital-banking','/deposit']
    menuLinks = set()
    visitedLinks = set()

    def parse(self, response):
        pageLinks = response.css('a::attr(href)')
        for link in pageLinks:
            link_url = link.get()
            if self.start_urls[0] in link_url and 'uploads' not in link_url:
                self.linkSet.add(link_url)
                if '/detail' in link_url:
                    self.detailLinkSet.add(link_url)
                if '/reports' in link_url:
                    self.reportLinks.add(link_url)
                if '/branch' in link_url:
                    self.branchLink.add(link_url)
                if '/team' in link_url:
                    self.teamLinks.add(link_url)
                if '/rates' in link_url:
                    self.rateLinks.add(link_url)
                if '/page' in link_url:
                    self.pageLinks.add(link_url)
                if '/downloads' in link_url:
                    self.downloadsLink.add(link_url)
                for menuPage in self.menuSites:
                    if menuPage in link_url:
                        self.menuLinks.add(link_url)


        ## for /detail : 
        # for link in self.detailLinkSet:
        #     self.visitedLinks.add(link)
        #     yield response.follow(link, callback=self.parse_detail)
        
        # ## for /branch : working
        # for link in self.branchLink:
        #     self.visitedLinks.add(link)
        #     yield response.follow(link, callback=self.parse_branch)
        
        # ## for /reports category : working
        # for link in self.reportLinks:
        #     self.visitedLinks.add(link)
        #     yield response.follow(link, callback=self.parse_report)

        # ## for /team : working
        # for link in self.teamLinks:
        #     self.visitedLinks.add(link)
        #     yield response.follow(link, callback=self.parse_team)

        # ## for /rates : working
        # for link in self.rateLinks:
        #     self.visitedLinks.add(link)
        #     yield response.follow(link, callback=self.parse_rate)

        # ## for /page : working
        # for link in self.pageLinks:
        #     self.visitedLinks.add(link)
        #     yield response.follow(link, callback=self.parse_page)

        # ## for /downloads : working
        # for link in self.downloadsLink:
        #     self.visitedLinks.add(link)
        #     yield response.follow(link, callback=self.parse_downloads)

        ## for menu type pages : working
        for link in self.menuLinks:
            self.visitedLinks.add(link)
            yield response.follow(link, callback=self.parse_menu)

    def extract_text_recursive(self, selector):
        # Extract text from the element and its children
        text_parts = selector.xpath('.//text()').getall()
        combined_text = ' '.join(text_parts).strip()
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

    def parse_team(self, response):
        title = response.xpath('//h1[@class="page-title"]/text()').get()
        people = response.xpath('//div[@class="teambox"]')
        details = []
        for person in people:
            image_src = person.xpath('.//img').xpath('@src').get()
            detail = self.extract_text_recursive(person)
            temp = f'Person Image Link : {image_src}\nPerson Detail:\n{detail.strip()}'
            details.append(temp)
        details = "\n".join(details)
        pageContent = f'{title}\n{details}'

        yield {
            'Page Source' : response.url,
            'Content' : pageContent
        }

    def parse_rate(self, response):
        # /rates working for 3 pages
        if 'base-and-spread-rate' not in response.url:
            title = response.xpath('//h1[@class="page-title"]/text()').get()
            tableContainer = response.xpath('//div[@class="editor-box"]//table')
            tablesContent = []
            for prollytable in tableContainer:
                tableContent=[] 
                rows = prollytable.xpath('./tbody/tr')
                for row in rows:
                    valueSelector = row.xpath('./td')
                    val = ' '.join(self.extract_text_recursive(valueSelector).split())
                    tableContent.append(val)
                tableContent = '\n'.join(tableContent)
                tablesContent.append(tableContent)
            tablesContent = '\n\n'.join(tablesContent)
            pageContent = f'{title}\n{tablesContent}'
            yield {
                'Page Source' : response.url,
                'Content' : pageContent
            }
        else:
            title = response.xpath('//div[@class="editor-box"]/h2/text()').get()
            cardContainer = response.xpath('//div[@id="accordion"]/div')
            tablesContent = []
            for card in cardContainer:
                year = card.xpath('./div[@class="card-header"]/h5/button/text()').get()
                tableRows = card.xpath('.//div[@class="card-body"]//table/tbody/tr')
                tableContent = []
                for row in tableRows:
                    valueSelector = row.xpath('./td')
                    val = ' '.join(self.extract_text_recursive(valueSelector).split())
                    tableContent.append(val)
                tableContent = '\n'.join(tableContent)
                tablesContent.append(tableContent)
            tablesContent = '\n\n'.join(tablesContent)
            pageContent = f'{title}\n{tablesContent}'

            yield {
                'Page Source' : response.url,
                'Content' : pageContent
            }

    def parse_page(self, response):
        # working for 2 page within /page
        if 'capital' in response.url:
            title = response.xpath('//div[@class="editor-box"]/h2/text()').get()
            tableRows = response.xpath('//div[@class="editor-box"]//table/tbody/tr')
            tableContent = []
            for row in tableRows:
                valueSelector = row.xpath('./td')
                val = ' '.join(self.extract_text_recursive(valueSelector).split())
                tableContent.append(val)
            tableContent = '\n'.join(tableContent)
            pageContent = f'{title}\n\n{tableContent}'

            yield {
                'Page Source' : response.url,
                'Content' : pageContent
            }
        else:
            title = response.xpath('//h1[@class="page-title"]/text()').get()
            paras = response.xpath('//div[@class="editor-box"]/p')
            parasContent = []
            for para in paras:
                p = self.extract_text_recursive(para)
                parasContent.append(p)
            parasContent = '\n'.join(parasContent)
            pageContent = f'{title}\n\{parasContent}'

            yield {
                'Page Source' : response.url,
                'Content' : pageContent
            }
    
    def parse_downloads(self, response):
        # working for /downloads
        title = response.xpath('//h1[@class="page-title"]/text()').get()
        reportSection = response.xpath('//div[@class="section report-list"]/div/div')
        sectionIterator = []
        sectionNames = []
        sectionDivs = []
        sectionCount = 0
        totalSecs = len(reportSection)-1
        for i,section in enumerate(reportSection):
            class_attr = section.css('::attr(class)').get()
            if class_attr == 'col-md-12':
                if sectionCount > 0:
                    sectionIterator.append(sectionDivs)
                    sectionDivs = []
                sectionNames.append(section.xpath('./h3/text()').get())
                sectionCount += 1
            else:
                sectionDivs.append(section)
            if i == totalSecs:
                sectionIterator.append(sectionDivs)
                del sectionDivs
        sectionsContent = []
        for i,section in enumerate(sectionIterator):
            sectionName = ''.join(sectionNames[i].strip().split())
            sectionContent = [f'Download link for {sectionName}']
            for div in section:
                divName = div.xpath('.//span[@class="main-title"]/text()').get()
                divName = ' '.join(divName.strip().split())
                downloadLink = div.xpath('.//a').xpath('@href').get()
                content = f'Document : {divName}\nDownload Link : {downloadLink}'
                sectionContent.append(content)
            sectionContent = '\n'.join(sectionContent)
            sectionsContent.append(sectionContent)
        sectionsContent = '\n\n'.join(sectionsContent)
        pageContent = f'{title}\n\n{sectionsContent}'

        yield {
            'Page Source' : response.url,
            'Content' : pageContent
        }
    
    def parse_menu(self, response):
        # working parser for 5 type of pages with menu type structure

        title = response.url.replace(f'{self.start_urls[0]}/','')
        menu = response.xpath('//div[contains(@class, "services-list")]/div')
        # print(f'\n\n{title}\n\t{len(menu)}')
        menuContent = []
        for element in menu:
            elementLink = element.xpath('./a').xpath('@href').get()
            elementName = element.xpath('.//span[@class="main-title"]/text()').get()
            elementDescription = element.xpath('.//span[@class="description"]/text()').get()
            elementName = ' '.join(elementName.strip().split())
            elementDescription = ' '.join(elementDescription.strip().split())
            content = f'Service name : {elementName}\nService Description : {elementDescription}\nService Link : {elementLink}'
            menuContent.append(content)
        menuContent = '\n\n'.join(menuContent)
        pageContent = f'Services under category : {title}\n\n{menuContent}'
        yield {
            'Page Source' : response.url,
            'Content' : pageContent
        }
