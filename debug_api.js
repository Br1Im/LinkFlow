const c2bMembers = `
{
  "version": "1.0",
  "dictionary": [
    {
      "bankName": "Сбербанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000111.png",
      "schema": "bank100000000111",
      "package_name": "ru.sberbankmobile",
      "isDrActive": true
    },
    {
      "bankName": "Т-Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000004.png",
      "schema": "bank100000000004",
      "package_name": "com.idamob.tinkoff.android",
      "webClientUrl": "https://www.tinkoff.ru/mybank/payments/qr-pay",
      "webClientUrlSub": "https://www.tinkoff.ru/mybank/payments/qr-sub",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "Банк ВТБ",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000005.png",
      "schema": "bank110000000005",
      "package_name": "ru.vtb24.mobilebanking.android",
      "webClientUrl": "https://online.vtb.ru/i/paymentSbp",
      "webClientUrlSub": "https://online.vtb.ru/i/subscriptionSbp",
      "isWebClientActive": "true",
      "isDrActive": true
    },
    {
      "bankName": "АЛЬФА-БАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000008.png",
      "schema": "bank100000000008",
      "package_name": "ru.alfabank.mobile.android",
      "webClientUrl": "https://alfa-mobile.alfabank.ru/mobile-public/goto/qr",
      "webClientUrlSub": "https://alfa-mobile.alfabank.ru/mobile-public/goto/sub",
      "isWebClientActive": "true",
      "isDrActive": true,
      "param_separator": "/"
    },
    {
      "bankName": "Райффайзенбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000007.png",
      "schema": "bank100000000007",
      "package_name": "ru.raiffeisennews",
      "webClientUrl": "https://online.raiffeisen.ru/outer/qr/qr.nspk.ru",
      "webClientUrlSub": "https://online.raiffeisen.ru/pay-qr",
      "isWebClientActive": "true"
    },
    {
      "bankName": "Газпромбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000001.png",
      "schema": "bank100000000001",
      "package_name": "ru.gazprombank.android.mobilebank.app",
      "webClientUrl": "https://sbpgpb.ru/c2bpayments",
      "webClientUrlSub": "https://sbpgpb.ru/c2bsubscribe",
      "isWebClientActive": "true",
      "isDrActive": true,
      "param_separator": "/"
    },
    {
      "bankName": "Банк ПСБ",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000010.png",
      "schema": "bank100000000010",
      "package_name": "logo.com.mbanking",
      "webClientUrl": "https://ib.psbank.ru/sbp/payment",
      "webClientUrlSub": "https://ib.psbank.ru/sbp/subscription",
      "isWebClientActive": "true",
      "isDrActive": true,
      "param_separator": "/"
    },
    {
      "bankName": "Совкомбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000013.png",
      "schema": "bank100000000013",
      "package_name": "ru.sovcomcard.halva.v1",
      "webClientUrl": "https://halvacard.ru/lk/qr",
      "webClientUrlSub": "https://halvacard.ru/lk/qr",
      "isWebClientActive": "true",
      "isDrActive": false,
      "param_separator": "/"
    },
    {
      "bankName": "Россельхозбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000020.png",
      "schema": "bank100000000020",
      "package_name": "ru.rshb.dbo"
    },
    {
      "bankName": "МОСКОВСКИЙ КРЕДИТНЫЙ БАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000025.png",
      "schema": "bank100000000025",
      "package_name": "ru.mkb.mobile",
      "webClientUrl": "https://online.mkb.ru/go/c2b",
      "webClientUrlSub": "https://online.mkb.ru/go/c2b-sub",
      "isWebClientActive": "true"
    },
    {
      "bankName": "ЮниКредит Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000030.png",
      "schema": "bank100000000030",
      "package_name": "ru.unicredit.android",
      "webClientUrl": "https://enter.unicredit.ru/c2b",
      "webClientUrlSub": "https://enter.unicredit.ru/c2b",
      "isWebClientActive": "true"
    },
    {
      "bankName": "Банк Синара",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000003.png",
      "schema": "bank100000000003",
      "package_name": "ru.skbbank.ib",
      "isDrActive": true
    },
    {
      "bankName": "Газэнергобанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000043.png",
      "schema": "bank100000000043",
      "package_name": "ru.gebank.ib"
    },
    {
      "bankName": "АКБ АВАНГАРД",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000028.png",
      "schema": "bank100000000028",
      "package_name": "ru.avangard.sbp_client"
    },
    {
      "bankName": "ПНКО ЭЛПЛАТ",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000086.png",
      "schema": "bank100000000086",
      "package_name": "ru.elplat.elplat2"
    },
    {
      "bankName": "РНКБ филиал ВТБ",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000011.png",
      "schema": "bank100000000011",
      "package_name": "com.bifit.rncbbeta"
    },
    {
      "bankName": "Экспобанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000044.png",
      "schema": "bank100000000044",
      "package_name": "ru.ftc.faktura.expobank",
      "webClientUrl": "https://online.expobank.ru/fps/c2b",
      "webClientUrlSub": "https://online.expobank.ru/fps/c2b",
      "isWebClientActive": "true",
      "isDrActive": true,
      "param_separator": "/"
    },
    {
      "bankName": "Банк ВБРР",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000049.png",
      "schema": "bank100000000049",
      "package_name": "com.bssys.vbrrretail",
      "webClientUrl": "https://online.vbrr.ru/redirect_anchor/external/fps",
      "webClientUrlSub": "https://online.vbrr.ru/redirect_anchor/external/fps",
      "isWebClientActive": "true",
      "isDrActive": true
    },
    {
      "bankName": "АБ РОССИЯ",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000095.png",
      "schema": "bank100000000095",
      "package_name": "ru.artsofte.russiafl",
      "webClientUrl": "https://i2.abr.ru/c2b/qr",
      "webClientUrlSub": "https://i2.abr.ru/c2b/qr",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "ДБО Фактура",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000900.png",
      "schema": "bank100000000900",
      "package_name": "ru.ftc.faktura.multibank"
    },
    {
      "bankName": "КБ Хлынов",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000056.png",
      "schema": "bank100000000056",
      "package_name": "ru.bank_hlynov.xbank",
      "webClientUrl": "https://my.bank-hlynov.ru/sbp/qr",
      "webClientUrlSub": "https://my.bank-hlynov.ru/sbp/sub",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "Бланк банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000053.png",
      "schema": "bank100000000053",
      "package_name": "ru.ftc.faktura.vesta"
    },
    {
      "bankName": "КБ Солидарность",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000121.png",
      "schema": "bank100000000121",
      "package_name": "com.isimplelab.ibank.solidarnost"
    },
    {
      "bankName": "Банк ДОМ.РФ",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000082.png",
      "schema": "bank100000000082",
      "package_name": "com.bssys.roscapretail",
      "webClientUrl": "https://my.domrfbank.ru/app/sbp/c2b",
      "webClientUrlSub": "https://my.domrfbank.ru/app/sbp/c2b",
      "isWebClientActive": "true",
      "isDrActive": true,
      "param_separator": "/"
    },
    {
      "bankName": "Хакасский муниципальный банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000127.png",
      "schema": "bank100000000127",
      "package_name": "ru.ftc.faktura.kbhmb"
    },
    {
      "bankName": "МТС-Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000017.png",
      "schema": "bank100000000017",
      "package_name": "ru.mts.money",
      "isDrActive": true
    },
    {
      "bankName": "Банк ПСКБ",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000087.png",
      "schema": "bank100000000087",
      "package_name": "ru.ftc.faktura.pskb",
      "webClientUrl": "https://dbo.pscb.ru/fps/c2b",
      "webClientUrlSub": "https://dbo.pscb.ru/fps/c2b",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "Банк Левобережный",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000052.png",
      "schema": "bank100000000052",
      "package_name": "ru.ftc.faktura.nskbl",
      "webClientUrl": "https://bl-online.nskbl.ru/fps/c2b",
      "webClientUrlSub": "https://bl-online.nskbl.ru/fps/c2b",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "АК БАРС БАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000006.png",
      "schema": "bank100000000006",
      "package_name": "ru.akbars.mobile",
      "isDrActive": true
    },
    {
      "bankName": "КБ РостФинанс",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000098.png",
      "schema": "bank100000000098",
      "package_name": "ru.ftc.faktura.rostfinance",
      "webClientUrl": "https://online.rostfinance.ru/petition/c2b_sbp/qr",
      "webClientUrlSub": "https://online.rostfinance.ru/petition/c2b_sbp/qr",
      "isWebClientActive": "true"
    },
    {
      "bankName": "БыстроБанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000092.png",
      "schema": "bank100000000092",
      "webClientUrl": "https://www.bystrobank.ru/sbp/c2b",
      "webClientUrlSub": "https://www.bystrobank.ru/sbp/c2b",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "МС Банк Рус",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000229.png",
      "schema": "bank100000000229",
      "package_name": "ru.mcbankrus.MCBankRus"
    },
    {
      "bankName": "Кредит Европа Банк (Россия)",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000027.png",
      "schema": "bank100000000027"
    },
    {
      "bankName": "АКБ Алмазэргиэнбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000080.png",
      "schema": "bank100000000080",
      "package_name": "ru.albank.online.aebit"
    },
    {
      "bankName": "ИК Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000122.png",
      "schema": "bank100000000122",
      "package_name": "com.bifit.mobile.citizen.icbru"
    },
    {
      "bankName": "БАНК ОРЕНБУРГ",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000124.png",
      "schema": "bank100000000124",
      "package_name": "ru.ftc.faktura.orbank"
    },
    {
      "bankName": "АКБ Энергобанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000159.png",
      "schema": "bank100000000159",
      "package_name": "com.energobank.digital"
    },
    {
      "bankName": "КОШЕЛЕВ-БАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000146.png",
      "schema": "bank100000000146",
      "package_name": "com.bifit.mobile.citizen.kbnk"
    },
    {
      "bankName": "СДМ-Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000069.png",
      "schema": "bank100000000069",
      "package_name": "ru.ftc.faktura.sdm",
      "webClientUrl": "https://online.sdm.ru/fps/c2b",
      "webClientUrlSub": "https://online.sdm.ru/fps/c2b",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "МБ Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000140.png",
      "schema": "bank100000000140",
      "package_name": "com.bifit.mobile.citizen.mbb"
    },
    {
      "bankName": "АКБ Абсолют Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000047.png",
      "schema": "bank100000000047",
      "package_name": "ru.ftc.faktura.absolutbank",
      "webClientUrl": "https://online.absolutbank.ru/fps/c2b",
      "webClientUrlSub": "https://online.absolutbank.ru/fps/c2b",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "КБ Модульбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000099.png",
      "schema": "bank100000000099",
      "package_name": "ru.ftc.faktura.multibank"
    },
    {
      "bankName": "Банк Акцепт",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000135.png",
      "schema": "bank100000000135",
      "package_name": "ru.ftc.faktura.akcept",
      "webClientUrl": "https://dbo.akcept.ru/fps/c2b",
      "webClientUrlSub": "https://dbo.akcept.ru/fps/c2b",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "КБ ЭНЕРГОТРАНСБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000139.png",
      "schema": "bank100000000139",
      "package_name": "ru.ftc.faktura.etbank",
      "webClientUrl": "https://online.energotransbank.com/fps/c2b",
      "webClientUrlSub": "https://online.energotransbank.com/fps/c2b",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "СИБСОЦБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000166.png",
      "schema": "bank100000000166",
      "package_name": "ru.ftc.faktura.multibank"
    },
    {
      "bankName": "Банк Развитие-Столица",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000172.png",
      "schema": "bank100000000172",
      "package_name": "ru.ftc.faktura.razvitiestolica"
    },
    {
      "bankName": "Банк РЕСО Кредит",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000187.png",
      "schema": "bank100000000187",
      "package_name": "ru.ftc.faktura.resokreditbank"
    },
    {
      "bankName": "НКО ЮМани",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000022.png",
      "schema": "bank100000000022",
      "package_name": "ru.yoo.money"
    },
    {
      "bankName": "Банк Санкт-Петербург",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000029.png",
      "schema": "bank100000000029",
      "package_name": "ru.bspb"
    },
    {
      "bankName": "КБ Кубань Кредит",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000050.png",
      "schema": "bank100000000050",
      "package_name": "com.isimplelab.ibank.kubankredit"
    },
    {
      "bankName": "Банк НОВИКОМ (НОВИКОМБАНК)",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000177.png",
      "schema": "bank100000000177",
      "package_name": "com.bssys.novikomretail",
      "isDrActive": true
    },
    {
      "bankName": "РосДорБанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000084.png",
      "schema": "bank100000000084",
      "package_name": "ru.rosdorbank.physical"
    },
    {
      "bankName": "СКБ Приморья Примсоцбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000088.png",
      "schema": "bank100000000088",
      "package_name": "ru.ftc.faktura.primsoc",
      "webClientUrl": "https://psl.pskb.com/fps/c2b",
      "webClientUrlSub": "https://psl.pskb.com/fps/c2b",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "Банк Саратов",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000126.png",
      "schema": "bank100000000126",
      "package_name": "ru.ftc.faktura.banksaratov"
    },
    {
      "bankName": "Тольяттихимбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000152.png",
      "schema": "bank100000000152",
      "package_name": "com.bifit.mobile.citizen.thbank"
    },
    {
      "bankName": "Банк Кремлевский",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000201.png",
      "schema": "bank100000000201",
      "package_name": "ru.ftc.faktura.kremlevskiy",
      "webClientUrl": "http://dbo.kremlinbank.ru/fps/c2b",
      "webClientUrlSub": "http://dbo.kremlinbank.ru/fps/c2b",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "ТКБ БАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000034.png",
      "schema": "bank100000000034",
      "package_name": "ru.ftc.faktura.tkbbank",
      "webClientUrl": "https://lk.tkbbank.ru/petition/c2b_sbp/qr",
      "webClientUrlSub": "https://lk.tkbbank.ru/petition/sbp_create_subscription/qr",
      "isWebClientActive": "true",
      "isDrActive": false
    },
    {
      "bankName": "ЧЕЛЯБИНВЕСТБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000094.png",
      "schema": "bank100000000094",
      "package_name": "ru.chelyabinvestbank.investpay"
    },
    {
      "bankName": "АКБ Держава",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000235.png",
      "schema": "bank100000000235",
      "package_name": "ru.ftc.faktura.derzhava"
    },
    {
      "bankName": "НБД-Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000134.png",
      "schema": "bank100000000134",
      "package_name": "ru.nbd.android"
    },
    {
      "bankName": "БАНК СНГБ",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000091.png",
      "schema": "bank100000000091",
      "package_name": "ru.sngb.dbo.client.android"
    },
    {
      "bankName": "АИКБ Енисейский объединенный банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000258.png",
      "schema": "bank100000000258",
      "package_name": "ru.ftc.faktura.united",
      "webClientUrl": "https://online.united.ru/fps/c2b",
      "webClientUrlSub": "https://online.united.ru/fps/c2b",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "Банк Венец",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000153.png",
      "schema": "bank100000000153",
      "package_name": "ru.ftc.faktura.venetsbank"
    },
    {
      "bankName": "Почта Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000016.png",
      "schema": "bank100000000016",
      "package_name": "ru.letobank.Prometheus"
    },
    {
      "bankName": "Банк Русский Стандарт",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000014.png",
      "schema": "bank100000000014",
      "package_name": "ru.simpls.brs2.mobbank"
    },
    {
      "bankName": "Дальневосточный банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000083.png",
      "schema": "bank100000000083",
      "package_name": "com.bifit.dvbank"
    },
    {
      "bankName": "Банк Интеза",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000170.png",
      "schema": "bank100000000170",
      "package_name": "ru.ftc.faktura.intesabank"
    },
    {
      "bankName": "ГЕНБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000037.png",
      "schema": "bank100000000037",
      "package_name": "com.mmonline.mobile"
    },
    {
      "bankName": "УРАЛПРОМБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000142.png",
      "schema": "bank100000000142",
      "package_name": "ru.uralprombank.mobilebanknew.googleplay"
    },
    {
      "bankName": "Банк Национальный стандарт",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000243.png",
      "schema": "bank100000000243",
      "package_name": "ru.ftc.faktura.nsbank"
    },
    {
      "bankName": "Банк Екатеринбург",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000090.png",
      "schema": "bank100000000090",
      "package_name": "ru.emb.android"
    },
    {
      "bankName": "МОРСКОЙ БАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000171.png",
      "schema": "bank100000000171",
      "package_name": "ru.ftc.faktura.maritimebank"
    },
    {
      "bankName": "Кредит Урал Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000064.png",
      "schema": "bank100000000064",
      "package_name": "com.credituralbank.CUBmobilenew",
      "webClientUrl": "https://direct.creditural.ru/mobile/",
      "webClientUrlSub": "https://direct.creditural.ru/mobile/",
      "isWebClientActive": "true"
    },
    {
      "bankName": "Углеметбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000093.png",
      "schema": "bank100000000093",
      "package_name": "com.isimplelab.isimpleceo.uglemet"
    },
    {
      "bankName": "Авто Финанс Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000253.png",
      "schema": "bank100000000253",
      "package_name": "ru.ftc.faktura.multibank"
    },
    {
      "bankName": "КБ СТРОЙЛЕСБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000193.png",
      "schema": "bank100000000193",
      "package_name": "com.bssys.stroylesretail"
    },
    {
      "bankName": "Банк ИТУРУП",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000158.png",
      "schema": "bank100000000158",
      "package_name": "ru.ftc.faktura.iturup",
      "webClientUrl": "https://pay.iturup.online/fps/c2b",
      "webClientUrlSub": "https://pay.iturup.online/fps/c2b",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "Первый Инвестиционный Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000174.png",
      "schema": "bank100000000174",
      "package_name": "ru.ftc.faktura.finbank"
    },
    {
      "bankName": "Газтрансбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000183.png",
      "schema": "bank100000000183",
      "package_name": "ru.ftc.faktura.gaztransbank"
    },
    {
      "bankName": "ЧЕЛИНДБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000106.png",
      "schema": "bank100000000106",
      "package_name": "com.isimplelab.ibank.chelind",
      "webClientUrl": "https://ibf.chelindbank.ru/fps/c2b",
      "webClientUrlSub": "https://ibf.chelindbank.ru/fps/c2b",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "НИКО-БАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000115.png",
      "schema": "bank100000000115",
      "package_name": "ru.ftc.faktura.multibank"
    },
    {
      "bankName": "НОКССБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000062.png",
      "schema": "bank100000000062",
      "package_name": "ru.ftc.faktura.nokss"
    },
    {
      "bankName": "ВЛАДБИЗНЕСБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000058.png",
      "schema": "bank100000000058",
      "package_name": "ru.ftc.faktura.vlbb"
    },
    {
      "bankName": "Кузнецкбизнесбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000195.png",
      "schema": "bank100000000195",
      "package_name": "ru.ftc.faktura.kbb"
    },
    {
      "bankName": "Томскпромстройбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000206.png",
      "schema": "bank100000000206",
      "package_name": "ru.ftc.faktura.multibank"
    },
    {
      "bankName": "АКБ МЕЖДУНАРОДНЫЙ ФИНАНСОВЫЙ КЛУБ",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000203.png",
      "schema": "bank100000000203",
      "package_name": "ru.ftc.faktura.mfkbank"
    },
    {
      "bankName": "АКБ Форштадт",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000081.png",
      "schema": "bank100000000081",
      "package_name": "ru.ftc.faktura.forshtadt"
    },
    {
      "bankName": "АКБ Солид",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000230.png",
      "schema": "bank100000000230",
      "package_name": "ru.ftc.faktura.solidbank"
    },
    {
      "bankName": "Банк АЛЕКСАНДРОВСКИЙ",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000211.png",
      "schema": "bank100000000211",
      "package_name": "ru.ftc.faktura.alexbank",
      "webClientUrl": "https://online.abank.ru/fps/c2b",
      "webClientUrlSub": "https://online.abank.ru/fps/c2b",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "АКИБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000107.png",
      "schema": "bank100000000107",
      "package_name": "ru.ftc.faktura.akibank"
    },
    {
      "bankName": "Нацинвестпромбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000185.png",
      "schema": "bank100000000185",
      "package_name": "ru.ftc.faktura.nipbank"
    },
    {
      "bankName": "АКБ Алеф-Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000113.png",
      "schema": "bank100000000113",
      "package_name": "ru.ftc.faktura.alefbank"
    },
    {
      "bankName": "КБ ВНЕШФИНБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000248.png",
      "schema": "bank100000000248",
      "package_name": "com.bifit.vfbank"
    },
    {
      "bankName": "Дом.ру (Урал ФД)",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000151.png",
      "schema": "bank100000000151",
      "package_name": "com.bssys.uralfdretail"
    },
    {
      "bankName": "КБ АРЕСБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000129.png",
      "schema": "bank100000000129",
      "package_name": "ru.ftc.faktura.multibank"
    },
    {
      "bankName": "Северный Народный Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000208.png",
      "schema": "bank100000000208",
      "package_name": "com.snb.online"
    },
    {
      "bankName": "Банк Объединенный капитал",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000182.png",
      "schema": "bank100000000182",
      "package_name": "com.bifit.mobile.citizen.okbank"
    },
    {
      "bankName": "ТАТСОЦБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000189.png",
      "schema": "bank100000000189",
      "package_name": "com.tatsotsbank.dbomobile"
    },
    {
      "bankName": "Норвик Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000202.png",
      "schema": "bank100000000202",
      "package_name": "ru.vtkbank.android"
    },
    {
      "bankName": "НС Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000071.png",
      "schema": "bank100000000071",
      "package_name": "ru.ftc.faktura.ns"
    },
    {
      "bankName": "Земский банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000066.png",
      "schema": "bank100000000066",
      "package_name": "ru.ftc.faktura.zemskybank"
    },
    {
      "bankName": "Банк Аверс",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000154.png",
      "schema": "bank100000000154",
      "package_name": "com.bssys.aversretail"
    },
    {
      "bankName": "КБ РУСНАРБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000194.png",
      "schema": "bank100000000194",
      "package_name": "ru.rusnarbank.correqts.retail",
      "webClientUrl": "https://online.rusnarbank.ru/#/external/fps",
      "webClientUrlSub": "https://online.rusnarbank.ru/#/external/fps",
      "isWebClientActive": "true"
    },
    {
      "bankName": "РЕАЛИСТ БАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000232.png",
      "schema": "bank100000000232",
      "package_name": "ru.ftc.faktura.baikalinvestbank"
    },
    {
      "bankName": "Эс-Би-Ай Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000105.png",
      "schema": "bank100000000105",
      "package_name": "ru.sbi.android"
    },
    {
      "bankName": "МЕТКОМБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000136.png",
      "schema": "bank100000000136",
      "package_name": "com.metkombank.mobile"
    },
    {
      "bankName": "КБЭР Банк Казани",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000191.png",
      "schema": "bank100000000191",
      "package_name": "com.isimplelab.ionic.kazan.fl"
    },
    {
      "bankName": "АКБ Трансстройбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000197.png",
      "schema": "bank100000000197",
      "package_name": "com.intervale.sbp.atlas"
    },
    {
      "bankName": "Банк Заречье",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000205.png",
      "schema": "bank100000000205",
      "package_name": "com.bifit.mobile.citizen.zarech"
    },
    {
      "bankName": "КБ Центр-инвест",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000059.png",
      "schema": "bank100000000059",
      "package_name": "ru.centrinvest.mobilebanking2018"
    },
    {
      "bankName": "Датабанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000070.png",
      "schema": "bank100000000070",
      "package_name": "com.mifors.izhcombank"
    },
    {
      "bankName": "СОЦИУМ-БАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000223.png",
      "schema": "bank100000000223",
      "package_name": "com.intervale.sbp.atlas"
    },
    {
      "bankName": "КБ СИНКО-БАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000148.png",
      "schema": "bank100000000148",
      "package_name": "com.intervale.sbp.atlas"
    },
    {
      "bankName": "ИШБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000199.png",
      "schema": "bank100000000199",
      "package_name": "com.bifit.pmobile.isbank"
    },
    {
      "bankName": "Банк ЗЕНИТ",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000045.png",
      "schema": "bank100000000045",
      "package_name": "ru.zenit.android",
      "webClientUrl": "https://i.zenit.ru/sbpPay",
      "webClientUrlSub": "https://i.zenit.ru/sbpSub",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "АКБ ФОРА-БАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000217.png",
      "schema": "bank100000000217",
      "package_name": "ru.briginvest.sense"
    },
    {
      "bankName": "МП Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000169.png",
      "schema": "bank100000000169",
      "package_name": "ru.ftc.faktura.multibank"
    },
    {
      "bankName": "ГОРБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000125.png",
      "schema": "bank100000000125",
      "package_name": "com.isimplelab.ionic.gorbank.prod"
    },
    {
      "bankName": "МОСКОМБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000176.png",
      "schema": "bank100000000176",
      "package_name": "ru.ftc.faktura.moscombank"
    },
    {
      "bankName": "Тимер Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000144.png",
      "schema": "bank100000000144",
      "package_name": "com.timerbank.retail"
    },
    {
      "bankName": "Автоторгбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000181.png",
      "schema": "bank100000000181",
      "package_name": "com.bifit.atbbank"
    },
    {
      "bankName": "БАНК УРАЛСИБ",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000026.png",
      "schema": "bank100000000026",
      "package_name": "ru.bankuralsib.mb.android",
      "webClientUrl": "https://online.uralsib.ru/sbp-pay",
      "webClientUrlSub": "https://online.uralsib.ru/sbp-pay",
      "isWebClientActive": "true"
    },
    {
      "bankName": "Инго Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000078.png",
      "schema": "bank100000000078",
      "package_name": "com.banksoyuz.artsofte",
      "isDrActive": true
    },
    {
      "bankName": "Русьуниверсалбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000165.png",
      "schema": "bank100000000165",
      "package_name": "ru.rubank.ubsmobile"
    },
    {
      "bankName": "КБ УБРиР",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000031.png",
      "schema": "bank100000000031",
      "package_name": "cb.ibank"
    },
    {
      "bankName": "АКБ Приморье",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000226.png",
      "schema": "bank100000000226",
      "package_name": "ru.ftc.faktura.multibank"
    },
    {
      "bankName": "Банк ИПБ",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000236.png",
      "schema": "bank100000000236",
      "package_name": "ru.ipb.ubsmobile",
      "webClientUrl": "https://on-line.ipb.ru/sbp",
      "webClientUrlSub": "https://on-line.ipb.ru/sbp",
      "isWebClientActive": "true"
    },
    {
      "bankName": "КБ Пойдём!",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000103.png",
      "schema": "bank100000000103",
      "package_name": "com.openwaygroup.ic.panda.poidem"
    },
    {
      "bankName": "АКБ ТЕНДЕР-БАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000175.png",
      "schema": "bank100000000175",
      "package_name": "com.bifit.mobile.citizen.tenderbank"
    },
    {
      "bankName": "ОТП Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000018.png",
      "schema": "bank100000000018",
      "package_name": "ru.otpbank.mobile"
    },
    {
      "bankName": "КБ Крокус-Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000212.png",
      "schema": "bank100000000212",
      "package_name": "ru.krk.ubsmobile"
    },
    {
      "bankName": "Ренессанс Банк (Ренессанс Кредит)",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000032.png",
      "schema": "bank100000000032",
      "package_name": "cz.bsc.rc"
    },
    {
      "bankName": "УКБ Белгородсоцбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000225.png",
      "schema": "bank100000000225",
      "package_name": "com.bifit.mobile.citizen.belsocbank"
    },
    {
      "bankName": "Хайс Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000272.png",
      "schema": "bank100000000272",
      "package_name": "com.hicebank.android"
    },
    {
      "bankName": "Севергазбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000219.png",
      "schema": "bank100000000219",
      "package_name": "com.bpc.crossplatform_trading.bpc_trading"
    },
    {
      "bankName": "АКБ НРБанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000184.png",
      "schema": "bank100000000184",
      "package_name": "com.bifit.nrb"
    },
    {
      "bankName": "КБ Москоммерцбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000110.png",
      "schema": "bank100000000110",
      "package_name": "com.bifit.mobile.citizen.moskb"
    },
    {
      "bankName": "Кубаньторгбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000180.png",
      "schema": "bank100000000180",
      "package_name": "ru.isfront.android.kt"
    },
    {
      "bankName": "УКБ Новобанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000222.png",
      "schema": "bank100000000222",
      "package_name": "ru.ftc.faktura.novobank"
    },
    {
      "bankName": "НК Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000233.png",
      "schema": "bank100000000233",
      "package_name": "com.bifit.mobile.citizen.nkbank",
      "webClientUrl": "https://sbp.nkbank.ru/sbp/c2b",
      "webClientUrlSub": "https://sbp.nkbank.ru/sbp/c2b",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "Тойота Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000138.png",
      "schema": "bank100000000138",
      "package_name": "com.isimplelab.ibank.toyota"
    },
    {
      "bankName": "ББР Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000133.png",
      "schema": "bank100000000133",
      "package_name": "com.bifit.mobile.private.bbr"
    },
    {
      "bankName": "АКБ Ланта-Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000245.png",
      "schema": "bank100000000245",
      "package_name": "ru.ftc.faktura.lanta",
      "webClientUrl": "https://dbo.lanta.ru/fps/c2b",
      "webClientUrlSub": "https://dbo.lanta.ru/fps/c2b",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "КБ Долинск",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000270.png",
      "schema": "bank100000000270",
      "package_name": "ru.ftc.faktura.dolinsk"
    },
    {
      "bankName": "Банк Финсервис",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000216.png",
      "schema": "bank100000000216",
      "package_name": "com.finservice.mobile"
    },
    {
      "bankName": "КБ ЮНИСТРИМ",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000042.png",
      "schema": "bank100000000042",
      "package_name": "com.ltech.unistream"
    },
    {
      "bankName": "КБ Новый век",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000067.png",
      "schema": "bank100000000067",
      "package_name": "com.isimplelab.ionic.standart"
    },
    {
      "bankName": "Банк МБА-МОСКВА",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000192.png",
      "schema": "bank100000000192",
      "package_name": "ru.ibam.retailmobile"
    },
    {
      "bankName": "БКС Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000041.png",
      "schema": "bank100000000041",
      "package_name": "ru.bcs.bcsbank",
      "webClientUrl": "https://bcs-bank.ru/nspklink",
      "webClientUrlSub": "https://bcs-bank.ru/nspksublink",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "АКБ СЛАВИЯ",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000200.png",
      "schema": "bank100000000200",
      "package_name": "com.isimplelab.ionic.slavia.prod"
    },
    {
      "bankName": "АКБ ЕВРОФИНАНС МОСНАРБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000167.png",
      "schema": "bank100000000167",
      "package_name": "com.bifit.mobile.citizen.efbank"
    },
    {
      "bankName": "Яндекс",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000150.png",
      "schema": "bank100000000150",
      "package_name": "com.yandex.bank"
    },
    {
      "bankName": "Банк БЖФ",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000260.png",
      "schema": "bank100000000260",
      "package_name": "ru.ftc.faktura.bgfbank"
    },
    {
      "bankName": "КБ ЛОКО-Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000161.png",
      "schema": "bank100000000161",
      "package_name": "com.idamobile.android.LockoBank"
    },
    {
      "bankName": "БАНК МОСКВА-СИТИ",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000234.png",
      "schema": "bank100000000234",
      "package_name": "com.bifit.mobile.citizen.MCBank"
    },
    {
      "bankName": "ГУТА-БАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000149.png",
      "schema": "bank100000000149",
      "package_name": "com.bssys.gutaretail"
    },
    {
      "bankName": "ФИНСТАР БАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000278.png",
      "schema": "bank100000000278",
      "package_name": "ru.ftc.faktura.siab"
    },
    {
      "bankName": "банк Раунд",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000247.png",
      "schema": "bank100000000247",
      "package_name": "com.isimplelab.ionic.round.prod"
    },
    {
      "bankName": "Прио-Внешторгбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000228.png",
      "schema": "bank100000000228",
      "package_name": "com.priobank.prio"
    },
    {
      "bankName": "Инбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000196.png",
      "schema": "bank100000000196",
      "package_name": "com.inbank.mobilebank"
    },
    {
      "bankName": "Уралфинанс",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000096.png",
      "schema": "bank100000000096",
      "package_name": "com.isimplelab.isimplemobile.payjet"
    },
    {
      "bankName": "Банк Агророс",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000102.png",
      "schema": "bank100000000102",
      "package_name": "ru.ftc.faktura.agroros",
      "webClientUrl": "https://my.agroros.ru/fps/c2b",
      "webClientUrlSub": "https://my.agroros.ru/fps/c2b",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "ЮГ-Инвестбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000160.png",
      "schema": "bank100000000160",
      "package_name": "com.bifit.mobile.citizen.invb"
    },
    {
      "bankName": "ЦентроКредит",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000231.png",
      "schema": "bank100000000231",
      "package_name": "com.compassplus.mobicash.customer"
    },
    {
      "bankName": "Снежинский",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000163.png",
      "schema": "bank100000000163",
      "package_name": "com.compassplus.mobicash.customer"
    },
    {
      "bankName": "Банк ФИНАМ",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000040.png",
      "schema": "bank100000000040",
      "package_name": "ru.finambank.app"
    },
    {
      "bankName": "Банк Точка",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000284.png",
      "schema": "bank100000000284",
      "package_name": "ru.zhuck.webapp",
      "webClientUrl": "https://i.tochka.com/a/sbp_c2b",
      "webClientUrlSub": "https://i.tochka.com/a/sbp_c2b",
      "isWebClientActive": "true"
    },
    {
      "bankName": "банк Элита",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000266.png",
      "schema": "bank100000000266",
      "package_name": ""
    },
    {
      "bankName": "Металлинвестбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000046.png",
      "schema": "bank100000000046",
      "package_name": ""
    },
    {
      "bankName": "ПроБанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000117.png",
      "schema": "bank100000000117",
      "webClientUrl": "https://bk.probank.pro/a567/",
      "webClientUrlSub": "https://bk.probank.pro/a567/",
      "isWebClientActive": "true"
    },
    {
      "bankName": "Цифра банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000265.png",
      "schema": "bank100000000265",
      "package_name": ""
    },
    {
      "bankName": "Озон Банк (Ozon)",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000273.png",
      "schema": "bank100000000273",
      "package_name": ""
    },
    {
      "bankName": "Первый Дортрансбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000137.png",
      "schema": "bank100000000137",
      "package_name": ""
    },
    {
      "bankName": "ЦМРБанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000282.png",
      "schema": "bank100000000282",
      "package_name": ""
    },
    {
      "bankName": "Плайт",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000296.png",
      "schema": "bank100000000296",
      "webClientUrl": "https://plait.ru/lk/qr",
      "webClientUrlSub": "https://plait.ru/lk/qr",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "Банк Оранжевый",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000286.png",
      "schema": "bank100000000286"
    },
    {
      "bankName": "ИКБР ЯРИНТЕРБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000293.png",
      "schema": "bank100000000293"
    },
    {
      "bankName": "РНКО Платежный конструктор",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000288.png",
      "schema": "bank100000000288"
    },
    {
      "bankName": "Азиатско-Тихоокеанский Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000108.png",
      "schema": "bank100000000108"
    },
    {
      "bankName": "Вайлдберриз Банк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000259.png",
      "schema": "bank100000000259"
    },
    {
      "bankName": "Экономбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000198.png",
      "schema": "bank100000000198"
    },
    {
      "bankName": "Ставропольпромстройбанк",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000267.png",
      "schema": "bank100000000267"
    },
    {
      "bankName": "НКО Мобильная карта",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000271.png",
      "schema": "bank100000000271",
      "webClientUrl": "https://wallet.1cupis.ru/qr",
      "webClientUrlSub": "https://wallet.1cupis.ru/qr",
      "isWebClientActive": "true",
      "param_separator": "/"
    },
    {
      "bankName": "МТС Деньги (ЭКСИ Банк)",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000289.png",
      "schema": "bank100000000289"
    },
    {
      "bankName": "ЖИВАГО БАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000295.png",
      "schema": "bank100000000295"
    },
    {
      "bankName": "РОКЕТБАНК",
      "logoURL": "https://qr.nspk.ru/proxyapp/logo/bank100000000301.png",
      "schema": "bank100000000301"
    }
  ]
}
`;

