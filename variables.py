SITE_TO_SCRAPE = "https://resale.ajax.nl/secured/content"

site_paths = {
    "accept_button": "js-first-screen-accept-all-button",
    "continue_button": '//*[@data-test="continue-button"]',
    "books_on_page": '//*[@data-test="product-title"]',
    "title": '//*[@data-test="title"]',
    "description": '//*[@data-test="description"]',
    "author": '//*[@data-role="AUTHOR"]',
    "thumbnail": '//*[@data-test="product-main-image"]',
    "publishedDate": '//*[@id="mainContent"]/div/div[1]/div[2]/div[1]/section[6]/div/div/div[1]/div/div[1]/dl/div[3]/dd/text()',
    "genre": '//*[@data-test="breadcrumb"]/li[last()]'
}