# LoginForce
Python script to bruteforce server with basic access authentification.

This method is more efficient than unary brute force test by test. It allows you to use multiple asynchronous processes such that each of them has its own list of passwords to test. So for a test of 14,000 passwords, instead of putting 15s by making the list with 1 process, using 4 processes we only get 4s. (tested with the i7-10 generation, 64 BITS architecture, 2.4 GHz, 16 GB of RAM).