var sbpStrategyIsDefined = false;
var sberpayStrategyIsDefined = false;
var isFirstSberpayClick = false;
const LogoDark = "/nova/img/icons/logo-dark.svg";
const Logo = "/nova/img/icons/logo.svg";
let updatePaymentStateHandle = null;
let checkLiveStatusHandle = checkLiveStatus();


function isMobile() {
    return /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
}

function ajaxPost(form, callback) {

    let url = form.action;
    url = addRandomNumber(url);
    const xhr = new XMLHttpRequest();
    let params = [].filter.call(form.elements, function () {
        return true;
    })
        .filter(function (el) {
            return !!el.name;
        })
        .map(function (el) {
            return encodeURIComponent(el.name) + '=' + encodeURIComponent(el.value);
        }).join('&');

    xhr.open("POST", url);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.timeout = 15000;
    xhr.onload = callback.bind(xhr);

    xhr.onerror = function () {
    };

    xhr.ontimeout = function () {
    };

    let extParams = '';
    try {
        extParams = '&extParams=' + window.btoa(getExtInfo());
    } catch (e) {
        console.error('getExtInfo failed:', e);
    }

    const baseBody = params + extParams + '&json=1';

    function sendWithExtras(extra) {
        const body = baseBody + (extra || '');
        xhr.send(body);
    }

    if (typeof fpPromise !== 'undefined') {
        const fpTimeoutMs = 1500;
        Promise.race([
            fpPromise.then(fp => fp.get()).catch(() => null),
            new Promise(resolve => setTimeout(() => resolve(null), fpTimeoutMs))
        ])
            .then(result => {
                let extra = '';
                if (result && result.visitorId) {
                    extra += '&visitorId=' + encodeURIComponent(result.visitorId);
                }
                if (result && result.requestId) {
                    extra += '&requestId=' + encodeURIComponent(result.requestId);
                }
                sendWithExtras(extra);
            })
            .catch(err => {
                console.error('fpPromise error:', err);
                sendWithExtras('');
            });
    } else {
        sendWithExtras('');
    }
}


