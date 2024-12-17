import pytest
from scrapy.http import HtmlResponse, Request
from scrapy.spiders import Spider
from unittest.mock import Mock
from hotel_scraper.middlewares import HotelScraperSpiderMiddleware, HotelScraperDownloaderMiddleware


@pytest.fixture
def spider():
    """Provide a mock spider with a name attribute."""
    mock_spider = Mock(spec=Spider)
    mock_spider.name = "test_spider"
    return mock_spider


def test_spider_middleware_process_spider_input(spider):
    """Test process_spider_input of HotelScraperSpiderMiddleware."""
    middleware = HotelScraperSpiderMiddleware()
    response = HtmlResponse(url="https://example.com")
    
    # Call process_spider_input
    result = middleware.process_spider_input(response, spider)
    
    # Assert it returns None (default behavior)
    assert result is None


def test_spider_middleware_process_spider_output(spider):
    """Test process_spider_output of HotelScraperSpiderMiddleware."""
    middleware = HotelScraperSpiderMiddleware()
    response = HtmlResponse(url="https://example.com")
    result = ["item1", "item2"]
    
    # Call process_spider_output
    output = list(middleware.process_spider_output(response, result, spider))
    
    # Assert it yields the result items
    assert output == result


def test_spider_middleware_process_spider_exception(spider):
    """Test process_spider_exception of HotelScraperSpiderMiddleware."""
    middleware = HotelScraperSpiderMiddleware()
    response = HtmlResponse(url="https://example.com")
    exception = Exception("Test exception")
    
    # Call process_spider_exception
    result = middleware.process_spider_exception(response, exception, spider)
    
    # Assert it returns None (default behavior)
    assert result is None


def test_downloader_middleware_process_request(spider):
    """Test process_request of HotelScraperDownloaderMiddleware."""
    middleware = HotelScraperDownloaderMiddleware()
    request = Request(url="https://example.com")
    
    # Call process_request
    result = middleware.process_request(request, spider)
    
    # Assert it returns None (default behavior)
    assert result is None


def test_downloader_middleware_process_response(spider):
    """Test process_response of HotelScraperDownloaderMiddleware."""
    middleware = HotelScraperDownloaderMiddleware()
    request = Request(url="https://example.com")
    response = HtmlResponse(url="https://example.com")
    
    # Call process_response
    result = middleware.process_response(request, response, spider)
    
    # Assert it returns the response object
    assert result == response


def test_downloader_middleware_process_exception(spider):
    """Test process_exception of HotelScraperDownloaderMiddleware."""
    middleware = HotelScraperDownloaderMiddleware()
    request = Request(url="https://example.com")
    exception = Exception("Test exception")
    
    # Call process_exception
    result = middleware.process_exception(request, exception, spider)
    
    # Assert it returns None (default behavior)
    assert result is None


def test_spider_opened_signal_spider_middleware(spider):
    """Test spider_opened signal handling in HotelScraperSpiderMiddleware."""
    middleware = HotelScraperSpiderMiddleware()
    
    # Mock the spider logger
    spider.logger = Mock()
    
    # Call spider_opened
    middleware.spider_opened(spider)
    
    # Assert the spider logger is called with the correct message
    spider.logger.info.assert_called_with(f"Spider opened: {spider.name}")


def test_spider_opened_signal_downloader_middleware(spider):
    """Test spider_opened signal handling in HotelScraperDownloaderMiddleware."""
    middleware = HotelScraperDownloaderMiddleware()
    
    # Mock the spider logger
    spider.logger = Mock()
    
    # Call spider_opened
    middleware.spider_opened(spider)
    
    # Assert the spider logger is called with the correct message
    spider.logger.info.assert_called_with(f"Spider opened: {spider.name}")
