var firebase = require('firebase');
var fs = require('fs');
var sys = require('util')
var exec = require('child_process').exec;
var moment = require('moment');

var pscloud;

// Initialize Firebase
var appConfig = {
  apiKey: "AIzaSyAT7spVMFGob7q6Q1UJCaMi6RvGoMBgcAc",
  authDomain: "prototipo1-8e37a.firebaseapp.com",
  databaseURL: "https://prototipo1-8e37a.firebaseio.com",
  storageBucket: "prototipo1-8e37a.appspot.com",
  messagingSenderId: "856846236373"
};

var app = firebase.initializeApp(appConfig);
var secondapp = firebase.initializeApp(appConfig, "Secondary");

var positivedb = firebase.database();
var root = positivedb.ref();
var transferdb = positivedb.ref('Transfer').orderByChild('processed').equalTo(false);

console.log('Starting up...');
fs.appendFileSync('status.log', "Starting up...\n");
fs.appendFileSync("process.bash", "#!/bin/bash\n");

transferdb.on('child_added', function(snapshot){
  // var key = (snapshot.key).substr(1, ((snapshot.key).length)-1 );
  var key = snapshot.key;
  var now = moment().format("YY/MM/DD - HH:mm:ss Z");
  console.log(key + '|' + now);
  fs.appendFileSync('status.log', "[NEW]" + snapshot.key + "  " + now + "\n");
  var args = '--mode=dev -s --key=' + key;
  fs.appendFileSync("process.bash", "../pscloud --mode=dev -s --key=" + key + "\n");
  child = exec('"../pscloud" ' + args, function (error, stdout, stderr) {
    fs.appendFileSync("status.log", "[COOL]: ID: " + snapshot.key + "\n");
    fs.appendFileSync("process.bash", "../pscloud --mode=dev -s --key=" + key + "\n");
    if (stderr.length > 0){
      fs.appendFileSync("status.log", "[Err]: ID: " + snapshot.key + "\n");
    }
    if (error !== null) {
      fs.appendFileSync("status.log", "[Err]: Execution error. " + error);
    }
    console.log(stdout);
    console.error(stderr);
  });

});
