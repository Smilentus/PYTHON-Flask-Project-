# Импортируем необходимые компоненты и библиотеки
from flask import Flask, render_template, request, redirect, abort, flash, session, escape
# Flask - основной модуль Фласка
# render_template - функция, позволяющая отрисовыват HTML страницы по заранее подготовленным шаблонам
# request - функция, позволяющая работать с запросами POST и GET и их информацией
# redirect - функция перенаправления на указанную страницу или адрес
# abort - функция, вызывающая срабатывание указанной ошибки
# flash - функция передачи текста об ошибках на отрисовываемые шаблоны внутри сессии
# session - функция, открывающая возможность работы с сессиями
# escape - функция для чего-то там, вроде не использую её 
import hashlib
# Библиотека для хэширования паролей

# Импортируем дополнительные скрипты
import db_handler as db
import event_router as er

# Инициализируем запуск Flask
app = Flask(__name__)
# Устанавливаем секретный ключ для инициализации настроек cookies
app.config['SECRET_KEY'] = '340cfed177c54e2d9491d3b9ad297cf4'

# Глобальная проверка на то, авторизован пользователь или нет
def checkUserAuth():
    # Если в сессии нет ключей значений user и user_token, возвращаем False иначе True
    if 'user' not in session or 'user_token' not in session:
        return False
    else: 
        return True 

# Маршрут для основной страницы
# == 
# Функция обрабатывает запросы на / и /main для отрисовки шаблона основной страницы
@app.route('/')
@app.route('/main', methods=['GET'])
def mainPage():
    # Возвращаем шаблон главной страницы с параметром isAuth
    return render_template("index.html", isAuth=checkUserAuth())

# Маршрут для страницы авторизации
# == 
# Функция обработки запроса по адресу /auth для отрисовки страницы авторизации 
@app.route('/auth', methods=['GET'])
def authPage():
    # Возвращаем шаблон страницы авторизации с параметром isAuth
    return render_template("auth.html", isAuth=checkUserAuth())

# Маршрут для страницы регистрации 
# == 
# Функция для обработки запроса по адресу /register для отрисовки страницы регистрации
@app.route('/register', methods=['GET'])
def registerPage():
    # Возвращаем шаблон страницы регистрации с параметром isAuth
    userType = ''
    if session['registerUserType'] is not None:
        userType = session['registerUserType']
    else:
        userType = 'student'
    return render_template("register.html", isAuth=checkUserAuth(), registerUserType=userType)

# Маршрут для страницы выхода с личного кабинета# == 
# Функция для обработки запроса по адресу /logout 
# Удаляет данных пользователя из сессии и перенаправляет на главную страницу /
@app.route('/logout', methods=['GET'])
def logout():
    # Обнуляем значения в текущей сессии
    session.pop('user_token', None)
    session.pop('user', None)
    # Перенаправляем на основную страницу
    return redirect('/')

# Маршрут для страницы работодателей
# == 
# Функция для обработки запроса /employers 
# Проверяет данные в сессии, если есть данные для поиска, сортируем по критерию
# Если данных нет, возвращаем список информации о всех сотрудниках
@app.route('/employers', methods=['GET'])
def employersPage():
    # Если в текущей сессии есть параметр для поиска, значит отображаем данные из поиска
    if 'search' in session:
        # Получаем информацию о всех работодателях
        data = er.getEmployersBySearch(session['search'])
        # Обнуляем параметры поиска из хранилища сессии
        session.pop('search', None)
    else:
        # Иначе получаем информацию о всех работодателях
        data = db.getAllEmployersWithExtra()

    # Возвращаем шаблон страницы работодателей с переданными параметрами
    return render_template("employers.html", data=data, isAuth=checkUserAuth())

# Маршрут на страницу студентов
# == 
# Функция, обрабатывающая запрос /students 
# Проверяет данные в сессии о поиске по критерию
# Если критерий есть, сортирует данные по нему, иначе отображает список всех студентов
@app.route('/students', methods=['GET'])
def studentsPage():
    # Если в текущей сессии есть параметр search, то выполняем поиск
    if 'search' in session:
        # Получаем информацию по параметру поиска из базы данныхы
        data = er.getStudentsBySearch(session['search'])
        # Очищаем параметр search из сессии
        session.pop('search', None)
    else:
        # Иначе просто получаем список всех студентов
        data = db.getAllStudents()
    # Возвращаем шаблон страницы студентов с параметром isAuth
    return render_template("students.html", data=data, isAuth=checkUserAuth())

