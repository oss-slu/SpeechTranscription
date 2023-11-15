The 'nltk' library installation is more complex than just doing 'pip install nltk'.
This guide will show you how to install the 'nltk' library on different opertating systems (OS).

MacOS: 

    Perform the following steps to install nltk on MacOS. Do not include apostrophe's ( ' ' ) in command line:

        1. Install nltk and ceertifi via pip:
            'pip install nltk'
            'pip3 install certifi'

        2. Open Python Interpreter and import/download nltk:
            'python'
            >>> 'import nltk'
            >>> 'nltk.download()''

        3. Enter to following commands to avoid SSL Certificate issues:
            'CERT_PATH=$(python -m certifi)
            'export SSL_CERT_FILE=${CERT_PATH}'
            'export REQUESTS_CA_BUNDLE=${CERT_PATH}'

    The nltk library should now be ready to use on MacOS!

Windows:
- will be completed Wednesday after talk with Logan.

Linux:
- will be completed after talking with Colin or looking up other guide.