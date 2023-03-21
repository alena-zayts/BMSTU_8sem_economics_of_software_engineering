"""
Исследовать влияние характеристик атрибутов программного проекта
(MODP, TOOL) на трудоемкость (РМ) и время разработки проекта
(ТМ) для базового уровня модели COCOMO и разных типов проектов
(обычного, встроенного, промежуточного). Для этого получить
значения PM и ТМ по всем типам проектов для одного и того же
значения параметра SIZE (размера программного кода) при изменении
значений атрибутов проекта от низких до высоких. Проанализировать
как повлияет на трудоемкость и время реализации проекта внесение
дополнительных ограничений на требуемые сроки разработки
(параметр SCED). Результаты исследований оформить графически и
сделать соответствующие выводы.
"""

"""
Трудозатраты = С1 * EAF * (Размер)^p1 (количество человеко-месяцев)

C1 - масштабируемый коэффициент
EAF - уточняющий фактор, хар-ий предметную область/персонал/среду/инструментарий, 
используемый для создания рабочих продуктов процесса
Размер - размер конечного продукта (кода, созданного человеком)
p1 - показатель степени, хар-ий экономию при больших масштабах, присущую тому 
процессу, который используется для создания конечного продукта; 
в частности, способность процесса избегать непроизводительных видов 
деятельности (доработок, бюрократических проволочек, накладных расходов)

Время = С2 * (Трудозатраты)^p2 (общее количество месяцев)

С2 - масштабирующий коэффициент для сроков исполнения
Р2 - показатель степени, характеризует инерцию и распараллеливание, присущие 
управлению разработкой ПО
"""
from typing import List, Dict, Tuple
from copy import deepcopy
import matplotlib.pyplot as plt
import math


NUM_LEVELS = 5
SIZE = 100

# Типы проектов
NORMAL = {'c1': 3.2, 'p1': 1.05, 'c2': 2.5, 'p2': 0.38}  # Обычный вариант - некрупный проект, нет нововведений, всё знакомо
INTER = {'c1': 3.0, 'p1': 1.12, 'c2': 2.5, 'p2': 0.35}  # Промежуточный вариант - средний проект, есть инновации
BUILDIN = {'c1': 2.8, 'p1': 1.2, 'c2': 2.5, 'p2': 0.32}  # Встроенный вариант - крупный проект, значительный объем инноваций

# Атрибуты программного продукта
RELY = [0.75, 0.86, 1.0, 1.15, 1.4]  # Требуемая надежность
DATA = [None, 0.94, 1.0, 1.08, 1.16]  # Размер БД
CPLX = [0.7, 0.85, 1.0, 1.15, 1.3]  # Сложность продукта

# Атрибуты копьютера
TIME = [None, None, 1.0, 1.11, 1.5]  # Ограничение времени выполнения
STOR = [None, None, 1.0, 1.06, 1.21]  # Ограничение объёма основной памяти
VIRT = [None, 0.87, 1.0, 1.15, 1.30]  # Изменчивость виртуальной машины
TURN = [None, 0.87, 1.0, 1.07, 1.15]  # Время реакции компьютера

# Атрибуты персонала
ACAP = [1.46, 1.19, 1.0, 0.86, 0.71]  # Способности аналитика
AEXP = [1.29, 1.15, 1.0, 0.91, 0.82]  # Знание приложений
PCAP = [1.42, 1.17, 1.0, 0.86, 0.7]   # Способности программиста
VEXP = [1.21, 1.1, 1.0, 0.9, None]    # Знание виртуальной машины
LEXP = [1.14, 1.07, 1.0, 0.95, None]  # Знание ЯП

# Атрибуты проекта
MODP = [1.24, 1.1, 1.0, 0.91, 0.82]  # Использование современных методов
TOOL = [1.24, 1.1, 1.0, 0.91, 0.82]  # Использование программных инструментов
SCED = [1.23, 1.08, 1.0, 1.04, 1.1]  # Требуемые сроки разработки

DEFAULT = {
    'RELY': RELY[2],
    'DATA': DATA[2],
    'CPLX': CPLX[2],
    'TIME': TIME[2],
    'STOR': STOR[2],
    'VIRT': VIRT[2],
    'TURN': TURN[2],
    'ACAP': ACAP[2],
    'AEXP': AEXP[2],
    'PCAP': PCAP[2],
    'VEXP': VEXP[2],
    'LEXP': LEXP[2],
    'MODP': MODP[2],
    'TOOL': TOOL[2],
    'SCED': SCED[2],
}


def getEAF(params: Dict[str, float]) -> float:
    mult = 1
    for elem in params.values():
        mult *= elem

    return mult


def getLaborCosts(c1: float, eaf: float, size: float, p1: float) -> float:
    return c1 * eaf * size ** p1


def getTime(c2: float, laborCosts: float, p2:float) -> float:
    return c2 * laborCosts ** p2


def calculate(params: Dict[str, float], variant: Dict[str, float], size: float) -> Tuple[float, float]:
    eaf = getEAF(params)
    laborCosts = getLaborCosts(variant['c1'], eaf, size, variant['p1'])
    time = getTime(variant['c2'], laborCosts, variant['p2'])

    return laborCosts, time


def process(variant: Dict[str, float], key: str, value: float, size: int):
    params = deepcopy(DEFAULT)
    params[key] = value

    return calculate(params, variant, size)