function checkLiveStatus() {
    if (document.getElementById('checklivestatus')) {
        return window.setInterval(() => {
            var url = addRandomNumber('?checkLiveStatus=1');
            fetch(url)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(`HTTP error. Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then((data) => {
                    if (data.status !== 1) {
                        window.location = 'https://' + location.hostname;
                    }
                })
                .catch((error) => {
                    console.error('checkLiveStatus error:', error);
                });
        }, 10000);
    } else {
        return false;
    }
}


function createHiddenForm(data, target = '') {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = data.url;
    if (target) {
        form.target = target;
    }
    data.postData.forEach(function (input) {
        const el = document.createElement('input');
        el.setAttribute('type', 'hidden');
        el.value = input.value;
        el.name = input.name;
        form.appendChild(el);
    });
    return form;
}

function handleDrawElement(data) {
    const icons = {
        fail: "/nova/img/icons/toast-error-light.svg",
        success: "/nova/img/icons/toast-check.svg",
        warning: "/nova/img/icons/toast-error-dark.svg"
    };
    const typeMap = {
        fail: "error"
    };
    if (data.elements) {
        for (const [type, text] of Object.entries(data.elements)) {
            Toastify({
                text: `
                        <div class="alert-content">
                          <img src="${icons[type]}" alt="toast-icon">
                          <span class="alert-text">${text}</span>
                        </div>
                     `,
                duration: 60000,
                close: true,
                gravity: isMobile() ? "top" : "bottom",
                position: (isMobile() || window.innerWidth < 768) ? "center" : "right",
                className: `alert-box box-${typeMap[type]}`,
                escapeMarkup: false

            }).showToast();
        }
    }
    changeFormState(document.forms[0], false);
    const formButton = document.getElementById("formButton");
    if (formButton) {
        formButton.classList.remove("loading");
        formButton.classList.remove("inactive");
        formButton.classList.add("active");
        formButton.disabled = false;
    }
    checkLiveStatusHandle = checkLiveStatus();
}

function handleSetPaymentStatusCheck(data) {
    if (updatePaymentStateHandle) window.clearInterval(updatePaymentStateHandle);
    globalThis.appSign = data.sign;
    globalThis.appPaymentId = data.paymentId;
    var url = '/pp/' + data.paymentId + '/?checkPaymentState=1&sign=' + data.sign;
    updatePaymentStateHandle = updatePaymentState(url);
}

function handlePostRedirect(data) {
    clearInterval(updatePaymentStateHandle);
    let form = createHiddenForm(data);
    document.body.appendChild(form);
    form.submit();
}

function handleQrCode(data) {
    if (isMobile()) {
        if (!sbpStrategyIsDefined) {
            let formConfig = window.getFormJsonConfig();
            const currentCase = formConfig.mobileBehavior.type;
            defineSbpStrategy(currentCase, data.url);
            sbpStrategyIsDefined = true;
            toggleLoader();
        }
    } else {
        var qrCodeContainer = document.getElementById("qr-code");
        if (!qrCodeContainer) {
            genQR(data.url, "formQRCodeWrapper");
            toggleLoader();
        }
    }
    if (updatePaymentStateHandle) window.clearInterval(updatePaymentStateHandle);
    var url = '/pp/' + data.order_id + '/?checkPaymentState=1&sign=' + data.sign;
    updatePaymentStateHandle = updatePaymentState(url);
}

function handleIframe(data) {
    const existedIframe = document.getElementById('iframeProcessWindow');
    if (existedIframe !== null) {
        //if (updatePaymentStateHandle) window.clearInterval(updatePaymentStateHandle);
    } else {
        const iframe = document.createElement('iframe');
        iframe.id = 'iframeProcessWindow';
        iframe.classList.add("iframe-modal")
        iframe.src = data.url;
        document.getElementsByClassName('iframe-holder')[0].replaceWith(iframe);
        iframe.addEventListener('load', () => {
        });
    }
}

function handleIframeHidden(data) {
    const existedHiddenIframe = document.getElementById('iframeHiddenWindow');
    if (existedHiddenIframe !== null) {
        //if (updatePaymentStateHandle) window.clearInterval(updatePaymentStateHandle);
    } else {
        const iframe = document.createElement('iframe');
        iframe.id = 'iframeHiddenWindow';
        iframe.name = 'iframeHiddenName';
        iframe.style.display = 'none';
        document.body.appendChild(iframe);
        const form = document.createElement('form');
        form.method = 'POST';
        form.target = 'iframeHiddenName';
        form.action = data.url;
        form.style.display = 'none';
        data.postData.forEach(function (input) {
            const el = document.createElement('input');
            el.setAttribute('type', 'hidden');
            el.value = input.value;
            el.name = input.name;
            form.appendChild(el);
        });
        document.body.appendChild(form);
        let finished = false;
        let timeoutId = null;

        function notifyOnce() {
            if (finished) return;
            finished = true;
            if (timeoutId) {
                clearTimeout(timeoutId);
                timeoutId = null;
            }

            const params = new URLSearchParams(document.location.search);
            let sign = params.get('sign');
            if (!(sign && sign.trim())) {
                sign = (typeof globalThis !== 'undefined' && globalThis.appSign)
                    ? String(globalThis.appSign)
                    : '';
            }
            let ppUrl = (typeof globalThis !== 'undefined' && globalThis.appPaymentId)
                ? '/pp/' + String(globalThis.appPaymentId)
                : '';
            var url = ppUrl + '?threeDSMethod=1&sign=' + sign;
            url = addRandomNumber(url);
            if (navigator.sendBeacon) {
                const ok = navigator.sendBeacon(url, new Blob([], {type: 'text/plain'}));
                if (ok) return;
            }

            if (window.fetch) {
                fetch(url, {method: 'GET', keepalive: true, credentials: 'same-origin', cache: 'no-store'})
                    .catch(() => {
                    });
            } else {
                try {
                    const xhr = new XMLHttpRequest();
                    xhr.open('GET', url, true);
                    xhr.send();
                } catch (e) {
                }
            }
        }

        function cleanup() {
            try {
                iframe.removeEventListener('load', onLoad);
            } catch (e) {
            }
            try {
                iframe.removeEventListener('error', onError);
            } catch (e) {
            }
            if (timeoutId) {
                clearTimeout(timeoutId);
                timeoutId = null;
            }
            setTimeout(() => {
                try {
                    form.remove();
                } catch (e) {
                }
            }, 0);
        }

        function onLoad() {
            cleanup();
            notifyOnce();
        }

        function onError() {
            cleanup();
            notifyOnce();
        }

        iframe.addEventListener('load', onLoad, {once: true});
        iframe.addEventListener('error', onError, {once: true});
        timeoutId = setTimeout(function () {
            cleanup();
            notifyOnce();
        }, 5000);
        form.submit();
    }
}

function handleSberpay(data) {
    let url2 = new URL(window.location.href);
    let nextSberpayStep = url2.searchParams.get('nextSberpayStep');
    if (isMobile() && (nextSberpayStep !== 'showQR')) {
        if (!sberpayStrategyIsDefined) {
            let formConfig = window.getFormJsonConfig();
            const currentCase = formConfig.sberpayMobileBehavior.type;
            defineSberpayStrategy(currentCase, data.deep_link);
            sberpayStrategyIsDefined = true;
        }
    } else {
        var qrCodeContainer = document.getElementById("qr-code");
        if (!qrCodeContainer) {
            genQR(data.deep_link, "formQRCodeSberpayWrapper");
            toggleLoader();
        }
    }
    if (updatePaymentStateHandle) window.clearInterval(updatePaymentStateHandle);
    var url = '/pp/' + data.order_id + '/?checkPaymentState=1&sign=' + data.sign;
    updatePaymentStateHandle = updatePaymentState(url);
}


function applyAction(data) {
    if (data instanceof ProgressEvent && data.target instanceof XMLHttpRequest) {
        const aaText = data.target.responseText || data.target.response;
        data = JSON.parse(aaText);
    }
    const params = new URLSearchParams(window.location.search);
    const isReturn = params.has('return');
    try {
        switch (data.action) {
            case 'drawElement':
                handleDrawElement(data);
                break;
            case 'setPaymentStatusCheck':
                handleSetPaymentStatusCheck(data);
                break;
            case 'post-redirect':
                handlePostRedirect(data);
                break;
            case 'reload':
                window.location.reload();
                break;
            case 'redirect':
                window.location = data.url;
                break;
            case 'qrcode':
                if (isReturn) break;
                handleQrCode(data);
                break;
            case 'sberpay':
                if (isReturn) break;
                handleSberpay(data);
                break;
            case 'iframe':
                handleIframe(data);
                break;
            case 'iframe_hidden':
                handleIframeHidden(data);
                break;
            default:
                break;
        }
    } catch (e) {
        checkLiveStatusHandle = checkLiveStatus();
        console.log(e);
    }
}

function updatePaymentState(url) {
    return window.setInterval(function () {
        url = addRandomNumber(url);
        fetch(url, {
            method: 'GET'
        }).then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error. Status: ${response.status}`);
            }
            return response.json();
        }).then((data) => {
            applyAction(data);
        }).catch((error) => {
        });
    }, 1000);
}