# Маршрут на страницу мест практики
# == 
# Функция обработки запроса /workplaces
# Если в сессии есть данные для поиска по критерию - запрашивает данные по критерию
# Если в сессии есть данные для фильтра по критерию - запрашивает данные по фильтру
# Иначе возвращает всю информацию о местах практики для отображения на странице
@app.route('/workplaces', methods=['GET'])
def workPlacesPage():
    # Если параметр search имеется в текущей сессии
    if 'search' in session:
        # Получаем информацию о местах практики с параметром search
        data = er.getWorkplacesBySearch(session['search'])
        # Очищаем параметр search из сессии
        session.pop('search', None)
    elif 'filter' in session:
        # Иначе проверяем параметр filter
        # Получаем информацию о местах практики по параметрам фильтра
        data = er.getWorkplacesByFilter(session['filter'])
        # Очищаем параметр фильтр из текущей сессии
        session.pop('filter', None)
    else:
        # Иначе просто получаем всю информацию о местах практики
        data = db.getAllWorkplacesWithExtra()
    # Отрисовываем шаблон страницы мест практики с параметрами data isAuth и cities
    # data - информация о всех местах практики с БД
    # isAuth - проверка авторизован ли пользователь
    # cities - информация о всех доступных городах для использования в фильтре 
    return render_template("workPlaces.html", data=data, isAuth=checkUserAuth(), cities=er.getWorkplacesCities())

# Маршрут на страницу личного кабинета
# == 
# Функция обработки запроса /cabinet
# Проверяет авторизован ли пользователь, затем проверяем информацию в сессии
# Если в сессии сидит тот же пользователь, к которому мы пытаемся зайти, то мы пропускаем пользователя в личный кабинет
# Иначе говорим, что произошла ошибка
@app.route('/cabinet', methods=['GET'])
def cabinetPage():
    # Если пользователь авторизован, то ...
    if checkUserAuth():
        # Проверяем тот ли пользователь пытается зайти в профиль ...
        if er.checkUserTokens(session['user_token'], session['user']) == True:
            # Получаем информацию о текущем пользователе
            user = db.getUserData(session['user'])
            user_link = db.getUserLink(user[0])
            # Получаем информацию о личном кабинете пользователя
            data = db.getDataByUser(user[4], user_link)
            
            pingedFromStudents = db.getPingedFrom(user_link, 'student', user[4])
            pingedFromEmployers = db.getPingedFrom(user_link, 'employer', user[4])
            pingedToStudents = db.getPingedTo(user_link, 'student', user[4])
            pingedToEmployers = db.getPingedTo(user_link, 'employer', user[4])
            
            return render_template("cabinet.html", user=user[4], data=data, isAuth=checkUserAuth(), fromStudents=pingedFromStudents, fromEmployers=pingedFromEmployers, toStudents=pingedToStudents, toEmployers=pingedToEmployers)
        else:
            # Иначе кидаем на страницу с ошибкой 404
            return redirect('/not_found')
    else:
        # Если пользователь не авторизован, кидаем на страницу с ошибкой 404
        return redirect('/not_found')

# Маршрут с собираемыми параметрами на профиль пользователя
# <user> - какой конкретный профиль, студента, работодателя или места практики
# <profileID> - идентификатор конкретного профиля
# == 
# Функция обработки запроса /profile/user/profileID
# Принимает на вход параметры пользователя и его идентификатора
# Обрабатывает эти данные и перенаправляет на профиль конкретного пользователя
@app.route('/profile/<user>/<profileID>', methods=['GET'])
def profilePage(user, profileID):
    # user - чей профиль, студента, работодателя
    # profileID - какой конкретно профиль
    if user in { "student", "employer", "workplace" }:
        # Получаем информацию о текущем пользователе
        data = db.getDataByUser(user, profileID)
        # Отрисовываем профиль пользователя с параметрами
        # user - информация о пользователе
        # data - информация о личном кабинете пользователя
        # isAuth - проверка на авторизацию пользователя
        return render_template("profile.html", user=user, data=data, isAuth=checkUserAuth())
    else:
        # Иначе возвращаем на страницу с ошибкой 404
        return redirect("/not_found")

