from config import config
from utils import HeadHunter, DBManager


def main():
    hh = HeadHunter(['3529', '78638', '1740', '2748', '2180',
                     '4352', '3501302', '15478', '6041', '4759512'])
    params = config()
    hh_vac = hh.get_api()

    while True:
        try:
            user_ans = int(input("""Выберите одно из следующих действий:
            1 - Все вакансии;
            2 - Все вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию;
            3 - Средняя зарплата по вакансиям;
            4 - Все вакансий, у которых зарплата выше средней по всем вакансиям;
            5 - Все вакансий, в названии которых содержатся переданные в метод слова;
            0 - Выйти;
            """))

            database = DBManager(hh_vac)
            database.create_database(hh_vac, 'HH_Vacancy', params)

            if user_ans == 1:
                answer_1 = database.get_companies_and_vacancies_count()
                for answer in answer_1:
                    print(*answer)
                break
            elif user_ans == 2:
                answer_2 = database.get_all_vacancies()
                for answer in answer_2:
                    print(*answer)
                break
            elif user_ans == 3:
                answer_3 = database.get_avg_salary()
                for answer in answer_3:
                    print(*answer)
                break
            elif user_ans == 4:
                answer_4 = database.get_vacancies_with_higher_salary()
                for answer in answer_4:
                    print(*answer)
                break
            elif user_ans == 5:
                answer_5 = database.get_vacancies_with_keyword()
                for answer in answer_5:
                    print(*answer)
                break
            elif user_ans == 0:
                break
            else:
                print("Введите цифру")
                break
        except ValueError:
            print("Возникла ошибка. Попробуйте снова.")
            break


if __name__ == '__main__':
    main()