def runExperiment(params: Dict[str, float], variant: Dict[str, float], size: float, salary: int):
    res = {}
    res['laborCosts'], res['time'] = calculate(params, variant, size)

    res['planWork'] = res['laborCosts'] * 1.08
    res['planTime'] = res['time'] * 1.36

    res['planWorkSingle'] = res['laborCosts'] * 0.08
    res['planTimeSingle'] = res['time'] * 0.36
    res['planPeople'] = math.ceil(res['planWorkSingle'] / res['planTimeSingle'])

    res['designWork'] = res['laborCosts'] * 0.18
    res['designTime'] = res['time'] * 0.36
    res['designPeople'] = math.ceil(res['designWork'] / res['designTime'])

    res['detailWork'] = res['laborCosts'] * 0.25
    res['detailTime'] = res['time'] * 0.18
    res['detailPeople'] = math.ceil(res['detailWork'] / res['detailTime'])

    res['codingWork'] = res['laborCosts'] * 0.26
    res['codingTime'] = res['time'] * 0.18
    res['codingPeople'] = math.ceil(res['codingWork'] / res['codingTime'])

    res['integWork'] = res['laborCosts'] * 0.31
    res['integTime'] = res['time'] * 0.28
    res['integPeople'] = math.ceil(res['integWork'] / res['integTime'])

    res['analysis'] = 4
    res['anPeople'] = res['laborCosts'] * 0.04

    res['design'] = 12
    res['dePeople'] = res['laborCosts'] * 0.12

    res['coding'] = 44
    res['coPeople'] = res['laborCosts'] * 0.44

    res['planning'] = 6
    res['plPeople'] = res['laborCosts'] * 0.06

    res['ver'] = 14
    res['verPeople'] = res['laborCosts'] * 0.14

    res['office'] = 7
    res['ofPeople'] = res['laborCosts'] * 0.07

    res['quality'] = 7
    res['quPeople'] = res['laborCosts'] * 0.07

    res['manuals'] = 6
    res['maPeople'] = res['laborCosts'] * 0.06

    res['budget'] = res['laborCosts'] * salary

    salary = {
        "Programmer": salary,
        "Analytic": salary * 1.4,
        "Manager": salary * 1.3,
        "Tester": salary * 0.65,
    }

    budget = []
    budget += [(((salary['Manager'] + salary['Analytic']) / 2) * res['designPeople'] * res['planTimeSingle'])]
    budget += [(((salary['Programmer'] + salary['Analytic']) / 2) * res['designPeople'] * res['designTime'])]
    budget += [(((salary['Programmer'] + salary['Analytic']) / 2) * res['detailPeople'] * res['detailTime'])]
    budget += [(((salary['Programmer'] + salary['Tester']) / 2) * res['codingPeople'] * res['codingTime'])]
    budget += [(((salary['Programmer'] + salary['Tester']) / 2) * res['integPeople'] * res['integTime'])]

    s = 0
    for i in range(len(budget)):
        s += budget[i]

    allTimeInfo = [res['planTimeSingle'], res['designTime'],
                   res['detailTime'], res['codingTime'],
                   res['integTime']]
    allPeopleInfo = [res['planPeople'], res['designPeople'],
                     res['detailPeople'], res['codingPeople'],
                     res['integPeople']]

    xData, yData = [], []

    s = 0
    for i in range(len(allTimeInfo)):
        time = s
        while time < s + allTimeInfo[i]:
            xData.append(time)
            yData.append(allPeopleInfo[i])
            time += 1
        s += allTimeInfo[i]

    plt.title('Сотрудники')
    plt.grid(True)
    plt.bar(xData, yData)
    plt.xlabel("Месяцы")
    plt.ylabel("Количество сотрудников")
    plt.show()

    return res


def draw(xArr, laborSIZE, timeSIZE, ind):
    fig, axs = plt.subplots(1, 2)
    nameArr = ['простой', 'средней сложности', 'сложный']
    fig.canvas.manager.set_window_title(nameArr[ind])
    typeArr = ['обычный тип проекта', 'промежуточный тип проекта', 'встроенный тип проекта']
    colorArr = [['green', 'black', 'blue'], ['red', 'yellow', 'purple'], ['grey', 'orange', 'fuchsia']]
    axs[0].set_title('Влияние SIZE на трудоёмкость (РМ)')
    axs[0].set(ylabel="PM, количество человеко-месяцев")
    axs[0].grid()

    axs[1].set_title("Влияние SIZE на время разработки (TМ)")
    axs[1].set(ylabel="PM, количество месяцев")
    axs[1].grid()

    for i in range(3):
        axs[0].plot(xArr, laborSIZE[i], label='SIZE ' + typeArr[i], color=colorArr[i][0])
        axs[1].plot(xArr, timeSIZE[i], label='SIZE ' + typeArr[i], color=colorArr[i][0])

    axs[0].legend()
    axs[1].legend()


def doTask1():
    sizeArr = [elem for elem in range(1, 100)]

    for i, cplx in enumerate([0.7, 1.0, 1.3]):
        laborSIZE = []
        timeSIZE = []

        for variant in [NORMAL, INTER, BUILDIN]:
            laborSIZEArr = []
            timeSIZEArr = []

            for size in sizeArr:
                laborCosts, time = process(variant, 'CPLX', cplx, size)
                laborSIZEArr.append(laborCosts)
                timeSIZEArr.append(time)

            laborSIZE.append(laborSIZEArr)
            timeSIZE.append(timeSIZEArr)

        draw(sizeArr, laborSIZE, timeSIZE, i)
    plt.show()


if __name__ == '__main__':
    doTask1()

