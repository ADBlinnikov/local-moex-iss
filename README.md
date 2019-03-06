## Тестовый вариант загрузки данных с iss.moex.com

1. Для запуска стэка: `docker-compose up -d`

2. На данный момент доступ к функциям осуществляется через вызов тестового ресурса и передачи имени вызываемого метода и необходимых параметров. Например:

   - Для запуска загрузки исторических данных за период : `curl -X http://localhost:8000/test?method=get_history_daterange&fromdate=2019-01-01&todate=2019-01-31&engine=futures&market=forts`

   - Для обновления данных по отсутсвующим в базе кодам бумаг: `curl -X http://localhost:8000/test?method=get_securities`
