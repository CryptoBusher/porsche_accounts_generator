## Генератор аккаунтов для Porsche
Скрипт для загона аккаунтов в waitlist от Porsche. Первый скрипт прогоняет аккаунты нормально с прокси и без. Во время работы скрипта вас может банить сервис (вроде mailchimp) за мульты. Надо работать с прокси, наверное.

Связь с создателем: https://t.me/CrytoBusher <br>
Залетай сюда, чтоб не пропускать дропы подобных скриптов: https://t.me/CryptoKiddiesClub <br>
И сюда, чтоб общаться с крутыми ребятами: https://t.me/CryptoKiddiesChat <br>

## Особенности
1. Работа с прокси и без
2. Автоматическая регистрация почт
3. Мультипоток
4. Парсер ссылок из почтовых ящиков для подтверждения почт
5. Прохождение капчи с помощью сервиса anticaptcha

## Недостатки
1. Вроде их нет

## Логика работы
1. Запускаем первый скрипт (step_1)
2. Регистрируется новая почта
3. Оставляется заявка на waitlist на сайте Porsche с использованием новой почты
4. Сохраняются данные в файл "registered_accounts.txt"
5. Запускаем второй скрипт (step_2)
6. Все аккаунты из файла "registered_accounts.txt" проходят авторизацию
7. Проверяется почта
8. Если есть письмо от порша - парсится ссылка из письма
9. Происходит переход по ссылке, решается капча, сабмиттится аккаунт
10. Авторизированные аккаунты сохраняются в файл "authorized_accounts.txt"

## Первый запуск
1. Устанавливаем Python (желательно последнюю версию)
2. Открываем терминал, переходим в папку с файлами и пишем команду "pip install -r requirements.txt"
3. Если хотим юзать прокси - вбиваем их в файл "proxies.txt"  в формате "http://login:pass@host:port" (ipv4). Все с новой строки. В таком случае количество зарегистрированных аккаунтов будет равняться количеству прокси в текстовике. Если не хотим юзать прокси - оставляем пустой файл
4. Вюиваем API ключ от сервиса anticaptcha в "config.json" файл
5. Запускаем скрипт "step_1.py" (гуглите, если не знаете, как это делается)
6. После завершения ждем немного (чтоб письма от порша успели долететь) и запускаем скрипт "step_2.py"