function sendForm() {
    if (checkLiveStatusHandle) window.clearInterval(checkLiveStatusHandle);
    ajaxPost(document.forms[0], applyAction);
    changeFormState(document.forms[0], true);
}


function changeFormState(form, state) {
    const inputs = form.elements;
    for (let i = 0; i < inputs.length; i++) {
        if (
            inputs[i].name !== 'card_mask'
            && inputs[i].name !== 'bank_search'
            && inputs[i].name !== "form-input-sberpay-phone"
            && inputs[i].name !== "phone_real"
            && inputs[i].id !== "toggleToPhone"
        ) inputs[i].disabled = state;
    }
}

function getExtInfo() {
    const date = new Date();
    const extInfo = {
        browserColorDepth: window.screen.colorDepth,
        browserLanguage: navigator.language,
        browserScreenHeight: window.screen.height,
        browserScreenWidth: window.screen.width,
        browserTz: date.getTimezoneOffset(),
        windowWidth: window.innerWidth,
        windowHeight: window.innerHeight
    };
    return JSON.stringify(extInfo);
}

function genQR(url, wrapper) {

    var formQRCodeWrapper = document.getElementById(wrapper);
    var windowWidth = window.innerWidth;
    var qrButton = document.getElementById("formButton");
    var qrCode = null;

    if (isMobile()) {
        qrCode = createQrCode(240, 240, url);
        document.getElementById("app").style.paddingTop = "0px";
        if (!document.body.classList.contains("route-sberpay")) {
            document.getElementById("formWrapper").style.marginTop = "0px";
        }
    } else {
        if (windowWidth < window.mobileBreakpoint) {
            qrCode = createQrCode(240, 240, url);
        } else {
            qrCode = createQrCode(300, 300, url);
        }
    }
    if (formQRCodeWrapper) {
        formQRCodeWrapper.classList.add("active");
        var qrCodeContainer = document.createElement("div");
        qrCodeContainer.classList.add("form-qrcode_container");
        qrCodeContainer.id = "qr-code";
        formQRCodeWrapper.prepend(qrCodeContainer);
    }
    if (qrCodeContainer) {
        qrCode.append(qrCodeContainer);
        if (qrButton) {
            qrButton.style.display = "none";
        }
        const observer = new MutationObserver(() => {
            const isDark = document.body.classList.contains('theme-dark');
            qrCode.update({
                dotsOptions: {color: isDark ? "white" : "black"},
                backgroundOptions: {color: isDark ? "transparent" : "transparent"},
                image: isDark ? "/nova/img/icons/logo-dark.svg" : "/nova/img/icons/logo.svg"
            });
        });
        observer.observe(document.body, {attributes: true, attributeFilter: ['class']});
    }


}


