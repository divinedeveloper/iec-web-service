'use strict';

/* Controllers */

myApp.controller('AppCtrl', ['$scope', '$http', '$rootScope', '$location', 'toaster', function($scope, $http, $rootScope, $location, toaster) {
	$scope.init = function () {
        $location.path("/");
    }
    
    $scope.lookupIECByCodeAndName = function(){
        $location.path("/lookup-iec");
    }

    $scope.getIECByCode = function(){
        $location.path("/get-iec");
    }
    
    $scope.goToHomePage= function(){
        $location.path("/");
    }
    
    
}]);
    