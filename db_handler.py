import sqlite3
import hashlib
import datetime

# Функция подключения к базе данных
# Создаём подключение и курсор управления базой данных
# Возвращает созданные объекты дальше по вызову функции
def connectToDatabase():
    # Создание подключения к базе данных
    conn = sqlite3.connect('database.db')
    # Создание курсора для управления базой данных
    cursor = conn.cursor()
    # Возвращение параметров дальше
    return conn, cursor

# Функция закрытия подключения к базе данных
# conn - подключение к БД
def closeConnection(conn):
    # Закрытие подключения к переданной базе данных
    conn.close()

# Функция создания стандартных таблиц в базе данных (используется для инициализации в начале, если базы нет)
# Функция только для разработки
def createDefaultTables():
    # Получение основных объектов управления БД
    conn, cursor = connectToDatabase()
    # Отправка запросов на создание базовых таблиц
    cursor.execute("CREATE TABLE workPlace (wp_ID INTEGER PRIMARY KEY, wp_name VARCHAR(255), wp_location_ID INTEGER, wp_contacts_ID INTEGER, wp_empl_ID INTEGER, wp_verified VARCHAR(32));")
    cursor.execute("CREATE TABLE student (stud_ID INTEGER PRIMARY KEY, stud_FullName VARCHAR(255), stud_contacts_ID INTEGER, stud_studyPlace VARCHAR(255), stud_prof_list_ID INTEGER, stud_study_year INTEGER, stud_study_speciality VARCHAR(255), stud_verified VARCHAR(32));")
    cursor.execute("CREATE TABLE employer (empl_ID INTEGER PRIMARY KEY, empl_FullName VARCHAR(255), empl_prof_list_ID INTEGER, empl_contacts_ID INTEGER, empl_verified VARCHAR(32));")
    cursor.execute("CREATE TABLE profession (prof_ID INTEGER PRIMARY KEY, prof_name VARCHAR(255));")
    cursor.execute("CREATE TABLE location (location_ID INTEGER PRIMARY KEY, location_name VARCHAR(255), location_city VARCHAR(255), location_address VARCHAR(255), location_geo VARCHAR(255), location_extra_descr VARCHAR(255));");
    cursor.execute("CREATE TABLE contacts (contacts_ID INTEGER PRIMARY KEY, phone VARCHAR(32), email VARCHAR(255));");
    cursor.execute("CREATE TABLE profession_list (prof_list_ID INTEGER, prof_ID INTEGER);")
    cursor.execute("CREATE TABLE users (user_ID INTEGER PRIMARY KEY, user_Name VARCHAR(255), user_Login VARCHAR(255), user_Password VARCHAR(255), user_Type VARCHAR(64));")
    cursor.execute("CREATE TABLE users_links (user_ID INTEGER, user_link INTEGER);")
    cursor.execute("CREATE TABLE users_to_verif (user_ID INTEGER, user_Type INTEGER);")
    cursor.execute("CREATE TABLE pinged_users (from_user_ID INTEGER, from_user_type VARCHAR(64), to_user_ID INTEGER, to_user_type VARCHAR(64));")
    cursor.execute("CREATE TABLE news_post (post_ID INTEGER PRIMARY KEY, post_Author_ID INTEGER, post_Title VARCHAR(255), post_Description VARCHAR, post_Created DATETIME, post_Token VARCHAR(64), post_AcceptLvl VARCHAR(32))")
    # Важная функция, благодаря которой все переданные изменения сохраняются в БД
    conn.commit()
    # Закрываем подключение к базе данных
    closeConnection(conn)
    # Вносим стандартные значения в БД
    insertDefaultTables()

# Функция для внесения основной информации в стандартную базу данных для того, чтобы она нормально функционировала
# Функцию только для разработки
def insertDefaultTables():
    # Получаем базовые объекты управления БД
    conn, cursor = connectToDatabase()
    # Отправляем запросы на внесение базовых значений
    cursor.execute("""INSERT INTO workPlace (wp_ID) VALUES (0)""")
    cursor.execute("""INSERT INTO student (stud_ID) VALUES (0)""")
    cursor.execute("""INSERT INTO employer (empl_ID) VALUES (0)""")
    cursor.execute("""INSERT INTO profession (prof_ID) VALUES (0)""")
    cursor.execute("""INSERT INTO location (location_ID) VALUES (0)""")
    cursor.execute("""INSERT INTO contacts (contacts_ID) VALUES (0)""")
    cursor.execute("""INSERT INTO users (user_ID) VALUES (0)""")
    cursor.execute("""INSERT INTO users_to_verif (user_ID) VALUES (0)""")
    cursor.execute("""INSERT INTO pinged_users (from_user_ID, to_user_ID) VALUES (0, 0)""")
    cursor.execute("""INSERT INTO news_post (post_ID, post_author_ID) VALUES (0, 0)""")
    # Подтверждаем изменения в БД
    conn.commit()
    # Закрываем подключение к БД
    closeConnection(conn)

