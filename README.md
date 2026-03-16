# netcat-py
Simple netcat (nc) replacement in pure Python.
```bash
python netcat.py -l -p 4444              # Listen
python netcat.py localhost 4444           # Connect
python netcat.py -l -p 8080 -e "ls -la"  # Execute on connect
python netcat.py host -z --range 1-1024  # Port scan
```
## Zero dependencies. Python 3.6+.