# Маршрут перенаправления для кнопки Я студент
# == 
# Функция для обработки запроса /api/goToStudents
# Проверяет авторизован ли пользователь и в зависимости от ответа перенаправляет на страницы
@app.route('/api/goToStudents')
def apiGoToStudents():
    # Проверяем авторизован ли пользователь
    if checkUserAuth():
        # Если да, перенаправляем на страницу со всеми студентами
        return redirect('/students')
    else:
        # Иначе перенаправляем на страницу регистрации
        session['registerUserType'] = 'student'
        return redirect('/register')

# Маршрут перенаправления для кнопки Я работодатель
# # == 
# Функция для обработки запроса /api/goToEmployers
# Проверяет авторизован ли пользователь и в зависимости от ответа перенаправляет на страницы
@app.route('/api/goToEmployers')
def apiGoToEmployers():
    # Проверяем авторизован ли пользователь
    if checkUserAuth():
        # Если да, то перенаправляем на страницу работодателей
        return redirect('/employers')
    else:
        # Если нет, перенаправляем на страницу регистрации
        session['registerUserType'] = 'employer'
        return redirect('/register')

# Маршрут для авторизации пользователя
# ==
# Функция обработки запроса /api/authUser 
# Проверяет тип запроса и обрабатывает POST
# Получает данные с формы ввода данных, обрабатывает их
# Если данные заполнены некорректно или пусты сообщает об этом
# Если пользователь уже существует, сообщает об этом
# Если введённые пароли не совпадают с хранимыми в базе данных, сообщает об этом
# Если все защиты пройдены - перенаправляет на личный кабинет с параметрами в сессии
@app.route('/api/authUser', methods=['POST'])
def apiAuthUser():
    # Если передаваемый метод запроса POST
    if request.method == "POST":
        # Получаем данные с формы авторизации
        login = request.form['inputLogin']
        password = request.form['inputPassword']
        option = request.form.get('inputRememberMe')

        # Проверяем введённые данные на пустоту
        if not login or not password:
            # Если не все поля заполнены, сообщаем об этом
            flash("Необходимо заполнить все поля!")
            # И перенаправляем на страницу авторизации
            return redirect('/auth')

        # Проверяем существует ли такой пользователь
        if not db.isUserExist(login):
            # Если нет, то сообщаем об ошибке 
            flash("Такого пользователя не существует!")
            # И перенаправляем на страницу авторизации обратно
            return redirect('/auth')

        # Если введённый пароль неверный, сообщаем об этом и перенаправляем на страницу авторизации
        if not db.IsUserPasswordCorrect(login, password):
            flash("Логин или пароль не совпадают, попробуйте ещё раз!")
            return redirect('/auth')

        # Если всё прошло удачно и ошибок нет
        # Запоминаем в текущей сессии атворизованного пользователя
        session['user'] = login
        # И его уникальный идентификатор
        session['user_token'] = er.generateUserToken(login)
        # Затем перенаправляем в личный кабинет
        return redirect('/cabinet')
        
    else:
        # Иначе перенаправляем на страницу с ошибкой 404
        return redirect('/not_found')

