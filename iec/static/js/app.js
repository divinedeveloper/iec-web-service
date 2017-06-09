'use strict';
// Declare app level module which depends on filters, and services
var myApp = angular.module('myApp', ['myApp.filters', 'myApp.services', 'myApp.directives','ngRoute', 'ng-environments', 'ngAnimate', 'toaster']).
 	config(['$routeProvider', '$locationProvider', function($routeProvider, $locationProvider, $rootScope) {
        // $routeProvider.when('/', {templateUrl: '/templates/partials/blurbs-list', controller: 'BlurbsListCtrl'});
        $routeProvider.when('/lookup-iec', {
            templateUrl: '/static/pages/iec-lookup.html', 
            controller: 'IecLookUpCtrl',
        });
        $routeProvider.when('/get-iec', {
            templateUrl: '/static/pages/getIecCode.html', 
            controller: 'GetIecCodeCtrl',
        });
        
        $routeProvider.when('/page-not-found', {
            templateUrl: '/static/pages/page-not-found.html'
                       
        });
	    $routeProvider.otherwise({redirectTo: '/'});
	    $locationProvider.html5Mode(true);
  }]);