function showBankList(universalDeepLink, bankListWithQr) {

    var generatedBankLinks = generateBankLinks(c2bMembers, universalDeepLink);
    var qrCodeFormWrapper = document.getElementById("formQRCodeWrapper");
    qrCodeFormWrapper.style.display = "none";
    const bankList = document.getElementById("bankList");
    const bankListWrapper = document.querySelector(".bank-list-wrapper");
    const formWrapper = document.getElementById("formWrapper");
    const alreadyRendered = bankList.querySelector('.bank-item');

    if (!alreadyRendered) {
        const bankListHtml = generatedBankLinks
            .map(
                bank => `
      <li class="bank-item">
        <a class="bank-link" href="${bank.link}" target="_blank" rel="noopener noreferrer">
          <div class="bank-container">
            <div class="bank-icon-container">
              <img 
              class="bank-icon" 
              src="${bank.logo}" 
              alt="${bank.name}"
              onerror="this.onerror=null; this.src='/nova/img/icons/bank-placeholder.png';">
            </div>
            <span class="bank-name">${bank.name}</span>
          </div>
          <img class="arrow-right-icon" src="/nova/img/icons/arrow-right.svg" alt="Перейти в приложение банка">
        </a>
      </li>`
            )
            .join("\n");
        bankList.insertAdjacentHTML('beforeend', bankListHtml);
        hideEllipses();
    }

    bankListWrapper.style.display = "block";
    formWrapper.style.background = "transparent";
    formWrapper.style.boxShadow = "none";
    formWrapper.style.padding = "0px";

    if (bankListWithQr) {

        const qrModalWrapperExisting = document.getElementById("qrModalWrapper");

        if (!qrModalWrapperExisting) {

            var description = document.getElementById("description")?.textContent ?? "";
            var payer = document.getElementById("payer")?.textContent ?? "";

            var modalTextBlock = `
             <div class="qr-code_modal_text">
                <label><span id="payerInQr" class="form-header_payer">${payer}</span></label>
                <label style="display:block"><span id="descriptionInQr" class="form-header_description">${description}</span></label>
             </div>
            `

            const bankSearchWrapper = document.querySelector(".bank-search-wrapper");
            const universalDeepLinkElement = document.createElement("button");
            universalDeepLinkElement.classList.add("qrcode_btn");
            universalDeepLinkElement.id = "qrCodeBtn";
            universalDeepLinkElement.type = "button";
            universalDeepLinkElement.innerHTML = `
      <span class="universal-deep-link__text">Показать QR-код</span>
      <svg class="arrow-right-icon" width="16" height="16" viewBox="0 0 16 16" fill="none"
           xmlns="http://www.w3.org/2000/svg">
        <path d="M6 4L10 8L6 12" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `;

            const qrModalWrapper = document.createElement("div");
            qrModalWrapper.classList.add("qr-code__modal");
            qrModalWrapper.id = "qrModalWrapper";
            qrModalWrapper.innerHTML = `
  <button type="button" class="qr-close-btn" id="qrCloseBtn" aria-label="Закрыть QR-код">
    <svg width="44" height="44" viewBox="0 0 20 20" fill="none"
         xmlns="http://www.w3.org/2000/svg">
      <path d="M4.5 4.5L15.5 15.5M15.5 4.5L4.5 15.5"
            stroke="#000000" stroke-width="2"
            stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </button>
  ${modalTextBlock}
  <div class="qr-code_modal_content" id="qrModal"></div>
`;
            bankSearchWrapper.insertAdjacentElement("afterend", universalDeepLinkElement);
            document.body.append(qrModalWrapper);
            var qrCode = createQrCode(300, 300, universalDeepLink);
            var qrCodeBtn = document.getElementById("qrCodeBtn");
            if (qrCodeBtn) {
                qrCodeBtn.addEventListener("click", (e) => {
                    var currentOverlay = document.getElementById("overlay");
                    if (!currentOverlay) {
                        var overlay = document.createElement("div");
                        overlay.style.position = "absolute";
                        overlay.id = "overlay";
                        overlay.classList.add("overlay");
                        overlay.style.top = "0";
                        overlay.style.left = "0";
                        overlay.style.background = "rgba(0,0,0, .5)";
                        overlay.style.zIndex = "90";
                        overlay.style.width = "100%";
                        overlay.style.height = "100%";
                        overlay.classList.add("active");
                        document.body.appendChild(overlay);
                    }
                    e.stopPropagation();
                    qrModalWrapper.classList.toggle("active");
                });
                document.addEventListener("click", (e) => {
                    if (
                        qrModalWrapper.classList.contains("active") &&
                        e.target !== qrModalWrapper
                    ) {
                        qrModalWrapper.classList.remove("active");
                        deleteOverlay();
                    }
                });
                qrModalWrapper.addEventListener("click", (e) => {
                    e.stopPropagation();
                });
            }
            var qrModal = document.getElementById("qrModal");
            var qrCloseBtn = document.getElementById("qrCloseBtn");
            if (qrModal) {
                qrCode.append(qrModal);
                const observer = new MutationObserver(() => {
                    const isDark = document.body.classList.contains('theme-dark');
                    qrCode.update({
                        dotsOptions: {color: isDark ? "white" : "black"},
                        backgroundOptions: {color: isDark ? "transparent" : "transparent"},
                        image: isDark ? "/nova/img/icons/logo-dark.svg" : "/nova/img/icons/logo.svg"
                    });
                });
                observer.observe(document.body, {attributes: true, attributeFilter: ['class']});
                qrCloseBtn.addEventListener("click", () => {
                    qrModalWrapper.classList.remove("active");
                    deleteOverlay();
                });
            }
        }

    }
}

