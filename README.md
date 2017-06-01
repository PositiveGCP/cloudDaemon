# Cloud LVA - Firebase (daemon)

**Positive Compliance LLC**

**Author:** Dante Bazaldua [danteese](https://github.com/danteese)

*Release:* 1.0

This service was created in order to tackle the problems the organization had processing audio files locally, and now that we have a cloud service this is the implementation. 

Architecture
------------

This is the file tree: (_/home/devroot/new_cloud/cloud_)
```
cloud
│   README.md   -> Description of system (you're actually reading it)
│   .gitignore  -> Files ignored by git 
│   cloud.py    -> The main system file
│   keys.py     -> Binding the keys/passwords/sensitive information
│   mainCLVA.py -> All classes and functions that process/connect/give result from LVA and firebase
│   requirements.txt -> What do you need for the virtual enviorment and pip 
│   tests.py    -> Tiny script to test the daemon
│   test_real.py  (The same)
│
└───env ( do not move/delete/modify )
└───transactions ( do not move/delete/modify )
└───logsystem ( do not move/delete/modify )
```

Principles 
----------

The first thing we have to make sense is how to start and stop the service. 

**In order to start:** `python cloud.py`

**Turn off:** `bash killcloud.sh` _Be specially careful with this file_, the functionallity is explained later.
