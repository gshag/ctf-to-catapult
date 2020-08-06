# ctf-to-catapult
Converts the CTF output of the OCaml instrumented runtime to the catapult format.

Put both the eventlog and the metadata files in a single directory and make sure that the metadata file is named "metadata".
If the directory path is "~/tracefiles" and the desired output file is "out.json", then you can run this script as:

`python3 ./bt.py ~/tracefiles out.json`
