from config import config
from utils import HeadHunter, DBManager

hh = HeadHunter(['3529', '78638', '1740', '2748', '2180',
                 '4352', '3501302', '15478', '6041', '4759512'])

params = config()
hh_vac = hh.get_api()
save = DBManager(hh_vac)
save.create_database(hh_vac, 'HH_Vacancy', params)
save.get_all_vacancies()


if __name__ == '__main__':
    print(save.get_avg_salary())
