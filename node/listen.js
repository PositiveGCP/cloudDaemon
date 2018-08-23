var firebase = require('firebase');
var fs = require('fs');
var sys = require('util');
// var exec = require('child_process').exec;
const spawn = require('child_process').spawn;
const exec = require('child_process').exec;
// const subprocess = spawn('bad_command');
var moment = require('moment');

// Initialize Firebase
// var appConfig = {
//   apiKey: "AIzaSyAT7spVMFGob7q6Q1UJCaMi6RvGoMBgcAc",
//   authDomain: "prototipo1-8e37a.firebaseapp.com",
//   databaseURL: "https://prototipo1-8e37a.firebaseio.com",
//   storageBucket: "prototipo1-8e37a.appspot.com",
//   messagingSenderId: "856846236373"
// };

// var appConfig = {
//   apiKey: "AIzaSyAy0Th8gfePK390H6siuFj2PwLpujpzczs",
//   authDomain: "prototipo3-da7e9.firebaseapp.com",
//   databaseURL: "https://prototipo3-da7e9.firebaseio.com",
//   projectId: "prototipo3-da7e9",
//   storageBucket: "prototipo3-da7e9.appspot.com",
//   messagingSenderId: "277348998180"
// };

var appConfig = {
  apiKey: "AIzaSyALs0CPCUtF8Qz0nZLKm-lGIIRjqVaGYJU",
  authDomain: "prototipo4-57544.firebaseapp.com",
  databaseURL: "https://prototipo4-57544.firebaseio.com",
  projectId: "prototipo4-57544",
  storageBucket: "prototipo4-57544.appspot.com",
  messagingSenderId: "889527900945"
};

// firefighter
// var appConfig = {
//   apiKey: "AIzaSyAhDYV5B4WnGz1S-ewBWNiow-cWB85T3-I",
//   authDomain: "prototipo2-5af1f.firebaseapp.com",
//   databaseURL: "https://prototipo2-5af1f.firebaseio.com",
//   projectId: "prototipo2-5af1f",
//   storageBucket: "prototipo2-5af1f.appspot.com",
//   messagingSenderId: "428785972383"
// };

// var appConfig = {
//   apiKey: "AIzaSyDI_Hux_iKuQ5713OuF2tseod0lNxmP-Og",
//   authDomain: "prot1-5db64.firebaseapp.com",
//   databaseURL: "https://prot1-5db64.firebaseio.com",
//   projectId: "prot1-5db64",
//   storageBucket: "prot1-5db64.appspot.com",
//   messagingSenderId: "711884414318"
// };

var app = firebase.initializeApp(appConfig);
var secondapp = firebase.initializeApp(appConfig, "Secondary");

var positivedb = firebase.database();
var root = positivedb.ref();
var transferdb = positivedb.ref('Transfer').orderByChild('processed').equalTo(false);

// Prevent DoS
const MAX_TIME_TO_WAIT = 4320; // Two days in minutes
const DICTIONARY_FOR_KEYS = 'keysDICT.txt';
const REGISTER_KEY_FILE = 'keys.log';
const ISSUES_KEY_FILE = 'issues.log';
const LOG_FILE = 'status.log';

let GB_COUNTER = 0;

fs.appendFileSync(LOG_FILE, "Starting up...\n");

transferdb.on('child_added', function(snapshot){
  GB_COUNTER++;
  let now, data, key, _date;

  now = moment();
  data = snapshot.val();
  key = snapshot.key;
  _date = data.date;

  if (_date == undefined){
    _date = data.date_inicio;
  }

  console.log(["Debugging", key]);
  

  if ( isNew(_date, now)) {
    if (isKeyInFile(key) != true) {
      pscloudSocket(key, now);
      addToDictionary(key);
      reportActivity(key, 1, 'COMPLETED|' + GB_COUNTER);
    }
    else{
      console.log("Repetido");
      
      reportActivity(key, 2, 'REPEATED');
    }
  }
  else{
    // TODO: Send mail
    console.log("No paso ni la fecha");
    reportActivity(key, 2, 'OLD');
    // process.exit(1);
  }

});

function reportActivity (key, file, type) {
  let fp = '';
  if ( file == 1 ) {
    fp = REGISTER_KEY_FILE;
  }
  else if (file == 2) {
    fp = ISSUES_KEY_FILE;
  }
  fs.appendFileSync(fp,  key + "\t\t" + moment().unix() + "\t\t" + type + "\n");
}

/**
 * [pscloudSocket description]
 * @param  {[String]} key [Key to use with pscloud]
 * @param  {[Moment]} now [Timestamp]
 */
function pscloudSocket (key, now) {
  console.log("Reporting from pscloudSocket");
  
  fs.appendFileSync(LOG_FILE, "[NEW]" + key + " | " + now.format("YY/MM/DD - HH:mm:ss Z") + "\n");

  console.log(key + '|' + now);
  // const pscloud = spawn('ls');
  const pscloud = spawn('python', ['pscloud', '--mode=dev', '-s', '--key=' + key],{
    cwd: '../',
  });

  pscloud.stdout.on('data', function(data) {
    fs.appendFileSync(LOG_FILE, "[COOL]: ID: " + key + "\n");
  });
  pscloud.stderr.on('data', function(err) {
    fs.appendFileSync(LOG_FILE, "[ERR]: ID: " + err + "\n");
    console.log(err);
  });
  pscloud.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
  });
}

function addToDictionary (key) {
  console.log("Reporting from addToDictionary");
  fs.appendFileSync(DICTIONARY_FOR_KEYS, key + "\n");
}

function isNew (date1, date2) {
  let d1, d2, diff;
  d1 = moment.unix(date1);
  d2 = moment(date2);
  if (isNaN(d1)){
    // console.log("No valido");
    return false;
  }
  if (!d1.isValid()){
    d1 = moment(date1);
  }
  diff = d2.diff(d1, 'minutes');
  // console.log(diff);
  if ( diff > MAX_TIME_TO_WAIT ) {
    return false;
  }
  return true;
}


function isKeyInFile (key) {
  let keys = fs.readFileSync(DICTIONARY_FOR_KEYS).toString();
  let search = keys.search(key);
  if ( search == -1 ) {
    return false;
  }
  return true;
}