function deleteOverlay() {
    var overlay = document.getElementById("overlay");
    overlay.classList.remove("active");
    overlay.remove();
}

function defineSbpStrategy(currentCase, dataUrl) {
    switch (currentCase) {
        case "showQr":
            var qrCodeContainer = document.getElementById("qr-code");
            if (!qrCodeContainer) {
                genQR(dataUrl, "formQRCodeWrapper");
            }
            break;
        case "bankList":
            showBankList(dataUrl, false);
            break;
        case "bankListWithQr":
            showBankList(dataUrl, true);
            break;
        default:
            window.location = dataUrl;
    }
}

function defineSberpayStrategy(currentCase, deepLink) {
    switch (currentCase) {
        case "sberpayButton":
            if (isFirstSberpayClick) {
                isFirstSberpayClick = false;
                triggerMobileSberpay(deepLink);
            }
            toggleLoader();
            break;
        default:
            triggerMobileSberpay(deepLink);
    }
}

function triggerMobileSberpay(deepLink) {
    const ua = navigator.userAgent || "";
    const isIphone = /iPhone|iPad|iPod/i.test(ua);
    const titleEl = document.querySelector('h3.form-qrcode_title');
    const textEl = document.querySelector('.form-qrcode_text');

    if (isIphone) {
        if (titleEl) {
            titleEl.textContent = 'Открываем Сбербанк Онлайн';
        }
        if (textEl) {
            textEl.textContent = 'Если приложение не открылось автоматически, сделайте скриншот QR-кода и загрузите его в приложении СберБанк Онлайн'
        }
        const loader = document.createElement('span');
        loader.classList.add("loader");
        loader.id = "loader";
        loader.style.display = "block";
        loader.style.margin = "8px 0";
        titleEl.insertAdjacentElement("afterend", loader);
        deepLinkRoutingForIPhone(deepLink);
    } else {
        createSberpayFallback(1000, deepLink);
        if (titleEl) {
            titleEl.textContent = 'Если приложение не открылось, сделайте скриншот QR-кода и загрузите его в приложении СберБанк Онлайн';
        }
        if (textEl) {
            textEl.style.display = "none";
            textEl.style.margin = "0";
        }
        window.location.href = deepLink;
    }

}