# ==============================
#createDefaultTables()

# Функция для проверки верификации
# user_ID - ID пользователя, который запросил подтверждение
# user_Link - ссылка на профиль пользователя
# user_Type - тип пользователя (студент, работодатель)
# Если пользователь уже отправлял заявку на верификацию, то функция найдёт его и скажет, что он уже отправлял запрос
# Иначе функция добавит пользователя в очередь на подтверждение
def checkForVerifyExist(user_ID, user_Link, user_Type):
    # Создаём подключение к БД
    conn, cursor = connectToDatabase()
    # Получаем информацию из таблицы очереди на подтверждение
    data1 = cursor.execute("SELECT * FROM users_to_verif WHERE user_ID = ? AND user_Type = ?", (user_ID, user_Type)).fetchall()
    # Получаем информацию о пользователе, которого хотим подтвердить
    data2 = []
    # Проверяем к какому именно пользователю это относится
    if user_Type == 'student':
        # Получаем информацию из таблицы студентов
        data2 = cursor.execute("SELECT * FROM student WHERE stud_ID = ? AND stud_verified = 'verified' OR stud_verified = 'processing' OR stud_verified = 'declined'", (user_Link, )).fetchall()
    if user_Type == 'employer':
        # Получаем информацию из таблицы работодателей
        data2 = cursor.execute("SELECT * FROM employer WHERE empl_ID = ? AND empl_verified = 'verified' OR empl_verified = 'processing' OR empl_verified = 'declined'", (user_Link, )).fetchall()
    # Закрываем подключение к БД
    closeConnection(conn)
    # Если массивы НЕ пустые, то возвращаем TRUE, значит пользователь существует
    if data1 or data2:
        return True
    else: # Иначе возвращаем FALSE, т.к. пользователя не существует
        return False

def isUserVerified(user_login):
    pass

# Функция для установки статуса подтверждения пользователю
# user_login - какому пользователю поменять статус верификации
# status - какой статус необходимо установить пользователю
# remove - FALSE изначально, только чтобы не удалять запись, когда TRUE, запись о потверждении удалится из очереди
def setVerificationStatus(user_login, status, remove=False):
    # Получаем информацию о пользователе по его логину
    userData = getUserData(user_login)
    # Вытаскиваем его идентификатор
    user_ID = userData[0]
    # И вытаскиваем тип пользователя
    user_Type = userData[4]
    # Получаем объекты управления БД
    conn, cursor = connectToDatabase()
    # Получаем ссылку на профиль пользователя
    user_Link = cursor.execute("SELECT user_link FROM users_links WHERE user_ID = ?", (user_ID, )).fetchone()[0]
    # Обрабатываем тип пользователя
    if user_Type == 'student':
        # Обновляем данные о статусе у студента
        cursor.execute('UPDATE student SET stud_verified = ? WHERE stud_ID = ?', (status, user_Link))
    elif user_Type == 'employer':
        # Обновляем данные о статусе у работодателя и его месте практики
        cursor.execute('UPDATE employer SET empl_verified = ? WHERE empl_ID = ?', (status, user_Link))
        cursor.execute('UPDATE workplace SET wp_verified = ? WHERE wp_empl_ID = ?', (status, user_Link))
    # Если установлен флаг remove=True, запись в очереди будет удалена
    if remove:
        # Удаление записи ожидания из БД
        cursor.execute("DELETE FROM users_to_verif WHERE user_ID = ? ", (user_Link, ))
    # Подтверждения действий работы с БД
    conn.commit()
    # Закрытие подключения к БД
    closeConnection(conn)

# Функция добавления запроса на верификацию пользователя
# user_login - логин пользователя
# Функция получает информацию о пользователе и добавляет его информацию в очередь на ожидание верификации
def addVerifyAsk(user_login):
    # Получаем информацию о пользователе
    userData = getUserData(user_login)
    # Вытаскиваем его идентификатор
    userID = userData[0]
    # Вытаскиваем его тип профиля
    userType = userData[4]
    # Подключаемся к БД
    conn, cursor = connectToDatabase()
    # Получаем связную ссылку на его профиль
    user_Link = cursor.execute("SELECT user_link FROM users_links WHERE user_ID = ?", (userID, )).fetchone()[0]
    # Проверяем был ли запрос от этого пользователя ранее
    if checkForVerifyExist(userID, user_Link, userType) == True:
        # Если был, закрываем соединение и прекращаем выполнение функции
        closeConnection(conn)
        return
    # Если запрос отправлен впервые, добавляем этот запрос в очередь на верификацию в БД
    cursor.execute("INSERT INTO users_to_verif (user_ID, user_Type) VALUES (?, ?)", (user_Link, userType))
    # Подтверждаем изменения в БД
    conn.commit()
    # Закрываем подключение к БД
    closeConnection(conn)
    # Устанавливаем статус пользователя на processing
    setVerificationStatus(user_login, "processing")

