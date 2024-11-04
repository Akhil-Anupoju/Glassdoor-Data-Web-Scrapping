import requests
from bs4 import BeautifulSoup
import os
import json
import time
import random
from datetime import datetime
import logging


class GlassdoorScraper:
    def __init__(self):
        self.base_url = "https://www.glassdoor.com"
        self.search_base_url = "https://www.glassdoor.com/Interview"
        self.company_patterns = {
            "42gears": "1358831",
            "abb": "3076",
            "accenture": "4138",
            "altran": "4317401",
            "axiscades": "942106",
            "betsol": "730260",
            "capgemini": "3803",
            "dell technologies": "1327",
            "deltax": "955507",
            "ellucian": "529143",
            "ey": "2784",
            "fidelity services group": "4924648",
            "globalsoft": "377210",
            "hashedIn by deloitte": "689428",
            "hsbc": "3482",
            "infosys": "7927",
            "jaro education": "427536",
            "jk tech": "393599",
            "l&t technology services": "394137",
            "in time tec": "484136",
            "mahindra comviva": "7004191",
            "micro focus": "15057",
            "nec corporation": "3532",
            "simeio": "233072",
            "amadeus": "6940",
            "cgi": "8452",
            "mistral": "1133892",
            "nokia": "3494",
            "persistent systems": "150639",
            "unisys": "692",
            "aryaka networks": "412515",
            "gyanSys": "286697",
            "mediakind": "2357386",
            "onedirect india": "1337171",
            "atkinsréalis": "8810",
            "eurofins": "25113",
            "harman": "315",
            "microchip": "1561340",
            "moog inc": "950",
            "optum": "2409113",
            "bosch": "4293",
            "the zebra": "1144721",
            "phonepe": "2289138",
            "lenovo": "8034",
            "planview": "33100",
            "société générale": "10350",
            "sprinklr": "427532",
            "target": "194",
            "tata consultancy services": "13461",
            "tech mahindra": "135932",
            "verifone": "1495",
            "wipro": "9936",
            "telstra": "6563",
            "goldman sachs": "2800",
            "mu sigma": "253258",
            "state street": "1911",
            "tejas": "11555",
            'google': '9079',
            'microsoft': '1651',
            'amazon': '6036',
            'apple': '1138',
            'facebook': '40772',
            'netflix': '11891',
            'ibm': '354',
            'cisco': '1425',
            'oracle': '1737',
            'intel': '1519',
            'adobe': '1090',
            'salesforce': '11159',
            'vmware': '12830',
            'intuit': '2293',
            'paypal': '9848',
            'uber': '575263',
            'x': '100569',
            'linkedin': '34865',
            'nvidia': '7633',
            'dell': '1327',
            'sap': '10471',
            'pinterest': '503467'
        }
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        ]
        self.session = self._create_session()
        self._setup_logging()
        self.saved_results_log = []  # List to store saved results log messages

    def _create_session(self):
        session = requests.Session()
        session.headers.update({
            'User-Agent': random.choice(self.user_agents)
        })
        return session

    def _setup_logging(self):
        if not os.path.exists('logs'):
            os.makedirs('logs')

        log_filename = f'logs/scraping_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s',  # Only show the message without timestamp or level
            handlers=[logging.FileHandler(log_filename), logging.StreamHandler()]
        )
        self.logger = logging.getLogger(__name__)

    def _get_company_url(self, company_name):
        company_id = self.company_patterns.get(company_name.lower().strip())
        if not company_id:
            return None
        return f"{self.search_base_url}/{company_name.capitalize()}-Interview-Questions-E{company_id}.htm"

    def _extract_reviews_from_response(self, response_text):
        questions = []
        soup = BeautifulSoup(response_text, 'html.parser')

        # Extract questions based on the specific div and p class structure
        question_elements = soup.find_all('div', class_="interview-details_interviewText__YH2ZO")

        for container in question_elements[:100]:  # Limit to first 100 questions
            question_text = container.find('p',
                                           class_="truncated-text_truncate__021Uu interview-details_textStyle__gmhSJ")
            if question_text:
                questions.append(question_text.get_text(strip=True))

        return questions

    def _save_results(self, questions, company_name):
        if not os.path.exists('results'):
            os.makedirs('results')

        filename = f'results/{company_name.lower()}_questions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=2)

        self.saved_results_log.append(f"Results saved to {filename}")  # Store log message

    def scrape_interview_questions(self, company_name):
        self.logger.info(f"Scrapping {company_name.capitalize()} data from Glassdoor!!")

        try:
            company_url = self._get_company_url(company_name)
            if not company_url:
                self.logger.error(f"Could not find URL for company: {company_name.capitalize()}")
                return [], []

            for attempt in range(5):  # Retry logic
                try:
                    self.session.headers.update({'User-Agent': random.choice(self.user_agents)})
                    response = self.session.get(company_url)

                    if response.status_code == 200:
                        questions = self._extract_reviews_from_response(response.text)
                        if questions:
                            self._save_results(questions, company_name)
                        return questions, self.saved_results_log  # Return questions and logs
                except requests.RequestException as e:
                    self.logger.error(f"Attempt {attempt + 1}: Request failed with error: {str(e)}")
                    time.sleep(random.uniform(3, 6))

            self.logger.error("Max retry attempts reached. Could not fetch data.")
            return [], []

        except Exception as e:
            self.logger.error(f"Error during scraping: {str(e)}")
            return [], []


def display_results(questions):
    if not questions:
        print("\nNo questions found for this company.")
        return

    print(f"\nFound {len(questions)} Interview Questions:")
    print("=" * 120)

    for i, question in enumerate(questions, 1):
        # Indent the whole question except for the question number
        formatted_question = question.replace('. ', '.\n    ')  # Indent subsequent sentences
        print(f"Q{i}: {formatted_question.strip()}")  # Q1: Question text
        print("    ")  # Add an extra indent line for clarity between questions

    print("-" * 120)


def ask_continue():
    """Prompt user to continue or quit after displaying questions."""
    while True:
        user_input = input("Would you like to continue with the next company? (yes/no): ").strip().lower()
        if user_input in ['yes', 'no']:
            return user_input == 'yes'  # Return True for yes, False for no
        print("Please enter 'yes' or 'no'.")


def display_available_companies(company_patterns):
    # Display companies in 4 columns
    companies = sorted([name.capitalize() for name in company_patterns.keys()])
    columns = 4
    print("\nAvailable Companies:\n" + "=" * 120)

    for i in range(0, len(companies), columns):
        row = companies[i:i + columns]
        print(" | ".join(f"{name:<30}" for name in row))  # Format with a fixed width for each column

    print("=" * 120)


def main():
    scraper = GlassdoorScraper()

    while True:
        display_available_companies(scraper.company_patterns)

        company_name = input("\nEnter the company name to scrape interview questions: ").strip()
        questions, saved_logs = scraper.scrape_interview_questions(company_name)

        display_results(questions)

        if not ask_continue():
            break

    if saved_logs:
        print("\n" + "\n".join(saved_logs))

    print("Thank you for using the HireStream Glassdoor Interview Question Scraper!")


if __name__ == "__main__":
    main()
