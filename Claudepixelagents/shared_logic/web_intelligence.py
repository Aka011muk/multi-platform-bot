"""
Web Intelligence Module
Веб-скрапинг, поиск данных и AI-анализ для ресторанных ботов
"""

import asyncio
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse

# Опциональные импорты
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class WebSearchEngine:
    """Поисковая система для ресторанной информации"""
    
    def __init__(self, search_api_key: str = None):
        self.search_api_key = search_api_key
        self.session = None
    
    async def initialize(self):
        """Инициализация HTTP сессии"""
        if AIOHTTP_AVAILABLE:
            self.session = aiohttp.ClientSession()
        else:
            print("Warning: aiohttp not available, web search limited")
    
    async def search_restaurant_info(self, restaurant_name: str, city: str = "") -> Dict[str, Any]:
        """Поиск информации о ресторане"""
        search_query = f"{restaurant_name} ресторан {city} меню цены отзывы"
        
        if self.search_api_key:
            return await self.search_with_api(search_query)
        else:
            return await self.search_with_duckduckgo(search_query)
    
    async def search_with_api(self, query: str) -> Dict[str, Any]:
        """Поиск с использованием API"""
        # Пример для Google Custom Search API или Bing Search API
        url = f"https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.search_api_key,
            "cx": "your_search_engine_id",
            "q": query,
            "num": 10
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                return self.process_search_results(data)
        except Exception as e:
            print(f"API search error: {e}")
            return {}
    
    async def search_with_duckduckgo(self, query: str) -> Dict[str, Any]:
        """Поиск через DuckDuckGo (бесплатно)"""
        if not REQUESTS_AVAILABLE:
            print("Warning: requests not available, search limited")
            return {"results": []}
            
        url = "https://duckduckgo.com/html/"
        params = {"q": query}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            html = response.text
            return self.parse_duckduckgo_results(html)
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return {}
    
    def parse_duckduckgo_results(self, html: str) -> Dict[str, Any]:
        """Парсинг результатов DuckDuckGo"""
        if not BS4_AVAILABLE:
            print("Warning: BeautifulSoup not available, parsing limited")
            return {"results": []}
            
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        for result in soup.find_all('div', class_='result'):
            title_elem = result.find('a', class_='result__a')
            snippet_elem = result.find('a', class_='result__snippet')
            
            if title_elem and snippet_elem:
                results.append({
                    "title": title_elem.get_text(),
                    "url": title_elem.get('href'),
                    "snippet": snippet_elem.get_text()
                })
        
        return {"results": results}
    
    def process_search_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка результатов поиска"""
        processed = {
            "restaurant_info": {},
            "menu_items": [],
            "prices": [],
            "reviews": [],
            "contacts": []
        }
        
        # Анализ результатов и извлечение информации
        for item in data.get("items", []):
            title = item.get("title", "").lower()
            snippet = item.get("snippet", "").lower()
            
            if "меню" in title or "menu" in title:
                processed["menu_items"].append({
                    "source": item.get("link"),
                    "title": item.get("title"),
                    "snippet": item.get("snippet")
                })
            
            if "цена" in title or "price" in title or "$" in snippet:
                processed["prices"].append({
                    "source": item.get("link"),
                    "info": item.get("snippet")
                })
            
            if "отзыв" in title or "review" in title:
                processed["reviews"].append({
                    "source": item.get("link"),
                    "info": item.get("snippet")
                })
        
        return processed
    
    async def close(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()

class WebScraper:
    """Веб-скрапер для ресторанных сайтов"""
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def initialize(self):
        """Инициализация сессии"""
        self.session = aiohttp.ClientSession(headers=self.headers)
    
    async def scrape_restaurant_website(self, url: str) -> Dict[str, Any]:
        """Сбор информации с сайта ресторана"""
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                return self.extract_restaurant_data(html, url)
        except Exception as e:
            print(f"Scraping error for {url}: {e}")
            return {}
    
    def extract_restaurant_data(self, html: str, base_url: str) -> Dict[str, Any]:
        """Извлечение данных из HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        data = {
            "name": self.extract_restaurant_name(soup),
            "description": self.extract_description(soup),
            "menu": self.extract_menu(soup, base_url),
            "prices": self.extract_prices(soup),
            "contacts": self.extract_contacts(soup),
            "working_hours": self.extract_working_hours(soup),
            "features": self.extract_features(soup)
        }
        
        return data
    
    def extract_restaurant_name(self, soup: BeautifulSoup) -> str:
        """Извлечение названия ресторана"""
        # Поиск в разных местах
        selectors = [
            'h1',
            '.restaurant-name',
            '.title',
            'title',
            '[class*="restaurant"]',
            '[class*="name"]'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                name = elem.get_text().strip()
                if len(name) > 2 and len(name) < 100:
                    return name
        
        return ""
    
    def extract_description(self, soup: BeautifulSoup) -> str:
        """Извлечение описания"""
        selectors = [
            '.description',
            '.about',
            '[class*="desc"]',
            'meta[name="description"]'
        ]
        
        for selector in selectors:
            if selector.startswith('meta'):
                elem = soup.select_one(selector)
                if elem:
                    return elem.get('content', '').strip()
            else:
                elem = soup.select_one(selector)
                if elem:
                    desc = elem.get_text().strip()
                    if len(desc) > 20:
                        return desc
        
        return ""
    
    def extract_menu(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Извлечение меню"""
        menu_items = []
        
        # Поиск секций меню
        menu_sections = soup.find_all(['div', 'section'], class_=re.compile(r'menu|dish|food'))
        
        for section in menu_sections:
            dishes = section.find_all(['li', 'div', 'p'])
            
            for dish in dishes:
                text = dish.get_text().strip()
                if len(text) > 3 and len(text) < 200:
                    # Попытка извлечь цену
                    price_match = re.search(r'(\d+[\d\s]*[₽$€]?)', text)
                    price = price_match.group(1) if price_match else ""
                    
                    name = text
                    if price:
                        name = text.replace(price, "").strip()
                    
                    menu_items.append({
                        "name": name,
                        "price": price,
                        "description": text
                    })
        
        return menu_items[:20]  # Ограничение количества
    
    def extract_prices(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Извлечение ценовой информации"""
        prices = []
        
        # Поиск цен
        price_elements = soup.find_all(text=re.compile(r'\d+[\d\s]*[₽$€]'))
        
        for price_text in price_elements:
            price = price_text.strip()
            if len(price) > 0:
                parent = price_text.parent
                context = parent.get_text().strip() if parent else ""
                
                prices.append({
                    "price": price,
                    "context": context
                })
        
        return prices[:15]
    
    def extract_contacts(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Извлечение контактной информации"""
        contacts = {}
        
        # Телефон
        phone_patterns = [
            r'[\+]?[78][-\s]?[(]?[0-9]{3}[)]?[-\s]?[0-9]{3}[-\s]?[0-9]{2}[-\s]?[0-9]{2}',
            r'\+?[1-9][\d\s]{7,14}'
        ]
        
        for pattern in phone_patterns:
            phones = soup.find_all(text=re.compile(pattern))
            if phones:
                contacts["phone"] = phones[0].strip()
                break
        
        # Email
        email_elem = soup.find('a', href=re.compile(r'mailto:'))
        if email_elem:
            contacts["email"] = email_elem.get('href').replace('mailto:', '')
        
        # Адрес
        address_patterns = [
            r'[А-Я][а-я]+,\s*[уулд]\.\s*\d+',
            r'[А-Я][а-я]+\s+улица\s*\d+',
            r'[A-Z][a-z]+,\s*[A-Z][a-z]*\s*\d+'
        ]
        
        for pattern in address_patterns:
            addresses = soup.find_all(text=re.compile(pattern))
            if addresses:
                contacts["address"] = addresses[0].strip()
                break
        
        return contacts
    
    def extract_working_hours(self, soup: BeautifulSoup) -> List[str]:
        """Извлечение часов работы"""
        hours = []
        
        # Поиск часов работы
        hours_patterns = [
            r'\d{1,2}[:]\d{2}\s*[-—]\s*\d{1,2}[:]\d{2}',
            r'с\s*\d{1,2}[:]\d{2}\s*до\s*\d{1,2}[:]\d{2}',
            r'ежедневно\s*с\s*\d{1,2}'
        ]
        
        for pattern in hours_patterns:
            hours_elements = soup.find_all(text=re.compile(pattern, re.IGNORECASE))
            for elem in hours_elements:
                hours_text = elem.strip()
                if len(hours_text) > 5:
                    hours.append(hours_text)
        
        return hours[:5]
    
    def extract_features(self, soup: BeautifulSoup) -> List[str]:
        """Извлечение особенностей ресторана"""
        features = []
        
        # Ключевые слова
        feature_keywords = [
            'банкет', 'фуршет', 'доставка', 'бронирование', 'терраса',
            'летняя веранда', 'караоке', 'живая музыка', 'wi-fi', 'парковка',
            'детское меню', 'бизнес-ланч', 'завтрак', 'десерты'
        ]
        
        page_text = soup.get_text().lower()
        
        for keyword in feature_keywords:
            if keyword in page_text:
                features.append(keyword.title())
        
        return features
    
    async def close(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()

class RestaurantDataIntegrator:
    """Интегратор данных о ресторанах"""
    
    def __init__(self, search_api_key: str = None):
        self.search_engine = WebSearchEngine(search_api_key)
        self.scraper = WebScraper()
        self.ai_analyzer = AIAnalyzer()
    
    async def initialize(self):
        """Инициализация компонентов"""
        await self.search_engine.initialize()
        await self.scraper.initialize()
        await self.ai_analyzer.initialize()
    
    async def get_comprehensive_restaurant_data(self, restaurant_name: str, city: str = "") -> Dict[str, Any]:
        """Получение полной информации о ресторане"""
        print(f"🔍 Поиск данных о ресторане: {restaurant_name}")
        
        # 1. Поиск в интернете
        search_results = await self.search_engine.search_restaurant_info(restaurant_name, city)
        
        # 2. Скрапинг сайтов
        scraped_data = {}
        for result in search_results.get("results", [])[:3]:
            url = result.get("url", "")
            if url and url.startswith(('http://', 'https://')):
                scraped_data[url] = await self.scraper.scrape_restaurant_website(url)
        
        # 3. AI-анализ и интеграция
        integrated_data = await self.ai_analyzer.analyze_and_integrate(
            restaurant_name, search_results, scraped_data
        )
        
        return integrated_data
    
    async def close(self):
        """Закрытие компонентов"""
        await self.search_engine.close()
        await self.scraper.close()
        await self.ai_analyzer.close()

class AIAnalyzer:
    """AI-анализатор данных"""
    
    def __init__(self):
        self.session = None
    
    async def initialize(self):
        """Инициализация"""
        self.session = aiohttp.ClientSession()
    
    async def analyze_and_integrate(self, restaurant_name: str, search_results: Dict, scraped_data: Dict) -> Dict[str, Any]:
        """AI-анализ и интеграция данных"""
        
        integrated = {
            "restaurant_name": restaurant_name,
            "basic_info": self.extract_basic_info(search_results, scraped_data),
            "menu_analysis": self.analyze_menu_data(search_results, scraped_data),
            "price_analysis": self.analyze_pricing(search_results, scraped_data),
            "reputation": self.analyze_reputation(search_results),
            "recommendations": self.generate_recommendations(search_results, scraped_data),
            "last_updated": datetime.now().isoformat()
        }
        
        return integrated
    
    def extract_basic_info(self, search_results: Dict, scraped_data: Dict) -> Dict[str, Any]:
        """Извлечение базовой информации"""
        info = {
            "name": "",
            "description": "",
            "cuisine_type": "",
            "contacts": {},
            "working_hours": []
        }
        
        # Из скрапированных данных
        for url, data in scraped_data.items():
            if data.get("name"):
                info["name"] = data["name"]
                break
        
        if not info["name"]:
            # Из результатов поиска
            for result in search_results.get("results", []):
                title = result.get("title", "")
                if "ресторан" in title.lower():
                    info["name"] = title.replace("ресторан", "").strip()
                    break
        
        return info
    
    def analyze_menu_data(self, search_results: Dict, scraped_data: Dict) -> Dict[str, Any]:
        """Анализ меню"""
        menu_analysis = {
            "popular_dishes": [],
            "price_ranges": {},
            "cuisine_specialties": [],
            "menu_structure": {}
        }
        
        all_menu_items = []
        for data in scraped_data.values():
            all_menu_items.extend(data.get("menu", []))
        
        # Анализ ценовых диапазонов
        prices = []
        for item in all_menu_items:
            price_text = item.get("price", "")
            price_match = re.search(r'(\d+)', price_text)
            if price_match:
                prices.append(int(price_match.group(1)))
        
        if prices:
            menu_analysis["price_ranges"] = {
                "min": min(prices),
                "max": max(prices),
                "average": sum(prices) / len(prices)
            }
        
        return menu_analysis
    
    def analyze_pricing(self, search_results: Dict, scraped_data: Dict) -> Dict[str, Any]:
        """Анализ ценообразования"""
        pricing = {
            "average_check": "",
            "price_category": "",
            "special_offers": []
        }
        
        # Извлечение информации о ценах
        all_prices = []
        for data in scraped_data.values():
            all_prices.extend(data.get("prices", []))
        
        if all_prices:
            # Определение средней цены чека
            numeric_prices = []
            for price_info in all_prices:
                price_text = price_info.get("price", "")
                price_match = re.search(r'(\d+)', price_text)
                if price_match:
                    numeric_prices.append(int(price_match.group(1)))
            
            if numeric_prices:
                avg_price = sum(numeric_prices) / len(numeric_prices)
                pricing["average_check"] = f"{int(avg_price)} ₽"
                
                # Категория цен
                if avg_price < 500:
                    pricing["price_category"] = "эконом"
                elif avg_price < 1500:
                    pricing["price_category"] = "средний"
                else:
                    pricing["price_category"] = "премиум"
        
        return pricing
    
    def analyze_reputation(self, search_results: Dict) -> Dict[str, Any]:
        """Анализ репутации"""
        reputation = {
            "rating_summary": "",
            "common_feedback": [],
            "review_count": 0
        }
        
        reviews = search_results.get("reviews", [])
        reputation["review_count"] = len(reviews)
        
        # Анализ отзывов
        positive_keywords = ["отлично", "хорошо", "вкусно", "красиво", "уютно"]
        negative_keywords = ["плохо", "дорого", "медленно", "грязно"]
        
        positive_count = 0
        negative_count = 0
        
        for review in reviews:
            text = review.get("info", "").lower()
            
            for keyword in positive_keywords:
                if keyword in text:
                    positive_count += 1
                    break
            
            for keyword in negative_keywords:
                if keyword in text:
                    negative_count += 1
                    break
        
        if positive_count > negative_count:
            reputation["rating_summary"] = "Преимущественно положительные отзывы"
        elif negative_count > positive_count:
            reputation["rating_summary"] = "Есть негативные отзывы"
        else:
            reputation["rating_summary"] = "Смешанные отзывы"
        
        return reputation
    
    def generate_recommendations(self, search_results: Dict, scraped_data: Dict) -> List[str]:
        """Генерация рекомендаций для бота"""
        recommendations = []
        
        # Анализ данных и рекомендации
        menu_items_count = sum(len(data.get("menu", [])) for data in scraped_data.values())
        
        if menu_items_count > 0:
            recommendations.append("Добавить интерактивное меню с фильтрацией")
        
        if any(data.get("contacts") for data in scraped_data.values()):
            recommendations.append("Настроить кнопки быстрой связи")
        
        if search_results.get("reviews"):
            recommendations.append("Добавить раздел с отзывами")
        
        recommendations.extend([
            "Интегрировать онлайн-бронирование",
            "Добавить акции и специальные предложения",
            "Настроить персонализированные рекомендации"
        ])
        
        return recommendations
    
    async def close(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