# ==============================

# Функция создания нового пользователя
# login - логин пользователя
# password - пароль пользователя
# utype - тип пользователя (студент, работодатель)
# Функция добавляет личный профиль и его связанные части пользователю в зависимости от его типа профиля
def createNewUser(login, password, utype):
    # Создаём подключение к БД
    conn, cursor = connectToDatabase()
    # Работаем ожидая ошибки ...
    try:
        # Добавляем в базу данных нового пользователя
        cursor.execute("INSERT INTO users (user_Login, user_Password, user_Type) VALUES (?, ?, ?)", (login, password, utype,))
        # Затем достаём идентификатор этого добавленного пользователя
        data1 = cursor.execute("SELECT user_ID FROM users ORDER BY user_ID DESC LIMIT 1").fetchone()[0]
        data2 = 0
        # Обрабатываем тип профиля
        if utype == 'student':
            # Если студент, достаём идентификаторы для создания нового профиля
            data2 = cursor.execute("SELECT stud_ID FROM student ORDER BY stud_ID DESC LIMIT 1").fetchone()[0] + 1
            data3 = cursor.execute("SELECT prof_ID FROM profession ORDER BY prof_ID DESC LIMIT 1").fetchone()[0] + 1
            data4 = cursor.execute("SELECT contacts_ID FROM contacts ORDER BY contacts_ID DESC LIMIT 1").fetchone()[0] + 1
            # Создаём новый профиль студента с внесёнными и обработанными ранее данными
            cursor.execute("INSERT INTO student (stud_ID, stud_contacts_ID, stud_prof_list_ID) VALUES (?, ?, ?)", (data2, data4, data3))
            cursor.execute("INSERT INTO profession (prof_ID) VALUES (?)", (data3,))
            cursor.execute("INSERT INTO contacts (contacts_ID) VALUES (?)", (data4,))
        elif utype == "employer":
            # Если тип работодатель, достаём старые идентификаторы прошлого работодателя
            data2 = cursor.execute("SELECT empl_ID FROM employer ORDER BY empl_ID DESC LIMIT 1").fetchone()[0] + 1
            data3 = cursor.execute("SELECT prof_ID FROM profession ORDER BY prof_ID DESC LIMIT 1").fetchone()[0] + 1
            data4 = cursor.execute("SELECT contacts_ID FROM contacts ORDER BY contacts_ID DESC LIMIT 1").fetchone()[0] + 1
            # Добавляем в таблицу базы данных новый профиль работодателя с обработанными ранее данными
            cursor.execute("INSERT INTO employer (empl_ID, empl_prof_list_ID, empl_contacts_ID) VALUES (?, ?, ?)", (data2, data3, data4))
            cursor.execute("INSERT INTO profession (prof_ID) VALUES (?)", (data3,))
            cursor.execute("INSERT INTO contacts (contacts_ID) VALUES (?)", (data4,))
            # Также добавляем информацию о месте практики работодателя, т.к. это связанные сущности
            data5 = cursor.execute("SELECT location_ID FROM location ORDER BY location_ID DESC LIMIT 1").fetchone()[0] + 1
            data6 = cursor.execute("SELECT contacts_ID FROM contacts ORDER BY contacts_ID DESC LIMIT 1").fetchone()[0] + 1
            # Добавляем новый профиль места практики и связываем его с работодателем
            cursor.execute("INSERT INTO workplace (wp_empl_ID, wp_contacts_ID, wp_location_ID) VALUES (?, ?, ?)", (data2, data6, data5))
            cursor.execute("INSERT INTO location (location_ID) VALUES (?)", (data5, ))
            cursor.execute("INSERT INTO contacts (contacts_ID) VALUES (?)", (data6, ))
        # Добавляем в базу данных нового пользователя, связанного с личным профилем
        cursor.execute("INSERT INTO users_links (user_ID, user_link) VALUES (?, ?)", (data1, data2))
        # Подтверждаем изменения в базе данных
        conn.commit()
    # Ловим случившиеся ошибки
    except Exception as e:
        # Выводим ошибку в консоль приложения
        print(e)
        # Возвращаем результат False
        return False
    finally:
        # И в любом случае закрываем подключение к БД
        closeConnection(conn)
    # Если всё прошло успешно, возвращаем True
    return True

