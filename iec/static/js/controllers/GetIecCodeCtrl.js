myApp.controller('GetIecCodeCtrl', ['$scope', '$http', '$location', '$routeParams', 'toaster', function($scope, $http, $location, $routeParams, toaster) {
        $scope.successMessage;
        $scope.errorMessage;
        $scope.getIecByCode = function(){
            
            // $http({method: 'GET', url: 'iec/api/v1/retrieve/' {params:{"code": $scope.ieCode}} }).            
            $http.get('iec/api/v1/retrieve/', {params:{"code": $scope.ieCode}}).
                success(function(data, status, headers, config) {
                       if(status == 200){
//                          console.log(data)
                        console.log(data.importer_exporter_code)
                        $scope.responseIecData = data
                           toaster.pop('success', "", "IEC data available");
                       }

                     }).
                error(function(data, status, headers, config) {
                    if(status == 401){
                        toaster.pop('error', "", data.message);
                    }
                    if(status == 400){
                        toaster.pop('error', "", data.message);
                    }
                    if(status == 500){
                        toaster.pop('error', "", data.message);
                    }
                    if(status == 502){
                        toaster.pop('error', "", "Server down");
                    }
                    if(status == 503){
                        toaster.pop('error', "", data.message);
                    }
                    if(status == 404){
                        toaster.pop('error', "", data.message);
//                      $location.path("/page-not-found");
                    }
//                   $scope.errorMessage = data.message;
                 }); 
        }
        
}]);