function createSberpayFallback(timer, deepLink) {
    const headerLogo = document.getElementById("headerLogo");
    const fallbackTimer = setTimeout(() => {
        var qrCodeContainer = document.getElementById("qr-code");
        if (!qrCodeContainer) {
            genQR(deepLink, "formQRCodeSberpayWrapper");
            toggleLoader();
            if (headerLogo) {
                headerLogo.style.display = "none";
            }
        }
    }, timer);
    const handleVisibility = () => {
        if (document.visibilityState === "hidden") {
            clearTimeout(fallbackTimer);
        } else {
            var qrCodeContainer = document.getElementById("qr-code");
            if (!qrCodeContainer) {
                genQR(deepLink, "formQRCodeSberpayWrapper");
                toggleLoader();
                if (headerLogo) {
                    headerLogo.style.display = "none";
                }
            }
        }
        document.removeEventListener("visibilitychange", handleVisibility);
    };
    document.addEventListener("visibilitychange", handleVisibility);
}

function createQrCode(width, height, url) {
    qrCode = new QRCodeStyling({
        width: width,
        height: height,
        data: url,
        type: 'svg',
        image: document.body.classList.contains("theme-dark") ? LogoDark : Logo,
        dotsOptions: {
            color: document.body.classList.contains("theme-dark") ? "white" : "black",
            type: "rounded"
        },
        backgroundOptions: {
            color: document.body.classList.contains("theme-dark") ? "transparent" : "transparent",
        },
        imageOptions: {
            imageSize: 0.2,
            crossOrigin: "anonymous",
            margin: 4,
        },
        qrOptions: {
            errorCorrectionLevel: 'H',
        }
    });
    return qrCode;
}