# Функция проверки корректности введённого пароля
# login - логин пользователя
# password - пароль пользователя
# Функция проверяет существует ли такой пользователь
# Затем хэширует переданный пароль и достаёт пароль пользователя из БД
# Если пароли совпадают, функцию возвращает True, иначе False
def IsUserPasswordCorrect(login, password):
    # Проверяем существует ли такой пользователь
    if isUserExist(login) == True:
        # Если да, получаем его информацию
        data = getUserData(login)
        # Хэшируем переданный пароль
        h = hashlib.md5(str(password).encode('utf-8'))
        hashPass = h.hexdigest()
        # Если хэшированные пароли совпадают, возвращаем True
        if (hashPass == data[3]):
            return True
        else: # Если пароли не совпали - возвращаем False
            return False
    else:
        # Если пользователя не существует - возвращаем False
        return False

# Функция получения информации о пользователе из БД
# login - логин пользователя
# Функция отправляет запрос к БД на получение информации о пользователе по его логину
def getUserData(login):
    # Подключаемся к БД
    conn, cursor = connectToDatabase()
    # Запрашиваем информацию
    cursor.execute("SELECT * FROM users WHERE user_Login = ?", (login, ))
    # Высекаем информацию в массив
    data = cursor.fetchall()[0]
    # Закрываем подключение к БД
    closeConnection(conn)
    # Возвращаем информацию из массива
    return data

# Функция получения связной ссылки пользователя
# user_id - идентификатор пользователя
# Функция подключается к БД и получает ссылку на профиль пользователя по его ID
def getUserLink(user_id):
    # Подключаемся к БД
    conn, cursor = connectToDatabase()
    # Получаем информацию о его связной ссылке
    cursor.execute("SELECT user_link FROM users_links WHERE user_id = ?", (user_id, ))
    # Заполняем информацию в массив
    data = cursor.fetchone()[0]
    # Закрываем подключение к БД
    closeConnection(conn)
    # Возвращаем информацию по вызову функции
    return data

# Функция проверки на существование пользователя
# login - логин пользователя
# Функция подключается к БД и запрашивает информацию о пользователе по логину
# Если пользователь существует, возвращает True, иначе False
def isUserExist(login):
    # Подключаемся к БД
    conn, cursor = connectToDatabase()
    # Отправляем запрос к БД на получение информации 
    cursor.execute("SELECT user_Login FROM users WHERE user_Login = (?)", (login, ))
    # Извлекаем дату из запроса
    data = cursor.fetchall()
    # Закрываем подключение к БД
    closeConnection(conn)
    # Если пользователь существует - возвращаем True, иначе False
    if data:
        return True
    else:
        return False
        
