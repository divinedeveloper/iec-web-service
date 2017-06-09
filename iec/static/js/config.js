myApp.config(['$environmentProvider',
    function ($environmentProvider) {
                $environmentProvider.environments = [
//                         {
//                                 name: 'local',
//                                 pattern: /127.0.0.1/,
//                                 url: 'http://127.0.0.1:8000/',
//                                 analyticsAppId: 'UA-XXXXXXXX-1',
//                                 facebookAppId: '12345678901234',
//                                 baseurl: '//127.0.0.1:8000',
// //                                custurl: '//localhost:3000/cust'
//         },
        {
                                name: 'local',
                                pattern: /localhost/,
                                url: 'http://localhost/',
                                // analyticsAppId: 'UA-XXXXXXXX-1',
                                // facebookAppId: '12345678901234',
                                baseurl: '//localhost',
//                                custurl: '//localhost:3000/cust'
        },
                        {
                                name: 'production',
                                pattern: /139.59.31.145/,
                                url: 'http://139.59.31.145/',
                                // analyticsAppId: 'UA-XXXXXXXX-1',
                                // facebookAppId: '12345678901234',
                                baseurl: '//139.59.31.145',
//                                custurl: '//54.251.2.39/cust'
        }
    ];
}]);