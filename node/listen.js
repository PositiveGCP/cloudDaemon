var firebase = require('firebase');
var fs = require('fs');
var sys = require('util')
// var exec = require('child_process').exec;
const { spawn } = require('child_process');
const subprocess = spawn('bad_command');
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

console.log('Starting up...');
fs.appendFileSync('status.log', "Starting up...\n");
fs.appendFileSync("process.bash", "#!/bin/bash\n");

transferdb.on('child_added', function(snapshot){
<<<<<<< HEAD
=======
  // var key = (snapshot.key).substr(1, ((snapshot.key).length)-1 );
>>>>>>> 96209346a08bdffd7d3e0b1c2f4fd4c479234cd2
  var key = snapshot.key;
  var now = moment().format("YY/MM/DD - HH:mm:ss Z");
<<<<<<< HEAD
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
=======
  fs.appendFileSync('status.log', "[NEW]" + snapshot.key + " |Â " + now + "\n");

  console.log(key + '|' + now);
  const pscloud = spawn('python', ['pscloud', '--mode=dev', '-s', '--key=' + key],{
    cwd: '../',
  });

  subprocess.on('error', (err) => {
    console.log('Failed to start subprocess.');
    console.log(err);
  });

  pscloud.stdout.on('data', function(data) {
    fs.appendFileSync("status.log", "[COOL]: ID: " + snapshot.key + "\n");
  });
  pscloud.stderr.on('data', function(err) {
    fs.appendFileSync("status.log", "[ERR]: ID: " + err + "\n");
    console.log(err);
  });
  pscloud.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
>>>>>>> 278b4a113cc1f363b72e1ce4c2c0631331458bc9
  });

});