# Функция изменения информации о пользователе
# user - информация о пользователе
# data - информация для изменения
# Функция получает информацию с формы ввода данных, определяет тип пользователя
# Отправляет запросы к БД на изменение определённых типов
# Обрабатывает ошибки, выявленные в ходе запросов
def changeUserData(user, data):
    # Подключаемся к БД
    conn, cursor = connectToDatabase()
    # Работаем с обработкой ошибок
    try:
        # Если тип профиля студент
        if user[4] == 'student':
            # Получаем информацию с формы ввода данных
            studentFullName = data['studentFullName']
            studentStudyPlace = data['studentStudyPlace']
            studentSpeciality = data['studentSpeciality']
            studentStudyYear = data['studentStudyYear']
            studentProfName = data['studentProfName']
            studentPhone = data['studentPhone']
            studentEMail = data['studentEMail']        
            # Проверяем переданные данные на корректность
            if not studentFullName or not studentProfName or not studentStudyPlace or not studentStudyYear or not studentPhone or not studentEMail or not studentSpeciality:
                raise # Если данные некорректно введены, возвращаем ошибку
            # Получаем связную ссылку на профиль пользователя
            userLink = cursor.execute("SELECT user_link FROM users_links WHERE user_ID = ?", (user[0],)).fetchone()[0]
            # Получаем информацию о профиле пользователя
            userData = cursor.execute("SELECT * FROM student WHERE stud_ID = ?", (userLink, )).fetchone()
            # Обновление информации студента
            cursor.execute("UPDATE student SET stud_FullName = ?, stud_studyPlace = ?, stud_study_year = ?, stud_study_speciality = ? WHERE stud_ID = ?", (studentFullName, studentStudyPlace, studentStudyYear, studentSpeciality, userData[0]))
            # Обновление информации профессии
            cursor.execute("UPDATE profession SET prof_name = ? WHERE prof_ID = ?", (studentProfName, userData[4]))
            # Обновление информации контактов
            cursor.execute("UPDATE contacts SET phone = ?, email = ? WHERE contacts_ID = ?", (studentPhone, studentEMail, userData[2]))
        # Если тип профиля работодатель
        elif user[4] == 'employer':
            # Получаем информацию с формы ввода данных
            emplFullName = data['emplFullName']
            emplProfName = data['emplProfName']
            emplPhone = data['emplPhone']
            emplEMail = data['emplEMail']
            workplaceName = data['workplaceName']
            workplaceLocation = data['workplaceLocation']
            workplaceCity = data['workplaceCity']
            workplaceAddress = data['workplaceAddress']
            workplaceLocationExtraData = data['workplaceLocationExtraData']
            workplacePhone = data['workplacePhone']
            workplaceEMail = data['workplaceEMail']

            # Проверяем данные на корректность
            if not emplFullName or not emplProfName or not emplPhone or not emplEMail or not workplaceName or not workplaceLocation or not workplaceCity or not workplaceAddress or not workplaceLocationExtraData or not workplacePhone or not workplaceEMail:
                raise
            # Получаем связанную ссылку на профиль пользователя
            userLink = cursor.execute("SELECT user_link FROM users_links WHERE user_ID = ?", (user[0],)).fetchone()[0]
            # Получаем информацию о пользователе
            userData = cursor.execute("SELECT * FROM employer WHERE empl_ID = ?", (userLink, )).fetchone()
            # Изменяем информацию у работодателя
            cursor.execute("UPDATE employer SET empl_FullName = ? WHERE empl_ID = ?", (emplFullName, userData[0]))
            cursor.execute("UPDATE profession SET prof_Name = ? WHERE prof_ID = ?", (emplProfName, userData[2]))
            cursor.execute("UPDATE contacts SET phone = ?, email = ? WHERE contacts_ID = ?", (emplPhone, emplEMail, userData[3]))
            # Изменяем информацию о месте практики
            wpData = cursor.execute("SELECT * FROM workplace WHERE wp_empl_ID = ?", (userData[0],)).fetchone()
            cursor.execute("UPDATE workplace SET wp_name = ? WHERE wp_ID = ?", (workplaceName, wpData[0]))
            cursor.execute("UPDATE location SET location_name = ?, location_city = ?, location_address = ?, location_extra_descr = ? WHERE location_ID = ?", (workplaceLocation, workplaceCity, workplaceAddress, workplaceLocationExtraData, wpData[2]))
            cursor.execute("UPDATE contacts SET phone = ?, email = ? WHERE contacts_ID = ? ", (workplacePhone, workplaceEMail, wpData[3]))
        # Подтверждаем изменения в БД
        conn.commit()
    # Обрабатываем ошибки и сообщаем о них
    except Exception as e:
        print("Ошибка при изменении данных: " + str(e))
        return False
    finally:
        # В любом случае закрываем подключение
        closeConnection(conn)
    # Возвращаем True если всё прошло успешно
    return True

# ==============================

# Функция получения идентификатора студента
# studentID - идентификатор студента
# Функция подключается к БД и отправляет запрос за получение студента с определённым идентификатором
def getStudentByID(studentID):
    # Подключаемся к БД
    conn, cursor = connectToDatabase()
    # Отправляем запрос к таблице студентов
    cursor.execute("SELECT * FROM student WHERE stud_ID = ?", (studentID, ))
    # Извлекаем информацию о студенте
    studentData = cursor.fetchall()[0]
    # Закрываем подключение к БД
    closeConnection(conn)
    # Возвращаем информацию о студентах
    return studentData

# Функция получения информации о работодателе по идентификатору
# employerID - идентификатор работодателя
# Функция подключается к БД, отправляет запрос на получение информации о работодателе по указанному идентификатору
def getEmployerByID(employerID):
    # Подключаемся к БД
    conn, cursor = connectToDatabase()
    # Отправляем запрос к БД на получение информации о работодателе по ID
    cursor.execute("SELECT * FROM employer WHERE empl_ID = ?", (employerID, ))
    # Достаём информацию
    emplData = cursor.fetchall()[0]
    # Закрываем подключение к Бд
    closeConnection(conn)
    # Возвращаем информацию о работодателе
    return emplData

