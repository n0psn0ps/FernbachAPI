# FernbachAPI
Welcome to Fernbach, a vulnerable API written in the Flask micro web framework. The intent of this API is for testing the OWASP top ten vulnerabilities in an API environment. Below is the low privilege user credentials there are quite a few endpoints and users present many of which are not listed. It is suggested to use a scanner to locate these endpoints Burp Suite is prefered. As well as using some basic methodologies to find these other users.

Status: Check that the server is up and running. This is just to see if the docker image has worked successfully. http://127.0.0.1:5000/status

User Credentials:
'''
username = user <br />
password = user1234 <br />
public_id = 5a139b37-98b0-4562-8b54-6c728e3d9794 <br />
'''
Example API Calls:

The login endpoint allows for the user to create a token with a GET request using the username and password in the authorization header and use this auth token with the header "x-access-token" to make actions within the API endpoints:

Login:

Token Request:
'''
GET /api/v1/login HTTP/1.1 <br />
Host: localhost:5000 <br />
Authorization: Basic YWRtaW46YWRtaW4xMjM0 <br />
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 <br />
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.9 <br />
Accept-Encoding: gzip, deflate <br />
Accept-Language: en-US,en;q=0.9 <br />
Content-Length: 48<br />

{ <br />
'username' : 'user', <br />
'password' : 'user1234' <br />
}<br />
'''
Use the public_id to make changes on the /api/v1/user with the token at the endpoint:
'''
GET /api/v1/user/[public_id] HTTP/1.1 <br />
x-access-token: [from the login endpoint] <br />
Authorization: Basic dXNlcjp1c2VyMTIzNA== <br />
Content-Type: application/json <br />
User-Agent: PostmanRuntime/7.26.8 <br />
Host: localhost:5000 <br />
Accept-Encoding: gzip, deflate <br />
Connection: close Content-Length: 80<br />
'''
Check the demo user's shipment status at the GET shipment endpoint:

http://127.0.0.1:5000/shipment/13