# Маршрут для регистрации пользователя
# ==
# Функция для обработки запроса /api/registerUser
# Получает информацию с полей ввода данных на форме
# Обрабатывает данные с проверками
# Если данные корректны, проверяет совпадение паролей, если они не совпадают, сообщает об этом
# Проверяет существует ли пользователь и если не существует, сообщает об этом
# Если все защиты прошли удачно, функция генерирует хэши для паролей и передаёт их в базу данных
# Если всё прошло успешно, функция отправляет запрос на создание нового пользователя и перенаправляет в личный кабинет
@app.route('/api/registerUser', methods=['POST'])
def apiRegisterUser():
    # Если передаваемый метод запроса POST
    if request.method == "POST":
        # Получаем данные с формы ввода
        option = request.form.getlist('userType')[0]
        login = request.form['inputLogin']
        password = request.form['inputPassword']
        rePassword = request.form['inputRepeatPassword']
        
        # Проверяем если не все поля заполнены
        if not login or not password or not rePassword:
            # Сообщаем об этом и перенаправляем обратно на страницу регистрации
            flash("Необходимо заполнить все поля")
            return redirect('/register')
            
        # Иначе проверяем если пароли не совпадают
        if password != rePassword:            
            # Сообщаем об этом и перенаправляем обратно на страницу регистрации
            flash("Пароли не совпадают, попробуйте ещё раз!")
            return redirect('/register')

        # Если всё прошло как надо, генерируем хэш для создания пароля
        h = hashlib.md5(str(password).encode('utf-8'))
        # Защищаем наш пароль от взлома хэшированной функцией
        hashPass = h.hexdigest()

        # Дальше проверяем существует ли такой пользователь, которого мы хотим зарегистрировать
        if db.isUserExist(login):
            # Если существует, сообщаем об этом и перенаправляем на страницу регистрации
            flash("Такой пользователь уже существует!")
            return redirect('/register')

        # Проверяем выбрана ли галочка типа профиля (студент или работодатель)
        if option not in ('student', 'employer'):
            # Если нет, сообщаем об этом и перенаправляем на страницу регистрации
            flash("Выберите стандартный тип профиля!")
            return redirect('/register')
            
        # Если всё прошло успешно и защиты были пройдены
        # Создаём нового пользователя в базе данных и получаем ответ функции
        result = db.createNewUser(login, hashPass, option)
        
        # Если регистрация пользователя прошла успешна
        if result == True:
            # Запоминаем пользователя и его токен в текущей сессии
            session['user'] = login
            session['user_token'] = er.generateUserToken(login)
            # Перенаправляем на личный кабинет
            return redirect('/cabinet')
        else:
            # Если зарегистрировать нового пользователя не получилось, сообщаем об этом
            flash("Не удалось зарегистрировать пользователя!")
            # И перенаправляем на страницу регистрации
            return redirect('/register')
    else:
        # Иначе перенаправляем на страницу с ошибкой 404
        return redirect('/not_found')

# Маршрут для изменения данные в личном кабинете
# ==
# Функция для обработки запроса /api/changeProfileSettings
# Функция проверяет авторизован ли пользователь, правильные ли данные находятся в сессии
# Получает информацию о пользователе и перенаправляет на страницу изменения этих самых данных
@app.route('/api/changeProfileSettings', methods=['POST', 'GET'])
def apiChangeProfileSettings():
    # Проверяем авторизован ли пользователь
    if checkUserAuth():
        # Если пользователь находится в данной сессии
        # Проверяем его данные, тот ли человек заходит в личный профиль
        if er.checkUserTokens(session['user_token'], session['user']) == True:
            # Получаем информацию о пользователе по его логину
            user = db.getUserData(session['user'])
            user_link = db.getUserLink(user[0])
            # Получаем информацию для личного кабинета пользователя
            data = db.getDataByUser(user[4], user_link)
            # Перенаправляем на страницу изменения настроек с параметрами
            # user - информация о пользователе
            # data - информация для личного кабинета
            # isAuth - информация о том авторизован пользователь или нет
            return render_template("cabinet_settings.html", user=user[4], data=data, isAuth=checkUserAuth())
        else:
            # Иначе перенаправляем на страницу с ошибкой 404
            return redirect('/not_found')
    else:
        # Иначе перенаправляем на страницу с ошибкой 404
        return redirect('/not_found')

