import requests
import json
import psycopg2
from typing import Any


class HeadHunter:
    """Получение данных с HeadHunter"""
    url = 'https://api.hh.ru/vacancies'

    def __init__(self, company_id):
        self.company_id = company_id

    def get_api(self):
        vacancy_list = []
        with open('companies.json', 'w', encoding='UTF-8') as file:
            for company in self.company_id:
                response = requests.get(url=self.url, headers={"User-Agent": "Ru.Zubayr@gmail.com"},
                                        params={'page': None, 'per_page': 10, 'employer_id': company})
                for item in response.json()['items']:
                    company = item['employer']['id']
                    company_name = item['employer']['name']
                    company_url = item['employer']['alternate_url']
                    vac_name = item['name']
                    vac_city = item['area']['name']
                    if item['salary'] is None:
                        salary_from = 0
                        salary_to = 0
                    else:
                        salary_from = item['salary']['from']
                        if salary_from is None:
                            salary_from = 0
                        else:
                            salary_from = salary_from
                        salary_to = item['salary']['to']
                        if salary_to is None:
                            salary_to = 0
                        else:
                            salary_to = salary_to
                    vac_url = item['alternate_url']
                    dict_vac = {
                        'company_id': company,
                        'company_name': company_name,
                        'company_url': company_url,
                        'vacancy_name': vac_name,
                        'vacancy_city': vac_city,
                        'salary_from': salary_from,
                        'salary_to': salary_to,
                        'vacancy_url': vac_url
                    }
                    vacancy_list.append(dict_vac)
            json.dump(vacancy_list, file, ensure_ascii=False, indent=4)
        with open('companies.json', 'r', encoding='UTF-8') as file:
            data = json.load(file)
        return data


class DBManager:
    """Класс для работы с базой данных"""

    def __init__(self, vacancy, keyword=None) -> None:
        self.vacancy = vacancy
        self.keyword = keyword

    def create_database(self, data: list[dict[str, Any]], database_name: str, params: dict) -> None:
        """Создание базы данных и таблиц для сохранения данных о канале"""

        conn = psycopg2.connect(dbname='HH_Vacancy', **params)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(f'DROP DATABASE {database_name}')
        cur.execute(f'CREATE DATABASE {database_name}')

        cur.close()
        conn.close()

        conn = psycopg2.connect(dbname=database_name, **params)
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS company
                (
                    company_id SERIAL PRIMARY KEY,
                    company_name varchar NOT NULL,
                    company_url varchar NOT NULL
                );
                CREATE TABLE IF NOT EXISTS vacancy
                (
                    vacancy_id SERIAL PRIMARY KEY,
                    vacancy_name varchar NOT NULL,
                    vacancy_city varchar,
                    salary_from int,
                    salary_to int,
                    vacancy_url varchar NOT NULL,
                    company_vacancy int REFERENCES company(company_id)
                )
                """)

            for data_vacancy in data:
                cur.execute("INSERT INTO company VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                            (data_vacancy['company_id'],
                             data_vacancy['company_name'],
                             data_vacancy['company_url']))
                cur.execute("INSERT INTO vacancy"
                            '(vacancy_name, vacancy_city, salary_from, salary_to, '
                            'vacancy_url, company_vacancy)'
                            ' VALUES (%s, %s, %s, %s, %s, %s)',
                            (
                                data_vacancy['vacancy_name'],
                                data_vacancy['vacancy_city'],
                                data_vacancy['salary_from'],
                                data_vacancy['salary_to'],
                                data_vacancy['vacancy_url'],
                                data_vacancy['company_id']))
        conn.close()

    def get_companies_and_vacancies_count(self):
        """Получаем список всех компаний и количество вакансий у каждой компании"""

        with psycopg2.connect(
            host='localhost',
            database='HH_Vacancy',
            user='postgres',
            password=1111
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                            SELECT company_name, COUNT(*)  AS count_vacancy FROM company
                            INNER JOIN vacancy ON vacancy.company_vacancy=company.company_id
                            GROUP BY company_name
                """)
                raws = cur.fetchall()
        cur.close()
        return raws

    def get_all_vacancies(self):
        """Получаем список всех вакансий с указанием названия компании,
         названия вакансии, зарплаты и ссылки на вакансию"""

        with psycopg2.connect(
                host='localhost',
                database='HH_Vacancy',
                user='postgres',
                password=1111
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT vacancy_name, company_name, salary_from, salary_to, vacancy_url
                FROM company, vacancy
                WHERE company_id = company_vacancy""")

                raws = cur.fetchall()
        cur.close()
        return raws

    def get_avg_salary(self):
        """Получаем среднюю зарплату по вакансиям"""
        with psycopg2.connect(
                host='localhost',
                database='HH_Vacancy',
                user='postgres',
                password=1111
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT round(AVG((salary_from + salary_to)/2)) 
                            FROM vacancy""")

                raws = cur.fetchall()
        cur.close()
        return raws

    def get_vacancies_with_higher_salary(self):
        """Получаем список всех вакансий, у которых зарплата выше средней по всем вакансиям"""
        with psycopg2.connect(
                host='localhost',
                database='HH_Vacancy',
                user='postgres',
                password=1111
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT vacancy_name, (salary_from + salary_to)/2 AS salary
                            FROM vacancy
                            WHERE (salary_from + salary_to)/2 > 
                            (SELECT round(AVG((salary_from + salary_to)/2)) FROM vacancy)
                            ORDER BY salary DESC""")

                raws = cur.fetchall()
        cur.close()
        return raws

    def get_vacancies_with_keyword(self):
        """Получаем список всех вакансий, в названии которых
        содержатся переданные в метод слова, например python"""
        with psycopg2.connect(
                host='localhost',
                database='HH_Vacancy',
                user='postgres',
                password=1111
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(f"""SELECT vacancy_name, vacancy_city, vacancy_url
                            FROM vacancy
                            WHERE lower(vacancy_name) LIKE '%{self.keyword}%""")

                raws = cur.fetchall()
        cur.close()
        return raws
