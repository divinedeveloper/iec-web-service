myApp.controller('IecLookUpCtrl', ['$scope', '$http', '$location', '$rootScope', 'toaster', function($scope, $http, $location, $rootScope, toaster) {
        $scope.errorMessage;
    $scope.fileuploaded = "";

        $scope.validateIEC = function(){
            if($scope.ieCode!="" && $scope.companyName!=""){
                var createIECData = {}
                createIECData.code = $scope.ieCode.toString();
                createIECData.name = $scope.companyName;

                // createIECData.code = createIECData.code.toString()
                $http({method: 'POST', url: 'iec/api/v1/lookup/', data: createIECData}).
                   success(function(data, status, headers, config) {
                    if(status == 200){
                        console.log(data)
                        console.log(data.importer_exporter_code)
                        $scope.responseIecData = data
                           toaster.pop('success', "", "IEC data available");
                        //change redirect to blurbs created by user
                        // $location.path("/admin-blurbs");

                   }
                       
                       
                     }).
                 error(function(data, status, headers, config) {
                   if(status == 500){
                        toaster.pop('error', "", data.message);
                    }
                       if(status == 401){
                           toaster.pop('error', "", data.message);
                       }
                       if(status == 403){
                           toaster.pop('error', "", data.message);
                       }
                     if(status == 400){
                           toaster.pop('error', "", data.message);
                       }
                    if(status == 404){
                        toaster.pop('error', "", data.message);
//                      $location.path("/page-not-found");
                    }
                 }); 
            }else{
                toaster.pop('warning', "", data.message);
            }
        }
        
}]);