function generateBankLinks(c2bJson, deepLink) {
    // https://sub.nspk.ru
    // https://qr.nspk.ru/
    const data = JSON.parse(c2bJson);
    const banks = data.dictionary;

    const ua = navigator.userAgent || "";
    const isIphone = /iPhone|iPad|iPod/i.test(ua);

    const url = new URL(deepLink);
    const qrId = url.pathname.replace(/^\//, '');
    const query = url.searchParams.toString();

    return banks.map(bank => {
        var link;
        const isSubscription = query.includes("type=03"); // type 03 это подписки, type 02 это обычный сбп
        let result = bank.webClientUrl;
        if (isSubscription && bank.webClientUrlSub) {
            result = bank.webClientUrlSub;
        }
        const filteredQuery = isSubscription ? "" : query;
        if (result) {
            if (bank.param_separator) {
                var sep = bank.param_separator;

                if (sep === "/") {
                    if (!result.endsWith("/")) {
                        result += "/";
                    }
                    if (qrId) {
                        result += qrId;
                    }
                    if (filteredQuery) {
                        result += "?" + filteredQuery;
                    }
                } else if (sep === "?") {
                    if (!result.endsWith("?")) {
                        result += "?";
                    }
                    if (qrId) {
                        result += qrId;
                    }
                    if (filteredQuery) {
                        result += "&" + filteredQuery;
                    }
                } else {
                    if (qrId) {
                        result += sep + qrId;
                    }
                    if (filteredQuery) {
                        result += (result.includes("?") ? "&" : "?") + filteredQuery;
                    }
                }
            } else {
                var endsWithSlash = result.endsWith("/");
                var endsWithQuestion = result.endsWith("?");
                if (qrId) {
                    if (endsWithSlash || endsWithQuestion) {
                        result += qrId;
                    } else {
                        result += "?" + qrId;
                    }
                }
                if (filteredQuery) {
                    if (result.includes("?")) {
                        result += "&" + filteredQuery;
                    } else {
                        result += "?" + filteredQuery;
                    }
                }
            }

            link = result;

        } else {
            link = `${bank.schema}://${deepLink.replace(/^https?:\/\//, "")}`;
        }

        return {
            name: bank.bankName,
            logo: bank.logoURL,
            link
        };
    });
}

function toggleLoader() {
    const globalLoader = document.getElementById("globalLoader");
    const paymentFormSbp = document.getElementById("paymentFormSbp");
    const paymentFormSberpay = document.getElementById("paymentFormSberpay");
    if (globalLoader && paymentFormSbp) {
        globalLoader.style.display = "none";
        paymentFormSbp.style.display = "block";
    } else if (globalLoader && paymentFormSberpay) {
        globalLoader.style.display = "none";
        paymentFormSberpay.style.display = "block";
    }
}

function addRandomNumber(url) {
    const [path, query = ''] = url.split('?');
    const params = new URLSearchParams(query);
    params.set('nc', Math.random().toString());
    return path + '?' + params.toString();
}


function deepLinkRoutingForIPhone(deepLink) {
    var params = extractParams(deepLink);
    const url = new URL(window.location.href);

    const openAppOnline = () => {
        window.location.href =
            `onlineappmobile://sbolpay/invoicing/v2?${params}`;
    };
    const openOnlineiosApp = () => {
        window.location.href =
            `onlineios-app://sbolpay/invoicing/v2?${params}`;
    };
    const openBtripEx = () => {
        window.location.href =
            `btripsexpenses://sbolpay/invoicing/v2?${params}`;
    };
    const openBuget = () => {
        window.location.href =
            `budgetonline-ios://sbolpay/invoicing/v2?${params}`;
    };
    const openAppSmart = () => {
        window.location.href =
            `ios-app-smartonline://sbolpay/invoicing/v2?${params}`;
    };
    const clearMessage = (e) => {
        url.searchParams.set('nextSberpayStep', e);
        window.location.href = url.toString();
        setTimeout(() => {
            window.location.href = url.toString();
        }, 60)
    };
    switch (url.searchParams.get('nextSberpayStep')) {
        case 'openOnlineiosApp':
            setTimeout(openOnlineiosApp, 50);
            clearMessage('openBtripEx')
            break;
        case 'openBtripEx':
            setTimeout(openBtripEx, 50);
            clearMessage('openBuget')
            break;
        case 'openBuget':
            setTimeout(openBuget, 50);
            clearMessage('openAppSmart')
            break;
        case 'openAppSmart':
            setTimeout(openAppSmart, 50);
            clearMessage('showQR')
            break;
        default:
            setTimeout(openAppOnline, 50);
            clearMessage('openOnlineiosApp')
    }
}

function extractParams(deepLink) {
    const index = deepLink.indexOf("?");
    if (index === -1) return "";
    return deepLink.slice(index + 1);
}

function hideEllipses() {
    var ellipseUp = document.querySelector(".ellipse-up");
    var ellipseDown = document.querySelector(".ellipse-down");
    if (window.innerWidth < window.tabletBreakpoint) {
        if (ellipseUp && ellipseDown) {
            var bankList = document.getElementById('bankList');
            if (bankList) {
                if (bankList.childElementCount > 0) {
                    ellipseUp.style.display = "none";
                    ellipseDown.style.display = "none";
                }
            }

        }
    }
}

window.addEventListener("resize", hideEllipses);
window.addEventListener("DOMContentLoaded", () => {
    const formButton = document.getElementById("formButton");
    if (formButton) {
        formButton.addEventListener('click', function (e) {
            e.preventDefault();
            if (checkLiveStatusHandle) window.clearInterval(checkLiveStatusHandle);
            ajaxPost(document.forms[0], applyAction);
            changeFormState(document.forms[0], true);
            document.forms[0].querySelectorAll('input, button').forEach(el => el.disabled = true);
            formButton.classList.remove('active', 'inactive');
            formButton.classList.add('loading');
            if (formButton.classList.contains("sberpay")) {
                isFirstSberpayClick = true;
            }
        });
        if (formButton.classList.contains("qr-code-trigger_btn")) {
            toggleLoader();
        }
        if (formButton.classList.contains("sberpay") && !document.forms[0].hasAttribute('sendOnLoad')) {
            toggleLoader();
        }
    }
});

if (document.getElementById('updatepaymentstate')) {
    let params = new URLSearchParams(document.location.search);
    let url = '?checkPaymentState=1&sign=' + params.get('sign');
    if (params.get('return') !== null) {
        url = url + '&return'
    }
    updatePaymentStateHandle = updatePaymentState(url);
}

if (document.forms[0] && document.forms[0].hasAttribute('sendOnLoad')) sendForm();