# Функция получения информации о контактах по идентификатору
# contactsID - идентификатор контактов
# Функция отправляет запрос к БД на получение контакта по укзанному ID
def getContactsByID(contactsID):
    # Подключаемся к БД
    conn, cursor = connectToDatabase()
    # Отправляем запрос к БД на получение контактов
    cursor.execute("SELECT * FROM contacts WHERE contacts_ID = ?", (contactsID, ))
    # Выделяем информацию в массив
    contactsData = cursor.fetchall()[0]
    # Закрываем подключение к БД
    closeConnection(conn)
    # Возвращаем информацию по вызову
    return contactsData

# Функция получения информации о профессии по уникальному идентификатору
# prof_list_ID - идентификатор профессии
def getProfessionsByID(prof_list_ID):
    # Подключаемся к БД
    conn, cursor = connectToDatabase()
    # Отправляем запрос к БД на получение информации
    cursor.execute("SELECT * FROM profession WHERE prof_ID = ?", (prof_list_ID, ))
    # Достаём информацию в массив
    profData = cursor.fetchall()[0]
    # Закрываем подключение к БД
    closeConnection(conn)
    # Возвращаем информацию по вызову
    return profData

# Функция получения информации о месте практики по уникальному идентификатору
# workplaceID - идентификатор места практики
def getWorkplaceByID(workplaceID):
    # Подключаемся к БД
    conn, cursor = connectToDatabase()
    # Отправляем запрос к БД для получения информации
    cursor.execute("SELECT * FROM workplace WHERE wp_ID = ?", (workplaceID, ))
    # Выделяем информацию в массив
    workPlaceData = cursor.fetchall()[0]
    # Закрываем подключение к БД
    closeConnection(conn)
    # Возвращаем информацию по вызову
    return workPlaceData

# Функция получения информации о местоположении по идентификатору
# locationID - идентификатор местоположения
def getLocationByID(locationID):
    # Подключаемся к БД
    conn, cursor = connectToDatabase()
    # Отправляем запрос к БД на получение информации
    cursor.execute("SELECT * FROM location WHERE location_ID = ?", (locationID, ))
    # Достаём информацию из запроса
    locationData = cursor.fetchall()[0]
    # Закрываем подключение
    closeConnection(conn)
    # Возвращаем информацию по вызову
    return locationData

# ==============================

# Функция для получения информации о всех студентах
def getAllStudents():
    # Подключаемся к БД
    conn, cursor = connectToDatabase()
    # Достаём информацию из отправленного запроса
    data = cursor.execute('SELECT * FROM student WHERE stud_verified = "verified"').fetchall()
    # Закрываем подключение
    closeConnection(conn)
    # Возвращаем информацию по вызову
    return data

# Функция для получения информации о всех работодателях
def getAllEmployers():
    # Подключаемся к БД
    conn, cursor = connectToDatabase()
    # Отправляем запрос и достаём из него информацию
    data = cursor.execute('SELECT * FROM employer WHERE em.empl_verified = "verified"').fetchall()
    # Закрываем подключение к БД
    closeConnection(conn)
    # Возвращаем информацию
    return data

# Получить полную информацию о всех работодателях
def getAllEmployersWithExtra():
    # Подключаемся к БД
    conn, cursor = connectToDatabase()
    # Отправляем запрос к БД и достаём из него информацию
    data = cursor.execute("""
        SELECT * FROM employer em 
        JOIN profession pr ON em.empl_prof_list_ID = pr.prof_ID
        JOIN workPlace wp ON wp.wp_empl_ID = em.empl_ID
        WHERE em.empl_verified = "verified" 
    """).fetchall()
    # Закрываем подключение к БД
    closeConnection(conn)
    # Возвращаем информацию по вызову
    return data

# Получаем информацию о местах практики
def getAllWorkplaces():  
    # Подключаемся к БД
    conn, cursor = connectToDatabase()
    # Отправляем запрос к БД и достаём из него информацию
    data = cursor.execute('SELECT * FROM workplace WHERE wp_verified = "verified"').fetchall()
    # Закрываем подключение к БД
    closeConnection(conn)
    # Возвращаем информацию по вызову
    return data

# Функция для получения полной информации о местах практики 
def getAllWorkplacesWithExtra():
    # Подключаемся к БД
    conn, cursor = connectToDatabase()
    # Отправляем запрос и достаём из него информацию
    data = cursor.execute("""
        SELECT * FROM workplace wp
        JOIN location loc ON wp.wp_location_ID = loc.location_ID
        WHERE wp.wp_verified = "verified"
    """).fetchall()
    # Закрываем подключение
    closeConnection(conn)
    # Возвращаем информацию по вызову
    return data

