# BM@N Dashboard

## 1. Размер файлов в директории и размер события

Запускать с помощью `python filesize.py` (в папке `file_size`). Информация об аргументах `python filesize.py --help`

Есть конфиг файл, в котором описаны параметры выполнения
* SIZE - размер длдя перехода к следующей единице измерения
* UNITS - единицы измерения по порядку
* EXTENSIONS - расширения файлов, которые нужно рассматривать
* RUN_NUM_REGEX - регулярное выражение для поиска номера рана в названии файла
* UNI_DB_USERNAME, UNI_DB_PASSWORD, UNI_DB_NAME, UNI_DB_HOST - креденшиалы для подключения к БД
* DPI = 300 - dpi для сохранения картинок
* NAME_FILESIZE - название картинки с гистограммой размера файлов, если `None`, то картинка открывается а не сохраняется
* NAME_FILESIZE_PER_EVENT - название картинки с гистограммой размера события, если `None`, то картинка открывается а не сохраняется
* FOLDERS_IGNORE - папки, которые не нужно рассматривать

Сейчас сохраняется картинка с отмеченным линией средним и тайтлом, где написаны единицы измерения и среднее. Можно отправить информацию о среднем в какой-нибудь файл или же передать запросом куда-либо.


## 2. Обработка логов

Запускать с помощью `python log_time.py` (в папке `log_time`). Информация об аргументах `python log_time.py --help`

Есть конфиг файл, в котором описаны параметры выполнения
* SIZE - размер длдя перехода к следующей единице измерения
* UNITS - единицы измерения по порядку
* START - признак строки с информацией о начале выполнения
* END - признак строки с информацией о конце выполнения
* SUCCESS - признак успешного завершения работы
* START_REGEX - регулярное выражение для строки, содержащей время начала выполнения
* END_REGEX - регулярное выражение для строки, содержащей время конца выполнения
* MONTH_ARR - массив с названиями месяцев года как в лог файле
* EXCLUDED_EXTENSIONS - расширения, которые не рассматриваются
* UNSUCCESSFUL_OUT - название файла, в который нужно записать список некорректно завершившихся задач
* RUN_REGEX - регулярное выражение для поиска номера рана в названии файла
* RUN_EXTENSION - расширение файла с данными
* UNI_DB_USERNAME, UNI_DB_PASSWORD, UNI_DB_NAME, UNI_DB_HOST - креденшиалы для подключения к БД
* NAME_TIME - название картинки с гистограммой времени выполнения, если `None`, то картинка открывается а не сохраняется
* NAME_TIME_PER_EVENT - название картинки с гистограммой времени выполнения события, если `None`, то картинка открывается а не сохраняется
* DPI - dpi для сохранения картинок
* FOLDERS_IGNORE - папки, которые не нужно рассматривать

Установка необходимых библиотек происходит с помощью `pip install requirements.txt` или другим любым известным Вам способом.

Сейчас сохраняется картинка с отмеченным линией средним и тайтлом, где написаны единицы измерения и среднее. Можно отправить информацию о среднем в какой-нибудь файл или же передать запросом куда-либо.
Список некорректно завершившихся задач записывается в файл, это тоже можно поменять.

Примеры выполнения я специально добавила в репозиторий, чтобы можно было посмотреть результат, не скачивая и не запуская.

Если будут предложения, открывайте issue тут или пишите на почту (loooj58@gmail.com), в youtrack (https://npm.mipt.ru/youtrack/issue/NICA-27), в телеграм (ta_nyan).