# Маршрут для подтверждения изменения настроек в личном кабинете 
# ==
# Функция для обработки запроса /api/applyProfileSettings
# Функция проверяет авторизован ли пользователь и совпадают ли данные в сессии
# Если всё правильно, собирает информаци с формы ввода данных и отправляет запрос на подтверждение
# Если всё прошло успешно, отправляет на личный кабинет пользователя с изменёнными данными
@app.route('/api/applyProfileSettings', methods=['POST'])
def apiApplyProfileSettings():
    # Если передаваемый метод запроса POST
    if request.method == 'POST':
        # Проверяем авторизован ли пользователь в текущей сессии
        if checkUserAuth():
            # Дальше проверяем тот ли пользователь пытается зайти в личный кабинет
            if er.checkUserTokens(session['user_token'], session['user']) == True:
                # Если всё правильно, получаем информацию о пользователе
                user = db.getUserData(session['user'])
                # Затем достаём информацию с формы ввода данных
                formData = request.form
                # Передаём информацию с формы ввода данных в функцию изменения данных
                if db.changeUserData(user, formData) == True:
                    # Если функция отработала правильно - перенаправляем на личный кабинет
                    return redirect('/cabinet')
                else:
                    # Иначе выводим ошибку, что данные не получилось изменить
                    flash("Не удалось изменить данные!")
                    # И перенаправляем на страницу изменения данных снова
                    return redirect('/api/changeProfileSettings')
            else:
                # Иначе перенаправляем на страницу с ошибкой 404
                return redirect('/not_found')
        else:
            # Иначе перенаправляем на страницу с ошибкой 404
            return redirect('/not_found')
    else:
        # Иначе перенаправляем на страницу с ошибкой 404
        return redirect('/not_found')

@app.route('/api/resetProfileSettings', methods=['POST'])
def resetProfileSettings():
    return redirect('/cabinet')

# Маршрут для запроса верификации (подтверждения) профиля пользователя
# ==
# Функция для обработки запроса /api/askForVerification
# Функция проверяет авторизован ли пользователь
# Если авторизован и сессия успешно совпадает
# Отправляет запрос в базу данных на подтверждение профиля пользователя
# Затем перенаправляет в личный кабинет пользователя
@app.route('/api/askForVerification', methods=['POST', 'GET'])
def apiAskForVerification():
    # Если пользователь авторизован
    if checkUserAuth():
        # Проверяем данные пользователя в текущей сессии
        # Тот ли пользователь пытается запросить верификацию
        if er.checkUserTokens(session['user_token'], session['user']) == True:
            # Запрашиваем верификацию в базе данных
            er.askForVerify(session['user'])
            # Подтверждаем верификацию пользователя
            er.verificateUser(session['user'])
            # Перенаправляем на страницу личного кабинета пользователя
            return redirect('/cabinet')
        else:
            # Иначе перенаправляем на страницу с ошибкой 404
            return redirect('/not_found')    
    else:
        # Иначе перенаправляем на страницу с ошибкой 404
        return redirect('/not_found')

# Маршрут для обработки функции поиска
# <string:userType> - параметр типа пользователя (студент, работодатель и место практики)
# ==
# Функция для обработки запроса /api/search/userType
# функция для работы поисковой системы
# Собирает данные с формы ввода для поиска, отправляет запрос в базу данных и сесиию
# Затем перенаправляет на необходимую страницу 
@app.route('/api/search/<string:userType>', methods=['POST'])
def apiSearch(userType):
    # Если поле поиска не пустое
    if request.form['searchText']:
        # Заполняем данные с формы ввода в текущую сессию
        session['search'] = request.form['searchText']
    else:
        # Если поле пустое, мы обнуляем информацию о поиске в сессии
        session.pop('search', None)

    # Проверяем тип пользователя для поиска среди них
    if userType == 'student':
        # Перенаправляем на страницу студентов
        return redirect('/students')
    elif userType == 'employer':
        # Перенаправляем на страницу работодателей
        return redirect('/employers')
    elif userType == 'workplace':
        # Перенаправляем на страницу мест практики
        return redirect('/workplaces')
    else:
        # Если типа нет, обнуляем поиск
        session.pop('search', None)
        # Иначе перенаправляем на страницу с ошибкой 404
        return redirect('/not_found')

