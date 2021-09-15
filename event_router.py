import db_handler as dh
import time
import hashlib

# Функция генерации пользовательского токена для сессии
# user_login - логин пользователя
def generateUserToken(user_login):
    # Проверяем если пользователь существует
    if (dh.isUserExist(user_login)):
        # Достаём ID пользователя
        user_id = dh.getUserData(user_login)[0]
        # Генерируем хэши для логина и ID 
        h1 = hashlib.md5(str(user_id).encode('utf-8'))
        h2 = hashlib.md5(str(user_login).encode('utf-8'))
        # Объединяем в один токен
        token = h1.hexdigest() + h2.hexdigest()
        # Возвращаем токен
        return token
    else:
        # Иначе возвращаем None
        return "None"

# Функция для проверки соответствия пользовательских токенов
# userToken - пользовательский токен из сессии
# userLogin - логин пользователя из сессии
def checkUserTokens(userToken, userLogin):
    # Проверяем если пользователь существует
    if (dh.isUserExist(userLogin)):
        # Получаем информацию о пользователе по его логину
        userData = dh.getUserData(userLogin)
        # Генерируем токен на основе данных из БД
        checkToken = generateUserToken(userData[2])
        # Проверяем совпадение токенов
        if checkToken == userToken:
            # Если совпали, возвращаем True
            return True
        else:
            # Если не совпали, возвращаем False
            return False
    else:
        # Возвращаем False, пользователя не существует
        return False

# Функцция для запроса верификации
# user_login - логин пользователя
def askForVerify(user_login):
    # Обращаемся к БД для запроса верификации
    dh.addVerifyAsk(user_login)

# Функция для подтверждения верификации пользователя
# user_login - логин пользователя
def verificateUser(user_login):
    user = dh.getUserData(user_login)
    userID = dh.getUserLink(user[0])
    userData = dh.getDataByUser(user[4], userID)
    if userData['type'] == 'student':
        if userData['studentData'][1] is None or userData['studentData'][3] is None or userData['studentData'][5] is None or userData['studentData'][6] is None:
            dh.setVerificationStatus(user_login, "declined", False)
            return
        if userData['contactsData'][1] is None or userData['contactsData'][2] is None:
            dh.setVerificationStatus(user_login, "declined", False)
            return
        if userData['profData'][1] is None:
            dh.setVerificationStatus(user_login, "declined", False)
            return

        dh.setVerificationStatus(user_login, "verified", True)
    elif userData['type'] == 'employer':
        if userData['emplData'][1] is None:
            dh.setVerificationStatus(user_login, "declined", False)
            return
        if userData['contactsData'][1] is None or userData['contactsData'][2] is None:
            dh.setVerificationStatus(user_login, "declined", False)
            return
        if userData['profData'][1] is None:
            dh.setVerificationStatus(user_login, "declined", False)
            return
        if userData['workplaceData']['workplaceData'][1] is None:
            dh.setVerificationStatus(user_login, "declined", False)
            return
        if userData['workplaceData']['locationData'][1] is None or userData['workplaceData']['locationData'][2] is None or userData['workplaceData']['locationData'][3] is None: 
            dh.setVerificationStatus(user_login, "declined", False)
            return
        if userData['workplaceData']['contactsData'][1] is None or userData['workplaceData']['contactsData'][2] is None:
            dh.setVerificationStatus(user_login, "declined", False)
            return
        if userData['workplaceData']['emplData'][1] is None:
            dh.setVerificationStatus(user_login, "declined", False)
            return
        
        dh.setVerificationStatus(user_login, "verified", True)

# Функция для получения списка студентов по поисковому тексту запроса
# searchText - текст поиска 
def getStudentsBySearch(searchText):
    # Получаем список всех студентов
    temp = dh.getAllStudents()
    # Инициализируем выходной массив
    output = []
    # Проходимся по всему списку студентов
    for line in temp:
        # Получаем полную информацию о каждом студенте
        user = dh.getStudentFullInfo(line[0])
        # Ищем совпадения в данных студента
        if str(searchText.lower()) in { str(user['studentData'][1]).lower(), str(user['studentData'][3]).lower(), str(user['studentData'][5]).lower(), str(user['studentData'][6]).lower(), str(user['contactsData'][1]).lower(), str(user['contactsData'][2]).lower(), str(user['profData'][1]).lower() }:
            # Если нашли совпадения, добавляем студента в выходной массив
            output.append(user['studentData'])
    # Возвращаем выделенную информацию 
    return output

# Функция получения информации о работодателях при помощи поиска
# searchText - текст поиска
def getEmployersBySearch(searchText):
    # Получения информации о всех работодателях
    temp = dh.getAllEmployersWithExtra()
    # Инициализация выходного массива
    output = []
    # Проходимся по всем работодателям
    for line in temp:
        # Получаем полную информацию о работодателе
        user = dh.getEmployerFullInfo(line[0])
        # Обрабатываем на совпадения в данных работодателя
        if str(searchText.lower()) in { str(user['emplData'][1]).lower(), str(user['contactsData'][1]).lower(), str(user['contactsData'][2]).lower(), str(user['profData'][1]).lower() }:
            # Если нашли совпадения - добавляем в выходной массив
            output.append(line)
    # Возвращаем выходной массив по вызову функции
    return output

# Функция получения списка мест для практики при помощи поиска
# searchText - текст поиска
def getWorkplacesBySearch(searchText):
    # Получаем список всех мест для практики 
    temp = dh.getAllWorkplacesWithExtra()
    # Инициализация выходного массива
    output = []
    # Проходимся по всем местам для практики
    for line in temp:
        # Получаем полную информацию о месте практики
        user = dh.getWorkplaceFullInfo(line[0])
        # Ищем совпадения в данных по фильтру поиска
        if str(searchText.lower()) in { str(user['workplaceData'][1]).lower(), str(user['contactsData'][1]).lower(), str(user['contactsData'][2]).lower(), str(user['locationData'][1]).lower(), str(user['locationData'][2]).lower(), str(user['locationData'][3]).lower(), str(user['locationData'][4]).lower(), str(user['locationData'][5]).lower(), str(user['emplData'][1]).lower() }:
            # Если нашлись совпадения, добавляем место для практики в выходной массив
            output.append(line)
    # Возвращаем информацию по вызову функции
    return output
    
# Функция для получения мест для практики по фильтру
# filter - тип критерия
def getWorkplacesByFilter(filter):
    # Получаем информацию о месте практики
    temp = dh.getAllWorkplacesWithExtra()
    # Инициализируем выходной массив
    output = []
    # Обрабатываем все места для практики
    for line in temp:
        # Получаем полную информацию о месте практики
        user = dh.getWorkplaceFullInfo(line[0])
        # Ищем на совпадения по фильтру города
        if (user['locationData'][2]).lower() == str(filter).lower():
            # Если нашли, добавляем в выходной список
            output.append(line)
    # Возвращаем список
    return output

# Функция для получения всех доступных городов из базы данных
def getWorkplacesCities():
    # Получаем информацию о всех рабочих местах 
    data = dh.getAllWorkplaces()    
    # Инициализируем выходной массив
    output = []
    # Обрабатываем каждое место для практики
    for line in data:
        # Получаем полную информацию о месте практики
        user = dh.getWorkplaceFullInfo(line[0])
        # Если совпадение по городу и мы его ещё не добавили, то добавляем
        if user['locationData'][2] and user['locationData'][2] not in output:
            output.append(user['locationData'][2])
    # Возвращаем информацию
    return output