# Функция для автоматического заполнения пустых мест в запросах на None
# counter - количество параметров
def getNoneParams(counter):
    # Инициализируем список
    params = []
    # Заполяем список
    for x in range(counter):
        params.append('None')
    # Возвращаем список по вызову
    return params

# Функция получения информации о пользователе по идентификатору и типу
# user - тип профиля
# userID - идентификатор профиля
def getDataByUser(user, userID):
    # Создаём список информации
    data = {}
    # Обрабатываем тип и возвращаем соответствующие данные
    if user in ('student', 'student'):
        data = getStudentFullInfo(userID)
    elif user in ('employer', 'employer'):
        data = getEmployerFullInfo(userID)
    elif user in ('workplace'):
        data = getWorkplaceFullInfo(userID);
    return data

# Функция получения полной информации о студенте по его уникальному идентификатору
# studentID - идентификатор студента
def getStudentFullInfo(studentID):
    # Получаем информацию о студенте
    studentData = getStudentByID(studentID)
    # Информацию о контактах
    contactsData = []
    # Информация о профессии
    profData = []
    # Если у студента нет контактов добавляем пустые значения
    if not studentData[2]:
        contactsData = getNoneParams(3)
    else: # Если у студента есть контакты, добавляем их из таблицы
        contactsData = getContactsByID(studentData[2])
    if not studentData[4]: # Если у студента нет профессии, добавляем пустые значения
        profData = getNoneParams(7) 
    else: # Если есть, достаём их из таблицы
        profData = getProfessionsByID(studentData[4])
    # Генерируем итоговый массив информации
    data = { 'type': 'student', "studentData": studentData, "contactsData": contactsData, "profData": profData }
    # Возвращаем информацию по вызову функции
    return data

# Функция получения полной информации о работодателе по его уникальному идентификатору
# employerID - идентификатор работодателя
def getEmployerFullInfo(employerID):
    # Получаем информацию о работодателе из БД
    emplData = getEmployerByID(employerID)
    # Информация о профессии
    profData = []
    # Информация о контактах
    contactsData = []
    # Информация о месте практики
    workplaceData = {}
    if not emplData[2]: # Если нет профессии, добавляем пустые значения
        profData = getNoneParams(3)
    else: # Если есть профессия, достаём её из БД
        profData = getProfessionsByID(emplData[2])
    if not emplData[3]: # Если нет контактов, добавляем пустые значения
        contactsData = getNoneParams(3) 
    else: # Если есть, достаём их из БД
        contactsData = getContactsByID(emplData[3])
    # Инициализируем информацию о месте практики
    wpID = getWorkplaceIdByEmployer(emplData[0])[0]
    # Получаем полную информацию о месте практики
    workplaceData = getWorkplaceFullInfo(wpID)
    # Формируем итоговый массив с информацией
    data = { 'type': 'employer', "emplData": emplData, "contactsData": contactsData, "profData": profData, "workplaceData": workplaceData }
    # Возвращаем информацию по вызову
    return data

# Функция получения информации о месте практики по идентификатору работодателя
# employerID - идентификатор работодателя
def getWorkplaceIdByEmployer(employerID):
    # Подключаемся к БД
    conn, cursor = connectToDatabase()
    # Получаем информацию из БД и выделяем её в массив
    data = cursor.execute("SELECT * FROM workplace WHERE wp_empl_ID = ?", (employerID,)).fetchone()
    # Закрываем подключение к БД
    closeConnection(conn)
    # Возвращаем массив по вызову
    return data

# Функция получения полной информации о месте практики
# workplaceID - идентификатор места практики
def getWorkplaceFullInfo(workplaceID):
    # Получаем информацию о месте практики по идентификатору
    workplaceData = getWorkplaceByID(workplaceID)
    # Информация о местоположении
    locationData = []
    # Информация о контактах
    contactsData = []
    # Информация о работодателе
    emplData = []
    # Если места для практик нет, добавляем пустые значения
    if not workplaceData[2]:
        locationData = getNoneParams(6)
    else: # Если есть, достаём из БД
        locationData = getLocationByID(workplaceData[2])
    if not workplaceData[3]: # Если нет контактов с места практики, добавляем пустые значения
        contactsData = getNoneParams(3)
    else: # Если есть, достаём из таблицы
        contactsData = getContactsByID(workplaceData[3])
    if not workplaceData[4]: # Если нет информации о работодателе, добавляем пустые значения
        emplData = getNoneParams(4)
    else: # Если есть, достаём из БД
        emplData = getEmployerByID(workplaceData[4])
    # Формируем итоговый массив с информацией
    data = { 'type': 'workplace', "workplaceData": workplaceData, "locationData": locationData, "contactsData": contactsData, "emplData": emplData}
    # Возвращаем итоговый массив
    return data

