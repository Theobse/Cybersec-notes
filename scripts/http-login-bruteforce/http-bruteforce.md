# HTTP Login Bruteforce – Write-up

## Objective
The goal of this project is to demonstrate how weak authentication mechanisms
can be exploited through a simple HTTP login bruteforce attack.

This script is designed for educational purposes and for use in labs or
authorized environments only.

## Target Description
- Web application with a login form
- HTTP POST authentication
- No rate limiting
- No account lockout
- Error message returned on invalid credentials

## Attack Methodology

### 1. Reconnaissance
The login form was identified at: `POST /login.php`

Parameters used:
- `username`
- `password`

The response contains the string **"Invalid"** when authentication fails.

### 2. Bruteforce Strategy
The attack consists of:
- Iterating over a list of usernames
- Iterating over a list of passwords
- Sending POST requests using a persistent HTTP session
- Detecting successful authentication by analyzing the response content

### 3. Script Logic
Main steps:
1. Load usernames and passwords from files
2. Create a persistent session (`requests.Session`)
3. Send POST requests to the login endpoint
4. Check response body for failure message
5. Stop execution when valid credentials are found

## Example Usage

```bash
python3 http_bruteforce.py http://target/login.php users.txt passwords.txt
```

Example output:
```
[-] Failed: admin:admin
[-] Failed: admin:password
[+] VALID CREDENTIALS FOUND
    Username: admin
    Password: admin123
```

## Impact
If exploited on a real application, this vulnerability could allow:
- Account takeover
- Privilege escalation
- Access to sensitive data
- Lateral movement in internal applications

## Mitigations
- Implement rate limiting
- Enforce strong password policies
- Enable account lockout
- Use CAPTCHA after failed attempts
- Monitor authentication logs
 
## Limitations of the Script
- No multi-threading
- No CSRF token handling
- Static success condition

## Possible Improvements
- Add threading or async requests
- Automatic CSRF token extraction
- Configurable success/failure conditions
- Delay randomization to bypass detection
