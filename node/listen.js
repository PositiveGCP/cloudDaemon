var firebase = require('firebase');
var fs = require('fs');
var sys = require('util');
// var exec = require('child_process').exec;
const spawn = require('child_process').spawn;
// const subprocess = spawn('bad_command');
var moment = require('moment');

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

fs.appendFileSync('status.log', "Starting up...\n");

transferdb.on('child_added', function(snapshot){
  var key = snapshot.key;
  var now = moment().format("YY/MM/DD - HH:mm:ss Z");
  fs.appendFileSync('status.log', "[NEW]" + snapshot.key + " | " + now + "\n");

  console.log(key + '|' + now);
  const pscloud = spawn('python', ['pscloud', '--mode=dev', '-s', '--key=' + key],{
    cwd: '../',
  });

  // subprocess.on('error', (err) => {
  //   console.log('Failed to start subprocess.');
  //   console.log(err);
  // });

  pscloud.stdout.on('data', function(data) {
    fs.appendFileSync("status.log", "[COOL]: ID: " + snapshot.key + "\n");
  });
  pscloud.stderr.on('data', function(err) {
    fs.appendFileSync("status.log", "[ERR]: ID: " + err + "\n");
    console.log(err);
  });
  pscloud.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
  });

});