def pingUser(from_user_login, to_user_ID, to_user_type):
    userData = getUserData(from_user_login)
    from_user_ID = getUserLink(userData[0])
    from_user_type = userData[4]

    # Проверяем, чтобы люди не пинговали сами себя
    if from_user_ID == to_user_ID and from_user_type == to_user_type:
        return False

    conn, cursor = connectToDatabase()
    check = cursor.execute("SELECT * FROM pinged_users WHERE from_user_ID = ? AND to_user_ID = ? AND from_user_type = ? AND to_user_type = ?", (from_user_ID, to_user_ID, from_user_type, to_user_type)).fetchall()
    if len(check) > 0:
        closeConnection(conn)
        return False
    else:
        cursor.execute("INSERT INTO pinged_users(from_user_ID, from_user_type, to_user_ID, to_user_type) VALUES (?, ?, ?, ?)", (from_user_ID, from_user_type, to_user_ID, to_user_type))
        conn.commit()
        closeConnection(conn)
        return True

def getPingedFrom(user_ID, from_user_type, to_user_type):
    conn, cursor = connectToDatabase()
    data = []
    if from_user_type == 'student':
        data = cursor.execute("SELECT st.stud_ID, st.stud_FullName FROM student st JOIN pinged_users pu ON st.stud_ID = pu.from_user_ID WHERE pu.to_user_ID = ? and pu.to_user_type = ? AND pu.from_user_type = ?", (user_ID, to_user_type, from_user_type)).fetchall()
    else:
        data = cursor.execute("SELECT em.empl_ID, em.empl_FullName FROM employer em JOIN pinged_users pu ON em.empl_ID = pu.from_user_ID WHERE pu.to_user_ID = ? and pu.to_user_type = ? AND pu.from_user_type = ?", (user_ID, to_user_type, from_user_type)).fetchall()
    closeConnection(conn)
    return data

def getPingedTo(user_ID, to_user_type, from_user_type):
    conn, cursor = connectToDatabase()
    data = []
    if to_user_type == 'student':
        data = cursor.execute("SELECT st.stud_ID, st.stud_FullName FROM student st JOIN pinged_users pu ON st.stud_ID = pu.to_user_ID WHERE pu.from_user_ID = ? and pu.from_user_type = ? and pu.to_user_type = ?", (user_ID, from_user_type, to_user_type)).fetchall()
    else:
        data = cursor.execute("SELECT em.empl_ID, em.empl_FullName FROM employer em JOIN pinged_users pu ON em.empl_ID = pu.to_user_ID WHERE pu.from_user_ID = ? and pu.from_user_type = ? and pu.to_user_type = ?", (user_ID, from_user_type, to_user_type)).fetchall()
    
    closeConnection(conn)
    return data

def getGlobalNewsFeed():
    conn, cursor = connectToDatabase()
    data = cursor.execute("SELECT * FROM news_post JOIN employer em ON empl_ID = post_Author_ID WHERE post_AcceptLvl = 'public' ORDER BY post_Created DESC").fetchall()
    closeConnection(conn)
    return data

def getNewsByWorkplace(workplaceID):
    conn, cursor = connectToDatabase()
    data = cursor.execute("SELECT * FROM news_post JOIN employer em ON empl_ID = post_Author_ID WHERE post_Author_ID = ? AND post_AcceptLvl = 'public' or post_AcceptLvl = 'private' ORDER BY post_Created DESC", (workplaceID, )).fetchall()
    closeConnection(conn)
    return data

def generatePostToken(createTime, author_ID):
    h1 = hashlib.md5(str(createTime).encode('utf-8'))
    h2 = hashlib.md5(str(author_ID).encode('utf-8'))
    token = h1.hexdigest() + h2.hexdigest()
    return token

def addNewPost(title, descr, radio, user):
    author = getUserLink(getUserData(user)[0])
    created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    token = generatePostToken(created, author)
    acceptance = ''
    if radio == 'opt1':
        acceptance = 'public'
    else:
        acceptance = 'private'
    conn, cursor = connectToDatabase()
    cursor.execute("INSERT INTO news_post (post_Author_ID, post_Title, post_Description, post_Created, post_Token, post_AcceptLvl) VALUES (?, ?, ?, ?, ?, ?)", (author, title, descr, created, token, acceptance))
    conn.commit()
    closeConnection(conn)
    
def isUserAuthor(user_login, wpID):
    user = getUserData(user_login)
    user_link = getUserLink(user[0])
    workplace = getWorkplaceByID(wpID)

    if user[4] == 'employer' and user_link == workplace[4]:
        return True
    else:
        return False