# Маршрут для очистки поля поиска
# <string:userType> - параметр типа пользователя (студент, работодатель, место практики)
# ==
# Функция для обработки запроса /api/search/userType/flush
# Функция очищает текущую сессию от информации о поиске и перенаправляет на необходимую страницу
@app.route('/api/search/<string:userType>/flush', methods=['POST'])
def apiFlushSearch(userType):
    # Очищаем в сессии информацию о поиске
    session.pop("search", None)
    # Проходимся по типу пользователя 
    if userType == 'student':
        # Если поиск по студенту, перенаправляем на студентов
        return redirect('/students')
    elif userType == 'employer':
        # Если поиск по работодателям, перенаправляем на работодателей
        return redirect('/employers')
    elif userType == 'workplace':
        # Если поиск по местам практики, перенаправляем на места практики
        return redirect('/workplaces')
    else:
        # Иначе перенаправляем на страницу с ошибкой 404
        return redirect('/not_found')

# Маршрут для реализации работы фильтра данных
# <string:ftype> - тип обрабатываемого пользователя (студент, работодатель, место практики) 
# <string:filter> - тип текущего фильтра, по которому нужно отсеять данные
# <string:value> - по какому именно критерию нужно отсеять
# ==
# Функция для обработки запроса /api/filter/ftype/filter/value
# Функция проверяет переданный фильтр и обрабатывает информацию
# Затем проверяет тип передаваемого пользователя и перенаправляет на его страницу
@app.route('/api/filter/<string:ftype>/<string:filter>/<string:value>', methods=['POST'])
def apiFilterBy(ftype, filter, value):
    # Обрабатываем тип фильтра
    # Если тип фильтра это города
    if filter == 'cities':
        # Добавляем параметр фильтра в текущую сессию
        session['filter'] = value
        # Обрабатываем тип пользователя
        if ftype == 'workplace':
            # Если место практики, перенаправляем на места практики
            return redirect('/workplaces')
        elif ftype == 'employer':
            # Если работодатели, перенаправляем на работодателей
            return redirect('/employers')
        elif ftype == 'student':
            # Если студенты, перенаправляем на студентов
            return redirect('/students')
        else:
            # Иначе удаляем фильтр из сессии
            session.pop('filter', None)
            # Перенаправляем на страницу с ошибкой 404
            return redirect('/not_found')
    else:
        # Иначе перенаправляем на страницу с ошибкой 404
        return redirect('/not_found')

@app.route('/api/pingUser/<string:userType>/<string:userID>', methods=['POST', 'GET'])
def apiPingUser(userID, userType):
    if request.method == 'GET':
        if er.checkUserTokens(session['user_token'], session['user']):
            db.pingUser(session['user'], userID, userType)
            return redirect('/cabinet')
        else:
            return redirect('/not_found')
    else:
        return redirect('/not_found')

@app.route('/news', methods=['GET'])
def globalFeed():
    posts = db.getGlobalNewsFeed()
    return render_template('news.html', posts=posts, isAuthor=False, isAuth=checkUserAuth())

@app.route('/news/wp/<string:workplaceID>', methods=['GET'])
def getNewsByWP(workplaceID):
    if checkUserAuth():
        if er.checkUserTokens(session['user_token'], session['user']) == True:
            if db.isUserAuthor(session['user'], workplaceID):
                posts = db.getNewsByWorkplace(workplaceID)
                return render_template('news.html', posts=posts, isAuthor=True, isAuth=checkUserAuth())

    posts = db.getNewsByWorkplace(workplaceID)
    return render_template('news.html', posts=posts, isAuthor=False, isAuth=checkUserAuth())

@app.route('/api/publishPost', methods=['POST'])
def apiPublishPost():
    if request.method == 'POST':
        if checkUserAuth():
            if er.checkUserTokens(session['user_token'], session['user']) == True:
                db.addNewPost(request.form['postTitle'], request.form['postDescr'], request.form['postAcceptance'], session['user'])
                return redirect('/news')

    return redirect('/not_found')

# Обработчик ошибки 404 (страница не найдена)
# ==
# Функция для обработки запроса /not_found и ошибки 404
# Перенаправляет на страницу с шаблоном отрисовки ошибки
@app.errorhandler(404)
@app.route('/not_found')
def page_not_found(e):
    # Возвращаем шаблон страницы с ошибкой
    return render_template("error404.html"), 404

# Главная точка запуска программы
if __name__ == '__main__':
    app.run()